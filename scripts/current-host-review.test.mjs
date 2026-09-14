import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import { spawn } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Preserve all pre-scan gate regressions against their immutable source/model
// phase. Active scan behavior is covered separately, not by changing these
// historical expected outcomes to match a new projection.
const ACTIVE_SCAN = await fs.readFile(path.join(ROOT,'verification/current-host-authority-scan.json'),'utf8').then(JSON.parse).catch(error=>{if(error.code==='ENOENT')return null;throw error;});
const PACKAGE = path.join(ROOT, ACTIVE_SCAN ? ACTIVE_SCAN.baseline.path : 'verification/current-host-docs-review.json');
let target;
let targetOrigin;
function listen(server) {
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => resolve(server.address().port));
  });
}

async function freePort() {
  const server = http.createServer();
  const port = await listen(server);
  await new Promise((resolve) => server.close(resolve));
  return port;
}

async function externalSibling(name) {
  let cursor = process.env.VV_TEST_SOURCE_ROOT ? path.resolve(process.env.VV_TEST_SOURCE_ROOT, 'docs') : ROOT;
  for (;;) {
    const candidate = path.join(path.dirname(cursor), name);
    try { return await fs.realpath(candidate); } catch { /* walk toward the workspace root */ }
    const parent = path.dirname(cursor);
    if (parent === cursor) throw new Error(`missing external source fixture: ${name}`);
    cursor = parent;
  }
}

function fixtureContainer(root) {
  return path.dirname(root);
}

