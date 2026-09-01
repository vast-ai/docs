import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import { spawn } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let targetServer;
let reviewProcess;
let targetOrigin;
let reviewOrigin;
let feedbackDir;
let reviewOutput = '';

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

async function contextFor(pathname) {
  const response = await fetch(`${reviewOrigin}/__review__/api/context?path=${encodeURIComponent(pathname)}`);
  assert.equal(response.status, 200);
  return response.json();
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
  const fixtureRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'vast-review-vv-'));
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
    await fs.cp(path.join(ROOT, 'host'), path.join(fixtureRoot, 'host'), { recursive: true });
    for (const name of ['host-docs-test-sets.json', 'host-docs-test-results.json', 'host-docs-command-scores.json']) {
      await fs.copyFile(path.join(ROOT, 'verification', name), path.join(verificationDir, name));
    }
    const testSetsFile = path.join(verificationDir, 'host-docs-test-sets.json');
    const resultsFile = path.join(verificationDir, 'host-docs-test-results.json');
    const scoresFile = path.join(verificationDir, 'host-docs-command-scores.json');
    const results = JSON.parse(await fs.readFile(resultsFile, 'utf8'));
    const scores = JSON.parse(await fs.readFile(scoresFile, 'utf8'));
    const testSets = JSON.parse(await fs.readFile(testSetsFile, 'utf8'));
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
    const fixtureAttemptId = 'ATTEMPT-FIXTURE-CURRENT-01';
    if (!results.attempts.some((attempt) => attempt.attempt_id === fixtureAttemptId)) {
      results.attempts.push({ attempt_id: fixtureAttemptId, kind: 'ISOLATED_REVIEW_FIXTURE', status: 'PASS',
        execution_state: 'EXECUTED', reason: 'Synthetic complete fixture for fail-closed loader tests.' });
    }
    results.counts.attempts = results.attempts.length;
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
    const ensureScore = (commandId, evidenceIds, executionStatus = 'PASS', value = 2) => {
      const command = commandById.get(commandId);
      let score = scores.records.find((row) => row.command_id === commandId);
      if (!score) {
        score = { command_id: commandId, score: value, execution_status: executionStatus,
          rationale: 'Fixture score directly supports the selected command.', evidence_ids: evidenceIds };
        scores.records.push(score);
      }
      Object.assign(score, { page_route: command.route, procedure_id: command.procedureId,
        source: command.source, evidence_ids: evidenceIds, execution_status: executionStatus, score: value });
      return score;
    };
    const fixtureTargetKey = (level, target) => [level, target.page_id, target.test_set_id,
      target.branch_id, target.step_id, target.command_id].filter((value) => value != null).join('\u0000');
    const baseEvidenceId = 'EV-FIXTURE-CURRENT-BASE-01';
    const baseRecords = allProjectionTargets.map(([level, target]) => statusRecord(level, target, baseEvidenceId));
    results.procedure_results = [procedureFor(baseRecords, {
      method: 'Synthetic complete fixture projection',
      observation: 'Every canonical target has a retained fixture status.',
      limitations: 'This fixture validates loader behavior, not Host product behavior.',
    })];
    results.current_status_projection = { schema_version: '1.0', records: baseRecords };
    scores.records = [];
    scores.not_applicable_records = [];
    for (const commandId of commandById.keys()) ensureScore(commandId, [baseEvidenceId]);
    for (const withdrawn of scores.withdrawn_records || []) {
      const command = commandById.get(withdrawn.command_id);
      if (command) {
        withdrawn.page_route = command.route;
        withdrawn.current_execution_status = 'PASS';
        withdrawn.current_score = 2;
      } else {
        withdrawn.current_execution_status = 'STALE';
        withdrawn.current_score = null;
      }
    }
    refreshScoreCounts();
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
    const canonicalApprovalRecords = [];
    if (mode === 'snapshot-mismatch') {
      results.test_set_snapshot_sha256 = '0'.repeat(64);
    } else if (mode === 'valid-current-status' || mode === 'valid-sanitized-current-status') {
      const records = useCurrentEvidence(projectionTargets, 'EV-PROJECTION-1');
      const score = ensureScore('CLM-582fe58ab6692d1a', ['EV-PROJECTION-1'], 'PASS', 3);
      if (mode === 'valid-sanitized-current-status') {
        const procedure = results.procedure_results.at(-1);
        procedure.method = `Inspected /Users/alice/private at 2001:db8::1 with token ${'a'.repeat(64)}.`;
        procedure.observation = 'Machine 424242 returned <img src=x onerror=alert(1)>.';
        procedure.limitations = 'Scratch path /var/folders/2f/private was excluded.';
        records[0].rationale = 'password=fixture-secret remained unavailable.';
        score.rationale = 'api_key=fixture-secret; output stayed relevant.';
      }
    } else if (mode === 'valid-history') {
      const target = projectionTargets.find(([level]) => level === 'STEP')[1];
      const superseded = results.attempts.find((attempt) => attempt.qualification_superseded_by);
      const failed = statusRecord('STEP', target, 'EV-HISTORY-FAIL-1', 'FAIL', superseded.attempt_id);
      const passed = projectionRecordFor('STEP', target);
      passed.evidence_ids = ['EV-HISTORY-PASS-2'];
      appendProcedure([failed], { method: 'Initial retained check', observation: 'The first attempt failed.',
        limitations: 'The failed attempt was corrected and retained.' });
      appendProcedure([passed], { method: 'Correction retest', observation: 'The corrected retest passed.',
        limitations: 'The result is limited to the fixture target.' });
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
      const record = statusRecord('PAGE', { page_id: 'PAGE-host-market-metrics' }, 'EV-PARTIAL-PROCEDURE-1', 'PARTIAL');
      appendProcedure([record]);
    } else if (mode === 'valid-not-applicable' || mode === 'invalid-not-applicable-approval' ||
      mode === 'numeric-not-applicable-status' || mode === 'not-applicable-nondisplay') {
      const requested = mode === 'not-applicable-nondisplay'
        ? [...commandById.values()].find((item) => item.treatment !== 'NON_EXECUTABLE_DISPLAY')
        : commandById.get('CLM-9bb850ad51054679');
      const command = requested;
      const target = { page_id: command.page_id, test_set_id: command.test_set_id, branch_id: command.branch_id,
        step_id: command.step_id, command_id: command.commandId };
      const records = useCurrentEvidence([['COMMAND', target]], 'EV-FIXTURE-NOT-APPLICABLE-1', 'NOT_APPLICABLE', {
        method: 'Static inventory classification review',
        observation: 'The selected carrier is classified as not independently executable.',
        limitations: 'The owning manual diagnostic procedure remains separately assessed.',
      });
      scores.records = scores.records.filter((row) => row.command_id !== command.commandId);
      if (mode === 'numeric-not-applicable-status') {
        scores.records.push({ command_id: command.commandId, procedure_id: command.procedureId,
          page_route: command.route, source: command.source, execution_status: 'NOT_APPLICABLE',
          evidence_ids: ['EV-FIXTURE-NOT-APPLICABLE-1'], score: 2,
          rationale: 'Invalid numeric N/A fixture.' });
      } else {
        const assessment = { command_id: command.commandId, procedure_id: command.procedureId,
          page_route: command.route, source: command.source, execution_status: 'NOT_APPLICABLE',
          evidence_ids: ['EV-FIXTURE-NOT-APPLICABLE-1'], rationale: 'Display-only command name is excluded from execution scoring.',
          approval_ref: mode === 'invalid-not-applicable-approval' ? 'APPROVAL:FIXTURE-1' : 'CANONICAL_PENDING' };
        scores.not_applicable_records.push(assessment);
        if (mode !== 'invalid-not-applicable-approval') canonicalApprovalRecords.push(assessment);
      }
      assert.equal(records.length, 1);
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
      const command = commandById.get('CLM-582fe58ab6692d1a');
      const target = { page_id: command.page_id, test_set_id: command.test_set_id, branch_id: command.branch_id,
        step_id: command.step_id, command_id: command.commandId };
      const semantic = statusRecord('COMMAND', target, 'EV-SCORE-CONTEXT-1', 'UNVALIDATED');
      appendProcedure([semantic], { method: 'Static semantic assessment',
        observation: 'The command occurrence is directly relevant to the documented context.',
        limitations: 'This evidence does not establish runtime execution.' });
      ensureScore(command.commandId, ['EV-SCORE-CONTEXT-1'], 'PASS', 3);
    } else if (mode === 'score3-current-not-pass') {
      const command = [...commandById.values()][0];
      const target = { page_id: command.page_id, test_set_id: command.test_set_id, branch_id: command.branch_id,
        step_id: command.step_id, command_id: command.commandId };
      useCurrentEvidence([['COMMAND', target]], 'EV-SCORE3-BLOCKED-1', 'BLOCKED');
      ensureScore(command.commandId, ['EV-SCORE3-BLOCKED-1'], 'BLOCKED', 3);
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
    }
    if (mode === 'missing-assessment-coverage') scores.records.pop();
    if (mode === 'missing-current-projection') results.current_status_projection.records.pop();
    if (mode === 'unknown-score-command') scores.records[0].command_id = 'CLM-unknown';
    if (mode === 'score-empty-evidence') scores.records[0].evidence_ids = [];
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
      scores.withdrawn_records.find((row) => commandById.has(row.command_id)).current_score = 3;
    }
    if (mode === 'invalid-retired-withdrawal') {
      const retired = scores.withdrawn_records.find((row) => !commandById.has(row.command_id));
      retired.current_execution_status = 'PASS';
      retired.current_score = 2;
    }
    refreshScoreCounts();
    await fs.writeFile(testSetsFile, JSON.stringify(testSets));
    const snapshot = crypto.createHash('sha256').update(await fs.readFile(testSetsFile)).digest('hex');
    if (mode !== 'snapshot-mismatch') {
      results.test_set_snapshot_sha256 = snapshot;
    }
    scores.test_set_snapshot_sha256 = snapshot;
    for (const assessment of canonicalApprovalRecords) {
      assessment.approval_ref = `CANONICAL_NON_EXECUTABLE_DISPLAY:${snapshot}`;
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
    for (let i = 0; i < 80; i += 1) {
      try {
        const response = await fetch(`http://127.0.0.1:${port}/__review__/api/context?path=${encodeURIComponent(pathname)}`);
        if (response.ok) return response.json();
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
  reviewProcess = spawn(process.execPath, [
    'review-server.mjs', '--port', String(reviewPort), '--target', targetOrigin, '--dir', feedbackDir,
  ], { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] });
  reviewProcess.stdout.on('data', (chunk) => { reviewOutput += chunk; });
  reviewProcess.stderr.on('data', (chunk) => { reviewOutput += chunk; });
  await waitForReviewServer();
});

