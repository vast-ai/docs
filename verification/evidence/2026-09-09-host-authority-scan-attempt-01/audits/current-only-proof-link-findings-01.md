# Internal current-only presentation inspection

Inspection of reviewer source SHA-256
`6f15158bfeb276c78c5af6a0ee8d3873c3309c485dcc7c9e998030a0037b3822`
and template SHA-256
`9988052a49e7710fb3c71f303373239c92f8eadc2bd2a8ac4824bd0f74cda941`.
This records reviewer-interface findings, not product evidence or a new command run.

1. **FAIL — misleading missing-source fallback.** The source-link renderer does
   not recognize the `official-publication` repository type. Agreement-backed
   claim `CUR-c5c5c961094767f1` has a bound-source card, but the secondary source
   area says no source pin is recorded. Filtering its source artifact from the
   generic evidence list also produces a contradictory missing-artifact message.
   Correct the publication link and use a bound-source-aware fallback.
2. **FAIL — supported read-only command proof hidden.** Filtering bookkeeping
   carriers hides the only reviewer link for ten PASS claims. Their validated
   read-only adjudication carrier must resolve to selected actual observations,
   without showing the history or treating the carrier as product proof.
   `MCL-aa735864a1cb734d` also has no supplemental mapping in the offline report.

All 227 PASS entries were accounted for: 176 ordinary evidence links, 37 source
cards, four selected direct-install observations and these ten affected entries:

`CUR-142629d88fb18726`, `CUR-705da5057d7f3360`, `CUR-2c04f5e4d6ef0b20`,
`MCL-96ee15f730e698d8`, `MCL-728ef13be833d21e`, `MCL-a54378e7f20b92e9`,
`MCL-e7db8b5148b63289`, `MCL-50f964a1bb6a2e95`, `MCL-f0b9b724554ce68a`,
`MCL-aa735864a1cb734d`.

Retest requirement: every supported card keeps accessible scoped proof, each
selected observation is authorized for the exact page/claim, invalid selectors
fail closed, and history/bookkeeping remains absent from the ordinary review.
Final retests are indexed separately in this attempt's final integrity record.
