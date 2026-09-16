# Host self-test procedure verification plan, attempt 01

> **Publication-redaction amendment (2026-09-04).** The restricted original
> plan is bound by SHA-256
> `534f608dd342aba81707ebce710f2f51a72ffaf15e52c275a1e16e2e383dd734`.
> This public projection replaces only the real machine identifier with
> `<authorized_machine_id>`; the frozen sequence, limits, expected
> observations, safety boundaries, and maximum claim are unchanged.

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SELF-TEST-01`
- Procedure: `ST-E01`, Host-owned machine self-test
- Target: authorized Host machine `<authorized_machine_id>`
- Client: macOS, Vast CLI `1.4.2.post7+54c1b69`
- Canonical test-set SHA-256:
  `4d5ad9a0897e04850d098d33837ec8f9e6b86e5d8fb900368d964a634a39ac39`
- Execution limit: one normal self-test attempt; no automatic retry

## Scope correction

This is a Host verification workflow against the authorized Host's own hardware,
not qualification of an unrelated marketplace machine. The CLI implementation
does create a temporary diagnostic contract on the selected Host and destroys
it after the run. Therefore the run still requires an idle Host and explicit
cleanup proof, even though no separate paid-machine test is being requested.

## Frozen sequence and expected observables

1. Confirm the Host is reachable over the already authorized SSH transport.
2. Confirm `vastai.service` is active, no renter containers are running, and no
   GPU compute processes are active.
3. Confirm the CLI credential can inspect/select machine `<authorized_machine_id>` and that the
   machine has a rentable offer. Stop on an authentication or permission error.
4. Run exactly one self-test with a private writable bundle directory:

   ```bash
   vastai self-test machine <authorized_machine_id> \
     --support-bundle-dir <restricted-evidence-directory>
   ```

5. Preserve the terminal result, failure code/stage if any, selected image
   metadata when emitted, and a sanitized inventory of any generated bundle.
6. Confirm the temporary self-test contract no longer exists and that the Host
   has returned to its pre-run idle state.

The expected success observable is a terminal self-test success after preflight
and all runtime stages. A normal preflight failure, runtime failure, timeout, or
permission error is retained as a valid observed result but does not become a
functional PASS for the full procedure.

## Safety, stop, and retention boundaries

- Do not expose, copy into Git, or print an API key.
- Do not use `--ignore-requirements`, a custom image, or automatic retry in this
  attempt.
- Stop before the workload if the Host is rented, has running containers, or
  has active GPU compute processes.
- Stop further live work if cleanup is uncertain. If the CLI reports a contract
  ID and cannot destroy it, inspect that exact contract and destroy only that
  contract under the already authorized cleanup boundary.
- Raw stdout, stderr, and bundles are restricted evidence outside Git. Public
  evidence may retain hashes, exits, timestamps, stage names, sanitized result
  fields, and the cleanup conclusion.

## Maximum claim

A clean pass can support the self-test command carriers and the executed
`ST-E01` branch on this exact Host/CLI/date. It does not prove immediate platform
verification, search placement, future rentability, or behavior on other Hosts.
