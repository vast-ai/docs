# Procedure next-action patch proposal

This proposal covers 651 baseline procedure nodes whose exact original action
was `No additional current action is recorded for this exact-source historical
carry-forward.` It preserves status, evidence, spans, and history and proposes
only the root audit's already-grounded `next_action`; it records no execution,
validation, or promotion.

| Status | Nodes |
| --- | ---: |
| UNVALIDATED | 530 |
| BLOCKED | 71 |
| FAIL | 4 |
| STALE | 46 |

The 605 unresolved (`UNVALIDATED`/`BLOCKED`/`FAIL`) nodes receive the audit's
child-review, source-inspection, repository-review, prerequisite-recheck, or
scoped-runtime action. The 46 `STALE` nodes receive `REMAP_CURRENT_SCOPE`:
remap the exact current step before transferring any older result; no historical
execution transfers. No procedure-level parent carried that literal action, so
`procedures` is deliberately empty.

Repeated generic text needs caution: it is the old carry-forward wording above,
not evidence of completion. The replacement action must be selected from the
node's audit method; a source inspection does not establish execution, and an
unresolved/stale child result cannot prove its parent.

Phase-43 canonical hash (sorted-key JSON of `nodes` and `procedures`):
`9d4735112c758d2bcc37001df9d225071382001e58052aa880d20859c446b0d1`.

The JSON also preserves a correction note: the prior runtime audit's claim that
the remaining items were individually screened was inaccurate. Only the 29
exceptions had manual text/context review; the other 978 were pattern-screened
coverage retentions, as its coverage ledger already states.
