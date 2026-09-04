# Host Docs repository-local V&V completion and status rebase

This retained record covers repository-local work for Host Docs PR #185 and Jira
CON-1518. It preserves the pre-edit repository identity and path/status baseline, the
failures found during the pass, each repository-local correction, and each
retest. It does **not** claim Host, API, paid, WAN, privileged, mutating,
destructive, or workload-affecting execution. It is not Product, Finance, Legal,
source-owner, reviewer, or human acceptance.

## Scope and evidence rule

- Primary Host scope: 40 top-level `/host/*` pages, including
  `/host/volume-offers`.
- Support scope: 18 CLI and 15 SDK wrapper pages. These are central-reference
  support layers, not independent Host workflows.
- Documentation text is always the claim under review, never evidence for
  itself.
- Implementation claims require canonical Vast code, schemas, configuration,
  generators, or generated references, with runtime/UI evidence where the claim
  also promises runtime behavior.
- Runtime behavior requires retained representative execution or UI evidence.
- Contract, price, payout, tax, policy, account, and legal claims require an
  accountable Product, Finance, Legal, or named source-owner confirmation. Code
  alone is insufficient.
- Missing evidence alone is `UNVALIDATED`. `FAIL` means a confirmed defect or a
  required citation/source binding that is absent. `BLOCKED` is used only when a
  suitable check cannot proceed because a concrete prerequisite is unavailable.

## Pre-edit working-tree baseline

The baseline was captured **before** this completion pass with the literal
commands `git status --short`, `git status --porcelain=v2 --branch`,
`git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, and
`git rev-list --left-right --count @{upstream}...HEAD`.

| Field | Retained value |
|---|---|
| Capture time | `2026-09-03T16:40:46Z` |
| Branch | `CON-1584-host-cli-api-sdk` |
| HEAD | `3b7e56f0db6588953589e0692e75b7274526d5f9` |
| HEAD tree | `b67e225c17901b4fa82c24f070c4de966de50681` |
| Upstream | `fork/CON-1584-host-cli-api-sdk` |
| Upstream relation | ahead 7, behind 0 |
| Sanitized path/status projection | [`pre-edit-working-tree-baseline-sanitized.txt`](./pre-edit-working-tree-baseline-sanitized.txt) |
| Sanitized projection SHA-256 | `a798f610af4e260c64a93d6b188e86cfb3b250a288651c938cd24b816c1ac80c` |
| Restricted raw capture SHA-256 | `b1bd6a1b423da195f68987e8a9b5ffe29bef7be00e0288eb3dbbc7f248ea981b` |
| Sanitized projection line count | 254 |

The retained `git status --short` output showed 40 tracked modified paths and
the following review-scope untracked paths. The linked, manifest-bound public
projection retains the complete Git/status data while replacing absolute
workstation and temporary-worktree paths. The exact raw capture remains outside
Git and is bound by digest; this inline review view omits one local tool-state
directory that is not a repository deliverable.

This baseline is exact for repository identity, path/status listings,
name-status/diffstat, worktree registry, and the SHA-256 hashes of eight selected
canonical artifacts. It is **not** a byte-for-byte snapshot of every dirty
working-tree file: the porcelain-v2 blob IDs for the other tracked paths identify
their HEAD/index versions, not their modified working-tree bytes, and untracked
directories are listed as collapsed paths. Those omitted pre-edit bytes cannot be
reconstructed from this record, so this limitation is retained rather than
claiming a full content capture.

```text
 M HOST-DOCS-CLI-COMMAND-CHECK.md
 M HOST-DOCS-COMMAND-ACCESS.md
 M HOST-DOCS-QA-SUMMARY.md
 M HOST-DOCS-VERIFICATION.md
 M cli/reference/create-volume.mdx
 M cli/reference/list-volume.mdx
 M cli/reference/list-volumes.mdx
 M cli/reference/unlist-volume.mdx
 M docs.json
 M guides/instances/storage/volumes.mdx
 M host-docs-cli-command-check.json
 M host-docs-command-access.json
 M host-docs-verification-inventory.csv
 M host-docs-verification-inventory.json
 M host/cli-api-sdk.mdx
 M host/common-errors-diagnostics.mdx
 M host/fleet-operations.mdx
 M host/host-teams.mdx
 M host/hosting-overview.mdx
 M host/machine-errors.mdx
 M host/maintenance-windows.mdx
 M host/market-metrics.mdx
 M host/network-ports.mdx
 M host/pricing-your-listing.mdx
 M host/removing-recreating-machines.mdx
 M review-server.mjs
 M scripts/inventory_host_docs.py
 M scripts/review-context.test.mjs
 M verification/HOST-DOCS-COMMAND-COVERAGE.md
 M verification/README.md
 M verification/evidence/2026-09-01-host-faq-route-attempt-01/result.md
 M verification/evidence/2026-09-01-host-faq-route-attempt-02/result.md
 M verification/evidence/2026-09-01-host-self-test-reference-attempt-01/result.md
 M verification/evidence/2026-09-01-host-team-catalog-attempt-01/result.md
 M verification/host-docs-command-scores.json
 M verification/host-docs-test-results.json
 M verification/host-docs-test-sets.json
 M verification/inventory.md
 M verification/issues.md
 M verification/summary.md
