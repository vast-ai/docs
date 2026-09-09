# RTX 6000 Ada — read-only readiness result

PR #185 / CON-1518. Captured 2026-09-08 at approximately 16:42:58 UTC.

## What was actually established

Two planned checks executed, two narrow PASS outcomes, no skipped checks. These are access/hardware readiness results, not Host documentation workflow acceptance.

- [Host API capture](api-01.json): HTTP 200 for the exact selected machine; four RTX 6000Ada GPUs. At this instant, all returned running/resident/reserved rental counters were zero, volume_rented_size was 0.0, listed was true, and verification was unverified.
- [SSH capture](ssh-01.json): existing trusted-key login succeeded without changing known_hosts. Four NVIDIA RTX 6000 Ada Generation GPUs were reported, with Linux kernel 6.8.0-138-generic.
- Both captures bind to the target pair declared in [the pre-execution plan](plan.md) through the same SHA-256. Matching GPU models/counts corroborates the user-supplied mapping but does not independently prove unique physical identity.

The machine is a candidate for a separately approved test, not reserved or guaranteed idle. It remains publicly listed. Read-only API and SSH commands made no workload/configuration changes.

## Interpretation and limitations

The canonical CLI revision 18c4f2ccd6da587d5352f8741c71805a9a18e1ae passes Host machine API responses through (vastai/api/machines.py:15-17 and 29-31); vastai/cli/display.py:242 displays gpu_occupancy without defining it. A separate source reviewer found no backend definitions of the named rental counters in that checkout. Therefore this record reports their literal values and does not certify their freshness, underlying semantics, or future exclusivity. The observed occupancy string is retained but not decoded.

This is not a GPU health test, self-test run, rental, client account ownership test, WAN check, storage safety certification, or proof that a renter workload completed. No existing Host-docs claim or procedure status is promoted. No source-owner or Product/Finance/Legal authority was invented.

## Exact next gates

1. Before any test capable of using resources, reconfirm the exact target and repeat occupancy; stop if a new rental or storage/reservation obligation is present. An observation does not reserve a listed machine.
2. Before paid work, obtain explicit maximum total spend, duration, intended workload/offer scope, and authority to stop/destroy only the instance created for this test. Do not delete, stop, unlist, or reconfigure existing customer resources.
3. Unique API-to-SSH machine binding remains unvalidated beyond the user mapping plus model/count consistency; strengthen it with an approved non-secret identity binding before workload operations.
4. RTX 4090 machine from the previous check remains excluded because it had a running rental. No command in this attempt touched it.

## Provenance and history

[Baseline](baseline.json) records pre-edit HEAD, branch, status, exact staged/unstaged diff SHA-256 and index SHA-256. Existing history is unchanged. The initial baseline collector failed before validation and is described in the plan; the successful retry precedes both live checks.

Captures were produced and checked by the main agent. An independent, read-only source review informed the limitations above, not the live outcomes. Secrets were consumed in memory and not printed or retained. API body and SSH output digests are retained alongside minimal sanitized projections; full API/profile/renter data is not retained.

No rental was created, no self-test run, no instance stopped/destroyed, no host configuration changed, and no push/merge/publication occurred.

