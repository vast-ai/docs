# Vast.ai self test

These docker images are pulled by the CLI self-test command:

```
vastai self-test machine <machine_id>
```

The CLI picks the newest image that is not newer than the host's CUDA driver version and
compute capability — see `cuda_map_to_image` in vast-cli for the routing
rules. Four images are published:

| Tag | torch | Targets | Platforms |
| --- | --- | --- | --- |
| `vastai/test:self-test-cuda-11.8` | 2.7.1 | Pre-sm_70 (Maxwell, Pascal); older R450+ drivers | linux/amd64 |
| `vastai/test:self-test-cuda-12.8` | 2.10.0 | sm_70+ (Volta and newer); current default | linux/amd64, linux/arm64 |
| `vastai/test:self-test-cuda-13.0` | 2.11.0 | sm_75+ (Turing and newer); cu130 wheels never shipped sm_70 | linux/amd64, linux/arm64 |
| `vastai/test:self-test-cuda-13.3` | 2.12.0 | sm_75+ (Turing and newer); CUDA 13.3 runtime with latest available CUDA-13 PyTorch wheels (`cu132`) | linux/amd64, linux/arm64 |

PyTorch currently publishes CUDA 13.2 (`cu132`) wheels, not a `cu133` wheel
index. The CUDA 13.3 image therefore installs CUDA 13.3 system/gpu-burn
packages from NVIDIA's apt repo and the latest available CUDA-13 PyTorch wheel
line from `https://download.pytorch.org/whl/cu132`.

Test scripts are adapted from https://github.com/jjziets/VastVerification.

## Runtime source

The `remote.py` and `remote.sh` runtime files are required by the Dockerfile and
are the entrypoint used by the Vast CLI self-test flow. They were restored from
the public image family so this repo can rebuild the current runtime source
before adding new structured progress work.

## Progress endpoints

The runtime keeps legacy CLI behavior on `GET /progress`: in-flight output is
plain text, success ends as exactly `DONE`, and failure ends with the existing
`ERROR N: ...` style message.

Structured consumers can also read:

| Endpoint | Format | Notes |
| --- | --- | --- |
| `/progress.jsonl` | newline-delimited JSON | Append-style event stream with `schema_version`, `run_id`, monotonic `sequence`, `timestamp`, `event_type`, `stage`, `status`, context fields, output tails, remediation, and `doc_id`. |
| `/summary.json` | JSON | Current/final summary keyed by run id and stage, including overall status and exit code once complete. |

The JSONL stream emits the stages `image_started`, `system_requirements`,
`resnet`, `ecc`, `nccl`, `stress_gpu_burn`, and `final_summary`. The local files
`progress.log`, `progress.jsonl`, and `summary.json` are also written in
`/verification` for container-side triage.

Lightweight validation that does not run live Vast commands:

```
python3 -m py_compile remote.py
bash -n remote.sh
docker buildx build --check --platform linux/amd64 --build-arg CUDA_VERSION=13.3 .
```

Source image details captured during recovery:

| Tag | Platform | Image digest |
| --- | --- | --- |
| `vastai/test:self-test-cuda-11.8` | `linux/amd64` | `sha256:3f8bfa9549696038728f67bc30fde0ff5c3d3d9ca97a1e102d52af12c1612957` |
| `vastai/test:self-test-cuda-12.8` | `linux/amd64` | `sha256:e284ff73f2f8fc89e2d139e41f095e57279238854919976fce2b560045d4caf5` |
| `vastai/test:self-test-cuda-12.8` | `linux/arm64` | `sha256:4d0bd8ebfc2625de15c93597212c59459f37710f0eaba4a34cef59619b6a7a38` |
| `vastai/test:self-test-cuda-13.0` | `linux/amd64` | `sha256:d53794528c4c0c84b9d213a973ef84c7a37152fa8dcb36f80fdf43ef65e479a6` |
| `vastai/test:self-test-cuda-13.0` | `linux/arm64` | `sha256:5b1094280d5b05bba2e30ee512c982e8e0e6428fe6df28ca37acbf2fd2111c80` |

The linux/amd64 variants for CUDA 11.8, 12.8, and 13.0 were extracted and the
six tracked `/verification` source files match this repo byte-for-byte. For the
CUDA 12.8 and 13.0 arm64 variants, registry layer digests show the source-copy
layers are identical to their amd64 counterparts.

## Building

A Makefile handles the buildx builder, multi-arch QEMU setup, and the
per-CUDA-version build args:

