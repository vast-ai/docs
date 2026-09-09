# Independent launch-safety review and correction

The read-only reviewer found that the preflight preceded the final quote and
watchdog setup. Before execution, add another full Host/API + strictly pinned
SSH idle check after those steps, then a final exact owned-machine zero-running/
zero-resident API read immediately before create. Any failure prevents dispatch.

This minimizes but cannot eliminate the marketplace race: the publicly listed
host is not reserved. Do not claim an atomic lock or change the listing without
authority. Ongoing customer-arrival guards stop and clean up only this task's
instance; no customer instance is touched. Quote and final read timestamps are
retained so a reviewer can see the actual interval.

Reviewer confirmed source-level single dispatch at retry1, pre-armed independent
watchdog, exact owned id/machine/GPU/label cleanup, uncertain-create reconciliation
against the baseline, and independent absence readback. Root inspected those
paths and ran 12 local safety predicates; those tests are not live cleanup proof.
