# Dogfood Report: Host Docs P1 rendered-context review

| Field | Value |
|---|---|
| Date | 2026-08-30 |
| App URL | `http://127.0.0.1:4000` |
| Session | `host-docs-p1-rendered` |
| Scope | 39 primary Host routes, 33 generated wrapper routes, notifications import context, and review dashboard |

## Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 0 |
| **Total** | **2** |

Status split: **1 open** (ISSUE-001) and **1 fixed with linked retest**
(ISSUE-002). The severity table is a historical finding count, not an open-defect count.

Rendered route coverage: **39/39 primary Host pages**, **18/18 Host CLI wrappers**,
**15/15 Host SDK wrappers**, **1/1 review dashboard**, and **3/3 fail-closed internal-path
probes**. All retained page-error files are empty. Because the browser tool reports
session history cumulatively, console files contain repeated warning-level
`Connected to Socket.io` development-log entries; these indicate the local preview
connection and are not connection-failure warnings. No other console entry was observed.
The Pricing Your Listing snapshot exposes the labelled image
`Machine listing and pricing controls`; the previously reported missing-image symptom
did not reproduce.

## Issues

### ISSUE-001: Section headings expose the anchor control in their accessible name

| Field | Value |
|---|---|
| Severity | medium |
| Category | accessibility |
| URL | `http://127.0.0.1:4000/host/pricing-your-listing` |
| Repro Video | N/A — static accessibility-tree issue |
| Status | Open |

**Description**

The rendered accessibility tree announces section headings as, for example,
“Navigate to header Before You Price” and “Navigate to header Listing Controls.” The
visible heading is only “Before You Price” or “Listing Controls.” The anchor control's
label should not become part of the heading's accessible name. The same pattern reproduced
on Hosting Overview, so it is shared page chrome rather than a one-page content typo.

**Repro Steps**

1. Navigate to the Pricing Your Listing page and inspect a section heading with a screen
   reader or browser accessibility tree.
2. Observe that the H2 accessible name is prefixed with “Navigate to header.” The annotated
   rendered page is retained in
   [screenshots/pricing-your-listing.png](screenshots/pricing-your-listing.png), and the
   underlying accessibility snapshot is retained in
   [host-pricing-your-listing-snapshot.txt](host-pricing-your-listing-snapshot.txt).

### ISSUE-002: Review dashboard exposes the workstation's absolute path

| Field | Value |
|---|---|
| Severity | medium |
| Category | privacy / information exposure |
| URL | `http://127.0.0.1:4000/__review__/` |
| Repro Video | N/A — static rendered-text issue |
| Status | Fixed and render-retested in this worktree |

**Description**

The dashboard tells reviewers that feedback files live in an absolute workstation path,
including the local user name and directory layout. The reviewer-facing projection should
use a repository-relative label such as `review-feedback/`; absolute local paths belong only
in restricted execution evidence. Loopback binding limits network exposure but does not make
the path appropriate for screenshots, exports, or an independently shared review package.

**Repro Steps**

1. Navigate to the review dashboard.
2. Read the sentence immediately below the page title.
3. Observe the absolute workstation feedback path. The original snapshot and annotated
   capture are retained only in the restricted evidence area, with SHA-256 digests
   `53fb86d91ea288fe8e30bfcba6a5920b04844901bfa97ce30026b6e536361d5e`
   and `993e148e45fbf72bb9638fa9283843c752e6170db626d008bd3bd7ba2a1180d1`;
   they are intentionally absent from this public projection.

**Retest**

The dashboard now renders only the sanitized repository-relative default
`review-feedback/`. The focused reviewer-interface suite passes 10/10, including a
fail-closed non-loopback-bind check; the replacement
page has empty browser and console error output, and the annotated retest is retained in
[screenshots/retest-review-dashboard.png](screenshots/retest-review-dashboard.png). The
test transcript is retained in [review-context-test.txt](review-context-test.txt).

## Security and interaction observations

- The exact directory-root requests `verification/`, `graphify-out/`, and
  `review-feedback/` each rendered `Page Not Found`; their complete
  open/wait/snapshot/screenshot/error/console records are retained. These are three point
  probes only. They do not establish a broader traversal, nested-file, normalization, or
  raw-file access boundary.
- The review overlay and page-note form were exercised as a contextual point observation,
  but no interaction transcript was retained in this package; that interaction is not
  counted as validated evidence here.
- A 390-pixel annotated capture is retained in
  [screenshots/mobile-hosting-overview.png](screenshots/mobile-hosting-overview.png). It is
  visual-only; no separate mobile error/console record was retained, so no mobile runtime
  PASS is assigned.
- Loopback-only configuration and the review server's non-loopback rejection are covered
  by source binding and the retained test transcript. No OS-level listener listing is
  retained here, so historical runtime listener state is not independently claimed.
- Exact source, worktree-overlay, capture-tool, and sanitized environment identities are
  recorded in [rendered-context-binding.json](rendered-context-binding.json).
