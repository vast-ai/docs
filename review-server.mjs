#!/usr/bin/env node
/*
 * Vast.ai docs review server — annotate the local Mintlify preview (PR #185)
 * ---------------------------------------------------------------------------
 * Zero dependencies. Node 18+.
 *
 * What it does:
 *   - Reverse-proxies the Mintlify dev preview (default http://localhost:3000)
 *     and injects a review overlay into every page.
 *   - Reviewers highlight text and leave comments; feedback autosaves to
 *     ./review-feedback/feedback-<reviewer>.json on this machine.
 *   - Exports Jira-importable CSV, plus Markdown and JSON, at any time.
 *
 * Usage:
 *   Terminal 1:  npm run dev -- --no-open     (Mintlify preview on :3000)
 *   Terminal 2:  node review-server.mjs       (review overlay on :4000)
 *   Browse:      http://localhost:4000/host/hosting-overview
 *
 * Options:
 *   --host 127.0.0.1           loopback address for this review server
 *   --port 4000                port for this review server
 *   --target http://localhost:3000   where the Mintlify preview runs
 *   --dir ./review-feedback    where feedback JSON files are written
 *
 * Status & exports: http://localhost:4000/__review__/
 */

import http from 'node:http';
import net from 'node:net';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

// The audit runner uses this runtime identity to reject a stale review-server
// process whose injected overlay does not match the file being assessed.
const REVIEW_SOURCE_SHA256 = crypto.createHash('sha256')
  .update(fs.readFileSync(new URL(import.meta.url))).digest('hex');

// ------------------------------------------------------------------ config
const argv = process.argv.slice(2);
function argValue(name, dflt) {
  const i = argv.indexOf(name);
  return i !== -1 && argv[i + 1] ? argv[i + 1] : dflt;
}
const BIND_HOST = argValue('--host', '127.0.0.1');
const LOOPBACK_HOSTS = new Set(['127.0.0.1', '::1', 'localhost']);
if (!LOOPBACK_HOSTS.has(BIND_HOST)) {
  throw new Error(`--host must be loopback-only (${[...LOOPBACK_HOSTS].join(', ')})`);
}
const DISPLAY_HOST = BIND_HOST === '::1' ? '[::1]' : BIND_HOST;
const PORT_VALUE = argValue('--port', '4000');
const PORT = Number(PORT_VALUE);
if (!/^\d+$/.test(PORT_VALUE) || !Number.isInteger(PORT) || PORT < 1 || PORT > 65535) {
  throw new Error('--port must be an integer from 1 through 65535');
}
const TARGET = new URL(argValue('--target', 'http://localhost:3000'));
const TARGET_HOSTNAME = TARGET.hostname.replace(/^\[|\]$/g, '');
if (TARGET.protocol !== 'http:' || !LOOPBACK_HOSTS.has(TARGET_HOSTNAME) ||
  TARGET.username || TARGET.password || TARGET.pathname !== '/' || TARGET.search || TARGET.hash) {
  throw new Error('--target must be an HTTP loopback origin with no credentials, path, query, or fragment');
}
const FEEDBACK_DIR = path.resolve(argValue('--dir', './review-feedback'));
const PR_URL = 'https://github.com/vast-ai/docs/pull/185';
const TRACEABILITY_URL = 'https://github.com/vast-ai/docs/pull/185/files#diff-5ff737a240842e44cbef287f5e73e05da3ae18bd6e4d4f55626941405cfbfae1';
const PR_LABEL = 'docs-pr185-review';
const JIRA_BASE_URL = 'https://vastai.atlassian.net/browse/';
const JIRA_STATUS_SNAPSHOT_DATE = '2026-07-13';
const FEEDBACK_EXPORT_FORMAT = 'vast-docs-review-feedback';
const FEEDBACK_EXPORT_VERSION = 1;
const MAX_IMPORT_ITEMS = 50000;

// Review-only provenance. This data is served only by the :4000 review proxy;
// it is never injected into the Mintlify MDX served directly on :3000.
const JIRA_ISSUES = Object.freeze({
  'CON-1187': { title: 'Host Docs ++', status: 'TO REVIEW' },
  'CON-1509': { title: 'Self-Test Improvements', status: 'To Do' },
  'CON-1584': { title: 'Host account docs and CLI/API/SDK intro', status: 'BLOCKED' },
  'CON-1581': { title: 'Host Teams', status: 'BLOCKED' },
  'CON-1531': { title: 'Machine Error Reference', status: 'BLOCKED' },
  'CON-1518': { title: 'Host docs IA and sidebar restructure', status: 'TO REVIEW' },
  'CON-1517': { title: 'Common Host questions and topics', status: 'TO REVIEW' },
  'CON-1516': { title: 'Supported Hardware', status: 'DOING NOW' },
  'CON-1515': { title: 'Verification / Self-Test Reference', status: 'TO REVIEW' },
  'CON-1514': { title: 'Commonly reported Self-Test issues', status: 'TO REVIEW' },
  'CON-1513': { title: 'Generate Verification docs from Self-Test code', status: 'TO REVIEW' },
  'CON-1512': { title: 'Self-Test --ignore-requirements messaging', status: 'QA Passed' },
  'CON-1510': { title: 'Self-Test explanations and error handling', status: 'TESTING' },
  'CON-1502': { title: 'Fix Self-Test image family', status: 'QA Passed' },
  'CON-1419': { title: 'Support older GPU architectures in Self-Test', status: 'TO REVIEW' },
  'CON-1256': { title: 'Business, pricing, and listing optimization', status: 'TO REVIEW' },
  'CON-1077': { title: 'Headless Hosting Guide', status: 'TO REVIEW' },
  'CON-1583': { title: 'Lower Self-Test RAM requirement for B300', status: 'TO REVIEW' },
  'CON-1519': { title: 'Self-Test diagnostic log bundles', status: 'TO REVIEW' },
});

const PAGE_REVIEW_CONTEXTS = [
  {
    paths: ['/host/hosting-overview', '/host/quickstart', '/host/persona-decision-guide'],
    epics: ['CON-1187'], issues: ['CON-1518'],
    blockers: [
      { issue: 'CON-1518', owner: 'Docs owners', question: 'Approve or modify the lifecycle sidebar and P0/P1/P2 ordering.' },
      { issue: 'CON-1518', owner: 'Docs owners', question: 'Keep, restyle, or remove the visible persona chips?' },
    ],
  },
  {
    paths: ['/host/account-hosting-agreement', '/host/account-security-for-hosts'],
    epics: ['CON-1187'], issues: ['CON-1584', 'CON-1581'],
    blockers: [
      { issue: 'CON-1584', owner: 'Product', question: 'Confirm that setup-page machine installation keys are account-specific and distinct from normal API keys.' },
      { issue: 'CON-1584', owner: 'Product', question: 'Confirm the dedicated-host-account guidance and escalation path for stale or wrong-account state.' },
    ],
  },
  {
    paths: ['/host/cli-api-sdk', '/host/fleet-operations'],
    epics: ['CON-1187'], issues: ['CON-1584', 'CON-1518'],
    blockers: [
      { issue: 'CON-1584', owner: 'Engineering', question: 'Confirm the exact team API-key flow and permissions for host registration and automation.' },
      { issue: 'CON-1518', owner: 'Docs owners', question: 'Do generated Host CLI/SDK reference pages require persona metadata, or are they exempt?' },
    ],
  },
  {
    paths: ['/host/host-teams'],
    epics: ['CON-1187'], issues: ['CON-1581', 'CON-1584'],
    blockers: [
      { issue: 'CON-1581', owner: 'Engineering', question: 'What happens to machines, accrued earnings, and payout history when an individual host moves to a team?' },
      { issue: 'CON-1581', owner: 'Engineering', question: 'Is the team-context undefined host-id/API-key installation issue fixed?' },
      { issue: 'CON-1581', owner: 'Engineering', question: 'What is the exact flow for granting machine registration rights to a team key or custom role?' },
      { issue: 'CON-1581', owner: 'Engineering', question: 'Can a custom role grant billing_read without machine_write?' },
    ],
  },
  {
    paths: ['/host/installing-host-software'],
    epics: ['CON-1187'], issues: ['CON-1518', 'CON-1584', 'CON-1581'],
    blockers: [
      { issue: 'CON-1518', owner: 'Product', question: 'Approve the Host Installer Wizard screenshot or provide a replacement asset.' },
      { issue: 'CON-1584', owner: 'Product', question: 'Confirm the public wording for setup-page machine installation keys.' },
      { issue: 'CON-1581', owner: 'Engineering', question: 'Confirm the correct team-context installation and registration-key flow.' },
    ],
  },
  {
    paths: ['/host/machine-errors'],
    epics: ['CON-1187'], issues: ['CON-1531', 'CON-1517'],
    blockers: [
      { issue: 'CON-1531', owner: 'Backend source owner', question: 'Is the host-visible machine-error catalog complete, and which fields/UI surfaces expose each error?' },
      { issue: 'CON-1531', owner: 'Backend source owner', question: 'What clears each error, including the actual heartbeat/TTL and Self-Test behavior?' },
      { issue: 'CON-1531', owner: 'Backend source owner', question: 'Which logged-only or admin-only errors are appropriate for public docs?' },
      { issue: 'CON-1531', owner: 'Product / Console', question: 'Should UI links target raw error strings, normalized categories, or both?' },
    ],
  },
  {
    paths: ['/host/common-errors-diagnostics'],
    epics: ['CON-1187', 'CON-1509'], issues: ['CON-1531', 'CON-1517', 'CON-1519', 'CON-1514', 'CON-1510'],
    blockers: [
      { issue: 'CON-1519', owner: 'Security / Engineering', question: 'Which host-local artifacts can be collected safely, and which must remain opt-in?' },
      { issue: 'CON-1514', owner: 'Backend', question: 'Which daemon, Docker, and port diagnostics can the backend expose directly?' },
    ],
  },
  {
    paths: ['/host/network-ports'],
    epics: ['CON-1187', 'CON-1509'], issues: ['CON-1517', 'CON-1514'],
    blockers: [
      { issue: 'CON-1514', owner: 'Backend / Networking', question: 'Confirm the per-GPU port requirement, TCP/UDP behavior, and per-instance versus total-host port-range wording.' },
      { issue: 'CON-1514', owner: 'Backend / Networking', question: 'Are reserved ports released on stop, destroy, or cleanup?' },
      { issue: 'CON-1514', owner: 'Backend / Networking', question: 'Can the backend expose the exact failed ports and protocol-level results?' },
    ],
  },
  {
    paths: ['/host/self-test-reference', '/host/how-to-self-test', '/host/understanding-verification', '/host/verification-stages'],
    epics: ['CON-1187', 'CON-1509'],
    issues: ['CON-1515', 'CON-1513', 'CON-1510', 'CON-1512', 'CON-1514', 'CON-1519', 'CON-1583', 'CON-1502', 'CON-1419'],
    blockers: [
      { issue: 'CON-1515', owner: 'Product / Backend', question: 'Confirm the authoritative verification queue and wait-time facts.' },
    ],
  },
  {
    paths: ['/host/supported-hardware', '/host/hardware-prep'],
    epics: ['CON-1187', 'CON-1509'], issues: ['CON-1516', 'CON-1583', 'CON-1419'],
    blockers: [
      { issue: 'CON-1516', owner: 'Product', question: 'Confirm exact GPU-family coverage, OS/cgroup guidance, and the CPU rule shared by docs, CLI, and Self-Test.' },
      { issue: 'CON-1583', owner: 'Self-Test maintainers', question: 'Confirm how the B300 RAM cap should be explained to hosts.' },
    ],
  },
  {
    paths: ['/host/pricing-your-listing', '/host/market-metrics', '/host/optimization-guide', '/host/earning', '/host/payment', '/host/datacenter-status', '/host/guide-to-taxes'],
    epics: ['CON-1187'], issues: ['CON-1256'],
    blockers: [
      { issue: 'CON-1256', owner: 'Solutions Engineering / Business', question: 'Review pricing, sales-process, datacenter, Secure Cloud, payment, and tax positioning.' },
      { issue: 'CON-1256', owner: 'Docs owners', question: 'Confirm Gobind as reviewer and content owner for this page family.' },
    ],
  },
  {
    paths: ['/host/headless-install'],
    epics: ['CON-1187'], issues: ['CON-1077'], blockers: [],
  },
  {
    paths: ['/host/common-host-questions'],
    epics: ['CON-1187'], issues: ['CON-1517'],
    blockers: [],
  },
  {
    paths: ['/review-questions'],
    epics: ['CON-1187', 'CON-1509'],
    issues: ['CON-1584', 'CON-1581', 'CON-1531', 'CON-1518', 'CON-1517', 'CON-1515', 'CON-1514', 'CON-1513', 'CON-1510', 'CON-1256'],
    blockers: [],
  },
];

function normalizeReviewPath(rawPath) {
  let pathname = String(rawPath || '/').split(/[?#]/, 1)[0] || '/';
  try { pathname = decodeURIComponent(pathname); } catch { /* keep raw safe path */ }
  if (!pathname.startsWith('/')) pathname = '/' + pathname;
  if (pathname.length > 1) pathname = pathname.replace(/\/+$/, '');
  return pathname;
}

const VV_FILES = [
  './verification/host-docs-test-sets.json',
  './verification/host-docs-test-results.json',
  './verification/host-docs-command-scores.json',
];
function vvArray(value) {
  if (!Array.isArray(value)) throw new Error('invalid V&V data');
  return value;
}
function vvText(value) {
  if (typeof value !== 'string') throw new Error('invalid V&V text');
  return value
    .replace(/\b[A-Za-z_][A-Za-z0-9._-]*@(?!(?:<|\[))[A-Za-z0-9][A-Za-z0-9.-]*\b/g, '[account-or-host]')
    .replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g, '[network-address]')
    .replace(/(^|[^A-Za-z0-9:])(\[?[A-Fa-f0-9:]*:[A-Fa-f0-9:]+\]?)(?![A-Za-z0-9:])/g,
      (whole, prefix, address) => net.isIP(address.replace(/^\[|\]$/g, '')) === 6
        ? `${prefix}[network-address]` : whole)
    .replace(/(?:[A-Za-z]:\\Users\\[^\\\s"'\x60]+|\/(?:Users|home|root)\/[^\s"'\x60]+|\/(?:private\/tmp|tmp|var\/folders)\/[^\s"'\x60]+)/g, '[local-path]')
    .replace(/\b(?:verification|review-feedback)\/[^\s"'\x60]+/g, '[artifact-ref]')
    .replace(/\b((?:machine|instance|offer|account|user|host)(?:[-_ ]?id)?)\s*[:=]\s*[A-Za-z0-9._-]{4,}\b/gi, '$1=[identifier]')
    .replace(/\b\d{6,}\b/g, '[identifier]')
    .replace(/\b((?:api[-_ ]?key|access[-_ ]?token|token|secret|password))\s*[:=]\s*(?:"[^"]*"|'[^']*'|[^\s,;]+)/gi, '$1=[redacted]')
    .replace(/\b[A-Fa-f0-9]{48,}\b/g, (token, offset, source) => {
      const prefix = source.slice(Math.max(0, offset - 28), offset);
      return /(?:sha(?:-?256)?|hash(?:es)?(?:\s+equal)?)\s*[:=]?\s*$/i.test(prefix) ? token : '[redacted-token]';
    });
}
function vvRequiredText(value) {
  const text = vvText(value).trim();
  if (!text) throw new Error('missing V&V text');
  return text;
}
function vvRawRequiredText(value) {
  if (typeof value !== 'string' || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)) {
    throw new Error('invalid V&V source text');
  }
  const text = value.trim();
  if (!text) throw new Error('missing V&V source text');
  return text;
}
function vvSectionTitle(value) {
  return vvRequiredText(value).replace(/`([^`]+)`/g, '$1');
}
function vvExactKeys(value, keys, message) {
  const actual = Object.keys(vvObject(value)).sort();
  const expected = [...keys].sort();
  if (actual.length !== expected.length || actual.some((key, index) => key !== expected[index])) {
    throw new Error(message);
  }
  return value;
}
function vvSha256(value, message = 'invalid V&V SHA-256') {
  if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) throw new Error(message);
  return value;
}
function vvSourceIndex(sourceText) {
  const lines = sourceText.split(/\r?\n/);
  const headings = [];
  let fence = null;
  for (let index = 0; index < lines.length; index += 1) {
    const fenceMatch = lines[index].match(/^\s*(`{3,}|~{3,})/);
    if (fenceMatch) {
      const marker = fenceMatch[1];
      if (!fence) fence = { character: marker[0], length: marker.length };
      else if (marker[0] === fence.character && marker.length >= fence.length) fence = null;
      continue;
    }
    if (fence) continue;
    const match = lines[index].match(/^#{1,6}\s+(.+?)\s*#*\s*$/);
    if (match) headings.push({
      title: vvSectionTitle(match[1]), start: index + 1,
      level: match[0].match(/^#+/)[0].length,
    });
  }
  return { lines, headings };
}
function vvSectionAtLine(sourceIndex, line) {
  const heading = sourceIndex.headings.findLast((candidate) => candidate.start <= line);
  return heading?.title || 'Introduction';
}
function vvHeadingSlug(value) {
  return value.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/<[^>]+>/g, '')
    .replace(/&/g, ' and ').replace(/[`*_~]/g, '').toLowerCase()
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}
function vvSourceFragmentIds(sourceText) {
  const ids = new Set([...sourceText.matchAll(/\bid=['"]([^'"]+)['"]/g)].map((match) => match[1]));
  for (const heading of vvSourceIndex(sourceText).headings) {
    const slug = vvHeadingSlug(heading.title);
    if (slug) ids.add(slug);
  }
  return ids;
}
function vvRenderedPageFragmentIds(pageMeta) {
  const ids = vvSourceFragmentIds(pageMeta.sourceIndex.lines.join('\n'));
  for (const dependency of pageMeta.renderedDependencies || []) {
    for (const id of vvSourceFragmentIds(dependency.sourceIndex.lines.join('\n'))) ids.add(id);
  }
  return ids;
}
function vvSourceSpan(value, sourceIndex, message = 'invalid V&V source span') {
  vvExactKeys(value, ['start', 'end'], message);
  const { start, end } = value;
  if (!Number.isInteger(start) || !Number.isInteger(end) || start < 1 || end < start ||
    end > sourceIndex.lines.length) throw new Error(message);
  return { start, end };
}
const VV_REPOSITORY_ROOT = fs.realpathSync(new URL('./', import.meta.url));
const VV_EXTERNAL_SOURCE_CACHE = new Map();
// The V&V package describes the source that was actually reviewed.  Its
// `sets.source.revision` is intentionally an older topology origin, not the
// final reviewed source snapshot.  Keep this value explicit: silently using
// HEAD (or a package supplied revision) would turn historical proof into a
// claim about later wording.
const VV_REVIEWED_SOURCE_REVISION = '7d42a0d439f91e4dc2877104db807ec6fb975ce4';
const VV_REVIEWED_PACKAGE_IDENTITY = Object.freeze({
  repository: 'vast-ai/docs', branch: 'CON-1584-host-cli-api-sdk',
  // These are package declarations, not a fallback mechanism.  They make the
  // archived-source mode opt-in only for this reviewed package family.
  primarySha256: '75780f6b7e23af67c02b7470aee98138f2e02f567353560b20b4cff51676f429',
  renderedSha256: 'ebe85adc57f8a8626d8a83e93e4d3905aab9c69e126feff3ddbbb190967e83e2',
  classificationSha256: '72dd1bc0ecf51ccf462b72500dfca035c1a6cc975a0a41699f9a32cd7207d639',
});
const VV_HISTORICAL_SOURCE_PATHS = Object.freeze([
  /^docs\.json$/,
  /^host\/[A-Za-z0-9._/-]+\.mdx$/,
  /^snippets\/[A-Za-z0-9._/-]+\.mdx$/,
  /^api-reference\/[A-Za-z0-9._/-]+\.mdx$/,
  /^cli\/reference\/[A-Za-z0-9._/-]+\.mdx$/,
  /^cli\/[A-Za-z0-9._/-]+\.mdx$/,
  /^guides\/[A-Za-z0-9._/-]+\.mdx$/,
  /^sdk\/python\/reference\/[A-Za-z0-9._/-]+\.mdx$/,
  /^sdk\/python\/[A-Za-z0-9._/-]+\.mdx$/,
  /^api-reference\/openapi\/yaml\/[A-Za-z0-9._/-]+\.yaml$/,
  /^scripts\/generate_self_test_reference\.py$/,
  /^host-docs-(?:verification-inventory|command-access)\.json$/,
]);
const VV_MAX_HISTORICAL_SOURCE_BYTES = 16 * 1024 * 1024;
let vvReviewedSourceCommitChecked = false;
const VV_HISTORICAL_SOURCE_CACHE = new Map();
function vvSafeRepositoryPath(relativePath, message) {
  if (typeof relativePath !== 'string' || relativePath.length > 500 ||
    !/^[A-Za-z0-9._/-]+$/.test(relativePath) || relativePath.includes('\\') ||
    relativePath.split('/').some((segment) => !segment || segment === '.' || segment === '..')) {
    throw new Error(message);
  }
  return relativePath;
}
function vvHistoricalSourceFile(relativePath, message = 'invalid historical V&V source file') {
  const safePath = vvSafeRepositoryPath(relativePath, message);
  if (!VV_HISTORICAL_SOURCE_PATHS.some((pattern) => pattern.test(safePath))) throw new Error(message);
  if (VV_HISTORICAL_SOURCE_CACHE.has(safePath)) return VV_HISTORICAL_SOURCE_CACHE.get(safePath);
  try {
    if (!vvReviewedSourceCommitChecked) {
      execFileSync('git', ['-C', VV_REPOSITORY_ROOT, 'cat-file', '-e',
        `${VV_REVIEWED_SOURCE_REVISION}^{commit}`], { stdio: ['ignore', 'ignore', 'ignore'] });
      // Resolve the tree once as a separate type check.  A path lookup alone
      // would not make the pinned snapshot boundary obvious to a reviewer.
      const tree = execFileSync('git', ['-C', VV_REPOSITORY_ROOT, 'rev-parse',
        `${VV_REVIEWED_SOURCE_REVISION}^{tree}`], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
      if (!/^[a-f0-9]{40}$/.test(tree)) throw new Error(message);
      vvReviewedSourceCommitChecked = true;
    }
    // All arguments are independent argv values.  In particular, source paths
    // are never interpolated into a shell command.
    const type = execFileSync('git', ['-C', VV_REPOSITORY_ROOT, 'cat-file', '-t',
      `${VV_REVIEWED_SOURCE_REVISION}:${safePath}`], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'],
    }).trim();
    if (type !== 'blob') throw new Error(message);
    const bytes = execFileSync('git', ['-C', VV_REPOSITORY_ROOT, 'cat-file', 'blob',
      `${VV_REVIEWED_SOURCE_REVISION}:${safePath}`], {
      encoding: 'buffer', maxBuffer: VV_MAX_HISTORICAL_SOURCE_BYTES,
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    if (!bytes.length || bytes.length > VV_MAX_HISTORICAL_SOURCE_BYTES || bytes.includes(0)) {
      throw new Error(message);
    }
    // Reject invalid UTF-8 rather than allowing replacement characters to
    // change line and hash contracts beneath the validation code.
    const text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
    const source = { bytes, text, sourceRevision: VV_REVIEWED_SOURCE_REVISION };
    VV_HISTORICAL_SOURCE_CACHE.set(safePath, source);
    return source;
  } catch {
    throw new Error(message);
  }
}
function vvPinnedExternalSource(repository, revision, sourcePath) {
  const repositoryDirectory = {
    'vast-ai/vast-cli': 'vast-cli',
    'vast-ai/self-test': 'self-test',
  }[repository];
  if (!repositoryDirectory || !/^[a-f0-9]{40}$/.test(revision)) {
    throw new Error('unpinned external V&V authority source');
  }
  const cacheKey = `${repository}\0${revision}\0${sourcePath}`;
  if (VV_EXTERNAL_SOURCE_CACHE.has(cacheKey)) return VV_EXTERNAL_SOURCE_CACHE.get(cacheKey);
  const candidates = [
    path.resolve(VV_REPOSITORY_ROOT, '..', repositoryDirectory),
    path.resolve(VV_REPOSITORY_ROOT, '..', '..', repositoryDirectory),
  ];
  for (const candidate of candidates) {
    try {
      const root = fs.realpathSync(candidate);
      if (!fs.statSync(root).isDirectory()) continue;
      const topLevel = fs.realpathSync(execFileSync('git', ['-C', root, 'rev-parse', '--show-toplevel'], {
        encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'],
      }).trim());
      if (topLevel !== root) continue;
      execFileSync('git', ['-C', root, 'cat-file', '-e', `${revision}^{commit}`], {
        stdio: ['ignore', 'ignore', 'ignore'],
      });
      const bytes = execFileSync('git', ['-C', root, 'cat-file', 'blob', `${revision}:${sourcePath}`], {
        encoding: 'buffer', maxBuffer: 16 * 1024 * 1024, stdio: ['ignore', 'pipe', 'ignore'],
      });
      if (!bytes.length || bytes.includes(0)) continue;
      const text = bytes.toString('utf8');
      VV_EXTERNAL_SOURCE_CACHE.set(cacheKey, text);
      return text;
    } catch { /* try the next explicit sibling-repository location */ }
  }
  throw new Error('unresolvable pinned external V&V authority source');
}
function vvRepositoryFile(relativePath, message = 'invalid V&V repository file') {
  if (typeof relativePath !== 'string' || relativePath.length > 500 ||
    !/^[A-Za-z0-9._/-]+$/.test(relativePath) || relativePath.includes('\\') ||
    relativePath.split('/').some((segment) => !segment || segment === '.' || segment === '..')) {
    throw new Error(message);
  }
  const fileUrl = new URL(`./${relativePath}`, import.meta.url);
  let stat;
  let realPath;
  try {
    stat = fs.lstatSync(fileUrl);
    realPath = fs.realpathSync(fileUrl);
  } catch {
    throw new Error(message);
  }
  const relativeRealPath = path.relative(VV_REPOSITORY_ROOT, realPath);
  if (!stat.isFile() || stat.isSymbolicLink() || !relativeRealPath || relativeRealPath === '..' ||
    relativeRealPath.startsWith(`..${path.sep}`) || path.isAbsolute(relativeRealPath)) {
    throw new Error(message);
  }
  return { fileUrl, bytes: fs.readFileSync(fileUrl), realPath };
}
function vvCitationRefKind(href) {
  if (href.startsWith('/') || href.startsWith('#')) return 'LOCAL_DOCUMENTATION';
  const normalized = href.toLowerCase().split('#', 1)[0].split('?', 1)[0].replace(/\/+$/, '');
  if (new Set(['https://cloud.vast.ai/host/agreement', 'https://vast.ai/terms',
    'https://www.vast.ai/terms']).has(normalized)) return 'AUTHORITATIVE_SOURCE_CANDIDATE';
  if (/^https?:\/\//i.test(href)) {
    if (['cloud.vast.ai/', 'vastai.app.box.com/', 's3.amazonaws.com/vast.ai/']
      .some((token) => normalized.includes(token))) return 'EXTERNAL_ACTION_OR_UI_DESTINATION';
    return 'EXTERNAL_REFERENCE';
  }
  return 'EXTERNAL_CONTACT_OR_REFERENCE';
}
function vvExtractCitationRefs(sourceText) {
  const hrefs = [];
  const markdownLink = /(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+['"][^'"]*['"])?\)/g;
  const autolink = /<((?:https?:\/\/|mailto:)[^>]+)>/g;
  for (const expression of [markdownLink, autolink]) {
    for (const match of sourceText.matchAll(expression)) hrefs.push(match[1]);
  }
  return [...new Set(hrefs)].map((href) => ({
    href, kind: vvCitationRefKind(href),
  }));
}
function vvValidateCitationHref(href, pageMeta) {
  if (href.startsWith('#')) {
    if (!/^#[A-Za-z0-9._-]+$/.test(href) ||
      !vvRenderedPageFragmentIds(pageMeta).has(href.slice(1))) {
      throw new Error('unresolved same-page V&V citation fragment');
    }
    return;
  }
  if (href.startsWith('/')) {
    const match = href.match(/^(\/[A-Za-z0-9._/-]+)(?:#([A-Za-z0-9._-]+))?$/);
    if (!match || match[1].split('/').some((segment, index) => index > 0 &&
      (!segment || segment === '.' || segment === '..'))) {
      throw new Error('invalid local V&V citation route');
    }
    const targetText = vvHistoricalSourceFile(`${match[1].slice(1)}.mdx`,
      'unresolved local V&V citation route').bytes.toString('utf8');
    const targetFragments = match[1] === pageMeta.route
      ? vvRenderedPageFragmentIds(pageMeta) : vvSourceFragmentIds(targetText);
    if (match[2] && !targetFragments.has(match[2])) {
      throw new Error('unresolved local V&V citation fragment');
    }
    return;
  }
  if (!/^(?:https?:\/\/|mailto:)/i.test(href)) throw new Error('invalid external V&V citation scheme');
  let parsed;
  try { parsed = new URL(href); } catch { throw new Error('invalid external V&V citation URL'); }
  if (parsed.username || parsed.password || !new Set(['http:', 'https:', 'mailto:']).has(parsed.protocol)) {
    throw new Error('unsafe external V&V citation URL');
  }
}
function vvGenericMaterialClaims(pageMeta) {
  const rawLines = pageMeta.sourceIndex.lines;
  const lines = [];
  let inComment = false;
  let maskingFence = null;
  for (const rawLine of rawLines) {
    const marker = rawLine.match(/^\s*(`{3,}|~{3,})/);
    if (!inComment && marker) {
      const token = marker[1];
      if (!maskingFence) maskingFence = { character: token[0], length: token.length };
      else if (token[0] === maskingFence.character && token.length >= maskingFence.length) maskingFence = null;
      lines.push(rawLine);
      continue;
    }
    if (maskingFence) { lines.push(rawLine); continue; }
    let output = '';
    let cursor = 0;
    while (cursor < rawLine.length) {
      if (inComment) {
        const end = rawLine.indexOf('*/}', cursor);
        if (end < 0) { output += ' '.repeat(rawLine.length - cursor); cursor = rawLine.length; }
        else { output += ' '.repeat(end + 3 - cursor); cursor = end + 3; inComment = false; }
      } else {
        const start = rawLine.indexOf('{/*', cursor);
        if (start < 0) { output += rawLine.slice(cursor); cursor = rawLine.length; }
        else { output += rawLine.slice(cursor, start) + '   '; cursor = start + 3; inComment = true; }
      }
    }
    lines.push(output);
  }
  if (inComment) throw new Error('unterminated MDX comment in material V&V claim source');
  const claimSourceIndex = vvSourceIndex(lines.join('\n'));
  const blocks = [];
  let paragraph = [];
  let frontmatter = Boolean(lines.length && lines[0].trim() === '---');
  let fence = null;
  const normalizeCodeText = (value) => value.replace(/\s+/g, ' ').trim();
  const normalizeText = (value) => {
    const inlineCode = [];
    let normalized = value.replace(/`([^`\n]+)`/g, (_match, literal) => {
      const token = `\u0000INLINE_CODE_${inlineCode.length}\u0000`;
      inlineCode.push(`\`${normalizeCodeText(literal)}\``);
      return token;
    });
    normalized = normalized.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ');
    inlineCode.forEach((literal, index) => {
      normalized = normalized.replace(`\u0000INLINE_CODE_${index}\u0000`, literal);
    });
    return normalized.trim();
  };
  const addBlock = (start, end, heading, text) => {
    blocks.push({ text, start, end, heading });
  };
  const flush = () => {
    if (!paragraph.length) return;
    const start = paragraph[0][0];
    const end = paragraph.at(-1)[0];
    const raw = paragraph.map((item) => item[1]).join('\n');
    const text = normalizeText(raw);
    paragraph = [];
    if (/^\s*!\[[^\]]*\]\([^)]*\)\s*$/.test(raw)) return;
    if (text && !/^[{}()[\],.;:'"`/*_ -]+$/.test(text)) {
      addBlock(start, end, vvSectionAtLine(claimSourceIndex, start), text);
    }
  };
  for (let offset = 0; offset < lines.length; offset += 1) {
    const lineNumber = offset + 1;
    const line = lines[offset];
    const stripped = line.trim();
    if (frontmatter) {
      if (lineNumber > 1 && stripped === '---') frontmatter = false;
      continue;
    }
    const marker = line.match(/^\s*(`{3,}|~{3,})(.*)$/);
    if (fence) {
      if (marker && marker[1][0] === fence.character && marker[1].length >= fence.length) {
        const text = normalizeCodeText(fence.content.join('\n'));
        if (text) addBlock(fence.start, lineNumber, vvSectionAtLine(claimSourceIndex, fence.start),
          `[${fence.language || 'code'}] ${text}`);
        fence = null;
      } else {
        fence.content.push(line);
      }
      continue;
    }
    if (marker) {
      flush();
      fence = { character: marker[1][0], length: marker[1].length,
        language: marker[2].trim(), start: lineNumber, content: [] };
      continue;
    }
    if (/^#{1,6}\s+/.test(line) || !stripped) {
      flush();
      continue;
    }
    if (/^(?:import|export)\s+/.test(stripped) || stripped.includes('persona-chips')) {
      flush();
      continue;
    }
    const frameCaption = stripped.match(/^<Frame\b[^>]*\bcaption=(['"])(.*?)\1[^>]*>$/);
    if (frameCaption) {
      flush();
      const text = normalizeText(frameCaption[2]);
      if (text) addBlock(lineNumber, lineNumber, vvSectionAtLine(claimSourceIndex, lineNumber), text);
      continue;
    }
    if (/^<\/?[A-Za-z][^>]*>$/.test(stripped) ||
      /^\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?$/.test(stripped)) {
      flush();
      continue;
    }
    if (stripped.startsWith('|') && stripped.endsWith('|')) {
      flush();
      const nextLine = lines[offset + 1]?.trim() || '';
      if (/^\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?$/.test(nextLine)) continue;
      const text = normalizeText(stripped.slice(1, -1).split('|').map((cell) => cell.trim()).join(' | '));
      if (text) addBlock(lineNumber, lineNumber, vvSectionAtLine(claimSourceIndex, lineNumber), text);
      continue;
    }
    if (/^(?:[-*+] |\d+[.)] )/.test(stripped)) {
      flush();
      const text = normalizeText(stripped.replace(/^(?:[-*+] |\d+[.)] )/, ''));
      if (text) addBlock(lineNumber, lineNumber, vvSectionAtLine(claimSourceIndex, lineNumber), text);
      continue;
    }
    paragraph.push([lineNumber, line]);
  }
  flush();
  const contextualListLeadins = {
    'host/account-security-for-hosts.mdx': new Map([
      [23, new Set([25, 26, 27, 28])],
      [38, new Set([40, 41, 42, 43])],
    ]),
    'host/datacenter-status.mdx': new Map([[33, new Set([35, 36, 37, 38, 39])]]),
    'host/guide-to-taxes.mdx': new Map([[23, new Set([25, 26, 27])]]),
    'host/hosting-agreement.mdx': new Map([[31, new Set([33, 34, 35, 36])]]),
    'host/hosting-overview.mdx': new Map([
      [18, new Set([20, 21, 22, 23])],
      [72, new Set([74, 75, 76, 77])],
    ]),
    'host/notifications.mdx': new Map([[29, new Set([33])]]),
    'host/payment.mdx': new Map([[31, new Set([33, 34, 35])]]),
    'host/workload-policy.mdx': new Map([[23, new Set([25, 26, 27, 28, 29, 30])]]),
  }[pageMeta.sourceFile] || new Map();
  const retainedLeadinText = {
    'host/hosting-agreement.mdx': new Map([[31,
      'Under the [Hosting Agreement](https://cloud.vast.ai/host/agreement), listing a machine creates offers that clients can accept as rental contracts.']]),
    'host/guide-to-taxes.mdx': new Map([[23,
      'Depending on your payout method, your payment provider may issue a tax form if you meet their reporting threshold.']]),
    'host/hosting-overview.mdx': new Map([[72,
      'Under the [Hosting Agreement](https://cloud.vast.ai/host/agreement), existing contracts cannot be changed by editing the offer.']]),
  }[pageMeta.sourceFile] || new Map();
  const contextualTextOverrides = {
    'host/account-security-for-hosts.mdx': new Map([[23,
      'Enable two-factor authentication on these accounts; it is especially important for:']]),
    'host/guide-to-taxes.mdx': new Map([[23, 'It is your responsibility to:']]),
    'host/hosting-agreement.mdx': new Map([[31,
      'Under the [Hosting Agreement](https://cloud.vast.ai/host/agreement), for each active rental contract you commit to:']]),
    'host/hosting-overview.mdx': new Map([[72,
      'Under the [Hosting Agreement](https://cloud.vast.ai/host/agreement), that means:']]),
  }[pageMeta.sourceFile] || new Map();
  const contextualSourceLines = {
    'host/account-security-for-hosts.mdx': new Map([[23, [21, 23]]]),
  }[pageMeta.sourceFile] || new Map();
  const leadinLines = new Set(contextualListLeadins.keys());
  const contextByItemLine = new Map();
  for (const [contextLine, itemLines] of contextualListLeadins) {
    for (const itemLine of itemLines) contextByItemLine.set(itemLine, contextLine);
  }
  return blocks.filter((block) => !leadinLines.has(block.start) || retainedLeadinText.has(block.start))
    .map((block) => {
    const contextLine = contextByItemLine.get(block.start);
    const sourceSpans = [{ start: block.start, end: block.end }];
    let raw = rawLines.slice(block.start - 1, block.end).join('\n');
    let text = retainedLeadinText.get(block.start) || block.text;
    if (contextLine != null) {
      const contextLines = contextualSourceLines.get(contextLine) || [contextLine];
      const contextRaw = contextLines.map((line) => rawLines[line - 1]).join('\n');
      raw = `${contextRaw}\n${raw}`;
      text = `${normalizeText(contextualTextOverrides.get(contextLine) || contextRaw)} ${text}`;
      sourceSpans.unshift(...contextLines.map((line) => ({ start: line, end: line })));
    }
    const rawHash = crypto.createHash('sha256').update(raw).digest('hex');
    const basis = sourceSpans.length === 1
      ? `${pageMeta.route}\0${block.heading}\0${block.start}\0${block.end}\0${rawHash}`
      : `${pageMeta.route}\0${block.heading}\0${sourceSpans.map((span) =>
        `${span.start}-${span.end}`).join(',')}\0${rawHash}`;
    return { id: `MCL-${crypto.createHash('sha256').update(basis).digest('hex').slice(0, 16)}`,
      text, start: sourceSpans[0].start, end: block.end, sourceSpans };
    });
}
function vvTotals(testSets, pageHistory = []) {
  const branches = testSets.flatMap((set) => set.branches);
  const steps = branches.flatMap((branch) => branch.steps);
  const commands = steps.flatMap((step) => step.commands);
  const displayOnlyCommands = commands.filter((command) => command.treatment === 'NON_EXECUTABLE_DISPLAY');
  const executableIntentCommands = commands.filter((command) => command.treatment !== 'NON_EXECUTABLE_DISPLAY');
  const nonCommandSteps = steps.filter((step) => !step.commands.length);
  const histories = [pageHistory,
    ...testSets.map((set) => set.history || []),
    ...branches.map((branch) => branch.history || []),
    ...steps.map((step) => step.history || []),
    ...commands.map((command) => command.history || []),
  ].flat();
  const observationIds = new Set([
    ...commands.flatMap((command) => command.evidence.map((row) => row.ref)),
    ...histories.flatMap((row) => row.evidenceIds || []),
  ]);
  return {
    testSets: testSets.length, branches: branches.length, steps: steps.length, commands: commands.length,
    nonCommandSteps: nonCommandSteps.length,
    displayOnlyCommands: displayOnlyCommands.length,
    executableIntentCommands: executableIntentCommands.length,
    retainedEvidenceRecords: observationIds.size,
    // `observations` is retained for the API's backward compatibility. The UI calls
    // these retained evidence records: a record can be an accounting or procedure
    // result rather than a human observation.
    observations: observationIds.size,
    // A display-only carrier is not executable, but it can still receive a
    // numeric *semantic documentation* assessment. Keep those counts separate
    // so the UI never implies that a static reference was functionally run.
    scored: commands.filter((command) => command.score).length,
    executableIntentScored: executableIntentCommands.filter((command) => command.score).length,
    displayOnlyScored: displayOnlyCommands.filter((command) => command.score).length,
    notApplicableAssessments: displayOnlyCommands.filter((command) => command.notApplicableAssessment).length,
  };
}
function vvSetTotals(set) {
  const totals = vvTotals([set]);
  const commands = set.branches.flatMap((branch) =>
    branch.steps.flatMap((step) => step.commands));
  return {
    ...totals,
    scoreCounts: [1, 2, 3].map((score) =>
      commands.filter((command) => command.score?.value === score).length),
  };
}
const VV_ATTEMPT_STATUSES = new Set(['PASS', 'FAIL', 'PARTIAL', 'BLOCKED', 'UNVALIDATED', 'STALE', 'NOT_APPLICABLE']);
const VV_TARGET_STATUSES = new Set(['PASS', 'FAIL', 'BLOCKED', 'UNVALIDATED', 'STALE', 'NOT_APPLICABLE']);
const VV_REQUIRED_EVIDENCE_TYPES = new Set([
  'ACCOUNTABLE_OWNER_CONFIRMATION',
  'APPROVED_NON_EXECUTABLE_CLASSIFICATION',
  'AUTHORITATIVE_DOCUMENTATION_CITATION',
  'CANONICAL_IMPLEMENTATION_SOURCE',
  'CHILD_STATUS_ROLLUP',
  'REPOSITORY_STATIC_CHECK',
  'RUNTIME_OR_UI_OBSERVATION',
]);
const VV_DIRECT_PROOF_ROLES = new Set([
  'DIRECT_FUNCTIONAL_EXACT_FULL',
  'DIRECT_FUNCTIONAL_EQUIVALENT_FULL',
  'DIRECT_FUNCTIONAL_PARTIAL',
  'BOUNDED_STATIC_SUPPORT',
  'EXACT_OCCURRENCE_AND_SAFETY_GATE_ONLY',
]);
const VV_SCORE3_PROOF_ROLES = new Set([
  'DIRECT_FUNCTIONAL_EXACT_FULL',
  'DIRECT_FUNCTIONAL_EQUIVALENT_FULL',
]);
const VV_STATUS_TARGET_FIELDS = {
  PAGE: ['page_id'],
  TEST_SET: ['page_id', 'test_set_id'],
  BRANCH: ['page_id', 'test_set_id', 'branch_id'],
  STEP: ['page_id', 'test_set_id', 'branch_id', 'step_id'],
  COMMAND: ['page_id', 'test_set_id', 'branch_id', 'step_id', 'command_id'],
};
function vvObject(value) {
  if (!value || Array.isArray(value) || typeof value !== 'object') throw new Error('invalid V&V object');
  return value;
}
function vvIdentifier(value) {
  if (typeof value !== 'string' || value.length > 200 || !/^[A-Za-z0-9][A-Za-z0-9._:-]*$/.test(value)) {
    throw new Error('invalid V&V identifier');
  }
  return value;
}
function vvEvidenceId(value) {
  const id = vvIdentifier(value);
  if (!/^EV-[A-Za-z0-9][A-Za-z0-9._:-]*$/.test(id)) throw new Error('invalid V&V evidence identifier');
  return id;
}
function vvAttemptId(value) {
  const id = vvIdentifier(value);
  if (!/^ATTEMPT-[A-Za-z0-9][A-Za-z0-9._:-]*$/.test(id)) throw new Error('invalid V&V attempt identifier');
  return id;
}
function vvEvidenceRef(value) {
  if (typeof value !== 'string' || value.length > 500 ||
    !/^verification\/evidence\/[A-Za-z0-9._/-]+$/.test(value) ||
    value.split('/').includes('..') || value.includes('\\')) {
    throw new Error('invalid V&V evidence reference');
  }
  const evidenceUrl = new URL(`./${value}`, import.meta.url);
  let stat;
  let realPath;
  try {
    stat = fs.lstatSync(evidenceUrl);
    realPath = fs.realpathSync(evidenceUrl);
  } catch {
    throw new Error('missing V&V evidence reference');
  }
  const evidenceRoot = fs.realpathSync(new URL('./verification/evidence/', import.meta.url));
  const relative = path.relative(evidenceRoot, realPath);
  if (!stat.isFile() || stat.isSymbolicLink() || !relative || relative.startsWith(`..${path.sep}`) ||
    relative === '..' || path.isAbsolute(relative)) {
    throw new Error('invalid V&V evidence reference');
  }
  return value;
}
function vvApprovalRef(value) {
  const id = vvIdentifier(value);
  if (/^CANONICAL_NON_EXECUTABLE_DISPLAY:[a-f0-9]{64}$/.test(id)) return id;
  return vvText(id);
}
function vvStatus(value, allowed = VV_TARGET_STATUSES) {
  if (typeof value !== 'string' || !allowed.has(value)) throw new Error('invalid V&V status');
  return value;
}
function vvCanonicalRoute(value) {
  if (typeof value !== 'string' || value.length > 500 ||
    !/^\/host\/[A-Za-z0-9._/-]+$/.test(value)) {
    throw new Error('invalid canonical V&V route');
  }
  const segments = value.split('/').slice(2);
  if (!segments.length || segments.some((segment) => !segment || segment === '.' || segment === '..')) {
    throw new Error('invalid canonical V&V route');
  }
  return value;
}
function vvStatusKey(level, target) {
  const fields = VV_STATUS_TARGET_FIELDS[level];
  if (!fields) throw new Error('invalid V&V status level');
  return [level, ...fields.map((field) => target[field] || '')].join('\u0000');
}
function canonicalStatusTargets(pages, declaredCounts) {
  const targets = new Map();
  const commandById = new Map();
  const pageById = new Map();
  const pageByRoute = new Map();
  const childrenByKey = new Map();
  const targetClaimByKey = new Map();
  const claimRefsByKey = new Map();
  const executionStatusByKey = new Map();
  const identifiers = new Map(Object.keys(VV_STATUS_TARGET_FIELDS).map((level) => [level, new Set()]));
  const routes = new Set();
  const counts = { pages: 0, test_sets: 0, branches: 0, steps: 0, command_carriers: 0, command_bearing_steps: 0 };
  const validateTextList = (value, message) => vvArray(value).map((item) => {
    try { return vvRequiredText(item); } catch { throw new Error(message); }
  });
  const validateIdentifierList = (value, parser, message) => {
    let items;
    try { items = vvArray(value).map(parser); } catch { throw new Error(message); }
    if (new Set(items).size !== items.length) throw new Error(message);
    return items;
  };
  const add = (level, target, parentKey = null, claim = null, claimRefs = [], required = true) => {
    const key = vvStatusKey(level, target);
    if (targets.has(key)) throw new Error('duplicate canonical V&V target');
    const ownId = target[VV_STATUS_TARGET_FIELDS[level].at(-1)];
    if (identifiers.get(level).has(ownId)) throw new Error('duplicate canonical V&V identifier');
    identifiers.get(level).add(ownId);
    targets.set(key, target);
    childrenByKey.set(key, []);
    targetClaimByKey.set(key, claim == null ? null : vvRequiredText(claim));
    const normalizedClaimRefs = vvArray(claimRefs).map(vvIdentifier);
    if (new Set(normalizedClaimRefs).size !== normalizedClaimRefs.length) {
      throw new Error('duplicate canonical V&V claim binding');
    }
    claimRefsByKey.set(key, normalizedClaimRefs);
    if (parentKey) {
      if (typeof required !== 'boolean') throw new Error('invalid canonical V&V child requirement');
      childrenByKey.get(parentKey).push({ level, target, key, required });
    }
    return key;
  };
  const assertStepSourceBinding = (step, sourceIndex, sourceFile) => {
    const stepId = vvIdentifier(step.step_id);
    const sourceLines = vvArray(step.source_lines).map((span) =>
      vvSourceSpan(span, sourceIndex, `invalid canonical V&V step source span in ${sourceFile}:${stepId}`));
    const sourceSections = vvArray(step.source_sections).map(vvSectionTitle);
    if (!sourceLines.length || !sourceSections.length || new Set(sourceSections).size !== sourceSections.length) {
      throw new Error('missing canonical V&V step source binding');
    }
    const spanMatchesSection = (span, section) => {
      if (section === 'Introduction') {
        const firstHeading = sourceIndex.headings[0]?.start || sourceIndex.lines.length + 1;
        return span.start < firstHeading;
      }
      return sourceIndex.headings.some((heading, index) => {
        const nextStart = sourceIndex.headings.slice(index + 1)
          .find((next) => next.level <= heading.level)?.start || sourceIndex.lines.length + 1;
        return heading.title === section && heading.start <= span.end && nextStart > span.start;
      });
    };
    for (const spanValue of sourceLines) {
      if (!sourceSections.some((section) => spanMatchesSection(spanValue, section))) {
        throw new Error(`invalid canonical V&V step source section in ${sourceFile}:${stepId}`);
      }
    }
    if (sourceSections.some((section) => !sourceLines.some((span) => spanMatchesSection(span, section)))) {
      throw new Error(`unbound canonical V&V step source section in ${sourceFile}:${stepId}`);
    }
    return { sourceLines, sourceSections };
  };
  for (const page of pages) {
    vvExactKeys(page, ['page_id', 'route', 'title', 'source_file', 'source_sha256',
      'rendered_dependencies', 'rendered_source_sha256', 'actionable_sections', 'disposition',
      'execution_status', 'material_claim_ids', 'test_sets'], 'invalid canonical V&V page structure');
    const pageId = vvIdentifier(page.page_id);
    const pageRoute = vvCanonicalRoute(page.route);
    const pageExecutionStatus = vvStatus(page.execution_status);
    if (routes.has(pageRoute)) throw new Error('invalid canonical V&V route');
    routes.add(pageRoute);
    const sourceFile = vvRequiredText(page.source_file);
    if (!/^host\/[A-Za-z0-9._/-]+\.mdx$/.test(sourceFile) || sourceFile.split('/').includes('..')) {
      throw new Error('invalid canonical V&V source path');
    }
    if (typeof page.source_sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(page.source_sha256)) {
      throw new Error('invalid canonical V&V source hash');
    }
    const sourceBytes = vvHistoricalSourceFile(sourceFile, 'invalid canonical V&V source file').bytes;
    if (crypto.createHash('sha256').update(sourceBytes).digest('hex') !== page.source_sha256) {
      throw new Error('stale canonical V&V page source');
    }
    const sourceIndex = vvSourceIndex(sourceBytes.toString('utf8'));
    const actionableSections = validateTextList(page.actionable_sections,
      'invalid canonical V&V actionable sections').map(vvSectionTitle);
    if (!actionableSections.length || new Set(actionableSections).size !== actionableSections.length ||
      actionableSections.some((heading) => heading !== 'Introduction' &&
        !sourceIndex.headings.some((item) => item.title === heading)) ||
      !new Set(['conceptual/policy', 'generated-reference', 'navigation/cross-page journey',
        'procedure-bearing']).has(vvRequiredText(page.disposition))) {
      throw new Error('invalid canonical V&V page disposition or actionable section');
    }
    const renderedDependencies = [];
    const dependencyIdentities = new Set();
    const escapePattern = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    for (const dependencyValue of vvArray(page.rendered_dependencies)) {
      const dependency = vvExactKeys(dependencyValue,
        ['component', 'source_file', 'source_sha256', 'import_line', 'insertion_line'],
        'invalid rendered V&V dependency');
      const component = vvIdentifier(dependency.component);
      const dependencyFile = vvRequiredText(dependency.source_file);
      const dependencyHash = vvSha256(dependency.source_sha256, 'invalid rendered V&V dependency hash');
      if (!/^snippets\/[A-Za-z0-9._/-]+\.mdx$/.test(dependencyFile) ||
        dependencyFile.split('/').some((segment) => !segment || segment === '.' || segment === '..') ||
        !Number.isInteger(dependency.import_line) || !Number.isInteger(dependency.insertion_line) ||
        dependency.import_line < 1 || dependency.import_line > sourceIndex.lines.length ||
        dependency.insertion_line < 1 || dependency.insertion_line > sourceIndex.lines.length) {
        throw new Error('invalid rendered V&V dependency scope');
      }
      const identity = `${component}\0${dependencyFile}`;
      if (dependencyIdentities.has(identity)) throw new Error('duplicate rendered V&V dependency');
      dependencyIdentities.add(identity);
      const dependencyBytes = vvHistoricalSourceFile(dependencyFile, 'invalid rendered V&V dependency file').bytes;
      if (crypto.createHash('sha256').update(dependencyBytes).digest('hex') !== dependencyHash) {
        throw new Error('stale rendered V&V dependency source');
      }
      const importPattern = new RegExp(`^import\\s+${escapePattern(component)}\\s+from\\s+['"]/${
        escapePattern(dependencyFile)}['"]\\s*;?\\s*$`);
      const insertionPattern = new RegExp(`^\\s*<${escapePattern(component)}\\s*/>\\s*$`);
      if (!importPattern.test(sourceIndex.lines[dependency.import_line - 1]) ||
        !insertionPattern.test(sourceIndex.lines[dependency.insertion_line - 1]) ||
        sourceIndex.lines.filter((line) => importPattern.test(line)).length !== 1 ||
        sourceIndex.lines.filter((line) => insertionPattern.test(line)).length !== 1) {
        throw new Error('detached rendered V&V dependency import or insertion');
      }
      renderedDependencies.push({ component, sourceFile: dependencyFile, sourceSha256: dependencyHash,
        importLine: dependency.import_line, insertionLine: dependency.insertion_line,
        sourceIndex: vvSourceIndex(dependencyBytes.toString('utf8')) });
    }
    const declaredRenderedDependencyOrder = renderedDependencies.map((dependency) =>
      `${dependency.insertionLine}\0${dependency.component}`);
    renderedDependencies.sort((left, right) => left.insertionLine - right.insertionLine ||
      left.component.localeCompare(right.component));
    if (JSON.stringify(declaredRenderedDependencyOrder) !== JSON.stringify(renderedDependencies.map((dependency) =>
      `${dependency.insertionLine}\0${dependency.component}`))) {
      throw new Error('noncanonical rendered V&V dependency order');
    }
    const renderedRows = [`PRIMARY\0${sourceFile}\0${page.source_sha256}\n`,
      ...renderedDependencies.map((dependency) =>
        `DEPENDENCY\0${dependency.component}\0${dependency.sourceFile}\0${dependency.sourceSha256}\0${
          dependency.importLine}\0${dependency.insertionLine}\n`)];
    const renderedSourceSha256 = vvSha256(page.rendered_source_sha256,
      'invalid rendered V&V page-source hash');
    if (crypto.createHash('sha256').update(renderedRows.join('')).digest('hex') !== renderedSourceSha256) {
      throw new Error('stale rendered V&V page-source binding');
    }
    const pageKey = add('PAGE', { page_id: pageId }, null, null, page.material_claim_ids);
    executionStatusByKey.set(pageKey, pageExecutionStatus);
    const pageMeta = {
      pageId, route: pageRoute, title: vvRequiredText(page.title), sourceFile,
      sourceSha256: page.source_sha256, sourceIndex, materialClaimIds: vvArray(page.material_claim_ids).map(vvIdentifier),
      renderedDependencies, renderedSourceSha256,
    };
    if (pageById.has(pageId) || pageByRoute.has(pageRoute)) throw new Error('duplicate canonical V&V page');
    pageById.set(pageId, pageMeta);
    pageByRoute.set(pageRoute, pageMeta);
    counts.pages += 1;
    for (const set of vvArray(page.test_sets)) {
      const setKeys = ['test_set_id', 'procedure_id', 'title', 'goal', 'context', 'prerequisites',
        'access_classes', 'safety_constraints', 'cleanup', 'expected_final_observables',
        'failure_behavior', 'limitations', 'source_context', 'attempt_ids', 'execution_status',
        'claim_ids', 'branches'];
      if (Object.prototype.hasOwnProperty.call(vvObject(set), 'no_material_claim_reason')) {
        setKeys.push('no_material_claim_reason');
      }
      vvExactKeys(set, setKeys, 'invalid canonical V&V test-set structure');
      const testSetId = vvIdentifier(set.test_set_id);
      vvIdentifier(set.procedure_id);
      vvRequiredText(set.title); vvRequiredText(set.goal);
      if (typeof set.context === 'string') vvRequiredText(set.context);
      else {
        const context = vvExactKeys(set.context,
          ['environment', 'intended_user', 'representativeness_limit'],
          'invalid canonical V&V test-set context');
        vvRequiredText(context.environment); vvRequiredText(context.intended_user);
        vvRequiredText(context.representativeness_limit);
      }
      for (const [field, label] of [
        ['prerequisites', 'prerequisites'], ['access_classes', 'access classes'],
        ['safety_constraints', 'safety constraints'], ['cleanup', 'cleanup'],
        ['expected_final_observables', 'expected observables'],
        ['failure_behavior', 'failure behavior'], ['limitations', 'limitations'],
      ]) validateTextList(set[field], `invalid canonical V&V test-set ${label}`);
      validateIdentifierList(set.attempt_ids, vvAttemptId, 'invalid canonical V&V test-set attempts');
      if (set.no_material_claim_reason != null) vvRequiredText(set.no_material_claim_reason);
      const setExecutionStatus = vvStatus(set.execution_status);
      const sourceContext = vvExactKeys(set.source_context,
        ['file', 'headings', 'line_start', 'line_end', 'rendered_route', 'rendered_status'],
        'invalid canonical V&V test-set source context');
      const contextHeadings = vvArray(sourceContext.headings).map(vvSectionTitle);
      if (sourceContext.file !== sourceFile || vvCanonicalRoute(sourceContext.rendered_route) !== pageRoute ||
        vvStatus(sourceContext.rendered_status) !== setExecutionStatus ||
        !Number.isInteger(sourceContext.line_start) || !Number.isInteger(sourceContext.line_end) ||
        sourceContext.line_start < 1 || sourceContext.line_end < sourceContext.line_start ||
        sourceContext.line_end > sourceIndex.lines.length || !contextHeadings.length ||
        new Set(contextHeadings).size !== contextHeadings.length || contextHeadings.some((heading) =>
          heading !== 'Introduction' && !sourceIndex.headings.some((candidate) => candidate.title === heading))) {
        throw new Error('mismatched canonical V&V test-set source context');
      }
      const setTarget = { page_id: pageId, test_set_id: testSetId };
      const setKey = add('TEST_SET', setTarget, pageKey, set.goal, set.claim_ids);
      executionStatusByKey.set(setKey, setExecutionStatus);
      counts.test_sets += 1;
      for (const branch of vvArray(set.branches)) {
        const branchKeys = ['branch_id', 'condition', 'attempt_ids', 'execution_status', 'claim_ids', 'steps'];
        if (Object.prototype.hasOwnProperty.call(vvObject(branch), 'no_material_claim_reason')) {
          branchKeys.push('no_material_claim_reason');
        }
        vvExactKeys(branch, branchKeys, 'invalid canonical V&V branch structure');
        const branchId = vvIdentifier(branch.branch_id);
        vvRequiredText(branch.condition);
        validateIdentifierList(branch.attempt_ids, vvAttemptId, 'invalid canonical V&V branch attempts');
        if (branch.no_material_claim_reason != null) vvRequiredText(branch.no_material_claim_reason);
        const branchExecutionStatus = vvStatus(branch.execution_status);
        const branchTarget = { ...setTarget, branch_id: branchId };
        const branchKey = add('BRANCH', branchTarget, setKey, branch.condition, branch.claim_ids);
        executionStatusByKey.set(branchKey, branchExecutionStatus);
        counts.branches += 1;
        for (const step of vvArray(branch.steps)) {
          const stepKeys = ['step_id', 'role', 'instruction', 'dependencies', 'expected_observables',
            'failure_behavior', 'cleanup_required', 'required', 'execution_classification', 'blocker_ids',
            'source_lines', 'source_sections', 'execution_status', 'claim_ids', 'commands'];
          if (Object.prototype.hasOwnProperty.call(vvObject(step), 'no_material_claim_reason')) {
            stepKeys.push('no_material_claim_reason');
          }
          vvExactKeys(step, stepKeys, 'invalid canonical V&V step structure');
          const stepId = vvIdentifier(step.step_id);
          vvIdentifier(step.role); vvRequiredText(step.instruction); vvIdentifier(step.execution_classification);
          validateTextList(step.dependencies, 'invalid canonical V&V step dependencies');
          validateTextList(step.expected_observables, 'invalid canonical V&V step expected observables');
          validateTextList(step.failure_behavior, 'invalid canonical V&V step failure behavior');
          validateIdentifierList(step.blocker_ids, vvIdentifier, 'invalid canonical V&V step blocker ids');
          if (typeof step.cleanup_required !== 'boolean' || typeof step.required !== 'boolean') {
            throw new Error('invalid canonical V&V step requirement');
          }
          if (step.no_material_claim_reason != null) vvRequiredText(step.no_material_claim_reason);
          const stepExecutionStatus = vvStatus(step.execution_status);
          const stepSource = assertStepSourceBinding(step, sourceIndex, sourceFile);
          if (stepSource.sourceLines.some((span) => span.start < sourceContext.line_start ||
            span.end > sourceContext.line_end) ||
            stepSource.sourceSections.some((section) => !contextHeadings.includes(section))) {
            throw new Error('canonical V&V step falls outside its test-set source context');
          }
          const stepTarget = { ...branchTarget, step_id: stepId };
          const stepKey = add('STEP', stepTarget, branchKey, step.instruction, step.claim_ids, step.required);
          executionStatusByKey.set(stepKey, stepExecutionStatus);
          counts.steps += 1;
          const commands = vvArray(step.commands);
          if (commands.length) counts.command_bearing_steps += 1;
          for (const command of commands) {
            const commandKeys = ['command_id', 'text', 'source', 'treatment', 'execution_status',
              'behavior_score', 'score_rationale', 'evidence_ids', 'finding_ids', 'attempt_ids', 'claim_ids'];
            const hasQualification = Object.prototype.hasOwnProperty.call(vvObject(command),
              'qualification_rationale');
            const hasInventory = Object.prototype.hasOwnProperty.call(command, 'inventory_id');
            const hasApplicability = Object.prototype.hasOwnProperty.call(command, 'applicability');
            if (hasQualification) commandKeys.push('qualification_rationale');
            if (hasInventory) commandKeys.push('inventory_id');
            if (hasApplicability) commandKeys.push('applicability');
            vvExactKeys(command, commandKeys, 'invalid canonical V&V command structure');
            const commandId = vvIdentifier(command.command_id);
            vvRawRequiredText(command.text); vvIdentifier(command.treatment);
            validateIdentifierList(command.evidence_ids, vvEvidenceId,
              'invalid canonical V&V command evidence ids');
            validateIdentifierList(command.finding_ids, vvIdentifier,
              'invalid canonical V&V command finding ids');
            validateIdentifierList(command.attempt_ids, vvAttemptId,
              'invalid canonical V&V command attempts');
            if (command.behavior_score != null && (!Number.isInteger(command.behavior_score) ||
              command.behavior_score < 1 || command.behavior_score > 3)) {
              throw new Error('invalid canonical V&V command behavior score');
            }
            if (command.score_rationale != null) vvRequiredText(command.score_rationale);
            if (hasQualification) vvRequiredText(command.qualification_rationale);
            if (hasInventory !== hasApplicability || (hasInventory && hasQualification)) {
              throw new Error('invalid canonical V&V command occurrence metadata');
            }
            if (hasInventory) {
              vvIdentifier(command.inventory_id); vvRequiredText(command.applicability);
            }
            const commandExecutionStatus = vvStatus(command.execution_status);
            const target = { page_id: pageId, test_set_id: testSetId, branch_id: branchId,
              step_id: stepId, command_id: commandId };
            const commandKey = add('COMMAND', target, stepKey, command.text, command.claim_ids);
            executionStatusByKey.set(commandKey, commandExecutionStatus);
            counts.command_carriers += 1;
            const source = vvExactKeys(command.source,
              ['file', 'section', 'line_start', 'line_end', 'source_type', 'text_sha256'],
              'invalid canonical command source');
            const sourceLine = source.line_start;
            if (source.file !== sourceFile || !Number.isInteger(sourceLine) || sourceLine < 1) {
              throw new Error('invalid canonical command source');
            }
            const sourceEnd = source.line_end;
            if (!Number.isInteger(sourceEnd) || sourceEnd < sourceLine || sourceEnd > sourceIndex.lines.length ||
              !stepSource.sourceLines.some((span) => span.start <= sourceLine && span.end >= sourceEnd) ||
              !stepSource.sourceSections.includes(vvSectionTitle(source.section)) ||
              !sourceIndex.lines.slice(sourceLine - 1, sourceEnd).join('\n').includes(command.text)) {
              throw new Error('invalid canonical command source span');
            }
            if (vvSectionTitle(source.section) !== vvSectionAtLine(sourceIndex, sourceLine)) {
              throw new Error('invalid canonical command source section');
            }
            if (vvSha256(source.text_sha256, 'invalid canonical command source text hash') !==
              crypto.createHash('sha256').update(command.text).digest('hex')) {
              throw new Error('stale canonical command source text');
            }
            const treatment = vvIdentifier(command.treatment);
            commandById.set(commandId, {
              ...target, route: pageRoute, procedureId: vvIdentifier(set.procedure_id),
              text: vvRawRequiredText(command.text), source: `${sourceFile}:${sourceLine}`, treatment,
              sourceContract: {
                file: sourceFile, section: vvSectionTitle(source.section), line_start: sourceLine,
                line_end: sourceEnd, source_type: vvIdentifier(source.source_type),
                text_sha256: vvSha256(source.text_sha256, 'invalid canonical command source text hash'),
              },
            });
          }
        }
      }
    }
  }
  const expected = vvObject(declaredCounts);
  vvExactKeys(expected, Object.keys(counts), 'invalid canonical V&V counts');
  for (const [name, actual] of Object.entries(counts)) {
    if (expected[name] !== actual) throw new Error('invalid canonical V&V count');
  }
  return { targets, commandById, pageById, pageByRoute, childrenByKey,
    targetClaimByKey, claimRefsByKey, executionStatusByKey, counts };
}
function validateVvSourceProvenance(sets, pages) {
  const source = vvExactKeys(sets.source,
    ['repository', 'branch', 'revision', 'tree', 'topology_snapshot_sha256',
      'safe_classification_sha256', 'reconciled_identity_method',
      'reconciled_primary_source_sha256', 'reconciled_rendered_source_sha256', 'working_tree_state_ref'],
    'invalid V&V source provenance');
  if (source.repository !== VV_REVIEWED_PACKAGE_IDENTITY.repository ||
    source.branch !== VV_REVIEWED_PACKAGE_IDENTITY.branch ||
    !/^[a-f0-9]{40}$/.test(source.revision) || !/^[a-f0-9]{40}$/.test(source.tree) ||
    source.reconciled_identity_method !==
      'PRIMARY_AND_RENDERED_SOURCE_SHA256_PLUS_FINAL_GIT_TREE') {
    throw new Error('invalid V&V source revision provenance');
  }
  vvSha256(source.topology_snapshot_sha256, 'invalid historical V&V topology snapshot');
  vvSha256(source.safe_classification_sha256, 'invalid V&V classification snapshot');
  vvSha256(source.reconciled_primary_source_sha256, 'invalid V&V primary-source snapshot');
  vvSha256(source.reconciled_rendered_source_sha256, 'invalid V&V rendered-source snapshot');
  if (source.reconciled_primary_source_sha256 !== VV_REVIEWED_PACKAGE_IDENTITY.primarySha256 ||
    source.reconciled_rendered_source_sha256 !== VV_REVIEWED_PACKAGE_IDENTITY.renderedSha256 ||
    source.safe_classification_sha256 !== VV_REVIEWED_PACKAGE_IDENTITY.classificationSha256) {
    throw new Error('unrecognized V&V reviewed-package identity');
  }
  const git = (...args) => execFileSync('git', args, {
    cwd: VV_REPOSITORY_ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'],
  }).trim();
  let historicalTree;
  try {
    git('cat-file', '-e', `${source.revision}^{commit}`);
    historicalTree = git('rev-parse', `${source.revision}^{tree}`);
  } catch {
    throw new Error('unresolvable V&V Git source provenance');
  }
  if (historicalTree !== source.tree) {
    throw new Error('stale V&V historical Git provenance');
  }
  const primarySnapshot = crypto.createHash('sha256').update(pages
    .map((page) => `${page.route}\0${page.source_sha256}\n`).join('')).digest('hex');
  const renderedSnapshot = crypto.createHash('sha256').update(pages
    .map((page) => `${page.route}\0${page.rendered_source_sha256}\n`).join('')).digest('hex');
  const classificationHash = crypto.createHash('sha256')
    .update(vvHistoricalSourceFile('host-docs-command-access.json', 'missing V&V classification source').bytes)
    .digest('hex');
  if (primarySnapshot !== source.reconciled_primary_source_sha256 ||
    renderedSnapshot !== source.reconciled_rendered_source_sha256 ||
    classificationHash !== source.safe_classification_sha256) {
    throw new Error('stale V&V current working-tree source binding');
  }
  const expectedWorkingTreeRef =
    'verification/evidence/2026-09-03-host-repository-rebase-01/result.md#pre-edit-working-tree-baseline';
  if (source.working_tree_state_ref !== expectedWorkingTreeRef) {
    throw new Error('invalid V&V pre-edit working-tree evidence reference');
  }
  const baselinePath = source.working_tree_state_ref.split('#', 1)[0];
  vvEvidenceRef(baselinePath);
  const baselineText = vvRepositoryFile(baselinePath, 'missing V&V pre-edit working-tree evidence').bytes
    .toString('utf8');
  if (!/^#{1,6}\s+Pre-edit working-tree baseline\s*$/mi.test(baselineText) ||
    !baselineText.includes('git status --short') || !baselineText.includes('git rev-parse HEAD') ||
    !/\| HEAD \| `[a-f0-9]{40}` \|/.test(baselineText) ||
    !/\| HEAD tree \| `[a-f0-9]{40}` \|/.test(baselineText) ||
    !/^\s*[ MADRCU?!]{1,2}\s+\S+/m.test(baselineText)) {
    throw new Error('incomplete V&V pre-edit working-tree evidence');
  }
  // `revision`/`tree` are the retained historical topology origin. Current
  // authored/rendered bytes are bound by the two source snapshots above; the
  // eventual Git tree/commit seals the complete package without creating a
  // self-invalidating parent-HEAD dependency.
  return {
    historicalTopologyOrigin: { revision: source.revision, tree: source.tree },
    currentContentBinding: {
      method: source.reconciled_identity_method,
      primarySha256: source.reconciled_primary_source_sha256,
      renderedSha256: source.reconciled_rendered_source_sha256,
    },
  };
}
function canonicalHostNavigationInventory() {
  const docs = vvObject(JSON.parse(vvHistoricalSourceFile('docs.json', 'invalid canonical Host navigation file')
    .bytes.toString('utf8')));
  const tabs = vvArray(vvObject(docs.navigation).tabs);
  const hostTabs = tabs.filter((tab) => vvObject(tab).tab === 'Host');
  if (hostTabs.length !== 1) throw new Error('invalid canonical Host navigation');
  const entries = [];
  for (const groupValue of vvArray(hostTabs[0].groups)) {
    const group = vvObject(groupValue);
    vvRequiredText(group.group);
    for (const page of vvArray(group.pages)) {
      if (typeof page !== 'string' || !/^host\/[A-Za-z0-9._/-]+$/.test(page) ||
        page.split('/').includes('..')) throw new Error('invalid canonical top-level Host route');
      entries.push({ route: `/${page}`, sourceFile: `${page}.mdx` });
    }
  }
  if (entries.length !== 40 || new Set(entries.map((entry) => entry.route)).size !== entries.length) {
    throw new Error('invalid canonical top-level Host route count');
  }
  return entries;
}
function vvCurrentSourceFile(relativePath, message = 'invalid current V&V source file') {
  const file = vvRepositoryFile(vvSafeRepositoryPath(relativePath, message), message);
  if (!file.bytes.length || file.bytes.length > VV_MAX_HISTORICAL_SOURCE_BYTES || file.bytes.includes(0)) {
    throw new Error(message);
  }
  try { new TextDecoder('utf-8', { fatal: true }).decode(file.bytes); } catch { throw new Error(message); }
  return file;
}
function currentHostNavigationInventory() {
  const docs = vvObject(JSON.parse(vvCurrentSourceFile('docs.json', 'invalid current Host navigation file')
    .bytes.toString('utf8')));
  const tabs = vvArray(vvObject(docs.navigation).tabs);
  const hostTabs = tabs.filter((tab) => vvObject(tab).tab === 'Host');
  if (hostTabs.length !== 1) throw new Error('invalid current Host navigation');
  const entries = [];
  const routes = new Set();
  const visitPages = (pages, depth = 0) => {
    if (depth > 16) throw new Error('invalid current Host navigation nesting');
    for (const item of vvArray(pages)) {
      if (typeof item === 'string') {
        if (!/^host\/[A-Za-z0-9._/-]+$/.test(item) || item.split('/').some((part) =>
          !part || part === '.' || part === '..')) throw new Error('invalid current Host route');
        const route = `/${item}`;
        if (routes.has(route)) throw new Error('duplicate current Host route');
        routes.add(route);
        entries.push({ route, sourceFile: `${item}.mdx` });
        continue;
      }
      const group = vvObject(item);
      // Mintlify groups may nest.  Do not silently treat arbitrary objects as
      // routes: a group must have a non-empty label and an explicit pages array.
      if (!Object.prototype.hasOwnProperty.call(group, 'pages') || !Array.isArray(group.pages) ||
        typeof group.group !== 'string' || !group.group.trim()) {
        throw new Error('invalid current Host navigation group');
      }
      visitPages(group.pages, depth + 1);
    }
  };
  const host = vvObject(hostTabs[0]);
  if (!Array.isArray(host.groups)) throw new Error('invalid current Host navigation groups');
  for (const group of host.groups) {
    const normalized = vvObject(group);
    if (typeof normalized.group !== 'string' || !normalized.group.trim() || !Array.isArray(normalized.pages)) {
      throw new Error('invalid current Host navigation group');
    }
    visitPages(normalized.pages);
  }
  if (!entries.length || entries.length > 500) throw new Error('invalid current Host navigation count');
  return entries;
}
function vvHash(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}
function currentSourceFreshness(canonical, supportLayers) {
  const currentNavigation = currentHostNavigationInventory();
  const baselineRoutes = new Set(canonical.pageByRoute.keys());
  const currentRoutes = new Set(currentNavigation.map((entry) => entry.route));
  const byRoute = new Map();
  for (const entry of currentNavigation) {
    const page = canonical.pageByRoute.get(entry.route);
    // A route cannot be declared without a safe regular MDX source, including
    // new routes that have no historical package entry yet.
    const primary = vvCurrentSourceFile(entry.sourceFile, 'invalid current Host page source').bytes;
    if (!page) {
      byRoute.set(entry.route, { state: 'UNVALIDATED', reason: 'new-current-route', sourceFile: entry.sourceFile });
      continue;
    }
    let changed = vvHash(primary) !== page.sourceSha256;
    for (const dependency of page.renderedDependencies) {
      const current = vvCurrentSourceFile(dependency.sourceFile,
        'invalid current rendered V&V dependency source').bytes;
      if (vvHash(current) !== dependency.sourceSha256) changed = true;
    }
    byRoute.set(entry.route, { state: changed ? 'STALE' : 'CURRENT',
      reason: changed ? 'historical-primary-or-rendered-dependency-changed' : 'matches-reviewed-snapshot',
      sourceFile: entry.sourceFile });
  }
  for (const route of baselineRoutes) {
    if (!currentRoutes.has(route)) byRoute.set(route, { state: 'HISTORICAL_ONLY', reason: 'route-removed-from-current-host-navigation' });
  }
  const supportByRoute = new Map();
  for (const support of supportLayers) {
    const current = [
      [support.sourceFile, support.sourceSha256], [support.fragmentFile, support.fragmentSha256],
      [support.centralReferenceFile, support.centralReferenceSha256],
    ];
    const changed = current.some(([file, hash]) => vvHash(vvCurrentSourceFile(file,
      'invalid current V&V support source').bytes) !== hash);
    supportByRoute.set(support.route, { state: changed ? 'STALE' : 'CURRENT',
      reason: changed ? 'historical-wrapper-snippet-or-central-reference-changed' : 'matches-reviewed-snapshot' });
  }
  return { currentNavigation, byRoute, supportByRoute,
    baselineHostRouteCount: baselineRoutes.size, currentHostRouteCount: currentNavigation.length };
}
function projectionTargetKey(record, canonicalTargets) {
  const level = vvIdentifier(record.level);
  const fields = VV_STATUS_TARGET_FIELDS[level];
  if (!fields) throw new Error('invalid V&V status level');
  const target = vvObject(record.target);
  if (Object.keys(target).length !== fields.length || fields.some((field) => !(field in target))) {
    throw new Error('invalid V&V status target');
  }
  for (const field of fields) vvIdentifier(target[field]);
  const key = vvStatusKey(level, target);
  if (!canonicalTargets.has(key)) throw new Error('unknown V&V status target');
  return key;
}
function vvSourceRef(value, subjectSourceFile) {
  vvExactKeys(value, ['repository', 'revision', 'path', 'locator', 'source_kind'], 'invalid V&V authority source');
  const source = {
    repository: vvRequiredText(value.repository), revision: vvRequiredText(value.revision),
    path: vvRequiredText(value.path), locator: vvRequiredText(value.locator),
    sourceKind: vvIdentifier(value.source_kind),
  };
  if (!new Set(['vast-ai/docs', 'vast-ai/vast-cli', 'vast-ai/self-test']).has(source.repository)) {
    throw new Error('unapproved V&V authority repository');
  }
  const contracts = {
    CANONICAL_API_CLIENT_SOURCE: {
      repository: 'vast-ai/vast-cli',
      paths: new Map([
        ['vastai/api/instances.py', new Set([
          'build_volume_info and build_create_instance_payload',
        ])],
        ['vastai/api/machines.py', new Set([
          'list_machine request payload fields vol_size and vol_price',
        ])],
        ['vastai/api/storage.py', new Set([
          'clone_volume source owned-volume ID and destination offer ID request builder',
          'show_volumes, create_volume, delete_volume, list_volume, list_volumes, and unlist_volume request builders',
        ])],
      ]),
    },
    CANONICAL_CLI_SOURCE: {
      repository: 'vast-ai/vast-cli',
      paths: new Map([
        ['vastai/cli/commands/instances.py', new Set([
          'create__instance volume-link arguments and request delegation',
        ])],
        ['vastai/cli/commands/machines.py', new Set([
          'list_machine_impl, list__machine, and list__machines volume-offer arguments',
        ])],
        ['vastai/cli/commands/storage.py', new Set([
          'clone__volume registration and source/destination volume syntax',
          'search__volumes, create__volume, delete__volume, show__volumes, list__volume, list__volumes, and unlist__volume command registrations',
        ])],
        ['vastai/cli/commands/billing.py', new Set([
          'show__earnings command registration and usage contract for `vastai show earnings`',
        ])],
        ['vastai/cli/commands/keys.py', new Set([
          'create__api_key command registration and usage contract for `vastai create api-key`',
          'delete__api_key command registration and usage contract for `vastai delete api-key`',
          'show__api_keys command registration and usage contract for `vastai show api-keys`',
        ])],
        ['vastai/cli/commands/metrics.py', new Set([
          'metrics__gpu command registration and usage contract for `vastai metrics gpu`',
          'metrics__gpu_locations command registration and usage contract for `vastai metrics gpu-locations`',
          'metrics__gpu_trends command registration and usage contract for `vastai metrics gpu-trends`',
        ])],
        ['vastai/cli/commands/teams.py', new Set([
          'create__team command registration and usage contract for `vastai create team`',
          'create__team_role command registration and usage contract for `vastai create team-role`',
          'destroy__team command registration and usage contract for `vastai destroy team`',
          'invite__member command registration and usage contract for `vastai invite member`',
          'remove__member command registration and usage contract for `vastai remove member`',
          'remove__team_role command registration and usage contract for `vastai remove team-role`',
          'show__members command registration and usage contract for `vastai show members`',
          'show__team_role command registration and usage contract for `vastai show team-role`',
          'show__team_roles command registration and usage contract for `vastai show team-roles`',
          'update__team_role command registration and usage contract for `vastai update team-role`',
        ])],
        ['vastai/cli/self_test/machine_diagnostics.py', new Set([
          'exact historical self-test requirement and failure catalogs consumed by the generator',
        ])],
      ]),
    },
    CANONICAL_DOC_GENERATOR_SOURCE: {
      repository: 'vast-ai/docs',
      paths: new Map([['scripts/generate_self_test_reference.py', new Set([
        'render_page source extraction and deterministic self-test reference generation',
      ])]]),
    },
    CANONICAL_SELF_TEST_SOURCE: {
      repository: 'vast-ai/self-test',
      paths: new Map([['remote.py', new Set([
        'exact historical EVENT_CATALOG consumed by the generator',
      ])]]),
    },
    OPENAPI_SOURCE: {
      repository: 'vast-ai/docs',
      paths: new Map([
        ['api-reference/openapi/yaml/list_volume.yaml', new Set(['list_volume and list_volumes request schemas'])],
        ['api-reference/openapi/yaml/list_machine.yaml', new Set(['list machine request schema fields vol_size and vol_price'])],
      ]),
    },
    ROUTE_CONFIGURATION: {
      repository: 'vast-ai/docs',
      paths: new Map([['docs.json', new Set(['Host, CLI, SDK, and guide route declarations'])]]),
    },
    ROUTE_DESTINATION_SOURCE: { repository: 'vast-ai/docs', routeDestination: true },
  };
  const contract = contracts[source.sourceKind];
  const allowedLocators = contract?.paths?.get(source.path);
  const destinationMatch = contract?.routeDestination
    ? source.locator.match(/^route (\/[A-Za-z0-9._/-]+)(?: fragment #([A-Za-z0-9._-]+))?$/) : null;
  const validRouteDestination = Boolean(destinationMatch &&
    source.path === `${destinationMatch[1].slice(1)}.mdx`);
  if (!contract || source.repository !== contract.repository ||
    (!allowedLocators?.has(source.locator) && !validRouteDestination)) {
    throw new Error('mismatched V&V authority source kind or locator');
  }
  if (!/^[A-Za-z0-9._/-]+$/.test(source.path) ||
    source.path.split('/').some((segment) => !segment || segment === '.' || segment === '..') ||
    source.repository === 'retained-evidence' || source.path === subjectSourceFile ||
    (source.repository === 'vast-ai/docs' && /^host\//.test(source.path) && !validRouteDestination)) {
    throw new Error('documentation under review cannot be its own V&V authority');
  }
  if (source.repository === 'vast-ai/docs') {
    const sourceBytes = vvHistoricalSourceFile(source.path, 'invalid V&V authority source file').bytes;
    const actualRevision = `sha256:${crypto.createHash('sha256').update(sourceBytes).digest('hex')}`;
    if (source.revision !== actualRevision) throw new Error('stale V&V authority source');
    const sourceText = sourceBytes.toString('utf8');
    let requiredSourceTokens;
    if (validRouteDestination) requiredSourceTokens = [];
    else if (source.sourceKind === 'ROUTE_CONFIGURATION' && source.path === 'docs.json') {
      requiredSourceTokens = ['"Host"', '"CLI"', '"SDK"'];
    } else if (source.sourceKind === 'CANONICAL_DOC_GENERATOR_SOURCE' &&
      source.path === 'scripts/generate_self_test_reference.py') {
      requiredSourceTokens = ['def render_page', 'load_cli_metadata(vast_cli)',
        'literal_assignment(self_test / "remote.py", "EVENT_CATALOG")'];
    } else if (source.sourceKind === 'OPENAPI_SOURCE' &&
      source.path === 'api-reference/openapi/yaml/list_volume.yaml') {
      requiredSourceTokens = ['/api/v0/volumes/', 'list volume', 'list volumes'];
    } else if (source.sourceKind === 'OPENAPI_SOURCE' &&
      source.path === 'api-reference/openapi/yaml/list_machine.yaml') {
      requiredSourceTokens = ['vol_size', 'vol_price'];
    } else {
      throw new Error('unresolved V&V authority source locator contract');
    }
    const fragment = destinationMatch?.[2] || null;
    const fragmentIds = vvSourceFragmentIds(sourceText);
    if (requiredSourceTokens.some((token) => !sourceText.includes(token)) ||
      (fragment && !fragmentIds.has(fragment))) {
      throw new Error('unresolved V&V authority source locator');
    }
  } else {
    const sourceText = vvPinnedExternalSource(source.repository, source.revision, source.path);
    const locatorIdentifiers = [...new Set(source.locator.match(/[A-Za-z][A-Za-z0-9_]{2,}/g) || [])]
      .filter((token) => token.includes('_'));
    const additionalTokens = source.sourceKind === 'CANONICAL_CLI_SOURCE' &&
      source.path === 'vastai/cli/self_test/machine_diagnostics.py'
      ? ['SYSTEM_RAM_REQUIREMENT_CAP_MIB', 'requirement_failure', 'no_offer_failure'] : [];
    if (![...locatorIdentifiers, ...additionalTokens].length ||
      [...locatorIdentifiers, ...additionalTokens].some((token) => !sourceText.includes(token))) {
      throw new Error('unresolved pinned external V&V authority source locator');
    }
  }
  return source;
}
function vvMaterialSourceRef(value, subjectSourceFile) {
  return vvSourceRef(value, subjectSourceFile);
}
function vvHeadingsForSubject(value, pageMeta) {
  const headings = vvArray(value).map(vvSectionTitle);
  if (!headings.length || new Set(headings).size !== headings.length) {
    throw new Error('invalid V&V subject headings');
  }
  const available = new Set(['Introduction', ...pageMeta.sourceIndex.headings.map((heading) => heading.title)]);
  if (headings.some((heading) => !available.has(heading))) throw new Error('unknown V&V subject heading');
  return headings;
}
function vvSpanOverlapsHeading(span, heading, sourceIndex) {
  if (heading === 'Introduction') {
    const firstHeading = sourceIndex.headings[0]?.start || sourceIndex.lines.length + 1;
    return span.start < firstHeading;
  }
  return sourceIndex.headings.some((candidate, index) => {
    if (candidate.title !== heading) return false;
    const nextStart = sourceIndex.headings.slice(index + 1)
      .find((next) => next.level <= candidate.level)?.start || sourceIndex.lines.length + 1;
    return candidate.start <= span.end && nextStart > span.start;
  });
}
function vvRenderedVia(value, pageMeta, sourceFile, message) {
  if (value == null) {
    if (sourceFile !== pageMeta.sourceFile) throw new Error(message);
    return null;
  }
  const rendered = vvExactKeys(value,
    ['component', 'host_source_file', 'import_line', 'insertion_line'], message);
  const component = vvIdentifier(rendered.component);
  const hostSourceFile = vvRequiredText(rendered.host_source_file);
  if (sourceFile === pageMeta.sourceFile || hostSourceFile !== pageMeta.sourceFile ||
    !Number.isInteger(rendered.import_line) || !Number.isInteger(rendered.insertion_line)) {
    throw new Error(message);
  }
  const dependency = pageMeta.renderedDependencies.find((item) =>
    item.component === component && item.sourceFile === sourceFile &&
    item.importLine === rendered.import_line && item.insertionLine === rendered.insertion_line);
  if (!dependency) throw new Error(message);
  return { component, hostSourceFile, importLine: rendered.import_line,
    insertionLine: rendered.insertion_line, dependency };
}
function vvComparableRenderedVia(value) {
  return value ? { component: value.component, hostSourceFile: value.hostSourceFile,
    importLine: value.importLine, insertionLine: value.insertionLine } : null;
}
function vvEvidenceIds(value, allEvidenceIds, message, { allowEmpty = false } = {}) {
  const ids = vvArray(value).map(vvEvidenceId);
  if ((!allowEmpty && !ids.length) || new Set(ids).size !== ids.length ||
    ids.some((id) => !allEvidenceIds.has(id))) throw new Error(message);
  return ids;
}
function loadContractBindingManifests(results, attemptsById, allEvidenceIds, evidenceRefById,
  canonical, scoreByCommand) {
  const loadEnvelope = (value, expectedMethod, message) => {
    vvExactKeys(value, ['evidence_id', 'attempt_id', 'method', 'limitations', 'bindings'], message);
    const evidenceId = vvEvidenceId(value.evidence_id);
    const attemptId = vvAttemptId(value.attempt_id);
    const attempt = attemptsById.get(attemptId);
    if (allEvidenceIds.has(evidenceId) || !attempt || attempt.status !== 'PASS' ||
      attempt.executionState !== 'EXECUTED' || attempt.supersededBy ||
      !attempt.evidenceRefSha256 ||
      vvIdentifier(value.method) !== expectedMethod) throw new Error(message);
    allEvidenceIds.add(evidenceId);
    evidenceRefById.set(evidenceId, attempt.evidenceRef);
    return { evidenceId, attemptId, method: expectedMethod,
      limitations: vvRequiredText(value.limitations), bindings: vvArray(value.bindings) };
  };
  const materialRows = vvArray(results.material_claim_results || []);
  const supportRows = vvArray(results.support_layer_results || []);
  if (results.counts?.material_claim_results !== materialRows.length || materialRows.length !== 3 ||
    results.counts?.support_layer_results !== supportRows.length || supportRows.length !== 1) {
    throw new Error('invalid V&V contract-binding manifest count');
  }
  const rowsByMethod = new Map(materialRows.map((row) => [row.method, row]));
  if (rowsByMethod.size !== materialRows.length) throw new Error('duplicate material V&V binding manifest method');
  const materialEnvelope = loadEnvelope(rowsByMethod.get('MATERIAL_CLAIM_OCCURRENCE_AND_DISPOSITION_MANIFEST'),
    'MATERIAL_CLAIM_OCCURRENCE_AND_DISPOSITION_MANIFEST', 'invalid material V&V binding manifest');
  const navigationEnvelope = loadEnvelope(rowsByMethod.get('STATIC_LOCAL_ROUTE_AND_FRAGMENT_RESOLUTION'),
    'STATIC_LOCAL_ROUTE_AND_FRAGMENT_RESOLUTION', 'invalid navigation V&V binding manifest');
  const commandEnvelope = loadEnvelope(rowsByMethod.get('EXACT_FENCED_COMMAND_TO_CARRIER_EVIDENCE_BINDING'),
    'EXACT_FENCED_COMMAND_TO_CARRIER_EVIDENCE_BINDING', 'invalid command-claim V&V binding manifest');
  const materialByClaim = new Map();
  const materialRoles = {
    PASS: new Set(['CLAIM_SUITABLE_BOUNDED_SUPPORT']),
    FAIL: new Set(['CONFIRMED_CITATION_OR_SOURCE_BINDING_DEFECT']),
    BLOCKED: new Set(['UNAVAILABLE_PREREQUISITE_DISPOSITION']),
    UNVALIDATED: new Set(['PARTIAL_EVIDENCE_BOUND_STATUS_UNCHANGED', 'OCCURRENCE_ACCOUNTING_ONLY']),
  };
  for (const bindingValue of materialEnvelope.bindings) {
    vvExactKeys(bindingValue, ['claim_id', 'page_id', 'status', 'source_file', 'heading', 'source_spans',
      'source_text_sha256', 'rendered_via', 'evidence_role', 'required_evidence_types', 'satisfied_evidence_types',
      'partially_supported_evidence_types', 'supporting_evidence_ids', 'command_evidence_binding', 'limitations'],
    'invalid material V&V claim binding');
    const claimId = vvIdentifier(bindingValue.claim_id);
    const pageId = vvIdentifier(bindingValue.page_id);
    const pageMeta = canonical.pageById.get(pageId);
    const sourceFile = vvRequiredText(bindingValue.source_file);
    if (!pageMeta) throw new Error('invalid material V&V claim binding page');
    const renderedVia = vvRenderedVia(bindingValue.rendered_via, pageMeta, sourceFile,
      'invalid rendered material V&V claim binding');
    const status = vvStatus(bindingValue.status);
    const evidenceRole = vvIdentifier(bindingValue.evidence_role);
    if (materialByClaim.has(claimId) || !materialRoles[status]?.has(evidenceRole)) {
      throw new Error('invalid material V&V claim binding identity');
    }
    const limitations = vvArray(bindingValue.limitations).map(vvRequiredText);
    if (!limitations.length) throw new Error('missing material V&V binding limitation');
    const requiredEvidenceTypes = vvArray(bindingValue.required_evidence_types).map(vvIdentifier);
    const satisfiedEvidenceTypes = vvArray(bindingValue.satisfied_evidence_types).map(vvIdentifier);
    const partiallySupportedEvidenceTypes = vvArray(bindingValue.partially_supported_evidence_types)
      .map(vvIdentifier);
    if (!requiredEvidenceTypes.length ||
      [requiredEvidenceTypes, satisfiedEvidenceTypes, partiallySupportedEvidenceTypes].some((types) =>
        new Set(types).size !== types.length || types.some((type) => !VV_REQUIRED_EVIDENCE_TYPES.has(type))) ||
      [...satisfiedEvidenceTypes, ...partiallySupportedEvidenceTypes].some((type) =>
        !requiredEvidenceTypes.includes(type)) ||
      satisfiedEvidenceTypes.some((type) => partiallySupportedEvidenceTypes.includes(type))) {
      throw new Error('invalid material V&V evidence-lane binding');
    }
    materialByClaim.set(claimId, {
      envelopeEvidenceId: materialEnvelope.evidenceId, pageId,
      status, sourceFile, renderedVia,
      heading: vvSectionTitle(bindingValue.heading), sourceSpans: vvArray(bindingValue.source_spans),
      sourceTextSha256: vvSha256(bindingValue.source_text_sha256),
      evidenceRole,
      requiredEvidenceTypes, satisfiedEvidenceTypes, partiallySupportedEvidenceTypes,
      supportingEvidenceIds: vvArray(bindingValue.supporting_evidence_ids).map(vvEvidenceId),
      commandEvidenceBinding: bindingValue.command_evidence_binding,
      limitations,
    });
  }
  const navigationByClaim = new Map();
  for (const bindingValue of navigationEnvelope.bindings) {
    vvExactKeys(bindingValue, ['claim_id', 'page_id', 'status', 'source_file', 'heading', 'source_spans',
      'source_text_sha256', 'destinations', 'evidence_role'], 'invalid navigation V&V claim binding');
    const claimId = vvIdentifier(bindingValue.claim_id);
    const sourceFile = vvRequiredText(bindingValue.source_file);
    if (navigationByClaim.has(claimId) || bindingValue.status !== 'PASS' ||
      bindingValue.evidence_role !== 'EXACT_LOCAL_ROUTE_AND_FRAGMENT_RESOLUTION') {
      throw new Error('invalid navigation V&V claim binding identity');
    }
    const destinations = vvArray(bindingValue.destinations).map((destinationValue) => {
      const destination = vvExactKeys(destinationValue,
        ['href', 'route', 'fragment', 'target_file', 'target_sha256'],
        'invalid navigation V&V destination binding');
      const href = vvRequiredText(destination.href);
      const route = vvRequiredText(destination.route);
      const fragment = destination.fragment == null ? null : vvIdentifier(destination.fragment);
      const targetFile = vvRequiredText(destination.target_file);
      const targetSha256 = vvSha256(destination.target_sha256, 'invalid navigation destination hash');
      if (!/^\/[A-Za-z0-9._/-]+$/.test(route) || route.split('/').includes('..') ||
        href !== `${route}${fragment ? `#${fragment}` : ''}` || targetFile !== `${route.slice(1)}.mdx`) {
        throw new Error('mismatched navigation V&V destination route');
      }
      const sourceRef = vvSourceRef({
        repository: 'vast-ai/docs', revision: `sha256:${targetSha256}`, path: targetFile,
        locator: `route ${route}${fragment ? ` fragment #${fragment}` : ''}`,
        source_kind: 'ROUTE_DESTINATION_SOURCE',
      }, sourceFile);
      return { href, route, fragment, targetFile, targetSha256, sourceRef };
    });
    if (!destinations.length || new Set(destinations.map((destination) => destination.href)).size !== destinations.length) {
      throw new Error('invalid navigation V&V destination coverage');
    }
    navigationByClaim.set(claimId, {
      envelopeEvidenceId: navigationEnvelope.evidenceId, pageId: vvIdentifier(bindingValue.page_id),
      status: 'PASS', sourceFile, heading: vvSectionTitle(bindingValue.heading),
      sourceSpans: vvArray(bindingValue.source_spans),
      sourceTextSha256: vvSha256(bindingValue.source_text_sha256), destinations,
      evidenceRole: bindingValue.evidence_role,
    });
  }
  const commandByClaim = new Map();
  for (const bindingValue of commandEnvelope.bindings) {
    vvExactKeys(bindingValue, ['claim_id', 'command_id', 'page_id', 'source_file', 'heading', 'source_spans',
      'source_text_sha256', 'command_source', 'score', 'command_execution_status', 'prior_claim_status',
      'current_claim_status', 'direct_evidence_ids', 'decision'], 'invalid command-claim V&V binding');
    const claimId = vvIdentifier(bindingValue.claim_id);
    const commandId = vvIdentifier(bindingValue.command_id);
    const command = canonical.commandById.get(commandId);
    const score = scoreByCommand.get(commandId);
    const commandSource = vvExactKeys(bindingValue.command_source,
      ['file', 'section', 'line_start', 'line_end', 'source_type', 'text_sha256'],
      'invalid command-claim source binding');
    if (commandByClaim.has(claimId) || !command || !score || !Number.isInteger(bindingValue.score) ||
      bindingValue.score !== score.value || vvStatus(bindingValue.command_execution_status) !== score.executionStatus ||
      bindingValue.page_id !== command.page_id || Object.entries(command.sourceContract || {})
        .some(([field, expected]) => commandSource[field] !== expected)) {
      throw new Error('mismatched command-claim V&V binding target');
    }
    const priorClaimStatus = vvStatus(bindingValue.prior_claim_status);
    const currentClaimStatus = vvStatus(bindingValue.current_claim_status);
    const decision = vvIdentifier(bindingValue.decision);
    const directEvidenceIds = vvArray(bindingValue.direct_evidence_ids).map(vvEvidenceId);
    if (JSON.stringify(directEvidenceIds) !== JSON.stringify(score.directEvidenceIds)) {
      throw new Error('mismatched command-claim direct evidence binding');
    }
    const decisionIsValid =
      (decision === 'BOUNDED_PASS_FROM_SCORE_3_DIRECT_EVIDENCE' && score.value === 3 &&
        score.executionStatus === 'PASS' && priorClaimStatus === 'UNVALIDATED' && currentClaimStatus === 'PASS') ||
      (decision === 'EXACT_BLOCKER_PROPAGATED' && score.value === 2 && score.executionStatus === 'BLOCKED' &&
        priorClaimStatus === 'UNVALIDATED' && currentClaimStatus === 'BLOCKED') ||
      (decision === 'ADVERSE_EVIDENCE_BOUND_WITHOUT_OVERBROAD_CLAIM_FAIL' && score.value === 1 &&
        score.executionStatus === 'FAIL' && priorClaimStatus === 'UNVALIDATED' && currentClaimStatus === 'UNVALIDATED') ||
      (decision === 'PARTIAL_EVIDENCE_BOUND_STATUS_UNCHANGED' && priorClaimStatus === 'UNVALIDATED' &&
        currentClaimStatus === 'UNVALIDATED' && score.executionStatus !== 'BLOCKED' && score.executionStatus !== 'FAIL');
    if (!decisionIsValid) throw new Error('invalid command-claim V&V decision');
    commandByClaim.set(claimId, {
      envelopeEvidenceId: commandEnvelope.evidenceId, claimId, commandId,
      pageId: vvIdentifier(bindingValue.page_id), sourceFile: vvRequiredText(bindingValue.source_file),
      heading: vvSectionTitle(bindingValue.heading), sourceSpans: vvArray(bindingValue.source_spans),
      sourceTextSha256: vvSha256(bindingValue.source_text_sha256), score: score.value,
      commandExecutionStatus: score.executionStatus, priorClaimStatus, currentClaimStatus,
      directEvidenceIds, decision, raw: bindingValue,
    });
  }
  const supportEnvelope = loadEnvelope(supportRows[0],
    'STATIC_WRAPPER_FRAGMENT_CENTRAL_REFERENCE_BINDING', 'invalid support-layer V&V binding manifest');
  const supportById = new Map();
  for (const bindingValue of supportEnvelope.bindings) {
    vvExactKeys(bindingValue, ['support_id', 'status', 'layer', 'route', 'source_file', 'source_sha256',
      'fragment_file', 'fragment_sha256', 'central_reference_file', 'central_reference_route',
      'central_reference_sha256', 'evidence_role'], 'invalid support-layer V&V binding');
    const supportId = vvIdentifier(bindingValue.support_id);
    if (supportById.has(supportId) || bindingValue.status !== 'PASS' ||
      bindingValue.evidence_role !== 'EXACT_STATIC_SUPPORT_LAYER_BINDING') {
      throw new Error('invalid support-layer V&V binding identity');
    }
    supportById.set(supportId, {
      envelopeEvidenceId: supportEnvelope.evidenceId, status: 'PASS', layer: vvIdentifier(bindingValue.layer),
      route: vvCanonicalRoute(bindingValue.route), sourceFile: vvRequiredText(bindingValue.source_file),
      sourceSha256: vvSha256(bindingValue.source_sha256), fragmentFile: vvRequiredText(bindingValue.fragment_file),
      fragmentSha256: vvSha256(bindingValue.fragment_sha256),
      centralReferenceFile: vvRequiredText(bindingValue.central_reference_file),
      centralReferenceRoute: vvRequiredText(bindingValue.central_reference_route),
      centralReferenceSha256: vvSha256(bindingValue.central_reference_sha256),
      evidenceRole: bindingValue.evidence_role,
    });
  }
  return { materialByClaim, navigationByClaim, commandByClaim, supportById,
    materialEnvelope, navigationEnvelope, commandEnvelope, supportEnvelope };
}
function loadClaimAndSupportContracts(sets, canonical, allEvidenceIds, evidenceRefById,
  procedureEvidence, commandEvidenceById, bindingManifests) {
  const navEntries = canonicalHostNavigationInventory();
  if (navEntries.length !== canonical.pageByRoute.size || navEntries.some((entry) =>
    canonical.pageByRoute.get(entry.route)?.sourceFile !== entry.sourceFile)) {
    throw new Error('V&V primary-page inventory does not match canonical Host navigation');
  }
  const evidenceTouchesPage = (evidenceId, pageId, requiredStatus = null) => {
    const procedure = procedureEvidence.get(evidenceId);
    if (procedure && [...procedure.targets].some(([targetKey, status]) =>
      canonical.targets.get(targetKey)?.page_id === pageId && (!requiredStatus || status === requiredStatus))) return true;
    const commandEvidence = commandEvidenceById.get(evidenceId);
    return Boolean(commandEvidence && (!requiredStatus || commandEvidence.status === requiredStatus) &&
      [...commandEvidence.commandIds].some((commandId) => canonical.commandById.get(commandId)?.page_id === pageId));
  };
  const evidenceSupportsClaim = (evidenceId, claimId, pageId, requiredStatus = null) => {
    const navigation = bindingManifests.navigationByClaim.get(claimId);
    if (navigation?.envelopeEvidenceId === evidenceId && navigation.pageId === pageId &&
      (!requiredStatus || navigation.status === requiredStatus)) return true;
    const commandBinding = bindingManifests.commandByClaim.get(claimId);
    if (commandBinding) {
      if (!commandBinding.directEvidenceIds.includes(evidenceId) || commandBinding.pageId !== pageId ||
        (requiredStatus && commandBinding.currentClaimStatus !== requiredStatus)) return false;
      const commandEvidence = commandEvidenceById.get(evidenceId);
      if (commandEvidence?.commandIds.has(commandBinding.commandId)) return true;
      const procedure = procedureEvidence.get(evidenceId);
      const command = canonical.commandById.get(commandBinding.commandId);
      return Boolean(procedure && command &&
        procedure.targets.has(vvStatusKey('COMMAND', command)));
    }
    const procedure = procedureEvidence.get(evidenceId);
    if (procedure && [...procedure.targets].some(([targetKey, status]) =>
      (!requiredStatus || status === requiredStatus) &&
      canonical.targets.get(targetKey)?.page_id === pageId &&
      canonical.claimRefsByKey.get(targetKey)?.includes(claimId))) return true;
    const commandEvidence = commandEvidenceById.get(evidenceId);
    return Boolean(commandEvidence && (!requiredStatus || commandEvidence.status === requiredStatus) &&
      [...commandEvidence.commandIds].some((commandId) => {
        const command = canonical.commandById.get(commandId);
        return command?.page_id === pageId &&
          canonical.claimRefsByKey.get(vvStatusKey('COMMAND', command))?.includes(claimId);
      }));
  };
  const materialClaims = [];
  const passageBlocksByIndex = new Map();
  const materialClaimsById = new Map();
  const materialClaimsByPage = new Map([...canonical.pageById.keys()].map((pageId) => [pageId, []]));
  const materialStatusCounts = new Map([...VV_TARGET_STATUSES].map((status) => [status, 0]));
  for (const value of vvArray(sets.material_claims)) {
    vvExactKeys(value, ['claim_id', 'page_id', 'scope', 'claim', 'evidence_requirement', 'citation',
      'authority', 'current', 'next_action'],
      'invalid material V&V claim record');
    const claimId = vvIdentifier(value.claim_id);
    const pageId = vvIdentifier(value.page_id);
    const pageMeta = canonical.pageById.get(pageId);
    if (!pageMeta || materialClaimsById.has(claimId)) throw new Error('invalid material V&V claim identity');
    const scope = vvExactKeys(value.scope,
      ['route', 'source_file', 'heading', 'source_spans', 'source_text_sha256', 'rendered_via'],
      'invalid material V&V claim scope');
    const sourceFile = vvRequiredText(scope.source_file);
    if (vvCanonicalRoute(scope.route) !== pageMeta.route) {
      throw new Error('mismatched material V&V claim page');
    }
    const renderedVia = vvRenderedVia(scope.rendered_via, pageMeta, sourceFile,
      'mismatched rendered material V&V claim scope');
    const claimSourceIndex = renderedVia?.dependency.sourceIndex || pageMeta.sourceIndex;
    const availableHeadings = new Set(['Introduction', ...claimSourceIndex.headings.map((heading) => heading.title)]);
    const headingLabel = vvSectionTitle(scope.heading);
    const headings = availableHeadings.has(headingLabel)
      ? [headingLabel] : headingLabel.split(/\s+\/\s+/).map(vvSectionTitle);
    if (!headings.length || headings.some((heading) => !availableHeadings.has(heading))) {
      throw new Error('unknown material V&V claim heading');
    }
    const spans = vvArray(scope.source_spans).map((span) => vvSourceSpan(span, claimSourceIndex,
      'invalid material V&V claim source span'));
    if (!spans.length || spans.some((span) => !headings.some((heading) =>
      vvSpanOverlapsHeading(span, heading, claimSourceIndex))) ||
      headings.some((heading) => !spans.some((span) =>
        vvSpanOverlapsHeading(span, heading, claimSourceIndex)))) {
      throw new Error('mismatched material V&V claim heading/span');
    }
    const sourceText = spans.map((span) =>
      claimSourceIndex.lines.slice(span.start - 1, span.end).join('\n')).join('\n');
    if (vvSha256(scope.source_text_sha256, 'invalid material V&V claim source hash') !==
      crypto.createHash('sha256').update(sourceText).digest('hex')) {
      throw new Error('stale material V&V claim source');
    }
    vvExactKeys(value.claim, ['text', 'kind', 'claim_limit'], 'invalid material V&V claim');
    const rawClaimText = vvRawRequiredText(value.claim.text);
    const claim = {
      text: vvText(rawClaimText), kind: vvIdentifier(value.claim.kind),
      claimLimit: vvRequiredText(value.claim.claim_limit),
    };
    vvExactKeys(value.evidence_requirement, ['types', 'citation_required', 'rationale'],
      'invalid material V&V evidence requirement');
    const requiredEvidenceTypes = vvArray(value.evidence_requirement.types).map(vvIdentifier);
    if (!requiredEvidenceTypes.length || new Set(requiredEvidenceTypes).size !== requiredEvidenceTypes.length ||
      requiredEvidenceTypes.some((type) => !VV_REQUIRED_EVIDENCE_TYPES.has(type)) ||
      typeof value.evidence_requirement.citation_required !== 'boolean') {
      throw new Error('invalid material V&V evidence requirement');
    }
    vvRequiredText(value.evidence_requirement.rationale);
    const citation = vvExactKeys(value.citation, ['required', 'state', 'refs', 'assessment'],
      'invalid material V&V citation contract');
    if (typeof citation.required !== 'boolean' ||
      citation.required !== value.evidence_requirement.citation_required) {
      throw new Error('mismatched material V&V citation requirement');
    }
    const citationState = vvIdentifier(citation.state);
    const citationRefs = vvArray(citation.refs).map((refValue) => {
      vvExactKeys(refValue, ['href', 'kind'], 'invalid material V&V citation reference');
      const href = refValue.href;
      if (typeof href !== 'string' || !href || href.length > 2000 || /[\u0000-\u001f\u007f]/.test(href)) {
        throw new Error('invalid material V&V citation href');
      }
      const kind = vvIdentifier(refValue.kind);
      if (kind !== vvCitationRefKind(href)) {
        throw new Error('mismatched material V&V citation reference kind');
      }
      vvValidateCitationHref(href, pageMeta);
      return { href, kind };
    });
    const extractedCitationRefs = vvExtractCitationRefs(sourceText);
    const hasPotentiallyAuthoritativeCitation = citationRefs.some((ref) =>
      ref.kind === 'AUTHORITATIVE_SOURCE_CANDIDATE');
    if (JSON.stringify(citationRefs) !== JSON.stringify(extractedCitationRefs) ||
      (!citation.required && citationState !== 'NOT_REQUIRED') ||
      (citation.required && !hasPotentiallyAuthoritativeCitation && citationState !== 'ABSENT') ||
      (citation.required && hasPotentiallyAuthoritativeCitation && citationState !== 'PRESENT_UNVERIFIED')) {
      throw new Error('mismatched material V&V citation/source binding');
    }
    const citationAssessment = vvRequiredText(citation.assessment);
    vvExactKeys(value.authority,
      ['source_refs', 'state', 'unresolved_owner_role', 'unresolved_evidence_requirements',
        'unresolved_question'],
      'invalid material V&V authority');
    const sourceRefs = vvArray(value.authority.source_refs).map((source) =>
      vvMaterialSourceRef(source, sourceFile));
    const authorityState = vvIdentifier(value.authority.state);
    const unresolvedOwnerRole = value.authority.unresolved_owner_role == null
      ? null : vvRequiredText(value.authority.unresolved_owner_role);
    const unresolvedQuestion = value.authority.unresolved_question == null
      ? null : vvRequiredText(value.authority.unresolved_question);
    const unresolvedEvidenceRequirements = vvArray(value.authority.unresolved_evidence_requirements)
      .map((requirementValue) => {
        const requirementObject = vvObject(requirementValue);
        const hasBoundEvidence = requirementObject.bound_evidence_ids != null ||
          requirementObject.evidence_state != null;
        vvExactKeys(requirementObject, hasBoundEvidence
          ? ['evidence_type', 'prerequisite_kind', 'responsible_role', 'required_input', 'next_action',
            'current_status', 'bound_evidence_ids', 'evidence_state']
          : ['evidence_type', 'prerequisite_kind', 'responsible_role', 'required_input', 'next_action',
            'current_status'], 'invalid unresolved material V&V evidence requirement');
        const evidenceType = vvIdentifier(requirementObject.evidence_type);
        const prerequisiteKind = vvIdentifier(requirementObject.prerequisite_kind);
        const expectedPrerequisiteKinds = {
          CANONICAL_IMPLEMENTATION_SOURCE: new Set(['SOURCE']),
          REPOSITORY_STATIC_CHECK: new Set(['SOURCE']),
          RUNTIME_OR_UI_OBSERVATION: new Set(['ENVIRONMENT_OR_PERMISSION', 'ENVIRONMENT_AND_AUTHORIZATION']),
          ACCOUNTABLE_OWNER_CONFIRMATION: new Set(['OWNER_CONFIRMATION']),
          AUTHORITATIVE_DOCUMENTATION_CITATION: new Set(['AUTHORITATIVE_CITATION']),
        };
        const currentStatus = vvStatus(requirementObject.current_status);
        if (!requiredEvidenceTypes.includes(evidenceType) ||
          !expectedPrerequisiteKinds[evidenceType]?.has(prerequisiteKind) ||
          ['NOT_APPLICABLE', 'STALE'].includes(currentStatus)) {
          throw new Error('mismatched unresolved material V&V evidence requirement');
        }
        const boundEvidenceIds = hasBoundEvidence
          ? vvEvidenceIds(requirementObject.bound_evidence_ids, allEvidenceIds,
            'invalid partially bound material V&V evidence requirement') : [];
        const evidenceState = hasBoundEvidence ? vvIdentifier(requirementObject.evidence_state) : null;
        const allowedEvidenceStates = {
          PASS: new Set(['SATISFIED_FOR_EXACT_COMMAND_CEILING']),
          BLOCKED: new Set(['BLOCKER_CONFIRMED_RUNTIME_NOT_EXECUTED']),
          UNVALIDATED: new Set(['PARTIAL', 'ADVERSE_RESULT_OUTSIDE_LITERAL_SYNTAX_CLAIM']),
        };
        if (hasBoundEvidence && (!boundEvidenceIds.length || !allowedEvidenceStates[currentStatus]?.has(evidenceState))) {
          throw new Error('mismatched partially bound material V&V evidence state');
        }
        return {
          evidenceType, prerequisiteKind,
          responsibleRole: vvRequiredText(requirementObject.responsible_role),
          requiredInput: vvRequiredText(requirementObject.required_input),
          nextAction: vvRequiredText(requirementObject.next_action), currentStatus,
          boundEvidenceIds: boundEvidenceIds.map(vvText), evidenceState,
        };
      });
    if (new Set(sourceRefs.map((source) => JSON.stringify(source))).size !== sourceRefs.length ||
      new Set(unresolvedEvidenceRequirements.map((item) => item.evidenceType)).size !==
        unresolvedEvidenceRequirements.length ||
      !new Set(['BOUND', 'EVIDENCE_BOUND', 'UNRESOLVED']).has(authorityState) ||
      (authorityState === 'BOUND' && (!sourceRefs.length || unresolvedEvidenceRequirements.length ||
        unresolvedOwnerRole || unresolvedQuestion)) ||
      (authorityState === 'EVIDENCE_BOUND' && (sourceRefs.length || unresolvedEvidenceRequirements.length ||
        unresolvedOwnerRole || unresolvedQuestion)) ||
      (authorityState === 'UNRESOLVED' && (!unresolvedOwnerRole || !unresolvedQuestion ||
        unresolvedEvidenceRequirements.length !== requiredEvidenceTypes.length ||
        requiredEvidenceTypes.some((type) =>
          !unresolvedEvidenceRequirements.some((requirement) => requirement.evidenceType === type)))) ||
      sourceRefs.some((ref) => ref.path === sourceFile)) {
      throw new Error('invalid material V&V authority state');
    }
    const currentKeys = ['status', 'rationale', 'evidence_ids', 'limitations', 'disposition_evidence_ids'];
    if (value.current.command_evidence_binding != null) currentKeys.push('command_evidence_binding');
    if (value.current.unavailable_prerequisite != null) currentKeys.push('unavailable_prerequisite');
    vvExactKeys(value.current, currentKeys, 'invalid current material V&V claim');
    const status = vvStatus(value.current.status);
    if (status === 'STALE' || status === 'NOT_APPLICABLE') throw new Error('invalid current material V&V claim status');
    const evidenceIds = vvEvidenceIds(value.current.evidence_ids, allEvidenceIds,
      'invalid material V&V claim evidence', { allowEmpty: true });
    const commandBinding = bindingManifests.commandByClaim.get(claimId) || null;
    const declaredCommandBinding = value.current.command_evidence_binding || null;
    if (Boolean(commandBinding) !== Boolean(declaredCommandBinding) ||
      (commandBinding && (JSON.stringify(declaredCommandBinding) !== JSON.stringify(commandBinding.raw) ||
        commandBinding.pageId !== pageId || commandBinding.sourceFile !== sourceFile ||
        commandBinding.heading !== headingLabel || commandBinding.sourceTextSha256 !== scope.source_text_sha256 ||
        JSON.stringify(commandBinding.sourceSpans) !== JSON.stringify(spans) ||
        commandBinding.currentClaimStatus !== status ||
        JSON.stringify(commandBinding.directEvidenceIds) !== JSON.stringify(evidenceIds)))) {
      throw new Error('mismatched exact command/material V&V claim binding');
    }
    let unavailablePrerequisite = null;
    if (value.current.unavailable_prerequisite != null) {
      const prerequisite = vvExactKeys(value.current.unavailable_prerequisite, ['kind', 'description'],
        'invalid material V&V unavailable prerequisite');
      const kind = vvIdentifier(prerequisite.kind);
      if (status !== 'BLOCKED' || commandBinding?.decision !== 'EXACT_BLOCKER_PROPAGATED' ||
        !new Set(['PERMISSION', 'AUTHORIZATION', 'ENVIRONMENT', 'INPUT']).has(kind)) {
        throw new Error('mismatched material V&V unavailable prerequisite');
      }
      unavailablePrerequisite = { kind, description: vvRequiredText(prerequisite.description) };
    }
    const navigationBinding = bindingManifests.navigationByClaim.get(claimId) || null;
    if (navigationBinding && (navigationBinding.pageId !== pageId || navigationBinding.sourceFile !== sourceFile ||
      navigationBinding.heading !== headingLabel || navigationBinding.sourceTextSha256 !== scope.source_text_sha256 ||
      JSON.stringify(navigationBinding.sourceSpans) !== JSON.stringify(spans) ||
      value.claim.kind !== 'NAVIGATION_CONTRACT' ||
      JSON.stringify(navigationBinding.destinations.map((destination) => destination.href)) !==
        JSON.stringify(citationRefs.map((ref) => ref.href)) ||
      JSON.stringify(navigationBinding.destinations.map((destination) => destination.sourceRef)) !==
        JSON.stringify(sourceRefs))) {
      throw new Error('mismatched exact navigation/material V&V claim binding');
    }
    if (Boolean(navigationBinding) !== evidenceIds.includes(bindingManifests.navigationEnvelope.evidenceId)) {
      throw new Error('missing or unused exact navigation V&V claim binding');
    }
    if (unresolvedEvidenceRequirements.some((requirement) =>
      requirement.boundEvidenceIds.some((evidenceId) => !evidenceIds.includes(evidenceId) ||
        !evidenceSupportsClaim(evidenceId, claimId, pageId)))) {
      throw new Error('unbound partially completed material V&V evidence lane');
    }
    const evidenceLaneStatuses = unresolvedEvidenceRequirements.map((requirement) => requirement.currentStatus);
    const unresolvedRollup = ['FAIL', 'BLOCKED', 'UNVALIDATED'].find((candidate) =>
      evidenceLaneStatuses.includes(candidate)) ||
      (evidenceLaneStatuses.length && evidenceLaneStatuses.every((laneStatus) => laneStatus === 'PASS') ? 'PASS' : null);
    if ((authorityState === 'UNRESOLVED' && unresolvedRollup !== status) ||
      (authorityState !== 'UNRESOLVED' && !['PASS', 'FAIL'].includes(status))) {
      throw new Error('mismatched material V&V per-evidence-lane rollup');
    }
    const sourceKinds = new Set(sourceRefs.map((source) => source.sourceKind));
    if (status === 'PASS' &&
      ((requiredEvidenceTypes.includes('CANONICAL_IMPLEMENTATION_SOURCE') &&
        ![...sourceKinds].some((kind) =>
          ['CANONICAL_API_CLIENT_SOURCE', 'CANONICAL_CLI_SOURCE', 'OPENAPI_SOURCE'].includes(kind))) ||
       (requiredEvidenceTypes.includes('REPOSITORY_STATIC_CHECK') &&
        ![...sourceKinds].some((kind) =>
          ['ROUTE_CONFIGURATION', 'ROUTE_DESTINATION_SOURCE'].includes(kind))) ||
       requiredEvidenceTypes.includes('ACCOUNTABLE_OWNER_CONFIRMATION') ||
       (requiredEvidenceTypes.includes('RUNTIME_OR_UI_OBSERVATION') &&
         (authorityState !== 'EVIDENCE_BOUND' || !commandBinding || commandBinding.score !== 3 ||
           commandBinding.commandExecutionStatus !== 'PASS')))) {
      throw new Error('unsatisfied material V&V claim required evidence type');
    }
    const citationDefect = citation.required && citationState === 'ABSENT';
    const confirmedIncorrect = status === 'FAIL' && !citationDefect &&
      ['BOUND', 'EVIDENCE_BOUND'].includes(authorityState) &&
      evidenceIds.length > 0 && evidenceIds.every((evidenceId) =>
        evidenceSupportsClaim(evidenceId, claimId, pageId, 'FAIL'));
    if ((['PASS', 'BLOCKED'].includes(status) && !evidenceIds.length) ||
      (status === 'FAIL' && !citationDefect && !confirmedIncorrect)) {
      throw new Error('mismatched material V&V claim evidence/status');
    }
    if (evidenceIds.some((evidenceId) => !evidenceRefById.get(evidenceId) ||
      !evidenceSupportsClaim(evidenceId, claimId, pageId))) {
      throw new Error('unretained or cross-page material V&V claim evidence');
    }
    if ((status === 'PASS' && !['BOUND', 'EVIDENCE_BOUND'].includes(authorityState)) ||
      (['BLOCKED', 'UNVALIDATED'].includes(status) && authorityState !== 'UNRESOLVED') ||
      (status === 'FAIL' && ((citationDefect && authorityState !== 'UNRESOLVED') ||
        (!citationDefect && !confirmedIncorrect)))) {
      throw new Error('mismatched material V&V claim authority/status');
    }
    if ((citationState === 'ABSENT' && status !== 'FAIL') ||
      (citationState === 'PRESENT_UNVERIFIED' && status === 'PASS') ||
      (status === 'FAIL' && !citationDefect && !confirmedIncorrect)) {
      throw new Error('mismatched material V&V citation/status semantics');
    }
    const limitations = vvArray(value.current.limitations).map(vvRequiredText);
    if (!limitations.length) throw new Error('missing material V&V claim limitation');
    const dispositionEvidenceIds = vvEvidenceIds(value.current.disposition_evidence_ids, allEvidenceIds,
      'invalid material V&V disposition evidence');
    const binding = bindingManifests.materialByClaim.get(claimId);
    const expectedDispositionEvidenceIds = [bindingManifests.materialEnvelope.evidenceId,
      ...(commandBinding ? [bindingManifests.commandEnvelope.evidenceId] : [])];
    const expectedSatisfiedEvidenceTypes = status === 'PASS'
      ? requiredEvidenceTypes
      : unresolvedEvidenceRequirements.filter((requirement) => requirement.currentStatus === 'PASS')
        .map((requirement) => requirement.evidenceType).sort();
    const expectedPartiallySupportedEvidenceTypes = unresolvedEvidenceRequirements
      .filter((requirement) => requirement.boundEvidenceIds.length && requirement.currentStatus !== 'PASS')
      .map((requirement) => requirement.evidenceType).sort();
    if (!binding || JSON.stringify(dispositionEvidenceIds) !== JSON.stringify(expectedDispositionEvidenceIds) ||
      dispositionEvidenceIds[0] !== binding.envelopeEvidenceId || binding.pageId !== pageId ||
      binding.status !== status || binding.sourceFile !== sourceFile || binding.heading !== headingLabel ||
      JSON.stringify(vvComparableRenderedVia(binding.renderedVia)) !==
        JSON.stringify(vvComparableRenderedVia(renderedVia)) ||
      binding.sourceTextSha256 !== scope.source_text_sha256 ||
      JSON.stringify(binding.sourceSpans) !== JSON.stringify(spans) ||
      JSON.stringify(binding.requiredEvidenceTypes) !== JSON.stringify(requiredEvidenceTypes) ||
      JSON.stringify(binding.satisfiedEvidenceTypes) !== JSON.stringify(expectedSatisfiedEvidenceTypes) ||
      JSON.stringify(binding.partiallySupportedEvidenceTypes) !==
        JSON.stringify(expectedPartiallySupportedEvidenceTypes) ||
      JSON.stringify(binding.supportingEvidenceIds) !== JSON.stringify(evidenceIds) ||
      JSON.stringify(binding.commandEvidenceBinding) !== JSON.stringify(declaredCommandBinding) ||
      JSON.stringify(binding.limitations) !== JSON.stringify(limitations)) {
      throw new Error('mismatched material V&V disposition binding');
    }
    const expectedEvidenceRole = {
      PASS: 'CLAIM_SUITABLE_BOUNDED_SUPPORT',
      FAIL: 'CONFIRMED_CITATION_OR_SOURCE_BINDING_DEFECT',
      BLOCKED: 'UNAVAILABLE_PREREQUISITE_DISPOSITION',
      UNVALIDATED: evidenceIds.length
        ? 'PARTIAL_EVIDENCE_BOUND_STATUS_UNCHANGED' : 'OCCURRENCE_ACCOUNTING_ONLY',
    }[status];
    if (binding.evidenceRole !== expectedEvidenceRole ||
      (binding.evidenceRole === 'OCCURRENCE_ACCOUNTING_ONLY' && evidenceIds.length) ||
      (binding.evidenceRole === 'PARTIAL_EVIDENCE_BOUND_STATUS_UNCHANGED' && !evidenceIds.length)) {
      throw new Error('mismatched material V&V disposition evidence role');
    }
    vvRequiredText(value.current.rationale);
    const nextAction = value.next_action == null ? null : vvRequiredText(value.next_action);
    if (status !== 'PASS' && !nextAction) throw new Error('missing material V&V claim next action');
    // Navigation is bound to literal, hash-checked documentation spans. Some
    // material claims summarize a passage rather than quote it (e.g. volumes).
    if (!passageBlocksByIndex.has(claimSourceIndex)) {
      passageBlocksByIndex.set(claimSourceIndex, vvGenericMaterialClaims({
        sourceIndex: claimSourceIndex, sourceFile: '', route: pageMeta.route,
      }));
    }
    const passageSpans = spans.flatMap((span) => {
      const contained = passageBlocksByIndex.get(claimSourceIndex).filter((block) =>
        block.start >= span.start && block.end <= span.end);
      return contained.length ? contained.map((block) => ({ start: block.start, end: block.end })) : [span];
    });
    const sourcePassages = passageSpans.map((span) => {
      const literal = claimSourceIndex.lines.slice(span.start - 1, span.end).join('\n').trim();
      const section = vvSectionAtLine(claimSourceIndex, span.start);
      const repeats = [];
      for (let start = 1; start <= claimSourceIndex.lines.length - (span.end - span.start); start++) {
        if (vvSectionAtLine(claimSourceIndex, start) === section &&
            claimSourceIndex.lines.slice(start - 1, start + span.end - span.start).join('\n').trim() === literal) repeats.push(start);
      }
      return { text: vvText(literal), section, start: span.start, end: span.end,
        redacted: vvText(literal) !== literal, occurrence: repeats.indexOf(span.start), occurrences: repeats.length };
    });
    const normalized = {
      id: claimId, pageId, checkedContent: { route: pageMeta.route, pageTitle: pageMeta.title, sections: headings },
      sourceLocation: { file: sourceFile, spans, textSha256: scope.source_text_sha256 },
      sourcePassages,
      renderedDependency: renderedVia ? { component: vvText(renderedVia.component) } : null,
      claim, requiredEvidenceTypes, citationRequired: value.evidence_requirement.citation_required,
      citation: { required: citation.required, state: citationState,
        refs: citationRefs.map((ref) => ({ href: vvText(ref.href), kind: ref.kind })),
        assessment: citationAssessment },
      evidenceRationale: vvText(value.evidence_requirement.rationale),
      authority: { state: authorityState, sourceRefs, unresolvedOwnerRole,
        unresolvedEvidenceRequirements, unresolvedQuestion },
      current: { status, rationale: vvText(value.current.rationale), evidenceIds: evidenceIds.map(vvText),
        dispositionEvidenceIds: dispositionEvidenceIds.map(vvText), dispositionEvidenceRole: binding.evidenceRole,
        requiredEvidenceTypes: binding.requiredEvidenceTypes.map(vvText),
        satisfiedEvidenceTypes: binding.satisfiedEvidenceTypes.map(vvText),
        partiallySupportedEvidenceTypes: binding.partiallySupportedEvidenceTypes.map(vvText),
        dispositionLimitations: binding.limitations.map(vvText),
        dispositionManifestLimitations: vvText(bindingManifests.materialEnvelope.limitations),
        commandEvidenceBinding: commandBinding ? {
          commandId: commandBinding.commandId, score: commandBinding.score,
          commandExecutionStatus: commandBinding.commandExecutionStatus,
          priorClaimStatus: commandBinding.priorClaimStatus, currentClaimStatus: commandBinding.currentClaimStatus,
          directEvidenceIds: commandBinding.directEvidenceIds.map(vvText), decision: commandBinding.decision,
          manifestEvidenceId: commandBinding.envelopeEvidenceId,
        } : null,
        unavailablePrerequisite, limitations: limitations.map(vvText) },
      nextAction,
    };
    materialClaims.push(normalized);
    materialClaimsById.set(claimId, { ...normalized, spans, rawClaimText });
    materialClaimsByPage.get(pageId).push(normalized);
    materialStatusCounts.set(status, materialStatusCounts.get(status) + 1);
  }
  for (const [pageId, pageMeta] of canonical.pageById) {
    const declared = pageMeta.materialClaimIds;
    const actual = materialClaimsByPage.get(pageId).map((claim) => claim.id);
    if (declared.length !== actual.length || declared.some((id, index) => id !== actual[index])) {
      throw new Error('mismatched page material V&V claim coverage');
    }
    const expected = pageMeta.route === '/host/volume-offers'
      ? [
        ['VOL-C01', 'A local volume is persistent storage.'],
        ['VOL-C02', 'A volume is backed by one physical Host and may attach only on that machine.'],
        ['VOL-C03', 'Volume storage is separate from the container disk; destroying the instance keeps the volume.'],
        ['VOL-C04', 'A Host can publish capacity and price as a volume offer.'],
        ['VOL-C05', 'A renter accepts an offer ID to create an owned volume; the CLI/API also use volume-contract terminology.'],
        ['VOL-C06', 'The renter supplies a chosen mount path during instance creation.'],
        ['VOL-C07', 'The command map assigns Host offer tasks to list machine, list volume(s), and unlist volume, and renter tasks to search, create, show, attach, and delete volume interfaces.'],
        ['VOL-C36', 'Machine, volume-offer, owned-volume, and mount-path identifiers have distinct interface roles and are not interchangeable.'],
        ['VOL-C08', 'list volume takes a machine ID.'],
        ['VOL-C09', 'Search results expose a volume-offer ID and unlist volume consumes a listing ID.'],
        ['VOL-C10', 'An owned-volume ID is returned by show volumes and accepted by instance-link, volume-clone, and delete interfaces.'],
        ['VOL-C11', 'Hosts should place Docker storage on fast SSD/NVMe with XFS project quotas.'],
        ['VOL-C12', 'An offer can be created with a machine listing or separately.'],
        ['VOL-C13', 'Published size is a maximum aggregate rentable capacity and publication alone creates no renter volume.'],
        ['VOL-C14', 'A renter searches offers and selects a size.'],
        ['VOL-C15', 'The allocated volume persists independently of an instance.'],
        ['VOL-C16', 'A new or existing volume is linked in the create-instance request.'],
        ['VOL-C17', 'The linked volume appears at the selected path in a running Docker instance.'],
        ['VOL-C18', 'Destroying an instance leaves its volume intact.'],
        ['VOL-C19', 'Every attached instance must be destroyed before the volume can be deleted.'],
        ['VOL-C20', 'Unlisting an offer is distinct from deleting an owned volume.'],
        ['VOL-C37', 'The renter workflow link resolves to the central Volumes guide.'],
        ['VOL-C21', 'list machine accepts --vol_size, --vol_price, and --end_date; zero disables the volume offer.'],
        ['VOL-C38', 'Hosts should pass an explicit volume size and price so advertised capacity is intentional.'],
        ['VOL-C22', 'list volume accepts machine ID, --size, --price_disk, and --end_date.'],
        ['VOL-C23', 'list volumes applies one size, price, and end-date tuple to several machine IDs.'],
        ['VOL-C24', '--end_date sets the volume offer expiration.'],
        ['VOL-C39', 'Hosts should review a volume-offer expiration date before publishing.'],
        ['VOL-C25', 'Local volumes, instance disks, stopped instances, cached images, and other allocations use one machine pool.'],
        ['VOL-C26', 'Renter-created size is allocated from the offer and shared pool.'],
        ['VOL-C27', 'A 200 GB volume drawn from a 500 GB offer must be included in storage planning; headroom is needed.'],
        ['VOL-C28', 'Hosts should not manually remove renter files and should use normal lifecycle/support paths for reconciliation failures.'],
        ['VOL-C29', 'A local volume stays on its creation machine.'],
        ['VOL-C30', 'Attachment is restricted to instances on the same machine.'],
        ['VOL-C31', 'Volume size is fixed after creation.'],
        ['VOL-C32', 'Local volumes work with Docker instances, not VM instances.'],
        ['VOL-C33', 'A local volume is persistent storage but not an off-machine backup.'],
        ['VOL-C34', 'The page routes storage maintenance to the Maintenance Windows workflow.'],
        ['VOL-C35', 'All local Related Pages and command-reference destinations exist.'],
      ].map(([id, text]) => ({ id, text }))
      : [vvGenericMaterialClaims(pageMeta), ...pageMeta.renderedDependencies.map((dependency) =>
        vvGenericMaterialClaims({ ...pageMeta, sourceFile: dependency.sourceFile,
          sourceIndex: dependency.sourceIndex }))]
        .flat().sort((left, right) => left.start - right.start || left.id.localeCompare(right.id));
    if (expected.length !== actual.length || expected.some((item, index) => item.id !== actual[index]) ||
      expected.some((item, index) => item.text !== materialClaimsById.get(actual[index]).rawClaimText)) {
      throw new Error(`incomplete material V&V source-occurrence coverage for ${pageMeta.route}`);
    }
  }
  if (bindingManifests.materialByClaim.size !== materialClaims.length) {
    throw new Error('unused or missing material V&V disposition binding');
  }
  if (bindingManifests.navigationByClaim.size !== materialClaims.filter((claim) =>
    claim.current.evidenceIds.includes(bindingManifests.navigationEnvelope.evidenceId)).length ||
    bindingManifests.commandByClaim.size !== materialClaims.filter((claim) =>
      claim.current.commandEvidenceBinding).length) {
    throw new Error('unused or missing material V&V supporting binding manifest');
  }
  const coverage = vvExactKeys(sets.material_claim_coverage,
    ['method', 'claims', 'pages', 'statuses', 'page_dispositions', 'coverage_limit'],
    'invalid material V&V coverage');
  vvRequiredText(coverage.method); vvRequiredText(coverage.coverage_limit);
  if (coverage.claims !== materialClaims.length || coverage.pages !== canonical.pageById.size ||
    coverage.pages !== 40) throw new Error('invalid material V&V coverage counts');
  const declaredStatuses = vvObject(coverage.statuses);
  if (Object.keys(declaredStatuses).some((status) => !VV_TARGET_STATUSES.has(status)) ||
    [...materialStatusCounts].some(([status, count]) => (declaredStatuses[status] ?? 0) !== count)) {
    throw new Error('invalid material V&V coverage statuses');
  }
  const aggregateStatuses = (values) => {
    if (!values.length) return null;
    for (const candidate of ['FAIL', 'BLOCKED', 'STALE', 'UNVALIDATED']) {
      if (values.includes(candidate)) return candidate;
    }
    if (values.every((status) => status === 'NOT_APPLICABLE')) return 'NOT_APPLICABLE';
    if (values.includes('PASS') && values.every((status) => ['PASS', 'NOT_APPLICABLE'].includes(status))) return 'PASS';
    throw new Error('unaggregatable material V&V statuses');
  };
  const materialPageDispositions = [];
  const materialPageDispositionByPage = new Map();
  const pageDispositionCounts = new Map([...VV_TARGET_STATUSES].map((status) => [status, 0]));
  const dispositionRows = vvArray(coverage.page_dispositions);
  const canonicalPages = [...canonical.pageById.values()];
  if (dispositionRows.length !== canonicalPages.length) throw new Error('invalid material V&V page-disposition count');
  for (let index = 0; index < dispositionRows.length; index += 1) {
    const value = vvExactKeys(dispositionRows[index],
      ['page_id', 'route', 'title', 'status', 'counts', 'rationale', 'next_action'],
      'invalid material V&V page disposition');
    const pageMeta = canonicalPages[index];
    const pageId = vvIdentifier(value.page_id);
    const status = vvStatus(value.status);
    if (pageId !== pageMeta.pageId || vvCanonicalRoute(value.route) !== pageMeta.route ||
      vvRequiredText(value.title) !== pageMeta.title || materialPageDispositionByPage.has(pageId)) {
      throw new Error('mismatched material V&V page disposition identity');
    }
    const claims = materialClaimsByPage.get(pageId);
    const actualCounts = new Map([...VV_TARGET_STATUSES].map((name) => [name, 0]));
    for (const claim of claims) actualCounts.set(claim.current.status, actualCounts.get(claim.current.status) + 1);
    const counts = vvObject(value.counts);
    if (Object.keys(counts).some((name) => !VV_TARGET_STATUSES.has(name) ||
      !Number.isInteger(counts[name]) || counts[name] <= 0) ||
      [...actualCounts].some(([name, count]) => (counts[name] ?? 0) !== count) ||
      aggregateStatuses(claims.map((claim) => claim.current.status)) !== status) {
      throw new Error('mismatched material V&V page disposition rollup');
    }
    const nextAction = value.next_action == null ? null : vvRequiredText(value.next_action);
    if ((['FAIL', 'BLOCKED', 'UNVALIDATED', 'STALE'].includes(status)) !== Boolean(nextAction)) {
      throw new Error('mismatched material V&V page disposition next action');
    }
    const normalized = { pageId, checkedContent: { route: pageMeta.route, pageTitle: pageMeta.title, sections: [] },
      status, counts: Object.fromEntries([...actualCounts].filter(([, count]) => count)),
      rationale: vvRequiredText(value.rationale), nextAction };
    materialPageDispositions.push(normalized);
    materialPageDispositionByPage.set(pageId, normalized);
    pageDispositionCounts.set(status, pageDispositionCounts.get(status) + 1);
  }

  const retiredMaterialClaims = [];
  const retiredMaterialClaimsByPage = new Map([...canonical.pageById.keys()].map((pageId) => [pageId, []]));
  const retiredIds = new Set();
  const retiredSignatures = new Map();
  for (const value of vvArray(sets.retired_material_claims)) {
    vvExactKeys(value, ['claim_id', 'status', 'source', 'claim', 'failure', 'correction', 'retest_evidence_id'],
      'invalid retired material V&V claim');
    const id = vvIdentifier(value.claim_id);
    if (retiredIds.has(id) || materialClaimsById.has(id) || value.status !== 'FAIL') {
      throw new Error('invalid retired material V&V claim identity');
    }
    retiredIds.add(id);
    const evidenceId = vvEvidenceId(value.retest_evidence_id);
    const currentClaimId = id.replace(/-HISTORICAL$/, '');
    const currentClaim = materialClaimsById.get(currentClaimId);
    const historicalSource = vvRequiredText(value.source);
    const sourceMatch = historicalSource.match(
      /^(host\/[A-Za-z0-9._/-]+\.mdx):\d+ at (?:pre-edit SHA-256|pre-correction source-text SHA-256) [a-f0-9]{64}$/);
    const pageMeta = sourceMatch && [...canonical.pageById.values()]
      .find((page) => page.sourceFile === sourceMatch[1]);
    const navigationRetestTouchesPage = evidenceId === bindingManifests.navigationEnvelope.evidenceId &&
      pageMeta && [...bindingManifests.navigationByClaim.values()].some((binding) =>
        binding.pageId === pageMeta.pageId && binding.status === 'PASS');
    const replacementIsBound = currentClaim && pageMeta && currentClaim.pageId === pageMeta.pageId &&
      currentClaim.current.status === 'PASS' && currentClaim.current.evidenceIds.includes(evidenceId) &&
      evidenceTouchesPage(evidenceId, currentClaim.pageId, 'PASS');
    const removedClaimIsBound = !currentClaim && id === 'HOV-C-VOLUME-ALIGNMENT-HISTORICAL' &&
      navigationRetestTouchesPage;
    if (!sourceMatch || !pageMeta || (!replacementIsBound && !removedClaimIsBound) ||
      !allEvidenceIds.has(evidenceId) || !evidenceRefById.get(evidenceId)) {
      throw new Error('unbound retired material V&V correction/retest');
    }
    const normalized = { id, status: 'FAIL', currentClaimId: currentClaim ? currentClaimId : null,
      replacementClaimPresent: Boolean(currentClaim),
      checkedContent: currentClaim?.checkedContent ||
        { route: pageMeta.route, pageTitle: pageMeta.title, sections: [] },
      claim: vvRequiredText(value.claim), failure: vvRequiredText(value.failure),
      correction: vvRequiredText(value.correction), retestEvidenceId: evidenceId };
    retiredSignatures.set(id, {
      source: historicalSource, claim: value.claim, failure: value.failure,
      correction: value.correction, retestEvidenceId: evidenceId,
    });
    retiredMaterialClaims.push(normalized);
    retiredMaterialClaimsByPage.get(pageMeta.pageId).push(normalized);
  }
  const expectedRetiredIds = ['VOL-C24-HISTORICAL', 'VOL-C34-HISTORICAL',
    'HOV-C-VOLUME-ALIGNMENT-HISTORICAL'];
  if (retiredIds.size !== expectedRetiredIds.length || expectedRetiredIds.some((id) => !retiredIds.has(id))) {
    throw new Error('incomplete retired material V&V failure history');
  }
  const expectedRetiredHistory = {
    'VOL-C24-HISTORICAL': {
      source: 'host/volume-offers.mdx:71 at pre-edit SHA-256 2be619b3d1ff66014a4301fa8a40ab17dcd13e48af5f78eed2d50e90fd1d37ad',
      claim: 'Volume-offer end date should use the same commitment window as GPU offers.',
      failure: 'A required Product/Legal source was absent; documentation text and client code could not authorize the contract claim.',
      correction: 'The sentence now states only the source-supported expiration-field behavior.',
      retestEvidenceId: 'EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01',
    },
    'VOL-C34-HISTORICAL': {
      source: 'host/volume-offers.mdx:95 at pre-edit SHA-256 2be619b3d1ff66014a4301fa8a40ab17dcd13e48af5f78eed2d50e90fd1d37ad',
      claim: 'Disk health and availability are part of the Host commitment and maintenance must not interrupt active volume contracts.',
      failure: 'A required Product/Legal/Operations source was absent.',
      correction: 'The sentence is now a bounded navigation handoff to the separately governed maintenance workflow.',
      retestEvidenceId: 'EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01',
    },
    'HOV-C-VOLUME-ALIGNMENT-HISTORICAL': {
      source: 'host/hosting-overview.mdx:109 at pre-correction source-text SHA-256 747f8ff68e10918a3d615b283da360ef576647858ca974a67b71f8a5ddc6966b',
      claim: 'Volume offer end dates must align with GPU offer end dates; unlisting a machine also unlists its volume offers.',
      failure: 'The commitment-window assertion contradicted the deliberately narrowed Volume Offers claim and had no Product/Legal authority; the unlisting behavior also lacked claim-suitable canonical backend or runtime proof.',
      correction: 'Removed both unsupported behavior assertions from Hosting Overview and kept the dedicated Volume Offers and central CLI-reference handoffs.',
      retestEvidenceId: 'EV-HOST-LOCAL-NAVIGATION-RESOLUTION-01',
    },
  };
  if (expectedRetiredIds.some((id) =>
    JSON.stringify(retiredSignatures.get(id)) !== JSON.stringify(expectedRetiredHistory[id]))) {
    throw new Error('changed retired material V&V failure history');
  }

  const supportLayers = [];
  const supportByRoute = new Map();
  const supportIds = new Set();
  const supportCounts = new Map([['CLI', 0], ['SDK', 0]]);
  for (const value of vvArray(sets.support_layers)) {
    vvExactKeys(value, ['support_id', 'layer', 'route', 'source_file', 'source_sha256', 'fragment_file',
      'fragment_sha256', 'central_reference_file', 'central_reference_route', 'central_reference_sha256',
      'classification', 'workflow', 'status', 'evidence_ids', 'claim_limit'], 'invalid V&V support layer');
    const id = vvIdentifier(value.support_id);
    const layer = vvIdentifier(value.layer);
    const route = vvCanonicalRoute(value.route);
    if (supportIds.has(id) || supportByRoute.has(route) || canonical.pageByRoute.has(route) || !supportCounts.has(layer) ||
      value.classification !== 'CENTRAL_REFERENCE_SUPPORT_LAYER' || value.workflow !== false || value.status !== 'PASS') {
      throw new Error('invalid V&V support layer identity');
    }
    const expectedPrefix = layer === 'CLI' ? '/host/cli/' : '/host/sdk/';
    const centralPrefix = layer === 'CLI' ? '/cli/reference/' : '/sdk/python/reference/';
    const sourcePrefix = layer === 'CLI' ? 'host/cli/' : 'host/sdk/';
    const fragmentPrefix = layer === 'CLI' ? 'snippets/host/cli/' : 'snippets/host/sdk/';
    const centralFilePrefix = layer === 'CLI' ? 'cli/reference/' : 'sdk/python/reference/';
    const sourceFile = vvRequiredText(value.source_file);
    const fragmentFile = vvRequiredText(value.fragment_file);
    const centralFile = vvRequiredText(value.central_reference_file);
    const centralRoute = vvRequiredText(value.central_reference_route);
    if (!route.startsWith(expectedPrefix) || !sourceFile.startsWith(sourcePrefix) ||
      !fragmentFile.startsWith(fragmentPrefix) || !centralFile.startsWith(centralFilePrefix) ||
      !centralRoute.startsWith(centralPrefix) || !/^\/(?:cli\/reference|sdk\/python\/reference)\/[A-Za-z0-9._/-]+$/.test(centralRoute) ||
      centralRoute.split('/').some((segment) => segment === '.' || segment === '..') ||
      route !== `/${sourceFile.replace(/\.mdx$/, '')}` ||
      centralRoute !== `/${centralFile.replace(/\.mdx$/, '')}` ||
      path.basename(sourceFile) !== path.basename(fragmentFile) || path.basename(sourceFile) !== path.basename(centralFile) ||
      ![sourceFile, fragmentFile, centralFile].every((file) =>
        /^[A-Za-z0-9._/-]+\.mdx$/.test(file) && !file.split('/').includes('..'))) {
      throw new Error('invalid V&V support layer path');
    }
    const readAndHash = (file, declaredHash) => {
      const bytes = vvHistoricalSourceFile(file, 'invalid V&V support layer source file').bytes;
      if (vvSha256(declaredHash, 'invalid V&V support layer hash') !==
        crypto.createHash('sha256').update(bytes).digest('hex')) throw new Error('stale V&V support layer source');
      return bytes.toString('utf8');
    };
    const sourceText = readAndHash(sourceFile, value.source_sha256);
    readAndHash(fragmentFile, value.fragment_sha256);
    const centralText = readAndHash(centralFile, value.central_reference_sha256);
    const importMatches = [...sourceText.matchAll(/^\s*import\s+([A-Za-z_$][\w$]*)\s+from\s+['"]([^'"]+)['"]\s*;?\s*$/gm)];
    const fragmentImports = importMatches.filter((match) => match[2] === `/${fragmentFile}`);
    if (value.source_sha256 !== value.central_reference_sha256 || sourceText !== centralText ||
      fragmentImports.length !== 1 || !new RegExp(`<${fragmentImports[0]?.[1]}\\s*/>`).test(sourceText)) {
      throw new Error('detached V&V support layer fragment');
    }
    const evidenceIds = vvEvidenceIds(value.evidence_ids, allEvidenceIds, 'invalid V&V support layer evidence');
    if (evidenceIds.some((evidenceId) => !evidenceRefById.get(evidenceId))) {
      throw new Error('unretained V&V support-layer evidence');
    }
    const binding = bindingManifests.supportById.get(id);
    if (!binding || evidenceIds.length !== 1 || evidenceIds[0] !== binding.envelopeEvidenceId ||
      binding.status !== value.status || binding.layer !== layer || binding.route !== route ||
      binding.sourceFile !== sourceFile || binding.sourceSha256 !== value.source_sha256 ||
      binding.fragmentFile !== fragmentFile || binding.fragmentSha256 !== value.fragment_sha256 ||
      binding.centralReferenceFile !== centralFile || binding.centralReferenceRoute !== centralRoute ||
      binding.centralReferenceSha256 !== value.central_reference_sha256) {
      throw new Error('mismatched V&V support-layer binding');
    }
    const normalized = { id, layer, route, sourceFile, sourceSha256: value.source_sha256,
      fragmentFile, fragmentSha256: value.fragment_sha256, centralReferenceFile: centralFile,
      centralReferenceRoute: centralRoute, classification: value.classification, workflow: false, status: 'PASS',
      centralReferenceSha256: value.central_reference_sha256,
      evidenceIds: evidenceIds.map(vvText), evidenceRole: binding.evidenceRole,
      evidenceLimitations: bindingManifests.supportEnvelope.limitations,
      claimLimit: vvRequiredText(value.claim_limit) };
    supportIds.add(id); supportByRoute.set(route, normalized); supportLayers.push(normalized);
    supportCounts.set(layer, supportCounts.get(layer) + 1);
  }
  const scope = vvExactKeys(sets.scope_reconciliation,
    ['jira', 'pull_request', 'primary_host_pages', 'authored_primary_pages', 'generated_primary_pages',
      'cli_support_layers', 'sdk_support_layers', 'total_host_routes', 'support_layer_rule',
      'prior_test_set_snapshot_sha256', 'historical_p1_state', 'historical_p1_check',
      'procedure_source_scope_reconciliation', 'command_occurrence_reconciliation',
      'self_test_command_topology_correction', 'nested_execution_status_semantics'],
    'invalid V&V scope reconciliation');
  const sourceScope = vvExactKeys(scope.procedure_source_scope_reconciliation,
    ['commands_checked', 'out_of_scope_commands_after_reconciliation',
      'historical_existing_carrier_scope_defects_corrected', 'newly_added_carriers_requiring_scope_expansion',
      'rule'], 'invalid V&V procedure-source reconciliation');
  if (sourceScope.commands_checked !== canonical.counts.command_carriers ||
    sourceScope.out_of_scope_commands_after_reconciliation !== 0 ||
    sourceScope.historical_existing_carrier_scope_defects_corrected !== 7 ||
    sourceScope.newly_added_carriers_requiring_scope_expansion !== 2 ||
    sourceScope.rule !== 'Every command source occurrence must be contained by its owning step span and test-set source context; parent headings include every child command section.') {
    throw new Error('mismatched V&V procedure-source reconciliation');
  }
  const selfTestCorrection = vvExactKeys(scope.self_test_command_topology_correction,
    ['finding_id', 'evidence_id', 'legacy_carrier_step', 'corrected_bindings',
      'historical_procedure_bindings_rekeyed', 'rule'],
    'invalid self-test command-topology correction');
  const topologyEvidenceId = vvEvidenceId(selfTestCorrection.evidence_id);
  const expectedSelfTestBindings = [
    ['CLM-b3cd48630e5f2b0c', 'ST-E01-normal', 'ST-E01-normal-s01', 'setup'],
    ['CLM-3ba3b25f5c3ddac1', 'ST-E01-normal', 'ST-E01-normal-s03', 'action'],
    ['CLM-3fa5d5948b34fc6a', 'ST-E01-bundle-dir', 'ST-E01-bundle-dir-s02', 'action'],
  ];
  const correctedBindings = vvArray(selfTestCorrection.corrected_bindings);
  if (selfTestCorrection.finding_id !== 'F-HOST-SELF-TEST-COMMAND-TOPOLOGY' ||
    topologyEvidenceId !== 'EV-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01' ||
    !allEvidenceIds.has(topologyEvidenceId) || !evidenceRefById.get(topologyEvidenceId) ||
    selfTestCorrection.legacy_carrier_step !== 'ST-E01-normal-s02' ||
    selfTestCorrection.historical_procedure_bindings_rekeyed !== 9 ||
    !/exact source span contains it/i.test(vvRequiredText(selfTestCorrection.rule)) ||
    correctedBindings.length !== expectedSelfTestBindings.length) {
    throw new Error('mismatched self-test command-topology correction');
  }
  correctedBindings.forEach((bindingValue, index) => {
    const binding = vvExactKeys(bindingValue,
      ['command_id', 'legacy_branch_id', 'legacy_step_id', 'branch_id', 'step_id',
        'step_role', 'source_file', 'heading', 'line_start', 'line_end', 'text_sha256',
        'preserved_execution_status', 'treatment'],
      'invalid self-test command-topology binding');
    const [commandId, branchId, stepId, stepRole] = expectedSelfTestBindings[index];
    const command = canonical.commandById.get(commandId);
    const commandKey = command && vvStatusKey('COMMAND', command);
    if (!command || binding.command_id !== commandId ||
      binding.legacy_branch_id !== 'ST-E01-normal' ||
      binding.legacy_step_id !== 'ST-E01-normal-s02' ||
      binding.branch_id !== branchId || binding.step_id !== stepId ||
      binding.step_role !== stepRole || command.route !== '/host/how-to-self-test' ||
      command.branch_id !== branchId || command.step_id !== stepId ||
      binding.source_file !== command.sourceContract.file ||
      vvSectionTitle(binding.heading) !== command.sourceContract.section ||
      binding.line_start !== command.sourceContract.line_start ||
      binding.line_end !== command.sourceContract.line_end ||
      vvSha256(binding.text_sha256, 'invalid self-test command-topology source hash') !==
        command.sourceContract.text_sha256 ||
      vvStatus(binding.preserved_execution_status) !== canonical.executionStatusByKey.get(commandKey) ||
      vvIdentifier(binding.treatment) !== command.treatment) {
      throw new Error('mismatched self-test command-topology binding');
    }
  });
  const occurrenceScope = vvExactKeys(scope.command_occurrence_reconciliation,
    ['static_inventory_unique_commands', 'procedure_command_carriers',
      'added_authored_fenced_occurrences', 'support_rule'],
    'invalid V&V command-occurrence reconciliation');
  const inventory = vvExactKeys(JSON.parse(vvHistoricalSourceFile('host-docs-verification-inventory.json',
    'missing canonical V&V command inventory').bytes.toString('utf8')),
  ['schema_version', 'source_revision', 'scope', 'safety', 'known_source_owner_gates', 'items',
    'summary', 'issues', 'content_fingerprint'], 'invalid canonical V&V command inventory structure');
  const commandAccess = vvExactKeys(JSON.parse(vvHistoricalSourceFile('host-docs-command-access.json',
    'missing hash-bound V&V command classification').bytes.toString('utf8')),
  ['schema_version', 'source_revision', 'content_fingerprint', 'command_count', 'group_counts',
    'dimension_counts', 'commands'], 'invalid hash-bound V&V command classification structure');
  const inventoryItems = vvArray(inventory.items);
  const inventoryCommands = inventoryItems.filter((item) => vvObject(item).kind === 'command');
  const inventoryCommandIds = inventoryCommands.map((item) => vvIdentifier(item.id));
  const projectInventoryCommand = (itemValue) => {
    const item = vvObject(itemValue);
    return {
      id: vvIdentifier(item.id), text: vvRawRequiredText(item.text),
      verification_tier: vvIdentifier(item.verification_tier), status: vvIdentifier(item.status),
      execution_access: vvObject(item.execution_access), locations: vvArray(item.locations),
    };
  };
  const classifiedCommands = vvArray(commandAccess.commands).map((commandValue) => {
    vvExactKeys(commandValue,
      ['id', 'text', 'verification_tier', 'status', 'execution_access', 'locations'],
      'invalid hash-bound V&V command classification');
    return projectInventoryCommand(commandValue);
  });
  const inventoryCommandProjection = inventoryCommands.map(projectInventoryCommand);
  const inventoryFingerprint = vvRequiredText(inventory.content_fingerprint);
  const classificationFingerprint = vvRequiredText(commandAccess.content_fingerprint);
  if (new Set(inventoryCommandIds).size !== inventoryCommandIds.length ||
    inventory.schema_version !== 3 || commandAccess.schema_version !== 1 ||
    !/^[a-f0-9]{40}$/.test(inventory.source_revision) ||
    inventory.source_revision !== commandAccess.source_revision ||
    !/^sha256:[a-f0-9]{64}$/.test(inventoryFingerprint) ||
    inventoryFingerprint !== classificationFingerprint ||
    commandAccess.command_count !== classifiedCommands.length ||
    JSON.stringify(inventoryCommandProjection) !== JSON.stringify(classifiedCommands) ||
    occurrenceScope.static_inventory_unique_commands !== inventoryCommandIds.length ||
    occurrenceScope.static_inventory_unique_commands !== 193 ||
    occurrenceScope.procedure_command_carriers !== canonical.counts.command_carriers ||
    vvObject(inventory.summary).command_count !== inventoryCommandIds.length ||
    occurrenceScope.support_rule !== 'The static inventory is the complete command/token occurrence ledger. Procedure carriers are the subset attached to Host workflows; generated wrappers, inline/display tokens, contextual cross-links, and duplicate occurrences remain inventory/support records rather than additional workflow carriers.') {
    throw new Error('mismatched V&V command-occurrence inventory reconciliation');
  }
  const inventoryById = new Map(inventoryCommands.map((item) => [item.id, item]));
  const addedOccurrenceIds = [];
  for (const value of vvArray(occurrenceScope.added_authored_fenced_occurrences)) {
    const occurrence = vvExactKeys(value,
      ['command_id', 'inventory_id', 'page_id', 'step_id', 'source_file', 'heading', 'line_start',
        'line_end', 'text_sha256', 'status', 'treatment', 'applicability'],
      'invalid added V&V command occurrence');
    const commandId = vvIdentifier(occurrence.command_id);
    const command = canonical.commandById.get(commandId);
    const inventoryItem = inventoryById.get(vvIdentifier(occurrence.inventory_id));
    const commandKey = command && vvStatusKey('COMMAND', command);
    const locations = inventoryItem ? vvArray(inventoryItem.locations) : [];
    if (!command || !inventoryItem || addedOccurrenceIds.includes(commandId) ||
      occurrence.page_id !== command.page_id || occurrence.step_id !== command.step_id ||
      occurrence.source_file !== command.sourceContract.file ||
      vvSectionTitle(occurrence.heading) !== command.sourceContract.section ||
      occurrence.line_start !== command.sourceContract.line_start ||
      occurrence.line_end !== command.sourceContract.line_end ||
      vvSha256(occurrence.text_sha256, 'invalid added V&V command hash') !== command.sourceContract.text_sha256 ||
      vvStatus(occurrence.status) !== canonical.executionStatusByKey.get(commandKey) ||
      vvIdentifier(occurrence.treatment) !== command.treatment ||
      vvRequiredText(occurrence.applicability).length === 0 || inventoryItem.text !==
        canonical.targetClaimByKey.get(commandKey) || !locations.some((locationValue) => {
        const location = vvObject(locationValue);
        return location.file === occurrence.source_file && location.line_start === occurrence.line_start &&
          location.line_end === occurrence.line_end && location.section === occurrence.heading &&
          location.source_type === 'authored';
      })) {
      throw new Error('mismatched added V&V command occurrence binding');
    }
    addedOccurrenceIds.push(commandId);
  }
  if (JSON.stringify(addedOccurrenceIds) !== JSON.stringify([
    'CLM-2872a25df6add3a5', 'CLM-1e2f077efd167bfd', 'CLM-0fa4c0088a41c909'])) {
    throw new Error('incomplete added V&V command-occurrence reconciliation');
  }
  if (scope.jira !== 'CON-1518' || scope.pull_request !== 185 || scope.primary_host_pages !== 40 ||
    scope.authored_primary_pages !== 39 || scope.generated_primary_pages !== 1 ||
    scope.cli_support_layers !== 18 || scope.sdk_support_layers !== 15 || scope.total_host_routes !== 73 ||
    scope.primary_host_pages + scope.cli_support_layers + scope.sdk_support_layers !== scope.total_host_routes ||
    scope.primary_host_pages !== canonical.pageById.size || scope.cli_support_layers !== supportCounts.get('CLI') ||
    scope.sdk_support_layers !== supportCounts.get('SDK') || !canonical.pageByRoute.has('/host/volume-offers') ||
    !/not independent Host workflows/i.test(vvRequiredText(scope.support_layer_rule)) ||
    !/DRAFT_NOT_FROZEN/i.test(vvRequiredText(scope.historical_p1_state)) ||
    scope.nested_execution_status_semantics !==
      'MIRROR_OF_CURRENT_STATUS_PROJECTION; evidence and rationale are in host-docs-test-results.json') {
    throw new Error('mismatched V&V scope reconciliation');
  }
  vvSha256(scope.prior_test_set_snapshot_sha256, 'invalid prior V&V snapshot');
  vvRequiredText(scope.historical_p1_check);
  if (bindingManifests.supportById.size !== supportLayers.length) {
    throw new Error('unused or missing V&V support-layer binding');
  }
  return { materialClaims, materialClaimsById, materialClaimsByPage,
    materialStatusCounts, materialPageDispositions, materialPageDispositionByPage, pageDispositionCounts,
    retiredMaterialClaims, retiredMaterialClaimsByPage, supportLayers, supportByRoute };
}
function loadCurrentStatusProjection(results, canonical, attemptsById, procedureEvidence, commandEvidenceById,
  snapshot, contracts, allEvidenceIds) {
  const canonicalTargets = canonical.targets;
  if (!('current_status_projection' in results)) return new Map();
  const projection = vvExactKeys(results.current_status_projection,
    ['schema_version', 'status_semantics', 'material_claim_page_dispositions_ref', 'records', 'counts'],
    'invalid V&V status projection');
  if (projection.schema_version !== '1.1' ||
    projection.status_semantics !== 'PROCEDURE_EXECUTION_AND_REQUIRED_CHILDREN_ONLY' ||
    projection.material_claim_page_dispositions_ref !==
      'verification/host-docs-test-sets.json#/material_claim_coverage/page_dispositions') {
    throw new Error('invalid V&V status projection semantics');
  }
  const statuses = new Map();
  const levels = Object.keys(VV_STATUS_TARGET_FIELDS);
  const statusNames = [...VV_TARGET_STATUSES];
  const levelCounts = new Map(levels.map((level) => [level, 0]));
  const statusCounts = new Map(statusNames.map((status) => [status, 0]));
  const levelStatusCounts = new Map(levels.map((level) => [level,
    new Map(statusNames.map((status) => [status, 0]))]));
  const evidenceDetailsFor = (evidenceId, targetKey, status) => {
    const procedure = procedureEvidence.get(evidenceId);
    const target = canonicalTargets.get(targetKey);
    if (procedure?.targets.get(targetKey) === status) {
      const attempt = attemptsById.get(procedure.attemptId);
      if (attempt && attempt.executionState === 'EXECUTED' && attempt.status !== 'STALE' && !attempt.supersededBy &&
        !(target?.command_id && attempt.supersededCommandIds.has(target.command_id))) {
        return { attemptId: procedure.attemptId, method: procedure.method,
          observation: procedure.observation, limitations: procedure.limitations,
          sourceRefs: procedure.sourceRefsByTarget.get(targetKey) || [] };
      }
    }
    const commandEvidence = commandEvidenceById.get(evidenceId);
    if (target?.command_id && commandEvidence?.status === status &&
      commandEvidence.commandIds.has(target.command_id)) {
      const attempt = attemptsById.get(commandEvidence.attemptId);
      if (attempt && attempt.executionState === 'EXECUTED' && attempt.status !== 'STALE' &&
        !attempt.supersededBy && !attempt.supersededCommandIds.has(target.command_id)) {
        // The status-basis method describes the evidence carrier, while the
        // attempt kind remains historical execution metadata.  A command
        // result may support only the exact COMMAND target it owns.
        return { attemptId: commandEvidence.attemptId, method: 'RETAINED_COMMAND_EXECUTION',
          observation: vvRequiredText(commandEvidence.observation),
          limitations: vvRequiredText(commandEvidence.claimLimit), sourceRefs: [] };
      }
    }
    return null;
  };
  const evidenceBindsTarget = (evidenceId, targetKey, status) =>
    Boolean(evidenceDetailsFor(evidenceId, targetKey, status));
  const leafKindsForStatus = {
    PASS: new Set(['DIRECT_OBSERVATION', 'STATIC_SOURCE_CONFORMANCE']),
    FAIL: new Set(['CONFIRMED_DEFECT']),
    BLOCKED: new Set(['UNAVAILABLE_PREREQUISITE']),
    UNVALIDATED: new Set(['NO_CLAIM_SUITABLE_EVIDENCE']),
    NOT_APPLICABLE: new Set(['APPROVED_NOT_APPLICABLE']),
  };
  const aggregateStatus = (values) => {
    if (!values.length) return null;
    for (const candidate of ['FAIL', 'BLOCKED', 'STALE', 'UNVALIDATED']) {
      if (values.includes(candidate)) return candidate;
    }
    if (values.every((status) => status === 'NOT_APPLICABLE')) return 'NOT_APPLICABLE';
    if (values.includes('PASS') && values.every((status) => ['PASS', 'NOT_APPLICABLE'].includes(status))) return 'PASS';
    throw new Error('unaggregatable V&V procedure statuses');
  };
  const loadRequiredEvidenceTypes = (value, message) => {
    const types = vvArray(value).map(vvIdentifier);
    if (!types.length || new Set(types).size !== types.length ||
      types.some((type) => !VV_REQUIRED_EVIDENCE_TYPES.has(type))) throw new Error(message);
    return types.map(vvText);
  };
  const loadAuthority = (value, basisKind, pageMeta, message) => {
    const authority = vvExactKeys(value,
      ['kind', 'source_refs', 'unresolved_owner_role', 'owner_confirmation_evidence_id'], message);
    const authorityKind = vvIdentifier(authority.kind);
    const expectedAuthorityKind = {
      APPROVED_NOT_APPLICABLE: 'APPROVED_CLASSIFICATION',
      STATIC_SOURCE_CONFORMANCE: 'CANONICAL_SOURCE',
      DIRECT_OBSERVATION: 'RETAINED_EVIDENCE',
      CONFIRMED_DEFECT: 'RETAINED_EVIDENCE',
      NO_CLAIM_SUITABLE_EVIDENCE: 'NOT_IDENTIFIED',
      UNAVAILABLE_PREREQUISITE: 'UNAVAILABLE_PREREQUISITE_OWNER',
      ROLLUP: 'DERIVED_FROM_CHILDREN',
      COMPOSITE_TARGET_AND_CHILDREN: 'COMPOSITE_TARGET_AND_CHILDREN',
    }[basisKind];
    const sourceRefs = vvArray(authority.source_refs).map((source) => vvSourceRef(source, pageMeta.sourceFile));
    const unresolvedOwnerRole = authority.unresolved_owner_role == null
      ? null : vvRequiredText(authority.unresolved_owner_role);
    const ownerEvidenceId = authority.owner_confirmation_evidence_id == null
      ? null : vvEvidenceId(authority.owner_confirmation_evidence_id);
    if (!expectedAuthorityKind || authorityKind !== expectedAuthorityKind ||
      new Set(sourceRefs.map((source) => JSON.stringify(source))).size !== sourceRefs.length ||
      (authorityKind === 'CANONICAL_SOURCE') !== Boolean(sourceRefs.length) ||
      (['NOT_IDENTIFIED', 'UNAVAILABLE_PREREQUISITE_OWNER'].includes(authorityKind)) !==
        Boolean(unresolvedOwnerRole) || ownerEvidenceId != null) {
      throw new Error(message);
    }
    return { kind: authorityKind, sourceRefs, unresolvedOwnerRole, ownerConfirmationEvidenceId: null };
  };
  const validateSatisfiedEvidenceTypes = (status, basisKind, requiredTypes, authority, message) => {
    if (status !== 'PASS') return;
    if (requiredTypes.includes('CANONICAL_IMPLEMENTATION_SOURCE') &&
      (basisKind !== 'STATIC_SOURCE_CONFORMANCE' || authority.kind !== 'CANONICAL_SOURCE' ||
        !authority.sourceRefs.length)) throw new Error(message);
    if (requiredTypes.includes('RUNTIME_OR_UI_OBSERVATION') && basisKind !== 'DIRECT_OBSERVATION') {
      throw new Error(message);
    }
    if (requiredTypes.includes('ACCOUNTABLE_OWNER_CONFIRMATION') &&
      !authority.ownerConfirmationEvidenceId) throw new Error(message);
  };
  const loadEvidenceBundle = (evidenceValue, methodsValue, key, status, message,
    expectedIds = null, expectedMethods = null) => {
    const ids = vvEvidenceIds(evidenceValue, allEvidenceIds, message);
    const methods = vvArray(methodsValue).map(vvIdentifier);
    if (methods.length !== ids.length || ids.some((id, index) => {
      const detail = evidenceDetailsFor(id, key, status);
      return !detail || detail.method !== methods[index];
    }) || (expectedIds && (ids.length !== expectedIds.length ||
      ids.some((id, index) => id !== expectedIds[index]))) ||
      (expectedMethods && (methods.length !== expectedMethods.length ||
        methods.some((method, index) => method !== expectedMethods[index])))) {
      throw new Error(message);
    }
    return { ids: ids.map(vvText), methods: methods.map(vvText),
      details: ids.map((id) => evidenceDetailsFor(id, key, status)) };
  };
  const validateStaticSourceBinding = (basisKind, authority, evidence, message) => {
    if (basisKind !== 'STATIC_SOURCE_CONFORMANCE') return;
    const boundSourceRefs = evidence.details.flatMap((detail) => detail.sourceRefs || []);
    if (!boundSourceRefs.length ||
      new Set(boundSourceRefs.map((source) => JSON.stringify(source))).size !== boundSourceRefs.length ||
      JSON.stringify(authority.sourceRefs) !== JSON.stringify(boundSourceRefs)) {
      throw new Error(message);
    }
  };
  const loadPrerequisite = (value, key, status, message) => {
    if (value == null) {
      if (status === 'BLOCKED') throw new Error(message);
      return null;
    }
    vvExactKeys(value, ['kind', 'description', 'evidence_ids', 'components'], message);
    const kind = vvIdentifier(value.kind);
    if (!new Set(['PERMISSION', 'AUTHORIZATION', 'ENVIRONMENT', 'INPUT', 'MULTIPLE',
      'DERIVED_FROM_CHILDREN']).has(kind) || status !== 'BLOCKED') throw new Error(message);
    const evidenceIds = vvEvidenceIds(value.evidence_ids, allEvidenceIds, message);
    if (evidenceIds.some((evidenceId) => !evidenceBindsTarget(evidenceId, key, 'BLOCKED'))) {
      throw new Error('unbound current-target V&V prerequisite evidence');
    }
    const componentKinds = new Set(['SOURCE', 'OWNER_CONFIRMATION', 'PERMISSION', 'AUTHORIZATION',
      'ENVIRONMENT', 'INPUT']);
    const components = vvArray(value.components).map((componentValue) => {
      const component = vvObject(componentValue);
      const hasViaTarget = component.via_target != null;
      vvExactKeys(component, hasViaTarget
        ? ['kind', 'description', 'evidence_ids', 'via_target']
        : ['kind', 'description', 'evidence_ids'], message);
      const componentKind = vvIdentifier(component.kind);
      if (!componentKinds.has(componentKind)) throw new Error(message);
      let componentTargetKey = key;
      let viaTarget = null;
      if (hasViaTarget) {
        vvExactKeys(component.via_target, ['level', 'target'], message);
        componentTargetKey = projectionTargetKey(component.via_target, canonicalTargets);
        viaTarget = { level: vvIdentifier(component.via_target.level),
          target: { ...component.via_target.target }, key: componentTargetKey };
      }
      const componentEvidenceIds = vvEvidenceIds(component.evidence_ids, allEvidenceIds, message);
      if (componentEvidenceIds.some((evidenceId) =>
        !evidenceBindsTarget(evidenceId, componentTargetKey, 'BLOCKED'))) {
        throw new Error('unbound V&V prerequisite component evidence');
      }
      return { kind: componentKind, description: vvRequiredText(component.description),
        evidenceIds: componentEvidenceIds.map(vvText), viaTarget };
    });
    if (!components.length || (kind === 'DERIVED_FROM_CHILDREN') !==
      components.every((component) => component.viaTarget) ||
      (kind !== 'DERIVED_FROM_CHILDREN' && components.some((component) => component.viaTarget)) ||
      (kind === 'MULTIPLE' && components.length < 2) ||
      (!['MULTIPLE', 'DERIVED_FROM_CHILDREN'].includes(kind) &&
        (components.length !== 1 || components[0].kind !== kind))) {
      throw new Error('mismatched V&V prerequisite aggregation');
    }
    return { kind, description: vvRequiredText(value.description),
      evidenceIds: evidenceIds.map(vvText), components };
  };
  const loadTargetBasis = (value, key, pageMeta) => {
    const targetBasis = vvExactKeys(value,
      ['status', 'basis_kind', 'required_evidence_types', 'authority', 'supporting_evidence_ids',
        'evidence_methods', 'unavailable_prerequisite', 'limitations'],
      'invalid V&V composite target basis');
    const status = vvStatus(targetBasis.status);
    const basisKind = vvIdentifier(targetBasis.basis_kind);
    if (!leafKindsForStatus[status]?.has(basisKind)) throw new Error('mismatched V&V composite target basis kind');
    const requiredEvidenceTypes = loadRequiredEvidenceTypes(targetBasis.required_evidence_types,
      'invalid V&V composite target required evidence');
    const authority = loadAuthority(targetBasis.authority, basisKind, pageMeta,
      'mismatched V&V composite target authority');
    validateSatisfiedEvidenceTypes(status, basisKind, requiredEvidenceTypes, authority,
      'unsatisfied V&V composite target evidence type');
    const evidence = loadEvidenceBundle(targetBasis.supporting_evidence_ids, targetBasis.evidence_methods,
      key, status, 'mismatched V&V composite target evidence');
    validateStaticSourceBinding(basisKind, authority, evidence,
      'mismatched V&V composite target canonical-source/evidence binding');
    const unavailablePrerequisite = loadPrerequisite(targetBasis.unavailable_prerequisite, key, status,
      'invalid V&V composite target prerequisite');
    return { status, basisKind, requiredEvidenceTypes, authority,
      supportingEvidenceIds: evidence.ids, evidenceMethods: evidence.methods,
      unavailablePrerequisite, limitations: vvRequiredText(targetBasis.limitations) };
  };
  const loadStatusBasis = (row, key, currentStatus, rowEvidenceIds, rowEvidenceMethods) => {
    const basis = vvExactKeys(row.status_basis,
      ['basis_kind', 'subject', 'required_evidence_types', 'authority', 'supporting_evidence_ids',
        'evidence_methods', 'unavailable_prerequisite', 'claim_impact', 'limitations', 'next_action',
        'source_snapshot_sha256', 'derived_from', 'target_basis'], 'invalid V&V status basis');
    const basisKind = vvIdentifier(basis.basis_kind);
    const aggregateKinds = new Set(['ROLLUP', 'COMPOSITE_TARGET_AND_CHILDREN']);
    if (!leafKindsForStatus[currentStatus]?.has(basisKind) && !aggregateKinds.has(basisKind)) {
      throw new Error('mismatched V&V status basis kind');
    }
    const canonicalTarget = canonicalTargets.get(key);
    const pageMeta = canonical.pageById.get(canonicalTarget.page_id);
    const subject = vvExactKeys(basis.subject,
      ['route', 'source_file', 'headings', 'source_spans', 'claim', 'claim_refs', 'claim_refs_role',
        'no_material_claim_reason'],
      'invalid V&V status subject');
    if (subject.claim_refs_role !== 'SOURCE_SPAN_OVERLAP_ONLY_NOT_STATUS_INHERITANCE') {
      throw new Error('invalid V&V status subject claim-reference role');
    }
    if (vvCanonicalRoute(subject.route) !== pageMeta.route || vvRequiredText(subject.source_file) !== pageMeta.sourceFile) {
      throw new Error('mismatched V&V status subject page');
    }
    const headings = vvHeadingsForSubject(subject.headings, pageMeta);
    const spans = vvArray(subject.source_spans).map((span) => vvSourceSpan(span, pageMeta.sourceIndex,
      'invalid V&V status subject span'));
    if ((row.level === 'PAGE') !== (spans.length === 0) || spans.some((span) =>
      !headings.some((heading) => vvSpanOverlapsHeading(span, heading, pageMeta.sourceIndex))) ||
      (row.level !== 'PAGE' && headings.some((heading) => !spans.some((span) =>
        vvSpanOverlapsHeading(span, heading, pageMeta.sourceIndex))))) {
      throw new Error('mismatched V&V status subject heading/span');
    }
    const claimRefs = vvArray(subject.claim_refs).map(vvIdentifier);
    const noMaterialClaimReason = subject.no_material_claim_reason == null
      ? null : vvRequiredText(subject.no_material_claim_reason);
    if (new Set(claimRefs).size !== claimRefs.length || Boolean(claimRefs.length) === Boolean(noMaterialClaimReason)) {
      throw new Error('invalid V&V status subject claim binding');
    }
    const expectedClaimRefs = canonical.claimRefsByKey.get(key);
    if (claimRefs.length !== expectedClaimRefs.length ||
      claimRefs.some((claimId, index) => claimId !== expectedClaimRefs[index])) {
      throw new Error('mismatched V&V status subject claim binding');
    }
    const expectedTargetClaim = canonical.targetClaimByKey.get(key);
    const subjectClaim = vvRequiredText(subject.claim);
    if (expectedTargetClaim != null && subjectClaim !== expectedTargetClaim) {
      throw new Error('mismatched V&V status subject claim');
    }
    for (const claimId of claimRefs) {
      const materialClaim = contracts.materialClaimsById.get(claimId);
      if (!materialClaim || materialClaim.pageId !== canonicalTarget.page_id) {
        throw new Error('unknown V&V status subject claim');
      }
    }
    if (spans.length) {
      const detachedClaimRef = claimRefs.some((claimId) => {
        const materialClaim = contracts.materialClaimsById.get(claimId);
        return !materialClaim.spans.some((claimSpan) => spans.some((subjectSpan) =>
          claimSpan.start <= subjectSpan.end && subjectSpan.start <= claimSpan.end));
      });
      if (detachedClaimRef) {
        throw new Error('mismatched V&V status claim-reference source-span overlap');
      }
    }
    const requiredEvidenceTypes = loadRequiredEvidenceTypes(basis.required_evidence_types,
      'invalid V&V status required evidence');
    const authority = loadAuthority(basis.authority, basisKind, pageMeta, 'mismatched V&V status authority');
    validateSatisfiedEvidenceTypes(currentStatus, basisKind, requiredEvidenceTypes, authority,
      'unsatisfied V&V status required evidence type');
    const evidence = loadEvidenceBundle(basis.supporting_evidence_ids, basis.evidence_methods, key,
      currentStatus, 'mismatched V&V status-basis evidence', rowEvidenceIds, rowEvidenceMethods);
    validateStaticSourceBinding(basisKind, authority, evidence,
      'mismatched V&V status canonical-source/evidence binding');
    const unavailablePrerequisite = loadPrerequisite(basis.unavailable_prerequisite, key, currentStatus,
      'invalid V&V unavailable prerequisite');
    const nextAction = basis.next_action == null ? null : vvRequiredText(basis.next_action);
    if (['FAIL', 'BLOCKED', 'UNVALIDATED'].includes(currentStatus) && !nextAction) {
      throw new Error('missing V&V status-basis next action');
    }
    if (currentStatus === 'NOT_APPLICABLE' && nextAction) throw new Error('invalid NOT_APPLICABLE next action');
    if (vvSha256(basis.source_snapshot_sha256, 'invalid V&V status-basis snapshot') !== snapshot) {
      throw new Error('stale V&V status basis');
    }
    const derivedFrom = vvArray(basis.derived_from).map((value) => {
      vvExactKeys(value, ['level', 'target', 'current_status', 'required'], 'invalid V&V status derivation');
      if (typeof value.required !== 'boolean') throw new Error('invalid V&V child requirement');
      const childKey = projectionTargetKey(value, canonicalTargets);
      return { level: vvIdentifier(value.level), target: { ...value.target },
        currentStatus: vvStatus(value.current_status), required: value.required, key: childKey };
    });
    const targetBasis = basis.target_basis == null ? null : loadTargetBasis(basis.target_basis, key, pageMeta);
    if ((basisKind === 'COMPOSITE_TARGET_AND_CHILDREN') !== Boolean(targetBasis)) {
      throw new Error('mismatched V&V composite target basis');
    }
    return {
      basisKind,
      subject: { route: pageMeta.route, pageTitle: pageMeta.title, headings, claim: subjectClaim,
        claimRefs: claimRefs.map(vvText), noMaterialClaimReason },
      requiredEvidenceTypes: requiredEvidenceTypes.map(vvText),
      authority,
      supportingEvidenceIds: evidence.ids, evidenceMethods: evidence.methods,
      unavailablePrerequisite,
      claimImpact: vvRequiredText(basis.claim_impact), limitations: vvRequiredText(basis.limitations), nextAction,
      derivedFrom, targetBasis,
    };
  };
  for (const record of vvArray(projection.records)) {
    const row = vvExactKeys(record,
      ['level', 'target', 'current_status', 'attempt_id', 'evidence_ids', 'rationale', 'status_basis'],
      'invalid current V&V status record');
    const key = projectionTargetKey(row, canonicalTargets);
    if (statuses.has(key)) throw new Error('duplicate current V&V status');
    const attemptId = vvAttemptId(row.attempt_id);
    const attempt = attemptsById.get(attemptId);
    const canonicalTarget = canonicalTargets.get(key);
    if (!attempt || attempt.supersededBy || attempt.status === 'STALE' ||
      (canonicalTarget.command_id && attempt.supersededCommandIds.has(canonicalTarget.command_id))) {
      throw new Error('unsafe current V&V status attempt');
    }
    const level = vvIdentifier(row.level);
    const currentStatus = vvStatus(row.current_status);
    levelCounts.set(level, levelCounts.get(level) + 1);
    statusCounts.set(currentStatus, statusCounts.get(currentStatus) + 1);
    levelStatusCounts.get(level).set(currentStatus, levelStatusCounts.get(level).get(currentStatus) + 1);
    const evidence = vvEvidenceIds(row.evidence_ids, allEvidenceIds, 'invalid V&V status evidence');
    const details = evidence.map((evidenceId) => evidenceDetailsFor(evidenceId, key, currentStatus));
    if (details.some((detail) => !detail || detail.attemptId !== attemptId)) {
      throw new Error('mismatched current V&V evidence');
    }
    const joinDistinct = (field) => [...new Set(details.map((item) => item[field]))].join(' | ');
    const basis = loadStatusBasis(row, key, currentStatus, evidence.map(vvEvidenceId), details.map((item) => item.method));
    statuses.set(key, {
      status: currentStatus, attemptId: vvText(attemptId), evidenceIds: evidence.map(vvEvidenceId),
      method: joinDistinct('method'), observation: joinDistinct('observation'),
      limitations: joinDistinct('limitations'),
      rationale: vvRequiredText(row.rationale),
      basis,
    });
  }

  const declared = vvExactKeys(projection.counts, ['targets', 'levels', 'statuses', 'by_level'],
    'invalid current V&V projection counts');
  if (declared.targets !== statuses.size || declared.targets !== canonicalTargets.size) {
    throw new Error('invalid current V&V projection target count');
  }
  const compareCounts = (value, actual, allowed, message) => {
    const bucket = vvObject(value);
    if (Object.keys(bucket).some((name) => !allowed.includes(name))) throw new Error(message);
    for (const name of allowed) {
      const expected = bucket[name] ?? 0;
      if (!Number.isInteger(expected) || expected < 0 || expected !== actual.get(name)) throw new Error(message);
    }
  };
  compareCounts(declared.levels, levelCounts, levels, 'invalid current V&V projection level counts');
  compareCounts(declared.statuses, statusCounts, statusNames, 'invalid current V&V projection status counts');
  const byLevel = vvObject(declared.by_level);
  if (Object.keys(byLevel).length !== levels.length || levels.some((level) => !(level in byLevel))) {
    throw new Error('invalid current V&V projection level/status counts');
  }
  for (const level of levels) {
    compareCounts(byLevel[level], levelStatusCounts.get(level), statusNames,
      'invalid current V&V projection level/status counts');
  }

  for (const [key, current] of statuses) {
    const expectedChildren = canonical.childrenByKey.get(key) || [];
    const actualChildren = current.basis.derivedFrom;
    const isAggregate = ['ROLLUP', 'COMPOSITE_TARGET_AND_CHILDREN'].includes(current.basis.basisKind);
    if (expectedChildren.length !== actualChildren.length || Boolean(expectedChildren.length) !== isAggregate) {
      throw new Error('invalid V&V direct-child rollup topology');
    }
    for (let index = 0; index < expectedChildren.length; index += 1) {
      const expected = expectedChildren[index];
      const actual = actualChildren[index];
      const childStatus = statuses.get(expected.key)?.status;
      if (!actual || actual.key !== expected.key || actual.level !== expected.level ||
        actual.currentStatus !== childStatus || actual.required !== expected.required) {
        throw new Error('mismatched V&V direct-child rollup status');
      }
    }
    const requiredStatuses = expectedChildren.filter((child) => child.required)
      .map((child) => statuses.get(child.key).status);
    if (current.basis.basisKind === 'ROLLUP' &&
      aggregateStatus(requiredStatuses) !== current.status) {
      throw new Error('mismatched V&V required-child rollup result');
    }
    if (current.basis.basisKind === 'ROLLUP' &&
      JSON.stringify(current.basis.requiredEvidenceTypes) !== JSON.stringify(['CHILD_STATUS_ROLLUP'])) {
      throw new Error('mismatched V&V required-child evidence contract');
    }
    if (current.basis.basisKind === 'COMPOSITE_TARGET_AND_CHILDREN' &&
      aggregateStatus([current.basis.targetBasis.status, ...requiredStatuses]) !== current.status) {
      throw new Error('mismatched V&V composite target-and-child result');
    }
    if (current.basis.basisKind === 'COMPOSITE_TARGET_AND_CHILDREN') {
      const expectedEvidenceTypes = [...new Set([
        ...current.basis.targetBasis.requiredEvidenceTypes, 'CHILD_STATUS_ROLLUP',
      ])];
      if (JSON.stringify(current.basis.requiredEvidenceTypes) !== JSON.stringify(expectedEvidenceTypes)) {
        throw new Error('mismatched V&V composite evidence contract');
      }
    }
  }

  const comparableComponent = (component, viaTarget = component.viaTarget) => ({
    kind: component.kind, description: component.description, evidenceIds: component.evidenceIds,
    ...(viaTarget ? { viaTarget: { level: viaTarget.level, target: viaTarget.target } } : {}),
  });
  for (const [key, current] of statuses) {
    const prerequisite = current.basis.unavailablePrerequisite;
    if (current.status !== 'BLOCKED') continue;
    const children = canonical.childrenByKey.get(key) || [];
    const inputs = [];
    if (current.basis.basisKind === 'UNAVAILABLE_PREREQUISITE') {
      inputs.push({ key, level: key.split('\0')[0], target: canonicalTargets.get(key), prerequisite });
    } else if (current.basis.targetBasis?.status === 'BLOCKED') {
      inputs.push({ key, level: key.split('\0')[0], target: canonicalTargets.get(key),
        prerequisite: current.basis.targetBasis.unavailablePrerequisite });
    }
    for (const child of children) {
      const childStatus = statuses.get(child.key);
      if (child.required && childStatus.status === 'BLOCKED') {
        inputs.push({ key: child.key, level: child.level, target: child.target,
          prerequisite: childStatus.basis.unavailablePrerequisite });
      }
    }
    if (!inputs.length || inputs.some((input) => !input.prerequisite)) {
      throw new Error('BLOCKED V&V status lacks an originating prerequisite');
    }
    let expectedPrerequisite;
    if (inputs.length === 1 && inputs[0].key === key && !children.some((child) => child.required)) {
      expectedPrerequisite = inputs[0].prerequisite;
    } else {
      const components = [];
      const seen = new Set();
      for (const input of inputs) {
        for (const component of input.prerequisite.components) {
          // A derived prerequisite keeps the deepest target that actually owns
          // the component evidence.  Only a root component lacks viaTarget and
          // therefore acquires the immediate blocked input as its origin.
          const normalized = comparableComponent(component, component.viaTarget ||
            { level: input.level, target: input.target, key: input.key });
          const marker = JSON.stringify(normalized);
          if (!seen.has(marker)) {
            seen.add(marker);
            components.push(normalized);
          }
        }
      }
      expectedPrerequisite = {
        kind: 'DERIVED_FROM_CHILDREN',
        description: `${components.length} concrete prerequisite component(s) from required blocked child targets are unavailable; each component names its originating target.`,
        evidenceIds: current.basis.supportingEvidenceIds,
        components,
      };
    }
    const actualComparable = {
      kind: prerequisite.kind, description: prerequisite.description,
      evidenceIds: prerequisite.evidenceIds,
      components: prerequisite.components.map((component) => comparableComponent(component)),
    };
    const expectedComparable = {
      kind: expectedPrerequisite.kind, description: expectedPrerequisite.description,
      evidenceIds: expectedPrerequisite.evidenceIds,
      components: expectedPrerequisite.components.map((component) => comparableComponent(component)),
    };
    if (JSON.stringify(actualComparable) !== JSON.stringify(expectedComparable)) {
      throw new Error('mismatched V&V unavailable-prerequisite origin aggregation');
    }
  }

  for (const [key, current] of statuses) {
    if (!key.startsWith('STEP\u0000') || current.status !== 'NOT_APPLICABLE') continue;
    const step = canonicalTargets.get(key);
    const children = [...canonicalTargets.entries()].filter(([childKey, target]) =>
      childKey.startsWith('COMMAND\u0000') && target.page_id === step.page_id &&
      target.test_set_id === step.test_set_id && target.branch_id === step.branch_id &&
      target.step_id === step.step_id);
    if (children.length && children.some(([childKey]) => statuses.get(childKey)?.status !== 'NOT_APPLICABLE')) {
      throw new Error('NOT_APPLICABLE V&V step has executable or unvalidated child');
    }
  }
  return statuses;
}
function loadCliSignatureChecks(canonical) {
  const artifact = vvRepositoryFile('host-docs-cli-command-check.json',
    'missing generated Host CLI signature check');
  const value = vvExactKeys(JSON.parse(artifact.bytes.toString('utf8')),
    ['schema_version', 'vast_cli_source', 'safety', 'summary',
      'documented_registered_signatures', 'records'],
    'invalid generated Host CLI signature check');
  const source = vvExactKeys(value.vast_cli_source, ['revision', 'branch', 'dirty'],
    'invalid Host CLI signature source');
  const revision = vvRequiredText(source.revision);
  if (value.schema_version !== 2 || !/^[a-f0-9]{40}$/.test(revision) || source.dirty !== false) {
    throw new Error('Host CLI signature check is not pinned to a clean revision');
  }
  const safety = vvExactKeys(value.safety,
    ['api_commands_executed', 'credentials_read_or_supplied', 'method'],
    'invalid Host CLI signature safety declaration');
  if (safety.api_commands_executed !== false || safety.credentials_read_or_supplied !== false ||
    !/argparse registrations/i.test(vvRequiredText(safety.method))) {
    throw new Error('unsafe or ambiguous Host CLI signature check');
  }
  const summary = vvExactKeys(value.summary,
    ['source_files_scanned', 'registered_cli_commands', 'documented_invocation_occurrences',
      'documented_registered_signatures', 'status_counts', 'actionable_findings'],
    'invalid Host CLI signature summary');
  const records = vvArray(value.records);
  if (summary.documented_invocation_occurrences !== records.length ||
    !Number.isInteger(summary.source_files_scanned) || summary.source_files_scanned < 1 ||
    !Number.isInteger(summary.registered_cli_commands) || summary.registered_cli_commands < 1) {
    throw new Error('mismatched Host CLI signature counts');
  }
  const normalizedCommand = (text) => vvRawRequiredText(text).replace(/\\\s*/g, ' ')
    .replace(/\s+/g, ' ').trim();
  const canonicalByOccurrence = new Map();
  for (const [commandId, command] of canonical.commandById) {
    const key = `${command.sourceContract.file}\0${command.sourceContract.line_start}`;
    canonicalByOccurrence.set(key, [...(canonicalByOccurrence.get(key) || []), { commandId, command }]);
  }
  const byFindingId = new Map();
  const byCommandId = new Map();
  const statusCounts = new Map();
  let actionable = 0;
  for (const recordValue of records) {
    const record = vvExactKeys(recordValue,
      ['id', 'file', 'line', 'invocation', 'executable', 'signature', 'flags',
        'unknown_flags', 'status', 'detail', 'handler_source'],
      'invalid Host CLI signature record');
    const id = vvIdentifier(record.id);
    const file = vvRequiredText(record.file);
    const line = record.line;
    const executable = vvRequiredText(record.executable);
    const signature = vvRequiredText(record.signature);
    const status = vvIdentifier(record.status);
    const flags = vvArray(record.flags).map(vvRequiredText);
    const unknownFlags = vvArray(record.unknown_flags).map(vvRequiredText);
    const expectedId = `cli-${crypto.createHash('sha256')
      .update(`${file}\0${line}\0${executable}\0${signature}`).digest('hex').slice(0, 10)}`;
    if (id !== expectedId || byFindingId.has(id) || !Number.isInteger(line) || line < 1 ||
      !/^(?:host|snippets\/host)\/[A-Za-z0-9._/-]+\.mdx$/.test(file) ||
      file.split('/').includes('..') || new Set(flags).size !== flags.length ||
      new Set(unknownFlags).size !== unknownFlags.length ||
      !new Set(['pass', 'command-family-reference', 'incomplete-placeholder',
        'wrong-executable', 'unknown-command', 'unknown-option']).has(status)) {
      throw new Error('invalid Host CLI signature record identity');
    }
    statusCounts.set(status, (statusCounts.get(status) || 0) + 1);
    if (['wrong-executable', 'unknown-command', 'unknown-option'].includes(status)) actionable += 1;
    let handlerSource = null;
    if (record.handler_source != null) {
      const handler = vvExactKeys(record.handler_source,
        ['line_end', 'line_start', 'path', 'symbol'], 'invalid Host CLI handler source');
      const handlerPath = vvRequiredText(handler.path);
      const symbol = vvIdentifier(handler.symbol);
      if (!/^vastai\/cli\/commands\/[A-Za-z0-9._/-]+\.py$/.test(handlerPath) ||
        handlerPath.split('/').includes('..') || !Number.isInteger(handler.line_start) ||
        !Number.isInteger(handler.line_end) || handler.line_start < 1 ||
        handler.line_end < handler.line_start) {
        throw new Error('invalid Host CLI handler source range');
      }
      const sourceText = vvPinnedExternalSource('vast-ai/vast-cli', revision, handlerPath);
      const sourceLines = sourceText.split(/\r?\n/);
      const sourceSlice = sourceLines.slice(handler.line_start - 1, handler.line_end).join('\n');
      if (handler.line_end > sourceLines.length ||
        !new RegExp(`(?:def|async\\s+def)\\s+${symbol.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`)
          .test(sourceSlice)) {
        throw new Error('unresolved Host CLI handler source');
      }
      handlerSource = {
        repository: 'vast-ai/vast-cli', revision, path: handlerPath, symbol,
        lineStart: handler.line_start, lineEnd: handler.line_end,
        href: `https://github.com/vast-ai/vast-cli/blob/${revision}/${handlerPath}#L${
          handler.line_start}-L${handler.line_end}`,
      };
    }
    if (status === 'pass' && !handlerSource) throw new Error('registered Host CLI signature lacks handler source');
    const normalized = {
      id, file, line, invocation: vvRawRequiredText(record.invocation), executable, signature,
      flags, unknownFlags, status, detail: vvRequiredText(record.detail), handlerSource,
      sourceRevision: revision, method: vvRequiredText(safety.method),
      claimLimit: 'Static parser/handler registration only. No API command, Host operation, credentialed authentication, rental, or workload was executed by this check.',
    };
    byFindingId.set(id, normalized);
    const occurrence = canonicalByOccurrence.get(`${file}\0${line}`) || [];
    const commandMatch = occurrence.find(({ command }) =>
      normalizedCommand(command.text) === normalizedCommand(normalized.invocation));
    if (commandMatch) {
      if (byCommandId.has(commandMatch.commandId)) throw new Error('duplicate Host CLI command/signature binding');
      const bound = { ...normalized, commandId: commandMatch.commandId };
      byFindingId.set(id, bound);
      byCommandId.set(commandMatch.commandId, bound);
    }
  }
  const declaredStatusCounts = vvObject(summary.status_counts);
  if (Object.keys(declaredStatusCounts).some((status) => declaredStatusCounts[status] !== statusCounts.get(status)) ||
    [...statusCounts].some(([status, count]) => declaredStatusCounts[status] !== count) ||
    summary.actionable_findings !== actionable ||
    summary.documented_registered_signatures !== vvArray(value.documented_registered_signatures).length) {
    throw new Error('mismatched Host CLI signature result summary');
  }
  return {
    byFindingId, byCommandId, sourceRevision: revision, method: vvRequiredText(safety.method),
    artifactSha256: crypto.createHash('sha256').update(artifact.bytes).digest('hex'),
  };
}
function loadVerificationEvidence() {
  try {
    // The three canonical package files are current evidence, not historical
    // source input.  Keep them on the live regular-file path so a corrupt or
    // substituted package cannot be accepted merely because the Git snapshot
    // remains readable.
    const bytes = VV_FILES.map((file) => {
      const safe = file.replace(/^\.\//, '');
      try { return vvRepositoryFile(safe, 'invalid canonical V&V package file').bytes; } catch (error) {
        // Preserve the established sanitized ENOENT failure for an absent
        // package, while keeping malformed/symlinked existing files rejected.
        try { fs.lstatSync(new URL(file, import.meta.url)); } catch { return fs.readFileSync(new URL(file, import.meta.url)); }
        throw error;
      }
    });
    const [sets, results, scores] = bytes.map((value) => JSON.parse(value.toString('utf8')));
    vvExactKeys(sets,
      ['schema_version', 'record_type', 'created_at', 'reconciled_at', 'state', 'source', 'method',
        'pages', 'counts', 'material_claims', 'retired_material_claims', 'material_claim_coverage',
        'support_layers', 'scope_reconciliation'], 'invalid V&V test-set package structure');
    vvExactKeys(results,
      ['schema_version', 'record_type', 'test_set_snapshot_sha256', 'raw_evidence_policy', 'attempts',
        'procedure_results', 'command_results', 'direct_proof_ceilings', 'findings',
        'material_claim_results', 'support_layer_results', 'current_status_projection',
        'evidence_artifact_manifest', 'counts'],
      'invalid V&V result package structure');
    vvExactKeys(scores,
      ['schema_version', 'record_type', 'test_set_snapshot_sha256', 'rubric', 'records',
        'not_applicable_records', 'withdrawn_records', 'direct_evidence_bindings', 'counts'],
      'invalid V&V score package structure');
    if (sets.schema_version !== '1.0' || sets.record_type !== 'HOST_DOCS_PAGE_TEST_SETS' ||
      results.schema_version !== '1.0' || results.record_type !== 'HOST_DOCS_TEST_RESULTS' ||
      scores.schema_version !== '1.0' || scores.record_type !== 'HOST_DOCS_COMMAND_CONTEXT_SCORES') {
      throw new Error('unsupported V&V package schema');
    }
    const snapshot = crypto.createHash('sha256').update(bytes[0]).digest('hex');
    if (results.test_set_snapshot_sha256 !== snapshot || scores.test_set_snapshot_sha256 !== snapshot) {
      throw new Error('V&V snapshot mismatch');
    }
    const pages = vvArray(sets.pages);
    const canonical = canonicalStatusTargets(pages, sets.counts);
    const cliSignatureChecks = loadCliSignatureChecks(canonical);
    validateVvSourceProvenance(sets, pages);
    const evidenceArtifactManifest = new Map();
    for (const value of vvArray(results.evidence_artifact_manifest)) {
      const artifact = vvExactKeys(value, ['path', 'sha256', 'role'],
        'invalid V&V evidence artifact manifest');
      const artifactPath = vvEvidenceRef(artifact.path);
      const artifactSha256 = vvSha256(artifact.sha256, 'invalid V&V evidence artifact hash');
      const role = vvIdentifier(artifact.role);
      const bytes = vvRepositoryFile(artifactPath, 'invalid retained V&V evidence artifact').bytes;
      const expectedRole = artifactPath ===
        'verification/evidence/2026-09-03-host-repository-rebase-01/result.md'
        ? 'CURRENT_REPOSITORY_RECONCILIATION_RETAINED_RESULT' : 'RETAINED_ATTEMPT_EVIDENCE';
      if (evidenceArtifactManifest.has(artifactPath)) {
        throw new Error('duplicate retained V&V evidence artifact manifest entry');
      }
      if (role !== expectedRole) throw new Error('invalid retained V&V evidence artifact role');
      if (crypto.createHash('sha256').update(bytes).digest('hex') !== artifactSha256) {
        throw new Error('retained V&V evidence artifact content does not match its manifest hash');
      }
      evidenceArtifactManifest.set(artifactPath, { sha256: artifactSha256, role });
    }
    if (!evidenceArtifactManifest.size) throw new Error('missing V&V evidence artifact manifest');
    const canonicalTargets = canonical.targets;
    const canonicalCommandIds = new Set(canonical.commandById.keys());
    const withdrawnCommandIds = new Set();
    const withdrawnRecords = [];
    for (const withdrawn of vvArray(scores.withdrawn_records || [])) {
      const row = vvExactKeys(vvObject(withdrawn),
        ['command_id', 'page_route', 'original_execution_status', 'original_score',
          'current_execution_status', 'current_score', 'reason', 'qualification_evidence_ref',
          'current_reassessment'], 'invalid withdrawn V&V assessment structure');
      const commandId = vvIdentifier(row.command_id);
      if (withdrawnCommandIds.has(commandId)) throw new Error('duplicate withdrawn V&V command');
      withdrawnCommandIds.add(commandId);
      const pageRoute = vvCanonicalRoute(row.page_route);
      if (!canonical.pageByRoute.has(pageRoute)) throw new Error('unknown withdrawn V&V page');
      const originalExecutionStatus = vvStatus(row.original_execution_status);
      const currentExecutionStatus = vvStatus(row.current_execution_status);
      const currentScore = row.current_score;
      if (currentScore !== null && (!Number.isInteger(currentScore) || currentScore < 1 || currentScore > 3)) {
        throw new Error('invalid withdrawn V&V current score');
      }
      if (!Number.isInteger(row.original_score) || row.original_score < 1 || row.original_score > 3) {
        throw new Error('invalid withdrawn V&V original score');
      }
      withdrawnRecords.push({
        commandId, pageRoute, originalExecutionStatus, originalScore: row.original_score,
        currentExecutionStatus, currentScore, reason: vvRequiredText(row.reason),
        qualificationEvidenceRef: vvEvidenceRef(row.qualification_evidence_ref),
        currentReassessment: vvRequiredText(row.current_reassessment),
        retired: !canonicalCommandIds.has(commandId),
      });
    }
    const attempts = vvArray(results.attempts);
    const attemptsById = new Map();
    const hashBoundEvidenceRefs = new Set();
    for (const attempt of attempts) {
      const row = vvObject(attempt);
      const requiredAttemptKeys = ['attempt_id', 'kind', 'status', 'execution_state',
        'evidence_ref', 'evidence_ref_sha256'];
      const optionalAttemptKeys = new Set(['summary', 'reason', 'manifest_sha256',
        'qualification_superseded_by', 'qualification_superseded_targets', 'qualification_command_ids',
        'accounting_corrected_by']);
      if (requiredAttemptKeys.some((key) => !(key in row)) ||
        Object.keys(row).some((key) => !requiredAttemptKeys.includes(key) && !optionalAttemptKeys.has(key))) {
        throw new Error('invalid V&V attempt structure');
      }
      if (row.summary != null) vvObject(row.summary);
      if (row.reason != null) vvRequiredText(row.reason);
      const manifestSha256 = row.manifest_sha256 == null ? null
        : vvSha256(row.manifest_sha256, 'invalid V&V attempt source-manifest hash');
      const attemptId = vvAttemptId(row.attempt_id);
      if (attemptsById.has(attemptId)) throw new Error('duplicate V&V attempt');
      const supersededBy = row.qualification_superseded_by == null ? null : vvAttemptId(row.qualification_superseded_by);
      let scopedSupersededBy = null;
      let supersededCommandIds = new Set();
      if (row.qualification_superseded_targets != null) {
        const scoped = vvObject(row.qualification_superseded_targets);
        if (Object.keys(scoped).sort().join(',') !== 'command_ids,superseded_by') {
          throw new Error('invalid scoped V&V supersession');
        }
        scopedSupersededBy = vvAttemptId(scoped.superseded_by);
        const commandIds = vvArray(scoped.command_ids).map(vvIdentifier);
        if (!commandIds.length || new Set(commandIds).size !== commandIds.length ||
          commandIds.some((commandId) => !canonicalCommandIds.has(commandId) && !withdrawnCommandIds.has(commandId))) {
          throw new Error('invalid scoped V&V supersession');
        }
        supersededCommandIds = new Set(commandIds);
      }
      const qualificationCommandIds = row.qualification_command_ids == null
        ? [] : vvArray(row.qualification_command_ids).map(vvIdentifier);
      if (new Set(qualificationCommandIds).size !== qualificationCommandIds.length ||
        qualificationCommandIds.some((commandId) =>
          !canonicalCommandIds.has(commandId) && !withdrawnCommandIds.has(commandId))) {
        throw new Error('invalid V&V qualification target set');
      }
      if (supersededBy && scopedSupersededBy) throw new Error('ambiguous V&V supersession');
      const accountingCorrectedBy = row.accounting_corrected_by == null
        ? null : vvAttemptId(row.accounting_corrected_by);
      const evidenceRef = vvEvidenceRef(row.evidence_ref);
      const evidenceRefSha256 = vvSha256(row.evidence_ref_sha256, 'missing V&V attempt evidence hash');
      const manifestEntry = evidenceArtifactManifest.get(evidenceRef);
      if (!manifestEntry || manifestEntry.sha256 !== evidenceRefSha256) {
        throw new Error('unmanifested or mismatched V&V attempt evidence hash');
      }
      if (manifestSha256 && !vvRepositoryFile(evidenceRef, 'missing V&V attempt evidence artifact').bytes
        .includes(Buffer.from(manifestSha256))) {
        throw new Error('unbound V&V attempt source-manifest hash');
      }
      hashBoundEvidenceRefs.add(evidenceRef);
      attemptsById.set(attemptId, {
        status: vvStatus(row.status, VV_ATTEMPT_STATUSES), supersededBy, scopedSupersededBy,
        supersededCommandIds, qualificationCommandIds: new Set(qualificationCommandIds),
        kind: vvIdentifier(row.kind), executionState: vvIdentifier(row.execution_state),
        evidenceRef, evidenceRefSha256, accountingCorrectedBy,
      });
    }
    if (hashBoundEvidenceRefs.size !== evidenceArtifactManifest.size ||
      [...evidenceArtifactManifest.keys()].some((artifactPath) => !hashBoundEvidenceRefs.has(artifactPath))) {
      throw new Error('unused V&V evidence artifact manifest entry');
    }
    if (results.counts?.attempts !== attempts.length) throw new Error('invalid V&V attempt count');
    for (const [attemptId, attempt] of attemptsById) {
      if (attempt.supersededBy && (attempt.supersededBy === attemptId || !attemptsById.has(attempt.supersededBy))) {
        throw new Error('invalid V&V supersession');
      }
      if (attempt.scopedSupersededBy &&
        (attempt.scopedSupersededBy === attemptId || !attemptsById.has(attempt.scopedSupersededBy))) {
        throw new Error('invalid scoped V&V supersession');
      }
      if (attempt.scopedSupersededBy) {
        const qualification = attemptsById.get(attempt.scopedSupersededBy);
        if (qualification.kind !== 'EVIDENCE_QUALIFICATION_REVIEW' ||
          [...attempt.supersededCommandIds].some((commandId) => !qualification.qualificationCommandIds.has(commandId))) {
          throw new Error('mismatched scoped V&V qualification');
        }
      }
      const seen = new Set([attemptId]);
      let cursor = attempt;
      while (cursor.supersededBy || cursor.scopedSupersededBy) {
        const nextId = cursor.supersededBy || cursor.scopedSupersededBy;
        if (seen.has(nextId)) throw new Error('cyclic V&V supersession');
        seen.add(nextId);
        cursor = attemptsById.get(nextId);
      }
      if (attempt.accountingCorrectedBy &&
        (attempt.accountingCorrectedBy === attemptId || !attemptsById.has(attempt.accountingCorrectedBy))) {
        throw new Error('invalid V&V accounting correction');
      }
      const correctionSeen = new Set([attemptId]);
      let correction = attempt;
      while (correction.accountingCorrectedBy) {
        const nextId = correction.accountingCorrectedBy;
        if (correctionSeen.has(nextId)) throw new Error('cyclic V&V accounting correction');
        correctionSeen.add(nextId);
        correction = attemptsById.get(nextId);
      }
    }
    const incomingQualificationTargets = new Map();
    for (const attempt of attemptsById.values()) {
      if (!attempt.scopedSupersededBy) continue;
      const incoming = incomingQualificationTargets.get(attempt.scopedSupersededBy) || new Set();
      for (const commandId of attempt.supersededCommandIds) incoming.add(commandId);
      incomingQualificationTargets.set(attempt.scopedSupersededBy, incoming);
    }
    for (const [attemptId, attempt] of attemptsById) {
      if (!attempt.qualificationCommandIds.size) continue;
      const incoming = incomingQualificationTargets.get(attemptId) || new Set();
      if (incoming.size !== attempt.qualificationCommandIds.size ||
        [...attempt.qualificationCommandIds].some((commandId) => !incoming.has(commandId))) {
        throw new Error('uncovered V&V qualification target');
      }
    }
    const evidence = new Map();
    const evidenceIds = new Set();
    const evidenceRefById = new Map();
    const commandEvidenceById = new Map();
    const commandResults = vvArray(results.command_results);
    const commandResultCounts = new Map([...VV_TARGET_STATUSES].map((status) => [status, 0]));
    for (const resultValue of commandResults) {
      const result = vvObject(resultValue);
      const evidenceId = vvEvidenceId(result.evidence_id);
      if (evidenceIds.has(evidenceId)) throw new Error('duplicate V&V evidence');
      evidenceIds.add(evidenceId);
      const hasAttemptId = result.attempt_id != null;
      const hasEvidenceRef = result.evidence_ref != null;
      if (hasAttemptId !== hasEvidenceRef) throw new Error('incomplete V&V command provenance');
      const attemptId = hasAttemptId ? vvAttemptId(result.attempt_id) : null;
      const evidenceRef = hasEvidenceRef ? vvEvidenceRef(result.evidence_ref) : null;
      const qualificationEvidenceRef = result.qualification_evidence_ref == null
        ? null : vvEvidenceRef(result.qualification_evidence_ref);
      const attempt = attemptId ? attemptsById.get(attemptId) : null;
      if (attemptId && (!attempt || attempt.evidenceRef !== evidenceRef)) {
        throw new Error('mismatched V&V command provenance');
      }
      const claimLimit = result.claim_limit == null ? null : vvRequiredText(result.claim_limit);
      const row = { ref: vvText(result.evidence_id), observation: vvRequiredText(result.observation),
        executionStatus: vvStatus(result.vv_status), attemptId,
        method: attempt?.kind || null, limitations: claimLimit ||
          'No command-specific claim limit was recorded; this result is retained only as historical command evidence.',
        qualificationEvidenceRef, accountingCorrectedBy: attempt?.accountingCorrectedBy || null };
      const plannedForm = result.planned_form == null ? null : vvRequiredText(result.planned_form);
      const processExitCode = result.process_exit_code == null ? null : result.process_exit_code;
      if (processExitCode != null && !Number.isInteger(processExitCode)) {
        throw new Error('invalid V&V command exit code');
      }
      commandResultCounts.set(row.executionStatus, commandResultCounts.get(row.executionStatus) + 1);
      const commandIds = vvArray(result.command_ids).map(vvIdentifier);
      if (!commandIds.length || new Set(commandIds).size !== commandIds.length) {
        throw new Error('invalid V&V command evidence targets');
      }
      for (const commandId of commandIds) {
        if (!canonicalCommandIds.has(commandId) && !withdrawnCommandIds.has(commandId)) {
          throw new Error('unknown V&V command evidence target');
        }
        if (canonicalCommandIds.has(commandId)) {
          const scopedSupersededBy = attempt?.supersededCommandIds.has(commandId)
            ? attempt.scopedSupersededBy : null;
          evidence.set(commandId, [...(evidence.get(commandId) || []), {
            ...row, supersededBy: attempt?.supersededBy || scopedSupersededBy || null,
          }]);
        }
      }
      commandEvidenceById.set(evidenceId, {
        commandIds: new Set(commandIds), status: row.executionStatus, attemptId, evidenceRef,
        observation: row.observation, claimLimit, qualificationEvidenceRef,
        plannedForm, processExitCode,
      });
      evidenceRefById.set(evidenceId, evidenceRef);
    }
    if (results.counts?.command_runs !== commandResults.length) throw new Error('invalid V&V command-run count');
    for (const [status, field] of Object.entries({ PASS: 'command_pass', BLOCKED: 'command_blocked',
      FAIL: 'command_fail', UNVALIDATED: 'command_unvalidated', NOT_APPLICABLE: 'command_not_applicable',
      STALE: 'command_stale' })) {
      if ((results.counts?.[field] ?? 0) !== commandResultCounts.get(status)) {
        throw new Error('invalid V&V command-status count');
      }
    }
    for (const [attemptId, attempt] of attemptsById) {
      if (!attempt.supersededCommandIds.size) continue;
      const owned = new Set([...commandEvidenceById.values()]
        .filter((item) => item.attemptId === attemptId)
        .flatMap((item) => [...item.commandIds]));
      if ([...attempt.supersededCommandIds].some((commandId) => !owned.has(commandId))) {
        throw new Error('scoped V&V supersession targets evidence owned by another attempt');
      }
    }
    const procedureEvidence = new Map();
    for (const item of vvArray(results.procedure_results || [])) {
      const row = vvExactKeys(item,
        ['evidence_id', 'attempt_id', 'method', 'observation', 'limitations', 'targets'],
        'invalid V&V procedure result');
      const evidenceId = vvEvidenceId(row.evidence_id);
      const attemptId = vvAttemptId(row.attempt_id);
      if (evidenceIds.has(evidenceId) || procedureEvidence.has(evidenceId) || !attemptsById.has(attemptId)) {
        throw new Error('invalid V&V procedure result');
      }
      const targets = new Map();
      const sourceRefsByTarget = new Map();
      const commandIds = new Set();
      for (const target of vvArray(row.targets)) {
        const targetRow = vvObject(target);
        const targetKeys = ['level', 'target', 'vv_status'];
        if (targetRow.basis_role != null) targetKeys.push('basis_role');
        if (targetRow.source_refs != null) targetKeys.push('source_refs');
        vvExactKeys(targetRow, targetKeys, 'invalid V&V procedure target');
        if (targetRow.basis_role != null &&
          !new Set(['STATUS_RECLASSIFICATION', 'STATUS_BASIS_REBOUND']).has(vvIdentifier(targetRow.basis_role))) {
          throw new Error('invalid V&V procedure target basis role');
        }
        const targetKey = projectionTargetKey(targetRow, canonicalTargets);
        if (targets.has(targetKey)) throw new Error('duplicate V&V procedure target');
        const canonicalTarget = canonicalTargets.get(targetKey);
        const targetStatus = vvStatus(targetRow.vv_status);
        const pageMeta = canonical.pageById.get(canonicalTarget.page_id);
        const sourceRefs = targetRow.source_refs == null ? [] : vvArray(targetRow.source_refs)
          .map((source) => vvSourceRef(source, pageMeta.sourceFile));
        if (new Set(sourceRefs.map((source) => JSON.stringify(source))).size !== sourceRefs.length ||
          (sourceRefs.length && (targetStatus !== 'PASS' || !new Set([
            'PINNED_CANONICAL_SOURCE_CONFORMANCE',
            'STATIC_CANONICAL_SOURCE_CITATION_OPENAPI_AND_LINK_RETEST',
          ]).has(row.method)))) {
          throw new Error('invalid V&V procedure target source binding');
        }
        targets.set(targetKey, targetStatus);
        sourceRefsByTarget.set(targetKey, sourceRefs);
        if (canonicalTarget.command_id) commandIds.add(canonicalTarget.command_id);
      }
      if (!targets.size) throw new Error('missing V&V procedure target');
      procedureEvidence.set(evidenceId, {
        attemptId, targets, sourceRefsByTarget, commandIds, method: vvRequiredText(row.method),
        observation: vvRequiredText(row.observation), limitations: vvRequiredText(row.limitations),
      });
      evidenceRefById.set(evidenceId, attemptsById.get(attemptId).evidenceRef);
      evidenceIds.add(evidenceId);
    }
    const historyByTarget = new Map();
    for (const [evidenceId, procedure] of procedureEvidence) {
      const attempt = attemptsById.get(procedure.attemptId);
      for (const [targetKey, status] of procedure.targets) {
        const commandId = canonicalTargets.get(targetKey)?.command_id;
        const scopedSupersededBy = commandId && attempt.supersededCommandIds.has(commandId)
          ? attempt.scopedSupersededBy : null;
        const history = {
          evidenceIds: [vvText(evidenceId)], attemptId: vvText(procedure.attemptId), status,
          method: procedure.method, observation: procedure.observation, limitations: procedure.limitations,
          supersededBy: attempt.supersededBy || scopedSupersededBy
            ? vvText(attempt.supersededBy || scopedSupersededBy) : null,
        };
        historyByTarget.set(targetKey, [...(historyByTarget.get(targetKey) || []), history]);
      }
    }
    for (const [evidenceId, commandEvidence] of commandEvidenceById) {
      if (!commandEvidence.attemptId) continue;
      const attempt = attemptsById.get(commandEvidence.attemptId);
      for (const commandId of commandEvidence.commandIds) {
        const command = canonical.commandById.get(commandId);
        if (!command) continue;
        const targetKey = vvStatusKey('COMMAND', command);
        const scopedSupersededBy = attempt.supersededCommandIds.has(commandId)
          ? attempt.scopedSupersededBy : null;
        const history = {
          evidenceIds: [vvText(evidenceId)], attemptId: vvText(commandEvidence.attemptId),
          status: commandEvidence.status, method: attempt.kind,
          observation: commandEvidence.observation,
          limitations: commandEvidence.claimLimit ||
            'No command-specific claim limit was recorded; this result is retained only as historical command evidence.',
          qualificationEvidenceRef: commandEvidence.qualificationEvidenceRef,
          accountingCorrectedBy: attempt.accountingCorrectedBy,
          supersededBy: attempt.supersededBy || scopedSupersededBy
            ? vvText(attempt.supersededBy || scopedSupersededBy) : null,
        };
        historyByTarget.set(targetKey, [...(historyByTarget.get(targetKey) || []), history]);
      }
    }
    const assessmentEvidence = (evidenceId, commandId) => {
      const commandEvidence = commandEvidenceById.get(evidenceId);
      if (commandEvidence?.commandIds.has(commandId)) return { status: commandEvidence.status };
      const procedure = procedureEvidence.get(evidenceId);
      if (procedure?.commandIds.has(commandId)) {
        const commandTarget = canonical.commandById.get(commandId);
        return { status: procedure.targets.get(vvStatusKey('COMMAND', commandTarget)) };
      }
      return null;
    };
    const directProofCeilings = new Map();
    for (const ceilingValue of vvArray(results.direct_proof_ceilings)) {
      const ceilingRow = vvObject(ceilingValue);
      if (Object.keys(ceilingRow).sort().join(',') !== 'ceiling,evidence_id') {
        throw new Error('invalid direct V&V proof ceiling');
      }
      const evidenceId = vvEvidenceId(ceilingRow.evidence_id);
      const ceiling = vvIdentifier(ceilingRow.ceiling);
      if (directProofCeilings.has(evidenceId) || !VV_DIRECT_PROOF_ROLES.has(ceiling) ||
        (!commandEvidenceById.has(evidenceId) && !procedureEvidence.has(evidenceId))) {
        throw new Error('invalid direct V&V proof ceiling');
      }
      directProofCeilings.set(evidenceId, ceiling);
    }
    const directEvidenceBindings = new Map();
    for (const bindingValue of vvArray(scores.direct_evidence_bindings)) {
      const binding = vvObject(bindingValue);
      const allowedKeys = binding.equivalence_note == null
        ? 'command_id,evidence_id,role' : 'command_id,equivalence_note,evidence_id,role';
      if (Object.keys(binding).sort().join(',') !== allowedKeys) {
        throw new Error('invalid direct V&V evidence binding');
      }
      const commandId = vvIdentifier(binding.command_id);
      const evidenceId = vvEvidenceId(binding.evidence_id);
      const role = vvIdentifier(binding.role);
      const equivalenceNote = binding.equivalence_note == null ? null : vvRequiredText(binding.equivalence_note);
      if (!canonicalCommandIds.has(commandId) || !VV_DIRECT_PROOF_ROLES.has(role) ||
        directProofCeilings.get(evidenceId) !== role ||
        (role === 'DIRECT_FUNCTIONAL_EQUIVALENT_FULL') !== Boolean(equivalenceNote)) {
        throw new Error('invalid direct V&V evidence role');
      }
      const key = `${commandId}\0${evidenceId}`;
      if (directEvidenceBindings.has(key)) throw new Error('duplicate direct V&V evidence binding');
      directEvidenceBindings.set(key, { role, equivalenceNote });
    }
    const usedDirectEvidenceBindings = new Set();
    const usedDirectProofCeilings = new Set();
    const directEvidence = (evidenceId, commandId, binding) => {
      const commandEvidence = commandEvidenceById.get(evidenceId);
      if (commandEvidence) {
        if (!commandEvidence.commandIds.has(commandId) || !commandEvidence.attemptId) {
          throw new Error('invalid direct V&V command evidence');
        }
        const attempt = attemptsById.get(commandEvidence.attemptId);
        if (!attempt || attempt.executionState !== 'EXECUTED' || attempt.status === 'STALE' || attempt.supersededBy ||
          attempt.supersededCommandIds.has(commandId) || attempt.evidenceRef !== commandEvidence.evidenceRef) {
          throw new Error('unsafe direct V&V command evidence');
        }
        return {
          status: commandEvidence.status, attemptId: commandEvidence.attemptId,
          method: attempt.kind, observation: commandEvidence.observation,
          limitations: commandEvidence.claimLimit, evidenceRef: commandEvidence.evidenceRef,
          proofRole: binding.role, equivalenceNote: binding.equivalenceNote,
          evidenceKind: 'COMMAND_RESULT', plannedForm: commandEvidence.plannedForm,
          processExitCode: commandEvidence.processExitCode,
        };
      }
      const procedure = procedureEvidence.get(evidenceId);
      if (!procedure || !procedure.commandIds.has(commandId)) {
        throw new Error('invalid direct V&V procedure evidence');
      }
      const attempt = attemptsById.get(procedure.attemptId);
      if (!attempt || attempt.executionState !== 'EXECUTED' || attempt.status === 'STALE' ||
        attempt.supersededBy || attempt.supersededCommandIds.has(commandId)) {
        throw new Error('unsafe direct V&V procedure evidence');
      }
      const command = canonical.commandById.get(commandId);
      return {
        status: procedure.targets.get(vvStatusKey('COMMAND', command)), attemptId: procedure.attemptId,
        method: procedure.method, observation: procedure.observation,
        limitations: procedure.limitations, evidenceRef: attempt.evidenceRef,
        proofRole: binding.role, equivalenceNote: binding.equivalenceNote,
        evidenceKind: 'PROCEDURE_RESULT', plannedForm: null, processExitCode: null,
      };
    };
    const assessmentIdentity = (row, commandId) => {
      const command = canonical.commandById.get(commandId);
      if (!command || row.page_route !== command.route || row.procedure_id !== command.procedureId || row.source !== command.source) {
        throw new Error('mismatched V&V assessment ancestry');
      }
      const ids = vvArray(row.evidence_ids).map(vvEvidenceId);
      if (!ids.length || new Set(ids).size !== ids.length || ids.some((id) => !assessmentEvidence(id, commandId))) {
        throw new Error('invalid V&V assessment evidence');
      }
      return ids;
    };
    const scoreRecords = vvArray(scores.records);
    const scoreCounts = [0, 0, 0];
    const scoreByCommand = new Map();
    for (const scoreValue of scoreRecords) {
      const score = vvObject(scoreValue);
      if (typeof score.command_id !== 'string' || !Number.isInteger(score.score) || score.score < 1 || score.score > 3) {
        throw new Error('invalid score');
      }
      const commandId = vvIdentifier(score.command_id);
      if (scoreByCommand.has(commandId)) throw new Error('duplicate score');
      if (!canonicalCommandIds.has(commandId)) throw new Error('unknown score command');
      const scoreEvidenceIds = assessmentIdentity(score, commandId);
      const directEvidenceIds = vvArray(score.direct_evidence_ids).map(vvEvidenceId);
      if (new Set(directEvidenceIds).size !== directEvidenceIds.length) {
        throw new Error('duplicate direct V&V score evidence');
      }
      const directResults = directEvidenceIds.map((evidenceId) => {
        const key = `${commandId}\0${evidenceId}`;
        const binding = directEvidenceBindings.get(key);
        if (!binding) throw new Error('missing direct V&V evidence binding');
        usedDirectEvidenceBindings.add(key);
        usedDirectProofCeilings.add(evidenceId);
        return directEvidence(evidenceId, commandId, binding);
      });
      const executionStatus = vvStatus(score.execution_status);
      if (executionStatus === 'NOT_APPLICABLE') throw new Error('numeric score cannot be NOT_APPLICABLE');
      if (score.score === 3 &&
        (!directResults.length || !directResults.some((result) =>
          result.status === 'PASS' && VV_SCORE3_PROOF_ROLES.has(result.proofRole) && result.limitations &&
          (result.evidenceKind === 'PROCEDURE_RESULT' ||
            (result.plannedForm && result.processExitCode === 0))))) {
        throw new Error('score 3 requires full direct functional PASS evidence');
      }
      scoreCounts[score.score - 1] += 1;
      scoreByCommand.set(commandId, { value: score.score, rationale: vvRequiredText(score.rationale),
        executionStatus, evidenceIds: scoreEvidenceIds.map(vvText),
        directEvidenceIds: directEvidenceIds.map(vvText),
        directEvidence: directResults.map((result, index) => ({
          id: vvText(directEvidenceIds[index]), status: vvStatus(result.status),
          attemptId: vvText(result.attemptId), method: vvText(result.method),
          observation: vvText(result.observation),
          limitations: result.limitations == null ? null : vvText(result.limitations),
          proofRole: vvText(result.proofRole),
          equivalenceNote: result.equivalenceNote == null ? null : vvText(result.equivalenceNote),
          evidenceRef: result.evidenceRef,
        })) });
    }
    if (usedDirectEvidenceBindings.size !== directEvidenceBindings.size) {
      throw new Error('unused direct V&V evidence binding');
    }
    if (usedDirectProofCeilings.size !== directProofCeilings.size) {
      throw new Error('unused direct V&V proof ceiling');
    }
    if (scores.counts?.scored !== scoreRecords.length || scores.counts?.score_1 !== scoreCounts[0] ||
      scores.counts?.score_2 !== scoreCounts[1] || scores.counts?.score_3 !== scoreCounts[2]) {
      throw new Error('invalid score counts');
    }
    const notApplicableRecords = vvArray(scores.not_applicable_records || []);
    const notApplicableByCommand = new Map();
    for (const assessmentValue of notApplicableRecords) {
      const assessment = vvObject(assessmentValue);
      const commandId = vvIdentifier(assessment.command_id);
      if (!canonicalCommandIds.has(commandId) || scoreByCommand.has(commandId) || notApplicableByCommand.has(commandId) ||
        assessment.execution_status !== 'NOT_APPLICABLE') {
        throw new Error('invalid NOT_APPLICABLE assessment');
      }
      const assessmentEvidenceIds = assessmentIdentity(assessment, commandId);
      if (assessmentEvidenceIds.some((id) => assessmentEvidence(id, commandId)?.status !== 'NOT_APPLICABLE')) {
        throw new Error('mismatched NOT_APPLICABLE evidence');
      }
      const command = canonical.commandById.get(commandId);
      const expectedApproval = `CANONICAL_NON_EXECUTABLE_DISPLAY:${snapshot}`;
      if (command.treatment !== 'NON_EXECUTABLE_DISPLAY' || vvApprovalRef(assessment.approval_ref) !== expectedApproval) {
        throw new Error('invalid NOT_APPLICABLE classification approval');
      }
      notApplicableByCommand.set(commandId, {
        rationale: vvRequiredText(assessment.rationale), approvalRef: vvApprovalRef(assessment.approval_ref),
        evidenceIds: assessmentEvidenceIds.map(vvText), executionStatus: 'NOT_APPLICABLE',
      });
    }
    if ((scores.counts?.not_applicable ?? 0) !== notApplicableRecords.length) {
      throw new Error('invalid NOT_APPLICABLE assessment count');
    }
    if (scoreByCommand.size + notApplicableByCommand.size !== canonicalCommandIds.size) {
      throw new Error('incomplete V&V command assessment coverage');
    }
    const bindingManifests = loadContractBindingManifests(
      results, attemptsById, evidenceIds, evidenceRefById, canonical, scoreByCommand,
    );
    const contracts = loadClaimAndSupportContracts(
      sets, canonical, evidenceIds, evidenceRefById, procedureEvidence, commandEvidenceById, bindingManifests,
    );
    // This is deliberately after all historical/package validation.  Current
    // sources are a freshness comparison, never replacement evidence.
    const sourceFreshness = currentSourceFreshness(canonical, contracts.supportLayers);
    const currentStatusByTarget = loadCurrentStatusProjection(
      results, canonical, attemptsById, procedureEvidence, commandEvidenceById, snapshot, contracts, evidenceIds,
    );
    if (currentStatusByTarget.size !== canonicalTargets.size) {
      throw new Error('incomplete current V&V status projection');
    }
    for (const [targetKey, current] of currentStatusByTarget) {
      if (canonical.executionStatusByKey.get(targetKey) !== current.status) {
        throw new Error('nested V&V execution status does not mirror current projection');
      }
    }
    for (const [commandId, command] of canonical.commandById) {
      const current = currentStatusByTarget.get(vvStatusKey('COMMAND', command));
      const assessment = scoreByCommand.get(commandId) || notApplicableByCommand.get(commandId);
      if (!assessment || !current || current.status !== assessment.executionStatus) {
        throw new Error('mismatched current V&V command assessment');
      }
      const score = scoreByCommand.get(commandId);
      if (score && current.status === 'PASS' &&
        !score.directEvidence.some((result) => result.status === 'PASS')) {
        throw new Error('current PASS requires direct V&V PASS evidence');
      }
      if (scoreByCommand.get(commandId)?.value === 3 && current.status !== 'PASS') {
        throw new Error('score 3 requires current PASS');
      }
    }
    const withdrawnByCommand = new Map();
    const retiredWithdrawnByPage = new Map();
    for (const withdrawn of withdrawnRecords) {
      const command = canonical.commandById.get(withdrawn.commandId);
      if (!command) {
        if (withdrawn.currentExecutionStatus !== 'STALE' || withdrawn.currentScore !== null) {
          throw new Error('invalid retired V&V withdrawal disposition');
        }
        retiredWithdrawnByPage.set(withdrawn.pageRoute,
          [...(retiredWithdrawnByPage.get(withdrawn.pageRoute) || []), withdrawn]);
        continue;
      }
      const score = scoreByCommand.get(withdrawn.commandId);
      const assessment = score || notApplicableByCommand.get(withdrawn.commandId);
      const expectedScore = score?.value ?? null;
      if (withdrawn.pageRoute !== command.route || withdrawn.currentExecutionStatus !== assessment.executionStatus ||
        withdrawn.currentScore !== expectedScore) {
        throw new Error('stale current V&V withdrawal disposition');
      }
      withdrawnByCommand.set(withdrawn.commandId,
        [...(withdrawnByCommand.get(withdrawn.commandId) || []), withdrawn]);
    }
    const canonicalCommands = [...canonical.commandById.values()];
    const statusTargetByBinding = new Map();
    for (const [key, target] of canonical.targets) {
      const level = key.split('\0')[0];
      const id = target[VV_STATUS_TARGET_FIELDS[level].at(-1)];
      const binding = `${level}:${id}`;
      if (statusTargetByBinding.has(binding)) throw new Error('duplicate V&V status-target binding');
      statusTargetByBinding.set(binding, { key, level, id, target });
    }
    const totals = {
      pages: canonical.counts.pages, testSets: canonical.counts.test_sets, branches: canonical.counts.branches,
      steps: canonical.counts.steps, commands: canonical.counts.command_carriers,
      nonCommandSteps: canonical.counts.steps - canonical.counts.command_bearing_steps,
      displayOnlyCommands: canonicalCommands.filter((command) => command.treatment === 'NON_EXECUTABLE_DISPLAY').length,
      executableIntentCommands: canonicalCommands.filter((command) => command.treatment !== 'NON_EXECUTABLE_DISPLAY').length,
      retainedEvidenceRecords: evidenceIds.size, observations: evidenceIds.size,
      scored: scoreRecords.length,
      executableIntentScored: canonicalCommands.filter((command) => command.treatment !== 'NON_EXECUTABLE_DISPLAY' &&
        scoreByCommand.has(command.command_id)).length,
      displayOnlyScored: canonicalCommands.filter((command) => command.treatment === 'NON_EXECUTABLE_DISPLAY' &&
        scoreByCommand.has(command.command_id)).length,
      notApplicableAssessments: notApplicableRecords.length,
      materialClaims: contracts.materialClaims.length,
      retiredMaterialClaims: contracts.retiredMaterialClaims.length,
      supportLayers: contracts.supportLayers.length,
      cliSupportLayers: contracts.supportLayers.filter((support) => support.layer === 'CLI').length,
      sdkSupportLayers: contracts.supportLayers.filter((support) => support.layer === 'SDK').length,
      withdrawnAssessments: withdrawnRecords.length,
    };
    if (Object.values(totals).some((value) => !Number.isInteger(value) || value < 0)) throw new Error('invalid totals');
    return { available: true, pages, evidence, scoreByCommand, notApplicableByCommand,
      currentStatusByTarget, historyByTarget,
      commandById: canonical.commandById,
      statusTargetByBinding,
      cliSignatureByCommandId: cliSignatureChecks.byCommandId,
      cliSignatureByFindingId: cliSignatureChecks.byFindingId,
      cliSignatureArtifactSha256: cliSignatureChecks.artifactSha256,
      evidenceRefById,
      evidenceRefs: new Set([
        ...[...attemptsById.values()].map((attempt) => attempt.evidenceRef),
        ...withdrawnRecords.map((withdrawn) => withdrawn.qualificationEvidenceRef),
        ...[...commandEvidenceById.values()].map((item) => item.qualificationEvidenceRef).filter(Boolean),
      ]), totals, withdrawnRecords, withdrawnByCommand, retiredWithdrawnByPage,
      materialClaimStatusCounts: Object.fromEntries([...contracts.materialStatusCounts]),
      materialPageDispositionStatusCounts: Object.fromEntries([...contracts.pageDispositionCounts]),
      materialClaims: contracts.materialClaims, materialClaimsByPage: contracts.materialClaimsByPage,
      materialPageDispositions: contracts.materialPageDispositions,
      materialPageDispositionByPage: contracts.materialPageDispositionByPage,
      retiredMaterialClaims: contracts.retiredMaterialClaims,
      retiredMaterialClaimsByPage: contracts.retiredMaterialClaimsByPage,
      supportLayers: contracts.supportLayers, supportByRoute: contracts.supportByRoute,
      sourceFreshness, reviewedSourceRevision: VV_REVIEWED_SOURCE_REVISION };
  } catch (error) {
    const unavailableReason = vvText(String(error?.message || 'package-integrity-failure'));
    if (process.env.VAST_REVIEW_DEBUG === '1') console.error(`V&V evidence unavailable: ${unavailableReason}`);
    return { available: false, pages: [], evidence: new Map(), scoreByCommand: new Map(),
      notApplicableByCommand: new Map(), currentStatusByTarget: new Map(), historyByTarget: new Map(),
      commandById: new Map(), cliSignatureByCommandId: new Map(), cliSignatureByFindingId: new Map(),
      statusTargetByBinding: new Map(),
      cliSignatureArtifactSha256: null,
      evidenceRefById: new Map(), evidenceRefs: new Set(), totals: null,
      withdrawnRecords: [], withdrawnByCommand: new Map(), retiredWithdrawnByPage: new Map(),
      materialClaimStatusCounts: {}, materialPageDispositionStatusCounts: {},
      materialClaims: [], materialClaimsByPage: new Map(), retiredMaterialClaims: [],
      materialPageDispositions: [], materialPageDispositionByPage: new Map(),
      retiredMaterialClaimsByPage: new Map(),
      supportLayers: [], supportByRoute: new Map(), sourceFreshness: null,
      reviewedSourceRevision: VV_REVIEWED_SOURCE_REVISION, unavailableReason };
  }
}
const VERIFICATION_EVIDENCE = loadVerificationEvidence();
const VV_EVIDENCE_LANES = [
  {
    code: 'IMPLEMENTATION_SOURCE',
    label: 'Implementation/source',
    requirement: 'Canonical Vast code, API schema, generated reference, formula, or configuration.',
  },
  {
    code: 'RUNTIME_OBSERVATION',
    label: 'Runtime/UI',
    requirement: 'Retained execution or UI evidence from the required authorized environment.',
  },
  {
    code: 'ACCOUNTABLE_OWNER',
    label: 'Product/Finance/Legal authority',
    requirement: 'An authoritative policy, contract, product, provider, or owner source; code alone may be insufficient.',
  },
  {
    code: 'DOCUMENTATION_CITATION',
    label: 'Documentation/citation',
    requirement: 'Correct wording plus a link or citation to its authoritative source; the documentation text does not prove itself.',
  },
];
function vvMergeClassifications(definitions, ...groups) {
  const codes = new Set(groups.flat().map((item) => item.code));
  return definitions.filter((item) => codes.has(item.code));
}
function vvMergeDetails(...groups) {
  const merged = new Map();
  for (const item of groups.flat()) {
    const key = `${item.code}\0${item.label}\0${item.nextAction || ''}`;
    if (!merged.has(key)) merged.set(key, item);
  }
  return [...merged.values()];
}
function vvBlockerDetails(status) {
  if (!status || status.status !== 'BLOCKED') return [];
  const prerequisite = status.basis?.unavailablePrerequisite;
  if (!prerequisite) throw new Error('BLOCKED status lacks a structured unavailable prerequisite');
  return [{
    code: prerequisite.kind,
    label: prerequisite.description,
    nextAction: status.basis.nextAction,
    claimImpact: status.basis.claimImpact,
    evidenceIds: prerequisite.evidenceIds,
  }];
}
function vvEvidenceLaneHints(accessClasses) {
  const values = accessClasses.map((value) => value.toLowerCase());
  const codes = new Set();
  if (values.some((value) =>
    /^(?:source-inspection|source\/static(?: inspection|-inspection)?|generated-source-inspection|generated-reference-inspection|formula-inspection)$/.test(value))) {
    codes.add('IMPLEMENTATION_SOURCE');
  }
  if (values.some((value) =>
    /host|account|browser|ssh|wan|container|hardware|network|credential|paid|service|listener|packet|reboot|external-client|market|local-safe/.test(value))) {
    codes.add('RUNTIME_OBSERVATION');
  }
  if (values.some((value) =>
    /source-owner|product-source|provider-source|legal|finance|financial\/contract|conceptual\/policy|third-party provider|support-coordinated/.test(value))) {
    codes.add('ACCOUNTABLE_OWNER');
  }
  if (values.some((value) =>
    /^(?:documentation-citation|claim-source-citation|authoritative-citation-review)$/.test(value))) {
    codes.add('DOCUMENTATION_CITATION');
  }
  return VV_EVIDENCE_LANES.filter((item) => codes.has(item.code));
}
function vvFreshnessContext(pathname, freshness, { supportLayer = false, page = null, baselineSourceFile = null } = {}) {
  const currentPageHref = pathname;
  const baselineFile = page?.source_file || page?.sourceFile || baselineSourceFile;
  const baselinePageHref = baselineFile
    ? `https://github.com/vast-ai/docs/blob/${VV_REVIEWED_SOURCE_REVISION}/${baselineFile}` : null;
  const state = freshness?.state || 'UNVALIDATED';
  const action = state === 'STALE' && supportLayer
    ? 'Review the current wrapper, snippet, and central reference, then create and retain a new support-layer V&V result for this exact current source.'
    : state === 'STALE'
    ? 'Review the current wording and rendered dependencies, then create and retain a new V&V result for this exact current source.'
    : state === 'HISTORICAL_ONLY'
      ? 'Restore this route to the current Host navigation or create a new current-route V&V package before presenting validation.'
      : 'Create and retain a V&V result for this new current route before presenting validation.';
  const explanation = state === 'STALE' && supportLayer
    ? 'The current support wrapper, snippet, or central reference differs from the reviewed source snapshot. Historical support results are not current validation.'
    : state === 'STALE'
    ? 'The current page or one of its rendered dependencies differs from the reviewed source snapshot. Historical results are not current validation.'
    : state === 'HISTORICAL_ONLY'
      ? 'This route is retained in the reviewed snapshot but is absent from the current Host navigation. It is historical only.'
      : 'This route is present in the current Host navigation but was not in the reviewed snapshot. It is unvalidated.';
  return {
    available: true, supportLayer, workflow: !supportLayer,
    currentStatus: state === 'HISTORICAL_ONLY' ? 'UNVALIDATED' : state,
    sourceFreshness: {
      state, reason: freshness?.reason || 'current-source-not-covered-by-reviewed-snapshot', explanation,
      nextAction: action, currentPageHref, baselinePageHref,
      reviewedSourceRevision: VV_REVIEWED_SOURCE_REVISION,
      currentHostRouteCount: VERIFICATION_EVIDENCE.sourceFreshness.currentHostRouteCount,
      baselineHostRouteCount: VERIFICATION_EVIDENCE.sourceFreshness.baselineHostRouteCount,
    },
    // Do not project historical PASS/score/cards into current status.  The
    // immutable source link is intentionally the only history exposed here.
    historical: { label: 'Reviewed historical snapshot (not current validation)', baselinePageHref,
      reviewedSourceRevision: VV_REVIEWED_SOURCE_REVISION },
    materialClaims: [], retiredMaterialClaims: [], retiredCommandWithdrawals: [], testSets: [],
    totals: { testSets: 0, branches: 0, steps: 0, commands: 0, nonCommandSteps: 0,
      displayOnlyCommands: 0, executableIntentCommands: 0, retainedEvidenceRecords: 0, observations: 0,
      scored: 0, executableIntentScored: 0, displayOnlyScored: 0, notApplicableAssessments: 0 },
  };
}
function verificationForPath(pathname) {
  if (!VERIFICATION_EVIDENCE.available) {
    return { available: false,
      unavailableReason: VERIFICATION_EVIDENCE.unavailableReason || 'package-integrity-failure' };
  }
  try {
    const evidenceLinksFor = (evidenceIds = [], binding = null) => evidenceIds.map((id) => ({
      id: vvEvidenceId(id), evidenceRef: VERIFICATION_EVIDENCE.evidenceRefById.get(id) || null,
      ...(binding ? { binding: vvIdentifier(binding) } : {}),
    }));
    const withdrawnForApi = (records = []) => records.map((record) => ({
      commandId: record.commandId, originalExecutionStatus: record.originalExecutionStatus,
      originalScore: record.originalScore, currentExecutionStatus: record.currentExecutionStatus,
      currentScore: record.currentScore, reason: record.reason,
      currentReassessment: record.currentReassessment, retired: record.retired,
      qualificationEvidence: [{ id: 'qualification-record',
        evidenceRef: record.qualificationEvidenceRef }],
    }));
    const support = VERIFICATION_EVIDENCE.supportByRoute.get(pathname);
    if (support) {
      const freshness = VERIFICATION_EVIDENCE.sourceFreshness.supportByRoute.get(pathname);
      if (freshness?.state !== 'CURRENT') {
        return vvFreshnessContext(pathname, freshness, { supportLayer: true, baselineSourceFile: support.sourceFile });
      }
      const pageTitle = `${support.layer} central-reference support: ${pathname.split('/').at(-1)}`;
      return {
        available: true, supportLayer: true, supportId: support.id,
        workflow: false, classification: support.classification,
        sourceFreshness: { state: 'CURRENT', reason: freshness?.reason || 'matches-reviewed-snapshot',
          reviewedSourceRevision: VV_REVIEWED_SOURCE_REVISION,
          currentHostRouteCount: VERIFICATION_EVIDENCE.sourceFreshness.currentHostRouteCount,
          baselineHostRouteCount: VERIFICATION_EVIDENCE.sourceFreshness.baselineHostRouteCount },
        checkedContent: { route: support.route, pageTitle, sections: [] },
        repositoryFiles: { wrapper: support.sourceFile, fragment: support.fragmentFile,
          centralReference: support.centralReferenceFile },
        centralReference: { route: support.centralReferenceRoute,
          label: `${support.layer} central reference` },
        currentStatus: support.status, currentEvidenceIds: support.evidenceIds,
        currentEvidence: evidenceLinksFor(support.evidenceIds, support.id),
        evidenceRole: support.evidenceRole, evidenceLimitations: support.evidenceLimitations,
        claimLimit: support.claimLimit,
        testSets: [], totals: { testSets: 0, branches: 0, steps: 0, commands: 0,
          nonCommandSteps: 0, displayOnlyCommands: 0, executableIntentCommands: 0,
          retainedEvidenceRecords: support.evidenceIds.length, observations: support.evidenceIds.length,
          scored: 0, executableIntentScored: 0, displayOnlyScored: 0, notApplicableAssessments: 0 },
      };
    }
    const page = VERIFICATION_EVIDENCE.pages.find((row) => row.route === pathname);
    const freshness = VERIFICATION_EVIDENCE.sourceFreshness.byRoute.get(pathname);
    if (freshness && freshness.state !== 'CURRENT') {
      return vvFreshnessContext(pathname, freshness, { page });
    }
    if (!page) return { available: false, unavailableReason: 'page-not-in-inventory' };
    const pageRoute = vvCanonicalRoute(page.route);
    const pageTitle = vvRequiredText(page.title);
    const checkedContentFor = (sections = []) => ({
      route: pageRoute,
      pageTitle,
      sections: [...new Set(sections.map(vvSectionTitle))],
    });
    const keyFor = (level, target) => vvStatusKey(level, target);
    const statusFor = (level, target) => VERIFICATION_EVIDENCE.currentStatusByTarget.get(keyFor(level, target)) || null;
    const historyFor = (level, target) => VERIFICATION_EVIDENCE.historyByTarget.get(keyFor(level, target)) || [];
    const pageTarget = { page_id: page.page_id };
    const pageStatus = statusFor('PAGE', pageTarget);
    const statusSubject = (status) => status?.basis ? {
      route: status.basis.subject.route, pageTitle: status.basis.subject.pageTitle,
      sections: status.basis.subject.headings,
    } : null;
    const prerequisiteForApi = (prerequisite, binding = null) => prerequisite ? {
      kind: prerequisite.kind, description: prerequisite.description,
      evidenceIds: prerequisite.evidenceIds,
      evidence: evidenceLinksFor(prerequisite.evidenceIds, binding),
      components: prerequisite.components.map((component) => {
        const origin = component.viaTarget
          ? VERIFICATION_EVIDENCE.currentStatusByTarget.get(component.viaTarget.key) : null;
        const targetFields = component.viaTarget ? Object.values(component.viaTarget.target) : [];
        return {
          kind: component.kind, description: component.description,
          evidenceIds: component.evidenceIds, evidence: evidenceLinksFor(component.evidenceIds, binding),
          viaTarget: component.viaTarget ? {
            level: component.viaTarget.level, target: component.viaTarget.target,
            id: targetFields.at(-1), checkedContent: statusSubject(origin),
          } : null,
        };
      }),
    } : null;
    const verificationContractFor = (status, binding = null) => status?.basis ? {
      basisKind: status.basis.basisKind,
      checkedContent: { route: status.basis.subject.route, pageTitle: status.basis.subject.pageTitle,
        sections: status.basis.subject.headings },
      claim: status.basis.subject.claim, claimRefs: status.basis.subject.claimRefs,
      noMaterialClaimReason: status.basis.subject.noMaterialClaimReason,
      requiredEvidenceTypes: status.basis.requiredEvidenceTypes,
      authority: status.basis.authority,
      supportingEvidence: evidenceLinksFor(status.basis.supportingEvidenceIds, binding),
      unavailablePrerequisite: prerequisiteForApi(status.basis.unavailablePrerequisite, binding),
      claimImpact: status.basis.claimImpact, limitations: status.basis.limitations,
      nextAction: status.basis.nextAction,
      targetBasis: status.basis.targetBasis ? {
        status: status.basis.targetBasis.status, basisKind: status.basis.targetBasis.basisKind,
        requiredEvidenceTypes: status.basis.targetBasis.requiredEvidenceTypes,
        authority: status.basis.targetBasis.authority,
        supportingEvidenceIds: status.basis.targetBasis.supportingEvidenceIds,
        supportingEvidence: evidenceLinksFor(status.basis.targetBasis.supportingEvidenceIds, binding),
        unavailablePrerequisite: prerequisiteForApi(status.basis.targetBasis.unavailablePrerequisite, binding),
        limitations: status.basis.targetBasis.limitations,
      } : null,
      derivedFrom: status.basis.derivedFrom.map((item) => ({
        level: item.level, target: item.target, currentStatus: item.currentStatus, required: item.required,
        id: Object.values(item.target).at(-1),
        checkedContent: statusSubject(VERIFICATION_EVIDENCE.currentStatusByTarget.get(item.key)),
      })),
    } : null;
    const currentFields = (status, history, binding = null) => ({
      currentStatus: status?.status || null, currentStatusAttemptId: status?.attemptId || null,
      currentEvidenceIds: status?.evidenceIds || [], currentMethod: status?.method || null,
      currentEvidence: evidenceLinksFor(status?.evidenceIds || [], binding),
      currentObservation: status?.observation || null, currentLimitations: status?.limitations || null,
      currentRationale: status?.rationale || null,
      verificationContract: verificationContractFor(status, binding),
      history: history.map((item) => {
        const { qualificationEvidenceRef, ...safeItem } = item;
        return { ...safeItem, evidence: evidenceLinksFor(item.evidenceIds, binding),
          qualificationEvidence: qualificationEvidenceRef
            ? [{ id: 'qualification-record', evidenceRef: qualificationEvidenceRef,
              ...(binding ? { binding: vvIdentifier(binding) } : {}) }] : [] };
      }),
    });
    const testSets = vvArray(page.test_sets).map((set) => {
      const setTarget = { page_id: page.page_id, test_set_id: set.test_set_id };
      const setStatus = statusFor('TEST_SET', setTarget);
      const branches = vvArray(set.branches).map((branch) => {
        const branchTarget = { ...setTarget, branch_id: branch.branch_id };
        const branchStatus = statusFor('BRANCH', branchTarget);
        const steps = vvArray(branch.steps).map((step) => {
          const stepTarget = { ...branchTarget, step_id: step.step_id };
          const stepStatus = statusFor('STEP', stepTarget);
          const checkedContent = checkedContentFor(vvArray(step.source_sections));
          const commands = vvArray(step.commands).map((command) => {
            const commandTarget = { ...stepTarget, command_id: command.command_id };
            const commandStatus = statusFor('COMMAND', commandTarget);
            const signature = VERIFICATION_EVIDENCE.cliSignatureByCommandId.get(command.command_id) || null;
            return {
              id: vvText(command.command_id), text: vvText(command.text),
              treatment: vvText(command.treatment),
              executionStatus: vvStatus(command.execution_status),
              checkedContent: checkedContentFor([command.source.section]),
              sourceLocation: {
                file: vvText(command.source.file), section: vvSectionTitle(command.source.section),
                lineStart: command.source.line_start, lineEnd: command.source.line_end,
              },
              sourceSignature: signature ? {
                status: signature.status === 'pass' ? 'PASS' :
                  (['wrong-executable', 'unknown-command', 'unknown-option'].includes(signature.status)
                    ? 'FAIL' : 'UNVALIDATED'),
                findingId: signature.id, result: signature.status, detail: signature.detail,
                method: signature.method, claimLimit: signature.claimLimit,
                sourceRevision: signature.sourceRevision, handlerSource: signature.handlerSource,
                recordHref: `/__review__/cli-signature?finding=${encodeURIComponent(signature.id)}&binding=${
                  encodeURIComponent(command.command_id)}`,
              } : null,
              ...currentFields(commandStatus, historyFor('COMMAND', commandTarget), command.command_id),
              blockerDetails: vvBlockerDetails(commandStatus),
              evidence: (VERIFICATION_EVIDENCE.evidence.get(command.command_id) || []).map((row) => {
                const { qualificationEvidenceRef, ...safeRow } = row;
                return { ...safeRow, evidenceRef: VERIFICATION_EVIDENCE.evidenceRefById.get(row.ref) || null,
                  binding: vvIdentifier(command.command_id),
                  qualificationEvidence: qualificationEvidenceRef
                    ? [{ id: 'qualification-record', evidenceRef: qualificationEvidenceRef,
                      binding: vvIdentifier(command.command_id) }] : [] };
              }),
              score: (() => {
                const score = VERIFICATION_EVIDENCE.scoreByCommand.get(command.command_id) || null;
                return score ? { ...score, evidence: evidenceLinksFor(score.evidenceIds, command.command_id),
                  directEvidence: score.directEvidence.map((item) => ({
                    ...item, binding: vvIdentifier(command.command_id),
                  })) } : null;
              })(),
              notApplicableAssessment: (() => {
                const assessment = VERIFICATION_EVIDENCE.notApplicableByCommand.get(command.command_id) || null;
                return assessment ? { ...assessment, evidence: evidenceLinksFor(assessment.evidenceIds) } : null;
              })(),
              withdrawnRecords: withdrawnForApi(
                VERIFICATION_EVIDENCE.withdrawnByCommand.get(command.command_id) || []),
            };
          });
          return {
            id: vvText(step.step_id), instruction: vvText(step.instruction),
            executionClassification: vvText(step.execution_classification),
            executionStatus: vvStatus(step.execution_status), checkedContent,
            ...currentFields(stepStatus, historyFor('STEP', stepTarget), `STEP:${step.step_id}`),
            blockerDetails: vvMergeDetails(
              vvBlockerDetails(stepStatus), ...commands.map((command) => command.blockerDetails)),
            commands,
          };
        });
        return {
          id: vvText(branch.branch_id), condition: vvText(branch.condition),
          executionStatus: vvStatus(branch.execution_status),
          checkedContent: checkedContentFor(steps.flatMap((step) => step.checkedContent.sections)),
          ...currentFields(branchStatus, historyFor('BRANCH', branchTarget), `BRANCH:${branch.branch_id}`),
          blockerDetails: vvMergeDetails(
            vvBlockerDetails(branchStatus), ...steps.map((step) => step.blockerDetails)),
          steps,
        };
      });
      const accessClasses = vvArray(set.access_classes).map(vvText);
      const normalized = {
        id: vvText(set.test_set_id), title: vvText(set.title), executionStatus: vvStatus(set.execution_status),
        goal: vvText(set.goal), accessClasses,
        evidenceLaneHints: vvEvidenceLaneHints(accessClasses),
        safetyConstraints: vvArray(set.safety_constraints).map(vvText),
        limitations: vvArray(set.limitations).map(vvText),
        checkedContent: checkedContentFor(branches.flatMap((branch) => branch.checkedContent.sections)),
        ...currentFields(setStatus, historyFor('TEST_SET', setTarget), `TEST_SET:${set.test_set_id}`),
        blockerDetails: vvMergeDetails(
          vvBlockerDetails(setStatus), ...branches.map((branch) => branch.blockerDetails)),
        branches,
      };
      return { ...normalized, totals: vvSetTotals(normalized) };
    });
    const pageHistory = historyFor('PAGE', pageTarget);
    const pageFields = currentFields(pageStatus, pageHistory, `PAGE:${page.page_id}`);
    const materialClaims = (VERIFICATION_EVIDENCE.materialClaimsByPage.get(page.page_id) || []).map((claim) => ({
      ...claim,
      authority: { ...claim.authority,
        unresolvedEvidenceRequirements: claim.authority.unresolvedEvidenceRequirements.map((requirement) => ({
          ...requirement, boundEvidence: evidenceLinksFor(requirement.boundEvidenceIds),
        })) },
      current: { ...claim.current, evidence: evidenceLinksFor(claim.current.evidenceIds),
        dispositionEvidence: evidenceLinksFor(claim.current.dispositionEvidenceIds, claim.id),
        commandEvidenceBinding: claim.current.commandEvidenceBinding ? {
          ...claim.current.commandEvidenceBinding,
          directEvidence: evidenceLinksFor(claim.current.commandEvidenceBinding.directEvidenceIds),
          manifestEvidence: evidenceLinksFor([claim.current.commandEvidenceBinding.manifestEvidenceId], claim.id),
        } : null },
    }));
    const retiredMaterialClaims = (VERIFICATION_EVIDENCE.retiredMaterialClaimsByPage.get(page.page_id) || [])
      .map((claim) => ({ ...claim, retestEvidence: evidenceLinksFor([claim.retestEvidenceId]) }));
    const materialDisposition = VERIFICATION_EVIDENCE.materialPageDispositionByPage.get(page.page_id);
    return { available: true, supportLayer: false, workflow: true,
      sourceFreshness: { state: 'CURRENT', reason: freshness?.reason || 'matches-reviewed-snapshot',
        reviewedSourceRevision: VV_REVIEWED_SOURCE_REVISION,
        currentHostRouteCount: VERIFICATION_EVIDENCE.sourceFreshness.currentHostRouteCount,
        baselineHostRouteCount: VERIFICATION_EVIDENCE.sourceFreshness.baselineHostRouteCount },
      executionStatus: vvStatus(page.execution_status),
      checkedContent: checkedContentFor(), ...pageFields,
      procedureStatusSemantics: 'PROCEDURE_EXECUTION_AND_REQUIRED_CHILDREN_ONLY',
      materialDisposition,
      blockerDetails: vvMergeDetails(
        vvBlockerDetails(pageStatus), ...testSets.map((set) => set.blockerDetails)),
      evidenceLaneHints: vvMergeClassifications(VV_EVIDENCE_LANES,
        ...testSets.map((set) => set.evidenceLaneHints)),
      materialClaims, retiredMaterialClaims,
      retiredCommandWithdrawals: withdrawnForApi(
        VERIFICATION_EVIDENCE.retiredWithdrawnByPage.get(pageRoute) || []),
      testSets, totals: vvTotals(testSets, pageHistory) };
  } catch (error) {
    if (process.env.VAST_REVIEW_DEBUG === '1') console.error(`V&V page context unavailable: ${error.message}`);
    return { available: false, unavailableReason: vvText(error.message) };
  }
}

function issueDetails(key) {
  const issue = JIRA_ISSUES[key] || { title: key, status: '' };
  return {
    key, title: issue.title, status: issue.status,
    statusAsOf: issue.status ? JIRA_STATUS_SNAPSHOT_DATE : null,
    statusVerification: issue.status ? 'UNVERIFIED_SNAPSHOT' : null,
    url: JIRA_BASE_URL + encodeURIComponent(key),
  };
}

function reviewContextForPath(rawPath) {
  const pathname = normalizeReviewPath(rawPath);
  const verification = verificationForPath(pathname);
  const matched = PAGE_REVIEW_CONTEXTS.filter((entry) =>
    (entry.paths || []).includes(pathname) || (entry.prefixes || []).some((prefix) => pathname.startsWith(prefix))
  );
  const epicKeys = [];
  const issueKeys = [];
  const blockers = [];
  const seenBlockers = new Set();
  const addUnique = (list, value) => { if (value && !list.includes(value)) list.push(value); };

  if (pathname.startsWith('/host/') && !matched.length) addUnique(epicKeys, 'CON-1187');
  if (verification.available && verification.supportLayer) addUnique(issueKeys, 'CON-1518');
  for (const entry of matched) {
    for (const key of entry.epics || []) addUnique(epicKeys, key);
    for (const key of entry.issues || []) addUnique(issueKeys, key);
    for (const blocker of entry.blockers || []) {
      const fingerprint = `${blocker.issue || ''}\n${blocker.question || ''}`;
      if (seenBlockers.has(fingerprint)) continue;
      seenBlockers.add(fingerprint);
      blockers.push({
        question: blocker.question,
        owner: blocker.owner || '',
        issue: blocker.issue ? issueDetails(blocker.issue) : null,
      });
    }
  }
  return {
    pathname,
    matched: matched.length > 0,
    epics: epicKeys.map(issueDetails),
    issues: issueKeys.map(issueDetails),
    blockers,
    verification,
  };
}

fs.mkdirSync(FEEDBACK_DIR, { recursive: true });

// ------------------------------------------------------------- feedback io
const FEEDBACK_CATEGORIES = new Set(['Error', 'Unclear', 'Missing', 'Outdated', 'Suggestion', 'Question', 'Praise']);
const FEEDBACK_SEVERITIES = new Set(['Blocker', 'Major', 'Minor', 'Nit']);
const FEEDBACK_STATUSES = new Set(['open', 'resolved']);
const FEEDBACK_TYPES = new Set(['inline', 'page']);
const FEEDBACK_ITEM_KEYS = new Set([
  'id', 'reviewer', 'page', 'pageTitle', 'type', 'quote', 'prefix', 'suffix', 'heading',
  'category', 'severity', 'comment', 'status', 'createdAt', 'updatedAt', 'deleted',
]);
function feedbackString(value, name, { min = 0, max = 20000 } = {}) {
  if (typeof value !== 'string' || value.length < min || value.length > max ||
    /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)) {
    throw new Error(`invalid feedback ${name}`);
  }
  return value;
}
function feedbackTimestamp(value, name, now = Date.now()) {
  const text = feedbackString(value, name, { min: 24, max: 30 });
  const parsed = Date.parse(text);
  if (!Number.isFinite(parsed) || new Date(parsed).toISOString() !== text || parsed > now + 5 * 60 * 1000) {
    throw new Error(`invalid feedback ${name}`);
  }
  return { text, parsed };
}
function normalizeFeedbackItem(item, fallbackReviewer = '', index = null, now = Date.now()) {
  const label = index == null ? 'item' : `item ${index + 1}`;
  if (!item || typeof item !== 'object' || Array.isArray(item) ||
    Object.keys(item).some((key) => !FEEDBACK_ITEM_KEYS.has(key))) {
    throw new Error(`${label} must be a supported feedback object`);
  }
  const id = feedbackString(item.id, 'id', { min: 1, max: 200 });
  if (!/^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/.test(id)) throw new Error(`${label} has an invalid id`);
  const reviewerValue = typeof item.reviewer === 'string' && item.reviewer.trim()
    ? item.reviewer.trim() : fallbackReviewer;
  const reviewer = feedbackString(reviewerValue, 'reviewer', { min: 1, max: 200 });
  const page = feedbackString(item.page, 'page', { min: 1, max: 500 });
  const pageSegments = page.split('/').slice(1);
  if (!page.startsWith('/') || page.includes('\\') || /[?#]/.test(page) ||
    (page !== '/' && pageSegments.some((segment) => !segment || segment === '.' || segment === '..' ||
      !/^[A-Za-z0-9._~!$&'()*+,;=:@%-]+$/.test(segment)))) {
    throw new Error(`${label} has an invalid page path`);
  }
  const type = feedbackString(item.type, 'type', { min: 1, max: 20 });
  const quote = feedbackString(item.quote, 'quote', { max: 2000 });
  const prefix = feedbackString(item.prefix, 'prefix', { max: 1000 });
  const suffix = feedbackString(item.suffix, 'suffix', { max: 1000 });
  const heading = feedbackString(item.heading, 'heading', { max: 500 });
  if (!FEEDBACK_TYPES.has(type) || (type === 'inline' && quote.length < 2) ||
    (type === 'page' && (quote || prefix || suffix || heading))) {
    throw new Error(`${label} has an invalid feedback type or anchor`);
  }
  const category = feedbackString(item.category, 'category', { min: 1, max: 30 });
  const severity = feedbackString(item.severity, 'severity', { min: 1, max: 30 });
  const status = feedbackString(item.status, 'status', { min: 1, max: 20 });
  if (!FEEDBACK_CATEGORIES.has(category) || !FEEDBACK_SEVERITIES.has(severity) ||
    !FEEDBACK_STATUSES.has(status)) throw new Error(`${label} has an invalid classification`);
  const createdAt = feedbackTimestamp(item.createdAt, 'createdAt', now);
  const updatedAt = feedbackTimestamp(item.updatedAt, 'updatedAt', now);
  if (updatedAt.parsed < createdAt.parsed) throw new Error(`${label} has reversed timestamps`);
  if (item.deleted != null && typeof item.deleted !== 'boolean') {
    throw new Error(`${label} has an invalid deletion state`);
  }
  return {
    id, reviewer, page,
    pageTitle: feedbackString(item.pageTitle, 'pageTitle', { max: 500 }),
    type, quote, prefix, suffix, heading, category, severity,
    comment: feedbackString(item.comment, 'comment', { min: 1, max: 20000 }),
    status, createdAt: createdAt.text, updatedAt: updatedAt.text,
    ...(item.deleted === true ? { deleted: true } : {}),
  };
}
function normalizeFeedbackItems(items, fallbackReviewer = '') {
  if (!Array.isArray(items) || items.length > MAX_IMPORT_ITEMS) {
    throw new Error(`expected at most ${MAX_IMPORT_ITEMS} feedback items`);
  }
  const now = Date.now();
  const seen = new Set();
  return items.map((item, index) => {
    const normalized = normalizeFeedbackItem(item, fallbackReviewer, index, now);
    if (seen.has(normalized.id)) throw new Error(`duplicate feedback item id: ${normalized.id}`);
    seen.add(normalized.id);
    return normalized;
  });
}
function reviewerSlug(name) {
  const raw = feedbackString(name, 'reviewer', { min: 1, max: 200 }).trim();
  if (!raw) throw new Error('invalid feedback reviewer');
  const s = raw.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  // short hash keeps distinct names ("Ana B" vs "ana-b", non-ASCII names) in distinct files
  const h = crypto.createHash('sha1').update(raw).digest('hex').slice(0, 6);
  return (s || 'reviewer') + '-' + h;
}
function feedbackFile(reviewer) {
  return path.join(FEEDBACK_DIR, `feedback-${reviewerSlug(reviewer)}.json`);
}
function readReviewerState(reviewer) {
  try {
    const raw = fs.readFileSync(feedbackFile(reviewer), 'utf8');
    const data = JSON.parse(raw);
    return normalizeFeedbackItems(data.items, typeof data.reviewer === 'string' ? data.reviewer.trim() : reviewer);
  } catch (error) {
    if (error?.code === 'ENOENT') return [];
    // Never convert a corrupt/permission-denied state into an empty state: the
    // next autosave would otherwise overwrite recoverable reviewer feedback.
    throw new Error('existing reviewer feedback is unreadable; refusing to overwrite it');
  }
}
function mergeById(existing, incoming) {
  const byId = new Map();
  for (const it of existing) if (it && typeof it.id === 'string') byId.set(it.id, it);
  for (const it of incoming) {
    if (!it || typeof it.id !== 'string') continue;
    const cur = byId.get(it.id);
    if (!cur || String(it.updatedAt || '') >= String(cur.updatedAt || '')) byId.set(it.id, it);
  }
  return [...byId.values()];
}
function writeReviewerState(reviewer, items) {
  // per-item merge (newest updatedAt wins) so concurrent tabs/late writers never clobber each other
  const normalizedReviewer = feedbackString(reviewer, 'reviewer', { min: 1, max: 200 }).trim();
  const normalizedItems = normalizeFeedbackItems(items, normalizedReviewer);
  if (normalizedItems.some((item) => item.reviewer !== normalizedReviewer)) {
    throw new Error('feedback item reviewer must match the state owner');
  }
  const existingItems = readReviewerState(normalizedReviewer);
  if (existingItems.some((item) => item.reviewer !== normalizedReviewer)) {
    throw new Error('stored feedback reviewer does not match the state owner');
  }
  const merged = mergeById(existingItems, normalizedItems);
  const file = feedbackFile(normalizedReviewer);
  const payload = { reviewer: normalizedReviewer, updatedAt: new Date().toISOString(), pr: PR_URL, items: merged };
  const tmp = file + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(payload, null, 2));
  fs.renameSync(tmp, file);
  return merged.length;
}
function readAllItems() {
  const byId = new Map();
  const reviewers = [];
  for (const f of fs.readdirSync(FEEDBACK_DIR)) {
    if (!/^feedback-.*\.json$/.test(f)) continue;
    try {
      const data = JSON.parse(fs.readFileSync(path.join(FEEDBACK_DIR, f), 'utf8'));
      if (Array.isArray(data.items)) {
        const normalizedItems = normalizeFeedbackItems(data.items,
          typeof data.reviewer === 'string' ? data.reviewer.trim() : '');
        // dedupe across files by item id (a reviewer renaming mid-session leaves copies in
        // both files) — keep the newest version, tombstones included so deletes win
        for (const it of normalizedItems) {
          const cur = byId.get(it.id);
          if (!cur || String(it.updatedAt || '') >= String(cur.updatedAt || '')) byId.set(it.id, it);
        }
        const fileReviewer = typeof data.reviewer === 'string' && data.reviewer.trim()
          ? feedbackString(data.reviewer.trim(), 'reviewer', { min: 1, max: 200 })
          : normalizedItems[0]?.reviewer || f;
        reviewers.push(fileReviewer);
      }
    } catch {
      // Exports and aggregate status must be visibly incomplete rather than
      // silently omitting a corrupt reviewer file.
      throw new Error('a stored reviewer feedback file is unreadable; aggregate output is unavailable');
    }
  }
  const allItems = [...byId.values()];
  allItems.sort((a, b) => (a.page || '').localeCompare(b.page || '') ||
    (a.createdAt || '').localeCompare(b.createdAt || ''));
  return { items: allItems.filter((it) => !it.deleted), allItems, reviewers };
}

function feedbackExportPayload() {
  const { allItems, reviewers } = readAllItems();
  return {
    format: FEEDBACK_EXPORT_FORMAT,
    version: FEEDBACK_EXPORT_VERSION,
    generatedAt: new Date().toISOString(),
    pr: PR_URL,
    reviewers,
    // JSON is the restorable format.  Keep deletion tombstones so importing a
    // backup over an older state cannot resurrect feedback that was deleted.
    items: allItems,
  };
}

function importFeedbackPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error('expected a JSON feedback export object');
  }
  if (payload.format != null && payload.format !== FEEDBACK_EXPORT_FORMAT) {
    throw new Error(`unsupported feedback format: ${String(payload.format)}`);
  }
  if (payload.version != null && payload.version !== FEEDBACK_EXPORT_VERSION) {
    throw new Error(`unsupported feedback version: ${String(payload.version)}`);
  }
  if (!Array.isArray(payload.items)) throw new Error('expected an items[] array');
  if (payload.items.length > MAX_IMPORT_ITEMS) {
    throw new Error(`too many feedback items (maximum ${MAX_IMPORT_ITEMS})`);
  }

  const fallbackReviewer = typeof payload.reviewer === 'string' ? payload.reviewer.trim() : '';
  const normalizedItems = normalizeFeedbackItems(payload.items, fallbackReviewer);
  const groups = new Map();
  for (const item of normalizedItems) {
    if (!groups.has(item.reviewer)) groups.set(item.reviewer, []);
    groups.get(item.reviewer).push(item);
  }

  const states = [];
  for (const [reviewer, items] of groups) {
    states.push({ reviewer, received: items.length, stored: writeReviewerState(reviewer, items) });
  }
  return {
    ok: true,
    imported: payload.items.length,
    reviewerCount: states.length,
    reviewers: states,
  };
}

// ---------------------------------------------------------------- exports
const PRIORITY_MAP = { Blocker: 'Highest', Major: 'High', Minor: 'Medium', Nit: 'Low' };

function csvCell(v) {
  let s = String(v ?? '');
  // Spreadsheet programs can ignore leading whitespace/control characters before
  // evaluating a formula.  Neutralize every formula-leading cell, including CLI
  // text beginning with a dash; preserving display is less important than making
  // an exported reviewer-controlled CSV inert when opened.
  if (/^[\u0000-\u0020]*[=+\-@]/.test(s) || /^[\t\r]/.test(s)) s = "'" + s;
  if (/[",\r\n]/.test(s)) s = '"' + s.replace(/"/g, '""') + '"';
  return s;
}
function firstLine(s) {
  return String(s || '').split(/\r?\n/)[0].trim();
}
function itemSummary(it) {
  const page = (it.page || '/').replace(/^\/host\//, '').replace(/^\//, '') || 'home';
  let head = firstLine(it.comment).slice(0, 90);
  if (!head) head = (it.quote || '').slice(0, 90);
  return `[${page}] ${it.category || 'Feedback'}: ${head}`;
}
function itemDescription(it) {
  const lines = [];
  lines.push(`Docs review feedback on PR 185 (${PR_URL})`);
  lines.push('');
  lines.push(`Page: ${it.page || '/'}${it.pageTitle ? ' — ' + it.pageTitle : ''}`);
  if (it.heading) lines.push(`Section: ${it.heading}`);
  if (it.quote) {
    lines.push('');
    lines.push('Quoted text:');
    lines.push(`"${it.quote}"`);
  }
  lines.push('');
  lines.push('Comment:');
  lines.push(it.comment || '(no comment)');
  lines.push('');
  lines.push(`Category: ${it.category || '-'} | Severity: ${it.severity || '-'} | Status: ${it.status || 'open'}`);
  lines.push(`Reviewer: ${it.reviewer || '-'} | Created: ${it.createdAt || '-'}`);
  return lines.join('\n');
}
function toCsv(items) {
  const header = ['Summary', 'Issue Type', 'Priority', 'Labels', 'Description', 'Page', 'Section', 'Quote', 'Category', 'Severity', 'Status', 'Reviewer', 'Created'];
  const rows = [header.map(csvCell).join(',')];
  for (const it of items) {
    rows.push([
      itemSummary(it),
      'Task',
      PRIORITY_MAP[it.severity] || 'Medium',
      PR_LABEL,
      itemDescription(it),
      it.page || '',
      it.heading || '',
      it.quote || '',
      it.category || '',
      it.severity || '',
      it.status || 'open',
      it.reviewer || '',
      it.createdAt || '',
    ].map(csvCell).join(','));
  }
  return '﻿' + rows.join('\r\n') + '\r\n';
}
function toMarkdown(items, reviewers) {
  const out = [];
  out.push('# Vast.ai docs review feedback — PR 185');
  out.push('');
  out.push(`Generated ${new Date().toISOString()} · ${items.length} item(s) · reviewers: ${reviewers.join(', ') || '—'}`);
  out.push(`PR: ${PR_URL}`);
  const byPage = new Map();
  for (const it of items) {
    const key = it.page || '/';
    if (!byPage.has(key)) byPage.set(key, []);
    byPage.get(key).push(it);
  }
  for (const [page, list] of byPage) {
    out.push('');
    out.push(`## ${page}${list[0].pageTitle ? ' — ' + list[0].pageTitle : ''}`);
    let n = 0;
    for (const it of list) {
      n += 1;
      out.push('');
      out.push(`### ${n}. [${it.severity || '-'} · ${it.category || '-'}]${it.heading ? ' ' + it.heading : ''}${it.status === 'resolved' ? ' (resolved)' : ''}`);
      if (it.quote) out.push(`> ${String(it.quote).replace(/\r?\n/g, '\n> ')}`);
      out.push('');
      out.push(it.comment || '(no comment)');
      out.push('');
      out.push(`*— ${it.reviewer || 'unknown'}, ${it.createdAt || ''}*`);
    }
  }
  out.push('');
  return out.join('\n');
}

// ------------------------------------------------------------ status page
function esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function statusPage() {
  const { items, reviewers } = readAllItems();
  const open = items.filter((i) => i.status !== 'resolved').length;
  const vv = VERIFICATION_EVIDENCE;
  const statusCountsText = (counts) => [...VV_TARGET_STATUSES]
    .filter((status) => counts?.[status])
    .map((status) => `${esc(status)}=${counts[status]}`).join(' · ');
  const vvSummary = vv.available
    ? `<p><b>V&amp;V evidence:</b> ${vv.sourceFreshness.currentHostRouteCount} current primary Host routes · ${vv.sourceFreshness.baselineHostRouteCount} retained reviewed baseline routes · ${vv.totals.materialClaims} historical material claims · ${vv.totals.testSets} historical test sets · ${vv.totals.branches} historical branches · ${vv.totals.steps} historical checks · ${vv.totals.nonCommandSteps} historical non-command checks · ${vv.totals.executableIntentCommands} historical executable command targets · ${vv.totals.displayOnlyCommands} historical display-only command references · ${vv.totals.retainedEvidenceRecords} retained evidence records · ${vv.totals.scored} historical numeric semantic scores (${vv.totals.executableIntentScored} executable-intent scores, ${vv.totals.displayOnlyScored} display-only semantic scores) · ${vv.totals.notApplicableAssessments} historical approved display-only N/A · ${vv.totals.cliSupportLayers} CLI and ${vv.totals.sdkSupportLayers} SDK central-reference support layers (not Host workflows). Current freshness is evaluated separately from this retained history.</p>
      <p><b>Material-claim disposition:</b> ${statusCountsText(vv.materialClaimStatusCounts)}.<br>
      <b>Page semantic disposition:</b> ${statusCountsText(vv.materialPageDispositionStatusCounts)}. This is the page-level claim rollup. Procedure projection is reported separately and does not override these claim dispositions.</p>`
    : `<p><b>V&amp;V evidence:</b> fail-closed because this prerequisite failed: <code>${esc(vv.unavailableReason || 'package unavailable')}</code>. No validation claim is made until it is repaired and retested.</p>`;
  const byReviewer = Object.create(null);
  for (const it of items) byReviewer[it.reviewer || '?'] = (byReviewer[it.reviewer || '?'] || 0) + 1;
  const rows = Object.entries(byReviewer)
    .map(([r, n]) => `<tr><td>${esc(r)}</td><td>${n}</td></tr>`).join('') || '<tr><td colspan="2">No feedback yet</td></tr>';
  return `<!doctype html><html><head><meta charset="utf-8"><title>PR 185 review feedback</title>
<style>body{font:15px/1.5 system-ui,sans-serif;max-width:640px;margin:40px auto;padding:0 16px;color:#1a1a2e}
h1{font-size:22px} table{border-collapse:collapse;margin:12px 0}td,th{border:1px solid #ccc;padding:6px 14px;text-align:left}
.btn{display:inline-block;margin:4px 8px 4px 0;padding:8px 14px;border:1px solid #4a5cf0;border-radius:8px;color:#4a5cf0;background:#fff;text-decoration:none;font:600 14px system-ui;cursor:pointer}
.btn.primary{background:#4a5cf0;color:#fff}.muted{color:#687086}#importResult{min-height:24px;font-weight:600}
code{background:#f0f0f6;padding:2px 5px;border-radius:4px}</style></head><body>
<h1>Vast.ai docs review — PR 185 feedback</h1>
<p><b>${items.length}</b> item(s), <b>${open}</b> open. Feedback is stored in this local review workspace (default <code>review-feedback/</code>).</p>
${vvSummary}
<table><tr><th>Reviewer</th><th>Items</th></tr>${rows}</table>
<p>
<a class="btn primary" href="/__review__/export/feedback.json" download>Save JSON</a>
<button class="btn" id="importJson" type="button">Import JSON</button>
<input id="importJsonFile" type="file" accept="application/json,.json" hidden>
</p>
<p class="muted">JSON is the restorable backup for every page and reviewer. Import merges it with current feedback; newer item timestamps win.</p>
<p>Other exports: <a href="/__review__/export/feedback.csv">CSV (Jira import)</a> · <a href="/__review__/export/feedback.md">Markdown</a></p>
<p id="importResult" role="status" aria-live="polite"></p>
<p><b>Reviewer inputs and Jira sources</b> are shown for each page inside the review panel. The combined list remains available at <a href="/review-questions">/review-questions</a>, with the implemented-versus-open evidence in the <a href="${TRACEABILITY_URL}">traceability audit</a>.</p>
<p>When you're done reviewing, send the JSON file back to restore all feedback, or use the CSV for Jira import.</p>
<p><a href="/host/hosting-overview">← Back to the docs preview</a></p>
<script>
(function () {
  var button = document.getElementById('importJson');
  var input = document.getElementById('importJsonFile');
  var result = document.getElementById('importResult');
  button.addEventListener('click', function () { input.click(); });
  input.addEventListener('change', async function () {
    var file = input.files && input.files[0];
    if (!file) return;
    try {
      var payload = JSON.parse(await file.text());
      var count = payload && Array.isArray(payload.items) ? payload.items.length : 0;
      if (!confirm('Import ' + count + ' feedback item(s)? Existing newer items will be kept.')) return;
      result.textContent = 'Importing…';
      var response = await fetch('/__review__/api/import', {
        method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload)
      });
      var data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Import failed');
      result.textContent = 'Imported ' + data.imported + ' item(s) for ' + data.reviewerCount + ' reviewer(s). Reloading…';
      setTimeout(function () { location.reload(); }, 700);
    } catch (error) {
      result.textContent = 'Import failed: ' + String(error && error.message ? error.message : error);
    } finally {
      input.value = '';
    }
  });
})();
</script>
</body></html>`;
}

// ---------------------------------------------------------------- overlay
// Client-side overlay source. Served at /__review__/overlay.js.
// NOTE: written without backticks or "$"+"{" so it can live in String.raw.
const OVERLAY_JS = String.raw`
(function () {
  'use strict';
  if (window.__vastReviewLoaded) return;
  window.__vastReviewLoaded = true;

  var API = '/__review__/api';
  var LS_REVIEWER = 'vastReview.reviewer';
  var LS_ITEMS = 'vastReview.items';
  var CATEGORIES = ['Error', 'Unclear', 'Missing', 'Outdated', 'Suggestion', 'Question', 'Praise'];
  var SEVERITIES = ['Blocker', 'Major', 'Minor', 'Nit'];
  var SEV_COLOR = { Blocker: '#d92d20', Major: '#e8590c', Minor: '#b58a00', Nit: '#5c677d' };

  // ---------------- state ----------------
  var reviewer = '';
  var items = [];
  var pending = null;      // selection captured but not yet saved
  var selectionDraft = null; // latest page selection, kept until commented on or cleared
  var editingId = null;
  var showAllPages = false;
  var saveStatus = 'idle'; // idle | saving | saved | offline
  var saveTimer = null;
  var anchorTimer = null;
  var selectionTimer = null;
  var contextRequest = 0;
  var pageContext = { epics: [], issues: [], blockers: [] };

  try { reviewer = localStorage.getItem(LS_REVIEWER) || ''; } catch (e) {}
  try { items = JSON.parse(localStorage.getItem(LS_ITEMS) || '[]'); } catch (e) { items = []; }
  if (!Array.isArray(items)) items = [];

  function uid() { return 'fb-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8); }
  function nowIso() { return new Date().toISOString(); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function pageTitle() {
    var t = document.title || '';
    return t.replace(/\s*[-|–—]\s*Vast.*$/i, '').trim() || t;
  }
  function visibleItems() { return items.filter(function (it) { return !it.deleted; }); }
  function pageItems() {
    return visibleItems().filter(function (it) { return it.page === location.pathname; });
  }

  // ---------------- persistence ----------------
  function persistLocal() {
    try { localStorage.setItem(LS_ITEMS, JSON.stringify(items)); } catch (e) {}
  }
  function scheduleSave() {
    persistLocal();
    renderBadge();
    if (saveTimer) clearTimeout(saveTimer);
    saveStatus = 'saving';
    renderSaveStatus();
    saveTimer = setTimeout(pushToServer, 700);
  }
  function itemsForReviewer(name) {
    return items.filter(function (item) { return item && item.reviewer === name; });
  }
  function pushReviewerState(name, reflectStatus) {
    if (!name) {
      if (reflectStatus) { saveStatus = 'offline'; renderSaveStatus(); }
      return Promise.resolve(false);
    }
    var ownedItems = itemsForReviewer(name);
    return fetch(API + '/state', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ reviewer: name, items: ownedItems })
    }).then(function (r) {
      if (reflectStatus) {
        saveStatus = r.ok ? 'saved' : 'offline';
        renderSaveStatus();
      }
      return r.ok;
    }).catch(function () {
      if (reflectStatus) { saveStatus = 'offline'; renderSaveStatus(); }
      return false;
    });
  }
  function pushToServer() { return pushReviewerState(reviewer, true); }
  function mergeServerState() {
    if (!reviewer) return;
    fetch(API + '/state?reviewer=' + encodeURIComponent(reviewer))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var server = (data && Array.isArray(data.items)) ? data.items : [];
        var byId = {};
        items.forEach(function (it) { byId[it.id] = it; });
        server.forEach(function (s) {
          var mine = byId[s.id];
          if (!mine || String(s.updatedAt || '') > String(mine.updatedAt || '')) byId[s.id] = s;
        });
        items = Object.keys(byId).map(function (k) { return byId[k]; });
        persistLocal();
        scheduleAnchor();
        renderAll();
        scheduleSave(); // push items that so far existed only in this browser back to disk
      })
      .catch(function () {});
  }
  function flushNow() {
    // best-effort synchronous save on tab close / navigation away
    if (!reviewer) return;
    var ownedItems = itemsForReviewer(reviewer);
    if (!ownedItems.length) return;
    if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
    persistLocal();
    try {
      var blob = new Blob([JSON.stringify({ reviewer: reviewer, items: ownedItems })],
        { type: 'application/json' });
      navigator.sendBeacon(API + '/state', blob);
    } catch (e) {}
  }
  window.addEventListener('pagehide', flushNow);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') flushNow();
  });

  function saveJsonBackup() {
    if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
    persistLocal();
    var sync = reviewer ? pushToServer() : Promise.resolve(false);
    sync.then(function (ok) {
      if (!ok) return { serverComplete: false, payload: null };
      return fetch('/__review__/export/feedback.json').then(function (response) {
        if (!response.ok) throw new Error('server export unavailable');
        return response.json();
      }).then(function (payload) {
        return { serverComplete: true, payload: payload };
      }).catch(function () {
        return { serverComplete: false, payload: null };
      });
    }).then(function (result) {
      var serverItems = result.payload && Array.isArray(result.payload.items) ? result.payload.items : [];
      var byId = {};
      serverItems.concat(items).forEach(function (item) {
        if (!item || typeof item.id !== 'string') return;
        var prior = byId[item.id];
        if (!prior || String(item.updatedAt || '') >= String(prior.updatedAt || '')) byId[item.id] = item;
      });
      var backupItems = Object.keys(byId).map(function (id) { return byId[id]; });
      var localPayload = {
        format: 'vast-docs-review-feedback', version: 1,
        generatedAt: new Date().toISOString(),
        pr: 'https://github.com/vast-ai/docs/pull/185',
        reviewers: Array.from(new Set(backupItems.map(function (item) { return item && item.reviewer; })
          .filter(Boolean))),
        items: backupItems
      };
      var link = document.createElement('a');
      var objectUrl = URL.createObjectURL(new Blob([JSON.stringify(localPayload, null, 2)],
        { type: 'application/json' }));
      link.href = objectUrl;
      link.download = result.serverComplete
        ? 'pr185-docs-feedback.json' : 'pr185-docs-feedback-browser-local.json';
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(function () { URL.revokeObjectURL(objectUrl); }, 0);
      if (!result.serverComplete) {
        toast('Saved browser-local JSON because server sync was unavailable');
      } else toast('Saved JSON backup');
    });
  }

  function importJsonBackup(file) {
    if (!file) return;
    file.text().then(function (text) {
      var payload = JSON.parse(text);
      var count = payload && Array.isArray(payload.items) ? payload.items.length : 0;
      if (!confirm('Import ' + count + ' feedback item(s)? Existing newer items will be kept.')) return null;
      var sync = reviewer ? pushToServer() : Promise.resolve(true);
      return sync.then(function () {
        return fetch(API + '/import', {
          method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload)
        });
      });
    }).then(function (response) {
      if (!response) return null;
      return response.json().then(function (data) {
        if (!response.ok) throw new Error(data.error || 'Import failed');
        toast('Imported ' + data.imported + ' item(s) for ' + data.reviewerCount + ' reviewer(s)');
        if (reviewer) mergeServerState();
        return data;
      });
    }).catch(function (error) {
      toast('Import failed: ' + String(error && error.message ? error.message : error));
    });
  }

  // ---------------- text index + anchoring ----------------
  function skipNode(el) {
    if (!el) return false;
    var tag = el.nodeName;
    return tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT' || tag === 'TEMPLATE' || el.id === '__vast_review_host__';
  }
  function buildTextIndex() {
    var nodes = [];
    var text = '';
    var visCache = new Map();
    function isRendered(el) {
      if (visCache.has(el)) return visCache.get(el);
      var ok = false;
      if (el.getClientRects().length > 0) {
        var r = el.getBoundingClientRect();
        // zero/1px boxes catch sr-only clip patterns as well as display:none
        ok = r.width > 1.5 && r.height > 1.5 && getComputedStyle(el).visibility !== 'hidden';
      }
      visCache.set(el, ok);
      return ok;
    }
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        var p = node.parentNode;
        while (p && p !== document.body) {
          if (p.nodeType === 1 && skipNode(p)) return NodeFilter.FILTER_REJECT;
          p = p.parentNode;
        }
        var el = node.parentElement;
        if (el && node.data.trim() && !isRendered(el)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n;
    while ((n = walker.nextNode())) {
      nodes.push({ node: n, start: text.length, end: text.length + n.data.length });
      text += n.data;
    }
    return { text: text, nodes: nodes };
  }
  function globalOffsetOf(container, offset, index) {
    if (container.nodeType === 3) {
      for (var i = 0; i < index.nodes.length; i++) {
        if (index.nodes[i].node === container) return index.nodes[i].start + offset;
      }
    }
    return -1;
  }
  function nodeAt(index, globalPos, preferStart) {
    // binary search for the text node containing globalPos
    var lo = 0, hi = index.nodes.length - 1;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      var e = index.nodes[mid];
      if (globalPos < e.start) hi = mid - 1;
      else if (globalPos > e.end || (globalPos === e.end && preferStart && mid + 1 < index.nodes.length)) lo = mid + 1;
      else return { node: e.node, offset: globalPos - e.start };
    }
    return null;
  }
  function commonSuffixLen(a, b) {
    var n = 0;
    while (n < a.length && n < b.length && a[a.length - 1 - n] === b[b.length - 1 - n]) n++;
    return n;
  }
  function findQuote(index, quote, prefix) {
    if (!quote) return null;
    var hits = [];
    var from = 0, at;
    while ((at = index.text.indexOf(quote, from)) !== -1) {
      hits.push({ start: at, end: at + quote.length });
      from = at + 1;
      if (hits.length > 50) break;
    }
    if (!hits.length) {
      // whitespace-tolerant fallback
      var pattern = quote.replace(/[.*+?^$()\[\]{}|\\]/g, '\\$&').replace(/\s+/g, '\\s*');
      try {
        var m = new RegExp(pattern).exec(index.text);
        if (m) hits.push({ start: m.index, end: m.index + m[0].length });
      } catch (e) {}
    }
    if (!hits.length) return null;
    if (hits.length === 1 || !prefix) return hits[0];
    var best = hits[0], bestScore = -1;
    hits.forEach(function (h) {
      var before = index.text.slice(Math.max(0, h.start - prefix.length), h.start);
      var score = commonSuffixLen(before, prefix);
      if (score > bestScore) { bestScore = score; best = h; }
    });
    return best;
  }
  function makeRange(index, start, end) {
    var s = nodeAt(index, start, true);
    var e = nodeAt(index, end, false);
    if (!s || !e) return null;
    try {
      var r = document.createRange();
      r.setStart(s.node, s.offset);
      r.setEnd(e.node, e.offset);
      return r;
    } catch (err) { return null; }
  }

  var anchoredRanges = {}; // id -> Range
  function anchorAll() {
    anchoredRanges = {};
    var list = pageItems().filter(function (it) { return it.type === 'inline'; });
    if (list.length) {
      var index = buildTextIndex();
      list.forEach(function (it) {
        var hit = findQuote(index, it.quote, it.prefix);
        if (hit) {
          var r = makeRange(index, hit.start, hit.end);
          if (r) anchoredRanges[it.id] = r;
        }
      });
    }
    paintHighlights();
    renderList();
  }
  function scheduleAnchor() {
    if (anchorTimer) clearTimeout(anchorTimer);
    anchorTimer = setTimeout(anchorAll, 400);
  }
  function paintHighlights() {
    if (typeof Highlight === 'undefined' || !CSS.highlights) return;
    var ranges = Object.keys(anchoredRanges).map(function (k) { return anchoredRanges[k]; });
    if (ranges.length) {
      var hl = new Highlight();
      ranges.forEach(function (r) { hl.add(r); });
      CSS.highlights.set('vast-review', hl);
    } else {
      CSS.highlights.delete('vast-review');
    }
  }
  function flashRange(r) {
    if (typeof Highlight === 'undefined' || !CSS.highlights) return;
    CSS.highlights.set('vast-review-flash', new Highlight(r));
    setTimeout(function () { CSS.highlights.delete('vast-review-flash'); }, 1600);
  }

  // ---------------- selection capture ----------------
  function hideSelBtn() { selBtn.style.display = 'none'; }
  function clearSelectionDraft() {
    selectionDraft = null;
    hideSelBtn();
    renderSelectionDraft();
  }
  function positionSelectionButton(rect) {
    // The panel has its own persistent selection action. Avoid placing the
    // transient button underneath it when a reviewer selects text nearby.
    if (panel && panel.classList.contains('open')) { hideSelBtn(); return; }
    selBtn.style.visibility = 'hidden';
    selBtn.style.display = 'flex';
    var width = selBtn.offsetWidth || 190;
    var height = selBtn.offsetHeight || 36;
    var x = rect.left + (rect.width / 2) - (width / 2);
    var y = rect.bottom + 8;
    x = Math.max(8, Math.min(x, window.innerWidth - width - 8));
    if (y + height > window.innerHeight - 8) y = rect.top - height - 8;
    y = Math.max(8, Math.min(y, window.innerHeight - height - 8));
    selBtn.style.left = x + 'px';
    selBtn.style.top = y + 'px';
    selBtn.style.visibility = 'visible';
  }
  function onSelectionSettled() {
    var sel = document.getSelection();
    if (!sel || sel.isCollapsed || sel.rangeCount === 0) { hideSelBtn(); return; }
    var anchor = sel.anchorNode;
    var anchorRoot = anchor && anchor.getRootNode ? anchor.getRootNode() : null;
    if (anchorRoot === shadow) { hideSelBtn(); return; }
    if (anchor && host.contains(anchor.nodeType === 1 ? anchor : anchor.parentNode)) { hideSelBtn(); return; }
    if (anchor === host) { hideSelBtn(); return; }
    var quote = sel.toString().replace(/\s+$/,'').replace(/^\s+/,'');
    if (quote.length < 2 || quote.length > 2000) { hideSelBtn(); return; }
    var range = sel.getRangeAt(0);
    var rects = range.getClientRects();
    var rect = rects.length ? rects[rects.length - 1] : range.getBoundingClientRect();
    if (!rect || (rect.width === 0 && rect.height === 0)) { hideSelBtn(); return; }

    var index = buildTextIndex();
    var s = globalOffsetOf(range.startContainer, range.startOffset, index);
    var e = globalOffsetOf(range.endContainer, range.endOffset, index);
    var prefix = '', suffix = '';
    if (s >= 0) prefix = index.text.slice(Math.max(0, s - 40), s);
    if (e >= 0) suffix = index.text.slice(e, e + 40);

    selectionDraft = {
      quote: quote, prefix: prefix, suffix: suffix,
      heading: nearestHeading(range)
    };
    renderSelectionDraft();
    positionSelectionButton(rect);
  }
  function nearestHeading(range) {
    var hs = document.querySelectorAll('h1, h2, h3, h4');
    var best = '';
    for (var i = 0; i < hs.length; i++) {
      var pos = range.startContainer.compareDocumentPosition(hs[i]);
      if (pos & Node.DOCUMENT_POSITION_PRECEDING) best = hs[i].textContent.trim();
    }
    return best;
  }

  // ---------------- item ops ----------------
  var composerCtx = null; // page identity captured when the composer opens, so a
                          // back/forward navigation mid-typing cannot mislabel the item
  function canMutateItem(item) { return !!item && !!reviewer && item.reviewer === reviewer; }
  function saveItem(fields) {
    var it;
    var consumedSelection = false;
    if (editingId) {
      it = items.filter(function (x) { return x.id === editingId; })[0];
      if (!it) return;
      if (!canMutateItem(it)) { toast('Only the original reviewer can edit this item'); return; }
      it.category = fields.category;
      it.severity = fields.severity;
      it.comment = fields.comment;
      it.updatedAt = nowIso();
    } else {
      consumedSelection = !!(pending && pending.quote);
      it = {
        id: uid(),
        reviewer: reviewer,
        page: composerCtx ? composerCtx.page : location.pathname,
        pageTitle: composerCtx ? composerCtx.pageTitle : pageTitle(),
        type: pending && pending.quote ? 'inline' : 'page',
        quote: pending ? (pending.quote || '') : '',
        prefix: pending ? (pending.prefix || '') : '',
        suffix: pending ? (pending.suffix || '') : '',
        heading: pending ? (pending.heading || '') : '',
        category: fields.category,
        severity: fields.severity,
        comment: fields.comment,
        status: 'open',
        createdAt: nowIso(),
        updatedAt: nowIso()
      };
      items.push(it);
    }
    pending = null;
    editingId = null;
    if (consumedSelection) clearSelectionDraft();
    scheduleSave();
    scheduleAnchor();
    renderAll();
    toast('Feedback saved');
  }
  function deleteItem(id) {
    var it = items.filter(function (x) { return x.id === id; })[0];
    if (!it) return;
    if (!canMutateItem(it)) { toast('Only the original reviewer can delete this item'); return; }
    it.deleted = true;
    it.updatedAt = nowIso();
    scheduleSave();
    scheduleAnchor();
    renderAll();
  }
  function toggleResolve(id) {
    var it = items.filter(function (x) { return x.id === id; })[0];
    if (!it) return;
    if (!canMutateItem(it)) { toast('Only the original reviewer can resolve this item'); return; }
    it.status = it.status === 'resolved' ? 'open' : 'resolved';
    it.updatedAt = nowIso();
    scheduleSave();
    renderAll();
  }

  // ---------------- UI ----------------
  var host = document.createElement('div');
  host.id = '__vast_review_host__';
  var shadow = host.attachShadow({ mode: 'open' });

  // document-level styles (::highlight can't live in shadow DOM)
  var docStyle = document.createElement('style');
  docStyle.textContent = '::highlight(vast-review){background:rgba(255,200,50,.45);}' +
    '::highlight(vast-review-claim){background:#ffe082;color:#172033;text-decoration:underline;}' +
    '::highlight(vast-review-flash){background:rgba(74,92,240,.35);}';
  document.head.appendChild(docStyle);

  var css = '' +
    ':host{all:initial}' +
    '*{box-sizing:border-box;font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}' +
    '#pill{position:fixed;right:18px;bottom:18px;z-index:2147483000;display:flex;align-items:center;gap:8px;' +
      'padding:10px 16px;border:none;border-radius:999px;background:#4a5cf0;color:#fff;font-size:14px;font-weight:600;' +
      'cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.25)}' +
    '#pill:hover{background:#3a49d6}' +
    '#pill.selection-ready{background:#1a1a2e;box-shadow:0 0 0 3px rgba(255,209,102,.85),0 4px 16px rgba(0,0,0,.25)}' +
    '#pill .count{background:rgba(255,255,255,.25);border-radius:999px;padding:1px 8px;font-size:12px}' +
    '#selbtn{position:fixed;z-index:2147483001;display:none;align-items:center;gap:6px;padding:7px 12px;' +
      'border:none;border-radius:8px;background:#1a1a2e;color:#fff;font-size:13px;font-weight:600;cursor:pointer;' +
      'box-shadow:0 0 0 3px rgba(255,209,102,.85),0 4px 14px rgba(0,0,0,.3);white-space:nowrap}' +
    '#panel{position:fixed;top:0;right:0;bottom:0;width:380px;max-width:95vw;z-index:2147483002;display:none;' +
      'flex-direction:column;background:#fff;color:#1a1a2e;border-left:1px solid #d5d9e4;box-shadow:-6px 0 24px rgba(0,0,0,.12);font-size:13px}' +
    '#panel.open{display:flex}' +
    '#panel header{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:#1a1a2e;color:#fff}' +
    '#panel header b{font-size:14px}' +
    '#panel header button{background:none;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1}' +
    '.meta{display:flex;align-items:center;gap:8px;padding:8px 14px;border-bottom:1px solid #e7eaf1;color:#5c677d}' +
    '.meta b{color:#1a1a2e}' +
    '.meta button,.filters button{background:#f0f2f8;border:1px solid #d5d9e4;border-radius:6px;padding:3px 9px;cursor:pointer;font-size:12px}' +
    '.filters{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 14px;border-bottom:1px solid #e7eaf1}' +
    '.filters label{display:flex;align-items:center;gap:6px;cursor:pointer;color:#5c677d}' +
    '.filters .primary{background:#4a5cf0;border-color:#4a5cf0;color:#fff;font-weight:600}' +
    '.context-count{background:#fff1b8;color:#6b4f00;border-radius:999px;padding:1px 7px;font-size:11px;font-weight:800}' +
    '#jiraContext{padding:10px 14px;border-bottom:1px solid #e7eaf1;background:#f8f9fc;color:#384056;' +
      'min-height:140px;overflow-y:auto;flex:1 1 auto}' +
    '#jiraContext[hidden]{display:none}' +
    '.jira-title{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:7px}' +
    '.jira-title b{color:#1a1a2e;font-size:12px}' +
    '.jira-title a{font-size:11px;color:#4a5cf0;text-decoration:none;font-weight:700}' +
    '.jira-links{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:7px}' +
    '.jira-link{display:inline-flex;align-items:center;gap:4px;border:1px solid #c9d0e2;border-radius:999px;padding:3px 7px;' +
      'background:#fff;color:#34405a;text-decoration:none;font-size:11px;font-weight:700}' +
    '.jira-link.epic{border-color:#8d9af1;background:#f0f2ff;color:#3446ba}' +
    '.jira-link.blocked{border-color:#efaaa5;background:#fff2f0;color:#a12620}' +
    '.jira-status{font-size:9px;font-weight:700;opacity:.72;text-transform:uppercase}' +
    '.jira-blockers{margin-top:6px;border:1px solid #efd28a;border-radius:8px;background:#fff9e8;padding:7px 9px}' +
    '.jira-blockers summary{cursor:pointer;color:#6b4f00;font-weight:800;font-size:11px}' +
    '.jira-blockers ul{margin:7px 0 0;padding-left:18px}' +
    '.jira-blockers li{margin:0 0 7px;line-height:1.35;color:#5c5233}' +
    '.jira-blockers li:last-child{margin-bottom:0}' +
    '.jira-blockers a{color:#4a5cf0;text-decoration:none;font-weight:800;white-space:nowrap}' +
    '.jira-owner{display:block;color:#8a6f2f;font-size:10px;margin-top:2px}' +
    '.jira-clear{font-size:11px;color:#687188}' +
    '.vv-context{margin-top:7px;border:1px solid #c9d0e2;border-radius:8px;background:#fff;padding:7px 9px;overflow-wrap:anywhere;min-width:0}' +
    '.vv-context summary{cursor:pointer;font-size:11px;font-weight:800;color:#34405a}' +
    '.vv-help{margin:7px 0;padding:6px 7px;border-radius:6px;background:#f0f2ff;color:#525e78;font-size:10px;line-height:1.35}' +
    '.vv-blocker-help{margin:7px 0;padding:7px 8px;border:1px solid #efd28a;border-radius:6px;background:#fff9e8;color:#5c5233;font-size:10px;line-height:1.4}' +
    '.vv-blocker-help>div{margin-top:4px}.vv-blocker-help code{color:#7a4f00}' +
    '.vv-evidence-guide{margin-top:6px;border-top:1px solid #efdca8;padding-top:5px}' +
    '.vv-evidence-guide summary{color:#6b4f00!important;font-size:10px!important}' +
    '.vv-evidence-guide ol{margin:5px 0 0;padding-left:19px}.vv-evidence-guide li{margin:0 0 5px}' +
    '.vv-set-blocker{margin:6px 0;padding:6px 7px;border-left:3px solid #d59b17;background:#fffaf0;color:#5c5233;font-size:10px;line-height:1.4}' +
    '.vv-command-proof-list{margin:8px 0;border:1px solid #9aa7e8;border-radius:7px;background:#f7f8ff;padding:7px}' +
    '.vv-command-proof-list>summary{cursor:pointer;color:#2f42b5!important;font-size:11px!important;font-weight:800!important}' +
    '.vv-command-proof-card{margin:7px 0 0;padding:7px 8px;border:1px solid #d8ddf4;border-radius:6px;background:#fff;overflow-wrap:anywhere}' +
    '.vv-command-proof-card>code,.vv-command-source>code{display:block;white-space:pre-wrap;color:#1a1a2e;font-size:10px;font-weight:700}' +
    '.vv-command-source{display:block;color:#2439b8!important;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:2px}' +
    '.vv-proof-lane{margin-top:6px;padding:6px 7px;border-left:3px solid #8d9af1;background:#f8f9ff;color:#525e78;font-size:10px;line-height:1.4}' +
    '.vv-proof-lane.runtime{border-left-color:#4f9b78;background:#f4fbf7}' +
    '.vv-proof-lane.status{border-left-color:#d59b17;background:#fffaf0}' +
    '.vv-proof-lane a,.vv-source-link{color:#4a5cf0;text-decoration:underline;text-underline-offset:2px}' +
    '.vv-accounting{margin:4px 0 6px;padding:4px 6px;border:1px dashed #c9d0e2;border-radius:5px;background:#fafbfc}' +
    '.vv-accounting summary{cursor:pointer;color:#687188!important;font-size:10px!important;font-weight:650!important}' +
    '.vv-set{margin:7px 0;border-top:1px solid #e7eaf1;padding-top:6px}.vv-set summary{font-weight:700}' +
    '.vv-set-meta{display:block;margin:2px 0 0 13px;color:#687188;font-size:10px;font-weight:600}' +
    '.vv-branch{margin:7px 0}.vv-branch ol{margin:4px 0;padding-left:20px}.vv-step{margin-bottom:7px}' +
    '.vv-command{margin:5px 0;padding:6px;background:#f7f8fc;border-radius:6px}.vv-command code{white-space:pre-wrap}' +
    '.vv-meta,.vv-evidence,.vv-score{margin-top:3px;font-size:10px;color:#687188}.vv-evidence{padding-left:16px}' +
    '.vv-subject{margin:4px 0;font-size:10px;line-height:1.4;color:#687188}' +
    '.vv-subject a{color:#4a5cf0;text-decoration:underline;text-underline-offset:2px}' +
    '.vv-subject a:focus-visible,.vv-evidence-link:focus-visible{outline:2px solid #4a5cf0;outline-offset:2px;border-radius:2px}' +
    '.vv-evidence-link{color:#4a5cf0;text-decoration:underline;text-underline-offset:2px}' +
    '.vv-history{margin:4px 0 6px}.vv-history summary{font-size:10px!important;font-weight:650!important;color:#687188!important}' +
    '.vv-reading{color:#273248;font-size:13px;line-height:1.5}' +
    '.vv-reading h3{margin:4px 0;font-size:17px;color:#172033}.vv-reading p{margin:8px 0}' +
    '.vv-reading-counts{font-size:12px;color:#525e73}.vv-section-label{display:block;font-weight:700;margin-top:12px}' +
    '#vv-section-filter{width:100%;font-size:13px;padding:8px;color:#172033;border:1px solid #aeb8cf;border-radius:6px;background:#fff}' +
    '#vv-location-notice{font-size:12px;color:#38476a}#vv-location-notice:empty{display:none}' +
    '.vv-reading-card{margin:12px 0;padding:12px;border:1px solid #d5dce9;border-radius:9px;background:#fff;overflow-wrap:anywhere}' +
    '.vv-reading-card[hidden]{display:none}.vv-reading-card.vv-selected-claim{border-color:#6b5500;box-shadow:0 0 0 2px #ffe082}' +
    '.vv-reading-card .vv-code-quote{white-space:pre-wrap;font-family:ui-monospace,monospace;font-size:12px;max-height:230px;overflow:auto}.vv-checking{font-size:13px}' +
    '.vv-reading-location{font-size:12px;color:#5c677d}.vv-reading-card blockquote{margin:8px 0 10px;padding:0 0 0 9px;border-left:3px solid #a4b0d2;color:#172033;font-weight:600;font-size:14px;line-height:1.5}' +
    '.vv-reading-status{display:inline-block;background:#fff3cb;color:#694b00;border-radius:5px;padding:2px 7px;font-size:12px;font-weight:700}' +
    '.vv-reading-status[data-status="PASS"]{background:#e4f4eb;color:#175637}.vv-reading-status[data-status="FAIL"]{background:#ffe9e5;color:#982d20}' +
    '.vv-reading-actions{display:flex;align-items:center;gap:12px;margin:10px 0}.vv-reading-actions button{background:#3548c5;color:#fff;border:0;border-radius:6px;padding:7px 10px;cursor:pointer;font-size:12px;font-weight:700}' +
    '.vv-reading a{color:#3045bd;text-decoration:underline;text-underline-offset:2px}.vv-reading button:focus-visible,.vv-reading a:focus-visible,.vv-reading select:focus-visible,.vv-reading summary:focus-visible{outline:2px solid #3045bd;outline-offset:3px}' +
    '.vv-reading-audit,.vv-reading-links{font-size:12px;margin-top:10px}.vv-reading-audit>summary,.vv-reading-links>summary{cursor:pointer;color:#4a5872;font-weight:600}' +
    '.vv-reading-audit .vv-claims{margin-top:8px}.vv-technical{margin-top:16px}' +
    '#selectionTools{padding:10px 14px;border-bottom:1px solid #e7eaf1;background:#f7f8ff}' +
    '#selectionTools .selection-empty{color:#5c677d;line-height:1.45}' +
    '#selectionTools .selection-ready-body{display:none;gap:8px;flex-direction:column}' +
    '#selectionTools.ready .selection-empty{display:none}' +
    '#selectionTools.ready .selection-ready-body{display:flex}' +
    '.selection-title{display:flex;align-items:center;justify-content:space-between;gap:8px}' +
    '.selection-title b{color:#1a1a2e}' +
    '.selection-title button{border:0;background:none;color:#5c677d;cursor:pointer;font-size:12px;padding:0}' +
    '#selectionQuote{margin:0;padding:6px 10px;border-left:3px solid #ffd166;background:#fff9e8;color:#5c5233;' +
      'font-style:italic;max-height:72px;overflow:auto;white-space:pre-wrap}' +
    '#commentSelection{align-self:flex-start;border:0;border-radius:7px;padding:7px 11px;background:#4a5cf0;color:#fff;' +
      'font-size:12px;font-weight:700;cursor:pointer}' +
    '#list{flex:0 1 auto;max-height:25vh;overflow-y:auto;padding:10px 14px}#list:has(.empty){display:none}' +
    '#panel footer summary{cursor:pointer;color:#44516d;font-size:12px;font-weight:600}' +
    '.pagegroup{margin:14px 0 6px;font-weight:700;font-size:12px;color:#5c677d;text-transform:uppercase;letter-spacing:.4px}' +
    '.card{border:1px solid #e0e4ee;border-radius:10px;padding:10px 12px;margin-bottom:10px;background:#fbfcfe}' +
    '.card.resolved{opacity:.55}' +
    '.card .chips{display:flex;gap:6px;align-items:center;margin-bottom:6px;flex-wrap:wrap}' +
    '.chip{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;color:#fff}' +
    '.chip.cat{background:#5c677d}' +
    '.chip.orphan{background:#fff;color:#b58a00;border:1px dashed #b58a00}' +
    '.card blockquote{margin:6px 0;padding:4px 10px;border-left:3px solid #ffd166;background:#fffbeb;color:#5c5233;' +
      'font-style:italic;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}' +
    '.card .comment{white-space:pre-wrap;margin:6px 0}' +
    '.card .byline{color:#8a93a6;font-size:11px;margin-top:4px}' +
    '.card .acts{display:flex;gap:10px;margin-top:8px}' +
    '.card .acts button{background:none;border:none;padding:0;color:#4a5cf0;font-size:12px;cursor:pointer;font-weight:600}' +
    '.card .acts button.danger{color:#d92d20}' +
    '.empty{color:#8a93a6;text-align:center;padding:30px 10px}' +
    '#panel footer{border-top:1px solid #e7eaf1;padding:10px 14px;display:flex;flex-direction:column;gap:8px;background:#f7f8fc}' +
    '.exports{display:flex;gap:8px;align-items:center;flex-wrap:wrap}' +
    '.exports a,.exports button{color:#4a5cf0;background:#fff;font-weight:600;text-decoration:none;font:600 12px system-ui;border:1px solid #c9d0f5;border-radius:6px;padding:4px 9px;cursor:pointer}' +
    '.exports .primary{background:#4a5cf0;color:#fff;border-color:#4a5cf0}' +
    '.exports .label{font-size:11px;color:#687086}' +
    '#saveStatus{font-size:11px;color:#8a93a6}' +
    '#composer,#nameModal{position:fixed;z-index:2147483003;top:50%;left:50%;transform:translate(-50%,-50%);width:420px;max-width:92vw;' +
      'display:none;flex-direction:column;gap:10px;background:#fff;color:#1a1a2e;border-radius:14px;padding:18px;box-shadow:0 12px 48px rgba(0,0,0,.3);font-size:13px}' +
    '#composer.open,#nameModal.open{display:flex}' +
    '#composer h3,#nameModal h3{margin:0;font-size:15px}' +
    '#composer blockquote{margin:0;padding:6px 10px;border-left:3px solid #ffd166;background:#fffbeb;color:#5c5233;font-style:italic;' +
      'max-height:70px;overflow:auto}' +
    '.row{display:flex;gap:10px}' +
    '.row label{flex:1;display:flex;flex-direction:column;gap:4px;font-weight:600;color:#5c677d;font-size:11px;text-transform:uppercase}' +
    'select,textarea,input[type=text]{border:1px solid #c9cfdd;border-radius:8px;padding:8px;font-size:13px;width:100%;background:#fff;color:#1a1a2e}' +
    'textarea{min-height:90px;resize:vertical}' +
    '.btnrow{display:flex;justify-content:flex-end;gap:8px}' +
    '.btnrow button{border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer;border:1px solid #c9cfdd;background:#fff;color:#1a1a2e}' +
    '.btnrow button.primary{background:#4a5cf0;border-color:#4a5cf0;color:#fff}' +
    '#overlaybg{position:fixed;inset:0;z-index:2147483002;background:rgba(10,12,30,.35);display:none}' +
    '#overlaybg.open{display:block}' +
    '#toast{position:fixed;bottom:80px;right:24px;z-index:2147483004;background:#1a1a2e;color:#fff;padding:8px 16px;border-radius:8px;' +
      'font-size:13px;display:none}' +
    '@media(max-width:520px){#panel{width:100vw;max-width:100vw;padding-bottom:env(safe-area-inset-bottom)}' +
      '.vv-meta,.vv-evidence,.vv-score,.vv-subject{font-size:11px}' +
      '.vv-subject a{display:inline-block;padding:3px 0}' +
      '.vv-command code,.vv-meta code,.vv-evidence code{overflow-wrap:anywhere}}';

  var wrap = document.createElement('div');
  wrap.innerHTML =
    '<style>' + css + '</style>' +
    '<button id="pill" type="button" aria-controls="panel" aria-expanded="false"><span id="pillLabel">&#128172; Review</span> <span id="jiraCount" class="context-count" hidden></span> <span class="count" id="pillCount">0</span></button>' +
    '<button id="selbtn" type="button">&#128172; Comment on selection</button>' +
    '<div id="overlaybg"></div>' +
    '<aside id="panel" role="dialog" aria-modal="false" aria-labelledby="reviewPanelTitle" aria-hidden="true" tabindex="-1">' +
      '<header><b id="reviewPanelTitle">Docs review &mdash; PR 185</b><button id="closePanel" type="button" title="Close" aria-label="Close docs review panel">&times;</button></header>' +
      '<div class="meta">Reviewer: <b id="who">&mdash;</b> <button id="editWho">change</button></div>' +
      '<div class="filters">' +
        '<label><input type="checkbox" id="allPages"> Notes from all pages</label>' +
        '<button id="addPageNote" class="primary">+ Page note</button>' +
      '</div>' +
      '<section id="jiraContext" hidden aria-live="polite"></section>' +
      '<div id="selectionTools" aria-live="polite">' +
        '<div class="selection-empty"><b>Comment on exact wording</b><br>Select text on the page. Your selection will stay here while you write feedback.</div>' +
        '<div class="selection-ready-body">' +
          '<div class="selection-title"><b>Selected text</b><button id="clearSelection" type="button">Clear</button></div>' +
          '<blockquote id="selectionQuote"></blockquote>' +
          '<button id="commentSelection" type="button">&#128172; Add comment to selection</button>' +
        '</div>' +
      '</div>' +
      '<div id="list"></div>' +
      '<footer>' +
        '<details><summary>Review tools &amp; exports</summary>' +
        '<div class="exports" style="border-bottom:1px solid #e7eaf1;padding-bottom:8px">' +
          '<a href="/review-questions" style="background:#4a5cf0;color:#fff;border-color:#4a5cf0">All reviewer inputs and Jira gates</a>' +
          '<a href="${TRACEABILITY_URL}" target="_blank" rel="noopener noreferrer">Traceability audit</a>' +
        '</div>' +
        '<div class="exports">' +
          '<button id="saveJson" class="primary" type="button">Save JSON</button>' +
          '<button id="importJson" type="button">Import JSON</button>' +
          '<input id="importJsonFile" type="file" accept="application/json,.json" hidden>' +
          '<span class="label">Other exports:</span>' +
          '<a href="/__review__/export/feedback.csv">CSV (Jira)</a>' +
          '<a href="/__review__/export/feedback.md">Markdown</a>' +
          '<a href="/__review__/" target="_blank">Status</a>' +
        '</div>' +
        '</details>' +
        '<div id="saveStatus"></div>' +
      '</footer>' +
    '</aside>' +
    '<div id="composer" role="dialog" aria-modal="true" aria-labelledby="composerTitle" aria-hidden="true" tabindex="-1">' +
      '<h3 id="composerTitle">Add feedback</h3>' +
      '<blockquote id="composerQuote" style="display:none"></blockquote>' +
      '<div class="row">' +
        '<label>Category<select id="fCategory"></select></label>' +
        '<label>Severity<select id="fSeverity"></select></label>' +
      '</div>' +
      '<label style="display:flex;flex-direction:column;gap:4px;font-weight:600;color:#5c677d;font-size:11px;text-transform:uppercase">Comment' +
        '<textarea id="fComment" placeholder="What should change, and why?"></textarea></label>' +
      '<div class="btnrow"><button id="composerCancel">Cancel</button><button id="composerSave" class="primary">Save feedback</button></div>' +
    '</div>' +
    '<div id="nameModal" role="dialog" aria-modal="true" aria-labelledby="nameModalTitle" aria-hidden="true" tabindex="-1">' +
      '<h3 id="nameModalTitle">Who is reviewing?</h3>' +
      '<p style="margin:0;color:#5c677d">Your name is attached to each comment so feedback can be tracked in Jira.</p>' +
      '<input type="text" id="fName" placeholder="e.g. Ana">' +
      '<div class="btnrow"><button id="nameCancel" type="button">Cancel</button>' +
        '<button id="nameSave" class="primary" type="button">Start reviewing</button></div>' +
    '</div>' +
    '<div id="toast" role="status" aria-live="polite"></div>';
  shadow.appendChild(wrap);
  document.body.appendChild(host);

  function $(id) { return shadow.getElementById(id); }
  var pill = $('pill'), selBtn = $('selbtn'), panel = $('panel'), composer = $('composer'),
      nameModal = $('nameModal'), overlaybg = $('overlaybg'), toastEl = $('toast');
  var panelReturnFocus = null;
  var composerReturnFocus = null;
  var nameReturnFocus = null;
  var inertPageElements = [];

  function activeReviewElement() {
    return shadow.activeElement || document.activeElement;
  }
  function rememberFocus(fallback) {
    var active = activeReviewElement();
    return active && active !== document.body && active !== document.documentElement ? active : fallback;
  }
  function setModalIsolation(active) {
    if (active) {
      if (!inertPageElements.length) {
        Array.prototype.forEach.call(document.body.children, function (element) {
          if (element !== host && !element.inert) { element.inert = true; inertPageElements.push(element); }
        });
      }
      panel.inert = true;
      pill.inert = true;
      selBtn.inert = true;
      return;
    }
    if (composer.classList.contains('open') || nameModal.classList.contains('open')) return;
    panel.inert = false;
    pill.inert = false;
    selBtn.inert = false;
    inertPageElements.forEach(function (element) { element.inert = false; });
    inertPageElements = [];
  }
  function focusableElements(container) {
    return Array.prototype.filter.call(container.querySelectorAll(
      'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),' +
      '[tabindex]:not([tabindex="-1"])'), function (element) {
      return element.getAttribute('aria-hidden') !== 'true' && element.offsetParent !== null;
    });
  }
  function trapDialogFocus(event, dialog) {
    var focusable = focusableElements(dialog);
    if (!focusable.length) { event.preventDefault(); dialog.focus(); return; }
    var first = focusable[0], last = focusable[focusable.length - 1];
    var active = activeReviewElement();
    if (event.shiftKey && (active === first || !dialog.contains(active))) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && (active === last || !dialog.contains(active))) {
      event.preventDefault(); first.focus();
    }
  }

  CATEGORIES.forEach(function (c) {
    var o = document.createElement('option'); o.value = c; o.textContent = c; $('fCategory').appendChild(o);
  });
  SEVERITIES.forEach(function (s) {
    var o = document.createElement('option'); o.value = s; o.textContent = s; $('fSeverity').appendChild(o);
  });
  $('fCategory').value = 'Suggestion';
  $('fSeverity').value = 'Minor';

  var toastTimer = null;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.style.display = 'block';
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.style.display = 'none'; }, 1800);
  }

  function renderBadge() {
    var n = pageItems().filter(function (i) { return i.status !== 'resolved'; }).length;
    var total = visibleItems().length;
    $('pillCount').textContent = total
      ? n + ' open · ' + total + ' note' + (total === 1 ? '' : 's')
      : 'no review notes';
    $('pillCount').title = 'Reviewer feedback count; this is not a V&V score.';
  }
  function renderSaveStatus() {
    var map = {
      idle: '', saving: 'Saving…',
      saved: 'Saved to disk ✓',
      offline: reviewer ? 'Review server unreachable — stored in browser only' : 'Set your name to save feedback'
    };
    $('saveStatus').textContent = map[saveStatus] || '';
  }
  function renderSelectionDraft() {
    var box = $('selectionTools');
    if (!box) return;
    var ready = !!(selectionDraft && selectionDraft.quote);
    box.classList.toggle('ready', ready);
    $('selectionQuote').textContent = ready ? selectionDraft.quote : '';
    pill.classList.toggle('selection-ready', ready);
    $('pillLabel').innerHTML = ready ? '&#128172; Selected text' : '&#128172; Review';
  }
  function jiraLinkHtml(issue, isEpic) {
    if (!issue || !issue.key || !issue.url) return '';
    var classes = 'jira-link' + (isEpic ? ' epic' : '') + (issue.status === 'BLOCKED' ? ' blocked' : '');
    var statusLabel = issue.status
      ? issue.status + ' · snapshot ' + (issue.statusAsOf || 'unknown') + ' (unverified)'
      : '';
    return '<a class="' + classes + '" href="' + esc(issue.url) + '" target="_blank" rel="noopener noreferrer"' +
      ' title="' + esc(issue.title || issue.key) + '">' + esc(issue.key) +
      (statusLabel ? ' <span class="jira-status">' + esc(statusLabel) + '</span>' : '') + '</a>';
  }
  function countLabel(value, singular) {
    return value + ' ' + singular + (value === 1 ? '' : 's');
  }
  function normalizedHeadingText(value) {
    return String(value || '').replace(/\x60/g, '').replace(/[\u200B-\u200D\uFEFF]/g, '')
      .replace(/\s+/g, ' ').trim();
  }
  function readableStatus(status) {
    return { PASS: 'Supported by evidence', UNVALIDATED: 'Needs evidence',
      FAIL: 'Correction needed', BLOCKED: 'Waiting on a prerequisite',
      STALE: 'Needs a fresh check', NOT_APPLICABLE: 'Not applicable' }[status] || 'Needs evidence';
  }
  function claimWording(value) {
    // Remove inventory/Markdown notation, retaining the words the customer sees.
    var text = String(value || '');
    if (/^\[[A-Za-z0-9_-]+\]\s/.test(text)) return text.replace(/^\[[A-Za-z0-9_-]+\]\s*/, '');
    var inline = [];
    text = text.replace(/\x60([^\x60]+)\x60/g, function (_, literal) {
      inline.push(literal); return '\u0001CODE' + (inline.length - 1) + '\u0001';
    });
    return decodeReviewEntities(text)
      .replace(/!?\[([^\]]+)\]\([^\s]+(?:\s+"[^"]*")?\)/g, '$1')
      .replace(/\x60+/g, '').replace(/\*\*([^*]+)\*\*/g, '$1')
      .replace(/\s+\|\s+/g, ' · ')
      .replace(/\u0001CODE(\d+)\u0001/g, function (_, index) { return inline[Number(index)]; });
  }
  function decodeReviewEntities(text) {
    return String(text).replace(/&(#x[\da-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi, function (whole, entity) {
      if (entity[0] !== '#') return { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' }[entity.toLowerCase()];
      var value = entity[1].toLowerCase() === 'x' ? parseInt(entity.slice(2), 16) : Number(entity.slice(1));
      return value > 0 && value <= 0x10ffff ? String.fromCodePoint(value) : whole;
    });
  }
  function passageWording(passage) {
    var text = passage.text;
    var fence = text.match(/^\s*(\x60{3,}|~{3,})[^\n]*\n([\s\S]*?)\n\s*(?:\x60{3,}|~{3,})\s*$/);
    if (fence) return { text: fence[2], code: true, comparison: comparableWording(fence[2], false) };
    var caption = text.match(/^<Frame\b[^>]*\bcaption=(['"])(.*?)\1[^>]*>$/);
    if (caption) text = caption[2];
    // Preserve inline-code bytes while normalizing typography in the prose
    // around them. MDX smart punctuation can turn a bare prose double hyphen into an
    // em dash, but command options and identifiers must remain literal.
    var inline = [];
    text = text.replace(/\x60([^\x60]+)\x60/g, function (_, literal) {
      inline.push(decodeReviewEntities(literal));
      return '\uE000INLINE' + (inline.length - 1) + '\uE001';
    });
    text = text.replace(/^[ \t]*#{1,6} .*$/gm, '')
      .replace(/^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/gm, '')
      .replace(/^\s*\|(.+)\|\s*$/gm, '$1')
      .replace(/^[ \t]*(?:[-*+] |\d+[.)] )/gm, '')
      .replace(/<\/?(?:Note|Warning|Info|Tip|Check|Steps|Step|AccordionGroup|Accordion|Tabs|Tab|Frame|span|div|br|p|strong|em)\b[^>]*>/g, '');
    var cleaned = claimWording(text).trim();
    var restoreInline = function (value) {
      return value.replace(/\uE000INLINE(\d+)\uE001/g, function (_, index) { return inline[Number(index)]; });
    };
    var comparable = '', last = 0, marker;
    var comparableText = cleaned.replace(/ · /g, '');
    var markerPattern = /\uE000INLINE(\d+)\uE001/g;
    while ((marker = markerPattern.exec(comparableText))) {
      comparable += comparableWording(comparableText.slice(last, marker.index), true);
      comparable += comparableWording(inline[Number(marker[1])], false);
      last = marker.index + marker[0].length;
    }
    comparable += comparableWording(comparableText.slice(last), true);
    return { text: restoreInline(cleaned), code: false, comparison: comparable };
  }
  function comparableChar(c, foldTypography) {
    if (!foldTypography) return c;
    return /[\u2018\u2019]/.test(c) ? "'" : /[\u201C\u201D]/.test(c) ? '"' :
      c === '\u2013' ? '--' : c === '\u2014' ? '--' : c === '\u2026' ? '...' : c;
  }
  function comparableWording(text, foldTypography) {
    var fold = foldTypography !== false;
    return Array.from(text).map(function (c) { return comparableChar(c, fold); }).join('')
      .replace(/\s|[\u200B-\u200D\uFEFF]/g, '');
  }
  function articleRoot() {
    return document.querySelector('.mdx-content') || document.querySelector('article') || document.querySelector('main');
  }
  function sectionHeading(section) {
    var root = articleRoot();
    if (!root || section === 'Introduction') return null;
    var matches = Array.from(root.querySelectorAll('h1,h2,h3,h4,h5,h6')).filter(function (heading) {
      return normalizedHeadingText(heading.textContent) === normalizedHeadingText(section);
    });
    return matches.length === 1 ? matches[0] : null;
  }
  function claimTextMatch(row) {
    var root = articleRoot();
    if (!root || row.checkedContent.route !== location.pathname) return { reason: 'Page text is not available yet.' };
    var passages = row.sourcePassages || [{ text: row.claim ? row.claim.text : row.text,
      section: row.checkedContent.sections[0] || 'Introduction', occurrence: 0, occurrences: 1 }];
    var ranges = [], index = buildTextIndex();
    for (var passage of passages) {
      if (passage.redacted) return { reason: 'This passage contains an example masked in review data. Use its section link to inspect the original wording.' };
      var wording = row.sourcePassages ? passageWording(passage) : { text: claimWording(passage.text), code: /^\[[A-Za-z0-9_-]+\]\s/.test(passage.text) };
      var match = matchSourcePassage(root, index, passage, wording);
      if (!match.ranges) return match;
      ranges.push.apply(ranges, match.ranges);
    }
    return { ranges: ranges, range: ranges[0] };
  }
  function matchSourcePassage(root, index, passage, wording) {
    var section = passage.section;
    var heading = sectionHeading(section);
    if (section !== 'Introduction' && !heading) return { reason: 'The section could not be identified uniquely.' };
    var headings = Array.from(root.querySelectorAll('h1,h2,h3,h4,h5,h6'));
    var endHeading = headings.find(function (candidate) {
      return heading ? (heading.compareDocumentPosition(candidate) & Node.DOCUMENT_POSITION_FOLLOWING) &&
        Number(candidate.tagName.slice(1)) <= Number(heading.tagName.slice(1)) : candidate.tagName !== 'H1';
    });
    var codeClaim = wording.code;
    var chars = '', offsets = [];
    index.nodes.forEach(function (entry) {
      var el = entry.node.parentElement;
      if (!root.contains(entry.node) || el.closest('h1,h2,h3,h4,h5,h6,button,[aria-hidden="true"]')) return;
      if (heading && !(heading.compareDocumentPosition(entry.node) & Node.DOCUMENT_POSITION_FOLLOWING)) return;
      if (endHeading && !(endHeading.compareDocumentPosition(entry.node) & Node.DOCUMENT_POSITION_PRECEDING)) return;
      for (var i = 0; i < entry.node.data.length; i++) {
        var c = entry.node.data[i];
        if (/\s|[\u200B-\u200D\uFEFF]/.test(c)) continue;
        // Smart punctuation is a prose-rendering transform. Keep fenced and
        // inline code literal so an em dash can never stand in for two option
        // hyphens inside a command or identifier.
        var mapped = comparableChar(c, !codeClaim && !el.closest('pre,code'));
        chars += mapped;
        for (var j = 0; j < mapped.length; j++) offsets.push({ node: entry.node, offset: i });
      }
    });
    // Inventory table-cell separators are presentation notation, not page text.
    // Source passages carry a segment-aware comparison so inline code stays
    // byte-for-byte strict while adjacent prose can follow MDX typography.
    var needle = typeof wording.comparison === 'string' ? wording.comparison :
      comparableWording(codeClaim ? wording.text : wording.text.replace(/ · /g, ''), !codeClaim);
    var hits = [], at = -1;
    while (needle && (at = chars.indexOf(needle, at + 1)) !== -1) {
      var range = document.createRange(), start = offsets[at], end = offsets[at + needle.length - 1];
      range.setStart(start.node, start.offset);
      range.setEnd(end.node, end.offset + 1);
      if (codeClaim) {
        // A short command also appears as the prefix of commands with options.
        // Only an entire rendered code block is the same command occurrence.
        var block = range.startContainer.parentElement.closest('pre');
        if (!block || comparableWording(block.textContent, false) !== needle) continue;
      }
      hits.push(range);
    }
    if (!hits.length) return { reason: 'Exact wording was not found in this section. Use the section link and audit details.' };
    if (!codeClaim && hits.length > 1) {
      var wholeBlocks = hits.filter(function (range) {
        var block = range.startContainer.parentElement.closest('li,[data-as="p"],p,tr');
        return block && comparableWording(block.textContent) === needle;
      });
      if (wholeBlocks.length) hits = wholeBlocks;
    }
    if (hits.length !== passage.occurrences || passage.occurrence < 0 || !hits[passage.occurrence]) {
      return { reason: 'This wording could not be matched to its source occurrence uniquely. Use the section link to review it.' };
    }
    return { ranges: [hits[passage.occurrence]], heading: heading };
  }
  var claimSectionFilter = null;
  var focusedReviewClaim = null;
  function clearClaimFocus() {
    focusedReviewClaim = null;
    if (CSS.highlights) CSS.highlights.delete('vast-review-claim');
    shadow.querySelectorAll('.vv-selected-claim').forEach(function (card) { card.classList.remove('vv-selected-claim'); });
  }
  function sectionFromHash(claims) {
    var id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return ''; }
    var anchor = id && document.getElementById(id), root = articleRoot();
    if (!anchor || !root || !root.contains(anchor)) return '';
    var heading = /^H[1-6]$/.test(anchor.tagName) ? anchor : null;
    if (!heading) {
      // Historical alias anchors sit just before the renamed heading.
      heading = Array.from(root.querySelectorAll('h1,h2,h3,h4,h5,h6')).find(function (item) {
        return !!(anchor.compareDocumentPosition(item) & Node.DOCUMENT_POSITION_FOLLOWING);
      });
    }
    var text = heading && normalizedHeadingText(heading.textContent);
    return (claims || []).some(function (claim) { return claim.checkedContent.sections.indexOf(text) !== -1; }) ? text : '';
  }
  function showReviewWording(row, button) {
    var match = claimTextMatch(row);
    var notice = $('vv-location-notice');
    clearClaimFocus();
    if (!match.range) {
      if (notice) notice.textContent = match.reason;
      toast(match.reason);
      return;
    }
    focusedReviewClaim = row.id;
    var canHighlight = typeof Highlight !== 'undefined' && CSS.highlights;
    if (canHighlight) CSS.highlights.set('vast-review-claim', new Highlight(...match.ranges));
    var element = match.range.startContainer.parentElement;
    if (window.innerWidth < 1000) closePanel();
    element.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
    var href = checkedContentLink(row.checkedContent, row.checkedContent.sections[0]).href;
    // Avoid the SPA hook: this is locating wording, not loading a new page.
    if (href) origReplace.call(history, history.state, '', href);
    shadow.querySelectorAll('[data-review-claim]').forEach(function (card) {
      card.classList.toggle('vv-selected-claim', card.getAttribute('data-review-claim') === row.id);
    });
    if (notice) notice.textContent = (canHighlight ? 'Highlighted ' : 'Located (highlighting unavailable): ') +
      match.ranges.length + (match.ranges.length === 1 ? ' passage' : ' passages') + ' for this statement on the page.';
    if (window.innerWidth < 1000) toast((canHighlight ? 'Highlighted' : 'Located') +
      ' in ' + (row.checkedContent.sections[0] === 'Introduction' ? 'Page introduction' : row.checkedContent.sections[0]) +
      '. Open Review to return to the proof.');
    if (button && panel.classList.contains('open')) button.focus({ preventScroll: true });
  }
  function checkedContentLink(checkedContent, section) {
    var route = checkedContent && typeof checkedContent.route === 'string' &&
      /^\/host\/[A-Za-z0-9._/-]+$/.test(checkedContent.route) ? checkedContent.route : '';
    var segments = route ? route.split('/').slice(2) : [];
    if (!segments.length || segments.some(function (segment) {
      return !segment || segment === '.' || segment === '..';
    })) route = '';
    if (!route) return { href: '', exactSection: false };
    if (!section) return { href: route, exactSection: false };
    if (section === 'Introduction') return { href: route, exactSection: true, introduction: true };
    var expected = normalizedHeadingText(section);
    var headings = document.querySelectorAll('h1[id],h2[id],h3[id],h4[id],h5[id],h6[id]');
    var matches = [];
    for (var index = 0; index < headings.length; index += 1) {
      if (normalizedHeadingText(headings[index].textContent) === expected) {
        matches.push(headings[index]);
      }
    }
    return matches.length === 1
      ? { href: route + '#' + encodeURIComponent(matches[0].id), exactSection: true }
      : { href: route, exactSection: false };
  }
  function checkedContentHtml(row) {
    var checkedContent = row && row.checkedContent;
    var route = checkedContentLink(checkedContent, '').href;
    if (!route) return '';
    var sections = Array.isArray(checkedContent.sections) ? checkedContent.sections : [];
    if (!sections.length) {
      return '<div class="vv-subject"><b>Page under review:</b> <a href="' + esc(route) +
        '" title="Open the documentation being checked">' + esc(checkedContent.pageTitle || route) + '</a></div>';
    }
    var links = sections.map(function (section) {
      var target = checkedContentLink(checkedContent, section);
      if (target.introduction) {
        return '<a href="' + esc(target.href) + '" title="Open the page introduction">Page introduction</a>';
      }
      if (!target.exactSection) {
        return '<span>' + esc(section) + ' — section anchor unavailable; <a href="' + esc(target.href) +
          '" title="Open the documentation page being checked">view page</a></span>';
      }
      return '<a href="' + esc(target.href) + '" title="Open the documentation section being checked">' +
        esc(section) + '</a>';
    });
    return '<div class="vv-subject"><b>Declared section' + (links.length === 1 ? '' : 's') +
      ' under review:</b> ' + links.join(' · ') + '</div>';
  }
  function verificationHtml(vv) {
    var html = '<details class="vv-context"><summary>V&amp;V evidence for this page';
    if (!vv || !vv.available) {
      var unavailable = vv && vv.unavailableReason === 'page-not-in-inventory'
        ? 'This Host page is not in the current V&amp;V inventory. No validation or command-scoring claim is made for it.'
        : 'The V&amp;V package is fail-closed. Specific failed prerequisite: <code>' +
          esc(vv && vv.unavailableReason ? vv.unavailableReason : 'package unavailable') +
          '</code>. No validation or command-scoring claim is made until the package is repaired and retested.';
      return html + '</summary><div class="vv-meta">' + unavailable + '</div></details>';
    }
    if (vv.sourceFreshness && vv.sourceFreshness.state !== 'CURRENT') {
      var freshness = vv.sourceFreshness;
      var currentLink = freshness.currentPageHref
        ? '<a href="' + esc(freshness.currentPageHref) + '">Open current page</a>' : 'Current page link unavailable';
      var baselineLink = freshness.baselinePageHref
        ? '<a href="' + esc(freshness.baselinePageHref) + '" target="_blank" rel="noopener noreferrer">Open reviewed pinned source</a>'
        : 'No reviewed source exists for this new route';
      return html + ' · current source ' + esc(freshness.state) + '</summary>' +
        '<div class="vv-blocker-help"><b>Current validation: <code>' + esc(vv.currentStatus) + '</code></b><br>' +
        esc(freshness.explanation) + '<br><b>Exact next action:</b> ' + esc(freshness.nextAction) +
        '<br>' + currentLink + ' · ' + baselineLink +
        '<br><b>Historical record:</b> ' + esc(vv.historical && vv.historical.label ||
          'Reviewed historical snapshot (not current validation)') + '</div></details>';
    }
    function isAccountingStatus(row) {
      return /RECONCILIATION|ACCOUNTING|STATUS_BASIS_REBASE|LOCAL_STATUS_REBASE|TOPOLOGY_CORRECTION/i
        .test(row.currentMethod || '') ||
        /CURRENT-RECONCILIATION|REPOSITORY-REBASE|TOPOLOGY-CORRECTION/i
          .test(row.currentStatusAttemptId || '');
    }
    function currentStatusSuffix(row) {
      return row.currentStatus ? ' · ' + (isAccountingStatus(row) ? 'derived procedure ' : 'procedure ') + esc(row.currentStatus) +
        ' (status basis ' + esc(row.currentStatusAttemptId) + ')' : '';
    }
    function classificationLabels(items, fallback) {
      return (items || []).map(function (item) { return esc(item.label); }).join('; ') ||
        esc(fallback || 'See the retained rationale');
    }
    function setBlockerHtml(set) {
      if (set.currentStatus !== 'BLOCKED') return '';
      var actions = Array.from(new Set((set.blockerDetails || []).map(function (item) { return item.nextAction; })));
      var impacts = Array.from(new Set((set.blockerDetails || []).map(function (item) { return item.claimImpact; }).filter(Boolean)));
      return '<div class="vv-set-blocker"><b>Unavailable prerequisite(s):</b> ' +
        classificationLabels(set.blockerDetails) +
        (impacts.length ? '<br><b>Claim impact:</b> ' + esc(impacts.join(' ')) : '') +
        '<br><b>Exact next action:</b> ' + esc(actions.join(' ')) + '</div>';
    }
    function retainedEvidenceHtml(records, fallbackIds) {
      var items = Array.isArray(records) && records.length
        ? records
        : (fallbackIds || []).map(function (id) { return { id: id, evidenceRef: null }; });
      return items.map(function (item) {
        var label = '<code>' + esc(item.id) + '</code>';
        if (!item.evidenceRef) return label;
        var href = '/__review__/evidence?ref=' + encodeURIComponent(item.evidenceRef) +
          (item.binding ? '&binding=' + encodeURIComponent(item.binding) : '');
        return '<a class="vv-evidence-link" href="' + href +
          '" target="_blank" rel="noopener noreferrer" title="Open the retained evidence artifact" aria-label="Open retained evidence ' +
          esc(item.id) + '">' + label + '</a>';
      }).join(', ');
    }
    function authorityHtml(authority) {
      if (!authority) return 'not recorded';
      var parts = ['<code>' + esc(authority.kind || authority.state || 'not recorded') + '</code>'];
      if (authority.sourceRefs && authority.sourceRefs.length) {
        parts.push(authority.sourceRefs.map(function (source) {
          if (typeof source === 'string') return esc(source);
          var immutableGithub = /^(?:vast-ai\/vast-cli|vast-ai\/self-test)$/.test(source.repository || '') &&
            /^[a-f0-9]{40}$/.test(source.revision || '') &&
            /^[A-Za-z0-9._/-]+$/.test(source.path || '') &&
            String(source.path).split('/').every(function (segment) { return segment && segment !== '..'; });
          var label = '<code>' + esc(source.repository) + '@' + esc(source.revision) + '</code> · ' +
            esc(source.path);
          if (immutableGithub) {
            var href = 'https://github.com/' + source.repository + '/blob/' + source.revision + '/' + source.path;
            label = '<a class="vv-source-link" href="' + esc(href) +
              '" target="_blank" rel="noopener noreferrer" title="Open immutable canonical source">' +
              label + '</a>';
          }
          return label + ' · ' + esc(source.locator) +
            (source.sourceKind ? ' · <code>' + esc(source.sourceKind) + '</code>' : '');
        }).join('<br>'));
      }
      if (authority.unresolvedOwnerRole) parts.push('Unresolved owner: ' + esc(authority.unresolvedOwnerRole));
      if (authority.unresolvedQuestion) parts.push('Open question: ' + esc(authority.unresolvedQuestion));
      if (authority.unresolvedEvidenceRequirements && authority.unresolvedEvidenceRequirements.length) {
        parts.push('<b>Evidence-lane status:</b><ol>' + authority.unresolvedEvidenceRequirements.map(function (item) {
          return '<li><code>' + esc(item.evidenceType) + ' · ' + esc(item.currentStatus) + '</code>' +
            (item.evidenceState ? ' · <code>' + esc(item.evidenceState) + '</code>' : '') +
            '<br><b>Missing prerequisite:</b> <code>' + esc(item.prerequisiteKind) + '</code>' +
            '<br><b>Responsible role:</b> ' + esc(item.responsibleRole) +
            '<br><b>Required input:</b> ' + esc(item.requiredInput) +
            '<br><b>Exact next action:</b> ' + esc(item.nextAction) +
            (item.boundEvidenceIds && item.boundEvidenceIds.length
              ? '<br><b>Partial/satisfied evidence already retained:</b> ' +
                retainedEvidenceHtml(item.boundEvidence, item.boundEvidenceIds) : '') + '</li>';
        }).join('') + '</ol>');
      }
      if (authority.ownerConfirmationEvidenceId) parts.push('Owner confirmation: <code>' +
        esc(authority.ownerConfirmationEvidenceId) + '</code>');
      return parts.join('<br>');
    }
    function verificationContractHtml(row) {
      var contract = row && row.verificationContract;
      if (!contract) return '';
      var prerequisite = contract.unavailablePrerequisite;
      var html = '<details class="vv-history vv-contract"><summary>Claim and evidence contract · <code>' +
        esc(contract.basisKind) + '</code></summary>' + checkedContentHtml({ checkedContent: contract.checkedContent }) +
        '<div class="vv-meta"><b>Claim under review:</b> ' + esc(contract.claim) +
        '<br><b>Required evidence type(s):</b> ' + esc((contract.requiredEvidenceTypes || []).join('; ')) +
        '<br><b>Authority / source:</b> ' + authorityHtml(contract.authority) +
        '<br><b>Claim impact:</b> ' + esc(contract.claimImpact) +
        '<br><b>Limitations:</b> ' + esc(contract.limitations);
      if (contract.claimRefs && contract.claimRefs.length) {
        html += '<br><b>Material claim reference(s):</b> ' + contract.claimRefs.map(function (id) {
          return '<code>' + esc(id) + '</code>';
        }).join(', ');
      } else if (contract.noMaterialClaimReason) {
        html += '<br><b>No material-claim reference:</b> ' + esc(contract.noMaterialClaimReason);
      }
      if (prerequisite) {
        html += '<br><b>Unavailable prerequisite:</b> <code>' + esc(prerequisite.kind) + '</code> · ' +
          esc(prerequisite.description) + '<br><b>Prerequisite record:</b> ' +
          retainedEvidenceHtml(prerequisite.evidence, prerequisite.evidenceIds);
        if (prerequisite.components && prerequisite.components.length) {
          html += '<br><b>Concrete prerequisite component(s):</b><ol>' +
            prerequisite.components.map(function (component) {
              var origin = component.viaTarget;
              return '<li><code>' + esc(component.kind) + '</code> · ' + esc(component.description) +
                (origin ? '<br><b>Originating ' + esc(origin.level.toLowerCase()) + ':</b> <code>' +
                  esc(origin.id) + '</code>' + checkedContentHtml({ checkedContent: origin.checkedContent }) : '') +
                '<br><b>Component evidence:</b> ' +
                  retainedEvidenceHtml(component.evidence, component.evidenceIds) + '</li>';
            }).join('') + '</ol>';
        }
      }
      if (contract.targetBasis) {
        html += '<br><b>Target\'s own basis before child rollup:</b> <code>' +
          esc(contract.targetBasis.status) + ' · ' + esc(contract.targetBasis.basisKind) + '</code>' +
          '<br><b>Own required evidence:</b> ' +
            esc((contract.targetBasis.requiredEvidenceTypes || []).join('; ')) +
          '<br><b>Own authority / source:</b> ' + authorityHtml(contract.targetBasis.authority) +
          '<br><b>Own retained evidence:</b> ' +
            retainedEvidenceHtml(contract.targetBasis.supportingEvidence,
              contract.targetBasis.supportingEvidenceIds) +
          '<br><b>Own limitations:</b> ' + esc(contract.targetBasis.limitations);
        if (contract.targetBasis.unavailablePrerequisite) {
          html += '<br><b>Own unavailable prerequisite:</b> <code>' +
            esc(contract.targetBasis.unavailablePrerequisite.kind) + '</code> · ' +
            esc(contract.targetBasis.unavailablePrerequisite.description) +
            '<br><b>Own prerequisite evidence:</b> ' +
            retainedEvidenceHtml(contract.targetBasis.unavailablePrerequisite.evidence,
              contract.targetBasis.unavailablePrerequisite.evidenceIds);
        }
      }
      if (contract.nextAction) html += '<br><b>Exact next action:</b> ' + esc(contract.nextAction);
      if (contract.derivedFrom && contract.derivedFrom.length) {
        html += '<br><b>Direct-child inputs:</b> ' + contract.derivedFrom.map(function (child) {
          return '<span><code>' + esc(child.level) + ' ' + esc(child.id) + ' · ' +
            esc(child.currentStatus) + ' · ' + (child.required ? 'required; included' : 'optional; excluded') +
            '</code>' + checkedContentHtml({ checkedContent: child.checkedContent }) + '</span>';
        }).join(' · ');
      }
      return html + '</div></details>';
    }
    function citationHtml(citation) {
      if (!citation) return 'not recorded';
      var refs = (citation.refs || []).map(function (ref) {
        var safeHref = /^(?:#[-A-Za-z0-9._]+$|\/(?!\/)|https?:\/\/|mailto:)/i.test(ref.href || '');
        var link = safeHref ? '<a href="' + esc(ref.href) + '" target="_blank" rel="noopener noreferrer">' +
          esc(ref.href) + '</a>' : '<code>' + esc(ref.href) + '</code>';
        return link + ' · <code>' + esc(ref.kind) + '</code>';
      });
      return '<code>' + esc(citation.state) + '</code> · ' + esc(citation.assessment) +
        (refs.length ? '<br>' + refs.join('<br>') : ' · no link in this exact source occurrence');
    }
    function materialClaimsHtml(claims) {
      if (!claims || !claims.length) return '';
      return '<details class="vv-history vv-claims"><summary>' + countLabel(claims.length, 'material claim') +
        '</summary><ol class="vv-evidence">' + claims.map(function (claim) {
          return '<li><code>' + esc(claim.id) + '</code> · <b>' + esc(claim.current.status) + '</b>' +
            checkedContentHtml(claim) +
            (claim.renderedDependency ? '<b>Rendered dependency:</b> <code>' +
              esc(claim.renderedDependency.component) + '</code> (rendered on the linked Host page)<br>' : '') +
            '<b>Claim:</b> ' + esc(claim.claim.text) +
            '<br><b>Claim kind / limit:</b> <code>' + esc(claim.claim.kind) + '</code> · ' +
              esc(claim.claim.claimLimit) +
            '<br><b>Required evidence type(s):</b> ' + esc(claim.requiredEvidenceTypes.join('; ')) +
            '<br><b>Satisfied evidence lane(s):</b> ' +
              esc((claim.current.satisfiedEvidenceTypes || []).join('; ') || 'none') +
            '<br><b>Partially supported evidence lane(s):</b> ' +
              esc((claim.current.partiallySupportedEvidenceTypes || []).join('; ') || 'none') +
            '<br><b>Evidence requirement rationale:</b> ' + esc(claim.evidenceRationale) +
            '<br><b>Citation:</b> ' + citationHtml(claim.citation) +
            '<br><b>Authority / source:</b> ' + authorityHtml(claim.authority) +
            '<br><b>Rationale:</b> ' + esc(claim.current.rationale) +
            '<br><b>Claim-suitable semantic evidence:</b> ' +
              (claim.current.evidenceIds.length ? retainedEvidenceHtml(claim.current.evidence,
                claim.current.evidenceIds) : 'none bound') +
            '<br><b>Disposition evidence:</b> ' +
              retainedEvidenceHtml(claim.current.dispositionEvidence, claim.current.dispositionEvidenceIds) +
              ' · <code>' + esc(claim.current.dispositionEvidenceRole) + '</code>' +
            '<br><b>Disposition-evidence limit:</b> ' + esc(claim.current.dispositionLimitations.join('; ')) +
            '<br><b>Disposition-manifest limit:</b> ' + esc(claim.current.dispositionManifestLimitations) +
            (claim.current.unavailablePrerequisite
              ? '<br><b>Concrete unavailable prerequisite:</b> <code>' +
                esc(claim.current.unavailablePrerequisite.kind) + '</code> · ' +
                esc(claim.current.unavailablePrerequisite.description) : '') +
            (claim.current.commandEvidenceBinding
              ? '<br><b>Exact command binding:</b> <code>' + esc(claim.current.commandEvidenceBinding.commandId) +
                ' · score ' + esc(claim.current.commandEvidenceBinding.score) + '/3 · ' +
                esc(claim.current.commandEvidenceBinding.commandExecutionStatus) + '</code>' +
                '<br><b>Binding decision:</b> <code>' + esc(claim.current.commandEvidenceBinding.decision) + '</code>' +
                '<br><b>Direct command evidence:</b> ' + retainedEvidenceHtml(
                  claim.current.commandEvidenceBinding.directEvidence,
                  claim.current.commandEvidenceBinding.directEvidenceIds) +
                '<br><b>Exact binding manifest:</b> ' + retainedEvidenceHtml(
                  claim.current.commandEvidenceBinding.manifestEvidence,
                  [claim.current.commandEvidenceBinding.manifestEvidenceId]) : '') +
            '<br><b>Limitations:</b> ' + esc(claim.current.limitations.join('; ')) +
            (claim.nextAction ? '<br><b>Exact next action:</b> ' + esc(claim.nextAction) : '') + '</li>';
        }).join('') + '</ol></details>';
    }
    function readingEvidenceLinks(records, label, binding) {
      return (records || []).filter(function (record) { return record.evidenceRef; }).map(function (record, index) {
        var href = '/__review__/evidence?ref=' + encodeURIComponent(record.evidenceRef) +
          '&binding=' + encodeURIComponent(binding);
        return '<a class="vv-evidence-link" href="' + esc(href) + '" target="_blank" rel="noopener noreferrer"' +
          ' title="' + esc(record.id) + '">' + esc(label) + (records.length > 1 ? ' ' + (index + 1) : '') + '</a>';
      }).join(' · ');
    }
    function readingNextAction(claim) {
      if (claim.current.status === 'PASS') return '';
      var requirements = (claim.authority.unresolvedEvidenceRequirements || []).filter(function (item) {
        return item.currentStatus !== 'PASS';
      });
      var actions = requirements.map(function (item) {
        var task = {
          CANONICAL_IMPLEMENTATION_SOURCE: 'provide the official code or API source and its version, then check it against this wording.',
          RUNTIME_OR_UI_OBSERVATION: 'provide an authorized test result showing what happened for this instruction.',
          ACCOUNTABLE_OWNER_CONFIRMATION: 'confirm this wording using the approved product, finance, legal, or account source.',
          AUTHORITATIVE_DOCUMENTATION_CITATION: 'add the required citation to the approved source for this wording.'
        }[item.evidenceType];
        return task ? esc(item.responsibleRole || claim.authority.unresolvedOwnerRole || 'Source owner') + ': ' + task : '';
      }).filter(Boolean);
      if (claim.citation.required && claim.citation.state === 'ABSENT' &&
          !requirements.some(function (item) { return item.evidenceType === 'AUTHORITATIVE_DOCUMENTATION_CITATION'; })) {
        actions.push('Add the required citation to an authoritative source.');
      }
      if (!actions.length && claim.nextAction) actions.push(esc(claim.nextAction.replace(/MCL-[a-f0-9]+/g, 'this wording')));
      return actions.length ? '<p><b>Next:</b> ' + Array.from(new Set(actions)).join('<br>') + '</p>' : '';
    }
    function readingProof(claim) {
      var current = claim.current, sources = claim.authority.sourceRefs || [];
      var links = sources.map(function (source) {
        if (!source || typeof source !== 'object') return '';
        if (/^vast-ai\/(?:vast-cli|self-test)$/.test(source.repository || '') &&
            /^[a-f0-9]{40}$/.test(source.revision || '') && /^[A-Za-z0-9._/-]+$/.test(source.path || '') &&
            source.path.split('/').every(function (part) { return part && part !== '..'; })) {
          return '<a href="https://github.com/' + esc(source.repository) + '/blob/' + esc(source.revision) + '/' +
            esc(source.path) + '" target="_blank" rel="noopener noreferrer">Official source: ' + esc(source.path) + '</a>';
        }
        return '';
      }).filter(Boolean);
      var evidence = readingEvidenceLinks(current.evidence, 'Read the recorded check', claim.id);
      if (evidence) links.push(evidence);
      var summary;
      if (current.status === 'PASS') {
        summary = claim.claim.kind === 'NAVIGATION_CONTRACT' || sources.some(function (source) { return source.sourceKind === 'ROUTE_DESTINATION_SOURCE'; })
          ? 'The link destination was checked. This supports navigation only.'
          : 'Supporting evidence is recorded for this wording; check its scope and limitations below.';
      } else if (!current.evidenceIds.length) {
        summary = current.status === 'FAIL' ? 'A required citation or source binding is missing or incorrect.' :
          'No supporting proof is attached to this wording yet.';
      } else {
        summary = 'Some evidence is attached, but it does not fully support this wording.';
      }
      var result = '<p><b>Proof:</b> ' + summary + (links.length ? '<br>' + links.join('<br>') : '') + '</p>';
      if (current.status === 'PASS' && current.limitations.length) result += '<p><b>Scope of proof:</b> ' +
        esc(current.limitations.join('; ')) + '</p>';
      var commands = (vv.testSets || []).flatMap(function (set) { return set.branches.flatMap(function (branch) {
        return branch.steps.flatMap(function (step) { return step.commands; });
      }); });
      var matchingCommands = commands.filter(function (command) {
        return command.checkedContent.sections[0] === claim.checkedContent.sections[0] &&
          claimWording(claim.claim.text).replace(/\s+/g, '') === command.text.replace(/\s+/g, '');
      });
      if (matchingCommands.length === 1 && matchingCommands[0].sourceSignature && matchingCommands[0].sourceSignature.handlerSource) {
        var signature = matchingCommands[0].sourceSignature;
        result += '<p><b>Command definition:</b> <a href="' + esc(signature.handlerSource.href) +
          '" target="_blank" rel="noopener noreferrer">See the official CLI code</a>. ' +
          'This checks the command and its options; it does not show that the command ran successfully.</p>';
      }
      if (matchingCommands.length === 1) {
        var command = matchingCommands[0];
        var commandReason = command.currentStatus === 'UNVALIDATED'
          ? 'No conclusive test result supports this command yet.'
          : (command.currentRationale || 'No result is recorded.').replace(
            /^(?:CONFIRMED_DEFECT(?:\s+CLM-[a-f0-9]+)?|UNAVAILABLE_PREREQUISITE(?:\s+[A-Z_]+)?):\s*/, '');
        result += '<p><b>Command test:</b> ' + esc(readableStatus(command.currentStatus)) + '. ' +
          esc(commandReason) + '</p>';
        var records = (command.evidence || []).filter(function (item) {
          return item.evidenceRef && !item.supersededBy && !/ACCOUNTING|RECONCILIATION|TOPOLOGY/i.test(item.method || '');
        }).map(function (item) { return { id: item.ref, evidenceRef: item.evidenceRef }; });
        if (records.length) result += '<p>' + readingEvidenceLinks(records, 'Read the command result', command.id) + '</p>';
      }
      if (current.unavailablePrerequisite) result += '<p><b>Waiting for:</b> ' + esc(current.unavailablePrerequisite.description) + '</p>';
      if (claim.citation.required) result += '<p><b>Citation:</b> ' +
        (claim.citation.state === 'ABSENT' ? 'Required source citation is missing.' : 'Required; see the citation assessment in audit details.') + '</p>';
      // Existing documentation links may be navigation only. Never label them as proof.
      if (claim.citation.refs.length) result += '<details class="vv-reading-links"><summary>Links in this wording</summary>' +
        citationHtml(claim.citation) + '</details>';
      return result;
    }
    function readingClaimsHtml(claims) {
      if (!claims || !claims.length) return '';
      var sections = Array.from(new Set(claims.flatMap(function (claim) { return claim.checkedContent.sections; })));
      var selected = claimSectionFilter === null ? sectionFromHash(claims) : claimSectionFilter;
      var counts = vv.materialDisposition && vv.materialDisposition.counts || {};
      var summary = Object.keys(counts).filter(function (status) { return counts[status]; }).map(function (status) {
        return counts[status] + ' ' + ({ PASS: 'with support', UNVALIDATED: 'awaiting evidence',
          FAIL: 'needing correction', BLOCKED: 'waiting on a prerequisite' }[status] || readableStatus(status).toLowerCase());
      }).join(' · ');
      var result = '<section class="vv-reading" aria-label="Wording and proof"><h3>Wording &amp; proof</h3>' +
        '<p>Read the statement, then check its support. <b>Show on page</b> highlights the customer-visible text.</p>' +
        '<p class="vv-reading-counts">Whole page: ' + claims.length + ' statements · ' + esc(summary) + '</p>' +
        '<label class="vv-section-label" for="vv-section-filter">Review section</label>' +
        '<select id="vv-section-filter"><option value=""' + (!selected ? ' selected' : '') + '>All sections (' + claims.length + ')</option>' +
        sections.map(function (section) {
          var count = claims.filter(function (claim) { return claim.checkedContent.sections.indexOf(section) !== -1; }).length;
          return '<option value="' + esc(section) + '"' + (selected === section ? ' selected' : '') + '>' +
            esc(section === 'Introduction' ? 'Page introduction' : section) + ' (' + count + ')</option>';
        }).join('') + '</select><p id="vv-location-notice" role="status" aria-live="polite"></p><div id="vv-reading-cards">';
      claims.forEach(function (claim) {
        var section = claim.checkedContent.sections[0] || 'Introduction';
        var href = checkedContentLink(claim.checkedContent, section).href;
        var redactedPassage = (claim.sourcePassages || []).some(function (passage) { return passage.redacted; });
        var passages = redactedPassage ? [] : (claim.sourcePassages || []).map(passageWording);
        var quoteHtml = redactedPassage
          ? '<p class="vv-checking"><b>Exact page wording is hidden in this review copy.</b> ' +
            'It contains a masked example. The review claim below is a summary, not a quote.</p>' +
            '<p class="vv-checking"><b>Review claim:</b> ' + esc(claimWording(claim.claim.text)) + '</p>'
          : passages.length ? passages.map(function (passage) {
          return '<blockquote' + (passage.code ? ' class="vv-code-quote"' : '') + '>' + esc(passage.text) + '</blockquote>';
        }).join('') : '<blockquote>' + esc(claimWording(claim.claim.text)) + '</blockquote>';
        var quoteDiffers = !redactedPassage && comparableWording(passages.map(function (item) { return item.text; }).join(' ')) !==
          comparableWording(claimWording(claim.claim.text));
        var inheritedBindingNotice = claim.id === 'VOL-C35' && claim.checkedContent.route === '/host/volume-offers' &&
          claim.checkedContent.sections.indexOf('Command Map') === -1
          ? '<p class="vv-checking"><b>Source-location note:</b> This link check also covers ' +
            '<a href="/host/volume-offers#command-map">Command Map</a>. Its retained source location currently lists Related Pages only.</p>'
          : '';
        var inheritedFormattingOption = claim.checkedContent.route === '/host/self-test-reference'
          ? { 'MCL-c99f9ecb5ea4e15a': '--ignore-requirements',
              'MCL-22a1a520d989a59f': '--debugging' }[claim.id]
          : null;
        var hasBareFormattingSource = inheritedFormattingOption && (claim.sourcePassages || []).some(function (passage) {
          // Once the option is marked as inline code in the bound source, this
          // inherited-defect warning removes itself.
          var proseOnly = String(passage.text || '').replace(/\x60[^\x60]*\x60/g, '');
          return proseOnly.indexOf(inheritedFormattingOption) !== -1;
        });
        var inheritedFormattingNotice = hasBareFormattingSource
          ? '<p class="vv-checking"><b>Page formatting issue:</b> This page renders the documented option with a typographic dash. ' +
            'The correct literal option is <code>' + esc(inheritedFormattingOption) + '</code>. ' +
            'Locating the page text is not proof that the option spelling works. ' +
            '<b>Maintainer follow-up:</b> mark the option as inline code and regenerate its source binding.</p>'
          : '';
        result += '<article class="vv-reading-card" data-review-claim="' + esc(claim.id) + '" data-review-section="' + esc(section) + '"' +
          ' data-review-sections="' + esc(JSON.stringify(claim.checkedContent.sections)) + '"' +
          (selected && claim.checkedContent.sections.indexOf(selected) === -1 ? ' hidden' : '') + '>' +
          '<div class="vv-reading-location">' + esc(claim.checkedContent.sections.map(function (item) {
            return item === 'Introduction' ? 'Page introduction' : item;
          }).join(' / ')) + '</div>' +
          (quoteDiffers ? '<p class="vv-checking"><b>Checking:</b> ' + esc(claimWording(claim.claim.text)) + '</p>' : '') + quoteHtml +
          inheritedBindingNotice + inheritedFormattingNotice +
          '<span class="vv-reading-status" data-status="' + esc(claim.current.status) + '" title="' + esc(claim.current.status) + '">' +
            esc(readableStatus(claim.current.status)) + '</span>' +
          '<div class="vv-reading-actions"><button type="button" data-show-claim="' + esc(claim.id) + '">Show on page</button>' +
          claim.checkedContent.sections.map(function (item) {
            return '<a href="' + esc(checkedContentLink(claim.checkedContent, item).href) + '">' +
              (item === 'Introduction' ? 'Open introduction' : claim.checkedContent.sections.length > 1 ? esc(item) : 'Open section') + '</a>';
          }).join(' ') + '</div>' + readingProof(claim) + readingNextAction(claim) +
          '<details class="vv-reading-audit"><summary>Audit details</summary>' +
            '<p>Tracking ID: <code>' + esc(claim.id) + '</code> · ' + esc(claim.current.status) + '</p>' +
            (claim.sourceLocation ? '<p>Documentation location: <code>' + esc(claim.sourceLocation.file) + '</code><br>Source lines: ' +
              esc(claim.sourceLocation.spans.map(function (span) { return span.start + '–' + span.end; }).join(', ')) + '</p>' : '') +
            '<p>' + esc(claim.current.rationale) + '</p>' +
            '<p><b>Limits:</b> ' + esc(claim.current.limitations.join('; ')) + '</p>' +
            '<p><b>Status record only:</b> ' + readingEvidenceLinks(claim.current.dispositionEvidence, 'Why this status was recorded', claim.id) +
              '. This record tracks the review; it does not prove the statement.</p>' +
            materialClaimsHtml([claim]) + '</details></article>';
      });
      return result + '</div></section>';
    }
    function retiredMaterialClaimsHtml(claims) {
      if (!claims || !claims.length) return '';
      return '<details class="vv-history vv-claims"><summary>' + countLabel(claims.length,
        'preserved failed claim/correction') + '</summary><ol class="vv-evidence">' +
        claims.map(function (claim) {
          return '<li><code>' + esc(claim.id) + '</code> · <b>historical FAIL preserved</b>' +
            checkedContentHtml(claim) + '<b>Original claim:</b> ' + esc(claim.claim) +
            '<br><b>Confirmed failure:</b> ' + esc(claim.failure) +
            '<br><b>Correction:</b> ' + esc(claim.correction) +
            (claim.currentClaimId
              ? '<br><b>Current replacement claim:</b> <code>' + esc(claim.currentClaimId) + '</code>'
              : '<br><b>Current disposition:</b> unsupported assertion removed; no replacement claim exists') +
            '<br><b>Correction retest:</b> ' + retainedEvidenceHtml(claim.retestEvidence,
              [claim.retestEvidenceId]) + '</li>';
        }).join('') + '</ol></details>';
    }
    if (vv.supportLayer) {
      var supportReading = '<section class="vv-reading vv-support-reading" aria-label="Central reference"><h3>Central reference</h3>' +
        '<p>This Host shortcut points to the shared ' + esc(vv.centralReference.label) + '.</p>' +
        '<p><a class="vv-central-reference" href="' + esc(vv.centralReference.route) + '">Open the ' +
          esc(vv.centralReference.label) + '</a></p>' +
        '<p><b>Reference check:</b> ' + (vv.currentStatus === 'PASS' ? 'The shortcut and destination match.' : esc(readableStatus(vv.currentStatus))) +
          ' This does not prove command execution.</p><p>' + readingEvidenceLinks(vv.currentEvidence, 'Read the reference check', vv.supportId) + '</p></section>';
      html += ' · central-reference support · current ' + esc(vv.currentStatus) + '</summary>' +
        checkedContentHtml(vv) +
        '<div class="vv-help"><b>This route is a support layer, not a separate Host workflow.</b> ' +
        'Its retained PASS establishes the wrapper/import/central-destination contract only. ' +
        '<a href="' + esc(vv.centralReference.route) + '">Open the ' + esc(vv.centralReference.label) + '</a>.</div>' +
        '<div class="vv-meta"><b>Workflow:</b> false<br><b>Classification:</b> <code>' +
          esc(vv.classification) + '</code><br><b>Support contract:</b> <code>' + esc(vv.supportId) +
          '</code><br><b>Wrapper → fragment → canonical file:</b> <code>' +
          esc(vv.repositoryFiles.wrapper) + '</code> → <code>' + esc(vv.repositoryFiles.fragment) +
          '</code> → <code>' + esc(vv.repositoryFiles.centralReference) +
          '</code><br><b>Claim limit:</b> ' + esc(vv.claimLimit) +
          '<br><b>Evidence role:</b> <code>' + esc(vv.evidenceRole) + '</code>' +
          '<br><b>Evidence limitations:</b> ' + esc(vv.evidenceLimitations) +
          '<br><b>Retained evidence:</b> ' + retainedEvidenceHtml(vv.currentEvidence, vv.currentEvidenceIds) +
        '</div></details>';
      return supportReading + html;
    }
    function currentEvidenceHtml(row) {
      if (!row.currentEvidenceIds || !row.currentEvidenceIds.length) return '';
      if (isAccountingStatus(row)) {
        return '<details class="vv-accounting"><summary>Accounting/status derivation only — not command proof</summary>' +
          '<div class="vv-meta"><b>Status record:</b> ' +
          retainedEvidenceHtml(row.currentEvidence, row.currentEvidenceIds) + '<br>' +
          '<b>Status basis:</b> ' + esc(row.currentMethod) + '<br><b>Recorded outcome:</b> ' +
          esc(row.currentObservation) + '<br><b>Limitations:</b> ' + esc(row.currentLimitations) +
          (row.currentRationale ? '<br><b>Current rationale:</b> ' + esc(row.currentRationale) : '') +
          '<br>This record explains how the current status was calculated. It does not show that a command executed or worked.</div></details>';
      }
      return '<div class="vv-meta"><b>Current supporting evidence</b> ' +
        retainedEvidenceHtml(row.currentEvidence, row.currentEvidenceIds) + '<br>' +
        '<b>Status basis:</b> ' + esc(row.currentMethod) + '<br><b>Recorded outcome:</b> ' + esc(row.currentObservation) +
        '<br><b>Limitations:</b> ' + esc(row.currentLimitations) +
        (row.currentRationale ? '<br><b>Current rationale:</b> ' + esc(row.currentRationale) : '') + '</div>';
    }
    function historyHtml(row) {
      if (!row.history || !row.history.length) return '';
      return '<details class="vv-history"><summary>Attempt history (' + row.history.length + ')</summary><ul class="vv-evidence">' +
        row.history.map(function (item) {
          return '<li><b>' + esc(item.status) + '</b> via <code>' + esc(item.attemptId) + '</code> · ' +
            retainedEvidenceHtml(item.evidence, item.evidenceIds) +
            (item.supersededBy ? ' · superseded by <code>' + esc(item.supersededBy) + '</code>' : '') +
            (item.accountingCorrectedBy ? ' · accounting corrected by <code>' +
              esc(item.accountingCorrectedBy) + '</code>' : '') +
            (item.qualificationEvidence && item.qualificationEvidence.length
              ? '<br><b>Qualification/disqualification record:</b> ' +
                retainedEvidenceHtml(item.qualificationEvidence, ['qualification-record']) : '') +
            '<br><b>Status basis:</b> ' + esc(item.method) + '<br><b>Recorded outcome:</b> ' + esc(item.observation) +
            '<br><b>Limitations:</b> ' + esc(item.limitations) + '</li>';
        }).join('') + '</ul></details>';
    }
    function withdrawnHistoryHtml(records) {
      if (!records || !records.length) return '';
      return '<details class="vv-history"><summary>' + countLabel(records.length,
        'withdrawn/disqualified historical command assessment') + '</summary><ul class="vv-evidence">' +
        records.map(function (item) {
          return '<li><code>' + esc(item.commandId) + '</code>' + (item.retired ? ' · retired carrier' : '') +
            '<br><b>Original withdrawn assessment:</b> ' + esc(item.originalExecutionStatus) +
              ' · score ' + esc(item.originalScore) + '/3' +
            '<br><b>Reason withdrawn:</b> ' + esc(item.reason) +
            '<br><b>Current reassessment:</b> ' + esc(item.currentReassessment) +
            '<br><b>Current disposition:</b> ' + esc(item.currentExecutionStatus) +
              ' · ' + (item.currentScore == null ? 'unscored' : 'score ' + esc(item.currentScore) + '/3') +
            '<br><b>Qualification evidence:</b> ' +
              retainedEvidenceHtml(item.qualificationEvidence, ['qualification-record']) +
            '<br>This history is preserved for audit; the withdrawn assessment is not current semantic proof.</li>';
        }).join('') + '</ul></details>';
    }
    function directEvidenceHtml(score) {
      if (!score.directEvidence || !score.directEvidence.length) return 'none linked';
      return '<details class="vv-history"><summary>' + countLabel(score.directEvidence.length, 'direct evidence record') +
        '</summary><ul class="vv-evidence">' + score.directEvidence.map(function (item) {
          return '<li><b>' + esc(item.status) + '</b> · <code>' + esc(item.id) + '</code> via <code>' +
            esc(item.attemptId) + '</code><br><b>Proof role:</b> <code>' + esc(item.proofRole) +
            '</code><br><b>Method:</b> ' + esc(item.method) +
            '<br><b>Recorded outcome:</b> ' + esc(item.observation) +
            (item.equivalenceNote ? '<br><b>Equivalence:</b> ' + esc(item.equivalenceNote) : '') +
            (item.limitations ? '<br><b>Limitations:</b> ' + esc(item.limitations) : '') +
            '<br><a class="vv-evidence-link" href="/__review__/evidence?ref=' + encodeURIComponent(item.evidenceRef) +
            (item.binding ? '&binding=' + encodeURIComponent(item.binding) : '') +
            '" target="_blank" rel="noopener noreferrer">Open retained evidence</a> · <code>' +
            esc(item.evidenceRef) + '</code></li>';
        }).join('') + '</ul></details>';
    }
    function commandRuntimeStatus(command) {
      var contract = command.verificationContract || {};
      var runtimeRequired = (contract.requiredEvidenceTypes || []).indexOf('RUNTIME_OR_UI_OBSERVATION') >= 0;
      if (runtimeRequired && ['DIRECT_OBSERVATION', 'CONFIRMED_DEFECT', 'UNAVAILABLE_PREREQUISITE']
        .indexOf(contract.basisKind) >= 0) return command.currentStatus || 'UNVALIDATED';
      if (command.currentStatus === 'NOT_APPLICABLE') return 'NOT_APPLICABLE';
      return 'UNVALIDATED';
    }
    function commandProofHtml(vvRow) {
      var commands = (vvRow.testSets || []).flatMap(function (set) {
        return set.branches.flatMap(function (branch) {
          return branch.steps.flatMap(function (step) { return step.commands; });
        });
      }).filter(function (command) { return command.treatment !== 'NON_EXECUTABLE_DISPLAY'; });
      if (!commands.length) return '';
      var cards = commands.map(function (command) {
        var signature = command.sourceSignature;
        var runtimeStatus = commandRuntimeStatus(command);
        var accountingOnly = isAccountingStatus(command);
        var runtimeEvidence = !accountingOnly && command.currentEvidenceIds && command.currentEvidenceIds.length
          ? retainedEvidenceHtml(command.currentEvidence, command.currentEvidenceIds) : 'none bound';
        var sourceLane;
        if (signature) {
          var sourceLink = signature.handlerSource
            ? '<a href="' + esc(signature.handlerSource.href) +
              '" target="_blank" rel="noopener noreferrer">open pinned handler source ' +
              esc(signature.handlerSource.path) + ':' + esc(signature.handlerSource.lineStart) + '-' +
              esc(signature.handlerSource.lineEnd) + '</a>' : 'canonical handler source not bound';
          sourceLane = '<div class="vv-proof-lane"><b>Source/signature support: <code>' +
            esc(signature.status) + '</code></b><br>' + esc(signature.detail) + '<br>' + sourceLink +
            ' · <a href="' + esc(signature.recordHref) +
            '" target="_blank" rel="noopener noreferrer">open exact static-check record</a>' +
            '<br><b>Pinned source revision:</b> <code>' + esc(signature.sourceRevision) + '</code>' +
            '<br><b>Limit:</b> ' + esc(signature.claimLimit) + '</div>';
        } else {
          sourceLane = '<div class="vv-proof-lane"><b>Source/signature support: <code>UNVALIDATED</code></b>' +
            '<br>No canonical implementation-source or generated CLI-signature binding is attached to this exact command. ' +
            'Runtime evidence, if present below, does not fill that source lane.</div>';
        }
        var runtimeObservation = runtimeStatus === 'UNVALIDATED' && accountingOnly
          ? 'No representative runtime result is bound to this exact command. The available reconciliation/rebase record is status accounting only.'
          : (command.currentObservation || 'No representative runtime result is bound to this exact command.');
        var prerequisite = command.verificationContract && command.verificationContract.unavailablePrerequisite;
        var runtimeLane = '<div class="vv-proof-lane runtime"><b>Runtime behavior: <code>' +
          esc(runtimeStatus) + '</code></b><br>' + esc(runtimeObservation) +
          '<br><b>Runtime evidence:</b> ' + runtimeEvidence +
          (command.currentLimitations ? '<br><b>Limitations:</b> ' + esc(command.currentLimitations) : '') +
          (prerequisite ? '<br><b>Unavailable prerequisite:</b> ' + esc(prerequisite.description) : '') +
          (command.withdrawnRecords && command.withdrawnRecords.length
            ? '<br><b>Historical result warning:</b> ' + countLabel(command.withdrawnRecords.length,
              'prior assessment') + ' withdrawn or disqualified; expand the detailed command record below.' : '') +
          '</div>';
        var nextAction = command.verificationContract && command.verificationContract.nextAction;
        var requiredEvidenceTypes = command.verificationContract &&
          command.verificationContract.requiredEvidenceTypes || [];
        var recordedActionCoversRuntime = Boolean(nextAction &&
          requiredEvidenceTypes.indexOf('RUNTIME_OR_UI_OBSERVATION') >= 0);
        var sourceActionCovered = Boolean(signature && signature.status === 'PASS' && nextAction &&
          /REPOSITORY_STATIC_CHECK|CANONICAL_IMPLEMENTATION_SOURCE/.test(nextAction));
        var runtimeNextAction = recordedActionCoversRuntime ? '' : runtimeStatus === 'UNVALIDATED'
          ? 'To prove that the command works at runtime, run it only in an authorized representative environment and retain the exact CLI/source revision, inputs, terminal result, environment identity, timestamps, and cleanup result.'
          : runtimeStatus === 'BLOCKED'
            ? 'Resolve the named unavailable prerequisite above, then retain the same representative runtime and cleanup evidence; the source PASS does not bypass that gate.'
            : runtimeStatus === 'FAIL'
              ? 'Correct the observed defect, preserve this failed result, and retain a representative retest without weakening the expected result.'
              : '';
        var statusLane = '<div class="vv-proof-lane status"><b>Why the command is currently <code>' +
          esc(command.currentStatus || 'UNVALIDATED') + '</code>:</b> ' +
          esc(command.currentRationale || 'No current rationale is recorded.') +
          (nextAction ? '<br><b>' + (recordedActionCoversRuntime
            ? 'Exact next action' : 'Recorded status-register next action') +
            (sourceActionCovered ? ' (source portion is now shown as PASS above)' : '') + ':</b> ' +
            esc(nextAction) : '') +
          (runtimeNextAction ? '<br><b>Runtime-proof next action:</b> ' + esc(runtimeNextAction) : '') + '</div>';
        var commandTitle = signature && signature.handlerSource
          ? '<a class="vv-command-source" href="' + esc(signature.handlerSource.href) +
            '" target="_blank" rel="noopener noreferrer" title="Open the pinned canonical CLI registration"><code>' +
            esc(command.text) + '</code></a>'
          : '<code>' + esc(command.text) + '</code>';
        return '<div class="vv-command-proof-card" id="vv-command-proof-' + esc(command.id) + '">' +
          commandTitle +
          '<div class="vv-meta"><b>Current exact-command status:</b> <code>' +
          esc(command.currentStatus || 'UNVALIDATED') + '</code> · <code>' + esc(command.id) + '</code>' +
          '<br><b>Documentation source:</b> <code>' + esc(command.sourceLocation.file) + ':' +
          esc(command.sourceLocation.lineStart) + '-' + esc(command.sourceLocation.lineEnd) + '</code></div>' +
          checkedContentHtml(command) + sourceLane + runtimeLane + statusLane + '</div>';
      }).join('');
      return '<details class="vv-command-proof-list" open><summary>Exact command proof (' +
        commands.length + ')</summary><div class="vv-help"><b>Read each command in two lanes.</b> ' +
        'Source/signature support proves that syntax is present in pinned code; it never proves execution. ' +
        'Runtime behavior requires a retained result from the stated environment. Compare its recorded revision and environment with the pinned source revision; the two lanes may describe different builds and must not be merged into one claim. ' +
        'Parent step, branch, set, and page statuses also include prose and other required children, so they may remain UNVALIDATED or BLOCKED when one command is PASS.</div>' +
        cards + '</details>';
    }
    function checkSummary(totals) {
      var parts = [countLabel(totals.steps, 'check')];
      if (totals.nonCommandSteps) parts.push(countLabel(totals.nonCommandSteps, 'non-command check'));
      if (totals.executableIntentCommands) parts.push(countLabel(totals.executableIntentCommands, 'executable command target'));
      if (totals.displayOnlyCommands) parts.push(countLabel(totals.displayOnlyCommands, 'display-only command reference'));
      parts.push(countLabel(totals.retainedEvidenceRecords, 'retained evidence record'));
      if (totals.scored) {
        var scoreParts = [countLabel(totals.scored, 'numeric semantic score')];
        if (totals.executableIntentScored) scoreParts.push(countLabel(totals.executableIntentScored, 'executable-intent score'));
        if (totals.displayOnlyScored) scoreParts.push(countLabel(totals.displayOnlyScored, 'display-only semantic score'));
        parts.push(scoreParts.join(' · '));
      }
      if (totals.notApplicableAssessments) parts.push(totals.notApplicableAssessments + ' approved display-only N/A');
      return parts.join(' · ');
    }
    function stepType(step) {
      if (!step.commands.length) {
        if (step.executionClassification === 'MANUAL_ACTION_NO_COMMAND_CARRIER') return 'manual action check';
        if (step.executionClassification === 'MANUAL_OR_CONTEXT') return 'manual/context check';
        return 'non-command check';
      }
      var treatments = step.commands.map(function (command) { return command.treatment; });
      var displayOnly = treatments.every(function (treatment) { return treatment === 'NON_EXECUTABLE_DISPLAY'; });
      var sourceDefect = treatments.every(function (treatment) { return treatment === 'SOURCE_DEFECT_BLOCKED'; });
      if (displayOnly) return step.executionClassification === 'NON_EXECUTABLE_DISPLAY_OR_DELEGATION'
        ? 'display/delegation command-reference check' : 'command-reference check';
      if (sourceDefect) return 'source-defect command check';
      if (treatments.some(function (treatment) { return treatment === 'NON_EXECUTABLE_DISPLAY'; })) return 'mixed executable command and command-reference check';
      if (treatments.some(function (treatment) { return treatment === 'SOURCE_DEFECT_BLOCKED'; })) return 'mixed executable and source-defect command check';
      return 'executable command check';
    }
    // Reader view is the entry point. Preserve the complete technical view underneath.
    var readerHtml = readingClaimsHtml(vv.materialClaims);
    html = '<details class="vv-context vv-technical"><summary>Technical V&amp;V details and history';
    html += ' <span class="vv-meta">' + countLabel(vv.totals.testSets, 'set') + ' · ' + checkSummary(vv.totals) + '</span></summary>';
    html += checkedContentHtml(vv) + '<div class="vv-help"><b>How to read this V&amp;V:</b> Declared-scope links open the page or section each record says it evaluates. A scope link is not evidence; retained-evidence links open the supporting proof or status record. The retained-evidence total counts records, not independently proved claims. <code>BLOCKED</code> means required verification could not be completed; it is not a page-load result.</div>';
    html += commandProofHtml(vv);
    if (vv.materialDisposition) {
      var materialCounts = Object.keys(vv.materialDisposition.counts || {}).map(function (status) {
        return '<code>' + esc(status) + '=' + esc(vv.materialDisposition.counts[status]) + '</code>';
      }).join(' · ');
      html += '<div class="vv-blocker-help"><b>Material-claim page disposition: ' +
        esc(vv.materialDisposition.status) + '</b><br>' + materialCounts +
        '<br><b>Basis:</b> ' + esc(vv.materialDisposition.rationale) +
        (vv.materialDisposition.nextAction ? '<br><b>Exact next action:</b> ' +
          esc(vv.materialDisposition.nextAction) : '') +
        '<br>This semantic claim rollup is separate from the procedure status below.</div>';
    }
    if (vv.currentStatus === 'BLOCKED') {
      html += '<div class="vv-blocker-help"><b>Procedure V&amp;V blocker</b>' +
        '<div><b>Recorded unavailable prerequisite:</b> ' + classificationLabels(vv.blockerDetails) + '</div>' +
        '<div><b>What this docs review can address:</b> wording, scope, links, and citations to authoritative sources available in this workspace. Fixing those items still requires a new retained check; it does not turn the existing record into PASS.</div>' +
        '<div><b>Reviewer handoff:</b> If canonical implementation sources are unavailable here, a runtime/UI check needs an authorized environment, or a Product/Finance/Legal decision is required, name that dependency and owner and leave the affected check BLOCKED.</div>' +
        '<details class="vv-evidence-guide" open><summary>Evidence source guide</summary><ol>' +
          '<li><b>Implementation/source:</b> canonical Vast source code, API schemas or configuration, generated references, or formulas. Inspect it here when available; otherwise hand off to Engineering or the source owner.</li>' +
          '<li><b>Runtime/UI:</b> retained execution or UI evidence from the required target. This needs an authorized account, host, environment, or operator.</li>' +
          '<li><b>Product/Finance/Legal authority:</b> an authoritative policy, contract, product source, or owner confirmation; code alone may not be authoritative and is insufficient without that source.</li>' +
          '<li><b>Documentation/citation:</b> the documentation text is the claim under review, not proof of itself. Correct the text and link or cite its authoritative source.</li>' +
        '</ol></details>' +
        '<div><b>Status rule:</b> missing evidence alone is <code>UNVALIDATED</code>, not <code>BLOCKED</code>. Use <code>BLOCKED</code> only when a concrete prerequisite is unavailable and named. A checked documentation claim that is wrong or lacks a required citation may instead be <code>FAIL</code>.</div>' +
        '<div>Until the recorded blocker is resolved with suitable retained evidence, the procedure check—and any completion gate that requires it—remains blocked. Drafting and rendering can continue.</div></div>';
    }
    if (!vv.totals.commands) {
      html += '<div class="vv-help"><b>This page contains no executable command instructions.</b> ' +
        'These V&amp;V checks cover narrative, navigation, source, or operational-context claims. Command scoring does not apply. Without retained evidence a check remains <code>UNVALIDATED</code>; it is <code>BLOCKED</code> only when a concrete prerequisite is unavailable and named.</div>';
    } else if (!vv.totals.executableIntentCommands) {
      html += '<div class="vv-help"><b>This page contains no executable command instructions.</b> Its command names are non-runnable display-only references, not a workflow to run. ' +
        'Their numeric semantic scores assess documentation support and relevance only; they do not claim command execution. Approved display-only N/A records are intentionally unscored. Procedure status remains separate: lacking evidence is <code>UNVALIDATED</code>, while <code>BLOCKED</code> requires a named unavailable prerequisite.</div>';
    } else {
      html += '<div class="vv-help"><b>Procedure status is separate from command scoring.</b> Current status is derived from its retained status basis. Nested topology status is an integrity-checked mirror of that projection, not a separate historical result. Historical attempts remain in the status history. A set remains <code>UNVALIDATED</code> until every required branch and step is covered. ' +
        'For executable-intent targets, score 1 = failed or gave no relevant support; 2 = partial or inconclusive execution/semantic support; 3 = current PASS with an explicit exact-full or equivalent-full functional proof binding. Partial functional and bounded static evidence cannot qualify score 3. Display-only references can instead carry a numeric semantic documentation score, which never claims execution, or an approved N/A assessment.</div>';
    }
    if (vv.currentStatus) html += '<div class="vv-meta">Page procedure V&amp;V status: ' + esc(vv.currentStatus) +
      ' (' + (isAccountingStatus(vv) ? 'derived from ' : 'supported by ') + esc(vv.currentStatusAttemptId) +
      '). This covers procedure execution and required children only; it is not overall page acceptance. ' +
      'Topology status mirror: ' + esc(vv.executionStatus) + '.</div>' +
      verificationContractHtml(vv) + currentEvidenceHtml(vv);
    html += historyHtml(vv);
    html += materialClaimsHtml(vv.materialClaims);
    html += retiredMaterialClaimsHtml(vv.retiredMaterialClaims);
    html += withdrawnHistoryHtml(vv.retiredCommandWithdrawals);
    vv.testSets.forEach(function (set) {
      var scoreParts = (set.totals.scoreCounts || []).map(function (count, index) {
        return count ? count + '×' + (index + 1) : '';
      }).filter(Boolean).reverse();
      var scoreBreakdown = scoreParts.length ? ' · score distribution ' + scoreParts.join(' · ') : '';
      html += '<details class="vv-set"><summary><span>' + esc(set.title) + currentStatusSuffix(set) +
        ' · topology mirror ' + esc(set.executionStatus) + '</span>' +
        '<span class="vv-set-meta">' + checkSummary(set.totals) + scoreBreakdown + '</span></summary>';
      html += '<div class="vv-meta"><b>Goal:</b> ' + esc(set.goal) +
        '<br><b>Evidence access/authority needed:</b> ' + esc((set.accessClasses || []).join('; ') || 'not recorded') +
        '<br><b>Safety constraints:</b> ' + esc((set.safetyConstraints || []).join('; ') || 'not recorded') +
        '<br><b>Limitations:</b> ' + esc((set.limitations || []).join('; ') || 'not recorded') + '</div>' +
        setBlockerHtml(set) + checkedContentHtml(set) + verificationContractHtml(set) +
        currentEvidenceHtml(set) + historyHtml(set);
      set.branches.forEach(function (branch) {
        html += '<div class="vv-branch"><b>' + esc(branch.id) + '</b>' + currentStatusSuffix(branch) + ' · topology mirror ' + esc(branch.executionStatus) + '<br>' + esc(branch.condition) + checkedContentHtml(branch) + verificationContractHtml(branch) + currentEvidenceHtml(branch) + historyHtml(branch) + '<ol>';
        branch.steps.forEach(function (step) {
          html += '<li class="vv-step"><b>' + esc(step.id) + '</b> · ' + stepType(step) + currentStatusSuffix(step) + ' · topology mirror ' + esc(step.executionStatus) + '<br>' + esc(step.instruction) + checkedContentHtml(step) + verificationContractHtml(step) + currentEvidenceHtml(step) + historyHtml(step);
          step.commands.forEach(function (command) {
            var commandType = command.treatment === 'NON_EXECUTABLE_DISPLAY' ? 'display-only command reference' :
              command.treatment === 'SOURCE_DEFECT_BLOCKED' ? 'source-defect command target' : 'executable command target';
            html += '<div class="vv-command"><code>' + esc(command.text) + '</code><div class="vv-meta">' + esc(command.id) + ' · ' + commandType + currentStatusSuffix(command) + ' · topology mirror ' + esc(command.executionStatus) + '</div>' + checkedContentHtml(command) + verificationContractHtml(command) + currentEvidenceHtml(command) + historyHtml(command);
            html += withdrawnHistoryHtml(command.withdrawnRecords);
            if (command.evidence.length) html += '<ul class="vv-evidence">' + command.evidence.map(function (row) {
              return '<li><b>' + esc(row.executionStatus) + '</b>' +
                (row.attemptId ? ' via <code>' + esc(row.attemptId) + '</code>' : ' · unscoped historical result') +
                (row.supersededBy ? ' · superseded by <code>' + esc(row.supersededBy) + '</code>' : '') +
                (row.accountingCorrectedBy ? ' · accounting corrected by <code>' +
                  esc(row.accountingCorrectedBy) + '</code>' : '') +
                '<br><b>Retained result:</b> ' +
                  retainedEvidenceHtml([{ id: row.ref, evidenceRef: row.evidenceRef,
                    binding: row.binding }], [row.ref]) +
                (row.method ? '<br><b>Method:</b> ' + esc(row.method) : '') +
                '<br><b>Recorded outcome:</b> ' + esc(row.observation) +
                '<br><b>Limitations:</b> ' + esc(row.limitations) +
                (row.qualificationEvidence && row.qualificationEvidence.length
                  ? '<br><b>Qualification/disqualification record:</b> ' +
                    retainedEvidenceHtml(row.qualificationEvidence, ['qualification-record']) : '') + '</li>';
            }).join('') + '</ul>';
            if (command.score) html += '<div class="vv-score">' +
              (command.treatment === 'NON_EXECUTABLE_DISPLAY' ? 'Semantic documentation score ' : 'Score ') +
              command.score.value + '/3 · ' +
              (command.treatment === 'NON_EXECUTABLE_DISPLAY' ? 'documentation-support basis ' : 'execution basis ') +
              esc(command.score.executionStatus) + ' · ' + esc(command.score.rationale) +
              '<br><b>Semantic assessment evidence:</b> ' +
              retainedEvidenceHtml(command.score.evidence, command.score.evidenceIds) +
              '<br><b>Direct functional/static evidence:</b> ' + directEvidenceHtml(command.score) + '</div>';
            if (command.notApplicableAssessment) html += '<div class="vv-score">Semantic assessment: NOT_APPLICABLE · ' +
              esc(command.notApplicableAssessment.rationale) + ' · approval <code>' +
              esc(command.notApplicableAssessment.approvalRef) + '</code> · evidence ' +
              retainedEvidenceHtml(command.notApplicableAssessment.evidence,
                command.notApplicableAssessment.evidenceIds) + '</div>';
            html += '</div>';
          });
          html += '</li>';
        });
        html += '</ol></div>';
      });
      html += '</details>';
    });
    return readerHtml + html + '</details>';
  }
  function renderPageContext() {
    var box = $('jiraContext');
    var epics = pageContext && Array.isArray(pageContext.epics) ? pageContext.epics : [];
    var issues = pageContext && Array.isArray(pageContext.issues) ? pageContext.issues : [];
    var blockers = pageContext && Array.isArray(pageContext.blockers) ? pageContext.blockers : [];
    var verification = pageContext && pageContext.verification ? pageContext.verification : { available: false };
    var count = $('jiraCount');
    count.hidden = blockers.length === 0;
    count.textContent = blockers.length ? '\u26A0 ' + blockers.length : '';
    var hostPageWithUnavailableVv = location.pathname.startsWith('/host/') && !verification.available;
    if (!epics.length && !issues.length && !blockers.length && !verification.available && !hostPageWithUnavailableVv) {
      box.hidden = true;
      box.innerHTML = '';
      return;
    }
    var html = verificationHtml(verification);
    html += '<details class="vv-history"><summary>Jira context for this page</summary><div class="jira-title"><span><a href="/review-questions">review inputs</a> &middot; <a href="${TRACEABILITY_URL}" target="_blank" rel="noopener noreferrer">traceability</a></span></div>';
    html += '<div class="jira-links">';
    epics.forEach(function (issue) { html += jiraLinkHtml(issue, true); });
    issues.forEach(function (issue) { html += jiraLinkHtml(issue, false); });
    html += '</div>';
    if (blockers.length) {
      html += '<details class="jira-blockers" open><summary>' + blockers.length +
        ' unresolved reviewer input' + (blockers.length === 1 ? '' : 's') + '</summary><ul>';
      blockers.forEach(function (blocker) {
        html += '<li>' + esc(blocker.question || 'Review input needed.');
        if (blocker.issue && blocker.issue.url) {
          html += ' <a href="' + esc(blocker.issue.url) + '" target="_blank" rel="noopener noreferrer">' +
            esc(blocker.issue.key) + '</a>';
        }
        if (blocker.owner) html += '<span class="jira-owner">Owner: ' + esc(blocker.owner) + '</span>';
        html += '</li>';
      });
      html += '</ul></details>';
    } else {
      html += '<div class="jira-clear">No page-specific blocker is recorded; use the linked Jira source for scope.</div>';
    }
    html += '</details>';
    box.innerHTML = html;
    box.hidden = false;
  }
  $('jiraContext').addEventListener('change', function (event) {
    if (event.target.id !== 'vv-section-filter') return;
    claimSectionFilter = event.target.value;
    clearClaimFocus();
    shadow.querySelectorAll('[data-review-section]').forEach(function (card) {
      var sections = JSON.parse(card.getAttribute('data-review-sections'));
      card.hidden = !!claimSectionFilter && sections.indexOf(claimSectionFilter) === -1;
    });
    if ($('vv-location-notice')) $('vv-location-notice').textContent = '';
  });
  $('jiraContext').addEventListener('click', function (event) {
    var button = event.target.closest('[data-show-claim]');
    if (!button) return;
    var claims = pageContext && pageContext.verification && pageContext.verification.materialClaims || [];
    var row = claims.find(function (claim) { return claim.id === button.getAttribute('data-show-claim'); });
    if (row) showReviewWording(row, button);
  });
  function loadPageContext() {
    var requestedPath = location.pathname;
    var requestId = ++contextRequest;
    fetch(API + '/context?path=' + encodeURIComponent(requestedPath))
      .then(function (r) { if (!r.ok) throw new Error('context request failed'); return r.json(); })
      .then(function (data) {
        if (requestId !== contextRequest || requestedPath !== location.pathname) return;
        pageContext = data || { epics: [], issues: [], blockers: [] };
        renderPageContext();
      })
      .catch(function () {
        if (requestId !== contextRequest) return;
        pageContext = { epics: [], issues: [], blockers: [] };
        renderPageContext();
      });
  }
  function cardHtml(it) {
    var eid = esc(it.id); // ids can arrive from shared feedback files — never trust them in markup
    var found = !!anchoredRanges[it.id];
    var sev = '<span class="chip" style="background:' + (SEV_COLOR[it.severity] || '#5c677d') + '">' + esc(it.severity) + '</span>';
    var cat = '<span class="chip cat">' + esc(it.category) + '</span>';
    var orphan = (it.type === 'inline' && !found && it.page === location.pathname)
      ? '<span class="chip orphan" title="The quoted text was not found on this page">not found</span>' : '';
    var quote = it.quote ? '<blockquote>' + esc(it.quote) + '</blockquote>' : '';
    var headline = it.heading ? '<div class="byline">&sect; ' + esc(it.heading) + '</div>' : '';
    var goBtn = (it.page === location.pathname && found) ? '<button data-act="go" data-id="' + eid + '">Go to</button>' : '';
    var openBtn = (it.page !== location.pathname) ? '<button data-act="open" data-id="' + eid + '">Open page</button>' : '';
    var mutationButtons = canMutateItem(it)
      ? '<button data-act="edit" data-id="' + eid + '">Edit</button>' +
        '<button data-act="resolve" data-id="' + eid + '">' + (it.status === 'resolved' ? 'Reopen' : 'Resolve') + '</button>' +
        '<button data-act="delete" data-id="' + eid + '" class="danger">Delete</button>'
      : '<span class="byline" title="Switch back to this reviewer identity to change the item">Read-only for this reviewer</span>';
    return '<div class="card ' + (it.status === 'resolved' ? 'resolved' : '') + '" data-card="' + eid + '">' +
      '<div class="chips">' + sev + cat + orphan + '</div>' +
      quote + headline +
      '<div class="comment">' + esc(it.comment) + '</div>' +
      '<div class="byline">' + esc(it.reviewer) + ' &middot; ' + esc(String(it.createdAt || '').slice(0, 16).replace('T', ' ')) + '</div>' +
      '<div class="acts">' + goBtn + openBtn + mutationButtons +
      '</div></div>';
  }
  function renderList() {
    var listEl = $('list');
    var data = showAllPages ? visibleItems() : pageItems();
    if (!data.length) {
      listEl.innerHTML = '<div class="empty">No feedback ' + (showAllPages ? 'yet' : 'on this page yet') +
        '.<br><br>Select any text on the page and click<br><b>&#128172; Comment on selection</b>,<br>or add a page-level note above.</div>';
      return;
    }
    var html = '';
    if (showAllPages) {
      var byPage = Object.create(null);
      data.forEach(function (it) { (byPage[it.page] = byPage[it.page] || []).push(it); });
      Object.keys(byPage).sort().forEach(function (pg) {
        html += '<div class="pagegroup">' + esc(pg) + '</div>';
        byPage[pg].forEach(function (it) { html += cardHtml(it); });
      });
    } else {
      data.forEach(function (it) { html += cardHtml(it); });
    }
    listEl.innerHTML = html;
  }
  function renderWho() { $('who').textContent = reviewer || '—'; }
  function renderAll() { renderBadge(); renderList(); renderWho(); renderSaveStatus(); renderSelectionDraft(); renderPageContext(); }

  function openPanel() {
    panelReturnFocus = rememberFocus(pill);
    panel.classList.add('open');
    panel.setAttribute('aria-hidden', 'false');
    pill.setAttribute('aria-expanded', 'true');
    hideSelBtn();
    renderAll();
    $('closePanel').focus();
  }
  function closePanel() {
    if (!panel.classList.contains('open')) return;
    panel.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
    pill.setAttribute('aria-expanded', 'false');
    var returnFocus = panelReturnFocus;
    panelReturnFocus = null;
    if (returnFocus && returnFocus.isConnected && returnFocus.focus) returnFocus.focus();
    else pill.focus();
  }
  function openComposer(title, quote) {
    if (!reviewer) { pendingAfterName = function () { openComposer(title, quote); }; openNameModal(); return; }
    composerReturnFocus = rememberFocus(panel.classList.contains('open') ? $('addPageNote') : pill);
    composerCtx = { page: location.pathname, pageTitle: pageTitle() };
    $('composerTitle').textContent = title;
    var q = $('composerQuote');
    if (quote) { q.textContent = quote; q.style.display = 'block'; } else { q.style.display = 'none'; }
    composer.classList.add('open');
    composer.setAttribute('aria-hidden', 'false');
    overlaybg.classList.add('open');
    setModalIsolation(true);
    $('fComment').focus();
  }
  function closeComposer() {
    if (!composer.classList.contains('open')) return;
    composer.classList.remove('open');
    composer.setAttribute('aria-hidden', 'true');
    if (!nameModal.classList.contains('open')) overlaybg.classList.remove('open');
    setModalIsolation(false);
    $('fComment').value = '';
    pending = null;
    editingId = null;
    var returnFocus = composerReturnFocus;
    composerReturnFocus = null;
    if (returnFocus && returnFocus.isConnected && returnFocus.focus) returnFocus.focus();
    else if (panel.classList.contains('open')) $('closePanel').focus();
    else pill.focus();
  }
  var pendingAfterName = null;
  function openNameModal() {
    nameReturnFocus = rememberFocus(panel.classList.contains('open') ? $('editWho') : pill);
    nameModal.classList.add('open');
    nameModal.setAttribute('aria-hidden', 'false');
    overlaybg.classList.add('open');
    setModalIsolation(true);
    $('fName').value = reviewer;
    $('fName').focus();
  }
  function closeNameModal() {
    if (!nameModal.classList.contains('open')) return;
    nameModal.classList.remove('open');
    nameModal.setAttribute('aria-hidden', 'true');
    if (!composer.classList.contains('open')) overlaybg.classList.remove('open');
    setModalIsolation(false);
    var returnFocus = nameReturnFocus;
    nameReturnFocus = null;
    if (returnFocus && returnFocus.isConnected && returnFocus.focus) returnFocus.focus();
    else if (panel.classList.contains('open')) $('closePanel').focus();
    else pill.focus();
  }

  // ---------------- events ----------------
  pill.addEventListener('click', function () {
    if (panel.classList.contains('open')) closePanel(); else openPanel();
  });
  $('closePanel').addEventListener('click', closePanel);
  $('editWho').addEventListener('click', openNameModal);
  $('saveJson').addEventListener('click', saveJsonBackup);
  $('importJson').addEventListener('click', function () { $('importJsonFile').click(); });
  $('importJsonFile').addEventListener('change', function (e) {
    var file = e.target.files && e.target.files[0];
    importJsonBackup(file);
    e.target.value = '';
  });
  $('allPages').addEventListener('change', function (e) { showAllPages = e.target.checked; renderList(); });
  $('addPageNote').addEventListener('click', function () {
    pending = null; editingId = null;
    openComposer('Page note — ' + location.pathname, '');
  });
  function beginSelectionComment() {
    if (!selectionDraft || !selectionDraft.quote) return;
    pending = selectionDraft;
    hideSelBtn();
    var sel = document.getSelection();
    if (sel) sel.removeAllRanges();
    editingId = null;
    openComposer('Comment on selection', pending ? pending.quote : '');
  }
  selBtn.addEventListener('click', beginSelectionComment);
  $('commentSelection').addEventListener('click', beginSelectionComment);
  $('clearSelection').addEventListener('click', function () {
    var sel = document.getSelection();
    if (sel) sel.removeAllRanges();
    clearSelectionDraft();
  });
  $('composerCancel').addEventListener('click', closeComposer);
  $('composerSave').addEventListener('click', function () {
    var comment = $('fComment').value.trim();
    if (!comment) { $('fComment').focus(); return; }
    saveItem({ category: $('fCategory').value, severity: $('fSeverity').value, comment: comment });
    closeComposer();
  });
  $('nameSave').addEventListener('click', function () {
    var v = $('fName').value.trim();
    if (!v) { $('fName').focus(); return; }
    var previousReviewer = reviewer;
    function finishRename() {
      reviewer = v;
      try { localStorage.setItem(LS_REVIEWER, reviewer); } catch (e) {}
      closeNameModal();
      renderWho();
      mergeServerState();
      if (pendingAfterName) { var f = pendingAfterName; pendingAfterName = null; f(); }
    }
    if (!previousReviewer || previousReviewer === v) { finishRename(); return; }
    if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
    persistLocal();
    pushReviewerState(previousReviewer, false).then(function (saved) {
      if (saved) finishRename();
      else toast('Could not save feedback for ' + previousReviewer + '; reviewer was not changed');
    });
  });
  $('fName').addEventListener('keydown', function (e) { if (e.key === 'Enter') $('nameSave').click(); });
  $('nameCancel').addEventListener('click', function () { pendingAfterName = null; closeNameModal(); });
  overlaybg.addEventListener('click', function () {
    if (composer.classList.contains('open')) closeComposer();
    else if (nameModal.classList.contains('open')) { pendingAfterName = null; closeNameModal(); }
  });
  $('list').addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-act]');
    if (!btn) return;
    var id = btn.getAttribute('data-id');
    var act = btn.getAttribute('data-act');
    var it = items.filter(function (x) { return x.id === id; })[0];
    if (!it) return;
    if (['delete', 'resolve', 'edit'].indexOf(act) !== -1 && !canMutateItem(it)) {
      toast('Switch back to ' + it.reviewer + ' to change this item');
      return;
    }
    if (act === 'delete') { if (confirm('Delete this feedback item?')) deleteItem(id); }
    else if (act === 'resolve') toggleResolve(id);
    else if (act === 'open') {
      // only same-origin paths — pages can arrive from shared feedback files
      if (/^\/([^\/]|$)/.test(String(it.page || ''))) location.href = it.page;
    }
    else if (act === 'go') {
      var r = anchoredRanges[id];
      if (r) {
        var el = r.startContainer.nodeType === 1 ? r.startContainer : r.startContainer.parentElement;
        if (el && el.scrollIntoView) el.scrollIntoView({ block: 'center', behavior: 'smooth' });
        flashRange(r);
      }
    }
    else if (act === 'edit') {
      editingId = id;
      pending = null;
      $('fCategory').value = it.category || CATEGORIES[0];
      $('fSeverity').value = it.severity || 'Minor';
      openComposer('Edit feedback', it.quote || '');
      $('fComment').value = it.comment || '';
    }
  });
  document.addEventListener('keydown', function (e) {
    var modal = nameModal.classList.contains('open') ? nameModal
      : composer.classList.contains('open') ? composer : null;
    if (e.key === 'Tab' && modal) { trapDialogFocus(e, modal); return; }
    if (e.key !== 'Escape') return;
    if (composer.classList.contains('open')) closeComposer();
    else if (nameModal.classList.contains('open')) { pendingAfterName = null; closeNameModal(); }
    else closePanel();
    hideSelBtn();
  });
  document.addEventListener('pointerup', function (e) {
    var path = e.composedPath ? e.composedPath() : [];
    if (path.indexOf(host) !== -1) return;
    setTimeout(onSelectionSettled, 30);
  });
  document.addEventListener('keyup', function (e) {
    if (e.shiftKey || e.key === 'Shift') setTimeout(onSelectionSettled, 30);
  });
  document.addEventListener('selectionchange', function () {
    if (selectionTimer) clearTimeout(selectionTimer);
    selectionTimer = setTimeout(onSelectionSettled, 120);
  });
  // click on a highlight opens the panel scrolled to that card
  document.addEventListener('click', function (e) {
    var path = e.composedPath ? e.composedPath() : [];
    if (path.indexOf(host) !== -1) return;
    var ids = Object.keys(anchoredRanges);
    for (var i = 0; i < ids.length; i++) {
      var rects = anchoredRanges[ids[i]].getClientRects();
      for (var j = 0; j < rects.length; j++) {
        var rc = rects[j];
        if (e.clientX >= rc.left && e.clientX <= rc.right && e.clientY >= rc.top && e.clientY <= rc.bottom) {
          openPanel();
          var card = shadow.querySelector('[data-card="' + CSS.escape(ids[i]) + '"]');
          if (card) { card.scrollIntoView({ block: 'center' }); card.style.outline = '2px solid #4a5cf0'; }
          return;
        }
      }
    }
  }, true);

  // SPA navigation: re-anchor highlights when the route or DOM changes
  function onNavigate() {
    claimSectionFilter = null;
    clearClaimFocus();
    clearSelectionDraft();
    pageContext = { epics: [], issues: [], blockers: [] };
    renderPageContext();
    loadPageContext();
    scheduleAnchor();
    setTimeout(renderAll, 450);
  }
  var origPush = history.pushState;
  history.pushState = function () { origPush.apply(this, arguments); onNavigate(); };
  var origReplace = history.replaceState;
  history.replaceState = function () { origReplace.apply(this, arguments); onNavigate(); };
  window.addEventListener('popstate', onNavigate);
  window.addEventListener('hashchange', function () {
    claimSectionFilter = null;
    clearClaimFocus();
    renderPageContext();
  });
  new MutationObserver(function (muts) {
    for (var i = 0; i < muts.length; i++) {
      if (muts[i].target === host || host.contains(muts[i].target)) continue;
      scheduleAnchor();
      return;
    }
  }).observe(document.body, { childList: true, subtree: true });

  // ---------------- boot ----------------
  renderAll();
  loadPageContext();
  scheduleAnchor();
  if (reviewer) { mergeServerState(); saveStatus = 'saved'; }
  renderSaveStatus();
})();
`;

// ------------------------------------------------------------------ proxy
const INJECT_TAG = '<script src="/__review__/overlay.js" defer></script>';

function injectOverlay(html) {
  const lower = html.toLowerCase();
  let at = lower.lastIndexOf('</body>');
  if (at === -1) at = lower.lastIndexOf('</html>');
  if (at === -1) return html + INJECT_TAG;
  return html.slice(0, at) + INJECT_TAG + html.slice(at);
}

function readBody(req, limitBytes) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on('data', (c) => {
      size += c.length;
      if (size > limitBytes) { reject(new Error('body too large')); req.destroy(); return; }
      chunks.push(c);
    });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function sendJson(res, code, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(code, { 'content-type': 'application/json', 'cache-control': 'no-store' });
  res.end(body);
}

function expectedReviewHost(req) {
  const host = typeof req.headers.host === 'string' ? req.headers.host.toLowerCase() : '';
  return new Set([`127.0.0.1:${PORT}`, `localhost:${PORT}`, `[::1]:${PORT}`]).has(host) ? host : null;
}

function reviewOriginError(req) {
  const host = expectedReviewHost(req);
  if (!host) return 'requests require the expected loopback Host';
  const origin = typeof req.headers.origin === 'string' ? req.headers.origin : null;
  if (origin) {
    let normalizedOrigin = null;
    try { normalizedOrigin = new URL(origin).origin.toLowerCase(); } catch { /* rejected below */ }
    if (normalizedOrigin !== `http://${host}`) return 'cross-origin request rejected';
  }
  if (String(req.headers['sec-fetch-site'] || '').toLowerCase() === 'cross-site') {
    return 'cross-site request rejected';
  }
  return null;
}

function allowReviewMutation(req, res) {
  const originError = reviewOriginError(req);
  if (originError) { sendJson(res, 403, { error: originError }); return false; }
  const contentType = String(req.headers['content-type'] || '').split(';', 1)[0].trim().toLowerCase();
  if (contentType !== 'application/json') {
    sendJson(res, 415, { error: 'review mutations require application/json' });
    return false;
  }
  return true;
}

function evidenceTextForDisplay(bytes) {
  if (bytes.includes(0)) throw new Error('binary V&V evidence cannot be displayed as text');
  let text = bytes.toString('utf8');
  let sanitized = false;
  const replaceSensitive = (pattern, replacement) => {
    text = text.replace(pattern, (...args) => {
      const next = typeof replacement === 'function' ? replacement(...args) : replacement;
      if (next !== args[0]) sanitized = true;
      return next;
    });
  };
  const placeholder = (value) => /^(?:\$\{?[A-Z_][A-Z0-9_]*\}?|<[^>]+>|\[[^\]]+\]|YOUR[_-]|EXAMPLE|DUMMY|TEST|X{3,})/i
    .test(String(value));
  replaceSensitive(/(^|[\s"'(])\.orchestra\/[^\s"'<>]*/gm,
    (value, prefix) => `${prefix}[redacted-agent-metadata]`);
  replaceSensitive(/\/(?:Users|home|root)\/[^\s"'<>]+|\/(?:private\/tmp|tmp|var\/folders)\/[^\s"'<>]+/g, (value) =>
    /\/(?:Users|home|root)\/(?:\$\{?[A-Z_][A-Z0-9_]*\}?|example|your[-_]?user|username)(?:\/|$)/i.test(value)
      || /\/(?:private\/tmp|tmp|var\/folders)\/(?:\$\{?[A-Z_][A-Z0-9_]*\}?|example|placeholder)(?:\/|$)/i.test(value)
      ? value : '[redacted-local-path]');
  replaceSensitive(/[A-Za-z]:\\Users\\[^\s"'<>]+/gi, (value) =>
    /\\Users\\(?:%[A-Z_]+%|\$\{?[A-Z_][A-Z0-9_]*\}?|example|your[-_]?user|username)(?:\\|$)/i.test(value)
      ? value : '[redacted-local-path]');
  replaceSensitive(/\b[A-Z0-9._%+-]+@(?:[A-Z0-9-]+\.)+[A-Z]{2,}\b/gi, (value) =>
    /@example\.(?:com|net|org)$/i.test(value) ? value : '[redacted-email]');
  replaceSensitive(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g, (value) => {
    const octets = value.split('.').map(Number);
    if (octets.some((octet) => octet > 255)) return value;
    const [a, b, c] = octets;
    const safeExample = a === 127 || value === '0.0.0.0' || value === '255.255.255.255' ||
      (a === 192 && b === 0 && c === 2) || (a === 198 && b === 51 && c === 100) ||
      (a === 203 && b === 0 && c === 113);
    return safeExample ? value : '[redacted-address]';
  });
  replaceSensitive(/(?<![A-Za-z0-9])[\[\]A-Fa-f0-9:]{2,}(?![A-Za-z0-9])/g, (value) => {
    const candidate = value.replace(/^\[|\]$/g, '');
    if (net.isIP(candidate) !== 6 || candidate === '::' || candidate === '::1' ||
      /^2001:db8(?::|$)/i.test(candidate)) return value;
    return '[redacted-address]';
  });
  replaceSensitive(/\b((?:authorization|proxy-authorization)\s*:\s*(?:bearer|basic)\s+)([^\s,;]+)/gi,
    (value, prefix, secret) => placeholder(secret) ? value : `${prefix}[redacted]`);
  replaceSensitive(/\b((?:api[-_ ]?key|access[-_ ]?token|secret|password|VAST_API_KEY)\s*[:=]\s*)("[^"]*"|'[^']*'|[^\s,;]+)/gi,
    (value, prefix, secret) => placeholder(secret.replace(/^['"]|['"]$/g, ''))
      ? value : `${prefix}[redacted]`);
  replaceSensitive(/\b(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b/g,
    '[redacted-token]');
  const redactScopedNumericIdentifier = (value, prefix, identifier, suffix = '') => {
    // Keep the explicit example used by generated reference snapshots, while
    // hiding retained machine/account identifiers from the reviewer copy.
    if (identifier === '12345' || /^0+$/.test(identifier)) return value;
    return `${prefix}[redacted-identifier]${suffix}`;
  };
  replaceSensitive(/\b((?:machine|instance|offer|account|user|host)(?:[-_ ]?id)?(?:\s*(?:[:=#]|is))?\s*`?)(\d{4,})(`?)/gi,
    redactScopedNumericIdentifier);
  replaceSensitive(/((?:["']?(?:machine|instance|offer|account|user|host)[_-]id["']?\s*[:=]\s*["']?))(\d{4,})(["']?)/gi,
    redactScopedNumericIdentifier);
  const preface = sanitized
    ? '[Reviewer display copy: restricted local or credential data was redacted.]\n\n' : '';
  return Buffer.from(preface + text, 'utf8');
}

async function handleReviewRoute(req, res, url) {
  const p = url.pathname;
  if (req.method === 'POST' &&
    (p === '/__review__/api/state' || p === '/__review__/api/import') &&
    !allowReviewMutation(req, res)) return;
  if (p === '/__review__/' || p === '/__review__') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' });
    res.end(statusPage());
    return;
  }
  if (p === '/__review__/overlay.js') {
    res.writeHead(200, { 'content-type': 'application/javascript; charset=utf-8', 'cache-control': 'no-store' });
    res.end(OVERLAY_JS);
    return;
  }
  if (p === '/__review__/api/context' && req.method === 'GET') {
    res.setHeader('x-vast-review-source-sha256', REVIEW_SOURCE_SHA256);
    sendJson(res, 200, reviewContextForPath(url.searchParams.get('path') || '/'));
    return;
  }
  if (p === '/__review__/cli-signature' && req.method === 'GET') {
    const findingId = url.searchParams.get('finding') || '';
    const bindingId = url.searchParams.get('binding') || '';
    const signature = VERIFICATION_EVIDENCE.cliSignatureByFindingId.get(findingId);
    const command = VERIFICATION_EVIDENCE.commandById.get(bindingId);
    if (!VERIFICATION_EVIDENCE.available || !signature || !command || signature.commandId !== bindingId ||
      VERIFICATION_EVIDENCE.cliSignatureByCommandId.get(bindingId)?.id !== findingId) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' });
      res.end('Exact CLI signature binding not found.');
      return;
    }
    const status = signature.status === 'pass' ? 'PASS' :
      (['wrong-executable', 'unknown-command', 'unknown-option'].includes(signature.status)
        ? 'FAIL' : 'UNVALIDATED');
    const lines = [
      'Exact command source/signature binding',
      `Page: ${command.route}`,
      `Heading: ${command.sourceContract.section}`,
      `Documentation source: ${command.sourceContract.file}:${command.sourceContract.line_start}-${command.sourceContract.line_end}`,
      `Command: ${command.text}`,
      `Command ID: ${bindingId}`,
      `Static signature result: ${status}`,
      `Finding: ${signature.id}`,
      `Checker method: ${signature.method}`,
      `Checker detail: ${signature.detail}`,
      'CLI source repository: vast-ai/vast-cli',
      `CLI source revision: ${signature.sourceRevision}`,
      `Canonical handler: ${signature.handlerSource.path}:${signature.handlerSource.lineStart}-${signature.handlerSource.lineEnd} (${signature.handlerSource.symbol})`,
      `Canonical source URL: ${signature.handlerSource.href}`,
      `Generated artifact SHA-256: ${VERIFICATION_EVIDENCE.cliSignatureArtifactSha256}`,
      `Proof limit: ${signature.claimLimit}`,
      '',
      'This record proves only that the documented executable, command signature, and options are registered in the pinned CLI source. It is not runtime proof that authentication, API access, rental creation, a diagnostic workload, cleanup, or any Host result succeeded.',
    ].map(vvText).join('\n');
    res.writeHead(200, {
      'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store',
      'x-content-type-options': 'nosniff',
    });
    res.end(evidenceTextForDisplay(Buffer.from(lines, 'utf8')));
    return;
  }
  if (p === '/__review__/evidence' && req.method === 'GET') {
    const ref = url.searchParams.get('ref') || '';
    if (!VERIFICATION_EVIDENCE.available || !VERIFICATION_EVIDENCE.evidenceRefs.has(ref)) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' });
      res.end('Evidence reference not found.');
      return;
    }
    const safeRef = vvEvidenceRef(ref);
    const bindingId = url.searchParams.get('binding');
    let bindingHeader = '';
    let bindingNavigation = null;
    if (bindingId) {
      const claim = VERIFICATION_EVIDENCE.materialClaims.find((item) => item.id === bindingId);
      const support = VERIFICATION_EVIDENCE.supportLayers.find((item) => item.id === bindingId);
      const command = VERIFICATION_EVIDENCE.commandById.get(bindingId);
      const statusTarget = VERIFICATION_EVIDENCE.statusTargetByBinding.get(bindingId);
      if (claim && claim.current.dispositionEvidenceIds.some((id) =>
        VERIFICATION_EVIDENCE.evidenceRefById.get(id) === safeRef)) {
        bindingNavigation = {
          route: claim.checkedContent.route,
          heading: claim.checkedContent.sections[0] || 'Introduction',
        };
        bindingHeader = [
          'Reviewer navigation context (generated; not retained evidence)',
          'Exact material-claim disposition binding',
          `Claim: ${claim.id}`,
          `Page: ${claim.checkedContent.route}`,
          `Heading: ${claim.checkedContent.sections.join(' / ')}`,
          `Disposition: ${claim.current.status}`,
          `Evidence role: ${claim.current.dispositionEvidenceRole}`,
          `Required evidence lanes: ${claim.current.requiredEvidenceTypes.join('; ')}`,
          `Satisfied evidence lanes: ${claim.current.satisfiedEvidenceTypes.join('; ') || 'none'}`,
          `Partially supported evidence lanes: ${claim.current.partiallySupportedEvidenceTypes.join('; ') || 'none'}`,
          `Claim: ${claim.claim.text}`,
          `Limitations: ${claim.current.dispositionLimitations.join('; ')}`,
          '', 'The retained artifact begins below. This generated header is not proof.', '',
        ].map(vvText).join('\n');
      } else if (claim && claim.current.evidenceIds.some((id) =>
        VERIFICATION_EVIDENCE.evidenceRefById.get(id) === safeRef)) {
        bindingNavigation = { route: claim.checkedContent.route,
          heading: claim.checkedContent.sections[0] || 'Introduction' };
        bindingHeader = [
          'Reviewer navigation context (generated; not retained evidence)',
          'Supporting evidence attached to this wording',
          `Page: ${claim.checkedContent.route}`,
          `Heading: ${claim.checkedContent.sections.join(' / ')}`,
          `Wording: ${claim.claim.text}`,
          `Current claim status: ${claim.current.status}`,
          `Tracking ID: ${claim.id}`,
          `Scope and limitations: ${claim.current.limitations.join('; ')}`,
          'An attached result may provide only partial support. The current claim status is unchanged.',
          '', 'The retained artifact begins below. This generated header is not proof.', '',
        ].map(vvText).join('\n');
      } else if (support && support.evidenceIds.some((id) =>
        VERIFICATION_EVIDENCE.evidenceRefById.get(id) === safeRef)) {
        bindingNavigation = { route: support.route, heading: 'Introduction' };
        bindingHeader = [
          'Reviewer navigation context (generated; not retained evidence)',
          'Exact central-reference support-layer binding',
          `Support contract: ${support.id}`,
          `Layer: ${support.layer}`,
          `Wrapper route: ${support.route}`,
          `Central reference: ${support.centralReferenceRoute}`,
          `Evidence role: ${support.evidenceRole}`,
          `Limitations: ${support.evidenceLimitations}`,
          '', 'The retained artifact begins below. This generated header is not proof.', '',
        ].map(vvText).join('\n');
      } else if (command) {
        const current = VERIFICATION_EVIDENCE.currentStatusByTarget.get(vvStatusKey('COMMAND', command));
        const score = VERIFICATION_EVIDENCE.scoreByCommand.get(bindingId) || null;
        const history = VERIFICATION_EVIDENCE.historyByTarget.get(vvStatusKey('COMMAND', command)) || [];
        const commandRows = VERIFICATION_EVIDENCE.evidence.get(bindingId) || [];
        const currentIds = current?.evidenceIds || [];
        const currentRefs = new Set(currentIds.map((id) => VERIFICATION_EVIDENCE.evidenceRefById.get(id)));
        const historyRefs = new Set(history.flatMap((item) => item.evidenceIds)
          .map((id) => VERIFICATION_EVIDENCE.evidenceRefById.get(id)));
        const scoreRefs = new Set((score?.evidenceIds || [])
          .map((id) => VERIFICATION_EVIDENCE.evidenceRefById.get(id)));
        const direct = score?.directEvidence.find((item) => item.evidenceRef === safeRef) || null;
        const commandRow = commandRows.find((item) =>
          VERIFICATION_EVIDENCE.evidenceRefById.get(item.ref) === safeRef) || null;
        const withdrawal = (VERIFICATION_EVIDENCE.withdrawnByCommand.get(bindingId) || [])
          .find((item) => item.qualificationEvidenceRef === safeRef) || null;
        const related = currentRefs.has(safeRef) || historyRefs.has(safeRef) || scoreRefs.has(safeRef) || Boolean(direct) ||
          Boolean(commandRow) || Boolean(withdrawal);
        if (!related) {
          res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' });
          res.end('Evidence binding not found.');
          return;
        }
        const accountingOnly = currentRefs.has(safeRef) &&
          (/RECONCILIATION|ACCOUNTING|STATUS_BASIS_REBASE|LOCAL_STATUS_REBASE|TOPOLOGY_CORRECTION/i
            .test(current?.method || '') ||
            /CURRENT-RECONCILIATION|REPOSITORY-REBASE|TOPOLOGY-CORRECTION/i
              .test(current?.attemptId || ''));
        const proofRole = accountingOnly
          ? 'ACCOUNTING_STATUS_DERIVATION_ONLY_NOT_RUNTIME_PROOF'
          : withdrawal ? 'QUALIFICATION_OR_DISQUALIFICATION_RECORD'
          : direct?.proofRole || (commandRow ? 'RETAINED_COMMAND_RESULT'
            : scoreRefs.has(safeRef) ? 'SEMANTIC_COMMAND_ASSESSMENT_NOT_RUNTIME_PROOF'
            : 'COMMAND_STATUS_HISTORY');
        const observation = commandRow?.observation || direct?.observation ||
          (currentRefs.has(safeRef) ? current?.observation : null) || withdrawal?.currentReassessment ||
          'See the retained artifact below.';
        const limitations = commandRow?.limitations || direct?.limitations ||
          (currentRefs.has(safeRef) ? current?.limitations : null) || withdrawal?.reason ||
          'This evidence is limited to the exact command binding and recorded attempt.';
        bindingNavigation = {
          route: command.route,
          heading: command.sourceContract.section,
        };
        bindingHeader = [
          'Reviewer navigation context (generated; not retained evidence)',
          'Exact command evidence binding',
          `Page: ${command.route}`,
          `Heading: ${command.sourceContract.section}`,
          `Documentation source: ${command.sourceContract.file}:${command.sourceContract.line_start}-${command.sourceContract.line_end}`,
          `Command: ${command.text}`,
          `Command ID: ${bindingId}`,
          `Current command status: ${current?.status || 'UNVALIDATED'}`,
          `Evidence proof role: ${proofRole}`,
          `Recorded outcome for this binding: ${observation}`,
          `Limitations for this binding: ${limitations}`,
          accountingOnly
            ? 'Important: this artifact explains status classification/accounting only. It does not show that the command executed or worked.'
            : 'Important: apply this artifact only within the proof role and limitations above; do not infer parent-page PASS.',
          '', 'The retained artifact begins below. This generated header is not proof.', '',
        ].map(vvText).join('\n');
      } else if (statusTarget) {
        const current = VERIFICATION_EVIDENCE.currentStatusByTarget.get(statusTarget.key);
        const history = VERIFICATION_EVIDENCE.historyByTarget.get(statusTarget.key) || [];
        const currentRefs = new Set((current?.evidenceIds || [])
          .map((id) => VERIFICATION_EVIDENCE.evidenceRefById.get(id)));
        const historyRefs = new Set(history.flatMap((item) => item.evidenceIds)
          .map((id) => VERIFICATION_EVIDENCE.evidenceRefById.get(id)));
        if (!current || (!currentRefs.has(safeRef) && !historyRefs.has(safeRef))) {
          res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' });
          res.end('Evidence binding not found.');
          return;
        }
        const accountingOnly = currentRefs.has(safeRef) &&
          (/RECONCILIATION|ACCOUNTING|STATUS_BASIS_REBASE|LOCAL_STATUS_REBASE|TOPOLOGY_CORRECTION/i
            .test(current.method || '') ||
            /CURRENT-RECONCILIATION|REPOSITORY-REBASE|TOPOLOGY-CORRECTION/i
              .test(current.attemptId || ''));
        const subject = current.basis.subject;
        bindingNavigation = {
          route: subject.route,
          heading: subject.headings[0] || 'Introduction',
        };
        bindingHeader = [
          'Reviewer navigation context (generated; not retained evidence)',
          'Exact V&V target evidence binding',
          `Target: ${statusTarget.level} ${statusTarget.id}`,
          `Page: ${subject.route}`,
          `Heading: ${subject.headings.join(' / ')}`,
          `Claim under review: ${subject.claim}`,
          `Current target status: ${current.status}`,
          `Evidence proof role: ${accountingOnly
            ? 'ACCOUNTING_STATUS_DERIVATION_ONLY_NOT_RUNTIME_PROOF'
            : ['ROLLUP', 'COMPOSITE_TARGET_AND_CHILDREN'].includes(current.basis.basisKind)
              ? 'PARENT_STATUS_ROLLUP_NOT_DIRECT_COMMAND_PROOF'
              : 'CURRENT_TARGET_STATUS_EVIDENCE'}`,
          `Recorded outcome for this binding: ${current.observation}`,
          `Limitations for this binding: ${current.limitations}`,
          accountingOnly
            ? 'Important: this artifact explains status classification/accounting only. It does not show that a command executed or worked.'
            : 'Important: evidence for a parent target or broader prose claim does not prove every nested command or branch.',
          '', 'The retained artifact begins below. This generated header is not proof.', '',
        ].map(vvText).join('\n');
      } else {
        res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' });
        res.end('Evidence binding not found.');
        return;
      }
    }
    const evidenceBytes = vvRepositoryFile(safeRef, 'invalid retained V&V evidence file').bytes;
    const displayBytes = evidenceTextForDisplay(
      Buffer.concat([Buffer.from(bindingHeader, 'utf8'), evidenceBytes]),
    );
    if (bindingNavigation) {
      const pageHref = vvCanonicalRoute(bindingNavigation.route);
      const heading = vvSectionTitle(bindingNavigation.heading);
      const fragment = heading === 'Introduction' ? '' : vvHeadingSlug(heading);
      const headingHref = fragment ? `${pageHref}#${fragment}` : pageHref;
      const headingLink = headingHref === pageHref ? '' :
        `<a id="review-heading-link" href="${esc(headingHref)}">Open heading: ${esc(heading)}</a>`;
      res.writeHead(200, {
        'content-type': 'text/html; charset=utf-8',
        'content-disposition': `inline; filename="${path.basename(safeRef)}.html"`,
        'cache-control': 'no-store',
        'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'",
        'x-content-type-options': 'nosniff',
      });
      res.end(`<!doctype html><html><head><meta charset="utf-8"><title>V&amp;V evidence — ${esc(pageHref)}</title>
<style>body{font:14px/1.55 ui-sans-serif,system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#1a1a2e}nav{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}a{color:#315fff;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f6f7fb;border:1px solid #dfe3ed;border-radius:10px;padding:18px}</style>
</head><body><nav aria-label="Evidence review navigation"><a id="review-page-link" href="${esc(pageHref)}">Back to page: ${esc(pageHref)}</a>${headingLink}</nav>
<pre>${esc(displayBytes.toString('utf8'))}</pre></body></html>`);
      return;
    }
    res.writeHead(200, {
      'content-type': 'text/plain; charset=utf-8',
      'content-disposition': `inline; filename="${path.basename(safeRef)}"`,
      'cache-control': 'no-store',
      'x-content-type-options': 'nosniff',
    });
    res.end(displayBytes);
    return;
  }
  if (p === '/__review__/api/state' && req.method === 'GET') {
    const reviewer = url.searchParams.get('reviewer') || '';
    sendJson(res, 200, { reviewer, items: readReviewerState(reviewer) });
    return;
  }
  if (p === '/__review__/api/state' && req.method === 'POST') {
    try {
      const body = JSON.parse((await readBody(req, 8 * 1024 * 1024)).toString('utf8'));
      if (!body || typeof body !== 'object' || Array.isArray(body) ||
        Object.keys(body).sort().join(',') !== 'items,reviewer' ||
        typeof body.reviewer !== 'string' || !body.reviewer.trim() || !Array.isArray(body.items)) {
        sendJson(res, 400, { error: 'expected { reviewer, items[] }' });
        return;
      }
      writeReviewerState(body.reviewer.trim(), body.items);
      sendJson(res, 200, { ok: true, saved: body.items.length });
    } catch (e) {
      sendJson(res, 400, { error: String(e.message || e) });
    }
    return;
  }
  if (p === '/__review__/api/import' && req.method === 'POST') {
    try {
      const payload = JSON.parse((await readBody(req, 8 * 1024 * 1024)).toString('utf8'));
      sendJson(res, 200, importFeedbackPayload(payload));
    } catch (e) {
      sendJson(res, 400, { error: String(e.message || e) });
    }
    return;
  }
  if (p.startsWith('/__review__/export/')) {
    const exportPayload = feedbackExportPayload();
    const { items, reviewers } = exportPayload;
    const visibleItems = items.filter((item) => !item.deleted);
    const kind = p.split('/').pop();
    if (kind === 'feedback.csv') {
      res.writeHead(200, {
        'content-type': 'text/csv; charset=utf-8',
        'content-disposition': 'attachment; filename="pr185-docs-feedback.csv"',
        'cache-control': 'no-store',
      });
      res.end(toCsv(visibleItems));
      return;
    }
    if (kind === 'feedback.md') {
      res.writeHead(200, {
        'content-type': 'text/markdown; charset=utf-8',
        'content-disposition': 'attachment; filename="pr185-docs-feedback.md"',
        'cache-control': 'no-store',
      });
      res.end(toMarkdown(visibleItems, reviewers));
      return;
    }
    if (kind === 'feedback.json') {
      res.writeHead(200, {
        'content-type': 'application/json',
        'content-disposition': 'attachment; filename="pr185-docs-feedback.json"',
        'cache-control': 'no-store',
      });
      res.end(JSON.stringify(exportPayload, null, 2));
      return;
    }
  }
  res.writeHead(404, { 'content-type': 'text/plain' });
  res.end('not found');
}

function badGateway(res, err) {
  if (res.headersSent) { try { res.destroy(); } catch { /* already gone */ } return; }
  res.writeHead(502, { 'content-type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html><body style="font:15px/1.6 system-ui;max-width:560px;margin:60px auto;padding:0 16px">
<h2>Docs preview is not running</h2>
<p>The review server could not reach the Mintlify preview at <code>${esc(TARGET.origin)}</code>.</p>
<p>In the repo folder, start it first:</p>
<pre style="background:#f0f2f8;padding:12px;border-radius:8px">npm run dev -- --no-open</pre>
<p>then reload this page. If the preview started on a different port, restart this server with
<code>node review-server.mjs --target http://localhost:&lt;port&gt;</code>.</p>
<p style="color:#888">(${esc(err.message || err)})</p></body></html>`);
}

const server = http.createServer(async (req, res) => {
  if (!expectedReviewHost(req)) {
    sendJson(res, 403, { error: 'review proxy requests require the expected loopback Host' });
    return;
  }
  const url = new URL(req.url, `http://localhost:${PORT}`);
  if (url.pathname.startsWith('/__review__')) {
    try { await handleReviewRoute(req, res, url); } catch (e) { sendJson(res, 500, { error: String(e.message || e) }); }
    return;
  }
  if (!new Set(['GET', 'HEAD', 'OPTIONS']).has(req.method)) {
    const originError = reviewOriginError(req);
    if (originError) {
      sendJson(res, 403, { error: `proxied mutation ${originError}` });
      return;
    }
  }

  const headers = { ...req.headers, host: TARGET.host, 'accept-encoding': 'identity' };
  const upstream = http.request(
    { hostname: TARGET.hostname, port: TARGET.port || 80, path: req.url, method: req.method, headers },
    (up) => {
      const outHeaders = { ...up.headers };
      delete outHeaders['content-security-policy'];
      delete outHeaders['content-security-policy-report-only'];
      if (outHeaders.location && outHeaders.location.startsWith(TARGET.origin)) {
        outHeaders.location = outHeaders.location.slice(TARGET.origin.length) || '/';
      }
      const ctype = String(up.headers['content-type'] || '');
      if (ctype.includes('text/html') && req.method !== 'HEAD') {
        const chunks = [];
        up.on('data', (c) => chunks.push(c));
        up.on('end', () => {
          const html = injectOverlay(Buffer.concat(chunks).toString('utf8'));
          delete outHeaders['content-length'];
          delete outHeaders['transfer-encoding'];
          outHeaders['content-length'] = Buffer.byteLength(html);
          res.writeHead(up.statusCode, outHeaders);
          res.end(html);
        });
        up.on('error', () => { try { res.destroy(); } catch {} });
      } else {
        res.writeHead(up.statusCode, outHeaders);
        up.pipe(res);
        up.on('error', () => { try { res.destroy(); } catch { /* already gone */ } });
      }
    }
  );
  upstream.on('error', (err) => badGateway(res, err));
  req.pipe(upstream);
});

// websocket passthrough (Next.js HMR etc.)
server.on('upgrade', (req, socket, head) => {
  if (reviewOriginError(req)) {
    socket.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\nContent-Length: 0\r\n\r\n');
    return;
  }
  const upstream = net.connect(Number(TARGET.port || 80), TARGET.hostname, () => {
    let raw = `${req.method} ${req.url} HTTP/1.1\r\n`;
    for (let i = 0; i < req.rawHeaders.length; i += 2) {
      const k = req.rawHeaders[i];
      const v = k.toLowerCase() === 'host' ? TARGET.host : req.rawHeaders[i + 1];
      raw += `${k}: ${v}\r\n`;
    }
    raw += '\r\n';
    upstream.write(raw);
    if (head && head.length) upstream.write(head);
    socket.pipe(upstream);
    upstream.pipe(socket);
  });
  upstream.on('error', () => socket.destroy());
  socket.on('error', () => upstream.destroy());
});

server.listen(PORT, BIND_HOST, () => {
  console.log('');
  console.log('  Vast.ai docs review server (PR #185)');
  console.log('  ------------------------------------');
  console.log(`  Review the docs at:   http://${DISPLAY_HOST}:${PORT}/host/hosting-overview`);
  console.log(`  Proxying preview at:  ${TARGET.origin}  (start it with: npm run dev -- --no-open)`);
  console.log(`  Feedback saved to:    ${FEEDBACK_DIR}`);
  console.log(`  Status & exports:     http://${DISPLAY_HOST}:${PORT}/__review__/`);
  if (VERIFICATION_EVIDENCE.available) {
    console.log('  V&V evidence:         available (strict package validation passed)');
  } else {
    console.warn(`  V&V evidence:         UNAVAILABLE (${VERIFICATION_EVIDENCE.unavailableReason || 'package-integrity-failure'})`);
  }
  console.log('');
});
