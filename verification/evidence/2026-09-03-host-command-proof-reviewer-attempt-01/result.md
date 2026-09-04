# Host command-proof reviewer correction — attempt 01

- Attempt: `ATTEMPT-2026-09-03-HOST-COMMAND-PROOF-REVIEWER-01`
- Evidence: `EV-HOST-COMMAND-PROOF-REVIEWER-01`
- Jira / pull request: `CON-1518` / Host Docs PR #185
- Pages: `/host/how-to-self-test` and `/host/vms`
- Method: `STATIC_SOURCE_SIGNATURE_RUNTIME_EVIDENCE_UI_RECONCILIATION`
- Outcome: `PASS` for the bounded repository-local reviewer correction only
- Completed: `2026-09-03T20:27:25Z`
- Credentialed Host/API, paid, WAN, privileged, mutating, destructive, or
  workload-affecting operation: none

## Claim under review

The reviewer must let a reviewer answer, for each exact documented command:

1. where the command occurs on the page;
2. whether the pinned canonical implementation recognizes its signature;
3. whether a representative runtime attempt exists and what it observed;
4. why the current status is `PASS`, `FAIL`, `BLOCKED`, or `UNVALIDATED`;
5. what remains unproved and the exact next action.

Documentation text is the claim under review, not evidence for itself. A
topology/status reconciliation record proves accounting only and cannot prove
that a command executed or behaved as documented.

## Defects retained

- The page panel foregrounded `EV-HOST-CURRENT-RECONCILIATION-01` under each
  test set. Although the record said it was classification only, its placement
  made it look like runtime proof.
- Three Self-Test command carriers were attached to the narrative **What
  Self-Test Checks** step instead of their actual **Before You Run It** and
  **Run The Test** headings.
- Exact commands did not provide separate source/signature and runtime lanes;
  the reviewer had to infer applicability from aggregate counts, semantic
  scores, and detached evidence records.
- Retained-evidence navigation did not state which page, heading, target, and
  command binding caused the evidence to be shown.
- The VM page could show an overall `UNVALIDATED` or `BLOCKED` rollup without
  making clear that the exact read-only `check` carrier passed while the
  mutating `off` carrier did not have representative evidence.

The exact Self-Test carrier relocation and status-preserving accounting change
is retained separately in
[`EV-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01`](../2026-09-03-host-self-test-topology-correction-01/result.md).

## Exact command proof matrix

