# Commit and update Host Docs PR185

User authorization: commit and PR the changes made in this Host Docs task.
Target: CON-1584-host-cli-api-sdk, existing open vast-ai/docs PR185, head fork
jjziets/docs, base main. No merge, release, Host operation or human acceptance.

1. Capture HEAD, index, exact dirty-file inventory/hashes and remote PR state.
2. Check the accumulated Host Docs/source-review/reviewer changes for scope,
   required generated dependencies, accidental private data, archive contents
   and file-size limits. An independent reader audits publication risks. Keep
   raw secret values out of outputs; do not silently rewrite historical evidence.
3. Reuse retained claim checks; rerun local regression/export integrity checks
   for the commit package. These checks establish repository consistency, not
   product runtime or closure of the remaining 26 corrections/23 blockers.
4. Stage only reviewed, in-scope files. Check the staged snapshot, commit, then
   push normally to the existing PR head branch. Never force-push.
5. Update the existing PR description with scope, tests, open work and reviewer
   entry points. Verify GitHub's head SHA equals the pushed commit. No duplicate
   PR, merge, acceptance, paid operation or credential use outside Git publishing.

PASS for publication requires a verified commit and remote head match. A detected
private-data risk prevents pushing that content until safely resolved. A failed
test is retained and diagnosed; a missing permission is a concrete blocker.
Preserve all existing task work and historical evidence. The main agent performs
Git operations and verifies independent findings; readers do not mutate the tree.

Orientation: PR185 is open on fork branch CON-1584-host-cli-api-sdk at bfa926c;
local HEAD is 4fa6fbb. The graph identifies coupled export/transition/reader files;
it is navigation, not proof. Initial `gh pr status --json currentBranch` was an
invalid field request; explicit `gh pr view 185` supplied the verified PR state.
