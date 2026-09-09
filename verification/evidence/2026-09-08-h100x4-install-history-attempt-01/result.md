# Installation evidence intake — new H100×4 and three existing hosts

PR #185 / CON-1518. Date: 2026-09-08. This is a bounded read-only evidence package, not a completed installation, self-test, listing or acceptance.

## What we found

The new host is accessible with the approved, strictly pinned administrator SSH identity. Four H100 PCIe GPUs are visible. `/var/lib/docker` is XFS with `prjquota`. Docker and Vast services are **not installed**. This is useful preparation evidence, not proof of an installed or load-tested host.

The inspected public installer launches a helper which temporarily lists an unlisted machine before self-test. For four GPUs its generated GPU-price argument is `24`; the helper provides no minimum-bid or storage-price argument. The stock route therefore does not enforce the user's approved $3/GPU-hour, $0.30/GPU-hour minimum bid and $0.50/GB-month storage from initial publication. We did not run it. Its three-hour expiry is within the approved seven-day ceiling; the short expiry is not itself a violation.

The user permits listing only the new host at those terms, ending no later than September 15, 2026, and prohibits reboots. The contemplated explicit-listing expiry is September 15 at 00:00 Africa/Johannesburg (September 14 at 22:00 UTC), with no rolling renewal. This value has **not** been applied. CLI source describes listing expiry separately from ending existing customer jobs; no forced termination is authorized or proved.

## How this relates to the client-facing page

