# Direct install attempt — stopped before installation

PR #185 / CON-1518, 2026-09-08. The direct route and replacement setup token were supplied/approved. **Installation is BLOCKED by password-required sudo, not by another missing route choice.** No installer, setup token, Host API, registration, listing or rental was invoked. No reboot or other-host change.

At 21:55:16–21:55:17 UTC, strict SSH confirmed the intended new host, four H100 PCIe GPUs, no compute processes, unchanged boot, persistent XFS/project-quota Docker mount, and absent Docker/Vast services. Both sudo checks returned exit 1 because authentication is required. [Retained preflight](preflight-02.json).

## Dispositions

| Check | Disposition and basis |
|---|---|
| LIVE-01 | **BLOCKED** overall by sudo authentication. GPU, identity, boot and mount observations succeeded. No failed documentation claim is inferred. |
| LIVE-02 | **PASS — static scope only.** Exact [source hashes](source-hashes-01.json) match reviewed source/candidate; [independent contract review](source-review.md) confirms limits. |
| LIVE-03 | **BLOCKED** before transfer/invocation: approved sudo credential entry not identified. Setup-token validity untested. |
| LIVE-04 | **BLOCKED** by unperformed installation; service readiness and embedded diagnostic outcomes do not exist. |
| LIVE-05 | **BLOCKED** by absent installed/ready target. Approved prices are recorded, not applied. Static listing contract was inspected. |
| LIVE-06 | **PASS — interface scope only.** Five exact bindings preserve historical selected checks and add the pinned preflight with current sudo next action. No model status changed. |
| LIVE-07 | **PASS after retained correction — repository/interface scope only.** Initial suite 69/70; generated-HTML ordering failure preserved and all 14 HTML tests pass after export. Browser and source/model checks pass. Final manifest is `final-integrity-01.json`. |

## Exact page relationship

All five findings are supplemental context on `/host/installing-host-software`, not proof of the documentation itself:

| Claim | Heading / source line | What this attempt contributes |
|---|---|---|
| MCL-fd7e8b86c5cfd383 | Host Installer Wizard / 40 | Direct-route prerequisite, no TUI execution evidence. |
| MCL-009da802cabe1bc9 | Host Installer Wizard / 44 | Approved modified route and concrete sudo stop; no official-command success. |
| MCL-ead93c85c2ff4168 | Headless Fallback / 65 | Four GPUs observed; no installer GPU/container test result. |
| MCL-ec2e1c9a8be1a706 | Headless Fallback / 66 | Current and persistent quota mount options observed; no quota-enforcement test. |
| MCL-ce118e1ce7bf71bb | After Install / 139 | Automatic helper deliberately omitted; no automated self-test or timing result. |

Required evidence is retained execution for behavior and canonical source for implementation. Source-owner and commercial authority gaps remain separate. All canonical statuses stay unchanged; no human acceptance is recorded.

## Preserved correction

The original collector labeled the entire preflight FAIL and included a persistent device identifier. Its original bytes remain in a restricted local capture. The public [first attempt](preflight-01.json) retains actual command failures with that identifier redacted. [Projection 02](preflight-02.json) corrects the install disposition to BLOCKED and records the original hash; it is not a new SSH run or a fabricated passing retest. The collector's sanitation was corrected for future runs. No secret was read or exposed by the checks.

Next action and remaining work: [runtime/operator register](runtime-operator-register.md), [source-owner/commercial register](source-owner-register.md). Evidence-package completion does not complete either workstream.

## Reviewer checks

The [independent consistency review](independent-consistency-review.md) found no actionable issue. The [live/offline proof-link checks](intake-browser-01.json) passed all five exact claim bindings and 34 contextual links, preserved each selected historical observation, rejected an unbound evidence request with HTTP 404, and used zero offline resources. The [two-page retest](browser-final-01/summary.json) located all 101 current passages with unchanged statuses. Main-agent visual inspection of retained loopback/offline screenshots confirmed the current sudo message and readable exact passage context.

The [HTML build](html-export-01.json) and [freshness check](html-check-01.json) pass: 2,005 claims and 144 embedded files. [Current-model freshness](model-freshness-01.json) passes for 44 primary routes and 33 support layers. The model remains `a3a7db11d24f99d972d61b011a5eb3bacbb3dd0903266d785508d5908c069b5a`; no claim count/status change. [Ready-server check](reviewer-ready-01.json) confirms source identity and current intake after restarting only port4000; port3000 and saved feedback were untouched.

The task-created isolated UI worktree was archived with file hashes and readback, then removed. Its changes are integrated; recovery archive SHA256 is `30be43501cabc74302a30b3bf161911919535ffd1eebaec848a0c4e38419b130`. No user checkout or historical evidence was removed. [Local integration command correction](integration-correction.md) preserves the failed patch-generator attempt and corrected application.

[Initial regression run](reviewer-regressions-01.json): 69 of 70 passed; the generated-file equality check raced the export. After export completed, the [complete 14-test HTML retest](html-regression-retest-02.json) passed against identical source. The evidence does not claim a single green 70-test run. [Projection checks](projection-checks-01.json) independently match raw hashes, retained command errors, corrected classification and declared redaction. Final preservation/sanitation manifest is retained separately as `final-integrity-01.json` after this result was written.

This closes the bounded evidence/interface work for this stopped attempt, not live installation, either external workstream, all outstanding Host Docs claims, or human acceptance. No commit/push/merge/post was performed.
