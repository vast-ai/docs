# Split rental review cards: final presentation finding

Completed locally on 10 September 2026 for CON-1518 / Host Docs PR #185.
This is a reviewer-interface correction, not new product evidence or claim
approval. No Host/API/SSH, paid work, publication or human acceptance occurred.

## What changed

The pricing introduction already has a separate source-only PASS. Four open
records repeated it before their own statement. The HTML and localhost reviewer
now display only the child statement, with a link to the existing pricing
finding. Related pricing evidence is neutral and collapsed, not green proof
for an unrelated statement. Each source dialog shows the child statement and
the source's limited scope. Full recorded wording remains under audit details.

All five records are on **Hosting Overview / The Rental Contract**:

| Finding | Exact source line | Unchanged status | Meaning |
| --- | --- | --- | --- |
| MCL-3d66c8305aa70982 | 75 | PASS | Published CLI pricing guidance only; not observed billing. |
| MCL-a4b087a3103c5bdb | 77 | UNVALIDATED | Pricing outcomes still need implementation and retained results. Both bound sources remain available. |
| MCL-470bf8ec992a342e | 78 | FAIL | Citation for offer-end-date effects on existing rentals remains missing. |
| MCL-8d3286528a924e12 | 79 | UNVALIDATED | Unlisting behavior still needs suitable evidence. |
| MCL-6e0046c21ac71be4 | 80 | FAIL | Citation for availability through the latest rental end date remains missing. |

The shared formatter pins the exact ID, full wording, status, classification,
evidence requirements, source revision, rationale/action hash and child span
hash. Changed adjudications fall back to their recorded finding. No new claim
records or PASS results were created. The customer-facing page is unchanged.

## Independent retained checks

- [Exact initial tree](baseline-01.json): HEAD, branch, staged/unstaged diff
  fingerprints and 4,362 Git-visible file hashes before implementation.
- [Initial failing regression](split-regression-before-01.json) and
  [first correction retest](split-regression-after-01.json): child-only wording
  and source guards. The finalized guards also run in the suite below.
- [Reviewer suite](javascript-full-02.json): 157 of 158 cases passed. Its one
  failure used an old test locator stub with no claim/source passages. The test
  now uses the actual production locator and
  [its retained retest passes](integration-retest-01.json).
- [Other 14 JavaScript cases](javascript-support-01.json) pass. Together these
  cover all 172 unique cases across `scripts/*.test.mjs`; this is aggregate
  coverage with the focused retest, not a claimed single all-green invocation.
- [All 44 localhost pages](localhost-01/summary.json): 2,013 cards, 1,994 exact
  highlights and 19 explicit masked fallbacks. Status, filters, headings and
  source controls remain available.
- [15 offline HTML groups](checks-01.json): filters, counts, source dialogs,
  safe links, desktop/mobile layout and offline operation pass.
- [Four-card checks in both views](split-browser-02/result.json): child-only
  highlights, full audit wording, neutral collapsed context, every source
  selector and the separate pricing finding pass. The parent remains reachable
  when filters would otherwise hide it.
- Visual inspection: [offline end-date card](split-browser-02/offline-end-date.png)
  and [localhost end-date highlight](split-browser-02/localhost-end-date.png).
- [Deterministic export](export-drift-01.json) and [preservation check](integrity-01.json).

## Retained failures and limits

The first suite was sandbox-limited by localhost `listen EPERM`
([record](javascript-full-01.json)); the permitted rerun is linked above.
The first restart attempt stopped before mutation because sandbox process
inspection was unavailable. Exact localhost process identity was then checked,
and only this workspace's reviewer was restarted
([final refresh](reviewer-restart-02.json)).

[Focused checks](focused-tests-02.json) retained an outdated test allowlist
expectation after the new evidence directory was added. The expectation was
updated and passed in the later suite. The first offline screenshot caught a
smooth scroll before it finished; [the original browser record](split-browser-01/result.json)
is retained, and the second screenshot uses immediate scrolling.

[Graphify AST refresh](graph-update-02.json) and its
[final incremental check](graph-update-03.json) are navigation support only. The refresh
warned that many JSON/doc files yield no AST nodes and skipped the oversized
graph visualization. It is not a semantic source audit or product proof.

The model remains **233 PASS / 41 FAIL / 23 BLOCKED / 13 N/A /
1,703 UNVALIDATED**. All 3,253 prior evidence files, Host source and the two
external registers remain unchanged. The [runtime/operator register](../../current-runtime-operator-blockers.md)
and [source/owner register](../../current-source-owner-blockers.md) stay open.
No push, merge, Jira post or human acceptance is included.
