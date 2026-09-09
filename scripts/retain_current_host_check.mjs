// Retain a local check without overwriting an earlier attempt.
// This recorder does not authorize the command: callers must choose only safe checks.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [name, command, ...args] = process.argv.slice(2);
if (!/^[a-z0-9-]+$/.test(name || '') || !command) throw new Error('Usage: recorder <unique-name> <safe-command> [...args]');
const output = path.join(root, 'verification/evidence/2026-09-07-host-current-vv-attempt-01', name + '.json');
if (fs.existsSync(output)) throw new Error('Earlier attempt exists; use a new attempt name');
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const sanitize = text => String(text).replaceAll(root, '<DOCS_REPO>')
  .replace(/\/Users\/hanneszietsman/g, '<USER>');
const git = (...gitArgs) => spawnSync('git', gitArgs, { cwd: root, encoding: 'utf8' }).stdout.trim();
const sourceFiles = ['review-server.mjs', 'docs.json', 'verification/current-host-docs-review.json',
  'scripts/build_current_host_vv_overlay.py', 'verification/current-host-claim-corrections.json'];
const sources = () => Object.fromEntries(sourceFiles.filter(file => fs.existsSync(path.join(root, file)))
  .map(file => [file, digest(fs.readFileSync(path.join(root, file)))]));
const before = sources();
const started = new Date().toISOString();
const result = spawnSync(command, args, { cwd: root, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, timeout: 600000 });
const after = sources();
const record = { started, finished: new Date().toISOString(), command: [command, ...args].map(sanitize),
  head: git('rev-parse', 'HEAD'), source_hashes_before: before, source_hashes_after: after,
  source_identity_unchanged: JSON.stringify(before) === JSON.stringify(after),
  tracked_dirty: !!git('status', '--porcelain', '--untracked-files=no'),
  exit_code: result.status, signal: result.signal, error: result.error ? sanitize(result.error.message) : null,
  stdout: sanitize(result.stdout || ''), stderr: sanitize(result.stderr || ''),
  raw_stdout_sha256: digest(result.stdout || ''), raw_stderr_sha256: digest(result.stderr || ''),
  sanitation: 'Workstation identity and repository path masked; raw output digests retained.',
  limitation: 'Local static or loopback check only. Does not establish Host/API behavior, owner authority, or human acceptance.' };
fs.writeFileSync(output, JSON.stringify(record, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify({ artifact: path.relative(root, output), exit_code: result.status, error: record.error,
  stdout_tail: record.stdout.slice(-1800), stderr_tail: record.stderr.slice(-1800) }));
process.exitCode = result.status === 0 && !result.error ? 0 : 1;
