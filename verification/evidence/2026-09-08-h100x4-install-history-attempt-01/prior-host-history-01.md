# Prior-host installation history — read-only result

`HIST-03-PRIOR-HOST-HISTORY-01` completed one strictly pinned, noninteractive, unprivileged SSH read for each approved alias. The collector returned only metadata, SHA-256 values, match counts, feature tags, and matching-line hashes; it returned no command lines, installer contents, logs, or credentials.

| Alias | SSH result | Narrow result | Limit |
| --- | --- | --- | --- |
| H100×8 prior install | exit 0 | No readable allowlisted history or named installer artifact | Does not disprove historic installation and supplies no exit/result. |
| RTX4090 prior install | exit 0 | Readable current bash history had zero allowlisted matches | Does not confirm or disprove earlier installation. |
| RTX 6000 Ada prior install | exit 0 | One sanitized history match plus an existing installer-file identity candidate | Invocation context only; no terminal exit, registration, listing, workload, or cleanup result. |

The Ada match has only `installer_python_invocation`, `no_driver_option`, `no_partitioning_option`, and `ports_option` categories. Its source line is not published. Exact timestamps, hashes, and match counts are in [prior-host-history-01.json](./prior-host-history-01.json).

Restricted local captures are mode 0600. No sudo/root escalation, reboot, service/package change, Host/API action, customer inspection, or raw history/log publication occurred.
