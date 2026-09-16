# Approved bandwidth-price retry and conditional client rental

Mode: PLAN_AND_EXECUTE. PR185 / CON-1518. Baseline.json records the exact tree,
index and current model before edits. Prior attempts remain immutable.

User authorization: try USD0.10/GB upload and download, or USD0.01/GB if required
to complete listing. These are two explicit allowed rates, not an arbitrary
range. Keep machine150296, GPU3/GPU-hour, min bid0.30/GPU-hour,
storage0.50/GB-month, disabled prepaid discounts, min_chunk1, vol_size0,
durationnull and fixed expiry1789423200 unchanged.

1. RETRY-01: inspect canonical listing contract and retain its identity; fresh
   strictly pinned read-only SSH and owned-machine API readiness. Stop on a
   changed host identity, new workload or incompatible state. No reboots.
2. RETRY-02: one guarded request with0.10 in both network fields; retain exact
   inputs/response and independent readback. If explicitly rejected for network
   price bounds and independently still unlisted, repeat as RETRY-03 at0.01 in
   a new rate-specific evidence directory. No fallback after an unknown response,
   partial listing or unrelated error. Reconcile first; never blind-retry.
3. RETRY-04: after successful exact-term readback, inspect the separate authorized
   client identity and machine-specific offer. No market fallback or other host.
   Establish cost, cached-image/traffic, SSH and cleanup prerequisites before rent.
4. RETRY-05: freeze exact claim/offer/image/command inventory before creation.
   At most one GPU,20minutes,USD5 all-in; only a tiny deterministic GPU check and
   this task-created instance's lifecycle if useful. Retain ownership, identity,
   output, timings and destroy/readback evidence. If bounds or cleanup cannot
   be ensured, do not rent. No full self-test, stress, speed, bulk transfer,
   packages, driver/daemon changes, reboot or customer interference.
5. RETRY-06: reconcile evidence, preserving both pricing failures and later
   retests; update reviewer4000, HTML and traceability with precise current
   outcome. Validate relevant model, source pins, controls, links and sanitation.
   Keep runtime/operator work separate from source-owner/commercial authority.

PASS requires suitable retained observations; FAIL is an observed mismatch;
UNVALIDATED is missing evidence; BLOCKED names a specific unavailable input,
permission, environment or authorization. API execution is not CLI invocation.
Price acceptance of a sample is not a universal pricing rule. Documentation
under review is not its own proof. No push, merge, Jira post or human acceptance.

The separate client key location may need recovery from prior task records;
do not dump Keychain contents or expose secrets. Use named entries only, secrets
in memory, restricted raw captures and public privacy-minimized projections.
