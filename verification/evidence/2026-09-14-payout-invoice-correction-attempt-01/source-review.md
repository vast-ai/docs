# Source decision

Inspected 14 September 2026. The independent source review is recorded in
`source-audit.html` (retained copy; its links use the original audit location); its conclusions are
subject to the main agent's source comparison and final checks.

The public capture is `published-invoice-guidance-01.json`, retrieved at
2026-09-14T15:34:50.914Z from https://docs.vast.ai/host/payment. Its SHA-256 is
`9e4a9ff965510e9c08f6c45c929ab5a180d882e7dfe6c14bd65b7b30cef5814c`.

| Current occurrence | Source section | Decision |
| --- | --- | --- |
| MCL-e2b956d14494e470, Payout Schedule, line53 | /sections/0/text | Use $20 USD as the invoice-generation threshold described by published guidance. The source heading says payout threshold, but its body describes invoice generation. |
| MCL-df7b287adb0df683, Payout Schedule, line54 | /sections/1/text | Published weekly Friday schedule; no noon-Pacific time. Remove that unsupported precision. |
| MCL-5936430d1b2d8de9, Payout Schedule, line58 | /sections/0/text | Balances below $20 roll forward until the threshold is reached. Keep account prerequisites separate. |
| MCL-bbd64c772e9b4693, Why are invoices not generating?, line106 | /sections/1/text and /sections/4/text | Valid connected payout method and at least $20 balance. Do not infer account verification or enforcement behavior. |
| MCL-3d796f5ae7f2020e, Payout Schedule, line55 | /sections/2/text | Attribute the first-payout estimate and additional provider/region processing qualification. Keep the contract clock distinct. |
| MCL-3afd93ae0b6cf8a4, When will I get paid?, line84 | /sections/2/text | Same first-payout estimate and provider/region qualification in the local FAQ. Section3 was inspected but is not needed for the revised sentence. No universal deadline or noon-Pacific promise. |

The retained Agreement capture at
`../2026-09-09-host-authority-scan-attempt-01/agreement-full-source-01.json`,
`/sections/4/text`, includes Hardware as a Service Payments: weekly billing
periods, payment payable within 14 days of a completed billing period, and
withholding rights. Existing contractual source support remains separately
bound. It does not validate an actual payout or the operational estimate.

## Cross-publication and circularity limits

The published page's Suggest edits link points to the same docs repository.
It is evidence of current published guidance, not independent product
corroboration. The revised statements must be attributed and the reviewers
must describe this source scope. No Finance acknowledgement is invented.

The older retained official FAQ at
`../2026-09-11-host-jurisdiction-authority-attempt-01/vast-legacy-faq-source-01.json`,
under "How and when will I be paid for hosting?", also calls $20 the minimum
payout and describes weekly Friday billing. Therefore the former payout label
is not proved false. The invoice-specific wording is a clarification supported
by the fresh publication. The older FAQ does not supply noon-Pacific timing,
rollover conditions or current account enforcement proof; its provider wording
is not reused for this correction.

The four original FAILs are retained missing-citation findings. The two added
timing records were UNVALIDATED. New source checks and retests must be linked
before reporting any of the six as resolved within the narrower scope.

## Implementation-review findings

The independent guard reader initially called the table's "$20 USD" minimum
label a P0 defect. That was not supported: the minimum label already denotes a
threshold. The reader withdrew that conclusion in guard-review-02.html. "At
least $20 USD" was nevertheless selected for explicit reader wording.

The main agent separately found that the new presentation initially dropped
the existing exact Agreement excerpt from the two timing cards, although the
model retained its source references. Both current cards must show separate
guidance and Agreement source controls. The retained original presentation
stays in history; its obsolete 2-to-4-week gap must not appear as a current
limitation after correction. check-context.mjs tests the exact current pair.

The integrated Python/JavaScript suites initially found stale historical and
latest-transition fixtures. Retests integrated-python-02.json (93 tests) and
integrated-js-02.json (68 tests) pass, including exact predecessor checks. The
older failed runs are retained, not relabeled. The first post-edit browser test
also expected a raw artifact filename where the dialog intentionally shows the
readable title "Published Host Payouts guidance". check-review-original.mjs and
after-01.json retain that test defect; the corrected check passes in after-02.json.

Rendered review also exposed 11 supported payout records labeled "Needs triage"
because four classifications were absent from the queue mapping. Their exact
classes are now registered. queue-01.json preserves the failure; queue-02.json
passes. Unknown future classes still require triage. No claim status or evidence
was changed by this presentation correction.
