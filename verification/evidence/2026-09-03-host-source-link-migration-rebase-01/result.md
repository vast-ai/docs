# Host Docs source-link migration rebase — attempt 01

- Attempt ID: `ATTEMPT-2026-09-03-HOST-SOURCE-LINK-MIGRATION-REBASE-01`
- Evidence ID: `EV-HOST-SOURCE-LINK-MIGRATION-REBASE-01`
- Method: static current-source identity rebase
- Canonical test-set SHA-256:
  `4cdce3a4f2ecd1dd4259682cdd7bc2b4a545bca4cb64afd87c32848176c4f301`
- New Host execution: none
- New command-result records: none
- Parent promotions: none

## Purpose

This append-only record rebases canonical page identities after a reviewed Host Docs
link migration. The migration redirects Host CLI and SDK links to the central CLI and
SDK reference routes, and updates the Docker runtime wording in Machine Errors. It
does not change a documented command's current carrier span, execution result,
semantic score, evidence outcome, or parent status.

## Rebased pages

| Page source | Current SHA-256 |
| --- | --- |
| `host/cli-api-sdk.mdx` | `ce65f03594bddf8ed403cbb4c60ae4be994ddd8f8be9b619a6b15b98032e25e0` |
| `host/fleet-operations.mdx` | `33412e18772fdf9e2999e71c930f4897cb45083c06784f7aece8a22e8932c6a1` |
| `host/host-teams.mdx` | `e9c42825cbbf3e5e225ec8f15e8a89c62a1cac3d297b92b4289ef0685d5ca7a3` |
| `host/hosting-overview.mdx` | `88e0a2df2ec978b1826cb9ad32ab7d86bdaadcaa3020ab0fb062224e113295c5` |
| `host/machine-errors.mdx` | `7c67af45e94568d951d77cd18c3d4a4265bf824a67c7421b983cf9d2179434f8` |
| `host/maintenance-windows.mdx` | `e4ea375afb171348fc4bc8907927a460dc84c78dd9ad47002ad9623d72bfdb52` |
| `host/market-metrics.mdx` | `791d3113ff1125ac17004141ed403d5cff790d9beb07615fb7e21568233ecb8e` |
| `host/pricing-your-listing.mdx` | `ea0746534b29c9a62fcfc5acb3fa89f60d1d56f34a556241dc7238aa279b436e` |
| `host/removing-recreating-machines.mdx` | `94f989704d9f8e939e7a83c22e5812a2b3a7b11c7b73b52d67bf35d7fb9e174f` |

## Binding checks

All 165 canonical command carriers remain text-contained in their declared current
source spans. All 468 canonical step bindings remain within their declared source
sections under heading-level scope. No source span or command text required a change.

## Limitations

This is an identity and link-migration rebase only. It is not runtime execution,
browser acceptance of the linked destinations, or semantic re-approval of the
procedures. Existing statuses, scores, evidence records, and parent outcomes remain
unchanged. The earlier 2026-09-03 source-binding rebase evidence remains retained and
is not overwritten.
