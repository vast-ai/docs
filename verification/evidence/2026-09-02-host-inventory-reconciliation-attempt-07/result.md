# Host Docs source-inventory reconciliation — attempt 07

- Item: `VV-HOST-001`
- Method: current generated inventory plus unchanged local freshness check
- Repository HEAD at replay: `3b7e56f0db6588953589e0692e75b7274526d5f9`
- Inventoried source revision: `2ea65a084fcd82aa9db0c0cc4f47f165add0737a`
- Current content fingerprint: `sha256:bd77e7dd7f66f18216fbb3404a08bcffd0a8bf7d417404bbe656d1c1d44bcbf7`
- Started: `2026-09-02T18:14:37Z`
- Finished: `2026-09-02T18:14:38Z`
- External, authenticated, Host, paid, WAN, privileged, or mutating action: none

## Reason for this replay

The Network and Ports page now explicitly requires two SSH sessions for the
foreground HTTP listener and listener check, followed by `Ctrl+C` and a
no-listener cleanup confirmation. That source correction added one unique
behavior claim without changing the command population. Attempt 06 remains the
evidence for its earlier 484-target snapshot; this attempt covers the current
485-target source state.

## Command and observed result

```bash
python3 -B scripts/inventory_host_docs.py --check
```

- Exit: `0`
- Standard output:

```text
Host Docs inventory is current: 72 pages, 485 unique targets; 182 commands reconcile across 5 execution-access groups.
```

- Standard error: empty.
- Current scope: 485 unique targets and 541 occurrences, including 182 commands,
  208 behavior claims, 77 errors or error categories, and 18 thresholds.
- Current command-access grouping: 55 Host-root, 21 Host-machine without root,
  and 106 requiring neither. No command is classified as paid-only or as
  requiring both payment and Host root. Five commands require an external
  client.
- Structural or local-reference issues: `0`.

## Current artifact identities

| Artifact | SHA-256 |
| --- | --- |
| `host-docs-verification-inventory.json` | `313cc09278bdc80e8e208eb5cd8bed80a8b67e8faf1d4d1c5a471818bca865f2` |
| `host-docs-verification-inventory.csv` | `390c3848fd542303c52b3a049f3326f25e4e010d3e9009d6b2ab3806fdf7c9ef` |
| `HOST-DOCS-VERIFICATION.md` | `d565ec23d914d20d8de2cde32eea05541795a53d7fcab5eb1a9a9f190510e896` |
| `host-docs-command-access.json` | `9ff7a172dbfc7ea8fd93006aea7639c918492eb720e8e348d112252f66699954` |
| `HOST-DOCS-COMMAND-ACCESS.md` | `ac2a297eba293167554d9b6594d95e06e6d8bec7832d46f5a137b735bfcfed7b` |
| `scripts/inventory_host_docs.py` | `db68ef3a0a4cb453a6ecdd961b630ab08fff7bf7adbd8467fb94c35d352b4710` |

## Disposition and limits

`VV-HOST-001` is `PASS` for the exact current source-discovery inventory and
five-group access reconciliation. The 485 targets and 182 commands are an
inventory population, not 485 independent shell runs and not a documentation
acceptance or readiness denominator.
