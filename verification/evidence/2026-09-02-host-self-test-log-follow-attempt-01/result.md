# Host self-test log follower attempt 01 result

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SELF-TEST-LOG-FOLLOW-01`
- Status: `PASS` with semantic score `2`
- Scope: `CLM-c36aed4218dd8d33` and `CLM-aa852c9bcbb5b005`
- Started: `2026-09-02T17:42:56Z`
- Finished: `2026-09-02T17:43:00Z`

The documented `sudo tail -f /var/lib/vastai_kaalia/self_test.log` child command opened the file and produced bounded initial output without a path or permission error. A four-second `SIGINT` timeout represented the page's `Ctrl+C` instruction and returned the expected harness status `124`. No follower process remained afterward.

The Host had zero running containers and zero GPU compute processes before and after the attempt. Standard error was empty, and the retained output did not trigger the credential-marker or identifier scans.

This is functional `PASS`, but semantic score `2`: it validates the path, privileges, follow behavior, interruption, and cleanup. No self-test was active, so the attempt does not prove that live self-test progress appears and does not promote either parent procedure.

| Restricted artifact | SHA-256 |
| --- | --- |
| `run.raw` | `013f13abd283099b80fef3555a0752f03d379d707389230796653060f4f339ba` |
| `run.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Raw evidence remains under `../private-evidence/2026-09-02-host-self-test-log-follow-attempt-01/`.
