# Generated Self-Test reference parity — attempt 01

- Attempt ID: `ATTEMPT-2026-09-01-HOST-SELF-TEST-REFERENCE-01`
- Evidence ID: `EV-STR-C01-PARITY-01`
- Procedure: `STR-C01`
- Test set: `TS-STR-C01`
- Branch: `STR-C01-parity`
- Steps: `STR-C01-parity-s01`, `STR-C01-parity-s02`
- Repository revision: `14d9af21fe8a6df205180d6f211415bf750ee4b8`
- Repository tree: `2eded9e87079a3cb2517ee7a7448018c388b122b`
- Test-set snapshot SHA-256: `50b010956942a3294ea12cbc3936330fbad2be932948a9b4b3e747c8c72c051a`
- Source page SHA-256: `b84e11e72b3571b4b59c4a3072d6cdd172eb78df446d8c4299d897929539ce12`
- Generator SHA-256: `933840448443ec57698ff3154dbd3f4cca97fea7245d1873b4c96b0724c5ae74`
- Detailed audit SHA-256: `86ef9bb9fe2ad08637654614d3fb9bbe2864bd7e85837c41f872ab95c0b89ccd`
- Execution class: local isolated static regeneration
- External, authenticated, Host, paid, WAN, privileged, or mutating action: none

## Preserved first observation

The first isolated run supplied the current local CLI and self-test source checkouts. The
generator exited `1` before output because that CLI checkout lacks the required
`vastai.cli.self_test.machine_diagnostics` module. That observation remains retained in
`.orchestra/host-vv-reconciliation-20260901/findings/self-test-reference-parity.html`; it
is not converted into a documentation defect or overwritten by the corrective run.

## Corrective historical-source method

1. Read the two source identities embedded in the generated page.
2. Created clean disposable local clones at those exact commits from already available
   repositories; no network operation occurred.
3. Ran the current docs generator with those two explicit source paths and an isolated
   output path.
4. Hashed the output and canonical page, then compared the complete bytes.
5. Removed the disposable clones and isolated output after metadata capture.

## Observation

| Item | Retained result |
| --- | --- |
| Vast CLI source | commit `d4316fb06631cea759f5a36542e6196450e897f2`, tree `071045d45bd18446f1537ce0eadc25f922767abe`, clean |
| Self-test source | commit `6f93fc4ba8ec61e3360b28829e91665f3ba7ade6`, tree `5da8e8cc57cf1676183504e33ae6851d598d1a5e`, clean |
| Generator | exit `0` |
| Generated output SHA-256 | `b84e11e72b3571b4b59c4a3072d6cdd172eb78df446d8c4299d897929539ce12` |
| Canonical page SHA-256 | `b84e11e72b3571b4b59c4a3072d6cdd172eb78df446d8c4299d897929539ce12` |
| Exact byte comparison | identical; `cmp` exit `0` |

## Disposition

| Step | Observation | V&V status |
| --- | --- | --- |
| `STR-C01-parity-s01` | The page explicitly records the exact CLI and self-test source identities reproduced above. | `PASS` |
| `STR-C01-parity-s02` | Isolated regeneration at that exact clean tuple produced bytes identical to the canonical page. | `PASS` |

- Branch `STR-C01-parity`: `PASS` (2/2 required steps pass in order).
- Test set `TS-STR-C01`: `PASS` for the exact historical static parity claim.

## Limitations

- This does not establish generator compatibility with the current CLI checkout; that
  separately retained attempt remains blocked at import.
- This does not prove current product support, live self-test behavior, paid-rental
  behavior, or compatibility of any source revision newer than the historical tuple.
- No generated page was hand-edited and no canonical source file changed during this
  attempt.
