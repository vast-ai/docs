# Hardware Prep read-only Host verification — attempt 01

- Attempt ID: `ATTEMPT-2026-09-01-HOST-HARDWARE-PREP-01`
- Evidence IDs: `EV-HWP-E01-INVENTORY-01`, `EV-HWP-C01-READINESS-01`
- Procedures: `TS-HWP-E01`, `TS-HWP-C01`
- Target: restricted alias `HOST_VV_TARGET`
- Transport: restricted alias `HOST_VV_SSH`
- Started at: `2026-09-01T14:51:00Z`
- Repository revision/tree: `14d9af21fe8a6df205180d6f211415bf750ee4b8` / `2eded9e87079a3cb2517ee7a7448018c388b122b`
- Test-set snapshot SHA-256: `50b010956942a3294ea12cbc3936330fbad2be932948a9b4b3e747c8c72c051a`
- Pre-correction page SHA-256: `2578763082452d0e9c9422a17ba38a618bb06e738623e4b25f7332991f13868a`
- Execution class: authorized Host read-only
- Sudo, service mutation, VM mutation, load, listener, WAN, account mutation, or paid action: none

## Safety and evidence handling

SSH key authentication completed non-interactively as the authorized root account. Only
read-only inventory, service-listing, and GPU-health queries ran. Output published here is
reduced to non-secret facts; hostname, addresses, interface identifiers, filesystem UUIDs,
and other unique device material are omitted. No credential was requested, printed, or
retained.

## Exact documented inventory observations

| Documented command | Exit | Sanitized observation |
| --- | ---: | --- |
| `lsb_release -a` | 0 | Ubuntu 24.04 LTS (`noble`). |
| `uname -a` | 0 | Linux 6.8.0-138-generic, x86_64; hostname removed. |
| `lscpu \| sed -n '1,25p'` | 0 | AMD EPYC, 32 physical cores / 64 threads, AVX/AVX2 and AMD-V visible. |
| `lspci \| grep -i nvidia` | 0 | Four matching NVIDIA RTX 6000 Ada GPU functions were visible. |
| `lsblk -f` | 0 | Root is ext4; Docker storage is a separate XFS filesystem. UUIDs removed. |
| `findmnt / /data0 /var/lib/docker` | 1 | No output. The form does not inspect three targets; this is a source defect, not proof that only optional `/data0` is absent. |
| `df -h /` | 0 | Root capacity returned normally with substantial free space. |
| `ip -brief address` | 0 | Interface states and addresses returned; addresses and unique interface identifiers are omitted here. |

Separate read-only diagnosis confirmed:

- `findmnt /` exits 0 and reports the root filesystem.
- `findmnt /data0` exits 1 because this target has no `/data0` mount.
- `findmnt /var/lib/docker` exits 0 and reports XFS with `prjquota`.
- Docker and Vast services are already active. This is an active Host, not evidence of a
  clean provider image, and it must not be described as freshly provisioned.
- Exact `nvidia-smi` exits 0. A non-identifying query reports four matching RTX 6000 Ada
  GPUs, driver 595.84, and 46,068 MiB per GPU; the header reports CUDA 13.2.

## Procedure disposition before correction

| Target | Status | Rationale |
| --- | --- | --- |
| `HWP-E01-S01` | `PASS` | Authorized target and read-only/redaction boundary were fixed before execution. |
| `HWP-E01-S02` | `FAIL` | Seven inventory commands returned usable observations, but the authored multi-target `findmnt` command exited 1 with no output. |
| `HWP-E01-S03` | `PASS` | Existing Docker/Vast state was identified and the target was explicitly not treated as clean. |
| `HWP-E01-S04` | `PASS` | Publishable evidence excludes restricted identifiers. |
| `HWP-E01-B-main` / `TS-HWP-E01` | `FAIL` | One required ordered step fails; retain this result before correction. |
| `HWP-C01-S02` | `PASS` | Observed Ubuntu 24.04 matches the page's preferred release. |
| `HWP-C01-S03` | `PASS` | Exact `nvidia-smi` succeeds and observes all four same-model GPUs with one driver/runtime tuple. |
| `HWP-C01-S01`, `HWP-C01-S04` | `BLOCKED` | A point-in-time shell snapshot cannot establish all current verification authority, physical PCIe layout, power, cooling, or maintenance controls. |
| `HWP-C01-B-standard` / `TS-HWP-C01` | `BLOCKED` | The observable OS/GPU checks pass, but complete readiness is not established. |
| `HWP-C01-B-vm-planned` | `UNVALIDATED` | VM readiness is intentionally separate and the Host's VM setup is known to be non-representative. |

## Supersession correction

The older `ATTEMPT-2026-08-30-HOST-READONLY-03` classified the exact multi-target
`findmnt` exit 1 as an expected optional-mount absence and rolled the combined Hardware
Prep procedures up to PASS. This new exact reproduction shows that interpretation was too
broad: the authored form returns no root or Docker mount observation at all. Retain the
older observation, but do not use its Hardware Prep PASS as the current result.

## Required correction and retest

Replace the invalid multi-target form with three separately observable `findmnt` commands,
then rerun the entire documented inventory block. A missing optional `/data0` mount must be
recorded separately rather than hiding the successful root and Docker checks.
