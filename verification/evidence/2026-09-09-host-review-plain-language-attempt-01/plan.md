# Plain-language Host review

Scope: all 44 Host page claim cards, their shared live reviewer and standalone
HTML rendering. The claim model, client documentation, proof bindings and
statuses are unchanged. Preserve current source links, check results, concrete
blockers and limits. Show only current findings by default.

1. Capture the exact dirty tree and prior evidence hashes before task edits.
2. Replace repeated classification jargon with concise findings and next steps.
   Give the Setup Path account requirement an exact, bounded explanation; do
   not assert that Vast enforces an unverified requirement.
3. Share the display formatter between live and offline views. Hide unchanged
   audit wording in record details and suppress only equivalent summaries.
4. Test the formatter, regressions, exact passage links, both rendered views and
   model/evidence integrity. Refresh HTML and the local reviewer; update graph.

Success: a reader can identify the statement, what is missing and the next
check without understanding our classification system. No invented support,
status promotion, hidden blocker or lost proof link. No credentials or live
Host operations; no publishing, merging or acceptance.

Baseline: baseline-02.json contains HEAD, branch, exact Git status, staged and
unstaged diff hashes and hashes of all 3,900 Git-visible existing files.
Initial capture failed before writing a record because the existing diff
exceeded a 30 MB buffer (ENOBUFS). The buffer was increased and capture rerun;
no repository task edit preceded the successful baseline.

Checks: focused display/unit tests, existing reviewer/export tests, live
Quickstart and representative page checks, offline desktop/mobile checks,
unchanged model/authority/source/history hashes. These establish presentation
behavior only, not the truth of product statements or human acceptance.
