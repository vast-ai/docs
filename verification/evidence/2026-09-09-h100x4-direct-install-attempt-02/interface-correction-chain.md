# Interface and collector corrections

## Root browser check: wrong expected page title

[First browser attempt](runtime-browser-01.json) passed all four loopback selected-output, exact-passage and wrong-selector checks. Its offline check then raised `Missing page context MCL-ead93c85c2ff4168` after selecting the correct GPU output.

The collector incorrectly hardcoded `Installing Host Software`; the actual current-model title and viewer text are `Installing the Vast Host Software`. The collector now derives the exact title from the same page model it tests. It also retains the browser stderr rather than the long base64 invocation when an evaluation fails. No reviewer, report or model bytes were changed by this correction. A fresh suffixed browser attempt is required; the first failure remains unchanged.

## Independent worker observations — report, not raw captured logs

The UI worker reported initial fixture failures (`invalid current Host review claim` and unresolved pinned external authority) because its disposable fixture omitted the new registry and the canonical external-source sibling layout. It reported a 2/2 focused reviewer retest and 18/18 intake/offline tests after fixing those fixtures. Those outputs exist only in the worker tool transcript; no raw filesystem log was created. This paragraph is a handoff transcription and is not substituted for the root's retained full regression run.

Independent review also identified the per-claim registry-ID binding gap. The integrated gate requires the exact `H100X4-POSTINSTALL-MCL-<claim>-01` ID in addition to the pinned registry/postcheck bytes and exact POST selector. Earlier template null-direct grouping and browser-constant defects were corrected before integration. The worker source and test files are preserved in the verified local worker archive.

The first integration command stopped on a handoff filename typo (`current_host_install_evidence_intake.test.mjs`). The real test filename uses hyphens; the remaining three scoped files were integrated with that correction. No file was deleted or overwritten by the failed lookup.

## Root full regression and visual review

[First full regression](reviewer-regressions-01.json) ran 72 tests: 71 passed and one failed because its diagnostic assertion called nonexistent `server.output()`. The test's real context availability is now asserted without that invalid diagnostic call. Its fixture and expected context list were also extended for the newly appended settled/image-retry records. The first run's stdout is retained in full.

Visual inspection found identical scope limits repeated twice because the registry and selected observation carry the same limit. The panel now deduplicates exact identical limit strings; it does not remove distinct limitations or change evidence/status. A fresh full regression and affected browser retests follow these source changes.

Final retests: [72/72 full reviewer tests](reviewer-regressions-retest-02.json), [all four exact runtime controls with deduplicated scope](runtime-browser-03.json), [69 contextual links](intake-browser-02.json) and [101 page controls](browser-final-02/summary.json) pass. The same report/model identities are retained; the reviewer source changed only for the visual correction after the first full run.
