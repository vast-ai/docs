# Multi-arch buildx Makefile for the verification self-test images.
#
# Produces four images on $(IMAGE):
#   make cu118 -> $(IMAGE):self-test-cuda-11.8 (linux/amd64; legacy GPUs/drivers)
#   make cu128 -> $(IMAGE):self-test-cuda-12.8 (linux/amd64,arm64)
#   make cu130 -> $(IMAGE):self-test-cuda-13.0 (linux/amd64,arm64)
#   make cu133 -> $(IMAGE):self-test-cuda-13.3 (linux/amd64,arm64)
#   make all          Build all four
#   make qemu-reset   Reset binfmt/QEMU if multi-arch builds core-dump
#
# Defaults push to the registry. For a local single-platform build:
#   make cu128 OUTPUT=--load PLATFORMS_MODERN=linux/amd64

IMAGE            ?= vastai/test
TAG_PREFIX       ?= self-test-cuda-
BUILDER          ?= multi-arch-builder
OUTPUT           ?= --push

PLATFORMS_LEGACY ?= linux/amd64
PLATFORMS_MODERN ?= linux/amd64,linux/arm64

.PHONY: all cu118 cu128 cu130 cu133 buildx-setup qemu-reset

all: cu118 cu128 cu130 cu133

buildx-setup:
	@docker buildx inspect $(BUILDER) >/dev/null 2>&1 || \
		docker buildx create --name $(BUILDER) --driver docker-container --bootstrap

qemu-reset:
	docker run --privileged --rm tonistiigi/binfmt:latest --uninstall 'qemu-*'
	docker run --privileged --rm tonistiigi/binfmt:qemu-v6.2.0 --install all

cu118: buildx-setup
	docker buildx build \
		--builder $(BUILDER) \
		--platform $(PLATFORMS_LEGACY) \
		--progress=plain \
		--build-arg BASE_IMAGE=ubuntu:22.04 \
		--build-arg CUDA_REPO_DISTRO=ubuntu2204 \
		--build-arg CUDA_VERSION=11.8 \
		-t $(IMAGE):$(TAG_PREFIX)11.8 \
		$(OUTPUT) \
		.

cu128: buildx-setup
	docker buildx build \
		--builder $(BUILDER) \
		--platform $(PLATFORMS_MODERN) \
		--progress=plain \
		--build-arg CUDA_VERSION=12.8 \
		-t $(IMAGE):$(TAG_PREFIX)12.8 \
		$(OUTPUT) \
		.

cu130: buildx-setup
	docker buildx build \
		--builder $(BUILDER) \
		--platform $(PLATFORMS_MODERN) \
		--progress=plain \
		--build-arg CUDA_VERSION=13.0 \
		-t $(IMAGE):$(TAG_PREFIX)13.0 \
		$(OUTPUT) \
		.

cu133: buildx-setup
	docker buildx build \
		--builder $(BUILDER) \
		--platform $(PLATFORMS_MODERN) \
		--progress=plain \
		--build-arg CUDA_VERSION=13.3 \
		-t $(IMAGE):$(TAG_PREFIX)13.3 \
		$(OUTPUT) \
		.
