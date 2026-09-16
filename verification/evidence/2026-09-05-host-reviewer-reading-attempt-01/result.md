# Host reviewer reading experience — attempt 01

Jira CON-1518 · Host Docs PR #185 · 2026-09-05

## Plan and baseline

Mode: PLAN_AND_EXECUTE. Scope: the local review proxy and its presentation of
existing evidence. The customer documentation and evidence verdicts are not
being changed. Requirement authority: the reviewer's reported inability to
connect a V&V ID to customer-visible wording, supplied in this conversation.

Pre-edit HEAD: `3e1e30e2221b65d7ce1e901d9ae305f63af5b64b`.
Pre-edit tree: `961d5836c517408495926ac70c7283e4fc6db15e`.
Tracked worktree and index were clean. The existing untracked local planning,
graph, dependency, feedback, candidate-script, and old evidence files were
present and remain outside this change. Exact path listing: [baseline.txt](baseline.txt).

Retained original defect: `MCL-f9f3ebb712a5588d` is an Introduction claim:
“Verification is automated. There is no manual review step for ordinary host
verification.” The user was reading Verification Requirements, while the
sidebar showed a page-wide list headed by opaque IDs, raw evidence-type enums,
and accounting history. A heading link did not identify or highlight the exact
wording. This is a reviewer-interface FAIL, not proof that the product claim
is false. Its existing UNVALIDATED result remains unchanged.

## Acceptance inventory

| ID | Requirement and method | Expected result |
|---|---|---|
| READ-01 | Browser: reported verification-stages introduction claim | Quote is the label; Show on page highlights that exact introduction text even when starting at another section. |
| READ-02 | Browser: select Verification Requirements | Only that section's claims appear; whole-page coverage and other sections remain accessible. |
| READ-03 | Inspect and browser: proof, citations, and missing inputs | Plain-language status and next action; supporting sources/results separate from accounting and links in the documentation. No status promotion. |
| READ-04 | Browser: representative code/list/link/table claims and ambiguous/missing wording | Correct exact match or an explicit unavailable/ambiguous message; no silent wrong highlight. |
| READ-05 | Browser: keyboard, narrow viewport, navigation, and client view | Controls are usable; focus and feedback survive; only the review proxy adds review UI. |
| READ-06 | Automated reviewer regression and independent review | Existing evidence integrity and feedback protections pass; historical records still accessible. |

Evidence: retained browser observations/screenshots, test output, source hashes,
and this new result. PASS is limited to observed reviewer behavior. Missing
observation is UNVALIDATED; a check prevented by a specific missing prerequisite
is BLOCKED. No Host/API credentials, paid work, privileged commands, or product
runtime operations are in scope. No human acceptance is recorded.

## Result and retained observations

The reviewer presentation is corrected. Customer MDX, material-claim statuses,
evidence manifests, and historical attempts are unchanged. This result is
limited to the reviewer interface; it does not accept the Host documentation
or resolve its Product/Finance/Legal/runtime workstreams.

| Check | Result | Observation and limits |
|---|---|---|
| READ-01 | PASS | The reported ID is displayed as the introductory sentence. Clicking Show on page highlights precisely that sentence. |
| READ-02 | PASS | The historical requirements anchor selects Verification Requirements and its 5 statements. All 37 remain accessible. Filtering/hash navigation clears the previous highlight. |
| READ-03 | PASS | Proof, command definitions, command results, citations, and accounting remain distinct. A missing required citation stays FAIL. The reported introduction stays UNVALIDATED. Supporting-evidence URLs reject unrelated claim bindings. |
| READ-04 | PASS within sample | All 37 Verification Stages statements and all 3 Self-Test command forms locate correctly. Duplicate/missing text and duplicate/missing headings reject matching. Combined passages give an explicit section/source-lines fallback. |
| READ-05 | UNVALIDATED for full keyboard/screen-reader use | Checked native control labels, focus, live-region roles, 1600×1000 and 390×844 rendering, and mobile panel-close/return behavior. Client HTML has no overlay. Native select keyboard changes and actual screen-reader speech remain UNVALIDATED; see limits below. |
| READ-06 | PASS | 26/26 reviewer tests, exit 0; syntax and whitespace checks pass. An independent agent reviewed evidence integrity and focus behavior; its six findings were corrected. |

