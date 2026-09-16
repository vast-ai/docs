# Host review publication attempt — 2026-09-06

PR #185 / CON-1518. Authority: the user explicitly requested merge and push.
This record concerns publication of the completed reviewer-interface changes,
not acceptance or runtime validation of Host documentation claims.

## Plan and starting state

1. Confirm the PR, fork branch, local ancestry, and upstream permissions.
2. Inspect the intended code and retained evidence for publication safety;
   exclude unrelated local plans, dependencies, feedback, and raw private logs.
3. Replay safe repository-local checks, stage exact reviewed paths, commit,
   and push normally to the PR's fork branch without rewriting history.
4. Merge only if permissions, conflicts, and required GitHub review/check gates
   permit it. Otherwise retain the specific reason and report the pushed head.

Starting HEAD: `3e1e30e2221b65d7ce1e901d9ae305f63af5b64b`.
Branch: `CON-1584-host-cli-api-sdk`; PR head is in `jjziets/docs`, base is
`vast-ai/docs:main`. After fetching, local HEAD is 12 commits ahead and zero
behind the fork branch (`09d729e72fbcb2bdd2dead2b9dc5d5e1eeeffcf5`).
The index starts clean. Tracked edits are confined to `REVIEW-TRACEABILITY.md`,
`review-server.mjs`, and `scripts/review-context.test.mjs`; the intended new
runner is `scripts/check_host_review_reading.mjs`. Two September 5 evidence
directories support those edits. The other existing untracked files remain
local and are not part of this publication.

Safe checks may run local test servers and disposable fixtures. No credentialed
Host/API, paid, privileged, destructive, or workload operation is authorized.
GitHub reads and the explicitly requested Git publication are in scope. No
forced push, administrative bypass, fabricated human approval, or Jira update.

## Observed merge blockers

- PR #185 is OPEN and DRAFT, with `REVIEW_REQUIRED` and no reported check runs.
- The current GitHub account has fork push permission but has no push,
  maintain, or admin permission on `vast-ai/docs`.
- A non-worktree merge analysis (`git merge-tree --write-tree --name-only HEAD
  origin/main`) returned exit 1 against upstream
  `d4217aa7d6e0d265c200909e3043cab33f264519`, with conflicts in
  `api-reference/openapi.yaml`, `docs.json`, `host/market-metrics.mdx`, and
  `host/verification-stages.mdx`. It did not alter the working tree or index.
- A maintainer with upstream authority must resolve/review the integration and
  satisfy the required review before the PR can merge. The requested push does
  not erase these gates or establish Product/Finance/Legal approval.

## Validation

- [Reviewer-interface replay](reviewer-tests.json): 33 of 33 tests passed.
  The three frozen reviewer source/test/runner hashes remain unchanged from
  the final September 5 all-pages attempt.
- [Original Python failure](python-failure-before-fix.md): 96 of 97 tests
  passed. One historical-evidence assertion incorrectly compared the present
  reviewer code against the September 4 packaging snapshot. The original
  failure and its expected/observed hashes are retained, not overwritten.
- Correction: `scripts/test_reconcile_host_vv_repository.py` now compares
  that historical table against immutable packaging commit
  `3e1e30e2221b65d7ce1e901d9ae305f63af5b64b`, whose 20 artifact hashes all match.
  Existing artifact identity, registration, status, and non-promotion checks
  remain in place. No historical digest or canonical status was changed.
- [Post-correction replay](python-retest.json): all 97 repository tests pass;
  the reconciler confirms 40 primary Host pages, 33 support layers, and 1,004
  targets are current; `git diff --check` passes. The corrected test source
  remained unchanged during this replay.
- The local AST knowledge graph was refreshed successfully. Its untracked
  generated output is excluded from publication.
- The full staged whitespace check reports ten trailing-whitespace warnings
  in two historical Markdown audit reports. All ten were inspected and are
  intentional two-space Markdown hard line breaks, not code defects; those
  original reports are preserved byte-for-byte. The staged code and this
  publication record pass their whitespace check. No other staged whitespace
  warning or unexpected path was found.

## Retained browser proof and publication scope

- [Initial reader presentation attempt](../2026-09-05-host-reviewer-reading-attempt-01/result.md).
- [All-pages attempt, original failures, and final retest](../2026-09-05-host-reviewer-all-pages-attempt-01/result.md).
- [Focused highlighting correction report](../2026-09-05-host-reviewer-all-pages-attempt-01/owner-tracked-change-audit-report.md),
  including the historical probe and retest directories it identifies. This
  link makes the focused report reachable without rewriting the earlier
  attempt record.

A read-only publication audit covered both September 5 evidence directories:
185 regular files, 8,515,362 bytes, 172 valid JSON records, and five PNGs.
No symlinks, special files, credentials, private keys, personal absolute paths,
emails, or concrete machine/instance identifiers were found. Screenshots
show the local documentation/reviewer UI with no reviewer identity. The
Authorization examples contain documentation placeholders only. Retained
loopback URLs, tool versions, hashes, and relative working-tree inventory are
provenance, not Host runtime evidence.

The commit is limited to the three original tracked edits, the new browser
runner, the historical-snapshot test correction, both September 5 evidence
directories, and this publication-attempt directory. Unrelated local files
remain excluded. No customer documentation claim or external evidence status
is promoted by this publication.

## Publication boundary

This is the validated candidate record prepared before the normal fork push.
The resulting Git commit and GitHub PR head establish which bytes were
published. No merge, human acceptance, runtime validation, or external owner
confirmation is claimed; the observed merge gates above remain unresolved.
