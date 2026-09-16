# Calculator evidence wording: completed locally

14 September 2026. Presentation-only result for MCL-18f04c2ae7ee95b4,
Earnings & Pricing Model / Market Data, host/earning.mdx:103.

The HTML and localhost4000 entry now says what closes its link check: open the
intended calculator, retain the final URL, date/time, screenshot and outcome,
and attach that observation to the exact entry. Separate expandable guidance
explains calculation checks and historical-data sourcing. Those stronger checks
are not required to close the navigation entry. The raw local inspection remains
accessible and is not presented as a calculator visit.

## Checks and scope

- **64 focused tests pass:** `focused-final-04.json`, covering shared copy,
  changed-record guards, offline modal rendering, queue and source preservation.
- **53 Earnings-page passages pass the existing loopback check:**
  `localhost-page-01.json` and `localhost-page-01/`, with exact locations and no
  masked fallbacks. This preceded the final calculator-only limit wording edit.
- **Final targeted browser/API checks pass:** `presentation-04.json` and
  `presentation-run-04.json`. Both cards, the offline modal, live reader-copy
  parity, exact-source HTTP 200 and invalid-selector HTTP 404 are recorded.
  The isolated browser closed. These checks did not visit the public calculator.
- **Deterministic export passes:** `export-check-final-02.json` before the
  display-date update. `export-dated-03.json` records the final HTML with the
  presentation date corrected to 14 September; underlying evidence dates stay
  unchanged. Final HTML SHA-256:
  `fbe8cdbe54b6d60b9b4e29192b9ad1668d7291504fab766ca174ed39b1db73dd`.
  `dated-tests-06.json` and `export-dated-check-03.json` record its final retests.
- **Protected files unchanged:** `integrity-final-02.json` checks 3,749 baseline
  evidence, Host-source and current-registry files. HEAD and index are unchanged.
  The claim model is byte-identical; all 2,013 claim statuses are unchanged.
- **Independent read-only implementation review:** `clarify_policy` found no
  actionable concern in the exact-match guards, scope wording or raw-evidence
  access. This is code/copy review, not calculator evidence.
- **AST graph refreshed:** `graph-update-final-02.json`. Non-code omissions and
  the oversized graph.html skip remain limitations; graph links are not proof.

## Retained failures and corrections

The initial baseline diff capture hit Node's output-buffer limit; a streamed
capture completed before edits. `html-tests-01.json` retains the one-line
function-extraction test failure; the multiline extractor and modal regression
pass in the later 64-test runs. `presentation-01.json` retains a helper's
undefined identifier; `presentation-02.json` passes after correction.
`presentation-03.json` retains a regex-escaping error in the added browser
assertion; `presentation-04.json` passes with literal substring checks.
`dated-tests-05.json` retains the old presentation-date assertion failure;
its expected display date was updated without changing evidence dates.
No earlier result was overwritten or turned into product evidence.

The initial offline screenshots caught the smooth scroll before reaching the
card. Use the final visual recheck, not those images, for the offline layout.
The live card is captured in `localhost-card-04.png`. `visual-recheck-01.json`
and `offline-card-final.png` retain the positioned offline card; the root agent
visually inspected both. These screenshots precede the footer/date-only update.

## Still open

This entry remains **UNVALIDATED** until a suitable destination observation is
retained and attached. No calculator formula, data provenance, estimate accuracy
or future earnings were validated. No paid rental or new owner approval is
needed just for the public destination check. Other source/runtime workstreams
remain open. No Host operation, credential use, commit, push, merge or human
acceptance occurred in this task.
