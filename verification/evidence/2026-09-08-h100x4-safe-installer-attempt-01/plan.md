# Reviewed local installer variant — frozen plan, attempt 01

PR #185 / CON-1518. PLAN_AND_EXECUTE. Frozen 2026-09-08, after the exact baseline and before variant creation or validation. This attempt follows the separately preserved installation-history intake.

## Authority and scope

The user approved preparing a reviewed modified installer that suppresses automatic listing/self-test, with evidence and reviewer updates. Target is only the new H100×4 host identified in the prior restricted capture. Approved eventual listing: USD 3 per GPU-hour on-demand; USD 0.30 per GPU-hour minimum bid; USD 0.50 per GB-month storage; fixed offer expiry no later than September 15, 2026. No reboot. No separate volume offer, rental, load test, NAT/storage/driver changes, changes to existing hosts, push, merge, post or human acceptance is authorized by this preparation step.

Preparation is local. Actual privileged installation requires the exact variant and downstream action chain to pass review, fresh target readiness/identity, explicit non-destructive choices, and a fresh setup credential supplied through an approved secure store. Do not reuse the chat-pasted key or substitute the existing Host/client API key. No secret-store inventory is authorized; use only a specific user-supplied entry when available. Stop and state concrete prerequisites if execution cannot safely proceed.

## Inventory and acceptance basis

| ID | Claim / target | Method and expected observation | Evidence and limits |
|---|---|---|---|
| SAFE-01 | Correct current docs/source baseline and original installer identity | Record Git/index/current model; check retained public source digests; source orientation | Exact baseline, source hashes and locators. No live behavior claim. |
| SAFE-02 | Minimal local variant suppresses the inspected automatic self-test/listing launch | Build from exact original digest; require exact unique replacement anchors; reject any drift, already modified input, invalid output or unexpected diff | Original and modified hashes, readable diff, deterministic preparation record. Original preserved; no upstream stock change. |
| SAFE-03 | Preparation and suppression checks detect unsafe old behavior | Run safe static and isolated simulation tests; old source fails suppression assertion, new variant passes; reject source/argument/path tampering | Retained commands, inputs, stdout/stderr, exit codes. Never execute the full installer, fetch dependencies, invoke sudo or call Host APIs in tests. |
| SAFE-04 | Independent review of execution side effects and no-reboot/storage constraints | Review actual diff and original command paths, downloaded dependencies, TUI handoff and registration/publication controls | Exact findings, provenance and missing prerequisites. A removed launch does not prove every daemon/downstream behavior. |
| SAFE-05 | Host ready for a future bounded installation | Evaluate existing read-only baseline and concrete credential/target/action prerequisites; only necessary approved read-only refresh if justified | Prerequisite register. No installation PASS without retained live execution. Missing fresh setup credential blocks this stage. |
| SAFE-06 | Findings trace to actual client-facing passages | Bind variant review to the current Installing Host Software headings/claims without status promotion or replacing prior attempts | Additive evidence map, exact source spans, evidence limits and next action. Modified route cannot prove untouched TUI/standard paths. |
| SAFE-07 | Reviewer, HTML and existing model remain faithful | Run local source/model/export/negative/link/browser checks on affected route and unrelated control; verify running port4000 source | Retained regressions, contextual evidence links and visible offline/loopback checks. Existing unrelated tooling issues remain recorded. |
| SAFE-08 | Evidence closure and safe handoff | Reconcile all inventory dispositions; separate runtime/operator work from source-owner/commercial work; confirm model/index preservation | Reviewer entry point, final manifests, blockers and next actions. Complete package is not installation or Host Docs acceptance. |

PASS requires the specified method's observed result, bound to exact inputs. FAIL means a confirmed failed expectation/defect; retain it before correction and append a retest. Missing evidence alone is UNVALIDATED. BLOCKED requires a named unavailable credential, authority, permission, input or environment that prevents the suitable check. N/A needs explicit rationale. Never promote runtime claims from static inspection or simulation.

## Isolation and sequencing

Main owns the plan, baseline, integration, verification and final evidence. One isolated builder may prepare the variant tooling/tests. A separate read-only reviewer examines the original source and execution boundary independently. Reviewer interface changes follow settled evidence and are isolated from the installer work. All live/credentialed operations remain main-controlled; no agent may install, reboot, list, rent, inspect customer workloads or read credentials.

Any discovered additional requirement or unsafe side effect is appended as an amendment, not silently removed. Preserve original attempts and current claim statuses. Use public/sanitized evidence in Git and restricted local paths for source/captures that contain private material.

## Amendment 01 — targeted read-only storage/readiness refresh

Before executing SAFE-05, refine its method because the existing baseline observes a mounted XFS filesystem but does not show the persistent fstab entry. Static source shows `--no-partitioning` can still fall back to loopback creation when the mount is not reused. Refresh only the already approved new host over the exact pinned SSH identity: UTC time, hostname, kernel/boot identity, four-GPU inventory, exact current and fstab Docker mount rows, checked service states, and presence of reboot-required marker. No sudo, mounting, package commands, customer data, workload queries, keys, networking probes or remote file writes. Retain raw capture privately and a sanitized projection publicly. PASS covers observations only; do not interpret an absent reboot marker as a no-reboot guarantee. This read is justified to distinguish a concrete preflight risk from a generic evidence gap; it does not authorize installation.
