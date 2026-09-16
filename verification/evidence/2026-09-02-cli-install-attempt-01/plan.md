# Vast CLI install attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-CLI-INSTALL-01`
- Scope: `CLM-ec1c88293b76cb4b`
- Method: execute the documented install command inside a new disposable Python virtual environment on macOS, then inspect the installed CLI version

## Commands

```bash
pip install --upgrade vastai
vastai --version
```

The virtual environment isolates the installation from the operator's existing CLI. The first command is the exact published form after activation.

## Outcome

- `PASS`: install exits `0`, creates a callable `vastai` entry point, and `vastai --version` exits `0` with a version.
- `FAIL`: the published package/command executes but does not install a usable CLI.
- `BLOCKED`: package-index/network availability prevents reaching installation behavior.

This attempt validates installation on the tested macOS/Python environment. It does not authenticate a Host account or validate Linux/Windows installation, so it cannot pass the full market-query procedure by itself.
