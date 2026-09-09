#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const DEFAULT_BASELINE =
  'verification/evidence/2026-09-09-host-repository-live-merge-attempt-01/mint-links-baseline-01.json';
const DEFAULT_NEGATIVE_TARGET = '/api-reference/invented-not-real';
const LOOPBACK_HOSTS = new Set(['localhost', '127.0.0.1', '[::1]']);
const MAX_REDIRECT_HOPS = 8;
const REQUEST_TIMEOUT_MS = 5_000;

function fail(message) {
  throw new Error(message);
}

function usage() {
  return [
    'Usage: node scripts/check_generated_api_links.mjs --origin http://127.0.0.1:3000',
    '',
    'This is a generated-route reconciliation check: it reads the retained Mint',
    'broken-links baseline, resolves configured local aliases, derives Mint-generated',
    'OpenAPI routes, and prints a JSON report to stdout. Only loopback origins are accepted.',
  ].join('\n');
}

export function parseArgs(args) {
  const options = {
    baseline: DEFAULT_BASELINE,
    docsConfig: 'docs.json',
    negativeTarget: DEFAULT_NEGATIVE_TARGET,
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === '--help' || arg === '-h') return { help: true };
    if (!['--origin', '--baseline', '--docs-config', '--negative-target'].includes(arg)) {
      fail(`Unknown argument: ${arg}`);
    }
    const value = args[index + 1];
    if (!value || value.startsWith('--')) fail(`Missing value for ${arg}`);
    index += 1;
    if (arg === '--origin') options.origin = value;
    if (arg === '--baseline') options.baseline = value;
    if (arg === '--docs-config') options.docsConfig = value;
    if (arg === '--negative-target') options.negativeTarget = value;
  }

  if (!options.origin) fail('--origin is required');
  return options;
}

export function validateLoopbackOrigin(originText) {
  let origin;
  try {
    origin = new URL(originText);
  } catch {
    fail(`Invalid --origin URL: ${originText}`);
  }
  if (!['http:', 'https:'].includes(origin.protocol)) {
    fail('--origin must use http or https');
  }
  if (!LOOPBACK_HOSTS.has(origin.hostname)) {
    fail('--origin must use localhost, 127.0.0.1, or ::1');
  }
  if (
    origin.username ||
    origin.password ||
    (origin.pathname !== '/' && origin.pathname !== '') ||
    origin.search ||
    origin.hash
  ) {
    fail('--origin must be a bare loopback origin without credentials, path, query, or hash');
  }
  return origin.origin;
}

function resolveFromRoot(root, file, label) {
  const resolved = path.resolve(root, file);
  const relative = path.relative(root, resolved);
  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    fail(`${label} must stay within the repository root`);
  }
  return resolved;
}

function readOpenApiEntries(value, entries = []) {
  if (Array.isArray(value)) {
    for (const item of value) readOpenApiEntries(item, entries);
    return entries;
  }
  if (!value || typeof value !== 'object') return entries;

  if (Object.hasOwn(value, 'openapi')) {
    const openapi = value.openapi;
    if (typeof openapi === 'string') {
      entries.push({ source: openapi, directory: 'api-reference' });
    } else if (Array.isArray(openapi) && typeof openapi[0] === 'string') {
      // Mint currently uses only the first source for an array-valued `openapi` field.
      entries.push({ source: openapi[0], directory: 'api-reference' });
    } else if (openapi && typeof openapi === 'object' && typeof openapi.source === 'string') {
      entries.push({ source: openapi.source, directory: openapi.directory ?? 'api-reference' });
    }
  }
  for (const child of Object.values(value)) readOpenApiEntries(child, entries);
  return entries;
}

export async function configuredOpenApiEntries(root, docsConfig) {
  const config = await loadDocsConfig(root, docsConfig);
  const entries = readOpenApiEntries(config.navigation);
  if (entries.length === 0) fail(`No OpenAPI navigation entry found in ${docsConfig}`);

  const unique = new Map();
  for (const entry of entries) {
    if (/^https?:\/\//i.test(entry.source)) {
      fail(`Configured OpenAPI source must be local for this localhost-only check: ${entry.source}`);
    }
    resolveFromRoot(root, entry.source, 'Configured OpenAPI source');
    unique.set(`${entry.source}\u0000${entry.directory}`, entry);
  }
  return [...unique.values()];
}

async function loadDocsConfig(root, docsConfig) {
  const configPath = resolveFromRoot(root, docsConfig, '--docs-config');
  return JSON.parse(await fs.readFile(configPath, 'utf8'));
}

