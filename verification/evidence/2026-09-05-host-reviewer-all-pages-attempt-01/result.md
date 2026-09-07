# Host reviewer reading view — all pages, attempt 01

CON-1518 · PR #185 · PLAN_AND_EXECUTE · local date 2026-09-05

## Plan and baseline

Extend the readable review experience to all 40 primary Host pages, including
Volume Offers and the generated Self-Test Reference. The 18 CLI and 15 SDK
wrappers remain central-reference support layers. Authority for the UI change:
the user's request to apply the preceding quote-first review experience to the
other Host pages. This checks reviewer navigation, not the truth of Host claims.

Starting commit: `3e1e30e2221b65d7ce1e901d9ae305f63af5b64b`. The index is clean.
The tracked working tree already contains the preceding authorized changes to
`review-server.mjs`, `scripts/review-context.test.mjs`, and
`REVIEW-TRACEABILITY.md` (422 insertions, 7 deletions). The prior untracked
planning, graph, dependencies, feedback, candidate scripts, old evidence, and
`2026-09-05-host-reviewer-reading-attempt-01` remain preserved. Per-run metadata
will retain Git status, source hashes, and the exact tested page inventory.

Acceptance inventory:

1. Every primary page displays readable wording, the unchanged evidence status,
   understandable proof/owner/action information, and collapsed audit history.
2. Every material claim can locate its actual rendered passage(s), or explicitly
   explains any unavailable passage. Source/claim mismatches must not invent a
   quotation or silently highlight an unrelated passage.
3. All section filters and page/heading/proof links keep their correct scope.
   Commands, tables, lists, generated content, and embedded components are covered.
4. The 33 support routes clearly point to their central references without
   claiming separate workflow validation.
5. Preserve all baseline failures and link fixes to new browser/API retests;
   maintain review feedback behavior, source/evidence integrity, and traceability.

Method: inventory-driven browser checks through isolated agent-browser sessions
on the local review proxy; independent code/API regression review; targeted
desktop/mobile inspection. Capture per-claim ranges and per-page results with
immutable attempt files. PASS means observed UI behavior met the specified
criterion. Missing observations are UNVALIDATED; a specific unavailable
prerequisite may be BLOCKED. Existing claim statuses are not changed by UI tests.

Only repository-local and loopback browser actions are authorized. No Host/API
credentials, paid, WAN, privileged, destructive, workload, publication, Jira,
or merge operations. Historical evidence and human acceptance remain unchanged.

## Execution and result

### Preserved baseline

The four `baseline/metadata-*.json` files retain the exact starting Git status,
inventory, runner and server hashes. All four runs report an unchanged source.
`review-server.mjs` SHA-256 was
`1a52e7965b3cbf7de4e3107ee65cfd867141baf84788e3988b0575e6b3e06936`.
All 40 pages rendered, exposing 1,687 material-claim cards. Every card preserved
its claim status; all page/heading links resolved. Exact passage location passed
for 1,539 claims and failed or explicitly fell back for 148. Three section filters
failed, all on Volume Offers (Identifiers And Values, Command Map, Shared Disk
Capacity). Per-claim observations, notices, source spans and selected ranges are
retained in the 40 page JSON files; per-shard totals are in `baseline/summary-*.json`.

The 148 non-locations comprise 41 combined-source fallbacks, 103 missing rendered
matches, and four ambiguity fallbacks. Their causes include semantic summaries
being presented as literal wording, Markdown/HTML/smart-punctuation differences,
shell pipes mistaken for table separators, duplicate source occurrences, and
intentionally sanitized examples. These are reviewer-navigation findings, not
new findings about Host product behavior.

### Correction and intermediate retest

The shared panel now uses literal passages from the existing hash-validated
source spans, separately labels the assertion being checked when it is a summary,
and supports multiple passage highlights and section memberships. Markdown
formatting is converted for display without changing literal shell pipelines.
Source occurrence ordinals disambiguate identical passages. Masked examples keep
an explicit section-link fallback rather than bypassing review-data sanitation.

`retest-01/` preserves the first six-page intermediate run (351 claims): 345
located, six did not; all filters, status comparisons and links passed. Two
remaining cases were sanitized examples; four exposed mixed prose/code spans
and smart-dash handling that needed another correction. This is an intermediate
target, not final-source evidence; the on-disk source changed during the run.

### Final result and reconciliation

The shared **reviewer presentation and navigation** change is complete within
the limits below. This is not a Host-docs semantic-readiness or acceptance claim.

Final server SHA-256:
`972a7be02697f90fbdcf52bc8054663affbf7515daf31c8261f2c09d141833f8`.
Runner SHA-256:
`98450124e3d807e6644cb1191ebae9f6ed4f902c4a4896156bc486644a32247f`.
Test-source SHA-256:
`6317d3f9b03c3fa9e60149b98c439b0a1655034fd865203ea081b5ea817d75d1`.

