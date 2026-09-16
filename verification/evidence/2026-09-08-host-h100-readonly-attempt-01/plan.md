# Host H100 read-only access observation

## Scope and authority

The user supplied a specific Host SSH destination and identity file in this
conversation and authorized SSH access. Use that destination only, identified
in shareable evidence as HOST-H100-01. This is a bounded PLAN_AND_EXECUTE
observation under vv-evidence, not authorization for maintenance or testing
workloads. The screenshot shows a stored instance; no stored-instance contents
or renter data will be accessed.

Related claim: MCL-e12ac9f6be2ce502, Hosting Overview / Introduction,
host/hosting-overview.mdx:16:

> Vast is a GPU marketplace. Hosts provide machines; renters run workloads on them.

This check can establish only SSH connectivity and the NVIDIA driver's reported
GPU inventory. It cannot establish the marketplace model, account ownership,
public offer visibility, renter workload execution, or current idle state.
The full claim stays unchanged. The conceptual evidence-requirement correction
and binding discussed previously are separate documentation work.

## Frozen check

- Method: one SSH invocation of `nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader,nounits`.
- Expected: authenticated access to the user-selected Host and eight reported H100 GPUs with driver version(s).
- Access constraints: supplied identity only; BatchMode; StrictHostKeyChecking=yes; no user SSH config, agent forwarding, port forwarding, local command, or TTY; 10-second connection timeout, one connection attempt and 30-second total local execution bound.
- No sudo, installation, API calls, self-test, process/container inspection, benchmarks, service changes, or workload-affecting commands.
- Stop on unknown/changed host key or denied credentials; do not bypass trust or authentication checks.
- Evidence: exact command/options with target/key placeholders, start/end timestamps, target binding digest, SSH exit code and sanitized stdout/stderr. The private target mapping is the supplied destination in this conversation; it is not included in the shareable record.
- PASS is limited to an observation matching the frozen expected result. FAIL records a mismatch or failed available check; BLOCKED records a concrete unavailable connection/authentication/trust prerequisite. No outcome promotes the full documentation claim.

## Pre-execution repository identity (2026-09-08T13:44:10.329Z)

- HEAD: bfa926c9421521767fa7411718bd31ea38b38528; branch CON-1584-host-cli-api-sdk.
- Index SHA-256: f94031ce155dabaf4a0c8cf60f50f22c76d68a38209b3502ce535c93e157310b.
- Full porcelain state SHA-256: 71388b10e42d4fcdb759ffd9b279ace1ca92e95425533e3cdf459e5ced89b740.
- Staged diff SHA-256: f59f3c12986c4a1750dbae920803828221b9f4d63b7104c5932e9b0ac5372803.
- Unstaged tracked diff: empty.
- Claim package SHA-256: 24492ac5b4c3059478d311c6d99733ebadad37255d0e570295c17605ab42f031.
- Supplied key file exists; its contents were not displayed or copied.

Independent read-only agent review agreed this query is proportionate and does
not require an idle Host. It reiterated the limited GPU-identity claim and the
requirement to stop on any host-key mismatch. No human acceptance is recorded.
