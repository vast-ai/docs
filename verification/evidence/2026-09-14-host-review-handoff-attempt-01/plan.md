# Clear reviewer handoff: plan and execute

Scope: PR185 / CON-1518 at 646e94e5386aa0e45034c7de339eac275ac2232f.
The initial working tree and index were clean. Capture the exact current model,
reader sources and all prior evidence hashes before making implementation edits.

The user's request authorizes a repository-local reviewer improvement: make open
work visible, distinguish checked source wording from confirmed rules, and retain
the six concrete owner questions raised in the preceding review. It does not
authorize new Host/API, account, rental, payment, Jira, push, merge or acceptance
actions. Do not introduce or resolve product claims while changing presentation.

## Acceptance inventory

| ID | Required result | Method and retained evidence |
| --- | --- | --- |
| UX1 | Port4000 shows page-wide corrections, pending checks and blockers prominently, independent of the selected heading. Review-note counts cannot look like an all-clear. | Before/current API and browser observations; focused code tests. |
| UX2 | Open claims appear before completed claims. One obvious control shows all page corrections and resets conflicting filters. Checked claims remain discoverable. | Real Datacenter page: 5 FAIL, 2 UNVALIDATED, 10 PASS; browser check with a Requirements hash and conflicting filters. |
| UX3 | Published-source checks are not displayed as policy approval, runtime proof or human acceptance. | Source-only and runtime examples from the real model; Payment threshold and its bound source controls. |
| UX4 | Six explicit open questions remain visible above claim filters, with proposed teams, precise question, related passages and required decision/source. | Datacenter documents and certification; payout threshold; deletion/volume retention/secure erasure; personal workloads; Vast-specific tax handling. Each remains UNVALIDATED, not automatically BLOCKED. |
| UX5 | Owner questions are separate from claim counts and evidence. No named owner, approval, uploaded documents, secure-erasure guarantee or new product fact is invented. | Registry validation and independent review; actual current passage IDs/headings; missing wording labeled as a coverage gap. |
| UX6 | The standalone HTML has the same summaries, distinctions, owner questions and direct passage/proof access. Questions follow the page filter, not status/category filters that could hide them. | Export integrity and browser inspections for Datacenter, Payment, Volume Offers, Workload Policy and Tax Guide. |
| UX7 | All 2,013 claims, statuses, source/evidence bindings, source pages and prior evidence remain unchanged. Current totals stay 319 PASS / 26 FAIL / 23 BLOCKED / 87 N/A / 1,558 UNVALIDATED. | Baseline/final SHA comparison, current-Host regressions, reader/export tests; source binding and evidence-link checks. |
| UX8 | Handoff and traceability describe the new controls and distinguish current open questions from historical results. | Root review of the rendered views and updated handoff notes. |

The six questions are a selected handoff list, not an exhaustive inventory of all
policy decisions or six additional failed claims. Existing clear source authority
remains usable; owner escalation is reserved for the recorded gap or conflict.

## Execution and accountability

Use one isolated implementing worker for the coupled reader/export files and
question registry. Root owns this plan, baseline, independent checks, generated
HTML/export, traceability and integration. A separate reader checks scope,
wording, source/approval distinctions and cross-view behavior. Preserve failing
tests and link them to retests; do not overwrite old evidence. Main performs
regression, browser and final integrity checks, not merely relay worker claims.

PASS applies only to the scoped reviewer behavior checked at the recorded version.
A missing renderer, wrong count, hidden question or false approval is FAIL.
An unavailable required environment is BLOCKED with its exact prerequisite;
unchecked behavior is UNVALIDATED. No result changes the underlying Host claims.
