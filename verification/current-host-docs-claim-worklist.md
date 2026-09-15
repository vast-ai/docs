# Current Host Docs claim worklist

Current-source claims requiring proof or correction. Historical evidence is carried only where exact source identity is recorded.

Current dispositions: 2008 occurrences (1902 PASS, 95 editorial NOT_APPLICABLE, 11 requiring review or evidence). Most dispositions are automated or exact historical carry-forward; this package records no invented manual completion.

## [Supported Hardware](http://127.0.0.1:4000/host/supported-hardware)

### [GPU Support](http://127.0.0.1:4000/host/supported-hardware#gpu-support) — `MCL-6842b63298275c23`

**Status:** UNVALIDATED

**Literal source text:** | AMD | MI25 or newer Radeon Instinct, Radeon VII, Radeon Pro VII, Radeon RX 7900 GRE/XT/XTX, and Radeon Pro W7900/W7800. Other 6000-series or newer Radeon RX/Pro W GPUs may work, but may not appear in standard ROCm filters. |

**Required proof:** Product Publication Source, Accountable Owner Confirmation

**Existing proof / limit:** [HARDWARE-OPERATOR-MCL-6842b63298275c23-1](evidence/2026-09-15-host-continuation-hardware-policy-attempt-01/source-pages/host/supported-hardware.mdx) — Source/static review only. No hardware purchase, installer, Host operation, rental, benchmark, CLI/self-test run or deployed eligibility/enforcement check. Historical listing guidance, dated owner answers and current NVIDIA verification requirements are distinct scopes.; [HARDWARE-OPERATOR-MCL-6842b63298275c23-2](evidence/2026-09-15-host-continuation-hardware-policy-attempt-01/primary/legacy-listing.mdx) — Source/static review only. No hardware purchase, installer, Host operation, rental, benchmark, CLI/self-test run or deployed eligibility/enforcement check. Historical listing guidance, dated owner answers and current NVIDIA verification requirements are distinct scopes.; [HARDWARE-OPERATOR-MCL-6842b63298275c23-3](evidence/2026-09-15-host-continuation-hardware-policy-attempt-01/primary/revised-listing.mdx) — Source/static review only. No hardware purchase, installer, Host operation, rental, benchmark, CLI/self-test run or deployed eligibility/enforcement check. Historical listing guidance, dated owner answers and current NVIDIA verification requirements are distinct scopes.; [HARDWARE-OPERATOR-MCL-6842b63298275c23-4](evidence/2026-09-15-host-continuation-verification-selftest-attempt-01/primary/source-excerpts.json) — Source/static review only. No hardware purchase, installer, Host operation, rental, benchmark, CLI/self-test run or deployed eligibility/enforcement check. Historical listing guidance, dated owner answers and current NVIDIA verification requirements are distinct scopes.

**Responsible role:** Host Product/Engineering owner

**Next:** Confirm the current AMD host listing families and ROCm-filter behavior in an applicable published product source or accountable owner answer. Distinguish listing support from NVIDIA-only verification requirements. Update the exact list/caveat or remove obsolete compatibility claims after that answer; no paid hardware trial is required to settle the published support policy.

## [Tax Guide for Hosts](http://127.0.0.1:4000/host/guide-to-taxes)

### [Introduction](http://127.0.0.1:4000/host/guide-to-taxes) — `CUR-99fb8d131e321e03`

**Status:** UNVALIDATED

**Literal source text:** **Important:** Vast.ai does not automatically withhold taxes.

**Required proof:** Authoritative Documentation Citation

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-99fb8d131e321e03-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/published-current.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-99fb8d131e321e03-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/existing-owner-question-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Ask Vast Finance/Tax to confirm current withholding practice and its jurisdiction/account exceptions in an approved source, or approve the pending tax-guide scope/removal decision.

### [By Payout Method](http://127.0.0.1:4000/host/guide-to-taxes#by-payout-method) — `CUR-11f83626486ada1d`

**Status:** FAIL

**Literal source text:** **Wise** If you are a **US-based host** receiving payouts via Wise, Vast.ai is required to collect your tax information directly. Please contact support for guidance on how to safely send your W9 to Vast.ai.

**Required proof:** Authoritative Documentation Citation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect applicable tax authority/provider guidance and existing official Vast reporting/withholding statement for the exact jurisdiction, period, and actor; retain those applicability limits.

### [Does Vast.ai handle VAT?](http://127.0.0.1:4000/host/guide-to-taxes#does-vast-ai-handle-vat) — `CUR-86b30052c0aa0b9c`

