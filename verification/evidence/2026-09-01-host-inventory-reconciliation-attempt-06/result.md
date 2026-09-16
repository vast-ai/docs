# Host Docs source-inventory reconciliation — attempt 06

- Item: `VV-HOST-001`
- Method: corrected generator plus unchanged local freshness check
- Repository HEAD at replay: `3b7e56f0db6588953589e0692e75b7274526d5f9`
- Inventoried source revision: `2ea65a084fcd82aa9db0c0cc4f47f165add0737a`
- Content fingerprint: `sha256:1f68160491e2cba46e6ac23cf66fbc3608536cd4eeaf6bbc63784b7cf9d1d81f`
- External, authenticated, Host, paid, WAN, privileged, or mutating action: none

## Preserved failure and correction

Attempt 05 exited 0 but failed qualification because the Markdown renderer still
hardcoded “176 command targets” while the current structured population contained 182.
The generator now renders this sentence from `summary.command_count`. All five generated
artifacts were regenerated before the unchanged check was replayed.

## Commands and observed results

```bash
python3 -B scripts/inventory_host_docs.py
python3 -B scripts/inventory_host_docs.py --check
```

- Generation exit: `0`; all five expected artifacts were written.
- Freshness-check exit: `0`.
- Freshness-check stdout:

```text
Host Docs inventory is current: 72 pages, 484 unique targets; 182 commands reconcile across 5 execution-access groups.
```

- Standard error: empty.
- Generated Markdown statement: “The 182 command targets are also grouped…”
- Structural or local-reference issues: `0`.

## Current artifact identities

| Artifact | SHA-256 |
| --- | --- |
| `host-docs-verification-inventory.json` | `fd2c74def000a6064c178d084c83f643ddca79ce3fc8fa67818433a481c1b33f` |
| `host-docs-verification-inventory.csv` | `6c3b36c80baea484fc94f136ef985ccc4cf012b50c91e7c2f188c889e802656d` |
| `HOST-DOCS-VERIFICATION.md` | `1c65a894903487d9373220148593cc0c66fa63d7bc1d6acb71cfd60714f56600` |
| `host-docs-command-access.json` | `6aee841dda870fcad4a76c7c51d70171dc34474dc4d435003ad0af7ff784e419` |
| `HOST-DOCS-COMMAND-ACCESS.md` | `a6e219e29ecfb1dc735673a20a1766f0c11ec9d861ed1547b0b5582c54c27394` |
| `scripts/inventory_host_docs.py` | `e5ffba8bf8eff3bd17ffb6adc87ad31e57f18cc7c73c5aabe497479a6461b954` |

## Disposition and limits

`VV-HOST-001` is `PASS` for the exact current source-discovery inventory and five-group
reconciliation. This correction prevents the generator from validating a stale prose
count against itself. The 484 targets and 182 commands are not procedure executions and
are not a readiness or pass-rate denominator.