?? HOST-DOCS-PROCEDURE-VV-GOAL.md
?? HOST-DOCS-VV-COMPLETION-GOAL.md
?? HOST-DOCS-VV-CURRENT-STATUS.md
?? HOST-DOCS-VV-HANDOFF.md
?? HOST-DOCS-VV-INDEPENDENT-REVIEW.html
?? HOST-DOCS-VV-LOCAL-REVIEW-HANDOFF.md
?? findings.md
?? graphify-out/
?? host/volume-offers.mdx
?? node_modules/
?? progress.md
?? review-feedback/
?? scripts/__pycache__/
?? scripts/assemble_procedure_baseline.py
?? scripts/build_atomic_semantic_candidate.py
?? scripts/build_atomic_semantic_candidate_repaired.py
?? scripts/build_procedure_claim_integration.py
?? scripts/build_procedure_context_candidate.py
?? scripts/build_procedure_context_topology_rebase.py
?? scripts/build_procedure_topology_candidate.py
?? scripts/build_rendered_section_binding_candidate.py
?? scripts/test_inventory_host_docs.py
?? scripts/test_live_vv_authorization.py
?? scripts/test_procedure_baseline_integrity.py
?? scripts/validate_live_vv_authorization.py
?? task_plan.md
?? verification/LIVE-VV-AUTHORIZATION.md
?? verification/PROCEDURE-P1-READINESS.md
?? verification/VV-EVIDENCE-MIGRATION-PLAN.md
?? verification/VV-SKILL-BINDING.json
?? verification/evidence/2026-08-30-rendered-p1/
?? verification/evidence/2026-09-01-host-current-reconciliation-attempt-02/
?? verification/evidence/2026-09-01-host-install-retained-record-audit-01/
?? verification/evidence/2026-09-01-host-inventory-reconciliation-attempt-05/
?? verification/evidence/2026-09-01-host-inventory-reconciliation-attempt-06/
?? verification/evidence/2026-09-01-host-third-party-remediation-attempt-01/
?? verification/evidence/2026-09-02-cli-dump-logs-attempt-01/
?? verification/evidence/2026-09-02-cli-install-attempt-01/
?? verification/evidence/2026-09-02-cli-install-attempt-02/
?? verification/evidence/2026-09-02-cli-set-api-key-permissions-attempt-01/
?? verification/evidence/2026-09-02-host-diagnostic-direct-binding-reconciliation-01/
?? verification/evidence/2026-09-02-host-gpu-injection-attempt-01/
?? verification/evidence/2026-09-02-host-gpu-injection-attempt-02/
?? verification/evidence/2026-09-02-host-gpu-injection-attempt-03/
?? verification/evidence/2026-09-02-host-install-nvidia-smi-retained-01/
?? verification/evidence/2026-09-02-host-installer-log-attempt-01/
?? verification/evidence/2026-09-02-host-inventory-reconciliation-attempt-07/
?? verification/evidence/2026-09-02-host-kernel-log-follow-attempt-01/
?? verification/evidence/2026-09-02-host-local-bundle-attempt-01/
?? verification/evidence/2026-09-02-host-safe-readonly-attempt-01/
?? verification/evidence/2026-09-02-host-safe-readonly-attempt-02/
?? verification/evidence/2026-09-02-host-safe-readonly-attempt-03/
?? verification/evidence/2026-09-02-host-self-test-attempt-01/
?? verification/evidence/2026-09-02-host-self-test-log-follow-attempt-01/
?? verification/evidence/2026-09-02-market-metrics-rest-attempt-01/
?? verification/evidence/2026-09-03-host-reviewer-clarity-attempt-01/
?? verification/evidence/2026-09-03-host-source-binding-rebase-01/
?? verification/evidence/2026-09-03-host-source-link-migration-rebase-01/
?? verification/live-vv-authorization.schema.json
?? verification/procedure-baseline-p1.json
```

No pre-existing user change was discarded. Historical attempts remain retained;
new evidence either supersedes them explicitly or records a separate correction
and retest.

## Pinned canonical source identities

| Repository | Revision | Tree | Use |
|---|---|---|---|
| `vast-ai/vast-cli` | `ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd` | `f477989d0efd307154aeb623d6a1bfcee33e822a` | CLI registration, signatures, and request construction |
| historical `vast-ai/vast-cli` self-test input | `d4316fb06631cea759f5a36542e6196450e897f2` | `071045d45bd18446f1537ce0eadc25f922767abe` | deterministic self-test reference generation |
| historical `vast-ai/self-test` input | `6f93fc4ba8ec61e3360b28829e91665f3ba7ade6` | `5da8e8cc57cf1676183504e33ae6851d598d1a5e` | deterministic self-test event catalog generation |

Temporary checkout locations are deliberately not evidence identities. The
repository, revision, tree, path, locator, and source kind are carried in the
structured result records.

## Initial findings, corrections, and linked retests

| Initial finding or failed attempt | Repository-local correction | Retest/result |
|---|---|---|
| Baseline omitted `/host/volume-offers` and treated CLI/SDK wrapper routes as peer Host workflows. | Rebased topology to 40 primary Host pages; classified 18 CLI and 15 SDK wrappers as support layers. | Reconciliation check passes with 40 primary and 33 support pages. |
| 97 declared Host fragment targets had empty anchors. | Replaced them with named, `aria-hidden` anchor spans. | Named-anchor and Host-link checks pass; no Host fragment failure remains. |
| CLI verifier did not parse multiline commands reliably. | Added multiline extraction/signature handling and focused tests. | CLI signature verifier passes 201 occurrences against pinned canonical source. |
| Risk classification could understate multiline or privileged authored commands. | Made the classifier conservative and added focused test coverage. | Inventory tests and generated risk records pass. |
| Volume documentation lacked a general Host overview, API/source bindings, and central-reference role map. | Added `/host/volume-offers`, linked it from the Host overview, and bound its command/interface claims to canonical CLI/OpenAPI evidence. | Volume OpenAPI/static-source checker passes with an explicit runtime/commercial limitation; the page has 39 atomic claim contracts. |
| Three fenced Host workflow commands existed in inventory but had no exact procedure carrier. | Added exact carriers `CLM-2872a25df6add3a5`, `CLM-1e2f077efd167bfd`, and `CLM-0fa4c0088a41c909`; retired temporary wrong IDs. | Command-occurrence reconciliation accounts for 193 inventory commands and 179 procedure carriers. The three unsafe runtime carriers remain concretely `BLOCKED`. |
| Seven existing procedure scopes did not contain every owned command occurrence; the two VM additions also needed wider source spans. | Normalized the source scopes without changing the authored commands. | Procedure-baseline integrity and reconciliation checks pass. |
| Whole-page link inference overclaimed navigation proof, while 112 bounded index rows and seven exact local handoffs were later underclassified. | Restricted navigation evidence to exact standalone links, bounded Related Pages/Common Questions index rows, and exact “For …, see …” handoffs, then verified route/file/fragment resolution. | 140 exact navigation claims pass; topical suitability, prose/runtime claims, and linked-page semantics do not inherit link status. |
| Current selection could bind superseded `-01` evidence after a corrected `-02` attempt. | Excluded superseded attempts from current selection while preserving their history. | All current hardware-prep references select the corrected `-02` evidence. |
| Citation logic initially classified claims by page membership, missed some workload/payout policy statements, and treated local/action links as possible authority. | Made policy detection page/heading aware, disambiguated technical contract IDs, and distinguished authoritative-source candidates from documentation, console/action, upload/download, and contact links. | Material ledger now distinguishes 153 absent required citations, 19 present-but-unverified citations, and 1,515 claims not requiring an authoritative citation. |
| Evidence requirements were flattened, hiding mixed source/runtime/owner gaps. | Added per-lane unresolved requirements with evidence type, prerequisite, responsible role, required input, next action, and partial evidence. | Runtime/operator and source-owner registers are disjoint by prerequisite component and claim subject. |
| Some procedure `PASS` leaves lacked exact canonical source references. | Bound 17 Host Teams catalog carriers and two generated self-test parity steps to pinned source paths/locators. | Independent static query finds zero source-based `PASS` targets lacking structured source references. |
| Exact fenced commands could not inherit the correct narrow result without accidentally promoting surrounding prose. | Added an exact command-claim binder with lane compatibility and adverse-evidence limitations. | 104 fenced-command material claims receive bounded dispositions; source+runtime claims retain unresolved lanes. |
| Initial inventory and CLI `--check` runs found five stale generated artifacts. | Regenerated only deterministic repository artifacts. | Both checks pass on the regenerated state; the initial failures remain recorded here. |
| Direct `mint` was unavailable on `PATH`. | Used the repository-local executable. | Host scope has zero broken-link and zero page-local accessibility findings. Repo-wide Mint still reports unrelated non-Host findings described below. |
| Initial self-test and Volume checks omitted required explicit source arguments. | Re-ran with the exact pinned revisions/inputs. | Both checks pass; no default or ambient checkout is treated as authority. |
| Hosting Overview repeated an unsupported volume-offer commitment-window rule and coupled it to unproven machine-unlisting behavior. | Removed both assertions, retained the original claim as a historical `FAIL`, and kept the dedicated Volume/CLI handoffs. | Current Hosting Overview no longer makes either claim; local destinations resolve. |
| Storage Setup routed volume readers indirectly through Hosting Overview. | Linked its exact navigation occurrence directly to `/host/volume-offers`. | The current route/file hash is bound as a bounded navigation `PASS`; linked-page semantics remain separate. |
| Fenced and inline-code placeholders such as `<machine_id>` were stripped as MDX tags; fragment-only links were labeled external. | Added code-aware lossless normalization and classified both `/...` and `#...` references as local documentation. | Exact placeholder invariants pass; all 22 fragment-only refs are local. |
| Three generated self-test error rows treated technical instance contract IDs as legal contracts. | Disambiguated code identifiers and narrow instance/volume contract-ID phrases for policy classification only. | The two purely technical rows no longer fail for citations; the cleanup row retains its separate Product/Finance lane for billing wording. |
| Material-result roles called runtime PASS evidence “static” and hid partial evidence behind occurrence-only labels. | Added required, satisfied, and partially supported evidence lanes with status-appropriate neutral roles. | Eight exact runtime command claims retain bounded runtime PASS; 35 partial bindings remain non-passing but visible. |
| Volume authority summaries could omit an operator or merge technical and owner roles. | Derived each summary from the distinct per-lane responsible roles. | Zero unresolved-authority summary mismatches remain. |
| The generic material denominator skipped the rendered Notifications snippet and visible Frame captions, while counting non-rendered MDX comments. | Bound imported local MDX bytes and insertion sites to their Host page, inventoried five rendered snippet claims and 24 visible UI captions, and masked comments outside code fences without changing line geometry. | Dependency hashes, exact source spans, UI lanes, and the mandatory-email citation failure are covered by focused regressions. |
| The 35-claim Volume map omitted line 29, the line-47 renter handoff, and two publishing recommendations embedded beside interface claims. | Expanded the map to 39 exact atomic claims: two bounded static PASS claims and two owner-governed UNVALIDATED recommendations. | All four prior gaps have explicit source spans, evidence types, authorities, limitations, and next actions. |
| UI workflow text could receive only source/owner lanes, and seven blocked non-Volume runtime claims were omitted from the runtime register because of an unhandled prerequisite kind. | Added conservative UI surface/action detection and included `ENVIRONMENT_OR_PERMISSION` in the runtime register partition. | Named UI fixtures carry `RUNTIME_OR_UI_OBSERVATION`; the register contains the exact set of all 23 blocked runtime claims. |
| One descriptive Headless Install sentence became a false policy failure because it used “provider” and “do not.” | Removed bare technical “provider” from the policy trigger while retaining provider-policy and normative terms. | The exact claim is UNVALIDATED for source evidence, not a missing-citation FAIL. |
| Plural payout, invoice, and responsibility terms plus a rental-dedication rule escaped owner/citation classification; four operational or routing sentences were false policy matches. | Added bounded plural and rental-policy rules, and disambiguated the exact technical contract-event, expired-rental, page-scope, docs-routing, and negated-pricing diagnostic phrases. | Exact positive and adverse fixtures now separate owner-governed claims from runtime, diagnostic, and documentation-routing claims. |
| Contract, provider, tax, account-security, and datacenter list qualifiers were detached from their items; two complete lead-ins also contained a separate claim. | Bound the exact context source spans to each dependent item, retained only the complete atomic lead-in sentences, and placed the known Hosting Agreement candidate citation in the two governing source lines. | Every affected claim hashes its literal declared spans; two pure lead-ins were retired and mixed lead-ins remain separate exact claims. |
| Datacenter eligibility/application rules, gross-revenue composition, and mixed price/contract claims omitted accountable owner domains. | Added page/heading-bounded program and revenue rules and derived mixed owner roles from the union of Product, Finance, Trust/Security, and Legal domains. | Requirements remain FAIL where citation is absent; revenue claims remain UNVALIDATED pending Product/Finance authority; mixed-domain roles no longer omit Legal or Finance. |
| Datacenter application, Discord connection, and W9 submission links were not treated as live action/UI claims. | Added exact action-path runtime/UI lanes without treating action destinations as authoritative sources. | The action claims remain non-passing until retained UI/runtime evidence exists; the W9 policy/citation defect remains independently visible. |
| The retained CLI API-key permission failure and its four required ancestors used generic discrepancy text. | Bound the exact macOS arm64/Python 3.14.6/Vast CLI 1.5.6 mode-0644 observation, bounded limitation, and platform-appropriate corrective retest to all five FAIL projections. | Each level points to failing command `CLM-b3cd48630e5f2b0c`; no descendant or ancestor is generalized to PASS. |
| The fail-closed reviewer schema validates the current unresolved package but cannot yet represent a future fully satisfied multi-lane owner claim or verified citation. | Kept the validator strict and recorded a forward integration gate rather than inventing owner evidence or accepting an untyped confirmation. | Before future owner evidence can promote a claim, add per-lane satisfied evidence/authority, a verified-citation state, and positive/adverse fixtures. This does not affect the honesty of current unresolved statuses. |
| Only the current rebase result was hash-bound. | Manifest-bound every attempt artifact and added the pre-edit path/status baseline as its own retained attempt. | 54 attempt records reference 53 unique immutable artifacts; the baseline's documented content-snapshot limitation and historical qualification still control what each artifact may support. |
| A source-binding provenance record was incorrectly listed as an unused command-score proof ceiling. | Removed it from direct-proof ceilings while retaining its exact per-target source references and limitations. | 38 consumed direct-proof ceilings and 101 command-specific bindings remain. |
| The first reconciliation invocation omitted the required `--write`/`--check` mode. | Preserved the nonzero usage result and re-ran explicitly with `--write`, then `--check`. | Deterministic write and idempotence check pass. |
| The first broad unittest invocation used invalid dotted module paths and produced six import errors. | Preserved that command error and reran with repository discovery. | The current complete Python discovery passes 85 tests. |
| The first final pinned-source replay used a mistyped historical CLI object (`d4316fb50a2354ad7019a4be28c4a048483d8d7a`) and failed before a source check ran. | Resolved the exact revision from the retained source contract (`d4316fb06631cea759f5a36542e6196450e897f2`) rather than guessing from an abbreviated display value. | The corrected detached-source replay identifies all three exact revisions and passes CLI, Volume/OpenAPI, and self-test generation checks. |
| The corrected pinned-source replay then found the CLI report and Markdown summary stale after the final documentation edits. | Regenerated only the deterministic CLI registry outputs against clean `vast-cli@ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd`. | The unchanged `--check` replay passes all 201 occurrences; the complete three-source replay then passes. |
| An attempted `api-reference/openapi/build.py --help` probe exposed that the generator has no help mode and began generation before the output pipe ended. | Treated it as a command-contract mistake, then ran the generator normally with before/after hashes and validated the result. | The complete generator preserves SHA-256 `1bea2a6520813589ce34492164dcd0ad6884416be14a2c1745104017c7136ff0`; Mint reports the OpenAPI definition valid. |
| The expanded reviewer sanitation fixture showed that compressed IPv6 and bare `token=` assignments could reach page context unredacted. | Extended reviewer-output sanitation for bracketed/compressed IPv6 and generic token assignments without weakening existing path, identifier, password, API-key, or high-entropy-token handling. | The unchanged sanitation regression passes, and the complete fail-closed reviewer suite passes 21 tests. |
| Reviewer badges displayed Jira statuses without saying that their only repository authority is the dated traceability snapshot. | Added `statusAsOf: 2026-07-13` and `statusVerification: UNVERIFIED_SNAPSHOT`, and rendered both qualifiers beside every status. | API and rendered-label regressions pass; the UI no longer implies current Jira state. |
| A final 21-test reviewer replay passed 20 tests but intermittently lost one large fixture response with `UND_ERR_SOCKET` because the helper terminated its isolated server before awaiting `response.json()`. | Awaited full response-body consumption before the helper's existing cleanup runs; no production reviewer behavior or evidence status was weakened. | The unchanged 21-test suite passes on the corrected harness, including the formerly flaky score/status-separation case. |
| Recording that harness failure changed this manifest-bound result after the prior reconciliation write; the next reviewer replay correctly failed closed (`9/21` passed) because the retained artifact hash no longer matched its manifest. | Refreshed the deterministic artifact manifest only after the chronology entry was complete. | Reconciliation and strict reviewer startup accept the new exact result hash, then the unchanged 21-test suite passes. |
| The first post-fix browser screenshot recapture stalled and was interrupted without producing an artifact. | Started a fresh isolated browser session and repeated the same loopback observation. | `browser-hosting-overview-vv-sanitized-retest-02.png` was retained successfully and is hash-bound below. |
| An initially broad repository MDX sanitation sweep returned one credential-pattern candidate and one private-path candidate, both in non-Host files outside PR #185 / CON-1518. | Derived the exact 73 primary/support route files from the canonical inventory and added the reviewer-facing closeout records; did not relabel or assess the two out-of-scope candidates. | The correctly scoped retest reports zero credential-pattern files and zero private-local-path files. The two non-Host candidates remain outside this result. |
| Independent closeout consistency review found one handoff sentence still saying 176 command assessments and one summary sentence still saying the named-anchor replay was pending. | Updated the prose to the canonical 179 carriers (152 scored plus 27 display-only `NOT_APPLICABLE`) and the completed passing anchor replay. | Reconciliation, inventory, manifest-hash, and fail-closed reviewer checks pass on the corrected closeout package. |

