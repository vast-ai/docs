# 88-passage continuation review

The accepted frozen inventory contains 88 passages: 32 CLI/reuse, 28 system examples, 19 Teams source/caption passages and 9 console observations. Seven wording corrections were applied. All 88 have claim-suitable PASS within their recorded limits; this is source/request/navigation evidence, not 88 executed workflows.

Current model SHA-256: `5e23962030e42fb599f89b56f232ba926cc0c6d11467ebfaa7c321d7d5ecec4e`. Baseline: `e4117c2948dd52e2f714fab95fb2419948a46d0f`, model `e376445856232f6a41f1b68ac3e01ee173590390cae8768c4392361bc04cc235`.

Complete inventory remains 44 pages, 2,008 passages, 116 procedures and 1,085 procedure nodes. Statuses: {'BLOCKED': 21, 'FAIL': 3, 'NOT_APPLICABLE': 91, 'PASS': 1130, 'UNVALIDATED': 763}.

## Exact corrections

| Passage | Source | Change basis |
| --- | --- | --- |
| CUR-fcc30ead99e2c846 | host/market-metrics.mdx | The current table groups gpu_name under Common parameters without identifying an endpoint. Both the original current public guide and pinned client/schema restrict gpu_name to GPU history. The exact replacement restores that endpoint scope while retaining the useful RTX 4090 example. |
| CUR-c42096e1282c0d44 | host/disable-ssh-password-login.mdx | OpenSSH uses the first applicable value; Ubuntu includes drop-ins at the beginning, and Match changes scope through the end of the file. Appending at EOF can therefore fail to change the effective value. The replacement uses explicit editing and keeps configuration validation, conditional restart and effective-value inspection. |
| CUR-89c08cb5b29ce444 | host/disable-ssh-password-login.mdx | The rollback copies every saved .orig file to its suffix-stripped original path. The original example could ignore a failed copy and proceed to restart; the replacement stops on a copy error and chains successful restoration to syntax validation and restart. Nonmatching optional backup globs are skipped. |
| MCL-9fc1250d7de86b7a | host/network-ports.mdx | Python http.server otherwise serves the working directory and its descendants; the original privileged listener could expose readable Host files. The replacement binds the same high port on all interfaces, serves a fresh empty directory as the user, retains the two-session listener inspection and removes only the empty temporary directory after Ctrl+C. |
| MCL-c097d0beccbacad9 | host/host-teams.mdx | The current Members destination and selected-team controls support this navigation. The replacement removes the broader assertion that no separate console page exists. |
| MCL-b142dfdfe312f402 | host/host-teams.mdx | The owner context exposes the specified fields, while the inspected manager context does not. The replacement explicitly scopes the instruction to an available section and avoids inventing a universal role rule. |
| CUR-c8657007c73f9603 | host/notifications.mdx | Current UI establishes the corrected destination, section name and Host group. The replacement removes the unsupported exclusive eligibility statement and makes the observed account-context dependency explicit; it does not claim which account governs team notifications. |

## Evidence and limits

The paired sealed projectors replay the full earlier 318 review, which retains the 358 source-family review and older evidence. The new registry binds the root acceptance, each lane inventory/decision/source index, exact source hashes and selectors, all prior claim evidence and history. The independent review corrected two self-test rationales to the actual string parser type before acceptance.

The changes relocate 24 procedure/node spans. No procedure status or evidence changes, no PASS command bytes change, and no outside-inventory literal overlaps were found. Changed command examples within already non-passing procedures retain those procedure outcomes. The seven corrections and every prior literal remain reviewable in the transition/history records.

Only sanitized current-console observations are included. The actual screenshots and raw DOM remain in the local research evidence directory, excluded from Git and the HTML export. Original included documentation images are unchanged; their captions are supported as descriptions of those exact images, with unrecorded capture-date/account limits.

No invitations, account settings, listing settings, ownership changes, deletions, contacts or notification preferences were submitted. No paid rental, host configuration or new hardware diagnostic was run. Visibility across different teams does not prove universal role permissions. Notification delivery and the account context governing team-machine notifications remain outside this check.

The current result is cumulative. Earlier failures, 18 other reviewed residual passages grouped into 11 source-follow-up topics, owner questions and workflow prerequisites remain visible; these 88 decisions close only their exact scoped occurrences. See `integration-impact.json`, `root-lane-acceptance.json`, the new registry and per-lane decisions for direct inspection.

## Integration checks

Paired projection, exact predecessor/source preservation, accepted-proposal and source-selector tamper tests, generator consistency, and the offline reviewer are checked after application. Final machine-readable outcomes are recorded in `integration-checks.json`; real-browser review is performed independently by the root reviewer.