async function fixtureRoot() {
  const container = await fs.mkdtemp(path.join(os.tmpdir(), 'vast-current-review-'));
  const root = path.join(container, 'docs');
  await fs.mkdir(root);
  // The server checks citations against sibling repositories at their pinned
  // commits. Symlink those source stores into the fixture instead of copying
  // their object databases for every focused assertion.
  await Promise.all(['vast-cli', 'self-test'].map(async (name) => fs.symlink(
    await externalSibling(name), path.join(container, name), 'dir',
  )));
  for (const item of ['docs.json', 'host', 'snippets/host', 'snippets/notifications/channels.mdx', 'cli/reference', 'sdk/python/reference', '.git']) {
    const source = path.join(ROOT, item);
    const destination = path.join(root, item);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.cp(source, destination, { recursive: true, dereference: false });
  }
  await fs.mkdir(path.join(root, 'verification'), { recursive: true });
  for (const item of [
    'host-docs-test-sets.json', 'host-docs-test-results.json', 'host-docs-command-scores.json',
    'current-host-docs-review.json', 'current-h100x4-direct-postinstall-adjudications.json', 'current-h100x4-rental-adjudications.json', 'current-host-claim-corrections.json', 'current-host-product-publications.json',
    'current-host-readonly-adjudications.json', 'current-host-connection-adjudications.json',
  ]) await fs.copyFile(path.join(ROOT, 'verification', item), path.join(root, 'verification', item));
  await fs.copyFile(
    path.join(ROOT, 'verification', 'current-host-live-adjudications.json'),
    path.join(root, 'verification', 'current-host-live-adjudications.json'),
  );
  await fs.copyFile(
    path.join(ROOT, 'verification', 'current-host-editorial-classifications.json'),
    path.join(root, 'verification', 'current-host-editorial-classifications.json'),
  ).catch((error) => { if (error.code !== 'ENOENT') throw error; });
  const authorityRef = 'verification/current-host-authority-adjudications.json';
  const authorityText = await fs.readFile(path.join(ROOT, authorityRef), 'utf8').catch((error) => {
    if (error.code === 'ENOENT') return null;
    throw error;
  });
  if (authorityText !== null) {
    await fs.copyFile(path.join(ROOT, authorityRef), path.join(root, authorityRef));
    const authority = JSON.parse(authorityText);
    const refs = [authority.baseline?.path, ...(authority.artifacts || []).map((row) => row.path),
      'verification/evidence/2026-09-09-host-authority-correction-attempt-01/current-static-checks-01.json'].filter(Boolean);
    for (const ref of new Set(refs)) {
      const source = path.join(ROOT, ref); const destination = path.join(root, ref);
      await fs.mkdir(path.dirname(destination), { recursive: true });
      await fs.copyFile(source, destination);
    }
  }
  const connection = JSON.parse(await fs.readFile(path.join(ROOT, 'verification', 'current-host-connection-adjudications.json'), 'utf8'));
  for (const artifact of connection.artifacts) {
    const source = path.join(ROOT, artifact.path); const destination = path.join(root, artifact.path);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.copyFile(source, destination);
  }
  const transitionRef = 'verification/current-two-defect-transition.json';
  const transitionText = await fs.readFile(path.join(ROOT, transitionRef), 'utf8').catch((error) => {
    if (error.code === 'ENOENT') return null;
    throw error;
  });
  if (transitionText !== null) {
    await fs.copyFile(path.join(ROOT, transitionRef), path.join(root, transitionRef));
    const transition = JSON.parse(transitionText);
    const refs = [transition.baseline?.model?.path, ...Object.values(transition.current_pages || {}).map((row) => row.snapshot),
      ...(transition.artifacts || []).map((row) => row.path)].filter(Boolean);
    for (const ref of new Set(refs)) {
      const source = path.join(ROOT, ref); const destination = path.join(root, ref);
      await fs.mkdir(path.dirname(destination), { recursive: true });
      await fs.copyFile(source, destination);
    }
  }
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-07-host-current-vv-attempt-01'), { recursive: true });
  await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-07-host-current-vv-attempt-01', 'current-static-checks.json'),
    path.join(root, 'verification', 'evidence', '2026-09-07-host-current-vv-attempt-01', 'current-static-checks.json'),
  );
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-08-host-live-readonly-attempt-01'), { recursive: true });
  await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-08-host-live-readonly-attempt-01', 'market-api-01.json'),
    path.join(root, 'verification', 'evidence', '2026-09-08-host-live-readonly-attempt-01', 'market-api-01.json'),
  );
  await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-08-host-live-readonly-attempt-01', 'product-source-capture-02.json'),
    path.join(root, 'verification', 'evidence', '2026-09-08-host-live-readonly-attempt-01', 'product-source-capture-02.json'),
  );
  for (const item of ['batch-d-cli-execution-01.json', 'batch-e-cli-execution-01.json', 'batch-d-source-provenance.json']) {
    await fs.copyFile(path.join(ROOT, 'verification', 'evidence', '2026-09-08-host-live-readonly-attempt-01', item),
      path.join(root, 'verification', 'evidence', '2026-09-08-host-live-readonly-attempt-01', item));
  }
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-08-host-ada-readiness-attempt-01'), { recursive: true });
  await fs.copyFile(path.join(ROOT, 'verification', 'evidence', '2026-09-08-host-ada-readiness-attempt-01', 'api-01.json'),
    path.join(root, 'verification', 'evidence', '2026-09-08-host-ada-readiness-attempt-01', 'api-01.json'));
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-08-host-client-unblocking-attempt-01'), { recursive: true });
  for (const item of ['cli-execution-01.json', 'host-search-execution-01.json', 'cli-source-provenance-01.json']) await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-08-host-client-unblocking-attempt-01', item),
    path.join(root, 'verification', 'evidence', '2026-09-08-host-client-unblocking-attempt-01', item));
  for (const item of ['vm-helper-source-retest-02.json', 'vm-status-01.json', 'client-discovery-cli-source-01.json']) await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-08-host-client-unblocking-attempt-01', item),
    path.join(root, 'verification', 'evidence', '2026-09-08-host-client-unblocking-attempt-01', item));
  await fs.copyFile(path.join(ROOT, 'verification', 'current-host-readonly-findings.json'), path.join(root, 'verification', 'current-host-readonly-findings.json'));
  await fs.mkdir(path.join(root, 'scripts'), { recursive: true });
  await fs.copyFile(path.join(ROOT, 'scripts', 'current_host_install_evidence_intake.mjs'),
    path.join(root, 'scripts', 'current_host_install_evidence_intake.mjs'));
  await fs.copyFile(path.join(ROOT, 'scripts', 'current_host_authority_scan.mjs'), path.join(root, 'scripts', 'current_host_authority_scan.mjs'));
  await fs.copyFile(path.join(ROOT, 'scripts', 'current_host_terms_binding.mjs'), path.join(root, 'scripts', 'current_host_terms_binding.mjs'));
  await fs.copyFile(path.join(ROOT, 'scripts', 'current_host_jurisdiction.mjs'), path.join(root, 'scripts', 'current_host_jurisdiction.mjs'));
  await fs.copyFile(path.join(ROOT, 'scripts', 'current_host_review_cleanup.mjs'), path.join(root, 'scripts', 'current_host_review_cleanup.mjs')).catch(error => { if (error.code !== 'ENOENT') throw error; });
  await fs.copyFile(path.join(ROOT, 'scripts', 'current_host_review_transition.mjs'), path.join(root, 'scripts', 'current_host_review_transition.mjs'));
  await fs.copyFile(path.join(ROOT, 'scripts', 'current_host_payout_provider_correction.mjs'), path.join(root, 'scripts', 'current_host_payout_provider_correction.mjs'));
  await fs.copyFile(path.join(ROOT, 'scripts', 'current_host_clarification.mjs'), path.join(root, 'scripts', 'current_host_clarification.mjs'));
  await fs.copyFile(path.join(ROOT, 'scripts', 'host_review_reader_copy.mjs'), path.join(root, 'scripts', 'host_review_reader_copy.mjs'));
  await fs.copyFile(path.join(ROOT, 'scripts', 'host_review_work_queue.mjs'), path.join(root, 'scripts', 'host_review_work_queue.mjs'));
  const scanPath = 'verification/current-host-authority-scan.json';
  const scan = await fs.readFile(path.join(ROOT, scanPath), 'utf8').then(JSON.parse).catch(error => { if (error.code === 'ENOENT') return null; throw error; });
  if (scan) {
    const snapshot = JSON.parse(await fs.readFile(path.join(ROOT, scan.source_snapshot.path), 'utf8'));
    for (const item of snapshot.records) {
      const destination = path.join(root, item.path); await fs.mkdir(path.dirname(destination), {recursive: true}); await fs.copyFile(path.join(ROOT, item.snapshot), destination);
    }
    await fs.copyFile(path.join(ROOT, scan.baseline.path),path.join(root,'verification/current-host-docs-review.json'));
  }
  await fs.copyFile(path.join(ROOT, 'verification', 'current-host-install-evidence-intake.json'),
    path.join(root, 'verification', 'current-host-install-evidence-intake.json'));
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-08-h100x4-install-history-attempt-01'), { recursive: true });
  for (const item of ['new-host-readonly-02.json', 'source-inspection-02.json', 'source-inspection-02.md', 'source-inspection-01.md']) {
    await fs.copyFile(path.join(ROOT, 'verification', 'evidence', '2026-09-08-h100x4-install-history-attempt-01', item),
      path.join(root, 'verification', 'evidence', '2026-09-08-h100x4-install-history-attempt-01', item));
  }
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-08-h100x4-safe-installer-attempt-01'), { recursive: true });
  for (const item of [
    'variant-preparation-01.json', 'variant-tests-01.json', 'variant-tests-02.json', 'readiness-01.json',
    'readiness-projection-01.json', 'tui-source-identity-01.json', 'source-review-summary.json', 'candidate-independent-review-02.json',
  ]) await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-08-h100x4-safe-installer-attempt-01', item),
    path.join(root, 'verification', 'evidence', '2026-09-08-h100x4-safe-installer-attempt-01', item),
  );
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-08-h100x4-direct-install-attempt-01'), { recursive: true });
  await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-08-h100x4-direct-install-attempt-01', 'preflight-02.json'),
    path.join(root, 'verification', 'evidence', '2026-09-08-h100x4-direct-install-attempt-01', 'preflight-02.json'),
  );
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-09-h100x4-listing-rental-attempt-01'), { recursive: true });
  for (const item of ['listing-request-01.json', 'listing-response-01.json', 'listing-readback-verification-01.json']) await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-09-h100x4-listing-rental-attempt-01', item),
    path.join(root, 'verification', 'evidence', '2026-09-09-h100x4-listing-rental-attempt-01', item),
  );
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-09-h100x4-listing-rental-attempt-02', 'rate-010'), { recursive: true });
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-09-h100x4-listing-rental-attempt-02', 'rate-001'), { recursive: true });
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-09-h100x4-listing-rental-attempt-02', 'rental-run-03'), { recursive: true });
  for (const item of [
    'rate-010/listing-response-01.json', 'rental-run-03/gpu-result-01.json', 'rate-001/host-read-09.json',
    'rate-001/listing-request-01.json', 'rate-001/listing-response-01.json', 'rate-001/host-read-after-01.json',
    'rate-001/listing-readback-verification-01.json', 'offer-search-request-01.json', 'offer-search-response-01.json',
    'rental-run-03/rental-fresh-offer-01.json', 'rental-run-03/rental-create-request-01.json',
    'rental-run-03/rental-create-response-01.json', 'rental-run-03/instance-read-03.json', 'rental-run-03/cleanup-main.json',
  ]) await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-09-h100x4-listing-rental-attempt-02', item),
    path.join(root, 'verification', 'evidence', '2026-09-09-h100x4-listing-rental-attempt-02', item),
  );
  await fs.mkdir(path.join(root, 'verification', 'evidence', '2026-09-09-h100x4-direct-install-attempt-02'), { recursive: true });
  for (const item of ['preflight-01.json', 'install-execution-01.json', 'postcheck-02.json', 'machine-readback-02.json', 'installer-findings-01.json', 'settled-01.json', 'image-retest-01.json']) await fs.copyFile(
    path.join(ROOT, 'verification', 'evidence', '2026-09-09-h100x4-direct-install-attempt-02', item),
    path.join(root, 'verification', 'evidence', '2026-09-09-h100x4-direct-install-attempt-02', item),
  );
  const packageData = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  const historicalArtifacts = new Set(packageData.pages.flatMap((page) => page.claims)
    .flatMap((claim) => claim.evidence_refs)
    .map((ref) => ref.artifact_ref)
    .filter((ref) => ref.startsWith('verification/evidence/')));
  for (const artifact of historicalArtifacts) {
    const source = path.join(ROOT, artifact);
    const destination = path.join(root, artifact);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.copyFile(source, destination);
  }
  await fs.copyFile(path.join(ROOT, 'review-server.mjs'), path.join(root, 'review-server.mjs'));
  return root;
}

