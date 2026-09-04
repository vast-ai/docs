# Host safe read-only follow-up verification — attempt 02

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SAFE-READONLY-02`
- Procedure evidence IDs: `EV-HOST-SAFE-READONLY-02-SNAPSHOT` and
  `EV-HOST-SAFE-READONLY-02-VM-CHECK`
- Method: authorized Host, bounded privileged read-only procedure observation
- Frozen plan SHA-256:
  `681a0b0c81b74e121fab9559fb4464bb28a302a531937c1dd7d03e29a4ee175c`
- Canonical test-set SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- New Host execution: two bounded read-only carrier groups

## Scope and retention boundary

Restricted raw bytes remain outside Git. This record publishes only the safe
result shape, exact exits, supplied hashes, and bounded interpretation. It does
not publish infrastructure, account, network, device, workload, or credential
data.

## Observations

### First-day current snapshot — `CLM-595e1c8f67f5692f`

The whole carrier exited 0; stdout SHA-256 is
`5196da060ccb9bccf1c83f9badba1c1f0e49c66be27a307ef9af654400a102ec`; stderr
was empty. The active-state and full-status components exited 0. Two bounded
80-line journal reads exited 0. An initial isolated tail transport attempt
exited 255 before authentication; the unchanged bounded retry exited 0 and
retained 100 lines. The authorized range comparison read exited 0 and matched.
The selected severity scan found zero matches.

This supports a current bounded service/log/range snapshot only. It does not
establish 24-hour stability, external reachability, account visibility, a
client workload, or cleanup behavior.

### VM state query — `CLM-ca44522b22c4c5ee`

The helper was present and 88 current IOMMU groups were observed without
publishing hardware identifiers. The exact documented read-only helper `check`
exited 0, wrote exactly `off` to stdout (SHA-256
`b470b84cf0cd3189e10615bffea7d5cbd9f61134ba1c2cfd513ddd45b776a5f6`), and
had empty stderr.

`off` is a configuration-state observation only. It is not enablement success,
VM boot proof, GPU-passthrough proof, or permission to perform the unrun
state-changing helper actions.

## Claim boundary

`EV-HOST-SAFE-READONLY-02-SNAPSHOT` supports
`CLM-595e1c8f67f5692f` as current PASS with semantic score 2 and the
`DIRECT_FUNCTIONAL_PARTIAL` ceiling. `EV-HOST-SAFE-READONLY-02-VM-CHECK`
supports `CLM-ca44522b22c4c5ee` as current PASS with semantic score 3 and the
`DIRECT_FUNCTIONAL_EXACT_FULL` ceiling for the exact state-query carrier only.
No step, branch, test set, or page status is promoted. The pre-authentication
transport failure remains retained as a transport observation and is not
presented as a command failure.
