# Host docs reconciliation and review

14 September 2026. This is a review handoff, not approval to merge.

The existing inventory is reconciled against **16 tickets and 35 grouped requirements**. Documentation, retained hardware/account evidence and acceptance are accounted for separately. The implementation covers Host lifecycle navigation, account/security guidance, CLI/API/SDK orientation, troubleshooting and the generated Self-Test reference. See the original-ticket matrix in [REVIEW-TRACEABILITY.md](../REVIEW-TRACEABILITY.md).

This integration starts at PR185 revision `646e94e5386aa0e45034c7de339eac275ac2232f`, includes the previously local reviewer changes, and incorporates upstream `175a318c27750ea64da94f043dda39ec5cb26259`. The upstream verification/reliability changes are retained in the canonical Host pages. Record `git rev-parse HEAD` with feedback to identify the actual checkout reviewed.

## Corrections and evidence

**24 of the 26 original findings are handled:** nineteen passages have narrower supported guidance, and five unsupported application-checklist entries were withdrawn into one existing application instruction. Original FAIL assertions and evidence remain in history. **Two tax findings remain**, covering Wise/W-9 and VAT handling. Nine rental-date and availability assertions were removed from active wording; their replacement PASSes cover source declarations, Agreement referrals and review advice only. Backend date semantics and maintenance-policy questions remain open separately. See [the exact remaining wording](host-corrections-walkthrough.md).

Current active ledger: **345 PASS / 2 FAIL / 21 BLOCKED / 87 NOT_APPLICABLE / 1,553 UNVALIDATED**, across **2,008 passages on 44 Host pages**, plus five retired historical records. The 1,576 open entries are passages, including repeats and shared evidence; they are not 1,576 unique defects or independent tasks. The earlier 1,586-open attempt-01 and 1,607-open predecessor counts remain historical. Checked passages retain their recorded evidence scope.

The new rental batch changes exactly eleven claim objects: nine original FAILs become scoped replacement PASSes, one adjacent unlisting instruction becomes a declaration/context PASS, and the example-date label stays NOT_APPLICABLE. The other 1,997 current claim objects and all 36 attempt-01 artifacts are unchanged. Shared introductions and list/unlist commands are preserved. Seven newly affected procedure nodes are STALE with prior evidence retained; no operational result is promoted.

Six retained runtime observations are now linked to applicable passages without promoting partial results to full-workflow success. Two Volume records now correctly describe missing evidence rather than an unavailable prerequisite. Existing installation, listing, rental, SSH and cleanup results remain usable within their actual revisions and environments. No new Host/account, paid, storage, reboot or GPU-burn operation was performed for this correction batch.

The [attempt-02 result](evidence/2026-09-14-host-closure-correction-attempt-02/result.md) records the exact nine-plus-two mapping, sources, limits and checks. All 18 selected closure/owner checks have passing results: the first run passed 17/18, then the missing-result-file payload check passed its focused retest. The original failure remains recorded. Model/register generation and whitespace checks passed. Root rendered all five edited pages and confirmed the new guidance, absence of the withdrawn assertions, preserved commands and stable source hashes. Independent code review found no blocking issue. Root source-control checks passed 3/3 with the exact canonical source URLs; the focused offline-context payload retest passed 1/1. Final HTML generation and consistency checks passed for 323 embedded files and 2,008 claims. The report is 99,198,053 bytes (below 100 MiB); its native manifest records the exact digest. Final model/register and whitespace checks passed.

The [attempt-01 result](evidence/2026-09-14-host-closure-correction-attempt-01/result.md) retains its earlier 16/16 focused checks, 32/32 historical JavaScript checks and 20/20 historical Python checks. Its all-44-page integration, generator, exporter and persona checks retain their exact earlier scope and revisions; they are not claimed as new attempt-02 runs. Neither attempt records human acceptance.

## Decisions still needed

- **Finance/tax owner:** resolve the two remaining Wise/W-9 and VAT assertions, including the separately pending Tax Guide scope choice.
- **Marketplace/backend and Hosting Agreement owners:** identify the implemented offer/rental date rules, constant-duration behavior and applicable availability/maintenance guidance. Removing unsupported wording did not answer these two owner questions or establish safe-stop permission.
- **Product/Security with Host/Storage Engineering:** approve the data-lifecycle and sanitization statement tracked in [CON1187 comment77494](https://vastai.atlassian.net/browse/CON-1187?focusedCommentId=77494).
- **Teams/account engineering:** answer the existing migration, earnings and registration/role questions in [CON1581](https://vastai.atlassian.net/browse/CON-1581).
- **Machine Error Reference source owner:** supply the backend back-pointer locator and the chosen upkeep implementation or filed follow-up for [CON1531](https://vastai.atlassian.net/browse/CON-1531). The required overview link is now present. Reuse [HOST3713](https://vastai.atlassian.net/browse/HOST-3713) for its NCCL-specific scope.
- **Asset/Product review:** finish the existing identifier-redaction and content-review requirement for the nine supplied screenshots. Their delivery is established; capture availability is no longer the blocker.
- **Docs/Product and Gobind:** record IA/business acceptance and explicit scope decisions for the hardware-catalog/changelog and verification-queue proposals.
- **Support/operations and QA:** agree bundle intake/retention and the original size-target disposition; accept the existing paired Self-Test follow-up within its actual source/revision limits. Earlier scoped CLI approvals remain valid and are not replaced by these pending decisions.

Some accountable owner names remain unassigned. Do not interpret proposed teams or historical reviewer requests as approval. PR185 requires an approving review before merge; record final acceptance, merge revision and actual publication state separately.

## How to review

Use [PR185 Files changed](https://github.com/vast-ai/docs/pull/185/files) for inline feedback, or follow the [local preview and feedback-export instructions on CON1187](https://vastai.atlassian.net/browse/CON-1187?focusedCommentId=77498). Open [host-docs-review.html](host-docs-review.html) from the same checkout for the standalone report. Source pages, review service and evidence must match the report revision. Feedback saved locally must be exported and shared; it is not automatically posted to Jira or GitHub.

Success remains accepted documentation for the agreed ticket scope, with material uncertainties resolved or explicitly dispositioned, the final PR checked and approved, and merge/publication recorded. Making every passage green is not a separate acceptance requirement.
