# Frozen SSH/Jupyter launch choices

This addendum precedes create. Use the actual modular CLI ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd
console entry with retry=1 (one dispatch, not automatic create retries).

Image: `pytorch/pytorch@sha256:11691e035a3651d25a87116b4f6adc113a27a29d8f5a6a583f8569e0ee5ff897`.
Public registry metadata confirms this is the current latest manifest; the exact
digest is already cached on the host. This pins the page's latest choice without
silently substituting a different image family. The manifest has about 3.66 GB
compressed layers; registry identity is not proof of successful Jupyter startup.

Launch shape: fresh exact-machine one-GPU on-demand offer, disk10 GiB,
`--jupyter --direct --env '-e TZ=PDT -p 22:22 -p 8080:8080'`, unique label
`host-docs-vv-150296-20260909-ssh-jupyter-01`, and `--cancel-unavail`.
No args/onstart override, volume, template, force, listing change or package
installation is added by the operator. Ordinary platform image startup may
install its connection dependencies; retain that limit if relevant.

Before create: fresh Host/API and SSH idle guard, owned client baseline IDs,
distinct accounts, >=USD5 client reserve, registered public-key match, and a
new quote <=USD4.10/hour compute/storage, <=USD0.014/GB each direction, fixed
unchanged expiry1789423200 and exact one-GPU idle/non-bid offer. Retain all.

Cleanup watchdog is a separate process armed before create, with a 15-minute
deadline (inside the approved 20-minute maximum); main stops earlier after
connection evidence, startup failure, price/credit guard failure, customer
arrival or manual finish marker. Deadline process re-reads owned instances and
deletes only the exact new id, machine150296, one GPU and unique label. An
uncertain create is reconciled against the absent-before label, never retried.
Actual readback must confirm absence. No provider-enforced spend cap is claimed.

SSH endpoints come from fresh owned-instance metadata, not a cached ssh-url.
For new container host-key trust, bind public host-key material through the
already pinned Host connection to the exact task-created container before
strict client SSH. Do not disable host-key checks. Inspect only this container's
identity/connection metadata and use a benign deterministic command.

Jupyter authentication token/session stays restricted. Retain a sanitized UI
observation and benign kernel output if available; no account/API token in
URLs shown to reviewers. Client is the local macOS observer over LAN/VPN;
do not claim independent external-network verification.

Normal self-test remains next. Current reliability0.8506588 fails the >0.90
prerequisite; no ignore-requirements override is authorized by this addendum.
Do not let a changing preflight unexpectedly create a rental using an unfunded
Host account. Freeze a fail-closed read-only preflight command separately after
SSH/Jupyter cleanup, retaining a bundle only if the real CLI produces one.
