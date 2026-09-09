# Repository-first result — PR185 / CON-1518

The bounded no-cost Host repository work is complete. Live SSH/Jupyter/self-test
qualification and PR merge are **not complete**. This attempt used no Host/API/SSH
or Keychain credentials, created no rental, changed no host or listing, and did
not commit, push, merge or record human acceptance.

## Scope and identity

Executed under vv-evidence PLAN_AND_EXECUTE; [initial plan](plan.md) and six
scope addenda precede the expanded checks. The initial plan's rounded minute
labels were corrected by [addendum 02](scope-addendum-02.md); each retained JSON's
actual start/finish timestamps are authoritative for execution timing.

HEAD remains bfa926c9421521767fa7411718bd31ea38b38528 on
CON-1584-host-cli-api-sdk. The private exact pre-action baseline captured 34,555
Git-visible paths at 2026-09-09T11:13:19.687Z, staged/unstaged binary diffs and
NUL status. The staged diff SHA256 remains
f59f3c12986c4a1750dbae920803828221b9f4d63b7104c5932e9b0ac5372803.

The current model is unchanged: **44 primary Host pages, 18 CLI and 15 SDK support
layers, 2,005 claims, 112 procedures and 1,060 nodes**. Claim statuses remain
**192 PASS / 149 FAIL / 22 BLOCKED / 4 N/A / 1,638 UNVALIDATED**. All 149 FAILs
are required-citation occurrences across 24 pages, not failed runtime checks.

## Corrected repository defects and proof

| Reviewed target | Change and retained retest | Limit |
| --- | --- | --- |
| Customer build / internal review records; .mintignore | Exact internal Markdown exclusions prevent traceability/evidence links becoming customer pages. [Route retest](internal-routes-retest-02.json) and [3 hygiene tests](publication-hygiene-final-02.json). | The intentional review-questions.mdx mirror remains available; its uppercase alias is not incorrectly reported as 404. Internal source/evidence stays in Git. |
| Git publication boundary / .gitignore | Dependencies, Python caches, .orchestra, graph output and local feedback are ignored. Same hygiene test verifies Host docs and evidence remain visible. | No existing tracked file or historical evidence was deleted/untracked. Ignore rules are not secret scanning. |
| API reference links / actual generated operations | New checker uses Mint's installed generator, docs.json, exact aliases and real local HTTP responses. [85 unique targets account for all 99 raw findings](generated-route-reconciliation-01.json); [10 adversarial regression tests](generated-route-regression-01.json). | Raw Mint link checker still returns nonzero for generated routes. Resolved only with independent generated-operation/title/path evidence; no blanket suppression or runtime API claim. |
| Dark-background text links / docs.json colors.light | #315FFF → #3F6DFF raises contrast 3.94 → 4.53:1. [Mint retest](mint-a11y-retest-01.json), [4 unit tests](theme-regression-retest-01.json), [actual rendered CSS token](rendered-theme-token-01.json). | Other palette/navigation values unchanged. 74 missing-alt findings in 19 non-Host files remain open; no full-site accessibility PASS. |
| Offline report / current result and historical evidence | The dated sealed claim-correction result is distinct from later repository work and earlier history; exact four local link/accessibility results are embedded; all claim verdicts and citation filters preserved. [94-test combined suite](reviewer-current-final-02.json), [deterministic export](html-current-final-02.json), [offline browser](report-browser-current-final-02.json). | New selected check records are not a signed artifact, customer behavior proof or owner approval. Report has 181 embedded files and no remote resources. |
| Navigation graph / 7 changed sources | Failed full refresh was preserved; [strict selected-source AST retest](graph-scoped-retest-02.json) and [identity accounting](graph-scoped-result-01.json) preserve 8,986 unrelated nodes and 11,596 unrelated edges. | AST navigation only. No semantic LLM extraction or source/claim promotion. HTML has no AST extraction; unrelated graph summaries were not regenerated. |

Original failures and every correction are joined in the
[failure/retest chain](failure-retest-chain.md). Four task-created worker
checkouts were archived, readback-verified and removed. Recovery archives remain
private under .orchestra/host-repository-live-merge-01/worker-archives/; no
pre-existing user or CLI checkout was removed.

## Executed coverage

- [183 Python tests](python-current-final-03.json) and [94 JavaScript tests](reviewer-current-final-02.json) pass. JavaScript count includes 21 HTML and 10 generated-route tests. These are local macOS repository/fixture tests, not Linux/Windows/live qualification.
- [Current generator](generator-current-final-01.json), [204 pinned CLI checks](cli-current-final-01.json), [inventory: 77 layers / 597 targets / 229 commands](inventory-current-final-01.json), [44-page persona checks](persona-baseline-01.json), [OpenAPI contract](openapi-contract-baseline-01.json) and [OpenAPI validation](openapi-validation-01.json) pass. Source/CLI parsing is not actual Host execution.
- [Six-page browser baseline](browser-baseline-01/summary.json) covers 266 exact-passage controls; [post-theme two-page retest](browser-theme-retest-01/summary.json) covers 106. These do not claim a new all-page visual audit.
- [Independent current API/preservation check](preservation-current-api-final-02.json) confirms all 44 Host reviewer contexts and 1,941 pre-existing evidence files unchanged, plus unchanged model, source-transition registry, server and staged diff. The 149 citation defects remain selectable on localhost:4000 and in the HTML report.
- [Closeout check](closeout-check-03.json) checks local report links, working/staged whitespace and selected credential patterns. The initial scan's exact synthetic sanitizer fixture is explicitly accounted for; no whole-file exclusion or exhaustive secret-audit claim is made.
- The final seal below records the exact final source identities and all artifacts. This is a dirty working-tree result, not remote CI coverage.

## Remaining work, not hidden by this result

1. [Runtime/operator register](runtime-operator-register.md): new bounded budget approval, fresh idle/owned-machine readback, compatible CLI/image, independent cleanup, then exact SSH/Jupyter and self-test observations. A healthy connection alone does not prove a compound troubleshooting claim.
2. [Product/Finance/Legal/source-owner register](source-owner-register.md): the 149 required citations and other missing implementation/owner authority remain unresolved. Documentation text is not its own proof.
3. Separate repository backlog: [74 missing-alt findings in 19 non-Host files](mint-a11y-retest-01.json). A docs maintainer can inspect those actual images, author meaningful descriptions and retest in a scoped follow-up. This is feasible no-cost work outside this Host batch, not an external blocker.
4. [PR readback](pr-metadata-final-01.json): OPEN, draft, MERGEABLE, REVIEW_REQUIRED, merge-state BLOCKED. The two green checks cover remote bfa926c from September 7, not current local edits. Required review, exact scoped commit/push and fresh CI must precede merge; unresolved citation risk needs accountable disposition, not invented acceptance.

Integrity: [final source/artifact manifest](final-integrity-01.json). The manifest
is created last and excludes itself; it establishes byte identity, not V&V
suitability or human acceptance. No external workstream is declared complete.
