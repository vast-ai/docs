# Host Docs review: 26 remaining corrections

Prepared 14 September 2026 for CON-1518 / PR #185.

The review model contains 26 FAIL entries. They identify documentation corrections, not 26 failed machine tests. Other pending reviews and the 23 prerequisite blockers remain separate. This walkthrough is navigation, not evidence or acceptance.

The bank-transfer FAQ is restored and cites Vast's published guidance. The liability note now cites the relevant Terms sections and keeps their qualifications. [Read the checks and limits](evidence/2026-09-14-payout-terms-correction-attempt-01/result.md).

The eight topics below show completed corrections and the remaining work. Payout and invoice guidance is now cited too: four citation corrections and two repeated timing passages are checked within their published-source scope. The next group is tax information and Vast's tax services. The grouping does not merge passage statuses. Use existing official authority first; ask an owner only about a genuine remaining gap or ambiguity. A link to another draft Host page is navigation, not independent proof.

## How to complete one group

1. Read the exact customer-facing passage and identify the claim that needs correction.
2. Check the existing official source or retained result. Record exactly what it supports and its limits.
3. Correct the wording or add the applicable citation. Separate advice, policy and observed behavior where mixed.
4. Retest the changed passage, source links and evidence binding. Refresh the standalone HTML and localhost reviewer when implementing corrections.
5. Close only the supported findings. If support is still missing, record the specific question and next action. Escalate only when a suitable check needs unavailable authority, access or input.

No new account, payment, rental, machine or publication action is authorized by this walkthrough. A policy rule needs its approved source, not a runtime demonstration. Historical evidence stays in the audit records; the walkthrough shows the current finding only.

## Order of work

| Step | Topic | Recorded FAILs |
| --- | --- | ---: |
| 1 | Payout providers and bank-transfer guidance checked | 0 |
| 2 | Published payout and invoice guidance checked | 0 |
| 3 | Liability wording corrected and cited | 0 |
| 4 | Tax information and Vast's tax services | 4 |
| 5 | Datacenter application documents | 5 |
| 6 | Host workloads and renter protection | 4 |
| 7 | Separate host and client accounts | 1 |
| 8 | Rental end dates, unlisting and availability | 12 |
| | Remaining corrections | 26 |

## 1. Payout providers and bank-transfer guidance checked

