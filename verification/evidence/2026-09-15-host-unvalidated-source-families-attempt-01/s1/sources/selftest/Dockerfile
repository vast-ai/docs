ARG BASE_IMAGE=ubuntu:24.04
ARG CUDA_VERSION=12.8
# Path segment under developer.download.nvidia.com/compute/cuda/repos for the
# CUDA apt repo. Must match BASE_IMAGE: ubuntu:22.04 -> ubuntu2204,
# ubuntu:24.04 -> ubuntu2404. CUDA 11.8 packages only live under ubuntu2204.
ARG CUDA_REPO_DISTRO=ubuntu2404

# PyTorch package sets. CUDA_VERSION picks one:
#   11.8 -> torch 2.7.1  (older R450+ drivers, pre-sm_70 Pascal/Maxwell)
#   12.8 -> torch 2.10.0 (last cu128 wheel line with sm_70; 2.11 dropped
#                         Volta to take cuDNN 9.15.1)
#   13.0 -> torch 2.11.0 (cu130 wheels never included sm_70)
#   13.3 -> torch 2.12.0 (latest CUDA-13 wheel line is cu132; no cu133
#                         wheel index is published yet)
# CUDA 12.8+ pins are >= 2.7 so Blackwell (sm_100/sm_120) stays in.
ARG PYTORCH_VERS_118="torch==2.7.1 torchvision==0.22.1"
ARG PYTORCH_VERS_128="torch==2.10.0 torchvision==0.25.0"
ARG PYTORCH_VERS_130="torch==2.11.0 torchvision==0.26.0"
ARG PYTORCH_VERS_133="torch==2.12.0 torchvision==0.27.0"
ARG PYTORCH_INDEX_118="cu118"
ARG PYTORCH_INDEX_128="cu128"
ARG PYTORCH_INDEX_130="cu130"
ARG PYTORCH_INDEX_133="cu132"

FROM ${BASE_IMAGE} AS builder

ARG CUDA_VERSION
ARG CUDA_REPO_DISTRO
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Install the NVIDIA CUDA apt repo and just the toolkit bits gpu-burn needs
# (nvcc, cudart-dev, cublas-dev). Arch-aware: amd64 -> x86_64, arm64 -> sbsa.
RUN \
    set -euo pipefail && \
    apt-get -y update && apt-get -y upgrade && \
    apt-get -y install --no-install-recommends \
        ca-certificates \
        build-essential \
        wget \
        git && \
    ARCH="$(dpkg --print-architecture)" && \
    case "$ARCH" in \
        amd64) CUDA_REPO_ARCH=x86_64 ;; \
        arm64) CUDA_REPO_ARCH=sbsa ;; \
        *) echo "Unsupported arch: $ARCH" >&2; exit 1 ;; \
    esac && \
    wget -q "https://developer.download.nvidia.com/compute/cuda/repos/${CUDA_REPO_DISTRO}/${CUDA_REPO_ARCH}/cuda-keyring_1.1-1_all.deb" -O /tmp/cuda-keyring.deb && \
    dpkg -i /tmp/cuda-keyring.deb && \
    rm /tmp/cuda-keyring.deb && \
    apt-get update && \
    apt-get -y install --no-install-recommends \
        cuda-nvcc-${CUDA_VERSION/./-} \
        cuda-cudart-dev-${CUDA_VERSION/./-} \
        libcublas-dev-${CUDA_VERSION/./-} && \
    cd / && \
    # Pin gpu-burn to a known commit so identical Dockerfiles produce
    # identical binaries and an upstream account compromise can't slip
    # tampered code into the next rebuild of any vastai/test:self-test-*
    # image. Bump the SHA deliberately when a new upstream change is needed.
    git clone https://github.com/wilicc/gpu-burn && \
    cd gpu-burn && \
    git checkout 671f4be92477ce01cd9b536bc534a006dbee058f && \
    # Pick the lowest compute capability each image needs to run on so the
    # JIT-resolved compare.ptx is forward-compatible to every GPU the image
    # targets. Upstream gpu-burn defaults to COMPUTE=75 (Turing), which
    # leaves Maxwell/Pascal/Volta unable to JIT the PTX at runtime.
    case "${CUDA_VERSION}" in \
        11.8) COMPUTE=50 ;; \
        12.8) COMPUTE=70 ;; \
        13.0) COMPUTE=75 ;; \
        13.3) COMPUTE=75 ;; \
        *) echo "Unsupported CUDA_VERSION: ${CUDA_VERSION} (expected 11.8, 12.8, 13.0, or 13.3)" >&2; exit 1 ;; \
    esac && \
    CUDAPATH=/usr/local/cuda-${CUDA_VERSION} COMPUTE=${COMPUTE} make

FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /verification
COPY --from=builder /gpu-burn/gpu_burn .
COPY --from=builder /gpu-burn/compare.ptx .

ARG BASE_IMAGE
ARG CUDA_VERSION
ARG CUDA_REPO_DISTRO

# Base packages + NVIDIA CUDA apt repo + the CUDA runtime libs gpu_burn
# dynamically links (libcudart, libcublas). openssl is needed by remote.py
# to generate the HTTPS server cert at startup. python3 (no version suffix)
# picks up whatever the distro ships: 3.10 on 22.04, 3.12 on 24.04.
RUN \
    set -euo pipefail && \
    apt-get -y update && apt-get -y upgrade && \
    apt-get -y install --no-install-recommends \
        ca-certificates \
        wget \
        openssl \
        python3 \
        python3-pip \
        stress-ng && \
    # PEP 668 is enforced on Ubuntu 24.04's python3-pip; drop the marker so
    # `pip install` works without --break-system-packages. No-op on 22.04.
    rm -f /usr/lib/python3*/EXTERNALLY-MANAGED && \
    ARCH="$(dpkg --print-architecture)" && \
    case "$ARCH" in \
        amd64) CUDA_REPO_ARCH=x86_64 ;; \
        arm64) CUDA_REPO_ARCH=sbsa ;; \
        *) echo "Unsupported arch: $ARCH" >&2; exit 1 ;; \
    esac && \
    wget -q "https://developer.download.nvidia.com/compute/cuda/repos/${CUDA_REPO_DISTRO}/${CUDA_REPO_ARCH}/cuda-keyring_1.1-1_all.deb" -O /tmp/cuda-keyring.deb && \
    dpkg -i /tmp/cuda-keyring.deb && \
    rm /tmp/cuda-keyring.deb && \
    apt-get update && \
    apt-get -y install --no-install-recommends \
        cuda-cudart-${CUDA_VERSION/./-} \
        libcublas-${CUDA_VERSION/./-} && \
    apt-get -y purge wget && \
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV LD_LIBRARY_PATH=/usr/local/cuda-${CUDA_VERSION}/lib64

ARG PYTORCH_VERS_118
ARG PYTORCH_VERS_128
ARG PYTORCH_VERS_130
ARG PYTORCH_VERS_133
ARG PYTORCH_INDEX_118
ARG PYTORCH_INDEX_128
ARG PYTORCH_INDEX_130
ARG PYTORCH_INDEX_133

RUN \
    set -euo pipefail && \
    case "${CUDA_VERSION}" in \
        11.8) PYTORCH_VERS="${PYTORCH_VERS_118}"; PYTORCH_INDEX="${PYTORCH_INDEX_118}" ;; \
        12.8) PYTORCH_VERS="${PYTORCH_VERS_128}"; PYTORCH_INDEX="${PYTORCH_INDEX_128}" ;; \
        13.0) PYTORCH_VERS="${PYTORCH_VERS_130}"; PYTORCH_INDEX="${PYTORCH_INDEX_130}" ;; \
        13.3) PYTORCH_VERS="${PYTORCH_VERS_133}"; PYTORCH_INDEX="${PYTORCH_INDEX_133}" ;; \
        *) echo "Unsupported CUDA_VERSION: ${CUDA_VERSION} (expected 11.8, 12.8, 13.0, or 13.3)" >&2; exit 1 ;; \
    esac && \
    pip3 install --no-cache-dir --upgrade psutil && \
    pip3 install --no-cache-dir ${PYTORCH_VERS} --index-url "https://download.pytorch.org/whl/${PYTORCH_INDEX}" && \
    rm -rf /root/.cache/pip /tmp/* /var/tmp/*


# Copy the test scripts into the container
COPY remote.py .
COPY remote.sh .
COPY eccfunction.py .
COPY testAllGpusResNet50.py .
COPY systemreqtest.py .
COPY test_NCCL.py .

# Define the command to run when the container is started
CMD ["/verification/remote.sh"]
