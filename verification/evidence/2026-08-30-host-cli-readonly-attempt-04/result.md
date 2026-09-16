# Host Docs local CLI read-only attempt 04 — direct machine search

- Attempt state: `EXECUTED`
- Evidence ID: `EV-CLI04-SEARCH-DIRECT`
- V&V status: `PASS`
- Procedure: `SRCH-E01`
- Command carrier: `CLM-257b1610cec2ed67`
- Authored command: `vastai search offers 'machine_id=<machine_id>' --limit 200`
- Executed form: authored command plus global `--raw` output mode
- Process exit code: `0`
- Observation: valid empty JSON array and no stderr
- Raw stdout SHA-256: `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- Raw stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Raw artifact policy: mode `0600`, outside Git

Claim limit: the direct lookup is accepted and returned no matching offer in the observed
market state. Because the preceding account-context check showed the configured account
is not the intended Host account, the empty result cannot establish why the Host machine
is absent. The page sequence correctly requires that account check first.
