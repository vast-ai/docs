# Host privileged VM and Docker retest — attempt 01

> **Qualification correction (2026-08-31):** The Host owner later confirmed that this target's VM/IOMMU setup was improper. The VM `check`, `off`, and `on -f` observations below are retained as exploratory process evidence only; they do not qualify those commands as tested. Their current status is `UNVALIDATED` and they are unscored pending the repaired-Host retest recorded in [`../2026-08-31-host-vm-environment-disqualification-01/result.md`](../2026-08-31-host-vm-environment-disqualification-01/result.md). The Docker result is unaffected.

## Scope and provenance

- Execution window: `2026-08-31T13:29:09Z` to `2026-08-31T13:31:45Z`
- Documentation target: branch `CON-1584-host-cli-api-sdk`, baseline commit `175d226adf1293c1ed54b74df6205ed7ac7fdff6`
- Test-set snapshot SHA-256: `63413c9c00fc394f727cb905db29aa787ac1ea3b4b8ef7c45ff6d727ed88a88c`
- Host target: `HOST_VV_TARGET`; authorized privileged SSH session; the stable machine and transport mapping is retained in the restricted local archive
- Installed VM helper SHA-256: `bb7c5922931aacbdff85528fcfb52733639db00361ae00b232f3cbfad0d251de`
- Authorization: the user explicitly authorized the disruptive VM state test after being told that forced enablement may install packages, restart services, and run a VM/GPU passthrough test.
- Secrets: SSH-key and API-key values were not printed or retained in this artifact.
- Predecessor: [`../2026-08-31-host-doc-defect-retest-01/result.md`](../2026-08-31-host-doc-defect-retest-01/result.md)

## Safety gate

Immediately before mutation, the Host-account view for `HOST_VV_TARGET` reported zero on-demand, reserved, resident, and running rentals; `client_end_date` was `null`; GPU occupancy was empty; and rented volume size was `0.0`. Root Host inspection reported zero running or stopped Docker containers, zero GPU compute processes, four GPUs expected from the account view, active Vast and Docker services, inactive libvirtd, no `.tried_vm_on` marker, no `kaalia.cfg`, and helper `check` result `pending`.

The machine remained listed during this bounded test. That created a residual race in which a new rental could theoretically have started after the precheck. A postcheck confirmed that all rental counters remained zero. Future full enablement attempts should prevent new rentals before beginning, then reconfirm no active work.

## Retained observations

### `CLM-9cba75bbdc780804` — disable VM support

Executed as root, equivalent to the documented sudo form:

```bash
python3 /var/lib/vastai_kaalia/enable_vms.py off
```

Observed process exit: `0`.

```text
Config file never written; skipping removal of VM config.
Marked machine to disable VM enablement.
VMs disabled.
```

The immediate unprivileged-form status check returned `off` with exit `0`. The helper created `/var/lib/vastai_kaalia/.tried_vm_on` as `root:root`, mode `0644`, size `1`; Vast and Docker services remained active.

Original classification, now superseded: `PASS`, score `3`. The output remains retained, but current qualification is `UNVALIDATED / UNSCORED` because this was not a representative VM environment.

### `CLM-ffda5e2c291c470e` — forced VM enablement retry

After reconfirming zero containers and GPU processes, executed as root, equivalent to the documented sudo form:

```bash
python3 /var/lib/vastai_kaalia/enable_vms.py on -f
```

Observed process exit: `0`.

```text
Config file never written; skipping removal of VM config.
IOMMU groups not set up for VMs, aborting.
```

The final status check returned `off`; the marker remained present and `kaalia.cfg` remained absent. Vast and Docker services were active, libvirtd was inactive, all four GPUs were visible, Docker had zero containers, and there were zero GPU compute processes.

Original classification, now superseded: `FAIL`, score `2`. The output still records the unmet IOMMU prerequisite and exit-`0` behavior, but current qualification is `UNVALIDATED / UNSCORED`; it does not establish a command defect or representative enablement behavior.

### `CLM-ca44522b22c4c5ee` — VM status check

The exact check command returned three observed states during the wider campaign: `pending` before an attempt and `off` after disablement and failed enablement. The check command itself exited `0` for both strings.

Original classification, now superseded: `PASS`, score `3`. Current qualification is `UNVALIDATED / UNSCORED`; the observed strings do not acceptance-test status reporting on a correctly configured VM-capable Host.

### `CLM-2c2c7d94c1bd259f` — Docker runtime diagnostics

Executed the corrected privileged block under root with pipeline-status checking:

```text
docker is /usr/bin/docker                                  [exit 0]
Docker version 28.5.2, build ecc6942                      [exit 0]
--runtime string  Runtime to use for this container       [pipeline exit 0]
Runtimes: io.containerd.runc.v2 nvidia runc               [pipeline exit 0]
Default Runtime: runc
```

Result: `PASS`, score `3`. This closes the prior documentation-permission failure for this diagnostic carrier and proves that the NVIDIA runtime is registered on this Host. It does not by itself prove GPU-container execution.

## Postcondition

At `2026-08-31T13:31:45Z`, `HOST_VV_TARGET` remained listed with all rental counters at zero and no client end date. Final VM configuration status was `off`, not the starting `pending` state, because the forced enablement aborted on IOMMU group setup. No undocumented direct-file manipulation was used to manufacture a `pending` or `on` result.

A later read-only Host follow-up at `2026-08-31T14:02:17Z` again reported VM status `off`, active Vast and Docker services, zero Docker containers, and zero GPU compute processes.

## Documentation implications

The following wording changes are supported as safety guidance and descriptions of the observed/helper-source behavior, but this attempt does not validate the VM commands themselves. Their functional and semantic qualification remains pending the repaired-Host retest.

1. Keep `sudo` and an approved idle/no-active-rental gate for `off` and `on -f`.
2. Explain that `off` marks VM enablement disabled and removes VM configuration when present; it does not establish that the Host is idle.
3. Explain that `-f` forces a state-changing retry and may perform substantial Host setup; it is not proof of success.
4. Require a follow-up `check` and accept only exact `on` as successful enablement.
5. Treat error or abort text as failure even when the helper process exits `0`.
6. For `IOMMU groups not set up for VMs, aborting.`, correct BIOS/kernel IOMMU configuration and verify grouping before retrying.
7. Verify GPU visibility and Host services before returning the machine to service.

## Remaining gap

The VM `check`, `off`, and `on -f` commands are all `UNVALIDATED / UNSCORED`. Their exploratory outputs must remain visible, but none can be promoted until the Host prerequisite is corrected and a new authorized, representative retest completes the full state-transition and health sequence.
