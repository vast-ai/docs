# TS-FAQ-C01 attempt 02 — local/static route audit

> **Portability amendment (2026-09-03; clarified 2026-09-04):** The original
> committed record is preserved as Git blob
> `0390063e4affbccbf26edff273a5d72b90f88774`. This amendment removes the
> workstation-local detail-file dependency by retaining the complete reviewable
> result here. It does not change the attempt's target, method, observation,
> status, or limitations.

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

This tracked record is the complete retained result. The coverage totals, corrected
source lines, disposition, and limitations needed to review the claim are recorded here;
no ignored or workstation-local report is a dependency.

This supports only static source/anchor and semantic-owner conformance, not rendered-site navigation or runtime behavior. Attempt 01's outcome remains unchanged; its tracked record carries the same dated portability amendment. The prior Mint result is context only and does not determine this Host-only audit.
