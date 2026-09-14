# Host source-authority correction — repository result

Host Docs PR185 / CON-1518 · 9 September2026 · starting commit4fa6fbb.
The requested source/classification/citation correction is implemented locally.
This is not full Host Docs acceptance, a new runtime result, or publication.

## What changed

- Four offer controls now require implementation evidence, not blanket policy
  approval: minimum GPU count, interruptible minimum bid, maximum prepaid
  discount, and offer end date. Corrected `min_gpu` to the exposed `min_chunk`
  control and named `discount_rate` precisely. [Pinned CLI source](cli-listing-source-01.json)
  and existing request/readback support control exposure and one stored value
  each—not enforcement, discount calculations, expiry execution or contract terms.
- Five narrowed customer-facing statements and one new security statement cite
  exact matching clauses of the public Hosting Agreement. The retained
  [agreement capture](agreement-source-01.json) records the source and three named
  sections. No version label or heading IDs were exposed; citations name the
  actual sections rather than inventing URL fragments. This establishes those
  obligations, not proof of compliance or new Legal approval.
- Three mixed statements retain FAIL despite a partial citation. Six unsupported
  residual clauses remain separate citation FAILs; Discord availability remains
  UNVALIDATED. Removed an unsupported data-access exception rather than treating
  it as agreement-authorized. Uncovered contract lock-in/concurrency and runtime
  behavior remain unresolved.
- Both review views show the exact passage, status, source and proof limits.
  Original findings remain available; the offline view displays exact predecessor
  wording/status. Contextual links identify the current page and claim rather
  than presenting an unexplained evidence ID.

See the [source guide](source-guide.md), [frozen17-occurrence inventory](candidate-inventory-01.json),
[pre-edit inventory amendment](inventory-amendment-01.md), and
[independent claim-transition reconciliation](claim-transitions-02.json).

## Current scope and counts

**2,013 claims:204 PASS /151 FAIL /23 BLOCKED /4 N/A /1,631 UNVALIDATED.**
Ten bounded statements newly have support. Four citation findings closed, while
six unsupported residual clauses were split out:149−4+6=151. This is more explicit
accounting, not151failed runtime tests. Missing proof alone stays UNVALIDATED.

All2,005 predecessor IDs remain;1,993 untouched proof/status records are exact,
12prior occurrences changed, and8new/split occurrences were added. The original
112procedure records remain auditable; eight changed-source carriers are now
STALE. Four source-only section review records add25nodes, giving116records/
1,085nodes. They are not newly executed Host workflows. All18CLI and15SDK support
layers remain unchanged, separate from44primary Host pages.

## Verification and retained failure → retest chain

The [plan](plan.md) froze AUTH-01–09 before validation. Baseline checks retain
186Python tests,97reviewer tests and158passage controls on five selected pages.

| Check | Retained result and limit |
| --- | --- |
| Exact baseline and preservation | [Baseline](baseline-01.json), [integrity retest](post-model-integrity-03.json): all2,247 old evidence artifacts byte-identical;39out-of-scope pages and all staged content unchanged. |
| Original overbroad classifier | Original failing checks and [four-test retest](classifier-retest-02.json); only four setting classifications change. Real obligations still require authority. |
| Full Python integration | [Initial195-test failure](python-integration-01.json) → [195pass](python-integration-02.json), including exact source identity, residual findings and refusal to overwrite retained static evidence. |
| Reviewer regressions | [Initial admission failures](reviewer-integration-01.json), [stale-count failures](reviewer-integration-02.json) → [102pass](reviewer-integration-03.json). The intermediate87-test run was not the complete five-suite set. Final full run uses all five suites. |
| Current-model generation | [Deterministic current check](model-current-check-02.json):44primary routes/33support layers; inventory/source accounting, not product proof. |
| CLI signatures | [Stale metadata failure](cli-signatures-current-01.json) → regeneration → [204invocations checked](cli-signatures-current-02.json). No documented Host command was executed. |
| OpenAPI/persona/anchors | [OpenAPI contract](openapi-source-contract-01.json), [persona](persona-current-01.json), [named anchors](named-anchors-current-01.json): static source conformance only. |
| Actual browser and proof links | [Unavailable reader](browser-authority-01.json) → [history-link404](browser-authority-02.json) → [passing retest](browser-authority-03.json):44contexts,14selected cards,57contextual proof links,14offline cards;151citation filter and zero remote offline resources. |
| All claims on inventoried pages | [166rendered passage controls](browser-passages-current-01.json) across overview, agreement, workload policy, community and persona; section filters/status fidelity pass. Not a44-page visual audit. |
| HTML final package | The final summary removed a stale count and mislabeled operational row. [Stale-label test failure](html-tests-final-01.json) → [24final export tests](html-tests-final-04.json) and [final browser refresh](browser-authority-final-04.json) cover the corrected report/result payload. This is later than the102-test suite; no later server/Python behavior change is implied. |
| Navigation graph | [Shrink refusal](graph-update-01.json) → [safe AST merge](graph-navigation-refresh-01.json), with8,752unrelated nodes and10,725unrelated edges preserved. The [final scoped refresh](graph-navigation-refresh-02.json) includes the final template tests and three additional changed Python tests. Navigation only, not evidence of product behavior. |
| Sanitation and final identity | The [first check](package-final-01.json) could not resolve its own not-yet-written result; the [second](package-final-02.json) flagged the known synthetic credential fixture in the newly retained collector source. The [final retest](package-final-03.json) exempts only that exact synthetic literal in named test/collector files and permits only its active record and the final seal to be written afterward. A post-seal read verifies all links exist. Limited-pattern sanitation is not an exhaustive privacy guarantee or disclosure authorization. See the [final seal](final-integrity-01.json). |

The [index-byte failure](index-byte-check-01.json) remains recorded. Git index
metadata bytes changed during local work, but independent path/mode/object-ID
comparison and staged-diff hashes match the initially clean HEAD. No content was
staged, no index was restored, and the byte-level difference is not hidden.

Visual inspection confirms the technical setting highlights its exact list item;
the partially cited report statement remains visibly marked as a missing citation.
The offline report remains readable and shows current totals. Full-site
accessibility is not claimed: the earlier74missing-alt findings in19non-Host files
remain separate backlog. Baseline cross-platform runtime coverage is unchanged;
this correction ran repository/browser checks on macOS only.

## What remains, separately

1. [Runtime/operator register](../../current-runtime-operator-blockers.md):
   retain the specific existing Jupyter browser-trust and normal-self-test
   reliability/upload prerequisites. New checks need fresh authorization and safe
   environment; no Host/API/SSH/paid/workload/reboot action ran in this correction.
2. [Source-owner/citation register](../../current-source-owner-blockers.md):
   obtain exact authority for uncovered commercial/contract/operational clauses,
   correct wording or split claims, and retest each occurrence. The agreement is
   not a blanket source for all technical claims. Partial clauses do not close
   their remaining requirements.

The earlier [bounded SSH/Jupyter/self-test result](../2026-09-09-host-ssh-jupyter-selftest-attempt-01/result.md)
remains dated operational evidence with its original limits. No external
workstream, commit, push, merge, Jira post, agreement acceptance or human review
acceptance is recorded here. Required review and publication authorization remain
separate. Final integrity is authoritative for the exact packaged bytes; summaries
and generated interfaces are not evidence for the claims themselves.
