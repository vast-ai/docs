/** Offline presentation export. Never changes the V&V input or its statuses. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import net from 'node:net';
import { fileURLToPath } from 'node:url';
import { INSTALL_INTAKE_PATH, loadInstallEvidenceIntake } from './current_host_install_evidence_intake.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const inputPath = 'verification/current-host-docs-review.json';
const attempt = 'verification/evidence/2026-09-08-host-live-readonly-attempt-01';
const supplementalAttempt = 'verification/evidence/2026-09-08-host-live-readonly-attempt-01';
const supplementalMapPath = `${supplementalAttempt}/check-to-claim-map.json`;
const currentAttempt = 'verification/evidence/2026-09-08-host-client-unblocking-attempt-01';
const currentMapPath = `${currentAttempt}/check-to-claim-map.json`;
// Explicit current-attempt selection, not an assertion that integration or
// sealing is complete. The retained result states its own scope and status.
const currentConnectionAttempt = 'verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01';
const currentResultPath = `${currentConnectionAttempt}/result.md`;
// Share the reviewed operational summary and the two separate open-work
// registers. Do not recursively embed private captures or the final seal:
// the final validation artifacts hash this generated HTML independently.
const currentAttemptArtifacts = ['operations-result-01.md', 'runtime-operator-register.md', 'source-owner-register.md']
  .map(name => `${currentConnectionAttempt}/${name}`);
const claimCorrectionAttempt = 'verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01';
const claimCorrectionResultPath = `${claimCorrectionAttempt}/result.md`;
const claimCorrectionArtifacts = [
  `${claimCorrectionAttempt}/final-integrity-01.json`, `${claimCorrectionAttempt}/python-full-retest-02.json`,
  `${claimCorrectionAttempt}/reviewer-full-retest-03.json`, `${claimCorrectionAttempt}/current-generator-final-01.json`,
  `${claimCorrectionAttempt}/html-current-retest-01.json`,
];
// Retained repository/interface checks from the later integration attempt.
// They are explicit inputs to this presentation and are not a new result phase
// or a basis for a product-status change.
const repositoryReconciliationAttempt = 'verification/evidence/2026-09-09-host-repository-live-merge-attempt-01';
const repositoryReconciliation = {
  generated_routes_ref: `${repositoryReconciliationAttempt}/generated-route-reconciliation-01.json`,
  mint_links_ref: `${repositoryReconciliationAttempt}/mint-links-post-exclusion-02.json`,
  mint_accessibility_ref: `${repositoryReconciliationAttempt}/mint-a11y-retest-01.json`,
  rendered_theme_ref: `${repositoryReconciliationAttempt}/rendered-theme-token-01.json`,
};
const twoDefectTransitionPath = 'verification/current-two-defect-transition.json';
const twoDefectTransitionSha256 = '14b51b3a15dc3f21c7c4fc7a911cb7c5f2964b07924d188e4d0c7e700124aea8';
const supplementalArtifacts = new Set([
  `${supplementalAttempt}/batch-b-execution-02.json`,
  `${supplementalAttempt}/batch-d-cli-execution-01.json`,
  `${supplementalAttempt}/batch-e-cli-execution-01.json`,
]);
const historicalSummaryPath = `${currentAttempt}/result.md`;
const earlierBaselineSummaryPath = 'verification/evidence/2026-09-07-host-current-vv-attempt-01/result.md';
const priorityPath = 'verification/HOST-DOCS-CLAIMS-TO-RESOLVE.md';
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const read = (ref) => {
  if (!/^(verification|host|snippets|cli|python)\//.test(ref) || ref.split('/').includes('..')) throw new Error(`Unsafe export path: ${ref}`);
  const resolved = fs.realpathSync(path.join(root, ref));
  if (!resolved.startsWith(root + path.sep)) throw new Error('Export symlink escapes repository');
  return fs.readFileSync(resolved);
};

// Same display boundaries as the local reviewer. Original source digests remain
// visible; a masked display copy must never be presented as byte-identical proof.
export function sanitize(value) {
  return String(value)
    .replace(/(^|[\s"'(])\.orchestra\/[^\s"'<>]*/gm, '$1[redacted-agent-metadata]')
    .replace(/\/(?:Users|home|root|private\/tmp|tmp|var\/folders)\/[^\s"'<>]+/g, '[redacted-local-path]')
    .replace(/[A-Za-z]:\\Users\\[^\s"'<>]+/g, '[redacted-local-path]')
    .replace(/\b[A-Z0-9._%+-]+@(?:[A-Z0-9-]+\.)+[A-Z]{2,}\b/gi, s => /@example\.(com|net|org)$/i.test(s) ? s : '[redacted-email]')
    .replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g, s => {
      const [a, b, c, d] = s.split('.').map(Number);
      return [a,b,c,d].some(v => v > 255) || a === 127 || s === '0.0.0.0' || s === '255.255.255.255' ||
        (a === 192 && b === 0 && c === 2) || (a === 198 && b === 51 && c === 100) || (a === 203 && b === 0 && c === 113) ? s : '[redacted-address]';
    })
    .replace(/(?<![A-Za-z0-9])[\[\]A-Fa-f0-9:]{2,}(?![A-Za-z0-9])/g, s => {
      const candidate = s.replace(/^\[|\]$/g, '');
      return net.isIP(candidate) !== 6 || candidate === '::' || candidate === '::1' || /^2001:db8(?::|$)/i.test(candidate) ? s : '[redacted-address]';
    })
    .replace(/\b((?:authorization|proxy-authorization)\s*:\s*(?:bearer|basic)\s+)([^\s,;]+)/gi, '$1[redacted]')
    .replace(/\b((?:api[-_ ]?key|access[-_ ]?token|secret|password|VAST_API_KEY)\s*[:=]\s*)("[^"]*"|'[^']*'|[^\s,;]+)/gi, (all, prefix, v) => /^(?:\$|<|\[|YOUR|EXAMPLE|DUMMY|TEST|X{3,})/i.test(v.replace(/^['"]|['"]$/g, '')) ? all : `${prefix}[redacted]`)
    .replace(/\b(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b/g, '[redacted-token]')
    .replace(/\b((?:machine|instance|offer|account|user|host)(?:[-_ ]?id)?(?:\s*(?:[:=#]|is))?\s*`?)(\d{4,})(`?)/gi, (s,p,n,e) => n === '12345' || /^0+$/.test(n) ? s : `${p}[redacted-identifier]${e}`)
    .replace(/((?:["']?(?:machine|instance|offer|account|user|host)[_-]id["']?\s*[:=]\s*["']?))(\d{4,})(["']?)/gi, (s,p,n,e) => n === '12345' || /^0+$/.test(n) ? s : `${p}[redacted-identifier]${e}`);
}

function sameJson(left, right) { return JSON.stringify(left) === JSON.stringify(right); }

function twoDefectTransition() {
  const bytes = read(twoDefectTransitionPath);
  if (sha(bytes) !== twoDefectTransitionSha256) throw new Error('Two-defect transition registry hash drift');
  const transition = JSON.parse(bytes);
  if (transition?.id !== 'CURRENT-TWO-DEFECT-TRANSITION-01' ||
    transition?.artifact_type !== 'EXACT_TWO_DEFECT_SOURCE_TRANSITION' ||
    !transition.current_pages || !transition.unmodified_claim_inventory || !transition.historical_fail_records) {
    throw new Error('Invalid two-defect transition registry');
  }
  return transition;
}

function transitionUnmodifiedHistory(record, claim, page) {
  const transition = twoDefectTransition();
  const pageBinding = transition.current_pages?.[record.route];
  const inventory = transition.unmodified_claim_inventory?.[record.route];
  const row = Array.isArray(inventory) ? inventory.find((item) => item?.id === record.id) : null;
  if (!pageBinding || !row || page.source_sha256 !== pageBinding.sha256 || record.page_sha256 !== pageBinding.snapshot_sha256 ||
    claim.coverage_state !== 'CHANGED' || claim.history?.carry_decision !== 'TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL' ||
    record.text !== row.text || !sameJson(record.headings, row.headings) || !sameJson(record.spans, row.spans) ||
    claim.text !== row.text || !sameJson(claim.headings, row.headings) ||
    !sameJson(claim.spans, row.spans) || claim.status !== row.historical_status) return false;
  return true;
}

function transitionHistoricalFail(record) {
  const transition = twoDefectTransition();
  const row = transition.historical_fail_records?.[record.route];
  const old = row?.old_fail_claim;
  return old && old.id === record.id && old.status === 'FAIL' && old.text === record.text &&
    sameJson(old.headings, record.headings) && sameJson(old.spans, record.spans) &&
    record.page_sha256 === transition.current_pages?.[record.route]?.snapshot_sha256 ? old : null;
}

function supplementalCoverage(coverage) {
  if (coverage === 'ALL_DOCUMENTED_INVOCATIONS') return { level: 'FULL', label: 'All documented invocations were exercised, within the stated limits.' };
  if (coverage === 'EXACT_SINGLE_COMMAND' || coverage === 'EXACT_COMMAND_EMPTY_BRANCH') return { level: 'EXACT', label: 'The exact recorded command/branch was exercised, within the stated limits.' };
  return { level: 'PARTIAL', label: 'Partial or related observation only; it is not whole-claim proof.' };
}

function supplementalLiveChecks(claims, pages, add) {
  const map = JSON.parse(read(supplementalMapPath));
  if (map.record_type !== 'SUPPLEMENTAL_LIVE_CHECK_TO_CLAIM_MAP' || !Array.isArray(map.records) || typeof map.recorded_at !== 'string') {
    throw new Error('Invalid supplemental live-check map');
  }
  const claimsById = new Map(claims.map((claim) => [claim.id, claim]));
  const pagesByRoute = new Map(pages.map((page) => [page.route, page]));
  const artifacts = new Map();
  for (const ref of supplementalArtifacts) {
    const artifact = JSON.parse(read(ref));
    const checks = Array.isArray(artifact.checks) ? artifact.checks : artifact.records;
    if (!Array.isArray(checks)) throw new Error(`Invalid supplemental record: ${ref}`);
    artifacts.set(ref, new Map(checks.map((check) => [check.check_id, check])));
    add(ref);
  }
  const seen = new Set();
  const mapped = map.records.map((record) => {
    if (!record || typeof record.id !== 'string' || seen.has(record.id)) throw new Error('Invalid supplemental claim identity');
    seen.add(record.id);
    const claim = claimsById.get(record.id);
    const page = pagesByRoute.get(record.route);
    const exactCurrentSource = claim && page && record.title === page.title && record.page_sha256 === page.source_sha256 &&
      record.text === claim.text && sameJson(record.headings, claim.headings) && sameJson(record.spans, claim.spans);
    const exactTransitionHistory = !exactCurrentSource && claim && page && record.title === page.title && transitionUnmodifiedHistory(record, claim, page);
    if ((!exactCurrentSource && !exactTransitionHistory) ||
      !Array.isArray(record.checks) || !Array.isArray(record.evidence) || record.checks.length !== record.evidence.length ||
      typeof record.coverage !== 'string' || typeof record.limit !== 'string' || typeof record.next !== 'string') {
      throw new Error(`Supplemental source text/span drift: ${record.id}`);
    }
    const checks = record.evidence.map((evidence, index) => {
      if (!evidence || evidence.check_id !== record.checks[index] || typeof evidence.artifact_ref !== 'string' ||
        !/^[a-z0-9-]+\.json$/.test(evidence.artifact_ref)) throw new Error(`Invalid supplemental evidence: ${record.id}`);
      const artifactRef = `${supplementalAttempt}/${evidence.artifact_ref}`;
      const artifact = artifacts.get(artifactRef);
      const check = artifact?.get(evidence.check_id);
      if (!check) throw new Error(`Missing supplemental check: ${record.id}/${evidence.check_id}`);
      const command = typeof check.command === 'string' ? check.command :
        (Array.isArray(check.argv) ? `vastai ${check.argv.map(arg => /\s/.test(arg) ? JSON.stringify(arg) : arg).join(' ')}` : null);
      if (!command) throw new Error(`Supplemental check has no command: ${record.id}/${evidence.check_id}`);
      return { id: evidence.check_id, artifact_ref: artifactRef, command,
        result: check.observation_status || (check.exit_code === 0 ? 'EXECUTED_EXIT_0' :
          (check.check_id === 'B07' && check.command === 'findmnt /data0' && check.exit_code === 1 && !check.stdout.trim() ? 'EXPECTED_ABSENCE' : 'RECORDED_NONZERO')),
        limit: check.limit || check.scope || check.expected_result_basis || 'See retained record for scope and output.' };
    });
    return { claim_id: claim.id, route: page.route, page_title: page.title, headings: claim.headings,
      coverage: supplementalCoverage(record.coverage), limit: record.limit, next: record.next, checks };
  });
  const hostChecks = artifacts.get(`${supplementalAttempt}/batch-b-execution-02.json`).size;
  const cliChecks = artifacts.get(`${supplementalAttempt}/batch-d-cli-execution-01.json`).size +
    artifacts.get(`${supplementalAttempt}/batch-e-cli-execution-01.json`).size;
  if (mapped.length !== 20 || hostChecks !== 20 || cliChecks !== 21) throw new Error('Unexpected supplemental live-check coverage');
  add(supplementalMapPath);
  return { recorded_at: map.recorded_at, mapped_claims: mapped,
    summary: { host_checks: hostChecks, cli_checks: cliChecks, api_checks: 6, total_checks: 47,
      note: 'Six direct API reads: three Market Metrics endpoints plus selected-machine, maintenance and reports reads. Only the three Market Metrics endpoint-description claims have separate API PASS adjudications. All 15 documented Market Metrics CLI examples also ran; those are separate command observations, not additional API-claim closures.' } };
}

function captureCheck(artifact, checkId) {
  const parsed = JSON.parse(read(artifact));
  const candidates = Array.isArray(parsed.checks) ? parsed.checks :
    (Array.isArray(parsed.records) ? parsed.records : [parsed]);
  const check = candidates.find((candidate) => candidate?.check_id === checkId);
  if (!check) throw new Error(`Missing retained check: ${artifact}/${checkId}`);
  const command = typeof check.command === 'string' ? check.command :
    (Array.isArray(check.argv) ? `vastai ${check.argv.map(arg => /\s/.test(arg) ? JSON.stringify(arg) : arg).join(' ')}` : null);
  if (!command) throw new Error(`Retained check has no command: ${artifact}/${checkId}`);
  return { check, command };
}

// This is intentionally a second map rather than an amendment to the 47-check
// historical map. It binds a selected current observation to an exact claim and
// keeps status adjudication in current-host-docs-review.json.
function currentReadonlyChecks(claims, pages, add) {
  const mapBytes = read(currentMapPath);
  const map = JSON.parse(mapBytes);
  if (map.record_type !== 'CURRENT_HOST_READONLY_CHECK_TO_CLAIM_MAP' ||
    map.attempt_ref !== currentAttempt || !Array.isArray(map.records) ||
    typeof map.recorded_at !== 'string') throw new Error('Invalid current read-only check map');
  const claimsById = new Map(claims.map((claim) => [claim.id, claim]));
  const pagesByRoute = new Map(pages.map((page) => [page.route, page]));
  if (!Array.isArray(map.context_artifacts)) throw new Error('Invalid current context-artifact list');
  for (const item of map.context_artifacts) {
    if (!item || !/^[a-z0-9-]+\.json$/.test(item.artifact_ref || '') || !/^[a-f0-9]{64}$/.test(item.artifact_sha256 || '')) {
      throw new Error('Invalid current context artifact');
    }
    const ref = `${currentAttempt}/${item.artifact_ref}`, raw = read(ref);
    if (sha(raw) !== item.artifact_sha256) throw new Error(`Current context capture hash drift: ${item.artifact_ref}`);
    add(ref);
  }
  const seen = new Set();
  const historicalSuperseded = [];
  const mapped = map.records.map((record) => {
    if (!record || typeof record.id !== 'string' || seen.has(record.id)) throw new Error('Invalid current claim identity');
    seen.add(record.id);
    const claim = claimsById.get(record.id), page = pagesByRoute.get(record.route);
    const historical = !claim ? transitionHistoricalFail(record) : null;
    const exactCurrentSource = claim && page && record.title === page.title && record.page_sha256 === page.source_sha256 &&
      record.text === claim.text && sameJson(record.headings, claim.headings) && sameJson(record.spans, claim.spans);
    const exactTransitionHistory = !exactCurrentSource && claim && page && record.title === page.title &&
      transitionUnmodifiedHistory(record, claim, page);
    if ((!historical && !exactCurrentSource && !exactTransitionHistory) ||
      !Array.isArray(record.evidence) || !record.evidence.length || typeof record.coverage !== 'string' ||
      typeof record.limit !== 'string' || typeof record.next !== 'string') {
      throw new Error(`Current source text/span drift: ${record.id}`);
    }
    const evidence = record.evidence.map((item) => {
      if (!item || typeof item.artifact_ref !== 'string' || !/^[a-z0-9-]+\.json$/.test(item.artifact_ref) ||
        !/^[a-f0-9]{64}$/.test(item.artifact_sha256 || '') || typeof item.check_id !== 'string') {
        throw new Error(`Invalid current evidence: ${record.id}`);
      }
      const artifactRef = `${currentAttempt}/${item.artifact_ref}`;
      const raw = read(artifactRef);
      if (sha(raw) !== item.artifact_sha256) throw new Error(`Current capture hash drift: ${record.id}/${item.check_id}`);
      const {check, command} = captureCheck(artifactRef, item.check_id);
      add(artifactRef);
      return { id: item.check_id, artifact_ref: artifactRef, command,
        result: check.observation_status || check.status || (check.exit_code === 0 ? 'RECORDED_EXIT_0' : 'RECORDED_NONZERO'),
        limit: item.limit || check.scope || 'See retained record for scope and output.' };
    });
    if (historical) {
      historicalSuperseded.push({ historical_claim_id: historical.id, route: record.route, page_title: record.title,
        text: historical.text, headings: historical.headings, spans: historical.spans, status: historical.status,
        rationale: historical.rationale, next_action: historical.next_action, limit: record.limit, checks: evidence,
        transition_ref: twoDefectTransitionPath,
        context: 'Historical FAIL retained from the signed source-transition record; it is not a current claim binding or a replacement status.' });
      return null;
    }
    return { claim_id: claim.id, route: page.route, page_title: page.title, headings: claim.headings,
      coverage: {level: record.coverage, label: record.coverage_label || 'Selected current observation; read the stated limit.'},
      limit: record.limit, next: record.next, checks: evidence, map_ref: currentMapPath };
  }).filter(Boolean);
  add(currentMapPath);
  return {recorded_at: map.recorded_at, mapped_claims: mapped, historical_superseded: historicalSuperseded,
    summary: map.summary || 'Current read-only follow-up observations are selected check proof, not a blanket status promotion.'};
}

export function buildReport() {
  const bytes = read(inputPath);
  const model = JSON.parse(bytes);
  const claims = model.pages.flatMap(page => page.claims.map(claim => ({ ...claim, route: page.route, page_title: page.title })));
  const ids = new Set(claims.map(c => c.id));
  if (ids.size !== claims.length || claims.length !== model.counts.claims) throw new Error('Claim inventory mismatch');
  const statuses = Object.fromEntries(Object.keys(model.counts.claim_statuses).map(s => [s, claims.filter(c => c.status === s).length]));
  if (JSON.stringify(statuses) !== JSON.stringify(model.counts.claim_statuses)) throw new Error('Status mismatch');
  const files = new Map();
  const add = (ref, expected) => {
    if (files.has(ref)) return;
    const raw = read(ref);
    if (raw.includes(0)) throw new Error(`Binary evidence excluded: ${ref}`);
    if (expected && sha(raw) !== expected) throw new Error(`Source no longer matches snapshot: ${ref}`);
    const text = raw.toString('utf8'), display = sanitize(text);
    files.set(ref, { ref, sha256: sha(raw), display_sha256: sha(display), masked: text !== display, text: display });
  };
  for (const p of model.pages) {
    add(p.source_file, p.source_sha256);
    for (const d of p.dependencies || []) add(d.source_file, d.source_sha256);
  }
  for (const c of claims) for (const e of c.evidence_refs || []) if (e.artifact_ref) add(e.artifact_ref);
  const supplementalLive = supplementalLiveChecks(claims, model.pages, add);
  const currentReadonly = currentReadonlyChecks(claims, model.pages, add);
  const installationIntake = loadInstallEvidenceIntake({ read, model });
  add(INSTALL_INTAKE_PATH);
  for (const ref of installationIntake.artifactRefs) add(ref);
  add(currentResultPath); add(claimCorrectionResultPath);
  for (const ref of currentAttemptArtifacts) add(ref);
  for (const ref of claimCorrectionArtifacts) add(ref);
  for (const ref of Object.values(repositoryReconciliation)) add(ref);
  add(historicalSummaryPath); add(earlierBaselineSummaryPath); add(priorityPath);
  // Include the result's directly linked evidence, but never crawl arbitrary paths
  // or raw nested logs (which may have separate disclosure restrictions).
  for (const summaryRef of [historicalSummaryPath, earlierBaselineSummaryPath]) {
   const summaryFolder = path.posix.dirname(summaryRef);
   for (const match of read(summaryRef).toString('utf8').matchAll(/\]\(([^)#]+)(?:#[^)]*)?\)/g)) {
    if (/^[a-z]+:/i.test(match[1])) continue;
    const ref = path.posix.normalize(path.posix.join(summaryFolder, match[1]));
    if (ref.startsWith(summaryFolder + '/') || /verification\/current-host-(claim-corrections|editorial-classifications)\.json$/.test(ref)) add(ref);
   }
  }
  const displayClaims = claims.map(c => {
    const out = JSON.parse(JSON.stringify(c, (_, v) => typeof v === 'string' ? sanitize(v) : v));
    out.display_masked = out.text !== c.text;
    return out;
  });
  const payload = {
    export_version: 1, snapshot_at: model.generated_at, export_date: '2026-09-09',
    input: { ref: inputPath, sha256: sha(bytes), revision: model.source.revision, tree: model.source.tree },
    counts: model.counts, current_result_ref: currentResultPath, claim_correction_history_ref: claimCorrectionResultPath,
    historical_summary_ref: historicalSummaryPath, earlier_baseline_summary_ref: earlierBaselineSummaryPath, priority_ref: priorityPath,
    repository_reconciliation: repositoryReconciliation,
    pages: model.pages.map(({ claims: ignoredClaims, procedures: ignoredProcedures, ...p }) => p),
    claims: displayClaims,
    supplemental_live_checks: JSON.parse(JSON.stringify(supplementalLive, (_, value) => typeof value === 'string' ? sanitize(value) : value)),
    current_readonly_checks: JSON.parse(JSON.stringify(currentReadonly, (_, value) => typeof value === 'string' ? sanitize(value) : value)),
    installation_evidence_intake: JSON.parse(JSON.stringify(installationIntake, (_, value) => typeof value === 'string' ? sanitize(value) : value)),
    support_layers: model.support_layers,
    files: Object.fromEntries(files),
  };
  const json = JSON.stringify(payload).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
  const template = fs.readFileSync(path.join(root, 'scripts/templates/host-docs-review.html'), 'utf8');
  if (template.split('/*__REPORT_DATA__*/').length !== 2) throw new Error('Expected exactly one data slot');
  const html = template
    .replace('__INPUT_SHA256__', payload.input.sha256)
    .replace('/*__REPORT_DATA__*/', () => json);
  return { html, payload, manifest: {
    schema_version: 1, export_date: payload.export_date, input: payload.input,
    html_sha256: sha(html), counts: payload.counts,
    claim_ids_sha256: sha(JSON.stringify(displayClaims.map(c => [c.id,c.status]))),
    embedded_files: [...files.values()].map(({text, ...f}) => f),
    masked_claim_displays: displayClaims.filter(c => c.display_masked).length,
    limit: 'Presentation-only snapshot. No status changes or new product validation. Embedded display copies may be masked; original digests retained. Nested raw logs are not bundled. Source wording is not evidence for itself.',
  }};
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const {html, manifest} = buildReport();
  const htmlPath = path.join(root, 'verification/host-docs-review.html');
  const manifestPath = path.join(root, 'verification/host-docs-review-export.json');
  if (process.argv.includes('--check')) {
    if (fs.readFileSync(htmlPath, 'utf8') !== html || fs.readFileSync(manifestPath, 'utf8') !== JSON.stringify(manifest,null,2)+'\n') throw new Error('Export drift');
  } else {
    fs.writeFileSync(htmlPath, html);
    fs.writeFileSync(manifestPath, JSON.stringify(manifest,null,2)+'\n');
  }
  console.log(JSON.stringify({result:'PASS',mode:process.argv.includes('--check')?'check':'build',claims:manifest.counts.claims,files:manifest.embedded_files.length,bytes:Buffer.byteLength(html),html_sha256:manifest.html_sha256,masked_claims:manifest.masked_claim_displays}));
}
