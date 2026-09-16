# Host GPU injection attempt 01 result

- Attempt ID: `ATTEMPT-2026-09-02-HOST-GPU-INJECTION-01`
- Status: `FAIL`
- Finding: `FINDING-HOST-GPU-INJECTION-RUNTIME-FLAG-01`
- Method: executed the documented sequence on the authorized idle Host
- Started: `2026-09-02T17:36:01Z`
- Finished: `2026-09-02T17:36:10Z`

## Observation

The Host-side `nvidia-smi -L` command exited `0` and enumerated four NVIDIA RTX 6000 Ada Generation GPUs. The documented container command downloaded the requested image, but exited `125` before starting the container. Docker reported that direct `--gpus`/CDI-hook invocation is not supported by this Host runtime and instructed the operator to use the NVIDIA runtime with `--runtime=nvidia` instead.

The kernel-journal source and filter both executed successfully. Their matches are retained privately and are not interpreted as a new hardware diagnosis in this attempt.

Cleanup checks passed: the Host had zero running containers and zero GPU compute processes before and after the attempt. `vastai.service` remained active. The downloaded CUDA image layers remain cached; no service, storage, VM, offer, or maintenance configuration was changed.

## Disposition

The three previously blocked source command carriers below are now directly executed failures, not access blockers:

- `CLM-2113f9109b2c79c5`
- `CLM-2ffc62f260fd8010`
- `CLM-9aa5c400c3ff1241`

Their current functional status is `FAIL` and semantic score is `1` for the documented form on this representative Vast Host. A corrected `--runtime=nvidia` form requires a separate retained retest before it can support replacement wording.

## Retained evidence

Restricted raw evidence root:

`../private-evidence/2026-09-02-host-gpu-injection-attempt-01/`

| Artifact | SHA-256 |
| --- | --- |
| `run.raw` | `56ef0a5513be61de97543fdb6e02a8908f0a373f2bbbe2a9d206f42061a64468` |
| `run.stderr` | `2644e4c1e7185783244fbb98d02f141e06d078b956a869ce27dca85e4d3f6650` |

Raw evidence contains Host-specific identifiers and stays outside the documentation commit. The hashes allow the retained files to be checked without publishing them.

## Limitation

This result applies to the tested Host runtime and the image digest resolved at execution time. It establishes that the published `--gpus all` form fails in this representative Host context. It does not establish that every Docker/NVIDIA installation rejects that form, and it does not validate the unrun GPU-burn command.
