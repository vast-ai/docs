# Host documentation defect correction and retest — attempt 01

## Scope and provenance

- Timestamp started: `2026-08-31T01:00:32Z`
- Documentation target: branch `CON-1584-host-cli-api-sdk`, baseline commit `175d226adf1293c1ed54b74df6205ed7ac7fdff6`
- Host target: `HOST_VV_TARGET` (authorized operator session; the stable machine and transport mapping is retained in the restricted local archive)
- Installed VM helper SHA-256: `bb7c5922931aacbdff85528fcfb52733639db00361ae00b232f3cbfad0d251de`
- Vast CLI used for control-plane inspection: `1.4.2.post7+54c1b69`
- Secrets: the Host API key was supplied interactively, was not printed, and is not retained here.

This attempt corrects four source-documentation defects while preserving the earlier failed or held observations. A source correction is not treated as a behavioral `PASS` without a claim-suitable retest.

## Preconditions and safety gate

The Host-account query for `HOST_VV_TARGET` reported:

- `listed: true`
- `num_gpus: 4`
- `gpu_occupancy: "x x x x "`
- `current_rentals_on_demand: 0`
- `current_rentals_reserved: 0`
- `current_rentals_resident: 0`
- `current_rentals_running: 0`
- `current_rentals_running_on_demand: 0`
- `current_rentals_running_reserved: 0`
- `client_end_date: null`
- `volume_rented_size: 0.0`

Host-local read-only checks found no GPU compute processes and no visible `containerd-shim`, `runc`, QEMU, or virsh processes. The VM helper `check` action returned `pending` with exit status `0`.

The default SSH key successfully authenticates as the authorized operator (`uid 1000`) on `HOST_VV_TARGET`. The operator is a member of the `sudo` group, but `sudo -n true` returns exit `1` with `sudo: a password is required`; SSH-key authentication therefore does not supply sudo elevation on this Host. One authorized credential attempt was supplied directly to the hidden sudo prompt without being printed or retained, but sudo rejected it, so it was not retried. Docker-socket inspection and VM state mutation still required valid interactive sudo. Neither `off` nor `on` was run in this attempt.

## Results

| Stable claim | Correction | Verification result | Behavioral result |
| --- | --- | --- | --- |
| `CLM-be71decb680d1423` | Replaced dynamic all-machine defrag expansion with explicit reviewed machine-ID placeholders. | `PASS` — local CLI help accepts one or more integer IDs; diff and formatting checks passed. | `UNVALIDATED` — defragmentation was not executed because it mutates Host offers. |
| `CLM-2c2c7d94c1bd259f` | Added `sudo` to `docker info` and documented Docker-daemon privilege and `grep` exit-1 semantics. | `PASS` — correction matches the retained permission failure and adjacent privileged diagnostics. | `BLOCKED` — interactive sudo is required for the post-correction Docker retest. |
| `CLM-9b86f864cf7df38c` | Added the owning `vastai list machine <machine-id>` command to the pricing flags. | `PASS` — CLI help confirms the required ID and every documented option/date form. | `UNVALIDATED` — listing was not changed because this command creates or updates offers. |
| `CLM-9cba75bbdc780804` | Added `sudo`, an approved-idle-window gate, a no-active-rental/workload condition, and a post-action status check. | `PASS` — the installed helper and directory ownership establish that `off` is a privileged Host mutation. | `BLOCKED` — idle preconditions passed, but interactive sudo is required for `off → check → on → check`. |

Restoration claim `CLM-ffda5e2c291c470e` remains `BLOCKED` for the same interactive-sudo reason. Check-only control `CLM-ca44522b22c4c5ee` remains separate; its observed `pending` result does not prove either state transition.

## Local checks

- `git diff --check`: exit `0`
- `npm run check-persona-chips`: exit `0` (`39` pages in sync)
- `npm run test-review-context`: exit `0` (`12/12` tests passed)
- `python3 vast.py defrag machines --help`: exit `0`, one-or-more `IDs` accepted
- `python3 vast.py list machine --help`: exit `0`, required `ID` and all five example options present
- Port-4000 review routes for Fleet Operations, Machine Errors, Pricing Your Listing, and VMs: HTTP `200`

The first Mint preview start used local Node 25 and failed because Mint requires an LTS release. The unchanged preview was restarted with the bundled LTS Node runtime before the four HTTP checks passed.

## Retained prior failure

The pre-correction Docker failure remains in [`../2026-08-30-host-readonly-attempt-03/result.md`](../2026-08-30-host-readonly-attempt-03/result.md). It must not be overwritten or silently promoted.

## Remaining actions

Historical note: a later privileged attempt superseded this action queue; see [`../2026-08-31-host-privileged-attempt-01/result.md`](../2026-08-31-host-privileged-attempt-01/result.md). Its VM observations were subsequently disqualified as non-representative by [`../2026-08-31-host-vm-environment-disqualification-01/result.md`](../2026-08-31-host-vm-environment-disqualification-01/result.md). The list below is retained as the original attempt closeout, not the current V&V status.

1. Authenticate interactive sudo on the supplied Host.
2. Reconfirm the control-plane rental counters immediately before mutation.
3. Run and capture `sudo python3 /var/lib/vastai_kaalia/enable_vms.py off`, then an unprivileged `check` confirming `off`.
4. Restore with `sudo python3 /var/lib/vastai_kaalia/enable_vms.py on`, then run `check` and record the actual resulting state. If restoration requires `-f`, record that as a deviation rather than hiding it.
5. Run `sudo docker info | grep -i runtime` and retain both pipeline status and output.
6. Append the observations to this attempt and reconcile the derived register and scores. Do not assign score `3` until execution and semantic relevance both pass.
