# H100×4 direct-install observations

The sudo prerequisite is resolved. The approved modified direct installer ran from **2026-09-08 22:09:12 to 22:18:18 UTC** (September 9 South Africa). It returned zero, reported NVML and NCCL success, submitted machine information, and deliberately omitted the late automatic marketplace self-test/listing launch. Independent post-install observations, not the exit code alone, establish the results below.

## Observed results

- `preflight-01.json`: `sudo -n true` and `sudo -n id -u` succeeded. Exact pinned-host, storage, GPU-idle and SSH-policy guards passed. Prior failed sudo attempts remain in the September 8 attempt.
- `install-execution-01.json` and `install-output-01.log`: the exact reviewed local candidate ran with `--no-driver --no-partitioning --no-libvirt --ports 30000 30499`. No stock TUI run is claimed.
- `postcheck-02.json`, POST-01: the documented four services were all active.
- POST-03: all four H100 PCIe GPUs were visible through `nvidia-smi`.
- POST-05: `/var/lib/docker` remained on the existing XFS filesystem with `prjquota`; POST-07 confirms **Project** accounting and enforcement ON. The separate User and Group quota states were OFF, which is not a project-quota failure.
- POST-08: host port range was `30000-30499`. This does not prove router forwarding or public-self/NAT reflection.
- Boot identity is unchanged, no reboot-required marker or Docker loopback fallback file was present, and `dpkg --audit` was empty.
- `machine-readback-02.json`: the exact authorized Host account returns the newly registered four-GPU machine, ID **150296**, with `listed: false`. The earlier in-progress HTTP 200 / empty response is retained as `machine-readback-01.json`; it was not proof of account mismatch.

## Warnings and limits

The installer log contains package-manager lock errors in a downstream helper and deprecated `apt-key` warnings. Preserve these failures: a zero final exit does not mean every subcommand passed. The later package audit was clean; it does not retroactively erase the lock failure. The fetched `send_mach_info.py` in the controlled directory and installed data directory had identical SHA-256 at the snapshot, and the retained output contains `Data sent successfully.`

A transient bandwidth diagnostic container was still running in the first postcheck. That snapshot is not cleanup proof. No customer/renter workload was created by the assistant. Driver installation, libvirt, reboot persistence, guided-TUI behavior, stock standard-installer behavior, separate marketplace self-test, paid rental acceptance, external network/NAT reflection and broad host-health claims remain outside this result.

The first verbose postcheck projection was moved to a restricted local archive, preserving its bytes and the original SSH capture. `postcheck-02.json` is a cleaner projection of the **same** observation, not a rerun: it omits unnecessary environment dumps, container labels and network/provider identifiers while retaining replayable command outputs and raw hashes.

## Listing hold at this checkpoint

No offer-write request has been sent. Approved values are USD 3/GPU-hour, minimum bid USD 0.30/GPU-hour, USD 0.50/GB-month storage, fixed expiry **1789423200** (September 15 00:00 South Africa), and no separate volume offer. The CLI transmits unspecified bandwidth prices and maximum prepaid discount as null; inspected client code does not establish server defaults. The remaining decision is the upload/download bandwidth price and allowed prepaid discount. Proposed to the user: USD 0/GB in both directions and prepaid discounts disabled. Await that choice before publishing; do not silently extend expiry or infer acceptance from listing.

This checkpoint is evidence of this modified direct run and exact observations. Documentation text remains the claim under review, never its own proof. Formal per-claim binding and reviewer regression are separate repository work.
