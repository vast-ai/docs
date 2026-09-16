# Host-local diagnostic bundle attempt 01 result

- Attempt ID: `ATTEMPT-2026-09-02-HOST-LOCAL-BUNDLE-01`
- Status: `BLOCKED`
- Blocker: `HOST_PYTHON_VENV_UNAVAILABLE`
- Scope: `CLM-321e05cb87fdcbe0` and `CLM-444903dafc2f1f6e`

The Host has Python `3.12.3`, but the attempt-owned virtual environment could not install pip because Ubuntu's `python3.12-venv`/`ensurepip` component is absent. The run stopped before installing Vast CLI or executing `dump-logs`.

No OS package or bootstrap script was installed. The partial virtual environment and bundle directory under `/tmp` were removed and their absence was confirmed. The setup attempt is `BLOCKED`; the two source carriers remain `UNVALIDATED` because the documented bundle command never ran, and they receive no new semantic score.

| Restricted artifact | SHA-256 |
| --- | --- |
| `setup.stdout` | `3cda39d0c3d7cfc8c53bbfcee8171f7357295b2f6637c15063348a89ded22480` |
| `setup.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Completing this check requires either an approved temporary CLI execution method already present on the Host or permission to add the missing venv support. Host access alone does not justify altering the system package set.
