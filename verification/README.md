# Host Docs verification and validation evidence

This package applies the [Oxiom Systems V&V Evidence procedure](https://github.com/Oxiom-Systems/vv-evidence) at commit `a0b49e328777b85c635016c7f5920ce270ade759` to the Host Docs review in [PR #185](https://github.com/vast-ai/docs/pull/185).

It is the reviewer entry point for fresh, retained evidence. The detailed population remains in [`HOST-DOCS-VERIFICATION.md`](../HOST-DOCS-VERIFICATION.md); the CLI population remains in [`HOST-DOCS-CLI-COMMAND-CHECK.md`](../HOST-DOCS-CLI-COMMAND-CHECK.md). This package does not duplicate those 474 targets.

## Validation plan

- **Scope and target:** corrected Host Docs content at commit `5088d76b89856185f3ab15a628e4152ff140ab26`, the QA artifacts added at review-branch commit `1566df66299d58aa0f8e5316dca2f5740456d031`, and a new clean evidence baseline committed before execution.
- **Population and coverage:** all 72 Host pages, all 33 imported Host snippets, all 474 unique inventory targets, and all 181 documented Vast CLI occurrences. The existing generated inventories establish the item-level population; the inventory freshness check establishes that they still describe the target.
- **Local-safe verification:** inventory freshness and structural parsing, CLI registry conformance, persona synchronization, review-context tests, review-server syntax, OpenAPI validation, link analysis, accessibility analysis, and whitespace checks.
- **Validation requiring another environment:** paid self-test, GPU, Docker, network, storage, privileged host, credential-bearing, account-mutating, and private control-plane behavior. These are not authorized by this plan and remain `BLOCKED` or `UNVALIDATED`.
- **Environment and prerequisites:** macOS arm64; Python 3; Bash; Git; repository dependencies from `npm ci`; supported Node 24 for Mint; and a clean official Vast CLI checkout whose full revision is retained.
- **Evidence retained:** exact command, timestamps, exit code, stdout, stderr, environment, docs and CLI Git identities, package-lock hash, result interpretation, known failures, and reviewer-facing status reconciliation.
- **Status criteria:** `PASS` requires retained current output from a method suitable for the claim; `FAIL` is an observed discrepancy; `BLOCKED` is a suitable check prevented by missing authority/access/environment; `UNVALIDATED` has no claim-suitable execution; `STALE` no longer applies to the named target; `NOT_APPLICABLE` requires a rationale.
- **Safety:** the runner refuses a dirty tracked docs baseline or dirty CLI checkout and contains no paid, credential-bearing, privileged, destructive, account-mutating, or production-changing command. Evidence is internal and must be checked for secrets before commit.
- **Execution gate:** **READY** for VV-HOST-001 through VV-HOST-009. **NOT READY** for VV-HOST-010 and VV-HOST-011 until host access/budget or authoritative source evidence is approved.

## Reviewer workflow

After checking out the evidence baseline and installing dependencies:

```bash
npm ci
./verification/run-local-safe-checks.sh \
  <unique-run-id> \
  /path/to/clean/official/vast-cli
```

The run ID creates a new append-only directory under `verification/evidence/`; the script refuses to overwrite an existing attempt. Review [`inventory.md`](./inventory.md), the current [`summary.md`](./summary.md), and the linked raw attempt outputs.

This package supports technical review; it does not constitute acceptance or certification. An authorized reviewer makes that decision.