## Final repository-local coverage

### Procedure projection

| Level | Total | PASS | FAIL | BLOCKED | UNVALIDATED | NOT_APPLICABLE |
|---|---:|---:|---:|---:|---:|---:|
| Page | 40 | 1 | 1 | 12 | 26 | 0 |
| Test set | 101 | 8 | 1 | 16 | 76 | 0 |
| Branch | 207 | 9 | 1 | 26 | 171 | 0 |
| Step | 477 | 26 | 1 | 34 | 416 | 0 |
| Command | 179 | 84 | 1 | 7 | 60 | 27 |
| **Total** | **1,004** | **128** | **5** | **95** | **749** | **27** |

This table is procedure execution/required-child status only. It is not a
material-claim semantic rollup.

### Material claims

| Measure | Retained result |
|---|---:|
| Material claims | 1,687 |
| PASS | 167 |
| FAIL | 153 |
| BLOCKED | 23 |
| UNVALIDATED | 1,344 |
| Pages by material-claim disposition | 3 BLOCKED, 26 FAIL, 11 UNVALIDATED |
| Required citation absent | 153 |
| Citation present but authority unverified | 19 |
| Citation not required by claim semantics | 1,515 |

A material `FAIL` is not generalized from a procedure status: it identifies a
confirmed claim defect or an exact claim whose required citation/source binding
is missing. The ledger records the page, heading, source span, claim, evidence
type, authority or unresolved role, status rationale, retained evidence,
limitations, and exact next action for every claim.

