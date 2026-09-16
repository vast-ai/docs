# Host H100 read-only retry — successful observation

The user-requested unchanged retry completed at 2026-09-08T14:04:02.558Z.
SSH accepted the connection with StrictHostKeyChecking=yes, and the single
read-only GPU query exited 0 with empty stderr.

- Reported GPUs: **8 × NVIDIA H100 PCIe**, indices 0–7.
- Reported NVIDIA driver: **595.71.05**, on all eight rows.
- Result: PASS for this single connectivity/GPU-inventory observation only.

See the [sanitized execution record](execution.json) for exact command/options,
timestamps, target-binding digest and output, and the [plan](plan.md) for scope.

The [earlier host-key failure](../2026-09-08-host-h100-readonly-attempt-01/result.md)
is preserved. No agent action changed known_hosts, server keys or trust settings.
Strict checking succeeded on this attempt, but the cause of the changed trust or
endpoint state between attempts was not independently established. This record
does not claim that a trust issue was diagnosed/remediated or that access is
reliably available over time.

This observation establishes driver-visible GPU inventory at the user-selected
SSH destination. It does not independently establish marketplace account
ownership, correspondence with a specific listing, public search visibility,
idle state, renter execution, verification status, or GPU health/performance.

MCL-e12ac9f6be2ce502 and its HTML presentation remain unchanged / UNVALIDATED.
Its high-level product-description source binding is separate documentation
work; this result must not be used as proof that renters ran workloads.

No sudo, self-test, benchmark, container/process inspection, renter-data access,
storage/service/workload change, API call, paid operation, push or acceptance
occurred. The SSH process exited; no interactive session was left running.

Record check: exact eight sequential GPU indices, H100 PCIe model on all rows,
driver versions, exit 0 and empty stderr were checked against the frozen
expectation before writing this result. The same agent ran and checked the query;
this is not human acceptance.

An additional local record-validation one-liner initially had an extra closing
parenthesis and failed before executing any check. The corrected read-only
one-liner passed, confirmed the record fields, and confirmed that the current
claim-package and Git index hashes are unchanged. No additional SSH command
was run for that local verifier correction.
