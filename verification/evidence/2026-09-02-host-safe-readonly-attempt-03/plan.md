# Host safe read-only procedure verification plan, attempt 03

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SAFE-READONLY-03`
- Method: authorized Host, bounded read-only command-carrier observation
- Canonical test-set SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- Execution limit: four command carriers, each under a 25-second remote timeout

## Safety and retention boundary

Use the already authorized noninteractive Host transport with no TTY, a bounded
connection timeout, and strict host-key checking. Retain raw stdout and stderr
only in the restricted evidence directory outside Git. The public result may
retain command IDs, exits, line and byte counts, hashes, and sanitized structural
observations. It must not publish infrastructure, account, network, device,
workload, renter, or credential data.

Stop on an authentication prompt, timeout, or unexpected side effect. Do not
install, restart, reconfigure, rent, delete, open a listener, create a container,
load a GPU, or inspect renter files.

## Frozen command-carrier set

| Order | Command carrier | Page procedure | Exact documented command | Expected bounded observable | Maximum claim |
| --- | --- | --- | --- | --- | --- |
| 1 | `CLM-d31f5b78bbf99242` | `DIA-E01`, Host Diagnostics log evidence | `sudo tail -n 100 /var/lib/vastai_kaalia/kaalia.log` | Exit and no more than 100 current daemon-log lines | The bounded read form and documented path work on the current Host. No incident diagnosis is proved. |
| 2 | `CLM-155ca5dc04aaf9d9` | `POL-E01`, renter-report Host-side evidence | `sudo tail -n 100 /var/lib/vastai_kaalia/kaalia.log` | Exit and no more than 100 current daemon-log lines | The bounded read form and documented path work on the current Host. No renter report or correlation is proved. |
| 3 | `CLM-9604a1e76cf3ec21` | `MNT-E01`, post-maintenance GPU visibility | `nvidia-smi` | Exit and current GPU visibility output | The query works and reports current GPU visibility. No maintenance sequence, Docker GPU access, or self-test is proved. |
| 4 | `CLM-7cac63760e51f4d0` | `STR-C02`, `nccl_failed` first check | `nvidia-smi` | Exit and current GPU visibility output | The query works and reports current GPU visibility. No NCCL failure, container behavior, or root cause is proved. |

## Promotion rule

A clean result may change only the four named command carriers from
`UNVALIDATED` to `PASS`. All four retain semantic score 2 and a
`DIRECT_FUNCTIONAL_PARTIAL` ceiling. No owning step, branch, test set, or page
may be promoted from this attempt.
