# Two-account V&V readiness — retained result

Scope: user-selected RTX4090 candidate, HOST-RTX4090-01. PR #185 / CON-1518. This is a prerequisite and bounded API-observation package, not completion of the client-facing claims or the full Host Docs review. The current claim JSON and HTML snapshot have not been regenerated or promoted.

## What is now established

The user-designated macOS Keychain entry was retrieved without displaying or copying the secret. At `2026-09-08T14:18:56.703Z`–`14:18:57.936Z`, GET `/api/v0/users/current/` and GET `/api/v0/machines/?owner=me` on `https://console.vast.ai` both returned HTTP 200. The owned-machine response contained four machines, including the user-selected candidate with four RTX 4090 GPUs and `verification: unverified`. These identity/hardware fields match the candidate row previously observed on the authenticated dashboard. The identity is retained as a digest; private IDs are omitted from this shareable record.

**PASS, bounded:** the supplied credential authenticates and can read the candidate through the Host owned-machine inventory. See [retained API retest](host-api-retest-02.json). No explicit boolean Host-role field was returned in the whitelisted projection; Host access is established by the successful owned-machine request, not an invented role flag. No running/stored fields were present in the retained API projection, so it cannot corroborate dashboard occupancy counts.

## Failures, correction and retest

- Preserve [first API attempt](host-api-first-attempt.json): the no-redirect client rejected the initial source-derived URLs without trailing slashes. Credential-free diagnostics at `14:18:25.929Z` and `14:18:26.162Z` returned 301 to the same-origin `/api/v0/users/current/` and `/api/v0/machines/` paths. The machines redirect retained a query. Only these trailing-slash destinations were used for the new retest, which returned 200. No general redirect following or credential-in-URL workaround was introduced. The first attempt's coarse error label and UNVALIDATED_TARGET_ACCESS are retained; the diagnosis is request routing, not failed credentials or a product defect.
- [SSH readiness](ssh-readiness.json) exited 255 before remote execution: no trusted ED25519 key for this new target. GPU/CLI checks and default client-key presence checks did not run. Do not interpret this as an absent CLI or key. No trust store was changed.
- The earlier H100 has a different constraint: the default SSH user cannot access its Docker socket. See [separate H100 attempt](../2026-09-08-host-instance-correlation-attempt-01/result.md). Neither target's observation proves the other target.
- Repository orientation first tried an absent `sources` directory; the read-only search was corrected to the actual local canonical Vast CLI checkout. This did not affect the runtime checks. The accessibility-delta extraction limitation is retained in the H100 result.

## What the two accounts can help us validate next

These are exact current inventory candidates, not promised closures. Required implementation/source lanes still need suitable sources. An API request is not proof that an exact CLI command ran successfully.

| Page / heading | Claim | Next suitable check | Current limit |
| --- | --- | --- | --- |
| Fleet Operations / Fleet State | MCL-f0b9b724554ce68a — `vastai show machines --raw` | Run the documented command with the Host credential in an isolated, known CLI environment; compare the selected machine with the retained API/dashboard identity. | Host API observation now available; exact CLI command not run. |
| Why Isn't My Machine in Search? / Check the machine directly | MCL-728ef13be833d21e — `vastai search offers 'machine_id=<machine_id>' --limit 200` | With the verified client key, run the exact documented default-filter search for this candidate and retain results; preserve any empty result before changing filters. | Client key/account not accessed. Candidate is unverified, while inspected CLI default search includes `verified=true`; this is an explicit test hypothesis, not an observed failure. |
| First 24 Hours After Install / Test Like A Client | MCL-323c8fb8180f5f62 — `vastai show machines` | Compare documented Host inventory command under both accounts and assess its placement after “List visible machines/offers”. | Do not silently replace it with offer search and call the original command validated. |
| GPU Market Metrics / Access | CUR-faec8c1dd6547ae5 — non-Host account access/401 guidance | Compare authorized read-only access with each account; no registration or permission mutation. | Account-scoped observations cannot prove a universal account rule. |
| First 24 Hours After Install / Test Like A Client | MCL-e6fb82f7e167fdc8 — rent a small test instance on the Host | Explicitly approved single rental binding client account, exact offer, Host and resulting instance. | No paid/lifecycle authorization, spending limit or cleanup scope yet. |
| First 24 Hours After Install / Test Like A Client | MCL-92edb99129fc96c9 — instance appears in the client account | Retain matching client API/UI observation for that same approved instance. | No client instance has been created or inspected. |
| First 24 Hours After Install / Test Like A Client | MCL-da591d84b7d08317 — destroy test instance / connection troubleshooting | Destroy only the specifically authorized test instance and independently confirm its absence. | Cleanup proof would not validate an unencountered SSH/Jupyter failure branch. |

The exact documented creation example uses a mutable image and Jupyter/direct ports. A safer, different workload would validate a separately bounded lifecycle, not that exact example. GPU computation and self-test require their own approved representative workload and evidence; a running instance alone is insufficient.

## Separate workstreams and missing prerequisites

**Runtime/operator:** verify the new server's ED25519 fingerprint via a trusted console, then establish trust deliberately; inspect only the exact configured CLI credential location and verify client identity. Alternatively provide a specifically identified secure local client-key entry so read-only client API checks need not wait for SSH. Before any rental, agree exact offer/workload, GPU/storage allocation, maximum spend and duration, monitoring and permission to destroy only the newly created test instance. Recheck occupancy immediately before any workload-affecting operation. No sudo, paid test or mutation has run.

**Source/owner confirmation:** the introductory marketplace claim `MCL-e12ac9f6be2ce502` is still UNVALIDATED in the current report. Its runtime-only classification needs reconsideration and suitable authoritative product evidence binding; a paid rental is unnecessary solely for that concept. Finance/Legal claim `CUR-86b30052c0aa0b9c` about VAT remains FAIL pending authoritative evidence/citation; accounts do not solve it. Verification enforcement claim `CUR-4d045dd2542b936b` needs source evidence; do not enable password login to manufacture a test.

## Provenance and limitations

Canonical CLI source SHA/revision and clean path status are recorded in [ssh-readiness.json](ssh-readiness.json). HTTP methods and paths are source-derived, but the CLI was not executed. Whitelisted outputs and response digests are retained; full responses were deliberately discarded because they can contain private account/renter data. A digest alone cannot let a reviewer recover excluded fields. The same agent performed and recorded the checks; a second agent independently reviewed closure criteria and mapped the exact claim candidates, but did not re-execute API requests.

No API key value, email, private SSH key, raw machine/instance ID, renter payload or billing data was retained. No rental, self-test, Host change, credential rewrite, Git push, Jira post or acceptance occurred. Original failure records remain. The broad Host Docs issues have not all become external blockers merely because these prerequisites are now concrete.

Package sanitation first found a numeric target ID in the plan introduction: [failed package check](package-check-01.json). The plan was corrected to the public alias without duplicating the private value in the failure log. A separate package retest checks JSON parsing, relative links, the ten mapped claim IDs, identifier sanitation, and preservation of the current claim package/index/staged diff. These package checks do not validate product behavior.
