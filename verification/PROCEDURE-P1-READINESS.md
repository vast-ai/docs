# Host Docs Procedure Baseline P1 — readiness and first-pass inventory

## State

- Operating mode: `PLAN_AND_EXECUTE`
- Current phase: `PLAN -> INVENTORY`
- Draft identifier: `HOST-DOCS-P1-DRAFT-0`
- Baseline state: `NOT_FROZEN`
- Execution readiness: `NOT_READY` for Host, privileged, mutating, WAN, credentialed,
  and paid execution
- Prepared: `2026-08-30T11:32:37Z`
- Docs branch: `CON-1584-host-cli-api-sdk`
- Docs HEAD: `09d729e72fbcb2bdd2dead2b9dc5d5e1eeeffcf5`
- Docs tree: `bfe3e9316893a2174b99779ce844e81f014d2b53`
- Tracked worktree: clean at discovery time; user-owned untracked planning, graph,
  dependencies, and feedback artifacts remain present and preserved
- Frozen legacy Host-content revision: `5088d76b89856185f3ab15a628e4152ff140ab26`
- Frozen Host-content fingerprint:
  `sha256:bc59a848d0cb8698097787b911bb9e5b6875570c7c58815baa6d1f48b2504b4d`
- Governing procedure: `Oxiom-Systems/vv-evidence@ab3c35b5bb7da41bc6bc3cbbefea6bc64c94c7b2`
- Installed `SKILL.md` SHA-256:
  `5c71f16cc25a52e62cb71cd01c9129e92cda8e971faa1d0779d712ef00e2e18d`

No documented Host command, Host/WAN operation, credentialed API call, or paid action was
executed while producing this draft. `inventory_host_docs.py --check` was run only as a
read-only recovery/freshness observation; it is not a P1 procedure PASS.

## 1. Recovered and superseded artifacts

`SUPERSEDED_FOR_EXECUTION_PLANNING` below is metadata, not a V&V status. Historical
evidence remains append-only and must not be rewritten.

| Artifact group | Treatment for P1 | Claim limit |
|---|---|---|
| `host-docs-verification-inventory.json`, CSV, and `HOST-DOCS-VERIFICATION.md` | Retain as the canonical legacy target/carrier crosswalk seed. SHA-256 of JSON: `9485b266...9ab`. Mark old item execution states superseded for procedure planning. | Stable legacy item IDs, source locations, access hints, and static syntax only; no sequence model or procedure PASS. |
| `host-docs-command-access.json` and `HOST-DOCS-COMMAND-ACCESS.md` | Retain as conservative access/safety hints. JSON SHA-256: `c2b5bfc6...781`. Reclassify at procedure and branch level. | Planning aid, not authorization and not runtime evidence. |
| `host-docs-cli-command-check.json` and Markdown | Retain as static CLI registry evidence at exact CLI revision `ecf32efa...`. JSON SHA-256: `e3eb1dcc...421`. | Syntax/signature/source support only; mark stale or replay against a clean current CLI before a current claim. |
| `HOST-DOCS-QA-SUMMARY.md` | Retain as historical findings/corrections and owner-gate context. | The old 8 PASS / 1 FAIL / 2 BLOCKED rollup is Baseline-A program history, not P1 procedure status. |
| `verification/README.md`, `inventory.md`, `summary.md`, `issues.md`, and `run-local-safe-checks.sh` | Preserve Baseline A and reuse its native runner/issue/attempt conventions where suitable. Supersede the 11 broad programs as the primary execution plan. | Repository/static supporting checks only; cannot establish page-procedure behavior. |
| `verification/evidence/2026-08-27-macos-arm64-attempt-01` through `attempt-04` | Preserve all 88 tracked files byte-for-byte. Map exact evidence to P1 steps only after target, context, method, expectation, and applicability review. | Historical macOS/static evidence; never infer a whole-procedure PASS. The retained accessibility failure remains a current-risk candidate until retested. |
| `REVIEW-TRACEABILITY.md`, `REVIEW-QUESTIONS.md`, and `review-server.mjs` | Retain Jira/page/owner context and the current reviewer shell. Refresh authority facts and later adapt the UI to page -> procedure -> branch -> step evidence. | Jira identifies context or a potential owner; it does not confirm product truth. The server currently has no V&V evidence consumer. |
| `review-feedback/*.json` | Preserve as user-owned reviewer input/test data; sanitize and review before publication. | Feedback is not automatically evidence or acceptance. |
| `verification/VV-EVIDENCE-MIGRATION-PLAN.md` | Retain as plan-only design history; superseded by the procedure goal and this P1 draft. | Not implemented evidence or authority. |
| `.orchestra/**`, `task_plan.md`, `findings.md`, `progress.md`, and isolated `/private/tmp` candidates | Preserve, restrict, and exclude from canonical P1. Reuse only a design lesson that is reverified against current bytes. | Rejected/mutable experimental history is not an accepted Baseline-B implementation. |
| `graphify-out/` and `node_modules/` | Preserve as user-owned derived/dependency state and exclude from evidence/readiness counts. | Orientation/dependency state only. |