### Command evidence quality

Of 179 carriers, 27 are explicitly non-executable display and therefore
`NOT_APPLICABLE`. The 152 scored carriers are distributed as 12 score 1,
119 score 2, and 21 score 3. Scores describe semantic support quality; they do
not override execution status or promote a parent procedure.

## Safe final commands and observations

All commands below are repository-local or operate on pinned read-only source
checkouts. No credential, Host, external API, paid resource, WAN probe,
privileged mutation, workload, or destructive action was used.

| Check | Final observation |
|---|---|
| `python3 -B scripts/reconcile_host_vv_repository.py --check` | PASS: 40 primary pages, 33 support pages, 1,004 projected targets. |
| `python3 -B -m unittest discover -s scripts -p '*test*.py'` | PASS: 85 tests. |
| `python3 -B scripts/inventory_host_docs.py --check` | PASS after retained stale-artifact failure and regeneration: 73 routes, 501 unique targets, 565 occurrences, and 193 commands in five groups. |
| pinned CLI signature checker | PASS after retained stale-artifact failure and regeneration: 201 occurrences. |
| named-anchor checker | PASS for Host scope. |
| Host persona checker | PASS for 40 primary pages. |
| Volume OpenAPI/static-source checker with explicit pinned input | PASS, limited to interface/source conformance. |
| self-test reference generator `--check` with explicit pinned inputs | PASS, byte-identical historical-source generation. |
| deterministic OpenAPI build plus repository-local `mint openapi-check` | PASS: before/after SHA-256 is identical and the combined definition is valid. |
| `npm run test-review-context` | PASS: 21 tests, including 56 malformed-package modes, the missing-package case, sanitation, accessibility, exact claim/citation accounting, support layers, scope links, evidence links, and feedback import. |
| inventory-derived Host/support and reviewer-record credential/private-path scan | PASS: zero credential-pattern files and zero private-local-path files in the exact 73-route Host/support scope plus reviewer-facing closeout records. |
| `git diff --check` | PASS. |
| JSON parsing for canonical ledgers | PASS. |
| repository-local `mint broken-links` | Exit 1: 99 findings in 10 non-Host files; zero findings in the 40-page Host scope. |
| repository-local `mint a11y` | Exit 1: one shared dark-theme contrast finding and 74 image findings in 19 non-Host files; zero page-local Host findings. |