The user's Earnings screenshot shows Wise, PayPal and Stripe. Those are the
three provider options it supports. It does not establish whether Vast offers
direct bank transfers.
[Read the intake and exact limits](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/verification/evidence/2026-09-14-payout-ui-intake-attempt-01/result.md).
The separate [published payout FAQ](https://docs.vast.ai/host/payment) explicitly
says direct bank transfers, ACH, wire and SWIFT are unavailable. Nothing in the
screenshot contradicts that guidance.

The restored FAQ reports what Vast's published guidance says. Its source check
does not establish how every payout route works. The retained publication comes
from the same documentation repository, so it is not independent technical proof.

**Scope:** The supplied view shows Stripe, PayPal and Wise. The URL is user-attributed and the capture time is unknown. The original attachment stays outside this shareable repository; the inspection record and its hash are retained.

**Checked:** The restored FAQ, its exact source excerpt and its passage links work in both reviewers. Recheck the wording if Vast changes its published guidance.

The screenshot supports the three provider choices. It does not establish successful payments, fees, eligibility or bank-transfer availability.

### 1. PayPal is shown under Earnings > Payout Account.

Host Payouts → Payout Methods. [Open page heading](http://127.0.0.1:4000/host/payment#payout-methods) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:31)

Audit reference: `MCL-77f72f0e0ac77e54` · current status: PASS within the supplied UI/provider scope.

### 2. Stripe is shown under Earnings > Payout Account.

Host Payouts → Payout Methods. [Open page heading](http://127.0.0.1:4000/host/payment#payout-methods) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:31)

Audit reference: `MCL-a04f3ef2f5a7d5fd` · current status: PASS within the supplied UI/provider scope.

### 3. Wise is shown under Earnings > Payout Account.

Host Payouts → Payout Methods. [Open page heading](http://127.0.0.1:4000/host/payment#payout-methods) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:31)

Audit reference: `MCL-cc62439b0f816902` · current status: PASS within the supplied UI/provider scope.

### 4. Vast's published guidance says direct bank transfers are unavailable.

Host Payouts → Can Vast send direct bank transfers? [Open page heading](http://127.0.0.1:4000/host/payment#can-vast-send-direct-bank-transfers) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:101)

Audit reference: `MCL-9826b26393329d27` · current status: PASS for the attributed description of the published FAQ. That FAQ says direct bank transfers, ACH, wire and SWIFT are unavailable. No bank transfer was attempted.

## 2. Published payout and invoice guidance checked

The four passages below now cite the exact sections of Vast's published payout guidance. The unsupported noon-Pacific time was removed. Two repeated timing passages now distinguish the published first-payout estimate from the Hosting Agreement's separate billing-period clock.

**Scope:** These checks establish what Vast publishes, not that invoices or payments ran successfully. The published page comes from this documentation repository, so it is not independent backend proof. The timing cards show separate guidance and Agreement excerpts. Recheck if either source changes.

[Read the current result and source limits](evidence/2026-09-14-payout-invoice-correction-attempt-01/result.md).

### 5. Published guidance sets an invoice minimum of at least $20 USD.

Host Payouts → Payout Schedule. [Open page heading](http://127.0.0.1:4000/host/payment#payout-schedule) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:53)

Audit reference: `MCL-e2b956d14494e470` · current status: PASS for the attributed invoice-threshold description.

### 6. Published guidance says invoices are generated weekly on Fridays.

Host Payouts → Payout Schedule. [Open page heading](http://127.0.0.1:4000/host/payment#payout-schedule) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:54)

Audit reference: `MCL-df7b287adb0df683` · current status: PASS for the published schedule. No specific time of day is claimed.

### 7. Published guidance says balances below $20 roll forward until the threshold is reached.

Host Payouts → Payout Schedule. [Open page heading](http://127.0.0.1:4000/host/payment#payout-schedule) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:58)

Audit reference: `MCL-5936430d1b2d8de9` · current status: PASS for the published rollover rule. Account prerequisites are stated separately.

### 8. Published guidance requires a connected valid payout method and a balance of at least $20 USD for invoices.

Host Payouts → Why are invoices not generating?. [Open page heading](http://127.0.0.1:4000/host/payment#why-are-invoices-not-generating) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:106)

Audit reference: `MCL-bbd64c772e9b4693` · current status: PASS for the published prerequisites, not a test of account enforcement.

The two timing descriptions, `MCL-3d796f5ae7f2020e` and `MCL-3afd93ae0b6cf8a4`, are also checked. They quote the typical first-payout estimate with provider/region qualifications and retain the separate Agreement citation. No payout deadline or successful payment is inferred.

## 3. Liability wording corrected and cited

The note describes three named Terms sections: disclaimers for third-party products or services offered through the website, delays or failures beyond Vast's reasonable control, and exclusions that may not apply under certain state laws.

Each statement links to its supporting section. This describes the published Terms; it does not decide liability for an individual payout, legal enforceability or which agreement takes priority.

Recheck these citations if the Terms change. The exact source excerpts and qualifications are available in both reviewers.

### 9. The payout note describes the applicable Terms clauses and their limits.

Host Payouts → Payout Account. [Open page heading](http://127.0.0.1:4000/host/payment#payout-account) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/payment.mdx:46)

Audit reference: `MCL-06956d724f70d2a3` · current status: PASS for the cited Terms summary. The former blanket payout exemption is not the current claim.

## 4. Tax information and Vast's tax services — 4 entries

**Question:** Separate official tax guidance from claims about what Vast itself does. The agreement already supports some host tax responsibilities; it does not establish all of Vast's document delivery, advice or VAT practices.

**Next action:** Use current official Vast tax/payment information for its practices, and applicable tax-authority guidance for legal requirements. For Wise/W-9, also identify the approved secure submission channel. Do not request or collect a completed W-9 for this documentation review.

**Done when:** Only supported service limitations, reporting requirements and jurisdiction-qualified practices remain. Each applicable claim has an exact citation; no global VAT conclusion is inferred from a California address.

### 10. Vast cannot provide tax advice or verify public tax guidance (the agreement-backed responsibilities are separate).

Tax Guide for Hosts → Introduction. [Open page heading](http://127.0.0.1:4000/host/guide-to-taxes) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/guide-to-taxes.mdx:13)

Audit reference: `CUR-a991f28f683ba829` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 11. Vast does not supply tax documents or advice to hosts outside the US.

Tax Guide for Hosts → International Hosts. [Open page heading](http://127.0.0.1:4000/host/guide-to-taxes#international-hosts) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/guide-to-taxes.mdx:19)

Audit reference: `CUR-93f089288e67669d` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 12. US hosts paid through Wise must give Vast tax information; support supplies the W-9 submission process.

Tax Guide for Hosts → By Payout Method. [Open page heading](http://127.0.0.1:4000/host/guide-to-taxes#by-payout-method) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/guide-to-taxes.mdx:37)

Audit reference: `CUR-11f83626486ada1d` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 13. Vast does not collect or remit VAT.

Tax Guide for Hosts → Does Vast.ai handle VAT?. [Open page heading](http://127.0.0.1:4000/host/guide-to-taxes#does-vastai-handle-vat) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/guide-to-taxes.mdx:46)

Audit reference: `CUR-86b30052c0aa0b9c` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

## 5. Datacenter application documents — 5 entries

**Question:** Check the actual current application checklist. General business verification does not prove that every listed document is required.

**Next action:** Read the applicable current Vast datacenter application/form or published checklist. Confirm required versus optional/conditional documents and which program it concerns. There is no need to submit an application or collect anyone's identity documents.

**Done when:** Each requested document is supported by the applicable checklist, or is clearly marked conditional/advisory where supported. Do not mix Certified Data Center requirements with a separate Secure Cloud program.

### 14. Additional due-diligence documents requested by Vast.

Datacenter Status → Apply. [Open page heading](http://127.0.0.1:4000/host/datacenter-status#apply) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/datacenter-status.mdx:33)

Audit reference: `MCL-08d534d1cc02eb2c` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 15. Business registration or certificate of good standing.

Datacenter Status → Apply. [Open page heading](http://127.0.0.1:4000/host/datacenter-status#apply) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/datacenter-status.mdx:33)

Audit reference: `MCL-4be2159765519977` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 16. Datacenter name, address and certificates.

Datacenter Status → Apply. [Open page heading](http://127.0.0.1:4000/host/datacenter-status#apply) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/datacenter-status.mdx:33)

Audit reference: `MCL-b87645b43a9136dd` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 17. Government-issued ID for business owners.

Datacenter Status → Apply. [Open page heading](http://127.0.0.1:4000/host/datacenter-status#apply) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/datacenter-status.mdx:33)

Audit reference: `MCL-d5001953fbd7df0b` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 18. A contract or invoice linking the business to the datacenter.

Datacenter Status → Apply. [Open page heading](http://127.0.0.1:4000/host/datacenter-status#apply) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/datacenter-status.mdx:33)

Audit reference: `MCL-e03564808f65b40b` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

## 6. Host workloads and renter protection — 4 entries

**Question:** Clarify whether a rule covers the rented GPUs/resources or the entire machine, and what the approved rule says about idle renter containers. These are policy questions; do not interfere with a renter to test them.

**Next action:** Read the applicable agreement and approved workload policy. Compare the broad whole-machine wording with the retained older hosting source describing background work on remaining GPUs. Ask for a policy decision only if current authority does not resolve the scope. The draft Workload Policy page cannot prove itself or another draft page.

**Done when:** All four passages consistently state the supported noninterference/dedication rule and cite its source. No stronger exclusive-use obligation is inferred from language assigning exclusive responsibility.

### 19. Hosting Overview: no local gaming, mining, display work or other GPU jobs on a rented machine.

Hosting Overview → Host Commitment. [Open page heading](http://127.0.0.1:4000/host/hosting-overview#host-commitment) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/hosting-overview.mdx:53)

Audit reference: `MCL-b61d15c0282ef567` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 20. Supported Hardware: rented machines should be dedicated.

Supported Hardware → Unsupported Or Discouraged Setups. [Open page heading](http://127.0.0.1:4000/host/supported-hardware#unsupported-or-discouraged-setups) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/supported-hardware.mdx:78)

Audit reference: `MCL-c59caa4cd52bcc1f` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 21. Workload Policy: do not interfere with renter containers because they appear idle.

Workload Policy → Host Responsibilities. [Open page heading](http://127.0.0.1:4000/host/workload-policy#host-responsibilities) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/workload-policy.mdx:23)

Audit reference: `MCL-393941d0e9be9d31` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 22. Workload Policy: no local gaming, mining, benchmarks, display or background GPU jobs during a rental.

Workload Policy → Host Responsibilities. [Open page heading](http://127.0.0.1:4000/host/workload-policy#host-responsibilities) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/workload-policy.mdx:23)

Audit reference: `MCL-af1c482a08b09316` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

## 7. Separate host and client accounts — 1 entry

**Question:** Separate the recommendation to use a dedicated account from the stronger claim that mixed host/client use is unsupported and causes management problems.

**Next action:** Use current official account/support guidance first, then relevant account-mode or permission code and existing observations for asserted behavior. Do not change account type or accept a new agreement merely to prove this instruction.

**Done when:** The recommendation, support boundary and any claimed technical problem are supported separately, or the wording is narrowed to the supported guidance.

### 23. Use a dedicated host account; mixed host/client use is unsupported and can cause account or machine-management issues.

Host Account and Agreement → Do I need a separate host account?. [Open page heading](http://127.0.0.1:4000/host/account-hosting-agreement#do-i-need-a-separate-host-account) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/account-hosting-agreement.mdx:20)

Audit reference: `MCL-57133525f112013a` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

## 8. Rental end dates, unlisting and availability — 12 entries

**Question:** Resolve three related questions: how offer dates affect new and existing rentals; what unlisting changes; and the host's availability obligations. A CLI source about price protection does not answer these other questions.

**Next action:** Start with canonical offer/rental lifecycle implementation and the applicable agreement clauses. Reuse suitable retained observations. If an actual transition still needs a test, plan the smallest separately authorized check on controlled resources; do not alter an active customer's offer or rental. Review composite passages sentence by sentence so supported advice is not treated as a new legal promise.

**Done when:** Each lifecycle statement matches the supported behavior, each obligation matches an applicable rule, and all affected pages agree. Bind evidence separately to all twelve occurrences; one successful check is not a blanket workflow PASS.

### 24. Hosting Overview: shortening an offer end date affects only future rentals.

Hosting Overview → The Rental Contract. [Open page heading](http://127.0.0.1:4000/host/hosting-overview#the-rental-contract) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/hosting-overview.mdx:75)

Audit reference: `MCL-470bf8ec992a342e` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 25. Hosting Overview: the machine must stay available until the latest active rental ends.

Hosting Overview → The Rental Contract. [Open page heading](http://127.0.0.1:4000/host/hosting-overview#the-rental-contract) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/hosting-overview.mdx:75)

Audit reference: `MCL-6e0046c21ac71be4` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 26. Hosting Overview: the offer end date is the acceptance deadline and becomes the rental end date.

Hosting Overview → Offer End Date. [Open page heading](http://127.0.0.1:4000/host/hosting-overview#offer-end-date) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/hosting-overview.mdx:86)

Audit reference: `MCL-9cfc73236e4c395a` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 27. Pricing: shortening an offer does not shorten active rental end dates.

Pricing Your Listing → Changing Price Later. [Open page heading](http://127.0.0.1:4000/host/pricing-your-listing#changing-price-later) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/pricing-your-listing.mdx:87)

Audit reference: `MCL-b7440bdb3eb40fa1` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 28. Pricing: unlisting stops new rentals while active contracts continue.

Pricing Your Listing → Changing Price Later. [Open page heading](http://127.0.0.1:4000/host/pricing-your-listing#changing-price-later) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/pricing-your-listing.mdx:88)

Audit reference: `MCL-dcb653ae3a927dae` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 29. Pricing: keep the machine online until the latest active rental end date.

Pricing Your Listing → Changing Price Later. [Open page heading](http://127.0.0.1:4000/host/pricing-your-listing#changing-price-later) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/pricing-your-listing.mdx:90)

Audit reference: `MCL-939467a533f82627` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 30. Maintenance: multiple rentals can coexist; wait for every active rental to finish.

Maintenance Windows → Before Maintenance. [Open page heading](http://127.0.0.1:4000/host/maintenance-windows#before-maintenance) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/maintenance-windows.mdx:28)

Audit reference: `MCL-e36ac539565db44a` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 31. Maintenance: set the offer end date for planned downtime while honoring existing rentals.

Maintenance Windows → Planned Maintenance. [Open page heading](http://127.0.0.1:4000/host/maintenance-windows#planned-maintenance) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/maintenance-windows.mdx:34)

Audit reference: `MCL-5286ec9ff0cc3272` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 32. Removing/recreating: unlisting prevents new contracts but does not end existing ones; preserve the separate recovery advice.

Removing or Recreating Machines → How do I unlist, delete, or recreate a machine?. [Open page heading](http://127.0.0.1:4000/host/removing-recreating-machines#how-do-i-unlist-delete-or-recreate-a-machine) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/removing-recreating-machines.mdx:20)

Audit reference: `MCL-ae7f4423cef61511` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 33. Workload Policy: unlisting stops new rentals while existing contracts continue.

Workload Policy → What To Do. [Open page heading](http://127.0.0.1:4000/host/workload-policy#what-to-do) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/workload-policy.mdx:95)

Audit reference: `MCL-47b85b40f58091a2` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 34. Glossary: accepted offer dates become rental end dates that later host changes cannot shorten.

Host Glossary → Offer end date / rental end date. [Open page heading](http://127.0.0.1:4000/host/glossary#offer-end-date-rental-end-date) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/glossary.mdx:75)

Audit reference: `MCL-250a0c0aa31550a1` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

### 35. Hosting Agreement explainer: provide advertised services until each rental's end date.

Hosting Agreement → What you commit to, in plain language. [Open page heading](http://127.0.0.1:4000/host/hosting-agreement#what-you-commit-to-in-plain-language) · [Exact source passage](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/host/hosting-agreement.mdx:31)

Audit reference: `MCL-c9441dfe43eb92f1` · current status: FAIL. Labels above summarize the issue; the source passage and model retain the exact wording.

## Inventory and limitations

- Inventory: [current-host-docs-review.json](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/verification/current-host-docs-review.json), SHA-256 `1b22bc97a8dc73fa34c047331a8a6a76e3a7564d8579cee5414139c269cf2857`.
- Coverage: every current FAIL occurrence appears once: 35/35, across 12 Host pages.
- Related authority conflicts: [11 September source scan](/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk/verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01/source-scan.md). This is a retained prior scan, not a new claim that its external pages are current today.
- The payout-method review must resolve the retained direct-transfer/provider-mediated ACH distinction. The workload review must resolve the retained whole-machine/rented-resource distinction.
- Local source-line links identify exact existing passages. Page-heading URLs are navigation targets; they have not received a new rendered-browser test for this walkthrough.
- No customer documentation, claim status, evidence, reviewer output, commit or publication is changed by creating this plan.
