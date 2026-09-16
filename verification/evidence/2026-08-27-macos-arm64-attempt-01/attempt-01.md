# Host Docs local-safe batch — attempt 01

- Kind: Verification
- Test basis: `VV-HOST-DOCS-2026-08-27-A`
- Docs target: commit `befc430c342509f31fae50708441dd60cbccd2e1`, tree `ee3bf3db5ce785d6fcc9a5a4391489b91e2b1ca7`
- Host content revision: `5088d76b89856185f3ab15a628e4152ff140ab26`
- Vast CLI target: clean `master@ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd`, tree `f477989d0efd307154aeb623d6a1bfcee33e822a`
- Environment: macOS 26.5 arm64; Python 3.14.6; Bash 5.3.15; Node 24.19.0; npm 11.17.0; Git 2.51.0
- Performed: 2026-08-27T07:48:10Z–2026-08-27T07:48:21Z
- Mode: Executed (local-safe checks only)
- Result: FAIL with two environment/method blockers
- Evidence sensitivity: Internal; no credentials or protected host data captured

## Preconditions and method

The tracked docs target and Vast CLI checkout were clean. The committed runner executed only the nine frozen local-safe items and captured each command's stdout, stderr, timestamps, and exit code. It did not run documented Host commands or access a paid instance, credential, Vast account, GPU, Docker host, or private control plane.

## Observed

| ID | Attempt result | Observation |
|---|---|---|
| VV-HOST-001 | FAIL | Inventory `--check` reported the JSON and Markdown stale because generated source identity used repository `HEAD`; the evidence-only baseline commit moved HEAD without changing inventoried Host content. |
| VV-HOST-002 | PASS | CLI registry check passed all 181 occurrences at clean current CLI master. |
| VV-HOST-003 | PASS | Persona check reported 39 synchronized pages. |
| VV-HOST-004 | BLOCKED | All nine review-context tests were prevented from binding `127.0.0.1` by sandbox `EPERM`; no application assertion was evaluated. |
| VV-HOST-005 | PASS | `node --check review-server.mjs` exited 0. |
| VV-HOST-006 | PASS | Mint reported the OpenAPI definition valid and exited 0. |
| VV-HOST-007 | BLOCKED | Mint stopped while parsing user-owned untracked `graphify-out` Markdown before it completed the clean tracked-tree link analysis. |
| VV-HOST-008 | FAIL | Mint retained the known shared dark-theme color failure and Host named-anchor findings. It did not report the corrected `host/payment.mdx` image as missing alt text. |
| VV-HOST-009 | PASS | `git diff --check` exited 0. |

## Evidence

- [Environment and target identity](./environment.txt)
- [Exit-status ledger](./results.tsv)
- Raw output: [`VV-HOST-001`](./VV-HOST-001.stdout.txt), [`VV-HOST-002`](./VV-HOST-002.stdout.txt), [`VV-HOST-003`](./VV-HOST-003.stdout.txt), [`VV-HOST-004`](./VV-HOST-004.stdout.txt), [`VV-HOST-005`](./VV-HOST-005.stdout.txt), [`VV-HOST-006`](./VV-HOST-006.stdout.txt), [`VV-HOST-007`](./VV-HOST-007.stdout.txt), [`VV-HOST-008`](./VV-HOST-008.stdout.txt), and [`VV-HOST-009`](./VV-HOST-009.stdout.txt)
- Stderr files beside each raw output preserve diagnostics and are intentionally not merged into stdout.

## Interpretation and limitations

This attempt provides current positive evidence for five items and current failure evidence for accessibility. It does not support a pass for inventory freshness, review-context behavior, or Host link integrity. The failures and blockers are preserved rather than rewritten. Corrections and a fresh attempt are required.

The run remains local/static evidence. It does not support Host runtime, paid self-test, privileged setup, account mutation, or private product-policy claims.

## Follow-up

See [`../../issues.md`](../../issues.md) for the target-identity correction, clean-snapshot Mint correction, authorized local-bind rerun, and unresolved accessibility findings.

