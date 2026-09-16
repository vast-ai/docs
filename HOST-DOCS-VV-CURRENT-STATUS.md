# Host Docs V&V current-status checkpoint

> Historical checkpoint: the counts below preserve the pre-execution
> reconciliation state. They are superseded by the current 2026-09-03
> repository-local projection in `HOST-DOCS-QA-SUMMARY.md`: 128 PASS, 97
> BLOCKED, 747 UNVALIDATED, 5 FAIL, and 27 N/A across 1,004 targets. Current
> command-carrier counts are 84 PASS, 7 BLOCKED, 60 UNVALIDATED, 1 FAIL, and 27
> N/A; semantic counts are 12 score-1, 119 score-2, 21 score-3, and 27 approved
> N/A. This is 84 of 152 applicable commands passing (55.3%), with 68 of 152
> still non-passing (44.7%). The primary scope is 40 Host pages; 33 CLI/SDK
> routes are support wrappers, yielding 73 routable files in the broad source
> inventory.
>
> The current repository-local evidence structure is complete for traceability
> review. Semantic acceptance, runtime/operator work, source-owner confirmation,
> and human approval remain incomplete.
>
> Official Host self-test uses the Host's own hardware. It requires a securely
> supplied Host-owner credential with `machine_read`, a protected workload
> window, a positive runtime limit, and cleanup authority, but no paid-test
> budget. Paid renter testing is separate. Host execution is paused after
> transient workload activity made the environment uncontrolled.
> Do not quote this checkpoint's historical counts as the current V&V result.

Date: 2026-09-01
Scope: 39 primary Host pages in `vast-ai/docs` PR #185 / Jira `CON-1518`
Mode: fail-closed reconciliation before new live, paid, WAN, mutating, or destructive work

## Outcome

The retained evidence is useful, current at the page-content snapshot level, and fully
accounted for. It is not yet a complete procedure-level V&V package.

- `EVIDENCE_PACKAGE_COMPLETE`: **NO**
- `TARGET_ACCEPTANCE_CANDIDATE`: **NO**
- Complete procedures currently at `PASS`: **0 of 97**
- The all-`UNVALIDATED` display in the port-4000 reviewer is a known projection gap: it
  copies frozen parent statuses instead of deriving the reconciled outcomes below.

## 1. Source identity

| Identity | Value | Interpretation |
| --- | --- | --- |
| Current Git revision | `14d9af21fe8a6df205180d6f211415bf750ee4b8` | Working revision used for this checkpoint |
| Current Git tree | `2eded9e87079a3cb2517ee7a7448018c388b122b` | Current tracked tree |
| Inventory-declared revision | `09d729e72fbcb2bdd2dead2b9dc5d5e1eeeffcf5` | Four commits behind current revision |
| Inventory-declared tree | `bfe3e9316893a2174b99779ce844e81f014d2b53` | Stale top-level metadata |
| Test-set snapshot SHA-256 | `50b010956942a3294ea12cbc3936330fbad2be932948a9b4b3e747c8c72c051a` | Exact bytes bound by results and scores |
| Result file SHA-256 | `37496109bdac5879b8ce5932e9339ff01c1114d548b174b06b5fc4dc379e55c1` | Retained result snapshot |
| Score file SHA-256 | `80fbf0498c82a663d14f8f93a9ad0faa8d713aa5450c286c323deed18cec681b` | Retained semantic-score snapshot |

All 39 recorded page hashes match the current Host source bytes. Four Host pages changed
between the declared revision and current revision—`fleet-operations`, `machine-errors`,
`pricing-your-listing`, and `vms`—but their inventory page hashes are current. The package
therefore has a current content-snapshot join with stale top-level Git metadata. Individual
result rows still lack their own source-revision/hash and generic current/supersedes links.

## 2. Reconciled status counts

These are checkpoint dispositions derived from retained evidence, corrected blocker
taxonomy, command-free-step review, required-step roll-up, and the independently reviewed
branch policy. They have not yet replaced the frozen statuses in the canonical JSON or
reviewer.

| Level | PASS | BLOCKED | UNVALIDATED | NOT_APPLICABLE | FAIL | STALE | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Command carriers | 6 | 42 | 116 | 1 | 0 | 0 | 165 |
| Steps | 0 | 322 | 145 | 1 | 0 | 0 | 468 |
| Branches | 0 | 155 | 48 | 0 | 0 | 0 | 203 |
| Test sets | 0 | 69 | 28 | 0 | 0 | 0 | 97 |
| Pages | 0 | 34 | 5 | 0 | 0 | 0 | 39 |

Of 451 required steps, 313 are blocked, 137 are unvalidated, and one is not applicable.
The 17 optional steps are nine blocked and eight unvalidated. No command-level PASS was
promoted to a step PASS without linked prerequisites, checkpoints, final observable, and
cleanup evidence.

Roll-up policy used here:

- ordered required branches gate their test set;
- each determinate alternative group requires one passing member;
- alternatives whose applicability is not yet selected remain unvalidated;
- optional modifiers and failure-only branches do not gate an unselected normal path;
- required-child precedence is `FAIL`, `STALE`, `BLOCKED`, then `UNVALIDATED`;
- partial evidence is reported as coverage and never treated as PASS.

## 3. Attempt and evidence linkage

