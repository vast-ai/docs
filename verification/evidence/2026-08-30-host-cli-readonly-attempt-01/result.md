# Host Docs local CLI read-only attempt 01 — result

All nine planned commands executed with the installed CLI
`1.4.2.post7+54c1b69`. Two machine-specific offer searches returned valid empty JSON
arrays with no stderr and pass only their bounded syntax/API-response claims.

Seven commands are `BLOCKED`, not failed: the existing local key lacks `machine_read`,
and the maintenance lookup additionally reports that the selected target is not owned by
the configured account. The correct Host credential must be installed through a secure
local path before retest; no secret from chat was reused.

The run also found a CLI behavior for source review: every HTTP 401/404 response observed
here was written to stderr while the CLI process still exited `0`. This is not yet scored
as a documentation defect.

Raw stdout/stderr files remain outside Git at mode `0600`. Exact hashes, redacted
observations, command mappings, and the 2 PASS / 7 BLOCKED / 0 FAIL rollup are retained in
`results.json`.
