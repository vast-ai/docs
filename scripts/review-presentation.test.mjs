import assert from 'node:assert/strict';
import { before, after, test } from 'node:test';
import fs from 'node:fs/promises';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { serveReviewPresentation, PRESENTATION_ROUTE } from './review_presentation.mjs';

let directory, server, origin;
const video = Buffer.from('0123456789abcdefghijklmnopqrstuvwxyz');
const files = {
  'index.html': '<!doctype html><h1>Review presentation</h1>',
  'walkthrough.js': 'window.presentationReady = true;',
  'owner-questions.html': '<!doctype html><h1>Owner questions</h1>',
  'references/original-rental-cleanup.json': '{"retained":true}',
  'assets/scene.png': Buffer.from([137, 80, 78, 71]),
  'deliverables/host-docs-review-walkthrough/walkthrough.mp4': video,
  'deliverables/host-docs-review-walkthrough/captions.vtt': 'WEBVTT\n',
};

function request(urlPath, { method = 'GET', headers = {} } = {}) {
  return new Promise((resolve, reject) => {
    const req = http.request(origin, { path: urlPath, method, headers }, res => {
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks) }));
    });
    req.on('error', reject); req.end();
  });
}

before(async () => {
  directory = await fs.mkdtemp(path.join(os.tmpdir(), 'review-presentation-test-'));
  for (const [file, data] of Object.entries(files)) {
    await fs.mkdir(path.dirname(path.join(directory, file)), { recursive: true });
    await fs.writeFile(path.join(directory, file), data);
  }
  await fs.writeFile(path.join(directory, '.secret'), 'must not be served');
  await fs.mkdir(path.join(directory, 'pipeline'));
  await fs.writeFile(path.join(directory, 'pipeline', 'runtime.js'), 'must not be served');
  await fs.symlink(path.join(directory, '.secret'), path.join(directory, 'assets', 'leak.png'));
  await fs.symlink(path.join(directory, 'assets'), path.join(directory, 'references', 'linked'));
  server = http.createServer(async (req, res) => {
    if (await serveReviewPresentation(req, res, directory)) return;
    res.writeHead(200, { 'content-type': 'text/html' }); res.end('<html>Unchanged docs response</html>');
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  origin = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  if (server) await new Promise(resolve => server.close(resolve));
  if (directory) await fs.rm(directory, { recursive: true, force: true });
});

test('serves the entry, script, owner companion and exact retained JSON with MIME types', async () => {
  for (const [file, mime] of [['', 'text/html'], ['walkthrough.js', 'text/javascript'],
    ['owner-questions.html', 'text/html'], ['references/original-rental-cleanup.json', 'application/json']]) {
    const result = await request(PRESENTATION_ROUTE + file);
    assert.equal(result.status, 200); assert.ok(result.headers['content-type'].startsWith(mime));
    assert.equal(result.headers['x-content-type-options'], 'nosniff');
    assert.deepEqual(result.body, Buffer.from(files[file || 'index.html']));
  }
  const redirect = await request(PRESENTATION_ROUTE.slice(0, -1));
  assert.equal(redirect.status, 308); assert.equal(redirect.headers.location, PRESENTATION_ROUTE);
});

test('MP4 full, bounded, suffix and open-ended reads return exact bytes for native seeking', async () => {
  const url = PRESENTATION_ROUTE + 'deliverables/host-docs-review-walkthrough/walkthrough.mp4';
  const full = await request(url);
  assert.equal(full.status, 200); assert.deepEqual(full.body, video);
  assert.equal(full.headers['content-type'], 'video/mp4'); assert.equal(full.headers['accept-ranges'], 'bytes');
  for (const [range, start, end] of [['bytes=2-5', 2, 5], ['bytes=-4', 32, 35], ['bytes=30-', 30, 35], ['bytes=30-999', 30, 35]]) {
    const result = await request(url, { headers: { range } });
    assert.equal(result.status, 206); assert.equal(result.headers['content-range'], `bytes ${start}-${end}/36`);
    assert.equal(Number(result.headers['content-length']), end - start + 1);
    assert.deepEqual(result.body, video.subarray(start, end + 1));
  }
  const head = await request(url, { method: 'HEAD' });
  assert.equal(head.status, 200); assert.equal(head.body.length, 0); assert.equal(head.headers['content-length'], '36');
});

test('invalid, multiple and unsatisfiable ranges fail without serving the media', async () => {
  for (const range of ['bytes=99-', 'bytes=5-2', 'bytes=-0', 'bytes=0-1,5-6', 'bytes=-', 'bytes=9007199254740993-']) {
    const result = await request(PRESENTATION_ROUTE + 'deliverables/host-docs-review-walkthrough/walkthrough.mp4', { headers: { range } });
    assert.equal(result.status, 416); assert.equal(result.headers['content-range'], 'bytes */36');
  }
});

test('rejects traversal, hidden files, unlisted code and symlink escapes', async () => {
  for (const suffix of ['../README.md', '%2e%2e/README.md', '%252e%252e/README.md',
    'assets/../../README.md', 'assets%2f..%2f..%2fREADME.md', '..%5cREADME.md', '.secret',
    'pipeline/runtime.js', 'assets/leak.png', 'references/linked/leak.png']) {
    const result = await request(PRESENTATION_ROUTE + suffix);
    assert.equal(result.status, 404, suffix);
    assert.ok(!result.body.includes(Buffer.from('must not be served')), suffix);
  }
  assert.equal((await request(PRESENTATION_ROUTE + '%ZZ')).status, 400);
  const original = path.join(directory, 'assets');
  await fs.rename(original, original + '-real'); await fs.symlink(original + '-real', original);
  try { assert.equal((await request(PRESENTATION_ROUTE + 'assets/scene.png')).status, 404); }
  finally { await fs.unlink(original); await fs.rename(original + '-real', original); }
});

test('presentation stays read-only and other doc routes fall through unchanged', async () => {
  const post = await request(PRESENTATION_ROUTE, { method: 'POST' });
  assert.equal(post.status, 405); assert.equal(post.headers.allow, 'GET, HEAD');
  const docs = await request('/host/hosting-overview');
  assert.equal(docs.status, 200); assert.equal(docs.body.toString(), '<html>Unchanged docs response</html>');
});

test('presentation is linked from reviewer surfaces and excluded from Mintlify', async () => {
  const source = await fs.readFile(new URL('../review-server.mjs', import.meta.url), 'utf8');
  assert.equal((source.match(/href="\/__review__\/presentation\/"[^>]*>Review presentation<\/a>/g) || []).length, 2);
  assert.ok(source.indexOf('await serveReviewPresentation(req, res,') < source.indexOf('const url = new URL(req.url,'));
  assert.match(await fs.readFile(new URL('../.mintignore', import.meta.url), 'utf8'), /^review-presentation\/$/m);
});
