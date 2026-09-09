# Client-account unblocking — plan and frozen initial inventory

2026-09-08. PR #185 / Jira CON-1518. PLAN_AND_EXECUTE with vv-evidence.

## Scope and authority

Use the newly provided client Keychain entry, existing Host Keychain entry, and user-selected alternative Ada Host for read-only evidence; re-adjudicate suitable already-retained command evidence. No paid rental, self-test, GPU workload, root/sudo, Host changes, container inspection, mutation, destructive operation, credential reconfiguration, push, post or human acceptance. The occupied RTX 4090 is excluded from Host operations.

Keys stay only in process memory / child environment, not arguments, files, logs or evidence. Sanitized captures retain request/command, timestamps, version, exact query substitutions as placeholders, response/output hashes, narrowly selected observed fields, exit status and explicit limitations.

## Frozen initial checks

- CLIENT-01: read both explicitly named Keychain entries; GET /api/v0/users/current/ for each, compare nonempty stable account IDs in memory. Retain HTTP status, ID-presence and equality result only. This establishes credential access and whether these two keys resolve to distinct accounts, not rental permission.
- CLIENT-02: with client key GET /api/v0/instances/?owner=me. Retain aggregate state counts and whether any instance belongs to the selected machine. Do not retain unrelated instance identities or renter content. Read only, no stop/cleanup.
- CLIENT-03..05: execute exact documented not-in-search command variants for the selected machine: default search, -n search, and explicit any filters, all --limit 200. Use canonical CLI source entry point; schema/source shows POST /bundles/ is a read-only search, not create. Retain only selected machine offer metadata and response shape/counts; no reservation, no price approval.
- CLIENT-06: execute exact documented show user command with client key. Retain output field names and successful authenticated account-object shape only, with full output hash; never profile values or keys.
- HOST-01: execute documented show machine <machine-id> (text) for selected Ada under Host key to complement prior retained show machines proof. Retain target-specific hardware and state only.
- LOCAL-01: test set api-key with an unmistakably non-secret test fixture in an isolated temporary XDG directory, seeding a fixture to prevent legacy-key migration. Confirm exact file write and preserve real key/config hashes. This proves local credential storage command only, NOT authentication with the fixture.
- ADJUDICATE-01: audit every exact whole command claim covered by the retained 47-check batch; bind only sufficient canonical implementation plus actual execution, and expose contextual limitations. Do not promote parents/compound claims from partial checks.
- BLOCKERS-01: reconcile concrete prerequisites against these new captures. Preserve old attempts. A resolved key-location prerequisite is not proof that a rental/self-test completed, nor does authentication prove machine-read/create scope.
- REVIEW-01: regenerate current JSON, worklists, two registers and standalone HTML; run source-binding negative tests, deterministic checks, reviewer tests, sanitation, and browser checks appropriate to changed UI/data. Update REVIEW-TRACEABILITY.md and retain exact delta/counts.

## Acceptance and unresolved items

Each command/API check gets PASS only for its stated narrow observation with independent retained proof. HTTP/SSH permission or unavailable authorized environment is BLOCKED for that check. Absent evidence alone remains UNVALIDATED; incorrect claim or required missing citation remains FAIL. Full original current claim objects are preserved for any adjudication and current exact literal/source span must match. No Product/Finance/Legal approval is invented.

Inventory expansions require an append-only amendment before execution. Snapshot occupancy cannot reserve a listed machine. Paid work requires explicit test scope, spend/runtime bounds, workload window and cleanup authority for only task-created resources. No automated status may infer these.

## Coordination and verification

Root owns captures, plan, baseline and final integration/verification. Two independent read-only audits cover retained proof and concrete blocker changes. Implementation uses an isolated worktree and exact ownership. The coupled importer/reviewer integration has one owner. Root verifies artifact hashes, strict failure cases and unchanged staged content before handoff.

Initial baseline records exact HEAD, staged/unstaged diff digests, index digest, current-package digest and git status (untracked directories summarized), before any task edits. Earlier attempts and authorizations remain historical data, not new permission.

