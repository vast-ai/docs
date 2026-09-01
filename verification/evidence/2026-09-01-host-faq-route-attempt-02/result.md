# TS-FAQ-C01 attempt 02 — local/static route audit

## Scope

- Attempt ID: `ATTEMPT-2026-09-01-HOST-FAQ-ROUTE-02`.
- Evidence ID: `EV-FAQ-C01-ROUTES-02`.
- Procedure: `TS-FAQ-C01` / `FAQ-C01-routes` / `FAQ-C01-routes-s01`.
- Target: `host/common-host-questions.mdx` at SHA-256 `d176fcf45a2948f427b13ae186c00da4051a8d6586592da1d4b16b436c960f3b`.
- Repository revision/tree: `14d9af21fe8a6df205180d6f211415bf750ee4b8` / `2eded9e87079a3cb2517ee7a7448018c388b122b` (working source is newer than that tree).
- Test-set snapshot SHA-256: `50b010956942a3294ea12cbc3936330fbad2be932948a9b4b3e747c8c72c051a`.
- Detailed audit SHA-256: `e8336b48a3ddaded8c4d24afdfd11b54adf3eef22aa2cf0e413220309cbac593`.
- Method: local source and fragment inspection only; no browser, network, account, Host, or paid action.

## Coverage and result

- 36/36 question prompts inspected.
- 38/38 local `/host` routes resolve across 24 target pages.
- 19/19 fragment routes resolve to an explicit anchor or heading-derived section.
- 0 semantic-route defects remain after the focused corrections at source lines 39, 41, and 54.

Proposed disposition: step `PASS`, branch `PASS`, test set `PASS`.

## Evidence and limitations

Detailed sanitized report: [FAQ route audit attempt 02](../../../.orchestra/host-vv-reconciliation-20260901/findings/faq-route-audit-attempt-02.html).

This supports only static source/anchor and semantic-owner conformance, not rendered-site navigation or runtime behavior. Attempt 01 remains unchanged. The prior Mint result is context only and does not determine this Host-only audit.
