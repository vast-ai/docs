import crypto from 'node:crypto';

export const INSTALL_INTAKE_PATH = 'verification/current-host-install-evidence-intake.json';
export const INSTALL_INTAKE_SHA256 = '0092f74764903c09260e31d4315d28812495acb52ad9ed8f1c68668875fce8f9';
export const INSTALL_INTAKE_ARTIFACTS = new Map([
  ['verification/evidence/2026-09-08-h100x4-install-history-attempt-01/new-host-readonly-02.json', 'e9c94d54d406347a28c5bd771facfe918491f41169b72cebf48343c168098538'],
  ['verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-02.json', '9bd7ec9ee22058365c84d9ca567754fba75335cd4c44834968a5f2732dea77fe'],
  ['verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-02.md', 'cfd270c743ce45de355f880df41ea06b71a0eaa3839081ff012ebf41ea359616'],
  ['verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-01.md', 'e613b261bd2276876c5371893f8c28c475b9d62ceb0b8a9be5aa6c583afc5f6c'],
  ['verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/variant-preparation-01.json', '4d36484e8fd4efc6d2bd39a06c52937d1a13d28091291c38487820328a65a6a3'],
  ['verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/variant-tests-01.json', 'b1cb46f52917bcb7e6d0e6aa46598286bc7faf050e387476c8c9737c99cd0bb2'],
  ['verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/readiness-01.json', 'c8f09cf82479a252b8b24b9f33a51024ecc601fb3e3a2c0ed2a1d01b5c06ac4b'],
  ['verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/readiness-projection-01.json', '5eee9ce5556a5ace86a9780a9cca48611f5a457fa27db52c1f7a92e3174a0c53'],
  ['verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/tui-source-identity-01.json', '64b7fee9dd3f0ff33cd7dfbc0cad6b3a0d14192785d190702ef79128235652ad'],
  ['verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/source-review-summary.json', 'bdc987e0dca7396cbeee39cc3cd37c42da08528ad5955eb0533a25f4a97cd819'],
  ['verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/candidate-independent-review-02.json', 'acc7b8884f1800c212ca5aad55302746a563ae6deff081d529cdd9776c554a3e'],
  ['verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/variant-tests-02.json', 'f0453e07d2c8e014b2a53398c4f142aebf982d90c6d640d7ef1a8c8638d21d6a'],
  ['verification/evidence/2026-09-08-h100x4-direct-install-attempt-01/preflight-02.json', '99e0bd0fa0ff80ac5d1f94dc81b7d0b3ffd8afbc322d539fa2c48c1eb1b73b80'],
  ['verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/preflight-01.json', 'c2f252d719317fc7f4a5593fda6af98719b97b030bcc9fe41090b576a67b45e7'],
  ['verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/install-execution-01.json', 'a8e87044f83023153ac937e7da0d0f096629a96281337acc8e53d793308f9ed4'],
  ['verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/postcheck-02.json', 'f30120d55712dbbd5b34af9a62d12690f9ffa1e84aee0f0e515fcce74c39e9c7'],
  ['verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/machine-readback-02.json', 'e48917bcdeccebd9b957974914ac5d81255d6bcc38a3a8f967103c392210ad90'],
  ['verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/installer-findings-01.json', '1f52d5b053c61db4725cc10f6690fde471b916bd4cd621832818bae261fdf3cd'],
  ['verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/settled-01.json', 'f9623324dcbc7876b66bd2e1b493a100aabe1891c1c13b2f6d1f478608c51dd9'],
  ['verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/image-retest-01.json', '6c95a5ba5996c2462b9e364b648469e4ec747b1c3e1b814ac526060a14e1b74e'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-request-01.json', '084ad948fe6bca3f27735092a029985ce2c771f40fbac4b19ef6288db64eb66d'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-response-01.json', '6a41e583fa44e97e833a8628f40b41c7edf2a53a9bc16155256eabd24adeb373'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-readback-verification-01.json', '21c94356b1ae2cff9f968b68a9a8061e42790d1a54fbb54ae1312748aa9397b8'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-010/listing-response-01.json', '6e0a233926034ca05da8c815a692931eb465d7854504a70cd7838f255b2ec0e6'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-readback-verification-01.json', '00ea44fc85b0aad6de0d403f8f97d678c2948ee614c9524a0b42e5e273181e3f'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/gpu-result-01.json', 'aa07b6b536b638b63e11adf15e70d6baec4051c7085354f43492f7a8199b9497'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/cleanup-main.json', 'd26bf6baf80bbbc846d4601e6f7be9d0424c73b1f17198672f61b4cd302b4785'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/host-read-09.json', 'e6787b426ae82c56fb55ba7c3a8c272c1dd55accb8058b351bb5e6155b80ac46'],
]);

