# Host self-test procedure verification result, attempt 01

> **Publication-redaction amendment (2026-09-04).** The restricted original
> result is bound by SHA-256
> `79cb9a4db6dbb0601bf0a40586fc374782dd011d1384623040477c8181b6b78b`;
> the restricted original plan is bound by SHA-256
> `534f608dd342aba81707ebce710f2f51a72ffaf15e52c275a1e16e2e383dd734`.
> This public projection replaces only the real machine identifier with
> `<authorized_machine_id>`. The command form, observations, `BLOCKED`
> outcome, limitations, restricted-artifact hashes, and next action are
> unchanged.

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SELF-TEST-01`
- Procedure: `ST-E01`
- Target: authorized Host machine `<authorized_machine_id>`
- Client: macOS, Vast CLI `1.4.2.post7+54c1b69`
- Published plan SHA-256:
  `e542a408b92dce7b1c40bd78ef95d5ce2793727e17d356edd4fd624c4a8ed472`
- Result: `BLOCKED`
- Blocker: `CREDENTIAL_PERMISSION`

## Observed sequence

1. The Host preflight completed at `2026-09-02T15:49:50Z`.
   `vastai.service` was active, with zero running containers and zero active GPU
   compute processes. The self-test log was readable.
2. Two read-only offer searches returned zero offers for the target machine.
3. The exact bundle-directory form was executed once:

   ```bash
   vastai self-test machine <authorized_machine_id> \
     --support-bundle-dir <restricted-evidence-directory>
   ```

4. The CLI stopped in preflight at `select_offer` with stable failure code
   `api_permission_failed`. Its machine lookup returned HTTP 401 because the
   configured client credential lacks the required Host machine-read access.
5. No contract creation was observed. The run stopped at `select_offer`, emitted
   no contract or instance ID, and the limited credential's post-run query
   returned zero visible instances. The Host post-check at
   `2026-09-02T15:52:30Z` again showed zero running containers and zero GPU
   compute processes.

The capture wrapper did not retain the numeric process exit code. The retained
terminal output says `Test failed`, and the bundle records `success=false`, but
no exact exit-code claim is made from this attempt.

## Bundle observation

The requested directory received a 1,577-byte diagnostic archive containing:

- `collection-errors.json`
- `manifest.json`
- `self-test-output.log`
- `self-test-result.json`

The result is machine-readable and records the phase, stage, failure code,
checks, root-state explanation, and remediation. A bounded scan found no
obvious API-key, token, password, or bare 64-hex secret in those four files.
The raw archive remains restricted and must still be reviewed before sharing.

## Functional and semantic conclusion

- The self-test command path, preflight failure classification, requested
  support-bundle directory, structured result, and return-to-idle observation
  after the `select_offer` failure are directly observed on this client/target.
- The runtime workload, success result, image selection, mapped-port checks, and
  runtime cleanup remain unvalidated because execution stopped at
  `select_offer`, before the create-instance stage.
- The correct next attempt must use the Host-enabled account that owns or can
  inspect the machine. The separate client-only key is not sufficient for this
  Host workflow.
- Billing was not assessed. This attempt does not establish whether a completed
  Host self-test contract is billable or free.
- No command carrier, parent step, branch, or page is promoted to full `PASS`
  from this attempt alone. The bundle-directory carriers may receive partial
  direct support at semantic score 2 once integrated into the canonical ledger.

## Post-attempt model correction

The frozen plan records the test-set snapshot used before execution. After the
attempt, the V&V access wording was corrected from a generic paid/client-account
classification to a Host-owner self-test classification. The command, ordered
steps, expected result, stop conditions, and cleanup requirement did not change.
The current canonical test-set snapshot has a new hash; the original plan hash
remains unchanged as the record of what was frozen before this attempt.

## Credential-safety observation

The operator observed that an uncaught DNS failure from the installed CLI
rendered a request URL containing the configured API key in a local execution
trace. That trace was not retained as an attempt artifact, so this is an
operator-reported security observation rather than hashed evidence. The secret
is not copied into this record and should be rotated after testing as already
planned. The operator also reports that the local key file was tightened from
mode `0644` to owner-only mode `0600`.

## Restricted evidence hashes

| Artifact | SHA-256 |
| --- | --- |
| Host CLI context | `53533c501b13bcfa20cb5e55f9c2e1e94c61a3b8633cc5a05fa2faa9e2f0633e` |
| Host preflight | `4812dea9c307f8e71da3d6ad11832ac45c6b7e57b99dbdfe207c1adc964c41b0` |
| Offer lookup | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |
| Offer lookup stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Simple offer lookup | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |
| Simple offer lookup stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| CLI stdout | `311826893a02be259765e8ee090f0d2591939e1faf5c02516d0c77ef57eab984` |
| CLI stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Diagnostic archive | `d0126cc2bfe8eb6499d328f468418c5136f25b2a01b4112003d18778596cfff9` |
| Post-run instance query | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |
| Post-run instance query stderr | `502ee708f6d1e1e1d23d6e1ba99a73ae884e441da5ce7b124bdded731bc89198` |
| Host post-check | `2123cba683d47699aa0504e6671bb48fc7a64971d9e6cbd62a9ae3417a432669` |

Raw evidence is stored outside the documentation checkout under the restricted
`CON-1584/private-evidence/2026-09-02-host-self-test-attempt-01` directory.
