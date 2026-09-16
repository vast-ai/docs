# Implementation notes: payout provider correction

This worker applied the bounded wording correction and added a fail-closed
four-claim projection. The retained UI observation is the terminal evidence for
the visible Stripe, PayPal, and Wise provider choices; its URL is
user-attributed and its capture time is unknown.

The projection deliberately does not infer a successful payout, active account,
fee, availability by country, provider-mediated bank route, or a universal
ACH/wire/SWIFT exclusion. The former blanket exclusion remains in the pinned
predecessor text and is replaced by provider setup guidance.

Root integration must regenerate the model/reviewer and record its own final
commands and output hashes in `result.md`; this draft is implementation context,
not final acceptance evidence.

[Correction registry](../../../current-host-payout-provider-correction.json) · [UI observation](../2026-09-14-payout-ui-intake-attempt-01/observation.json) · [Frozen plan](plan.md)
