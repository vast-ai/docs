# CLI diagnostic bundle attempt 01 result

- Attempt ID: `ATTEMPT-2026-09-02-CLI-DUMP-LOGS-01`
- Status: `PASS`
- CLI: Vast CLI `1.4.2.post7+54c1b69`
- Scope: `CLM-ac5731cde3180fca` and `CLM-6b3d212806990265`
- Method: local CLI execution with restricted output directory

The documented `vastai dump-logs <machine>` behavior exited `0` and created a readable 847-byte archive. It contained exactly:

- `collection-errors.json`
- `manifest.json`
- `self-test-output.log`
- `self-test-result.json`

The manifest parsed, listed four files, and reported that local Host artifacts were not included. `collection-errors.json` parsed with zero collection errors. Scans found no credential markers, IP literals, or 64-character hexadecimal values. Standard error was empty.

This directly validates manual CLI-visible bundle creation and is semantically score `3` for the two stated command carriers. It does not validate `--include-local-host-artifacts`, instance-log retrieval, or the completeness of an automatic bundle produced after a real self-test failure.

| Restricted artifact | SHA-256 |
| --- | --- |
| `stdout.raw` | `b726ae893ad7cb625a7a6f0c1820246afe4df7f029a37c91600cac1298d68cd7` |
| `stderr.raw` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Diagnostic archive | `0b81ba526a4abe11a2c4fd1e90fea7075a7e49e24ae40a7af2463f641c2c8dfa` |

Raw evidence remains under `../private-evidence/2026-09-02-cli-dump-logs-attempt-01/`. The archive should still receive human review before external sharing.