async function startContextServer(root) {
  const port = await freePort();
  const child = spawn(process.execPath, ['review-server.mjs', '--port', String(port), '--target', targetOrigin,
    '--dir', path.join(root, 'feedback')], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
  let output = '';
  child.stdout.on('data', (chunk) => { output += chunk; });
  child.stderr.on('data', (chunk) => { output += chunk; });
  async function context(route) {
    // A valid current package performs integrity checks over every retained
    // source/evidence reference before the server starts listening.
    for (let attempt = 0; attempt < 600; attempt += 1) {
      if (child.exitCode !== null || child.signalCode !== null) {
        throw new Error(`review server exited early (${child.exitCode ?? child.signalCode})\n${output}`);
      }
      try {
        const response = await fetch(`http://127.0.0.1:${port}/__review__/api/context?path=${encodeURIComponent(route)}`);
        if (response.ok) return await response.json();
      } catch { /* server is still starting */ }
      await new Promise((resolve) => setTimeout(resolve, 25));
    }
    throw new Error(`review server did not start\n${output}`);
  }
  return {
    origin: `http://127.0.0.1:${port}`,
    context,
    async stop() {
    if (child.exitCode == null) child.kill('SIGTERM');
    await new Promise((resolve) => child.exitCode == null ? child.once('exit', resolve) : resolve());
    },
  };
}

async function contextFrom(root, route) {
  const server = await startContextServer(root);
  try { return await server.context(route); } finally { await server.stop(); }
}

async function withFixture(mutator, route, assertion) {
  const root = await fixtureRoot();
  try {
    await mutator(root);
    await assertion(await contextFrom(root, route));
  } finally {
    await fs.rm(fixtureContainer(root), { recursive: true, force: true });
  }
}

before(async () => {
  await fs.access(PACKAGE);
  target = http.createServer((req, res) => res.end(`<!doctype html><main>${req.url}</main>`));
  targetOrigin = `http://127.0.0.1:${await listen(target)}`;
});

after(async () => {
  if (target) await new Promise((resolve) => target.close(resolve));
});

test('current package supplies a current record for every one of the 44 Host routes', async () => {
  const packageData = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  assert.equal(packageData.pages.length, 44);
  const root = await fixtureRoot();
  try {
    const server = await startContextServer(root);
    try {
      for (const page of packageData.pages) {
        const context = await server.context(page.route);
      assert.equal(context.currentReview.available, true, page.route);
      assert.equal(context.currentReview.page.route, page.route);
      assert.equal(context.currentReview.page.sourceFile, page.source_file);
      }
      const refs = new Set(packageData.pages.flatMap((page) => page.claims)
        .flatMap((claim) => claim.evidence_refs).map((ref) => ref.artifact_ref));
      for (const ref of refs) {
        const response = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(ref)}`);
        assert.equal(response.status, 200, ref);
      }
      const page = packageData.pages.find((page) => page.claims.some((claim) => claim.evidence_refs.length));
      const claim = page.claims.find((claim) => claim.evidence_refs.length);
      const ref = claim.evidence_refs[0].artifact_ref;
      const contextual = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(ref)}&page=${encodeURIComponent(page.route)}&claim=${encodeURIComponent(claim.id)}`);
      assert.equal(contextual.status, 200);
      const html = await contextual.text();
      assert.ok(html.includes('Back to the documentation page'));
      assert.ok(html.includes('not evidence for itself'));
      const unrelated = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(ref)}&page=${encodeURIComponent(page.route)}&claim=not-attached`);
      assert.equal(unrelated.status, 404);
    } finally { await server.stop(); }
  } finally { await fs.rm(fixtureContainer(root), { recursive: true, force: true }); }
});

test('only the exact introductory product description receives publication-only PASS with clickable public sources', async () => {
  const root = await fixtureRoot();
  try {
    const server = await startContextServer(root);
    try {
      const context = await server.context('/host/hosting-overview');
      assert.equal(context.currentReview.available, true);
      const claim = context.currentReview.page.claims.find((item) => item.id === 'MCL-e12ac9f6be2ce502');
      assert.equal(claim.status, 'PASS');
      assert.equal(claim.classification, 'PRODUCT_DESCRIPTION');
      assert.deepEqual(claim.requiredEvidenceTypes, ['PRODUCT_PUBLICATION_SOURCE']);
      assert.equal(claim.history.carryDecision, 'CURRENT_PRODUCT_PUBLICATION_ADJUDICATION');
      assert.equal(claim.sourceRefs.length, 3);
      assert.equal(claim.evidenceRefs.length, 2);
      for (const ref of claim.evidenceRefs) {
        assert.match(ref.limit, /Not runtime observation/);
        const response = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(ref.artifactRef)}&page=/host/hosting-overview&claim=${claim.id}`);
        assert.equal(response.status, 200);
      }
      const source = await fs.readFile(path.join(ROOT, 'review-server.mjs'), 'utf8');
      const renderer = source.slice(source.indexOf('  function currentSourceLinks(refs) {'), source.indexOf('  function currentEvidenceRefs('));
      const html = vm.runInNewContext(renderer + '\ncurrentSourceLinks(refs)', {
        refs: claim.sourceRefs, esc: (value) => String(value).replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;'),
      });
      for (const ref of claim.sourceRefs) assert.ok(html.includes(`href="${ref.path}"`), ref.path);
      assert.match(html, /live page may change; retained excerpt is the citation/);
      assert.equal(vm.runInNewContext(renderer + '\ncurrentSourceLinks(refs)', {
        refs: [{ ...claim.sourceRefs[0], path: 'https://vast.ai.evil.example/hosting' }], esc: String,
      }), '');
    } finally { await server.stop(); }
  } finally { await fs.rm(fixtureContainer(root), { recursive: true, force: true }); }
});

test('product publication correction fails closed on artifact drift and exact claim/source/history substitution', async () => {
  for (const artifact of [
    'verification/current-host-product-publications.json',
    'verification/evidence/2026-09-08-host-live-readonly-attempt-01/product-source-capture-02.json',
  ]) {
    await withFixture(async (root) => fs.appendFile(path.join(root, artifact), '\n'), '/host/hosting-overview',
      async (context) => assert.equal(context.currentReview.available, false, artifact));
  }
  const mutations = [
    (claim) => { claim.id = 'MCL-unrelated-product-claim'; },
    (claim) => { claim.source_refs[0].path = 'https://docs.vast.ai/host/hosting-overview'; },
    (claim) => { claim.source_refs[0].path = 'https://vast.ai.evil.example/hosting'; },
    (claim) => { claim.required_evidence_types = ['RUNTIME_OR_UI_OBSERVATION']; },
    (claim) => { claim.required_evidence_types.push('ACCOUNTABLE_OWNER_CONFIRMATION'); },
    (claim) => { claim.source_refs.pop(); },
    (claim) => { claim.source_refs[1] = structuredClone(claim.source_refs[0]); },
    (claim) => { claim.history.reason = 'Runtime execution established.'; },
    (claim) => { claim.evidence_refs[0].limit = 'Specific rental verified.'; },
    (claim) => { claim.text += ' Specific rental execution is verified.'; },
  ];
  for (const mutate of mutations) {
    await withFixture(async (root) => {
      const file = path.join(root, 'verification/current-host-docs-review.json');
      const data = JSON.parse(await fs.readFile(file, 'utf8'));
      const claim = data.pages.find((page) => page.route === '/host/hosting-overview').claims
        .find((item) => item.id === 'MCL-e12ac9f6be2ce502');
      mutate(claim);
      await fs.writeFile(file, JSON.stringify(data));
    }, '/host/hosting-overview', async (context) => assert.equal(context.currentReview.available, false));
  }
  await withFixture(async (root) => {
    const file = path.join(root, 'verification/current-host-docs-review.json');
    const data = JSON.parse(await fs.readFile(file, 'utf8'));
    data.support_layers[0].evidence_refs[0].artifact_ref = 'verification/current-host-product-publications.json';
    await fs.writeFile(file, JSON.stringify(data));
  }, '/host/hosting-overview', async (context) => assert.equal(context.currentReview.available, false));
});

test('three registry-approved Market Metrics endpoint descriptions retain narrow direct API PASS', async () => {
  await withFixture(async () => {}, '/host/market-metrics', async (context) => {
    const expected = new Map([
      ['CUR-a5b27de02fca3c9a', '/api/v0/metrics/gpu/current/'],
      ['CUR-6c8062ab1c766957', '/api/v0/metrics/gpu/history/'],
      ['CUR-2de1188bec6c9f72', '/api/v0/metrics/gpu/locations/'],
    ]);
    for (const [id, endpoint] of expected) {
      const claim = context.currentReview.page.claims.find((item) => item.id === id);
      assert.equal(claim.status, 'PASS');
      assert.equal(claim.history.carryDecision, 'CURRENT_LIVE_ENDPOINT_ADJUDICATION');
      assert.deepEqual(claim.requiredEvidenceTypes, ['CANONICAL_IMPLEMENTATION_SOURCE', 'RUNTIME_OR_UI_OBSERVATION']);
      assert.match(claim.text, new RegExp(endpoint.replaceAll('/', '\\/')));
      assert.equal(claim.evidenceRefs.length, 1);
      assert.equal(claim.evidenceRefs[0].role, 'CURRENT_LIVE_ENDPOINT_ADJUDICATION');
      assert.match(claim.evidenceRefs[0].limit, /does not prove/i);
    }
  });
});