- [Browser observations and exact DOM actions](browser-checks.json)
- [Desktop introduction screenshot](reader-introduction.png)
- [Mobile located-text screenshot](reader-mobile.png)
- [Retained reviewer regression output](reviewer-tests.txt)

The full regression suite executed `npm run test-review-context`; the author
of the two new API regression tests ran it independently. npm exit status was
captured as `PIPESTATUS[0]=0`, not inferred from the log-writing process.
The primary agent implemented the UI and performed the browser checks. The
independent code review was read-only and did not constitute human acceptance.

## Corrections and preserved retests

| Original observed failure | Correction | Later result |
|---|---|---|
| Original manager-facing UI led with opaque IDs and accounting history. | Quote-first cards, section filtering, exact-wording navigation, simple proof/status/next action, collapsed audit history. | READ-01–03 passed. |
| Plain self-test also matched the prefix of the command with bundle options. | Require complete rendered code-block equality for fenced claims. | All 3 command forms highlight their own code blocks. |
| A hidden duplicate could be included by a range endpoint at a text-node boundary. | Bind exact start/end DOM nodes and offsets. | Hidden duplicate excluded; visible duplicate rejected. |
| Removing Highlight support left the old highlight present. | Clear old highlights separately from constructor availability; disclose unsupported highlighting. | No retained highlight; accurate located-only message. |
| Independent review found stale card selection on failed matching and stale highlights after hash navigation. | One focus-clearing function on match, filter, hash, and route changes. | Adverse/navigation retests show zero stale selections/highlights. |
| Independent review found a dead navigation enum, introduction link wording, count grammar, and hidden narrow-screen announcement. | Correct enum and labels; announce narrow-screen success in an outside-panel status region. | Static review passed; mobile focus returns to Review and status text remains outside the hidden panel. |
| Initial added regression assertion expected multiline wording. | Test expectation corrected to the inventory's existing single-line normalization. | 26/26 passed; original 25/26 is retained here. |
| Browser harness assumed paragraphs were p elements, used a CORS-restricted cross-port fetch, and used relative screenshot paths. | Target actual rendered elements; use Node for the separate customer HTML response; use absolute screenshot destinations. | Each corrected check completed; original errors remain in browser-checks.json. |

## Target identity and limitations

Local date: 2026-09-05; final checks span the preceding UTC evening.
Base commit is recorded above; the following changed files identify the tested
working tree without attributing these results to the unchanged base commit:

| File | SHA-256 |
|---|---|
| review-server.mjs | `1a52e7965b3cbf7de4e3107ee65cfd867141baf84788e3988b0575e6b3e06936` |
| scripts/review-context.test.mjs | `ebfc8b0d5ca76511b767594b0252ee24c1105462baa0b474ef0c175b095b521f` |
| REVIEW-TRACEABILITY.md | `2d62cfdee1dd2ad8bab609cc7541a00666b3594a517527e88deb5107fcecb7e3` |
| reviewer-tests.txt | `d7e1b6ce6c68175bc89a0cf94d041bf9ff302d0f6aad6c8a27e8956ddd989a80` |

Browser coverage is complete for the 37 statements on the reported page, plus
the stated samples; it is not an all-page rendered matching claim. For
non-contiguous source spans, reviewers must use the section and source lines.
The automation tool's key operations did not change the native select value
despite focus; selection and button activation worked through its select/click
operations. A human keyboard/screen-reader usability check is the exact next
action for that unvalidated portion. No new permission blocker is inferred.

No credentialed API, paid, WAN, privileged, destructive, workload, publication,
Jira-posting, or merge operation ran. Existing product/source-owner blocker
registers remain applicable. A manager still needs to assess the new reading
experience; no approval is recorded here.
