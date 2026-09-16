# Host Docs V&V third-party review remediation — attempt 01

## Qualification

- Recorded: `2026-09-01`
- Scope: the four independently reported evidence-package defects D1–D4.
- Result: `PASS` for the bounded package-integrity and reviewer claims below.
- Excluded: Host runtime behavior, paid rental behavior, private product facts,
  documentation acceptance, and merge approval.

## Findings and corrections

| Finding | Reproduced result | Correction | Current result |
| --- | --- | --- | --- |
| D1 — parent/child status mismatch | Step `ERR-T04-B02-S03` was N/A while its only command child was UNVALIDATED. | Preserved attempt 01 as history, appended accounting correction attempt 02, changed only that step to UNVALIDATED, corrected the branch rationale, and added derived projection counts. | 972 targets: 78 PASS, 589 BLOCKED, 278 UNVALIDATED, 27 N/A. No PASS changed. |
| D2 — non-portable detail references | Four evidence summaries depended on private orchestration output outside the review package. | Made all four summaries self-contained and added fail-closed path, file, symlink, and private-dependency checks for retained evidence references. | All retained references used by the reviewer resolve beneath `verification/evidence/`; the portability test passes. |
| D3 — score provenance | All 138 numeric scores cited only the contextual assessment record. The first remediation also scoped one historical VM attempt too broadly, used a procedure-method denylist, allowed score-side role relabelling, and treated three partially exercised Market Metrics carriers as score 3. | Added `direct_evidence_ids`, 50 command-specific proof-role bindings, and 20 evidence-owned proof ceilings; linked command observations to owning attempts/files; required each binding to equal its evidence ceiling; scoped each source VM attempt to only its affected commands and required the union to cover the qualifier exactly; made score 3 require current PASS plus exact-full or explicitly equivalent-full functional PASS evidence with an execution form/result and claim limit; added static/partial relabel and uncovered-qualifier negative fixtures. | 8 score-3 records link to six qualifying full functional PASS records. Static or partial evidence cannot be promoted by changing the score-side role. The three partial Market Metrics carriers are score 2. Another 37 score-2 records expose direct evidence; records without it use an explicit empty list. |
| D4 — stale generated inventory assertion | The self-check reproduced a hardcoded 176-command sentence while structured output contained 182 commands. | Preserved the false-positive replay as failed attempt 05, derived the prose count from the generated summary, regenerated the artifact, and recorded passing attempt 06. | Inventory check reports 72 pages, 484 unique targets, and 182 commands in five access groups. |

## Reproduced checks

```text
npm run test-review-context
18 tests, 18 pass, 0 fail

python3 -B scripts/inventory_host_docs.py --check
Host Docs inventory is current: 72 pages, 484 unique targets; 182 commands reconcile across 5 execution-access groups.

npm run check-persona-chips
check_persona_chips: OK — 39 pages, frontmatter and chips in sync

node --check review-server.mjs
node --check scripts/review-context.test.mjs
jq empty verification/host-docs-test-sets.json verification/host-docs-test-results.json verification/host-docs-command-scores.json
git diff --check
All exited 0.
```

The review-context suite used approved loopback binding after the restricted
sandbox correctly denied its first local-listener attempt. The code and input
bytes were unchanged between the environment-only failure and the passing run.

Read-only requests to the restarted port-4000 reviewer confirmed:

- the package is available rather than failed closed;
- the three Market Metrics carriers are score 2 and expose
  `EV-CLI05-MARKET-METRICS` as `DIRECT_FUNCTIONAL_PARTIAL` evidence;
- the Not In Search score-3 commands expose exact-full or explicitly
  equivalent-full functional proof roles; and
- `ERR-T04-B02-S03` is UNVALIDATED through
  `EV-HOST-CURRENT-RECONCILIATION-02`.

## Integrity anchors

| Artifact | SHA-256 |
| --- | --- |
| `review-server.mjs` | `92d1de821ff25f0153aa1f139827eb2f7acb4fdc0302aac503865435d1683183` |
| `scripts/review-context.test.mjs` | `c02f4ef53ed52f8a7d6a9d0755f08e6ae37123f02dc321001e23f9407d3b91b3` |
| `verification/host-docs-test-results.json` | `0a76b61f5f2c141e146d7e03ecd608513008f904afaa4c6f6e568fd357e2ed33` |
| `verification/host-docs-command-scores.json` | `5041dc365d345b4a771f823f43a3db7736d3f09800e106160d11d1ac0d70e66c` |
| `scripts/inventory_host_docs.py` | `e5ffba8bf8eff3bd17ffb6adc87ad31e57f18cc7c73c5aabe497479a6461b954` |

## Limitations and release condition

This attempt qualifies the corrected accounting, provenance, portability, and
reviewer-loader behavior only. It does not convert any BLOCKED or UNVALIDATED
Host target to PASS. The new and modified evidence files must be included in
the eventual commit; a local uncommitted file is not remotely reviewable.
