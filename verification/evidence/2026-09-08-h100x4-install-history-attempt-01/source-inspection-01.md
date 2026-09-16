# HIST-04 source inspection 01

## Scope and method

This is a static, public-artifact inspection for HIST-04 in `plan.md:10`. On 2026-09-08, the two public URLs named in the plan were retrieved as opaque bytes into the non-publishable `.orchestra/h100x4-install-history/source-inspection-01-restricted/` directory (directory mode `0700`, files mode `0600`). Neither artifact was made executable or executed. No host, API, SSH, credential, or service access occurred.

| Artifact | SHA-256 | Static identification |
|---|---|---|
| public installer script | `6b00488ccf837ed6b7b5375270b75db284c3906f6aec832ad9c8573f44eaac6c` | 89,020-byte UTF-8 Python script |
| public TUI binary | `0d078186004a37f8d2518fced156d39caf0ae36834797f008ce79d53459c268e` | 32,295,864-byte stripped x86-64 ELF; GNU Build ID `85c0774f6116b4a98dbb3ea5f31cd2a68d4b21ba` |

The downloaded public installer is the sole executable-source artifact reviewed. The local TUI checkout is source-only context at revision `2d33c362bd0293f73730b258e77c9bcd1945ee14`; it is not evidence that this revision produced the downloaded TUI binary.

## Findings

### HIST-04-A — registration is automatic in the inspected installer: PASS (static-only)

`public-install:97-121` posts to the daemon identify endpoint and returns `machine_id` on success. `public-install:1586-1607` reads/creates the local machine key, calls `send_identify`, and persists the returned numeric machine ID. This call occurs before the `--no-daemon` conditional at `1658`; therefore that documented flag does not gate this registration call.

### HIST-04-B — self-test launch is automatic when its two runtime predicates succeed: PASS (static-only)

The complete argument definition is `public-install:1387-1411`; it includes `--no-daemon`, but no `--no-self-test`, no self-test-disable flag, and no public-rental/listing-prevention flag. The `--no-daemon` condition gates daemon setup/start at `1658-1926`. Its post-install block resumes outside that condition at `1927` and:

- downloads and runs `send_mach_info.py` with `--speedtest` (`1943-1959`); then
- launches `start_self_test.sh` when `machine_id` and successful speed-test output are both truthy (`1961-1969`).

The launch is asynchronous and passes opaque positional values to an externally obtained script. Static evidence therefore establishes the conditional launch, not completion or outcome.

### HIST-04-C — automatic public listing is not established: UNVALIDATED

The inspected script registers the machine and launches the conditional self-test above, but it contains no inspected call that explicitly lists the machine for rental. Instead, its terminal message says to go to the listing page to set prices and list the machine (`1971-1974`). The local TUI support guide independently says the initial self-test is automatic and warns the operator not to list early (`host-installer-wizard/docs/support_guide.md:9-10`).

This is not proof that a listing cannot arise from the downloaded/updated daemon or from `start_self_test.sh`: `public-install:1934-1941` retrieves and executes `update_scripts.sh`, and `1945-1948` retrieves `send_mach_info.py`; those dynamic artifacts and `/var/lib/vastai_kaalia/start_self_test.sh` were intentionally not retrieved or inspected in this bounded task.

### HIST-04-D — no documented safe *real-install* no-public-rental mode found: UNVALIDATED

`--no-daemon` is documented as “Skip daemon installer; only set up environment” in the local source (`host-installer-wizard/docs/installer_interface.md:33-53`) and does not gate the registration/self-test portions shown above. The local TUI’s real command construction contains only the API key, ports, logfile, and optional Docker partition (`host-installer-wizard/src/host_installer_wizard/workers/installer_runner.py:1123-1138`), so it cannot pass a self-test or listing-control flag. Its CLI parser exposes only `--api-key`, `--debug`, `--debug-live`, `--start-at`, and `--installer-path` (`host-installer-wizard/src/host_installer_wizard/app.py:431-459`).

The source documents `--debug` as an explicitly simulated, no-real-change UI preview (`host-installer-wizard/README.md:51-65`; `CONTRIBUTING.md:189-193`). It is not a real-install/no-public-rental mode. No safe real-install mode meeting that description was located in the inspected source and documentation.

### HIST-04-E — downloaded TUI/source correspondence: UNVALIDATED

The downloaded TUI binary was recorded only by hash and file metadata. No binary execution, decompilation, or source-to-binary provenance verification was performed. Consequently, the local TUI source can show what that checkout would construct, but cannot establish the behavior of the downloaded binary.

### HIST-04-F — the stock installer/TUI cannot guarantee the newly authorized publication bounds: FAIL-CLOSED

The public installer exposes no price, minimum-bid, storage-price, or expiry/end-time argument in its complete parser (`public-install:1387-1411`). The only storage parameter is local loopback size in GiB (`1401`, `1486-1491`), not a storage charge. Its only price-related source is a comment and generated value before the external self-test launch: `public-install:1963-1967` computes `max(1, int(96 // gpu_count))` and passes it, followed by the opaque strings `"1"` and `"0"`, to `start_self_test.sh`. Neither their units nor their semantics are defined in the inspected script. For four GPUs, that arithmetic source value would be `24`; it is not an interface for, or proof of, any authorized dollar amount.

The local TUI has no price/expiry state and its exact real-install command adds only ports, logfile, and optional Docker partition (`host-installer-wizard/src/host_installer_wizard/workers/installer_runner.py:1123-1138`). It therefore cannot provide the requested $3/GPU-hour on-demand, $0.30/GPU-hour minimum-bid, $0.50/GB-month storage, or no-later-than-2026-09-15 expiry guarantee from initial publication.

The no-reboot condition is not guaranteed either. When the installer decides a driver install is needed, it explicitly warns that it will reboot the system (`public-install:1667-1682`), after running `update-initramfs` (`1675`). It also restarts Docker and containerd (`1207-1212`), libvirtd (`1359-1375`), and may restart the Vast daemon after key rotation (`166-170`, `1591-1597`). This static result does not establish that those branches would be avoided on a particular host.

## Decision boundary and residual risks

This result is retained source evidence only. It does not authorize an installation, registration, self-test, listing, public rental, workload, or readiness claim. The principal unresolved risks are dynamic unpinned downstream scripts, daemon behavior, server-side effects, the semantics of the self-test positional arguments, missing source/binary provenance, and the inability of the stock paths to guarantee the authorized prices, expiry, or no-reboot constraint. No bypass or operational recommendation is made here.