after(async () => {
  if (reviewProcess && reviewProcess.exitCode == null) {
    reviewProcess.kill('SIGTERM');
    await new Promise((resolve) => reviewProcess.once('exit', resolve));
  }
  if (targetServer) await new Promise((resolve) => targetServer.close(resolve));
  if (feedbackDir) await fs.rm(feedbackDir, { recursive: true, force: true });
});

test('Review server rejects non-loopback bind addresses', async () => {
  const result = await runReviewServer(['--host', '0.0.0.0', '--port', '0']);
  assert.notEqual(result.code, 0);
  assert.equal(result.signal, null);
  assert.match(result.output, /--host must be loopback-only/);
});

test('Host Teams shows its Jira sources and only its page blockers', async () => {
  const context = await contextFor('/host/host-teams');
  assert.deepEqual(context.epics.map((issue) => issue.key), ['CON-1187']);
  assert.deepEqual(context.issues.map((issue) => issue.key), ['CON-1581', 'CON-1584']);
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
  assert.equal(commands.flatMap((command) => command.evidence).length, 6);
  assert.ok(commands.flatMap((command) => command.evidence).every((row) => /^EV-[A-Z0-9-]+$/.test(row.ref)));
  assert.ok(commands.filter((command) => command.score || command.notApplicableAssessment).length >= 3);
  const serialized = JSON.stringify(context.verification);
  assert.doesNotMatch(serialized, /evidence_ref|source_file|source_context|test_set_snapshot_sha256|\/private\/tmp|\/Users\//);

  const network = await contextFor('/host/network-ports');
  const networkCommands = network.verification.testSets.flatMap((set) =>
    set.branches.flatMap((branch) => branch.steps.flatMap((step) => step.commands)));
  const redacted = networkCommands.find((command) => command.id === 'CLM-f93e44da84eeeef6');
  assert.match(redacted.text, /\[network-address\]/);
  assert.doesNotMatch(redacted.text, /(?:\d{1,3}\.){3}\d{1,3}/);
});

test('Missing or malformed verification input fails closed', async () => {
  assert.deepEqual((await isolatedVerificationContext()).verification, { available: false });
  for (const mode of [
    'malformed', 'snapshot-mismatch', 'schema-mismatch', 'record-type-mismatch',
    'inventory-count-mismatch', 'invalid-baseline-status', 'duplicate-canonical-command', 'stale-page-source',
    'unknown-status-target', 'duplicate-status', 'unknown-status-attempt', 'unknown-status-evidence',
    'unsafe-status-attempt', 'partial-current-status', 'partial-procedure-target',
    'mismatched-procedure-evidence', 'superseded-current-attempt', 'command-evidence-current-status',
    'unknown-score-command', 'score-empty-evidence', 'score-duplicate-evidence',
    'score-wrong-command-evidence', 'score-ancestry-mismatch', 'score-source-mismatch',
    'numeric-not-applicable-status', 'assessment-current-status-mismatch',
    'score-count-mismatch', 'invalid-not-applicable-approval', 'not-applicable-nondisplay',
    'missing-assessment-coverage', 'missing-current-projection', 'score3-current-not-pass',
    'withdrawn-current-status-mismatch', 'withdrawn-current-score-mismatch', 'invalid-retired-withdrawal',
  ]) {
    assert.deepEqual((await isolatedVerificationContext(mode)).verification, { available: false }, mode);
  }
});

test('Current status projection preserves frozen execution status and supports procedure evidence', async () => {
  const context = await isolatedVerificationContext('valid-current-status', '/host/market-metrics');
  assert.equal(context.verification.available, true);
  assert.equal(context.verification.currentStatus, 'PASS');
  assert.equal(context.verification.currentStatusAttemptId, 'ATTEMPT-FIXTURE-CURRENT-01');
  assert.deepEqual(context.verification.currentEvidenceIds, ['EV-PROJECTION-1']);
  assert.equal(context.verification.currentMethod, 'Retained static procedure review');
  assert.equal(context.verification.currentObservation, 'Sanitized fixture procedure observation.');
  assert.equal(context.verification.currentLimitations, 'No live Host product behavior was exercised.');
  const set = context.verification.testSets.find((row) => row.id === 'TS-MET-E02');
  const branch = set.branches.find((row) => row.id === 'MET-E02-current');
  const step = branch.steps.find((row) => row.id === 'MET-E02-current-s01');
  const command = step.commands.find((row) => row.id === 'CLM-582fe58ab6692d1a');
  for (const row of [set, branch, step, command]) {
    assert.equal(row.executionStatus, 'UNVALIDATED');
    assert.equal(row.currentStatus, 'PASS');
    assert.equal(row.currentStatusAttemptId, 'ATTEMPT-FIXTURE-CURRENT-01');
    assert.deepEqual(row.currentEvidenceIds, ['EV-PROJECTION-1']);
    assert.equal(row.currentMethod, 'Retained static procedure review');
    assert.equal(row.currentObservation, 'Sanitized fixture procedure observation.');
    assert.equal(row.currentLimitations, 'No live Host product behavior was exercised.');
    assert.ok(row.history.some((item) => item.evidenceIds.includes('EV-PROJECTION-1')));
  }
  assert.deepEqual(command.score.evidenceIds, ['EV-PROJECTION-1']);
  assert.equal(command.score.value, 3);
  assert.doesNotMatch(JSON.stringify(context.verification), /\/private\/tmp|\/Users\//);
});

test('Current evidence and score text are sanitized before reaching the review context', async () => {
  const context = await isolatedVerificationContext('valid-sanitized-current-status', '/host/market-metrics');
  assert.equal(context.verification.available, true);
  const serialized = JSON.stringify(context.verification);
  assert.doesNotMatch(serialized, /\/Users\/alice|\/var\/folders|2001:db8|424242|a{64}|fixture-secret/);
  assert.match(serialized, /\[local-path\]|\[network-address\]|\[identifier\]|\[redacted-token\]|\[redacted\]/);
  assert.match(context.verification.currentRationale, /password=\[redacted\]/);
  const command = context.verification.testSets.find((row) => row.id === 'TS-MET-E02').branches
    .find((row) => row.id === 'MET-E02-current').steps[0].commands
    .find((row) => row.id === 'CLM-582fe58ab6692d1a');
  assert.match(command.score.rationale, /api_key=\[redacted\]/);
});

test('Approved NOT_APPLICABLE semantic assessment remains separate from numeric scores', async () => {
  const context = await isolatedVerificationContext('valid-not-applicable', '/host/machine-errors');
  assert.equal(context.verification.available, true);
  const command = context.verification.testSets.flatMap((set) => set.branches)
    .flatMap((branch) => branch.steps).flatMap((step) => step.commands)
    .find((row) => row.id === 'CLM-9bb850ad51054679');
  assert.equal(command.executionStatus, 'NOT_APPLICABLE');
  assert.equal(command.currentStatus, 'NOT_APPLICABLE');
  assert.equal(command.score, null);
  assert.match(command.notApplicableAssessment.approvalRef,
    /^CANONICAL_NON_EXECUTABLE_DISPLAY:[a-f0-9]{64}$/);
  assert.deepEqual(command.notApplicableAssessment.evidenceIds, ['EV-FIXTURE-NOT-APPLICABLE-1']);
});

test('Semantic score evidence can remain UNVALIDATED while current execution separately supplies PASS', async () => {
  const context = await isolatedVerificationContext('valid-score-status-separation', '/host/market-metrics');
  assert.equal(context.verification.available, true);
  const command = context.verification.testSets.find((row) => row.id === 'TS-MET-E02').branches
    .find((row) => row.id === 'MET-E02-current').steps
    .find((row) => row.id === 'MET-E02-current-s01').commands
    .find((row) => row.id === 'CLM-582fe58ab6692d1a');
  assert.equal(command.currentStatus, 'PASS');
  assert.deepEqual(command.currentEvidenceIds, ['EV-FIXTURE-CURRENT-BASE-01']);
  assert.equal(command.score.value, 3);
  assert.equal(command.score.executionStatus, 'PASS');
  assert.deepEqual(command.score.evidenceIds, ['EV-SCORE-CONTEXT-1']);
  const semantic = command.history.find((row) => row.evidenceIds.includes('EV-SCORE-CONTEXT-1'));
  assert.equal(semantic.status, 'UNVALIDATED');
  assert.match(semantic.limitations, /does not establish runtime execution/);
});

test('Procedure history retains the failed attempt and linked correction retest', async () => {
  const context = await isolatedVerificationContext('valid-history', '/host/market-metrics');
  assert.equal(context.verification.available, true);
  const step = context.verification.testSets.find((row) => row.id === 'TS-MET-E02').branches
    .find((row) => row.id === 'MET-E02-current').steps
    .find((row) => row.id === 'MET-E02-current-s01');
  assert.equal(step.currentStatus, 'PASS');
  const failed = step.history.find((row) => row.evidenceIds.includes('EV-HISTORY-FAIL-1'));
  const passed = step.history.find((row) => row.evidenceIds.includes('EV-HISTORY-PASS-2'));
  assert.equal(failed.status, 'FAIL');
  assert.ok(failed.supersededBy);
  assert.equal(passed.status, 'PASS');
  assert.equal(passed.supersededBy, null);
  assert.match(passed.observation, /corrected retest passed/);
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
  assert.deepEqual(context.verification, { available: false });
});

test('Only the review proxy injects the overlay', async () => {
  const targetHtml = await (await fetch(`${targetOrigin}/host/host-teams`)).text();
  const reviewHtml = await (await fetch(`${reviewOrigin}/host/host-teams`)).text();
  assert.doesNotMatch(targetHtml, /__review__\/overlay\.js/);
  assert.match(reviewHtml, /__review__\/overlay\.js/);
  const overlay = await (await fetch(`${reviewOrigin}/__review__/overlay.js`)).text();
  assert.match(overlay, /Jira context for this page/);
  assert.match(overlay, /V&amp;V evidence for this page/);
  assert.match(overlay, /Procedure status is separate from command scoring/);
  assert.match(overlay, /Score 1 = failed to run or produced no relevant semantic result/);
  assert.match(overlay, /frozen baseline/);
  assert.match(overlay, /Current evidence/);
  assert.match(overlay, /Attempt history/);
  assert.match(overlay, /Semantic assessment: NOT_APPLICABLE/);
  assert.match(overlay, /REVIEW-TRACEABILITY\.md/);
  assert.match(overlay, /\/context\?path=/);
  assert.match(overlay, /Save JSON/);
  assert.match(overlay, /Import JSON/);
  assert.match(overlay, /\/import/);
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
  assert.match(statusHtml, /V&amp;V evidence:<\/b> 39 pages · 97 test sets · 203 branches · 468 steps · 165 commands · \d+ observations · \d+ numeric scores · \d+ approved N\/A/);
  assert.match(statusHtml, /default <code>review-feedback\/<\/code>/);
  assert.doesNotMatch(statusHtml, new RegExp(feedbackDir.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
});

test('JSON import rejects an invalid backup before writing any reviewer state', async () => {
  const response = await postJson('/__review__/api/import', {
    format: 'vast-docs-review-feedback', version: 1,
    items: [
      {
        id: 'atomic-valid', reviewer: 'Charlie', page: '/host/quickstart', comment: 'Would otherwise be valid.',
        updatedAt: '2026-07-13T10:00:00.000Z',
      },
      { id: 'atomic-invalid', page: '/host/quickstart', comment: 'Missing reviewer.' },
    ],
  });
  assert.equal(response.status, 400);
  const error = await response.json();
  assert.match(error.error, /missing a valid reviewer/);
  const charlieState = await reviewerState('Charlie');
  assert.deepEqual(charlieState.items, []);
});
