import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import { execFileSync, spawn } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REVIEWED_SOURCE_REVISION = '7d42a0d439f91e4dc2877104db807ec6fb975ce4';
let targetServer;
let reviewProcess;
let targetOrigin;
let reviewOrigin;
let feedbackDir;
let reviewOutput = '';
let reviewSourceSha256AtStartup;
let reviewedSourceFiles;
let historicalFixtureRoot;
let historicalReviewProcess;
let historicalReviewOrigin;
let historicalReviewOutput = '';

function listen(server, port = 0) {
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, '127.0.0.1', () => {
      server.removeListener('error', reject);
      resolve(server.address().port);
    });
  });
}

async function freePort() {
  const server = http.createServer();
  const port = await listen(server);
  await new Promise((resolve) => server.close(resolve));
  return port;
}

async function waitForReviewServer() {
  let lastError;
  for (let i = 0; i < 80; i += 1) {
    if (reviewProcess.exitCode != null) {
      throw new Error(`review server exited early (${reviewProcess.exitCode})\n${reviewOutput}`);
    }
    try {
      const response = await fetch(`${reviewOrigin}/__review__/api/context?path=%2Fhost%2Fhost-teams`);
      if (response.ok) return;
      lastError = new Error(`HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  throw new Error(`review server did not become ready: ${lastError}\n${reviewOutput}`);
}

async function currentContextFor(pathname) {
  const response = await fetch(`${reviewOrigin}/__review__/api/context?path=${encodeURIComponent(pathname)}`);
  assert.equal(response.status, 200);
  return response.json();
}

async function contextFor(pathname) {
  const response = await fetch(`${historicalReviewOrigin}/__review__/api/context?path=${encodeURIComponent(pathname)}`);
  assert.equal(response.status, 200);
  return response.json();
}

const SOURCE_PASSAGE_KEYS = [
  'end', 'occurrence', 'occurrences', 'redacted', 'section', 'start', 'text',
];

async function sourceLinesFor(claim) {
  return execFileSync('git', ['-C', ROOT, 'show',
    `${REVIEWED_SOURCE_REVISION}:${claim.sourceLocation.file}`], { encoding: 'utf8' }).split(/\r?\n/);
}

async function materializeReviewedSourceFixture(fixtureRoot) {
  if (!reviewedSourceFiles) {
    const paths = ['docs.json', 'api-reference', 'cli', 'guides', 'host', 'scripts', 'sdk', 'snippets'];
    const files = execFileSync('git', ['-C', ROOT, 'ls-tree', '-r', '--name-only',
      REVIEWED_SOURCE_REVISION, '--', ...paths], { encoding: 'utf8' })
      .split('\n').filter(Boolean);
    reviewedSourceFiles = new Map(files.map((file) => [file,
      execFileSync('git', ['-C', ROOT, 'show', `${REVIEWED_SOURCE_REVISION}:${file}`])
    ]));
  }
  for (const [file, bytes] of reviewedSourceFiles) {
    const destination = path.join(fixtureRoot, file);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(destination, bytes);
  }
}

function sourceLiteral(lines, { start, end }) {
  return lines.slice(start - 1, end).join('\n').trim();
}

function assertSourcePassageContract(claim, sourceLines) {
  assert.ok(claim.sourcePassages.length > 0, `${claim.id} has no source passages`);
  for (const passage of claim.sourcePassages) {
    assert.deepEqual(Object.keys(passage).sort(), SOURCE_PASSAGE_KEYS);
    assert.ok(Number.isInteger(passage.start) && Number.isInteger(passage.end));
    assert.ok(passage.start > 0 && passage.end >= passage.start);
    assert.equal(typeof passage.text, 'string');
    assert.ok(passage.text.length > 0);
    assert.equal(typeof passage.section, 'string');
    assert.ok(claim.checkedContent.sections.includes(passage.section));
    assert.equal(typeof passage.redacted, 'boolean');
    assert.ok(Number.isInteger(passage.occurrence) && Number.isInteger(passage.occurrences));
    assert.ok(passage.occurrences > 0);
    assert.ok(passage.occurrence >= 0 && passage.occurrence < passage.occurrences);
    assert.ok(claim.sourceLocation.spans.some((span) =>
      passage.start >= span.start && passage.end <= span.end),
    `${claim.id} passage ${passage.start}-${passage.end} is outside its declared source spans`);
    if (!passage.redacted) assert.equal(passage.text, sourceLiteral(sourceLines, passage));
  }
}

function assertCurrentClaimState(claim, { status, evidenceIds, dispositionEvidenceIds }) {
  assert.equal(claim.current.status, status);
  assert.deepEqual(claim.current.evidenceIds, evidenceIds);
  assert.deepEqual(claim.current.evidence.map((item) => item.id), evidenceIds);
  assert.deepEqual(claim.current.dispositionEvidenceIds, dispositionEvidenceIds);
}

async function postJson(pathname, payload) {
  return fetch(`${reviewOrigin}${pathname}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

async function reviewerState(reviewer) {
  const response = await fetch(`${reviewOrigin}/__review__/api/state?reviewer=${encodeURIComponent(reviewer)}`);
  assert.equal(response.status, 200);
  return response.json();
}

async function runReviewServer(args) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, ['review-server.mjs', ...args], {
      cwd: ROOT,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let output = '';
    child.stdout.on('data', (chunk) => { output += chunk; });
    child.stderr.on('data', (chunk) => { output += chunk; });
    child.once('exit', (code, signal) => resolve({ code, signal, output }));
  });
}

async function isolatedVerificationContext(mode, pathname = '/host/network-ports') {
  // Keep the isolated checkout beside the task worktree so the strict loader can
  // resolve the pinned Vast CLI/self-test sibling repositories without network access.
  const fixtureRoot = await fs.mkdtemp(path.join(path.dirname(ROOT), '.vast-review-vv-'));
  const script = path.join(fixtureRoot, 'review-server.mjs');
  await fs.copyFile(path.join(ROOT, 'review-server.mjs'), script);
  if (!mode) {
    // Deliberately omit the canonical package: loader must fail closed.
  } else if (mode === 'malformed') {
    await fs.mkdir(path.join(fixtureRoot, 'verification'));
    await fs.writeFile(path.join(fixtureRoot, 'verification', 'host-docs-test-sets.json'), '{');
  } else {
    const verificationDir = path.join(fixtureRoot, 'verification');
    await fs.mkdir(verificationDir);
    await fs.copyFile(path.join(ROOT, '.git'), path.join(fixtureRoot, '.git'));
    for (const name of [
      'docs.json', 'host-docs-cli-command-check.json', 'host-docs-command-access.json',
      'host-docs-verification-inventory.json',
    ]) {
      await fs.copyFile(path.join(ROOT, name), path.join(fixtureRoot, name));
    }
    // Fixture drift must be applied to the exact reviewed source, not to
    // whichever merged working tree happens to run the suite.
    await materializeReviewedSourceFixture(fixtureRoot);
    await fs.cp(path.join(ROOT, 'verification', 'evidence'), path.join(verificationDir, 'evidence'), { recursive: true });
    for (const name of ['host-docs-test-sets.json', 'host-docs-test-results.json', 'host-docs-command-scores.json']) {
      await fs.copyFile(path.join(ROOT, 'verification', name), path.join(verificationDir, name));
    }
    const testSetsFile = path.join(verificationDir, 'host-docs-test-sets.json');
    const resultsFile = path.join(verificationDir, 'host-docs-test-results.json');
    const scoresFile = path.join(verificationDir, 'host-docs-command-scores.json');
    const results = JSON.parse(await fs.readFile(resultsFile, 'utf8'));
    const scores = JSON.parse(await fs.readFile(scoresFile, 'utf8'));
    const originalTestSetsBytes = await fs.readFile(testSetsFile);
    const testSets = JSON.parse(originalTestSetsBytes.toString('utf8'));
    const commandById = new Map();
    const allProjectionTargets = [];
    for (const page of testSets.pages) {
      const pageTarget = { page_id: page.page_id };
      allProjectionTargets.push(['PAGE', pageTarget]);
      for (const set of page.test_sets) {
        const setTarget = { ...pageTarget, test_set_id: set.test_set_id };
        allProjectionTargets.push(['TEST_SET', setTarget]);
        for (const branch of set.branches) {
          const branchTarget = { ...setTarget, branch_id: branch.branch_id };
          allProjectionTargets.push(['BRANCH', branchTarget]);
          for (const step of branch.steps) {
            const stepTarget = { ...branchTarget, step_id: step.step_id };
            allProjectionTargets.push(['STEP', stepTarget]);
            for (const command of step.commands) {
              const commandTarget = { ...stepTarget, command_id: command.command_id };
              allProjectionTargets.push(['COMMAND', commandTarget]);
              commandById.set(command.command_id, {
                ...commandTarget, route: page.route, procedureId: set.procedure_id,
                commandId: command.command_id, treatment: command.treatment,
                source: `${command.source.file}:${command.source.line_start}`,
              });
            }
          }
        }
      }
    }
    const activeFixtureAttempt = results.attempts.find((attempt) =>
      attempt.execution_state === 'EXECUTED' && !attempt.qualification_superseded_by);
    const fixtureAttemptId = activeFixtureAttempt.attempt_id;
    const fixtureEvidenceRef = activeFixtureAttempt.evidence_ref;
    const refreshScoreCounts = () => {
      scores.counts = {
        scored: scores.records.length,
        score_1: scores.records.filter((row) => row.score === 1).length,
        score_2: scores.records.filter((row) => row.score === 2).length,
        score_3: scores.records.filter((row) => row.score === 3).length,
        not_applicable: scores.not_applicable_records.length,
      };
    };
    const statusRecord = (level, target, evidenceId, currentStatus = 'PASS', attemptId = fixtureAttemptId) => ({
      level, target: { ...target }, current_status: currentStatus, attempt_id: attemptId,
      evidence_ids: [evidenceId],
    });
    const projectionTargets = [
      ['PAGE', { page_id: 'PAGE-host-market-metrics' }],
      ['TEST_SET', { page_id: 'PAGE-host-market-metrics', test_set_id: 'TS-MET-E02' }],
      ['BRANCH', { page_id: 'PAGE-host-market-metrics', test_set_id: 'TS-MET-E02', branch_id: 'MET-E02-current' }],
      ['STEP', { page_id: 'PAGE-host-market-metrics', test_set_id: 'TS-MET-E02', branch_id: 'MET-E02-current', step_id: 'MET-E02-current-s01' }],
      ['COMMAND', { page_id: 'PAGE-host-market-metrics', test_set_id: 'TS-MET-E02', branch_id: 'MET-E02-current', step_id: 'MET-E02-current-s01', command_id: 'CLM-582fe58ab6692d1a' }],
    ];
    const procedureFor = (records, fields = {}) => ({
      evidence_id: records[0].evidence_ids[0], attempt_id: records[0].attempt_id,
      method: 'Retained static procedure review', observation: 'Sanitized fixture procedure observation.',
      limitations: 'No live Host product behavior was exercised.',
      targets: records.map((record) => ({ level: record.level, target: record.target, vv_status: record.current_status })),
      ...fields,
    });
    const appendProcedure = (records, fields) => {
      results.procedure_results = [...(results.procedure_results || []), procedureFor(records, fields)];
    };
    const appendCommandEvidence = (commandId, evidenceId, vvStatus = 'PASS', fields = {}) => {
      results.command_results.push({
        evidence_id: evidenceId,
        attempt_id: fixtureAttemptId,
        evidence_ref: fixtureEvidenceRef,
        command_ids: [commandId],
        planned_form: 'fixture command --exact',
        process_exit_code: vvStatus === 'PASS' ? 0 : 1,
        vv_status: vvStatus,
        observation: 'The isolated command-execution fixture produced the requested result.',
        claim_limit: 'This is a loader regression fixture, not retained Host qualification evidence.',
        ...fields,
      });
    };
    const ensureScore = (commandId, evidenceIds, executionStatus = 'PASS', value = 2,
      directEvidenceIds = [], directRole = 'DIRECT_FUNCTIONAL_EXACT_FULL', directCeiling = directRole) => {
      const command = commandById.get(commandId);
      let score = scores.records.find((row) => row.command_id === commandId);
      if (!score) {
        score = { command_id: commandId, score: value, execution_status: executionStatus,
          rationale: 'Fixture score directly supports the selected command.', evidence_ids: evidenceIds };
        scores.records.push(score);
      }
      Object.assign(score, { page_route: command.route, procedure_id: command.procedureId,
        source: command.source, evidence_ids: evidenceIds, direct_evidence_ids: directEvidenceIds,
        execution_status: executionStatus, score: value });
      scores.direct_evidence_bindings = (scores.direct_evidence_bindings || [])
        .filter((binding) => binding.command_id !== commandId);
      for (const evidenceId of directEvidenceIds) {
        scores.direct_evidence_bindings.push({ command_id: commandId, evidence_id: evidenceId, role: directRole });
        const ceiling = (results.direct_proof_ceilings || []).find((row) => row.evidence_id === evidenceId);
        if (ceiling) ceiling.ceiling = directCeiling;
        else results.direct_proof_ceilings.push({ evidence_id: evidenceId, ceiling: directCeiling });
      }
      return score;
    };
    const fixtureTargetKey = (level, target) => [level, target.page_id, target.test_set_id,
      target.branch_id, target.step_id, target.command_id].filter((value) => value != null).join('\u0000');
    const baseRecords = results.current_status_projection.records;
    const baseEvidenceId = results.procedure_results[0].evidence_id;
    const projectionCounts = (records) => {
      const levels = ['PAGE', 'TEST_SET', 'BRANCH', 'STEP', 'COMMAND'];
      const statuses = ['PASS', 'FAIL', 'BLOCKED', 'UNVALIDATED', 'STALE', 'NOT_APPLICABLE'];
      const levelCounts = Object.fromEntries(levels.map((level) => [level, 0]));
      const statusCounts = Object.fromEntries(statuses.map((status) => [status, 0]));
      const byLevel = Object.fromEntries(levels.map((level) =>
        [level, Object.fromEntries(statuses.map((status) => [status, 0]))]));
      for (const record of records) {
        levelCounts[record.level] += 1;
        statusCounts[record.current_status] += 1;
        byLevel[record.level][record.current_status] += 1;
      }
      return { targets: records.length, levels: levelCounts, statuses: statusCounts, by_level: byLevel };
    };
    const projectionRecordFor = (level, target) => results.current_status_projection.records.find((record) =>
      fixtureTargetKey(record.level, record.target) === fixtureTargetKey(level, target));
    const useCurrentEvidence = (targets, evidenceId, currentStatus = 'PASS', fields = {}) => {
      const records = targets.map(([level, target]) => projectionRecordFor(level, target));
      for (const record of records) {
        record.evidence_ids = [evidenceId];
        record.current_status = currentStatus;
      }
      appendProcedure(records, fields);
      return records;
    };
    if (mode === 'snapshot-mismatch') {
      results.test_set_snapshot_sha256 = '0'.repeat(64);
    } else if (mode === 'valid-blocker-classification') {
      // The canonical Volume Offers package already exercises typed leaf and
      // derived blocker prerequisites; do not synthesize authority or runtime proof.
    } else if (mode === 'valid-current-status' || mode === 'valid-sanitized-current-status') {
      if (mode === 'valid-sanitized-current-status') {
        for (const procedure of results.procedure_results) {
          procedure.observation = `Inspected /Users/alice/private at 2001:db8::1 with token ${'a'.repeat(64)}.`;
          procedure.limitations = 'Machine 424242 used scratch path /var/folders/2f/private; password=fixture-secret.';
        }
        for (const commandResult of results.command_results) {
          commandResult.observation = 'Machine 424242 returned <img src=x onerror=alert(1)> at 2001:db8::1.';
          commandResult.claim_limit = 'Scratch path /Users/alice/private; token=fixture-secret.';
        }
        for (const score of scores.records) score.rationale = 'api_key=fixture-secret; output stayed relevant.';
      }
    } else if (mode === 'valid-history') {
      // Canonical FAQ and hardware-prep attempts retain failures and linked retests.
    } else if (mode === 'unknown-status-target' || mode === 'duplicate-status' || mode === 'unknown-status-attempt' ||
      mode === 'unknown-status-evidence' || mode === 'unsafe-status-attempt' || mode === 'partial-current-status' ||
      mode === 'mismatched-procedure-evidence' || mode === 'superseded-current-attempt' || mode === 'command-evidence-current-status') {
      const pageTarget = { page_id: 'PAGE-host-market-metrics' };
      const record = projectionRecordFor('PAGE', pageTarget);
      if (mode === 'unknown-status-target') record.target.page_id = 'PAGE-unknown';
      if (mode === 'unknown-status-attempt') record.attempt_id = 'ATTEMPT-unknown';
      if (mode === 'unknown-status-evidence') record.evidence_ids = ['EV-unknown'];
      if (mode === 'unsafe-status-attempt') record.attempt_id = '/private/tmp/attempt';
      if (mode === 'partial-current-status') record.current_status = 'PARTIAL';
      if (mode === 'mismatched-procedure-evidence') {
        record.evidence_ids = ['EV-MISMATCHED-PROJECTION-1'];
        appendProcedure([statusRecord('TEST_SET', { ...pageTarget, test_set_id: 'TS-MET-E02' },
          'EV-MISMATCHED-PROJECTION-1')]);
      }
      if (mode === 'superseded-current-attempt') {
        const superseded = results.attempts.find((attempt) => attempt.qualification_superseded_by);
        record.attempt_id = superseded.attempt_id;
      }
      if (mode === 'command-evidence-current-status') {
        record.evidence_ids = [results.command_results[0].evidence_id];
      }
      if (mode === 'duplicate-status') results.current_status_projection.records.push({ ...record, target: { ...record.target } });
    } else if (mode === 'partial-procedure-target') {
      results.procedure_results[0].targets[0].vv_status = 'PARTIAL';
    } else if (mode === 'valid-not-applicable' || mode === 'invalid-not-applicable-approval' ||
      mode === 'numeric-not-applicable-status' || mode === 'not-applicable-nondisplay') {
      if (mode === 'valid-not-applicable') {
        // Exercise a canonical approved display-only classification unchanged.
      } else {
      const requested = mode === 'not-applicable-nondisplay'
        ? [...commandById.values()].find((item) => item.treatment !== 'NON_EXECUTABLE_DISPLAY')
        : commandById.get(scores.not_applicable_records[0].command_id);
      const command = requested;
      if (mode === 'numeric-not-applicable-status') {
        const assessment = scores.not_applicable_records.shift();
        scores.records.push({ ...scores.records[0], command_id: assessment.command_id,
          procedure_id: assessment.procedure_id, page_route: assessment.page_route,
          source: assessment.source, execution_status: 'NOT_APPLICABLE',
          evidence_ids: assessment.evidence_ids, direct_evidence_ids: [], score: 2,
          rationale: 'Invalid numeric N/A fixture.' });
      } else if (mode === 'invalid-not-applicable-approval') {
        scores.not_applicable_records[0].approval_ref = 'APPROVAL:FIXTURE-1';
      } else if (mode === 'not-applicable-nondisplay') {
        scores.not_applicable_records[0].command_id = command.commandId;
      }
      }
    } else if (mode === 'assessment-current-status-mismatch') {
      const command = commandById.get('CLM-582fe58ab6692d1a');
      const target = { page_id: command.page_id, test_set_id: command.test_set_id, branch_id: command.branch_id,
        step_id: command.step_id, command_id: command.commandId };
      const assessed = statusRecord('COMMAND', target, 'EV-ASSESSMENT-PASS-1', 'PASS');
      const projected = projectionRecordFor('COMMAND', target);
      projected.current_status = 'BLOCKED';
      projected.evidence_ids = ['EV-PROJECTION-BLOCKED-2'];
      appendProcedure([assessed]);
      appendProcedure([projected]);
      ensureScore(command.commandId, ['EV-ASSESSMENT-PASS-1'], 'PASS', 2);
    } else if (mode === 'valid-score-status-separation') {
      // The canonical assessment manifest is context-only while exact command
      // execution evidence independently supplies current PASS results.
    } else if (mode === 'score3-current-not-pass') {
      const command = [...commandById.values()][0];
      const target = { page_id: command.page_id, test_set_id: command.test_set_id, branch_id: command.branch_id,
        step_id: command.step_id, command_id: command.commandId };
      useCurrentEvidence([['COMMAND', target]], 'EV-SCORE3-BLOCKED-1', 'BLOCKED');
      appendCommandEvidence(command.commandId, 'EV-SCORE3-DIRECT-PASS-1');
      ensureScore(command.commandId, ['EV-SCORE3-BLOCKED-1'], 'BLOCKED', 3,
        ['EV-SCORE3-DIRECT-PASS-1']);
    } else if (mode === 'score3-missing-direct-evidence' || mode === 'score3-duplicate-direct-evidence') {
      const commandId = 'CLM-582fe58ab6692d1a';
      appendCommandEvidence(commandId, 'EV-SCORE3-DIRECT-PASS-1');
      const directIds = mode === 'score3-duplicate-direct-evidence'
        ? ['EV-SCORE3-DIRECT-PASS-1', 'EV-SCORE3-DIRECT-PASS-1'] : [];
      ensureScore(commandId, [baseEvidenceId], 'PASS', 3, directIds);
    } else if (mode === 'score3-direct-not-pass') {
      const command = commandById.get('CLM-582fe58ab6692d1a');
      const target = { page_id: command.page_id, test_set_id: command.test_set_id,
        branch_id: command.branch_id, step_id: command.step_id, command_id: command.commandId };
      appendCommandEvidence(command.commandId, 'EV-SCORE3-DIRECT-BLOCKED-1', 'BLOCKED');
      ensureScore(command.commandId, [baseEvidenceId], 'PASS', 3, ['EV-SCORE3-DIRECT-BLOCKED-1']);
    } else if (mode === 'score3-direct-wrong-command') {
      const command = commandById.get('CLM-582fe58ab6692d1a');
      const other = [...commandById.values()].find((row) => row.commandId !== command.commandId);
      const otherTarget = { page_id: other.page_id, test_set_id: other.test_set_id,
        branch_id: other.branch_id, step_id: other.step_id, command_id: other.commandId };
      appendCommandEvidence(other.commandId, 'EV-SCORE3-DIRECT-WRONG-1');
      ensureScore(command.commandId, [baseEvidenceId], 'PASS', 3, ['EV-SCORE3-DIRECT-WRONG-1']);
    } else if (mode === 'score3-static-procedure-direct' || mode === 'score3-static-relabelled-full') {
      const command = commandById.get('CLM-582fe58ab6692d1a');
      const target = { page_id: command.page_id, test_set_id: command.test_set_id,
        branch_id: command.branch_id, step_id: command.step_id, command_id: command.commandId };
      appendProcedure([statusRecord('COMMAND', target, 'EV-SCORE3-STATIC-PASS-1', 'PASS')], {
        method: 'Static source conformance fixture',
        observation: 'The static fixture found matching command text.',
        limitations: 'No Host behavior or command execution was exercised.',
      });
      const role = mode === 'score3-static-relabelled-full'
        ? 'DIRECT_FUNCTIONAL_EXACT_FULL' : 'BOUNDED_STATIC_SUPPORT';
      ensureScore(command.commandId, [baseEvidenceId], 'PASS', 3, ['EV-SCORE3-STATIC-PASS-1'],
        role, 'BOUNDED_STATIC_SUPPORT');
    } else if (mode === 'score3-partial-relabelled-full') {
      const command = commandById.get('CLM-582fe58ab6692d1a');
      appendCommandEvidence(command.commandId, 'EV-SCORE3-PARTIAL-PASS-1');
      ensureScore(command.commandId, [baseEvidenceId], 'PASS', 3, ['EV-SCORE3-PARTIAL-PASS-1'],
        'DIRECT_FUNCTIONAL_EXACT_FULL', 'DIRECT_FUNCTIONAL_PARTIAL');
    } else if (mode === 'score3-scoped-superseded-direct') {
      const commandId = 'CLM-2c2c7d94c1bd259f';
      const attempt = results.attempts.find((row) => row.attempt_id === 'ATTEMPT-2026-08-31-HOST-PRIVILEGED-01');
      attempt.qualification_superseded_targets.command_ids.push(commandId);
      ensureScore(commandId, [baseEvidenceId], 'PASS', 3, ['EV-HOST04-DOCKER-RUNTIME']);
    } else if (mode === 'qualification-command-uncovered') {
      const attempt = results.attempts.find((row) =>
        row.attempt_id === 'ATTEMPT-2026-08-31-HOST-PRIVILEGED-01');
      attempt.qualification_superseded_targets.command_ids =
        attempt.qualification_superseded_targets.command_ids.filter((commandId) =>
          commandId !== 'CLM-ffda5e2c291c470e');
    } else if (mode === 'not-applicable-parent-child-mismatch') {
      const [, stepTarget] = allProjectionTargets.find(([level, target]) =>
        level === 'STEP' && allProjectionTargets.some(([childLevel, child]) => childLevel === 'COMMAND' &&
          child.page_id === target.page_id && child.test_set_id === target.test_set_id &&
          child.branch_id === target.branch_id && child.step_id === target.step_id));
      useCurrentEvidence([['STEP', stepTarget]], 'EV-FIXTURE-NOT-APPLICABLE-PARENT-1', 'NOT_APPLICABLE');
    } else if (mode === 'missing-attempt-evidence-ref') {
      results.attempts[0].evidence_ref = 'verification/evidence/missing/result.md';
    } else if (mode === 'unsafe-attempt-evidence-ref') {
      results.attempts[0].evidence_ref = '../outside.md';
    } else if (mode === 'nonportable-attempt-evidence-content') {
      await fs.appendFile(path.join(fixtureRoot, results.attempts[0].evidence_ref),
        '\nUntracked detail: .orchestra/private/result.html\n');
    } else if (mode === 'direct-command-missing-evidence-ref') {
      delete results.command_results.find((row) => row.evidence_id === 'EV-CLI05-MARKET-METRICS').evidence_ref;
    } else if (mode === 'schema-mismatch') {
      results.schema_version = '2.0';
    } else if (mode === 'record-type-mismatch') {
      scores.record_type = 'NOT_THE_SCORE_SCHEMA';
    } else if (mode === 'inventory-count-mismatch') {
      testSets.counts.pages += 1;
    } else if (mode === 'invalid-baseline-status') {
      testSets.pages[0].test_sets[0].execution_status = 'PARTIAL';
    } else if (mode === 'duplicate-canonical-command') {
      const commands = [...commandById.values()];
      const source = testSets.pages.flatMap((page) => page.test_sets).flatMap((set) => set.branches)
        .flatMap((branch) => branch.steps).flatMap((step) => step.commands);
      source.find((command) => command.command_id === commands[1].commandId).command_id = commands[0].commandId;
    } else if (mode === 'stale-page-source') {
      await fs.appendFile(path.join(fixtureRoot, 'host', 'market-metrics.mdx'), '\n<!-- stale fixture -->\n');
    } else if (mode === 'stale-rendered-dependency') {
      await fs.appendFile(path.join(fixtureRoot, 'snippets', 'notifications', 'channels.mdx'), '\n<!-- stale fixture -->\n');
    } else if (mode === 'stale-support-wrapper') {
      await fs.appendFile(path.join(fixtureRoot, 'host', 'cli', 'cancel-maint.mdx'), '\n<!-- stale fixture -->\n');
    } else if (mode === 'merged-current-host-nav') {
      const docsFile = path.join(fixtureRoot, 'docs.json');
      const docs = JSON.parse(await fs.readFile(docsFile, 'utf8'));
      const host = docs.navigation.tabs.find((tab) => tab.tab === 'Host');
      const added = ['machine-metrics', 'upgrade-kernel', 'disable-ssh-password-login', 'machine-offline'];
      for (const slug of added) {
        await fs.copyFile(path.join(fixtureRoot, 'host', 'market-metrics.mdx'), path.join(fixtureRoot, 'host', `${slug}.mdx`));
        host.groups[4].pages.push(`host/${slug}`);
      }
      await fs.writeFile(docsFile, JSON.stringify(docs, null, 2) + '\n');
    } else if (mode === 'removed-current-nav-route') {
      const docsFile = path.join(fixtureRoot, 'docs.json');
      const docs = JSON.parse(await fs.readFile(docsFile, 'utf8'));
      const host = docs.navigation.tabs.find((tab) => tab.tab === 'Host');
      const removeRoute = (pages) => pages.filter((item) => item !== 'host/network-ports')
        .map((item) => typeof item === 'string' ? item : { ...item, pages: removeRoute(item.pages) });
      for (const group of host.groups) group.pages = removeRoute(group.pages);
      assert.ok(!JSON.stringify(host).includes('host/network-ports'), 'removed-route fixture must actually remove the route');
      await fs.writeFile(docsFile, JSON.stringify(docs, null, 2) + '\n');
    } else if (mode === 'nested-current-nav') {
      const docsFile = path.join(fixtureRoot, 'docs.json');
      const docs = JSON.parse(await fs.readFile(docsFile, 'utf8'));
      const host = docs.navigation.tabs.find((tab) => tab.tab === 'Host');
      host.groups[0].pages = [{ group: 'Nested', pages: host.groups[0].pages }];
      await fs.writeFile(docsFile, JSON.stringify(docs, null, 2) + '\n');
    } else if (mode === 'duplicate-current-nav-route') {
      const docsFile = path.join(fixtureRoot, 'docs.json');
      const docs = JSON.parse(await fs.readFile(docsFile, 'utf8'));
      const host = docs.navigation.tabs.find((tab) => tab.tab === 'Host');
      host.groups[0].pages.push('host/hosting-overview');
      await fs.writeFile(docsFile, JSON.stringify(docs, null, 2) + '\n');
    } else if (mode === 'traversal-current-nav-route') {
      const docsFile = path.join(fixtureRoot, 'docs.json');
      const docs = JSON.parse(await fs.readFile(docsFile, 'utf8'));
      const host = docs.navigation.tabs.find((tab) => tab.tab === 'Host');
      host.groups[0].pages.push('host/../review-questions');
      await fs.writeFile(docsFile, JSON.stringify(docs, null, 2) + '\n');
    } else if (mode === 'invalid-canonical-route') {
      testSets.pages[0].route = '/host/../review-questions';
    } else if (mode === 'invalid-step-source-span') {
      testSets.pages[0].test_sets[0].branches[0].steps[0].source_lines = [{ start: 1, end: 999999 }];
    } else if (mode === 'invalid-step-source-section') {
      testSets.pages[0].test_sets[0].branches[0].steps[0].source_sections = ['Heading that does not exist'];
    } else if (mode === 'invalid-command-source-span') {
      const command = testSets.pages.flatMap((page) => page.test_sets).flatMap((set) => set.branches)
        .flatMap((branch) => branch.steps).flatMap((step) => step.commands)[0];
      command.source.line_start = 1;
      command.source.line_end = 1;
    } else if (mode === 'invalid-command-source-section') {
      const command = testSets.pages.flatMap((page) => page.test_sets).flatMap((set) => set.branches)
        .flatMap((branch) => branch.steps).flatMap((step) => step.commands)[0];
      command.source.section = 'Heading that does not own this command';
    }
    if (mode === 'missing-assessment-coverage') scores.records.pop();
    if (mode === 'missing-current-projection') results.current_status_projection.records.pop();
    if (mode === 'unknown-score-command') scores.records[0].command_id = 'CLM-unknown';
    if (mode === 'score-empty-evidence') scores.records[0].evidence_ids = [];
    if (mode === 'pass-missing-direct-evidence') {
      const score = scores.records.find((row) => row.execution_status === 'PASS' && row.score === 2);
      score.direct_evidence_ids = [];
      scores.direct_evidence_bindings = scores.direct_evidence_bindings.filter((row) =>
        row.command_id !== score.command_id);
    }
    if (mode === 'score-duplicate-evidence') scores.records[0].evidence_ids = [scores.records[0].evidence_ids[0], scores.records[0].evidence_ids[0]];
    if (mode === 'score-wrong-command-evidence') {
      const score = scores.records[0];
      score.evidence_ids = [results.command_results.find((row) => !row.command_ids.includes(score.command_id)).evidence_id];
    }
    if (mode === 'score-ancestry-mismatch') scores.records[0].page_route = '/host/wrong-page';
    if (mode === 'score-source-mismatch') scores.records[0].source = 'host/wrong-page.mdx:1';
    if (mode === 'withdrawn-current-status-mismatch') {
      scores.withdrawn_records.find((row) => commandById.has(row.command_id)).current_execution_status = 'BLOCKED';
    }
    if (mode === 'withdrawn-current-score-mismatch') {
      const withdrawn = scores.withdrawn_records.find((row) => commandById.has(row.command_id));
      withdrawn.current_score = withdrawn.current_score === 1 ? 2 : 1;
    }
    if (mode === 'invalid-retired-withdrawal') {
      const retired = scores.withdrawn_records.find((row) => !commandById.has(row.command_id));
      retired.current_execution_status = 'PASS';
      retired.current_score = 2;
    }
    refreshScoreCounts();
    const commandCountFields = {
      PASS: 'command_pass', BLOCKED: 'command_blocked', FAIL: 'command_fail',
      UNVALIDATED: 'command_unvalidated', NOT_APPLICABLE: 'command_not_applicable',
    };
    results.counts.command_runs = results.command_results.length;
    for (const [status, field] of Object.entries(commandCountFields)) {
      results.counts[field] = results.command_results.filter((row) => row.vv_status === status).length;
    }
    results.current_status_projection.counts = projectionCounts(results.current_status_projection.records);
    if (mode === 'projection-count-mismatch') results.current_status_projection.counts.targets += 1;
    await fs.writeFile(testSetsFile, JSON.stringify(testSets));
    const snapshot = crypto.createHash('sha256').update(await fs.readFile(testSetsFile)).digest('hex');
    if (mode !== 'snapshot-mismatch') {
      results.test_set_snapshot_sha256 = snapshot;
    }
    scores.test_set_snapshot_sha256 = snapshot;
    for (const record of results.current_status_projection.records) {
      record.status_basis.source_snapshot_sha256 = snapshot;
    }
    if (mode !== 'invalid-not-applicable-approval') {
      for (const assessment of scores.not_applicable_records) {
        assessment.approval_ref = `CANONICAL_NON_EXECUTABLE_DISPLAY:${snapshot}`;
      }
    }
    await fs.writeFile(resultsFile, JSON.stringify(results));
    if (mode === 'score-count-mismatch') {
      scores.counts.scored += 1;
    }
    await fs.writeFile(scoresFile, JSON.stringify(scores));
  }
  const port = await freePort();
  const debugFixture = process.env.VAST_TEST_DEBUG === '1';
  const child = spawn(process.execPath, [script, '--port', String(port), '--target', targetOrigin,
    '--dir', path.join(fixtureRoot, 'feedback')], {
    cwd: fixtureRoot, stdio: debugFixture ? 'inherit' : 'ignore',
    env: debugFixture ? { ...process.env, VAST_REVIEW_DEBUG: '1' } : process.env,
  });
  try {
    // Pinned Git-blob integrity validation takes longer than live-file reads.
    // Keep a bounded startup deadline without weakening any integrity check.
    for (let i = 0; i < 400; i += 1) {
      try {
        const response = await fetch(`http://127.0.0.1:${port}/__review__/api/context?path=${encodeURIComponent(pathname)}`);
        // Consume the response body before the `finally` block terminates the
        // isolated server; returning the unresolved promise makes large
        // contexts race the shutdown and intermittently fail with UND_ERR_SOCKET.
        if (response.ok) return await response.json();
      } catch { /* wait for startup */ }
      await new Promise((resolve) => setTimeout(resolve, 25));
    }
    throw new Error('isolated review server did not start');
  } finally {
    if (child.exitCode == null) child.kill('SIGTERM');
    await new Promise((resolve) => child.exitCode == null ? child.once('exit', resolve) : resolve());
    await fs.rm(fixtureRoot, { recursive: true, force: true });
  }
}

async function startHistoricalReviewServer() {
  historicalFixtureRoot = await fs.mkdtemp(path.join(path.dirname(ROOT), '.vast-review-history-'));
  await fs.copyFile(path.join(ROOT, 'review-server.mjs'), path.join(historicalFixtureRoot, 'review-server.mjs'));
  const gitSource = path.join(ROOT, '.git');
  const gitStat = await fs.lstat(gitSource);
  if (gitStat.isDirectory()) await fs.cp(gitSource, path.join(historicalFixtureRoot, '.git'), { recursive: true });
  else await fs.copyFile(gitSource, path.join(historicalFixtureRoot, '.git'));
  await materializeReviewedSourceFixture(historicalFixtureRoot);
  await fs.mkdir(path.join(historicalFixtureRoot, 'verification'));
  for (const name of [
    'docs.json', 'host-docs-cli-command-check.json', 'host-docs-command-access.json',
    'host-docs-verification-inventory.json',
  ]) {
    if (name !== 'docs.json') await fs.copyFile(path.join(ROOT, name), path.join(historicalFixtureRoot, name));
  }
  await fs.cp(path.join(ROOT, 'verification', 'evidence'), path.join(historicalFixtureRoot, 'verification', 'evidence'),
    { recursive: true });
  for (const name of ['host-docs-test-sets.json', 'host-docs-test-results.json', 'host-docs-command-scores.json']) {
    await fs.copyFile(path.join(ROOT, 'verification', name), path.join(historicalFixtureRoot, 'verification', name));
  }
  const port = await freePort();
  historicalReviewOrigin = `http://127.0.0.1:${port}`;
  historicalReviewProcess = spawn(process.execPath, ['review-server.mjs', '--port', String(port), '--target', targetOrigin,
    '--dir', path.join(historicalFixtureRoot, 'feedback')], {
    cwd: historicalFixtureRoot, stdio: ['ignore', 'pipe', 'pipe'],
  });
  historicalReviewProcess.stdout.on('data', (chunk) => { historicalReviewOutput += chunk; });
  historicalReviewProcess.stderr.on('data', (chunk) => { historicalReviewOutput += chunk; });
  for (let i = 0; i < 160; i += 1) {
    if (historicalReviewProcess.exitCode != null) {
      throw new Error(`historical review server exited early (${historicalReviewProcess.exitCode})\n${historicalReviewOutput}`);
    }
    try {
      const response = await fetch(`${historicalReviewOrigin}/__review__/api/context?path=%2Fhost%2Fverification-stages`);
      if (response.ok) { await response.arrayBuffer(); return; }
    } catch { /* wait for startup */ }
    await new Promise((resolve) => setTimeout(resolve, 25));
  }
  throw new Error(`historical review server did not start\n${historicalReviewOutput}`);
}

before(async () => {
  targetServer = http.createServer((req, res) => {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><body><h1>Stub preview</h1><p>${req.url}</p></body></html>`);
  });
  const targetPort = await listen(targetServer);
  const reviewPort = await freePort();
  targetOrigin = `http://127.0.0.1:${targetPort}`;
  reviewOrigin = `http://127.0.0.1:${reviewPort}`;
  feedbackDir = await fs.mkdtemp(path.join(os.tmpdir(), 'vast-review-context-'));
  reviewSourceSha256AtStartup = crypto.createHash('sha256')
    .update(await fs.readFile(path.join(ROOT, 'review-server.mjs'))).digest('hex');
  reviewProcess = spawn(process.execPath, [
    'review-server.mjs', '--port', String(reviewPort), '--target', targetOrigin, '--dir', feedbackDir,
  ], { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] });
  reviewProcess.stdout.on('data', (chunk) => { reviewOutput += chunk; });
  reviewProcess.stderr.on('data', (chunk) => { reviewOutput += chunk; });
  await waitForReviewServer();
  await startHistoricalReviewServer();
});

after(async () => {
  if (reviewProcess && reviewProcess.exitCode == null) {
    reviewProcess.kill('SIGTERM');
    await new Promise((resolve) => reviewProcess.once('exit', resolve));
  }
  if (historicalReviewProcess && historicalReviewProcess.exitCode == null) {
    historicalReviewProcess.kill('SIGTERM');
    await new Promise((resolve) => historicalReviewProcess.once('exit', resolve));
  }
  if (historicalFixtureRoot) await fs.rm(historicalFixtureRoot, { recursive: true, force: true });
  if (targetServer) await new Promise((resolve) => targetServer.close(resolve));
  if (feedbackDir) await fs.rm(feedbackDir, { recursive: true, force: true });
});

test('Review server rejects non-loopback bind addresses', async () => {
  const result = await runReviewServer(['--host', '0.0.0.0', '--port', '0']);
  assert.notEqual(result.code, 0);
  assert.equal(result.signal, null);
  assert.match(result.output, /--host must be loopback-only/);
});

test('Context responses identify the exact review-server source loaded at startup', async () => {
  const response = await fetch(`${reviewOrigin}/__review__/api/context?path=%2Fhost%2Fhost-teams`);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('x-vast-review-source-sha256'), reviewSourceSha256AtStartup);
  const currentSourceSha256 = crypto.createHash('sha256')
    .update(await fs.readFile(path.join(ROOT, 'review-server.mjs'))).digest('hex');
  assert.equal(response.headers.get('x-vast-review-source-sha256'), currentSourceSha256);
});

test('Host Teams shows its Jira sources and only its page blockers', async () => {
  const context = await contextFor('/host/host-teams');
  assert.deepEqual(context.epics.map((issue) => issue.key), ['CON-1187']);
  assert.deepEqual(context.issues.map((issue) => issue.key), ['CON-1581', 'CON-1584']);
  for (const issue of [...context.epics, ...context.issues]) {
    assert.equal(issue.statusAsOf, '2026-07-13');
    assert.equal(issue.statusVerification, 'UNVERIFIED_SNAPSHOT');
  }
  assert.equal(context.blockers.length, 4);
  assert.ok(context.blockers.some((item) => item.question.includes('accrued earnings')));
  assert.ok(context.blockers.every((item) => item.issue.url.startsWith('https://vastai.atlassian.net/browse/')));
});

test('Self-Test reference links both epics without stale implementation blockers', async () => {
  const context = await contextFor('/host/self-test-reference');
  assert.deepEqual(context.epics.map((issue) => issue.key), ['CON-1187', 'CON-1509']);
  for (const key of ['CON-1515', 'CON-1513', 'CON-1510', 'CON-1583', 'CON-1419']) {
    assert.ok(context.issues.some((issue) => issue.key === key), `missing ${key}`);
  }
  assert.equal(context.blockers.length, 1);
  assert.ok(context.blockers.some((item) => item.question.includes('queue and wait-time')));
  assert.ok(context.blockers.every((item) => !item.question.includes('actual-versus-required')));
  assert.ok(context.blockers.every((item) => !item.question.includes('source-repository dispatch')));
});

test('Diagnostics no longer reports merged dump-logs documentation as missing', async () => {
  const context = await contextFor('/host/common-errors-diagnostics');
  assert.ok(context.issues.some((issue) => issue.key === 'CON-1519'));
  assert.ok(context.blockers.every((item) => !item.question.includes('vastai dump-logs')));
});

test('Network page receives network blockers without unrelated Teams blockers', async () => {
  const context = await contextFor('/host/network-ports');
  assert.deepEqual(context.issues.map((issue) => issue.key), ['CON-1517', 'CON-1514']);
  assert.ok(context.blockers.some((item) => item.question.includes('TCP/UDP')));
  assert.ok(context.blockers.every((item) => item.issue.key === 'CON-1514'));
});

test('Page context joins only sanitized page-scoped V&V evidence', async () => {
  const context = await contextFor('/host/market-metrics');
  assert.equal(context.verification.available, true);
  assert.equal(context.verification.totals.testSets, 3);
  assert.equal(context.verification.totals.branches, 7);
  assert.equal(context.verification.totals.steps, 10);
  assert.equal(context.verification.totals.commands, 6);
  assert.ok(context.verification.totals.observations >= 4);
  assert.ok(Number.isInteger(context.verification.totals.notApplicableAssessments));
  assert.equal(context.verification.testSets[0].totals.testSets, 1);
  assert.equal(context.verification.testSets[0].totals.branches, 2);
  assert.equal(context.verification.testSets[0].totals.steps, 3);
  assert.equal(context.verification.testSets[0].totals.commands, 1);
  const cliMatrix = context.verification.testSets.find((set) => set.title === 'CLI market query matrix');
  assert.equal(cliMatrix.totals.testSets, 1);
  assert.equal(cliMatrix.totals.branches, 4);
  assert.equal(cliMatrix.totals.steps, 4);
  assert.equal(cliMatrix.totals.commands, 4);
  assert.ok(cliMatrix.totals.observations >= 4);
  const commands = context.verification.testSets.flatMap((set) =>
    set.branches.flatMap((branch) => branch.steps.flatMap((step) => step.commands)));
  // The retained sandbox BLOCKED and isolated PASS CLI-install attempts add two
  // history rows for the same install carrier. The later REST authorization
  // attempt adds one page-scoped row for the curl carrier.
  assert.equal(commands.flatMap((command) => command.evidence).length, 9);
  assert.ok(commands.flatMap((command) => command.evidence).every((row) => /^EV-[A-Z0-9-]+$/.test(row.ref)));
  assert.ok(commands.filter((command) => command.score || command.notApplicableAssessment).length >= 3);
  const directlyScored = commands.find((command) => command.score?.directEvidence.length > 0);
  assert.ok(directlyScored.score.directEvidence.every((row) =>
    /^verification\/evidence\/[A-Za-z0-9._/-]+$/.test(row.evidenceRef)));
  const retained = await fetch(`${reviewOrigin}/__review__/evidence?ref=${encodeURIComponent(
    directlyScored.score.directEvidence[0].evidenceRef)}`);
  assert.equal(retained.status, 200);
  assert.match(retained.headers.get('content-type'), /^text\/plain/);
  assert.ok((await retained.text()).length > 20);
  assert.equal((await fetch(`${reviewOrigin}/__review__/evidence?ref=${encodeURIComponent('../outside')}`)).status, 404);
  const search = await contextFor('/host/not-in-search');
  const searchCommands = search.verification.testSets.flatMap((set) => set.branches)
    .flatMap((branch) => branch.steps).flatMap((step) => step.commands);
  const score3 = searchCommands.find((command) => command.score?.value === 3);
  assert.ok(score3.score.directEvidence.length > 0);
  assert.ok(score3.score.directEvidence.every((row) => row.status === 'PASS'));
  assert.ok(score3.score.directEvidence.some((row) =>
    ['DIRECT_FUNCTIONAL_EXACT_FULL', 'DIRECT_FUNCTIONAL_EQUIVALENT_FULL'].includes(row.proofRole)));
  const serialized = JSON.stringify(context.verification);
  assert.doesNotMatch(serialized,
    /evidence_ref|source_file|source_context|source_sections|source_lines|line_start|line_end|test_set_snapshot_sha256|\/private\/tmp|\/Users\//);

  const network = await contextFor('/host/network-ports');
  const networkCommands = network.verification.testSets.flatMap((set) =>
    set.branches.flatMap((branch) => branch.steps.flatMap((step) => step.commands)));
  const redacted = networkCommands.find((command) => command.id === 'CLM-f93e44da84eeeef6');
  assert.match(redacted.text, /\[network-address\]/);
  assert.doesNotMatch(redacted.text, /(?:\d{1,3}\.){3}\d{1,3}/);
});

test('Self-test command proof keeps pinned source signatures separate from runtime status', async () => {
  const context = await contextFor('/host/how-to-self-test');
  assert.equal(context.verification.available, true);
  const commands = context.verification.testSets.flatMap((set) => set.branches)
    .flatMap((branch) => branch.steps).flatMap((step) => step.commands);
  const byId = new Map(commands.map((command) => [command.id, command]));
  const revision = 'ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd';
  const expectedSources = new Map([
    ['CLM-b3cd48630e5f2b0c', {
      findingId: 'cli-dae1e5fb9b',
      href: `https://github.com/vast-ai/vast-cli/blob/${revision}/vastai/cli/commands/auth.py#L199-L204`,
      path: 'vastai/cli/commands/auth.py', lineStart: 199, lineEnd: 204, symbol: 'set__api_key',
    }],
    ['CLM-3ba3b25f5c3ddac1', {
      findingId: 'cli-4caeeed44e',
      href: `https://github.com/vast-ai/vast-cli/blob/${revision}/vastai/cli/commands/machines.py#L699-L717`,
      path: 'vastai/cli/commands/machines.py', lineStart: 699, lineEnd: 717, symbol: 'self_test__machine',
    }],
    ['CLM-3fa5d5948b34fc6a', {
      findingId: 'cli-268cbc7b03',
      href: `https://github.com/vast-ai/vast-cli/blob/${revision}/vastai/cli/commands/machines.py#L699-L717`,
      path: 'vastai/cli/commands/machines.py', lineStart: 699, lineEnd: 717, symbol: 'self_test__machine',
    }],
  ]);
  for (const [commandId, expected] of expectedSources) {
    const command = byId.get(commandId);
    assert.ok(command, commandId);
    assert.equal(command.sourceSignature.status, 'PASS');
    assert.equal(command.sourceSignature.result, 'pass');
    assert.equal(command.sourceSignature.sourceRevision, revision);
    assert.match(command.sourceSignature.claimLimit, /Static parser\/handler registration only/);
    assert.deepEqual(command.sourceSignature.handlerSource, {
      repository: 'vast-ai/vast-cli', revision, path: expected.path, symbol: expected.symbol,
      lineStart: expected.lineStart, lineEnd: expected.lineEnd, href: expected.href,
    });
    assert.equal(command.sourceSignature.recordHref,
      `/__review__/cli-signature?finding=${expected.findingId}&binding=${commandId}`);
  }

  const setApiKey = byId.get('CLM-b3cd48630e5f2b0c');
  assert.equal(setApiKey.currentStatus, 'FAIL');
  assert.equal(setApiKey.verificationContract.basisKind, 'CONFIRMED_DEFECT');
  assert.match(setApiKey.currentObservation, /mode 0644/);
  assert.deepEqual(setApiKey.score.directEvidence.map((row) =>
    [row.status, row.proofRole, row.binding]), [
    ['FAIL', 'DIRECT_FUNCTIONAL_PARTIAL', setApiKey.id],
  ]);

  const plainSelfTest = byId.get('CLM-3ba3b25f5c3ddac1');
  assert.equal(plainSelfTest.currentStatus, 'UNVALIDATED');
  assert.equal(plainSelfTest.verificationContract.basisKind, 'NO_CLAIM_SUITABLE_EVIDENCE');
  assert.deepEqual(plainSelfTest.verificationContract.requiredEvidenceTypes,
    ['RUNTIME_OR_UI_OBSERVATION']);
  assert.match(plainSelfTest.verificationContract.nextAction,
    /representative idle listed Host/);
  assert.doesNotMatch(plainSelfTest.verificationContract.nextAction,
    /REPOSITORY_STATIC_CHECK/);
  assert.match(plainSelfTest.currentLimitations, /Static source\/topology\/accounting evidence only/);
  assert.deepEqual(plainSelfTest.score.directEvidence, []);
  assert.match(plainSelfTest.sourceSignature.claimLimit,
    /No API command, Host operation, credentialed authentication, rental, or workload was executed/);

  const supportBundle = byId.get('CLM-3fa5d5948b34fc6a');
  assert.equal(supportBundle.currentStatus, 'BLOCKED');
  assert.equal(supportBundle.verificationContract.basisKind, 'UNAVAILABLE_PREREQUISITE');
  assert.equal(supportBundle.verificationContract.unavailablePrerequisite.kind, 'PERMISSION');
  assert.match(supportBundle.currentObservation, /reached select_offer.*api_permission_failed/);
  assert.deepEqual(supportBundle.score.directEvidence.map((row) =>
    [row.status, row.proofRole, row.binding]), [
    ['BLOCKED', 'DIRECT_FUNCTIONAL_PARTIAL', supportBundle.id],
  ]);

  assert.notEqual(setApiKey.sourceSignature.status, setApiKey.currentStatus);
  assert.notEqual(plainSelfTest.sourceSignature.status, plainSelfTest.currentStatus);
  assert.notEqual(supportBundle.sourceSignature.status, supportBundle.currentStatus);
});

test('VM command proof does not promote incomplete parent procedures', async () => {
  const context = await contextFor('/host/vms');
  assert.equal(context.verification.available, true);
  const inspectOrDisable = context.verification.testSets.find((set) => set.id === 'TS-VM-E01');
  const commands = inspectOrDisable.branches.flatMap((branch) => branch.steps)
    .flatMap((step) => step.commands);
  const check = commands.find((command) => command.id === 'CLM-ca44522b22c4c5ee');
  const disable = commands.find((command) => command.id === 'CLM-9cba75bbdc780804');

  assert.equal(check.currentStatus, 'PASS');
  assert.equal(check.score.executionStatus, 'PASS');
  assert.deepEqual(check.score.directEvidence.map((row) =>
    [row.id, row.status, row.proofRole, row.binding]), [[
    'EV-HOST-SAFE-READONLY-02-VM-CHECK', 'PASS', 'DIRECT_FUNCTIONAL_EXACT_FULL', check.id,
  ]]);
  assert.match(check.score.directEvidence[0].limitations, /state-query carrier only/);

  assert.equal(disable.currentStatus, 'UNVALIDATED');
  assert.equal(disable.verificationContract.basisKind, 'NO_CLAIM_SUITABLE_EVIDENCE');
  assert.deepEqual(disable.verificationContract.requiredEvidenceTypes,
    ['CANONICAL_IMPLEMENTATION_SOURCE', 'RUNTIME_OR_UI_OBSERVATION']);
  assert.match(disable.verificationContract.nextAction,
    /check → off → check → on -f → check/);
  assert.deepEqual(disable.score.directEvidence, []);
  assert.ok(disable.withdrawnRecords.length > 0);
  assert.ok(disable.withdrawnRecords.every((row) => /improperly configured target/i.test(row.reason)));
  assert.ok(disable.withdrawnRecords.every((row) =>
    /does not restore the withdrawn runtime PASS/i.test(row.currentReassessment)));

  const checkBranch = inspectOrDisable.branches.find((branch) => branch.id === 'VM-E01-B-check');
  assert.equal(checkBranch.currentStatus, 'UNVALIDATED');
  assert.equal(checkBranch.steps[0].currentStatus, 'UNVALIDATED');
  assert.equal(inspectOrDisable.currentStatus, 'UNVALIDATED');
  assert.equal(context.verification.currentStatus, 'BLOCKED');
  assert.notEqual(checkBranch.currentStatus, 'PASS');
  assert.notEqual(inspectOrDisable.currentStatus, 'PASS');
  assert.notEqual(context.verification.currentStatus, 'PASS');
});

test('Exact CLI-signature and retained-evidence links preserve command proof context', async () => {
  const context = await contextFor('/host/how-to-self-test');
  const commands = context.verification.testSets.flatMap((set) => set.branches)
    .flatMap((branch) => branch.steps).flatMap((step) => step.commands);
  const setApiKey = commands.find((command) => command.id === 'CLM-b3cd48630e5f2b0c');
  const plainSelfTest = commands.find((command) => command.id === 'CLM-3ba3b25f5c3ddac1');

  const signatureResponse = await fetch(`${reviewOrigin}${setApiKey.sourceSignature.recordHref}`);
  assert.equal(signatureResponse.status, 200);
  assert.match(signatureResponse.headers.get('content-type'), /^text\/plain/);
  const signature = await signatureResponse.text();
  assert.match(signature, /^Exact command source\/signature binding/m);
  assert.match(signature, /^Page: \/host\/how-to-self-test$/m);
  assert.match(signature, /^Heading: Before You Run It$/m);
  assert.match(signature, /^Command: vastai set api-key <API_KEY>$/m);
  assert.match(signature, /^Command ID: CLM-b3cd48630e5f2b0c$/m);
  assert.match(signature, /^Static signature result: PASS$/m);
  assert.match(signature,
    /^Canonical source URL: https:\/\/github\.com\/vast-ai\/vast-cli\/blob\/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd\/vastai\/cli\/commands\/auth\.py#L199-L204$/m);
  assert.match(signature, /proves only.*registered in the pinned CLI source.*not runtime proof/s);

  const wrongBinding = await fetch(`${reviewOrigin}/__review__/cli-signature?finding=${
    encodeURIComponent(setApiKey.sourceSignature.findingId)}&binding=${encodeURIComponent(plainSelfTest.id)}`);
  assert.equal(wrongBinding.status, 404);
  assert.equal(await wrongBinding.text(), 'Exact CLI signature binding not found.');

  const runtimeEvidence = setApiKey.score.directEvidence[0];
  const runtimeResponse = await fetch(`${reviewOrigin}/__review__/evidence?ref=${
    encodeURIComponent(runtimeEvidence.evidenceRef)}&binding=${encodeURIComponent(setApiKey.id)}`);
  assert.equal(runtimeResponse.status, 200);
  assert.match(runtimeResponse.headers.get('content-type'), /^text\/html/);
  const runtime = await runtimeResponse.text();
  assert.match(runtime, /<pre>Reviewer navigation context \(generated; not retained evidence\)/);
  assert.match(runtime, /^Exact command evidence binding$/m);
  assert.match(runtime, /^Page: \/host\/how-to-self-test$/m);
  assert.match(runtime, /^Heading: Before You Run It$/m);
  assert.match(runtime, /^Command: vastai set api-key &lt;API_KEY&gt;$/m);
  assert.match(runtime, /^Evidence proof role: DIRECT_FUNCTIONAL_PARTIAL$/m);
  assert.match(runtime, /id="review-page-link" href="\/host\/how-to-self-test"/);
  assert.match(runtime,
    /id="review-heading-link" href="\/host\/how-to-self-test#before-you-run-it"/);
  assert.match(runtime, /The retained artifact begins below\. This generated header is not proof\./);

  const accountingEvidence = plainSelfTest.currentEvidence[0];
  const accountingResponse = await fetch(`${reviewOrigin}/__review__/evidence?ref=${
    encodeURIComponent(accountingEvidence.evidenceRef)}&binding=${encodeURIComponent(plainSelfTest.id)}`);
  assert.equal(accountingResponse.status, 200);
  assert.match(accountingResponse.headers.get('content-type'), /^text\/html/);
  const accounting = await accountingResponse.text();
  assert.match(accounting, /^Exact command evidence binding$/m);
  assert.match(accounting, /^Page: \/host\/how-to-self-test$/m);
  assert.match(accounting, /^Heading: Run The Test$/m);
  assert.match(accounting, /^Command: vastai self-test machine &lt;machine_id&gt;$/m);
  assert.match(accounting, /^Evidence proof role: ACCOUNTING_STATUS_DERIVATION_ONLY_NOT_RUNTIME_PROOF$/m);
  assert.match(accounting, /id="review-page-link" href="\/host\/how-to-self-test"/);
  assert.match(accounting,
    /id="review-heading-link" href="\/host\/how-to-self-test#run-the-test"/);
  assert.match(accounting,
    /explains status classification\/accounting only\. It does not show that the command executed or worked\./);
  assert.match(accounting, /The retained artifact begins below\. This generated header is not proof\./);

  const rebaseRef =
    'verification/evidence/2026-09-03-host-repository-rebase-01/result.md';
  const boundNavigationCases = [
    ['VOL-C01', '/host/volume-offers', null],
    ['SUPPORT-CLI-cancel-maint', '/host/cli/cancel-maint', null],
    ['PAGE:PAGE-host-hosting-overview', '/host/hosting-overview',
      '/host/hosting-overview#maintenance'],
  ];
  for (const [binding, pageHref, headingHref] of boundNavigationCases) {
    const response = await fetch(`${reviewOrigin}/__review__/evidence?ref=${
      encodeURIComponent(rebaseRef)}&binding=${encodeURIComponent(binding)}`);
    assert.equal(response.status, 200, binding);
    assert.match(response.headers.get('content-type'), /^text\/html/, binding);
    const evidenceHtml = await response.text();
    assert.match(evidenceHtml,
      new RegExp(`id="review-page-link" href="${pageHref.replaceAll('/', '\\/')}"`),
      binding);
    if (headingHref) {
      assert.match(evidenceHtml,
        new RegExp(`id="review-heading-link" href="${headingHref.replaceAll('/', '\\/')}"`),
        binding);
    }
  }
});

test('Host V&V context separates non-command checks, executable targets, and display-only references', async () => {
  const overview = await contextFor('/host/hosting-overview');
  assert.equal(overview.verification.available, true);
  assert.equal(overview.verification.totals.commands, 0);
  assert.equal(overview.verification.totals.executableIntentCommands, 0);
  assert.equal(overview.verification.totals.displayOnlyCommands, 0);
  assert.equal(overview.verification.totals.nonCommandSteps, overview.verification.totals.steps);
  assert.ok(Number.isInteger(overview.verification.totals.retainedEvidenceRecords));
  assert.deepEqual(overview.verification.checkedContent,
    { route: '/host/hosting-overview', pageTitle: 'Hosting Overview', sections: [] });
  assert.ok(overview.verification.testSets.every((set) => set.totals.commands === 0));
  assert.ok(overview.verification.testSets.every((set) => set.branches.every((branch) =>
    branch.steps.every((step) => step.executionClassification))));
  assert.ok(overview.verification.testSets.flatMap((set) => set.branches).flatMap((branch) => branch.steps)
    .some((step) => step.executionClassification === 'MANUAL_OR_CONTEXT'));
  const contractModel = overview.verification.testSets.find((set) => set.id === 'TS-HOV-C01');
  assert.deepEqual(contractModel.checkedContent.sections,
    ['Offers And Rental Contracts', 'The Rental Contract', 'Volume Offers', 'Maintenance']);
  const firstHostRoute = overview.verification.testSets.find((set) => set.id === 'TS-HOV-P01');
  assert.deepEqual(firstHostRoute.checkedContent.sections, ['Start Here']);
  assert.equal(overview.verification.currentStatus, 'UNVALIDATED');
  assert.deepEqual(overview.verification.blockerDetails, []);
  assert.deepEqual(contractModel.blockerDetails, []);
  assert.deepEqual(firstHostRoute.blockerDetails, []);
  assert.deepEqual(contractModel.evidenceLaneHints.map((item) => item.code), ['ACCOUNTABLE_OWNER']);
  assert.deepEqual(firstHostRoute.evidenceLaneHints.map((item) => item.code), ['RUNTIME_OBSERVATION']);
  assert.deepEqual(overview.verification.evidenceLaneHints.map((item) => item.code),
    ['RUNTIME_OBSERVATION', 'ACCOUNTABLE_OWNER']);
  const overviewBranches = overview.verification.testSets.flatMap((set) => set.branches);
  const overviewSteps = overviewBranches.flatMap((branch) => branch.steps);
  assert.equal(overviewSteps.length, 9);
  assert.ok(overviewSteps.every((step) => step.currentStatus === 'UNVALIDATED'));
  assert.ok(overviewSteps.every((step) => /missing evidence alone is UNVALIDATED/.test(step.currentRationale)));
  assert.ok(overviewSteps.every((step) => step.blockerDetails.length === 0));
  assert.deepEqual(overviewSteps.find((step) => step.id === 'HOV-C01-S03').checkedContent.sections,
    ['Volume Offers']);
  assert.ok([overview.verification, ...overview.verification.testSets, ...overviewBranches, ...overviewSteps]
    .every((row) => row.checkedContent.route === '/host/hosting-overview'));

  const diagnostics = await contextFor('/host/common-errors-diagnostics');
  const escalation = diagnostics.verification.testSets.find((set) => set.title === 'Redacted escalation packet');
  assert.equal(escalation.totals.commands, 0);
  assert.equal(escalation.totals.nonCommandSteps, escalation.totals.steps);
  assert.ok(diagnostics.verification.totals.executableIntentCommands > 0);
  const diagnosticCommands = diagnostics.verification.testSets.flatMap((set) => set.branches)
    .flatMap((branch) => branch.steps).flatMap((step) => step.commands);
  assert.deepEqual(diagnosticCommands.find((command) => command.id === 'CLM-a86c033f7e767f31').checkedContent.sections,
    ['GPU And Kernel Diagnostics']);

  const glossary = await contextFor('/host/glossary');
  const glossarySets = glossary.verification.testSets;
  const glossaryBranches = glossarySets.flatMap((set) => set.branches);
  const glossarySteps = glossaryBranches.flatMap((branch) => branch.steps);
  const glossaryCommands = glossarySteps.flatMap((step) => step.commands);
  assert.ok(glossarySteps.some((step) => step.checkedContent.sections.includes('Direct ports (direct_port_count)')));
  assert.ok([glossary.verification, ...glossarySets, ...glossaryBranches, ...glossarySteps, ...glossaryCommands]
    .every((row) => row.checkedContent.sections.every((section) => !section.includes('`'))));

  const teams = await contextFor('/host/host-teams');
  assert.ok(teams.verification.totals.displayOnlyCommands > 0);
  assert.equal(teams.verification.totals.executableIntentCommands, 0);
  assert.ok(teams.verification.totals.scored > 0);
  assert.equal(teams.verification.totals.scored, teams.verification.totals.displayOnlyScored);
  assert.equal(teams.verification.totals.executableIntentScored, 0);
  assert.equal(teams.verification.totals.displayOnlyScored + teams.verification.totals.notApplicableAssessments,
    teams.verification.totals.displayOnlyCommands);
  const catalog = teams.verification.testSets.find((set) => set.title === 'Host team CLI command support catalog');
  assert.equal(catalog.totals.displayOnlyCommands, catalog.totals.commands);
  assert.ok(catalog.totals.displayOnlyScored > 0);
  assert.ok(catalog.branches.flatMap((branch) => branch.steps).every((step) =>
    step.commands.every((command) => command.treatment === 'NON_EXECUTABLE_DISPLAY')));
  assert.ok(catalog.goal && catalog.accessClasses.length && catalog.safetyConstraints.length && catalog.limitations.length);

  const volume = await contextFor('/host/volume-offers');
  assert.equal(volume.verification.available, true);
  assert.equal(volume.verification.checkedContent.route, '/host/volume-offers');
  assert.deepEqual(volume.verification.testSets.map((set) => set.id),
    ['TS-VOL-C01', 'TS-VOL-E01', 'TS-VOL-E02', 'TS-VOL-C02']);
  assert.equal(volume.verification.totals.testSets, 4);
  assert.equal(volume.verification.totals.branches, 4);
  assert.equal(volume.verification.totals.steps, 9);
  assert.equal(volume.verification.totals.commands, 11);
  assert.equal(volume.verification.materialClaims.length, 39);
});

test('Canonical material-claim, citation, and page dispositions remain fully accounted', async () => {
  const testSets = JSON.parse(await fs.readFile(
    path.join(ROOT, 'verification', 'host-docs-test-sets.json'), 'utf8'));
  assert.equal(testSets.pages.length, 40);
  const contexts = await Promise.all(testSets.pages.map((page) => contextFor(page.route)));
  assert.ok(contexts.every((context) => context.verification.available));
  const claims = contexts.flatMap((context) => context.verification.materialClaims);
  assert.equal(claims.length, 1687);
  assert.equal(new Set(claims.map((claim) => claim.id)).size, 1687);

  const countBy = (items, valueFor) => items.reduce((counts, item) => {
    const value = valueFor(item);
    counts[value] = (counts[value] || 0) + 1;
    return counts;
  }, {});
  assert.deepEqual(countBy(claims, (claim) => claim.current.status), {
    PASS: 167, FAIL: 153, BLOCKED: 23, UNVALIDATED: 1344,
  });
  assert.deepEqual(countBy(claims, (claim) => claim.citation.state), {
    ABSENT: 153, PRESENT_UNVERIFIED: 19, NOT_REQUIRED: 1515,
  });
  assert.deepEqual(countBy(contexts, (context) => context.verification.materialDisposition.status), {
    FAIL: 26, BLOCKED: 3, UNVALIDATED: 11,
  });
});

test('Material claims expose exact documentation source locations without promoting status', async () => {
  const context = await contextFor('/host/verification-stages');
  const claim = context.verification.materialClaims.find((item) =>
    item.id === 'MCL-f9f3ebb712a5588d');

  assert.ok(claim);
  assert.deepEqual(claim.checkedContent, {
    route: '/host/verification-stages', pageTitle: 'Verification Stages', sections: ['Introduction'],
  });
  assert.equal(claim.claim.text,
    'Verification is automated. There is no manual review step for ordinary host verification.');
  assert.deepEqual(claim.sourceLocation, {
    file: 'host/verification-stages.mdx',
    spans: [{ start: 16, end: 16 }],
    textSha256: '73d7d624e9122cb81d36075a6962e3540c84d466943d1b102682a22564577298',
  });

  const sourceLines = await sourceLinesFor(claim);
  const boundText = claim.sourceLocation.spans.flatMap(({ start, end }) =>
    sourceLines.slice(start - 1, end)).join('\n');
  assert.equal(boundText, claim.claim.text);
  assert.equal(crypto.createHash('sha256').update(boundText).digest('hex'),
    claim.sourceLocation.textSha256);

  assert.equal(claim.current.status, 'UNVALIDATED');
  assert.deepEqual(claim.current.evidenceIds, []);
  assert.deepEqual(claim.current.evidence, []);
  assert.deepEqual(claim.current.dispositionEvidenceIds,
    ['EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01']);
  assert.equal(claim.current.dispositionEvidence[0].binding, claim.id);
});

test('Material claim source passages expose the exact bound block without changing disposition', async () => {
  const context = await contextFor('/host/verification-stages');
  const claim = context.verification.materialClaims.find((item) =>
    item.id === 'MCL-f9f3ebb712a5588d');

  assert.ok(claim);
  const sourceLines = await sourceLinesFor(claim);
  assertSourcePassageContract(claim, sourceLines);
  assert.deepEqual(claim.sourcePassages, [{
    text: 'Verification is automated. There is no manual review step for ordinary host verification.',
    section: 'Introduction', start: 16, end: 16, redacted: false, occurrence: 0, occurrences: 1,
  }]);
  assertCurrentClaimState(claim, {
    status: 'UNVALIDATED', evidenceIds: [],
    dispositionEvidenceIds: ['EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01'],
  });
});

test('Volume source passages preserve every declared multi-span section and disposition', async () => {
  const context = await contextFor('/host/volume-offers');
  const claims = new Map(context.verification.materialClaims.map((claim) => [claim.id, claim]));
  const expected = new Map([
    ['VOL-C06', {
      spans: [{ start: 21, end: 21 }, { start: 36, end: 36 }],
      sections: ['Introduction', 'Identifiers And Values'], status: 'PASS', passageCount: 2,
    }],
    ['VOL-C07', {
      spans: [{ start: 24, end: 24 }, { start: 101, end: 109 }],
      sections: ['Introduction', 'Command Map'], status: 'PASS', passageCount: 10,
    }],
    ['VOL-C13', {
      spans: [{ start: 41, end: 41 }, { start: 77, end: 77 }],
      sections: ['Volume Lifecycle', 'Shared Disk Capacity'], status: 'BLOCKED', passageCount: 2,
    }],
  ]);

  for (const [id, contract] of expected) {
    const claim = claims.get(id);
    assert.ok(claim, id);
    assert.deepEqual(claim.sourceLocation.spans, contract.spans);
    assert.deepEqual(claim.checkedContent.sections, contract.sections);
    assert.equal(claim.sourcePassages.length, contract.passageCount);
    assert.deepEqual([...new Set(claim.sourcePassages.map((passage) => passage.section))],
      contract.sections);
    const sourceLines = await sourceLinesFor(claim);
    assertSourcePassageContract(claim, sourceLines);
    const boundText = claim.sourceLocation.spans.flatMap(({ start, end }) =>
      sourceLines.slice(start - 1, end)).join('\n');
    assert.equal(crypto.createHash('sha256').update(boundText).digest('hex'),
      claim.sourceLocation.textSha256);
    assertCurrentClaimState(claim, {
      status: contract.status,
      evidenceIds: ['EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01'],
      dispositionEvidenceIds: ['EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01'],
    });
  }

  assert.deepEqual(claims.get('VOL-C07').sourcePassages.map(({ start, end }) => ({ start, end })), [
    { start: 24, end: 24 },
    ...Array.from({ length: 9 }, (_, index) => ({ start: 101 + index, end: 101 + index })),
  ]);
});

test('Source passages split spans containing prose and fenced commands into contained blocks', async () => {
  const context = await contextFor('/host/volume-offers');
  const claims = new Map(context.verification.materialClaims.map((claim) => [claim.id, claim]));
  const contracts = new Map([
    ['VOL-C21', {
      span: { start: 51, end: 60 },
      passages: [{ start: 51, end: 51 }, { start: 53, end: 58 }, { start: 60, end: 60 }],
    }],
    ['VOL-C22', {
      span: { start: 62, end: 69 },
      passages: [{ start: 62, end: 62 }, { start: 64, end: 69 }],
    }],
  ]);

  for (const [id, contract] of contracts) {
    const claim = claims.get(id);
    assert.ok(claim, id);
    assert.deepEqual(claim.sourceLocation.spans, [contract.span]);
    assert.deepEqual(claim.sourcePassages.map(({ start, end }) => ({ start, end })), contract.passages);
    const sourceLines = await sourceLinesFor(claim);
    assertSourcePassageContract(claim, sourceLines);
    assert.ok(claim.sourcePassages.some((passage) => passage.text.startsWith('```bash\n')));
    assert.ok(claim.sourcePassages.some((passage) => !passage.text.startsWith('```')));
    assertCurrentClaimState(claim, {
      status: 'PASS', evidenceIds: ['EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01'],
      dispositionEvidenceIds: ['EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01'],
    });
  }
});

test('Repeated identical source passages expose stable source occurrence ordinals', async () => {
  const context = await contextFor('/host/network-ports');
  const claims = ['MCL-11c443771c46d426', 'MCL-1cbdc60b57d73107'].map((id) => {
    const claim = context.verification.materialClaims.find((item) => item.id === id);
    assert.ok(claim, id);
    return claim;
  });

  const expectedStarts = [79, 100];
  for (const [index, claim] of claims.entries()) {
    const sourceLines = await sourceLinesFor(claim);
    assertSourcePassageContract(claim, sourceLines);
    assert.deepEqual(claim.sourcePassages, [{
      text: 'From Windows PowerShell outside the LAN:',
      section: 'Test Ports From Outside The LAN', start: expectedStarts[index], end: expectedStarts[index],
      redacted: false, occurrence: index, occurrences: 2,
    }]);
    assertCurrentClaimState(claim, {
      status: 'UNVALIDATED', evidenceIds: [],
      dispositionEvidenceIds: ['EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01'],
    });
  }
  assert.equal(claims[0].sourcePassages[0].text, claims[1].sourcePassages[0].text);
});

test('Source passage projection keeps numeric and scoped-identifier sanitizers active', async () => {
  const cases = [
    {
      route: '/host/maintenance-windows', id: 'MCL-5789114e2e680769',
      raw: '1782950400', replacement: '[identifier]',
      expected: '```bash\nvastai schedule maint 8207 --sdate [identifier] --duration 2 --maintenance_category power\n```',
      dispositionEvidenceIds: [
        'EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01', 'EV-HOST-EXACT-COMMAND-CLAIM-BINDINGS-01',
      ],
    },
    {
      route: '/host/notifications', id: 'MCL-d858cb9cf7cb85ca',
      raw: 'host:machine_offline', replacement: 'host=[identifier]',
      expected: 'Notification types are identified by a `key` with a context prefix. Host events use the `host:` prefix, such as `host=[identifier]`.',
      dispositionEvidenceIds: ['EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01'],
    },
  ];

  for (const contract of cases) {
    const context = await contextFor(contract.route);
    const claim = context.verification.materialClaims.find((item) => item.id === contract.id);
    assert.ok(claim, contract.id);
    const sourceLines = await sourceLinesFor(claim);
    assertSourcePassageContract(claim, sourceLines);
    assert.equal(claim.sourcePassages.length, 1);
    const passage = claim.sourcePassages[0];
    assert.equal(passage.redacted, true);
    assert.match(sourceLiteral(sourceLines, passage), new RegExp(contract.raw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    assert.doesNotMatch(passage.text, new RegExp(contract.raw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    assert.match(passage.text, new RegExp(contract.replacement.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    assert.equal(passage.text, contract.expected);
    assertCurrentClaimState(claim, {
      status: 'UNVALIDATED', evidenceIds: [],
      dispositionEvidenceIds: contract.dispositionEvidenceIds,
    });
  }
});

test('Frame-caption source passages retain wrapper markup for the reader projection', async () => {
  const context = await contextFor('/host/account-hosting-agreement');
  const claim = context.verification.materialClaims.find((item) =>
    item.id === 'MCL-e7e229ef151582f6');
  assert.ok(claim);
  const sourceLines = await sourceLinesFor(claim);
  assertSourcePassageContract(claim, sourceLines);
  assert.deepEqual(claim.sourcePassages, [{
    text: '<Frame caption="Host-enabled console navigation showing the Machines link under Hosting.">',
    section: 'How to accept the hosting agreement', start: 28, end: 28,
    redacted: false, occurrence: 0, occurrences: 1,
  }]);
  assert.equal(claim.claim.text,
    'Host-enabled console navigation showing the Machines link under Hosting.');
  assertCurrentClaimState(claim, {
    status: 'UNVALIDATED', evidenceIds: [],
    dispositionEvidenceIds: ['EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01'],
  });

  const overlay = await (await fetch(`${reviewOrigin}/__review__/overlay.js`)).text();
  assert.match(overlay, /\(claim\.sourcePassages \|\| \[\]\)\.map\(passageWording\)/);
  assert.match(overlay, /var caption = text\.match\(\/\^<Frame/);
});

test('Material-claim evidence links accept only evidence attached to that wording', async () => {
  const context = await contextFor('/host/how-to-self-test');
  const claim = context.verification.materialClaims.find((item) =>
    item.id === 'MCL-9ad33b25fd88c5cb');

  assert.ok(claim);
  assert.equal(claim.current.status, 'UNVALIDATED');
  assert.equal(claim.current.dispositionEvidenceRole, 'PARTIAL_EVIDENCE_BOUND_STATUS_UNCHANGED');
  assert.deepEqual(claim.current.evidenceIds, ['EV-CLI-SET-API-KEY-PERMISSIONS-01']);
  assert.deepEqual(claim.current.evidence.map((item) => item.id),
    ['EV-CLI-SET-API-KEY-PERMISSIONS-01']);

  const evidenceRef = claim.current.evidence[0].evidenceRef;
  const allowed = await fetch(`${reviewOrigin}/__review__/evidence?ref=${
    encodeURIComponent(evidenceRef)}&binding=${encodeURIComponent(claim.id)}`);
  assert.equal(allowed.status, 200);
  assert.match(allowed.headers.get('content-type'), /^text\/html/);
  const html = await allowed.text();
  assert.match(html, /^Supporting evidence attached to this wording$/m);
  assert.match(html, /^Page: \/host\/how-to-self-test$/m);
  assert.match(html, /^Heading: Before You Run It$/m);
  assert.match(html, /^Wording: \[bash\] vastai set api-key &lt;API_KEY&gt;$/m);
  assert.match(html, /^Current claim status: UNVALIDATED$/m);
  assert.match(html, /^Tracking ID: MCL-9ad33b25fd88c5cb$/m);
  assert.match(html,
    /An attached result may provide only partial support\. The current claim status is unchanged\./);
  assert.match(html, /id="review-page-link" href="\/host\/how-to-self-test"/);
  assert.match(html,
    /id="review-heading-link" href="\/host\/how-to-self-test#before-you-run-it"/);

  const unrelated = await fetch(`${reviewOrigin}/__review__/evidence?ref=${
    encodeURIComponent(evidenceRef)}&binding=${encodeURIComponent('MCL-f9f3ebb712a5588d')}`);
  assert.equal(unrelated.status, 404);
  assert.equal(await unrelated.text(), 'Evidence binding not found.');

  const refreshed = await contextFor('/host/how-to-self-test');
  assert.equal(refreshed.verification.materialClaims.find((item) => item.id === claim.id).current.status,
    'UNVALIDATED');
});

test('Blocker causes and access-derived evidence hints stay separate and conservative', async () => {
  const context = await isolatedVerificationContext('valid-blocker-classification', '/host/volume-offers');
  const vv = context.verification;
  assert.equal(vv.currentStatus, 'BLOCKED');
  assert.match(vv.currentRationale, /rollup/);
  assert.deepEqual(new Set(vv.blockerDetails.map((item) => item.code)),
    new Set(['DERIVED_FROM_CHILDREN', 'MULTIPLE']));
  assert.ok(vv.blockerDetails.every((item) => item.nextAction && item.claimImpact && item.evidenceIds.length));
  const blockedSteps = vv.testSets.flatMap((set) => set.branches)
    .flatMap((branch) => branch.steps).filter((step) => step.currentStatus === 'BLOCKED');
  assert.equal(blockedSteps.length, 3);
  assert.ok(blockedSteps.every((step) => step.blockerDetails.length === 1));
  assert.ok(blockedSteps.every((step) => step.blockerDetails[0].code === 'MULTIPLE'));

  assert.deepEqual(vv.testSets[0].evidenceLaneHints.map((item) => item.code),
    ['IMPLEMENTATION_SOURCE', 'ACCOUNTABLE_OWNER', 'DOCUMENTATION_CITATION']);
  assert.deepEqual(vv.testSets[1].evidenceLaneHints.map((item) => item.code),
    ['IMPLEMENTATION_SOURCE', 'ACCOUNTABLE_OWNER', 'DOCUMENTATION_CITATION']);
  assert.deepEqual(vv.evidenceLaneHints.map((item) => item.code), [
    'IMPLEMENTATION_SOURCE', 'ACCOUNTABLE_OWNER', 'DOCUMENTATION_CITATION',
  ]);
});

test('Retained V&V references are repository-relative and do not depend on .orchestra state', async () => {
  const results = JSON.parse(await fs.readFile(path.join(ROOT, 'verification', 'host-docs-test-results.json'), 'utf8'));
  const scores = JSON.parse(await fs.readFile(path.join(ROOT, 'verification', 'host-docs-command-scores.json'), 'utf8'));
  const refs = [
    ...results.attempts.map((row) => row.evidence_ref),
    ...results.command_results.flatMap((row) => [row.evidence_ref, row.qualification_evidence_ref]),
    ...(scores.withdrawn_records || []).map((row) => row.qualification_evidence_ref),
  ].filter(Boolean);
  const historicalBaseline =
    'verification/evidence/2026-09-03-host-repository-rebase-01/pre-edit-working-tree-baseline-sanitized.txt';
  for (const ref of refs) {
    assert.match(ref, /^verification\/evidence\/[A-Za-z0-9._/-]+$/);
    assert.ok(!ref.split('/').includes('..'));
    const file = path.join(ROOT, ref);
    const stat = await fs.lstat(file);
    assert.equal(stat.isFile(), true, ref);
    assert.equal(stat.isSymbolicLink(), false, ref);
    const contents = await fs.readFile(file, 'utf8');
    if (ref === historicalBaseline) {
      assert.match(contents, /^\? \.orchestra\/$/m,
        'the sanitized pre-edit projection must preserve the observed untracked path');
      assert.match(contents,
        /b1bd6a1b423da195f68987e8a9b5ffe29bef7be00e0288eb3dbbc7f248ea981b/,
        'the sanitized projection must bind the restricted raw capture');
      assert.doesNotMatch(contents,
        /(?:\/Users\/|\/private\/tmp\/|\/var\/folders\/|github\.com\/(?!vast-ai\/)[^/\s]+\/(?:docs|vast-python|self-test)(?=[\s)/#]|$))/,
        'the public projection must not expose workstation paths');
    } else {
      assert.doesNotMatch(contents, /(?:^|[\s("'])\.orchestra\//m, ref);
    }
  }
});

test('Missing or malformed verification input fails closed', async () => {
  const missing = (await isolatedVerificationContext()).verification;
  assert.equal(missing.available, false);
  assert.match(missing.unavailableReason, /^ENOENT:.*\[local-path\]/);
  const failureReasons = new Set();
  for (const mode of [
    'malformed', 'snapshot-mismatch', 'schema-mismatch', 'record-type-mismatch',
    'inventory-count-mismatch', 'invalid-baseline-status', 'duplicate-canonical-command',
    'invalid-canonical-route',
    'invalid-step-source-span', 'invalid-step-source-section', 'invalid-command-source-span',
    'invalid-command-source-section',
    'unknown-status-target', 'duplicate-status', 'unknown-status-attempt', 'unknown-status-evidence',
    'unsafe-status-attempt', 'partial-current-status', 'partial-procedure-target',
    'mismatched-procedure-evidence', 'superseded-current-attempt', 'command-evidence-current-status',
    'unknown-score-command', 'score-empty-evidence', 'pass-missing-direct-evidence', 'score-duplicate-evidence',
    'score-wrong-command-evidence', 'score-ancestry-mismatch', 'score-source-mismatch',
    'numeric-not-applicable-status', 'assessment-current-status-mismatch',
    'score-count-mismatch', 'invalid-not-applicable-approval', 'not-applicable-nondisplay',
    'missing-assessment-coverage', 'missing-current-projection', 'score3-current-not-pass',
    'score3-missing-direct-evidence', 'score3-duplicate-direct-evidence', 'score3-direct-not-pass',
    'score3-direct-wrong-command', 'score3-static-procedure-direct', 'score3-static-relabelled-full',
    'score3-partial-relabelled-full', 'score3-scoped-superseded-direct',
    'qualification-command-uncovered',
    'not-applicable-parent-child-mismatch', 'projection-count-mismatch',
    'missing-attempt-evidence-ref', 'unsafe-attempt-evidence-ref',
    'nonportable-attempt-evidence-content', 'direct-command-missing-evidence-ref',
    'withdrawn-current-status-mismatch', 'withdrawn-current-score-mismatch', 'invalid-retired-withdrawal',
  ]) {
    const verification = (await isolatedVerificationContext(mode)).verification;
    assert.equal(verification.available, false, mode);
    assert.ok(verification.unavailableReason, mode);
    assert.doesNotMatch(verification.unavailableReason, /\/Users\/|\/private\/tmp|\/var\/folders/, mode);
    failureReasons.add(verification.unavailableReason);
  }
  assert.ok(failureReasons.size >= 20,
    `expected distinct fail-closed integrity gates, observed ${failureReasons.size}`);
});

test('Historical proof stays bounded when current Host sources or navigation drift', async () => {
  const stalePage = (await isolatedVerificationContext('stale-page-source', '/host/market-metrics')).verification;
  assert.equal(stalePage.available, true);
  assert.equal(stalePage.currentStatus, 'STALE');
  assert.equal(stalePage.sourceFreshness.state, 'STALE');
  assert.match(stalePage.sourceFreshness.explanation, /differs from the reviewed source snapshot/);
  assert.match(stalePage.sourceFreshness.nextAction, /new V&V result/);
  assert.match(stalePage.sourceFreshness.baselinePageHref, /7d42a0d439f91e4dc2877104db807ec6fb975ce4\/host\/market-metrics\.mdx$/);
  assert.deepEqual(stalePage.materialClaims, []);
  assert.deepEqual(stalePage.testSets, []);

  const staleDependency = (await isolatedVerificationContext('stale-rendered-dependency', '/host/notifications')).verification;
  assert.equal(staleDependency.available, true);
  assert.equal(staleDependency.sourceFreshness.state, 'STALE');
  assert.deepEqual(staleDependency.testSets, []);

  const staleSupport = (await isolatedVerificationContext('stale-support-wrapper', '/host/cli/cancel-maint')).verification;
  assert.equal(staleSupport.available, true);
  assert.equal(staleSupport.currentStatus, 'STALE');
  assert.equal(staleSupport.supportLayer, true);
  assert.match(staleSupport.sourceFreshness.baselinePageHref,
    /7d42a0d439f91e4dc2877104db807ec6fb975ce4\/host\/cli\/cancel-maint\.mdx$/);
  assert.match(staleSupport.sourceFreshness.explanation, /support wrapper, snippet, or central reference/);

  const merged = (await isolatedVerificationContext('merged-current-host-nav', '/host/machine-metrics')).verification;
  assert.equal(merged.available, true);
  assert.equal(merged.currentStatus, 'UNVALIDATED');
  assert.equal(merged.sourceFreshness.state, 'UNVALIDATED');
  assert.equal(merged.sourceFreshness.currentHostRouteCount, 44);
  assert.equal(merged.sourceFreshness.baselineHostRouteCount, 40);
  assert.equal(merged.sourceFreshness.baselinePageHref, null);

  const removed = (await isolatedVerificationContext('removed-current-nav-route', '/host/network-ports')).verification;
  assert.equal(removed.available, true);
  assert.equal(removed.sourceFreshness.state, 'HISTORICAL_ONLY');
  assert.equal(removed.currentStatus, 'UNVALIDATED');

  const nested = (await isolatedVerificationContext('nested-current-nav', '/host/network-ports')).verification;
  assert.equal(nested.available, true);
  assert.equal(nested.sourceFreshness.state, 'CURRENT');
  for (const mode of ['duplicate-current-nav-route', 'traversal-current-nav-route']) {
    const invalid = (await isolatedVerificationContext(mode)).verification;
    assert.equal(invalid.available, false, mode);
    assert.match(invalid.unavailableReason, /current Host route|current Host navigation/);
  }
});

test('Actual merged sources expose freshness separately from retained proof', async (t) => {
  const changed = await currentContextFor('/host/verification-stages');
  assert.equal(changed.verification.available, true, changed.verification.unavailableReason);
  if (changed.verification.sourceFreshness?.currentHostRouteCount !== 44) {
    t.skip('requires the merged 44-route Host navigation fixture');
    return;
  }
  assert.equal(changed.verification.available, true);
  assert.equal(changed.verification.currentStatus, 'STALE');
  assert.equal(changed.verification.sourceFreshness.state, 'STALE');
  assert.deepEqual(changed.verification.testSets, []);
  assert.match(changed.verification.sourceFreshness.baselinePageHref,
    /7d42a0d439f91e4dc2877104db807ec6fb975ce4\/host\/verification-stages\.mdx$/);

  const added = await currentContextFor('/host/machine-metrics');
  assert.equal(added.verification.available, true);
  assert.equal(added.verification.currentStatus, 'UNVALIDATED');
  assert.equal(added.verification.sourceFreshness.state, 'UNVALIDATED');
  assert.equal(added.verification.sourceFreshness.currentHostRouteCount, 44);
  assert.equal(added.verification.sourceFreshness.baselineHostRouteCount, 40);
  assert.equal(added.verification.sourceFreshness.baselinePageHref, null);
});

test('Current status projection preserves frozen execution status and supports procedure evidence', async () => {
  const context = await isolatedVerificationContext('valid-current-status', '/host/common-host-questions');
  assert.equal(context.verification.available, true);
  assert.equal(context.verification.currentStatus, 'PASS');
  assert.equal(context.verification.currentStatusAttemptId,
    'ATTEMPT-2026-09-01-HOST-CURRENT-RECONCILIATION-01');
  assert.deepEqual(context.verification.currentEvidenceIds, ['EV-HOST-CURRENT-RECONCILIATION-01']);
  assert.deepEqual(context.verification.currentEvidence, [{
    id: 'EV-HOST-CURRENT-RECONCILIATION-01',
    evidenceRef: 'verification/evidence/2026-09-01-host-current-reconciliation-attempt-01/result.md',
    binding: 'PAGE:PAGE-host-common-host-questions',
  }]);
  assert.equal(context.verification.currentMethod, 'CURRENT_SOURCE_AND_RETAINED_EVIDENCE_RECONCILIATION');
  assert.match(context.verification.currentObservation, /Final topology reconciled/);
  assert.match(context.verification.currentLimitations, /Classification only, not command execution/);
  const set = context.verification.testSets.find((row) => row.id === 'TS-FAQ-C01');
  const branch = set.branches.find((row) => row.id === 'FAQ-C01-routes');
  const step = branch.steps.find((row) => row.id === 'FAQ-C01-routes-s01');
  for (const row of [set, branch]) {
    assert.equal(row.executionStatus, 'PASS');
    assert.equal(row.currentStatus, 'PASS');
    assert.equal(row.currentStatusAttemptId, 'ATTEMPT-2026-09-01-HOST-CURRENT-RECONCILIATION-01');
    assert.deepEqual(row.currentEvidenceIds, ['EV-HOST-CURRENT-RECONCILIATION-01']);
    assert.ok(row.history.some((item) => item.evidenceIds.includes('EV-HOST-CURRENT-RECONCILIATION-01')));
  }
  assert.equal(step.executionStatus, 'PASS');
  assert.equal(step.currentStatus, 'PASS');
  assert.equal(step.currentStatusAttemptId, 'ATTEMPT-2026-09-01-HOST-FAQ-ROUTE-02');
  assert.deepEqual(step.currentEvidenceIds, ['EV-FAQ-C01-ROUTES-02']);
  assert.equal(step.currentMethod, 'LOCAL_STATIC_ROUTE_OWNERSHIP_AUDIT');
  assert.ok(step.history.some((item) => item.evidenceIds.includes('EV-FAQ-C01-ROUTES-01') &&
    item.status === 'FAIL' && item.supersededBy === 'ATTEMPT-2026-09-01-HOST-FAQ-ROUTE-02'));
  assert.doesNotMatch(JSON.stringify(context.verification), /\/private\/tmp|\/Users\//);
});

test('Current evidence and score text are sanitized before reaching the review context', async () => {
  const context = await isolatedVerificationContext('valid-sanitized-current-status', '/host/market-metrics');
  assert.equal(context.verification.available, true);
  const serialized = JSON.stringify(context.verification);
  for (const unsafe of [/\/Users\/alice/, /\/var\/folders/, /2001:db8/, /424242/, /a{64}/]) {
    const match = unsafe.exec(serialized);
    assert.equal(match, null, match
      ? `unsanitized fixture value matched ${unsafe}: ${serialized.slice(Math.max(0, match.index - 100), match.index + 180)}`
      : `unsanitized fixture value matched ${unsafe}`);
  }
  assert.match(serialized, /\[local-path\]|\[network-address\]|\[identifier\]|\[redacted-token\]|\[redacted\]/);
  assert.match(context.verification.currentObservation, /\[local-path\].*\[network-address\].*\[redacted-token\]/);
  assert.match(context.verification.currentLimitations, /password=\[redacted\]/);
  const command = context.verification.testSets.find((row) => row.id === 'TS-MET-E02').branches
    .find((row) => row.id === 'MET-E02-current').steps[0].commands
    .find((row) => row.id === 'CLM-582fe58ab6692d1a');
  assert.match(command.score.rationale, /api_key=\[redacted\]/);
});

test('Approved NOT_APPLICABLE semantic assessment remains separate from numeric scores', async () => {
  const context = await isolatedVerificationContext('valid-not-applicable', '/host/fleet-operations');
  assert.equal(context.verification.available, true);
  const command = context.verification.testSets.flatMap((set) => set.branches)
    .flatMap((branch) => branch.steps).flatMap((step) => step.commands)
    .find((row) => row.id === 'CLM-949ef36e5c67b2ef');
  assert.equal(command.executionStatus, 'NOT_APPLICABLE');
  assert.equal(command.currentStatus, 'NOT_APPLICABLE');
  assert.equal(command.score, null);
  assert.match(command.notApplicableAssessment.approvalRef,
    /^CANONICAL_NON_EXECUTABLE_DISPLAY:[a-f0-9]{64}$/);
  assert.deepEqual(command.notApplicableAssessment.evidenceIds, ['EV-HOST-COMMAND-ASSESSMENT-01']);
});

test('Semantic score evidence can remain UNVALIDATED while current execution separately supplies PASS', async () => {
  const context = await isolatedVerificationContext('valid-score-status-separation', '/host/market-metrics');
  assert.equal(context.verification.available, true);
  const command = context.verification.testSets.find((row) => row.id === 'TS-MET-E02').branches
    .find((row) => row.id === 'MET-E02-current').steps
    .find((row) => row.id === 'MET-E02-current-s01').commands
    .find((row) => row.id === 'CLM-582fe58ab6692d1a');
  assert.equal(command.currentStatus, 'PASS');
  assert.deepEqual(command.currentEvidenceIds, ['EV-CLI05-MARKET-METRICS']);
  assert.equal(command.score.value, 2);
  assert.equal(command.score.executionStatus, 'PASS');
  assert.deepEqual(command.score.evidenceIds, ['EV-HOST-COMMAND-ASSESSMENT-01']);
  assert.deepEqual(command.score.directEvidenceIds, ['EV-CLI05-MARKET-METRICS']);
  assert.equal(command.score.directEvidence[0].status, 'PASS');
  assert.equal(command.score.directEvidence[0].proofRole, 'DIRECT_FUNCTIONAL_PARTIAL');
  const semantic = command.history.find((row) => row.evidenceIds.includes('EV-HOST-COMMAND-ASSESSMENT-01'));
  assert.equal(semantic.status, 'UNVALIDATED');
  assert.match(semantic.limitations, /Score-traceability evidence only/);
});

test('Procedure history retains the failed attempt and linked correction retest', async () => {
  const context = await isolatedVerificationContext('valid-history', '/host/common-host-questions');
  assert.equal(context.verification.available, true);
  const step = context.verification.testSets.find((row) => row.id === 'TS-FAQ-C01').branches
    .find((row) => row.id === 'FAQ-C01-routes').steps
    .find((row) => row.id === 'FAQ-C01-routes-s01');
  assert.equal(step.currentStatus, 'PASS');
  const failed = step.history.find((row) => row.evidenceIds.includes('EV-FAQ-C01-ROUTES-01'));
  const passed = step.history.find((row) => row.evidenceIds.includes('EV-FAQ-C01-ROUTES-02'));
  assert.equal(failed.status, 'FAIL');
  assert.equal(failed.supersededBy, 'ATTEMPT-2026-09-01-HOST-FAQ-ROUTE-02');
  assert.equal(passed.status, 'PASS');
  assert.equal(passed.supersededBy, null);
  assert.match(passed.observation, /passed after the three focused semantic-owner corrections/);
});

test('Unmapped Host pages retain epic provenance without invented blockers', async () => {
  const context = await contextFor('/host/workload-policy');
  assert.equal(context.matched, false);
  assert.deepEqual(context.epics.map((issue) => issue.key), ['CON-1187']);
  assert.deepEqual(context.issues, []);
  assert.deepEqual(context.blockers, []);
});

test('Non-Host pages do not inherit Host Jira context', async () => {
  const context = await contextFor('/guides/get-started');
  assert.deepEqual(context.epics, []);
  assert.deepEqual(context.issues, []);
  assert.deepEqual(context.blockers, []);
  assert.equal(context.verification.available, false);
  assert.ok(['page-not-in-inventory', 'package-integrity-failure'].includes(context.verification.unavailableReason));
});

test('Only the review proxy injects the overlay', async () => {
  const targetHtml = await (await fetch(`${targetOrigin}/host/host-teams`)).text();
  const reviewHtml = await (await fetch(`${reviewOrigin}/host/host-teams`)).text();
  assert.doesNotMatch(targetHtml, /__review__\/overlay\.js/);
  assert.match(reviewHtml, /__review__\/overlay\.js/);
  const overlay = await (await fetch(`${reviewOrigin}/__review__/overlay.js`)).text();
  assert.match(overlay, /Jira context for this page/);
  assert.match(overlay, /issue\.status \+ ' · snapshot ' \+ \(issue\.statusAsOf \|\| 'unknown'\) \+ ' \(unverified\)'/);
  assert.match(overlay, /V&amp;V evidence for this page/);
  assert.match(overlay, /This page contains no executable command instructions/);
  assert.match(overlay, /Command scoring does not apply/);
  assert.match(overlay, /Without retained evidence a check remains <code>UNVALIDATED<\/code>/);
  assert.match(overlay, /BLOCKED<\/code> only when a concrete prerequisite is unavailable and named/);
  assert.match(overlay, /numeric semantic scores assess documentation support and relevance only/);
  assert.match(overlay, /Semantic documentation score/);
  assert.match(overlay, /non-command check/);
  assert.match(overlay, /command-reference check/);
  assert.match(overlay, /source-defect command check/);
  assert.match(overlay, /display-only command reference/);
  assert.match(overlay, /retained evidence record/);
  assert.match(overlay, /Recorded outcome/);
  assert.match(overlay, /page is not in the current V&amp;V inventory/);
  assert.match(overlay, /V&amp;V package is fail-closed/);
  assert.match(overlay, /Specific failed prerequisite/);
  assert.match(overlay, /Procedure status is separate from command scoring/);
  assert.match(overlay, /score 1 = failed or gave no relevant support/);
  assert.match(overlay, /Direct functional\/static evidence/);
  assert.match(overlay, /Open retained evidence/);
  assert.match(overlay, /Page under review:/);
  assert.match(overlay, /under review:/);
  assert.match(overlay, /Declared section/);
  assert.match(overlay, /Declared-scope links open the page or section each record says it evaluates/);
  assert.match(overlay, /A scope link is not evidence/);
  assert.match(overlay, /retained-evidence total counts records, not independently proved claims/);
  assert.match(overlay, /it is not a page-load result/);
  assert.match(overlay, /Procedure V&amp;V blocker/);
  assert.match(overlay, /Recorded unavailable prerequisite/);
  assert.match(overlay, /Evidence source guide/);
  assert.match(overlay, /Status rule/);
  assert.match(overlay, /What this docs review can address/);
  assert.match(overlay, /Reviewer handoff/);
  assert.match(overlay, /Implementation\/source/);
  assert.match(overlay, /Runtime\/UI/);
  assert.match(overlay, /Product\/Finance\/Legal authority/);
  assert.match(overlay, /Documentation\/citation/);
  assert.match(overlay, /missing evidence alone is/);
  assert.match(overlay, /concrete prerequisite is unavailable and named/);
  assert.match(overlay, /documentation text is the claim under review, not proof of itself/);
  assert.match(overlay, /canonical Vast source code, API schemas or configuration/);
  assert.match(overlay, /code alone may not be authoritative/);
  assert.match(overlay, /Material-claim page disposition/);
  assert.match(overlay, /Evidence access\/authority needed/);
  assert.match(overlay, /Open the retained evidence artifact/);
  assert.match(overlay, /vv-evidence-link/);
  assert.match(overlay, /Page procedure V&amp;V status/);
  assert.match(overlay, /section anchor unavailable/);
  assert.match(overlay, /Page introduction/);
  assert.match(overlay, /aria-controls="panel" aria-expanded="false"/);
  assert.match(overlay, /aria-labelledby="reviewPanelTitle" aria-hidden="true"/);
  assert.match(overlay, /aria-label="Close docs review panel"/);
  assert.match(overlay, /pill\.setAttribute\('aria-expanded', 'true'\)/);
  assert.match(overlay, /e\.key !== 'Escape'/);
  assert.match(overlay, /Topology status mirror/);
  assert.match(overlay, /Accounting\/status derivation only — not command proof/);
  assert.match(overlay, /Exact command proof/);
  assert.match(overlay, /Source\/signature support/);
  assert.match(overlay, /Runtime behavior/);
  assert.match(overlay, /recordedActionCoversRuntime/);
  assert.match(overlay, /Exact next action/);
  assert.match(overlay, /Runtime-proof next action/);
  assert.match(overlay,
    /runtimeStatus === 'UNVALIDATED'[\s\S]*To prove that the command works at runtime/);
  assert.match(overlay,
    /Source\/signature support proves that syntax is present in pinned code; it never proves execution/);
  assert.match(overlay, /Pinned source revision/);
  assert.match(overlay,
    /Compare its recorded revision and environment with the pinned source revision/);
  assert.match(overlay, /source portion is now shown as PASS above/);
  assert.match(overlay, /var commandTitle = signature && signature\.handlerSource/);
  assert.match(overlay,
    /'<a class="vv-command-source" href="' \+ esc\(signature\.handlerSource\.href\)[\s\S]*title="Open the pinned canonical CLI registration"><code>' \+[\s\S]*esc\(command\.text\)/);
  assert.match(overlay, /open exact static-check record/);
  assert.match(overlay, /Current supporting evidence/);
  assert.match(overlay, /Attempt history/);
  assert.match(overlay, /Semantic assessment: NOT_APPLICABLE/);
  assert.match(overlay,
    /https:\/\/github\.com\/vast-ai\/docs\/pull\/185\/files#diff-5ff737a240842e44cbef287f5e73e05da3ae18bd6e4d4f55626941405cfbfae1/);
  assert.doesNotMatch(
    overlay,
    /https:\/\/github\.com\/(?!vast-ai\/)[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+/,
  );
  assert.match(overlay, /\/context\?path=/);
  assert.match(overlay, /Save JSON/);
  assert.match(overlay, /Import JSON/);
  assert.match(overlay, /\/import/);
  assert.match(overlay, /no review notes/);
  assert.match(overlay, /this is not a V&V score/);
});

test('JSON import restores multiple reviewers and keeps newer server items', async () => {
  const newerAlice = {
    id: 'roundtrip-alice', reviewer: 'Alice', page: '/host/hosting-overview',
    pageTitle: 'Hosting Overview', type: 'inline', quote: 'Hosts provide machines',
    prefix: 'Overview: ', suffix: '; renters run workloads', heading: 'Hosting Overview',
    category: 'Suggestion', severity: 'Minor', comment: 'Keep the newer wording.',
    status: 'open', createdAt: '2026-07-13T08:00:00.000Z', updatedAt: '2026-07-13T10:00:00.000Z',
  };
  const saveResponse = await postJson('/__review__/api/state', { reviewer: 'Alice', items: [newerAlice] });
  assert.equal(saveResponse.status, 200);

  const olderAlice = { ...newerAlice, comment: 'Older backup wording.', updatedAt: '2026-07-13T09:00:00.000Z' };
  const bob = {
    id: 'roundtrip-bob', reviewer: 'Bob', page: '/host/network-ports',
    pageTitle: 'Network & Ports', type: 'page', quote: '', prefix: '', suffix: '', heading: '',
    category: 'Question', severity: 'Major', comment: 'Confirm the UDP wording.',
    status: 'resolved', createdAt: '2026-07-13T09:15:00.000Z', updatedAt: '2026-07-13T09:20:00.000Z',
  };
  const importResponse = await postJson('/__review__/api/import', {
    format: 'vast-docs-review-feedback', version: 1, generatedAt: '2026-07-13T09:30:00.000Z',
    pr: 'https://github.com/vast-ai/docs/pull/185', reviewers: ['Alice', 'Bob'], items: [olderAlice, bob],
  });
  assert.equal(importResponse.status, 200);
  const imported = await importResponse.json();
  assert.equal(imported.imported, 2);
  assert.equal(imported.reviewerCount, 2);

  const aliceState = await reviewerState('Alice');
  assert.equal(aliceState.items.length, 1);
  assert.equal(aliceState.items[0].comment, 'Keep the newer wording.');
  assert.equal(aliceState.items[0].quote, 'Hosts provide machines');
  assert.equal(aliceState.items[0].prefix, 'Overview: ');
  assert.equal(aliceState.items[0].suffix, '; renters run workloads');

  const bobState = await reviewerState('Bob');
  assert.equal(bobState.items.length, 1);
  assert.equal(bobState.items[0].comment, 'Confirm the UDP wording.');

  const exportResponse = await fetch(`${reviewOrigin}/__review__/export/feedback.json`);
  assert.equal(exportResponse.status, 200);
  const exported = await exportResponse.json();
  assert.equal(exported.format, 'vast-docs-review-feedback');
  assert.equal(exported.version, 1);
  assert.ok(exported.items.some((item) => item.id === 'roundtrip-alice' && item.comment === 'Keep the newer wording.'));
  assert.ok(exported.items.some((item) => item.id === 'roundtrip-bob'));

  const statusHtml = await (await fetch(`${reviewOrigin}/__review__/`)).text();
  assert.match(statusHtml, /Save JSON/);
  assert.match(statusHtml, /Import JSON/);
  assert.match(statusHtml, /restorable backup for every page and reviewer/);
  assert.match(statusHtml, /V&amp;V evidence:<\/b> 44 current primary Host routes · 40 retained reviewed baseline routes · 1687 historical material claims · 101 historical test sets · 207 historical branches · 477 historical checks/);
  assert.match(statusHtml,
    /Material-claim disposition:<\/b> PASS=167 · FAIL=153 · BLOCKED=23 · UNVALIDATED=1344/);
  assert.match(statusHtml, /Page semantic disposition:<\/b> FAIL=26 · BLOCKED=3 · UNVALIDATED=11/);
  assert.match(statusHtml, /default <code>review-feedback\/<\/code>/);
  assert.doesNotMatch(statusHtml, new RegExp(feedbackDir.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
});

test('JSON import rejects an invalid backup before writing any reviewer state', async () => {
  const response = await postJson('/__review__/api/import', {
    format: 'vast-docs-review-feedback', version: 1,
    items: [
      {
        id: 'atomic-valid', reviewer: 'Charlie', page: '/host/quickstart', pageTitle: 'Quickstart',
        type: 'page', quote: '', prefix: '', suffix: '', heading: '', category: 'Question', severity: 'Minor',
        comment: 'Would otherwise be valid.', status: 'open', createdAt: '2026-07-13T09:59:00.000Z',
        updatedAt: '2026-07-13T10:00:00.000Z',
      },
      {
        id: 'atomic-invalid', page: '/host/quickstart', pageTitle: 'Quickstart', type: 'page', quote: '',
        prefix: '', suffix: '', heading: '', category: 'Question', severity: 'Minor',
        comment: 'Missing reviewer.', status: 'open', createdAt: '2026-07-13T10:00:00.000Z',
        updatedAt: '2026-07-13T10:00:00.000Z',
      },
    ],
  });
  assert.equal(response.status, 400);
  const error = await response.json();
  assert.match(error.error, /invalid feedback reviewer/);
  const charlieState = await reviewerState('Charlie');
  assert.deepEqual(charlieState.items, []);
});
