# Hardware Prep `findmnt` correction and read-only retest — attempt 02

- Attempt ID: `ATTEMPT-2026-09-01-HOST-HARDWARE-PREP-02`
- Evidence IDs: `EV-HWP-E01-INVENTORY-02`, `EV-HWP-C01-READINESS-02`
- Procedures: `TS-HWP-E01`, `TS-HWP-C01`
- Supersedes for current Hardware Prep result: `ATTEMPT-2026-09-01-HOST-HARDWARE-PREP-01`
- Target: restricted alias `HOST_VV_TARGET`
- Transport: restricted alias `HOST_VV_SSH`
- Repository revision/tree: `14d9af21fe8a6df205180d6f211415bf750ee4b8` / `2eded9e87079a3cb2517ee7a7448018c388b122b` (working source is newer than that tree)
- Test-set snapshot before inventory refresh: `50b010956942a3294ea12cbc3936330fbad2be932948a9b4b3e747c8c72c051a`
- Corrected page SHA-256: `ce24cfe18c2b1862114e9b1d5c7bf6f6425b02fa4da5dfd3372f0a5f8a27ded1`
- Execution class: authorized Host read-only
- Sudo, service mutation, VM mutation, load, listener, WAN, account mutation, or paid action: none

## Correction

The source now runs `findmnt /`, `findmnt /data0`, and
`findmnt /var/lib/docker` as separate observations. It explains that an unmounted target
returns exit 1 with no output and that optional `/data0` must not hide root or Docker
storage results. Attempt 01's failed authored form remains retained.

## Complete corrected inventory retest

| Documented command | Exit | Sanitized observation |
| --- | ---: | --- |
| `lsb_release -a` | 0 | Ubuntu 24.04 LTS. |
| `uname -a` | 0 | Linux 6.8.0-138-generic, x86_64; hostname removed. |
| `lscpu \| sed -n '1,25p'` | 0 | 32 physical cores / 64 threads; AVX/AVX2 visible. |
| `lspci \| grep -i nvidia` | 0 | Four same-model NVIDIA GPU functions visible. |
| `lsblk -f` | 0 | Root and separate XFS Docker storage visible; identifiers removed. |
| `findmnt /` | 0 | Root mount resolved independently. |
| `findmnt /data0` | 1 | No `/data0` mount; this is the documented optional-target outcome. |
| `findmnt /var/lib/docker` | 0 | XFS Docker mount resolved with `prjquota`. |
| `df -h /` | 0 | Root capacity returned normally. |
| `ip -brief address` | 0 | Interface state and address inventory returned; identifiers and addresses removed. |

The procedure then correctly identified active Docker/Vast state and did not describe this
machine as a clean provider image. Exact `nvidia-smi` also exits 0 and observes all four
same-model GPUs under one driver/runtime tuple.

## Current disposition

| Target | Status | Rationale |
| --- | --- | --- |
| `HWP-E01-S01` | `PASS` | Target, read-only boundary, and restricted evidence handling fixed before execution. |
| `HWP-E01-S02` | `PASS` | Every corrected inventory observation ran; optional `/data0` produced the explicitly documented exit-1/no-output outcome. |
| `HWP-E01-S03` | `PASS` | Existing Host state was recognized and the target was not misclassified as clean. |
| `HWP-E01-S04` | `PASS` | Publishable evidence is sanitized. |
| `HWP-E01-B-main` / `TS-HWP-E01` | `PASS` | All four required ordered steps pass for this exact read-only snapshot procedure. |
| `HWP-C01-S02` | `PASS` | Ubuntu 24.04 matches the preferred release stated by the page. |
| `HWP-C01-S03` | `PASS` | Exact `nvidia-smi` succeeds and all four expected same-model GPUs are visible. |
| `HWP-C01-S01`, `HWP-C01-S04` | `BLOCKED` | Full verification authority and physical PCIe, power, cooling, stability, and maintenance controls are not established by this shell snapshot. |
| `HWP-C01-B-standard` / `TS-HWP-C01` | `BLOCKED` | The observable OS/GPU/storage checks pass, but complete Host readiness remains unproven. |
| `HWP-C01-B-vm-planned` | `UNVALIDATED` | VM readiness remains separately excluded on the known non-representative VM setup. |

## Claim limits

This PASS validates the corrected inventory procedure on one authorized active Host. It
does not prove a clean provider image, sustained stability, physical power/cooling/PCIe
layout, public network reachability, current marketplace verification acceptance, or VM
readiness. Those claims remain separately BLOCKED or UNVALIDATED.