No accepted Baseline-B implementation, stable 407-occurrence registry, authority ledger,
or semantic audit exists in the current tracked worktree. Do not represent an isolated or
mutable candidate as current repository evidence.

## 2. Exact current scope and legacy denominators

### Route and source scope

- 72 unique Host routes in `docs.json`.
- 39 primary top-level `host/*.mdx` routes:
  - 38 authored pages;
  - 1 generated page: `host/self-test-reference.mdx`.
- 33 supporting generated wrappers:
  - 18 `host/cli/*.mdx` routes;
  - 15 `host/sdk/*.mdx` routes.
- Route-level authorship: 38 authored + 34 generated = 72.
- Imports are a separate overlapping dimension:
  - all 33 CLI/SDK wrappers import one `snippets/host/cli|sdk/*.mdx` command fragment;
  - `host/notifications.mdx` imports the prose-only
    `snippets/notifications/channels.mdx` fragment;
  - 34 routes therefore import a snippet.
- The 39 primary pages contain 120 fenced blocks across 18 pages; 21 have no fence.
  Content inspection found 16 pages with at least one complete executable instruction.
  Fence count is neither a command count nor a procedure count.

Preliminary page-purpose checksum: 11 procedural, 9 mixed, 11 conceptual/reference, 4
policy/legal, and 4 troubleshooting pages. This classification is reviewable judgment,
not a frozen acceptance result.

### Legacy crosswalk denominators

| Population | Unique items | Source occurrences |
|---|---:|---:|
| Commands | 176 | 203 |
| Behavior claims | 203 | 204 |
| Errors | 77 | 104 |
| Thresholds | 18 | 18 |
| All kinds | 474 | 529 |

The semantic command/behavior subset is 407 occurrences: 203 command + 204 behavior.
The separate CLI registry report contains 181 invocation occurrences; those are supporting
source checks and do not change the 529 denominator.

Every one of the 529 frozen source occurrences must receive exactly one primary treatment
and a new page/procedure/branch/step/claim reference or an approved non-executable/N/A
rationale. No legacy status becomes P1 `PASS` automatically.

## 3. Provisional page-to-procedure seed

This raw-page pass found 82 candidate units: 45 executable/interactive procedures (`E`),
13 symptom-driven troubleshooting bundles (`T`), 21 non-executable claim/source bundles
(`C`), and 3 parent/cross-page journeys (`P`). These IDs and groupings are provisional and
must be independently reconciled before P1 freezes.

