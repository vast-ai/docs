# Preserved failures, corrections and limits

## Diff locator defect — FAIL, corrected and retested

The builder's [original preparation record](builder-preparation-initial-01.json)
reported a diff against an extracted block, starting at line 1. That was insufficient
for the required full-installer source locator. The candidate bytes were already the
intended one-block edit; the defect was provenance presentation, not an executed
installer failure. The original remains retained (private source paths are masked
in this public projection).

Correction: generate the unified diff from actual full original/candidate bytes
with three context lines and record exact old/new block spans. Add tests for the
real hunk, context, already-modified input, and symlink output parent.

Retest: [preparation](variant-preparation-01.json) records hunk
`@@ -1959,14 +1959,10 @@`, old block 1961–1969, new block 1961–1965.
[Nine tests](variant-tests-01.json) pass; [explicit-input retest](variant-tests-02.json)
also passes and records the required source-path environment input in the command
vector. The first run's inherited environment was not shown in that vector, so it
is not presented as fully self-contained replay instructions. Both runs are retained.
Candidate bytes stayed SHA256
`4d87c48acc12a15eee1c2793d0631e1d936b2f996bdd50de4ad27b5acdf3d519`.

[Independent actual-byte/AST review](candidate-independent-review-02.json) confirms
the exact transformation and its limits. This does not prove live installation.

## Intended TUI skip compatibility — scoped FAIL, unresolved

The [reviewed TUI source](source-review-summary.json) waits for the very self-test
banner the local variant deliberately omits. No stock-TUI run occurred. A direct
modified-installer run or explicit TUI skip-state implementation is still needed;
this finding is not silently converted into a client-facing claim status.

## Readiness projection — sanitation correction, original retained privately

The first public readiness projection contained the persistent storage identifier.
Before interface integration, that field was masked; the exact original projection
and raw capture remain restricted. [Projection verification](readiness-projection-01.json)
records their digests and confirms the masked correction. Other captured host
identities were already projected as a match or hash. This is not a new host run.

## Local proxy startup — FAIL, corrected orchestration and retested

The first health probe and browser checks were started before the restarted
port4000 proxy had finished strict package validation and opened its listener.
The health probe reported ECONNREFUSED; the retained
[page-control attempt](browser-controls-01.json) and
[proof-viewer attempt](intake-browser-run-01.json) failed with connection errors.
This is a check-orchestration failure, not evidence of Host or installer behavior.

Correction: wait for the server's ready message, then require the
[health/context retest](proxy-readiness-retest-02.json) to return HTTP200, the
expected source hash, and available current installation findings before browsers.
The browser skill's [offline diagnosis](browser-doctor-01.json) reported zero
failures; its old browser-state warning was not repaired or deleted.

[Page controls retest](browser-controls-02.json) passes all 101 exact passage/status
controls. [Proof-viewer retest](intake-browser-02.json) passes 29 contextual links,
all five selected observations, rejection of unrelated-page access, and offline
proof/passage viewing with zero network resources. No reviewer code changed between
the failed startup checks and successful ready-server retests. This does not close
the separate earlier unexplained intermittent Self-Test fetch finding.

## Earlier attempts

The [preceding intake and reviewer retest](../2026-09-08-h100x4-install-history-attempt-01/reviewer-result.md)
preserve its host-key lookup, interpretation, fixture/export and startup failures.
Neither this local preparation nor passing interface checks close the prior
intermittent Self-Test fetch issue, known documentation wording defects, or the
isolated key-file permission finding.
