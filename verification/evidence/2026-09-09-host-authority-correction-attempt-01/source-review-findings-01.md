# Independent source-review findings

Reviewed against the retained public agreement sections and pinned CLI source,
not against the Host Docs as evidence for themselves. Original claim records are
preserved in the candidate inventory and full predecessor snapshot.

| Finding | Exact occurrence | Original finding / candidate issue | Required correction and retest |
| --- | --- | --- | --- |
| AUTH-SOURCE-01 | Hosting Agreement / Data isolation; MCL-f855ff5e92cfbec1 | FAIL: the old wording permits renter-file access through an unspecified documented platform/support process. The captured Operation and Maintenance prohibition supplies no such exception. This is a source-conflict finding, not a failed runtime test. | Remove that unsupported exception, retain the old wording and finding, bind only the narrowly stated prohibited data operations, and retain residual container rules separately. Recheck exact new literal against the named clause. |
| AUTH-SOURCE-02 | Community / introduction and Hosting Overview / introduction; MCL-181b0127498ba639 and MCL-3cfe1a3c265f0223 | Candidate FAIL: “does not provide” overstates the agreement's narrower allocation of technical-assistance responsibility. | Use the bounded responsibility wording. Do not promote Discord availability or individual setup-support behavior. |
| AUTH-SOURCE-03 | Hosting Overview / introduction; MCL-805ef8a72833f2b8 | Partial source only: the hardware obligation does not establish every driver, storage, or network troubleshooting procedure. | Split the supported hardware duty from the residual operational claims; do not transfer PASS to the residual. |
| AUTH-SOURCE-04 | Hosting Overview / Offers And Rental Contracts; MCL-508003945b6ef934 and MCL-437e58c77dcafecc | Identifier/concept mismatch: pinned CLI declares minimum GPU count and maximum long-term prepaid discount. | Correct `min_gpu` to `min_chunk`; use count and prepaid-discount labels. Bind exact CLI options/request mapping and the historical stored-value readback, with enforcement/calculation limits. |

Candidate implementation review also found insufficient protection against
jointly altered source artifacts and registry hashes, wrong-claim proof transfer,
and text-only deduplication of distinct occurrences. These candidates were not
integrated. Their corrected fail-closed tests are required before final promotion.

No legal interpretation beyond the explicit captured clauses, newly confirmed
product policy, or human acceptance is recorded.

Partial-citation safeguard: MCL-ed68c47bda19e986, MCL-8fe2020c0e7efe26 and
MCL-399798a3c4946b5f were all required-citation FAILs. A clause supporting only
part of each compound statement does not cure missing authority for the
remainder. Retain FAIL with the exact supported subset, missing source, original
evidence lanes and responsible role. Do not relabel these as UNVALIDATED merely
because an agreement link has been added.
