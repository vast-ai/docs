# Reviewer handover cleanup

Mode: PLAN_AND_EXECUTE. User approval: correct the overbroad review backlog and
prepare an understandable handover. Target: the exact dirty-tree baseline in
baseline-01.json, 44 Host pages / 2,013 current claim occurrences, with 18 CLI and
15 SDK support references kept separate. No customer-text change is required.

| Check | Basis and method | Expected result and evidence |
|---|---|---|
| CLEAN-01 Inventory | Inspect every current claim's status, classification, required checks, page and passage; distinguish occurrences from shared work. | Complete reconciled inventory; nothing hidden or silently discarded. |
| CLEAN-02 Editorial decisions | Inspect exact passages in context. Pure labels/preambles are not product assertions. Advice gets a clarity/safety review; calculations get arithmetic checks; navigation gets destination/heading checks. | Explicit per-occurrence decision and limits. PASS only for completed claim-appropriate checks, NOT_APPLICABLE only for recorded non-claim rationale. Ambiguous/mixed factual advice remains open. |
| CLEAN-03 Safe local checks | Use retained or fresh repository/localhost checks for exact navigation and calculations. Do not infer technical behavior from a working link. | Inputs, observed outputs, source hashes and result per selected occurrence. Original failures retained, corrections linked to retest. |
| CLEAN-04 Actionable handover | Show editorial, source/citation, technical and blocked work separately. Group only demonstrably compatible shared questions, retain all passages and distinct status/prerequisites. | Both offline HTML and localhost4000 use the same grouping/categories; exact counts, readable questions, source/proof links, no blanket PASS. |
| CLEAN-05 Integrity/retests | Python and JavaScript projection/regression suites; category/count/group/negative tests; local rendered-page and offline browser checks; old evidence/index/source preservation. | Retained exit codes, hashes and screenshots; no previous PASS/FAIL/BLOCKED silently overwritten by broad rules. |
| CLEAN-06 Handover | Refresh report, traceability, progress, two external registers and graph index. | Current entry point, completed local work, explicit remaining work and exact next actions. |

UNVALIDATED means the appropriate check is incomplete or support insufficient.
FAIL means a confirmed defect, including a required missing citation. BLOCKED
requires a specific unavailable permission, environment, input or owner. A
classification correction alone is not completed verification. Documentation is
the object of review, not independent evidence for its product statements.

Safety: repository and loopback only. No Host/API/SSH, credentials, paid workloads,
privileged commands, reboots, external posting, push, merge or human acceptance.
Retain history below the current finding rather than making reviewers read it first.
Use independent inspection of selected dispositions; root verifies integrated
outputs and records the remaining limitations.
