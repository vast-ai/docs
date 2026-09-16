# Host command semantic assessment — attempt 01

- Attempt ID: `ATTEMPT-2026-09-01-HOST-COMMAND-ASSESSMENT-01`
- Evidence ID: `EV-HOST-COMMAND-ASSESSMENT-01`
- Method: static current-source inspection plus reconciliation of retained V&V evidence
- Population: 165 current Host-documentation command carriers
- Proposal artifact SHA-256:
  `bedf029c2256034928c635974cf574860ea3fc1f8b5a6deab925c1ea84d86f9b`
- Test-set snapshot SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- New blanket runtime execution performed by this assessment: none

## Method

Every current carrier was joined to its exact canonical page route, procedure, source
file, and source line. The assessment reconciled the current documentation wording,
canonical execution treatment, existing semantic scores, focused command audits, and
retained V&V results. Conflicts were resolved conservatively: no static inspection or
healthy-host observation was promoted into proof of an unobserved failure, load,
mutation, cleanup, prerequisite, or exception branch.

The semantic rubric is independent of execution status:

- Score 1: the command failed to run, failed to provide relevant semantic support, is
  wrong or unsafe, or remains materially unsupported for the exact page claim.
- Score 2: the command is relevant or syntactically accepted, but retained evidence is
  incomplete or provides only partial support for the exact documented behavior,
  prerequisites, exceptions, result meaning, or cleanup.
- Score 3: representative retained evidence shows the command works and directly
  supports the documented behavior, including applicable prerequisites, exceptions,
  result meaning, and cleanup boundary.
- `NOT_APPLICABLE`: limited to canonical approved non-executable/display carriers.

## Reconciled accounting

| Disposition | Count |
| --- | ---: |
| Score 1 | 15 |
| Score 2 | 112 |
| Score 3 | 11 |
| Not applicable | 27 |
| Total current carriers | 165 |

| Current execution status represented by the assessment | Count |
| --- | ---: |
| `PASS` | 46 |
| `BLOCKED` | 34 |
| `UNVALIDATED` | 58 |
| `NOT_APPLICABLE` | 27 |
| Total current carriers | 165 |

All 165 current carriers have one mutually exclusive disposition: 138 numeric scores
and 27 approved not-applicable records. Seven historical records are retained as
withdrawn evidence history; they are not additional current dispositions.

## Withdrawn history

The seven withdrawals preserve three VM observations disqualified by an unsuitable
environment, one retired hardware-preparation carrier replaced after a documentation
correction, one overclaimed conditional Fabric Manager score, and two score-1
live-follow safety findings superseded after the surrounding source wording was fixed.
Withdrawal preserves the audit trail and does not restore the earlier runtime or
semantic claim.

## Limitations and claim boundary

- This attempt is a static source and retained-evidence reconciliation, not blanket
  execution of all 165 commands.
- The 46 `PASS` statuses come from current qualifying retained attempts; this assessment
  did not rerun those commands.
- Score 2 can represent relevant static form, partial observation, a missing target
  condition, or a safely blocked operation. It is not equivalent to runtime acceptance.
- The 34 blocked and 58 unvalidated carriers still require their stated authority,
  representative condition, safe execution window, or external environment before they
  can gain stronger runtime support.
- A not-applicable record classifies only its non-executable/display carrier. Its owning
  procedure can remain blocked or unvalidated.
- Semantic scores are evidence summaries, not a blanket readiness declaration. Final
  acceptance remains a human review decision.

This public-facing result contains no credentials, machine addresses, hostnames, account
identifiers, or raw command output. Exact carrier bindings belong in the canonical
machine-readable V&V results and score ledgers.
