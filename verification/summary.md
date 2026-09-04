# Host Docs verification and validation summary

The current Host Docs V&V projection incorporates 58 retained attempts for
baseline `VV-HOST-DOCS-2026-08-27-A`. The evidence model contains 50 command
results, 42 procedure results, 38 direct-proof ceilings, and 101 direct
command-to-evidence bindings. All 58 attempts are hash-bound to 57 unique
retained artifacts. It also contains three material-claim result manifests and
one support-layer result with 33 exact bindings. The final reviewer-context
replay passes 24/24 tests, including fail-closed, sanitation, exact accounting,
scope/evidence-link, support-layer, Jira-snapshot, and feedback-import checks.

A current disposition exists for every projected target, making the
repository-local structure complete for traceability review. A disposition is
not successful semantic validation: `FAIL`, `BLOCKED`, and `UNVALIDATED` remain
visible, external workstreams remain incomplete, and no parent procedure or
page is promoted from command-only proof.

## Current projection

| Target status | Count |
|---|---:|
| PASS | 128 |
| FAIL | 5 |
| BLOCKED | 97 |
| UNVALIDATED | 747 |
| N/A | 27 |
| **Total** | **1004** |

The 1,004 targets are 40 top-level Host pages (39 authored and one generated),
101 test sets, 207 branches, 477 steps, and 179 command carriers. The 18 CLI and
15 SDK wrapper routes are separately governed central-reference support layers,
not additional Host workflows.

The separate material-claim register contains 1,687 claims: 167 PASS, 153 FAIL,
23 BLOCKED, and 1,344 UNVALIDATED. Citation status is 153 required-and-absent,
19 required-and-present-but-unverified, and 1,515 not required. These claim
counts do not change the 1,004-target hierarchy arithmetic.

| Command functional status | Count |
|---|---:|
| PASS | 84 |
| FAIL | 1 |
| BLOCKED | 7 |
| UNVALIDATED | 60 |
| N/A | 27 |
| **Total** | **179** |

Of the 152 applicable command carriers, 84 (55.3%) have current functional
PASS evidence. The other 68 (44.7%) comprise 7 BLOCKED, 60 UNVALIDATED, and
one observed FAIL.

| Command semantic disposition | Count |
|---|---:|
| Score 1 | 12 |
| Score 2 | 119 |
| Score 3 | 21 |
| Approved display-only N/A | 27 |
| **Total** | **179** |

A score describes how well a command and its observed behavior support the
surrounding documentation claim. It does not replace functional status. Score
3 requires current command-level functional PASS evidence with an exact-full
or explicitly equivalent-full proof role. Partial evidence cannot be promoted
through a parent result or a score label.

## What the evidence supports

- All 73 routable files—40 primary Host pages and 33 central-reference support
  layers represented by 18 CLI and 15 SDK wrapper routes—and 33 imported Host
  snippets are inventoried as 501 unique targets
  and 565 occurrences with no local structural or reference
  issue.
- All 193 command targets reconcile into five execution-access groups: 0
  paid+root, 2 paid-only, 54 Host-root/privileged, 22 Host-machine without
  root, and 115 requiring neither. Five commands require an external client;
  account, credential, mutation, and environment gates remain visible per
  command.
- All 201 documented Vast CLI occurrences conform to the recorded clean CLI
  baseline; 199 pass directly and two are intentional command-family
  references.
- Persona synchronization covers all 40 primary pages. Reviewer-context
  behavior passes 24/24 tests after the current schema/scope changes; syntax,
  OpenAPI, Host-scope links, and whitespace retain only the status of their
  latest explicitly linked attempts.
- The direct-proof model is current: 50 command results and 42 procedure
  results feed 38 proof ceilings and 101 direct bindings. Evidence roles and
  ceilings must agree before a command can receive score 3.
- The digest-bound restricted v1.1 installation record supports five duplicate
  `nvidia-smi` GPU-visibility carriers at command level. Its missing serialized
  nested exit remains explicit, no exit code is invented, and broader
  installation steps and pages remain non-passing.