| Primary page | Candidate units | Essential grouping/sequence boundary |
|---|---|---|
| `hosting-overview` | `HOV-P01` First-host route; `HOV-C01` offer/contract/end-date model | Parent journey delegates execution; contract/offer claims need authority. |
| `supported-hardware` | `SHW-C01` pre-purchase fit; `SHW-C02` listing/verification baseline | Threshold/source validation, not fake hardware execution. |
| `persona-decision-guide` | `FIT-C01` hosting go/no-go and path selection | Branch by persona, hardware, Linux, and network suitability. |
| `earning` | `EARN-C01` compute revenue; `EARN-C02` gross-to-net/market scenario | Formula/data validation; omissions and assumptions remain explicit. |
| `guide-to-taxes` | `TAX-C01` location/provider tax responsibility | Legal/current-source branches; no operational command test. |
| `account-hosting-agreement` | `ACC-E01` host-account conversion/agreement; `ACC-T01` missing Host context | Account state precedes machine setup. |
| `account-security-for-hosts` | `SEC-E01` Host 2FA; `SEC-E02` scoped API-key lifecycle | Personal/team context branches; secret handling is mandatory. |
| `quickstart` | `QST-P01` eight-stage first-host journey | Preserve fit -> account -> prep -> install -> list -> self-test -> verify -> operate order without duplicating child evidence. |
| `hardware-prep` | `HWP-E01` inventory snapshot; `HWP-C01` readiness assessment | One read-only snapshot followed by comparison to authoritative gates. |
| `storage-setup` | `STO-E01` inspect/backup; `STO-E02` existing XFS mount/quota; `STO-E03` disposable-device provision | Raw disk/partition/RAID/LVM branches; formatting is irreversible and default-blocked. |
| `network-ports` | `NET-E01` size/forward range; `NET-E02` update daemon range; `NET-E03` outside-LAN TCP/UDP | Configuration branches and external-client platform alternatives; listeners/capture require cleanup. |
| `installing-host-software` | `INS-E01` setup-page TUI; `INS-E02` raw fallback; `INS-T01` failure/completion diagnosis | TUI/fallback alternatives; completion includes service/storage/port/log checkpoints. |
| `headless-install` | `HDL-E01` clean Ubuntu -> listed/self-tested Host | One conditional end-to-end journey with reboot/storage/driver/TUI/fallback branches, not 28 fence tests. |
| `vms` | `VM-E01` inspect/disable; `VM-E02` enable/retry | Intel/AMD and idle/reboot/process-removal branches. |
| `how-to-self-test` | `ST-E01` paid self-test/result/bundle/cleanup; `ST-T01` fresh-install/not-rentable/ignore path | Normal and diagnostic branches; ignore mode cannot qualify verification. |
| `self-test-reference` | `STR-C01` generator parity; `STR-C02` result/runtime/error/bundle contract | Generator/source validation; error rows are not individual runtime tests. |
| `pricing-your-listing` | `PRICE-C01` derive terms; `PRICE-E01` apply terms/observe contract effect | Fenced text is an option fragment, not a standalone command. |
| `market-metrics` | `MET-E01` dashboard/calculation; `MET-E02` CLI query matrix; `MET-E03` REST metrics | Query variants and dashboard/API methods are alternatives. |
| `optimization-guide` | `OPT-C01` listing optimization loop | Observe market/utilization and adjust future terms. |
| `understanding-verification` | `VER-C01` verification eligibility/automation model | Source/platform validation, not command execution. |
| `verification-stages` | `VST-C01` threshold parity; `VST-C02` stage lifecycle/recovery | Thresholds join generated source; observations do not prove deterministic timing. |
| `not-in-search` | `SRCH-E01` account/machine visibility; `SRCH-E02` comparable ranking | Progressive lookup/filter branches, then separate market comparison. |
| `first-24-hours` | `DAY1-E01` health/monitor checkpoint; `DAY1-E02` client-like paid rental/access/cleanup | Separate Host and client roles; mandatory destruction/cleanup for paid instance. |
| `reliability-uptime` | `REL-C01` score drop/recovery/verification relationship | Sustained observation and source validation. |
| `notifications` | `NOT-E01` email/webhook preferences; `NOT-E02` webhook delivery | Shared prose fragment once at source plus rendered context; delivery contract comes from canonical source. |
| `maintenance-windows` | `MNT-E01` contract-aware planned maintenance; `MNT-E02` schedule/check/cancel lifecycle | Existing contracts gate unlisting; test cancellation is cleanup, not always production behavior. |
| `removing-recreating-machines` | `RM-E01` cleanup/decommission/recreate; `RM-T01` ghost state | Active contracts/workloads gate destructive steps; escalation for backend state. |
| `fleet-operations` | `FLT-E01` inventory/monitor; `FLT-E02` list/reprice; `FLT-E03` maintenance; `FLT-E04` default job; `FLT-E05` defrag; `FLT-E06` cleanup | Six distinct goals sharing inventory state, not one script. |
| `host-teams` | `TEAM-E01` team/role/invite; `TEAM-E02` team-context registration; `TEAM-E03` scoped team key/operations; `TEAM-T01` wrong context/ownership/deletion | Context switch precedes key and registration; migration/destructive branches stay separate. |
| `common-errors-diagnostics` | `DIA-E01` collect/redact bundles; `DIA-E02` service/storage/port snapshot; `DIA-E03` symptom diagnostics; `DIA-T01` escalation packet | Select bundle by symptom; live watch/load tests have separate gates. |
| `machine-errors` | `ERR-T01` ports; `ERR-T02` Docker/NVIDIA/CDI; `ERR-T03` PCIe/GPU/ECC; `ERR-T04` CUDA/NCCL; `ERR-T05` XFS/storage; `ERR-T06` rentability/admin/VM state | Exact visible error selects one diagnostic bundle; no indiscriminate execution. |
| `datacenter-status` | `DC-C01` eligibility/application requirements | Current business/source-owner validation; submission is out of scope. |
| `payment` | `PAY-E01` connect/switch payout; `PAY-E02` download records; `PAY-T01` payout/invoice diagnosis | Provider/region/schedule/threshold claims need current authority. |
| `workload-policy` | `POL-E01` investigate report without renter-data access; `POL-C01` policy/escalation decision | Redact/escalate; never inspect renter files. |
| `common-host-questions` | `FAQ-C01` route/anchor audit | Validate canonical destinations; do not duplicate runtime checks. |
| `glossary` | `GLO-C01` term/authority/anchor audit | Definition and deep-link validation. |
| `hosting-agreement` | `AGR-C01` Terms precedence/plain-language mapping | Canonical legal source wins. |
| `community` | `COM-E01` join community and prepare safe help request | Validate access plus redaction/content safety. |
| `cli-api-sdk` | `API-P01` choose/authenticate CLI/SDK/REST and route workflow | Parent orientation; 33 generated wrappers are source contracts, not 33 end-to-end tests. |