const ROUTE = '/host/installing-host-software';
const INVENTORY_ARTIFACT = 'verification/evidence/2026-09-08-h100x4-install-history-attempt-01/new-host-readonly-02.json';
const STATIC_ARTIFACT = 'verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-02.json';
const EXACT_RECORDS = [
  ['H100-INSTALL-INTAKE-01', 'MCL-fd7e8b86c5cfd383', 'H100-SERVICE-BASELINE', INVENTORY_ARTIFACT, 'inventory_observation', 6],
  ['H100-INSTALL-INTAKE-02', 'MCL-009da802cabe1bc9', 'H100-NO-INSTALL-BASELINE', INVENTORY_ARTIFACT, 'inventory_observation', 6],
  ['H100-INSTALL-INTAKE-03', 'MCL-ead93c85c2ff4168', 'H100-GPU-INVENTORY', INVENTORY_ARTIFACT, 'inventory_observation', 3],
  ['H100-INSTALL-INTAKE-04', 'MCL-ec2e1c9a8be1a706', 'H100-DOCKER-MOUNT-INVENTORY', INVENTORY_ARTIFACT, 'inventory_observation', 5],
  ['H100-INSTALL-INTAKE-05', 'MCL-ce118e1ce7bf71bb', 'H100-SELFTEST-HELPER-SOURCE', STATIC_ARTIFACT, 'static_finding', 'HIST-04-02-B'],
];
const SAFE_ATTEMPT = 'verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/';
const DIRECT_PREFLIGHT = 'verification/evidence/2026-09-08-h100x4-direct-install-attempt-01/preflight-02.json';
const DIRECT_PREFLIGHT_LINK = [DIRECT_PREFLIGHT, 'DIRECT_INSTALL_PREFLIGHT', 'Blocked direct-install preflight (context only; not installation proof)'];
const CURRENT_ATTEMPT = 'verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/';
const CURRENT_CONTEXT_LINKS = [
  [CURRENT_ATTEMPT + 'preflight-01.json', 'CURRENT_INSTALL_PREFLIGHT', 'September 9 direct-install preflight (sudo and guards passed)'],
  [CURRENT_ATTEMPT + 'install-execution-01.json', 'CURRENT_INSTALL_EXECUTION', 'September 9 modified direct-install execution (not stock TUI or marketplace self-test)'],
  [CURRENT_ATTEMPT + 'postcheck-02.json', 'CURRENT_INSTALL_POSTCHECK', 'September 9 independent post-install observations'],
  [CURRENT_ATTEMPT + 'machine-readback-02.json', 'CURRENT_MACHINE_READBACK', 'September 9 registered machine readback (machine 150296 remains unlisted)'],
  [CURRENT_ATTEMPT + 'installer-findings-01.json', 'CURRENT_INSTALL_FAILURES', 'September 9 retained installer subcommand failures and follow-up'],
  [CURRENT_ATTEMPT + 'settled-01.json', 'CURRENT_SETTLED_OBSERVATION', 'September 9 settled snapshot (no Docker containers or GPU compute processes)'],
  [CURRENT_ATTEMPT + 'image-retest-01.json', 'CURRENT_IMAGE_PULL_RETEST', 'September 9 image-only pull retest (passed; original installer failure preserved)'],
];
const LISTING_CONTEXT_LINKS = [
  [
    "verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-request-01.json",
    "LISTING_REQUEST",
    "September 9 listing request (approved prices; not proof of publication)"
  ],
  [
    "verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-response-01.json",
    "LISTING_REJECTION",
    "September 9 API rejection ($1/GB upload price rejected)"
  ],
  [
    "verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-readback-verification-01.json",
    "LISTING_READBACK",
    "September 9 independent readback (still unlisted; no rental started)"
  ]
];
const RENTAL_CONTEXT_LINKS = [
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-010/listing-response-01.json', 'LISTING_LOW_RATE_REJECTION', 'September 9 USD 0.10/GB listing rejection (failure retained)'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-readback-verification-01.json', 'LISTING_APPROVED_RATE_READBACK', 'September 9 USD 0.01/GB listing readback (approved terms published)'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/gpu-result-01.json', 'TINY_CLIENT_GPU_RESULT', 'September 9 tiny one-GPU client result (H100; sum of squares 1240)'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/cleanup-main.json', 'TASK_INSTANCE_CLEANUP', 'September 9 task instance cleanup (destroyed and absent)'],
  ['verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/host-read-09.json', 'FINAL_LISTED_HOST_READBACK', 'September 9 final host readback (listed approved terms; zero jobs)'],
];
const EXACT_SOURCE_LINKS = [
  [
    [SAFE_ATTEMPT + 'source-review-summary.json', 'PREPARED_ROUTE_REVIEW', 'Prepared-route source review'],
    [SAFE_ATTEMPT + 'tui-source-identity-01.json', 'TUI_SOURCE_IDENTITY', 'Local TUI source identity and timeout annotation'],
  ],
  [
    [SAFE_ATTEMPT + 'source-review-summary.json', 'PREPARED_ROUTE_REVIEW', 'Prepared-route source review'],
    [SAFE_ATTEMPT + 'variant-preparation-01.json', 'LOCAL_VARIANT_PREPARATION', 'Prepared local installer variant'],
    [SAFE_ATTEMPT + 'variant-tests-01.json', 'LOCAL_VARIANT_TESTS', 'Nine local variant checks'],
    [SAFE_ATTEMPT + 'tui-source-identity-01.json', 'TUI_SOURCE_IDENTITY', 'Local TUI source identity and timeout annotation'],
    [SAFE_ATTEMPT + 'candidate-independent-review-02.json', 'CANDIDATE_INDEPENDENT_REVIEW', 'Independent candidate-byte review'],
    [SAFE_ATTEMPT + 'variant-tests-02.json', 'LOCAL_VARIANT_RETEST', 'Reproducible nine-test retest'],
  ],
  [
    [SAFE_ATTEMPT + 'source-review-summary.json', 'PREPARED_ROUTE_REVIEW', 'Prepared-route source review'],
    [SAFE_ATTEMPT + 'readiness-01.json', 'READONLY_READINESS', 'Current read-only readiness snapshot'],
    [SAFE_ATTEMPT + 'readiness-projection-01.json', 'READINESS_PROJECTION', 'Readiness redaction projection'],
  ],
  [
    [SAFE_ATTEMPT + 'source-review-summary.json', 'PREPARED_ROUTE_REVIEW', 'Prepared-route source review'],
    [SAFE_ATTEMPT + 'readiness-01.json', 'READONLY_READINESS', 'Current read-only readiness snapshot'],
    [SAFE_ATTEMPT + 'readiness-projection-01.json', 'READINESS_PROJECTION', 'Readiness redaction projection'],
  ],
  [
    [SAFE_ATTEMPT + 'source-review-summary.json', 'PREPARED_ROUTE_REVIEW', 'Prepared-route source review'],
    [SAFE_ATTEMPT + 'variant-preparation-01.json', 'LOCAL_VARIANT_PREPARATION', 'Prepared local installer variant'],
    [SAFE_ATTEMPT + 'variant-tests-01.json', 'LOCAL_VARIANT_TESTS', 'Nine local variant checks'],
    [SAFE_ATTEMPT + 'tui-source-identity-01.json', 'TUI_SOURCE_IDENTITY', 'Local TUI source identity and timeout annotation'],
    [SAFE_ATTEMPT + 'candidate-independent-review-02.json', 'CANDIDATE_INDEPENDENT_REVIEW', 'Independent candidate-byte review'],
    [SAFE_ATTEMPT + 'variant-tests-02.json', 'LOCAL_VARIANT_RETEST', 'Reproducible nine-test retest'],
  ],
];
const sha = (value) => crypto.createHash('sha256').update(value).digest('hex');
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const exactKeys = (value, keys, message) => {
  if (!value || typeof value !== 'object' || Array.isArray(value) || !same(Object.keys(value).sort(), [...keys].sort())) throw new Error(message);
};
const text = (value, message) => {
  if (typeof value !== 'string' || !value.trim()) throw new Error(message);
  return value;
};

