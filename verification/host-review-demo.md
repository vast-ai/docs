# Host Docs: a short reviewer walkthrough

For CON-1518 / [PR185](https://github.com/vast-ai/docs/pull/185).

Open [the standalone report](host-docs-review.html), or use the local review service. Port 3000 shows the customer-facing docs; port 4000 adds the review panel. A localhost link works on the computer running that checkout's services.

## Start with a remaining correction

1. Open [Tax Guide](http://127.0.0.1:4000/host/guide-to-taxes) and click **Review**.
2. Read the whole-page summary. Use **Show all page corrections** to see the two remaining Wise/W-9 and VAT assertions. Claim filters do not change the page-wide totals.
3. Open an exact passage and its existing source controls. The remaining assertion and next source/owner question are kept explicit.

## Show the completed application correction

Open [Datacenter Status — Apply](http://127.0.0.1:4000/host/datacenter-status#apply). The page now has zero corrections, one pending check and eleven checked passages. One instruction routes the reader to the application form. The unsupported five-document checklist has been withdrawn; all five historical FAIL objects are retained in the application instruction's model history and [frozen baseline](evidence/2026-09-14-host-closure-correction-attempt-01/pre-correction-model.json).

The two owner questions remain distinct: applicable certification requirements are unresolved; detailed document-collection instructions require an approved checklist and secure channel before they are restored. That second question does not block the narrowed application instruction.

## Distinguish a source check from operational proof

Open [Host Payouts](http://127.0.0.1:4000/host/payment#payout-methods). The $20 passage is checked as a description of published guidance. Its source control shows the publication and the check's limits. It does not establish payment processing or Finance approval of the operational rule.

Open [Host Diagnostics — Logs And Support Bundles](http://127.0.0.1:4000/host/common-errors-diagnostics#logs-and-support-bundles). The retained normal Self-Test attempt failed its requirements before any diagnostic rental. Its failure bundle is evidence of that bounded attempt, not a successful official workload.

## Find the other owner questions

- [Hosting Overview](http://127.0.0.1:4000/host/hosting-overview#the-rental-contract): nine unsupported rental assertions have narrower guidance. Open their original FAIL history and current scoped source checks. The separate date-edit and availability questions remain UNVALIDATED; the replacement PASSes do not answer them.
- [Volume Offers](http://127.0.0.1:4000/host/volume-offers#volume-lifecycle): distinguish instance removal, separately rented volumes, retention and secure erasure.
- [Workload Policy](http://127.0.0.1:4000/host/workload-policy#host-responsibilities): the narrower noninterference advice is cited; broader local-workload restrictions remain a separate question.

The eight questions are separate from the 2,008 active passage records. They do not add eight failed claims or record acceptance. Page filters select related questions; claim filters do not hide them.

[Current traceability](../REVIEW-TRACEABILITY.md) · [Two remaining corrections](host-corrections-walkthrough.md) · [Bounded result and limitations](evidence/2026-09-14-host-closure-correction-attempt-02/result.md)
