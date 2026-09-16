# Host Docs local CLI read-only attempt 03 — account context

- Attempt state: `EXECUTED`
- Evidence ID: `EV-CLI03-SHOW-USER`
- V&V status: `PASS`
- Procedure: `SRCH-E01`
- Command carrier: `CLM-4025e53706d33f3a`
- Authored command: `vastai show user`
- Executed form: authored command plus global `--raw` output mode
- Process exit code: `0`
- Raw stdout SHA-256: `c5bd29956f5b15f3f67f0214c560bba3a62c44b96caa27353a0d94248a836cee`
- Raw stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Raw artifact policy: mode `0600`, outside Git

The command returned a valid account object with no stderr. A bounded redacted projection
shows that the configured account is not Host-only, has not accepted the Host agreement,
and its current rights do not include `machine_read`. This explains the 401 results in
attempt 01 and confirms that those commands need a different, role-correct Host key.

No email, name, account ID, key ID, address, balance, SSH key, or other raw account value
is retained. The command PASS is limited to account-context inspection; the current
account state blocks Host-machine procedures and is not itself a documentation failure.

Semantic score remains unset until this behavior is compared with the complete
`/host/not-in-search` diagnostic sequence.
