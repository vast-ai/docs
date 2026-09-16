# RTX4090 readiness — retry 02 result

SSH readiness: **PASS**, limited to the authorized first-use trust and read-only observations. [Original strict-trust failure remains retained](../2026-09-08-host-rtx4090-readiness-attempt-01/result.md).

- [Exact baseline](baseline.json), [frozen plan](plan.md), [execution](ssh-execution.json), [first-use trust record](trust-record.json).
- The user authorized trusting this exact Host. `accept-new` enrolled its ED25519 key; no changed-key bypass was used. All later checks used strict checking. This is trust on first use, not an independently compared console fingerprint.
- Default-user SSH returned four RTX 4090 GPUs, driver 595.84. This establishes GPU enumeration at capture time, not workload health or verification eligibility.
- No `vastai` executable, default Python package, or either standard CLI key file was present in that user's default environment. That does not rule out another machine, user or virtual environment. Client-key checks remain **BLOCKED** pending its exact authorized location; do not search arbitrary secrets.

The confirmed Host Keychain credential and existing local CLI checkout allowed the subsequent [live read-only batch](../2026-09-08-host-live-readonly-attempt-01/result.md). No CLI was installed on the Host. No paid, self-test, sudo, workload, configuration, deletion, publishing or acceptance action occurred. The only lasting configuration change here is the user-authorized local SSH trust entry.
