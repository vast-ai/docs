# RTX4090 readiness — retry 02

Mode: PLAN_AND_EXECUTE. This is an additive retry of [attempt 01](../2026-09-08-host-rtx4090-readiness-attempt-01/result.md), after the user explicitly said to retry and that the Host can be trusted. Target remains HOST-RTX4090-01, with the same target-binding digest. No historical record is overwritten.

## Authorized change and boundary

Accept a previously unknown SSH key for this exact user-specified target with `StrictHostKeyChecking=accept-new`, `UpdateHostKeys=no`, batch mode, no forwarding, no sudo, 30-second timeout. This user-authorized trust-on-first-use enrollment does not independently authenticate the key through a console fingerprint. Do not disable checking or accept a changed known key. Use `StrictHostKeyChecking=yes` for all subsequent requests. The authorized trust-store addition is the only intended configuration change.

Repeat the original read-only GPU query and standard-library inspection of CLI package/version/source identity and exact default credential-file presence/readability. Do not import/execute the Vast CLI during discovery: its import may create directories or migrate credential files. No recursive searches, secret values in output, or renter inspection.

If the installed CLI source confirms the configured key path, the previous user authorization allows reading that exact existing client key in memory and checking it against the source-derived official API. Do not assume it is a different account from the previously verified Host key. Use the same read-only API plan as attempt 01: identity, owned machines, selected-machine existing instances and exact-machine offer search. Source inspection and any added query/filter are recorded before execution; API observations do not prove exact CLI command execution.

No rental, self-test, privileged operation, workload command, stop/destroy, key rewrite, billing mutation, Git push or human acceptance. Any paid test still needs explicit target/offer/workload, spending/duration limits, monitoring and cleanup authorization. Mask private identifiers and secrets before retaining output.

## Expected outcomes and evidence

PASS applies only to successful SSH/GPU/CLI availability observations or exact bounded API observations. A denied/missing credential or scope blocks that suitable check; missing broader claim evidence remains UNVALIDATED. Retain timestamps, command or request method, selected fields, response/source digests, exit/HTTP status and limitations. Preserve attempt 01 and identify this attempt as a retry with user-authorized first-use trust, not an unexplained resolution of the old failure. The current claim/HTML snapshots remain unchanged until their own evidence-binding correction and retest.

The pre-edit repository state is in [baseline.json](baseline.json). The same agent executes and records the observations; any independent review does not substitute for runtime evidence.
