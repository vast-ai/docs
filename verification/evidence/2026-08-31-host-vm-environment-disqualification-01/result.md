# Host VM evidence qualification correction — attempt 01

## Decision and authority

- Recorded: `2026-08-31T14:10:00Z`
- Scope: VM helper commands on `/host/vms`
- Authority: the Host owner/operator confirmed that the target's VM/IOMMU setup was improper and will correct it before retesting.
- Execution in this attempt: none; this is an evidence-qualification review.
- Predecessor observations: [`../2026-08-30-host-readonly-attempt-03/result.md`](../2026-08-30-host-readonly-attempt-03/result.md) and [`../2026-08-31-host-privileged-attempt-01/result.md`](../2026-08-31-host-privileged-attempt-01/result.md)

## Current qualification

The earlier shell invocations and outputs remain valid observations of what the improperly configured target did. They are **not representative acceptance tests** of the documented VM procedures. They cannot support `PASS` or establish a command defect.

| Stable command | Retained observation | Current V&V status | Semantic/functional score |
| --- | --- | --- | --- |
| `CLM-ca44522b22c4c5ee` — `check` | Printed `pending` before the attempt and `off` afterwards. | `UNVALIDATED` | `UNSCORED` |
| `CLM-9cba75bbdc780804` — `off` | Returned exit `0`; a later check printed `off`. | `UNVALIDATED` | `UNSCORED` |
| `CLM-ffda5e2c291c470e` — `on -f` | Printed the IOMMU-group abort, returned exit `0`, and left status `off`. | `UNVALIDATED` | `UNSCORED` |

No 1–3 score is assigned because the commands have not been tested in a representative environment. A score is prohibited until a claim-suitable retest succeeds on the repaired Host.

The Docker runtime diagnostic from the same privileged session is outside this correction and remains qualified by its own evidence.

## Retest entry criteria

Do not promote any of the three VM commands until a new linked attempt records all of the following:

1. BIOS and kernel IOMMU settings are corrected, the Host has rebooted, and expected IOMMU groups are directly observed.
2. New rentals are prevented for the maintenance window; control-plane rental counters, containers, and GPU processes are all zero immediately before mutation.
3. The intended starting VM state is recorded.
4. The exact documented `check`, `off`, follow-up `check`, `on -f`, and final `check` sequence is run without substituting hidden file edits.
5. Exit status, sanitized output, final VM state, expected GPU visibility, Vast/Docker service health, and cleanup are retained.
6. Only `off` after disablement and `on` after enablement, with healthy GPUs/services and no abort/error output, may qualify the corresponding procedure.

Until then, the accurate reviewer-facing statement is: **the VM commands were attempted on an improperly configured Host, but they have not yet been acceptance-tested and remain unscored.**
