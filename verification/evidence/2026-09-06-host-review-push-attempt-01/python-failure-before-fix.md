# Preserved pre-push Python regression failure

Observed on 2026-09-06 before the historical-snapshot assertion correction.
Command: `python3 -m unittest discover -s scripts -p 'test_*.py'`.
Exit status: 1. Observed summary: `Ran 97 tests in 11.374s`; `FAILED (failures=1)`.
The other 96 tests passed. No Host command was executed.

Failing test:
`test_command_proof_reviewer_attempts_are_registered_without_status_promotion`
in `scripts/test_reconcile_host_vv_repository.py`, line 650 at this attempt.
It compared the current `review-server.mjs` SHA-256
`972a7be02697f90fbdcf52bc8054663affbf7515daf31c8261f2c09d141833f8`
to the September 4 historical artifact digest
`b3c804a4ca5433645e25790e7599d78310da2168f50ac4a273de2391afc39468`.

Read-only investigation found all 20 artifact digests in the September 4
packaging record exactly match their Git blobs in
`3e1e30e2221b65d7ce1e901d9ae305f63af5b64b`. The record is authentic historical
evidence, not evidence that subsequent code edits retained the same bytes.
The correction must validate that immutable snapshot and keep present-day
reviewer validation separate; it must not rewrite the historical record.

The first JavaScript inspection of those Git blobs hit Node's default stdout
buffer limit on `verification/host-docs-test-sets.json` (`ENOBUFS`). Repeating
the same read-only inspection with a 32 MiB buffer succeeded for all 20 blobs.
That invocation failure is not a product failure or proof result.
