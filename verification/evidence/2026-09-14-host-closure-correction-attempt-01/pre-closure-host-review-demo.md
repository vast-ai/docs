# Host Docs: a short reviewer walkthrough

For CON-1518 / [PR185](https://github.com/vast-ai/docs/pull/185).

Open [the standalone report](host-docs-review.html), or use the local review
service. The report includes checkout and setup instructions. Port 3000 shows
the customer-facing docs; port 4000 adds the review panel. A localhost link only
works on the computer running those services.

## Start with Datacenter Status

1. Open [Datacenter Status — Requirements](http://127.0.0.1:4000/host/datacenter-status#requirements) and click **Review**.
2. Read the page-wide summary. This page has **five corrections, two pending
   checks and ten checked passages**. A heading filter does not change those totals.
3. Use **Show all page corrections** to see the five application-document statements
   under **Apply**. Open a passage to see the wording the customer will read.
4. Read the two open questions: when supporting documents are collected, and
   which certification requirements apply. Product/Compliance is a proposed
   team to consult, not an assigned or approving owner.

## Then show the difference between a source check and an open question

Open [Host Payouts](http://127.0.0.1:4000/host/payment#payout-methods).
The $20 passage is checked as a description of published guidance. Its source
control shows the retained publication and the check's limits. It does not
establish actual payment processing or Finance approval of the current rule.
The separate open question asks for that operating rule and its approved source.

## Find the other questions

- [Volume Offers](http://127.0.0.1:4000/host/volume-offers#volume-lifecycle): distinguish instance removal, a separately rented volume, retention and secure erasure. Missing secure-erasure wording is a coverage gap, not a verified guarantee.
- [Workload Policy](http://127.0.0.1:4000/host/workload-policy#host-responsibilities): clarify the specific restriction on hosts' personal workloads.
- [Tax Guide](http://127.0.0.1:4000/host/guide-to-taxes): confirm Vast-specific forms, withholding and VAT handling. Already-cited official jurisdiction guidance remains usable.

The six selected questions are separate from the 2,013 passage records. They
are not six additional failed claims, proof of a rule, or evidence of acceptance.
The report's page filter selects the relevant questions; claim filters do not
hide them. Use the exact source controls for proof, not this walkthrough or
another draft documentation page.

Current status, retained checks and limitations are recorded in
[REVIEW-TRACEABILITY.md](../REVIEW-TRACEABILITY.md). The remaining 26 documentation
corrections are listed in [the correction walkthrough](host-corrections-walkthrough.md).
