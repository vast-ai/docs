# Host Docs official-source correction

Status: completed locally for this eight-finding repository/source pass.
The wider Host V&V and the two external workstreams below remain open.
CON-1518 / PR185, 11 September 2026. Repository/public-source work only.

## What changed

Eight exact findings now have bounded support. Three Tax Guide instructions use
payment-provider, IRS and California FTB guidance. One Workload Policy instruction
uses the existing Agreement privacy rule, with report handling reviewed as advice.
Four Datacenter statements now describe the current program's published benefits
and requirements, without adding unsupported reliability or chat-channel claims.
Secure Cloud partner audits are attributed separately from Certified Data Center
application requirements.

Current counts: **241 PASS / 35 FAIL / 23 BLOCKED / 13 NOT_APPLICABLE /
1,701 UNVALIDATED**. This closes six missing-citation findings and two previously
unvalidated advice/publication findings. All **2,005 other complete claim records
are unchanged**. No procedure or page receives a runtime PASS from these checks.
The 18 CLI and 15 SDK wrappers remain reference-support layers.

The reviewer uses plain finding/next-step wording. Tax citation warnings no longer
discuss failed runtime tests. Original limitations remain in collapsed history;
our contextual review note is separate from independent official sources.

## Scope and authority

The [scan report](source-scan.md) explains US, California, UK and EU sources and
the questions they cannot answer. The [inventory](scan-inventory-01.json) accounts
for all 44 pages and 2,013 claims; 336 retrieval candidates were identified.
Detailed inspection covered all 15 Tax records and 311 unique non-Tax claims,
including all 35 non-Tax FAIL records. This is not a new substantive adjudication
of every product claim.

Twelve successful public-source captures retain response metadata, original
bodies, text, timestamps and hashes. Earlier provider and Agreement captures keep
their own dates. Government guidance cannot establish Vast's actual withholding,
VAT, form-delivery or payout practices. Residence outside the US does not by itself
exclude US tax obligations. California rules apply only in their proper scope.
This is not personal tax advice or human acceptance.

## Checks and independent review

| Check | Retained result / scope |
| --- | --- |
| Exact source/model projection and integrity | [Integration check](integration-01.json): eight bounded changes, 2,005 other claims unchanged; all 3,329 pre-existing evidence files and the starting index unchanged. |
| Independent source and guard review | [Independent review](independent-review-01.md): corrected one scope error; no remaining issue found in the eight selected mappings. |
| Full Python suite | [Retest](python-full-02.json): 232 tests pass. |
| Full JavaScript suite | [Rerun](javascript-full-02.json): 187 tests pass. After the final presentation change, [51 affected regression tests](final-ui-regressions-02.json) pass; this overlaps the full suite rather than adding 51 independent cases. |
| Localhost browser | [All 44 pages](localhost-01/summary.json): 2,013 cards, 1,994 exact highlights and 19 explicit masked fallbacks. [Final affected-page retest](localhost-02/summary.json): all 77 cards on the three changed pages pass. |
| Offline browser | [Final 15 check groups](checks-03.json): all claims reachable, 138 exact source/review controls, safe links, named controls, desktop/mobile layout and no external resources. |
| Focused visual check | [Final two cards](visual-02/result.json): Tax advice and Workload rule, exact highlight, collapsed history, and review notes separated from official sources. Root inspected both final screenshots. |
| Static checks | [Model](model-check-01.json), [44 persona pages](persona-01.json), [OpenAPI](openapi-01.json), [204 CLI signatures](cli-signatures-01.json) and [volume contract](volume-contract-02.json) pass. CLI source is ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd. These are not backend/runtime proof. |
| Derived navigation | [AST update](graph-update-02.json), [current claim/source index](current-derived-index-02.json). All 44 pages / 2,013 claims indexed; graph/index/registry are not terminal evidence. |

Final AST extraction warned that 2,256 non-code sources produced no nodes, and skipped
the oversized graph visualization. Exact claim/source navigation was refreshed
separately; this does not claim a full semantic graph rebuild. No CLI/runtime code
changed, so no cross-platform or paid dogfood was performed.

## Corrections and retained attempts

- [Original classifications](before-findings-01.json) → current exact projection.
- [First Datacenter scope error](proposal-01-scope-defect.json) →
  [corrected contextual inspection](contextual-advice-review-02.json) and independent review.
- [First Python suite](python-full-01.json) → historical-fixture correction → 232-test retest.
- First JavaScript suite: two historical fixture builders omitted the new imported
  module. Corrected the copies without weakening source/model guards; the 187-test rerun passes.
- [Earlier limits shown as current](historical-limits-red-01.json) →
  [collapsed-history regression](historical-limits-green-01.json).
- [Visual date finding](visual-review-01.md): original screenshots preserved;
  presentation labels corrected to 11 September, without changing source dates.
- [Review-note presentation failure](review-note-red-01.json) →
  [production-renderer regression](review-note-green-01.json). A stale dialog-title
  assertion failed in [final UI attempt 01](final-ui-regressions-01.json) and the
  second offline check. Exact review-note/source expectations were corrected;
  the 51-test retest and third offline check pass.
- Initial volume/generator invocations lacked required arguments; [volume retest](volume-contract-02.json)
  and [model regeneration](regenerate-model-02.json) pass. These invocation errors
  were not Host behavior failures.
- Archive verification first rejected macOS AppleDouble metadata. The [new readback](worker-archive-readback-02.json)
  verifies all 4,549 files/links and 25 integrated worker evidence records; metadata stays retained.
  [Only the integrated task worker was removed](worker-retirement-01.json); the
  private recovery archive remains available. The main workspace was not removed.

## Separate unfinished workstreams

1. **Runtime/operator work:** [current register](../../current-runtime-operator-blockers.md).
   Runtime claims still need their recorded environment, permission, inputs and
   authorization. No Host/API/SSH, credentials, rental, reboot, or customer work
   was attempted here. This workstream is not complete.
2. **Source/owner confirmation:** [current register](../../current-source-owner-blockers.md).
   Vast's tax handling, Wise/W9 process, international documents and exact
   datacenter application documents still need applicable current authority.
   Older Vast sources conflict with the draft on ACH and unused-GPU scope;
   resolve those conflicts rather than selecting whichever source closes an item.
   Missing proof alone remains UNVALIDATED, not an invented external blocker.

The [plan](plan.md) and [exact 4,440-file starting tree](baseline-01.json) precede
edits. No commit, push, merge, Jira post or human acceptance is part of this result.
