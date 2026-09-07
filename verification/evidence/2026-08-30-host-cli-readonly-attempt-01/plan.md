# Host Docs local CLI read-only attempt 01

- Test-set snapshot SHA-256: `63413c9c00fc394f727cb905db29aa787ac1ea3b4b8ef7c45ff6d727ed88a88c`
- CLI identity observed before the run: `1.4.2.post7+54c1b69`
- Credential source: existing local Vast CLI configuration; no key is passed on the
  command line, copied into evidence, or printed.
- Target machine: restricted alias `HOST_MACHINE_ID`

Run the following authored read-only forms with raw output redirected mode `0600` outside
Git. Replace the placeholder only in the private invocation:

1. `vastai show machines --raw`
2. `vastai show machine <machine-id> --raw`
3. `vastai show maints --ids <machine-id> --raw`
4. `vastai metrics gpu --raw`
5. `vastai metrics gpu-trends "RTX 4090" --raw`
6. `vastai metrics gpu-locations --raw`
7. `vastai search offers -n 'machine_id=<machine-id>' --limit 200 --raw`
8. `vastai search offers 'machine_id=<machine-id> rentable=any rented=any verified=any external=any' --limit 200 --raw`
9. `vastai reports <machine-id> --raw`

These checks may query the control plane but do not list/unlist, schedule/cancel, clean,
delete, create, change price, change account state, start a rental, run Self-Test, or
perform a paid action. A command rejected by the installed CLI or API is retained as a
result and does not stop unrelated read-only checks.

Raw response bodies may contain account, machine, offer, network, contract, or report
details. Only exit codes, hashes, bounded redacted observations, and documentation
findings belong in the repository.
