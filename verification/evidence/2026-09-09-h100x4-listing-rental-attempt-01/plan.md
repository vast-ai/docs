# Listing and bounded client rental — frozen initial scope

Target: owned machine **150296**, four H100 PCIe GPUs, the previously pinned new-host SSH endpoint. PR185 / CON-1518. Mode: PLAN_AND_EXECUTE. The exact initial tree/index is in baseline.json; earlier attempts are immutable history.

## Authority and limits

The user confirmed upload and download at **$1/GB each**, prepaid discounts disabled, and explicitly requested listing followed by a useful client-account rental. Other approved terms remain **$3/GPU-hour**, **$0.30/GPU-hour minimum bid**, **$0.50/GB-month storage**, fixed expiry **1789423200**, **vol_size=0**. Use min_chunk=1 to permit the smallest representative rental. No rolling duration or separate volume offer.

This authorizes one small representative rental, not an unlimited test campaign. Agent-imposed ceiling: **one GPU, at most 20 minutes from creation, at most $5 including compute/storage/bandwidth**. Require read-back prices that fit the bound, a cached image or bounded download, and reliable cleanup before creation. No full self-test, bandwidth/speed test, bulk transfer, package upgrade, driver work, router changes, reboot, other-host change, or interference with third-party instances. If a safe bounded rental cannot be established, retain the reason without renting.

Use only the exact previously authorized Host and client credential-store entries; secrets stay in memory and must not enter argv, source, logs or public evidence. Host SSH remains strictly pinned. Client access is limited to this attempt's newly created instance. Destroy that instance at completion/failure/deadline; never destroy existing client resources. No push, merge, Jira post or human acceptance.

## Initial inventory

| ID | Basis and method | Required observation and evidence | Stop condition / limitation |
| --- | --- | --- | --- |
| LR-01 | Verify canonical local CLI listing/search/create/lifecycle implementation and source revision | Retain selected source lines, hashes, request/response contract and exact intended commands | Documentation is the claim, not self-proof; no Product/Finance/Legal authority inferred |
| LR-02 | Strict SSH + owned Host API read immediately before listing | Identity150296/four H100s, service state, occupancy and no third-party workload; retain inputs/output/UTC | No host mutation to manufacture readiness; a conflicting identity or occupancy stops further workload actions |
| LR-03 | One Host API listing mutation using all approved fields, then independent owned-machine GET | Listed true; GPU/bid/storage/upload/download/discount/expiry/min-chunk/volume fields match exactly | Unknown response requires readback reconciliation before retry; do not extend expiry or silently accept mismatched terms |
| LR-04 | Client account read + exact-machine offer search | Distinct client/Host identities, funded/authorized account, exact candidate offer prices and GPU count | No broad market fallback or another machine; lack of permissions/offer/budget blocks rental only |
| LR-05 | Freeze exact claim-level rental inventory after read-only discovery and before creation | Exact page/heading/claim, required evidence lane, version/image, command and expected result | Static or owner-governed claims do not become runtime PASS merely because a rental works |
| LR-06 | If LR-04/05 pass: one scoped rental, connection, tiny deterministic GPU result and own-instance lifecycle where relevant | Offer→contract→machine linkage, timestamps, selected output, cost observations and cleanup receipt | At most one GPU/20min/$5, no stress/bulk traffic; stop/restart only this task-created instance |
| LR-07 | Evidence reconciliation + reviewer/HTML retest | Original failures preserved, new retests linked, only exact claim-suitable changes applied; actual panel on4000 updated | Report remaining runtime and owner/source work separately; no whole-workflow or project acceptance inferred |

Statuses: PASS requires direct suitable retained evidence. A confirmed mismatch is FAIL. Missing evidence alone is UNVALIDATED. A specific unavailable permission/input/environment/authorization is BLOCKED. Newly discovered checks are appended with rationale before their execution; expectations are not rewritten to fit observations.

The source graph is orientation only. Its previous refresh failed closed; canonical files/API/retained output remain the evidence sources.
