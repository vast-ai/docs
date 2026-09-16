# Host safe read-only follow-up verification, attempt 02

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SAFE-READONLY-02`
- Target: restricted alias `HOST_VV_TARGET`
- Transport: restricted alias `HOST_VV_SSH`
- Planned at: `2026-09-02T14:38:22Z`
- Repository HEAD: `3b7e56f0db6588953589e0692e75b7274526d5f9`
- Test-set SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- Execution class: authorized Host, bounded privileged read-only

## Purpose

Close two remaining read-only questions that the first six-carrier batch does not answer:
capture the exact first-day service/log/range carrier with current root access, and determine
whether the VM helper's previously disqualified environment is now suitable for a new check.

## Safety boundary

- Apply the same noninteractive SSH, 30-second remote timeout, restricted raw-output, and
  sanitization rules as attempt 01.
- Do not restart or repair a service in response to any observation.
- Do not run `enable_vms.py off` or `on -f`, change BIOS/kernel/IOMMU state, or create a VM.
- Do not infer 24-hour stability from one snapshot or VM readiness from process exit alone.

## Frozen groups

### 1. First-day current snapshot

- `CLM-595e1c8f67f5692f`: exact documented service active/status, bounded Vast and metrics
  journals, bounded Kaalia log, and configured range reads.

Expected: every component returns a bounded current observation or a retained nonzero exit.
The carrier may support snapshot collection but cannot by itself prove 24-hour stability.

### 2. VM readiness and exact helper check

- Preflight only: count current IOMMU groups and record whether the helper exists; do not
  publish boot arguments or hardware identifiers.
- `CLM-ca44522b22c4c5ee`: `python3 /var/lib/vastai_kaalia/enable_vms.py check`.

Expected: exact output and exit are retained. Promotion is permitted only if the current Host
is demonstrably representative of the documented VM prerequisite and the output supports the
documented state meaning. Otherwise the prior environment blocker remains.

## Outcome rules

- Preserve each component exit; final group exit may not hide an earlier failure.
- A current snapshot can support command-level functional PASS with semantic score 2 while
  the first-day procedure remains blocked on duration and external behavior.
- A VM helper exit of zero is not sufficient. Unknown text, abort text, or an unrepaired
  prerequisite remains UNVALIDATED or BLOCKED and must not trigger corrective mutation.
