import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import test from 'node:test';
import {PAYOUT_OBSERVATION, PAYOUT_PATH, PAYOUT_SOURCE, loadPayoutProviderCorrection, projectPayoutProviderCorrection} from './current_host_payout_provider_correction.mjs';

const root = new URL('../', import.meta.url);
const read = ref => fs.readFileSync(new URL(ref, root));
const frozenRead = ref => ref === PAYOUT_SOURCE ? read('verification/evidence/2026-09-14-payout-terms-correction-attempt-01/pre-correction-payment.mdx') : read(ref);
const exists = ref => fs.existsSync(new URL(ref, root));
const targets = new Set(['MCL-77f72f0e0ac77e54','MCL-a04f3ef2f5a7d5fd','MCL-cc62439b0f816902','MCL-9826b26393329d27']);
const claims = model => new Map(model.pages.flatMap(page => page.claims.map(claim => [claim.id, claim])));

test('actual frozen before state fails and current four-claim projection passes', () => {
  const before = JSON.parse(read('verification/evidence/2026-09-14-payout-provider-correction-attempt-01/pre-correction-model.json'));
  assert.deepEqual(new Set([...claims(before).values()].filter(c => targets.has(c.id)).map(c => c.status)), new Set(['FAIL']));
  assert.match(read('verification/evidence/2026-09-14-payout-provider-correction-attempt-01/pre-correction-payment.mdx').toString(), /ACH, wire, and SWIFT payouts are not available/);
  const projected = projectPayoutProviderCorrection({read:frozenRead, exists});
  assert.deepEqual(projected.model.counts.claim_statuses, {PASS:312, UNVALIDATED:1560, NOT_APPLICABLE:87, FAIL:31, BLOCKED:23});
  const faq = claims(projected.model).get('MCL-9826b26393329d27');
  for (const [id, claim] of claims(projected.model)) assert.deepEqual(projected.matches.get(id)?.claim, claim, 'live reader match: ' + id);
  for (const [ref, digest] of projected.artifactHashes) assert.equal(crypto.createHash('sha256').update(frozenRead(ref)).digest('hex'), digest, 'live reader freshness: ' + ref);
  assert.deepEqual(faq.evidence_refs.map(item => item.id), ['EV-PAYOUT-PROVIDER-SOURCE-LINK-01','EV-PAYOUT-UI-PAYPAL-01','EV-PAYOUT-UI-STRIPE-01','EV-PAYOUT-UI-WISE-01']);
  assert.equal(loadPayoutProviderCorrection({read:frozenRead, model:projected.model, exists}).payoutProvider.registrySha256, projected.payoutProvider.registrySha256);
});

test('tampered evidence, source, unsupported absence proof, and unrelated model drift reject', () => {
  assert.throws(() => projectPayoutProviderCorrection({read: ref => ref === PAYOUT_OBSERVATION ? Buffer.concat([frozenRead(ref), Buffer.from(' ')]) : frozenRead(ref), exists}));
  assert.throws(() => projectPayoutProviderCorrection({read: ref => ref === PAYOUT_SOURCE ? Buffer.from(frozenRead(ref).toString().replace('Stripe, PayPal or Wise', 'Stripe, PayPal, Wise and ACH')) : frozenRead(ref), exists}));
  const registry = JSON.parse(read(PAYOUT_PATH)); registry.transitions.at(-1).observation_ids = ['PAYOUT-UI-DIRECT-01'];
  assert.throws(() => projectPayoutProviderCorrection({read: ref => ref === PAYOUT_PATH ? Buffer.from(JSON.stringify(registry)) : frozenRead(ref), exists}));
  const model = projectPayoutProviderCorrection({read:frozenRead, exists}).model;
  const unselected = [...claims(model).values()].find(claim => !targets.has(claim.id)); unselected.rationale += ' tampered';
  assert.throws(() => loadPayoutProviderCorrection({read:frozenRead, model, exists}), /whole model differs/);
});