**Status:** FAIL

**Literal source text:** Vast.ai is based in California and does not currently collect or remit VAT.

**Required proof:** Authoritative Documentation Citation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect applicable tax authority/provider guidance and existing official Vast reporting/withholding statement for the exact jurisdiction, period, and actor; retain those applicability limits.

### [Is VAT shown on invoices?](http://127.0.0.1:4000/host/guide-to-taxes#is-vat-shown-on-invoices) — `CUR-8eb23dae453fdd8b`

**Status:** UNVALIDATED

**Literal source text:** VAT is not currently specified on Vast.ai invoices.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

## [Verification Stages](http://127.0.0.1:4000/host/verification-stages)

### [CPU](http://127.0.0.1:4000/host/verification-stages#cpu) — `CUR-1da68c391b45b80a`

**Status:** UNVALIDATED

**Literal source text:** | Instruction set | AVX |

**Required proof:** Authoritative Documentation Citation, Accountable Owner Confirmation

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-1da68c391b45b80a-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/upstream-verification.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/requirement-con-1516.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/context_verification-stages.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-4](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/setup-requirement-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [VERIFICATION-STORAGE-CUR-1da68c391b45b80a-1](evidence/2026-09-15-host-continuation-verification-selftest-attempt-01/source-pages/verification-stages.mdx) — No Host, account, installation, network, image publication, rental, self-test or paid operation was performed. The pinned CLI and image revisions are distinct; their code does not prove the deployed image or platform verification algorithm. Prior evidence and procedure status remain unchanged.; [VERIFICATION-STORAGE-CUR-1da68c391b45b80a-2](evidence/2026-09-15-host-continuation-verification-selftest-attempt-01/primary/source-excerpts.json) — No Host, account, installation, network, image publication, rental, self-test or paid operation was performed. The pinned CLI and image revisions are distinct; their code does not prove the deployed image or platform verification algorithm. Prior evidence and procedure status remain unchanged.; [VERIFICATION-STORAGE-CUR-1da68c391b45b80a-3](evidence/2026-09-15-host-continuation-verification-selftest-attempt-01/primary/published-verification-stages.md) — No Host, account, installation, network, image publication, rental, self-test or paid operation was performed. The pinned CLI and image revisions are distinct; their code does not prove the deployed image or platform verification algorithm. Prior evidence and procedure status remain unchanged.

**Responsible role:** Host Product/Engineering owner

**Next:** Ask the Host Product/Engineering owner to state the instruction-set requirement separately for x 86_64 and ARM64, and update the public Setup/table consistently. Do not infer a platform exception from a successful ARM64 image build or remove the rule using a host test alone.

## [Host Teams](http://127.0.0.1:4000/host/host-teams)

### [Earnings And Payouts](http://127.0.0.1:4000/host/host-teams#earnings-and-payouts) — `MCL-f426518c26948ea1`

**Status:** UNVALIDATED

**Literal source text:** Rental earnings from team-owned machines accrue to the team account, not to the individual operator who installed or managed the machine.

**Required proof:** Published Vendor Documentation, Canonical Implementation Source, Static Context Review, Accountable Owner Confirmation

**Existing proof / limit:** [TEAMS-CONSOLE-MCL-f426518c26948ea1-1](evidence/2026-09-15-host-continuation-88-attempt-01/c-teams-source/guides-excerpts.json) — No account balances, rental settlement or payout destination were observed. Do not infer a Host-specific financial allocation rule solely from separate team accounts.; [TEAMS-CONSOLE-MCL-f426518c26948ea1-2](evidence/2026-09-15-host-continuation-teams-account-attempt-01/source-excerpts.json) — No account balances, rental settlement or payout destination were observed. Do not infer a Host-specific financial allocation rule solely from separate team accounts.; [TEAMS-CONSOLE-MCL-f426518c26948ea1-3](evidence/2026-09-15-host-continuation-teams-account-attempt-01/context-review.json) — No account balances, rental settlement or payout destination were observed. Do not infer a Host-specific financial allocation rule solely from separate team accounts.; [RECOVERY-EARNINGS-MCL-f426518c26948ea1-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Host finance or Teams product owner

**Next:** Confirm whether rental earnings for team-owned machines accrue only to the team account rather than an individual installer/operator.

### [Earnings And Payouts](http://127.0.0.1:4000/host/host-teams#earnings-and-payouts) — `MCL-350d25401b2594d2`

**Status:** UNVALIDATED

**Literal source text:** Earnings and payout visibility is role-gated:

**Required proof:** Published Vendor Documentation, Static Context Review, Accountable Owner Confirmation

**Existing proof / limit:** [TEAMS-CONSOLE-MCL-350d25401b2594d2-1](evidence/2026-09-15-host-continuation-88-attempt-01/c-teams-source/guides-excerpts.json) — Published billing_read coverage for earnings/invoices does not establish the separate payout-history surface or role mapping.; [TEAMS-CONSOLE-MCL-350d25401b2594d2-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/published-current.json) — Published billing_read coverage for earnings/invoices does not establish the separate payout-history surface or role mapping.; [TEAMS-CONSOLE-MCL-350d25401b2594d2-4](evidence/2026-09-15-host-continuation-teams-account-attempt-01/context-review.json) — Published billing_read coverage for earnings/invoices does not establish the separate payout-history surface or role mapping.; [RECOVERY-EARNINGS-MCL-350d25401b2594d2-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Teams permissions product owner

**Next:** Provide the current permission/role matrix for team Earnings and Payout visibility, including custom roles.

### [Earnings And Payouts](http://127.0.0.1:4000/host/host-teams#earnings-and-payouts) — `MCL-ff0e592ec9d37394`

**Status:** UNVALIDATED

**Literal source text:** | Owner or billing administrator | Configure the team payout account. |

**Required proof:** Published Vendor Documentation, Static Context Review, Accountable Owner Confirmation

**Existing proof / limit:** [TEAMS-CONSOLE-MCL-ff0e592ec9d37394-1](evidence/2026-09-15-host-continuation-88-attempt-01/c-teams-source/guides-excerpts.json) — No payout settings were opened or changed by this lane. Manager/owner UI differences from other teams cannot isolate the payout permission rule.; [TEAMS-CONSOLE-MCL-ff0e592ec9d37394-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/published-current.json) — No payout settings were opened or changed by this lane. Manager/owner UI differences from other teams cannot isolate the payout permission rule.; [TEAMS-CONSOLE-MCL-ff0e592ec9d37394-3](evidence/2026-09-15-host-continuation-teams-account-attempt-01/context-review.json) — No payout settings were opened or changed by this lane. Manager/owner UI differences from other teams cannot isolate the payout permission rule.; [RECOVERY-EARNINGS-MCL-ff0e592ec9d37394-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Teams permissions and Host payouts owner

**Next:** Confirm which current team permissions allow configuring payout accounts; clarify whether owner or billing administrator are applicable role names.

### [Earnings And Payouts](http://127.0.0.1:4000/host/host-teams#earnings-and-payouts) — `MCL-fe79b15ff39543a3`

**Status:** UNVALIDATED

**Literal source text:** The payout account is configured on the team account. Individual members do not receive separate payouts for team-owned machine rentals.

**Required proof:** Published Vendor Documentation, Static Context Review, Accountable Owner Confirmation

**Existing proof / limit:** [TEAMS-CONSOLE-MCL-fe79b15ff39543a3-1](evidence/2026-09-15-host-continuation-88-attempt-01/c-teams-source/guides-excerpts.json) — No settlement, bank/provider destination or member payout behavior was observed. This is a substantive source gap, not an unavailable-hardware blocker.; [TEAMS-CONSOLE-MCL-fe79b15ff39543a3-2](evidence/2026-09-15-host-continuation-teams-account-attempt-01/context-review.json) — No settlement, bank/provider destination or member payout behavior was observed. This is a substantive source gap, not an unavailable-hardware blocker.; [RECOVERY-EARNINGS-MCL-fe79b15ff39543a3-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Host finance or Teams product owner

**Next:** Confirm team payout-account ownership and whether member-specific payouts or splits exist for team-owned machine rentals.

## [Host Payouts](http://127.0.0.1:4000/host/payment)

### [Introduction](http://127.0.0.1:4000/host/payment) — `MCL-b5b2716c025774a3`

**Status:** UNVALIDATED

**Literal source text:** For team-owned host machines, earnings and payout settings belong to the team account. See [Host Teams](/host/host-teams#earnings-and-payouts).

**Required proof:** Canonical Implementation Source, Product Publication Source, Accountable Owner Confirmation

**Existing proof / limit:** [RECOVERY-EARNINGS-MCL-b5b2716c025774a3-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Host finance or Teams product owner

**Next:** Confirm ownership of earnings and payout settings for team-owned machines and how account context applies.
