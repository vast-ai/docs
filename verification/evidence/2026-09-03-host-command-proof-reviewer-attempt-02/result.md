# Host command-proof reviewer post-final-change retest — attempt 02

- Attempt: `ATTEMPT-2026-09-03-HOST-COMMAND-PROOF-REVIEWER-02`
- Evidence: `EV-HOST-COMMAND-PROOF-REVIEWER-02`
- Jira / pull request: `CON-1518` / Host Docs PR #185
- Pages: `/host/how-to-self-test` and `/host/vms`
- Exact command bindings: 5
- Supporting reference layers: 33 support layers (18 CLI, 15 SDK)
- Method: `STATIC_COMMAND_PROOF_REVIEWER_POST_CHANGE_RETEST`
- Outcome: `PASS` for the bounded repository-local reviewer and evidence-registration contract only
- Completed: `2026-09-03T21:01:48Z`
- Credentialed Host/API, paid, WAN, privileged, mutating, destructive, or
  workload-affecting operation: none

## Relationship to attempt 01

`EV-HOST-COMMAND-PROOF-REVIEWER-01` remains the historical initial reviewer
attempt completed at `2026-09-03T20:27:25Z`. It does not qualify bytes changed
after that boundary. This second attempt covers the later source/runtime
presentation warning, VM read-only access-classification correction, concrete
support-bundle action, final evidence-lane contracts, and formal evidence
registration.

Neither attempt is command-runtime proof. Their attempt and artifact-manifest
registrations make the retained reviewer history discoverable without adding
them to the status-bearing procedure evidence. They do not replace the current
source-signature or runtime evidence for those commands and do not change any
status or rollup.

## Final command-contract corrections

- `CLM-3ba3b25f5c3ddac1` remains `UNVALIDATED`. Its pinned CLI signature is
  independently `PASS`, so its missing procedure evidence is now explicitly
  `RUNTIME_OR_UI_OBSERVATION`, not another repository-static check. The exact
  next action requires the default form without `--support-bundle-dir` on an
  authorized representative idle listed Host, with revisions, target IDs,
  terminal result, lifecycle, and cleanup retained.
- `CLM-9cba75bbdc780804` remains `UNVALIDATED`. Its contract now requires both
  `CANONICAL_IMPLEMENTATION_SOURCE` and `RUNTIME_OR_UI_OBSERVATION`. The exact
  next action requires immutable helper-source binding and an authorized,
  representative, idle, unlisted VM-capable Host that begins enabled, with the
  controlled `check → off → check → on -f → check` sequence and safe restoration
  evidence.
- `CLM-3fa5d5948b34fc6a` remains `BLOCKED`; its next action now names the exact
  Host-owner capability and exact retained artifacts instead of exposing an
  internal `unavailable_prerequisite.components` instruction.
- The exact VM `check` carrier remains the only bounded runtime `PASS` among the
  VM examples. Its no-`sudo` documented form is classified independently from
  the privileged VM `off` form without claiming that every Host filesystem
  grants every unprivileged user access to the helper.

## Preserved failure and retest chronology

| Stage | Preserved result | Correction and retest |
|---|---|---|
| Initial topology-aware reviewer integration | `10/24`; strict loading rejected the incomplete V&V scope reconciliation | Added the exact topology-correction structure and bindings; the later reviewer replay reached `24/24`. |
| Initial aggregate replay | `21/24`; one limitation expectation, accounting classification, and aggregate totals were stale | Corrected only those expectations and retained the later `24/24` result. |
| Focused independent reviewer assertions | `2/4`; the VM-history assertion was overbroad and one accounting-only evidence record was misclassified | Narrowed the VM-history assertion and classified the reconciliation record as accounting-only; unchanged focused replay passed `4/4`. |
| Full reviewer replay after the focused correction | `17/24`; the test fixture omitted the required generated CLI-signature artifact | Supplied the exact schema-v2 CLI artifact in the fixture; the next full replay advanced to `23/24`. |
| Full reviewer replay with the CLI artifact | `23/24`; the new exact PAGE evidence-binding expectation was absent | Added the exact PAGE binding expectation; the unchanged full replay passed `24/24`. |
| Source/runtime revision audit | The proof card did not foreground that pinned source and runtime evidence can describe different builds | Added the pinned revision and separate-build warning; full reviewer replay passed `24/24`. |
| VM access-classification audit | The exact no-`sudo`, read-only VM `check` form inherited a root label from its `/var/lib/` path | Narrowed only that exact static classification; Python replay passed `96/96`, while VM `off` remained Host-root. |
| Support-bundle action audit | The generated next action exposed the internal `unavailable_prerequisite.components` field | Replaced it with the exact missing Host-owner capability and retained-artifact list; focused/full reconciler checks passed `3/3` and `41/41`, and reviewer checks passed `24/24`. |
| Final evidence-lane audit | Plain self-test requested another static check and VM off requested only source evidence | Set runtime-only for plain self-test and source-plus-runtime with restoration for VM off; focused/full reconciler checks passed `3/3` and `41/41`, and reviewer checks passed `24/24`. |
| Initial formal-registration focused replay | `3/4`; the new presentation-only reviewer record was swept into the historical Self-Test relocation population | Excluded only the two reviewer presentation IDs from historical rekeying and current evidence selection; the unchanged focused replay passed `4/4`. |
| First strict reviewer replay with status-bearing registration | `23/24`; adding two procedure-result rows changed the retained status-evidence count from 96 to 98 | Registered the reviewer records only as retained attempts plus hash-bound manifest artifacts, removed their status-bearing procedure rows, and preserved the 96-record proof set; the unchanged reviewer replay passed `24/24`. |
| Focused registration command replay | `3/4`; one requested unittest selector named a method that does not exist | Reissued the same four focused checks with the exact current method name; the replay passed `4/4`. This was an invocation error, not a product or evidence-status result. |

