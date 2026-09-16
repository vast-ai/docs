# Host GPU injection attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-HOST-GPU-INJECTION-01`
- Frozen: 2026-09-02
- Source revision: `3b7e56f0db6588953589e0692e75b7274526d5f9`
- Worktree: dirty; the exact Host Docs test-set snapshot is recorded below
- Test-set SHA-256: `4a94a7f98a8a6a4db344e46b7b314c68af125f97474f08f01bae0d542b21a42c`
- Target: authorized idle Vast Host; exact identity is retained only in restricted evidence

## Scope

Validate the Host-to-container GPU visibility sequence used by:

- `CLM-2113f9109b2c79c5` on `/host/common-errors-diagnostics`
- `CLM-2ffc62f260fd8010` on `/host/machine-errors`
- `CLM-9aa5c400c3ff1241` on `/host/machine-errors`

The attempt checks whether the documented commands run on this representative installed Host and whether the Host and container report the same GPU inventory. It does not prove that the mutable image tag will behave identically in the future or that these commands diagnose every possible NVIDIA runtime failure.

## Preconditions and safety gate

- Root SSH access is available.
- `vastai.service` is active.
- No running containers and no GPU compute processes are present immediately before execution.
- Docker advertises the `nvidia` runtime.
- The image is not currently cached, so Docker may download and retain image layers.
- Do not run GPU burn, stress, VM, storage, service-restart, offer, or maintenance commands.
- Use `--rm`; verify that no test container remains and that the Host returns to idle.

## Exact execution sequence

```bash
nvidia-smi -L
sudo docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi -L
sudo journalctl -k -b --no-pager | grep -Ei 'NVRM|Xid|AER|PCIe|fallen'
```

The kernel-log grep may exit `1` when no matching lines exist. That means “no matches,” not failure to access the log. Its status and output are retained separately from the GPU-injection result.

## Outcome rules

- `PASS`: Host `nvidia-smi -L` exits `0`; the ephemeral container exits `0`; both enumerate the same GPU count; no test container remains; the Host returns to zero running containers and zero GPU compute processes.
- `FAIL`: the documented GPU-injection command runs in the authorized environment but exits nonzero, reports an invalid NVIDIA runtime, or exposes a materially different GPU inventory.
- `BLOCKED`: image retrieval, registry/network access, authorization, active work, or another prerequisite prevents the documented command from reaching its diagnostic behavior.

Raw stdout, stderr, exit statuses, resolved image identity, and pre/post state are retained under the restricted evidence root. Public evidence contains only sanitized observations and hashes.
