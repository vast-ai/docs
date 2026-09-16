# First report correction review — FAIL, not integrated

Independent root review of the initial REPORT-01 patch found three local defects:

1. The existing generated HTML/manifest on-disk freshness test was replaced by
   comparing two executions of buildReport. That loses the stale-artifact guard.
2. Historical 124 Python / 35 review-context / 9 current-package checks were
   attributed to September 8. They actually belong to the September 7 result,
   line46. September 8 reports 142 Python, 29 current/HTML and an initial64-test
   JavaScript run (result line33).
3. The failure-history button was moved from the September 7 package to a
   different package without independently checking that its target is bundled.

The patch was not integrated. Required correction: restore the disk freshness
guard, attribute each count to its actual retained result and verify every
summary/proof button target. Also update the old report footer so it cannot imply
that the separately retained bounded paid run never happened. A new worker/root
retest must follow; these defects do not change any product claim verdict.
