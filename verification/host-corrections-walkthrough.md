# Host Docs review: 2 remaining corrections

Prepared 14 September 2026 for CON-1518 / [PR185](https://github.com/vast-ai/docs/pull/185).

The current model contains two FAIL occurrences, both Vast-specific tax assertions. Nine rental-date or availability assertions have been withdrawn into narrower source-bounded guidance, with their original FAIL assertions and evidence preserved in history. The separate 21 BLOCKED and 1,529 UNVALIDATED occurrences retain their own evidence scope; they are not a new checklist of required live tests.

A separate [unchanged-source reconciliation](evidence/2026-09-14-host-unvalidated-source-attempt-01/result.md) supports 24 of 26 frozen UNVALIDATED candidates, holds two rounded bandwidth rows, and changes no customer wording or owner question. Current totals are 369 PASS / 2 FAIL / 21 BLOCKED / 87 NOT_APPLICABLE / 1,529 UNVALIDATED. Of the original 1,558 UNVALIDATED passages, 31 now have scoped PASS results; two earlier BLOCKED passages separately entered UNVALIDATED.

The bounded closure correction accounted for all 26 earlier FAIL IDs. Nineteen were narrowed to supported wording, five unsupported application checklist clauses were retired, and two tax assertions remain unchanged. The single existing application instruction retains all five withdrawn FAIL objects in its history. No five new product PASSes were created.

| Topic | Earlier FAILs | Current FAILs | Disposition |
| --- | ---: | ---: | --- |
| Tax advice/documents and Vast tax handling | 4 | 2 | General Agreement-backed responsibilities retained; unsupported service disclaimers removed. Wise/W-9 and VAT remain open. |
| Application documents | 5 | 0 | Checklist withdrawn; one application instruction follows the form. Detailed collection rules still need an approved source before restoration. |
| Local workloads and renter protection | 4 | 0 | Narrowed to cited noninterference and data-review restrictions with practical advice. Whole-machine restrictions remain a separate owner question. |
| Separate accounts | 1 | 0 | Attributed to published hosting guidance; no account restriction or failure was tested. |
| Rental dates, unlisting and availability | 12 | 0 | Three earlier unlisting passages describe the declared interface; nine original rental assertions were withdrawn into narrower guidance. Backend semantics and maintenance-policy questions stay open. |

## Exact remaining occurrences

- **CUR-11f83626486ada1d** — [Tax Guide for Hosts](http://127.0.0.1:4000/host/guide-to-taxes) / By Payout Method. Source: `host/guide-to-taxes.mdx:37`. Inspect applicable tax authority/provider guidance and existing official Vast reporting/withholding statement for the exact jurisdiction, period, and actor; retain those applicability limits.
- **CUR-86b30052c0aa0b9c** — [Tax Guide for Hosts](http://127.0.0.1:4000/host/guide-to-taxes) / Does Vast.ai handle VAT?. Source: `host/guide-to-taxes.mdx:46`. Inspect applicable tax authority/provider guidance and existing official Vast reporting/withholding statement for the exact jurisdiction, period, and actor; retain those applicability limits.

Two adjacent changes remove the hypothetical “maintenance-safe date” label and the universal contract-end prerequisite before unlisting. The example remains NOT_APPLICABLE. The unlisting instruction is checked only against its declared offer-removal interface and separate review advice. No date edit or unlist command is presented as permission to stop the host.

The nine replacement PASSes do not confirm initial rental dates, shortening, constant-duration roll-forward, an exact safe-stop boundary, or applicable maintenance guidelines. Their [exact before/after map](evidence/2026-09-14-host-closure-correction-attempt-02/change-map.json) and frozen histories preserve those distinctions. Seven affected procedure nodes now carry STALE; prior procedure evidence is retained.

The eight [owner questions](current-host-owner-questions.json) name proposed teams, exact passages and required decisions or sources. Rental-date semantics and governing availability commitments have separate questions. Retaining a question does not record assignment, acceptance or product proof.

The earlier payout corrections remain checked within their original scope: supplied UI evidence supports the shown providers; published guidance supports the attributed invoice, timing and bank-transfer descriptions; the Terms and Agreement clauses support only their cited subjects. No new payment test or Finance approval is implied.

[Current result and limits](evidence/2026-09-14-host-closure-correction-attempt-02/result.md) · [Exact 26-finding reconciliation](current-host-closure-correction.json) · [Short reviewer demo](host-review-demo.md) · [Standalone report](host-docs-review.html)

The [previous walkthrough](evidence/2026-09-14-host-closure-correction-attempt-01/pre-closure-host-corrections-walkthrough.md) is retained as historical navigation, with the previous counts and wording.
