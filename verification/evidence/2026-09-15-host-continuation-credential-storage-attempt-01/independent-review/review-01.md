# Independent credential-storage review

One claim reviewed: MCL-9ad33b25fd88c5cb. **Amendment required for two narrow recipe defects.**

1. Match the installed xdg helper’s absolute-path/default rule. A relative XDG_CONFIG_HOME currently makes the shell harden a different file from the one the CLI writes.
2. Read and reject blank/EOF input before filesystem mutation. Creating an empty current file before cancellation can suppress an existing legacy key on subsequent CLI runs.

Root accepted both findings and will preserve this packet while preparing revision02 with focused relevant cases. No other first-pass blocker was found.

The full baseline claim and literal, eight exact proof selectors, eight source-alias hashes, eleven source-parent hashes, eight parent selector ranges, and all four retained installed source files match. The fenced replacement equals the tested script; the harness-generated observation hook equals the retained source. The five recorded macOS fixture outcomes are appropriately limited and do not claim new Linux/Windows execution, real authentication or a fixed CLI release.

No recipe was rerun during this independent review. Preserve the original0644 CLI failure and procedure evidence after correcting the documentation.
