# Runtime/operator work — not complete

## Current blocker: sudo authentication

**BLOCKED:** the approved SSH login works, but both `sudo -n true` and the privileged SSH-policy check returned exit 1, `sudo: a password is required`. See [actual observations and corrected disposition](preflight-02.json). The user supplied a replacement setup token and approved the direct route; neither a missing route choice nor an absent setup token is the current blocker. Token validity remains untested.

Responsible role: authorized operator / credential custodian for the new H100×4 host. Provide the exact approved credential-store entry (metadata only) or enter the sudo password at a controlled hidden prompt. Do not broaden sudo policy or switch to an older root/clientadmin access path to bypass authentication. The referenced September 8 rebuild record describes password-required sudo; no exact credential-store entry was identified in the referenced runbook/rebuild pages.

Impact: Docker/Vast installation, registration, embedded diagnostics, post-install proof, listing and price/expiry readback have **not run**. No host reboot, remote file write, package operation, rental, API/setup-token use or change to other hosts occurred. The two sudo checks did not authenticate; normal SSH/sudo access logs may record these checks.

Once authentication is available: refresh exact identity/boot/occupancy/storage and SSH policy; use the reviewed direct variant and a still-valid setup token; capture installation exit and postconditions; retain downstream identities; only then consider the approved listing with independent readback. Stop on actual unexpected state, failed diagnostics or unsafe fallback. Public-self connectivity and final host acceptance remain separate unfinished work; no reboot is authorized here.

## Not proved by this attempt

- Stock TUI or unchanged current standard installer behavior.
- Marketplace self-test, rented workload performance, network reflection, or final acceptance.
- Persisted listing terms and expiry (listing never attempted).
- XFS quota enforcement under load (mount options were observed only).

The repository/interface update is tracked in [result.md](result.md); it is not a runtime completion claim.
