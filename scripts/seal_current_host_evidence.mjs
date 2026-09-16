// Record exact current source identities and an evidence-file manifest.
// No V&V status is promoted by this accounting operation.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const directory = 'verification/evidence/2026-09-07-host-current-vv-attempt-01';
const name = process.argv[2] || 'final-manifest.json';
if (!/^final-manifest(?:-\d+)?\.json$/.test(name)) throw new Error('Use a final-manifest[-attempt].json name');
const output = path.join(root, directory, name);
if (fs.existsSync(output)) throw new Error('Final manifest already exists; use a new attempt for further changes.');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }).trim();
const review = JSON.parse(fs.readFileSync(path.join(root, 'verification/current-host-docs-review.json')));
const named = new Set([
  ...git('diff', '--name-only', 'HEAD').split('\n').filter(Boolean),
  ...review.source.source_manifest.map(item => item.path),
  'verification/HOST-DOCS-CURRENT-REVIEW-PLAN.md', 'verification/HOST-DOCS-CLAIMS-TO-RESOLVE.md',
  'scripts/check_current_host_review.mjs', 'scripts/retain_current_host_check.mjs', 'scripts/seal_current_host_evidence.mjs',
]);
const describe = relative => {
  const bytes = fs.readFileSync(path.join(root, relative));
  return { path: relative, bytes: bytes.length, sha256: sha(bytes) };
};
const walk = relative => fs.readdirSync(path.join(root, relative), { withFileTypes: true }).flatMap(entry => {
  const child = relative + '/' + entry.name;
  if (entry.isSymbolicLink()) throw new Error('No symlink permitted in current evidence');
  return entry.isDirectory() ? walk(child) : [child];
});
const historical = ['host-docs-test-sets.json', 'host-docs-test-results.json', 'host-docs-command-scores.json'].map(name => {
  const file = 'verification/' + name;
  const current = fs.readFileSync(path.join(root, file));
  const original = execFileSync('git', ['show', '7d42a0d439f91e4dc2877104db807ec6fb975ce4:' + file], { cwd: root, maxBuffer: 32 * 1024 * 1024 });
  if (!current.equals(original)) throw new Error('Frozen historical package changed: ' + file);
  return { ...describe(file), unchanged_from_frozen_7d: true };
});
const record = {
  captured_at: new Date().toISOString(), head: git('rev-parse', 'HEAD'), tree: git('rev-parse', 'HEAD^{tree}'),
  branch: git('branch', '--show-current'), tracked_worktree_dirty: !!git('status', '--porcelain', '--untracked-files=no'),
  baseline_capture_sha256: '0696817522e0d1a34844ccf8268bb99ca42cb7cc47641307c18e6e824082f510',
  counts: review.counts, historical,
  sources: [...named].filter(file => fs.existsSync(path.join(root, file))).sort().map(describe),
  evidence: walk(directory).sort().map(describe),
  limits: 'Identity and completeness accounting only. Source content, evidence suitability, and human acceptance are separate. The manifest excludes itself. Pre-existing private/untracked files are neither enumerated nor included.',
};
fs.writeFileSync(output, JSON.stringify(record, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify({ sources: record.sources.length, evidence: record.evidence.length,
  historical_unchanged: historical.length, manifest_sha256: sha(fs.readFileSync(output)) }));