```
make cu118        # cuda-11.8 image (linux/amd64)
make cu128        # cuda-12.8 image (linux/amd64,arm64)
make cu130        # cuda-13.0 image (linux/amd64,arm64)
make cu133        # cuda-13.3 image (linux/amd64,arm64)
make all          # all four
make qemu-reset   # reinstall binfmt emulators if multi-arch builds core-dump
```

Defaults push to `vastai/test:self-test-cuda-X.Y` via `--push`. Override
with `IMAGE=...`, `TAG_PREFIX=...`, or `OUTPUT=--load` for a single-platform
local build.

## GitHub Actions CI/CD

The `Self-test Images` workflow validates image sources on pull requests and
pushes to `main`/`CON-*` branches. It also provides a manual build/publish path
through GitHub-hosted runners:

1. Open GitHub Actions for `vast-ai/self-test`.
2. Run `Self-test Images`.
3. Choose one CUDA version or `all`.
4. Keep the default image/tag family for the v2 CLI flow:
   - image: `vastai/test`
   - tag prefix: `self-test-v2-cuda-`
5. Leave `push=false` for a runner-only build check.
6. Set `push=true` only when Docker Hub secrets are configured.

Publishing requires these repository or organization secrets:

| Secret | Purpose |
| --- | --- |
| `DOCKERHUB_USERNAME` | Docker Hub account or organization user with push access |
| `DOCKERHUB_TOKEN` | Docker Hub access token for that account |

The workflow builds:

| CUDA | Platforms |
| --- | --- |
| `11.8` | `linux/amd64` |
| `12.8` | `linux/amd64,linux/arm64` |
| `13.0` | `linux/amd64,linux/arm64` |
| `13.3` | `linux/amd64,linux/arm64` |

If Vast GitHub runner access is unavailable, the same images can still be built
from a local Docker buildx builder:

```
make all IMAGE=vastai/test TAG_PREFIX=self-test-v2-cuda-
```

For a smaller local fallback from an Apple Silicon Mac, restrict modern images
to amd64 while testing:

```
make cu128 IMAGE=vastai/test TAG_PREFIX=self-test-v2-cuda- PLATFORMS_MODERN=linux/amd64
```

## Build args

The Dockerfile starts from a plain Ubuntu base (no `nvidia/cuda:*`
images) and installs only the CUDA toolkit pieces it needs from NVIDIA's
apt repo (`developer.download.nvidia.com/compute/cuda/repos/...`).
Architecture is detected at build time so multi-arch `linux/amd64` +
`linux/arm64 (sbsa)` builds work out of the box for CUDA 12.8, 13.0, and 13.3.

| Arg | Default | Notes |
| --- | --- | --- |
| `BASE_IMAGE` | `ubuntu:24.04` | Set to `ubuntu:22.04` for the cu118 build |
| `CUDA_VERSION` | `12.8` | One of `11.8`, `12.8`, `13.0`, `13.3` |
| `CUDA_REPO_DISTRO` | `ubuntu2404` | Must match the base — `ubuntu2204` for the cu118 build (NVIDIA only ships CUDA 11.8 packages under the 22.04 path) |
| `PYTORCH_VERS_118` | `torch==2.7.1 torchvision==0.22.1` | Used when `CUDA_VERSION=11.8` |
| `PYTORCH_VERS_128` | `torch==2.10.0 torchvision==0.25.0` | Used when `CUDA_VERSION=12.8`. Stays on 2.10 because 2.11 dropped sm_70 from cu128 wheels |
| `PYTORCH_VERS_130` | `torch==2.11.0 torchvision==0.26.0` | Used when `CUDA_VERSION=13.0` |
| `PYTORCH_VERS_133` | `torch==2.12.0 torchvision==0.27.0` | Used when `CUDA_VERSION=13.3` |
| `PYTORCH_INDEX_133` | `cu132` | PyTorch's latest CUDA-13 wheel index at time of writing; no `cu133` wheel index is published |

## Manual build (without make)

```
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --build-arg CUDA_VERSION=12.8 \
    -t vastai/test:self-test-cuda-12.8 \
    --push \
    .
```

For the cu118 image, also pass `--build-arg BASE_IMAGE=ubuntu:22.04` and
`--build-arg CUDA_REPO_DISTRO=ubuntu2204`, and restrict `--platform` to
`linux/amd64` — NVIDIA does not publish CUDA 11.8 packages for sbsa/arm64.
