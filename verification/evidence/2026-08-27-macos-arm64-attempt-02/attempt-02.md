# Host Docs local-safe batch — attempt 02

- Kind: Verification and corrective retest
- Test basis: `VV-HOST-DOCS-2026-08-27-A` (expectations unchanged)
- Docs target: commit `9a872a4db52649835d77e87982ee642dad72b9ac`, tree `66d4e46d60b639f72e72c779ddc7e2867633d23b`
- Host content revision: `5088d76b89856185f3ab15a628e4152ff140ab26`
- Host content fingerprint: `sha256:bc59a848d0cb8698097787b911bb9e5b6875570c7c58815baa6d1f48b2504b4d`
- Vast CLI target: clean `master@ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd`, tree `f477989d0efd307154aeb623d6a1bfcee33e822a`
- Environment: macOS 26.5 arm64; Python 3.14.6; Bash 5.3.15; Node 24.19.0; npm 11.17.0; Mint 4.2.234; Git 2.51.0
- Performed: 2026-08-27T07:51:54Z–2026-08-27T07:52:06Z
- Mode: Executed (local-safe checks only)
- Result: 8 PASS, 1 FAIL for the nine local-safe items
- Evidence sensitivity: Internal; no credentials or protected host data captured

## Preconditions and corrective method

The tracked docs target and official Vast CLI checkout were clean. This retest kept the original expected results. It changed only the failed test context from attempt 01:

- inventory identity now uses the newest commit affecting the inventoried content roots plus an exact SHA-256 path/byte fingerprint;
- Mint ran against a clean `git archive` snapshot so untracked graph output could not contaminate results;
- the unchanged review-context tests ran with localhost bind permission.

No documented Host command was executed. No paid instance, credential, Vast account, GPU, Docker host, privileged command, account mutation, or private control plane was accessed.

## Observed

| ID | Current result | Observation |
|---|---|---|
| VV-HOST-001 | PASS | Inventory is current for all 72 Host pages and 474 unique targets; the post-evidence-commit retest confirms source identity is no longer self-invalidating. |
| VV-HOST-002 | PASS | CLI registry check passed all 181 occurrences: 179 registered invocations and two intentional command-family references, with zero actionable defects. |
| VV-HOST-003 | PASS | Persona check reported all 39 authored pages synchronized. |
| VV-HOST-004 | PASS | All nine review-context tests passed after localhost binding was authorized. |
| VV-HOST-005 | PASS | `node --check review-server.mjs` exited 0. |
| VV-HOST-006 | PASS | Mint reported the OpenAPI definition valid and exited 0. |
| VV-HOST-007 | PASS within Host scope | Clean-snapshot Mint found 99 broken links in 10 files, none under `host/`. Repository-wide link health remains failing outside the Host correction scope. |
| VV-HOST-008 | FAIL | The corrected Payment image has no missing-alt finding (0 Host missing-alt findings), but 97 Host named-anchor findings and the shared `#315FFF` dark-theme contrast failure remain. |
| VV-HOST-009 | PASS | `git diff --check` exited 0. |

## Evidence

- [Environment and target identity](./environment.txt)
- [Exit-status ledger](./results.tsv)
- Raw output: [`VV-HOST-001`](./VV-HOST-001.stdout.txt), [`VV-HOST-002`](./VV-HOST-002.stdout.txt), [`VV-HOST-003`](./VV-HOST-003.stdout.txt), [`VV-HOST-004`](./VV-HOST-004.stdout.txt), [`VV-HOST-005`](./VV-HOST-005.stdout.txt), [`VV-HOST-006`](./VV-HOST-006.stdout.txt), [`VV-HOST-007`](./VV-HOST-007.stdout.txt), [`VV-HOST-008`](./VV-HOST-008.stdout.txt), and [`VV-HOST-009`](./VV-HOST-009.stdout.txt)
- Stderr files beside each raw output preserve diagnostics. All attempt-02 stderr files are empty.

## Interpretation and limitations

This attempt supports eight defined local/static Host Docs claims at the exact targets above. It does not support a blanket claim that the Host Docs are fully validated or ready: the accessibility item remains failed, and host-runtime/private-product validation remains blocked.

The nonzero Mint exit codes are not treated as passes by themselves. VV-HOST-007 passes only because the complete retained link report contains no Host file; VV-HOST-008 remains failed because its retained findings are in scope.

## Follow-up

See [`../../issues.md`](../../issues.md). VV-ISSUE-001 through VV-ISSUE-003 are closed by this retest. VV-ISSUE-004 remains open for documentation-owner triage.