The Mint exit codes are not relabeled as global passes. They are retained
repo-wide failures with a zero-finding Host-scope observation, and their
non-Host remediation is outside PR #185 / CON-1518.

## Browser and reviewer-interface retest

The corrected loopback-only review server restarted with strict package
validation. Agent Browser `0.26.0` then performed these local observations; no
external destination, credential, Host, API, paid resource, or workload was
used:

- all 40 primary Host routes rendered at their exact route with a non-empty H1
  and an injected page-scoped reviewer context;
- all 33 support routes rendered and identified themselves as central-reference
  support layers rather than Host workflows, with each of the 18 CLI and 15 SDK
  destinations matching its exact canonical reference route;
- `/host/hosting-overview`, `/host/volume-offers`, `/host/storage-setup`, and
  `/host/how-to-self-test` exposed exact page/section scope links. Storage Setup
  links directly to `/host/volume-offers`;
- the Volume panel showed 39 material claims and separated its material
  disposition (`19 PASS`, `1 FAIL`, `16 BLOCKED`, `3 UNVALIDATED`) from its
  procedure status. The `VOL-C01` evidence link opened a generated navigation
  header naming `/host/volume-offers`, `Introduction`, the exact claim, required
  lanes, `BLOCKED` rationale, and limitation before the retained artifact;