function exactArtifactMap(input, read) {
  if (!Array.isArray(input.artifacts) || input.artifacts.length !== INSTALL_INTAKE_ARTIFACTS.size) throw new Error('Invalid installation intake artifacts');
  const refs = new Set();
  for (const item of input.artifacts) {
    exactKeys(item, ['artifact_ref', 'artifact_sha256', 'role'], 'Invalid installation intake artifact');
    const expected = INSTALL_INTAKE_ARTIFACTS.get(item.artifact_ref);
    if (!expected || item.artifact_sha256 !== expected || refs.has(item.artifact_ref) || !/^[A-Z_]+$/.test(item.role)) throw new Error('Invalid installation intake artifact');
    if (sha(read(item.artifact_ref)) !== expected) throw new Error(`Installation intake artifact hash drift: ${item.artifact_ref}`);
    refs.add(item.artifact_ref);
  }
  return refs;
}

function selectedCheck(check, read) {
  exactKeys(check, ['id', 'artifact_ref', 'selector', 'scope'], 'Invalid installation intake check');
  if (!INSTALL_INTAKE_ARTIFACTS.has(check.artifact_ref) || !/^[A-Z0-9-]+$/.test(check.id)) throw new Error('Invalid installation intake check');
  const raw = read(check.artifact_ref);
  exactKeys(check.selector, check.selector?.kind === 'inventory_observation'
    ? ['kind', 'index', 'stdout_sha256'] : ['kind', 'finding_id'], 'Invalid installation intake selector');
  if (check.selector.kind === 'inventory_observation') {
    if (check.artifact_ref !== INVENTORY_ARTIFACT) throw new Error('Invalid installation intake check artifact kind');
    const artifact = JSON.parse(raw);
    const observation = artifact.observations?.[check.selector.index];
    if (!Number.isInteger(check.selector.index) || !observation || typeof observation.stdout !== 'string' || sha(observation.stdout) !== check.selector.stdout_sha256) throw new Error('Installation intake observation drift');
    return { id: check.id, artifactRef: check.artifact_ref, artifactSha256: sha(raw), selector: check.selector, scope: text(check.scope, 'Invalid installation intake check'), observation };
  }
  if (check.selector.kind === 'static_finding') {
    if (check.artifact_ref !== STATIC_ARTIFACT) throw new Error('Invalid installation intake check artifact kind');
    const artifact = JSON.parse(raw);
    const finding = artifact.static_findings?.find((item) => item.id === check.selector.finding_id);
    if (!finding) throw new Error('Installation intake static finding drift');
    return { id: check.id, artifactRef: check.artifact_ref, artifactSha256: sha(raw), selector: check.selector, scope: text(check.scope, 'Invalid installation intake check'), finding };
  }
  throw new Error('Invalid installation intake selector');
}

