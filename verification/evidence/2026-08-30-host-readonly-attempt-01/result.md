# Host Docs read-only Host attempt 01 — result

- Attempt state: `NOT_EXECUTED`
- V&V status: `BLOCKED`
- Blocker class: `NETWORK_UNREACHABLE`
- Target: restricted alias `HOST_VV_TARGET`
- SSH exit code: `255`
- Plan SHA-256: `c6f18d0fceaeea862f0c994d2b623cae4c5c5cc7b29415f6fceeaa1612a10429`
- Raw stdout SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Raw stderr SHA-256: `6a44025611d3c35e7ee32f83279313d950378ceba38c6e2e8ecf66bc71d11dd3`
- Raw artifact permissions: mode `0600`, outside Git

The SSH transport to the supplied private Host address timed out before authentication.
No remote shell opened and no planned Host check ran. This result blocks only the
read-only Host attempt; it is not a Host Docs command failure, runtime PASS, or evidence
about sudo, services, Docker, GPU, storage, logs, or configured ports.

Required retest condition: run from a network context with a route to the private Host
address (for example the relevant LAN/VPN/jump path), without changing the frozen plan.
Local Host-account CLI/API and static test sets continue independently.
