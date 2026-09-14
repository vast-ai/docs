# Host Docs commit and PR publication — 14 September 2026

**Published to the existing draft [PR185](https://github.com/vast-ai/docs/pull/185).**
Signed content commit: `95b7165a9cfebe539ec1bbf6115544407ae65ff8`.
Normal push updated `jjziets/docs:CON-1584-host-cli-api-sdk` from bfa926c to
95b7165, including the earlier local progress commit 4fa6fbb. GitHub's PR
head readback exactly matched 95b7165; state OPEN, isDraft true. Its updated
description links traceability, the current offline HTML, the correction
walkthrough, the latest payout result and both open external-work registers.
The check list was empty at readback; this is not a claim of CI success.

## What was checked

- [Pre-staging baseline](baseline.json): 1,749 accumulated task files, with exact
  hashes, HEAD and index state. Publication records were captured separately.
- [Scope and integration preflight](preflight.md): required earlier layers and
  repository references are present. No baseline file exceeds GitHub's 100 MiB
  file limit. Large historical artifacts remain retained, not silently dropped.
- [Privacy disposition](privacy-disposition.json): frozen text, archive and OCR
  checks found no confirmed account-credential or private payment-data blocker.
  The bounded method and remaining operational metadata are explicit; this is
  not exhaustive security certification.
- [Python](python-01.json): 93 passed. [JavaScript](reviewer-01.json): 68 passed.
- The stale 'not pushed' warning failed the
  [new expectation](publication-wording-before-01.json). Its commit/digest
  replacement passed the [35-test focused HTML retest](publication-wording-retest-01.json).
  Those 35 are not additional unique cases beyond the 68-test suite.
- [Final export check](export-check-02.json) passed. The same command after
  commit again returned PASS: 2,013 claims, 280 embedded files, 85,625,989 bytes,
  HTML SHA-256 `b5aaa79052525a9a62439b9f8b8103fe1076230cc96c47af067e05ddc675015e`.
- [Staged snapshot](staged-snapshot.json): zero reviewed-file/blob mismatches.
  The receipt and subsequent [GPG sandbox failure note](commit-signing-sandbox.md)
  were added separately. Signing was retained on the successful retry.

GitHub accepted the push with size warnings for the 81.66 MiB standalone HTML
and 76.98 MiB historical working-tree patch. Download the raw HTML for offline
review; GitHub's file preview is not the interactive reviewer.

## What this does not close

The current claim model is unchanged:
`56650fad892d1f1d387dd4328bdb474f7c2c923907419a2b74868c4a68b7daf5`.
It records 319 scoped PASS, 26 FAIL, 23 BLOCKED, 87 N/A and 1,558 UNVALIDATED
passages across 44 primary Host pages, with 18 CLI and 15 SDK support references.
These are passage counts, not unique product facts or an acceptance score.

The remaining corrections and runtime/operator and source/owner workstreams
remain open. This publication ran no new Host/API, account, payment or paid
operation. It did not merge the PR or record human acceptance. This receipt and
the updated handoff notes follow the verified content push; subsequent Git
commits identify their publication without a self-referential commit hash.
