# Host Docs — approved SSH/Jupyter and self-test follow-up

PR185 / CON-1518 · 9 September 2026 · machine **150296** only. This bounded follow-up records completed operational work and six exact reviewer bindings. It is not a complete Jupyter/self-test workflow, full Host acceptance, or permission to merge. Final byte-current validation is recorded separately below.

## Observed result

- **SSH passed.** A real direct SSH command returned the expected output using the registered key and strict host-key verification.
- **Jupyter service responded; browser completion is blocked.** Authenticated HTTPS status and page requests returned 200 using the official CA scoped to the test process. The isolated browser stopped at `ERR_CERT_AUTHORITY_INVALID`; browser/kernel success is not claimed.
- **Normal self-test stopped before renting.** Advertised reliability was **85.1%** (requires **>90%**) and upload **221.1 Mb/s** (requires **500 Mb/s**). The actual failure support bundle was created. No requirements bypass, paid self-test or self-test image launch occurred.
- **Cleanup passed; no reboot.** Test instance **50386523** was destroyed after about **8m22s**. Independent absence and post-cleanup idle/boot observations are retained. The roughly **$0.40** immediate account-wide credit difference is not a settled or instance-attributable bill.

Read the [exact operational observations and limitations](operations-result-01.md), [19 retained boundary/history checks](operational-audit-01.json), and [independent operational review](independent-operational-review-01.md). All 2,027 pre-existing evidence artifacts and the staged diff are unchanged. Only macOS client execution over LAN/VPN and the named Linux host were observed; no independent WAN or other client-platform PASS is implied.

## Exact reviewer work

| Exact page / heading / statement | Current outcome and bound proof |
| --- | --- |
| First 24 Hours / Test Like A Client — corrected `search offers` command | **PASS**, bounded to the real client query and canonical CLI signature. |
| First 24 Hours / Test Like A Client — SSH works | **PASS**, actual nonce output on the identified rental. |
| First 24 Hours / Test Like A Client — Jupyter opens | **BLOCKED**, isolated browser lacks the required certificate trust. Successful authenticated service responses remain partial evidence. |
| First 24 Hours / Test Like A Client — ports / connection check | **UNVALIDATED**, only the observed SSH/Jupyter endpoints were checked; arbitrary port and independent WAN coverage are not established. |
| First 24 Hours / Test Like A Client — compound destroy / troubleshooting statement | **UNVALIDATED**, cleanup is proved; conditional troubleshooting is not. |
| How to Self-Test / Run The Test — command with `--support-bundle-dir` | **BLOCKED**, actual preflight requirements prevent the complete diagnostic. Failure-bundle creation is separately retained, not relabelled full self-test success. |

The [exact six-claim delta](claim-delta-02.json) preserves **1,999 other claim records**, every procedure/support-layer record, and all **149 required-citation FAILs**. Three connection-check taxonomies were explicitly corrected from implementation-only to runtime observation; their complete prior records remain hash-pinned. Original search FAIL and source-transition links remain visible. Documentation wording identifies the claim and is never used as its own proof.

Current totals: **194 PASS / 149 FAIL / 23 BLOCKED / 4 N/A / 1,635 UNVALIDATED** across 2,005 claims, 44 primary Host pages, 112 procedures and 1,060 nodes. The 18 CLI and 15 SDK wrappers remain support layers. The additional BLOCKED status names an observed browser prerequisite, not a newly demonstrated product defect. The citation filter remains separate and shows 149 occurrences across 24 pages.

## Repository and reviewer validation

The [failure/correction chain](reviewer-integration-corrections-01.md) preserves unsuccessful collector, importer, historical-fixture and report-generation attempts. The historical transition tests still compare all 2,003 original unaffected records exactly; an isolated worker's seven-ID drift exception was not adopted. No product verdict is changed merely to make a test pass.

Final validation records are deliberately outside the embedded HTML input set to avoid a circular hash dependency:

- [186-test Python suite](python-closeout-04.json) and [97-test JavaScript suite](reviewer-closeout-04.json), local macOS repository/fixture checks.
- [Deterministic current model](generator-closeout-02.json) and [deterministic HTML](html-closeout-01.json).
- [Final browser check](browser-closeout-04.json): 44 reviewer API contexts, six exact cards and their 24 contextual proof links, six offline proof dialogs, the 149-citation filter, and no remote offline resources. [All 88 passage/section/status controls on the two affected pages](passage-browser-01.json) were separately checked. This is not a new all-page visual audit or full-site accessibility PASS.
- [63 focused CLI unit checks](cli-focused-static-02.json) are narrow source-only tests; [full-scope collection was unavailable](cli-focused-static-scope-01.md), so no full CLI-suite or cross-platform PASS is claimed.
- [Final AST-only navigation refresh](graph-scoped-result-03.json) preserves unrelated graph identities; it is not implementation/runtime proof.
- [Final exact-secret sanitation](public-final-sanitation-01.json) checks the named Host/client keys and task Jupyter token against this public attempt and report. Private raw rows and bundles are not published.

The [final source/artifact seal](final-integrity-01.json) is produced only after the required final checks succeed against the final bytes. It verifies all 2,027 pre-existing evidence artifacts, the original staged diff and HEAD remain unchanged, and excludes itself. Earlier successful checks are retained but do not substitute for this final gate. Source revision remains `bfa926c9421521767fa7411718bd31ea38b38528` plus the explicitly hashed dirty working tree; remote CI does not cover these edits.

## Work that remains open

1. [Runtime/operator register](runtime-operator-register.md): browser trust setup; reported reliability/upload requirements; funded Host context, a fresh idle window and an approved outside-LAN origin before a complete normal self-test.
2. [Source-owner/citation and review register](source-owner-register.md): suitable authoritative citations and owner review. Runtime success does not establish contract, pricing, policy, account or legal authority.

No new commit, push, merge, Jira post or human acceptance is recorded by this follow-up.
