# Host Docs V&V issue and retest ledger

| Issue | Item | Classification | First attempt | Corrective action | Retest | Final state |
|---|---|---|---|---|---|---|
| VV-ISSUE-001 | VV-HOST-001 | TEST_EVIDENCE_IDENTITY | [attempt 01](./evidence/2026-08-27-macos-arm64-attempt-01/attempt-01.md) | Replace repository-HEAD identity with the newest inventoried-content revision plus a SHA-256 fingerprint of exact path names and bytes. Regenerate artifacts. | Pending | OPEN |
| VV-ISSUE-002 | VV-HOST-004 | PERMISSION_ENVIRONMENT | [attempt 01](./evidence/2026-08-27-macos-arm64-attempt-01/attempt-01.md) | Do not alter tests; rerun the frozen command with authorized localhost bind permission. | Pending | BLOCKED |
| VV-ISSUE-003 | VV-HOST-007 | TEST_ISOLATION | [attempt 01](./evidence/2026-08-27-macos-arm64-attempt-01/attempt-01.md) | Make the runner execute Mint against a clean `git archive` snapshot so user-owned untracked files cannot contaminate tracked-tree results. | Pending | OPEN |
| VV-ISSUE-004 | VV-HOST-008 | ACCESSIBILITY | [attempt 01](./evidence/2026-08-27-macos-arm64-attempt-01/attempt-01.md) | Keep the corrected Payment image retest separate. Triage named anchors and shared dark-theme color with the documentation owner; do not bulk-edit or suppress without a decision. | Pending | FAIL |
