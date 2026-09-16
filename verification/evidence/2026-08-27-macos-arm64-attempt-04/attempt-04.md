# Host Docs local-safe batch — attempt 04

- Kind: Verification replay after command execution-access grouping
- Test basis: `VV-HOST-DOCS-2026-08-27-A`, with VV-HOST-001 expanded and frozen before execution
- Docs target: commit `0b4af06c35f77517397708ed41d97b7642c8f5e3`, tree `180cd13643a3d4128205b80322f0c870919c7ac2`
- Host content revision: `5088d76b89856185f3ab15a628e4152ff140ab26`
- Host content fingerprint: `sha256:bc59a848d0cb8698097787b911bb9e5b6875570c7c58815baa6d1f48b2504b4d`
- Vast CLI target: clean `master@ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd`, tree `f477989d0efd307154aeb623d6a1bfcee33e822a`
- Environment: macOS 26.5 arm64; Python 3.14.6; Bash 5.3.15; Node 24.19.0; npm 11.17.0; Mint 4.2.234; Git 2.51.0
- Performed: 2026-08-27T08:07:37Z–2026-08-27T08:07:46Z
- Mode: Executed (local-safe checks only)
- Result: 8 PASS, 1 FAIL for the nine local-safe items
- Evidence sensitivity: Internal; no credentials or protected host data captured

## Purpose and method

Attempt 04 verifies the generated execution-planning view added to the complete command inventory. The frozen target classifies all 176 command targets into five mutually exclusive groups while retaining stable IDs, source locations, existing safety tiers, and additional authentication/credential/mutation/environment/client gates.

The tracked docs target and official Vast CLI checkout were clean. No documented Host command, paid resource, Host-root action, credential, account mutation, GPU/Docker workload, or private control plane was used. The grouping is derived conservatively from command text and remains reviewable in Markdown, JSON, and CSV.

## Observed

| ID | Current result | Observation |
|---|---|---|
| VV-HOST-001 | PASS | Inventory current: 72 Host pages, 474 unique targets, and all 176 commands reconcile across five execution-access groups: 0 paid+root, 6 paid-only, 52 Host-root/privileged, 14 Host-context without root, and 104 requiring neither paid spend nor Host root. |
| VV-HOST-002 | PASS | CLI registry check passed all 181 occurrences at clean current CLI master. |
| VV-HOST-003 | PASS | All 39 authored pages have synchronized persona metadata. |
| VV-HOST-004 | PASS | All nine review-context tests passed. |
| VV-HOST-005 | PASS | Review-server JavaScript syntax check exited 0. |
| VV-HOST-006 | PASS | OpenAPI definition is valid. |
| VV-HOST-007 | PASS within Host scope | Mint found 99 broken links in 10 non-Host files and none under `host/`. |
| VV-HOST-008 | FAIL | Zero Host missing-alt findings; 97 Host named-anchor findings and the shared dark-theme contrast failure remain. |
| VV-HOST-009 | PASS | Git whitespace check exited 0. |

## Evidence

- [Environment, target identity, and artifact hashes](./environment.txt)
- [Exit-status ledger](./results.tsv)
- Raw output: [`VV-HOST-001`](./VV-HOST-001.stdout.txt), [`VV-HOST-002`](./VV-HOST-002.stdout.txt), [`VV-HOST-003`](./VV-HOST-003.stdout.txt), [`VV-HOST-004`](./VV-HOST-004.stdout.txt), [`VV-HOST-005`](./VV-HOST-005.stdout.txt), [`VV-HOST-006`](./VV-HOST-006.stdout.txt), [`VV-HOST-007`](./VV-HOST-007.stdout.txt), [`VV-HOST-008`](./VV-HOST-008.stdout.txt), and [`VV-HOST-009`](./VV-HOST-009.stdout.txt)
- All attempt-04 stderr files are empty.

## Interpretation and limitations

The access matrix proves inventory completeness, reproducible classification, and traceability—not runtime success. Paid Self-Test forms remain blocked pending budget/target approval. Host-root and Host-context forms remain blocked pending an approved disposable Host. Account mutations, credentials, matching environments, and external-client checks retain their separate gates. The accessibility failure and two external validation blockers remain open, and acceptance remains an authorized human decision.