| Check | Observed result | Retained evidence |
| --- | --- | --- |
| All primary Host pages | 40/40 rendered the readable view; 1,687/1,687 claim cards accounted for | `final-browser-retest-02/metadata-0.json` through `metadata-3.json`, 40 per-page JSONs, four `summary-*.json` files |
| Passage location | 1,680 located; 7 explicit masked-section fallbacks; no unexplained non-locations | Same per-page records, including every claim ID, source passage, selected range, notice and section link |
| Source, filters, section links, card counts, history disclosure | All four shards exited 0, reported matching served identities and unchanged source, and passed their gates | Same four summaries |
| Central-reference support layers | 18 CLI + 15 SDK routes passed; central and bound evidence links returned 200; no independent workflow/command claim | `support-retest-02.json` |
| Review-context regression suite | 33/33 passed; syntax and diff checks passed; source/test/runner hashes unchanged | `final-validation.json` |
| Independent audit | Complete source/API inspection plus focused browser checks, including security and known scope limitations | `independent-source-binding-audit.md` |
| Desktop/mobile example | Bound Related Pages rows highlighted; mobile control closed the panel and retained the location notice | `visual-check.md` and its three screenshots |
| User's port 4000 | Restarted with the final source; strict package load passed; context and page returned successfully with the matching source header | `port-4000-refresh.json` |

All 1,687 current statuses match the preserved baseline: 167 PASS, 153 FAIL,
23 BLOCKED, and 1,344 UNVALIDATED. No status, historical attempt, or canonical
V&V binding was changed. Location is evaluated separately from claim truth:
the two known bare-option typography cases below are included in the 1,680
locations, but are **not** passes for exact CLI-token fidelity. The seven masked
fallbacks are **not** successful exact highlights. Source-derived excerpts can
omit blank lines and table scaffolding; `VOL-C35`'s table header is not selected.

The earlier `final-browser/` sweep was a full, passing intermediate run against
`1ac458…`, before the additional reader warnings and runner hardening. It is
preserved and superseded for final-target purposes by `final-browser-retest-02/`.
`support-final.json` preserves an expectation failure on all 33 routes: the first
probe incorrectly required the primary-page `.vv-technical` class on support
pages. Every other observed support assertion passed. The corrected probe checks
the actual adjacent `.vv-context` disclosure, retains its code, and passed all
33 routes in `support-retest-02.json`; no support status was changed to obtain it.

`source-passages-api-regression-attempt-01.md` retains the API test's original
expectation and source-drift failures and their retests. The main agent also
reran all 33 tests independently on the final source (`final-validation.json`).
The local AST-only `graphify update .` completed with 5,823 nodes and 7,049 edges;
it skipped oversized HTML visualization and reported 173 evidence/data files
without AST nodes. No semantic extraction or external API was run.

### Independent review findings and follow-up

- The original browser runner hashed the on-disk server but did not authenticate
  that identity against the running process. It also recorded, but did not reject,
  source drift. The corrected runner requires a startup source-hash header and
  fails on drift. `stale-server-rejection/` retains the observed rejection of the
  older process on port 4000 before any browser result was attributed to it.
- Seven passages are intentionally masked by the existing sanitizer, including
  overbroad matches on public documentation syntax. Sanitizer changes are outside
  this presentation correction: the reader marks masked copies and provides
  explicit section navigation. A masked section fallback is counted separately
  from a successful highlight, never as runtime or product proof.
- `VOL-C35` has an inherited incomplete source-location binding. Its link-check
  assertion covers both Related Pages and command-reference destinations, while
  its retained span only covers `host/volume-offers.mdx:111–118`. Command Map is
  at lines 97–109. The reader must expose that limit and link the extra section;
  it must not fabricate a broader retained binding. Canonical correction remains
  a documentation/V&V maintainer action: append a source-binding correction and
  retest, preserving the original span and attempt. This is not an external
  operator or Product/Finance/Legal blocker. The existing claim PASS is not
  revalidated by this navigation work.
- Two generated Self-Test Reference table cells render bare CLI flags with an
  em dash: `MCL-c99f9ecb5ea4e15a` (`--ignore-requirements`, line 155) and
  `MCL-22a1a520d989a59f` (`--debugging`, line 198). This is a confirmed rendered
  token-formatting defect, not merely missing evidence. Both cards now show a
  guarded **Page formatting issue** note and the correct literal option. A
  documentation/V&V maintainer must wrap these options in inline code in the
  authoritative generation path, regenerate source hashes/bindings while
  preserving this failure, and retest rendered token fidelity. The warning is
  a presentation mitigation, not a canonical documentation correction. The
  generic locator's prose matching is not a complete CLI-token-fidelity test.

The page-browser runner checks review action links, not every destination
asserted by a product/navigation claim. Accordingly `linksPass` in its output
means review-navigation links only. Existing canonical link-check evidence is
separate; these UI results must not be substituted for it.

## Scope limits and external work

These browser checks exercise the local review interface on macOS/Chromium,
not Host commands or platform runtime. They do not establish human usability
acceptance, screen-reader acceptance, Linux/Windows behavior, product authority,
or legal/financial approval. No material claim, command status, historical attempt,
source-authority binding or reviewer acceptance is promoted by this work.

The separate [runtime/operator register](../../runtime-operator-blockers.md) and
[Product/Finance/Legal/source-owner register](../../source-owner-blockers.md)
remain the handoff for external work; neither workstream is completed here.
The customer documentation served without the local review proxy is unchanged.
