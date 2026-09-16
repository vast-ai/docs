# RTX 6000 Ada readiness — plan and inventory

Recorded 2026-09-08 before execution. Scope: user-supplied alternative machine 149198 at 10.0.100.86; preserve and do not operate on occupied RTX 4090 machine 149229. This is readiness evidence, not proof of a Host docs workflow or a paid qualification.

Authority: user's explicit SSH target and previous Host-key read-only authorization. No new paid, privileged, mutating, destructive, or workload operations are authorized. Host API key is read from the named Keychain entry into memory only. Never retain keys, account/profile details, public network addresses, renter contents, or unrelated machines.

## Frozen checks

- ADA-01: Direct GET /api/v0/machines/<selected-machine>/?owner=me, using the established canonical Host endpoint. Retain timestamp, HTTP status, exact selected-machine match, GPU model/count, scalar occupancy counters, and listed/verification state. PASS establishes only response access and expected hardware metadata; any nonzero rentals/resident/reserved/volume counters prevent an idle-candidate conclusion. Absence is unknown, not zero.
- ADA-02: SSH with existing identity, BatchMode=yes, StrictHostKeyChecking=yes, UpdateHostKeys=no, ConnectTimeout=10. Run only `id -un`, `uname -s`, `uname -r`, and `nvidia-smi --query-gpu=name --format=csv,noheader`. Retain command, timestamps, exits, GPU names and OS/kernel. No password prompt, unknown-key trust, sudo, containers, process inspection, or benchmarks. PASS is limited to SSH reachability and model/count consistency; matching GPU models is not unique proof that the SSH endpoint and API machine are the same physical machine.

## Results and safety interpretation

Unknown or changed SSH host key, connection error, or missing permission -> BLOCKED for that check with concrete prerequisite. API access error -> BLOCKED, not a product defect. Confirmed target/hardware mismatch -> FAIL target precondition. No future rental/self-test may proceed based solely on these snapshots: repeat occupancy immediately before an authorized run, protect existing/stored workloads, agree budget/duration/workload and exact cleanup ownership. A non-mutating check cannot reserve the host against new rentals.

Retain sanitized outputs and full-output SHA-256 where applicable. No current claim status is promoted, no historical attempt is replaced, and no push/merge/post is performed. The main agent produces and verifies the capture; a parallel reviewer inspects occupancy interpretation separately.

## Local preparation attempt history

The first baseline collector did not return parseable JSON; the tool wrapper failed with Unexpected token '<'. No validation had run and no files were written. The retry explicitly raises the child-process output buffer for the existing large git diffs. Do not treat the failed collector as a completed baseline.

