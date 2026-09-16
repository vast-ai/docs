# Host diagnostic direct-binding reconciliation — attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-HOST-DIAGNOSTIC-DIRECT-BINDING-RECONCILIATION-01`
- Evidence ID: `EV-HOST-DIAGNOSTIC-DIRECT-BINDING-RECONCILIATION-01`
- Method: append-only retained-evidence traceability audit
- Canonical test-set SHA-256:
  `83e9c2de4fbd5be08209186ffaed13600eac70eb120407c48f2300ccf12543f5`
- New Host execution: none
- New command-result records: none
- Parent promotions: none

## Purpose

Six current command-level `PASS` / score-2 assessments were supported by retained
observations, but their score records did not name direct evidence. This audit closes
that traceability gap without changing a command disposition, semantic score, parent
status, historical attempt, or recorded exit.

## Retained sources

The reconciliation inspected these existing public records:

- `EV-DIAG-READONLY-01`,
  `verification/evidence/2026-09-01-host-diagnostics-readonly-attempt-01/result.md`,
  SHA-256 `a0a51c3f0f5d4dfc773b22a8fc6fe8d63dd831e6ec794ab1f351f1f518a92483`;
- `EV-HOST-INSTALL-NVIDIA-SMI-RETAINED-01`,
  `verification/evidence/2026-09-02-host-install-nvidia-smi-retained-01/result.md`,
  SHA-256 `6b8a583b74323bb312c2509190a614cd601eec16391e9582df188aa07ae3bacc`.

The first record directly reports the exact current-boot kernel-journal and `dmesg`
grep behavior, including the no-match exit from `dmesg`, and the exact
`nvidia-smi -L` behavior. It does not explicitly report a plain `nvidia-smi`
invocation. The second record directly reports an exact plain `nvidia-smi`
invocation and affirmative eight-GPU output, while explicitly declining to invent a
nested numeric exit code.

## Command-level mappings

| Command carrier | Exact bounded behavior supported | Retained source | Result |
| --- | --- | --- | --- |
| `CLM-ae94a456c56a5bdb` | Current-boot kernel-journal grep plus `dmesg` grep collection | `EV-DIAG-READONLY-01` | `PASS`, score 2 retained |
| `CLM-0bae256f5a9e7bc7` | Current-boot kernel-journal grep plus `dmesg` grep collection | `EV-DIAG-READONLY-01` | `PASS`, score 2 retained |
| `CLM-9e9b545d694a34cc` | `nvidia-smi -L` GPU inventory collection | `EV-DIAG-READONLY-01` | `PASS`, score 2 retained |
| `CLM-a86c033f7e767f31` | Plain `nvidia-smi` GPU visibility collection | `EV-HOST-INSTALL-NVIDIA-SMI-RETAINED-01` | `PASS`, score 2 retained |
| `CLM-6ddedf5cc9aced91` | Plain `nvidia-smi` GPU visibility collection | `EV-HOST-INSTALL-NVIDIA-SMI-RETAINED-01` | `PASS`, score 2 retained |
| `CLM-a71cddd213a49f46` | Plain `nvidia-smi` GPU visibility collection | `EV-HOST-INSTALL-NVIDIA-SMI-RETAINED-01` | `PASS`, score 2 retained |

The formal proof ceiling for this reconciliation is
`DIRECT_FUNCTIONAL_PARTIAL`. The mapping proves only that each bounded collection
carrier produced relevant output on the retained representative system. It does not
establish the surrounding symptom, incident-time correlation, failure branch,
repair, container/load behavior, or external boundary.

## Host-attempt counter reconciliation

The top-level Host counters use these explicit conventions:

- `host_attempts_executed` counts an attempt only when it issued one or more commands
  on the authorized Host. Local static checks, control-plane-only calls, and audits of
  retained records are excluded. Sixteen attempts meet that definition: Host read-only
  attempt 03; Host privileged attempt 01; Hardware Prep attempts 01 and 02; diagnostics
  read-only attempt 01; safe read-only attempts 01–03; Host self-test attempt 01; GPU
  injection attempts 01–03; installer-log attempt 01; self-test-log-follow attempt 01;
  Host-local-bundle attempt 01; and kernel-log-follow attempt 01.
- `host_attempts_blocked` counts Host-targeting attempts that ended at a recorded
  blocker, whether the blocker prevented Host execution or stopped an attempted Host
  procedure. Four attempts meet that definition: Host read-only attempts 01 and 02,
  Host self-test attempt 01, and Host-local-bundle attempt 01.

This reconciliation itself is a retained-evidence audit, so it increments the overall
attempt count but neither Host counter.

## Claim boundary

This audit adds one evidence-owned command mapping for the six carriers. It does not
upgrade any carrier to score 3, promote a step or other parent, replay a Host command,
or infer an exit absent from the source record. Historical evidence remains unchanged.
