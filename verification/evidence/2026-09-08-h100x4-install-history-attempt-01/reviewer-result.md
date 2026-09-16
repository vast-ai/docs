# HIST-05 — Installation findings in the reviewer and offline report

Result: **PASS for this bounded repository/interface change**, on 2026-09-08. This is not an installation, listing, self-test, workflow, cross-platform CLI or human-acceptance PASS. See the [installation intake result and two open-work registers](result.md).

The localhost reviewer and shareable HTML now display five exact passage bindings on **Installing Host Software**. They distinguish partial pre-install/static findings from complete evidence, preserve every claim's status, and open the selected observation with the page, heading, wording, scope limit and remaining action. Unrelated pages keep their existing presentation.

| Exact passage | Retained finding | Limit |
|---|---|---|
| Host Installer Wizard — `MCL-fd7e8b86c5cfd383` | Services absent on the new host; earlier public-source inspection retained | No TUI execution observed |
| Host Installer Wizard — `MCL-009da802cabe1bc9` | Pre-install services and current helper/source inspection | No fresh setup command or installation executed |
| Headless Fallback — `MCL-ead93c85c2ff4168` | Selected observation of four H100 GPUs | Inventory query, not literal plain `nvidia-smi`, CUDA or load proof |
| Headless Fallback — `MCL-ec2e1c9a8be1a706` | Selected XFS `prjquota` mount observation | No installation, formatting or quota-enforcement test |
| After Install — `MCL-ce118e1ce7bf71bb` | Static helper listing/self-test sequence and corrected source inspection | No actual listing, self-test outcome or cleanup proof |

The [intake map](../../current-host-install-evidence-intake.json) contains exact source spans, wording and pinned artifact selectors. It is display-only and does not modify the canonical current review model or historical attempts.

## Failures and linked retests

1. [Initial wider test attempt](reviewer-unit-retest-01.json) failed because isolated server fixtures did not copy the newly imported validator; the generated HTML was also stale. The failing child was stopped after the fixture defect was confirmed, so this is not a completed full-suite run. Fixtures now copy the module and required input artifacts; the HTML was regenerated. The follow-up draft's negative-context test used another legitimately bound claim; integration corrected the test to a genuinely unbound claim before execution. [Retest 03](reviewer-unit-retest-03.json) passed all 69 tests, including rejected substitutions and missing/malformed intake preserving current review.
2. [Initial browser proof](intake-browser-01.json) passed functionally, but its visible wording still put “no supporting proof” above supplemental findings, and its offline screenshot did not show the intended card. Conditional wording now distinguishes complete/current-model evidence from the partial finding. It does not change statuses. The browser harness now explicitly positions the offline card before taking a screenshot.
3. [Browser attempt 02](intake-browser-02.json) failed with connection refused while the restarted local proxy was still starting; no page check ran. After the proxy reported ready, [attempt 03](intake-browser-03.json) passed on the final source. This explained startup race does not resolve the separately retained earlier intermittent fetch issue.

## Final retained checks

- [Final regression suite](reviewer-unit-final-04.json): **69 tests passed, 0 failed, 0 skipped**, on the final reviewer/template source. Includes current-review, historical review-context, intake guard and offline export tests.
- [Current model consistency](model-final-02.json): PASS, 44 primary Host routes plus 33 CLI/SDK support layers. The full model digest is unchanged.
- [Offline export consistency](html-consistency-final-02.json): PASS, 2,005 claims and 135 embedded files.
- [Two-page rendered controls](browser-final-02/summary.json): **101/101** claims located with matching statuses, valid section filters and heading links; 51 installation claims plus 50 overview claims.
- [Final intake browser test](intake-browser-03.json): five exact passage controls; **nine bound evidence links returned HTTP 200**; selected observations matched their pinned records; an unrelated claim/artifact context returned HTTP 404. Offline equivalents passed with zero network resources and no horizontal overflow.
- Visually inspected [loopback screenshot](intake-loopback-03.png) and [offline screenshot](intake-offline-03.png). The client-facing passage, partial finding, evidence controls and limits are readable. These are desktop observations, not mobile/browser-matrix coverage.
- [Local AST index update](graph-update-final-01.json): completed without model calls. The graph HTML size limit and zero-node source warnings remain recorded; the graph is navigation support, not product evidence.
- [Final identity and artifact manifest](final-state-01.json): source identities, model/index preservation, current server identity and bounded sanitation results. The manifest is accounting, not proof of a product claim.

Final reviewer source SHA-256: `b5a9fa3d98338ea834711ed5efecdabdc5398a10e8db8f41085010248d57778b`.

Final shareable HTML SHA-256: `5f8508521cc8aa1060c237bde9c7536892922b90b19aa6da9e5dacee1a04d6fb`.

Current model SHA-256, unchanged from baseline: `a3a7db11d24f99d972d61b011a5eb3bacbb3dd0903266d785508d5908c069b5a`.

Counts remain **185 PASS / 4 N/A / 151 FAIL / 22 BLOCKED / 1,643 UNVALIDATED**. The 22 BLOCKED claims are not the whole outstanding population. No new material claim or procedure was promoted.

Only the existing port4000 proxy was restarted; port3000 preview and remote hosts were untouched. The disposable UI worktree was removed after independently checking its complete binary diff and all 16 untracked files against the main checkout or recovery archive (`e9e7957c8431854f131b4bd4f7f545b15f987c05509c6890f666d692e5320788`). No unrelated worktree or staged content was discarded.

No Host/API/setup credential use, remote installation, listing, rental, workload, reboot, push, merge, external post or human acceptance occurred in this interface retest. Runtime/operator and source-owner/commercial work remains open as separately listed in the intake result.
