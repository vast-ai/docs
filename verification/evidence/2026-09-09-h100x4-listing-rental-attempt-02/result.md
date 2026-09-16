# H100×4 listing and bounded client rental — September 9, 2026

PR185 / CON-1518. This completes the authorized listing and one small client
GPU run, not all Host Docs V&V or host acceptance. No push, merge, Jira post,
reboot or human acceptance was performed.

## Live outcome

- **Machine 150296 remains publicly listed.** USD 0.10/GB upload/download was
  rejected; the explicitly approved fallback **USD 0.01/GB each** succeeded.
  The earlier USD 1/GB failure is also preserved.
- Independent Host readback at **08:56:03 UTC** matches GPU **USD 3/GPU-hour**,
  minimum bid **USD 0.30/GPU-hour**, storage **USD 0.50/GB-month**, zero prepaid
  discounts, one-GPU minimum, no separate volume offer, and fixed expiry
  **1789423200** (September 15, 00:00 South Africa time). It shows zero running
  and resident rentals at that instant; customers may arrive later.
- A separately authenticated client created **instance 50364501**, one H100
  on machine 150296 from the freshly checked offer **50363390**. The retained
  args-mode container returned CUDA available, one NVIDIA H100 PCIe, unique
  nonce, and sum of squares **1240.0**. It was then **destroyed**, with owner GET
  absence and an independent owned-instance-list check. The pre-armed watchdog
  observed verified cleanup and exited without a second deletion.

### Direct proof

1. [Failed USD 0.10 request](rate-010/listing-response-01.json),
   [successful request](rate-001/listing-request-01.json),
   [accepted response](rate-001/listing-response-01.json),
   [matched listing terms](rate-001/listing-readback-verification-01.json).
2. [Fresh client offer](rental-run-03/rental-fresh-offer-01.json),
   [create request](rental-run-03/rental-create-request-01.json),
   [create response](rental-run-03/rental-create-response-01.json),
   [independent running-instance read](rental-run-03/instance-read-03.json).
3. [Actual GPU result](rental-run-03/gpu-result-01.json),
   [Host occupancy during the run](rental-run-03/host-during-rental-01.json),
   [exact deletion and independent absence](rental-run-03/cleanup-main.json),
   [finished watchdog](rental-run-03/watchdog-finished.json),
   [final Host readback](rate-001/host-read-09.json).

The client quote was approximately USD 4.0093/hour including 10 GB storage.
The instance lifecycle was about 46 seconds. The immediate account-wide credit
delta was zero, but this is **not settled or attributable billing** and does not
mean the rental was free. The USD 5/20-minute limits were operational safeguards,
not a Vast-enforced spending/TTL cap. Only one instance was created and removed.

## Exact client-facing claim impact

All four occurrences are on `/host/first-24-hours`; page SHA-256
`3ab83e7558387edc07416aa84c4cf8e5721f1312a4c94f3841c1af4ecd8cf970`.
The required lane is retained runtime/UI observation. The responsible evidence
collector is the authorized Host/client operator, not a Product/Finance/Legal
authority. Canonical CLI/API source identity is retained in the request records;
the actual operation used direct API calls, not the displayed CLI command.

| Exact section / passage | Current result and bounded evidence | Remaining action |
| --- | --- | --- |
| Monitor, line 44: machine visibility and active offers — MCL-fabfbad844e625b4 | PASS: successful listing, independent Host readback and client offer search. | Retest after source/offer changes. No broad ranking or future-availability claim. |
| Test Like A Client, line 63: create from one available offer — MCL-7d10fc61bf9a884b | PASS: exact fresh offer, create acknowledgement and independently observed contract. | Retest this chain when changed. The following CLI/Jupyter command is separately unvalidated. |
| Test Like A Client, line 71: instance appears in client account — MCL-92edb99129fc96c9 | PASS: independent owner-scoped read matches exact contract, host, one GPU and label. | No inference about other accounts or rentals. |
| Test Like A Client, line 76: destroy, plus conditional SSH/Jupyter troubleshooting — MCL-da591d84b7d08317 | UNVALIDATED with partial cleanup proof: exact owned contract destroyed and absent. SSH/Jupyter condition was not exercised. | Obtain suitable source or separately authorized evidence for that conditional guidance. Do not promote the whole paragraph from deletion alone. |

The [strict adjudication registry](../../current-h100x4-rental-adjudications.json)
pins original claims, exact source spans, ordered per-claim proof artifacts and
their digests. [Exact delta](claim-impact-02.json): three new PASS statuses,
one partial-proof update, **2,001 other claims unchanged**. Totals: **192 PASS,
151 FAIL, 22 BLOCKED, 4 N/A, 1,636 UNVALIDATED**, across 44 primary pages and
33 central-reference support layers. No whole-page PASS is inferred.

## Repository verification and history

The exact starting tree/index is in [baseline](baseline.json). Original live
rejections, pre-create guard failures, rejected adjudication and interface
integration failures remain linked in the [correction log](correction-log.md).
Focused adjudication (8 tests) and current-model Python suites (50 tests) passed.
The [final reviewer suite](reviewer-tests-03.json) passes **75/75**; the earlier
62/73 result remains a failed integration attempt. [Affected-page controls](page-controls-03.json)
pass **84/84**. Final [installation-context browser checks](intake-browser-04.json)
pass 109 links; [rental-proof browser checks](rental-browser-05.json) pass 19 links,
all four exact passages and the three-PASS/one-partial statuses in both views.
Wrong-claim binding is rejected. The final sidebar-date correction separately
passes [15 HTML tests](html-tests-04.json). The HTML embeds **170 files**, makes
zero network-resource requests offline, and labels privacy-masked copies.
Screenshots were inspected; there is no horizontal overflow. The
[integrity seal](final-integrity-01.json) records final hashes and verifies all
98 previously sealed artifacts, unchanged staged diff and HEAD. Only the two
task-created worktrees were removed after complete recoverable archival and
readback verification; [archive receipts](worker-archives-01.json) retain hashes.

The optional knowledge-graph update refused a smaller replacement (8,511 versus
8,667 nodes); existing graph content was not force-overwritten. This remains
repository maintenance, not a Host-operation blocker or evidence of failed rental.

## Work not completed by this run

Keep [runtime/operator work](runtime-operator-register.md) separate from
[Product, Finance, Legal and source-owner confirmation](source-owner-register.md).
This run does not establish SSH/Jupyter, external/public-self networking, full
self-test or support bundles, performance/stability, stock TUI/standard/fallback
installer behavior, reboot persistence, backup access or settled billing.
Missing evidence stays UNVALIDATED; BLOCKED requires a concrete unavailable
prerequisite. No additional host work is authorized by this result document.
