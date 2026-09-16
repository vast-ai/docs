# Corrections and retained retests

1. Default SSH was denied before connection. Preserve preflight-01.json; scoped
   approved execution passed in preflight-02.json and fresh preflight-03.json.
2. The exact approved listing failed. Preserve request/response/readback01. No
   changed-price retry exists, so this live failure is not marked resolved.
3. Current reviewer wording still said bandwidth/discount choices were missing
   and no offer write had occurred. Append three pinned listing records to the
   five unchanged exact intake bindings; state that a request was rejected and
   no offer was published. Prior artifacts and selected checks remain intact.
   Export01/check01 and intake-browser01 retain actual projection/link retests.
4. reviewer-tests01:18/73 passed; local socket permissions prevented54 cases,
   and the new HTML assertion referenced undefined `report`. The scoped
   elevated reviewer-tests02 ran all cases:72/73 passed, preserving that one
   test defect. Correct the two assertions to the existing `payload` binding.
   reviewer-tests03 is the separate post-correction full-suite retest.
   Earlier recorder hashes cover product/reviewer inputs, not all test files;
   the final recorder additionally hashes all four test files before/after.
5. Preparation-tool limitations (not Host claim failures): memsearch could not
   acquire its sandbox-restricted database LOCK; no reset or rebuild occurred.
   Narrow path/glob orientation errors were corrected without secret discovery.
   These are reported from the tool transcript, not reconstructed executions.

No documentation command or canonical material-claim status was changed to
manufacture PASS. Listing rejection and interface regression statuses are
different evidence scopes.
