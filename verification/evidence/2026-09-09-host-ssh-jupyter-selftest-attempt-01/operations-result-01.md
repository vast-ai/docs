# Machine 150296 — bounded operational result

PR185 / CON-1518 · 9 September 2026 · macOS operator over LAN/VPN; Linux H100 host. This is operational evidence, not human acceptance or a complete Host-docs PASS.

## What actually happened

| Exact page / heading or safety check | Result and independent proof | Limits |
| --- | --- | --- |
| First 24 Hours / Test Like A Client — corrected renter offer query | [Actual client CLI query returned offers for machine 150296](documented-client-02.json). | Exact pinned CLI revision and timestamp; not future availability. The first wrong-entry-point collector attempt is retained and linked to its retest. |
| Only-if-idle and correct target | [Immediate pre-create owned-machine read](immediate-precreate-idle-01.json), [strict Host SSH preflight](ssh-idle-03.json). | Four H100, zero running/resident rentals, zero containers/compute PIDs before create. Point-in-time observations, not an atomic marketplace reservation. No other machine was used. |
| First 24 Hours / Test Like A Client — small client rental | [One create request](create-request-01.json) and [running-instance readback](ready-01.json). | Instance **50386523**, one GPU, 10 GiB, unique test label, cached PyTorch image pinned by digest. The same image bytes were resolved from `latest`; this is not a promise about later tag contents. |
| First 24 Hours / Test Like A Client — SSH command works | [Direct SSH returned the expected nonce, exit 0](direct-ssh-01.json). | Registered user key, strict host-key verification bound through trusted Host SSH to this exact task container. Public-address connection from LAN/VPN, not independent outside-LAN proof. |
| First 24 Hours / Test Like A Client — Jupyter opens | [Browser stopped at ERR_CERT_AUTHORITY_INVALID](jupyter-browser-open-02.json); [actual warning controls](jupyter-certificate-snapshot-01.json). | **BLOCKED for browser completion:** this isolated browser lacks trust in the Vast Jupyter CA. No warning bypass or system trust-store change was made. First HTTP assumption/reset is retained separately as a collector correction. |
| Jupyter service availability, partial proof | [Authenticated `/api/status` and `/tree` returned 200 with certificate-chain and hostname verification](jupyter-scoped-tls-01.json). | Vast's CA was fetched through verified HTTPS and added only to one process's SSL context. Proves the service responds, not browser render, notebook/kernel execution, or arbitrary port/WAN reachability. |
| How to Self-Test / Run The Test — normal command with support-bundle directory | [Actual normal CLI preflight and bundle inventory](selftest-normal-preflight-01.json). | **Full diagnostic BLOCKED:** advertised reliability 0.8506588 is not >0.9, and upload 221.1 Mb/s is below the 500 Mb/s requirement. These are advertised offer values, not a new throughput measurement. No requirements bypass. |
| How to Self-Test / Run The Test — failure support bundle | The same record contains the produced 2,663-byte, mode-0600 archive and hashes of its four members. | Failure path only; no rental logs because no self-test rental was created. Restricted archive is not embedded in the shareable report. Raw CLI exit 0 is not success: structured `success` is false. |
| Cleanup and no reboot | [DELETE plus independent GET/list absence](cleanup-main-01.json), [watchdog confirmation](watchdog-finished-01.json), [post-cleanup Host state](host-idle-04.json), [post-cleanup SSH state](ssh-idle-04.json). | Only instance 50386523 was deleted. Zero rentals/containers/compute PIDs afterward; boot hash unchanged. Host remains listed under unchanged terms; future customers may arrive. |

The executed CLI revision is **ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd**. [Canonical source excerpts with exact GitHub links](canonical-cli-source-01.json) separately establish signatures, request assembly, preflight gates and failure-bundle implementation. Documentation text only identifies the reviewed claim; it is not its own evidence.

## Time, money and safety

The SSH/Jupyter runner took about **8 minutes 22 seconds**, including cleanup and account readback, inside the approved 20-minute window. An independent 15-minute watchdog was armed before the single create. The immediate account-wide credit difference was about **$0.40**; [that observation is not a settled or instance-attributable bill](charge-observation-01.json). The quoted one-GPU rate was about $4.01/hour, with an early-stop reserve under the approved $5 budget. No provider-enforced hard spending cap is claimed.

Normal self-test lasted about 1.4 seconds, made only the real offer-search request, and stopped at requirements. A fail-closed transport allowlist prohibited every create/update/delete operation. There was no paid self-test rental, no self-test image launch and no reboot; the 30-minute/$15 allowance was not used for a diagnostic workload. The guard did not trigger: the actual product preflight failed first.

Only macOS command/browser execution and the named Linux host were covered. Windows, Linux runner clients, independent WAN execution, notebook/kernel operation, full self-test results, installer paths, reboot persistence, final billing and Product/Finance/Legal claims were not qualified by this attempt.

## Next work, kept separate

- [Runtime/operator prerequisites](runtime-operator-register.md): browser certificate trust, advertised self-test requirements, a fresh idle window, funded Host context and an approved outside-LAN execution environment.
- [Source-owner, citation and review work](source-owner-register.md): authoritative citations and source/owner review. A working rental does not close these defects.

Reviewer-interface integration and its retests are recorded separately in this attempt's final result. No commit, push, merge, Jira post or human acceptance is established by this operational record.
