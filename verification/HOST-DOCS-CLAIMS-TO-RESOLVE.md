# Host Docs: claims to work through

For [CON-1518](https://vastai.atlassian.net/browse/CON-1518) and
[PR #185](https://github.com/vast-ai/docs/pull/185).

Start with the decisions below, then use the
[complete page-by-page worklist](current-host-docs-claim-worklist.md).
The worklist quotes the current customer-facing wording and identifies its
section, evidence, limits, responsible role, and next action. An audit ID is
only a tracking key; it is not the statement or its proof.

These are requests to establish facts, not approved product statements.
Missing proof is **UNVALIDATED**. A required missing citation or a confirmed
defect is **FAIL**. **BLOCKED** is reserved for a specific unavailable
prerequisite. Repository checks do not establish live Host behavior.

## Start here: owner decisions

| Topic and page | Customer-facing statement or question to resolve | What would settle it |
| --- | --- | --- |
| [Tax Guide — introduction](http://127.0.0.1:4000/host/guide-to-taxes) | “Vast.ai does not automatically withhold taxes.” | Finance/Legal confirms the current scope and supplies an authoritative, publishable citation. |
| [Tax Guide — By Payout Method](http://127.0.0.1:4000/host/guide-to-taxes#by-payout-method) | Who issues tax documents for Stripe, PayPal, and Wise? Is Vast required to collect a US host's W-9, and through which approved secure channel? | Finance/Legal and the payment owner confirm each provider-specific statement and the safe collection instructions. |
| [Tax Guide — Does Vast.ai handle VAT?](http://127.0.0.1:4000/host/guide-to-taxes#does-vastai-handle-vat) | “Vast.ai is based in California and does not currently collect or remit VAT.” The following section also says VAT is absent from invoices. | Finance/Legal confirms both statements, any jurisdiction/account exceptions, and the citation. Other Host docs are not independent evidence. |
| [Verification Stages — Verification Requirements](http://127.0.0.1:4000/host/verification-stages#verification-requirements) | Which listed requirements are enforced gates, and which are recommendations? In particular, what enforces SSH-password-login and kernel restrictions? | Verification/backend owner supplies the exact implementation/configuration and version; Product confirms policy language where applicable. |
| [Disable SSH Password Login — introduction](http://127.0.0.1:4000/host/disable-ssh-password-login) | “A machine with it enabled will not pass verification.” | Bind the enforcement rule to its authoritative source. A matching sentence on Verification Stages is not proof. |
| [Machine Metrics — page](http://127.0.0.1:4000/host/machine-metrics) | Sampling, batching/backfill, chart freshness, retention, and VM limitations. | Daemon and dashboard owners identify the exact source/configuration; retain representative observations for claims about what the UI actually displays. |
| [Notifications — All Host Notifications](http://127.0.0.1:4000/host/notifications#all-host-notifications) | Event names, recipients, defaults, notice periods, and the effects attributed to notifications. | Notifications/backend owner binds event configuration; Product confirms notice commitments; runtime evidence shows delivery/recipient behavior. |
| [Market Metrics — Freshness And Limits](http://127.0.0.1:4000/host/market-metrics#freshness-and-limits) | The unsupported fixed refresh/cache/per-user promises have been removed. What, if anything, should replace them? | Only if fixed promises are needed: the metrics owner supplies the authoritative freshness and limit configuration. This is a content decision, not proof that a remaining number is wrong or a mandatory blocker to keeping the narrower wording. |

The detailed records also cover account/Teams ownership, agreements, earnings,
payouts, workload policy, verification transitions, and volume lifecycle claims.
Do not treat this short meeting queue as the complete inventory.

## Separate runtime/operator work

| Workflow | Evidence still needed |
| --- | --- |
| [Self-Test](http://127.0.0.1:4000/host/how-to-self-test) | Authorized representative runs of each documented path, with exact CLI/image revisions and sanitized results. A source/signature check does not demonstrate authentication, successful diagnostics, bundle contents, or cleanup. |
| [VMs — Check VM Status](http://127.0.0.1:4000/host/vms#check-vm-status) | Preserve the limited existing read-only observation. Other states and disabling VM support require a suitable idle VM-capable host, source binding, and explicit authorization. |
| [Offline Machine](http://127.0.0.1:4000/host/machine-offline) | Host Operations reviews the diagnostic branches and supplies representative observations. Do not run public-network probes, restart services, or touch renter workloads just to complete this review. |
| [Upgrade the Kernel](http://127.0.0.1:4000/host/upgrade-kernel) and [Disable SSH Password Login](http://127.0.0.1:4000/host/disable-ssh-password-login) | A disposable, representative OS/Host environment and explicit permission for privileged changes, SSH changes, reboot, and recovery testing. Local documentation tests cannot validate these procedures. |

See the separate [runtime/operator register](current-runtime-operator-blockers.md)
and [source-owner register](current-source-owner-blockers.md). They distinguish
unvalidated evidence requests from genuinely blocked checks.

## How to close one item

1. Open the linked section and confirm the exact sentence or command being reviewed.
2. Supply a pinned source or retained result suitable for that statement. For
   policy, pricing, legal, tax, or account commitments, identify the accountable
   owner and authoritative citation; code alone may not settle the claim.
3. Correct the customer-facing wording if needed. Keep the original finding.
4. Retest the corrected statement and record its evidence and limitations.

Do not mark a whole page PASS because its links work or one command passed.
No human acceptance or external workstream completion is recorded here.
