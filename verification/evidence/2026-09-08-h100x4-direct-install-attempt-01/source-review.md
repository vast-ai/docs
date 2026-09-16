# Direct route and listing contract — independent review

2026-09-08. Independent read-only agent inspection, followed by main-agent inspection of the cited source and actual SHA checks. No API request, installer execution, or server listing proof.

The exact candidate matches the previously reviewed digest; see [retained hash command](source-hashes-01.json). Only its explicit late automatic `start_self_test.sh` invocation is omitted. The driver-install branch is skipped by `--no-driver`. Existing `/var/lib/docker` XFS/project-quota storage with a matching fstab entry takes the reuse branch at lines 1096–1118. `--no-partitioning` alone does not stop a loopback fallback if that reuse guard fails. Immediate recheck remains mandatory. The independent SSH-policy check cannot currently run because sudo authentication is unavailable; the downloaded installer helper has a fail-open download path at lines 1337–1345, so its presence cannot replace this check.

The direct route still installs packages/services, executes downloaded updater/daemon code, runs embedded NVML/NCCL diagnostics and a speed test. It is not an untouched TUI run and does not prove the normal automatic marketplace self-test. This attempt did not invoke any of those operations. Dynamic dependencies are not completely pinned by the candidate hash.

## Listing contract inspected, not executed

Canonical local Vast CLI revision: `18c4f2ccd6da587d5352f8741c71805a9a18e1ae`. The three inspected files have no working-tree modifications:

| Source | SHA256 | Meaning |
|---|---|---|
| `vastai/api/machines.py` | `6724080bf611369580e1328a17867383d1b3e72c2f459efcccb038e7109c2b92` | Lines 49–91: `PUT /machines/create_asks/`; `price_gpu` and `price_min_bid` per GPU/hour, `price_disk` per GB/month; `end_date` Unix epoch. Lines 5–17: single-machine owner readback. |
| `vastai/cli/commands/machines.py` | `64aef749a44e1c66742ba7796c6bcec9053ee87ae882bab783393bcbb2e29bbe` | Listing flags `-g`, `-s`, `-b`, `-e`; minimum chunk defaults to 1. Explicit `-v 0` avoids creating the optional separate volume offer. |
| `vastai/api/query.py` | `40be0f69f1e0b2128eb81ba8b366a57856f9013ddb68db091995124de9a3869b` | Lines 36–46: numeric expiry parsed as a Unix float. |

Approved future target values are GPU price 3, minimum bid 0.30, storage 0.50 and expiry 1789423200. Four GPUs at those per-GPU rates total USD 12/hour on demand and USD 1.20/hour bid floor. GPU grouping is separate; no all-four-only requirement was supplied. Do not silently introduce one. Bandwidth/discount defaults still require review before publication if they materially alter the approved terms.

A successful create response alone would not prove the applied terms. Retain exact target identity and independent machine/offer readback. The client forwards opaque server JSON; the local source does not establish all production disk/expiry readback field names. No listing command or API request was made in this attempt.
