# Host installation retained-record audit — attempt 01

- Attempt ID: `ATTEMPT-2026-09-01-HOST-INSTALL-RETAINED-RECORD-AUDIT-01`
- Method: audit of existing, local, digest-bound installation records
- Canonical test-set snapshot SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- Canonical result snapshot SHA-256 before this audit:
  `9e87b532fd12e53018d8e5981964d56b93f0172a255305169a5576144a4dfba8`
- Canonical score snapshot SHA-256 before this audit:
  `55198b7328d2338d4d1b1b02d2e037680aad2a8ba347f528c67a0101c09557c7`
- Representative target alias: `VENTER_H100_REPRESENTATIVE`
- New Host, installer, SSH, network, API, paid, privileged, or mutating execution:
  none

## Scope

This audit tested whether an existing installation record can qualify the ordered
commands and behavior claims on `/host/headless-install` and
`/host/installing-host-software`. It did not treat command strings as independent tests.

| Scope | Count |
| --- | ---: |
| Pages | 2 |
| Test sets | 4 |
| Branches | 25 |
| Ordered steps | 54 |
| Command carriers | 40 |
| Executable or blocked carriers | 34 |
| Display-only / approved N/A carriers | 6 |

Before this audit, the 40 command carriers were 10 `BLOCKED`, 24 `UNVALIDATED`, and
6 `NOT_APPLICABLE`; all 34 numeric semantic records had score 2.

## Source identity and publication boundary

Ten allowlisted local records were hashed and inspected through a private source
crosswalk. Their current byte states comprise three tracked-but-modified files and seven
untracked files; none is byte-identical clean evidence from the source repository's
published `main` revision. The source bytes therefore support only a local,
digest-bound audit. They must not be described as GitHub-main evidence.

| Private handle | SHA-256 | Classification |
| --- | --- | --- |
| `VENTER-E01` | `e805b870c84aad4f6870bb98f04d2f2c62bf6fb44ad0d609ab6e8700d524259e` | postcondition only |
| `VENTER-E02` | `8dafb22d23431cfaa26f570ddb16efab780448a4b1ee984398a3c516ea856df2` | postcondition only |
| `VENTER-E03` | `349945b08857a7fb964c47f1a3741bb6da91c2afddf37ad93aed546917f6f4f9` | authorization/context |
| `VENTER-E04` | `00c8662f6cc5e14c5c3bae8f5cfe41e1ced47e89cdd5a7018f7a9c79b20a9953` | authorization/context |
| `VENTER-E05` | `fa6dcae3f51197d8790a16cffdc21436fa15d69ae9ebd6c68af8212d2601147c` | postcondition only |
| `VENTER-E06` | `1af7f474241ee9714472376e006214da1a6a12cd025e744e33860a5b386e0891` | postcondition only |
| `VENTER-E07` | `e5543d6e124d15049b1e5b1212cf6cac67268319e7ffd7aff4a8b70334d7c289` | semantic-equivalent subset |
| `VENTER-E08` | `e90fc6f74d34313165c4ae60ddd46a4d3323aa85c1450f0680eac4ef02b90460` | authorization/context |
| `VENTER-E09` | `d50033984a189b72ff6d54ac8c4023438ae8c8378a5f09df5c26c9427fe216cb` | authorization/context |
| `VENTER-E10` | `dfe27673f8b1739349c9f4270b6b5e46fbde36eec7b5fb011af0206a900bddb8` | unusable for installation behavior |

No address, hostname, user, account, machine identifier, serial, credential, setup key,
raw screenshot, autoinstall input, or private build material is copied into this record.

## Evidence classification

| Maximum claim from one allowlisted record | Records |
| --- | ---: |
| Exact execution | 0 |
| Semantically equivalent subset | 1 |
| Postcondition only | 4 |
| Authorization/context only | 4 |
| Unusable for installation behavior | 1 |

The historical gate records establish identity, authority, HOLD state, and that no disk
write had yet occurred. They do not prove later installation. Later state summaries show
relevant Ubuntu, NVIDIA, storage, Docker, service, port-range, workload, and self-test
postconditions, but they omit the complete action chain that produced that state.

## Command-level assessment

The strongest observation is the target-bound post-reboot NVIDIA state: every expected
GPU is reported through the NVIDIA management utility after two reboots. This is highly
relevant to `HDL-E01-S11` and carriers `CLM-e28eb5444bf1cbda` and
`CLM-6fa844203326e661`. It is not promoted to command `PASS` or score 3 because the
allowlisted raw record does not retain the exact argv, process exit, or an unbroken link
to the documented package-selection and installation sequence. Those two carriers and
their step remain `UNVALIDATED` / score 2.

The records also provide partial postcondition support for:

- the Docker XFS/project-quota mount architecture, but not the documented destructive
  single-device partition/format commands or quota accounting/enforcement output;
- persistence after reboot, but through a different systemd implementation rather than
  the documented root crontab carrier;
- a configured daemon range and later service state, but not the documented write,
  restart, and log-observation sequence;
- stronger full-range external TCP/UDP behavior, but only as a later summary without the
  admitted sender, receiver, exit, correlation, and cleanup records;
- the final after-install service/storage/range/GPU goals, but not one ordered composite
  execution with per-command outcomes.

No allowlisted record identifies whether the TUI or raw installer route ran, the exact
installer revision/hash, masked argv, setup-page/account context, installer exit,
registration transition, or setup-key/history/log cleanup. The installer carriers remain
`BLOCKED` and score 2.

## Integrity observation

The allowlisted integrity summary reports eight action-index rows and 187 command-index
rows with zero reported validation errors. The stated total of 195 is arithmetically
reproduced as `8 + 187`; this audit did not inspect 195 individual manifests. The reported
eight-of-19 top-manifest mismatch cannot be reproduced from the allowlisted inputs because
the top manifest and its expected comparison basis are absent.

## Disposition

- Evidence audit: `PASS` for complete classification of the 40 scoped carriers against
  the ten allowlisted records.
- Installation command execution: no new `PASS`.
- Functional counts: unchanged.
- Semantic scores: unchanged.
- Page, test-set, branch, and step rollups: unchanged.
- Evidence-package acceptance: unchanged; human acceptance and missing live gates remain.

An independent review proposed promoting the two post-driver NVIDIA carriers. The final
audit rejected that promotion because the retained record does not meet the existing
command-level provenance standard. This disagreement is preserved rather than silently
resolved in favor of a stronger claim.

## Evidence needed for promotion

A future sanitized derivative can support exact command changes only when it binds:

1. the selected installer route and immutable installer identity;
2. masked exact argv or an explicitly justified equivalent method;
3. target alias and prerequisite snapshot;
4. ordered timestamps and per-command exits;
5. bounded observations and expected-result comparison;
6. setup-key, history, log, session, listener, and temporary-file cleanup as applicable;
7. registration, service, storage, quota, port, GPU, self-test, and listing boundaries;
8. a digest-bound source crosswalk retained outside public Git.

The two independent audit reports and the exact command map are retained locally under
the orchestration run. Their SHA-256 values are:

- command map: `7c7a9b49b95dd5cf5f6526fcc8f93fc793940fdde60b48f66a4106ff6476f9f3`;
- source-evidence audit: `c23a0155eb25330a05a9984569d505474fff3141a42ab9b13789e0030112a1b8`;
- adversarial review: `d5db2c611d687141086a9e6af4be1d45d5fe262f5f2ef0e1c41ee7b405f00239`.

This record contains the sanitized decision and claim boundary. It does not publish the
private crosswalk or source material.