| Page / heading / command | Canonical source or unresolved authority | Retained runtime evidence | Current result and rationale | Exact next action |
|---|---|---|---|---|
| `/host/how-to-self-test` · **Before You Run It** · `CLM-b3cd48630e5f2b0c` · `vastai set api-key <API_KEY>` | `PASS`: pinned Vast CLI handler [`set__api_key`, `auth.py:199-204`](https://github.com/vast-ai/vast-cli/blob/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd/vastai/cli/commands/auth.py#L199-L204) and generated argparse registry check | `EV-CLI-SET-API-KEY-PERMISSIONS-01`, direct functional partial | `FAIL`: the exact isolated synthetic invocation exited 0 but created the credential file with mode `0644` under umask `022`. It proves neither secure storage nor real Host authentication. | CLI owner corrects atomic owner-only credential-file creation; retain synthetic no-network retests on Linux, macOS, and Windows. |
| `/host/how-to-self-test` · **Run The Test** · `CLM-3ba3b25f5c3ddac1` · `vastai self-test machine <machine_id>` | `PASS`: pinned Vast CLI handler [`self_test__machine`, `machines.py:699-717`](https://github.com/vast-ai/vast-cli/blob/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd/vastai/cli/commands/machines.py#L699-L717) and generated argparse registry check | No direct representative runtime evidence | `UNVALIDATED`: source proves the command signature exists; it does not prove offer selection, temporary-instance creation, image execution, result rendering, or cleanup. Missing proof alone is not a blocker. | Authorized Host operator supplies a suitable idle listed machine, Host-owner credential with required permission, bounded runtime, and cleanup authority, then retains the exact run and before/after state. |
| `/host/how-to-self-test` · **Run The Test** · `CLM-3fa5d5948b34fc6a` · `vastai self-test machine <machine_id> --support-bundle-dir /path/to/output` | `PASS`: the same pinned handler and the generated registry check include `--support-bundle-dir` | `EV-HOST-SELF-TEST-01`, direct functional partial | `BLOCKED`: the exact form reached `select_offer` and retained a structured `api_permission_failed` result before instance creation. The unavailable prerequisite is a Host-owner credential with the required machine-read permission; no workload or cleanup path ran. | Repeat under separately approved Host-owner authorization on a suitable idle machine and retain bundle path, terminal result, instance lifecycle, and cleanup evidence. |
| `/host/vms` · **Check VM Status** · `CLM-ca44522b22c4c5ee` · `python3 /var/lib/vastai_kaalia/enable_vms.py check` | `UNVALIDATED`: no immutable canonical helper-source binding is available in the documentation repository; the Host software/source owner is required for implementation provenance | `EV-HOST-SAFE-READONLY-02-VM-CHECK`, direct functional exact-full for this carrier | `PASS` for the exact read-only carrier: a later representative preflight found the helper and IOMMU groups, and the command exited 0 with `off`. This does not validate the page's disable or enable workflows. | Bind the helper to immutable canonical source; test other documented status values only when their representative states are safely available. |
| `/host/vms` · **Disable VM Support** · `CLM-9cba75bbdc780804` · `sudo python3 /var/lib/vastai_kaalia/enable_vms.py off` | `UNVALIDATED`: immutable helper source and privilege/state-transition contract remain unavailable | The earlier `EV-HOST04-VM-OFF` observation was withdrawn for acceptance because the VM/IOMMU target was improperly configured | `UNVALIDATED`: the prior exit-0/off observation is historical but non-representative; it cannot prove disablement on a correctly configured VM-capable Host. The command is not labeled `BLOCKED` merely because direct proof is missing. | Host software owner supplies immutable source/contract; an authorized operator uses a suitable idle, unlisted VM-capable Host, records before/after state and completion timing, and verifies cleanup without an active workload. |

The VM page/test-set remains non-passing because a child command PASS proves
only that read-only carrier. Parent status is not promoted over unvalidated or
blocked required behavior elsewhere in the procedure.

## Repository-local corrections

- Added a fail-closed schema-v2 CLI-signature registry with exact handler path,
  symbol, and line range at pinned revision
  `ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd`.
- Made each exact command in the reviewer proof card a clickable immutable
  source link when canonical source support exists.
- Added separate **Source/signature support** and **Runtime behavior** lanes,
  including current status, observation, evidence role, limitations, and a
  runtime-proof next action.
- Relabeled reconciliation/topology records as **Accounting/status derivation
  only — not command proof** and collapsed them behind that label.
- Bound evidence navigation to the exact page, heading, target, command,
  current status, and proof role. The generated navigation header explicitly
  says that it is context, not evidence.
- Corrected the three Self-Test command owners without changing their command
  statuses: API key `FAIL`, plain self-test `UNVALIDATED`, and bundle form
  `BLOCKED`.
- Updated `REVIEW-TRACEABILITY.md` and `verification/README.md` with the same
  two-lane proof model and concrete examples.

## Preserved failures and correction chain

| Attempt or check | Original result | Correction and retest |
|---|---|---|
| Reviewer suite immediately after the topology artifact was added | `10/24`; the reviewer failed closed with `invalid V&V scope reconciliation` | Added strict validation for the declared topology-correction structure and bindings; later suite passed `24/24`. |
| Next reviewer replay | `21/24`; one limitation expectation, accounting-record classification, and aggregate totals were stale | Updated only the corresponding contract/classification/count assertions; unchanged full replay passed `24/24`. |
| First Volume/OpenAPI invocation | Exit `2`; required `--vast-cli` input was omitted | Reissued with the explicit pinned clean checkout; static comparison passed with its no-runtime limitation retained. |
| First historical Self-Test generator `--check` | Failed because the temporary clone exposed local branch/remote identity instead of the canonical `vast-ai/vast-cli master` source metadata | Set the disposable clone to the canonical branch and official remotes, then reran against the same historical revisions; passed. No tracked source was changed for this tool setup error. |
| First browser attribute request | Unsupported `get attribute` form | Used the supported `get attr` form and verified exact command, source, page/heading, and evidence URLs. |
| Browser screenshot attempts | Two explicit-path captures hung and were interrupted; a selector capture reported zero width | Did not use those attempts as evidence. Retained DOM/accessibility inspection and direct reviewer API checks; a later bounded page capture completed. |
| First Mint replay after traceability examples | `103` broken links in `11` files; four were newly added repository-relative evidence links | Changed only those four review-document links to reviewable branch URLs. Unchanged replay returned the known `99` findings in `10` non-Host files and zero Host-page findings. |

## Retained checks

| Check | Result |
|---|---|
| `npm run test-review-context` | `PASS` — 24/24, including exact source links, command-bound evidence, accounting-only labels, four status classes, and parent non-promotion |
| `python3 -B -m unittest discover -s scripts -p 'test_*.py'` | `PASS` — 94/94 |
| `python3 scripts/reconcile_host_vv_repository.py --check` | `PASS` — 40 primary Host pages, 33 support layers (18 CLI, 15 SDK), 1,004 current procedure targets |
| `python3 -B scripts/verify_host_cli_commands.py --vast-cli <pinned-clean-checkout> --check` | `PASS` — 201 occurrences: 199 exact registrations and two intentional family references; zero actionable findings |
| CLI verifier focused unit suite | `PASS` — 7/7 schema-v2 and fail-closed cases |
| Host inventory, persona, named-anchor, OpenAPI, Volume/OpenAPI, and historical Self-Test generation checks | `PASS` within their declared static/source scopes |
| Loopback browser review | `PASS` for the corrected rendering and links on `/host/how-to-self-test` and `/host/vms`; no product/runtime status was inferred from rendering |
| `mint broken-links` | Exit `1`: known repository-wide baseline of 99 findings in 10 non-Host files; zero Host-page findings |
| `mint a11y` | Exit `1`: known shared dark-theme contrast plus 74 image findings in 19 non-Host files; zero page-local Host findings |

## Limitations and unresolved work

This record validates the reviewer interface, source/signature linkage,
topology, accounting, and retained-evidence binding. It does not validate
credentialed authentication, a successful Host self-test workload, full
support-bundle lifecycle, VM disablement, pricing, policy, contract, account,
or legal claims. It does not record Product, Finance, Legal, source-owner, or
human reviewer acceptance.

Unresolved operator/runtime prerequisites remain in
[`verification/runtime-operator-blockers.md`](../../runtime-operator-blockers.md).
Unresolved Product, Finance, Legal, and source-owner prerequisites remain in
[`verification/source-owner-blockers.md`](../../source-owner-blockers.md).

## Artifact identity boundary

This historical attempt records the repository-local observations completed at
`2026-09-03T20:27:25Z`. It intentionally does not claim hashes for files that
were changed afterwards. The final post-change artifact identities and retests
are retained in `EV-HOST-COMMAND-PROOF-REVIEWER-02`. This record does not embed
the final `verification/host-docs-test-results.json` hash.
