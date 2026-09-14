## Current Host Docs review update — 14 September 2026

For [CON-1518](https://vastai.atlassian.net/browse/CON-1518), this update publishes the accumulated Host Docs source/citation corrections, clearer per-passage reviewer controls, and refreshed handoff.

- [REVIEW-TRACEABILITY.md](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-TRACEABILITY.md): current results, scope and open work.
- [Standalone review HTML](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/verification/host-docs-review.html): download the raw file and open it in a browser; includes PR checkout and localhost3000/4000 instructions. GitHub's preview is not the interactive report.
- [Remaining corrections walkthrough](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/verification/host-corrections-walkthrough.md): **26 corrections remain**.
- [Latest payout/invoice result](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/verification/evidence/2026-09-14-payout-invoice-correction-attempt-01/result.md): four citation corrections and two timing passages now describe exact published guidance. This is not proof of completed invoices or payments.

The current inventory covers **44 Host pages**, with **18 CLI and 15 SDK support references** kept separate from Host workflows. It records 319 scoped PASS / 26 FAIL / 23 BLOCKED / 87 not applicable / 1,558 UNVALIDATED passages. These are passage counts, not unique product facts or an acceptance score.

Validation for this publication: 93 current-Host Python tests and 68 reviewer JavaScript tests passed; the final publication-copy change is separately retested. Prior retained checks cover all 38 payout-page passage locators and exact source controls in both reviewers. The generated HTML is checked against its export manifest. No new Host/API, account, payment or paid operation was performed for this publication.

[Runtime/operator work](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/verification/current-runtime-operator-blockers.md) and [source/owner confirmation](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/verification/current-source-owner-blockers.md) remain separate and open. This update does not request automatic merge or record human acceptance.

> [!IMPORTANT]
> **Reviewer focus:** use the eight shared decisions in **[REVIEW-QUESTIONS.md](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md)** plus the page-specific Jira gates shown by the local port 4000 review panel. Start with [CON-1187](https://vastai.atlassian.net/browse/CON-1187) and [CON-1509](https://vastai.atlassian.net/browse/CON-1509).
>
> [1 · IA approval](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md#input-1-ia-approval) · [2 · Review mechanics](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md#input-2-review-mechanics) · [3 · Pricing](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md#input-3-pricing-content-review) · [4 · Machine errors](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md#input-4-machine-error-platform-behavior) · [5 · Installer screenshot](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md#input-5-installer-wizard-screenshot) · [6 · Supported Hardware](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md#input-6-supported-hardware-sign-off) · [7 · Host Teams](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md#input-7-host-teams-engineering-answers) · [8 · Persona scope](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-QUESTIONS.md#input-8-persona-scope-ruling)

## Summary

- Reworks the Host documentation into a lifecycle-oriented IA with account/security, installation, verification, operations, business, CLI/API/SDK, and troubleshooting guidance.
- Adds a local review tool on port 4000 with selection-anchored comments, page notes, Jira provenance, and page-scoped blocker questions. **Save JSON** is the default restorable backup for every page/reviewer; **Import JSON** merges it without overwriting newer items, while CSV (Jira) and Markdown remain secondary exports. Port 3000 remains the plain documentation preview.
- Adds Host account/agreement and security guidance plus a Host CLI/API/SDK bridge to the canonical references.
- Reconciles the generated Verification / Self-test reference from docs PR #145 into this PR without replacing the later Host IA, persona metadata, and human-reviewed troubleshooting guidance.
- Adds a source-driven generator and CI workflow for the Self-test reference. It checks relevant PRs, runs weekly, supports manual source refs and optional repository dispatch, and fails when the committed MDX drifts from Vast CLI or Self-Test metadata.
- Documents merged Self-Test behavior: actual-versus-required checks, stable failure codes, runtime stages, diagnostic bundles, `vastai dump-logs`, the B300/very-high-VRAM cap, and older-GPU CUDA image selection.

## Corrected Jira traceability

Full evidence matrix and the CON-1519 bundle-ownership decisions: **[REVIEW-TRACEABILITY.md](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/REVIEW-TRACEABILITY.md)**.

- **CON-1517 is already implemented in this branch.** Commit `0cb28ff` is in PR 185 and distributed the human-reviewed common-host answers across 33 canonical Host pages. `/host/common-host-questions` is intentionally a routing index, not the full source-review artifact.
- **CON-1510 is implemented in merged runtime code and represented here.** Vast CLI PR #408 and Self-Test PR #2 provide extractable actual/required diagnostics, explanations, stable errors, remediation, and structured events; this PR now renders them from source.
- **CON-1513 is implemented here.** `scripts/generate_self_test_reference.py` and `.github/workflows/self-test-reference.yml` provide generation and drift detection. The passing `verify-self-test-reference` check proves the repository can read the private `vast-ai/self-test` source.
- **CON-1515 is now integrated here.** Draft docs PR #145 is no longer a dependency for its generator, workflow, or complete reference.
- **CON-1583, CON-1519, CON-1502, and CON-1419 docs gaps are represented here.** The page explicitly covers the ~2 TB B300 cap, `dump-logs` and opt-in host-local artifacts, the rebuilt image/platform matrix, and pre-Volta/Volta image-selection rules.

## Remaining Jira gates

The port 4000 panel is the page-by-page source of truth. The highest-impact remaining questions are:

- Product-approved setup-page machine-installation-key wording, dedicated-host-account guidance, and stale/wrong-account escalation ([CON-1584](https://vastai.atlassian.net/browse/CON-1584)).
- Host Teams migration, registration permission, `undefined` install-command, earnings/payout, and `billing_read` behavior ([CON-1581](https://vastai.atlassian.net/browse/CON-1581)).
- Machine-error catalog completeness, UI/field mapping, clearing/TTL behavior, and public-vs-internal scope ([CON-1531](https://vastai.atlassian.net/browse/CON-1531)).
- Exact failed-port/protocol evidence and authoritative offline-vs-hidden state, which still require backend/API support ([CON-1514](https://vastai.atlassian.net/browse/CON-1514)).
- Authoritative verification queue and wait-time wording ([CON-1515](https://vastai.atlassian.net/browse/CON-1515)).
- Diagnostic-bundle intake location, accountable owner, retention/access policy, first-line triage, and subsystem escalation ([CON-1519](https://vastai.atlassian.net/browse/CON-1519)).

## Stack context

This PR includes the stacked work from:

- vast-ai/docs#153 — CON-1518/CON-1077 Host docs IA + headless handover
- vast-ai/docs#156 — CON-1581 Host Teams draft

Because the upstream repository does not expose PR #156's head as an available upstream base branch, this PR targets `main`. The narrow CON-1584-only comparison remains available in the fork stack at jjziets/docs#2.

## Earlier validation (historical)

- `npm run test-review-context` — 9/9 passing, including multi-reviewer JSON round-trip, newest-item-wins, anchor preservation, and atomic invalid-import rejection
- `npm run check-persona-chips` — 39 authored Host pages in sync
- Self-test generator rerun twice from clean `vast-ai/vast-cli@d4316fb` and `vast-ai/self-test@6f93fc4` sources — byte-for-byte idempotent
- `actionlint .github/workflows/self-test-reference.yml`
- `node --check review-server.mjs`
- `git diff --check`
- Browser dogfood at `localhost:3000/host/self-test-reference`: generated content and legacy anchors render; no review overlay
- Browser dogfood at `localhost:4000/host/self-test-reference`: Jira issues render and only the authoritative queue/wait-time question remains
- `mint broken-links` still reports the branch's existing 100 API-reference/notification links; none are introduced by the changed files

## Review locally with inline commenting

Use Git, the GitHub CLI and **Node.js 24**. The current preview was checked on macOS; a fresh clone/install and Linux/Windows setup were not re-executed for this publication. Compare the fetched checkout and report digest as described in the standalone HTML.

### 1. Clone and prepare the PR

Use Terminal on macOS/Linux or PowerShell/Windows Terminal on Windows:

```text
gh repo clone vast-ai/docs vast-docs-pr185
cd vast-docs-pr185
gh pr checkout 185
npm ci
```

### 2. Start the plain docs preview — terminal 1

Open a terminal in the parent folder:

```text
cd vast-docs-pr185
npm run dev -- --no-open
```

Leave it running. It serves the plain docs preview on port 3000.

### 3. Start the review overlay — terminal 2

Open a second terminal in the same parent folder:

```text
cd vast-docs-pr185
node review-server.mjs
```

Leave it running. It serves the review tool on port 4000.

Open **http://localhost:4000/host/hosting-overview**.

- Select exact page text and choose **Comment on selection**, or use **+ Page note** for page-level feedback.
- Open the review panel to see the relevant Jira epics/issues and unresolved questions for the current page.
- Feedback stays in `review-feedback/` inside the checkout.
- At **http://localhost:4000/__review__/**, use **Save JSON** for the complete restorable backup and **Import JSON** to rebuild feedback. Imports cover all pages/reviewers and keep the newer timestamp for duplicate item IDs. CSV (Jira) and Markdown remain secondary exports.

If Mintlify selects port 3001 because port 3000 is occupied, start the review server with `node review-server.mjs --target http://localhost:3001`.



