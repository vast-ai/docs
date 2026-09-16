# Independent closure-successor review

Initial read-only production review completed 2026-09-14T17:28:36.827331+00:00. No blocking production finding identified in the reviewed sealed successor. This conclusion is limited to the exact inputs below; final customer wording/rendering and any later successor changes remain root/writer review scope.

## Exact reviewed inputs

Repository: `/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914`.

- `scripts/current_host_closure_correction.py`: SHA-256 `82b80ff0ad91b32a2b4159714341ce5894d4bafea70fb6011544837f4c4c87e8`.
- `scripts/current_host_closure_correction.mjs`: SHA-256 `3f6299ee40c1538394a9257cfeed281915d3a29621c197575adc078a6f8e5c59`.
- `verification/current-host-closure-correction.json`: SHA-256 `5975bbbd9c01a70bfd5a6c3a59c71f08033da74fd35aa26d3225a65856ff53e2`.
- Projected model: SHA-256 `6c3d82b9168d393e1fd08c51b5ebe112568ade3c1f8194d158113afbf8827d19`.

The local graph query found no graph in this isolated checkout; direct bounded source and registry inspection followed.

## Findings and scope assessment

- **No predecessor bypass found.** Python forwards the frozen source view through invoice → payout terms → provider → cleanup → jurisdiction → terms → clarification/authority. Each layer overlays its own historically correct source bytes before validating its sealed predecessor. Registry, baseline and evidence pins remain checked; whole-model equality must reproduce the exact frozen baseline before closure transitions apply. JavaScript achieves the corresponding source view via its read callback.
- **No unbounded runtime PASS promotion found.** The six retained runtime bindings preserve prior unresolved statuses. Normal self-test remains BLOCKED and describes its actual failed reliability/upload preflight; it does not claim a rental/image workload or treat raw exit 0 as success. VOL-C31/C33 move only from BLOCKED to UNVALIDATED because the record demonstrates missing evidence, not an unavailable prerequisite.
- **New PASS scope is bounded.** Ten former FAIL assertions are narrowed to an agreement-backed rule/advice, attributed publication description, or declared CLI command purpose. No active-rental preservation, secure-erasure or whole-machine workload ban is newly asserted as proved. Five upstream verification/reliability statements become explicitly attributed descriptions of upstream guidance; they are not independent backend observations. The upstream source capture was independently compared byte-for-byte with Git revision `175a318c27750ea64da94f043dda39ec5cb26259` and matches. One application navigation claim becomes PASS; the existing Machine Error Reference navigation claim remains PASS.
- **Retirement accounting is preserved.** Five unsupported checklist claims are removed from the active inventory and retained as complete original FAIL objects in the replacement navigation history and frozen baseline. No active references to retired IDs were found outside history/corrections. Remaining eleven stronger FAIL assertions remain exactly equal to baseline records, including their evidence and rationale.
- **Source and reader checks remain closed on mismatches.** Exact current/before source pins, monotonic unchanged-line maps and complete old/new line partitions are checked. Unreviewed changed claim spans are rejected; changed procedure spans become STALE. Reader acceptance requires equality with the complete reconstructed model, and a marked model without its registry is rejected. No broad schema weakening was identified.

Initial accounting: 2,008 active claims — 335 PASS / 11 FAIL / 21 BLOCKED / 87 N/A / 1,554 UNVALIDATED. These are scoped claim dispositions, not acceptance or new runtime-test counts. Five checklist retirements are not five new PASS results.

## Independent verification run

`PYTHONDONTWRITEBYTECODE=1 node --test scripts/current-host-closure-correction.test.mjs` — **7/7 test groups passed** on local macOS using the configured Node and Python 3.14.6. This includes Python/JavaScript model parity; original-finding/retirement accounting; partial runtime nonpromotion; tampered registry/source/baseline/evidence/model rejection; selector mismatch below the registry seal; predecessor evidence replay; and owner-question references. No mutating generator, Host/account action, network operation or rental was run for this review.