test('ten exact retained readonly command claims pass, while the normal support-bundle command remains concretely blocked', async () => {
  await withFixture(async () => {}, '/host/market-metrics', async (context) => {
    assert.equal(context.currentReview.available, true, context.currentReview.unavailableReason);
    const expected = new Set(['CUR-142629d88fb18726', 'CUR-705da5057d7f3360', 'CUR-2c04f5e4d6ef0b20']);
    for (const claim of context.currentReview.page.claims.filter((item) => expected.has(item.id))) {
      assert.equal(claim.status, 'PASS');
      assert.equal(claim.history.carryDecision, 'CURRENT_HOST_READONLY_COMMAND_ADJUDICATION');
      assert.equal(claim.evidenceRefs[0].artifactRef, 'verification/current-host-readonly-adjudications.json');
    }
  });
  await withFixture(async () => {}, '/host/how-to-self-test', async (context) => {
    const claim = context.currentReview.page.claims.find((item) => item.id === 'MCL-eeaf6da83da9eca7');
    assert.equal(claim.status, 'BLOCKED');
    assert.match(claim.rationale, /preflight_requirements/);
    assert.match(claim.rationale, /0\.8506588/);
    assert.match(claim.rationale, /221\.1 Mb\/s/);
    assert.match(claim.nextAction, /new approved idle rental/i);
    assert.equal(claim.history.carryDecision, 'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION');
  });
});

test('the VM correction remains a historical FAIL transition while the search replacement retains that history beside its new bounded PASS', async () => {
  await withFixture(async () => {}, '/host/vms', async (context) => {
    const replacement = context.currentReview.page.claims.find((item) => item.id === 'COR-02-MCL-dfebca7edafe9c59-REPLACEMENT');
    assert.equal(replacement.status, 'UNVALIDATED');
    assert.equal(replacement.history.carryDecision, 'TWO_DEFECT_REPLACEMENT_UNVALIDATED');
    assert.equal(replacement.sourceTransition.oldFailClaim.id, 'MCL-dfebca7edafe9c59');
    assert.equal(replacement.sourceTransition.oldFailClaim.status, 'FAIL');
  });
  await withFixture(async () => {}, '/host/first-24-hours', async (context) => {
    const replacement = context.currentReview.page.claims.find((item) => item.id === 'COR-01-MCL-323c8fb8180f5f62-REPLACEMENT');
    assert.equal(replacement.status, 'PASS');
    assert.equal(replacement.history.carryDecision, 'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION');
    assert.equal(replacement.sourceTransition, null);
    assert.deepEqual(replacement.evidenceRefs.slice(0, 3).map((ref) => ref.id), [
      'CLI-QUERY-SOURCE-INSPECTION-01', 'CLI-QUERY-SEMANTIC-RETEST-01', 'COR-01-MCL-323c8fb8180f5f62-REPLACEMENT',
    ]);
    assert.ok(replacement.evidenceRefs.some((ref) => ref.id === 'CONNECTION-COR-01-MCL-323c8fb8180f5f62-REPLACEMENT-01'));
  });
});

test('six hash-pinned connection rows expose only their bounded outcomes and direct evidence', async () => {
  const model = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  assert.deepEqual(model.counts.claim_statuses, { BLOCKED: 23, FAIL: 151, NOT_APPLICABLE: 4, PASS: 204, UNVALIDATED: 1631 });
  await withFixture(async () => {}, '/host/first-24-hours', async (context) => {
    const expected = new Map([
      ['COR-01-MCL-323c8fb8180f5f62-REPLACEMENT', 'PASS'], ['MCL-4c49eaf437cfa29e', 'PASS'],
      ['MCL-1ebb3e6e2b370757', 'BLOCKED'], ['MCL-3fb43d8a410371df', 'UNVALIDATED'],
      ['MCL-da591d84b7d08317', 'UNVALIDATED'],
    ]);
    for (const [id, status] of expected) {
      const claim = context.currentReview.page.claims.find((item) => item.id === id);
      assert.equal(claim.status, status); assert.equal(claim.history.carryDecision, 'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION');
      assert.ok(claim.evidenceRefs.some((ref) => ref.artifactRef === 'verification/current-host-connection-adjudications.json'));
    }
    for (const id of ['MCL-4c49eaf437cfa29e', 'MCL-1ebb3e6e2b370757', 'MCL-3fb43d8a410371df']) {
      const claim = context.currentReview.page.claims.find((item) => item.id === id);
      assert.deepEqual(claim.requiredEvidenceTypes, ['RUNTIME_OR_UI_OBSERVATION']);
      assert.equal(claim.ownerRole, 'Authorized client/browser/network operator');
    }
  });
  await withFixture(async () => {}, '/host/how-to-self-test', async (context) => {
    const claim = context.currentReview.page.claims.find((item) => item.id === 'MCL-eeaf6da83da9eca7');
    assert.equal(claim.status, 'BLOCKED');
    assert.equal(claim.history.carryDecision, 'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION');
    assert.equal(claim.sourcePassages[0].start, 84);
    assert.match(claim.text, /--support-bundle-dir/);
  });
});

test('connection registry, bound artifact, and projected status tampering fail closed', async () => {
  await withFixture(async (root) => fs.appendFile(path.join(root, 'verification/current-host-connection-adjudications.json'), '\n'),
    '/host/first-24-hours', async (context) => assert.equal(context.currentReview.available, false));
  await withFixture(async (root) => fs.appendFile(path.join(root, 'verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/direct-ssh-01.json'), '\n'),
    '/host/first-24-hours', async (context) => assert.equal(context.currentReview.available, false));
  await withFixture(async (root) => {
    const file = path.join(root, 'verification/current-host-docs-review.json'); const data = JSON.parse(await fs.readFile(file, 'utf8'));
    const claim = data.pages.find((page) => page.route === '/host/first-24-hours').claims.find((item) => item.id === 'MCL-4c49eaf437cfa29e');
    claim.status = 'UNVALIDATED'; data.counts.claim_statuses.PASS -= 1; data.counts.claim_statuses.UNVALIDATED += 1;
    await fs.writeFile(file, JSON.stringify(data));
  }, '/host/first-24-hours', async (context) => assert.equal(context.currentReview.available, false));
});

test('authority transition admits only its exact agreement atoms and keeps partial citations failed', async () => {
  await withFixture(async () => {}, '/host/hosting-agreement', async (context) => {
    assert.equal(context.currentReview.available, true, context.currentReview.unavailableReason);
    const atom = context.currentReview.page.claims.find((claim) => claim.id === 'AUTH-DATA-SECURITY-01');
    const data = context.currentReview.page.claims.find((claim) => claim.id === 'MCL-f855ff5e92cfbec1');
    assert.equal(atom.status, 'PASS');
    assert.equal(data.status, 'PASS');
    assert.equal(atom.sourceRefs[0].locator, 'INTELLECTUAL PROPERTY AND DATA SECURITY');
  });
  await withFixture(async () => {}, '/host/workload-policy', async (context) => {
    const partial = context.currentReview.page.claims.find((claim) => claim.id === 'MCL-8fe2020c0e7efe26');
    assert.equal(partial.status, 'FAIL');
    assert.deepEqual(partial.requiredEvidenceTypes, [
      'RUNTIME_OR_UI_OBSERVATION', 'ACCOUNTABLE_OWNER_CONFIRMATION', 'AUTHORITATIVE_DOCUMENTATION_CITATION',
    ]);
  });
});

