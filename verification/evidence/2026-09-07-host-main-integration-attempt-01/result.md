# Host Docs upstream-main integration — attempt 01

PR #185 / CON-1518. User authority: resolve conflicts with main; prior explicit
push authorization remains in effect. This is repository integration, not
Host runtime validation or human acceptance.

## Frozen starting state and plan

Starting commit: `7d42a0d439f91e4dc2877104db807ec6fb975ce4`.
Starting tree: `3e171a0abfd0173ee5320f3ed131dd4250c93750`.
Branch: `CON-1584-host-cli-api-sdk`, synchronized with its fork tracking branch.
Tracked working tree and index were clean. All 30,999 existing untracked path
entries remain local. The full restricted pre-edit porcelain-v2 capture is
retained locally; its SHA-256 is
`c5f29c60c2bf2f089a5a563f5d5b99224bc20fefd4567fbcafba4a0f723e6d91`.

Target fetched main: `d4217aa7d6e0d265c200909e3043cab33f264519`.
Use a normal merge, not history rewriting. Preserve all predecessor commits,
historical evidence, current reviewer behavior, and intentional upstream
content. Generated files must follow their merged generators/source inputs.

1. Inspect every conflict and all upstream Host/API/navigation changes; check
   PR #153 ancestry independently of the citation-failure count.
2. Record the unresolved merge before correcting it. Resolve local integration
   defects; stop only at a specific missing semantic decision or authority.
3. Refresh affected inventories and source bindings without promoting stale or
   unvalidated behavior. Upstream additions are not covered by the earlier
   40-page browser attempt.
4. Run safe static, generator, repository, reviewer, link, and rendered checks
   proportionate to the changed surface. Retain commands, exact identities,
   outputs, failures, corrections, and retests.
5. Commit/push only the integration and safe evidence. Confirm remote ancestry
   and PR gates; never bypass required review or record human acceptance.

PASS means only the exact repository check has current suitable evidence.
Missing evidence is UNVALIDATED; a confirmed defect is FAIL. BLOCKED requires
a specific unavailable source, decision, environment, permission, or authority.
No Host/API credentials, paid work, WAN checks, privileged/destructive commands,
or workload-affecting operations are in scope.

## Results

- Exact PR #153 head `fcdd8aca5906bdf218d3fbc9bc80a4322f800db8` is an
  ancestor of starting PR #185 head: `git merge-base --is-ancestor` exited 0.
  PR #153 remains OPEN on GitHub; a separate merge is not a dependency. The
  unrelated number 153 in the prior status report counts citation failures.
- [Initial merge](merge-initial.json) records all four conflicts before
  correction. [OpenAPI rebuild](openapi-build-public.json) preserves merged
  endpoint source changes and regenerates the aggregate; the raw build log
  remains local and the public derivative masks only the workstation path.
- Navigation retains the 40-page PR lifecycle layout and adds the four new
  upstream Host pages exactly once: Machine Metrics, Machine Offline,
  Upgrade the Kernel, and Disable SSH Password Login. Current scope is 44
  primary pages plus the 33 separate central-reference support routes.
- The candidate Verification Stages integration retains the concise PR
  lifecycle/personas and upstream's current requirements tables. It removes
  the competing old numeric lists from this page and links the separately
  pinned generated Self-Test reference. This preserves upstream publishing
  intent, not proof of backend enforcement or Product/Security approval.
  The new CPU/ports/network/storage/security policy wording requires its own
  source/owner validation and must not inherit old evidence statuses.
- [Initial post-merge checks](post-merge-initial.json): persona check FAIL
  (eight missing-label findings across four new pages); repository suite
  95/97 PASS (two historical-claim source-location tests are stale); current
  reconciliation FAIL (one formerly bound installer command changed).
- The four upstream pages now carry matching all-Host-persona frontmatter and
  visible labels. The kernel guide's incorrect `vastai schedule maintenance`
  label and Host-wrapper link are corrected to the central `schedule maint`
  reference; this is static naming/link support, not execution evidence.
- [Local static retest](local-static.json): persona 44/44 PASS, named-anchor
  check PASS, OpenAPI validation PASS, and 44 unique existing Host navigation
  destinations with no duplicated CLI/SDK submenu aliases.
- [Initial Mint link scan](mint-links-initial.json): 100 findings in 11 files,
  including one review-only traceability link into the intentionally excluded
  evidence route. The traceability link is corrected to the immutable GitHub
  artifact, and the earlier reader artifact is made clickable too. The other
  99 findings match the previously recorded non-Host link baseline; a retest
  follows rather than relabeling the global result PASS.
- First preview startup exited 1 because the default Node runtime is v26.5.0
  and the installed Mint CLI explicitly rejects Node versions 25 or later.
  No system runtime is modified; use the available bundled compatible Node
  executable for the isolated loopback preview and retain its actual version.

## Integration follow-up scope

The four new pages and changed source/dependency bytes cannot be represented
by the historical 40-page proof. Preserve that evidence package unchanged,
validate it against its exact tested Git snapshot, and separate current source
freshness: unchanged source may retain its bounded evidence status, changed
source is STALE, and a new route is UNVALIDATED with an explicit review action.
This compatibility layer is not a completed 44-page procedure/claim rebaseline.
Do not reclassify absent evidence as external BLOCKED.

