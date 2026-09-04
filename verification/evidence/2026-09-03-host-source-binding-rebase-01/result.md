# Host Docs source-binding rebase — attempt 01

- Attempt ID: `ATTEMPT-2026-09-03-HOST-SOURCE-BINDING-REBASE-01`
- Evidence ID: `EV-HOST-SOURCE-BINDING-REBASE-01`
- Method: static current-source binding rebase
- Canonical test-set SHA-256:
  `121d56294902ed3eb119e701383f2802c3c0ac207784a11f97f991e7582dff6e`
- New Host execution: none
- New command-result records: none
- Parent promotions: none

## Purpose

This append-only audit repairs stale line coordinates in the active Host Docs V&V
snapshot after current-source line movement. It also narrows two Hosting Overview
handoff steps to what their source actually says. Historical attempts, command
results, and score values remain unchanged.

## Binding changes

The snapshot rebases these command carriers to their exact current source spans:

| Carrier | Current source span |
| --- | --- |
| `CLM-a1ecff41b73b1413` | `host/common-errors-diagnostics.mdx:191-194` |
| `CLM-6ddedf5cc9aced91` | `host/common-errors-diagnostics.mdx:183` |
| `CLM-2c2c7d94c1bd259f` | `host/machine-errors.mdx:132-135` |
| `CLM-885315f98e7e1dd9` | `host/machine-errors.mdx:150-152` |
| `CLM-0bae256f5a9e7bc7` | `host/machine-errors.mdx:165-166` |
| `CLM-d2cb5452a0e2063a` | `host/machine-errors.mdx:186-188` |
| `CLM-a4c552f07e09986c` | `host/machine-errors.mdx:201-203` |
| `CLM-a71cddd213a49f46` | `host/machine-errors.mdx:213` |
| `CLM-720bb6982a2e7948` | `host/machine-errors.mdx:225-228` |
| `CLM-3959b3397aeb7b35` | `host/machine-errors.mdx:250-252` |
| `CLM-9e9b545d694a34cc` | `host/machine-errors.mdx:332` |
| `CLM-ffda5e2c291c470e` | `host/vms.mdx:109` |

The audit also rebases `VM-E02-S01` and `VM-E02-S03` to
`host/vms.mdx:67-71`, and `VM-E02-S05` to `host/vms.mdx:96-98`.

`HOV-P01-S04` now records only the Installing Host Software handoff and
`HOV-P01-S05` only the How to Self-Test handoff. The parent route no longer claims
headless-install success, downstream operations, paid-workload gates, or WAN gates.

## Limitations

This is source-coordinate and wording maintenance, not functional execution. It does
not run a command, establish a Host state, infer an exit status, raise a semantic
score, promote a command or parent target, or validate the new untracked Volume
Offers page. That page remains outside this 39-page snapshot until separately
inventoried and reviewed.

The four observed canonical source-file hashes remain current in this rebase:

- `host/common-host-questions.mdx`: `d176fcf45a2948f427b13ae186c00da4051a8d6586592da1d4b16b436c960f3b`
- `host/glossary.mdx`: `2ed79adfeb63b2ad61c232c87a7c9967869a0eb6d37a92eecfb7133613765e80`
- `host/hosting-overview.mdx`: `a17c61a26a3b3e9aad610d7d57e36cbd6cd7e91b3e8f9a81fa028d751dd047ab`
- `host/storage-setup.mdx`: `601ac00ccff535b607e96cf4242568e798f4e6da9dc481f0c8f2d71ec230ab74`
