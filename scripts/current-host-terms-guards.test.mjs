import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const TERMS_PATH = 'verification/current-host-terms-binding.json';
const TERMS_SOURCE = 'host/workload-policy.mdx';
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const newerPath = path.join(ROOT, 'verification/current-host-jurisdiction.json');
const newer = fs.existsSync(newerPath) ? JSON.parse(fs.readFileSync(newerPath)) : null;
const current = () => JSON.parse(fs.readFileSync(path.join(ROOT, newer?.baseline.path || 'verification/current-host-docs-review.json')));
// Terms guards retain the original Terms model and source bytes, even when a
// later sealed transition edits other pages. No production pin is replaced.
const frozenSources = new Map((newer?.sources || []).map(source =>
  [source.path, fs.readFileSync(path.join(ROOT, source.before_artifact.path))]));
const baseRegistry = () => JSON.parse(fs.readFileSync(path.join(ROOT, TERMS_PATH)));

async function sealedFixture({registryMutate = value => value, sourceMutate = value => value} = {}) {
  const registry = registryMutate(baseRegistry());
  const registryBytes = Buffer.from(JSON.stringify(registry));
  const source = Buffer.from(sourceMutate(fs.readFileSync(path.join(ROOT, TERMS_SOURCE), 'utf8')));
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'terms-guards-'));
  for (const name of ['current_host_authority_scan.mjs', 'current_host_clarification.mjs', 'current_host_terms_binding.mjs']) {
    const input = fs.readFileSync(path.join(ROOT, 'scripts', name), 'utf8');
    const output = name === 'current_host_terms_binding.mjs'
      ? input.replace(/TERMS_REGISTRY_SHA256='[0-9a-f]{64}'/, `TERMS_REGISTRY_SHA256='${sha(registryBytes)}'`)
      : input;
    fs.writeFileSync(path.join(temp, name), output);
  }
  const module = await import(`${pathToFileURL(path.join(temp, 'current_host_terms_binding.mjs')).href}?${Math.random()}`);
  const read = ref => ref === TERMS_PATH ? registryBytes : ref === TERMS_SOURCE ? source : frozenSources.get(ref) || fs.readFileSync(path.join(ROOT, ref));
  const exists = ref => ref === TERMS_PATH || fs.existsSync(path.join(ROOT, ref));
  return { module, read, exists, model: current(), temp };
}

async function rejects(mutator, expected, sourceMutate) {
  const fixture = await sealedFixture({registryMutate: mutator, sourceMutate});
  try {
    assert.throws(() => fixture.module.loadTermsBinding({read: fixture.read, model: fixture.model, exists: fixture.exists}), expected);
  } finally { fs.rmSync(fixture.temp, {recursive: true, force: true}); }
}

test('Terms guard rejects an omitted exact transition after temporary resealing', async () => {
  await rejects(registry => { registry.transitions.pop(); return registry; }, /six Terms claims required/);
});

test('Terms guard requires a canonical Terms source ref in every patched after-record', async () => {
  await rejects(registry => { registry.transitions[0].after.source_refs = []; return registry; }, /dropped retained source\/evidence/);
});

test('Terms guard binds patched span source file and current-slice hash', async () => {
  await rejects(registry => { registry.transitions[0].after.spans[0].source_file = 'host/hosting-overview.mdx'; return registry; }, /span provenance drift/);
  await rejects(registry => { registry.transitions[0].after.spans[0].text_sha256 = '0'.repeat(64); return registry; }, /span provenance drift/);
});

test('Terms guard rejects an excerpt absent from its pinned Terms clause', async () => {
  await rejects(registry => { registry.transitions[0].basis[0].excerpt = 'not in the captured clause'; return registry; }, /invalid Terms basis/);
});

test('Terms guard rejects a line-count expansion before projection', async () => {
  await rejects(registry => { registry.source.after_sha256 = sha(Buffer.from(fs.readFileSync(path.join(ROOT, TERMS_SOURCE), 'utf8') + '\nextra source line')); return registry; }, /preserve line count/, source => source + '\nextra source line');
});

test('Terms guard rejects a changed nonblank source line without a claim occurrence', async () => {
  await rejects(registry => {
    const source = fs.readFileSync(path.join(ROOT, TERMS_SOURCE), 'utf8').replace('\n\n| Category |', '\nNew unclaimed policy prose.\n| Category |');
    registry.source.after_sha256 = sha(Buffer.from(source));
    return registry;
  }, /changed nonblank Workload Policy source line lacks a claim occurrence/, source => source.replace('\n\n| Category |', '\nNew unclaimed policy prose.\n| Category |'));
});
