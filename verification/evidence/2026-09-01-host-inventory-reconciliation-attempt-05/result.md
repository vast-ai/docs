# Host Docs source-inventory reconciliation — attempt 05 (failed qualification)

- Item: `VV-HOST-001`
- Method: unchanged local generated-inventory freshness check
- Repository HEAD at replay: `3b7e56f0db6588953589e0692e75b7274526d5f9`
- Inventoried source revision: `2ea65a084fcd82aa9db0c0cc4f47f165add0737a`
- Content fingerprint: `sha256:1f68160491e2cba46e6ac23cf66fbc3608536cd4eeaf6bbc63784b7cf9d1d81f`
- External, authenticated, Host, paid, WAN, privileged, or mutating action: none

## Preserved discrepancy

The previous current row still expected 474 targets and 176 commands from Attempt 04.
Those numbers correctly describe that retained 2026-08-27 replay, but they do not describe
the generated artifacts at the current source snapshot. The old attempt is preserved and
linked from the issue ledger; it is not relabeled as evidence for the new population.

## Command and observed result

```bash
python3 -B scripts/inventory_host_docs.py --check
```

- Process exit: `0`
- Standard output:

```text
Host Docs inventory is current: 72 pages, 484 unique targets; 182 commands reconcile across 5 execution-access groups.
```

- Standard error: empty
- Structural or local-reference issues: `0`

## Discovered generator defect

Independent review found that `scripts/inventory_host_docs.py` still hardcoded the
sentence “The 176 command targets…” in its Markdown renderer. Because `--check`
compared generated outputs against the same defective renderer, exit `0` did not prove
that every generated statement agreed with the 182-command data. This attempt is
therefore `FAIL` for VV-HOST-001 despite the observed process exit.

The failed record remains retained. The generator must derive that sentence from
`summary.command_count`, regenerate all five artifacts, and pass a new replay before the
current inventory row can be marked PASS.

## Artifact identities observed before correction

| Artifact | SHA-256 |
| --- | --- |
| `host-docs-verification-inventory.json` | `fd2c74def000a6064c178d084c83f643ddca79ce3fc8fa67818433a481c1b33f` |
| `host-docs-verification-inventory.csv` | `6c3b36c80baea484fc94f136ef985ccc4cf012b50c91e7c2f188c889e802656d` |
| `HOST-DOCS-VERIFICATION.md` | `3c3abf97ece2bcb69bcd105ff5f9b73bf3042360a83a0b75a9ac8f25181e5b7b` |
| `host-docs-command-access.json` | `6aee841dda870fcad4a76c7c51d70171dc34474dc4d435003ad0af7ff784e419` |
| `HOST-DOCS-COMMAND-ACCESS.md` | `a6e219e29ecfb1dc735673a20a1766f0c11ec9d861ed1547b0b5582c54c27394` |
| `scripts/inventory_host_docs.py` | `28163d31de1363892d550da2ef8b7d67f65ef609ca8e9c1e79f6ea7d8bb033ff` |

## Disposition and limits

`VV-HOST-001` is `FAIL` in this attempt because a stale generated sentence contradicted
the current 182-command population. The 484 targets and 182 unique commands are not
procedure executions and are not a readiness or pass-rate denominator. Procedure-level
V&V remains a separate 39-page, 97-test-set, 165-carrier model with its own retained
results.
