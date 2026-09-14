# Host docs review traceability

Jira status snapshot: 2026-07-13 (not re-verified by this repository review)

Retained 40-page repository V&V reconciliation: 2026-09-03

Current upstream integration: 2026-09-07 (44 primary Host pages; freshness and
new-page review coverage are separate from the retained 40-page proof).

Review PR: [vast-ai/docs#185](https://github.com/vast-ai/docs/pull/185)

## Publication checkpoint, 14 September 2026

The accumulated Host Docs corrections, offline review HTML and traceability
were committed and pushed as
[95b7165](https://github.com/jjziets/docs/commit/95b7165a9cfebe539ec1bbf6115544407ae65ff8).
GitHub PR185 readback matched that content commit, and its description now links
the current review package, remaining corrections and localhost setup instructions.
The PR remains **open and draft**, not merged or accepted.

Publication retests passed 93 Python and 68 JavaScript tests, with the final
publication wording checked separately and the HTML export unchanged after
commit. The bounded privacy/archive audit found no confirmed credential or
private payment-data blocker. The current claim totals below did not change.
No new Host/API, account, payment or paid operation was performed. The empty
GitHub check list at readback is not a CI PASS.

[Publication result and limitations](verification/evidence/2026-09-14-host-docs-publish-attempt-01/result.md)

## Current payout and invoice guidance correction, 14 September 2026

Four citation corrections and two repeated timing passages now cite the exact
published guidance. The unsupported noon-Pacific time is removed. First-payout
estimates retain their provider/region qualifications; the Agreement's billing
clock has its own source control. Both reviewers say "Published guidance checked"
and explain that this does not test invoice generation or payment processing.
The publication shares this docs repository: it supports the attributed description,
not independent backend behavior. No Finance or Legal approval is inferred.

Current totals: **319 PASS, 26 FAIL, 23 BLOCKED, 87 NOT_APPLICABLE and 1,558
UNVALIDATED**. Six complete claim records changed; 2,007 others and all 3,822
prior evidence files are unchanged. The 44 Host pages and 33 support layers remain.
The review queue now recognizes 11 supported payout findings instead of calling
them "Needs triage". That display correction changes no claim status or evidence.

Regression retests passed **93 Python and 68 JavaScript tests**. All 38 Payment
passage locators pass, with six exact current source mappings checked in both
reviewer views. Initial failures remain linked to corrected retests.

[Current result and source limits](verification/evidence/2026-09-14-payout-invoice-correction-attempt-01/result.md)
· [Correction walkthrough: 26 remain](verification/host-corrections-walkthrough.md)
· [Runtime/operator work — open](verification/current-runtime-operator-blockers.md)
· [Source/owner confirmation — open](verification/current-source-owner-blockers.md)

This completes the selected repository correction, not all Host Docs V&V.
No payment, Host operation, push, merge or human acceptance was performed.

## Earlier payout citations and FAQ correction, 14 September 2026

The bank-transfer FAQ now reports Vast's published restriction on direct bank
transfers, ACH, wire and SWIFT. The Payout Account note describes three named
Terms sections with their reasonable-control and state-law qualifications.

Exactly two claim records changed: MCL-9826b26393329d27 and
MCL-06956d724f70d2a3. The current totals are 313 PASS, 30 FAIL, 23 BLOCKED,
87 NOT_APPLICABLE and 1,560 UNVALIDATED. The other 2,011 claims and all
3,767 prior evidence files are unchanged. These checks establish the published
wording, not a completed payment, bank-route implementation or legal acceptance.

Both exact passages and their source controls pass in the localhost and offline
reviewers. All 38 payout-page claim locators pass. The final regression retest
passed 91 Python and 39 JavaScript tests; the retained result below records the
initial failures and their corrections separately.

[Current result and exact source limits](verification/evidence/2026-09-14-payout-terms-correction-attempt-01/result.md)
· [Integrity check](verification/evidence/2026-09-14-payout-terms-correction-attempt-01/final-audit-01.json)
· [38 rendered claim checks](verification/evidence/2026-09-14-payout-terms-correction-attempt-01/rendered-payment-01/summary.json)

## Earlier payout options correction, 14 September 2026

Four Host Payouts passages now have bounded support: PayPal, Stripe and Wise as
shown under Earnings > Payout Account, plus the replacement setup instruction.
The universal ACH/wire/SWIFT exclusion was withdrawn, not verified.
The supplied screenshot has a user-attributed URL and unknown capture time; it
does not establish successful payments, fees, eligibility, active account state
or bank-transfer rules. The documentation link check is separate from the UI proof.

Current totals: **312 PASS, 31 FAIL, 23 BLOCKED, 87 NOT_APPLICABLE and 1,560
UNVALIDATED**, across the same 2,013 occurrences. All 2,009 other claim records are
unchanged. The 44 Host pages and 33 central-reference support layers are unchanged.
Only four Payment source lines changed; both old FAQ fragments remain available.

The standalone HTML and localhost reviewer show the exact revised passages and
their evidence. Root checks include 88 Python tests, 38 JavaScript tests, all 38
Payment passage locators, and the four proof-link/dialog checks.
Earlier failures and old wording remain in audit records, not the current finding.
See the [correction result and retests](verification/evidence/2026-09-14-payout-provider-correction-attempt-01/result.md)
and [31 remaining corrections](verification/host-corrections-walkthrough.md).
No account action, payment, publication or human acceptance was performed.

## Calculator proof guidance, 14 September 2026

MCL-18f04c2ae7ee95b4, Earnings & Pricing Model / Market Data, now explains
what closes its link check: confirm the intended calculator opens and attach
the final URL, date/time, screenshot and outcome. Calculation accuracy and
historical-data sourcing have separate, conditional instructions. Neither is
required to close this navigation entry. Both reviewer views retain the original
record; the entry remains UNVALIDATED. No claim or evidence was promoted.
See the [bounded presentation result](verification/evidence/2026-09-14-calculator-proof-clarity-attempt-01/result.md).

## Current handover cleanup — 11 September 2026

The review now separates **what kind of check is needed** from **whether it is
finished**. “Review pending” does not mean a failed test or an external blocker.
All 2,013 passages remain traceable across 44 Host pages. The 18 CLI and 15 SDK
references remain support layers, not extra Host workflows.

151 selected occurrences were reviewed in context. **67 documentation checks
passed within their scope; 74 labels, introductions or hypothetical inputs were
classified as non-claims; 10 selected items remain pending.** The 1,862 other
complete claim records, all 3,498 prior evidence files and all 77 Host source
files are unchanged. No customer-facing statement was removed to reduce a count.

| Current work queue | Passages |
| --- | ---: |
| Documentation checks | 10 |
| Source/citation checks | 534 |
| Technical verification | 1,016 |
| Prerequisite unavailable | 23 |
| Correction needed | 35 |
| Checked within scope or not applicable | 395 |

These are passage counts, not unique questions. The underlying statuses are
**308 PASS / 87 N/A / 1,560 UNVALIDATED / 35 FAIL / 23 BLOCKED**. Every passage
keeps its own source context, evidence limits and next action. Exact compatible
shared wording can be grouped, but that does not merge proof or decisions.

The HTML and localhost reviewer use the same categories. The localhost panel
keeps explanations collapsed so the filters and passages are easier to reach.
Documentation checks are shown as local review records, not product proof.

Current checks cover 237 Python tests, all 44 localhost pages / 2,013 cards,
and 16 offline browser groups with 289 bound source/check controls. The live
passage check includes 1,994 exact highlights and 19 explicit masked fallbacks.
All 204 JavaScript cases have passing coverage across the full run (203 pass)
and the remaining case's focused retest; the failed full run remains recorded.
Regression-fixture failures and their linked retests are retained in the result.
The graph/index is navigation only; it is not another source of product proof.

[Current result and retained checks](verification/evidence/2026-09-11-host-review-cleanup-attempt-01/result.md)
· [Shareable review and local setup instructions](verification/host-docs-review.html)
· [Runtime/operator work](verification/current-runtime-operator-blockers.md)
· [Source/citation work](verification/current-source-owner-blockers.md)

The two evidence workstreams remain open. No new Host/API/SSH access, credentials,
paid operation, reboot, commit, push, merge, external posting or human acceptance
is included in this cleanup.

## Earlier source finding — 11 September 2026

Eight bounded source/advice findings are now supported: three Tax Guide
instructions, one Workload Policy instruction/rule, and four Datacenter program
statements. Exact government, provider, Agreement and Vast program citations are
bound to the relevant wording. Secure Cloud audits and Certified Data Center
requirements are attributed separately. Advice review is not proof of personal
tax compliance, actual program eligibility or platform enforcement.

Current inventory: **44 primary Host pages / 2,013 claims: 241 PASS / 35 FAIL /
23 BLOCKED / 13 N/A / 1,701 UNVALIDATED**. Six citation defects and two
unvalidated findings were resolved. The other **2,005 complete claim records**
and all **3,329 prior evidence files** remain unchanged. CLI/SDK wrappers remain
18/15 reference-support layers, not extra Host workflows.

The [official-source scan](verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01/source-scan.md)
covers US, California, UK and EU authority and names remaining gaps. General law
does not establish Vast's withholding, VAT, international-document or payout
practices. Older Vast pages also conflict with the draft on ACH and unused-GPU
scope; those questions remain open.

The report and localhost reviewer show current findings first, with plain next
steps, exact passage links and official source excerpts. Citation-only tax cards
no longer discuss failed runtime tests. Earlier limits and our review notes are
separate from independent source proof. Historical records are retained without
being shown as current gaps.

Broad checks pass: **232 Python tests, 187 JavaScript tests, all 44 localhost
pages / 2,013 cards, and 15 offline browser groups with 138 source controls**.
Final presentation-specific retests and export hashes are recorded in the result.
The source mismatch guards remain strict; initial fixture failures are preserved.

[Current result and checks](verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01/result.md)
· [Shareable review](verification/host-docs-review.html)
· [Runtime/operator work](verification/current-runtime-operator-blockers.md)
· [Source/owner gaps](verification/current-source-owner-blockers.md)
· [Current derived index](verification/current-host-authority-index.md)

This is a local, bounded repository/source review. No new Host/API/SSH, credentials,
paid run, reboot, commit, push, merge, Jira post or human acceptance occurred.
The runtime/operator and source-owner workstreams are not complete.

## Dated predecessor — 10 September 2026

The following retains the earlier state and counts; it is not today's result.

### Reviewer presentation: separate rental questions

The four mixed **Hosting Overview / The Rental Contract** cards now show only
their own statement: pricing behavior, offer end dates, unlisting or required
availability. Each links to the existing, separate pricing-guidance finding.
Related or partial sources use a neutral, collapsed section; their presence
does not imply that the open statement passed. Page controls highlight only
the relevant bullet. Full recorded wording and source bindings remain in the
audit details. No claim status, customer-facing text or evidence was changed.
Both views pass the four-card interaction check. The broader checks cover all
44 Host pages / 2,013 cards and 15 offline groups. All 172 unique JavaScript
cases pass across the suite and a focused integration-fixture retest; the
initial failure and correction remain linked in the result below.

[Split-card checks and result](verification/evidence/2026-09-10-host-split-review-attempt-01/result.md)

### Published Terms findings

Six statements in **Workload Policy / Restricted Activity** now cite the
applicable clauses of the published Vast Terms (version 10 November 2025).
The current inventory is **44 primary Host pages / 2,013 claims: 233 PASS /
41 FAIL / 23 BLOCKED / 13 N/A / 1,703 UNVALIDATED**. The 18 CLI and 15 SDK
wrappers remain reference-support layers. All other 2,007 claim records are
unchanged.

These six findings establish what the published rules say, not whether the
platform enforces them or a host complies. Mining wording retains the Terms'
credit-card condition; no blanket ban is inferred. Existing Agreement citations
remain separate. Reviewers can follow the exact page passage and retained
section/item excerpt. Current findings lead; historical attempts stay in the
audit records.

Final checks pass: **226 Python tests, 171 JavaScript tests, all 44 localhost
pages / 2,013 claim cards, and 15 offline HTML check groups**. The final export
is deterministic. These checks establish source bindings and reviewer integrity,
not runtime behavior or human acceptance.

[Terms source-binding result and checks](verification/evidence/2026-09-10-host-terms-binding-attempt-01/result.md)
· [Shareable review](verification/host-docs-review.html)
· [Runtime/operator work](verification/current-runtime-operator-blockers.md)
· [Source and owner gaps](verification/current-source-owner-blockers.md)
· [Derived claim/source index](verification/current-host-authority-index.md)

This correction is local. No new Host/API/SSH work, rental, human acceptance,
commit, push, merge or Jira post is included. The separate external workstreams
remain open; this is not full Host readiness.

## Dated predecessor — clarification sweep, 10 September 2026

The following describes the earlier same-day state, not the current counts.

The clarification sweep accounts for all **44 primary Host pages and 2,013
claims**. It makes **701 claim-method-only corrections**, including **58 pure
advice** records, and corrects next actions for **651 unresolved or STALE
procedure nodes**. Claim statuses remain **227 PASS / 47 FAIL / 23 BLOCKED / 13
N/A / 1,703 UNVALIDATED**. Existing authority and source bases are preserved.

This is not a new truth re-adjudication of every statement: the 29 scoped
runtime exceptions were screened, while the remaining 978-claim runtime cohort
retains its current method. It creates no product proof, acknowledgement,
acceptance, Host/API/SSH/paid action, or status change. The separate
[runtime/operator](verification/current-runtime-operator-blockers.md) and
[source/owner](verification/current-source-owner-blockers.md) registers remain
current. The [clarification-sweep result](verification/evidence/2026-09-10-host-clarification-sweep-attempt-01/result.md)
records the bounded handoff. Final checks passed: 224 Python tests, 160
JavaScript tests, all 44 localhost pages and 15 offline HTML check groups.
These verify repository integrity and reviewer behavior, not product truth.

Five workload instructions now lead with **Needs policy acknowledgement**.
Use existing approved policy first; ask the responsible owner to confirm or
correct only what is missing or unclear, then cite the source or decision.
No rental test is needed to establish a rule. The Fleet Operations policy link
does not require a new approval. The basic marketplace introduction already has
official-publication support and needs no test rental. These are review requests,
not recorded acknowledgements; claim statuses and missing citations are unchanged.
See the [policy-review presentation result](verification/evidence/2026-09-10-host-policy-acknowledgement-attempt-01/result.md).

The local reviewer and standalone HTML now use shorter explanations of what
is missing and what to check next. Repeated passage summaries and empty proof
messages are removed. Exact source links, limits and recorded details remain
available. This is a presentation change, not new evidence or a status change.
See the [plain-language review result](verification/evidence/2026-09-09-host-review-plain-language-attempt-01/result.md).

The complete authority-first scan covers **44 Host pages and 2,013 statements**:
**227 PASS / 47 FAIL / 23 BLOCKED / 13 N/A / 1,703 UNVALIDATED**.
The 18 CLI and 15 SDK wrappers remain reference-support layers, not additional
Host workflows. The localhost reviewer and shared HTML present the current
passage, its proof and limitations, and any remaining action—not superseded
findings or correction history.

Existing canonical CLI declarations and applicable agreement/publication
sections are used first. Agreement clauses support matching obligations; they
do not prove runtime compliance or uncovered rental guarantees. Owner
clarification is reserved for actual gaps, ambiguity or conflicting sources.
Thirty additional statements have independently reviewed, source-only support;
no new runtime PASS is claimed. Circularity checks reject documentation,
registries, the current review model and Graphify as terminal product proof.

[Clarification-sweep handoff](verification/evidence/2026-09-10-host-clarification-sweep-attempt-01/result.md)
· [Prior authority-first result and checks](verification/evidence/2026-09-09-host-authority-scan-attempt-01/result.md)
· [Shareable review](verification/host-docs-review.html)
· [Runtime/operator work](verification/current-runtime-operator-blockers.md)
· [Source and owner gaps](verification/current-source-owner-blockers.md)
· [Derived claim/source index](verification/current-host-authority-index.md)

This correction remains local: no new Host/API/SSH operation, rental, commit,
push, merge, Jira post or human acceptance. It does not establish full Host
readiness.

## Internal dated audit context

The entries below retain earlier snapshots and are not the current finding.
Use the current review links above for manager and customer-document review.

Source-authority correction — **2026-09-09** (local, not published):
Four Hosting Overview offer controls now use implementation evidence rather than
blanket policy classification. Pinned Vast CLI source and retained listing
request/readback support the exposed settings, not server enforcement or contract
guarantees. Five narrowed statements and one new bounded security statement cite
the exact applicable section of the public Hosting Agreement. The agreement is
authority for those obligations, not proof of compliance or all product behavior.

Current inventory: **2,013 claims — 204 PASS / 151 FAIL / 23 BLOCKED / 4 N/A /
1,631 UNVALIDATED**. The citation count increases from149 to151 because four
findings close while six unsupported residual clauses are separately retained;
three partially cited statements remain FAIL. All2,005 predecessor IDs remain,
with1,993 untouched proof/status records. The old112procedure records remain
auditable; eight changed-source carriers are STALE, and four new source-only
section reviews add25nodes. These are not new executed Host workflows.

See the [exact source correction and retest result](verification/evidence/2026-09-09-host-authority-correction-attempt-01/result.md),
[source guide](verification/evidence/2026-09-09-host-authority-correction-attempt-01/source-guide.md),
and [updated HTML review](verification/host-docs-review.html).
The [runtime/operator register](verification/current-runtime-operator-blockers.md)
and [source-owner/citation register](verification/current-source-owner-blockers.md)
remain separate and open. All2,247 prior evidence artifacts are byte-identical.
Git index metadata bytes changed, but every staged path, mode and object ID and
the staged diff match the initial clean state; no index restoration was performed.
No new Host/API/SSH, paid operation, commit, push, merge, Jira post or human
acceptance is included. Earlier publication and operational notes below are dated
history, not a claim that this local correction has reached the PR.

Publication handoff — **2026-09-09**: the user authorizes committing and pushing
the completed Host Docs progress to the existing PR branch, without merging.
Start with the [short progress and next-actions guide](verification/HOST-DOCS-PROGRESS.md).
The [publication plan and checks](verification/evidence/2026-09-09-host-progress-publication-attempt-01/plan.md)
keep the 149 citation defects and runtime prerequisites open. Publication does
not rewrite the sealed operational results or record human acceptance.

Approved live follow-up — **2026-09-09**:
Machine 150296 was idle immediately before the single one-GPU test rental.
**SSH passed** with actual output. Jupyter returned authenticated HTTPS status
and page responses with a process-scoped official CA, but **browser completion
is blocked by missing certificate trust**. No global trust change or warning
bypass was performed. Instance 50386523 was destroyed within about 8m22s;
independent absence, zero remaining host jobs/containers and unchanged boot
confirm cleanup and no reboot. The roughly $0.40 immediate account-wide credit
delta is not a settled instance bill.

Normal self-test stopped before creation: reliability **85.1%** is below the
required **>90%**, and advertised upload **221.1 Mb/s** is below **500 Mb/s**.
The actual failure support bundle was retained privately with a sanitized
inventory. This proves the preflight/failure-bundle path, not a completed
diagnostic. No requirements bypass or paid self-test was performed.

See [actual observations and their limits](verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/operations-result-01.md),
[runtime/operator next actions](verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/runtime-operator-register.md),
and [separate source-owner/citation work](verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/source-owner-register.md).
All 2,027 prior evidence artifacts and the pre-existing staged diff are unchanged.
The 149 required-citation FAILs remain open. Six exact-claim bindings now identify
the actual page passage, source and retained observation. Two atomic statements
newly PASS; totals are **194 PASS / 149 FAIL / 23 BLOCKED / 4 N/A / 1,635
UNVALIDATED**. All 1,999 other claim records and every procedure/support layer
are unchanged. Three connection taxonomies were explicitly corrected while
retaining their complete prior records. The extra BLOCKED row names the browser
certificate prerequisite, not a product failure.

The port4000 and offline checks cover six updated cards, 24 contextual proof
links, all 44 API contexts and the 149-citation filter. All 88 passage controls
on the two affected pages were checked separately. See the
[bounded result, exact final retests and integrity gate](verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/result.md)
and [shareable report](verification/host-docs-review.html). The result distinguishes
current validation from earlier dated suites; it does not imply a new all-page
visual audit, full-site accessibility PASS or external acceptance.
No commit, push, merge, Jira post or human acceptance occurred in this follow-up.
Earlier dated snapshots below remain historical, including their then-current
“awaiting approval” statements and totals.

Repository-first follow-up — **2026-09-09, 11:56 UTC**:
The scoped no-cost fixes are complete: internal review records stay out of the
customer build; private archives, dependencies and caches stay out of Git;
generated API links are checked against Mint's actual generator and rendered
routes; and the dark-background link color now meets 4.5:1 contrast. The offline
report distinguishes the latest sealed claim result from historical attempts
and embeds the new link/accessibility reconciliation without changing a verdict.

Current checks: **183 Python tests, 94 JavaScript tests, 85 unique generated API
targets (99 static findings), all 44 current reviewer contexts**, and retained
exact-passage browser checks pass. The original link and contrast failures remain
linked to their retests. The separate **74 missing-alt findings in 19 non-Host
files remain open**; this is not a blanket repository accessibility PASS.
All **1,941 pre-existing evidence artifacts**, the staged diff, the exact claim
model and all 149 citation FAILs remain unchanged. The AST-only navigation graph
was safely refreshed after rejecting a shrinking candidate; it is not proof.

See the [repository-first result](verification/evidence/2026-09-09-host-repository-live-merge-attempt-01/result.md),
[runtime/operator prerequisites](verification/evidence/2026-09-09-host-repository-live-merge-attempt-01/runtime-operator-register.md),
and [source-owner and review gates](verification/evidence/2026-09-09-host-repository-live-merge-attempt-01/source-owner-register.md).
No new Host/API/SSH, Keychain access, rental, reboot, commit, push, merge or human
acceptance occurred. New SSH/Jupyter/self-test execution awaits bounded spend
approval and fresh safety checks. PR185 remains draft and requires review; its
green remote CI covers bfa926c, not these local changes.

Current bounded documentation/citation-review correction — **2026-09-09**:
The two non-citation documentation defects are corrected: **First 24 Hours /
Test Like A Client** now uses renter offer search, and **VMs / Check VM Status**
includes the unreadable-configuration case for `off`. The original two FAIL
occurrences and their evidence are preserved in the
[exact source transition](verification/current-two-defect-transition.json).
The replacement statements remain **UNVALIDATED**: local CLI parsing is not
live offer visibility, and an installed VM helper is not upstream VM authority.

Current totals: **192 PASS, 149 FAIL, 22 BLOCKED, 4 N/A, 1,638 UNVALIDATED**
across 2,005 claim occurrences. The 149 FAIL records are the unchanged required-
citation defects across 24 pages; they are not failed runtime tests. In the
localhost:4000 sidebar select **Missing authoritative citation** to see the
wording, heading, **Show on page**, missing source, responsible role and next
action. The shareable [HTML report](verification/host-docs-review.html) has the
same citation filter and retains the two original failures as historical context.

All 2,003 unaffected claim records retain their proof/status bindings; the only
permitted change on the two edited pages is the explicit source-transition
history/coverage metadata. The three earlier rental PASSs and one partial
UNVALIDATED claim remain unchanged. The 107, 35 and 63 artifacts in the three
prior sealed attempts are byte-identical, and the pre-existing staged diff is
unchanged. No new SSH, Host/API, rental, reboot, publication or human acceptance
was performed. See the [bounded result and retests](verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/result.md),
[runtime/operator work](verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/runtime-operator-register.md),
and [citation/source-owner work](verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/source-owner-register.md).
Those external workstreams are still open.

Historical listing and client-rental follow-up — **2026-09-09, 08:56 UTC**:
Machine **150296** is listed at the user-approved **USD 0.01/GB upload and
download**. The earlier USD 1/GB and new USD 0.10/GB API rejections remain
historical failures. [Independent final Host readback](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/host-read-09.json)
matches USD 3/GPU-hour, USD 0.30/GPU-hour minimum bid, USD 0.50/GB-month storage,
disabled prepaid discounts and the unchanged fixed expiry (September 15 at
00:00 South Africa time).

A distinct client account created **50364501**, ran one small H100 CUDA check
(sum of squares **1240**), and destroyed it. [GPU output](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/gpu-result-01.json)
and [independent cleanup/absence](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/cleanup-main.json)
are retained. The host remains publicly listed; final point-in-time readback
shows zero running/resident rentals. Later customer arrival is possible.

On **First 24 Hours**, machine/offer visibility, creation, and client-account
visibility are now separately PASS. The combined destroy/SSH/Jupyter passage
remains **UNVALIDATED**: cleanup is proved, its troubleshooting clause is not.
[Exact claim delta](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/claim-impact-02.json):
three statuses changed, one partial-proof binding added, and 2,001 other claims
are unchanged. Then-current totals: **192 PASS, 151 FAIL, 22 BLOCKED, 4 N/A,
1,636 UNVALIDATED**. API/args-mode execution does not establish the CLI/Jupyter
command, full self-test, stock installer, reboot persistence or final billing.
The immediate account-wide credit delta is not a settled instance bill.

See the [bounded result and reviewer retests](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/result.md),
[runtime/operator register](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/runtime-operator-register.md),
and [source-owner register](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/source-owner-register.md).
No push, merge, Jira post or human acceptance is recorded by this follow-up.

Historical listing follow-up — **2026-09-09, 05:27 UTC**:
The user confirmed USD 1/GB upload/download and disabled prepaid discounts.
The exact [listing request](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-request-01.json)
was attempted for machine **150296**. The API returned
[400 price_out_of_bounds](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-response-01.json).
An [independent readback](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/listing-readback-verification-01.json)
confirms the machine remains **unlisted**. No client rental was created and no
lower-price fallback was attempted. The server-reported bound is not established
as a permissible host-input rate; revised API-valid prices need user approval.
Earlier installation observations and all 2,005 claim statuses are unchanged.
The reviewer and shareable HTML now link these three current findings to the
existing exact installation passages, without presenting them as rental proof.
See the [bounded result and retests](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/result.md),
[runtime/operator register](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/runtime-operator-register.md),
and [source-owner register](verification/evidence/2026-09-09-h100x4-listing-rental-attempt-01/source-owner-register.md).

Completed direct-install retest — **2026-09-09 South Africa (September 8 UTC)**:
[exact installation observations](verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/operations-summary.md).
The sudo blocker is resolved and the approved modified direct installer completed.
NVML/NCCL success markers, all four active services, all four visible H100 GPUs,
XFS/project-quota enforcement and unchanged boot were retained independently.
The owned-machine API returned the new machine **150296**, unlisted. The later
[settled snapshot](verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/settled-01.json)
shows no Docker containers or GPU compute PIDs, all four services enabled/active,
and an empty package audit. Earlier helper package-lock failures are preserved;
this is not a claim that every installer subcommand succeeded. No stock TUI,
reboot, paid rental or separate marketplace self-test is proved. At that attempt's
handoff, listing awaited the bandwidth-price/prepaid-discount choice (superseded
by the listing follow-up above); exact runtime claim binding and
reviewer regression are completed for this bounded attempt. See the
[final handoff](verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/result.md).
Four exact runtime-only claims now have selected command-output proof; the other
2,001 claims are unchanged. Then-current totals were **189 PASS, 151 FAIL, 22 BLOCKED,
4 N/A and 1,639 UNVALIDATED**. The 158-test Python retest and 72-test reviewer
retest pass. All 101 affected-page passage/status controls, 69 contextual links
and four selected runtime outputs pass in the live reviewer and offline report.
The HTML embeds 152 files with zero network resource requests. Original failures
and retests remain linked. The optional knowledge-graph refresh refused a
smaller replacement and remains local maintenance; no force overwrite occurred.

Historical direct-install attempt — **2026-09-08, 21:55 UTC**:
[exact preflight and dispositions](verification/evidence/2026-09-08-h100x4-direct-install-attempt-01/result.md).
The user supplied a replacement setup token and approved the direct route.
SSH, four H100 GPUs, unchanged boot and persistent XFS/quota mount were observed;
**sudo requires a password**, so installation stopped before invocation. No
setup token, API, registration, listing, rental or reboot was used/performed.
The [operator register](verification/evidence/2026-09-08-h100x4-direct-install-attempt-01/runtime-operator-register.md)
names the missing sudo authentication and exact next action. The
[source-owner register](verification/evidence/2026-09-08-h100x4-direct-install-attempt-01/source-owner-register.md)
keeps external authority separate. Prior selected observations and canonical
claim statuses are preserved. Reviewer integration/retests are recorded in the
attempt result, not inferred from this summary.

Direct-attempt reviewer retest: all 101 two-page passage/status controls and
34 contextual links pass; offline HTML embeds 144 files with no network resources.
The initial suite passed 69/70; its HTML-export ordering failure is retained,
and all 14 HTML tests passed on the post-export retest. Source/model identities
are unchanged across that correction. No single green 70-test run is claimed.

Historical local installer preparation — **2026-09-08**:
[exact-page source and preparation findings](verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/source-review-summary.json).
A digest-pinned local variant omits only the inspected automatic listing/self-test
helper launch; nine local tests pass. It has not been installed or listed. A new
read-only capture adds the persistent XFS/quota mount entry to the earlier GPU and
mount observations. The reviewed TUI expects the omitted self-test and would
report failure; this is not proof of a successful stock TUI or standard install.
The [runtime/operator register](verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/runtime-operator-register.md)
names the fresh setup credential and remaining execution requirements. The
[source-owner/commercial register](verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/source-owner-register.md)
keeps provenance and owner work separate. Prior attempts and all canonical claim
statuses are preserved. See the [bounded attempt result](verification/evidence/2026-09-08-h100x4-safe-installer-attempt-01/result.md)
for final reviewer checks and limits.

Preparation handoff retest: 69 regression tests, 101 rendered passage/status
controls and 29 contextual evidence links pass; the HTML embeds 143 files and
works offline. The first proxy-startup connection failures are retained beside
the successful ready-server retests. This closes only the preparation/interface
package, not installation or unresolved Host Docs claims.

Historical installation evidence intake — **2026-09-08**:
[new H100×4 and three existing-host review](verification/evidence/2026-09-08-h100x4-install-history-attempt-01/result.md).
Four strictly pinned read-only SSH captures completed; no host was rebooted or
changed. The new host exposes four GPUs and XFS/project-quota mount options, but
Docker and Vast are not installed. Historical installation records remain useful
for bounded invocation/postcondition evidence; no missing terminal installer exit
was reconstructed.

The [public helper inspection](verification/evidence/2026-09-08-h100x4-install-history-attempt-01/source-inspection-02.md)
confirms temporary listing before automatic self-test. Its generated GPU-price
argument and omitted bid/storage controls do not enforce the newly approved
$3/GPU-hour, $0.30 minimum bid per GPU-hour and $0.50/GB-month terms. Its three-hour
expiry is within the seven-day ceiling, not itself a violation. Installation/listing
is paused for a safe initial-publication route and a fresh securely supplied setup
key. This is supplemental evidence, not installation proof or a claim-status change.
The result links exact client-facing headings and separates runtime/operator work
from source-owner and commercial-authority work. No installation, listing, rental,
reboot, Host/API/setup credential use or acceptance is recorded by this intake.
The approved SSH identity was used for the bounded read-only captures.

[Reviewer and shareable HTML integration retest](verification/evidence/2026-09-08-h100x4-install-history-attempt-01/reviewer-result.md):
five exact installation-page findings, 69 passing regression tests, 101 matching
passage/status controls and nine working evidence links. Partial findings are
explicitly distinguished from complete proof; current claim statuses are unchanged.
Original fixture/export failures and the proxy-startup browser failure remain
linked to passing retests. Port4000 serves the final source; the offline report
works without network resources. This does not resolve the earlier intermittent
fetch issue or any outstanding product/owner work.

Previous additive V&V update: **2026-09-08**, [client/Host unblocking result](verification/evidence/2026-09-08-host-client-unblocking-attempt-01/result.md)
and [shareable HTML](verification/host-docs-review.html). Then-current totals: **185 bounded
PASS, 4 editorial N/A, 151 FAIL, 22 BLOCKED and 1,643 UNVALIDATED** (1,816 unresolved).
The [exact delta](verification/evidence/2026-09-08-host-client-unblocking-attempt-01/current-delta-01.json)
contains ten newly supported command occurrences, two confirmed documentation
defects and two refreshed self-test prerequisites. These are not completed
workflows. The 18 new observations/inspections are separate from the prior 47.

Both Host/client keys authenticate and resolve to distinct accounts. Missing-key
wording is no longer a current execution gate. Self-test still needs explicit
workload authority, the necessary create permissions, a controlled runtime window
and cleanup scope. VM `off` was inconclusive with unreadable configuration; the
unconditional description and First 24 Hours' Host-inventory command in a client
discovery sequence are now FAIL with exact retained findings. The isolated
key-file mode-0644 security failure remains open.

[Current runtime/operator prerequisites](verification/evidence/2026-09-08-host-client-unblocking-attempt-01/runtime-operator-register.md)
and [current Product/Finance/Legal/source-owner work](verification/evidence/2026-09-08-host-client-unblocking-attempt-01/source-owner-register.md)
remain separate. The latter explicitly identifies the two remaining repository-local
wording corrections; not all unresolved work is an external blocker. Current
adjudications preserve full prior claim objects. All other claims, procedure and
support-layer states, page text, the staged diff and retained historical artifacts
are unchanged. No rental/self-test, Host mutation, instance stop/destruction,
push, merge, Jira/PR post or human acceptance occurred in this follow-up.

Final retests: 142 Python tests, 29 current-review/HTML tests and 11 offline browser
check groups pass. All 44 pages have retained passage/status observations, but one
intermittent localhost fetch failure remains unexplained despite three successful
sequential Self-Test retries; it is not relabeled as a stability PASS.

Reviewer panel follow-up: the [port4000 findings retest](verification/evidence/2026-09-08-reviewer-findings-refresh-attempt-01/result.md)
confirms the running reviewer serves these current findings. Four representative
pages passed exact passage/status checks for 145 claims; eight retained proof
links from four selected findings returned HTTP200. This is interface verification,
not new product proof or closure of the earlier intermittent transport issue.
Final handoff must refresh and retest both the localhost panel and shareable HTML
after any further evidence/content change.

Previous additive result: **2026-09-08**, [47-check live read-only result](verification/evidence/2026-09-08-host-live-readonly-attempt-01/result.md).
Its totals were 175 bounded
PASS, 4 editorial N/A, 149 FAIL, 22 BLOCKED and 1,655 UNVALIDATED (1,826 unresolved).
Three Market Metrics endpoint descriptions have canonical-source plus API proof;
the Hosting Overview marketplace introduction has separate official product-source
proof, not a paid rental or renter-workload result. All 15 documented Market Metrics
CLI examples ran; the [20-occurrence map](verification/evidence/2026-09-08-host-live-readonly-attempt-01/check-to-claim-map.json)
distinguishes full invocations, partial procedures and related context. Forty-seven
checks does not mean forty-seven claims closed.

[Runtime/operator prerequisites](verification/evidence/2026-09-08-host-live-readonly-attempt-01/runtime-operator-register.md)
and [Product/Finance/Legal/source-owner work](verification/evidence/2026-09-08-host-live-readonly-attempt-01/source-owner-register.md)
remain separate. No paid/privileged/workload-affecting operation, push, Jira post,
merge or human acceptance is recorded. Prior attempts and the original static
evidence bytes are preserved; the figures below describe the previous dated pass.

Client-facing claim review baseline (2026-09-07): start with the repository files
`verification/HOST-DOCS-CLAIMS-TO-RESOLVE.md` and
`verification/HOST-DOCS-CURRENT-REVIEW-PLAN.md`.
The dated evidence below remains historical; it must not be read as proof of
changed or newly merged wording. Repository review does not complete the
runtime/operator or Product/Finance/Legal/source-owner workstreams.

Previous repository-only V&V result: `verification/evidence/2026-09-07-host-current-vv-attempt-01/result.md`.
The additive current package covers 44 primary pages and 33 support layers.
It recorded 2,005 statement occurrences: 171 bounded PASS, 4 editorial
NOT_APPLICABLE, 149 FAIL, 22 BLOCKED and 1,659 UNVALIDATED. The 1,830 unresolved
occurrences are listed in `verification/current-host-docs-claim-worklist.md`;
runtime/operator and source-owner registers are separate. These are not 1,830
confirmed external blockers or 2,005 newly completed semantic reviews.
All 44 reviewer pages and 33 support layers passed their final browser checks;
19 masked examples use explicit section-link fallbacks instead of exact highlights.
Historical attempts, intermediate failures and correction retests are retained.
New/changed-page heading checks are inventory, not completed branch-level runtime
validation. Global non-Host link/alt-text and shared contrast findings remain open.

Jira epics: [CON-1187](https://vastai.atlassian.net/browse/CON-1187) and [CON-1509](https://vastai.atlassian.net/browse/CON-1509)

## Purpose

This review-only audit maps the Host documentation in PR #185 to the 16 child
tickets assigned to Hannes. It distinguishes work that is implemented from
facts, policy decisions, and sign-offs that still need an owner.

This document does not reproduce internal support source material, customer
data, credentials, or machine-local research paths. It records only the
traceability needed to review the PR.

## Ticket matrix

| Jira | Current state | Evidence in or linked from PR #185 | Review verdict |
|---|---|---|---|
| [CON-1584](https://vastai.atlassian.net/browse/CON-1584) | BLOCKED | Host Account Security and Host CLI/API/SDK orientation, with links to canonical account and developer docs | Partial: Teams ownership, setup-key wording, screenshot/redaction, and review-stack decisions remain |
| [CON-1581](https://vastai.atlassian.net/browse/CON-1581) | BLOCKED | `/host/host-teams` covers context, ownership, roles, keys, CLI use, earnings, payouts, and recovery | Partial: migration semantics, the `undefined` install failure, registration permissions, and `billing_read` behavior need engineering answers |
| [CON-1531](https://vastai.atlassian.net/browse/CON-1531) | BLOCKED | `/host/machine-errors` provides a broad lookup, impact, remediation, and public/admin distinctions | Partial: catalog completeness, field/UI mapping, clearing/TTL rules, and public-error policy need backend answers |
| [CON-1518](https://vastai.atlassian.net/browse/CON-1518) | TO REVIEW | Lifecycle IA, overview split, persona chips, installer assets, and persona consistency check | Substantially documented; IA/persona and stakeholder sign-off remain |
| [CON-1517](https://vastai.atlassian.net/browse/CON-1517) | TO REVIEW | Source review and a human-reviewed answer pass were completed; PR commit `0cb28ff` distributes the answers across 33 canonical Host pages | Implemented in PR #185; shared product confirmations remain under their topic-specific tickets |
| [CON-1515](https://vastai.atlassian.net/browse/CON-1515) | TO REVIEW | Generated `/host/self-test-reference`, source-derived thresholds, runtime stages, image matrix, stable codes, bundle guidance, generator, and CI workflow | Implemented in PR #185; authoritative verification queue/wait-time wording still needs confirmation |
| [CON-1256](https://vastai.atlassian.net/browse/CON-1256) | TO REVIEW | Pricing, earnings, market metrics, optimization, payment, datacenter, tax, and persona guidance | Partial: Solutions Engineering/business review and content ownership remain |
| [CON-1077](https://vastai.atlassian.net/browse/CON-1077) | TO REVIEW | `/host/headless-install` provides an SSH-only setup path from first login through listing and Self-Test | Implemented in docs; reviewer sign-off remains |
| [CON-1583](https://vastai.atlassian.net/browse/CON-1583) | TO REVIEW | [self-test#3](https://github.com/vast-ai/self-test/pull/3) is merged; the generated reference documents the approximately 2 TB high-VRAM cap and B300 behavior | Implemented in runtime and PR #185; reviewer sign-off remains |
| [CON-1519](https://vastai.atlassian.net/browse/CON-1519) | TO REVIEW | [vast-cli#410](https://github.com/vast-ai/vast-cli/pull/410) is merged; Host Diagnostics and the generated reference document automatic bundles, `dump-logs`, redaction, caps, and opt-in host-local artifacts | Command and docs are implemented; operations ownership and safe transfer/retention policy remain |
| [CON-1514](https://vastai.atlassian.net/browse/CON-1514) | TO REVIEW | [vast-cli#409](https://github.com/vast-ai/vast-cli/pull/409) is merged; docs cover common causes, port requirements, TCP/UDP guidance, and offline/unlisted/rented possibilities | Partial: exact failed-port/protocol evidence and authoritative offline-vs-hidden state require backend/API support |
| [CON-1513](https://vastai.atlassian.net/browse/CON-1513) | TO REVIEW | Generator plus scheduled, PR, manual, and optional dispatch drift checks; the PR check passes against both source repositories | Implemented and active in PR #185 |
| [CON-1512](https://vastai.atlassian.net/browse/CON-1512) | QA Passed | [vast-cli#407](https://github.com/vast-ai/vast-cli/pull/407) is merged; docs warn that `--ignore-requirements` does not qualify a machine for verification | Implemented |
| [CON-1510](https://vastai.atlassian.net/browse/CON-1510) | TESTING | [vast-cli#408](https://github.com/vast-ai/vast-cli/pull/408) and [self-test#2](https://github.com/vast-ai/self-test/pull/2) are merged; the generated page exposes actual/required values, purpose, remediation, stable codes, and source metadata | Implemented in runtime and PR #185; Jira testing/sign-off remains |
| [CON-1502](https://vastai.atlassian.net/browse/CON-1502) | QA Passed | [self-test#4](https://github.com/vast-ai/self-test/pull/4) is merged; the generated reference exposes the validated image/platform matrix | Implemented |
| [CON-1419](https://vastai.atlassian.net/browse/CON-1419) | TO REVIEW | [vast-cli#408](https://github.com/vast-ai/vast-cli/pull/408) selects CUDA 11.8 for pre-Volta and caps Volta at CUDA 12.8; the generated page documents the rules | Implemented in runtime and PR #185; reviewer sign-off remains |

## Implemented review corrections

- PR #185 contains the generated Self-Test reference and its source generator;
  docs PR [#145](https://github.com/vast-ai/docs/pull/145) is superseded and is
  being closed rather than treated as an integration dependency.
- The `verify-self-test-reference` check passes against Vast CLI and the private
  Self-Test source repository.
- The review panel links each page to its relevant epics, tickets, named owner
  questions, and remaining blocker count.
- The Self-Test page now has one remaining product-fact gate: authoritative
  verification queue and wait-time wording. Generated thresholds, failure
  codes, dispatch checking, B300 guidance, and older-GPU selection are present.
- Host Diagnostics documents the merged `vastai dump-logs` workflow. Remaining
  questions concern operations ownership, artifact policy, and evidence that
  only backend or host-side systems can provide.

## CON-1519: what exists and what the meeting must decide

### Implemented mechanics

- A failed `vastai self-test machine <machine_id>` creates a redacted diagnostic
  archive automatically unless support bundles are explicitly disabled.
- `vastai dump-logs <machine_id>` creates one on demand. The caller can provide
  an instance ID for API-visible instance logs and can choose the output
  directory.
- The archive is created on the machine where the CLI runs. The default
  directory is `/tmp`; nothing uploads it to Vast, Jira, or object storage.
- The archive is named `vast_selftest_<machine>_<UTC timestamp>.tar.gz` and is
  written with `0600` permissions.
- Every archive records a manifest and collection errors. Self-Test output,
  structured result data, and API-visible instance status/container/daemon
  evidence are included when available.
- Non-JSON text/log artifacts are tail-bounded; collection commands have a
  timeout; sensitive key names and explicit secrets are redacted. The user is
  told to review the archive before sharing it.
- Host-local Kaalia, Docker, kernel, NVIDIA, network, and mount evidence is
  opt-in with `--include-local-host-artifacts` and is useful only when the CLI
  is running on the actual host. A laptop cannot collect the host's local OS
  state remotely.

### Ownership decisions still required

| Decision | Question to answer in the meeting | Proposed starting point, not yet approved |
|---|---|---|
| Intake | Where should a host send a reviewed archive? | A restricted support-ticket attachment or approved private upload, never a public Jira/Slack channel |
| Accountable owner | Who owns the bundle after it is received? | Support Operations owns intake and case tracking |
| First triage | Who confirms scope, redaction, completeness, and failure category? | Support L1 uses a checklist and routes by evidence type |
| Diagnosis | Who diagnoses CLI, backend/daemon, and host-local failures? | CLI maintainers own schema/collection bugs; Backend/Daemon owns API/instance evidence; Host Engineering/SRE owns host-local runtime evidence |
| Retention and access | How long is the archive kept, who can access it, and who deletes it? | Security/Support Operations must approve a retention period and least-privilege access group |
| Escalation | What evidence and response are required when L1 cannot resolve it? | A routing matrix with named queues and a feedback path for new error codes/remediation |

The implementation cannot settle this RACI by itself. To close CON-1519
operationally, the meeting should name one accountable intake owner, approve a
transfer location and retention/access policy, and name the first diagnostic
owner for each evidence class.

## Remaining decisions by review area

- **Host Teams / account setup:** migration and earnings behavior, installation
  key semantics, registration permissions, and billing-role behavior.
- **Machine errors / network:** complete public catalog, UI fields, clearing
  behavior, exact failed-port/protocol evidence, and offline-versus-hidden state.
- **Self-Test:** verification queue and wait-time wording; CON-1519 operations
  ownership and safe artifact policy.
- **Business pages:** Solutions Engineering/business review and named content
  owner.
- **Review mechanics:** approve lifecycle IA/persona treatment and the remaining
  product assets, then choose the merge/review sequence for PR #185.

## Validation evidence

### Review wording directly on the page (2026-09-05)

The local review panel now opens with **Wording & proof**. Select a section,
read the customer-visible statement, and use **Show on page** to highlight
its exact wording. Opening a section URL selects that section's statements;
**All sections** shows the full page inventory. The review IDs and complete
evidence history remain under **Audit details** and **Technical V&V details
and history**.

For example, `MCL-f9f3ebb712a5588d` is the opening statement on Verification
Stages: “Verification is automated. There is no manual review step for
ordinary host verification.” It belongs to **Page introduction**, not to
Verification Requirements. Its **Needs evidence** label means the existing
`UNVALIDATED` status: the Self-Test and Verification source owner still needs
to supply the canonical implementation supporting that statement.

Cards distinguish proof from links in the wording and review tracking records.
Source definitions for commands are labeled as syntax support; command test
results keep their separate status. A successful highlight proves only that
the reviewer can locate the wording. Ambiguous, missing, and masked passages
show an explicit fallback instead of choosing a passage silently. Combined
passages now highlight each bound excerpt, as verified in the follow-up below. Customer
pages served without the local review proxy are unchanged.

The correction, observed failures, retests, and limits are retained in the
[reader presentation attempt](https://github.com/vast-ai/docs/blob/7d42a0d439f91e4dc2877104db807ec6fb975ce4/verification/evidence/2026-09-05-host-reviewer-reading-attempt-01/result.md).

### All Host pages: readable wording and proof (2026-09-05 follow-up)

The same view covers all **40 primary Host pages**, including Volume Offers and
the generated Self-Test Reference. The **18 CLI and 15 SDK wrappers** instead
show a readable link to the central reference, with the explicit limitation
that a reference check is not command-execution proof.

Cards quote the bound page passages, separately label a summarized assertion,
and link every declared section. Multi-section filters, multi-passage highlights,
literal shell pipelines, repeated source occurrences, and rendered prose
typography are covered. Audit IDs and historical records remain collapsed.

The final browser sweep accounted for all **1,687 statements**: **1,680 located**
and **7 explicitly masked section fallbacks**. All section filters and review
section links passed; all existing claim statuses were preserved. The 33 support
routes and 33 review-context regression tests passed. These are interface results,
not new validation of the Host claims or commands. The runner rejects stale
servers using the source identity returned by the running process.

The panel also exposes inherited issues rather than hiding them: `VOL-C35`'s
binding covers Related Pages but omits Command Map; two unbackticked Self-Test
options render with typographic dashes. Those canonical documentation/binding
repairs remain maintainer follow-ups. Masked passages are not presented as exact
quotations. Source-span navigation may omit table scaffolding; it is not proof
of a whole claim's scope or rendered CLI-token correctness.

[All-page results, original failures, corrections, retests, screenshots and limits](https://github.com/vast-ai/docs/blob/7d42a0d439f91e4dc2877104db807ec6fb975ce4/verification/evidence/2026-09-05-host-reviewer-all-pages-attempt-01/result.md)
are retained separately from the earlier single-page attempt. Neither the
runtime/operator nor Product/Finance/Legal/source-owner workstream is completed
by this presentation change; no human acceptance is recorded.

### How command proof is presented

#### Upstream integration freshness (2026-09-07)

PR #153's head is already an ancestor of PR #185; it is not a separate merge
dependency. The number **153 citation failures** elsewhere in this report is
a count of findings, not a pull-request reference.

The upstream integration adds Machine Metrics, Machine Offline, Upgrade the
Kernel, and Disable SSH Password Login to the Host lifecycle navigation. It
also changes existing source text and central references. The September 5
evidence applies to its exact tested commit, `7d42a0d`, not automatically to
these additions or changes. A changed page is **STALE** until its wording,
source bindings, procedures, and proof are re-reviewed; a new page is
**UNVALIDATED** until inventoried and checked. Neither label implies a confirmed
external blocker. Old failures and runtime/owner limitations remain visible as
history and must not be promoted by the merge.

The integration plan, initial failures, corrections, and retests are retained
in `verification/evidence/2026-09-07-host-main-integration-attempt-01/result.md`.
The current static inventory covers 44 primary pages and 33 support routes.
Reviewer source coverage is 36 unchanged primary pages, four changed pages,
four new pages, and six changed support routes. "Unchanged" preserves the
previous bounded status; it does not mean PASS. Renewing the changed/new
claim and procedure contracts remains repository work, not an external blocker.

#### Retained command evidence

The review panel now keeps two evidence lanes separate for every exact command:

- **Source/signature support** links to the immutable Vast CLI handler and to
  the repository-local argparse check. This proves only that the documented
  executable, command signature, and options exist in the pinned source. It
  does not prove execution.
- **Runtime behavior** links to the retained command attempt, identifies its
  proof role and limitations, and states the concrete next action when the
  result is incomplete.

Status-reconciliation records are shown as accounting only, not as command
proof. Every retained-evidence link carries its exact page, heading, target or
command, current status, proof role, and limitations into the evidence view.

Current examples reviewers can use:

| Page and command | Source/signature | Runtime result | Meaning |
|---|---|---|---|
| [How to Self-Test — Before You Run It](/host/how-to-self-test#before-you-run-it) — `vastai set api-key <API_KEY>` | PASS at pinned [`set__api_key` source](https://github.com/vast-ai/vast-cli/blob/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd/vastai/cli/commands/auth.py#L199-L204) | FAIL — [retained isolated result](https://github.com/vast-ai/docs/pull/185/files#diff-4f5c08df9a17c2408167b8eeb03e88105ebed7f9651672660450a59648f95d27) | The synthetic value was written, but the file was mode `0644`; this is not proof of real Host authentication. |
| [How to Self-Test — Run The Test](/host/how-to-self-test#run-the-test) — `vastai self-test machine <machine_id>` | PASS at pinned [`self_test__machine` source](https://github.com/vast-ai/vast-cli/blob/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd/vastai/cli/commands/machines.py#L699-L717) | UNVALIDATED — no direct retained runtime result | The command exists; successful rental, workload, result, and cleanup behavior are not proved. |
| [How to Self-Test — Run The Test](/host/how-to-self-test#run-the-test) — `--support-bundle-dir /path/to/output` variant | PASS at pinned [`self_test__machine` source](https://github.com/vast-ai/vast-cli/blob/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd/vastai/cli/commands/machines.py#L699-L717) | BLOCKED/PARTIAL — [retained attempt](https://github.com/vast-ai/docs/pull/185/files#diff-c886a1940ad73cc0cd932cc4661dee8a9d76e7748a9b6f15ba33f2e7292680e9) | The exact form reached offer selection and produced early-failure bundle evidence, but permission failed before instance creation. |
| [VMs — Check VM Status](/host/vms#check-vm-status) — `enable_vms.py check` | No immutable helper-source binding | PASS — [retained representative read-only result](https://github.com/vast-ai/docs/pull/185/files#diff-1e34fca669c5308f4e7359fe41ed5ca31fd991ae69f661083bd60a4a36bad660) | The exact query returned `off`; broader status interpretation and state-transition claims remain separate. |
| [VMs — Disable VM Support](/host/vms#disable-vm-support) — `enable_vms.py off` | UNVALIDATED | UNVALIDATED — prior run was [disqualified as non-representative](https://github.com/vast-ai/docs/pull/185/files#diff-47c65eaaa665010583ea2af9497f03fdb46a7d0cd487c47085ba9ac5a59e47d9) | A suitable idle VM-capable Host, mutation authorization, before/after observation, cleanup, and canonical helper source are still needed. |

The generated [Host CLI registry check](./HOST-DOCS-CLI-COMMAND-CHECK.md)
links every recognized Host Docs CLI occurrence to its pinned canonical handler
and explicitly records that no API command was executed.

The initial correction remains in
[reviewer attempt 01](https://github.com/vast-ai/docs/pull/185/files#diff-0d7ac13642ddf099b2df6fecf9c4944347be90bbde1f1b05a0f1ddab3ad11b31).
The complete post-change failure, correction, retest, and limitation chain is
retained separately in
[reviewer attempt 02](https://github.com/vast-ai/docs/pull/185/files#diff-f2f0f374040d89b371ff06383a605611cf433c0486baf421692bbafe5b2629e8).
The final repository-local package and its exact artifact identities are in
[PR-ready packaging attempt 01](https://github.com/vast-ai/docs/pull/185/files#diff-bd9dfc2ac184fc347b116686588390a790a86868cd89511469cf1e4589ad87a3).

- `npm run test-review-context` covers page-scoped Jira context and verifies that
  the overlay exists only on the port 4000 review proxy.
- `verify-self-test-reference` passes on PR #185 and guards source/docs drift.
- Vast CLI PRs #407, #408, #409, and #410 are merged.
- Self-Test PRs #2, #3, and #4 are merged.