test('authority predecessor proof opens with exact current context and rejects unbound claims', async () => {
  const root = await fixtureRoot();
  try {
    const server = await startContextServer(root);
    try {
      const context = await server.context('/host/hosting-overview');
      assert.equal(context.currentReview.available, true);
      const ref = 'verification/evidence/2026-09-09-host-authority-correction-attempt-01/pre-authority-current-host-docs-review.json';
      const url = new URL('/__review__/current-artifact', server.origin);
      for (const [key, value] of Object.entries({ref, page: '/host/hosting-overview', claim: 'MCL-508003945b6ef934'})) url.searchParams.set(key, value);
      const response = await fetch(url);
      assert.equal(response.status, 200);
      const html = await response.text();
      assert.match(html, /<blockquote>- Minimum GPU count \(`min_chunk`\)\.<\/blockquote>/);
      assert.match(html, /Frozen predecessor wording and status only/);
      assert.match(html, /Minimum GPU size/);
      url.searchParams.set('claim', 'NOT-AN-AUTHORITY-CLAIM');
      assert.equal((await fetch(url)).status, 404);
      url.searchParams.set('page', '/host/workload-policy');
      url.searchParams.set('claim', 'MCL-508003945b6ef934');
      assert.equal((await fetch(url)).status, 404);
    } finally { await server.stop(); }
  } finally { await fs.rm(fixtureContainer(root), {recursive: true, force: true}); }
});

test('authority registry and jointly altered captured agreement fail closed', async () => {
  await withFixture(async (root) => {
    const registryPath = path.join(root, 'verification/current-host-authority-adjudications.json');
    const registry = JSON.parse(await fs.readFile(registryPath, 'utf8'));
    const agreement = registry.artifacts.find((artifact) => artifact.id === 'agreement');
    const agreementPath = path.join(root, agreement.path);
    const capture = JSON.parse(await fs.readFile(agreementPath, 'utf8'));
    capture.sections[0].text_sha256 = '0'.repeat(64);
    const captureBytes = Buffer.from(JSON.stringify(capture));
    agreement.sha256 = crypto.createHash('sha256').update(captureBytes).digest('hex');
    await fs.writeFile(agreementPath, captureBytes);
    await fs.writeFile(registryPath, JSON.stringify(registry));
  }, '/host/hosting-agreement', async (context) => assert.equal(context.currentReview.available, false));
});

test('authority post-claim literal and agreement heading substitutions fail closed', async () => {
  await withFixture(async (root) => {
    const modelPath = path.join(root, 'verification/current-host-docs-review.json');
    const model = JSON.parse(await fs.readFile(modelPath, 'utf8'));
    const claim = model.pages.find((page) => page.route === '/host/hosting-agreement').claims
      .find((item) => item.id === 'AUTH-DATA-SECURITY-01');
    claim.text = claim.text.replace('reasonable safeguards', 'absolute safeguards');
    await fs.writeFile(modelPath, JSON.stringify(model));
  }, '/host/hosting-agreement', async (context) => assert.equal(context.currentReview.available, false));
  await withFixture(async (root) => {
    const modelPath = path.join(root, 'verification/current-host-docs-review.json');
    const model = JSON.parse(await fs.readFile(modelPath, 'utf8'));
    const claim = model.pages.find((page) => page.route === '/host/hosting-agreement').claims
      .find((item) => item.id === 'MCL-f855ff5e92cfbec1');
    claim.source_refs[0].locator = 'PERFORMANCE OF SERVICES';
    await fs.writeFile(modelPath, JSON.stringify(model));
  }, '/host/hosting-agreement', async (context) => assert.equal(context.currentReview.available, false));
});

test('current citation-lane FAIL records are counted independently of the legacy verification reader', async () => {
  await withFixture(async () => {}, '/host/guide-to-taxes', async (context) => {
    assert.equal(context.currentReview.available, true, context.currentReview.unavailableReason);
    assert.equal(context.currentReview.citationDefects.total, 149 - 4 + 6);
    const citation = context.currentReview.page.claims.filter((claim) => claim.status === 'FAIL' &&
      claim.requiredEvidenceTypes.includes('AUTHORITATIVE_DOCUMENTATION_CITATION'));
    assert.equal(citation.length, context.currentReview.citationDefects.page);
    assert.ok(citation.every((claim) => claim.ownerRole));
    assert.ok(citation.some((claim) => !claim.rationale.startsWith('CONFIRMED_CITATION_DEFECT:')));
    const source = await fs.readFile(path.join(ROOT, 'review-server.mjs'), 'utf8');
    assert.match(source, /current-citation-filter/);
    assert.match(source, /Missing authoritative citation on this page/);
    assert.match(source, /Current Host review:[\s\S]*missing authoritative citations across Host pages/);
    assert.match(source, /Obtain the authoritative source for this wording from the recorded owner, add its citation, and retain a source\/link retest\./);
  });
});

