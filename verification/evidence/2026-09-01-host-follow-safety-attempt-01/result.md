# Live-follow safety wording correction and static retest — attempt 01

- Attempt ID: `ATTEMPT-2026-09-01-HOST-FOLLOW-SAFETY-01`
- Evidence ID: `EV-HOST-FOLLOW-SAFETY-01`
- Command carriers: `CLM-08d538a4bfda6ba5`, `CLM-c36aed4218dd8d33`
- Method: exact-source safety-context inspection
- Test-set snapshot SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- Runtime follow, load, self-test, Host mutation, or paid action: none

## Initial finding

Both pages presented an intentionally live `journalctl -f` or `tail -f` command without
an adjacent explicit stop and process-exit confirmation. The procedure inventory already
required cleanup, but the user-facing page wording did not state it. The initial semantic
audit therefore classified both carriers as score 1 safety defects.

## Correction

- `host/common-errors-diagnostics.mdx` now limits the watcher to a planned bounded
  reproduction, tells the operator to press `Ctrl+C` when that reproduction ends, and
  requires confirmation that the pipeline exited.
- `host/how-to-self-test.mdx` now limits the watcher to the planned self-test window,
  tells the operator to press `Ctrl+C` when the test ends, and requires confirmation that
  `tail` exited.

The exact command text and source line numbers did not change. Static retest confirms that
each command is immediately preceded by its stop/cleanup condition. Current page hashes
are `4d08c53a4efa83c7a01292a81c043811743c9a816178ec9b9d5c19691cc6898e`
and `15c7a15c89ccccc4630af3a186ef071e672dd3b542ec166e5208c9dd57cc2cc4`.

## Current disposition

The source safety defect is corrected and the command forms now have score-2 static
support. Neither carrier receives runtime `PASS`: no representative live fault/load or
fresh-install self-test was run, and no retained watcher-output/termination observation
exists. Both runtime procedures remain `BLOCKED` until their own trigger, authority, and
cleanup evidence is available.
