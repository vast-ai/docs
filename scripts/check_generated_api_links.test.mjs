import assert from 'node:assert/strict';
import http from 'node:http';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import {
  checkGeneratedApiLinks,
  configuredOpenApiEntries,
  configuredRedirects,
  fetchTarget,
  generatedRouteMap,
  reportedArrowTargets,
  resolveConfiguredTarget,
  titleMatchesCanonical,
  validateLoopbackOrigin,
} from './check_generated_api_links.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const endpoint = (target) => ({ stdout: `source.mdx\n  ⎿ ${target}\n` });

async function startServer(t, handler) {
  const server = http.createServer(handler);
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => server.close());
  return `http://127.0.0.1:${server.address().port}`;
}

test('reads the configured OpenAPI source and its two local alias mappings', async () => {
  const entries = await configuredOpenApiEntries(root, 'docs.json');
  assert.deepEqual(entries, [{ source: 'api-reference/openapi.yaml', directory: 'api-reference' }]);

  const { config, routes } = await generatedRouteMap(root, 'docs.json');
  assert.deepEqual(routes.get('/api-reference/search/search-offers'), {
    href: '/api-reference/search/search-offers',
    title: 'Search offers',
    openapi: '/api-reference/openapi.yaml post /api/v0/bundles',
    source: 'api-reference/openapi.yaml',
  });
  const redirects = configuredRedirects(config);
  assert.deepEqual(resolveConfiguredTarget('/api-reference/search/search-template', routes, redirects), {
    kind: 'local-redirect-to-mint-generated-route',
    canonicalTarget: '/api-reference/search/search-templates',
    redirectChain: ['/api-reference/search/search-templates'],
  });
  assert.deepEqual(resolveConfiguredTarget('/api-reference/billing/search-invoices', routes, redirects), {
    kind: 'local-redirect-to-mint-generated-route',
    canonicalTarget: '/api-reference/billing/show-invoices',
    redirectChain: ['/api-reference/billing/show-invoices'],
  });
});

test('parses ordinary arrow targets instead of silently filtering them', () => {
  const baseline = {
    stdout: [
      'source.mdx',
      '  ⎿ /api-reference/search/search-offers',
      '  ⎿ /ordinary/missing',
      '  ⎿ verification/retained-evidence.json',
      '  ⎿ https://example.invalid/not-fetched',
    ].join('\n'),
  };
  assert.deepEqual(reportedArrowTargets(baseline), [
    '/api-reference/search/search-offers',
    '/ordinary/missing',
    'verification/retained-evidence.json',
    'https://example.invalid/not-fetched',
  ]);
});

test('fails closed for unknown, cyclic, and external configured redirect chains', () => {
  const routes = new Map([['/api-reference/canonical', { title: 'Canonical' }]]);
  assert.equal(
    resolveConfiguredTarget('/unknown', routes, new Map()).kind,
    'unmapped-or-ordinary-link',
  );
  assert.equal(
    resolveConfiguredTarget('/first', routes, new Map([['/first', '/second'], ['/second', '/first']])).kind,
    'redirect-cycle',
  );
  assert.equal(
    resolveConfiguredTarget('/first', routes, new Map([['/first', 'https://example.invalid/outside']])).kind,
    'redirect-rejected-external-or-invalid',
  );
});

test('accepts IPv6 loopback but rejects query and hash origins', () => {
  assert.equal(validateLoopbackOrigin('http://[::1]:3000'), 'http://[::1]:3000');
  assert.throws(() => validateLoopbackOrigin('http://127.0.0.1:3000/?x=1'), /query/);
  assert.throws(() => validateLoopbackOrigin('http://127.0.0.1:3000/#anchor'), /query/);
  assert.throws(() => validateLoopbackOrigin('https://docs.example.com'), /localhost/);
});

test('matches an exact normalized operation title segment', () => {
  assert.equal(titleMatchesCanonical('SHOW-INSTANCE \u2014 Vast.ai Documentation', 'show instance'), true);
  assert.equal(titleMatchesCanonical('show instances - Site', 'show instance'), false);
});

test('rejects an escaped initial target before any request', async (t) => {
  const originalFetch = globalThis.fetch;
  const requestedUrls = [];
  globalThis.fetch = async (input) => {
    requestedUrls.push(String(input));
    throw new Error('fetch must not be called for an escaped initial target');
  };
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  const observed = await fetchTarget('http://127.0.0.1:3000', '/\\external.test');
  assert.deepEqual(requestedUrls, []);
  assert.match(observed.error, /initial target outside/);
});

