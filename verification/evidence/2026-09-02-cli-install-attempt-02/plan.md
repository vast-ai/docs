# Vast CLI install attempt 02

> **Publication-path amendment (2026-09-04).** The restricted original plan is
> bound by SHA-256
> `b55f056538b287ccd6a8057a76fde433221321283c535cc5f54d177befd49dda`.
> This public projection replaces only the workstation-temporary virtual
> environment path with `<disposable-venv>`; the method, acceptance checks,
> limits, and maximum claim are unchanged.

- Attempt ID: `ATTEMPT-2026-09-02-CLI-INSTALL-02`
- Supersedes: no result; this is a retry after the external DNS blocker in attempt 01
- Scope: `CLM-ec1c88293b76cb4b`
- Method: run the exact install command in the existing clean disposable virtual environment with package-index network access

## Acceptance checks

1. `pip install --upgrade vastai` exits `0`.
2. `<disposable-venv>/bin/vastai` exists and is executable.
3. That exact entry point runs `--version` with exit `0`.

The global CLI must not satisfy the check. Retain install output, exit statuses, executable path, version, Python, pip, and platform. Remove the disposable environment after evidence is finalized.

PASS validates installation on the tested macOS/Python environment only. Host-account authentication and market queries remain separate.