test('the two-defect transition remains exact beneath connection and authority projections', async () => {
  await withFixture(async () => {}, '/host/first-24-hours', async (context) => {
    assert.equal(context.currentReview.available, true, context.currentReview.unavailableReason);
    assert.equal(context.currentReview.citationDefects.total, 151);
    const replacement = context.currentReview.page.claims.find((claim) => claim.id === 'COR-01-MCL-323c8fb8180f5f62-REPLACEMENT');
    assert.equal(replacement.status, 'PASS');
    assert.equal(replacement.history.carryDecision, 'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION');
    assert.equal(replacement.sourceTransition, null);
    assert.deepEqual(replacement.evidenceRefs.slice(0, 3).map((ref) => ref.id), [
      'CLI-QUERY-SOURCE-INSPECTION-01', 'CLI-QUERY-SEMANTIC-RETEST-01', 'COR-01-MCL-323c8fb8180f5f62-REPLACEMENT',
    ]);
    assert.ok(replacement.evidenceRefs.some((ref) => ref.id === 'CONNECTION-COR-01-MCL-323c8fb8180f5f62-REPLACEMENT-01'));
    assert.deepEqual(context.currentReview.page.claims.filter((claim) => [
      'MCL-fabfbad844e625b4', 'MCL-7d10fc61bf9a884b', 'MCL-92edb99129fc96c9', 'MCL-da591d84b7d08317',
    ].includes(claim.id)).map((claim) => [claim.id, claim.status, claim.history.carryDecision]), [
      ['MCL-fabfbad844e625b4', 'PASS', 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL'],
      ['MCL-7d10fc61bf9a884b', 'PASS', 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL'],
      ['MCL-92edb99129fc96c9', 'PASS', 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL'],
      ['MCL-da591d84b7d08317', 'UNVALIDATED', 'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION'],
    ]);
    assert.deepEqual(context.currentReview.page.claims.filter((claim) => [
      'MCL-e0ca872617263ab3', 'MCL-c967f75958c7276a', 'MCL-a82451cb4f2ee66e',
    ].includes(claim.id)).map((claim) => [claim.id, claim.status, claim.history.carryDecision]), [
      ['MCL-e0ca872617263ab3', 'PASS', 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL'],
      ['MCL-c967f75958c7276a', 'PASS', 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL'],
      ['MCL-a82451cb4f2ee66e', 'PASS', 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL'],
    ]);
  });
  await withFixture(async () => {}, '/host/vms', async (context) => {
    const replacement = context.currentReview.page.claims.find((claim) => claim.id === 'COR-02-MCL-dfebca7edafe9c59-REPLACEMENT');
    assert.equal(replacement.status, 'UNVALIDATED');
    assert.equal(replacement.sourceTransition.oldFailClaim.id, 'MCL-dfebca7edafe9c59');
    assert.equal(replacement.sourceTransition.oldFailClaim.status, 'FAIL');
    assert.deepEqual(replacement.evidenceRefs.map((ref) => ref.id), [
      'VM-HELPER-SOURCE-RETEST-02', 'VM-STATUS-01', 'COR-02-MCL-dfebca7edafe9c59-REPLACEMENT',
    ]);
  });
  await withFixture(async (root) => fs.appendFile(path.join(root, 'verification', 'current-two-defect-transition.json'), '\n'),
    '/host/first-24-hours', async (context) => assert.equal(context.currentReview.available, false));
  await withFixture(async (root) => {
    const file = path.join(root, 'verification', 'current-host-docs-review.json');
    const model = JSON.parse(await fs.readFile(file, 'utf8'));
    const claim = model.pages.find((page) => page.route === '/host/first-24-hours').claims.find((item) => item.id === 'MCL-cce90286b53e70ad');
    claim.history.carry_decision = 'TWO_DEFECT_REPLACEMENT_UNVALIDATED';
    await fs.writeFile(file, JSON.stringify(model, null, 2) + '\n');
  }, '/host/first-24-hours', async (context) => assert.equal(context.currentReview.available, false));
  for (const [route, id, mutate] of [
    ['/host/vms', 'MCL-53020aef5be19505', (claim) => { claim.status = 'UNVALIDATED'; }],
    ['/host/first-24-hours', 'MCL-e0ca872617263ab3', (claim) => { claim.evidence_refs = []; }],
    ['/host/first-24-hours', 'MCL-c967f75958c7276a', (claim) => { claim.text += ' drift'; }],
    ['/host/first-24-hours', 'MCL-a82451cb4f2ee66e', (claim) => { claim.history.reason += ' drift'; }],
    ['/host/first-24-hours', 'MCL-a82451cb4f2ee66e', (claim) => { claim.id = 'MCL-transition-noninventory'; }],
  ]) {
    await withFixture(async (root) => {
      const file = path.join(root, 'verification', 'current-host-docs-review.json');
      const model = JSON.parse(await fs.readFile(file, 'utf8'));
      const claim = model.pages.find((page) => page.route === route).claims.find((item) => item.id === id);
      mutate(claim);
      await fs.writeFile(file, JSON.stringify(model, null, 2) + '\n');
    }, route, async (context) => assert.equal(context.currentReview.available, false));
  }
});

test('the correction panel helper is in the shared overlay scope with a browser-safe transition path', async () => {
  const source = await fs.readFile(path.join(ROOT, 'review-server.mjs'), 'utf8');
  const helperStart = source.indexOf('  function sourceTransitionHtml(transition, page, claim) {');
  const currentReviewStart = source.indexOf('  function currentReviewHtml(currentReview) {');
  const evidenceStart = source.indexOf('  function currentEvidenceRefs(refs, page, claim) {');
  assert.ok(helperStart > 0 && helperStart < evidenceStart && evidenceStart < currentReviewStart);
  const helper = source.slice(helperStart, evidenceStart);
  assert.doesNotMatch(helper, /Original finding|Open frozen|Open bounded authority registry/);
  assert.match(helper, /What the source proves/);
  assert.doesNotMatch(helper, /encodeURIComponent\(TWO_DEFECT_TRANSITION\)/);
  assert.match(source.slice(currentReviewStart), /sourceTransitionHtml\(sourceTransition, page, claim\)/);
  assert.match(source, /var TWO_DEFECT_TRANSITION_ARTIFACT = 'verification\/current-two-defect-transition\.json';/);
});

test('H100 installation intake is display-only, claim-bound, and opens its selected observation', async () => {
  const root = await fixtureRoot();
  try {
    const server = await startContextServer(root);
    try {
      const context = await server.context('/host/installing-host-software');
      assert.equal(context.currentReview.available, true, context.currentReview.unavailableReason);
      const intake = context.currentReview.installationEvidenceIntake;
      assert.equal(intake.available, true);
      assert.match(intake.message, /USD 0\.01\/GB in both directions/i);
      assert.match(intake.message, /instance 50364501/i);
      assert.equal(intake.records.length, 5);
      assert.equal(intake.records.every((item) => item.route === '/host/installing-host-software'), true);
      const baseline = intake.records.find((item) => item.claimId === 'MCL-fd7e8b86c5cfd383');
      const response = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(baseline.checks[0].artifactRef)}&page=/host/installing-host-software&claim=${baseline.claimId}&intake=1`);
      assert.equal(response.status, 200);
      const html = await response.text();
      assert.match(html, /Pre-install finding only/);
      assert.match(html, /Id=vastai\.service/);
      assert.equal(intake.records.every((item) => item.sourceLinks.at(-1).artifactRef === 'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/host-read-09.json'), true);
      const finalReadback = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(baseline.sourceLinks.at(-1).artifactRef)}&page=/host/installing-host-software&claim=${baseline.claimId}`);
      assert.equal(finalReadback.status, 200);
      const unbound = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(baseline.checks[0].artifactRef)}&page=/host/installing-host-software&claim=MCL-1ef8a4aa92b66755&intake=1`);
      assert.equal(unbound.status, 404);
    } finally { await server.stop(); }
  } finally { await fs.rm(fixtureContainer(root), { recursive: true, force: true }); }
});

test('four direct post-install runtime claims open only their selected postcheck observation', async () => {
  const root = await fixtureRoot();
  try {
    const server = await startContextServer(root);
    try {
      const expected = new Map([
        ['MCL-ead93c85c2ff4168', ['POST-03', 'GPU_INVENTORY_4_H100']],
        ['MCL-82fa8860fe3ef124', ['POST-01', 'FOUR_SERVICES_ACTIVE']],
        ['MCL-2f9f572d80e1e8f9', ['POST-05', 'DOCKER_XFS_PROJECT_QUOTA']],
        ['MCL-aa383ba37f55f306', ['POST-07', 'PROJECT_QUOTA_ON']],
      ]);
      const context = await server.context('/host/installing-host-software');
      for (const [claimId, [postcheck, predicate]] of expected) {
        const claim = context.currentReview.page.claims.find((item) => item.id === claimId);
        assert.equal(claim.status, 'PASS');
        const response = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent('verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/postcheck-02.json')}&page=/host/installing-host-software&claim=${claimId}&postcheck=${postcheck}`);
        assert.equal(response.status, 200, claimId);
        const html = await response.text();
        assert.match(html, new RegExp(`Selected runtime observation ${postcheck}`));
        assert.match(html, new RegExp(predicate));
        assert.doesNotMatch(html, /Open runtime adjudication record|Original finding/);
        assert.match(html, /Selected post-install command output/);
      }
      const wrong = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent('verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/postcheck-02.json')}&page=/host/installing-host-software&claim=MCL-ead93c85c2ff4168&postcheck=POST-01`);
      assert.equal(wrong.status, 404);
    } finally { await server.stop(); }
  } finally { await fs.rm(fixtureContainer(root), { recursive: true, force: true }); }
});

test('exact H100 listing-and-rental registry admits only three atomic PASS claims and one partial UNVALIDATED claim', async () => {
  const root = await fixtureRoot();
  try {
    const server = await startContextServer(root);
    try {
      const expected = new Map([
        ['MCL-fabfbad844e625b4', ['PASS', ['LISTING_REQUEST', 'LISTING_RESPONSE', 'LISTING_READBACK', 'LISTING_VERIFICATION', 'OFFER_SEARCH_REQUEST', 'OFFER_SEARCH_RESPONSE']]],
        ['MCL-7d10fc61bf9a884b', ['PASS', ['FRESH_OFFER', 'CREATE_REQUEST', 'CREATE_RESPONSE', 'INSTANCE_READ']]],
        ['MCL-92edb99129fc96c9', ['PASS', ['CREATE_RESPONSE', 'INSTANCE_READ']]],
        ['MCL-da591d84b7d08317', ['UNVALIDATED', ['CREATE_RESPONSE', 'INSTANCE_READ', 'CLEANUP']]],
      ]);
      const registry = JSON.parse(await fs.readFile(path.join(root, 'verification/current-h100x4-rental-adjudications.json'), 'utf8'));
      const paths = new Map(registry.artifacts.map((item) => [item.id, item.path]));
      const transition = JSON.parse(await fs.readFile(path.join(root, 'verification', 'current-two-defect-transition.json'), 'utf8'));
      const connection = JSON.parse(await fs.readFile(path.join(root, 'verification', 'current-host-connection-adjudications.json'), 'utf8'));
      const connectionByClaim = new Map(connection.adjudications.map((entry) => [entry.claim_id, entry]));
      const baseline = JSON.parse(await fs.readFile(path.join(root, transition.baseline.model.path), 'utf8'));
      const baselineClaims = new Map(baseline.pages.flatMap((page) => page.claims).map((claim) => [claim.id, claim]));
      const context = await server.context('/host/first-24-hours');
      assert.equal(context.currentReview.available, true, context.currentReview.unavailableReason);
      for (const [claimId, [status, artifactIds]] of expected) {
        const claim = context.currentReview.page.claims.find((item) => item.id === claimId);
        assert.equal(claim.status, status, claimId);
        const connectionEntry = connectionByClaim.get(claimId);
        assert.equal(claim.history.carryDecision, connectionEntry
          ? 'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION' : 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL');
        assert.equal(baselineClaims.get(claimId).history.carry_decision, status === 'PASS'
          ? 'CURRENT_H100X4_LISTING_RENTAL_RUNTIME_ADJUDICATION'
          : 'CURRENT_H100X4_LISTING_RENTAL_RUNTIME_ADJUDICATION_PARTIAL');
        if (connectionEntry) {
          assert.equal(connectionEntry.previous_claim.history.carry_decision, 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL');
          assert.deepEqual(claim.evidenceRefs.map((item) => item.id), [connectionEntry.id, ...connectionEntry.artifact_ids]);
        } else assert.deepEqual(claim.evidenceRefs.map((item) => item.id), [`H100X4-RENTAL-${claimId}-01`, ...artifactIds]);
        for (const ref of claim.evidenceRefs) {
          const response = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(ref.artifactRef)}&page=/host/first-24-hours&claim=${claimId}`);
          assert.equal(response.status, 200, `${claimId} ${ref.id}`);
        }
      }
      const wrong = await fetch(`${server.origin}/__review__/current-artifact?ref=${encodeURIComponent(paths.get('LISTING_REQUEST'))}&page=/host/first-24-hours&claim=MCL-7d10fc61bf9a884b`);
      assert.equal(wrong.status, 404);
    } finally { await server.stop(); }
  } finally { await fs.rm(fixtureContainer(root), { recursive: true, force: true }); }
});

