# H100×4 direct installation and Host Docs evidence — September 9, 2026

PR [vast-ai/docs#185](https://github.com/vast-ai/docs/pull/185) / Jira CON-1518.
Dates in the raw records are September 8 UTC; the local operating date is September 9 in South Africa.

## Outcome and resource state

The approved **modified direct installer**, not the stock guided wizard, completed at 22:18:18 UTC. Its exact candidate SHA-256 is `4d87c48acc12a15eee1c2793d0631e1d936b2f996bdd50de4ad27b5acdf3d519`; execution used `--no-driver --no-partitioning --no-libvirt --ports 30000 30499`. See [execution](install-execution-01.json), [sanitized output](install-output-01.log), and [independent postcheck](postcheck-02.json).

The new machine is **150296, four H100 PCIe GPUs**. The [last retained owned-machine read](machine-readback-03.json) returned it unlisted, with zero running or resident rentals and no separate volume capacity. The [settled SSH snapshot](settled-01.json) observed no Docker containers or GPU compute PIDs, four active/enabled services and an empty package audit. Boot identity remained unchanged. No offer write, paid rental, separate marketplace self-test, reboot, router change or other-host change was performed.

Listing is **BLOCKED by two unspecified commercial inputs**, not by absent installation evidence: upload/download bandwidth prices and the maximum prepaid discount. Proposed values await confirmation: both bandwidth rates $0/GB, prepaid discount disabled. Already approved terms remain $3/GPU-hour, $0.30 minimum bid per GPU-hour, $0.50/GB-month storage, expiry `1789423200` (September 15 00:00 SAST), and `vol_size=0`. Do not extend that expiry.

## Four exact statements now have bounded runtime proof

All are on [Installing the Vast Host Software](../../../host/installing-host-software.mdx). The authority is the identified host's retained command output, not the documentation text. Each changed from UNVALIDATED to PASS only for this modified-route snapshot.

| Heading and statement | Claim | Selected postcheck |
| --- | --- | --- |
| Headless Fallback: `nvidia-smi` shows every GPU | `MCL-ead93c85c2ff4168` | POST-03: four H100 rows |
| After Install: services report `active` | `MCL-82fa8860fe3ef124` | POST-01: four active service results |
| After Install: `/var/lib/docker` is XFS with `pquota` or `prjquota` | `MCL-2f9f572d80e1e8f9` | POST-05: XFS mount with `prjquota` |
| After Install: project quota accounting and enforcement are ON | `MCL-aa383ba37f55f306` | POST-07: the Project quota block, not User/Group quotas |

The [adjudication registry](../../current-h100x4-direct-postinstall-adjudications.json) binds exact page/claim/command/output identities to [postcheck-02](postcheck-02.json). The [delta audit](model-delta-01.json) preserves each earlier record and confirms all other **2,001 claims unchanged**. Totals: **189 PASS, 151 FAIL, 22 BLOCKED, 4 N/A, 1,639 UNVALIDATED**. These four gains are not four of the 22 blockers closed. Coverage remains 44 primary Host pages plus 18 CLI and 15 SDK support layers.

Limits remain explicit: no stock TUI/standard-command verification, driver/libvirt installation, reboot persistence, WAN/NAT, paid workload, automatic marketplace self-test, general host health, or human acceptance. A transient bandwidth-test diagnostic container was still present in the first postcheck; the settled snapshot is a separate later observation.

## Failures and corrections remain visible

- Sudo authentication: the previous failure is preserved; [new preflight](preflight-01.json) passes the guards and resolves that prerequisite.
- Installer subcommands: [retained findings](installer-findings-01.json) record image-download EOF, updater write/chmod permission failures and package-manager lock/selection errors. Exit zero is not treated as an all-subcommands PASS.
- Image-only retry: [new bounded retest](image-retest-01.json) passed and retained `pytorch/pytorch@sha256:11691e035a3651d25a87116b4f6adc113a27a29d8f5a6a583f8569e0ee5ff897`. It did not start a container or fix installer error propagation.
- Repository checks: the [generator usage failure](generator-usage-failure-01.json), [Python setup failure](python-regressions-01.json), [first full reviewer regression](reviewer-regressions-01.json) and [first runtime browser attempt](runtime-browser-01.json) remain beside their retests. [Correction details](interface-correction-chain.md) distinguish raw retained root output from the worker's transcript-only report.

## Reviewer and repository verification

The localhost reviewer and [single-file shareable HTML](../../host-docs-review.html) show current completion context, historical pre-install observations, original failures, settled state and the successful image retry. The four PASS cards offer plainly labelled selected-result links and exact passage navigation. Identical scope warnings are deduplicated without removing distinct limits.

- [Python retest](python-regressions-retest-02.json): **158 tests pass**, with the exact original installer source supplied for static tests; no installer is executed by this suite.
- [Current-model check](model-check-final-02.json): **44 primary + 33 support layers pass**.
- [Full reviewer regression retest](reviewer-regressions-retest-02.json): **72/72 tests pass**, with source identities unchanged throughout the run; the original 71/72 result remains retained.
- [Affected-page browser retest](browser-final-02/summary.json): **101/101 passage/status controls pass**.
- [Installation-context browser retest](intake-browser-02.json): **69/69 links pass**; wrong page/claim binding is rejected.
- [Selected runtime browser retest](runtime-browser-03.json): **4/4 exact outputs pass in both views**, wrong selectors return 404, offline resource requests zero and no horizontal overflow. [Visual review](visual-review.md) records the inspected screenshots.
- [HTML export check](html-check-01.json): **152 embedded files**, deterministic export passes. Tests ran on macOS; runtime observations came from the Linux host. No Windows or cross-platform paid run is claimed.

The ancillary [graph refresh](graph-update-retest-02.json) **did not complete**: its node-loss guard refused to replace the existing graph. No force replacement was attempted. Reconciling the intentionally excluded private/temporary files and rebuilding that graph remains local maintenance, not an external Host Docs evidence blocker or a claimed PASS.

## What remains, separated by authority

1. [Runtime/operator register](runtime-operator-register.md): listing inputs, separately bounded paid/WAN testing, no-reboot constraint, stock installer paths and public-self connectivity.
2. [Product/Finance/Legal/source-owner register](source-owner-register.md): installer error/ownership/locking behavior, shipped binary provenance and unsupported general product/commercial/legal claims.

Neither external workstream is complete. No human acceptance, push, merge or Jira post was recorded. The [starting working-tree baseline](baseline.json) and final integrity record preserve HEAD/staged content, old evidence pins and the exact four-claim delta. Raw captures remain private and locally Git-ignored; the two task-created worktrees were archived, readback-verified and removed recoverably. This closes a bounded installation/evidence handoff, not the whole Host Docs project.
