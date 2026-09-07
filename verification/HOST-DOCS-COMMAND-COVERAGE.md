# Host Docs command V&V coverage

Coverage is counted over the 179 command carriers in
`host-docs-test-sets.json`. Commands remain grouped in their page, procedure,
branch, and ordered-step context. A help/signature check proves only registry or
static conformance; it does not establish runtime product behavior.

## Current functional disposition

| Current status | Command carriers |
| --- | ---: |
| `PASS` | 84 |
| `BLOCKED` | 7 |
| `UNVALIDATED` | 60 |
| `NOT_APPLICABLE` | 27 |
| `FAIL` | 1 |
| **Total** | **179** |

Each carrier has one exact current projection record. Its status is supported
by the current reconciliation evidence and must agree with the execution status
stored beside its semantic assessment. Superseded and disqualified attempts
remain visible in history but cannot drive the current projection.

Of 152 applicable executable carriers, 84 are current PASS (55.3%) and 68
remain non-passing (44.7%): 7 BLOCKED, 60 UNVALIDATED, and one FAIL. The 27
approved display-only carriers are excluded from this completion rate.

## Contextual semantic assessment

| Assessment | Command carriers |
| --- | ---: |
| Score 1 — failed, irrelevant, unsafe, obsolete, or materially unsupported | 12 |
| Score 2 — relevant but partial, conditional, static-only, or incomplete | 119 |
| Score 3 — representative evidence strongly supports the exact page claim | 21 |
| Approved display-only `NOT_APPLICABLE` | 27 |
| **Total** | **179** |

Semantic score and functional status are deliberately separate. The shared
semantic-assessment evidence binds all 179 current carriers without pretending
that the assessment itself executed them: its 152 numeric targets remain
`UNVALIDATED` as assessment evidence, while its 27 canonical display targets are
`NOT_APPLICABLE`. Functional PASS/BLOCKED/UNVALIDATED/N/A comes from the separate
current-status projection and retained evidence.

Direct evidence uses 101 command-specific bindings backed by 38 evidence-owned
proof ceilings. A score-side role must equal its evidence ceiling, so static or
partial evidence cannot be relabelled into full score-3 proof. Separate
repository-local records bind 1,687 material-claim dispositions and all 33
CLI/SDK support layers; those records do not turn static structure into runtime
or owner acceptance.

The 17 Host Teams catalog tokens are static/catalog score-2 assessments. Their
`PASS` status means the declared CLI help/catalog path was observed; it does not
claim that account permissions, billing, or mutation behavior ran successfully.

## Retained corrections and limitations

- Three earlier VM scores remain withdrawn from runtime qualification because
  the observed Host had an unsuitable VM/IOMMU configuration. Their current
  semantic score 2 does not restore the disqualified execution evidence.
- The original multi-target Hardware Prep mount carrier is retained as `STALE`.
  Its split replacement form passed the corrected read-only inventory procedure.
- One conditional Fabric Manager score-3 claim was corrected to score 2 because
  a non-NVSwitch observation cannot prove the executable NVSwitch branch.
- Three Market Metrics carriers are score 2 because the retained run exercised
  only one alternative in each multi-command carrier. Their direct evidence is
  explicitly `DIRECT_FUNCTIONAL_PARTIAL`, not full score-3 proof.
- Two live-follow score-1 findings are retained as superseded history. Corrected
  bounded stop/exit wording and bounded Host execution now support
  command-mechanics PASS at score 2. No active self-test or matching kernel
  event was reproduced, and no parent target was promoted.
- Five duplicate `nvidia-smi` carriers now have command-level PASS and score 3
  from a digest-bound restricted installation record. The equivalent-full
  proof discloses its missing serialized nested exit and does not promote the
  broader driver, wizard, fallback, step, branch, test-set, or page claims.
- The bare `tcpdump` token is an approved display-only N/A carrier. The owning
  external UDP/WAN procedure remains blocked and is not silently passed.
- Twelve Phase 24 carriers passed on the authorized Host using bounded read-only
  collection only. Eleven carry partial direct proof and do not promote their
  parent step, branch, test set, or page; the exact VM `check` carrier is the
  one exact-full result. No state-changing, paid, external-WAN, or incident-path
  behavior was exercised.
- One Host self-test preflight reached `select_offer` and stopped with
  `api_permission_failed` before the create-instance stage. The exact
  support-bundle-directory form is retained as score-2 partial evidence for two
  blocked carriers; it is not runtime success or billing evidence.
- The exact Market Metrics REST carrier reached the endpoint but is BLOCKED by
  the configured client credential's missing machine-read permission. Its
  structured authorization response supports score 2 only.
- Host-local bundle setup is BLOCKED on missing isolated Python venv support;
  because the bundle command never ran, its two carriers remain UNVALIDATED.
- Vast CLI 1.5.6 completed `vastai set api-key` in an isolated environment but
  created its credential file with mode `0644` under normal umask `022`. This
  unsafe result is current FAIL with score 1 pending a product correction and
  retest; no real credential was used.

## Highest-value remaining runs

1. After VM/IOMMU repair and reboot, run the controlled
   `check → off → check → on -f → check` sequence while the Host is idle and
   rentals are prevented; retain state, health, and safe-final-state evidence.
2. With explicit idle/load authorization and a trusted pinned image, run the
   bounded Docker GPU-injection/load procedure and verify cleanup.
3. From a genuinely external client, test TCP and UDP separately on one approved
   unused forwarded port with bounded listener/capture and verified cleanup.
4. Run one bounded Host self-test only after a role-correct Host-owner key with
   `machine_read` is supplied through secure non-chat injection, with explicit
   workload-impact approval, a runtime limit, and cleanup authority. Treat any
   paid renter-side procedure as a separate client-authorized run with numeric
   spend/runtime limits.
5. Leave installer, storage, listing, repricing, maintenance, cleanup, and other
   mutations blocked unless a disposable/rebuildable target or explicit
   operational change boundary is provided.

## Canonical evidence

- Inventory: `verification/host-docs-test-sets.json`
- Results and structurally complete 1,004-target current projection:
  `verification/host-docs-test-results.json`
- Scores and approved N/A records:
  `verification/host-docs-command-scores.json`
- Command assessment:
  `verification/evidence/2026-09-01-host-command-assessment-attempt-01/result.md`
- Current reconciliation:
  `verification/evidence/2026-09-01-host-current-reconciliation-attempt-01/result.md`
- Retained installation GPU-visibility acceptance:
  `verification/evidence/2026-09-02-host-install-nvidia-smi-retained-01/result.md`
- CLI API-key file-permission failure:
  `verification/evidence/2026-09-02-cli-set-api-key-permissions-attempt-01/result.md`
- Authorized-Host bounded read-only acceptance:
  `verification/evidence/2026-09-02-host-safe-readonly-attempt-01/result.md`
  and `verification/evidence/2026-09-02-host-safe-readonly-attempt-02/result.md`
- Final bounded read-only acceptance:
  `verification/evidence/2026-09-02-host-safe-readonly-attempt-03/result.md`
- Host self-test preflight attempt:
  `verification/evidence/2026-09-02-host-self-test-attempt-01/result.md`
- Bounded kernel-log follower:
  `verification/evidence/2026-09-02-host-kernel-log-follow-attempt-01/result.md`
- Market Metrics REST authorization blocker:
  `verification/evidence/2026-09-02-market-metrics-rest-attempt-01/result.md`

The port-4000 reviewer is the preferred human entry point because it shows each
carrier beside its exact page wording, current status, retained history,
limitations, and semantic score.