| Page and section | Statement or action under review | Evidence and what it does not establish |
|---|---|---|
| [Installing Host Software — Host Installer Wizard](http://127.0.0.1:4000/host/installing-host-software#host-installer-wizard) | Run the setup-page wizard and complete its checks | [Public installer/helper source inspection](source-inspection-02.md) establishes selected static side effects, not a successful TUI run. Downloaded TUI binary-to-local-source provenance is unresolved. |
| [Headless Fallback](http://127.0.0.1:4000/host/installing-host-software#headless-fallback) | Every GPU visible; Docker storage XFS with project quotas | [New-host observation](new-host-readonly-02.json) shows four GPUs and the mount. It does not prove CUDA, Docker, quota enforcement, network correctness or a completed headless installation. The query differs from the literal plain `nvidia-smi` example. |
| [After Install](http://127.0.0.1:4000/host/installing-host-software#after-install) | Services active; account registration; automatic self-test and results | Services are absent on this **pre-install** target. That is not a failure of the page's post-install expectation. No fresh registration, self-test, result or cleanup was observed. The helper's unlist is an attempted final command, not guaranteed cleanup after interruption. |
| [Install Command](http://127.0.0.1:4000/host/installing-host-software#install-command) | Use a fresh setup-page command in the intended account/team | [Existing-host history recovery](prior-host-history-01.md) supplies only limited invocation context and historical artifact identity. It does not authorize reusing any credential, prove the current command ran, or transfer account authority to the new host. |

Documentation wording is the claim under review, not independent proof of itself. These supplemental findings do not change any current material-claim status or close an install workflow.

## Retained observations, failures and corrections

- [Frozen plan and explicit authority amendments](plan.md); [exact dirty working-tree/index baseline](baseline.json).
- [SSH attempt 01](new-host-readonly-01.json) was BLOCKED by strict host-key lookup; no remote command ran. The [retest basis](ssh-capture-retest-basis.md) retained the same trusted pin bytes at a path without spaces. [Attempt 02](new-host-readonly-02.json) exited 0. Pin verification was never disabled. Serial reads were permission-denied, **not evidence of a physical-identity mismatch**; no sudo was used.
- [Three existing-host captures](prior-host-history-01.json) all exited 0. H100×8 had no readable named history/artifact; RTX4090 had no matching history; Ada had one sanitized invocation-context match and an installer hash. No historical terminal exit, registration response or cleanup result was recovered. No customer data, containers or workloads were inspected.
- [Source inspection 01](source-inspection-01.md) left helper listing unvalidated and misstated the extent of a `--no-daemon` block. [Source inspection 02](source-inspection-02.md) inspected the named helper, confirmed its temporary-listing path and corrected the block boundaries. Its `BLOCKED` execution disposition replaces the earlier nonstandard “FAIL-CLOSED” decision label. The earlier artifact is preserved.
- [Static listing-unit/expiry basis](listing-basis-01.json) pins a local CLI source revision and excerpts. It is not proof of the deployed helper executable, backend enforcement or commercial policy. The actual executable must be checked before a future listing. Its proposed `vol_size=0` is an unexecuted scope-control suggestion, not an approved payload or observed behavior; the CLI describes it as disabling a separate volume offer. No separate volume offer is authorized. Any future payload requires a reviewed decision on these side effects before execution.
- [Historical source ledger](historical-source-ledger-01.json) identifies the restricted records by label, heading and full digest. The [history integrity check](history-integrity-01.json) compares all three public captures with their restricted originals. Neither creates missing historical proof.
- [Sanitation correction and retest](sanitation-retest-01.md) masks one workstation path in the first source metadata record while retaining its complete original bytes privately. Source inspection 01's original interpretations remain available and superseded explicitly by inspection 02.

## Runtime/operator register

| Item | Status and concrete prerequisite | Next action / responsible role |
|---|---|---|
| Install the new host without unintended initial prices | BLOCKED: the stock helper generates its own GPU price and omits the approved bid/storage controls | Installer owner and authorized operator agree a reviewed install/listing route that prevents publication at other terms. Do not race the helper, rely on later price correction, or silently modify the stock installer. |
| Authenticate the new installation | BLOCKED: no fresh setup-page installation credential has been securely supplied for execution | Account operator provides a fresh setup key through an approved secret store once the install route is ready. The key pasted in chat is not reused or retained. |
| No-reboot and storage preservation | UNVALIDATED: public source is not a proof of every downloaded downstream artifact or host-side effect | Pin/review the exact executable chain and explicit storage/driver choices before installation. No reboot, formatting, NAT or package action has occurred in this package. |
| New-host registration and correct listing readback | BLOCKED behind safe installation and fresh account/target identity | Authorized operator confirms the newly assigned machine under the intended account, then sets and reads back the approved terms and fixed expiry. No unrelated host or volume offer is in scope. |
| Container, network, load, self-test result and cleanup | UNVALIDATED: no such runtime check was performed here | Plan separately after installation, with explicit workload/cost/cleanup boundaries and no customer interference. Historical external-port evidence is not a new public-self/container result. |

## Product, Finance, Legal and source-owner register

| Item | Status and evidence gap | Next action / responsible role |
|---|---|---|
| Supported installer controls for exact initial publication | BLOCKED: no suitable price/bid/storage control is exposed in the inspected stock path | Installer/source owner supplies or approves a safe supported route. A separately approved local variant, if chosen, must be labelled modified and cannot prove the untouched stock path. |
| Downloaded TUI and on-host CLI provenance | UNVALIDATED: local source is not bound to the downloaded binary or future helper executable | Release/source owner supplies reproducible revision/digest provenance; operator pins the actual artifacts. |
| Complete historical standard-installer execution | UNVALIDATED: reviewed bundles/history lack a retained terminal installer result | Evidence custodian checks the H100×8 v1.1 source ledger for a separately retained result. If absent, keep the historical invocation/postcondition limit; do not reconstruct an exit or repeat a live install merely for documentation. |
| Pricing, contract expiry and existing-rental obligations | UNVALIDATED beyond the inspected CLI interface | Product/Finance/Legal owner confirms any client-facing commercial or contractual claim. The user's approved prices authorize this operation; they do not establish platform policy. |

## Scope accounting

HIST-01 baseline/source intake, HIST-02 new-host read-only capture, HIST-03 three-host history recovery and HIST-04 public-source inspection are complete within their bounded methods. HIST-05's [additive reviewer presentation and final retest](reviewer-result.md) is also complete: 69 regression tests, 101 passage controls and all nine new evidence links pass on the final source. Four successful SSH captures are not four installed-host passes. No current claim count is changed by this intake; installation and external workstreams remain open.

No installer, listing, rental, self-test, reboot, service/package/network/storage mutation, BMC access, Host/API/setup credential use, push, merge, external post or human acceptance occurred. The approved SSH identity was used for the four bounded read-only captures.
