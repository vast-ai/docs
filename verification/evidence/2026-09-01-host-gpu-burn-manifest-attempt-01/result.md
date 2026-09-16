# GPU-burn example registry inspection — attempt 01

- Attempt ID: `ATTEMPT-2026-09-01-HOST-GPU-BURN-MANIFEST-01`
- Evidence ID: `EV-DIA-E03-GPU-BURN-MANIFEST-01`
- Procedure: `TS-DIA-E03`
- Command carrier: `CLM-1112ca628ad4639f`
- Method: unauthenticated read-only Docker Hub repository, manifest, and image-config
  inspection
- Repository revision: `7a8a2c4c571dcf64341055e8277083e5aea380bf`
- Test-set snapshot SHA-256:
  `a61a9f23ff2e24c6daf8763c123efcf1190715045037e0b202d09e4ac1f3ea77`
- Container pull, container run, GPU load, Host access, or state change: none

## Observation

The current `oguzpastirmaci/gpu-burn:latest` Docker Hub manifest resolves to one Linux
`amd64` image with manifest digest
`sha256:e83916e562e22c5d01ad9bc89936f5e196cb3d70b64e14de01004d1525a93444`
and config digest
`sha256:df68b27f38d15e6b7973f6c5db6e810b76b687c3e75c8feb5f594428398c9fbd`.
The image config was created on 2022-12-02, declares `./gpu_burn` as its entrypoint, and
declares `60` as its default command. This supports the documented trailing `60` argument
as a structurally meaningful duration form for the image observed at inspection time.

## Disposition

The exact runtime command remains `BLOCKED` and is not promoted to execution `PASS`.
The page uses a mutable third-party tag, the image was not pulled or independently
reviewed, no idle/load authorization was exercised, and no thermal, power, diagnostic,
or cleanup result exists. The static registry result gives the command partial semantic
support only; it cannot prove safe or correct Host behavior.

## Claim limits

Docker tags are mutable. This observation applies only to the exact manifest and config
digests above at the recorded inspection time. It is not an endorsement of the image,
does not establish source provenance, and does not qualify any GPU-load result.
