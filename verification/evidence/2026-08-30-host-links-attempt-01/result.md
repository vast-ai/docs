# Host Docs link check attempt 01 — result

- Evidence ID: `EV-HOST-LINKS-01`
- Command: `npx mint broken-links`
- Process exit code: `1`
- V&V status: `PASS` for the scoped authored Host pages; repository-wide result remains `FAIL`

Mint reported 104 broken links in 11 files. No file under `host/` appeared in
the reported offender list. Five findings were in the root
`HOST-DOCS-QA-SUMMARY.md`; the remaining findings were in existing API, guide,
and SDK files outside the authored Host-page population.

Claim limit: this supports only that Mint's current scanner did not report a
broken link originating from an authored `host/*.mdx` page in this run. It does
not establish repository-wide link health, external-link reachability, or
rendered interaction correctness.