- the status page showed 40 primary pages, 1,687 material claims, 101 sets, 207
  branches, 477 checks, 179 carriers, 95 reviewer-visible retained evidence
  records, and 18/15 support layers. Its material counts were exactly
  `167/153/23/1,344` and page dispositions `26 FAIL/3 BLOCKED/11 UNVALIDATED`;
- Jira badges rendered `snapshot 2026-07-13 (unverified)`. The final browser
  error collection was empty. Six expected local Mint development Socket.io
  connection warnings were observed separately and are not page exceptions.

The screenshots are supplemental UI evidence. Their hashes are carried here so
the manifest-bound result detects substitution; they establish only the visible
local state shown, not semantic product behavior.

**Status-screenshot publication amendment (2026-09-04).** The original status
capture (SHA-256
`32dcfc49381d2060a4e7309a75b6cf68e323d566f78134acb723ef2efa9812dc`)
showed synthetic reviewer fixtures used during local UI testing. It remains
local and is not part of the publication set. The replacement was captured from
the same current reviewer bytes against an isolated empty feedback directory;
it shows zero review items and cannot be interpreted as human acceptance. This
presentation-only September-4 retest displays the current 96-record evidence
count; it does not replace the September-3 numeric observation above or alter
any outcome or limitation in this record.

| Screenshot | SHA-256 |
|---|---|
| [`browser-hosting-overview-vv.png`](./browser-hosting-overview-vv.png) | `a7f59bcc7506f6cc070796aae03704ee6071cebae8aa1f037e8b24f199f2f8c5` |
| [`browser-hosting-overview-vv-expanded.png`](./browser-hosting-overview-vv-expanded.png) | `64b46f9d403d6b1466bcf0fb5bdde9f751b9b2c7e08d4d776db70c8c2a5ac3cb` |
| [`browser-volume-offers-vv.png`](./browser-volume-offers-vv.png) | `02443d7436b6dd7c3e14115f3a53c8fcd49d290d65fa8c53817911f4b2046dbe` |
| [`browser-review-status-empty-retest-01.png`](./browser-review-status-empty-retest-01.png) | `2b913ec083af972fa6345f4ac021e0b5d35c3804ac76e8ae0f0e39fbae404ab0` |
| [`browser-hosting-overview-vv-sanitized-retest-02.png`](./browser-hosting-overview-vv-sanitized-retest-02.png) | `6b598cca4d3360ca50c8a9e991813117c55faa4aec79271663e755ee0a88f773` |

## Remaining work outside this repository-local pass

The exact outstanding prerequisites are maintained in two separate registers:

1. [`verification/runtime-operator-blockers.md`](../../runtime-operator-blockers.md)
   — credentials, representative Hosts, permissions, controlled runtime inputs,
   and authorization needed for runtime/operator checks.
2. [`verification/source-owner-blockers.md`](../../source-owner-blockers.md)
   — accountable Product, Finance, Legal, or named source-owner confirmation and
   authoritative source inputs.

Those external workstreams are not complete. Every register entry identifies
the affected page/heading/claim, concrete missing prerequisite, claim impact,
available partial evidence and limitation, responsible role, and exact next
action. No generic “needs evidence” label is used as a blocker.

## Acceptance boundary

This record establishes repository-local completion only: inventory,
traceability, exact status accounting, safe static/source/render checks,
corrections, and retained evidence packaging. It does not assert that all Host
documentation behavior is validated, and it does not record human acceptance.
No branch was pushed, no Jira issue was changed, and no merge was performed.
