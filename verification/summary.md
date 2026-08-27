# Host Docs verification and validation summary

Attempt 01 is retained for baseline `VV-HOST-DOCS-2026-08-27-A`. It is not a readiness pass: five local items pass, inventory freshness failed because of an evidence-identity defect, accessibility remains failed, two local checks were blocked by execution context, and two validation classes still require external access or owner evidence.

| Status | Count |
|---|---:|
| PASS | 5 |
| FAIL | 2 |
| BLOCKED | 4 |
| NOT_APPLICABLE | 0 |
| STALE | 0 |
| UNVALIDATED | 0 |
| Total | 11 |

- Disposition coverage: `11 / 11` planned items
- Evaluated local-safe coverage: `6 / 9` items completed with a claim-suitable method
- Passing items: `5 / 11` planned items

See [`README.md`](./README.md) for the plan, [`inventory.md`](./inventory.md) for item status, [`issues.md`](./issues.md) for corrections/retests, and [attempt 01](./evidence/2026-08-27-macos-arm64-attempt-01/attempt-01.md) for raw evidence.
