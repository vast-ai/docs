# Host Docs read-only Host attempt 03 — result

> **Qualification correction (2026-08-31):** The later Host-owner review determined that the VM target was improperly configured. The retained `pending` observation does not acceptance-test the VM `check` command. Its current status is `UNVALIDATED` and it is unscored pending a repaired-Host retest; see [`../2026-08-31-host-vm-environment-disqualification-01/result.md`](../2026-08-31-host-vm-environment-disqualification-01/result.md).

- Attempt state: `EXECUTED`
- V&V status: `PARTIAL`
- Target: restricted alias `HOST_VV_TARGET`
- Transport: restricted alias `HOST_VV_SSH`
- Source revision: `9439b9bbcd4810294a1420d7d618dd462ea2dbd7`
- Frozen plan SHA-256: `c6f18d0fceaeea862f0c994d2b623cae4c5c5cc7b29415f6fceeaa1612a10429`
- Frozen checks executed: `41/41`
- Read-only delta checks executed: `14/14`
- SSH process exit: `0`
- Raw artifact policy: mode `0600` in a local restricted archive outside Git

## Logical procedure results

| Evidence ID | Host page procedure | Result | Sanitized observation |
| --- | --- | --- | --- |
| `EV-HOST03-HARDWARE-PREP` | `HWP-E01`, `HWP-C01` | `PASS` | OS, CPU, storage, network, PCI, and GPU inventory commands executed. Four expected GPUs were visible and the health query completed. The optional `/data0` mount was absent; `/var/lib/docker` was XFS with a project-quota mount option. |
| `EV-HOST03-DAY1` | `DAY1-E01` | `BLOCKED` | All four services were active and bounded logs contained no fatal/restart-loop markers. Exact `sudo` forms still require an interactive privilege check, and a point snapshot cannot prove 24-hour stability. |
| `EV-HOST03-DIAGNOSTICS-SERVICE` | `DIA-E02` service branch | `BLOCKED` | Service state, journals, daemon log, and the configured range were readable without privilege; the configured range matched the authorized forwarding. Exact `sudo` forms remain manually blocked. |
| `EV-HOST03-DIAGNOSTICS-STORAGE` | `DIA-E02` storage branch | `BLOCKED` | Capacity and mount facts were available, but Docker usage required Docker-socket or sudo access. |
| `EV-HOST03-DIAGNOSTICS-KERNEL` | `DIA-E03` | `BLOCKED` | Current, previous, and file-backed kernel evidence was collected without privilege. `dmesg`, compressed-log coverage, and exact `sudo` forms remain blocked. No explicit PCIe Bus Error, Xid, or fallen-GPU line was observed in the bounded evidence. |
| `EV-HOST03-GPU-INJECTION` | `ERR-T02` / `ERR-T03` container branch | `BLOCKED` | Host GPU visibility passed. The procedure's Docker GPU-container run is mutating and was not executed in this read-only attempt. |
| `EV-HOST03-DOCKER-RUNTIME` | `ERR-T02-B02-S01` | `FAIL` | Docker type, version, and `--runtime` help passed; `docker info` failed as authored because this operator lacks Docker-socket access. The page omits `sudo` for this command while adjacent privileged Docker commands include it. |
| `EV-HOST03-DOCKER-DAEMON` | `ERR-T02-B03-S01` | `BLOCKED` | Docker service and journal checks passed; exact `sudo docker ps` remains manually blocked. |
| `EV-HOST03-PCIE` | `ERR-T03-B03-S01` | `BLOCKED` | PCI and NVIDIA inventories returned successfully; the exact privileged kernel-log command remains manually blocked. |
| `EV-HOST03-ECC` | `ERR-T03-B04-S01` | `BLOCKED` | ECC/remap queries completed without nonzero remap findings; the exact privileged Xid-log command remains manually blocked. |
| `EV-HOST03-NVSWITCH` | `ERR-T04-B02-S03` | `NOT_APPLICABLE` | The page correctly scopes Fabric Manager checks to NVSwitch systems; this Host is not such a system and the unit is absent. GPU topology still returned. |
| `EV-HOST03-STORAGE` | `ERR-T05-B02-S01` | `BLOCKED` | Docker capacity and XFS/project-quota mount facts passed; Docker usage remains blocked by socket privilege. |
| `EV-HOST03-VM-CHECK` | `VM-E01-S01` | `UNVALIDATED` | The exact read-only command returned `pending`, but the target was later confirmed to have improper VM/IOMMU setup; retain the output without treating it as acceptance evidence. |

## Claim limits and manual queue

For the qualified items, this snapshot validates present command behavior, not
long-duration stability or repair outcomes. VM `check` is explicitly excluded
and remains unvalidated. The snapshot does not validate a Docker GPU container, live load, paid
self-test, listener/WAN reachability, service restart, cleanup, reboot, VM state
mutation, or any branch requiring an actual observed fault. Exact privileged
forms must be completed interactively by an authorized operator.

`check-results.json` retains every check ID, exit code, classification, raw hash,
and the sanitized Host snapshot. Hostname, usernames, addresses, device IDs,
container/workload details, and raw logs are excluded from Git.
