# Host installer log attempt 01 result

- Attempt ID: `ATTEMPT-2026-09-02-HOST-INSTALLER-LOG-01`
- Status: `PASS`
- Scope: `CLM-fe567beab014649b`

The installer log was found in the confirmed administrator launch directory. From that directory, the exact documented command `cat vast_host_install.log` exited `0`, returned 100,403 bytes across 901 lines, and wrote nothing to standard error.

This directly validates the page's relative-path location and read command on the tested Host, so the command is functional `PASS` with semantic score `3`. It does not validate installation success or generalize the log contents to every Host installation.

The raw log triggered credential-marker, IP-literal, and 64-character-hex review gates. Those may include legitimate installer diagnostics, but the file must remain restricted until a human secret review and sanitization is completed. No excerpt is published in this result.

| Restricted artifact | SHA-256 |
| --- | --- |
| `stdout.raw` | `088e56e97543a7e2974f26df72825fc9e565a4fcf21dbad21230121d7dcb9222` |
| `stderr.raw` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Raw evidence remains under `../private-evidence/2026-09-02-host-installer-log-attempt-01/` and must not be committed or shared as-is.
