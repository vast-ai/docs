# Host GPU injection published-form retest 03 result

- Attempt ID: `ATTEMPT-2026-09-02-HOST-GPU-INJECTION-03`
- Status: `PASS`
- Linked finding: `FINDING-HOST-GPU-INJECTION-RUNTIME-FLAG-01`
- Started: `2026-09-02T17:39:43Z`
- Finished: `2026-09-02T17:39:44Z`

## Observation

The corrected published sequence executed on the authorized idle Host:

- Host `nvidia-smi -L`: exit `0`, four NVIDIA RTX 6000 Ada Generation GPUs.
- `docker run --rm --runtime=nvidia ... nvidia-smi -L`: exit `0`, the same four GPUs.
- Kernel journal source: exit `0`; filter: exit `0`. Matches are retained privately and are not interpreted as a hardware diagnosis by this attempt.
- Cleanup: zero running containers and zero GPU compute processes after execution; `vastai.service` stayed active.

## Disposition

The corrected current forms of `CLM-2113f9109b2c79c5`, `CLM-2ffc62f260fd8010`, and `CLM-9aa5c400c3ff1241` have functional status `PASS` and semantic score `3`: each executes successfully and directly supports the page's Host/container GPU-injection diagnostic checkpoint.

The parent troubleshooting procedures remain only partially validated. This result does not validate every failure branch, interpret the retained kernel matches, or validate the separate GPU-burn command.

## Retained evidence

| Restricted artifact | SHA-256 |
| --- | --- |
| `run.raw` | `1600a5acb63de9f1f9d4c4c55096b064e60aeb835577609f2ebf0ee7edf2ef84` |
| `run.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Raw evidence remains under `../private-evidence/2026-09-02-host-gpu-injection-attempt-03/` and contains Host-specific identifiers.

## Limitation

This runtime proof applies to the tested Vast Host and the image digest resolved and retained in the earlier linked attempt. It does not establish behavior on arbitrary non-Vast Docker installations or guarantee that a mutable image tag will never change.

After execution, the adjacent explanatory sentence was narrowed to avoid implying that every Host has the same runtime configuration. The tested command text did not change. The plan therefore retains the pre-clarification page hashes while this command-level evidence remains applicable to the identical published command.
