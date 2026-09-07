# Host safe read-only procedure verification — attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SAFE-READONLY-01`
- Evidence ID: `EV-HOST-SAFE-READONLY-01`
- Method: authorized Host, bounded read-only procedure observation
- Frozen plan SHA-256:
  `480920c027a0cb01a227bab38d5281ccfb6af2521450982872cc49d0afa27791`
- Canonical test-set SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- New Host execution: six bounded read-only carrier groups

## Scope and retention boundary

This result records the exact six planned read-only carrier groups. Restricted raw
bytes remain outside Git. This public record retains only command-group exits,
safe structural observations, and the supplied whole-carrier SHA-256 values. It
does not publish infrastructure, account, network, device, workload, or credential
data.

## Observations

| Command carrier | Result | Public retained detail |
| --- | --- | --- |
| `CLM-e1ca96623c45ccf7` | PASS | The bounded block-device read exited 0 and produced a non-empty 19-line snapshot. Whole-carrier stdout SHA-256: `08abb5e7201451f0be2ca7bcbf3f2b07d6cdfcc3c85e6c7950fc5d53a1e6c5d7`. Stderr was empty. |
| `CLM-128d433cdb393ca9` | PASS | The filesystem/mount group exited 0. Its block/filesystem, root-mount, and application-mount reads exited 0; the authored optional data-mount lookup exited 1 with empty stdout under `|| true`. Whole-carrier stdout SHA-256: `9bdef9b3186520c93df9414d13f208603046ab040d89ce1f849b86a419e668b8`. Stderr was empty. |
| `CLM-a95c02cbab56772e` | PASS | The filesystem, mount, and root-capacity group exited 0. Its required components exited 0 and the same authored optional data-mount lookup exited 1 with empty stdout. Whole-carrier stdout SHA-256: `5dd5056a22a079f3d27c7b2d1b82ae5e396b2da9581bb451022dbe2c3ab45f8b`. Stderr was empty. |
| `CLM-10bcbc68d0d8f1a2` | PASS | The bounded driver-recommendation query exited 0 and reported one recommendation. Whole-carrier stdout SHA-256: `dbef638fc6d2016de4a5b59eef6e7f6bd9387f555b031e334fd049badbb5517d`. Stderr SHA-256: `0a78eba9cc4b6272a54ab21f28b647e35e0bbfb63c15721ef3795f7ef303da9`; it contained ten deprecation notices and one missing local-audio-command message. |
| `CLM-c7a8ac27359a2b4b` | PASS | The installed-Host health snapshot exited 0. Four required services were active; the application mount reported XFS project accounting and enforcement on; the authorized range comparison matched; all component exits were 0. Whole-carrier stdout SHA-256: `f9d356949a3c8d9eff245b92610fe0fcb44c8359158a3bbabf7722a4306ccde0`. Stderr was empty. |
| `CLM-6391e55bdef1e3cc` | PASS | The final-state read-only snapshot exited 0. Capacity, mount, quota, service, range, and GPU-visibility components exited 0; four GPU rows were observed. Whole-carrier stdout SHA-256: `c3e54056fdf97f2776329e73d27f5d44cfdcf9ff09f4183810a528475df83cf6`. Stderr was empty. |

The nonzero optional data-mount component is retained as an authored tolerated
absence; it neither changes the whole-carrier exit nor establishes a storage
disposability decision.

## Claim boundary

Each PASS applies only to its named, bounded read-only command carrier on the
authorized current Host. The direct proof ceiling is
`DIRECT_FUNCTIONAL_PARTIAL`, and each semantic score remains 2.

This result does not establish device disposability, valuable-data handling,
pre-mutation timing, clean installation, driver application, reboot chronology,
installer or wizard completion, account visibility, external reachability,
Docker GPU injection, self-test, listing, paid rental, or sustained health.
No step, branch, test set, or page status is promoted.
