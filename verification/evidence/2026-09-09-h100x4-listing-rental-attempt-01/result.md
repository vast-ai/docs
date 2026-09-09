# Listing rejected; client rental not started

Machine **150296**, new four-H100 host. Host Docs PR185 / Jira CON-1518.
This closes the bounded evidence/interface package, not the listing, rental,
remaining installation acceptance, or overall Host Docs project.

## Actual outcome

At **2026-09-09 05:27:29 UTC**, one Host API request attempted the user-approved
listing: GPU3/GPU-hour, bid0.30/GPU-hour, storage0.50/GB-month, upload/download
1/GB each, prepaid discount0, minimum GPU1, no extra volume offer, fixed expiry
1789423200. [Exact request](listing-request-01.json).

The API returned **400 price_out_of_bounds**, specifically:
`Price price_inetu was out of bound 0.1 at value 1.3333333333333333`.
[Retained response](listing-response-01.json).

The separate owned-machine GET completed at **05:27:31 UTC** and confirms
**unlisted**, null listing prices and zero running/resident rentals.
[Readback](host-read-after-01.json) and
[comparison against intended terms](listing-readback-verification-01.json).
No changed-price retry, client instance, rental lifecycle, reboot, other-host
change or customer workload operation occurred. No cleanup was required because
no new instance was created. Billing was not independently audited.

The CLI passes the requested network prices unchanged. Neither the inspected
CLI nor schema establishes the server's conversion or valid host-input maximum.
Do **not** use0.1 as an inferred replacement. The client-facing pricing table
states units, not that1/GB is accepted; this failure does not establish an
incorrect documentation claim. [Exact source capture](source-contract-01.json).
This was a direct API request equivalent to the inspected CLI body, not execution
of `vastai list machine`; no CLI-command PASS is claimed.

## Frozen-plan accounting

| Check | Result | Retained evidence and remaining action |
| --- | --- | --- |
| LR-01 source contract | Listing portion PASS; rental portion UNVALIDATED | source-contract-01.json matches the source SHA pinned before the request. Rental execution contract is not finalized without a valid offer. |
| LR-02 readiness | PASS | preflight02/03 and host-read02/03; seven host and seven listing guards passed. Default-sandbox preflight01 remains BLOCKED history. |
| LR-03 approved listing and readback | FAIL | Exact approved input rejected; readback confirms intended listing state not achieved. Do not overwrite or reclassify the failed attempt. |
| LR-04 client identity and exact offer | BLOCKED | No API-accepted listing at approved prices. No client credential used or rental offer selected in this attempt. |
| LR-05 exact rental claim inventory | UNVALIDATED | claim-impact-01.json retains eight exact reviewed/proposed occurrences. Final offer/instance-bound inventory was not frozen; no runtime proof inferred. |
| LR-06 representative rental and cleanup | BLOCKED | Requires LR-03/04/05. No instance created; one-GPU/20-minute/USD5 ceiling remains conditional, not executed. |
| LR-07 evidence and reviewer integration | PASS for bounded package | Three append-only context artifacts, original five selected checks preserved, unchanged canonical model, tested localhost and offline controls. This is not product acceptance. |

## Reviewer and repository retests

- [Full suite retest](reviewer-tests-03.json): **73/73 PASS**. The sandbox socket failures in tests01 and the new test-variable defect in tests01/02 are preserved in the [correction log](correction-log.md).
- [Actual browser context checks](intake-browser-01.json): five exact passages, **84 contextual evidence-link responses**, selected observations and wrong-claim404 rejection. Offline HTML has no horizontal overflow and **zero external resource requests**. Root visually inspected both retained screenshots.
- [Page-control checks](page-controls-01.json): **84/84** exact passage/status controls across Installing Host Software and First24Hours.
- [Export check](export-check-01.json): deterministic shareable HTML includes **155 embedded files** and all **2,005 claims**. It shows the rejected listing and unchanged installation findings. The current loopback proxy was restarted to load the updated intake; port3000 and reviewer feedback were left untouched.
- The canonical model is unchanged: **189 PASS /151 FAIL /22 BLOCKED /4 N/A /1,639 UNVALIDATED**. No claim receives evidence credit from this failed listing. There are44 primary Host pages plus18 CLI and15 SDK support layers.
- [Model check](model-check-01.json), [whitespace check](whitespace-01.json), and [final integrity](final-integrity-01.json) retain their actual outcomes. Prior63 sealed installation artifacts, pinned intake artifacts, HEAD and staged content are verified separately by the integrity check.
- [Optional graph refresh](graph-update-01.json) failed closed: the node-loss guard refused replacement. No force overwrite occurred. Graph maintenance remains local work, not an external evidence blocker and not completed proof.

## Next decision and separate workstreams

The host owner must approve revised bandwidth prices that the API accepts;
retain all other approved terms and the fixed expiry. A new guarded attempt must
independently read back all prices before any bounded client rental.

1. [Runtime/operator register](runtime-operator-register.md): accepted-listing prerequisite, conditional rental, exact claim impact and cleanup bounds.
2. [Source-owner/Product/Finance/Legal register](source-owner-register.md): obtain backend bounds/conversion evidence before documenting a numeric rule; no invented commercial/legal authority or external completion.

Historical attempts are preserved. No push, Jira post, merge, human acceptance,
new project-complete declaration or external workstream completion occurred.
