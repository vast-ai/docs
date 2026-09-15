# Lane C review — operations and verification

All 108 frozen occurrences reviewed: 88 supported, 14 substantive corrections, 6 residuals. These are proposals for independent integration; no model or documentation was edited and no new host/account operation was run.

The review reuses exact current CLI/SDK source, dated host/client observations, original product-author Machine Metrics documentation, the independent renter Volumes guide, primary engineering comments and the freshly captured public Host Setup/Agreement. Intended product semantics can be source-reviewed; that does not claim a lifecycle, collector, billing rule or platform transition was executed. Prior partial results and the browser trust/transport failures remain retained.

Substantive corrections cover the Docker partition requirement, recommendation-only Secure Boot, ARM image-build versus eligibility scope, overbroad container-error/deverification examples, the unsupported internal reliability explanation, maintenance/update wording, and Linux metric definitions. The 730 GB example is an ordinary upward rounding of 729.6 GB; it is supported without a rounding-related blocker.

Remaining source questions:

- CUR-718eae8798859de8 — Confirm the verification-state lifecycle: Obtain the verification owner’s state definitions and allowed transitions, then correct or confirm this exact four-state fence. No induced failure or new rental is required merely to document the state model.
- CUR-2a4d8f7b6bf42c0c — Confirm verification-priority guidance: Ask the verification owner to confirm the current prioritized GPU families and whether these dense configurations are priority criteria; retain a dated rule and remove unsupported demand superlatives if needed.
- CUR-0186c37202bd5029 — Confirm ARM support and architecture-specific requirements: Obtain one current owner ruling defining supported ARM64 host families, any beta/access conditions, and how the instruction-set rule differs from x86_64; reconcile this row and Supported Hardware together.
- CUR-1da68c391b45b80a — Confirm ARM support and architecture-specific requirements: Have the hardware/verification owner specify whether AVX applies only to x86_64 and what ARM64 instruction requirements replace it. Correct the paired architecture rows as one topic.
- CUR-ac44298a51ffb285 — Confirm the published verification requirements: Obtain a current security/verification owner rule identifying the exploited-vulnerability restriction and its effect; otherwise retain security-update advice without claiming the undocumented enforcement.
- MCL-d7643ee2685f24ec — Confirm AutoSort ranking and randomness: Resolve together with existing MCL-b106578dbaccc269: obtain the search owner’s current AutoSort definition or remove the unsupported randomness explanation. Treat both occurrences as one source follow-up topic.

ARM rows share one topic with lane B. AutoSort explicitly joins existing MCL-b106578dbaccc269. These are source follow-ups, not six independent defects, inaccessible-host claims, or new release blockers.

The integrity record verifies every current literal SHA, all retained source hashes and exact JSON/line selectors. Source references retain their actual revision and observation limits; no claims outside these 108 are changed.