- Three authorized-Host bounded read-only attempts support 12 command carriers
  with zero parent promotions. Eleven are point-in-time partial proofs; the VM
  `check` query is exact only for its reported status.
- A documented container GPU-injection form using `--gpus all` failed with exit
  125 on the authorized idle Host. Docker directed the operator to the
  registered NVIDIA runtime. The docs now use `--runtime=nvidia`, and both a
  candidate run and the corrected published form passed while enumerating the
  same four GPUs. The three corrected command carriers are PASS with score 3;
  the separate GPU-burn command and parent troubleshooting procedures remain
  non-passing.
- Manual `vastai dump-logs <machine>` execution passed for two command
  carriers and produced a parseable four-file bundle with no collection
  errors. The bundle remains restricted pending human review before external
  sharing.
- The exact `cat vast_host_install.log` command passed from the confirmed
  installer launch directory. Its raw output remains private because automated
  review gates found possible credential, address, and hexadecimal markers.
- The bounded equivalent of the documented self-test log follower passed for
  two carriers. It proved the path, privileges, follow behavior, interruption,
  and cleanup, but no self-test was active, so both carriers remain semantic
  score 2 and their parent procedures were not promoted.
- The exact kernel-log follower passed at command-mechanics level in a bounded
  Host run. A concurrent transient workload made the environment non-controlled,
  so Host execution was paused. No matching kernel event was reproduced; the
  carrier remains score 2 and no parent target was promoted.
- The exact Market Metrics REST request reached the endpoint and returned
  structured JSON, but the configured client credential lacks machine-read
  permission. The command is BLOCKED with score 2; a transport exit of zero is
  not treated as a successful API result.
- `pip install --upgrade vastai` passed in a clean disposable macOS arm64
  virtual environment and the environment's own CLI reported version 1.5.6.
  The earlier DNS-blocked attempt and its rejected fall-through to a global
  executable remain retained.
- `vastai set api-key <API_KEY>` completed with a synthetic value in an
  isolated configuration directory, but Vast CLI 1.5.6 created the credential
  file with mode `0644` under normal umask `022`. The command is current FAIL
  with score 1; no real credential or Host operation was used.
- The Host-local `dump-logs --include-local-host-artifacts` attempt stopped
  before installation because the Host lacks the Python venv/ensurepip
  component. No operating-system package was installed, attempt-owned files
  were removed, and both carriers remain UNVALIDATED. The setup attempt itself
  is BLOCKED.

## Host self-test and paid behavior

The official Host self-test is a Host-owner workflow run against the Host's own
hardware. It is not gated on approval for a paid renter test. The end-to-end
workflow still needs Host-owner API authentication because it selects and
creates its temporary diagnostic workload through the control plane. The
available client credential does not provide that Host-owner permission.
Billing behavior was not assessed, so this package makes no billing claim.

Paid renter-side behavior is a separate validation class. It remains gated by
the relevant client authority, budget, marketplace availability, and cleanup
requirements and must not be used as a substitute for Host self-test evidence.

## Exceptions and residual risk

- Accessibility remains a separate repository QA concern. The corrected
  named-anchor source defect passes the final retained replay; the shared
  `#315FFF` dark-theme contrast failure remains unresolved. This QA result is
  not one of the 1,004 procedure-projection statuses above.
- Mint reports 99 broken links in 10 non-Host files. This does not fail the
  Host-scope item, but repository-wide link health is not passing.
- The official Host self-test remains blocked pending securely supplied
  Host-owner API authentication. The earlier attempt stopped at
  `api_permission_failed` before the diagnostic workload was created.
- External-WAN behavior, GPU burn/load, NVSwitch-specific behavior, repaired
  VM/IOMMU sequences, incident-only paths, and disruptive or state-changing
  operations still require their exact environment and explicit authority.
- Paid renter-side behavior and private product-policy claims remain separate
  unfinished classes.
- The same agent prepared and executed much of this package. Independent human
  review and acceptance remain open.

## Evidence index

