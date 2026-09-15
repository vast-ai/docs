What triggers each machine error, and how it affects your listing. Three effect levels:

* **De-verifies the whole machine** — the machine is marked unverified and taken off the market until the error clears.
* **Affects VM offers only** — your machine stays listed for containers, but VM (GPU-passthrough) rentals are disabled until the VM condition clears.
* **Logged only** — recorded against a specific rental attempt; does **not** change your machine's verification or listing.

---

## A. Errors that de-verify the whole machine

These take the machine off the market until resolved.

| error_message | category | root cause — why it triggers |
| --- | --- | --- |
| `nvidia-container-cli: device error:` | Docker/NVIDIA runtime | The NVIDIA container runtime couldn't access a GPU when starting a container. Usually the GPU is in a bad state — the driver/NVML lost access to the device (GPU fell off the PCIe bus, a driver crash, or a system change that broke container GPU access). |
| `port networking issues` / `Port networking issues` | Networking | The machine's advertised direct-port range isn't reachable from the public internet — a firewall, router/NAT, or port-forwarding misconfiguration (or CGNAT/double-NAT). |
| `Port Networking Issues` (title case) | Networking | Same as above, raised by the platform's periodic inbound port-reachability check (it could not connect to your ports from outside). |
| `GPU PCIE issue` | GPU hardware | The kernel logged PCIe bus errors (AER / "Uncorrected") for a GPU within the last 24 hours — a degraded or failing PCIe link (bad slot/riser/cable, needs reseating, or a failing GPU). "Uncorrected" is the serious case. |
| `unknown or invalid runtime nvidia` | Docker/NVIDIA runtime | Docker has no valid `nvidia` runtime registered — the NVIDIA Container Toolkit isn't installed/configured, or Docker wasn't restarted after installing it. |
| `unknown flag: runtime` | Docker/NVIDIA runtime | Docker rejected the `--runtime` flag — Docker is too old to support it, or a wrapper/alias is intercepting the `docker` command. |
| `CUDA error: uncorrectable ECC error encountered` | GPU hardware | A GPU workload hit an uncorrectable (double-bit) ECC memory error — failing GPU VRAM, usually requiring a row-remap or GPU replacement. |
| `failed to inject CDI devices: unresolvable CDI devices` | Docker/CDI | The container runtime couldn't resolve the GPU device specification — typically a stale or missing GPU device spec after the machine's GPU set changed. |
| `Unable to determine the device handle for` | GPU/CUDA | The driver/NVML can't get a handle for a GPU — the GPU is no longer enumerable (fell off the bus, or a power/thermal/hardware fault). |
| `Cannot connect to the Docker daemon` | Docker | Docker commands can't reach the Docker daemon — dockerd is stopped, crashed, or its socket is inaccessible. |
| `Error response from daemon: --storage-opt is supported only for overlay over xfs` | Docker/storage | Docker rejected a per-container disk-size limit because the storage driver/filesystem isn't `overlay2` backed by XFS with project quotas (`ftype=1`). |
| `<admin-set>` | Admin override | Set manually by a Vast administrator (e.g., flagged for investigation); does not come from automatic detection. |

---

## B. Errors that affect VM (GPU-passthrough) offers only

The machine stays listed for container rentals; VM rentals are disabled while the condition persists. (These clear on their own after the underlying condition is fixed and the machine reports clean for a while.)

| error_message | category | root cause — why it triggers |
| --- | --- | --- |
| `IOMMU config or Nvidia DRM Modeset has changed to no longer support VMs` | VM/IOMMU | The host's IOMMU/passthrough setup changed so GPUs can no longer be isolated for VMs — e.g., a GPU now shares an IOMMU group with non-bridge devices, or NVIDIA DRM modeset got enabled. |
| `GDM is on; VMs will no longer work.` | VM/desktop | A desktop display manager (GDM) is running and holding the GPU, which conflicts with VFIO passthrough. |
| `Error: machine does not support VMs.` | VM/IOMMU | A VM failed to start because hardware virtualization / IOMMU (Intel VT-d or AMD-Vi) isn't enabled in BIOS. |
| `Error: Unexpected configuration change; cannot assign GPUs to VMs.` | VM/config | A GPU's IOMMU grouping changed since verification, so it can no longer be passed through to a VM. |
| `Error: Machine incompatible with VMs after host change. Please destroy the instance and find a new machine.` | VM/config | After a host configuration change, the machine no longer meets the VM-passthrough prerequisites. |
| `Error: unable to complete out-of-memory-check` | VM/memory | A VM pre-flight memory check failed (not enough usable host memory to safely start the VM). |
| `Secrets fetch failed: machine authentication denied (HTTP 401)` | Auth | The machine's credentials were rejected while fetching instance secrets (authentication failure). |
| `Error: GPU error, unable to start instance.` | GPU | A GPU error blocked a VM instance from starting. Milder signal — only disables VM offers after repeated occurrences. |

---

## C. Logged only — does NOT affect verification or listing

These are recorded against a specific rental attempt (per-instance), not the machine. They don't de-verify or unlist anything.

| error_message | category | root cause — why it triggers |
| --- | --- | --- |
| `Error: Internal error.` | Container create | An unexpected internal error occurred while creating the container. |
| `Error: container is mounted` | Container | A leftover mount from a previous run blocked the operation. |
| `Error: Requested volume does not exist: <name>` | Volume | The requested storage volume was deleted or never existed. |
| `docker_build(): <inner error>` | Build | A `docker build` step failed (wraps the build's own error output). |
| `Waiting for template update` | Transitional | Normal transient state while the image/template updates — not a real fault. |
| `unknown` | Fallback | A failure occurred that carried no message (generic fallback). |
| `Secrets fetch failed: network/subprocess error` | Secrets/network | Could not reach the secrets service (network or local subprocess failure before any response). |
| `Secrets fetch failed: empty response` | Secrets | The secrets service returned an empty body. |
| `Secrets fetch failed: instance not found or access denied (HTTP 404)` | Secrets/auth | The instance wasn't found, or access was denied. |
| `Secrets fetch failed: bad request (HTTP 400)` | Secrets | The secrets request was malformed. |
| `Secrets fetch rate limited (HTTP 429)` | Secrets/rate-limit | The secrets service rate-limited the request. |
| `Secrets fetch failed: server error (HTTP <code>)` | Secrets | The secrets service returned a 5xx server error. |
| `Secrets fetch failed: unexpected HTTP <code>` | Secrets | The secrets service returned some other non-success status. |
| `Secrets fetch JSON parse error` | Secrets | The secrets response wasn't valid JSON. |

---

## Corrections applied vs. the source catalog

While verifying against the system, these changes were made to your catalog:

**Moved to "affects VM offers" (they DO disable VM rentals — the source catalog marked them "no effect"):**

* `Error: unable to complete out-of-memory-check`
* `Error: machine does not support VMs.`
* `Error: Unexpected configuration change; cannot assign GPUs to VMs.`
* `Error: Machine incompatible with VMs after host change…`
* `Secrets fetch failed: machine authentication denied (HTTP 401)`

**Wording fixes (actual text differs from the catalog):**

* "…after host **change**…" (the catalog said "after host **reboot**" — that text does not exist).
* "Secrets fetch failed: **unexpected HTTP** `<code>`" (the catalog said "`<other>`").

**Removed — these never reach the platform (local logs only / never reported), so they cannot trigger a machine error:**

* `Error: unable to map ports`
* `Error response from rocm-smi: unable to get num_gpus.`
* `Error response from rocm-smi: unable to gpu render node.`

