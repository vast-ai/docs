# Payout provider correction — repository and reviewer result

14 September 2026 · CON-1518 / PR #185.

The four approved Host Payouts occurrences have been corrected to describe the
Stripe, PayPal and Wise choices shown in the supplied Payout Account screenshot,
and to link the setup instruction to Earnings. The blanket ACH/wire/SWIFT
exclusion was withdrawn, not proved.

The supplied crop has a user-attributed URL and unknown capture time. It proves
only the displayed options within that view, not a payment, active account,
fees, country eligibility, bank-transfer rules or Finance approval.

## Current finding

The four revised occurrences are PASS only for the displayed provider options
and the linked setup guidance. They require a supplied UI observation plus a
repository source/link check, not a Finance approval. The other 2,009 complete
claim records are unchanged. There is no whole-page or whole-workflow PASS.

| Exact occurrence | Revised scope | Independent basis |
| --- | --- | --- |
| MCL-77f72f0e0ac77e54 — Payout Methods | PayPal shown in Payout Account | PAYOUT-UI-PAYPAL-01 |
| MCL-a04f3ef2f5a7d5fd — Payout Methods | Stripe shown in Payout Account | PAYOUT-UI-STRIPE-01 |
| MCL-cc62439b0f816902 — Payout Methods | Wise shown in Payout Account | PAYOUT-UI-WISE-01 |
| MCL-9826b26393329d27 — How do I set up payouts? | Setup through the displayed providers | All three positive provider observations; not the absence of a bank-transfer card |

The source-link record checks the exact Earnings href on lines 31 and 101. It is
not independent proof of provider availability. The terminal UI basis is the
retained inspection of the user-supplied screenshot, not this documentation.
The original attachment hash was rechecked; the image itself is outside this
repository, so the shared transcription is not a self-contained raw image archive.

Current model: 2,013 occurrences on 44 Host pages, with 33 CLI/SDK support layers.
Counts: **312 PASS / 31 FAIL / 23 BLOCKED / 87 NOT_APPLICABLE / 1,560 UNVALIDATED**.
The separate current runtime/operator register is unchanged; the source-owner
register no longer requests Finance authority for these four narrowed UI items.
The 31 remaining corrections are not claimed completed.

## Checks and failure-to-retest links

- Exact dirty input: [baseline](baseline.json), [prior model](pre-correction-model.json)
  and [prior Payment source](pre-correction-payment.mdx). No pre-existing edit was discarded.
- The actual old rendered page failed the intended correction assertions:
  [before](corrected-ui-regression-before-02.json) → [corrected rendered page](corrected-ui-regression-after-03.json).
  All four statuses/passages, both legacy FAQ fragments and exact local proof links pass.
- [Python initial run](root-python-suite-01.json) → [88 tests pass](root-python-suite-02.json).
  Legacy checks use hash-pinned historical Payment bytes; current-source tamper
  checks remain in the new projection. The frozen-source hash is also tested.
- [JavaScript initial run](root-js-suite-01.json), [procedure incompatibility](root-js-suite-02.json),
  [intermediate run](root-quick-js-03.json), [fixture mismatch](root-quick-js-04.json)
  → [38 final tests pass](root-quick-js-05.json). This includes whole-inventory
  source selection, stale/tampered input rejection, export sanitation and deterministic output.
- Root integration corrected the stale live match map and current Payment digest,
  plus the explicit changed-procedure marker. The [first unavailable response](live-unavailable-01.json)
  and [second response](live-unavailable-02.json) are retained; the final browser
  checks exercise the repaired reader rather than treating source tests as UI proof.
- [All 38 Payment locators pass](final-localhost-01-wrapper.json), with full records
  under final-localhost-01. The [offline four-card and proof-dialog check](offline-provider-01.json)
  also passes without remote resources. Final export-only checks are retained separately.

Browser setup failures remain in the attempt records. One initial browser helper
read the blank page left after another checker closed its session; explicitly
opening the page corrected it. Subsequent waits on an unavailable reviewer failed
before a rendered result; they are not successful checks. Two patch-helper calls
failed before edits (shell quoting and a non-unique match), then succeeded with
exact scoped patches. The worker's future placeholder timestamp was replaced with
the observed root integration timestamp; no future check is claimed.

The graph update was AST-only navigation, not product evidence. Its warnings about
unextracted non-code files and skipped large visualization are retained in
[graph update](graph-update-01.json); no semantic-source review is inferred.
The worker checkout's 27 deltas were archived and byte-checked before removal:
[archive manifest](worker-handoff-manifest.json). This is implementation history,
not proof of payout behavior.

## Boundary and next work

No Host/API credentials, account changes, payment, rental, remote financial-source
retrieval, commit, push, merge or human acceptance occurred. Original findings
are preserved in the pinned predecessor; current cards show only the corrected
finding. Next are the four payout/invoice rule questions in the
[remaining correction walkthrough](../../host-corrections-walkthrough.md).

[Plan](plan.md) · [UI observation](../2026-09-14-payout-ui-intake-attempt-01/observation.json)
· [Exact local source-link check](source-link-check.json)
