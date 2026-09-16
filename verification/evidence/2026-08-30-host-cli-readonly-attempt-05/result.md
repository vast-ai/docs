# Host Docs Host-account CLI read-only attempt 05

- Attempt state: `EXECUTED`
- V&V status: `PASS`
- Target: restricted alias `HOST_VV_TARGET`
- Credential: ephemeral Host-account key; never written to Git or the raw archive
- Source revision: `9439b9bbcd4810294a1420d7d618dd462ea2dbd7`
- CLI target: Vast CLI `1.4.2.post7+54c1b69`; the same installed
  entrypoint was fingerprinted after the run, and its modification time
  predates the attempt
- Executed commands: `11/11`
- Process exit `0`: `11/11`
- Empty stderr: `11/11`
- Raw artifact policy: mode `0600` in a local restricted archive outside Git

The role-correct account is Host-only, has accepted the Host agreement, and can
read the authorized machine. This clears the credential and ownership blockers
from attempt 01 without rewriting that historical evidence.

## Logical procedure results

| Evidence ID | Page procedure | Result | Sanitized observation |
| --- | --- | --- | --- |
| `EV-CLI05-HOST-ACCOUNT` | `SRCH-E01` account precondition | `PASS` | Host account context and owned-machine read access were confirmed. |
| `EV-CLI05-FLEET-READ` | `FLT-E01` fleet state | `PASS` | Structured fleet output contained the authorized target. |
| `EV-CLI05-MAINTENANCE-READ` | `MNT-E01`, `MNT-E02` | `PASS` | Machine detail returned required state/end-date fields; the current target had no active rental or scheduled maintenance. |
| `EV-CLI05-MARKET-METRICS` | `MET-E02` alternatives | `PASS` | Current, trend, and location endpoints returned structured nonempty Host-market data. |
| `EV-CLI05-REPORTS` | `POL-E01` report lookup | `PASS` | The owned-machine lookup completed with an empty report list. The `--raw` presentation was text, not strict JSON. |
| `EV-CLI05-SEARCH-SEQUENCE` | `SRCH-E01` ordered diagnosis | `PASS` | The default direct search was empty; `-n` and explicit state filters each exposed the same two target offers. |

The search result directly supports the page's distinction between a listed
machine and an offer hidden by default search filters. The maintenance and
reports results are bounded: an empty current state does not validate a known
maintenance record, active-contract edge cases, or report/log correlation.

Full sanitized command records, raw-output hashes, and the post-run executable
and installed-distribution fingerprints are in `results.json`.
