import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let targetServer;
let reviewProcess;
let targetOrigin;
let reviewOrigin;
let feedbackDir;
let reviewOutput = '';

function listen(server, port = 0) {
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, '127.0.0.1', () => {
      server.removeListener('error', reject);
      resolve(server.address().port);
    });
  });
}

async function freePort() {
  const server = http.createServer();
  const port = await listen(server);
  await new Promise((resolve) => server.close(resolve));
  return port;
}

async function waitForReviewServer() {
  let lastError;
  for (let i = 0; i < 80; i += 1) {
    if (reviewProcess.exitCode != null) {
      throw new Error(`review server exited early (${reviewProcess.exitCode})\n${reviewOutput}`);
    }
    try {
      const response = await fetch(`${reviewOrigin}/__review__/api/context?path=%2Fhost%2Fhost-teams`);
      if (response.ok) return;
      lastError = new Error(`HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  throw new Error(`review server did not become ready: ${lastError}\n${reviewOutput}`);
}

async function contextFor(pathname) {
  const response = await fetch(`${reviewOrigin}/__review__/api/context?path=${encodeURIComponent(pathname)}`);
  assert.equal(response.status, 200);
  return response.json();
}

async function postJson(pathname, payload) {
  return fetch(`${reviewOrigin}${pathname}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

async function reviewerState(reviewer) {
  const response = await fetch(`${reviewOrigin}/__review__/api/state?reviewer=${encodeURIComponent(reviewer)}`);
  assert.equal(response.status, 200);
  return response.json();
}

before(async () => {
  targetServer = http.createServer((req, res) => {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><body><h1>Stub preview</h1><p>${req.url}</p></body></html>`);
  });
  const targetPort = await listen(targetServer);
  const reviewPort = await freePort();
  targetOrigin = `http://127.0.0.1:${targetPort}`;
  reviewOrigin = `http://127.0.0.1:${reviewPort}`;
  feedbackDir = await fs.mkdtemp(path.join(os.tmpdir(), 'vast-review-context-'));
  reviewProcess = spawn(process.execPath, [
    'review-server.mjs', '--port', String(reviewPort), '--target', targetOrigin, '--dir', feedbackDir,
  ], { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] });
  reviewProcess.stdout.on('data', (chunk) => { reviewOutput += chunk; });
  reviewProcess.stderr.on('data', (chunk) => { reviewOutput += chunk; });
  await waitForReviewServer();
});

after(async () => {
  if (reviewProcess && reviewProcess.exitCode == null) {
    reviewProcess.kill('SIGTERM');
    await new Promise((resolve) => reviewProcess.once('exit', resolve));
  }
  if (targetServer) await new Promise((resolve) => targetServer.close(resolve));
  if (feedbackDir) await fs.rm(feedbackDir, { recursive: true, force: true });
});

test('Host Teams shows its Jira sources and only its page blockers', async () => {
  const context = await contextFor('/host/host-teams');
  assert.deepEqual(context.epics.map((issue) => issue.key), ['CON-1187']);
  assert.deepEqual(context.issues.map((issue) => issue.key), ['CON-1581', 'CON-1584']);
  assert.equal(context.blockers.length, 4);
  assert.ok(context.blockers.some((item) => item.question.includes('accrued earnings')));
  assert.ok(context.blockers.every((item) => item.issue.url.startsWith('https://vastai.atlassian.net/browse/')));
});

test('Self-Test reference links both epics without stale implementation blockers', async () => {
  const context = await contextFor('/host/self-test-reference');
  assert.deepEqual(context.epics.map((issue) => issue.key), ['CON-1187', 'CON-1509']);
  for (const key of ['CON-1515', 'CON-1513', 'CON-1510', 'CON-1583', 'CON-1419']) {
    assert.ok(context.issues.some((issue) => issue.key === key), `missing ${key}`);
  }
  assert.equal(context.blockers.length, 1);
  assert.ok(context.blockers.some((item) => item.question.includes('queue and wait-time')));
  assert.ok(context.blockers.every((item) => !item.question.includes('actual-versus-required')));
  assert.ok(context.blockers.every((item) => !item.question.includes('source-repository dispatch')));
});

test('Diagnostics no longer reports merged dump-logs documentation as missing', async () => {
  const context = await contextFor('/host/common-errors-diagnostics');
  assert.ok(context.issues.some((issue) => issue.key === 'CON-1519'));
  assert.ok(context.blockers.every((item) => !item.question.includes('vastai dump-logs')));
});

test('Network page receives network blockers without unrelated Teams blockers', async () => {
  const context = await contextFor('/host/network-ports');
  assert.deepEqual(context.issues.map((issue) => issue.key), ['CON-1517', 'CON-1514']);
  assert.ok(context.blockers.some((item) => item.question.includes('TCP/UDP')));
  assert.ok(context.blockers.every((item) => item.issue.key === 'CON-1514'));
});

test('Unmapped Host pages retain epic provenance without invented blockers', async () => {
  const context = await contextFor('/host/workload-policy');
  assert.equal(context.matched, false);
  assert.deepEqual(context.epics.map((issue) => issue.key), ['CON-1187']);
  assert.deepEqual(context.issues, []);
  assert.deepEqual(context.blockers, []);
});

test('Non-Host pages do not inherit Host Jira context', async () => {
  const context = await contextFor('/guides/get-started');
  assert.deepEqual(context.epics, []);
  assert.deepEqual(context.issues, []);
  assert.deepEqual(context.blockers, []);
});

test('Only the review proxy injects the overlay', async () => {
  const targetHtml = await (await fetch(`${targetOrigin}/host/host-teams`)).text();
  const reviewHtml = await (await fetch(`${reviewOrigin}/host/host-teams`)).text();
  assert.doesNotMatch(targetHtml, /__review__\/overlay\.js/);
  assert.match(reviewHtml, /__review__\/overlay\.js/);
  const overlay = await (await fetch(`${reviewOrigin}/__review__/overlay.js`)).text();
  assert.match(overlay, /Jira context for this page/);
  assert.match(overlay, /REVIEW-TRACEABILITY\.md/);
  assert.match(overlay, /\/context\?path=/);
  assert.match(overlay, /Save JSON/);
  assert.match(overlay, /Import JSON/);
  assert.match(overlay, /\/import/);
});

test('JSON import restores multiple reviewers and keeps newer server items', async () => {
  const newerAlice = {
    id: 'roundtrip-alice', reviewer: 'Alice', page: '/host/hosting-overview',
    pageTitle: 'Hosting Overview', type: 'inline', quote: 'Hosts provide machines',
    prefix: 'Overview: ', suffix: '; renters run workloads', heading: 'Hosting Overview',
    category: 'Suggestion', severity: 'Minor', comment: 'Keep the newer wording.',
    status: 'open', createdAt: '2026-07-13T08:00:00.000Z', updatedAt: '2026-07-13T10:00:00.000Z',
  };
  const saveResponse = await postJson('/__review__/api/state', { reviewer: 'Alice', items: [newerAlice] });
  assert.equal(saveResponse.status, 200);

  const olderAlice = { ...newerAlice, comment: 'Older backup wording.', updatedAt: '2026-07-13T09:00:00.000Z' };
  const bob = {
    id: 'roundtrip-bob', reviewer: 'Bob', page: '/host/network-ports',
    pageTitle: 'Network & Ports', type: 'page', quote: '', prefix: '', suffix: '', heading: '',
    category: 'Question', severity: 'Major', comment: 'Confirm the UDP wording.',
    status: 'resolved', createdAt: '2026-07-13T09:15:00.000Z', updatedAt: '2026-07-13T09:20:00.000Z',
  };
  const importResponse = await postJson('/__review__/api/import', {
    format: 'vast-docs-review-feedback', version: 1, generatedAt: '2026-07-13T09:30:00.000Z',
    pr: 'https://github.com/vast-ai/docs/pull/185', reviewers: ['Alice', 'Bob'], items: [olderAlice, bob],
  });
  assert.equal(importResponse.status, 200);
  const imported = await importResponse.json();
  assert.equal(imported.imported, 2);
  assert.equal(imported.reviewerCount, 2);

  const aliceState = await reviewerState('Alice');
  assert.equal(aliceState.items.length, 1);
  assert.equal(aliceState.items[0].comment, 'Keep the newer wording.');
  assert.equal(aliceState.items[0].quote, 'Hosts provide machines');
  assert.equal(aliceState.items[0].prefix, 'Overview: ');
  assert.equal(aliceState.items[0].suffix, '; renters run workloads');

  const bobState = await reviewerState('Bob');
  assert.equal(bobState.items.length, 1);
  assert.equal(bobState.items[0].comment, 'Confirm the UDP wording.');

  const exportResponse = await fetch(`${reviewOrigin}/__review__/export/feedback.json`);
  assert.equal(exportResponse.status, 200);
  const exported = await exportResponse.json();
  assert.equal(exported.format, 'vast-docs-review-feedback');
  assert.equal(exported.version, 1);
  assert.ok(exported.items.some((item) => item.id === 'roundtrip-alice' && item.comment === 'Keep the newer wording.'));
  assert.ok(exported.items.some((item) => item.id === 'roundtrip-bob'));

  const statusHtml = await (await fetch(`${reviewOrigin}/__review__/`)).text();
  assert.match(statusHtml, /Save JSON/);
  assert.match(statusHtml, /Import JSON/);
  assert.match(statusHtml, /restorable backup for every page and reviewer/);
});

test('JSON import rejects an invalid backup before writing any reviewer state', async () => {
  const response = await postJson('/__review__/api/import', {
    format: 'vast-docs-review-feedback', version: 1,
    items: [
      {
        id: 'atomic-valid', reviewer: 'Charlie', page: '/host/quickstart', comment: 'Would otherwise be valid.',
        updatedAt: '2026-07-13T10:00:00.000Z',
      },
      { id: 'atomic-invalid', page: '/host/quickstart', comment: 'Missing reviewer.' },
    ],
  });
  assert.equal(response.status, 400);
  const error = await response.json();
  assert.match(error.error, /missing a valid reviewer/);
  const charlieState = await reviewerState('Charlie');
  assert.deepEqual(charlieState.items, []);
});
