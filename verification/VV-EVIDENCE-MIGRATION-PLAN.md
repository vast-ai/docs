# vv-evidence `ab3c35b` migration plan

- **Operating mode for this document:** `PLAN_ONLY`
- **Procedure target:** `Oxiom-Systems/vv-evidence@ab3c35b5bb7da41bc6bc3cbbefea6bc64c94c7b2`
- **Repository target:** Host Docs PR #185 at current evidence head `09d729e72fbcb2bdd2dead2b9dc5d5e1eeeffcf5`
- **Existing evidence baseline:** `VV-HOST-DOCS-2026-08-27-A`
- **Proposed migration baseline:** `VV-HOST-DOCS-2026-08-27-B`
- **Execution readiness:** ready to implement locally after approval; not authorized for paid, privileged, credential-bearing, destructive, account-mutating, or production execution

## Outcome

Adopt the updated skill without replacing the existing evidence package or rewriting attempts 01–04. Add explicit operating mode, authoritative source/provenance, execution readiness, inventory-change impact, and structured human acceptance. Preserve current stable IDs, raw evidence, issue history, access groups, and status counts.

The migration should end with a new frozen baseline and local-safe replay. It must not imply that the six paid commands, 52 Host-root/privileged commands, 14 Host-context commands, or private product-policy claims were runtime-validated.

## Gap assessment

| Updated requirement | Current state | Planned change |
|---|---|---|
| Explicit operating mode | Attempt records say “Executed,” but the package does not declare one of the three modes | Add `PLAN_AND_EXECUTE` to the implementation baseline and retain `PLAN_ONLY` for this migration plan |
| Authoritative source/rationale for material claims | Exact generated-source SHAs and Jira traceability exist, but the V&V inventory has no authority field | Add structured authority records and references; leave unanswered product facts `PENDING_OWNER` |
| Proportionate/native evidence | Existing Markdown/JSON/CSV, runner, and raw attempts already qualify | Reuse them; do not introduce hooks, CI enforcement, or another project-management system |
| Inventory change record | Baseline change log exists | Add author, rationale, claim impact, and carry-forward/staleness decision for baseline B |
| Execution readiness | READY/NOT READY split already exists | Rename it “Execution readiness” and keep item-class authorization explicit |
| Structured human acceptance | Summary says “Open” | Add authority source, reviewer identity/role, decision, date, conditions/expiry, and closure evidence fields with `NOT DECIDED` defaults |
| Historical evidence integrity | Attempts 01–04 are append-only | Do not edit them; record migration verification in attempt 05 |

## Proposed authority model

Create one compact `verification/authority-map.json` used by both the inventory generator and review UI. It is evidence metadata, not an approval system.

Each authority record should contain:

```json
{
  "id": "AUTH-SELFTEST-SOURCE",
  "kind": "generated-source",
  "state": "CONFIRMED",
  "references": ["vast-cli@<sha>", "self-test@<sha>"],
  "owner": "Vast CLI / Self-Test maintainers",
  "rationale": "Generated reference derives its thresholds and codes from these exact revisions.",
  "claim_limit": "Supports generated-source conformance, not current backend policy or runtime success."
}
```

Allowed authority states:

- `CONFIRMED`: a named requirement, exact source revision, or recorded owner decision supports the claim.
- `PENDING_OWNER`: a Jira issue or named owner identifies the decision, but the fact is not yet confirmed.
- `ADVISORY`: the material is guidance or rationale rather than a product contract.
- `NOT_IDENTIFIED`: no suitable authority is known; the claim remains unvalidated and must not pass.

Every detailed inventory item receives `authority_refs`, `authority_state`, and `claim_limit` independently of its evidence `status`. Authority and runtime evidence must not be collapsed into one field.

Initial authority classes should cover:

1. Host Docs scope and IA — CON-1187, CON-1518, and recorded docs-owner decisions.
2. Vast CLI syntax — exact clean CLI revision and packaged command registry.
3. Generated Self-Test reference — exact Vast CLI/self-test revisions and generator.
4. Repository-native QA contracts — package scripts, review-context tests, OpenAPI source, and docs configuration.
5. Machine errors — CON-1531, `PENDING_OWNER` for catalog/TTL/UI policy questions.
6. Network and ports — CON-1514, `PENDING_OWNER` for protocol and release semantics.
7. Verification policy — CON-1515, `PENDING_OWNER` for queue/wait-time behavior.
8. Host Teams — CON-1581, `PENDING_OWNER` for migration/role/billing behavior.
9. Pricing/business — CON-1256, `PENDING_OWNER` until Solutions Engineering/business review.
10. Review and acceptance — PR #185 plus the identity and authority of the eventual human reviewer.

## Implementation sequence

### 1. Freeze and impact-assess

- Confirm the tracked tree starts clean at `09d729e...`; preserve existing untracked planning, graph, dependencies, and feedback.
- Record baseline B before executing any new checks.
- State that Host content revision and fingerprint are unchanged.
- Mark attempts 01–04 historical and still valid for their recorded targets. They do not prove the new provenance schema.

### 2. Add shared authority data

