# Host Docs local-safe batch — attempt 03

- Kind: Verification replay after reviewer-package commit
- Test basis: `VV-HOST-DOCS-2026-08-27-A` (expectations unchanged)
- Docs target: commit `792295cd0f0dde77bd4c400e2f26c32f46bd8459`, tree `f305c198957edc1a921f71c9cbd27a6f5d8e3ecb`
- Host content revision: `5088d76b89856185f3ab15a628e4152ff140ab26`
- Host content fingerprint: `sha256:bc59a848d0cb8698097787b911bb9e5b6875570c7c58815baa6d1f48b2504b4d`
- Vast CLI target: clean `master@ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd`, tree `f477989d0efd307154aeb623d6a1bfcee33e822a`
- Environment: macOS 26.5 arm64; Python 3.14.6; Bash 5.3.15; Node 24.19.0; npm 11.17.0; Mint 4.2.234; Git 2.51.0
- Performed: 2026-08-27T07:54:40Z–2026-08-27T07:54:50Z
- Mode: Executed (local-safe checks only)
- Result: 8 PASS, 1 FAIL for the nine local-safe items
- Evidence sensitivity: Internal; no credentials or protected host data captured

## Purpose and method

Attempt 02 established the corrective results. Attempt 03 replays the same frozen commands after the reviewer summary, attempt-02 evidence, and issue ledger were committed, so Mint evaluates the completed tracked reviewer package in its clean-tree snapshot. No expectations or Host content changed.

The tracked docs target and official Vast CLI checkout were clean. Localhost binding was authorized for the unchanged review-context tests. No documented Host command, paid instance, credential, account, GPU, Docker host, privileged action, mutation, or private control plane was used.

## Observed

| ID | Current result | Observation |
|---|---|---|
| VV-HOST-001 | PASS | Inventory current: 72 Host pages and 474 unique targets. |
| VV-HOST-002 | PASS | CLI registry check passed all 181 occurrences at clean current CLI master. |
| VV-HOST-003 | PASS | All 39 authored pages have synchronized persona metadata. |
| VV-HOST-004 | PASS | All nine review-context tests passed. |
| VV-HOST-005 | PASS | Review-server JavaScript syntax check exited 0. |
| VV-HOST-006 | PASS | OpenAPI definition is valid. |
| VV-HOST-007 | PASS within Host scope | Mint found 99 broken links in 10 non-Host files and none under `host/`. |
| VV-HOST-008 | FAIL | Zero Host missing-alt findings; 97 Host named-anchor findings and the shared dark-theme contrast failure remain. |
| VV-HOST-009 | PASS | Git whitespace check exited 0. |

## Evidence

- [Environment and target identity](./environment.txt)
- [Exit-status ledger](./results.tsv)
- Raw output: [`VV-HOST-001`](./VV-HOST-001.stdout.txt), [`VV-HOST-002`](./VV-HOST-002.stdout.txt), [`VV-HOST-003`](./VV-HOST-003.stdout.txt), [`VV-HOST-004`](./VV-HOST-004.stdout.txt), [`VV-HOST-005`](./VV-HOST-005.stdout.txt), [`VV-HOST-006`](./VV-HOST-006.stdout.txt), [`VV-HOST-007`](./VV-HOST-007.stdout.txt), [`VV-HOST-008`](./VV-HOST-008.stdout.txt), and [`VV-HOST-009`](./VV-HOST-009.stdout.txt)
- All attempt-03 stderr files are empty.

## Interpretation and limitations

The current local-safe result remains eight passes and one accessibility failure. The package is complete enough for an independent reviewer to reproduce and challenge those claims, but the target is not fully validated or accepted. Paid/privileged/runtime Host behavior and private product claims remain blocked, and acceptance remains an authorized human decision.

