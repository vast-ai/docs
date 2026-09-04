# Host Docs reviewer V&V clarity — attempt 01

- Review target: `vast-ai/docs` PR 185 / `CON-1518`
- Tracked baseline: `3b7e56f0db6588953589e0692e75b7274526d5f9`
- Current canonical test-set SHA-256:
  `4cdce3a4f2ecd1dd4259682cdd7bc2b4a545bca4cb64afd87c32848176c4f301`
- Started: `2026-09-03T12:37:39Z`
- Finished: `2026-09-03T12:41:25Z`
- Host, paid, credential-bearing, privileged, destructive, or mutating action:
  none

## Purpose

Remove ambiguous V&V presentation across Host pages without changing what the
evidence proves. In particular, a page with no command carriers must not show a
`0/0` command score or the executable-command rubric. Display-only command
references, executable-intent targets, non-command checks, current derived
status, historical inventory baseline, and reviewer-feedback counts must remain
visibly distinct.

## Current page model

The governed procedure snapshot contains 39 Host routes:

- 21 routes contain no command carriers;
- 1 route contains display-only command references and no executable-intent
  targets;
- 17 routes contain executable-intent targets as well as non-command checks.

Across those routes the panel accounts for 357 non-command checks, 121
executable-intent targets, 44 display-only references, 138 numeric semantic
scores (121 executable-intent and 17 display-only), and 27 approved display-only
N/A assessments. The new `/host/volume-offers` route is outside this governed
snapshot and is explicitly labeled as not inventoried; no validation or scoring
claim is made for it.

## Retained checks

| Check | Result |
| --- | --- |
| `npm run test-review-context` | PASS — 19 passed, 0 failed |
| `python3 -B scripts/inventory_host_docs.py --check` | PASS — 73 pages, 503 unique targets, 193 commands, 0 structural/local-reference issues |
| `python3 -B scripts/verify_host_cli_commands.py --vast-cli <clean-ecf32efa-checkout> --check` | PASS — 201 occurrences: 199 direct matches, 2 intentional command-family references, 0 actionable findings |
| `npm run check-persona-chips` | PASS — 40 top-level Host pages |
| `node --check review-server.mjs` and test syntax check | PASS |
| Canonical page/source binding audit | PASS — 39/39 page hashes, 165/165 command spans, 468/468 step-section bindings, 138/138 score locations |
| Canonical snapshot linkage | PASS — test results, scores, and all 27 N/A approvals bind to the current snapshot |
| `npm run check-openapi` | PASS |
| `git diff --check` | PASS |
| Port-4000 API audit | PASS — all 39 governed routes available; `/host/volume-offers` returns `page-not-in-inventory` |

The installed Mint CLI does not expose a `mint validate` command. Its supported
checks were run separately. `mint broken-links` retained 99 repository findings
in 10 non-Host files and reported no Host-page broken link. `mint a11y` retained
the existing shared-color failure and named-anchor/image findings; these are not
reclassified as passes by this attempt.

## Rendered checks

The port-4000 panel was opened and inspected in a browser on representative
routes for every display class:

- `/host/hosting-overview`: no command carriers; no numeric-score fraction or
  executable rubric; nine checks are labeled non-command;
- `/host/host-teams`: 32 display-only references; 17 semantic documentation
  scores and 15 approved N/A records are explicitly separated from execution;
- `/host/hardware-prep` and `/host/machine-errors`: mixed non-command and
  executable-intent totals, with procedure status separate from scoring;
- `/host/payment`: manual/context checks expose goal, access, safety constraints,
  and limitations without pretending they are shell commands;
- `/host/volume-offers`: explicit not-in-inventory message and no validation
  claim.

The floating Review button now says `no review notes` or gives an explicit note
count; it no longer displays an unlabeled `0/0` that could be mistaken for a V&V
score. Browser error output was empty. Mint's Socket.io development connection
and reload messages remained warnings only.

## Source corrections and limits

Two Hosting Overview handoff steps were narrowed to the links actually present
in the page. Twelve stale command spans and three VM step-section bindings were
rebased in the earlier retained source-binding correction. A later nine-page
central-link migration received a separate append-only identity rebase. No
functional status, numeric score, command outcome, or parent target was promoted
by either rebase or by this UI review.

This attempt verifies reviewer clarity, source identity, generated inventory,
and local integration behavior. It does not complete the remaining blocked or
unvalidated runtime procedures, accept the documentation, or bring Volume
Offers into the governed 39-page procedure snapshot.

## Artifact identities

| Artifact | SHA-256 |
| --- | --- |
| `review-server.mjs` | `12e8de3ac86dbe58fb558cbbe2b8f0f5dde593586ef4e2e0adafa1364ff0fd5c` |
| `scripts/review-context.test.mjs` | `48a557a6df647fd220866ef612cf8f1ad34c3b7d9ea9fe75ec6eb66ba35ae4db` |
| `host-docs-verification-inventory.json` | `fa20e591348cf7eea47688d06bac445383c65865a88d33f502d4eac1f8747f42` |
| `host-docs-cli-command-check.json` | `e835ccbde6ad57c53e2497c0890f1cbf75e0327e5bf9f79c5fbf9e80f1e45aed` |
| `verification/host-docs-test-sets.json` | `4cdce3a4f2ecd1dd4259682cdd7bc2b4a545bca4cb64afd87c32848176c4f301` |
| `verification/host-docs-test-results.json` | `0022721208c6ddc63d7d98b21c2ff0154f4bf932be26f82e67e631e59609093b` |
| `verification/host-docs-command-scores.json` | `f393be5f87d407fbea34343d3501551c02dfc939fc8856db5f12bbcca7a0d1a8` |
