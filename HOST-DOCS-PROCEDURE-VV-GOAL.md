# GOAL: Rebaseline and complete Host Docs V&V as page-level procedures

## Working context

- Repository: `/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk`
- Review target: `vast-ai/docs` PR #185
- Jira: `CON-1518`
- Reviewer interface: `http://localhost:4000/host/hosting-overview`
- Live target alias: `HOST_VV_TARGET`, resolved only from an approved restricted record
  outside Git using the machine, SSH, WAN, and forwarded-port details already supplied by
  the user.

Do not copy the restricted target record, credentials, private network details, raw
machine/account/offer/instance identifiers, or unrestricted diagnostic output into this
goal file, Git, PR comments, Jira, or the public review projection.

## Objective

Use the installed `$vv-evidence` skill in `PLAN_AND_EXECUTE` mode to rebuild the Host
Docs V&V plan around complete user procedures rather than isolated command strings,
execute every authorized procedure with a claim-suitable method, retain independently
reviewable evidence, audit the surrounding documentation semantically, correct and
retest authorized documentation defects, expose sanitized page-specific evidence in the
existing review interface, and prepare an accurate reviewer handoff for PR #185 and Jira
CON-1518 without posting it.

The repository-local evidence structure is complete when every in-scope Host page and every
discovered procedure has a traceable disposition. That structural result does not complete
runtime/operator or source-owner work, does not mean every procedure passes, and does not
authorize the agent to approve, accept, post, push, or merge its own work.

## Mandatory methodological reset

Do not treat the existing 176 unique command strings, 203 command source occurrences,
407 combined command/behavior semantic occurrences, 474 unique extracted targets, or 529
all-kind target occurrences as independent executable tests.
A command string is usually only a carrier or one step in a larger instruction. Running
it alone can produce misleading or valueless evidence when it depends on prior state,
later checks, an alternative branch, or cleanup.

The new primary hierarchy is:

```text
HOST PAGE
  -> PROCEDURE / USER SCENARIO
       -> PREREQUISITES AND START STATE
       -> ORDERED OR CONDITIONAL STEPS
       -> CHECKPOINTS AND EXPECTED OBSERVABLES
       -> FINAL OUTCOME
       -> FAILURE BEHAVIOR, LIMITATIONS, AND EXCEPTIONS
       -> CLEANUP / ROLLBACK AND END STATE
       -> ATTEMPTS, OBSERVATIONS, ISSUES, CORRECTIONS, AND RETESTS
```

The old command inventory remains useful for source coverage, provenance, static CLI
registry checks, access classification, and discovery reconciliation. It is not the new
execution plan and its prior item-level statuses must not be automatically inherited as
procedure PASS results.

## Governing rules

1. Follow `$vv-evidence` as the governing V&V procedure.
2. Prefer the smallest useful evidence package and existing repository conventions.
3. Do not build another workflow framework, project-management system, cryptographic
   ledger, receipt system, or identity subsystem merely to perform this audit.
4. Do not resume or integrate experimental isolated branches from the superseded
   command-occurrence design unless a specific artifact is demonstrably needed by the
   procedure model and is independently reviewed first.
5. Preserve failures and historical attempts. Append corrections and retests; never
   rewrite history.
6. Keep execution status, authority/provenance state, semantic-support score, and human
   acceptance separate.