Every failed replay above remains part of the chronology. No failed result was
rewritten as a pass, and no runtime or owner evidence was inferred from these
repository-local corrections.

## Final registration replay

| Check | Retained result |
|---|---|
| Four focused topology, contract, and registration regressions | `PASS` — `4/4` |
| Full reconciler unit suite | `PASS` — `42/42` |
| Full repository Python unit discovery | `PASS` — `97/97` |
| Strict review-context suite | `PASS` — `24/24`; retained status-evidence count remained 96 |
| Deterministic reconciler check | `PASS` — 40 primary Host pages, 33 support layers (18 CLI, 15 SDK), 1,004 targets |

The final results contain 57 retained attempts, 56 unique attempt-artifact
references, and 42 status-bearing procedure results. The two reviewer records
are present once each in `attempts` and once each in the artifact manifest, but
are absent from the current-status projection, command scores, direct-proof
ceilings, material-claim results, support-layer results, and procedure results.
That separation makes the reviewer history durable without letting it prove
the commands it describes.

## Independent artifact identities

| Artifact | SHA-256 |
|---|---|
| `review-server.mjs` | `b72c5729361b6669f0d645238ff143bef11752fbbb9a807bd97f5b03ba84c575` |
| `scripts/review-context.test.mjs` | `5e7516427000beb330fe3129af555f417d0549be1b23a531e46dc4963c013c48` |
| `scripts/reconcile_host_vv_repository.py` | `e8fe7cf9ed907ac56c577251555733c6f3b554d2abe822c67c374f30262fa675` |
| `scripts/test_reconcile_host_vv_repository.py` | `bc6f97804a2f177a1c9ac59a439e59e317205bbdc9fc8dfe7148cba9c74d35e9` |
| `host-docs-cli-command-check.json` | `0a26455debd3d436720aee8ad3344d40475cab5b8d436afd0c17bab07c4c800c` |
| `host-docs-command-access.json` | `6911d69e2f4e59af4d28f2f7282c89a7eb849b709e3352a3be061eb638c8a626` |
| `host-docs-verification-inventory.json` | `c59ffc1b36628064168e71111eb203d289a8b73176b552feb0f8dd7d2292044b` |
| `verification/host-docs-test-sets.json` | `8beb017b5f69e19223e0fa5ecf31493ac62e97ccc11a1dca3125554d4f3ceda0` |
| `verification/host-docs-command-scores.json` | `1a946937050febbd483b97aab6889ef811507c081f2ac038205621980b1bffb5` |
| `verification/evidence/2026-09-03-host-command-proof-reviewer-attempt-01/result.md` | `b9059c441223623705755eda3b83f78099dba625704baf66c07c3f840783d793` |

## Limitations and unresolved work

This evidence validates only the current repository-local reviewer interface,
source/signature linkage, evidence navigation, evidence-lane wording, strict
schema loading, and retained-attempt/manifest registration. It does not validate
credentialed authentication, a successful Host self-test workload, full
support-bundle lifecycle, VM disablement, pricing, policy, contract, account,
legal meaning, or human acceptance.

The final artifact table intentionally omits
`verification/host-docs-test-results.json` and this evidence file. Including
either would create or invite a self-referential hash cycle because the results
manifest stores this evidence file's digest.
