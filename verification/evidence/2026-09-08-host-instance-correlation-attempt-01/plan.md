# Existing Host instance correlation — attempt 01

Mode: PLAN_AND_EXECUTE. Claim: MCL-e12ac9f6be2ce502, `/host/hosting-overview`, Introduction, source line 16: “Vast is a GPU marketplace. Hosts provide machines; renters run workloads on them.” Documentation wording is the claim, not evidence for itself.

## Authorization and boundary

The user authorized SSH to their specified H100 Host and now explicitly asks to check whether an existing instance is running and matches their dashboard. Use target alias HOST-H100-01; no raw account/network/machine/instance identifiers in shareable evidence. The target/key binding digest from the earlier read-only attempt is `3ddc7f5b60bf8bfda68925b4476547978b99316b948be3929749ba6914a64364`. Do not copy private key contents.

Only observe the authenticated Host Machines page and execute `docker ps --all --format '{{.ID}}\t{{.Names}}\t{{.State}}'` through SSH with strict host-key checking, no forwarding, no sudo and a 30-second limit. If necessary, an equivalent default-user container listing is a read-only check, not permission to inspect renter data. Do not read container contents, environment, commands, logs or mounts. Do not create, start, stop, change or delete instances, test the machine, modify host trust, or use a client key. The conditional suggestion of a paid rental has no agreed spend, duration or cleanup bounds.

## Baseline before plan edits

Captured 2026-09-08T14:10:03.544Z. HEAD `bfa926c9421521767fa7411718bd31ea38b38528`; branch `CON-1584-host-cli-api-sdk`.

- Index SHA-256: `f94031ce155dabaf4a0c8cf60f50f22c76d68a38209b3502ce535c93e157310b`.
- Porcelain status SHA-256: `b0285d247806d4ced13c064cec09a416a4a1b1dbc2c09cbc5968cab03503c5b4`.
- Staged diff SHA-256: `f59f3c12986c4a1750dbae920803828221b9f4d63b7104c5932e9b0ac5372803`.
- Unstaged tracked diff SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Current claim package SHA-256: `24492ac5b4c3059478d311c6d99733ebadad37255d0e570295c17605ab42f031`.

Existing historical attempts, current claim status and HTML export remain unchanged. Known client-key environment variables were checked for presence only and were absent; no credential contents or personal stores were searched.

## Checks and decisions

1. Observe live dashboard Running/Stored counts for HOST-H100-01, with timestamp. Retain a minimal redacted excerpt, never unrelated account/browser content. A screenshot supplied earlier is historical, not the current result.
2. Read only Docker ID/name/state, record exit code, timestamp, limitations and pseudonymized identifiers. A permission/tool/trust failure is a specific unavailable prerequisite, not evidence of no instances.
3. Compare same-target counts and identifiers only when visible and interpretable. Count agreement alone is not an exact instance match. A running system container is not a renter instance; a stored/exited instance is not a running workload.
4. Report independently observed listing/storage/running-state facts separately from actual workload execution. Do not promote the whole claim merely because SSH works, GPUs exist, or Docker lists a running container.

PASS is bounded to a successfully observed fact or independently supported identity match. A confirmed contradiction is FAIL with its scope; missing proof of workload execution remains UNVALIDATED. BLOCKED is reserved for an attempted suitable check prevented by a specific unavailable permission, input, environment or authorization. This procedure need not and must not incur a rental charge just to prove a high-level marketplace description.

Responsible role for runtime observation: authorized Host/API operator. A subsequent representative paid workload, if actually required, needs target/offer, securely supplied renter credentials, current occupancy checks, spend/duration limits and cleanup authorization before execution. Official product sources may support the high-level concept separately, but do not prove backend behavior or legal/policy promises.