Cross-page setup dependency:

`FIT/SHW -> ACC/SEC -> HWP/STO/NET -> INS or HDL -> PRICE/list -> ST/STR -> VER/VST -> DAY1`

Parent journeys reference child evidence. Passing one platform, account context, hardware
branch, shell, or diagnostic bundle cannot pass unexercised applicable branches.

## 4. Proposed smallest canonical P1 package

Reuse `verification/` and keep three canonical record families:

```text
verification/
|-- README.md                       # concise reviewer entry point
|-- procedure-baseline-p1.json      # frozen page/procedure/branch/step/claim/crosswalk
|-- issues.json                     # issue/correction/retest ledger
|-- evidence/
|   |-- ...attempt-01 through -04/  # immutable history
|   `-- <attempt-id>/
|       |-- attempt.json            # canonical applicability/result record
|       |-- attempt.md              # optional generated narrative
|       `-- stdout/stderr/artifacts
|-- inventory.md                    # generated view
|-- summary.md                      # generated view
|-- issues.md                       # generated view
|-- procedure-inventory.csv         # optional generated view
|-- legacy-crosswalk.csv            # generated view
`-- review-evidence.json            # generated sanitized UI projection
```

Do not create a second semantic ledger. Semantic assessments live with claim results in
append-only attempt records and are projected into current views.

### Canonical hierarchy and required fields

- `page`: stable ID, route, source identity, title/persona/goals, authorship/generator
  state, disposition/rationale, imports, actionable sections, procedure IDs, page claims.
- `procedure`: stable line-independent ID, owning page, goal, verification/validation
  basis, authority refs, prerequisites/start state, representative environment,
  access/safety class, evidence plan, expected final result, failure behavior, cleanup,
  branches, steps, initial status.
- `branch`: stable ID, applicability condition, ordered step IDs, access override, status.
  A linear procedure has one `main` branch.
- `step`: stable ID, role (`setup`, `action`, `checkpoint`, `cleanup`), required flag,
  source instruction, executable template/typed parameters, dependencies, expected
  observables, failure behavior, claim IDs, status.
- `claim`: occurrence-specific ID, page/procedure/branch/step refs, raw and rendered
  context, kind/text, authority refs/state/claim limit, test basis, expected observable,
  method, status, and whether semantic scoring is required.
- `legacy_crosswalk`: one row per 529 occurrence with the legacy item ID, new stable
  occurrence ID, source tuple, source-text digest, legacy status, exactly one primary
  treatment, new entity refs, rendered-context refs, and rationale.
- `attempt`: baseline/target identities, mode (`EXECUTED`, `INSPECTED`, `SIMULATED`, or
  `NOT_RUN`), environment/authorization, exact branch/step/claim applicability, expected
  and observed results, evidence refs, limitations/redactions, cleanup, and current status.
- `issue`: affected IDs, first attempt, classification/cause, correction, later retest,
  final state, owner/risk decision.

Keep V&V status, attempt mode, authority state, 1–3 semantic score, page disposition,
supersession metadata, and human acceptance as separate fields.

## 5. Read-only discovery and reconciliation method

1. Pin docs HEAD/tree, Host-content revision/fingerprint, tracked cleanliness, and the
   governing skill revision/digest.
2. Derive route counts from `docs.json`; derive primary/generated/import source classes
   from raw MDX imports and generator markers.
3. Inspect every primary page's headings, prose, inline code, fences, imports, callouts,
   inputs, expected outputs, errors, links, and cross-page handoffs.
4. Classify carriers as steps, prerequisites, checkpoints, cleanup, branches, templates,
   config, outputs/errors, formulas/examples, generated references, duplicates, or approved
   exclusions.
5. Group by meaningful user outcome and shared state. Preserve order, conditional edges,
   session/working-directory state, parameter flow, failure behavior, and cleanup.
6. Generate the 529-row legacy crosswalk and reconcile all unique/occurrence/kind totals.
7. Identify authority, expected observable, representative context, access/safety class,
   and evidence method before any execution.
8. Render source-dependent snippets/pages and verify each material context rather than
   trusting language labels or fence counts.
9. Run a second-pass grouping/crosswalk reconciliation. Record disagreements and resolve
   them before freezing P1.

## 6. P1 freeze checklist

- [ ] Current route/source/import counts rederived and pinned.
- [ ] All 39 primary pages have a disposition and candidate-unit review.
- [ ] Generator/source contracts identified for `self-test-reference` and all 33 wrappers.
- [ ] Every actionable section and cross-page handoff is represented.
- [ ] All 82 provisional units accepted, split, merged, or removed with rationale; final
  procedure count is source-derived rather than quota-driven.
- [ ] Every applicable procedure branch has prerequisites, ordered steps, expected
  checkpoints/final result, failure behavior, limitations, cleanup, access class, and
  evidence plan.
- [ ] All 529 legacy occurrence rows have exactly one primary treatment and reconciled new
  references; all frozen denominators agree.
- [ ] Authority/provenance and claim limits are visible, including unresolved owners.
- [ ] Destructive/mutating/paid/WAN actions have exact gates and default to `BLOCKED` until
  separately approved.
- [ ] Second-pass inventory reconciler recorded; same-agent limitations disclosed.
- [ ] Baseline ID, frozen timestamp, exact target, hashes, author/reconciler, and append-only
  change record written.

P1 is not frozen and no new claim-suitable live execution may start yet.

## 7. Safe work that can continue now

- Normalize the 82 candidate units into page/procedure/branch/step/claim records.
- Build and independently reconcile the 529-row legacy crosswalk.
- Locate and pin the generator/source contract for `self-test-reference` and the 33
  CLI/SDK wrapper/snippet pairs.
- Map prior CLI/static/access evidence to narrow P1 support claims without inheriting PASS.
- Refresh owner questions and identify authoritative public/internal sources.
- Design generated Markdown/CSV views and the minimal fail-closed sanitized projection.
- Inspect current Host docs and reviewer interface locally without running documented
  Host instructions or exposing restricted data.

## 8. Missing live approvals and secure inputs

These gates pause only the affected execution class; read-only inventory work continues.

1. Named human safety approver and exact role.
2. Approved test window/timezone and operation-level scope for the active/shared Host,
   including explicit read-only, privileged-read, temporary-listener, mutation, and
   forbidden classes.
3. Restricted `HOST_VV_TARGET` record containing the approved target/SSH/WAN/port details;
   raw coordinates must remain outside Git and public review artifacts.
4. A genuinely external client and one confirmed-unused approved TCP/UDP test port.
5. Numeric `MAX_SPEND_USD`, numeric `MAX_RUNTIME_MINUTES`, polling interval, automatic
   stop condition, and cleanup-escalation trigger for paid tests.
6. Confirmation that the paid credential has the client/renter role and the Host credential
   has the intended Host role.
7. Fresh rotated Host/client keys supplied through a secure non-chat injection path. Never
   use a credential pasted into chat.
8. Explicit cleanup authority and escalation contact if instance, listener, or resource
   cleanup becomes uncertain.
9. Named human acceptance owner and role for the final decision.

Destructive tests on an active/shared Host remain `BLOCKED` unless a disposable or
explicitly isolated target, zero affected workloads, recovery plan, operation-specific
approval, maintenance window, stop conditions, and cleanup proof all exist.

## 9. Material grouping and source uncertainties

- No current local generator for the 33 CLI/SDK wrapper/snippet pairs has yet been located.
- Host Teams machine-registration permissions still require engineering confirmation.
- `headless-install` may assume `./install` exists without documenting the exact preceding
  download/start-state dependency.
- The headless driver example pins `nvidia-driver-595-open`; it must not become a universal
  expected package without current authority.
- `pricing-your-listing` contains only an option fragment, not a complete command.
- `first-24-hours` may use the wrong discovery command for a separate client account before
  `create instance`; confirm against current CLI/source.
- Maintenance examples contain epoch `1782950400` (`2026-07-02T00:00:00Z`), which is past
  at this draft date.
- Self-Test generator inputs, CLI/Self-Test revisions, image mappings, thresholds, runtime
  stages, and cleanup contracts require current source-freshness review.
- Market freshness/rate limits, payout timing/providers/thresholds, taxes, notifications,
  datacenter requirements, verification timing, and legal/policy claims need current
  authoritative sources or owners.
- Storage instructions omit the actual `/etc/fstab` editing step, and formatting has no
  rollback; model both explicitly.
- Network listeners/captures imply cleanup that is not fully documented.
- Planned maintenance lacks an explicit post-maintenance relist/health-check end state.
- VM privilege/output behavior requires live or source confirmation.
- Rendered-context review is still required; this first pass used raw MDX, navigation,
  imports, and generator markers.

## 10. First-turn conclusion

The old command inventory is recoverable as source coverage and historical evidence, but
it is superseded as an execution plan. The current source supports a provisional 82-unit
page/procedure inventory, not 176 or 474 independent command tests. P1 remains incomplete
until the procedure groupings, generator contracts, and 529-row crosswalk are independently
reconciled and frozen.

Current outcome labels:

- `EVIDENCE_PACKAGE_COMPLETE`: not yet reached.
- `TARGET_ACCEPTANCE_CANDIDATE`: not reached.
- Human acceptance: `NOT_DECIDED`.
