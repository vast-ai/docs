# Host Docs V&V inventory

- Plan baseline: `VV-HOST-DOCS-2026-08-27-A`
- Review target: `vast-ai/docs` PR #185
- Content revision: `5088d76b89856185f3ab15a628e4152ff140ab26`
- Prior QA revision: `1566df66299d58aa0f8e5316dca2f5740456d031`
- Detailed population: [`HOST-DOCS-VERIFICATION.md`](../HOST-DOCS-VERIFICATION.md) and [`host-docs-verification-inventory.json`](../host-docs-verification-inventory.json)

Statuses below are the planned baseline before fresh execution. They are updated only by linking a retained attempt; original attempt history remains intact.

| ID | Kind | Test basis | Method and expected observable result | Initial status | Evidence |
|---|---|---|---|---|---|
| VV-HOST-001 | Verification | Inventory completeness, structural conformance, and command-access reconciliation | Execute `inventory_host_docs.py --check`; expect 72 Host pages, 474 targets, 176 commands reconciled across five access groups, current generated artifacts, and zero structural/local-reference issues. | PASS | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md); history in [`issues.md`](./issues.md) |
| VV-HOST-002 | Verification | Documented CLI names and options match the official registry | Against a clean, exact Vast CLI revision, execute the registry verifier; expect 181 occurrences, 179 passes, two intentional family references, and zero actionable defects. | PASS | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md) |
| VV-HOST-003 | Verification | Persona metadata matches the authored Host pages | Execute `npm run check-persona-chips`; expect 39 pages synchronized and exit 0. | PASS | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md) |
| VV-HOST-004 | Verification | Review-context behavior matches its test contract | Execute `npm run test-review-context`; expect 9 tests passing and exit 0. | PASS | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md); history in [`issues.md`](./issues.md) |
| VV-HOST-005 | Verification | Local review server is syntactically valid JavaScript | Execute `node --check review-server.mjs`; expect exit 0. | PASS | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md) |
| VV-HOST-006 | Verification | OpenAPI input is valid | Execute `npm run check-openapi` under Node 24; expect Mint to report a valid definition and exit 0. | PASS | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md) |
| VV-HOST-007 | Verification | Host links resolve within Mint's route model | Execute `mint broken-links` under Node 24; expect zero Host Docs broken-link findings. Preserve and separate unrelated repository findings rather than calling the repository-wide result a pass. | PASS | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md); history in [`issues.md`](./issues.md) |
| VV-HOST-008 | Verification | Corrected image accessibility and remaining Host accessibility state are visible | Execute `mint a11y` under Node 24; expect no missing-alt finding for `host/payment.mdx`, plus retained known named-anchor/shared-color findings. Any unresolved in-scope failure remains `FAIL`. | FAIL | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md) |
| VV-HOST-009 | Verification | Tracked patch has no whitespace errors | Execute `git diff --check`; expect exit 0. | PASS | [Current replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md) |
| VV-HOST-010 | Validation | Host commands work in representative GPU/Docker/network/privileged contexts | Execute only on an approved disposable or development host, with before/after state and exact machine/image/instance evidence. | BLOCKED | Requires approved HydraHost budget or Vast dev-host access. |
| VV-HOST-011 | Validation | Private product-policy and control-plane statements match current behavior | Confirm against authoritative source, redacted fixture, or named source-owner review. | BLOCKED | Requires owners listed in `HOST-DOCS-QA-SUMMARY.md`. |

## Baseline change log

- 2026-08-27 — Initial V&V baseline created from the complete Host Docs inventory. No items sampled or removed. Local-safe checks separated from host-runtime and source-owner validation so a static pass cannot be presented as full validation.
- 2026-08-27 — Attempt 01 added without changing the planned expectations. It exposed a generated-evidence identity defect, a sandbox bind blocker, and a Mint clean-tree isolation defect; corrections require a new attempt.
- 2026-08-27 — Attempt 02 retained against the unchanged expectations. It closes the identity, bind, and clean-tree issues. Accessibility remains failed; paid-host and private-product validation remain blocked.
- 2026-08-27 — Attempt 03 replayed the same checks after the reviewer package was committed. Current counts and residual risks are unchanged.
- 2026-08-27 — Expanded VV-HOST-001 to require a complete five-group execution-access reconciliation for all 176 command targets. The grouping distinguishes paid resources from direct Host root and retains authentication, credential, mutation, matching-environment, and external-client gates.
