import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { INSTALL_INTAKE_PATH, loadInstallEvidenceIntake, validateInstallEvidenceIntake } from './current_host_install_evidence_intake.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const modelRoot = process.env.H100_INTAKE_MODEL_ROOT || root;
const read = (ref) => fs.readFileSync(path.join(root, ref));
const model = JSON.parse(fs.readFileSync(path.join(modelRoot, 'verification/current-host-docs-review.json'), 'utf8'));
const originalStatuses = model.pages.flatMap((page) => page.claims.map((claim) => [claim.id, claim.status]));

test('actual current model receives five historical checks plus pinned September 9 installation context', () => {
  const intake = loadInstallEvidenceIntake({ read, model });
  assert.match(intake.message, /modified direct installation completed with retained warnings and failures/i);
  assert.match(intake.message, /USD 0\.01\/GB in both directions/i);
  assert.match(intake.message, /instance 50364501/i);
  assert.match(intake.message, /sum of squares 1240/i);
  assert.doesNotMatch(intake.message, /remains unlisted/i);
  assert.doesNotMatch(intake.message, /No client rental was started/);
  assert.equal(intake.records.length, 5);
  assert.deepEqual(intake.records.map((record) => record.claimId), [
    'MCL-fd7e8b86c5cfd383', 'MCL-009da802cabe1bc9', 'MCL-ead93c85c2ff4168',
    'MCL-ec2e1c9a8be1a706', 'MCL-ce118e1ce7bf71bb',
  ]);
  assert.equal(intake.records.every((record) => record.route === '/host/installing-host-software'), true);
  assert.deepEqual(intake.records.map((record) => record.checks[0].id), [
    'H100-SERVICE-BASELINE', 'H100-NO-INSTALL-BASELINE', 'H100-GPU-INVENTORY',
    'H100-DOCKER-MOUNT-INVENTORY', 'H100-SELFTEST-HELPER-SOURCE',
  ]);
  assert.deepEqual(model.pages.flatMap((page) => page.claims.map((claim) => [claim.id, claim.status])), originalStatuses);
  const selfTest = intake.records.at(-1);
  assert.equal(selfTest.checks[0].finding.id, 'HIST-04-02-B');
  assert.match(selfTest.limit, /suppresses only one explicit automatic listing\/self-test launch/i);
  assert.match(selfTest.remainingAction, /USD 0\.01\/GB both directions/i);
  assert.match(selfTest.remainingAction, /final billing, a hard spending cap, or a free rental/i);
  const wizard = intake.records[1];
  assert.equal(wizard.checks[0].id, 'H100-NO-INSTALL-BASELINE');
  assert.deepEqual(wizard.sourceLinks.slice(-15, -8).map((link) => link.label), [
    'September 9 direct-install preflight (sudo and guards passed)',
    'September 9 modified direct-install execution (not stock TUI or marketplace self-test)',
    'September 9 independent post-install observations',
    'September 9 registered machine readback (machine 150296 remains unlisted)',
    'September 9 retained installer subcommand failures and follow-up',
    'September 9 settled snapshot (no Docker containers or GPU compute processes)',
    'September 9 image-only pull retest (passed; original installer failure preserved)',
  ]);
  assert.equal(intake.records.every((record) => record.sourceLinks.at(-1).artifactRef === 'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/host-read-09.json'), true);
  assert.equal(intake.records.every((record) => /No further listing or rental action is authorized/i.test(record.remainingAction)), true);
  assert.ok(intake.artifactRefs.includes('verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/source-review-summary.json'));
  assert.ok(intake.artifactRefs.includes('verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/postcheck-02.json'));
  assert.ok(intake.artifactRefs.includes('verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/installer-findings-01.json'));
});

test('intake rejects a status injection, source drift, and artifact drift', () => {
  const bytes = read(INSTALL_INTAKE_PATH);
  const injected = JSON.parse(bytes); injected.records[0].status = 'PASS';
  assert.throws(() => validateInstallEvidenceIntake({ inputBytes: Buffer.from(JSON.stringify(injected)), read, model }), /input hash drift/);
  const drifted = JSON.parse(bytes); drifted.records[0].text += ' drift';
  assert.throws(() => validateInstallEvidenceIntake({ inputBytes: Buffer.from(JSON.stringify(drifted)), read, model }), /input hash drift/);
  assert.throws(() => loadInstallEvidenceIntake({ read: (ref) => ref.endsWith('new-host-readonly-02.json') ? Buffer.from('{}') : read(ref), model }), /artifact hash drift/);
});

test('contract rejects a valid-looking same-page substitution and unbound association', () => {
  const bytes = read(INSTALL_INTAKE_PATH);
  const substituted = JSON.parse(bytes);
  const replacement = model.pages.find((page) => page.route === '/host/installing-host-software').claims
    .find((claim) => claim.id === 'MCL-1ef8a4aa92b66755');
  substituted.records[0].claim_id = replacement.id;
  substituted.records[0].text = replacement.text;
  substituted.records[0].headings = replacement.headings;
  substituted.records[0].spans = replacement.spans;
  assert.throws(() => validateInstallEvidenceIntake({ inputBytes: Buffer.from(JSON.stringify(substituted)), read, model, enforceInputHash: false }), /record contract/);
  const unbound = JSON.parse(bytes);
  unbound.records[0].checks[0].artifact_ref = 'verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-02.md';
  assert.throws(() => validateInstallEvidenceIntake({ inputBytes: Buffer.from(JSON.stringify(unbound)), read, model, enforceInputHash: false }), /check artifact kind/);
  const changedCoverage = JSON.parse(bytes); changedCoverage.records[0].coverage = 'PASS';
  assert.throws(() => validateInstallEvidenceIntake({ inputBytes: Buffer.from(JSON.stringify(changedCoverage)), read, model }), /input hash drift/);
  const changedLink = JSON.parse(bytes); changedLink.records[1].source_links.pop();
  assert.throws(() => validateInstallEvidenceIntake({ inputBytes: Buffer.from(JSON.stringify(changedLink)), read, model, enforceInputHash: false }), /source-link contract/);
  assert.throws(() => loadInstallEvidenceIntake({ read: (ref) => ref.endsWith('postcheck-02.json') ? Buffer.from('{}') : read(ref), model }), /artifact hash drift/);
});

test('listing and rental context retains both failed prices plus the bounded successful lifecycle', () => {
  const intake = loadInstallEvidenceIntake({ read, model });
  const labels = ["September 9 USD 0.10/GB listing rejection (failure retained)","September 9 USD 0.01/GB listing readback (approved terms published)","September 9 tiny one-GPU client result (H100; sum of squares 1240)","September 9 task instance cleanup (destroyed and absent)","September 9 final host readback (listed approved terms; zero jobs)"];
  for (const record of intake.records) {
    assert.deepEqual(record.sourceLinks.slice(-5).map(link => link.label), labels);
    assert.match(record.remainingAction, /USD 1\/GB and USD 0\.10\/GB listing rejections remain retained failures/);
    assert.match(record.remainingAction, /Test instance 50364501 ran one tiny H100 result and was destroyed/);
  }
  for (const ref of [
    'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-010/listing-response-01.json',
    'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-readback-verification-01.json',
    'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/gpu-result-01.json',
    'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/cleanup-main.json',
    'verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/host-read-09.json',
  ]) {
    assert.throws(() => loadInstallEvidenceIntake({ read: candidate => candidate === ref ? Buffer.from('{}') : read(candidate), model }), /artifact hash drift/);
  }
  assert.deepEqual(model.pages.flatMap(page => page.claims.map(claim => [claim.id, claim.status])), originalStatuses);
});