Integration and validation remain in progress. No completed merge or new Host
claim validation is asserted yet.

## Retests and current coverage

The statements above preserve the original observations before their corrections.

- The Mint [link retest](mint-links-retest.json) returns the known 99 non-Host
  findings in ten files; the introduced traceability finding is gone. No global
  clean-link result is asserted.
- The compatible loopback preview used bundled Node v24.19.0, without changing
  the system Node installation. [Rendered route smoke](rendered-route-smoke.json)
  returned HTTP 200 with a heading for all 44 current Host routes. This is not
  a full accessibility or semantic validation result.
- [Current inventory generation](current-inventory-generation.json) and
  [static final retest](static-final-02.json) reconcile 77 route files: 44 primary
  pages and 33 central-reference support routes, 593 unique extracted targets,
  and 228 command targets. Extraction and shell syntax checks execute none of
  the documented commands. The inventory content fingerprint includes exact
  current bytes; its Git history reference is not proof that uncommitted text
  was already present at that older revision.
- The first [current CLI scan](current-cli-signatures.json) reported one unknown
  option because the checker attributed the outer `-e` to the inner command in
  a nested `$()` example. The extractor now separates substitution/quote
  contexts. Its [retest](current-cli-signatures-retest.json) has 204 occurrences:
  202 registered signatures/options and two family references, zero actionable
  findings. Source: clean pinned Vast CLI `ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd`.
  The final static check reproduces that exact JSON after the quoted-parenthesis
  regression fix. This proves registry compatibility, not successful API or Host
  execution; the checker remains a bounded static scanner, not a complete shell
  parser.
- Python regressions progressed from the original 95/97 failure through 98/98,
  100/100, and finally **101/101 PASS**. The historical claim/span integrity
  tests deliberately read exact `7d42a0d` Git blobs. Corrupt claim hashes still
  fail the real integrity loop; historical results were not rebound to new text.
- [Reviewer initial failure](reviewer-initial.json): 23/34 failed because the
  new historical source allowlist omitted legitimate central references.
  Corrective [retest 01](reviewer-retest-01.json): 27/35 passed; the remaining
  isolated fixtures exceeded their old two-second startup allowance. A bounded
  ten-second allowance preserves every integrity assertion.
  [Retest 02](reviewer-retest-02.json): 34/35 passed; the removed-route fixture
  edited the wrong navigation group and therefore removed nothing. The fixture
  now removes the exact route recursively and asserts that removal.
- [Reviewer route coverage](reviewer-route-coverage.json) checks every current
  primary/support route: 36 primary sources unchanged, four STALE, four new
  UNVALIDATED; 27 support sources unchanged and six STALE. All 77 contexts are
  available, and non-current contexts expose no old current claim/procedure
  cards. An unchanged source retains only its previous bounded disposition,
  not an inferred PASS. The old package's three canonical JSON files and all
  historical evidence remain unchanged.
- Browser inspection retained [changed-page review](changed-page-review.png),
  [new-page review](new-page-review.png), and [rendered requirements](verification-requirements.png).
  Changed pages link to their exact pinned prior source; new pages explain that
  no prior proof exists. No reviewer identity, feedback, or acceptance was added.

## Work remaining after the integration

This merge is not a completed 44-page V&V rebaseline. Repository work remains:
create exact current claim/procedure/source bindings for the four changed pages
(Tax Guide, Market Metrics, Verification Stages, Notifications), four added
pages, and six changed CLI/SDK support routes. Preserve all old attempts and
retain new retests. Current missing evidence alone stays UNVALIDATED; do not
turn this repository work into an external blocker.

The existing runtime/operator and Product/Finance/Legal/source-owner registers
remain separate external workstreams. This attempt neither executes their
operations nor supplies their authority, and it records no human acceptance.
Upstream PR review/merge permission remains a publishing gate, not Host proof.

## Final integration check

[Reviewer retest 03](reviewer-retest-03.json) passes **35/35**, with zero skips.
It checks the retained historical package separately from the actual merged
44-route sources, including stale/new/removed routes, source links, corruption
rejection, evidence limits, and synthetic review export/import behavior.
The synthetic feedback remains isolated; it is not human acceptance.

The current source/retained-artifact hashes are listed in `integration-manifest.json`.
All four original Git conflicts are resolved. Main's retirement of eighteen
old cluster/overlay CLI and SDK reference files is retained; those files remain
recoverable from Git history. This attempt does not remove any historical V&V
evidence. Commit and remote publication are checked separately after this local
verification; the PR is still subject to draft/review/maintainer gates.

The final [staged whitespace audit](staged-whitespace-audit.json) exits 2:
main includes trailing whitespace in generated SDK references and a literal
patch artifact. [Byte comparisons](inherited-whitespace-binding.json) show every
flagged staged file is identical to upstream main. The wider comparison against
main also flags formatting in preserved historical evidence. These records are
not rewritten to obtain a green whitespace check. Earlier `git diff --check`
results covered unstaged edits only; no global whitespace PASS is claimed.
