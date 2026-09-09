# Host Docs — client/Host unblocking follow-up

PR #185 / Jira CON-1518. 2026-09-08. **Safe read-only batch complete: ten more command claims supported, two documentation defects identified, and credential prerequisites clarified.** The Host docs are not acceptance-ready; remaining local corrections and external work are listed below.

## What we can now establish

- Both Keychain credentials authenticate to distinct accounts. No key value or account profile was retained. [Account observations](account-observations-01.json).
- The client can see the alternate Ada's offers using the documented troubleshooting filters: three selected-machine offers, 1/2/4 GPUs, rentable and not rented at the recorded instant. Host-account searches were also run in the exact documentation context. [CLI checks](cli-execution-01.json), [Host searches](host-search-execution-01.json).
- The VM helper is readable here. Its status-only branch was inspected before execution, and the installed hash was rechecked immediately before running it. It returned off; kaalia.cfg was unreadable, so **this does not prove VM support is disabled**. [Source](vm-helper-source-retest-02.json), [status query](vm-status-01.json).
- The isolated set-api-key fixture was written successfully, but file mode 0644 remains a separate security failure. No real key was saved by this test. [Limits](local-key-storage-limitations-02.json).

The follow-up contains 18 checks/inspections: three direct account/instance reads, eleven CLI reads/searches, one isolated fixture write, one VM-source readability check, one installed-source inspection and one hash-guarded VM status query. These are not 18 claims closed. The earlier [47-check batch](../2026-09-08-host-live-readonly-attempt-01/result.md) remains separate and unchanged.

## Current review impact

Current totals: **185 PASS, 4 editorial NOT_APPLICABLE, 151 FAIL, 22 BLOCKED, 1,643 UNVALIDATED** out of 2,005 claim occurrences. There are 1,816 unresolved occurrences, not 1,816 confirmed external blockers. [Exact delta](current-delta-01.json).

| Page / section | Newly supported occurrences | Bounded result |
|---|---:|---|
| [Market Metrics / CLI](http://127.0.0.1:4000/host/market-metrics#cli) | 3 | All 15 commands in the three blocks have canonical source and retained execution/output-shape proof. |
| [Fleet Operations](http://127.0.0.1:4000/host/fleet-operations) / Fleet State and Monitor | 2 | The raw Host-inventory command and its separate pull instruction. |
| [Not In Search / Check the machine directly](http://127.0.0.1:4000/host/not-in-search#check-the-machine-directly) | 4 | Host-context show-user and three exact documented offer searches. |
| [Maintenance Windows / Before Maintenance](http://127.0.0.1:4000/host/maintenance-windows#before-maintenance) | 1 | Both Host-inventory commands in the block, not maintenance itself. |

[Command adjudications](../../current-host-readonly-adjudications.json) preserve each full original claim. Source text, evidence lanes, roles, canonical provenance, every command and retained capture must match; edits to the reviewed registry require explicit code-pin review. The [new nine-occurrence map](check-to-claim-map.json) supplements the unchanged previous map with selected-check links and limitations. No workflow parent, support wrapper or owner claim inherits a command result.

Two self-test claims remain BLOCKED, but their current reasons no longer say the key is missing. Actual workload authorization, create permission, controlled runtime/window and cleanup authority remain absent. Authentication and read access do not establish those prerequisites.

Two confirmed local defects are now **FAIL**, with originals retained in the [exact findings](../../current-host-readonly-findings.json): the unconditional VM off interpretation and First 24 Hours' Host-inventory instruction in a client-discovery sequence. Their page wording has not been edited in this batch. Correct that wording, refresh its source bindings/static evidence in a new attempt, and retest; these are repository-local tasks, not external blockers. The existing mode-0644 CLI key-storage failure also remains open.

## Repository and reviewer verification

- Final full Python suite: 142 passed. Final current-review and HTML tests: 29 passed. The initial full JavaScript run also passed all 64 tests, including 35 unchanged legacy review-context tests. [Retest](repository-tests-retest-02.json).
- Root negative tests now reject missing command members, empty or trivial expected-output predicates, altered originals and stale key reasons. Initial failures remain linked. [Retest](root-gate-negative-retest-03.json), [failure history](implementation-failures-01.json).
- Persona checks cover all 44 pages; Volume OpenAPI/static CLI payload checks pass. These do not establish backend behavior. [Checks](local-static-checks-01.json).
- Every Host page has retained passage/status observations covering all 2,005 claims, with 19 explicit masked-text section fallbacks. The sweep passed 43 routes; Self-Test passed three later sequential page checks. **One intermittent localhost fetch failure remains unexplained**, so no blanket review-server stability PASS is claimed. Startup and overlapping-retry errors are also preserved. [Browser reconciliation](browser-reconciliation-01.json).
- The standalone report retains its offline page/claim filters, exact selected-check dialogs, source/passage links, desktop/mobile layout, and local-review setup instructions. Its final presentation retest is retained separately as `checks-03.json`; it is not embedded in the HTML to avoid a self-referential content hash.

Live CLI observations used the pinned source entry point on macOS, not a packaged CLI qualification on all operating systems. The installed VM helper check ran over SSH on the selected Linux Host; it is not Linux/Windows CLI coverage. The isolated fixture/cache were removed; no real key/config or remote resource was removed. [Fixture cleanup](local-fixture-cleanup-01.json).

## What remains outside this completed read-only scope

- [Runtime/operator register](runtime-operator-register.md): authorization, controlled runtime, create/privilege scopes and cleanup for any workload or resource-changing check.
- [Product/Finance/Legal/source-owner register](source-owner-register.md): backend authority, published policy/contract sources, and owner confirmations.

No rental or self-test was started. No instance was stopped/destroyed, no Host configuration changed, and no real CLI key/config was altered. No push, merge, Jira/PR post or human acceptance occurred. The occupied RTX4090 was excluded from Host operations.

[Plan](plan.md) · [baseline](baseline.json) · [canonical CLI source provenance](cli-source-provenance-01.json). Full API/profile/renter output is not retained; sanitized projections and original output digests state the limits.
