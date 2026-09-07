# Host Docs lean P1 — read-only Host attempt 01

- Frozen: `2026-08-30T17:26:56Z`
- Docs revision: `09d729e72fbcb2bdd2dead2b9dc5d5e1eeeffcf5`
- Docs tree: `bfe3e9316893a2174b99779ce844e81f014d2b53`
- Page scope: 39 primary Host pages
- Procedure snapshot: 97 procedures / 203 branches / 468 steps
- Instruction classification: 112 logical step groups / 165 command carriers
- Topology snapshot SHA-256: `41f1c65bec8dd1e45d842884915bb117273c7ca018f41b3c3b6c3eb5fefa4599`
- Safe-form classification SHA-256: `3885037c91f99382542c27d48876f814687ef3cfb43a986f7e6c2799d529ee01`
- Author/reconciler limitation: prepared from the already source-reconciled candidate by
  the primary agent; independent reviews found open defects outside this bounded attempt.

## Frozen attempt boundary

This attempt executes only read-only observation commands on the supplied Ubuntu Host.
It covers relevant observation steps in `HWP-C01`, `HWP-E01`, `DAY1-E01`, `DIA-E02`,
`DIA-E03`, `ERR-T02`, `ERR-T03`, `ERR-T04`, and `ERR-T05`. One artifact may support
several steps only through the exact check IDs in `plan.sh`; no result rolls up beyond
its observed branch.

The attempt explicitly excludes installation, package changes, service restart, reboot,
file copy/edit, storage mutation, firewall/router changes, listeners, external probes,
container creation, GPU load, account mutation, credentialed API calls, and paid work.
Those remain `UNVALIDATED` or `BLOCKED`; a clean read-only snapshot cannot pass them.

The exact authored `findmnt / /data0 /var/lib/docker` form is intentionally retained as
one safe read-only check so its real behavior can be assessed. Missing optional services,
prior-boot logs, log files, `/data0`, Docker mount separation, NVSwitch/Fabric Manager,
or matched error lines are observations to classify, not automatic product failures.

Raw stdout/stderr may contain target, network, machine, service, or renter context. Store
it mode `0600` outside Git. Retain in the repository only the plan, hashes, per-check exit
and observation summaries, redacted excerpts needed to support findings, and cleanup
statement. Never retain credentials or the raw supplied target coordinates.

## Stop conditions

Stop immediately if a command requests a password, appears to mutate state, hangs beyond
30 seconds, or reveals a credential. No fallback mutation is permitted. A blocked or
failed check does not prevent unrelated read-only checks from continuing.