/**
 * Ask Mint's installed generator for the same hrefs it adds for docs.json OpenAPI
 * navigation. This intentionally does not recreate Mint's filename/collision rules.
 */
export async function generatedRouteMap(root, docsConfig) {
  const entries = await configuredOpenApiEntries(root, docsConfig);
  const config = await loadDocsConfig(root, docsConfig);
  const originalCwd = process.cwd();
  process.chdir(root);
  try {
    const { generateOpenApiPagesForDocsConfig } = await import('@mintlify/scraping');
    const routes = new Map();
    for (const entry of entries) {
      const generated = await generateOpenApiPagesForDocsConfig(entry.source, {
        openApiFilePath: entry.source,
        outDir: entry.directory,
        writeFiles: false,
      });
      for (const page of Object.values(generated.pagesAcc)) {
        if (!page?.href || !page?.openapi) continue;
        routes.set(page.href, {
          href: page.href,
          title: page.title ?? null,
          openapi: page.openapi,
          source: entry.source,
        });
      }
    }
    return { config, entries, routes };
  } finally {
    process.chdir(originalCwd);
  }
}

export function reportedArrowTargets(baseline) {
  const stdout = typeof baseline?.stdout === 'string' ? baseline.stdout : '';
  const targets = [];
  for (const line of stdout.split(/\r?\n/)) {
    const match = /⎿\s+([^\s]+)/.exec(line);
    if (!match) continue;
    const target = match[1].replace(/[),.;:]+$/, '');
    targets.push(target);
  }
  return [...new Set(targets)];
}

function pageTitle(html) {
  const match = /<title\b[^>]*>([\s\S]*?)<\/title>/i.exec(html);
  return match ? match[1].replace(/\s+/g, ' ').trim() : null;
}

function isLocalPath(target) {
  return target.startsWith('/') && !target.startsWith('//');
}

export function configuredRedirects(config) {
  const redirects = new Map();
  for (const redirect of config.redirects ?? []) {
    if (!redirect || typeof redirect.source !== 'string' || typeof redirect.destination !== 'string') continue;
    redirects.set(redirect.source, redirect.destination);
  }
  return redirects;
}

export function resolveConfiguredTarget(target, routes, redirects) {
  if (!isLocalPath(target)) {
    return { kind: 'external-or-invalid-target', canonicalTarget: null, redirectChain: [] };
  }
  const redirectChain = [];
  const seen = new Set();
  let current = target;
  for (let hop = 0; hop <= MAX_REDIRECT_HOPS; hop += 1) {
    if (routes.has(current)) {
      return {
        kind: redirectChain.length ? 'local-redirect-to-mint-generated-route' : 'mint-generated-openapi-route',
        canonicalTarget: current,
        redirectChain,
      };
    }
    const destination = redirects.get(current);
    if (destination === undefined) {
      return { kind: 'unmapped-or-ordinary-link', canonicalTarget: null, redirectChain };
    }
    if (!isLocalPath(destination)) {
      return { kind: 'redirect-rejected-external-or-invalid', canonicalTarget: null, redirectChain: [...redirectChain, destination] };
    }
    if (seen.has(current) || seen.has(destination)) {
      return { kind: 'redirect-cycle', canonicalTarget: null, redirectChain: [...redirectChain, destination] };
    }
    seen.add(current);
    redirectChain.push(destination);
    current = destination;
  }
  return { kind: 'redirect-hop-limit', canonicalTarget: null, redirectChain };
}

export function titleMatchesCanonical(observedTitle, canonicalTitle) {
  if (!observedTitle || !canonicalTitle) return false;
  const normalize = (value) => value.toLowerCase().replace(/[^a-z0-9]/g, '');
  const operationTitle = observedTitle.split(/\s+[-\u2013\u2014]\s+/, 1)[0];
  return normalize(operationTitle) === normalize(canonicalTitle);
}

