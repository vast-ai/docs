# Verified GitHub evidence locations

[PR185](https://github.com/vast-ai/docs/pull/185) is **open and draft**, from `jjziets/docs:CON-1584-host-cli-api-sdk` into `vast-ai/docs:main`. Its verified head is `646e94e5386aa0e45034c7de339eac275ac2232f`. The fork is public. These files exist at that head; all six selected result/output files exactly match the local retained bytes.

| Evidence | Immutable GitHub link |
|---|---|
| H100 direct install, September 9 | [Open evidence](https://github.com/jjziets/docs/blob/646e94e5386aa0e45034c7de339eac275ac2232f/verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/result.md) |
| H100 direct-install operations summary | [Open evidence](https://github.com/jjziets/docs/blob/646e94e5386aa0e45034c7de339eac275ac2232f/verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/operations-summary.md) |
| H100 listing and client rental, September 9 | [Open evidence](https://github.com/jjziets/docs/blob/646e94e5386aa0e45034c7de339eac275ac2232f/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/result.md) |
| H100 rental run03 complete retained output | [Open evidence](https://github.com/jjziets/docs/tree/646e94e5386aa0e45034c7de339eac275ac2232f/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03) |
| H100 run03 GPU workload result | [Open evidence](https://github.com/jjziets/docs/blob/646e94e5386aa0e45034c7de339eac275ac2232f/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/gpu-result-01.json) |
| H100 run03 cleanup | [Open evidence](https://github.com/jjziets/docs/blob/646e94e5386aa0e45034c7de339eac275ac2232f/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/cleanup-main.json) |
| GPU injection correction, September 2 | [Open evidence](https://github.com/jjziets/docs/blob/646e94e5386aa0e45034c7de339eac275ac2232f/verification/evidence/2026-09-02-host-gpu-injection-attempt-03/result.md) |

The current owner-question model is [current-host-owner-questions.json](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/current-host-owner-questions.json). The [owner-question presentation page](/Users/hanneszietsman/VastAi/research/host-docs-meeting-20260914/presentation-20260915/owner-questions.html) is a **local September15 snapshot** with three publication conflicts, seven future-detail questions and one separate incident follow-up. Neither is in PR185 at the verified head. The snapshot binds `bb8f85b6 / 4df6d258`; the latest local source-refresh model is `a2488f89`. Its question objects were preserved, but the old page should retain its snapshot label.

GitHub has an [earlier source/owner work register](https://github.com/jjziets/docs/blob/646e94e5386aa0e45034c7de339eac275ac2232f/verification/current-source-owner-blockers.md). Label it as the PR's historical register, not the current curated owner questions. The newer closure reconciliation and source refresh are local-only; nothing in this check was pushed or merged.

Suggested narration:

> The plans, command outputs and cleanup records for these hardware examples are in the GitHub evidence folders linked from pull request one eighty-five.
>
> Each example links to an exact saved revision, so you can inspect the evidence behind it.
>
> The owner questions are linked from this presentation; that newer reconciliation is still local and has not yet been pushed to the pull request.

Checked using live read-only GitHub PR/tree APIs and exact Git blob comparisons. Complete paths, hashes, snapshot boundaries and counts are in [github-locations.json](/Users/hanneszietsman/VastAi/research/host-docs-meeting-20260914/presentation-guided-20260916/references/github-locations.json).
