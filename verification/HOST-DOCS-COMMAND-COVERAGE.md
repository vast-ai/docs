# Host Docs command V&V coverage

Coverage is counted over the 165 command carriers in
`host-docs-test-sets.json`. Commands remain grouped in their page, procedure,
branch, and ordered-step context. A help/signature check proves only registry or
static conformance; it does not establish runtime product behavior.

## Current functional disposition

| Current status | Command carriers |
| --- | ---: |
| `PASS` | 46 |
| `BLOCKED` | 34 |
| `UNVALIDATED` | 58 |
| `NOT_APPLICABLE` | 27 |
| `FAIL` | 0 |
| **Total** | **165** |

Each carrier has one exact current projection record. Its status is supported
by the current reconciliation evidence and must agree with the execution status
stored beside its semantic assessment. Superseded and disqualified attempts
remain visible in history but cannot drive the current projection.

## Contextual semantic assessment

| Assessment | Command carriers |
| --- | ---: |
| Score 1 — failed, irrelevant, unsafe, obsolete, or materially unsupported | 15 |
| Score 2 — relevant but partial, conditional, static-only, or incomplete | 112 |
| Score 3 — representative evidence strongly supports the exact page claim | 11 |
| Approved display-only `NOT_APPLICABLE` | 27 |
| **Total** | **165** |

Semantic score and functional status are deliberately separate. The shared
semantic-assessment evidence binds all 165 current carriers without pretending
that the assessment itself executed them: its 138 numeric targets remain
`UNVALIDATED` as assessment evidence, while its 27 canonical display targets are
`NOT_APPLICABLE`. Functional PASS/BLOCKED/UNVALIDATED/N/A comes from the separate
current-status projection and retained evidence.

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
- Two live-follow score-1 findings are retained as superseded history. Corrected
  bounded stop/exit wording now supports score 2, while runtime stays blocked.
- The bare `tcpdump` token is an approved display-only N/A carrier. The owning
  external UDP/WAN procedure remains blocked and is not silently passed.

## Highest-value remaining runs

1. After VM/IOMMU repair and reboot, run the controlled
   `check → off → check → on -f → check` sequence while the Host is idle and
   rentals are prevented; retain state, health, and safe-final-state evidence.
2. With explicit idle/load authorization and a trusted pinned image, run the
   bounded Docker GPU-injection/load procedure and verify cleanup.
3. From a genuinely external client, test TCP and UDP separately on one approved
   unused forwarded port with bounded listener/capture and verified cleanup.
4. Run one capped paid Self-Test/rental procedure only after a fresh client key
   is supplied through secure non-chat injection, with numeric spend/runtime
   limits and cleanup authority.
5. Leave installer, storage, listing, repricing, maintenance, cleanup, and other
   mutations blocked unless a disposable/rebuildable target or explicit
   operational change boundary is provided.

## Canonical evidence

- Inventory: `verification/host-docs-test-sets.json`
- Results and complete 972-target current projection:
  `verification/host-docs-test-results.json`
- Scores and approved N/A records:
  `verification/host-docs-command-scores.json`
- Command assessment:
  `verification/evidence/2026-09-01-host-command-assessment-attempt-01/result.md`
- Current reconciliation:
  `verification/evidence/2026-09-01-host-current-reconciliation-attempt-01/result.md`

The port-4000 reviewer is the preferred human entry point because it shows each
carrier beside its exact page wording, current status, retained history,
limitations, and semantic score.
