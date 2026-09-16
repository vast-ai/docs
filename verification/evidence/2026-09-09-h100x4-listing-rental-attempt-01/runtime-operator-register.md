# Runtime/operator work — listing attempt 01

This register covers machine150296 only, not all outstanding Host Docs work.

## LR-03 — listing FAIL; LR-04/LR-06 — rental BLOCKED

The user-approved USD1/GB upload/download request was rejected with HTTP400
`price_out_of_bounds`. The independent owned-machine readback shows unlisted,
no listing prices and no running/resident rentals. No altered-price retry or
client rental was created. See [request](listing-request-01.json),
[response](listing-response-01.json), and [readback](host-read-after-01.json).

- Missing prerequisite: an API-accepted listing at explicitly user-approved prices.
- Responsible role: host owner for changed-price approval; authorized operator for a new guarded attempt.
- Impact: cannot select a valid offer, create a representative client instance, observe its lifecycle or retain its cleanup proof. Missing runtime claim evidence remains UNVALIDATED; the attempted listing check itself is FAIL.
- Next action: obtain revised upload/download price approval, without guessing that the server's reported bound0.1 is a valid input. Preserve GPU3, bid0.30, disk0.50, disabled discounts, min_chunk1, no extra volume offer, and fixed expiry1789423200. Recheck identity/occupancy, use a separately retained attempt, and verify all fields independently before renting.
- Conditional next stage: establish the separate client identity and exact offer/image/budget/cleanup contract before creating one GPU for at most20minutes and USD5. Never reuse or destroy another instance. No full self-test, stress test, bulk transfer or reboot is authorized by this bounded plan.

The [exact affected/proposed claim inventory](claim-impact-01.json) gives page,
heading, wording, spans, evidence types and unchanged current dispositions.
It is not runtime proof. LR-05's final rental inventory is not frozen because
there is no accepted offer to bind.

## Resolved attempt-local environment prerequisite

The default sandbox denied SSH before connection in [preflight01](preflight-01.json).
Approved scoped network access allowed [preflight02](preflight-02.json), with
[fresh preflight03](preflight-03.json) immediately before listing. All seven
readiness guards passed. This is not a remaining SSH/sudo blocker.

## Preserved earlier work

Earlier installation/helper warnings, stock-TUI coverage, independent public-self
connectivity, acceptance load/reboot and backup-access work are not completed by
this listing attempt. No machine repair, price reduction, reboot, customer-job
inspection, or change on other hosts was performed.
