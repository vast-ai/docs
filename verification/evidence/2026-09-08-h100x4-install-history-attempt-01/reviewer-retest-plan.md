# HIST-05 reviewer integration retest basis

Target: the current dirty documentation checkout and existing loopback review proxy, after the additive installation-intake patch. All prior claim/source/adjudication gates must remain intact.

1. Inspect the patch against the seeded current working-tree files, not merely HEAD; preserve staged and unrelated changes.
2. Run focused intake validation tests plus existing current-review and standalone-report tests. Reject injected status, substituted current claim, changed bound evidence/selector, source/hash drift, and arbitrary artifact paths. A missing/invalid intake must not promote or suppress the existing current review.
3. Check the current model without rewriting it. Compare its entire digest and staged Git diff with the first baseline. Regenerate the standalone HTML from existing counts plus supplemental findings, then check export consistency.
4. Verify the running port4000 source hash. Restart only the existing local review proxy if needed; do not touch the port3000 preview or a remote Host service.
5. Retest all 51 installation-page passage/status controls and the five new findings. Open every new bound evidence link, confirm page/heading/claim context and selected observation. Probe one unrelated route and one unbound artifact context. This is browser/interface proof only.
6. Open the standalone HTML, verify five findings and their passage/evidence dialogs, and inspect a screenshot for readable wording. Preserve any failure and subsequent corrected retest.
7. Retain final artifact identities, scope/status accounting and limitations, update traceability/planning notes, and keep runtime/operator and source-owner work open. No installer, listing, rental, customer workload, API key, privilege, reboot, external post or acceptance action is part of this retest.