- 18 retained attempts contain 37 command-result rows.
- Those rows contain 50 command bindings covering 35 unique command carriers.
- Carrier evidence kind: 35 behavioral, 53 signature-only, and 77 with neither.
- Nine carriers have conflicting candidate outcomes without a generic current/supersedes
  relationship. They remain `UNVALIDATED`; array order is not treated as chronology.
- The frozen inventory has zero attempt links at test-set, branch, or step level and six
  command carriers with attempt/evidence links.
- All 357 command-free steps were reconciled. None has an exact, current, claim-suitable
  retained observation. Their corrected evidence dispositions are 235 authority-blocked,
  52 environment-blocked, 56 review-UI candidate-link ambiguities, and 14 unevidenced.
- Static link, persona, generated-source, and rendered-review evidence remains useful but
  is not silently promoted into product or procedure behavior.

## 4. Semantic scoring

- Scored carriers: 32 of 165 (19.4%).
- Score 1: 0.
- Score 2: 20.
- Score 3: 12.
- Unscored carriers: 133.
- Withdrawn score records retained for audit: 3.

Execution status and semantic score remain separate. A score of 3 does not create a PASS,
and a blocked command can still receive a score describing how well its safe evidence
supports the surrounding wording. Every remaining carrier still needs a 1–3 assessment or
an approved `NOT_APPLICABLE` rationale before evidence-package completion.

## 5. Corrected blockers

The 31 frozen blocked steps own 38 command carriers. They are not all documentation
defects: the canonical frozen split was 29 `SOURCE_DEFECT_BLOCKED` plus two
`EXECUTABLE_TEMPLATE` rows, and the current source/evidence review replaces that taxonomy.

| Current blocker category | Steps |
| --- | ---: |
| Safety or mutation blocked | 15 |
| Parameter required | 7 |
| Non-executable source form | 3 |
| Corrected/retested documentation defect | 2 |
| Test or extraction defect | 2 |
| Environment blocked | 1 |
| Ambiguous; needs review | 1 |

Current V&V disposition for those 31 steps is 25 `BLOCKED`, six `UNVALIDATED`, and zero
`PASS`. The corrected defrag and pricing examples have current source plus read-only
CLI-help correction evidence, but their live state-changing behavior remains blocked.

## 6. Procedure queues

### Already complete at PASS

None. Six command carriers have uncontested observed PASS, but no full test set has linked
evidence for every required action, contextual claim, observable, and cleanup.

### Safe work that can proceed now

1. `TS-FAQ-C01` — resolve every Host question route/anchor and confirm ownership.
2. `TS-TEAM-C01` — verify the Host-team CLI support catalog as static signature evidence,
   not as a live mutation workflow.
3. `TS-COM-E02` — review a synthetic, redacted Host help request against the page rules.
4. `TS-STR-C01` — verify generated-reference provenance and isolated regeneration parity.
5. `TS-HWP-E01` — run the documented read-only clean-host inventory sequence on the
   authorized Host, retain sanitized output, review it, and record cleanup/no-mutation.
6. `TS-HWP-C01` — assess the observed Host against the standard readiness claims. The
   VM-planned branch remains separate until the repaired VM target is representative.

### Must remain blocked until its exact gate is met

- account/team/UI procedures needing the correct authorized role or owner;
- Host self-test work until a fresh securely injected Host-owner key, an idle listed
  target, a runtime cap, stop authority, and cleanup proof are available;
- paid renter-side work until a fresh securely injected client key, a numeric spend and
  runtime cap, stop authority, and cleanup proof are available;
- external TCP/UDP work until an approved unused forwarded port and genuine external
  client are available;
- Docker GPU/load work until the Host is confirmed idle/unrented and the exact load is
  approved;
- VM work until IOMMU repair/reboot, rental prevention, idle state, and operation approval;
- installer, storage, daemon-range, listing/pricing, maintenance, default-job, defrag,
  decommission, and team mutations until a disposable target or explicit operational
  change authority exists;
- machine-error, verification-timing, Host Teams, pricing/business, legal, tax, payout,
  and policy claims until an authoritative owner or current canonical source is linked.

## 7. Next smallest safe batch

Run the four local/static sets first in the order listed above. Preserve one attempt record
per coherent procedure, including source identity, exact steps, observation, limitation,
and semantic assessment. Then run the two Host-read procedures in their documented order,
using only read-only commands and sanitized retained output. Stop before any mutation,
paid action, WAN listener, GPU load, or VM transition.

After this batch, update the canonical result/score snapshots and the port-4000 reviewer
so each page shows reconciled status, coverage, evidence, blockers, limitations, and
scores rather than the frozen inventory status.

## Reconciliation evidence

- `.orchestra/host-vv-reconciliation-20260901/artifacts/evidence-linkage.json`
- `.orchestra/host-vv-reconciliation-20260901/artifacts/blocker-reclassification.json`
- `.orchestra/host-vv-reconciliation-20260901/artifacts/noncommand-linkage.json`
- `.orchestra/host-vv-reconciliation-20260901/artifacts/branch-policy-corrections.json`
- `.orchestra/host-vv-reconciliation-20260901/findings/source-identity.html`
- `.orchestra/host-vv-reconciliation-20260901/findings/noncommand-linkage-review.html`
- `.orchestra/host-vv-reconciliation-20260901/findings/branch-policy-review.html`

This checkpoint is a local reconciliation artifact. It is not a human acceptance record
and has not been pushed or posted to GitHub or Jira.
