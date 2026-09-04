# Vast CLI install attempt 01 result

- Attempt ID: `ATTEMPT-2026-09-02-CLI-INSTALL-01`
- Status: `BLOCKED`
- Blocker: `NETWORK_DNS_RESTRICTED`

The exact `pip install --upgrade vastai` command could not resolve `pypi.org` in the sandbox and did not install the package. The original shell wrapper continued and resolved the pre-existing global `vastai` executable, so its version output is explicitly rejected as evidence for this attempt.

This attempt supports no functional or semantic promotion. A new attempt must require the virtual environment's own `vastai` entry point and retain the `pip` exit status.

| Restricted artifact | SHA-256 |
| --- | --- |
| `environment.txt` | `e1e08dd79743a1b5176795f7e4fa8e592093fe3f641e197edbaed3346de09c2f` |
| `install.stdout` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `install.stderr` | `a2b05264173561ae19af2a5b667b4595023b97b7a89103d958ebae0c481b05` |
| Rejected global `version.stdout` | `615b446abb676d042797ac568fa188a922ea142841f40adaee102333fea53eaa` |
| `version.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Raw evidence remains restricted. The failed attempt is preserved rather than overwritten.
