# Six published-rule findings resolved

10 September 2026 · CON-1518 · Host Docs PR #185 · local correction.

Six statements in **Workload Policy / Restricted Activity** now cite the
applicable published Terms. They move from missing citation (FAIL) to supported
within the cited rule's scope (PASS). Missing-citation findings fall from
**47 to 41**. The current inventory remains 44 primary Host pages and 2,013
claims: **233 PASS / 41 FAIL / 23 BLOCKED / 13 N/A / 1,703 UNVALIDATED**.
The other 2,007 claim records and all 33 CLI/SDK support layers are unchanged.

## What supports these findings

The independent source is the official [Vast Terms](https://vast.ai/terms),
version **10 November 2025**, captured **10 September 2026 at 16:55:56 UTC**.
The [retained capture](terms-source-01.json) records the URL, HTTP 200 response,
version, section/item text and fingerprints. Whole capture SHA-256:
`936cc633ff36966ade3b063ee8eaf6bdd61cb9fd9d2f79201b03c9d5fbb84c38`.
Existing independent Hosting Agreement captures remain bound separately.

| Statement | Exact claim | Source and limit |
| --- | --- | --- |
| The Terms list prohibited activity | `MCL-99ca28f707d5966a` | Prohibited Activities introduction; a published rule, not observed enforcement. |
| Illegal or abusive activity | `MCL-2c3f7082e2c7fdf2` | Prohibited Activities 3, 13, 14, 21; retains the knowingly-qualified content restriction. |
| Malware, spam or interference | `MCL-c4c4bfc59eb7b49f` | Prohibited Activities 5, 12, 20; Website/network/Services scope. The Provider-specific Agreement clause remains separate. |
| Intellectual-property concerns | `MCL-399798a3c4946b5f` | Prohibited Activities 15; Agreement Operation and Maintenance separately supports the renter-data restriction. |
| Export-controlled or sanctioned use | `MCL-633317ca7ebecfef` | Export Compliance; distinguishes prohibited destinations/people, restricted end uses and required government authorization. |
| Cryptocurrency mining | `MCL-fe3eccd1cd40b4bd` | Prohibited Activities 22; retains credit-card-purchased credits and Company/Provider resources. No blanket ban or permission for other payment methods is inferred. |

See the [plain source guide](source-guide.md) and
[customer-page passage](http://127.0.0.1:4000/host/workload-policy#restricted-activity).
The official page has no section anchors, so links use its real URL and name
the clause. The reviewer opens the retained exact excerpt with the current
passage, readable section/item label, source version and limits.

The Terms establish these published rules. They do not prove technical
enforcement, runtime compliance, account acceptance or a Host monitoring or
escalation workflow. Unsupported escalation wording was not carried into these
six summaries. The already-supported platform-abuse row is unchanged.

## Repository and reviewer checks

- [Exact baseline](baseline-01.json): branch `CON-1584-host-cli-api-sdk`, HEAD
  `4fa6fbb53f1b547f36652bff32a8133bab387f33`, 4,217 Git-visible files and exact
  dirty/staged state recorded before edits.
- [Source integrity](source-integrity-01.json): official origin, version,
  retained clause text, scope conditions and absence of invented anchors checked.
- [Independent projection](integrity-03.json): six exact status/source changes;
  2,007 other claim records, 33 support layers, HEAD/staged diff and all 3,115
  prior evidence artifacts unchanged.
- [Python suite](python-full-02.json): 226 tests pass.
- [Final JavaScript suite](javascript-full-03.json): the frozen-source run
  records the complete local reviewer suite, including the Terms and historical
  predecessor guards. It runs after report generation, with no concurrent
  report changes.
- [Model/source gate](model-check-01.json): all 44 primary routes and 33 support
  layers match their current sources.
- [Negative binding and freshness guards](freshness-guards-01.json): eight
  tests pass. Missing claims/references, altered excerpts/spans, source drift
  and unclaimed edits fail closed; every returned artifact fingerprint matches
  its actual current or retained historical path.
- [Localhost browser retest](browser-final-02/summary.json): all 44 pages and
  2,013 claim cards pass; 1,994 exact highlights and 19 explicit privacy-masked
  section fallbacks. All 45 Workload Policy passages locate exactly.
- [Offline HTML checks](checks-01.json): all 15 groups pass, including exact
  excerpt selection, local setup instructions, filters, source links, safe
  controls and 390px mobile layout. The final report/date refresh is covered by
  [the final offline retest](checks-02.json) and
  [deterministic export check](export-check-03.json).
- [Derived graph/source index](current-derived-index-01.json): refreshed all
  2,013 current claim links and preserved unowned graph records. The AST update
  reports unsupported document extraction and skips the oversized visualization;
  this is navigation, not product proof.

The [construction findings and retests](candidate-findings-01.md) retain the
initial invocation/fixture/freshness failures. They are not displayed as the
current policy finding. No earlier attempt or failure is overwritten.

## Remaining work and boundaries

The [runtime/operator register](../../current-runtime-operator-blockers.md) and
[source/owner register](../../current-source-owner-blockers.md) remain separate
and open. Terms citations do not close account transitions, listing behaviour,
financial guarantees or operational checks. Use existing applicable authority
first; seek owner confirmation only for a genuine gap or ambiguity.

The V&V source-binding method prevents circular proof: customer documentation
is the statement being reviewed; the model, registry and Graphify index record
the connection but are not independent authority. Reader wording is shortened
without dropping source conditions or limitations.

No new Host/API/SSH access, credential use, rental, privileged operation,
reboot, human acknowledgement, acceptance, commit, push, merge or Jira post
occurred. This is not a full Host-readiness or external-workstream completion.
