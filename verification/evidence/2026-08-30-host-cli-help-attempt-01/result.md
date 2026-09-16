# Host Docs installed CLI signature check

- Installed CLI: `1.4.2.post7+54c1b69`
- Planned signatures: 42
- Executed: 42
- Exit code 0: 42
- Nonempty help output: 42
- Nonempty stderr: 0
- Manifest SHA-256: `c66d1b3f87f31430e52560ab25498da8baf4168e8a430af2300e677efafc76e5`

Each documented registered signature was invoked only as
`vastai <signature> --help`. This proves the installed parser accepts all 42 command
paths and emits help without making an API call. It does not prove authorization,
control-plane behavior, Host behavior, mutations, paid actions, or page semantics.

Four accepted aliases display a different spelling in their first usage line:
`create team` → `create-team`, `defrag machines` → `defragment machines`,
`schedule maint` → `schedule maintenance`, and `set min-bid` → `set min_bid`.
These are retained as CLI-help consistency observations, not Host Docs command failures,
because the documented signatures themselves were accepted.
