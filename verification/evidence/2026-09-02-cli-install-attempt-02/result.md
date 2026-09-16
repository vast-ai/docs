# Vast CLI install attempt 02 result

- Attempt ID: `ATTEMPT-2026-09-02-CLI-INSTALL-02`
- Status: `PASS`
- Scope: `CLM-ec1c88293b76cb4b`
- Environment: macOS arm64, Python `3.14.6`, pip `26.1.2`

Inside a clean disposable virtual environment, the exact documented `pip install --upgrade vastai` command exited `0` and installed Vast CLI `1.5.6`. The virtual environment's own `vastai` entry point existed, was executable, and returned version `1.5.6` with exit `0` and empty standard error.

This is functional `PASS` with semantic score `3` for installing or upgrading the CLI on the tested environment. It does not validate Host-account authentication, market-query permissions, Linux/Windows installation, or future package versions. The failed sandboxed attempt remains recorded separately.

| Restricted artifact | SHA-256 |
| --- | --- |
| `environment.txt` | `e1e08dd79743a1b5176795f7e4fa8e592093fe3f641e197edbaed3346de09c2f` |
| `install.stdout` | `c233c1b6827bcb8b6d241b7532604d46baf8709002df9c693c868ae83334a1b0` |
| `install.stderr` | `95c6cbc58abc300bfa52297317839bc87ac1f8aedab38a12f93a5d894e80cfbf` |
| `status.txt` | `d5226a984e9e99a63fc1c441a8aa7fb0718041d9c1652a7d1c3feac8f7eeb6e1` |
| `version.stdout` | `dab64e06c0817d77b4f887261832cbb34ba023cac7c74d72d81068553652d0c5` |
| `version.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Raw evidence remains under `../private-evidence/2026-09-02-cli-install-attempt-02/`. The disposable virtual environment was removed after evidence capture.
