# Current Host Docs V&V update — CON-1518 / PR #185

## Outcome

The current-source inventory, known local corrections, and safe automated
repository/browser checks are complete for this update. **The customer-facing
claims are not all validated; the Host docs are not acceptance-ready.**
Unvalidated claims are not automatically external blockers.

Start with the [short claim queue](../../HOST-DOCS-CLAIMS-TO-RESOLVE.md), then the
[complete page-by-page worklist](../../current-host-docs-claim-worklist.md).
Each unresolved occurrence quotes the customer-facing text and identifies its
page/heading, evidence requirements, existing proof and limits, owner role,
status and next action. The original 40-page evidence package remains unchanged.

## Target and coverage

- Starting commit: `bfa926c9421521767fa7411718bd31ea38b38528`; tree:
  `b603f6ac42f2e4a2c99385fceae23a0cd2b7a036`; branch `CON-1584-host-cli-api-sdk`.
- Starting tracked/index state was clean. The exact local-only capture records
  31,169 pre-existing untracked paths; its SHA-256 is
  `0696817522e0d1a34844ccf8268bb99ca42cb7cc47641307c18e6e824082f510`.
  Those private paths are not published in this package.
- 44 primary Host pages: 35 exact-source carries, 5 changed, 4 new. Volume Offers
  is included. The 18 CLI and 15 SDK wrappers are support layers, not workflows.
- 2,005 statement occurrences: **171 PASS, 4 editorial NOT_APPLICABLE,
  149 FAIL, 22 BLOCKED, 1,659 UNVALIDATED**. The 1,830 unresolved occurrences
  remain visible. These are occurrence counts, not unique product decisions.
- 164 PASS results are exact historical carries; 7 are current navigation-only
  checks. No new runtime success is asserted. Most classifications are automated
  dispositions or historical carry-forward, not 2,005 new human reviews.
- 110 procedure records / 1,047 nodes retain historical topology and add 83
  current heading checks. On the five changed pages, 91 historical nodes remain
  STALE; their 47 new heading checks, plus 36 on the four new pages, inventory
  sections. They do **not** establish branch-by-branch runtime validation.

## Corrections and retained verification

| What changed or was checked | Retained result and limit |
| --- | --- |
| Generated Self-Test `--ignore-requirements` and `--debugging` typography | [Original failure](self-test-formatting-initial-failure.json), [formatting retest](formatting-retest.json), [pinned generator parity](generated-reference-retest.json), [rendered ASCII-token retest](rendered-token-retest.json). No self-test run. |
| Volume Offers Command Map binding and proof scope | [Scope failure/correction](volume-current-scope-audit-failure.md), [nine-command source inspection](volume-command-map-source-inspection.md). Destination checks PASS; backend semantics remain UNVALIDATED. |
| Unsupported Market Metrics timing/rate promises and six Offline Machine diagnostic conclusions | [Original-target check](claim-corrections-original-target-check.json), [correction retest](claim-corrections-retest.json), [hash-bound correction input](../../current-host-claim-corrections.json). Runtime outcomes remain unproven. |
| CLI Markdown-label extraction | [Original failure](cli-extraction-original-target-check.json), [13-test retest](cli-extraction-retest.json), [204 occurrence signature check](cli-signatures-corrected.json): 202 signature PASS and 2 non-executable family references; no CLI commands executed. |
| Current model, links and support structure | [Current static evidence](current-static-checks.json): 489 local navigation destinations and 33 support structures; [model parity](current-output-parity-final-01.json). Links do not prove linked-page semantics. |
| Automated repository tests | [124 Python tests](python-suite-final-03.json), [35 review-context tests](legacy-review-context-final-03.json), [9 current-package integrity tests](current-reviewer-final-06.json). Negative cases reject false PASS, unsafe paths, stale source and mismatched evidence. |
| Persona, anchors and OpenAPI | [44-page persona check](persona-final-01.json), [named anchors](anchors-final-01.json), [pinned OpenAPI/client contract](openapi-contract-final-01.json). Static conformance only. |
| Actual reviewer interface | [44-page browser pass](browser-final/summary.json): 1,986 exact highlights and 19 explicitly masked section-link fallbacks; all filters/statuses/location controls checked. [33 support-layer browser checks](support-browser-02/summary.json) PASS. No operator commands clicked. |

The [reviewer failure/retest chain](reviewer-failure-and-retest-chain.md) retains
intermediate parser, proof-link, status-scope, startup and highlighting failures.
Proof views now identify the statement and its limits and link back to the page;
unrelated statement/artifact pairs are rejected. The reviewer overlay remains
local to the proxy; it is not injected into the customer preview directly.

## Remaining work — two separate registers

1. [Runtime/operator register](../../current-runtime-operator-blockers.md):
   1,113 unresolved occurrences need runtime/UI evidence, sometimes alongside
   source or owner evidence. Named blockers include unavailable authorized
   credentials, an idle/disposable representative Host, or explicit permission
   for workload/privileged changes. No credentialed, paid, WAN-probe, privileged,
   destructive, mutating Host or workload-affecting action was run.
2. [Product / Finance / Legal / source-owner register](../../current-source-owner-blockers.md):
   1,106 unresolved occurrences require canonical implementation evidence,
   333 accountable-owner confirmation, and 168 authoritative citations.
   Lanes overlap. Code cannot substitute for policy, tax, contract or pricing
   authority. An absent source pin alone remains UNVALIDATED, not BLOCKED.

Owners need to confirm or correct the priority tax, verification-gate,
notification, telemetry, account, payout and volume-lifecycle statements.
Documentation maintainers must bind suitable evidence, correct wording/citations,
and retest each affected claim when that evidence is available. New/changed
workflow expectations still require branch-level review; heading coverage is
not a substitute. No Product/Finance/Legal approval or human acceptance is recorded.

## Known global exceptions and environment limits

[Mint link checking](links-final-03.json) still reports 99 inherited
broken links in 10 non-Host files. [Accessibility checking](accessibility-final-01.json)
still reports 74 missing-alt findings in 19 non-Host files and a shared dark-mode
accent contrast failure (3.94:1). These are repository issues, **not external
blockers**, and were not represented as PASS or silently fixed outside this
Host-scoped update. Browser control/name checks are not a full accessibility audit.

Tests ran locally on macOS with loopback previews. No Linux/Windows or paid/live
dogfood result is claimed. The agent team produced and checked the changes;
independent subagent inspections are not human acceptance. The AST-only graph
was refreshed; its warnings about non-code evidence files do not affect this
verification package and the graph is not proof of product behavior.

The [final manifest](final-manifest-02.json) records exact source/evidence hashes
and rechecks all three frozen historical JSON files. No push, Jira post, merge,
or acceptance was performed in this update.

[Evidence sanitation](evidence-secret-pattern-scan-01.json) found no matches for
the selected credential/private-key patterns in 240 text artifacts. This is a
bounded scan, not a claim that pattern matching can detect every kind of secret.
The reviewer projection's existing masking tests also remain enabled.

Final staging found trailing blank lines in the three generated worklist/register
Markdown files. [The failure](staged-whitespace-failure-01.json) is retained;
the generator now emits exactly one terminal newline. The original
`final-manifest.json` remains a pre-correction identity record; manifest 02 is
the current seal. No claim, source passage, browser code or evidence status
changed in this whitespace correction.
