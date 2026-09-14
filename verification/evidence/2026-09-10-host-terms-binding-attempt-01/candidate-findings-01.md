# Candidate assembly findings — not final results

On 10 September 2026, before integration, an independent field comparison ran
against the isolated writer checkout:

`node <DOCS_REPO>/.orchestra/host-terms/verify-projection.mjs`

It exited 1 at the exact source-span hash assertion (line 19). The current
source slice hash was
`36783d4fca41b907dc3f905f28a309839bddbe598089dafc7eccd1f3db395e5a`;
the candidate model still recorded
`fa50a655bc5001a79a40aca2e2064fcbfc5346689e38b2af936c13f40ffe3ce4`.
Source wording had continued changing during candidate assembly. This result
does not establish a product defect: the model must be rebuilt from final
wording and the exact comparison must pass again in the integrated repository.

Independent code review also found incomplete candidate guards: JavaScript
Set comparison was vacuous; patched spans needed exact file/bounds/hash checks;
the Terms source reference needed explicit enforcement; and the Python and
JavaScript changed-line coverage/mapping checks needed parity. The correction
is deliberately limited to same-line-count edits in this pinned transition,
with unchanged lines mapped to their original positions. Extra source changes
must fail rather than acquire inferred coverage.

These are implementation-review findings during construction. The final result
must point to retained integration and negative-fixture retests; neither this
note nor the model/registry is independent proof of the published policy.

## Integrated corrections and retests

- Final wording was rebuilt. `projection-02.json` passes the exact six-claim
  delta, current-span hashes and preservation of all 2,007 other claim records.
- The negative fixtures in `freshness-guards-01.json` pass for omitted claims,
  absent Terms references, wrong span provenance, unbound excerpts, extra lines
  and uncovered changed wording. Neither language's production pin is relaxed.
- The first integrated regeneration omitted `--write` and exited 2 before
  changing the model (`regenerate-model-01.json`). Its dependent projection
  failed against the old model (`projection-01.json`). The corrected invocation
  and retest are `regenerate-model-02.json` and `projection-02.json`.
- The first full Python run used three dated fixtures against later source
  bytes (`python-full-01.json`). Those fixtures now select their exact retained
  predecessor; the original historical validation still runs. The new current
  path is tested separately. `python-full-02.json` passes 226 tests.
- The first local reviewer run rejected freshness because the Terms transition
  carried the old Workload Policy fingerprint at its current path. The current
  path now records its current hash; the retained old source has its own path
  and old hash. `freshness-guards-01.json` checks all 380 returned fingerprints
  and rejects source drift. `reviewer-restart-02.json` passes. The failed
  `browser-final-01/` remains separate from the new `browser-final-02/` retest.
- `javascript-full-01.json` passed 170 of 171 checks. One actual-current-model
  test still called the predecessor-only loader; it now uses the same sealed
  current transition entry point as production. All synthetic predecessor
  tamper tests still use the original gate.
- `javascript-full-02.json` passed 170 of 171 checks. Its deterministic export
  assertion ran while the report was being regenerated, so its before/after
  HTML differed. The final report is frozen and exported before
  `javascript-full-03.json`; no exporter or report edit runs concurrently.
- Visual review found a stale 9 September header. Terms-active output now names
  the 10 September evidence update and the bounded six-statement source check.
  Legacy evidence dates remain dated history. `checks-02.json` retests the final
  regenerated HTML.

See the final result for the completed browser and full-suite outcomes. These
construction failures are audit history, not the current reviewer finding.
