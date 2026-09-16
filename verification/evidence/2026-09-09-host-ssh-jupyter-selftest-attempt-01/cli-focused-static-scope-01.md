# Focused CLI unit checks — scope and retained first failure

[Initial collection](cli-focused-static-01.json) could not load the CLI repository's global test fixtures because this Python environment lacks `Crypto` (PyCryptodome). No test ran in that attempt. This is a test-environment prerequisite, not a failed Host instruction or live result.

[The explicitly narrower run](cli-focused-static-02.json) passed **63 self-contained tests**: all create-instance payload tests and two support-bundle redaction/archive-name tests. It used `--noconftest` and selected only tests that do not need the repository's shared fixtures. Credentials were removed from the environment; no live/integration test was selected. No dependency was installed and no source was changed.

These are actual macOS local tests at CLI revision `ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd`, not the full CLI suite, cross-platform qualification, or a retest of the omitted fixture-dependent cases. The full selected-file collection remains unperformed until a suitable complete test environment is available. The earlier failure is preserved rather than silently reported as 63 passing tests over the original scope.