test('follows the two configured aliases locally and verifies canonical URL and title', async (t) => {
  const origin = await startServer(t, (request, response) => {
    const replies = {
      '/api-reference/search/search-template': [302, '/api-reference/search/search-templates'],
      '/api-reference/search/search-templates': [200, 'search templates - Vast.ai Documentation'],
      '/api-reference/billing/search-invoices': [302, '/api-reference/billing/show-invoices'],
      '/api-reference/billing/show-invoices': [200, 'show invoices - Vast.ai Documentation'],
    };
    const reply = replies[request.url] ?? [404, 'not found'];
    if (reply[0] === 302) response.writeHead(302, { location: reply[1] });
    else response.writeHead(reply[0], { 'content-type': 'text/html' });
    response.end(reply[0] === 302 ? '' : `<title>${reply[1]}</title>`);
  });
  const baseline = { stdout: '  ⎿ /api-reference/search/search-template\n  ⎿ /api-reference/billing/search-invoices' };
  const report = await checkGeneratedApiLinks({
    root, origin, baseline, docsConfig: 'docs.json', negativeTarget: '/api-reference/invented-not-real',
  });

  assert.equal(report.results.every((result) => result.passed), true);
  assert.equal(report.results.every((result) => result.finalUrlMatchesCanonical), true);
  assert.equal(report.results.every((result) => result.canonicalTitleMatches), true);
  assert.equal(report.negativeControl.passed, true);
  assert.equal(report.passed, true);
});

test('rejects a 200 response whose endpoint title is not the canonical title', async (t) => {
  const origin = await startServer(t, (request, response) => {
    response.writeHead(request.url === '/api-reference/search/search-offers' ? 200 : 404, { 'content-type': 'text/html' });
    response.end('<title>wrong endpoint - Vast.ai Documentation</title>');
  });
  const report = await checkGeneratedApiLinks({
    root, origin, baseline: endpoint('/api-reference/search/search-offers'), docsConfig: 'docs.json',
    negativeTarget: '/api-reference/invented-not-real',
  });
  assert.equal(report.results[0].status, 200);
  assert.equal(report.results[0].canonicalTitleMatches, false);
  assert.equal(report.results[0].passed, false);
});

test('rejects external redirects without requesting the external location', async (t) => {
  let requests = 0;
  const origin = await startServer(t, (request, response) => {
    requests += 1;
    if (request.url === '/api-reference/search/search-offers') {
      response.writeHead(302, { location: 'https://example.invalid/outside' });
      response.end();
      return;
    }
    response.writeHead(404).end();
  });
  const report = await checkGeneratedApiLinks({
    root, origin, baseline: endpoint('/api-reference/search/search-offers'), docsConfig: 'docs.json',
    negativeTarget: '/api-reference/invented-not-real',
  });
  assert.equal(requests, 2); // Generated route and negative control; no external request is attempted.
  assert.match(report.results[0].error, /outside/);
  assert.equal(report.results[0].passed, false);
});

test('bounds redirect loops and fails ordinary links without fetching them', async (t) => {
  let requests = 0;
  const origin = await startServer(t, (request, response) => {
    requests += 1;
    if (request.url === '/api-reference/search/search-offers') {
      response.writeHead(302, { location: '/api-reference/search/search-offers' });
      response.end();
      return;
    }
    response.writeHead(404).end();
  });
  const loopReport = await checkGeneratedApiLinks({
    root, origin, baseline: endpoint('/api-reference/search/search-offers'), docsConfig: 'docs.json',
    negativeTarget: '/api-reference/invented-not-real',
  });
  assert.match(loopReport.results[0].error, /hop limit/);

  requests = 0;
  const ordinaryReport = await checkGeneratedApiLinks({
    root, origin, baseline: endpoint('/ordinary/missing'), docsConfig: 'docs.json',
    negativeTarget: '/api-reference/invented-not-real',
  });
  assert.equal(requests, 1); // Only negative control; ordinary target is failed without a broadened fetch.
  assert.equal(ordinaryReport.results[0].classification, 'unmapped-or-ordinary-link');
  assert.equal(ordinaryReport.results[0].passed, false);
});
