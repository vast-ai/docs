# Host Docs review: 11 remaining corrections

Prepared 14 September 2026 for CON-1518 / [PR185](https://github.com/vast-ai/docs/pull/185).

The current model contains 11 FAIL occurrences: two Vast-specific tax assertions and nine rental-date or availability assertions. These are documentation findings. The separate 21 BLOCKED and 1,554 UNVALIDATED occurrences retain their own evidence scope; they are not a new checklist of required live tests.

The bounded closure correction accounted for all 26 earlier FAIL IDs. Ten were narrowed to supported wording, five unsupported application checklist clauses were retired, and eleven stronger assertions remain unchanged. The single existing application instruction retains all five withdrawn FAIL objects in its history. No five new product PASSes were created.

| Topic | Earlier FAILs | Current FAILs | Disposition |
| --- | ---: | ---: | --- |
| Tax advice/documents and Vast tax handling | 4 | 2 | General Agreement-backed responsibilities retained; unsupported service disclaimers removed. Wise/W-9 and VAT remain open. |
| Application documents | 5 | 0 | Checklist withdrawn; one application instruction follows the form. Detailed collection rules still need an approved source before restoration. |
| Local workloads and renter protection | 4 | 0 | Narrowed to cited noninterference and data-review restrictions with practical advice. Whole-machine restrictions remain a separate owner question. |
| Separate accounts | 1 | 0 | Attributed to published hosting guidance; no account restriction or failure was tested. |
| Rental dates, unlisting and availability | 12 | 9 | Three unlisting passages describe the declared interface; nine stronger rental assertions remain open. |

## Exact remaining occurrences

- **CUR-11f83626486ada1d** — [Tax Guide for Hosts](http://127.0.0.1:4000/host/guide-to-taxes) / By Payout Method. Source: `host/guide-to-taxes.mdx:37`. Inspect applicable tax authority/provider guidance and existing official Vast reporting/withholding statement for the exact jurisdiction, period, and actor; retain those applicability limits.
- **CUR-86b30052c0aa0b9c** — [Tax Guide for Hosts](http://127.0.0.1:4000/host/guide-to-taxes) / Does Vast.ai handle VAT?. Source: `host/guide-to-taxes.mdx:46`. Inspect applicable tax authority/provider guidance and existing official Vast reporting/withholding statement for the exact jurisdiction, period, and actor; retain those applicability limits.
- **MCL-470bf8ec992a342e** — [Hosting Overview](http://127.0.0.1:4000/host/hosting-overview) / The Rental Contract. Source: `host/hosting-overview.mdx:75`. Locate exact independent offer/rental lifecycle authority establishing whether shortening an offer affects existing rental end dates, and cite that clause/control at this occurrence. Retain FAIL for this specific missing citation; price-increase guidance does not resolve it.
- **MCL-b7440bdb3eb40fa1** — [Pricing Your Listing](http://127.0.0.1:4000/host/pricing-your-listing) / Changing Price Later. Source: `host/pricing-your-listing.mdx:87`. Inspect the retained agreement Offer/Rental Contract/Operation and Maintenance clauses and any current published terms; bind only supported clauses. Inspect the corresponding offer/update/unlist/extension implementation and retained execution for actual system effects.
- **MCL-9cfc73236e4c395a** — [Hosting Overview](http://127.0.0.1:4000/host/hosting-overview) / Offer End Date. Source: `host/hosting-overview.mdx:86`. Inspect the retained agreement Offer/Rental Contract/Operation and Maintenance clauses and any current published terms; bind only supported clauses. Inspect the corresponding offer/update/unlist/extension implementation and retained execution for actual system effects.
- **MCL-250a0c0aa31550a1** — [Host Glossary](http://127.0.0.1:4000/host/glossary) / Offer end date / rental end date. Source: `host/glossary.mdx:75`. Inspect the retained agreement Offer/Rental Contract/Operation and Maintenance clauses and any current published terms; bind only supported clauses. Inspect the corresponding offer/update/unlist/extension implementation and retained execution for actual system effects.
- **MCL-6e0046c21ac71be4** — [Hosting Overview](http://127.0.0.1:4000/host/hosting-overview) / The Rental Contract. Source: `host/hosting-overview.mdx:75`. Locate and cite the actual rental obligation requiring machine availability through the latest active rental end date. Do not substitute price-extension help or general uptime language for that exact commitment.
- **MCL-939467a533f82627** — [Pricing Your Listing](http://127.0.0.1:4000/host/pricing-your-listing) / Changing Price Later. Source: `host/pricing-your-listing.mdx:90`. Inspect the retained agreement Offer/Rental Contract/Operation and Maintenance clauses and any current published terms; bind only supported clauses. Inspect the corresponding offer/update/unlist/extension implementation and retained execution for actual system effects.
- **MCL-e36ac539565db44a** — [Maintenance Windows](http://127.0.0.1:4000/host/maintenance-windows) / Before Maintenance. Source: `host/maintenance-windows.mdx:28`. Inspect the retained agreement Offer/Rental Contract/Operation and Maintenance clauses and any current published terms; bind only supported clauses. Inspect the corresponding offer/update/unlist/extension implementation and retained execution for actual system effects.
- **MCL-5286ec9ff0cc3272** — [Maintenance Windows](http://127.0.0.1:4000/host/maintenance-windows) / Planned Maintenance. Source: `host/maintenance-windows.mdx:34`. Inspect the retained agreement Offer/Rental Contract/Operation and Maintenance clauses and any current published terms; bind only supported clauses. Inspect the corresponding offer/update/unlist/extension implementation and retained execution for actual system effects.
- **MCL-c9441dfe43eb92f1** — [Hosting Agreement](http://127.0.0.1:4000/host/hosting-agreement) / What you commit to, in plain language. Source: `host/hosting-agreement.mdx:31`. Find and cite the exact individual-rental commitment for advertised services through each rental end date. General Hardware as a Service/Performance clauses and price cutover help are only partial; retain the specific citation FAIL until resolved.

The eight [owner questions](current-host-owner-questions.json) name proposed teams, exact passages and required decisions or sources. Rental-date semantics and governing availability commitments have separate questions. Retaining a question does not record assignment, acceptance or product proof.

The earlier payout corrections remain checked within their original scope: supplied UI evidence supports the shown providers; published guidance supports the attributed invoice, timing and bank-transfer descriptions; the Terms and Agreement clauses support only their cited subjects. No new payment test or Finance approval is implied.

[Current result and limits](evidence/2026-09-14-host-closure-correction-attempt-01/result.md) · [Exact 26-finding reconciliation](current-host-closure-correction.json) · [Short reviewer demo](host-review-demo.md) · [Standalone report](host-docs-review.html)

The [previous walkthrough](evidence/2026-09-14-host-closure-correction-attempt-01/pre-closure-host-corrections-walkthrough.md) is retained as historical navigation, with the previous counts and wording.