- Add `verification/authority-map.json` with the records and page/path mappings above.
- Extract the existing Jira issue catalog, page relationships, owner questions, and confirmation state from `review-server.mjs`, `REVIEW-TRACEABILITY.md`, and `REVIEW-QUESTIONS.md` without treating an open ticket as a confirmed fact.
- Update `review-server.mjs` to consume the shared map while preserving the current page panel behavior.
- Extend `scripts/review-context.test.mjs` to confirm the same Jira/page/blocker results and authority states.

### 3. Extend the inventory, additively

- Update `scripts/inventory_host_docs.py` to load the authority map and emit `authority_refs`, `authority_state`, and `claim_limit` in Markdown, JSON, and CSV.
- Keep every existing stable ID and the complete 474-target/176-command reconciliation.
- Fail `--check` when a material threshold, behavior claim, generated-source item, or command lacks an authority reference or an explicit pending/not-identified record.
- Do not change an item to `PASS` merely because an authority record exists.

### 4. Update the reviewer package

- Update `verification/README.md` to cite `ab3c35b...`, declare `PLAN_AND_EXECUTE`, name verification and validation claims, and use the “Execution readiness” wording.
- Add an `Authority / provenance` column to `verification/inventory.md` and link each VV-HOST item to the compact authority records.
- Append the baseline-B change record with author, rationale, affected claims, and staleness/carry-forward decision.
- Expand `verification/summary.md` with source provenance and the structured `NOT DECIDED` acceptance fields.
- Retain the same-agent disclosure and current blockers.

### 5. Freeze, execute local-safe checks, and retain attempt 05

- Commit the baseline-B plan/schema before execution.
- Run only the existing authorized local-safe batch against a clean official Vast CLI checkout and supported Node 24.
- Add authority-map/schema integrity to VV-HOST-001 or a new explicit item; do not hide it inside prose.
- Preserve exact commands, environment, target identities, artifact hashes, results, and stderr as attempt 05.
- Secret-scan proposed committed evidence and verify all generated artifacts are current.
- Keep paid/Host-runtime and private-policy validation `BLOCKED` unless separate access and authority are granted.

### 6. Reconcile and publish for review

- Reconcile disposition coverage, evaluated coverage, and pass rate separately.
- Confirm attempts 01–04 and all failures remain linked.
- Refresh graphify after the generator/review-server changes.
- Commit and push the migration evidence, then post a concise update to PR #185 and CON-1518.
- Leave acceptance `NOT DECIDED`; only an authorized human reviewer may change it.

## Expected file impact

| File | Planned impact |
|---|---|
| `verification/authority-map.json` | New compact authority and page/path mapping |
| `scripts/inventory_host_docs.py` | Additive provenance fields and completeness validation |
| Generated verification Markdown/JSON/CSV | Expose authority state and references per item |
| `review-server.mjs` | Consume shared authority data instead of duplicating page/Jira mappings |
| `scripts/review-context.test.mjs` | Preserve UI mapping behavior and validate authority states |
| `verification/README.md` | New skill revision, operating mode, claims, and readiness wording |
| `verification/inventory.md` | Authority/provenance column and baseline-B change record |
| `verification/summary.md` | Provenance overview and structured human acceptance |
| `verification/run-local-safe-checks.sh` | Hash the authority map and capture the new baseline identity |
| `verification/evidence/...attempt-05/` | New append-only local-safe replay |

## Verification gates

Implementation is ready to publish only when:

- installed skill revision is pinned and recorded as `ab3c35b...`;
- 474 unique targets and 176 commands retain their stable IDs and counts;
- every material item has a valid authority reference or explicit unresolved authority state;
- no unknown or dangling authority ID exists;
- the review-context suite still passes 9/9 or its intentional additions all pass;
- inventory, CLI registry, persona, review server, OpenAPI, Host links, and whitespace checks retain their expected outcomes;
- accessibility remains visibly `FAIL` unless separately corrected and retested;
- paid/privileged/private-policy classes remain visibly blocked without authorization;
- no historical attempt is rewritten or removed;
- acceptance remains a human decision with recorded authority.

## Risks and rollback

- **False authority:** a Jira link alone may identify an owner but not confirm a fact. Use `PENDING_OWNER` until the decision is recorded.
- **Duplicate sources of truth:** the shared map must replace, not merely copy, hard-coded review-context mappings.
- **Historical overclaim:** do not retrofit provenance into attempts 01–04 or describe them as having captured fields they did not record.
- **Schema drift:** version the authority-map and inventory schemas; fail freshness checks on mismatches.
- **Merge conflicts:** PR #185 is currently conflicting. Keep the migration in focused commits so it can be rebased or reverted independently.
- **Rollback:** revert the focused schema/baseline commit and evidence commit together while preserving historical attempts. Do not delete the installed skill automatically; reinstall a pinned prior revision under a separate name if comparison is required.

## Approval boundary

This plan authorizes no repository implementation or new validation execution by itself. A later implementation turn should use the newly installed `$vv-evidence` skill in `PLAN_AND_EXECUTE` mode. Paid Self-Test, Host-root, credential-bearing, destructive, account-mutating, production, or private-system actions still require their own explicit authorization and prerequisites.
