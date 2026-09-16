import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import { loadCurrentHostReviewTransition } from './current_host_review_transition.mjs';
import { TERMS_PATH, TERMS_SOURCE } from './current_host_terms_binding.mjs';
import crypto from 'node:crypto';

const root = new URL('../', import.meta.url);
const read = ref => fs.readFileSync(new URL(ref, root));
const current = () => JSON.parse(read('verification/current-host-docs-review.json'));
const exists = ref => fs.existsSync(new URL(ref, root));
const digest = value => crypto.createHash('sha256').update(value).digest('hex');

test('sealed Terms transition retains all six bounded published-rule bindings', () => {
  const scan = loadCurrentHostReviewTransition({ read, model: current(), exists });
  assert.equal(scan.matches.size, 2013);
  assert.equal(scan.terms.registry.transitions.length, 6);
  for (const [ref, wanted] of scan.artifactHashes) assert.equal(digest(read(ref)), wanted, ref);
  assert.equal(scan.artifactHashes.get(TERMS_SOURCE), digest(read(TERMS_SOURCE)));
  assert.equal(scan.artifactHashes.get(scan.terms.source.before_artifact.path), scan.terms.source.before_artifact.sha256);
  for (const entry of scan.terms.registry.transitions) {
    const shown = scan.presentation.get(entry.claim_id);
    assert.equal(shown.registryRef, TERMS_PATH);
    assert.equal(shown.baselineRef, scan.terms.baseline);
    assert.equal(shown.previous.id, entry.claim_id);
    assert.ok(shown.basis.some(basis => basis.sourceLabel === 'Terms of Service' && basis.sourceUrl === 'https://vast.ai/terms'));
  }
});

test('Terms transition rejects registry and model tampering', () => {
  const model = current();
  assert.throws(() => loadCurrentHostReviewTransition({ read: ref => ref === TERMS_PATH ? Buffer.from('{}') : read(ref), model, exists }), /Terms registry drift/);
  const changed = structuredClone(model);
  const claim = changed.pages.flatMap(page => page.claims).find(item => item.id === 'MCL-fe3eccd1cd40b4bd');
  claim.spans[0].text_sha256 = '0'.repeat(64);
  assert.throws(() => loadCurrentHostReviewTransition({ read, model: changed, exists }), /whole model differs/);
  const noSource = structuredClone(model);
  const exportClaim = noSource.pages.flatMap(page => page.claims).find(item => item.id === 'MCL-633317ca7ebecfef');
  exportClaim.source_refs = exportClaim.source_refs.filter(ref => ref.path !== 'https://vast.ai/terms');
  assert.throws(() => loadCurrentHostReviewTransition({ read, model: noSource, exists }), /whole model differs/);
  assert.throws(() => loadCurrentHostReviewTransition({ read: ref => ref === 'host/workload-policy.mdx' ? Buffer.concat([read(ref), Buffer.from('\nextra')]) : read(ref), model, exists }), /current source drift/);
});
