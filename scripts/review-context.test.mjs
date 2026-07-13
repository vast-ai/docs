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
  assert.match(overlay, /\/context\?path=/);
});
