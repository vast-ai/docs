# Host installation NVIDIA visibility retained-evidence acceptance — attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-HOST-INSTALL-NVIDIA-SMI-RETAINED-01`
- Evidence ID: `EV-HOST-INSTALL-NVIDIA-SMI-RETAINED-01`
- Method: restricted, digest-bound session execution-record audit
- Canonical test-set SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- Restricted bundle: `h100x8-01-install-review-v1.1-2026-09-02.zip`
- Restricted bundle SHA-256:
  `61789455a18311803f778fd05caae0bdb98911432e7833670f76b8ac74b753bb`
- Representative target alias: `REPRESENTATIVE_H100_HOST`
- New Host execution: none

## Scope

This attempt reassesses five duplicate `nvidia-smi` command carriers using the
newly supplied v1.1 retained runtime evidence. It supplements, rather than
rewrites, the earlier installation retained-record audit.

## Evidence inspected

The restricted bundle binds these safe internal member handles:

- `evidence/post-cutoff/curated-execution-records/NVIDIA-COMMISSIONING.md`,
  SHA-256
  `fce28c2117ff8c9a30ff6bd531f1782803954643c2601cf5fede592bcc5f981c`;
- `evidence/post-cutoff/commissioning-outputs/09-load-driver-enable-persistence.txt`,
  SHA-256
  `ded5298be479be56b2b933db56eb52d565cb1b6506936ce2f8a2f04d762bc563`.

The retained binding contains the exact simple command `nvidia-smi` in a
sequential remote shell beginning with `set -euo pipefail`. Its bound output
contains a complete NVIDIA-SMI table showing all eight expected GPUs, followed
by an independent GPU query, a successful eight-GPU count gate, an active
persistence service, and an explicit no-Xid observation. Later retained
post-reboot query forms independently show every expected GPU again.

The source format did not serialize the nested numeric exit code. This record
therefore does not claim a captured `process_exit_code: 0`. The plain command
was not inside a conditional or pipeline, and the same `errexit` shell
continued through the subsequent query and count assertions. Together with
the command's own affirmative output, this is claim-suitable evidence that the
bounded command ran successfully and showed every expected GPU.

## Accepted mappings

| Command carrier | Location | Disposition |
| --- | --- | --- |
| `CLM-e28eb5444bf1cbda` | `host/headless-install.mdx:86` | `PASS` / score 3 |
| `CLM-6fa844203326e661` | `host/headless-install.mdx:89` | `PASS` / score 3 |
| `CLM-905d1c05a245588a` | `host/headless-install.mdx:237` | `PASS` / score 3 |
| `CLM-eed66ab11e34285f` | `host/installing-host-software.mdx:58` | `PASS` / score 3 |
| `CLM-f2432ac74fe70d7a` | `host/installing-host-software.mdx:65` | `PASS` / score 3 |

`DIRECT_FUNCTIONAL_EQUIVALENT_FULL` is the proof ceiling: the retained chain
combines an exact plain invocation with equivalent post-reboot query forms,
rather than preserving a standalone post-reboot plain invocation with a
serialized numeric exit.

For the inline failure-context carrier at `host/headless-install.mdx:89`, the
same retained chain includes an earlier NVIDIA communication failure,
diagnosis and corrective driver work, reboots, and the final affirmative GPU
visibility result. That supports the bounded retry-and-confirm behavior, but
not every possible `nouveau` diagnosis.

## Claim boundary

`PASS` and score 3 apply only to the shared command-level behavior: the exact
`nvidia-smi` invocation works and shows every expected GPU on the
representative Host.

This evidence does not validate the complete driver-install sequence, every
`nouveau` failure branch, every wizard checkpoint, the raw Vast installer,
the other fallback prerequisites, or whole-page acceptance. The four owning
steps and all surrounding branches, test sets, and pages retain their previous
statuses.

The source bundle remains restricted because it contains infrastructure and
device identifiers. Its bytes are not copied into public Git. Public
traceability is limited to the versioned source handles, cryptographic digests,
sanitized observations, and bounded interpretation above. This record neither
claims current live Host health nor authorizes a public listing or operational
change.