export function validateInstallEvidenceIntake({ inputBytes, read, model, enforceInputHash = true }) {
  if (enforceInputHash && sha(inputBytes) !== INSTALL_INTAKE_SHA256) throw new Error('Installation intake input hash drift');
  const input = JSON.parse(inputBytes);
  exactKeys(input, ['schema_version', 'artifact_type', 'purpose', 'recorded_at', 'artifacts', 'records'], 'Invalid installation evidence intake');
  if (input.schema_version !== 1 || input.artifact_type !== 'CURRENT_HOST_INSTALL_EVIDENCE_INTAKE' || input.purpose !== 'DISPLAY_ONLY_INSTALL_CONTEXT' || !/^\d{4}-\d{2}-\d{2}$/.test(input.recorded_at)) throw new Error('Invalid installation evidence intake');
  const artifacts = exactArtifactMap(input, read);
  if (!Array.isArray(input.records) || input.records.length !== 5) throw new Error('Invalid installation intake records');
  const claims = new Map(model.pages.flatMap((page) => page.claims.map((claim) => [claim.id, { claim, page }])));
  const seen = new Set();
  const records = input.records.map((record, index) => {
    exactKeys(record, ['id', 'claim_id', 'route', 'title', 'page_sha256', 'text', 'headings', 'spans', 'coverage', 'limit', 'remaining_action', 'checks', 'source_links'], 'Invalid installation intake record');
    const found = claims.get(record.claim_id);
    if (!found || seen.has(record.claim_id) || record.route !== ROUTE || found.page.route !== ROUTE || record.title !== found.page.title || record.page_sha256 !== found.page.source_sha256 ||
      record.text !== found.claim.text || !same(record.headings, found.claim.headings) || !same(record.spans, found.claim.spans) || !/^[A-Z0-9-]+$/.test(record.id) || !/^[A-Z_]+$/.test(record.coverage)) throw new Error(`Installation intake source text/span drift: ${record.claim_id}`);
    seen.add(record.claim_id);
    const expected = EXACT_RECORDS[index];
    if (!expected || record.id !== expected[0] || record.claim_id !== expected[1] || !Array.isArray(record.checks) || record.checks.length !== 1 || !Array.isArray(record.source_links)) throw new Error('Invalid installation intake record contract');
    const checks = record.checks.map((check) => selectedCheck(check, read));
    if (checks[0].id !== expected[2] || checks[0].artifactRef !== expected[3] || checks[0].selector.kind !== expected[4] ||
      (expected[4] === 'inventory_observation' ? checks[0].selector.index : checks[0].selector.finding_id) !== expected[5]) throw new Error('Invalid installation intake check contract');
    const sourceLinks = record.source_links.map((link) => {
      exactKeys(link, ['artifact_ref', 'role', 'label'], 'Invalid installation intake source link');
      if (!artifacts.has(link.artifact_ref) || !/^[A-Z_]+$/.test(link.role)) throw new Error('Invalid installation intake source link');
      return { artifactRef: link.artifact_ref, artifactSha256: INSTALL_INTAKE_ARTIFACTS.get(link.artifact_ref), role: link.role, label: text(link.label, 'Invalid installation intake source link') };
    });
    const expectedLinks = [
      ...(index === 0 ? [['verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-01.md', 'CORRECTION_HISTORY', 'Earlier static installer/TUI inspection']] : []),
      ...(index === 1 ? [['verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-02.md', 'CURRENT_STATIC_SOURCE', 'Static installer/helper boundary']] : []),
      ...(index === 4 ? [
        ['verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-02.md', 'CURRENT_STATIC_SOURCE', 'Static updater/self-test-helper inspection'],
        ['verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-01.md', 'CORRECTION_HISTORY', 'Earlier inspection and correction history'],
      ] : []),
      ...EXACT_SOURCE_LINKS[index],
      DIRECT_PREFLIGHT_LINK,
      ...CURRENT_CONTEXT_LINKS,
      ...LISTING_CONTEXT_LINKS,
      ...RENTAL_CONTEXT_LINKS,
    ];
    if (!same(sourceLinks.map((link) => [link.artifactRef, link.role, link.label]), expectedLinks)) throw new Error('Invalid installation intake source-link contract');
    return { id: record.id, claimId: record.claim_id, route: record.route, pageTitle: record.title, headings: record.headings, coverage: record.coverage,
      limit: text(record.limit, 'Invalid installation intake limit'), remainingAction: text(record.remaining_action, 'Invalid installation intake action'), checks, sourceLinks };
  });
  return { recordedAt: input.recorded_at, message: 'September 9 modified direct installation completed with retained warnings and failures; four active services, four H100 GPUs, and XFS project quotas were independently observed. Earlier USD 1/GB and USD 0.10/GB listing requests were rejected and remain retained failures. Machine 150296 is now listed at USD 0.01/GB in both directions with the approved GPU, storage, bid, discount, and expiry terms. Client test instance 50364501 ran one tiny H100 computation (sum of squares 1240) and was destroyed; final Host readback shows zero jobs. This does not validate SSH, a full marketplace self-test, the stock TUI, reboot persistence, or final billing.', records, artifactRefs: [...artifacts] };
}

export function loadInstallEvidenceIntake({ read, model }) {
  return validateInstallEvidenceIntake({ inputBytes: read(INSTALL_INTAKE_PATH), read, model });
}
