# Direct H100×4 install — attempt 01

PR #185 / CON-1518. PLAN_AND_EXECUTE. Baseline retained before edits in baseline.json; frozen before live checks, 2026-09-08. This is a new authorized execution attempt; earlier preparation failures and limitations remain historical evidence.

## Scope and authority

The user approved the reviewed direct route using the latest replacement setup token and then separate listing. Only the new H100×4 host, pinned SSH identity and host key. No reboot, driver installation, filesystem formatting, partitioning, NAT/firewall edits, libvirt installation, other-host changes, customer workload inspection or separate paid self-test/rental. Normal Docker/Vast installation, service setup, registration and embedded container/NVML/NCCL/speed diagnostics are in scope. Existing XFS/project-quota storage must be reused. No push, merge, ticket post or human acceptance.

The token is supplied but validity is not assumed. Keep secrets out of public evidence, shell history and process command lines where feasible. Use stdin/in-memory handoff, restricted logs, and sanitation. Regular Host API Keychain access is limited to the exact user-named service/account for target readback and listing. No Client API key is needed.

Approved listing: USD 3/GPU-hour on-demand; USD 0.30/GPU-hour minimum bid; USD 0.50/GB-month storage. Expiry 1789423200 (2026-09-14 22:00 UTC / September 15 00:00 South Africa), no later than the approved September 15 ceiling. No separate volume offer. Verify source-defined units and server readback before claiming these terms took effect.

## Frozen checks

| ID | Claim / exact target | Method and expected observation | Limits / failure action |
|---|---|---|---|
| LIVE-01 | Installing Host Software / prerequisites and storage | Strict SSH: approved identity, four H100 GPUs, same boot, mounted and persistent XFS project quota, no Docker/Vast, no GPU processes, sudo available, correct ports from retained operations record | Capture outputs/time/exit. Stop on identity, occupancy, storage or privilege discrepancy. Read-only observations do not prove enforcement. |
| LIVE-02 | Modified direct route / source and invocation | SHA256 4d87c48acc12a15eee1c2793d0631e1d936b2f996bdd50de4ad27b5acdf3d519 from retained original 6b00488ccf837ed6b7b5375270b75db284c3906f6aec832ad9c8573f44eaac6c. Args: [SETUP_TOKEN] --no-driver --no-partitioning --no-libvirt --ports 30000 30499; no other flags | Exact hashes and reviewed paths. Removes only explicit late automatic self-test/listing helper; not stock TUI proof. |
| LIVE-03 | Installing Host Software / installation and embedded diagnostics | Transfer/hash-check candidate in a new restricted temporary directory. Repeat storage/identity guards immediately before sudo execution. Capture actual masked output, exit, timestamps and post-state. | No automatic retry on ambiguous/failed partial install. Inspect actual state first. Preserve downstream-source/digest limits. Setup registration may change server state even if installation later fails. |
| LIVE-04 | After installation / correct target and service | Read numeric machine ID only (never machine secret), four GPU inventory, Docker/Vast state, same boot/storage, diagnostic result and cleanup state | Do not infer workload correctness from service active. Fail/blocked installation may leave partial state; record it. |
| LIVE-05 | Pricing Your Listing / listing controls | Independent canonical CLI/schema contract review, then single target listing only after readiness; Host API readback of price, bid, storage and expiry | Stop on target mismatch or missing readiness. No rental or volume offer. Readback failure is not success. |
| LIVE-06 | Client-facing evidence / exact passage bindings | Preserve previous intake; append exact findings and limitations, update current reviewer and standalone HTML, traceability, separate operator and owner registers | Modified route cannot promote stock wizard, automated marketplace self-test or entire host acceptance. |
| LIVE-07 | Reviewer and evidence integrity | Relevant regression, export/model checks, rendered exact-passage/proof-link checks after server readiness, secret scan and staged diff preservation | Preserve failures and corrections with new retest records. No undocumented claim/status promotions. |

Missing evidence is UNVALIDATED; observed failed expectation is FAIL; suitable check prevented by a concrete unavailable prerequisite is BLOCKED. Main owns live operations and credentials. Independent agents may inspect local source only. Inputs, outputs, timestamps and limitations must be retained. Remaining external owner/commercial authority is not fabricated.
