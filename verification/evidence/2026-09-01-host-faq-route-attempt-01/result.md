# Common Host questions route and ownership audit — attempt 01

- Attempt ID: `ATTEMPT-2026-09-01-HOST-FAQ-ROUTE-01`
- Evidence ID: `EV-FAQ-C01-ROUTES-01`
- Procedure: `FAQ-C01`
- Test set: `TS-FAQ-C01`
- Branch: `FAQ-C01-routes`
- Step: `FAQ-C01-routes-s01`
- Repository revision: `14d9af21fe8a6df205180d6f211415bf750ee4b8`
- Repository tree: `2eded9e87079a3cb2517ee7a7448018c388b122b`
- Test-set snapshot SHA-256: `50b010956942a3294ea12cbc3936330fbad2be932948a9b4b3e747c8c72c051a`
- Source page SHA-256: `c6b99497891a3e357ffbea1f454d275721bd431013adc284c08cb0b2407dddaa`
- Detailed audit SHA-256: `a1ca0e8051c9b4f77123f214a72cca655706bdf923112c7ba801d98129bb418d`
- Execution class: local static/manual inspection
- External, authenticated, Host, paid, WAN, privileged, or mutating action: none

## Method

1. Inspected all 36 question prompts in `host/common-host-questions.mdx`.
2. Resolved all 38 local Host routes across their 24 destination pages.
3. Resolved all 19 explicit or heading-derived fragment destinations.
4. Compared each question's complete meaning with the destination section that owns the
   answer. A syntactically valid link was not accepted when the destination covered only
   part of the question or was merely a supporting diagnostic page.

The detailed sanitized table is retained at
`.orchestra/host-vv-reconciliation-20260901/findings/faq-route-audit.html`.

## Observation

- Local route resolution: `38/38`.
- Fragment resolution: `19/19`.
- Semantically correct ownership: `33/36` question prompts.
- Material semantic-route defects: `3`.

| Source question | Observed defect |
| --- | --- |
| What Ubuntu and driver versions should I use? | The destination lands on the Ubuntu section but omits the separate NVIDIA-driver section needed to answer the full question. |
| What should I do for NVIDIA/NVML/CDI errors? | The current destination is a supporting evidence-collection page; the Machine Error Reference owns the exact errors and first response. |
| Why is my machine not found, not rentable, or not in search? | The current destination owns listed-but-not-visible search diagnosis, not all combined not-found and rentability states. |

## Disposition

- Step `FAQ-C01-routes-s01`: `FAIL`.
- Branch `FAQ-C01-routes`: `FAIL` because its only required step fails.
- Test set `TS-FAQ-C01`: `FAIL` because its only required applicable branch fails.

This is a documentation semantic-ownership failure, not a broken-file or missing-anchor
failure. The original FAIL must remain retained after correction.

## Limitations

- This proves current repository route, fragment, and source-ownership conformance only.
  It does not prove rendered-browser navigation or the runtime behavior described by the
  destination pages.
- A repository-wide Mint run reported failures outside `host/`; those unrelated results
  were not used to infer this Host procedure's disposition.

## Required correction and retest

Split or add the canonical destinations for the three combined questions, then repeat the
complete 36-question, 38-route, and 19-fragment audit as a new attempt against the changed
source. Do not overwrite or relabel this attempt.
