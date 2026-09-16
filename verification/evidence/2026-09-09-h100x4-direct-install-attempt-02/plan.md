# Direct H100×4 install — attempt 02

PLAN_AND_EXECUTE, PR #185 / CON-1518. Frozen after baseline capture and before renewed SSH verification, September 9 South Africa (September 8 UTC).

User reports enabling passwordless sudo for vastadmin and supplies a new replacement setup token. Reuse the already approved modified direct route, not the stock wizard launch. Supersede neither original failed sudo evidence nor its old result. Treat the newest token as secret and do not reuse any older token.

## Frozen inventory and bounds

- RETEST-01: strict pinned SSH to the same NEW_H100X4_HOST; run `sudo -n true`, `sudo -n id -u` (expect 0), and selected `sudo -n sshd -T` policy fields. Refresh four idle GPUs, exact boot/hostname, current and fstab XFS quota mount, absent Docker/Vast and registration. PASS only for observed checks. Stop on identity, occupancy, storage or policy drift; no privilege-policy edit by the assistant.
- INSTALL-02: after passing guards, transfer the previously reviewed candidate (SHA256 4d87c48acc12a15eee1c2793d0631e1d936b2f996bdd50de4ad27b5acdf3d519) into a restricted unique temporary directory, verify remote bytes, then invoke with `[SETUP_TOKEN] --no-driver --no-partitioning --no-libvirt --ports 30000 30499`. Root-controlled stdin/in-memory credential handoff, restrictive umask/logs, masked capture, no secret shell history. Capture command, times, outputs and exit. No automatic retry after ambiguous or partial install.
- POST-03: retain numeric machine ID (not machine secret), actual Docker/Vast/GPU state, boot and storage identity, embedded diagnostic results, fetched-source identities and temporary-container state. No arbitrary customer content. An exit code alone is not readiness or acceptance.
- OFFER-04: only the exact newly registered, ready target may be listed. Values: USD3/GPU-hour, USD0.30/GPU-hour minimum bid, USD0.50/GB-month, fixed expiry1789423200, no separate volume offer. Inspect final defaults before publishing; retain exact request and independent readback. No rental or separate marketplace self-test. Stop on unsafe readiness state or unsupported commercial defaults.
- DOCS-05: append exact findings to reviewer/HTML and traceability; retain earlier failures, source bindings and unproven limits. Do not promote stock TUI, unchanged standard installer, automatic self-test, or general owner/commercial claims from this local variant. Export before export-equality tests. Verify affected links/pages and model/index preservation.

No reboot, formatting, partition/loop creation, driver installation, NAT/firewall edits, libvirt setup, other-host change, customer workload interference, push, merge, ticket post or human acceptance. Normal authorized Docker/Vast packages/services/registration and embedded NVML/NCCL/speed diagnostics are known install effects. Dynamic dependencies are not wholly pinned by the top-level candidate digest. Stop on a concrete unexpected unsafe action, not on a generic missing-evidence label.

PASS is method-scoped observed evidence; FAIL is a confirmed failed expectation; BLOCKED means a suitable check cannot proceed due to a named missing prerequisite. UNVALIDATED is absence of evidence. Root owns live operations and secrets; delegated review is local/read-only and receives no secrets.
