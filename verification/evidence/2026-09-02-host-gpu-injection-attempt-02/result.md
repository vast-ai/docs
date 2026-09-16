# Host GPU injection correction attempt 02 result

- Attempt ID: `ATTEMPT-2026-09-02-HOST-GPU-INJECTION-02`
- Status: `PASS`
- Linked finding: `FINDING-HOST-GPU-INJECTION-RUNTIME-FLAG-01`
- Started: `2026-09-02T17:37:54Z`
- Finished: `2026-09-02T17:37:55Z`

The daemon-recommended `--runtime=nvidia` candidate exited `0` and enumerated the same four NVIDIA RTX 6000 Ada Generation GPUs as the Host command. The Host had zero running containers and zero GPU compute processes before and after the attempt, and `vastai.service` remained active.

This result supported correcting the documentation. It did not promote the old `--gpus all` source carriers; the corrected published form was separately retested in attempt 03.

| Restricted artifact | SHA-256 |
| --- | --- |
| `run.raw` | `37750bc1a311bfe4829107ff0e272373333fbc3e8c092496b2835ac3ef74ceb8` |
| `run.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Raw evidence remains under `../private-evidence/2026-09-02-host-gpu-injection-attempt-02/` and contains Host-specific identifiers.
