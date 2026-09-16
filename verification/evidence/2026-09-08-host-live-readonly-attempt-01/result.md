# Host Docs live read-only V&V — 8 September 2026

PR #185 / Jira CON-1518. **47 read-only checks completed**, not 47 claims closed: 20 unprivileged Linux Host subcommands, 21 canonical source-entry-point CLI runs on macOS, and six direct API GET requests. The original trust failures, runner failure and evidence corrections are retained.

## What this now supports

- Three exact GPU Market Metrics / API rows have bounded **PASS**: current snapshot, historical supply/demand/pricing response, and geography response. [Retained API checks](market-api-01.json) are independently bound to pinned CLI client code and OpenAPI schemas; they do not prove measurement accuracy, Finance policy, freshness or all access/filter rules.
- Hosting Overview / Introduction, `MCL-e12ac9f6be2ce502`, has a separate **product-description PASS** from dated official Vast publications. [Retained source capture](product-source-capture-02.json). A paid rental was not required for this general description. This is not renter execution, provisioning, GPU-health or cleanup proof. The original runtime-only classification remains in the additive registry.
- All 15 documented Market Metrics CLI examples ran, plus one additional raw filtered-location variant. These are invocation/rendering observations, not an automatic promotion of every surrounding claim.
- Host inventory, GPU enumeration, storage mount/options/capacity and service state were observed. XFS `prjquota` visibility does not prove enforcement; disabled/N/A ECC fields do not prove GPU health. Empty maintenance/reports validate only the empty branch.

Current inventory: 44 Host pages, 33 central-reference support layers, 2,005 material occurrences. **175 bounded PASS, 4 editorial N/A, 149 FAIL, 22 BLOCKED, 1,655 UNVALIDATED**; 1,826 unresolved. Only four claim statuses changed in this batch. The 20-occurrence supplemental map carries exact/partial execution context without changing other statuses.

## Read the proof next to the statement

[Exact check-to-claim map](check-to-claim-map.json) identifies each page, heading, literal, source hash, check, coverage limit and next action. The shareable HTML embeds these records and shows “What we actually tested” within each mapped claim, with a button for the exact check.

- [Linux Host checks](batch-b-execution-02.json): 20 subcommands; `/data0` absence was expected.
- [macOS CLI runs](batch-d-cli-execution-01.json) and [remaining CLI examples](batch-e-cli-execution-01.json).
- [CLI source/runner identity](batch-d-source-provenance.json).
- [Selected-machine / maintenance / reports API reads](machine-api-01.json).
- [VM source-access denial](vm-source-access-01.json): source inspection stopped at permission denial; no helper ran.
- [Runtime/operator register](runtime-operator-register.md) and [Product/Finance/Legal/source-owner register](source-owner-register.md) remain separate.

## Failures and retests preserved

- [Local runner setup failure](batch-b-local-failure-01.json) happened before SSH; Batch B execution-02 is the corrected run.
- [Identifier masking defect](sanitation-correction-01.json) and [sanitation retest](sanitation-retest-02.json): private UUID/FAT/LVM identifiers removed from the publication copy, original output digests retained.
- [Initial public-source matcher failure](product-source-capture-01.json) and [new retrieval/retest](product-source-capture-02.json): decode the HTML apostrophe entity, rather than pretending the first match passed.
- [Root span-binding regression failure](api-root-review-failure-01.json) and [unchanged negative-test retest](api-root-retest-02.json).
- Static historical evidence retains its original timestamp and bytes. Updating the live package must not rewrite a previous static attempt.

## Limits and remaining work

The client key's exact authorized location is still needed before client-role/account/offer checks. Paid or workload-changing tests require an agreed target, workload, spending/duration limit, monitoring and cleanup scope. The default SSH user cannot inspect the VM helper or the earlier H100 Docker socket; no sudo or alternative credential search was used.

Repository-local follow-up remains: formally adjudicate suitable command-level claims from the already retained evidence and continue source/citation work. Missing evidence alone is not a confirmed external blocker. This batch does not complete every Host workflow or the external owner registers.

Only the user-authorized local SSH trust entry persists. Task-only CLI placeholders/caches were removed ([Batch D cleanup](batch-d-cleanup.json), [Batch E cleanup](batch-e-cleanup.json)); normal CLI keys/configuration were not changed. No paid rental, self-test, Host installation/configuration, privileged command, renter-content inspection, push, post, merge or human acceptance occurred.
