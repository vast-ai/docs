# Host Docs V&V inventory

- Plan baseline: `VV-HOST-DOCS-2026-08-27-A`
- Review target: `vast-ai/docs` PR #185
- Content revision: `5088d76b89856185f3ab15a628e4152ff140ab26`
- Prior QA revision: `1566df66299d58aa0f8e5316dca2f5740456d031`
- Detailed population: [`HOST-DOCS-VERIFICATION.md`](../HOST-DOCS-VERIFICATION.md) and [`host-docs-verification-inventory.json`](../host-docs-verification-inventory.json)

Statuses below are the planned baseline before fresh execution. They are updated only by linking a retained attempt; original attempt history remains intact.

| ID | Kind | Test basis | Method and expected observable result | Initial status | Evidence |
|---|---|---|---|---|---|
| VV-HOST-001 | Verification | Inventory completeness and structural conformance | Execute `inventory_host_docs.py --check`; expect 72 Host pages, 474 targets, current generated artifacts, and zero structural/local-reference issues. | UNVALIDATED | Pending |
| VV-HOST-002 | Verification | Documented CLI names and options match the official registry | Against a clean, exact Vast CLI revision, execute the registry verifier; expect 181 occurrences, 179 passes, two intentional family references, and zero actionable defects. | UNVALIDATED | Pending |
| VV-HOST-003 | Verification | Persona metadata matches the authored Host pages | Execute `npm run check-persona-chips`; expect 39 pages synchronized and exit 0. | UNVALIDATED | Pending |
| VV-HOST-004 | Verification | Review-context behavior matches its test contract | Execute `npm run test-review-context`; expect 9 tests passing and exit 0. | UNVALIDATED | Pending |
| VV-HOST-005 | Verification | Local review server is syntactically valid JavaScript | Execute `node --check review-server.mjs`; expect exit 0. | UNVALIDATED | Pending |
| VV-HOST-006 | Verification | OpenAPI input is valid | Execute `npm run check-openapi` under Node 24; expect Mint to report a valid definition and exit 0. | UNVALIDATED | Pending |
| VV-HOST-007 | Verification | Host links resolve within Mint's route model | Execute `mint broken-links` under Node 24; expect zero Host Docs broken-link findings. Preserve and separate unrelated repository findings rather than calling the repository-wide result a pass. | UNVALIDATED | Pending |
| VV-HOST-008 | Verification | Corrected image accessibility and remaining Host accessibility state are visible | Execute `mint a11y` under Node 24; expect no missing-alt finding for `host/payment.mdx`, plus retained known named-anchor/shared-color findings. Any unresolved in-scope failure remains `FAIL`. | UNVALIDATED | Pending |
| VV-HOST-009 | Verification | Tracked patch has no whitespace errors | Execute `git diff --check`; expect exit 0. | UNVALIDATED | Pending |
| VV-HOST-010 | Validation | Host commands work in representative GPU/Docker/network/privileged contexts | Execute only on an approved disposable or development host, with before/after state and exact machine/image/instance evidence. | BLOCKED | Requires approved HydraHost budget or Vast dev-host access. |
| VV-HOST-011 | Validation | Private product-policy and control-plane statements match current behavior | Confirm against authoritative source, redacted fixture, or named source-owner review. | BLOCKED | Requires owners listed in `HOST-DOCS-QA-SUMMARY.md`. |

## Baseline change log

- 2026-08-27 — Initial V&V baseline created from the complete Host Docs inventory. No items sampled or removed. Local-safe checks separated from host-runtime and source-owner validation so a static pass cannot be presented as full validation.

