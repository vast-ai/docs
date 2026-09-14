# Exact source decision

Verification only. Root inspected the fresh public DOM capture in
[terms-source-02.json](terms-source-02.json), retrieved 14 September 2026,
Version Date: September 1, 2026. A separate read-only reviewer reached the same
scope decision. No account or payment observation was used as legal authority.

The sole correction is MCL-06956d724f70d2a3, Host Payouts / Payout Account,
host/payment.mdx line 46. The revised paragraph describes three published clauses:

| Replacement statement | Exact authority | Limit |
| --- | --- | --- |
| Terms contain disclaimers for third-party products/services offered through the website | Disclaimer of Website, /sections/0/text | No finding that a specific payment provider or dispute falls within the clause |
| Terms limit responsibility for delays/failures beyond Vast's reasonable control | Miscellaneous, /sections/2/text | No blanket exemption for all payout delays |
| Some exclusions may not apply under certain state laws | Limitations of Liability, /sections/1/text | No opinion that every exclusion is enforceable |

The public headings have no fragment IDs. Customer citations name the section
and link to https://vast.ai/terms. Reviewer links must open the retained section
text directly rather than an unrelated summary.

The original universal exclusion of provider delays, account holds, compliance
reviews and rejections is withdrawn, not proved. The Hosting Agreement is a
separate source with payment obligations; this update does not decide its
priority or remove those obligations. The Terms do not establish the four other
failed payout/invoice rules. All other occurrence records must remain unchanged.

## Amended decision: restore the published bank-transfer FAQ

The initial one-claim decision above predates the user's bank-transfer
clarification. The continued scope also changes MCL-9826b26393329d27.
[Published FAQ capture](published-payout-faq-01.json), retrieved at
2026-09-14T15:09:07.325Z, retains the exact heading, text, URL and text hash.
It explicitly lists Wise, PayPal and Stripe and says direct bank transfers,
ACH, wire and SWIFT payments are unavailable. Its “Suggest edits” link points
to `vast-ai/docs` main, so it is not independent technical corroboration of
the documentation repository.

Root inspected `git show 0cb28ff871f687225ae6e922ba90bcfe8e6cf4d8:host/payment.mdx`.
That historical local version contains the same restriction. The commit is dated
19 June 2026. This is historical context, not proof of the deployed revision or
of backend routing. A separate read-only reviewer confirmed the same boundary.

Restore the answer as an attributed description of Vast's published guidance.
A scoped PASS establishes that the description accurately reports that
publication, not that bank routes were exercised or independently ruled out.
Keep the earlier provider-setup PASS in history; it did not prove the removed
restriction. The screenshot still establishes only the displayed provider
choices. No provider-mediated transfer, country eligibility, individual account
permission or completed payout is established by this correction.
