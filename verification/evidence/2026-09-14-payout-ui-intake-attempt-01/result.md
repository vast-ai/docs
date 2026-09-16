# Result: evidence received for payout methods

The supplied screenshot shows Stripe, PayPal and Wise in **Payout Account**. The user also reports having used all three. That is useful support for the provider list; it does not call for another test payout.

## Exact findings

| Current finding | Intake finding | Remaining documentation work |
| --- | --- | --- |
| MCL-77f72f0e0ac77e54 — PayPal | Provider option visible; user reports prior use. | Add the official Earnings citation and bind this bounded observation. |
| MCL-a04f3ef2f5a7d5fd — Stripe | Provider option and connected-state wording visible; user reports prior use. | Add the official Earnings citation and bind this bounded observation. |
| MCL-cc62439b0f816902 — Wise | Provider option and connection controls visible; user reports prior use. | Add the official Earnings citation and bind this bounded observation. |
| MCL-9826b26393329d27 — bank-transfer exclusion | No separate direct-transfer card is visible in this crop. | Correct the unsupported blanket ACH/wire/SWIFT prohibition. This view cannot establish it. |

Suggested concise provider instruction: **Choose Stripe, PayPal or Wise in Earnings > Payout Account to set up payouts.** This is proposed wording, not an applied correction.

The source is the user-supplied screenshot, not the Host Docs repeating a list. The URL is user-attributed and the screenshot capture date is unknown. Original screenshot SHA-256: `a8531ae800b796ce185dc468a2e817d958d5362bf37c31284a09214a7dd48819`. Only a sanitized transcription is retained here; the original remains in the user's attachment location. No account email or payment details are copied into repository evidence. A second reader independently checked the proposed scope and cautioned against universal absence, active-account and fee inferences.

## Status and next action

This intake covers all four selected entries but changes no current status: **35 corrections remain displayed**, including these four until the citation/wording edits and retests are completed. It neither rejects the new evidence nor claims the four documentation corrections are already done. The remaining implementation step is to apply the bounded source binding, correct the bank-transfer wording, and refresh both reviewer views with their retests.

No account action, transfer, API call, Host operation, commit or publication occurred. The first baseline capture exceeded tool output length and its JSON could not be parsed; a smaller second capture succeeded before any write. This was an intake-helper failure, not a payout failure.

[Observation and limits](observation.json) · [Target baseline](baseline.json) · [Intake plan](plan.md)