test('listing-and-rental runtime gate rejects substituted artifacts, registry drift, and a promoted compound occurrence', async () => {
  const mutations = [
    async (root) => fs.appendFile(path.join(root, 'verification/current-h100x4-rental-adjudications.json'), '\n'),
    async (root) => fs.appendFile(path.join(root, 'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-request-01.json'), '\n'),
    async (root) => {
      const file = path.join(root, 'verification/current-host-docs-review.json'); const data = JSON.parse(await fs.readFile(file, 'utf8'));
      data.pages.find((page) => page.route === '/host/first-24-hours').claims.find((claim) => claim.id === 'MCL-fabfbad844e625b4').evidence_refs[1].artifact_ref = 'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/cleanup-main.json';
      await fs.writeFile(file, JSON.stringify(data));
    },
    async (root) => {
      const file = path.join(root, 'verification/current-host-docs-review.json'); const data = JSON.parse(await fs.readFile(file, 'utf8'));
      const claim = data.pages.find((page) => page.route === '/host/first-24-hours').claims.find((item) => item.id === 'MCL-da591d84b7d08317');
      claim.status = 'PASS'; claim.history.carry_decision = 'CURRENT_H100X4_LISTING_RENTAL_RUNTIME_ADJUDICATION';
      data.counts.claim_statuses.UNVALIDATED -= 1; data.counts.claim_statuses.PASS += 1;
      await fs.writeFile(file, JSON.stringify(data));
    },
  ];
  for (const mutate of mutations) await withFixture(mutate, '/host/first-24-hours', async (context) => assert.equal(context.currentReview.available, false));
});

test('missing or malformed H100 intake hides only the intake and preserves current review', async () => {
  for (const mutate of [
    async (root) => fs.rm(path.join(root, 'verification', 'current-host-install-evidence-intake.json')),
    async (root) => fs.writeFile(path.join(root, 'verification', 'current-host-install-evidence-intake.json'), '{'),
  ]) await withFixture(mutate, '/host/installing-host-software', async (context) => {
    assert.equal(context.currentReview.available, true);
    assert.equal(context.currentReview.installationEvidenceIntake.available, false);
  });
});

test('readonly command adjudication fails closed on capture, argv, command text, lane, and borrowed source drift', async () => {
  const mutations = [
    async (root) => fs.appendFile(path.join(root, 'verification/evidence/2026-09-08-host-live-readonly-attempt-01/batch-d-cli-execution-01.json'), '\n'),
    async (root) => { const f = path.join(root, 'verification/current-host-readonly-adjudications.json'); const d = JSON.parse(await fs.readFile(f)); d.adjudications[0].checks[0].argv = ['metrics', 'wrong']; await fs.writeFile(f, JSON.stringify(d)); },
    async (root) => { const f = path.join(root, 'verification/current-host-readonly-adjudications.json'); const d = JSON.parse(await fs.readFile(f)); d.adjudications[0].checks.pop(); await fs.writeFile(f, JSON.stringify(d)); },
    async (root) => { const f = path.join(root, 'verification/current-host-readonly-adjudications.json'); const d = JSON.parse(await fs.readFile(f)); d.adjudications[0].checks[0].required_output = {}; await fs.writeFile(f, JSON.stringify(d)); },
    async (root) => { const f = path.join(root, 'verification/current-host-readonly-adjudications.json'); const d = JSON.parse(await fs.readFile(f)); d.adjudications[0].checks[0].required_output = {exit_code: 0}; await fs.writeFile(f, JSON.stringify(d)); },
    async (root) => { const f = path.join(root, 'verification/current-host-docs-review.json'); const d = JSON.parse(await fs.readFile(f)); d.pages.find((p) => p.route === '/host/market-metrics').claims.find((c) => c.id === 'CUR-142629d88fb18726').text = 'different'; await fs.writeFile(f, JSON.stringify(d)); },
    async (root) => { const f = path.join(root, 'verification/current-host-docs-review.json'); const d = JSON.parse(await fs.readFile(f)); d.pages.find((p) => p.route === '/host/market-metrics').claims.find((c) => c.id === 'CUR-142629d88fb18726').required_evidence_types.push('ACCOUNTABLE_OWNER_CONFIRMATION'); await fs.writeFile(f, JSON.stringify(d)); },
    async (root) => { const f = path.join(root, 'verification/current-host-readonly-adjudications.json'); const d = JSON.parse(await fs.readFile(f)); d.adjudications[0].source_binding[0].path = 'host/market-metrics.mdx'; await fs.writeFile(f, JSON.stringify(d)); },
  ];
  for (const mutate of mutations) await withFixture(mutate, '/host/market-metrics', async (context) => assert.equal(context.currentReview.available, false));
});

