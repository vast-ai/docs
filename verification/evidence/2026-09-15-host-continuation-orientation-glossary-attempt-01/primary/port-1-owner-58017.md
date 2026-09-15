# Machine-Level Error Table — message, keyword, daemon command & verified self-check

For each machine-level error: the stored/shown message, the keyword captured, the **actual command**  
**the daemon runs**, a host **self-check command**, and an **equivalence verdict** confirmed against  
the daemon source (`Kaalia/src/`, `kaalia_docker_shim`, `daemon_ext/send_mach_info.py`, `web/scripts.py`).

Verdict legend: **✓ Equivalent** — detects the same condition the daemon flags · **◐ Partial** —  
detects it but with caveats (see notes) · all "server-side" rows are matched from the failed  
`docker create/run/start` stderr the daemon forwards.

| error_message | keyword captured | actual daemon command | self-check command | equivalence |
| --- | --- | --- | --- | --- |
| `nvidia-container-cli: device error: <details>` | `device error`, `nvml error` | — withheld (internal log scan) | `sudo nvidia-container-cli -k -d /dev/tty info` (see note 1) | ◐ Partial |
| `GPU PCIE issue` | `AER`, `Uncorrected` | `sudo timeout --foreground 3s journalctl -o short-precise -r -k --since '24 hours ago' | grep 'AER' | tail -n 1` (and `grep 'Uncorrected'`) | `sudo journalctl -k --since '24 hours ago' | grep -iE 'AER|Uncorrected'` | ✓ Equivalent (superset) |
| `failed to inject CDI devices: unresolvable CDI devices` | `failed to inject CDI devices: unresolvable CDI devices` | — withheld (internal log scan) | `sudo nvidia-ctk cdi generate --mode=auto --device-name-strategy=index >/dev/null && echo OK` (see note 2) | ◐ Partial (rewritten — `cdi list` was wrong) |
| `port networking issues` / `Port networking issues` | `port networking issues` | server probe: `nc -zv -w 5 <public_ip> <port>` (top port first, then a random in-range port) | from a host **outside your LAN**: `nc -vz <public_ip> <END>` where `END` = `cat /var/lib/vastai_kaalia/host_port_range` (see note 3) | ✓ Equivalent (external only) |
| `unknown or invalid runtime nvidia` | `unknown or invalid runtime nvidia` | — server-side; from failed `docker create --runtime=nvidia …` stderr | `docker info --format '{{json .Runtimes}}'` (must contain `nvidia`) ; `docker info --format '{{.Runtimes.nvidia.path}}'` (expect `…/kaalia_docker_shim`) | ✓ Equivalent |
| `unknown flag: runtime` | `unknown flag: runtime` | — server-side; from failed `docker create` stderr | `docker create --help | grep -- --runtime` ; `type docker` (see note 4) | ◐ Partial |
| `CUDA error: uncorrectable ECC error encountered` | `uncorrectable ECC error encountered` | — server-side; from container CUDA failure on `docker start` (daemon never queries ECC) | `nvidia-smi -q -d ECC` (read the **Aggregate** "Uncorrectable" counts; see note 5) | ◐ Partial |
| `Unable to determine the device handle for` | `Unable to determine the device handle for` | — server-side; NVML enumeration failure surfaced at container start | `nvidia-smi -L` ; `nvidia-smi` ; `lspci -d 10de:` ; `sudo dmesg | grep -iE 'NVRM|Xid|fell off the bus'` | ✓ Equivalent |
| `Cannot connect to the Docker daemon` | `Cannot connect to the Docker daemon` | — server-side; same client→dockerd socket the daemon uses | `docker info` ; `systemctl status docker` ; `journalctl -u docker -n 50` | ✓ Equivalent |
| `Error response from daemon: --storage-opt is supported only for overlay over xfs` | `--storage-opt is supported only for overlay over xfs` | — server-side; daemon passes `--storage-opt size=…` on create (KaaliaCreate.cpp) | `docker info | grep -i 'Storage Driver'` (expect `overlay2`) ; `df -T /var/lib/docker` (expect `xfs`) ; `xfs_info /var/lib/docker | grep -o 'ftype=[01]'` (expect `ftype=1`) | ✓ Equivalent |
| `IOMMU config or Nvidia DRM Modeset has changed to no longer support VMs` | IOMMU group composition / `nvidia_drm modeset` | enumerate `/sys/kernel/iommu_groups/*` → `sudo cat <pci_device>/class` (bridge=`06`) → `sudo cat /sys/module/nvidia_drm/parameters/modeset` (must be `N`) | `cat /sys/module/nvidia_drm/parameters/modeset` (must be `N`) + per-group bridge check (see note 6) | ◐ Partial |
| `GDM is on; VMs will no longer work.` | `gdm` service active | `systemctl is-active gdm` | `systemctl is-active gdm` (fix: `sudo systemctl disable --now gdm`) | ✓ Equivalent |

