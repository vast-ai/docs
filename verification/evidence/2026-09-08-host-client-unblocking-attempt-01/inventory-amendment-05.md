# Amendment 05 — classify confirmed documentation defects

2026-09-08. Additive follow-up to the already retained read-only observations;
no additional Host/API action is authorized.

- FINDING-01: `/host/vms` / Check VM Status, `MCL-dfebca7edafe9c59`.
  Inspect the captured installed helper and retained VM status observation against
  the exact `off` meaning. Expected: no unconditional conclusion of disabled VM
  configuration when the helper masks configuration-read failure. Preserve the
  full original claim and classify the interpretation gap as a documentation
  FAIL; installed-artifact scope is not upstream source-owner provenance.
- FINDING-02: `/host/first-24-hours` / Test Like A Client,
  `MCL-323c8fb8180f5f62`. Compare the exact `show machines` instruction and its
  client-discovery context with pinned canonical CLI dispatch/API source.
  Expected: renter-offer discovery must not be represented by a Host-owned
  inventory command. Retain the source excerpt, full original claim, and FAIL
  rationale. Do not infer a renter workload result or promote a replacement.

These are FAIL-only current findings with exact source/evidence gates. They do
not edit the published wording in this pass or overwrite the static baseline.
Correction and new source/rendered retests remain explicit repository-local next
actions, separate from the two external workstreams.
