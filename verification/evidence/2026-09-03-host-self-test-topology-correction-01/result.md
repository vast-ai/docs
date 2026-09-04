# How to Self-Test command-topology correction

- Attempt: `ATTEMPT-2026-09-03-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01`
- Evidence: `EV-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01`
- Jira / pull request: `CON-1518` / Host Docs PR #185
- Page: `/host/how-to-self-test` (`host/how-to-self-test.mdx`)
- Test set: `TS-ST-E01`
- Method: `STATIC_SELF_TEST_COMMAND_TOPOLOGY_CORRECTION_RETEST`
- Outcome: `PASS` for the bounded repository-local topology and accounting correction only

## Defect retained

The active generated topology placed all three exact command carriers below
`ST-E01-normal-s02`, a narrative checkpoint for **What Self-Test Checks**. That
made the reviewer show setup and action commands as if the checkpoint owned
them. The command observations themselves were not invalidated by this
structural defect, but their active target coordinates and affected rollups
needed correction.

The retained 39-page `verification/procedure-baseline-p1.json` draft and every
historical attempt evidence artifact remain unchanged. The current generated
index rekeys nine historical procedure-result pointers so that the retained
observations remain reachable from the current canonical command targets. Each
affected attempt's accounting-correction chain points to this attempt.

## Exact source-to-step mapping

| Command ID | Exact documented command | Heading and source | Correct branch / step | Step role | Preserved command status |
|---|---|---|---|---|---|
| `CLM-b3cd48630e5f2b0c` | `vastai set api-key <API_KEY>` | **Before You Run It**, line 29 | `ST-E01-normal` / `ST-E01-normal-s01` | setup | `FAIL` |
| `CLM-3ba3b25f5c3ddac1` | `vastai self-test machine <machine_id>` | **Run The Test**, line 79 | `ST-E01-normal` / `ST-E01-normal-s03` | action | `UNVALIDATED` |
| `CLM-3fa5d5948b34fc6a` | `vastai self-test machine <machine_id> --support-bundle-dir /path/to/output` | **Run The Test**, lines 85-86 | `ST-E01-bundle-dir` / `ST-E01-bundle-dir-s02` | action | `BLOCKED` |

`ST-E01-normal-s02` is restored to its exact **What Self-Test Checks** scope,
lines 33-64, with no command children. All three carriers use
`EXECUTABLE_TEMPLATE_REQUIRED`; a misplaced carrier is no longer represented
as a source defect.

## Status and evidence boundary

Relocation does not claim that any command newly ran:

- The API-key command remains `FAIL` because the retained isolated macOS check
  observed a credential file with mode `0644`.
- The normal self-test command remains `UNVALIDATED`; no suitable retained
  execution proves its runtime behavior.
- The support-bundle form remains `BLOCKED` by the exact unavailable Host-owner
  machine-read permission recorded in its retained attempt.

Required-child recomputation moves the step-level `FAIL` from
`ST-E01-normal-s02` to `ST-E01-normal-s01`, changes
`ST-E01-bundle-dir-s02` and its branch from `UNVALIDATED` to `BLOCKED`, and
leaves `TS-ST-E01` and the page `FAIL`. Across the 1,004-target projection this
changes the status distribution to 128 `PASS`, 5 `FAIL`, 97 `BLOCKED`, 747
`UNVALIDATED`, and 27 `NOT_APPLICABLE`.

## Retained repository checks

The following safe checks were run from the documentation repository:

```text
python3 -m unittest scripts.test_reconcile_host_vv_repository
python3 scripts/reconcile_host_vv_repository.py --check
```

Both completed successfully after regeneration. The focused regressions check
the three exact command-to-step mappings, clean checkpoint scope, preserved
command statuses, 11-target correction record, nine rekeyed historical
procedure bindings, correction-chain continuity, aggregate rollups, projection
counts, generator idempotence, and the unchanged retained P1 baseline hash.

## Limitations and next actions

This is static source, topology, and accounting evidence. It did not use a real
credential or execute any Host/API, paid, WAN, privileged, mutating,
destructive, or workload-affecting operation. It does not turn documentation
text into evidence for itself, does not resolve the retained API-key permission
failure, and does not prove normal or support-bundle self-test runtime success.

- CLI credential owner: correct the credential-file permissions and retain
  cross-platform no-network retests without real credentials.
- Authorized Host operator: when separately approved and the exact credential,
  idle machine, spend, and cleanup prerequisites are available, run and retain
  the normal and support-bundle paths on the supported platforms.
