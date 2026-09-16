# Payout provider correction and reviewer refresh

Date: 14 September 2026. CON-1518 / PR #185. Mode: PLAN_AND_EXECUTE.

## Approved scope

Apply the user's approved provider wording and remove the unsupported blanket
bank-transfer exclusion. Bind the supplied official-UI screenshot observation
separately from user-reported historical use. Scope is four current Host Payouts
findings: MCL-77f72f0e0ac77e54 (PayPal), MCL-a04f3ef2f5a7d5fd (Stripe),
MCL-cc62439b0f816902 (Wise), MCL-9826b26393329d27 (bank-transfer answer).
No other claim's substantive status may change.

## Basis and limits

Use the retained 2026-09-14-payout-ui-intake-attempt-01 observation and attachment
hash. The screenshot shows three providers in Payout Account; the source URL is
user-attributed and capture time unknown. Retain those limits and exclude email.
The existing intake is a sanitized inspection record, not a self-contained raw
image archive. Do not invent a redacted image, successful payment, fee, country
eligibility, active account, backend enforcement or global transfer prohibition.
The earlier FAQ conflict remains historical evidence, not the basis for a new
universal claim. The replacement is a bounded provider-setup instruction.

## Exact intended customer-facing edits

- Payout Methods intro: The payout providers shown under
  [Earnings > Payout Account](https://cloud.vast.ai/earnings/) are:
  retain the Wise, PayPal and Stripe bullets.
- Replace the bank-transfer FAQ with heading How do I set up payouts? and answer:
  Set up payouts through Stripe, PayPal or Wise under
  [Earnings > Payout Account](https://cloud.vast.ai/earnings/).
- Preserve both older bank-transfer fragment destinations with explicit aliases.
- Keep every unrelated payout statement unchanged, including its review status.

## Checks and success criteria

1. Freeze exact dirty Git-visible state, current model, Host sources and earlier
   evidence hashes before changes. Preserve all prior records.
2. Implement through the existing generation/validation path with strict current
   source and evidence binding; no hand-edited status-only model or UI badge.
3. Four corrected occurrences may become PASS only for the narrowed published-UI
   provider description/setup guidance, not the withdrawn universal exclusion.
   Retain predecessor text/FAIL and reason for correction. If source drift means
   IDs change, explicitly map all four predecessors to successors.
4. Tests use the actual generator/model. Demonstrate baseline failure and corrected
   PASS; test wrong source hashes/text, missing evidence and stale claim bindings.
5. Rebuild the current model, registers, worklist and standalone HTML. Test the
   local payment page and reviewer at port 4000, claim links and evidence modal,
   old fragment aliases, and the offline HTML. The current correction count must
   follow exact records, not a hard-coded target. No whole-page PASS inference.
6. Check sanitation and preservation of unrelated claims, sources and prior
   evidence. Update REVIEW-TRACEABILITY.md and the correction walkthrough with
   final measured counts and limits.

## Safety and ownership

No credential use, live account access, payment, rental, Host action, settings
change, commit to the user branch, push, merge or human acceptance. Browser checks
are localhost/offline only. One isolated worker owns the coupled MDX/model/
validator/test change; root independently verifies and regenerates final outputs,
checks browser presentation and writes final evidence/traceability. Graph data is
navigation, not proof. Any unavailable access is named without promoting status.

## Method clarification during independent review

The original financial-rule classification is too broad for the corrected UI
provider description/setup instruction. The required methods are the supplied
UI observation and exact repository source/link conformance, not an asserted
Finance/Legal authoritative-citation lane. The Earnings URL remains linked and
user-attributed; it is not counted as a second independently retrieved source.
This is a source-method correction within the approved four occurrences, not
permission for a wider policy decision or an additional account operation.
The unchanged screenshot limits remain mandatory in both reviewer views.
