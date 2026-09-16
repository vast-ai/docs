# Host safe read-only procedure verification, attempt 03

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SAFE-READONLY-03`
- Procedure evidence IDs: `EV-HOST-SAFE-READONLY-03-LOG-TAIL` and
  `EV-HOST-SAFE-READONLY-03-GPU-VISIBILITY`
- Method: authorized Host, bounded read-only command-carrier observation
- Frozen plan SHA-256:
  `fcdf0b3cd2fa56c828697f8744667a4ef0f57a37c12b2444b28dcbd3ddeb7a9b`
- Canonical test-set SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- New Host execution: four command carriers in two evidence groups

## Scope and retention boundary

Restricted raw stdout and stderr remain outside Git. This public record retains
only the result shape and bounded interpretation. It does not publish Host,
network, account, device, workload, renter, credential, or private-path data.

## Observations

### Bounded daemon-log tails

The exact bounded log-tail form completed with exit 0 for both documented
carriers. Each observation was limited to at most 100 current lines, and stderr
was empty. The retained raw outputs are restricted because log content can be
sensitive.

| Command carrier | Exit | Sanitized result shape | Stdout SHA-256 |
| --- | ---: | --- | --- |
| `CLM-d31f5b78bbf99242` | 0 | 100 stdout lines, 9,914 bytes; empty stderr | `605dab0af884f6800a6f4d137fca85cea9ff2d6246984f03afb21129c071d55a` |
| `CLM-155ca5dc04aaf9d9` | 0 | 100 stdout lines, 9,809 bytes; empty stderr | `f2103268e1141be4cd4a5a20b0f2b021ae79c721bef21868ff3739fb2a0e03fb` |

Both empty stderr files have SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

This proves that the current Host accepts the documented privileged, bounded
read form and path. It does not reproduce an install failure, a renter report,
or the correlation and diagnosis described by either broader procedure.

### GPU-visibility checks

The exact `nvidia-smi` form completed with exit 0 for both documented carriers.
Each observation reported four current GPU rows and had empty stderr. No
expected GPU inventory was frozen for this attempt, so the observation is a
current visibility check rather than an inventory conformance claim.

| Command carrier | Exit | Sanitized result shape | Stdout SHA-256 |
| --- | ---: | --- | --- |
| `CLM-9604a1e76cf3ec21` | 0 | 32 stdout lines, 2,793 bytes, four GPU rows; empty stderr | `b4e36ebc6f03e8df5bb1a8ec17b33d767ea9a3eb79cbfc2fc42470c9a9a13ef5` |
| `CLM-7cac63760e51f4d0` | 0 | 32 stdout lines, 2,793 bytes, four GPU rows; empty stderr | `21b748c47ff8c9cd482612848f570c6fd12e159ea0f3440f4a301c3c1446b237` |

Both empty stderr files have the same empty-file SHA-256 recorded above.

This proves the current read-only query form only. It does not prove a completed
maintenance sequence, Docker GPU access, self-test behavior, an NCCL failure,
or root-cause diagnosis.

## Reviewer integration correction and retest

The first full reviewer replay after integrating this attempt passed 16 of 18
tests and failed closed for all V&V display. The attempt array had grown from 34
to 35, but the declared attempt count still said 34. The current projection had
also moved to 95 PASS and 262 UNVALIDATED, while the reconciliation checkpoint
still declared the preceding 91/266 totals.

Only those two accounting declarations were corrected. The attempt, command
outcomes, scores, evidence mappings, parent statuses, and raw observations were
not changed. The unchanged reviewer suite then passed 18 of 18 tests, including
the page-scoped evidence, portability, sanitization, current-projection, and
fail-closed cases.

## Claim boundary

`EV-HOST-SAFE-READONLY-03-LOG-TAIL` supports
`CLM-d31f5b78bbf99242` and `CLM-155ca5dc04aaf9d9` as current PASS with
semantic score 2. `EV-HOST-SAFE-READONLY-03-GPU-VISIBILITY` supports
`CLM-9604a1e76cf3ec21` and `CLM-7cac63760e51f4d0` as current PASS with
semantic score 2. Both records have the `DIRECT_FUNCTIONAL_PARTIAL` ceiling.
No step, branch, test set, or page status is promoted.

There is no separate public shell transcript or wrapper record for this
attempt. The restricted evidence record and exact planned carrier forms are the
retained basis for these limited command-level results.
