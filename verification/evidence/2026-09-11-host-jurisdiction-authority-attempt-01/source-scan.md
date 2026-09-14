# Official sources: what they answer

Source inspection on 11 September 2026. This scan is not personal tax advice or approval to publish the Host Docs.

## Coverage

The frozen inventory accounts for all 44 primary Host pages and 2,013 claims.
Subject/status matching identified 336 source-search candidates; it is retrieval,
not proof. Eight exact corrections were selected before implementation. A separate
reader inspected all 35 non-Tax FAIL findings and 311 unique non-Tax claims across
the focused business/security pages and subject matches. Another reader inspected
all 15 Tax Guide records. Root independently checked the sources used for the eight
corrections and the jurisdiction limits below. The other product/runtime claims
have not received a new substantive adjudication. The 18 CLI and 15 SDK wrappers
remain central-reference support layers.

## Selected corrections

| Page / passage | Answer available | Limit |
| --- | --- | --- |
| Tax Guide / United States Hosts: keep provider tax details current | Stripe explains tax-information updates and account/platform availability. | Advice review, not a promise that every account has the same controls. |
| Tax Guide / United States Hosts: check tax-form eligibility | PayPal conditions delivery on eligibility; IRS explains Form 1099-K and reporting. | Check the provider, account and tax year. No particular host's eligibility is decided. |
| Tax Guide / United States Hosts: filing and payment preparation | IRS gig-economy guidance includes equipment rental; FTB provides California guidance. | General preparation advice. California applies only where its tax rules apply to the host. |
| Workload Policy / Renter Reports And Host Logs | Agreement, Operation and Maintenance, prohibits reviewing Authorized User data. | Written privacy rule plus diagnostic advice. No proof of enforcement or report accuracy. |
| Datacenter Status / Requirements: business-owned equipment and owner identity checks | Current program application, What It Takes / Verified Business; separately, Compliance / Auditing & oversight describes Secure Cloud partner audits. | Keep the two publication scopes separate. They do not specify registration documents or prove completed applicant checks. |
| Datacenter Status / Benefits: search placement | Current program application, Priority Placement. | Correct the vague reliability/search wording to the published search-placement benefit. No reliability-score increase is established. |
| Datacenter Status / Benefits: support | Current program application, Dedicated Support. | Describe its stated team access; it does not specify Discord or Slack. |

## US, California and international guidance

| Official source | What it can answer | What it cannot answer |
| --- | --- | --- |
| [IRS Gig Economy Tax Center](https://www.irs.gov/businesses/gig-economy-tax-center), What is gig work / Gig economy income is taxable | Federal guidance includes equipment rental and reporting income without an information form. | A particular host's filing threshold, entity classification, deductions, or Vast's actual reporting. |
| [IRS Form 1099-K](https://www.irs.gov/businesses/understanding-your-form-1099-k), Who sends Form 1099-K | General form/reporting guidance; use the applicable tax year and payment route. | Whether Vast or a provider owes a particular host this form. |
| [California FTB Gig Economy](https://www.ftb.ca.gov/file/business/industries/gig-economy.html), Gig income and taxes / Estimated taxes | California income, recordkeeping and payment guidance. | California residency or tax liability merely because Vast is located there. It is not a VAT rule. |
| [IRS taxpayers abroad](https://www.irs.gov/individuals/international-taxpayers/us-citizens-and-resident-aliens-abroad), opening scope | US citizens and resident aliens abroad may still have US filing/reporting duties. | That residence outside the US means only local obligations apply. |
| [HMRC online-platform income](https://www.gov.uk/guidance/check-if-you-need-to-tell-hmrc-about-your-income-from-online-platforms) | UK guidance for checking whether platform income must be reported. | A global rule or Vast's international form-delivery policy. |
| [European Commission VAT place of taxation](https://taxation-customs.ec.europa.eu/taxation/vat/vat-directive/place-taxation_en), Supply of services, and [cross-border VAT guidance](https://europa.eu/youreurope/business/taxation/vat/cross-border-vat/index_en.htm) | Service/customer circumstances affect the applicable VAT treatment. | Classification of the exact Vast transaction, the liable party, or proof that Vast collects or remits VAT. |
| [IRS Form W-9](https://www.irs.gov/forms-pubs/about-form-w-9), purpose | W-9 supplies a TIN to a person required to file an information return. | The blanket Wise/Vast requirement or Vast's approved secure submission channel. |
| [IRS backup withholding](https://www.irs.gov/businesses/small-businesses-self-employed/backup-withholding), What is backup withholding | Withholding can be required in specified circumstances. | Proof of Vast's current withholding setup or actions. |

The government pages above were retrieved without credentials and retained with
HTTP status, original body, extracted text and hashes. Captures establish what
the source published at retrieval time. They do not determine a host's tax position.
Stripe/PayPal and Agreement captures used by the corrections retain their earlier
9 September capture dates and exact-source limits.

## Specific questions still open

- Tax Guide introduction: the Agreement supports the named contract clauses;
  Vast's corporate tax-advice/service disclaimer needs its own published authority.
- International Hosts: no retrieved tax authority establishes that Vast never
  supplies documents to hosts outside the US. Check the current Vast policy and
  qualify the jurisdiction guidance for US taxpayers abroad.
- Withholding: obtain Vast's applicable reporting/withholding policy. Do not infer
  it from independent-contractor language or the absence of a tax form.
- Wise/W9: confirm the payer/reporting relationship and approved secure submission
  process, not just the general purpose of W-9.
- VAT handling and invoice display: confirm actual Vast tax handling separately
  from checking a representative invoice or its implementation.
- Datacenter application: exact ID, good-standing, facility-invoice and certificate
  document requirements are not established by the public program summary.
- Rental end dates, unlisting and contract availability: government tax/security
  rules do not establish these product lifecycle behaviors or specific promises.

## Conflicting sources to resolve

The older [Vast console FAQ](https://console.vast.ai/faq/), Hosting / How and when
will I be paid for hosting, describes US ACH through Stripe. This conflicts with
the blanket ACH-unavailable sentence in Host Payouts (MCL-9826b26393329d27).
Distinguish direct Vast transfers from provider-mediated ACH and confirm the
current payout policy. The same FAQ contains dated product guidance, so its
payment schedule and threshold were not treated as sufficient current authority.

The older [Vast hosting page](https://console.vast.ai/hosting/), Automatic
Management, describes background tasks on remaining GPUs while other GPUs are
rented. This raises a scope question for whole-machine dedication statements:
MCL-b61d15c0282ef567, MCL-af1c482a08b09316 and MCL-c59caa4cd52bcc1f.
Resolve current policy and rented-versus-unused resource scope before changing
those findings. No background workload was run.

## Circularity check

The draft Host pages are the claims. This scan, registry, tests, generated HTML
and knowledge graph only record/retrieve the review. Terminal authorities are
the independently published government, provider, Agreement and program sources.
Matching a claim's words, adding a link, or passing an interface test cannot prove
the claim. Advice checks establish appropriateness within the cited context;
program-rule checks establish the published rule, not runtime compliance.
