# User-requested read-only SSH retry

The user explicitly requested another connection attempt to the same supplied
Host and key. This is an unchanged retry of the [first attempt's check](../2026-09-08-host-h100-readonly-attempt-01/plan.md), not authorization to bypass a host-key warning or modify trust.

Target alias HOST-H100-01; private destination/key mapping remains in the user
message. Method: strict, noninteractive, single-identity SSH connection with
no forwarding or TTY, a 10-second connection timeout and 30-second overall bound.
If authenticated, execute only:

`nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader,nounits`

Expected: eight driver-visible H100 GPUs. PASS is bounded to that observation;
BLOCKED requires a concrete unavailable trust/authentication/connectivity
prerequisite; FAIL records a mismatch against an available check. No broad
claim promotion follows. No sudo, self-test, process/container inspection,
renter data, service changes, or new workloads are permitted. Stop on any
unknown/changed host key. Do not alter known_hosts.

Capture start/end times, sanitized command/options and output, SSH exit status
and a target-binding digest. Preserve attempt 01 unchanged. MCL-e12ac9f6be2ce502
and the HTML report are not reclassified merely because SSH access succeeds.

Pre-execution identity, 2026-09-08T14:03:33.650Z:

- HEAD bfa926c9421521767fa7411718bd31ea38b38528.
- Index SHA-256 f94031ce155dabaf4a0c8cf60f50f22c76d68a38209b3502ce535c93e157310b.
- Staged diff SHA-256 f59f3c12986c4a1750dbae920803828221b9f4d63b7104c5932e9b0ac5372803.
- Unstaged tracked diff empty.
- Current claim package SHA-256 24492ac5b4c3059478d311c6d99733ebadad37255d0e570295c17605ab42f031.