export async function fetchTarget(origin, target) {
  if (!isLocalPath(target)) {
    return { status: null, title: null, finalUrl: null, redirects: [], error: 'Target is not a local absolute path' };
  }
  const expectedOrigin = new URL(origin).origin;
  let current = new URL(target, origin);
  const redirects = [];
  if (current.origin !== expectedOrigin) {
    return {
      status: null,
      title: null,
      finalUrl: current.toString(),
      redirects,
      error: 'Rejected initial target outside the requested loopback origin',
    };
  }
  try {
    for (let hop = 0; hop <= MAX_REDIRECT_HOPS; hop += 1) {
      const response = await fetch(current, {
        redirect: 'manual',
        signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
      });
      if (response.status < 300 || response.status > 399) {
        const html = await response.text();
        return { status: response.status, title: pageTitle(html), finalUrl: current.toString(), redirects, error: null };
      }
      const location = response.headers.get('location');
      if (!location) {
        return { status: response.status, title: null, finalUrl: current.toString(), redirects, error: 'Redirect response omitted Location' };
      }
      const next = new URL(location, current);
      if (next.origin !== expectedOrigin) {
        return {
          status: response.status,
          title: null,
          finalUrl: current.toString(),
          redirects,
          error: 'Rejected redirect outside the requested loopback origin',
        };
      }
      redirects.push({ status: response.status, location, acceptedUrl: next.toString() });
      current = next;
    }
    return { status: null, title: null, finalUrl: current.toString(), redirects, error: `Redirect hop limit exceeded (${MAX_REDIRECT_HOPS})` };
  } catch (error) {
    return {
      status: null,
      title: null,
      finalUrl: current.toString(),
      redirects,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export async function checkGeneratedApiLinks({ root, origin, baseline, docsConfig, negativeTarget }) {
  const normalizedOrigin = validateLoopbackOrigin(origin);
  if (!negativeTarget.startsWith('/api-reference/')) {
    fail('--negative-target must be an /api-reference/ path');
  }
  const { config, entries, routes } = await generatedRouteMap(root, docsConfig);
  const redirects = configuredRedirects(config);
  const targets = reportedArrowTargets(baseline);
  if (targets.length === 0) fail('No arrow targets found in the retained baseline');

  const results = [];
  for (const target of targets) {
    const resolution = resolveConfiguredTarget(target, routes, redirects);
    const configuredOperation = resolution.canonicalTarget ? routes.get(resolution.canonicalTarget) ?? null : null;
    const observed = configuredOperation
      ? await fetchTarget(normalizedOrigin, target)
      : { status: null, title: null, finalUrl: null, redirects: [], error: 'Not fetched: target is not a configured generated route or local alias' };
    const finalUrl = observed.finalUrl ? new URL(observed.finalUrl) : null;
    const finalUrlMatchesCanonical = finalUrl !== null &&
      finalUrl.pathname === resolution.canonicalTarget && !finalUrl.search && !finalUrl.hash;
    const canonicalTitleMatches = titleMatchesCanonical(observed.title, configuredOperation?.title);
    results.push({
      target,
      classification: resolution.kind,
      canonicalTarget: resolution.canonicalTarget,
      configuredRedirectChain: resolution.redirectChain,
      configuredOperation,
      ...observed,
      finalUrlMatchesCanonical,
      canonicalTitleMatches,
      passed: configuredOperation !== null && observed.status === 200 && finalUrlMatchesCanonical && canonicalTitleMatches,
    });
  }

  const negativeResolution = resolveConfiguredTarget(negativeTarget, routes, redirects);
  const negativeConfiguredOperation = negativeResolution.canonicalTarget
    ? routes.get(negativeResolution.canonicalTarget) ?? null
    : null;
  const negativeObserved = await fetchTarget(normalizedOrigin, negativeTarget);
  const negativeControl = {
    target: negativeTarget,
    classification: negativeConfiguredOperation ? 'unexpectedly-mapped-route' : negativeResolution.kind,
    canonicalTarget: negativeResolution.canonicalTarget,
    configuredRedirectChain: negativeResolution.redirectChain,
    configuredOperation: negativeConfiguredOperation,
    ...negativeObserved,
    passed: negativeConfiguredOperation === null && negativeResolution.kind === 'unmapped-or-ordinary-link' && negativeObserved.status === 404,
  };

  return {
    origin: normalizedOrigin,
    docsConfig,
    configuredOpenApiSources: entries,
    generatedOperationCount: routes.size,
    reportedTargetCount: results.length,
    results,
    unmappedTargets: results.filter((result) => result.configuredOperation === null).map((result) => result.target),
    negativeControl,
    passed: results.every((result) => result.passed) && negativeControl.passed,
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    process.stdout.write(`${usage()}\n`);
    return;
  }
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const baselinePath = resolveFromRoot(root, options.baseline, '--baseline');
  const baseline = JSON.parse(await fs.readFile(baselinePath, 'utf8'));
  const report = await checkGeneratedApiLinks({
    root,
    origin: options.origin,
    baseline,
    docsConfig: options.docsConfig,
    negativeTarget: options.negativeTarget,
  });
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  if (!report.passed) process.exitCode = 1;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stdout.write(`${JSON.stringify({ passed: false, error: error.message })}\n`);
    process.exitCode = 1;
  });
}
