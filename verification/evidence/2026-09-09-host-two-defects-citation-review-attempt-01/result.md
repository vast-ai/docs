# Two wording corrections and citation review — bounded result

PR **vast-ai/docs#185** / Jira **CON-1518**, 2026-09-09.
Mode: **PLAN_AND_EXECUTE**. This repository-only correction pass is complete;
Host Docs acceptance and the external evidence workstreams are not complete.

## What changed

| Exact customer passage | Correction and independent proof | Current disposition |
| --- | --- | --- |
| [First 24 Hours / Test Like A Client](http://127.0.0.1:4000/host/first-24-hours#test-like-a-client), source lines 59–61 | Host inventory was replaced by `vastai search offers 'machine_id=<machine_id> verified=any' --limit 200`. [Pinned canonical CLI inspection](cli-query-source-inspection-01.json) and [offline execution of the pinned query parser](cli-query-semantic-retest-01.json) establish the local signature/query interpretation only. | COR-01-MCL-323c8fb8180f5f62-REPLACEMENT is **UNVALIDATED** for live offer visibility/workflow success. Original MCL-323c8fb8180f5f62 remains a historical **FAIL**. |
| [VMs / Check VM Status](http://127.0.0.1:4000/host/vms#check-vm-status), source line 48 | The `off` row now includes the helper being unable to read its configuration. Prior [installed helper source](../2026-09-08-host-client-unblocking-attempt-01/vm-helper-source-retest-02.json) and [unreadable-configuration observation](../2026-09-08-host-client-unblocking-attempt-01/vm-status-01.json) support the bounded correction. | COR-02-MCL-dfebca7edafe9c59-REPLACEMENT is **UNVALIDATED** for upstream implementation/general VM authority. Original MCL-dfebca7edafe9c59 remains a historical **FAIL**. |

The [exact transition registry](../../current-two-defect-transition.json) retains
the two original full FAIL records, replacements, fixed page/evidence hashes and
69 unchanged claim records on the edited pages. It is accounting/source binding,
not independent proof of product behavior. The installed VM helper is not
identified upstream source; the parser test used synthetic machine ID 999999 and
never contacted a machine or API.

## Reviewer outcome

- **149 missing authoritative citations across 24 pages** remain FAIL. The
  localhost:4000 sidebar and [shareable HTML](../../host-docs-review.html) have a
  **Missing authoritative citation** filter, readable reason/owner/next action,
  and a button pointing to the exact customer-facing passage. These are
  documentation/source defects, not failed runtime tests.
- The two replacement cards say **Wording corrected; further evidence needed**,
  preserve the original quoted failures and link directly to scoped proof.
- Current totals: **192 PASS, 149 FAIL, 22 BLOCKED, 4 N/A, 1,638 UNVALIDATED**;
  **2,005** claim occurrences, **44** primary pages and **33** central-reference
  support layers (18 CLI / 15 SDK). Procedures are **112** / **1,060** nodes,
  including new UNVALIDATED heading checks and retained STALE history—not
  completed runtime workflows.

The reduction from 151 to 149 FAIL is two incorrect passages being replaced,
not two new product-validation PASSs. The same 149 citation FAIL IDs are retained.

## Retained verification

| Check | Result / evidence | Limit |
| --- | --- | --- |
| Full Python regression | **176 PASS**, [retest 02](python-full-retest-02.json) | Local parsing, inventory, evidence contracts and fixtures; the retained installer is not run. |
| Full reviewer regression | **81 PASS**, [retest 03](reviewer-full-retest-03.json) | Includes rejection of evidence/status/source/history substitutions and browser-helper scope. |
| Exact current package | [Generator check](current-generator-final-01.json) and [deterministic HTML check](html-current-retest-01.json) PASS | Current source/model/report coherence, not claim truth. HTML embeds 171 source/evidence files. |
| CLI and documentation inventory | [204 CLI signatures](cli-inventory-retest-01.json); [77 routes / 597 targets / 229 commands](material-inventory-retest-01.json) PASS | Source/registry and static inventory only; 33 wrappers are support layers. |
| Persona contract | [44 pages PASS](persona-integrated-01.json) | Frontmatter/chip agreement. |
| Citation UI | [149 cards on 24 pages PASS](citation-browser-final-04.json) | Actual filter, owner/reason/next and every exact passage highlight; no citation authority supplied. |
| Affected-page browser | [211 controls on five pages PASS](affected-browser-final-04.json) | First 24 Hours, VMs, Hosting Overview, Volume Offers, Installing Host Software: exact passage/status/heading controls and accessible control names. |
| Proof relationships and offline view | [Final proof-browser run PASS](correction-proof-browser-05.json) | Both corrections and six unique contextual proof links show their exact statement, heading and UNVALIDATED status. Both offline history cards and the 149 filter work with zero HTTP resource requests. |
| Preservation / API / sanitation | [Final claim-preservation audit](final-claim-preservation-02.json) | 2,003 unaffected full claim records preserved except explicitly allowed transition history/coverage; all 44 API pages current; selected secret-pattern scan only. |
| Knowledge graph | [AST-only refresh](graph-refresh-final-01.json) completed without an LLM call | 9,075 nodes; 307 existing excluded nodes retained, 1,090 files yielded no nodes, HTML graph omitted for size. Navigation aid only, not evidence of Host behavior or exhaustive coverage. |

All original failures remain linked in the
[failure/correction/retest chain](failure-and-retest-chain.md). Read the final
[integrity manifest](final-integrity-01.json) for exact source and artifact hashes.
The checklist outcome is COR-01/COR-02/BIND-01/UI-01/RETEST-01/BROWSER-01/CLOSE-01
complete **within the frozen repository scope**, not human acceptance.

## Preservation and open work

Before edits, the exact dirty tree/index/diffs were captured at HEAD
`bfa926c9421521767fa7411718bd31ea38b38528` on `CON-1584-host-cli-api-sdk` in the
restricted local baseline. The existing staged diff is unchanged. The prior
sealed attempts retain all **107 + 35 + 63** artifacts byte-for-byte; historical
test sets/results/scores were not rewritten. Task-created worker checkouts were
archived, readback-verified and removed, with recoverable private archives
recorded in [initial workers](worker-archives-01.json) and [scope-fix worker](worker-archives-02.json).

Two separate workstreams remain open:

1. [Runtime/operator work](runtime-operator-register.md): approved representative
   execution and workflow observations still required by each exact claim.
2. [Source-owner / Product / Finance / Legal work](source-owner-register.md):
   authoritative citations and decisions, including all 149 citation defects.

No new SSH, credentialed Host/client API call, rental, reboot, privileged or
workload-affecting operation occurred. Only the local documentation proxy was
restarted. No push, merge, Jira post or human acceptance was recorded. Existing
out-of-scope documentation/accessibility findings and external workstreams are
not reported as completed.
