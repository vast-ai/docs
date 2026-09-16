# Internal traceability is not a public route — addendum 04

PUB-02: The new full Mint link output actually contains140 findings in11 files:
the earlier99 generated API links plus41 relative evidence links from
REVIEW-TRACEABILITY.md. The initial 99-only commentary was incomplete; the raw
mint-links-baseline-01.json preserves the exact140 finding result.

The traceability file is an internal GitHub/reviewer record. Its repository-
relative evidence links should remain intact, but the file must not become a
customer documentation route. Add only REVIEW-TRACEABILITY.md to .mintignore;
retain it in Git and in the reviewer. Test this exact distinction and rerun
Mint. No other product page or ordinary broken link may be suppressed.

The generated-route checker will use that new retained output explicitly, while
the original140 finding remains historical failure evidence.
