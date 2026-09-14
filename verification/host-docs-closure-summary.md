# Host docs reconciliation and review

14 September 2026. This is a review handoff, not approval to merge.

The existing inventory is reconciled against **16 tickets and 35 grouped requirements**. Documentation, retained hardware/account evidence and acceptance are accounted for separately. The implementation covers Host lifecycle navigation, account/security guidance, CLI/API/SDK orientation, troubleshooting and the generated Self-Test reference. See the original-ticket matrix in [REVIEW-TRACEABILITY.md](../REVIEW-TRACEABILITY.md).

This integration starts at PR185 revision `646e94e5386aa0e45034c7de339eac275ac2232f`, includes the previously local reviewer changes, and incorporates upstream `175a318c27750ea64da94f043dda39ec5cb26259`. The upstream verification/reliability changes are retained in the canonical Host pages. Record `git rev-parse HEAD` with feedback to identify the actual checkout reviewed.

## Corrections and evidence

**15 of the 26 original findings are addressed:** ten passages were narrowed to supported guidance, and five unsupported application-checklist entries were withdrawn into one existing application instruction. All five historical FAIL records are preserved. **Eleven findings remain**, covering three questions: W-9/VAT handling, offer versus active rental end dates, and availability/maintenance commitments. See [the exact remaining wording](host-corrections-walkthrough.md).

Current active ledger: **335 PASS / 11 FAIL / 21 BLOCKED / 87 NOT_APPLICABLE / 1,554 UNVALIDATED**, across **2,008 passages on 44 Host pages**, plus five retired historical records. The 1,586 open entries are passages, including repeats and shared evidence; they are not 1,586 unique defects or independent tasks. The preceding 1,607-open baseline remains historical. Verified passages retain their recorded evidence scope.

Six retained runtime observations are now linked to applicable passages without promoting partial results to full-workflow success. Two Volume records now correctly describe missing evidence rather than an unavailable prerequisite. Existing installation, listing, rental, SSH and cleanup results remain usable within their actual revisions and environments. No new Host/account, paid, storage, reboot or GPU-burn operation was performed for this correction batch.

The [correction result](evidence/2026-09-14-host-closure-correction-attempt-01/result.md) links exact sources, failures, fixes and retests. Final focused closure/owner checks pass 16/16; historical JavaScript checks pass 32/32 and historical Python checks 20/20. All-44-page reader integration passed before the subsequent source-annotation and canonical-link corrections, which have focused retests. Generator, model/register, exporter, persona and whitespace checks pass within their recorded scope. These results do not constitute human acceptance.

## Decisions still needed

- **Finance and rental/backend owners:** settle the three remaining wording questions or explicitly approve a scoped alternative.
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