- [Plan and reviewer workflow](./README.md)
- [Inventory and current status](./inventory.md)
- [Issue, correction, and retest ledger](./issues.md)
- [Attempt 01, preserved failures](./evidence/2026-08-27-macos-arm64-attempt-01/attempt-01.md)
- [Attempt 02, corrective retest](./evidence/2026-08-27-macos-arm64-attempt-02/attempt-02.md)
- [Attempt 03, final clean-tree replay](./evidence/2026-08-27-macos-arm64-attempt-03/attempt-03.md)
- [Attempt 04, command-access reconciliation replay](./evidence/2026-08-27-macos-arm64-attempt-04/attempt-04.md)
- [Attempt 05, preserved stale-generator false positive](./evidence/2026-09-01-host-inventory-reconciliation-attempt-05/result.md)
- [Attempt 06, corrected current inventory replay](./evidence/2026-09-01-host-inventory-reconciliation-attempt-06/result.md)
- [Attempt 07, prior 485-target inventory replay](./evidence/2026-09-02-host-inventory-reconciliation-attempt-07/result.md)
- [Superseded 39-page reviewer-clarity replay](./evidence/2026-09-03-host-reviewer-clarity-attempt-01/result.md)
- [Source-binding correction rebase](./evidence/2026-09-03-host-source-binding-rebase-01/result.md)
- [Central-link migration identity rebase](./evidence/2026-09-03-host-source-link-migration-rebase-01/result.md)
- [Current repository-local scope and status rebase](./evidence/2026-09-03-host-repository-rebase-01/result.md)
- [Initial command-proof reviewer correction](./evidence/2026-09-03-host-command-proof-reviewer-attempt-01/result.md)
- [Final command-proof reviewer retest](./evidence/2026-09-03-host-command-proof-reviewer-attempt-02/result.md)
- [Third-party D1-D4 remediation replay](./evidence/2026-09-01-host-third-party-remediation-attempt-01/result.md)
- [Restricted installation GPU-visibility acceptance](./evidence/2026-09-02-host-install-nvidia-smi-retained-01/result.md)
- [Authorized-Host bounded read-only attempt 01](./evidence/2026-09-02-host-safe-readonly-attempt-01/result.md)
- [Authorized-Host bounded read-only attempt 02](./evidence/2026-09-02-host-safe-readonly-attempt-02/result.md)
- [Authorized-Host bounded read-only attempt 03](./evidence/2026-09-02-host-safe-readonly-attempt-03/result.md)
- [Host self-test authorization attempt](./evidence/2026-09-02-host-self-test-attempt-01/result.md)
- [Documented GPU-injection failure](./evidence/2026-09-02-host-gpu-injection-attempt-01/result.md)
- [GPU-injection correction candidate](./evidence/2026-09-02-host-gpu-injection-attempt-02/result.md)
- [Corrected published GPU-injection retest](./evidence/2026-09-02-host-gpu-injection-attempt-03/result.md)
- [Manual CLI diagnostic bundle](./evidence/2026-09-02-cli-dump-logs-attempt-01/result.md)
- [Host installer log command](./evidence/2026-09-02-host-installer-log-attempt-01/result.md)
- [Bounded Host self-test log follower](./evidence/2026-09-02-host-self-test-log-follow-attempt-01/result.md)
- [CLI install blocked attempt](./evidence/2026-09-02-cli-install-attempt-01/result.md)
- [CLI install successful retest](./evidence/2026-09-02-cli-install-attempt-02/result.md)
- [Host-local diagnostic bundle blocker](./evidence/2026-09-02-host-local-bundle-attempt-01/result.md)
- [Bounded Host kernel-log follower](./evidence/2026-09-02-host-kernel-log-follow-attempt-01/result.md)
- [Market Metrics REST authorization blocker](./evidence/2026-09-02-market-metrics-rest-attempt-01/result.md)
- [Vast CLI API-key file-permission failure](./evidence/2026-09-02-cli-set-api-key-permissions-attempt-01/result.md)

## Acceptance

Open. This package does not self-approve the work; an authorized reviewer must
record acceptance, rejection, or conditions.
