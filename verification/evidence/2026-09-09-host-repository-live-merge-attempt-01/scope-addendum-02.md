# Generated API route verification — addendum 02

Recorded before implementation. The tool-generated timestamps in retained check
JSON files are the timing authority. The minute labels in the initial plan and
addendum01 were manually estimated and are not execution timestamps.

LINK-01: Repeated `mint broken-links` still reports 99 findings, but an independent
localhost probe returned HTTP200 and distinct expected endpoint titles for
search offers, create API key and show instance; an invented endpoint returns
HTTP404. These representative findings are static checker false positives for
OpenAPI-generated routes. They do not justify rewriting 99 canonical links.

Add a separate generated-route-aware check with regression tests. Derive allowed
routes from the actual docs.json OpenAPI configuration and generator contract,
not a broad /api-reference exclusion. Retain the raw Mint failure, verify all
reported generated targets against localhost (with a negative control), and
leave ordinary broken-link failures actionable. No public Host/API call or
customer-facing text, schema, navigation or claim verdict changes.

The independent root retest, rather than the worker report, determines coverage.
No link finding is marked resolved solely because a static route was guessed.