## Separate, authorized test-fixture implementation

After the production review, root separately authorized this reviewer to modify only six historical Python test files. These edits are **not independently reviewed by their author** and must be inspected by root/writer:

- `scripts/test_current_host_payout_invoice_correction.py`
- `scripts/test_current_host_payout_terms_correction.py`
- `scripts/test_current_host_payout_provider_correction.py`
- `scripts/test_current_host_review_cleanup.py`
- `scripts/test_current_host_jurisdiction.py`
- `scripts/test_current_host_terms_binding.py`

The fixtures select their actual immutable pre-closure Host source bytes, keep their older payment/jurisdiction source overrides, and forward the optional source-view parameter through existing mocks. Historical expected counts, target sets and mutation assertions remain intact; the invoice fixture additionally requires full equality with the retained closure predecessor. Loaders without an override parameter invoke their real projector under a test-only source-view wrapper. The jurisdiction source-tampering test targets the actual frozen source artifact now consumed, rather than the deliberately superseded current page.

Initial payout run failed seven tests due to old source views and obsolete three-argument mocks; adapted payout fixtures passed **7/7**. A subsequent cleanup/jurisdiction/terms run exposed a test-wrapper argument mismatch and one concurrent self-test-reference source refresh during repeated validation. The wrapper was fixed and the writer confirmed the final source/registry refresh was stable before the passing combined rerun below. No production or JavaScript source was edited by this reviewer.

## Final stable-source verification

Recorded 2026-09-14T17:30:31.004088+00:00. The final D10 refresh adds only the generated self-test reference CLI revision annotation, its retained before-source bytes and the generator comparison artifact; it does not change claim dispositions. Replacing the final registry pin with the initial registry pin in both core scripts exactly reconstructs the initially reviewed hashes, confirming that their correction algorithms did not change.

Final SHA-256 inputs:

- `scripts/current_host_closure_correction.py`: `b3fdfcd1aff7135eeab941680a820e6d123d0fa9a6140fc2761b3decf81869bd`.
- `scripts/current_host_closure_correction.mjs`: `6c347f98cc9cdedcb87925419b65ce1499dbe386d08d0d684a09b9b783821afe`.
- `verification/current-host-closure-correction.json`: `ae18d9f42b69cdf4ad39f849a447f7cea0d9e2e6b07fd704b544c94775963c14`.
- `verification/current-host-docs-review.json`: `14fbb1f66d12d8da54215b227b9eb669fd21ca452c9a64eb780f274844b2bc6e`.

The retained generator comparison artifact is `verification/evidence/2026-09-14-host-closure-correction-attempt-01/generator-source-refresh.json`, SHA-256 `09930170c6830eda5ef3bfe94067c1f422f257b2f9f7c228fabd3f81507e1e56`. Final accounting is unchanged: 26 transitions and 5 retirements; 2,008 active claims — 335 PASS / 11 FAIL / 21 BLOCKED / 87 N/A / 1,554 UNVALIDATED.

Final runs against this stable source set:

- `PYTHONDONTWRITEBYTECODE=1 node --test scripts/current-host-closure-correction.test.mjs`: **7/7 passed**, including Python/JavaScript parity and predecessor/evidence tamper rejection.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.test_current_host_payout_invoice_correction scripts.test_current_host_payout_terms_correction scripts.test_current_host_payout_provider_correction scripts.test_current_host_review_cleanup scripts.test_current_host_jurisdiction scripts.test_current_host_terms_binding`: **20/20 passed** in 26.123 seconds.
- `git diff --check --` the six owned Python test files: **passed**.

Final owned test diff is six files, 91 insertions and 70 deletions. No production, JavaScript, docs or model files were edited by this reviewer. This is a focused local macOS verification result, not a claim that the whole repository suite or any live Host workflow was rerun. Root/writer independent inspection of the six fixture changes remains required before integration.
