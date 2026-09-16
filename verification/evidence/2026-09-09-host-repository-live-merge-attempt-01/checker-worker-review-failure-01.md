# Initial route/theme regression review — FAIL, not integrated

The first generated-route checker was not integrated. Root review identified:

- Two routes returned HTTP200 but were classified unmapped. docs.json has exact
  redirects from search/search-template to search/search-templates and from
  billing/search-invoices to billing/show-invoices. Those aliases must be checked
  against the configured redirect graph and actual destination, not rewritten.
- Automatic fetch redirects could leave localhost; the checker needs bounded,
  same-origin-only redirects and timeouts.
- HTTP200 was sufficient for PASS despite the availability of an expected
  generated operation title. Require matching destination/title as well.
- The parser silently excluded non-API findings, and the promised IPv6 handling
  did not account for URL.hostname brackets. Negative tests must cover these.

Separately, the initial contrast script used only a main function and assertions.
It would run no tests during the repository's unittest discovery. It was returned
for discoverable TestCase coverage before integration. No claim status changed.

Both original worker versions remain in task tool history; corrected versions
require independent root execution and retained retests before promotion.