7. Use only these V&V statuses:
   `UNVALIDATED`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`, and `STALE`.
   A material `NOT_APPLICABLE` exclusion requires a recorded rationale and scope-owner
   approval; otherwise retain `UNVALIDATED` or `BLOCKED`.
8. Use these separate authority states unless an existing repository enum is already
   stricter: `CONFIRMED`, `PENDING_OWNER`, `ADVISORY`, `NOT_IDENTIFIED`, and
   `CONTRADICTED`.
9. A Jira issue, existing documentation statement, or successful syntax check is context;
   it is not automatically authoritative proof of runtime or product behavior.
10. Do not call the docs ready or accepted while material non-passing items remain unless
   an authorized human records an explicit risk decision.
11. Never use, echo, persist, or publish a credential pasted into chat. Require currently
    valid Host and client keys through a secure, non-chat injection path before credentialed
    execution, and remind the user to rotate temporary credentials afterward.

## Phase 0 — Preserve and supersede the earlier model

Before changing implementation or running claim-suitable tests:

- Record the exact current docs branch, commit, tree/worktree state, and material local
  artifacts.
- Label Baseline B and the command/semantic-occurrence execution model
  `SUPERSEDED_FOR_EXECUTION_PLANNING` without deleting it.
- Preserve attempts 01–04 and every later retained failure exactly as historical evidence.
- Preserve useful source spans, raw carriers, safety/access classifications, authority
  mappings, CLI registry results, static checks, and issue history.
- Do not carry forward a prior command-level PASS or semantic score unless its exact
  target, context, method, expected result, and evidence are explicitly mapped to a new
  procedure step. Even then, do not infer a whole-procedure PASS.
- Keep user-owned untracked files, graph output, review feedback, and unrelated changes
  intact.
- Write a short recovery map showing what is retained, what is stale, what is
  superseded only for execution planning, and what is excluded from the new package.

“Preserve” does not mean recommit unsafe raw data. Sensitive historical originals remain
only in approved restricted storage. The reviewable package retains a sanitized index,
target applicability, status, and evidence-gap note when the original cannot be exposed.

## Phase 1 — Establish the exact Host-page population

Use the raw MDX, imports, navigation configuration, and rendered context to establish the
scope. Derive the current counts from the exact pinned docs revision rather than assuming
they are unchanged. The expected starting checksum is:

- 40 primary top-level `host/*.mdx` routes: 39 authored pages plus the generated
  `host/self-test-reference.mdx`; each route must be accounted for, and the generated
  page must also be checked against its generator/source contract.
- 18 generated `host/cli/*.mdx` pages and 15 generated `host/sdk/*.mdx` pages: validate
  them as generated/reference wrapper layers, not as 33 independent end-to-end workflows.
- Imported snippets: inspect the source once and each rendered use in context. Reuse a
  stable fragment identity where appropriate, but keep distinct page/procedure
  occurrences when the surrounding claim or prerequisites differ.

A completed read-only raw-page classification of the historical pre-Volume 39-page
population supplied this preliminary checksum: 11 procedural pages, 9 mixed pages, 11
conceptual/reference pages, 4 policy/legal pages, and 4 troubleshooting pages. Sixteen
pages contain complete
executable instructions and 23 do not. It found 120 fenced blocks, but content review
showed why fence counts are not test counts. Reproduce or challenge these classifications
against the current 40-page population; do not treat the historical split as final.

Do not use code-fence count as procedure count. Inspect headings, prose, inline code,
lists, tabs, imports, callouts, links, expected outputs, configuration fragments, and
cross-page journeys. A page with no shell fence can still contain an actionable procedure;
a shell-labeled fence can be a non-executable option fragment.

Create one page record for every primary top-level page in the newly derived population
(expected count: 40, split 39 authored + 1 generated) with:

- page ID, route, source file, title, and current source identity;
- intended Host persona and user goal;
- authoritative sources or unresolved source-owner questions;
- imported/generated dependencies;
- actionable sections and cross-page handoffs;
- procedure IDs owned or referenced by the page;
- page disposition and rationale;
- factual claims, error strings, thresholds, external effects, and material exceptions
  requiring validation even when no executable procedure exists.

Valid page dispositions include procedure-bearing, reference-only, conceptual/policy,
navigation/cross-page journey, generated-reference, and no-actionable-instruction. Record
the rationale; do not force conceptual content into a fake command test.

If the PR head or Host navigation changes, rederive the population, append a baseline
change, and mark affected evidence `STALE`; do not retain 40/18/15 as silent fixed truth.

## Phase 2 — Recover command carriers into logical procedures

Reconcile every legacy command/source carrier to exactly one documented treatment:

- required procedure step;
- prerequisite or setup;
- checkpoint or verification step;
- cleanup or rollback;
- conditional or alternative branch;
- standalone one-step diagnostic procedure;
- parameter/option fragment;
- placeholder or illustrative template;
- configuration/file content;
- expected output, error, or log sample;
- formula/data/example;
- generated CLI/SDK reference;
- duplicate/shared fragment; or
- approved exclusion / `NOT_APPLICABLE` with rationale.

No old carrier may silently disappear. This reconciliation proves source coverage; it
does not create one execution obligation per carrier.

The legacy crosswalk must reconcile all three frozen Baseline-B populations without
turning any of them into procedure counts:

- every frozen source occurrence receives exactly one primary treatment from the list
  above;
- all 176 deduplicated command records, 203 command occurrences, 474 extracted targets,
  and 529 all-kind target occurrences link to their applicable new procedure/claim
  records;
- shared snippets use one fragment identity plus every rendered context occurrence; and
- the 407 combined command/behavior semantic occurrences reconcile as 203 command plus
  204 behavior-claim occurrences. All legacy totals must reconcile to the frozen
  Baseline-B artifacts, or the mismatch is recorded as an inventory defect rather than
  forced to fit.

Define a procedure as the smallest complete instruction that accomplishes a meaningful
Host user goal and has an observable outcome. Group commands when they share state,
working directory, shell/session, prior output, account/machine state, or cleanup. Split
procedures when paths are true alternatives, apply to materially different environments,
or have independently meaningful outcomes and safety boundaries.

Rules for sequence modeling:

- Preserve the documented order. Never execute dependent lines independently merely to
  increase a pass count.
- Represent branches and conditions explicitly, including OS, shell, account state,
  hardware, and success/failure alternatives.
- Treat `cd`, environment setup, variable assignment, generated identifiers, pipes,
  redirection, and prior command output as state dependencies.
- Treat placeholders as parameters with type, source, example, and redaction rules; a
  template is not executable until safely instantiated.
- Treat output/error/config examples as expected observations or inputs, not commands.
- Allow a genuinely independent diagnostic command to be a one-step procedure.
- Model cleanup and end-state confirmation as required steps when the procedure creates
  resources, listeners, files, services, mounts, firewall rules, instances, or spend.
- Model ordered cross-page journeys, such as a quickstart that hands off to other pages,
  even when the entry page contains no shell commands.
- Treat `headless-install` as a conditional end-to-end journey unless raw-page review
  proves independently meaningful sub-procedures; do not turn its many fences into many
  isolated tests.
- Group troubleshooting commands by the symptom-specific diagnostic bundle and outcome
  they support. Keep market-query variants, operating-system alternatives, and
  single-machine/fleet variants as explicit branches rather than arbitrary duplicate
  executions.

## Procedure inventory schema

Assign stable, human-readable IDs that survive line shifts. Record source spans separately
and append identity changes rather than deriving identity solely from line numbers.

Each procedure must contain:

- procedure ID, title, owning page, route, heading, source span, and rendered context;
- referenced/imported fragment provenance;
- intended Host persona, goal, and validation use case;
- verification, validation, or both;
- authority/provenance, test basis, and claim boundary;
- prerequisites, authorized environment, start state, and representative-context rationale;
- ordered steps, each with a stable step ID and role;
- sequence, dependency, conditional, and alternative edges;
- exact source-form instruction plus parameterized executable form where applicable;
- expected observable at every material checkpoint and at completion;
- documented and expected failure behavior, error strings, limitations, and exceptions;
- cleanup/rollback method and required end state;
- execution/access/safety class;
- evidence sensitivity and public-redaction rules;
- planned method and retained evidence;
- current status, blocker or N/A rationale, attempt links, issue links, correction links,
  and retest links.

Use procedure classes such as:

- local-safe executable;
- source/static inspection;
- Host read-only;
- Host privileged read-only;
- Host mutating;
- Host destructive or maintenance-window-only;
- WAN/external-client;
- paid/client-account;
- conceptual/policy/source-owner validation;
- illustrative/generated/non-executable.

One attempt may cover several steps or several procedures only when the artifact records
the exact applicability mapping. Every required step still needs a traceable observation.

Branch results are scoped. Passing one operating system, shell, hardware type, account
state, or conditional path does not pass the broader procedure. Every applicable branch
has its own disposition; unexercised branches remain `UNVALIDATED` or `BLOCKED`, or
`NOT_APPLICABLE` only with a recorded rationale and scope-owner approval.

## Phase 3 — Independently reconcile and freeze Procedure Baseline P1

Do not begin new live, privileged, mutating, WAN, or paid execution until Procedure
Baseline `P1` is frozen and independently reconciled.

P1 is ready to freeze only when:

1. all primary top-level pages in the current pinned population (expected count: 40,
   split 39 authored + 1 generated) have a recorded disposition;
2. every actionable section has been inspected in raw and rendered context;
3. every legacy source carrier is mapped to a procedure role or explicit non-executable
   treatment;
4. every procedure has prerequisites, ordered/conditional steps, expected observables,
   failure behavior, limitations, cleanup, access class, and evidence plan;
5. generated CLI/SDK pages are accounted for through their generator/source contracts;
6. unresolved placeholders and required authorities are visible;
7. a reviewer can reproduce the inventory count without using the old command count as
   the target; and
8. the inventory has a baseline ID, timestamp, exact target identity, author, reviewer,
   and append-only change record.

Create claim IDs, source contexts, and authority mappings during P1. Semantic scores may
be provisional until suitable evidence exists, but every final score must use the frozen
rubric and link to the evidence then available.

Keep three roles explicit:

- a second-pass inventory reconciler checks P1 completeness and grouping independently
  of the first pass;
- a named human safety approver authorizes risky/live operation classes; and
- a named human acceptance owner makes the final product/process decision.

The reconciler does not replace the safety approver or acceptance owner. If the same
agent performs both inventory passes, disclose that limitation and require human review
of the safety gates and final acceptance.

The procedure count must be discovered from the pages. Do not choose or optimize for a
desired count.

After P1 freezes, additions or changes require an appended baseline change with rationale,
affected pages/procedures, evidence impact, and stale-status impact. Do not silently edit
expectations after seeing runtime results.

## Phase 4 — Run local and static checks against P1

Run current repository-native checks that support procedure prerequisites or static
claims, including as applicable:

- authored-page and carrier reconciliation freshness;
- MDX/build, link, accessibility, generated-artifact, and whitespace checks;
- shell/PowerShell syntax only where syntax is the stated claim;
- current Vast CLI command/option/help/registry conformance from an exact clean target;
- source/API/OpenAPI or generator conformance;
- review-server and review-context tests;
- secret scanning of every proposed evidence artifact.

Where reviewer tooling, Vast CLI, or Self-Test code is changed, follow the repository's
cross-platform dogfooding rules on Linux, macOS, and Windows when feasible. Record exactly
which platforms were exercised and which could not be covered. Host-only Linux procedures
must not be presented as cross-platform merely because the reviewer tooling is portable.

Record exact docs, CLI, Self-Test, package, image, dependency, and environment identities
where material. Mark prior evidence `STALE` when its target changed. A program-level suite
PASS may support listed static claims, but it must not be projected as runtime validation
of every documented procedure.

## Phase 5 — Resolve live-test readiness and authorization

Continue all safe local/static work while requesting missing live inputs. Before each
live class, record:

- approving human's full name and exact role;
- approved window, timezone, and target;
- exact allowed operations and forbidden operations;
- whether sudo/root, a temporary listener, a port probe, service inspection, service
  mutation, package installation, reboot, storage/network changes, or workload impact is
  authorized;
- external-client availability and one confirmed-unused TCP/UDP port;
- numeric `MAX_SPEND_USD`, numeric `MAX_RUNTIME_MINUTES`, polling interval, automatic
  stop condition, cleanup-escalation trigger, confirmed client/renter role, and whether
  bounded monitored execution is approved if the provider has no hard spend cap;
- secure availability of rotated Host/client credentials; and
- cleanup authority and escalation path if cleanup is uncertain.

If an operation is unsafe, unauthorized, security-restricted, or cannot run in the
available context, record V&V status `BLOCKED` with its exact reason and claim impact,
then continue independent procedures. A tooling or policy interruption uses V&V status
`BLOCKED`, blocker class `TOOLING_RESTRICTION`, and attempt execution state
`NOT_EXECUTED`; `NOT_EXECUTED` is not a seventh V&V status. Page dispositions and
`SUPERSEDED_FOR_EXECUTION_PLANNING` are metadata, not V&V statuses. A tooling restriction
is neither a product FAIL nor a PASS and must not stop unrelated safe work.

## Phase 6 — Execute Host procedures in documented order

Begin with a fresh SSH reachability/authentication observation and preserve the earlier
timeout as history. Perform read-only orientation only to establish the environment and
safety of the frozen procedures; do not overclaim it as procedure validation.

For each authorized Host procedure:

- confirm prerequisites and the exact start state;
- instantiate parameters without exposing secrets;
- execute required steps in documented order and in the documented shell/context;
- capture checkpoint and final observations, exit status, timestamps, and relevant state;
- compare observations with pre-frozen expectations;
- capture documented failure paths where safe and required;
- perform and independently confirm cleanup/end state; and
- assign the procedure result from the full sequence, not from one successful line.

A procedure may be `PASS` only when all required steps and checkpoints, the final expected
state, and required cleanup are supported by current claim-suitable evidence. Step-level
passes do not imply procedure PASS. If a prerequisite fails, preserve the observation and
mark dependent work `BLOCKED` with `PREREQUISITE_FAILED` rather than running later steps
out of context.

On an active or shared Host, destructive or availability-affecting procedures default to
`BLOCKED`. Do not run an installer, firewall change, mount/format operation, service
restart, reboot, machine removal, workload interruption, or other material mutation unless
all of the following exist: a disposable or explicitly isolated target, confirmed absence
of affected workloads, a backup/recovery plan, operation-level human approval, an approved
maintenance window, stop conditions, and independently confirmed cleanup/recovery. A
general maintenance-window approval is insufficient.

## Phase 7 — Execute WAN procedures safely

For an authorized WAN scenario:

- prove the chosen port is unused and inside the approved range stored in the restricted
  `HOST_VV_TARGET` record;
- create only the planned temporary TCP or UDP listener;
- capture host-side listener state and timestamped external-client probes;
- test the exact documented behavior and relevant safe failure behavior;
- remove the listener and confirm the port/end state is clean; and
- avoid every existing workload/listener.

TCP and UDP are separate behaviors. Do not infer one from the other or infer reachability
from configuration inspection alone.

## Phase 8 — Execute bounded paid/client procedures

Use only a confirmed client/renter credential supplied securely; never substitute the
Host credential. Run at most one paid rental or Self-Test attempt at a time and no
unattended outer retries.

Before spending, capture a read-only offer preflight for the frozen target and record the
current price, compatibility, availability, direct-port state, requirements, projected
maximum cost, cleanup plan, and stop conditions. Do not start if projected spend exceeds
the approved `MAX_SPEND_USD`, the monitored attempt cannot be bounded by
`MAX_RUNTIME_MINUTES`, or the automatic stop/cleanup-escalation path is not ready.

Paid evidence must bind the actual attempt to:

- docs revision;
- exact CLI source/package/build identity;
- exact Self-Test source identity;
- image tag and immutable OCI/platform digest;
- machine/offer and instance identities in restricted evidence;
- start/end timestamps and runtime stages;
- rendered diagnostic or workload result;
- exit/failure result;
- actual or calculated cost; and
- explicit instance cleanup plus post-cleanup confirmation.

Launch, initialization, connection, or cleanup alone does not prove a completed workload.
If cleanup becomes uncertain, cleanup is the only authorized follow-up action until the
resource state is resolved.

## Phase 9 — Capture evidence, classify issues, correct, and retest

For each attempt, retain the smallest artifact set that lets an independent reviewer see:

- the procedure and steps covered;
- exact target and environment;
- preconditions/start state;
- exact sanitized action or command actually performed;
- expected observations defined before execution;
- actual observations, exit state, timestamps, and artifacts;
- deviations, limitations, redactions, and representativeness;
- cleanup/end state; and
- result interpretation.

Keep sensitive raw evidence in an approved restricted location and publish only a
sanitized projection. Never reconstruct missing evidence after the fact.

Classify discrepancies as product behavior/defect, documentation drift/defect,
configuration/environment, dependency/version, permission/access, test defect,
expectation error, or source-owner evidence gap.

Preserve the first failure. Correction authority in this goal covers only Host Docs and
the existing review interface on the PR branch. Report product, CLI, API, Self-Test, or
infrastructure defects with evidence; do not change those systems unless the user
separately authorizes that expanded scope. Correct only an authorized source, record cause
and impact, then create a linked retest against the same acceptance basis. An unchanged
retry is not a correction retest, and a later transient pass does not erase an unexplained
failure.

## Phase 10 — Audit semantic support in procedure context

After relevant runtime/static evidence exists, audit every place the Host Docs presents a
procedure step, command, factual threshold, literal error, or external behavior claim.
Score the source occurrence in its page/procedure context, not the deduplicated command
string.

Each semantic record must link:

- page, route, heading, source span, and surrounding claim;
- procedure and step IDs, or non-procedure claim ID;
- intended Host goal and stated behavior;
- authority/provenance and claim boundary;
- applicable attempt/observation and execution status;
- prerequisites, sequence, failure behavior, limitations, exceptions, and cleanup;
- semantic score, rationale, finding classification, and correction/retest link.

Use this rubric:

- **1 — Not adequately supported:** wrong, broken, unsafe, obsolete, misleading,
  contradicted, materially insufficient, unrelated to the claim, or missing a material
  prerequisite/exception.
- **2 — Partially supported:** relevant but incomplete, ambiguous, weakly evidenced,
  environment-dependent, or valid only within a narrower claim than the prose states.
- **3 — Strongly supported:** current representative evidence directly addresses the
  exact wording and observed goal, prerequisites, ordered behavior, expected and failure
  behavior, limitations, material exceptions, and cleanup where applicable.

Use finding classes such as `SUPPORTED`, `UNSUPPORTED`, `INACCURATE`, `INSUFFICIENT`,
`BROKEN`, `OBSOLETE`, `AMBIGUOUS`, `UNSAFE`, `MISSING_PREREQUISITE`,
`MISSING_EXCEPTION`, and `EVIDENCE_GAP`.

Do not assign score 3 from syntax/help output alone when the page makes a runtime claim.
Do not turn execution PASS into semantic score 3 automatically, or score 3 into execution
PASS. Authority remains a separate field: score 3 does not resolve `PENDING_OWNER`,
`NOT_IDENTIFIED`, or `CONTRADICTED` authority and therefore may still block readiness.
Unassessed occurrences remain `UNVALIDATED`; do not invent a score zero.

## Minimal canonical evidence package

Reuse the existing `verification/` package and create no parallel ledger. Maintain only:

- one concise reviewer entry point;
- one canonical machine-readable page/procedure/step/claim inventory, with Markdown or
  CSV views generated from it rather than maintained as independent truths;
- append-only attempt artifacts only where a procedure or claim needs them;
- one issue/correction/retest ledger; and
- one generated sanitized projection for the existing review interface.

Index legacy artifacts from this package instead of cloning them into a second hierarchy.
Do not create empty template files or duplicate evidence merely to fill a schema.

## Phase 11 — Reconcile coverage and outcomes

Report these separately:

- primary-page coverage: accounted pages / frozen top-level Host-page population
  (expected 40, split 39 authored + 1 generated);
- actionable-section coverage;
- legacy carrier reconciliation coverage;
- discovered procedure count and procedure disposition coverage;
- required-step evidence coverage;
- evaluated coverage;
- procedure and step status counts;
- semantic score counts and unassessed count;
- cleanup-required and cleanup-confirmed counts;
- generated/reference/non-executable and approved N/A counts;
- failures, blockers, stale evidence, corrections, and retests.

Do not use raw command pass count as a readiness or quality metric. Counts must reconcile
to item-level records and every PASS must link to current evidence suitable for its exact
claim.

## Phase 12 — Add evidence to the existing review interface

Only after P1 and the evidence projection schema are stable, extend the existing
localhost reviewer interface. Do not create a second app.

The Host page view should present:

```text
Page -> Procedure -> Ordered steps -> Status/observations -> Semantic support
     -> Failures/blockers -> Correction/retest -> Reviewer feedback
```

The dashboard should show the reconciled coverage metrics, open failures/blockers, stale
evidence, semantic distribution, and sanitized exports.

Requirements:

- the canonical evidence package remains the source of truth;
- the browser consumes a generated sanitized artifact, not raw logs;
- missing, mismatched, or stale data fails closed as unavailable/stale, never PASS;
- values are escaped and evidence routes are allowlisted;
- private files, credentials, absolute paths, network details, and restricted IDs are not
  exposed;
- existing feedback export/import compatibility is preserved;
- normal, missing, stale, malformed, redaction, traversal, XSS, keyboard, accessibility,
  and compatibility behavior is tested; and
- browser validation covers the actual rendered page and dashboard, not only unit/server
  tests.

Use a minimal, reviewable projection. Do not add custom cryptographic receipts or a
parallel integrity architecture unless a concrete requirement and threat model demand it
and the user separately authorizes that expansion.

## Phase 13 — Final independent review and publication

Before publishing:

- answer all seven `$vv-evidence` completion questions from the package entry point;
- independently reconcile every page in the frozen primary Host-page population, every
  procedure, every required step, every blocker/N/A, and every semantic record;
- verify each PASS against its evidence and exact target;
- preserve failures and ensure every correction links to a retest;
- mark changed-target evidence STALE;
- run final repository-native tests, browser QA, artifact freshness, and secret scans;
- inspect the complete diff and exclude private/restricted evidence;
- refresh graphify after code changes; and
- disclose when the same agent created and checked work.

Commit focused, reviewable changes to the existing branch, push PR #185, and update PR
#185 and Jira CON-1518 with:

- exact software/source/package/image identities, plus only a sanitized Host environment
  alias; raw machine, account, offer, instance, IP, and port identities remain restricted;
- reviewer checkout/install/run commands;
- how to use the page/procedure review interface and submit feedback;
- Host/WAN/paid environments actually exercised;
- page, procedure, step, status, semantic, failure, blocker, cleanup, and stale counts;
- important corrections and linked retests;
- explicit residual risks and source-owner questions;
- credential-rotation reminder; and
- an explicit statement that human acceptance remains undecided.

Do not merge, self-approve, record acceptance, or claim broader production readiness.

## Completion outcomes

Report two outcomes separately:

- `REPOSITORY_LOCAL_STRUCTURE_COMPLETE`: every repository-local frozen page,
  procedure, step, claim, branch, exclusion, status, limitation, and evidence gap
  is reconciled and independently reviewable. Runtime/operator and source-owner
  work remains separately incomplete.
- `TARGET_ACCEPTANCE_CANDIDATE`: every safe, available, authorized procedure has a current
  claim-suitable attempt, and no material `UNVALIDATED`, `FAIL`, `BLOCKED`, `STALE`,
  unresolved authority, or unapproved residual risk remains.

Never use the first label to imply semantic validation, external-workstream
completion, or the second label. Human acceptance is a separate decision.

## Success criteria

This goal is complete only when:

1. the installed `$vv-evidence` skill revision is recorded and its procedure followed;
2. the earlier command-level model is preserved but clearly superseded for execution
   planning;
3. all primary top-level Host pages in the frozen current population (expected 40: 39
   authored + 1 generated) and all generated/imported support layers are accounted for;
4. every legacy command carrier is reconciled into a procedure role or explicit
   non-executable treatment;
5. Procedure Baseline P1 is frozen before new claim-suitable live execution;
6. every discovered procedure has a current status, planned method, authority, and direct
   evidence or an exact blocker/N/A rationale;
7. every required step and final observable is traceable, including cleanup where needed;
8. paid/Host/WAN attempts are bounded, authorized, target-bound, securely captured, and
   cleaned up;
9. every in-scope procedure/claim occurrence has a reconciled semantic assessment; an
   occurrence may remain non-passing because its evidence status is `UNVALIDATED`, but it
   must still have an explicit evidence-gap rationale and a 1–3 score under the frozen
   rubric unless it has an approved `NOT_APPLICABLE` disposition;
10. failures remain visible and corrections have linked retests;
11. the review interface exposes sanitized page/procedure evidence and fails closed;
12. final coverage counts reconcile without using command pass counts as readiness;
13. every safe, available, and authorized procedure has a claim-suitable attempt; every
    remaining blocker reflects a genuine external, safety, or authority constraint;
14. PR #185 and CON-1518 contain reproducible review instructions and accurate residual
    risks; and
15. an independent reviewer can answer the seven `$vv-evidence` completion questions
    without searching unrelated logs.

The repository-local structure may be complete while containing `FAIL`, `BLOCKED`,
`STALE`, or `UNVALIDATED` procedures. Structural completeness is not semantic
validation, external completion, or acceptance.

## Required first response when this goal starts

Do not run a Host, WAN, credentialed API, or paid command in the first turn. First return:

1. the recovered/superseded artifact map;
2. the freshly derived primary top-level page population (expected 40: 39 authored + 1
   generated) and supporting generated/imported layers;
3. the proposed procedure-inventory schema and grouping rules;
4. the read-only discovery steps used to calculate the real procedure population;
5. the P1 freeze checklist;
6. the work that can continue locally without further permission; and
7. one concise list of still-missing live approvals/secure inputs.

Then proceed with read-only inventory work. Pause only the affected execution class when
authorization is missing; continue independent safe work.
