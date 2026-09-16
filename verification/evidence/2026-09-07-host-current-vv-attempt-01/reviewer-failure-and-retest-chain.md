# Current reviewer: failures and corrections

These are repository/interface findings, not Host or API execution results.
Each original observation is retained in this directory.

| Original attempt | Observation | Correction / new retest |
| --- | --- | --- |
| `current-static-checks-initial-failure.json` | Aggregate PASS concealed individual unresolved links; the intermediate generator also used a fixed midnight timestamp. | Explicit anchor resolution, aggregate result from child results, actual UTC generation time; `current-static-checks.json` and model tests. The earlier timestamp is preserved as a generator defect, not asserted as execution time. |
| `current-model-initial-parser-failure.json` | Hidden MDX comments and table syntax appeared as customer claims. | Exclude comment bodies, delimiters and table headers; parser regression tests and current model parity check. |
| `volume-current-scope-audit-failure.md` | Broader Command Map scope inherited a link-only PASS. | Expanded claim is UNVALIDATED; navigation proof is explicitly separate. Nine pinned client dispatches were inspected in `volume-command-map-source-inspection.md`. |
| `current-model-final-03.json` | A test selected the first referenced claim, which was now an editorial correction rather than a historical evidence carry. | Select by historical carry decision; `current-model-final-04.json`. |
| `legacy-review-context-final-01.json` | The original four-second startup deadline expired before both packages finished loading; no test assertions ran. | Bounded twenty-second startup deadline; `legacy-review-context-final-02.json` passed all 35 tests. |
| `browser-all-first/summary.json` | 57 statement-location failures across 15 of 44 pages. | Split composite spans into rendered blocks; use the actual section and section-scoped occurrence; show current-card location notices. |
| `browser-all-retest-01/` | Two page checks timed out waiting for a current panel; run stopped rather than repeating that failure across all pages. | Inspection found a server-only constant referenced by browser proof-link code. The replacement routes proof links through the strict current-artifact handler. This interrupted attempt has metadata and per-page failures, but no completion summary. |
| `current-reviewer-final-02.json` | Historical proof links returned 404 in isolated fixtures; two test mutations were not written to their fixtures. | Serve only package-referenced, hash-checked artifacts independently of the old loader. Persist the negative fixture mutations. `current-reviewer-final-03.json` and `current-reviewer-final-04.json` passed seven tests each. |
| `browser-all-retest-02/summary.json` | Three remaining Offline Machine locations: two Markdown blockquotes and a repeated command under a parent heading. | Strip blockquote notation only outside code; limit an atomic passage to its nearest heading, excluding descendant subsections. Final browser retest records the outcome. |

The seven API/fixture tests also verify all 44 current page contexts and every
distinct referenced proof artifact. Later tests add a statement-scoped evidence
header and reject an unrelated claim/artifact pairing. Current checks refuse
stale source, navigation, package or referenced-artifact hashes. Historical
carry remains bound to the frozen status, evidence IDs, source spans and scope.

Masked examples intentionally use an explicit section-link fallback. A masked
fallback is not a successful exact-text highlight and is counted separately.
