# Vast CLI API-key file-permission verification — attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-CLI-SET-API-KEY-PERMISSIONS-01`
- Command evidence ID: `EV-CLI-SET-API-KEY-PERMISSIONS-01`
- Projection evidence ID: `EV-CLI-SET-API-KEY-PERMISSIONS-PROCEDURE-01`
- Canonical command carrier: `CLM-b3cd48630e5f2b0c`
- Canonical test-set SHA-256:
  `83e9c2de4fbd5be08209186ffaed13600eac70eb120407c48f2300ccf12543f5`
- Parent promotions: none

## Method

Vast CLI 1.5.6 was installed in a disposable macOS arm64 Python 3.14.6 virtual
environment. The exact documented `vastai set api-key <API_KEY>` form was exercised
with a fixed synthetic, non-secret value, an isolated `XDG_CONFIG_HOME`, and normal
umask `022`. The legacy home-directory key file was absent before and after the run.

The command exited 0 and the stored content matched the synthetic input. The isolated
configuration directory contained one file, `vastai/vast_api_key`, with size 25 bytes
and mode `0644`. The installed `auth.py` had SHA-256
`624c749457ebd2f23b34da95329165e75503a350a576d0fe04f26a6c48b4da45`; inspection
showed the key file is opened for writing without a subsequent permission hardening
step. The disposable directory was removed after observation.

## Result

The command-level functional result is `FAIL`. Although the command completes and
writes the requested value, mode `0644` makes API-key material readable by users other
than the owner on a multi-user system. Under the Host Docs rubric, unsafe credential
storage is score 1 rather than a successful but weakly relevant score 2 result.

The current command projection changes from `BLOCKED` to `FAIL`, and its semantic score
changes from 2 to 1. No step, branch, test set, or page is promoted or otherwise
reclassified.

## Claim boundary

This result is limited to Vast CLI 1.5.6 on the stated disposable macOS/Python
environment with umask `022`. It used no real credential, performed no Host operation,
spent no funds, and does not establish behavior on Linux, Windows, a different umask,
or a corrected CLI release. No secret value, secret digest, or private filesystem path
is retained here.
