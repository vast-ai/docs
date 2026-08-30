# Host Docs local CLI read-only attempt 02 — comparable offer search

- Attempt state: `EXECUTED`
- Evidence ID: `EV-CLI02-SEARCH-COMPARABLE`
- V&V status: `PASS`
- Procedure: `SRCH-E02`
- Command carrier: `CLM-16e21c4911f77054`
- Authored command: `vastai search offers 'gpu_name=RTX_4090 cpu_ram>257 cpu_ram<258'`
- Process exit code: `0`
- Observation: nonempty 36-line result table, no stderr, and no error marker detected
- Raw stdout SHA-256: `1078af4c5f3cd7ec69e7064e8389576492f81a6ae3403c36294ab13b6c0081f4`
- Raw stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Raw artifact policy: mode `0600`, outside Git

Claim limit: this proves that the exact documented query is accepted by the installed CLI
and returns a nonempty comparable-offer table in the observed marketplace state. It does
not prove that these filters are sufficient for a pricing decision, that every row is a
true operational comparable, or that the same results persist over time.

Semantic score remains unset until the command is assessed against the complete
surrounding ranking guidance on `/host/not-in-search`.