test('live endpoint PASS fails closed when its retained response shape or independent source binding changes', async () => {
  await withFixture(async (root) => {
    const evidence = path.join(root, 'verification/evidence/2026-09-08-host-live-readonly-attempt-01/market-api-01.json');
    const data = JSON.parse(await fs.readFile(evidence, 'utf8'));
    data.requests[0].shape_ok = false;
    await fs.writeFile(evidence, JSON.stringify(data));
  }, '/host/market-metrics', async (context) => assert.equal(context.currentReview.available, false));
  await withFixture(async (root) => {
    const file = path.join(root, 'verification/current-host-docs-review.json');
    const data = JSON.parse(await fs.readFile(file, 'utf8'));
    const claim = data.pages.find((page) => page.route === '/host/market-metrics').claims
      .find((item) => item.id === 'CUR-a5b27de02fca3c9a');
    claim.source_refs[1].path = 'host/market-metrics.mdx';
    await fs.writeFile(file, JSON.stringify(data));
  }, '/host/market-metrics', async (context) => assert.equal(context.currentReview.available, false));
  await withFixture(async (root) => {
    const evidence = path.join(root, 'verification/evidence/2026-09-08-host-live-readonly-attempt-01/market-api-01.json');
    const data = JSON.parse(await fs.readFile(evidence, 'utf8'));
    data.requests[0].url += '?unapproved-filter=1';
    const bytes = Buffer.from(JSON.stringify(data));
    await fs.writeFile(evidence, bytes);
    const registry = path.join(root, 'verification/current-host-live-adjudications.json');
    const input = JSON.parse(await fs.readFile(registry, 'utf8'));
    input.artifact.sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
    await fs.writeFile(registry, JSON.stringify(input));
  }, '/host/market-metrics', async (context) => assert.equal(context.currentReview.available, false));
});

test('a changed source refuses current review status instead of falling back to historical evidence', async () => {
  const packageData = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  const page = packageData.pages[0];
  const root = await fixtureRoot();
  try {
    const server = await startContextServer(root);
    try {
      assert.equal((await server.context(page.route)).currentReview.available, true);
      await fs.appendFile(path.join(root, page.source_file), '\n<!-- stale fixture -->\n');
      const context = await server.context(page.route);
      assert.equal(context.currentReview.available, false);
      assert.match(context.currentReview.unavailableReason, /changed|regenerate/i);
    } finally { await server.stop(); }
  } finally { await fs.rm(fixtureContainer(root), { recursive: true, force: true }); }
});

test('an unsafe current source path is rejected without reading it', async () => {
  const packageData = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  const page = packageData.pages[0];
  await withFixture(async (root) => {
    const file = path.join(root, 'verification', 'current-host-docs-review.json');
    const data = JSON.parse(await fs.readFile(file, 'utf8'));
    data.source.source_manifest[0].path = '../review-server.mjs';
    await fs.writeFile(file, JSON.stringify(data));
  }, page.route, async (context) => {
    assert.equal(context.currentReview.available, false);
    assert.match(context.currentReview.unavailableReason, /invalid/i);
  });
});

test('the current volume review binds Command Map and Related Pages together', async () => {
  await withFixture(async () => {}, '/host/volume-offers', async (context) => {
    const claim = context.currentReview.page.claims.find((item) => item.id === 'VOL-C35');
    assert.ok(claim);
    assert.deepEqual(claim.headings, ['Command Map', 'Related Pages']);
    assert.deepEqual(claim.spans.map((span) => [span.start, span.end]), [[101, 109], [111, 118]]);
  });
});

test('a new current Host page remains a current record without historical carry-forward', async () => {
  const packageData = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  const page = packageData.pages.find((item) => item.coverage_state === 'NEW');
  assert.ok(page, 'package must contain the new-page coverage case');
  await withFixture(async () => {}, page.route, async (context) => {
    assert.equal(context.currentReview.available, true);
    assert.equal(context.currentReview.page.coverageState, 'NEW');
    for (const claim of context.currentReview.page.claims) {
      assert.equal(claim.history.baselineClaimId, null);
      assert.equal(claim.history.carryDecision, 'NOT_CARRIED_NEW');
    }
  });
});

test('a runtime claim cannot be promoted by a synthetic static link check', async () => {
  const packageData = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  const page = packageData.pages.find((item) => item.claims.some((claim) =>
    claim.required_evidence_types.includes('RUNTIME_OR_UI_OBSERVATION') &&
    claim.history.carry_decision !== 'CARRIED_FORWARD_EXACT_SOURCE'));
  assert.ok(page);
  await withFixture(async (root) => {
    const file = path.join(root, 'verification', 'current-host-docs-review.json');
    const data = JSON.parse(await fs.readFile(file, 'utf8'));
    const claim = data.pages.find((item) => item.route === page.route).claims.find((item) =>
      item.required_evidence_types.includes('RUNTIME_OR_UI_OBSERVATION') &&
      item.history.carry_decision !== 'CARRIED_FORWARD_EXACT_SOURCE');
    const originalStatus = claim.status;
    claim.status = 'PASS';
    claim.evidence_refs = [{ id: 'EV-CURRENT-LOCAL-NAVIGATION-01', role: 'CURRENT_STATIC_RETEST',
      limit: 'Synthetic link check.', artifact_ref: 'verification/evidence/2026-09-07-host-current-vv-attempt-01/current-static-checks.json' }];
    data.counts.claim_statuses[originalStatus] -= 1;
    data.counts.claim_statuses.PASS = (data.counts.claim_statuses.PASS || 0) + 1;
    if (data.counts.claim_statuses[originalStatus] === 0) delete data.counts.claim_statuses[originalStatus];
    await fs.writeFile(file, JSON.stringify(data));
  }, page.route, async (context) => assert.equal(context.currentReview.available, false));
});

test('an exact historical carry cannot name an arbitrary baseline claim', async () => {
  const packageData = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  const page = packageData.pages.find((item) => item.claims.some((claim) =>
    claim.coverage_state === 'UNCHANGED_EXACT' && claim.history.carry_decision === 'CARRIED_FORWARD_EXACT_SOURCE'));
  assert.ok(page);
  await withFixture(async (root) => {
    const file = path.join(root, 'verification', 'current-host-docs-review.json');
    const data = JSON.parse(await fs.readFile(file, 'utf8'));
    const claim = data.pages.find((item) => item.route === page.route).claims.find((item) =>
      item.coverage_state === 'UNCHANGED_EXACT' && item.history.carry_decision === 'CARRIED_FORWARD_EXACT_SOURCE');
    claim.history.baseline_claim_id = 'MCL-arbitrary-baseline';
    await fs.writeFile(file, JSON.stringify(data));
  }, page.route, async (context) => assert.equal(context.currentReview.available, false));
});

test('an unchanged unvalidated claim cannot silently acquire historical PASS', async () => {
  const data = JSON.parse(await fs.readFile(PACKAGE, 'utf8'));
  const page = data.pages.find((page) => page.claims.some((claim) => claim.status === 'UNVALIDATED' &&
    claim.history.carry_decision === 'CARRIED_FORWARD_EXACT_SOURCE'));
  await withFixture(async (root) => {
    const file = path.join(root, 'verification/current-host-docs-review.json');
    const altered = JSON.parse(await fs.readFile(file, 'utf8'));
    const claim = altered.pages.find((item) => item.route === page.route).claims.find((item) =>
      item.status === 'UNVALIDATED' && item.history.carry_decision === 'CARRIED_FORWARD_EXACT_SOURCE');
    claim.status = 'PASS';
    altered.counts.claim_statuses.UNVALIDATED -= 1;
    altered.counts.claim_statuses.PASS += 1;
    await fs.writeFile(file, JSON.stringify(altered));
  }, page.route, async (context) => assert.equal(context.currentReview.available, false));
});

test('aggregate navigation PASS cannot conceal a failed child check', async () => {
  await withFixture(async (root) => {
    const file = path.join(root, 'verification/evidence/2026-09-07-host-current-vv-attempt-01/current-static-checks.json');
    const altered = JSON.parse(await fs.readFile(file, 'utf8'));
    altered.checks.find((item) => item.id === 'EV-CURRENT-LOCAL-NAVIGATION-01').hrefs[0].result = 'FAIL';
    await fs.writeFile(file, JSON.stringify(altered));
  }, '/host/hosting-overview', async (context) => assert.equal(context.currentReview.available, false));
});
