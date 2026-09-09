# Shareable Host Docs HTML report — CON-1518 / PR #185

## Result

The [single-file HTML report](../../host-docs-review.html) is complete for its
presentation scope. It includes a short summary, priority decisions, the two
separate evidence workstreams, all 2,005 searchable/filterable claim occurrences,
exact page-source passages and 98 embedded source/evidence display files.

It also explains how to obtain the published PR, install its dependencies, run
the loopback preview and review proxy in two terminals, review page wording,
export feedback, troubleshoot ports, and stop the local services.

The GitHub PR read on 2026-09-08 returned OPEN / draft at
`bfa926c9421521767fa7411718bd31ea38b38528`. The report prominently warns that
the current local V&V update and HTML have not been pushed; a fresh published-PR
checkout does not yet reproduce this snapshot. Setup commands were inspected
against package.json, scripts/mint-dev-loopback.mjs, and review-server.mjs.
No fresh network clone/npm installation was executed for this export.

## Identity and verification

- HTML SHA-256: `a74ada444ceab688b709bf0bf41592176aa60203dc89451f232ab1a6bdb2efb8`.
- Input JSON SHA-256: `24492ac5b4c3059478d311c6d99733ebadad37255d0e570295c17605ab42f031`.
- [Export manifest](../../host-docs-review-export.json) records all 98 original
  and display hashes. Eleven claim displays and 13 source/evidence display files
  have conservative masking, explicitly labeled. Source line counts are preserved.
- [Final checks](checks-02.json): all 8 deterministic tests and 10 retained
  browser/check groups passed. The file was opened with a file URL and browser
  offline mode; no resource requests or page errors were observed.
- All 44 page filters and all 2,005 IDs were traversed through pagination. All
  status totals, both registers, search, empty state, owner/page filters and
  priority navigation were checked. All 26 unique claim-bound evidence records
  were opened with current claim context. Three representative page-passage
  dialogs (Self-Test, VMs and Verification Stages) were checked in the browser;
  all source spans and bound references were checked statically.
- Desktop 1440px and mobile 390px layouts had no horizontal overflow. Visible
  controls were checked for names; source dialog fit the mobile viewport.
  [Desktop](checks-02-desktop.png), [mobile](checks-02-mobile.png), and
  [localhost setup](local-setup.png) screenshots were retained and visually reviewed.
- Print preparation includes the entire filtered selection and restores screen
  pagination afterward. OS print-dialog behavior and PDF page layout were not tested.
- Independent read-only agent review found no blocking export defects. Its one
  copy ambiguity (“merged” might imply PR #185 was merged) was corrected to
  “current”; the unchanged test matrix passed again in checks-02.

The [first check pass](checks-01.json) and earlier screenshots remain available.
The capture-directory prerequisite error and read-only filename-glob error are
recorded in the [plan](plan.md). Checks-02 also strengthens the final error/network
assertion rather than merely recording its output. No earlier attempt was erased.

## Limits and preservation

No claim was promoted: 171 bounded PASS, 4 editorial NOT_APPLICABLE, 149 FAIL,
22 BLOCKED and 1,659 UNVALIDATED remain unchanged. The 1,830 unresolved occurrences
are not all blockers. Existing semantic, operator and accountable-owner work is
not complete; the documentation is not acceptance-ready.

The HTML bundles public retained records only, not the full raw archive or
restricted evidence referenced by them. Historical record totals/outcomes cannot
override current claim classifications. Documentation snapshots are claims under
review, not evidence of their own truth. External GitHub/Jira links and optional
live preview links need connectivity; nothing connects automatically.

At closeout the existing index SHA-256 remained
`f94031ce155dabaf4a0c8cf60f50f22c76d68a38209b3502ce535c93e157310b` and staged diff
SHA-256 remained `f59f3c12986c4a1750dbae920803828221b9f4d63b7104c5932e9b0ac5372803`.
The tracked unstaged diff stayed empty and the current input JSON hash was unchanged.
Previous source and sealed evidence were not rewritten. New export artifacts are
local and unstaged. The graph was refreshed AST-only (no LLM/API cost); it is not
evidence of product behavior.

No new Host/API/runtime operation, paid test, privilege change, publishing,
commit, push, Jira post, merge, owner confirmation or human acceptance occurred.
