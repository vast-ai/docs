# Host GPU injection published-form retest 03

- Attempt ID: `ATTEMPT-2026-09-02-HOST-GPU-INJECTION-03`
- Linked finding: `FINDING-HOST-GPU-INJECTION-RUNTIME-FLAG-01`
- Retest type: source corrected, then executed
- Source revision: `3b7e56f0db6588953589e0692e75b7274526d5f9` with a dirty worktree
- `host/common-errors-diagnostics.mdx` SHA-256: `e88557ca8c21f404c534f1ec9d37c704baecc2c6c700f504d3e4603dc7f117ba`
- `host/machine-errors.mdx` SHA-256: `80b06b005f4371925d47dccc27cb1d72594de8d4d0e52d28ec79a0bff9f29169`

## Corrected source in scope

- `CLM-2113f9109b2c79c5`: Host/container GPU comparison on `/host/common-errors-diagnostics`
- `CLM-2ffc62f260fd8010`: Host/container/kernel diagnostic sequence on `/host/machine-errors`
- `CLM-9aa5c400c3ff1241`: Host/container GPU comparison on `/host/machine-errors`

The procedure inventory still carries these stable claim IDs while its source hashes are reconciled after execution. This attempt is frozen against the exact source-file hashes above.

## Safety gate

Require the authorized Host to have `vastai.service` active, zero running containers, and zero GPU compute processes. Use the cached CUDA image, `--rm`, and the registered NVIDIA runtime. Do not run GPU burn or change Host configuration. Confirm post-run idle state.

## Exact published sequence

```bash
nvidia-smi -L
sudo docker run --rm --runtime=nvidia nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi -L
sudo journalctl -k -b --no-pager | grep -Ei 'NVRM|Xid|AER|PCIe|fallen'
```

## Outcome rules

- `PASS`: Host and container commands exit `0`, enumerate the same GPU count, kernel journal access succeeds, no container remains, and the Host returns to idle.
- `FAIL`: the corrected source form executes but does not produce the expected GPU-injection behavior.
- `BLOCKED`: an external prerequisite prevents execution.

Command-level PASS supports only the stated diagnostic behavior on the tested Host. It does not pass the full troubleshooting procedures or validate the separate GPU-burn branch.