## Notes (verified against the daemon)

1. **device error / nvml error** — the daemon doesn't author these strings; it captures docker / nvidia-container-cli / NVML stderr. `nvidia-container-cli -k -d /dev/tty info` is the real probe (it touches the GPUs like a container launch). Plain `nvidia-smi` is **not** sufficient — it can succeed while a containerized NVML init still fails (the classic "Failed to initialize NVML: Unknown Error"). Strongest reproduction:  
  `docker run --rm --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all nvcr.io/nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi -L`
2. **CDI** — `nvidia-ctk cdi list` does **not** reproduce this: the shim writes a per-container `/etc/cdi/D.<id>.yaml`, and "unresolvable" means that spec is stale/missing — by self-check time the container (and its spec) is gone. Check that the generator the shim relies on still works (`nvidia-ctk cdi generate …`), inspect on-disk specs (`ls -l /etc/cdi/*.yaml /var/run/cdi/*.yaml`), and surface stale Vast specs: `sudo python3 /var/lib/vastai_kaalia/purge_stale_cdi.py --dry-run`.
3. **port networking** — the server runs `nc -zv -w 5 <public_ip> <port>` _inbound_ from outside; it tests the **top port** of the range first (`direct_port_start + direct_port_count − 1`, where the daemon's sshd listens) and a random in-range port. So run the `nc` probe from a machine **outside your network** (same-LAN tests can false-pass if the router doesn't hairpin). `sudo ss -tlnp` only proves a local listener exists — it's necessary but **not** sufficient (it can't see firewall/NAT/CGNAT). For a mid-range port: on the host `nc -l -p <port>`, then `nc -vz <public_ip> <port>` from outside.
4. **unknown flag: runtime** — `--runtime` has existed since Docker 1.12 (2016), so this rarely means "old Docker"; it almost always means a shim/alias is intercepting the `docker` CLI. `docker create --help | grep -- --runtime` confirms the binary accepts the flag; `type docker` reveals an intercepting wrapper.
5. **ECC** — the daemon never reads ECC; this is a container CUDA runtime error. `nvidia-smi -q -d ECC` **Aggregate** counters persist across reboots (strong signal), but **Volatile** counters reset on GPU/driver reset, so a clean reading does **not** exonerate the GPU. Corroborate: `nvidia-smi -q | grep -iE 'Xid|Remapped|Pending'` and `journalctl -k | grep -i xid` (Xid 48/63/64/94/95 = ECC / row-remap).
6. **IOMMU** — `modeset=N` + groups existing is not enough; the daemon also requires each GPU to be **alone in its IOMMU group** with only PCI **bridges** (class `06`) as group-mates. Full check:

    ```
    cat /sys/module/nvidia_drm/parameters/modeset   # must be N
    for g in /sys/kernel/iommu_groups/*; do echo "group ${g##*/}:"; for d in "$g"/devices/*; do lspci -nns "${d##*/}"; done; done
    
    ```

    A group is VM-OK only if it holds exactly one GPU and every other device is a bridge (class `06`).



## Not keyword-detected (emitted directly by the daemon, no self-check)

`Error: Internal error.`, `Error: container is mounted`, `Error: Requested volume does not exist: <name>`, `docker_build(): <inner error>`, `Waiting for template update`, `unknown`, `Error: GPU error, unable to start instance.`, `Error: machine does not support VMs.`, `Error: Unexpected configuration change; cannot assign GPUs to VMs.`, `Error: Machine incompatible with VMs after host change…`, and all `Secrets fetch …` messages (HTTP 400/401/404/429/5xx).