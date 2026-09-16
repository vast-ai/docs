import fs from 'node:fs';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const dir = 'verification/evidence/2026-09-14-host-docs-publish-attempt-01';
const git = (args, input) => execFileSync('git', args, { input, maxBuffer: 256 * 1024 * 1024 });
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const baseline = JSON.parse(fs.readFileSync(`${dir}/baseline.json`));
const original = new Map(baseline.files.map(f => [f.path, f]));
const allowedRetests = new Set([
  'scripts/host-review-html.test.mjs', 'scripts/templates/host-docs-review.html',
  'verification/host-docs-review-export.json', 'verification/host-docs-review.html',
]);
if (git(['diff', '--cached', '--name-only']).length) throw Error('Expected empty index');
const rows = git(['status', '--porcelain=v1', '-z', '--untracked-files=all'])
  .toString().split('\0').filter(Boolean);
const paths = rows.map(row => {
  const path = row.slice(3);
  if (!original.has(path) && !path.startsWith(`${dir}/`)) throw Error(`Unreviewed path: ${path}`);
  if (path.includes('\n')) throw Error('Unexpected newline in path');
  const stat = fs.lstatSync(path);
  if (!stat.isFile() || stat.size >= 100 * 1024 * 1024) throw Error(`Unexpected target: ${path}`);
  if (original.has(path) && !allowedRetests.has(path) && sha(fs.readFileSync(path)) !== original.get(path).sha256)
    throw Error(`Unreviewed change since baseline: ${path}`);
  return path;
});
const receipt = `${dir}/staged-snapshot.json`;
if (fs.existsSync(receipt)) throw Error('Refuse receipt overwrite');
git(['add', '--pathspec-from-file=-', '--pathspec-file-nul'], paths.join('\0') + '\0');
const index = new Map(git(['ls-files', '--stage', '-z']).toString().split('\0').filter(Boolean)
  .map(row => { const [meta, path] = row.split('\t'); return [path, meta.split(' ')[1]]; }));
const hashes = git(['hash-object', '--no-filters', '--stdin-paths'], paths.join('\n') + '\n')
  .toString().trim().split('\n');
const mismatches = paths.filter((path, i) => index.get(path) !== hashes[i]);
if (mismatches.length) throw Error(`Staged bytes mismatch: ${mismatches.join(', ')}`);
const result = {
  recorded_at: new Date().toISOString(), base_head: git(['rev-parse', 'HEAD']).toString().trim(),
  staged_file_count_before_receipt: paths.length, exact_blob_mismatches: mismatches,
  staged_tree_before_receipt: git(['write-tree']).toString().trim(),
  staged_paths_sha256: sha(Buffer.from(paths.join('\0') + '\0')),
  current_model_sha256: sha(fs.readFileSync('verification/current-host-docs-review.json')),
  html_sha256: sha(fs.readFileSync('verification/host-docs-review.html')),
  scope: 'Baseline task files, four documented publication-copy retest files, and this publication attempt only. This receipt is added afterward and is not included in its own tree hash. No push, merge, CI or acceptance is established by this receipt.',
};
fs.writeFileSync(receipt, JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
git(['add', '--', receipt]);
console.log(JSON.stringify(result));
