# Host GPU injection correction attempt 02

- Attempt ID: `ATTEMPT-2026-09-02-HOST-GPU-INJECTION-02`
- Linked finding: `FINDING-HOST-GPU-INJECTION-RUNTIME-FLAG-01`
- Method: execute the daemon-recommended correction on the same authorized idle Host
- Scope: candidate correction only; source wording remains unchanged until this result is known

## Preconditions and safety

The Host must have `vastai.service` active, zero running containers, and zero GPU compute processes. Use the already-resolved CUDA image, `--rm`, and the NVIDIA runtime advertised by Docker. Do not run GPU burn or change Host configuration.

## Candidate command

```bash
nvidia-smi -L
sudo docker run --rm --runtime=nvidia nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi -L
```

## Outcome

- `PASS`: both commands exit `0`, enumerate the same GPU count, no container remains, and the Host returns to idle.
- `FAIL`: the proposed form reaches execution but does not expose the same GPU inventory.
- `BLOCKED`: an external prerequisite prevents execution.

Passing this candidate attempt permits a documentation correction but does not itself mark the old `--gpus all` carriers as PASS. The corrected source must be inventoried and retested as the published form.
