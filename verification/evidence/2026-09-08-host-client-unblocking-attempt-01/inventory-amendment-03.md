# Inventory amendment 03 — safe VM status query

Before execution: root full-source inspection and an independent source-only audit agree that the exact check dispatcher calls only vm_check, whose effects are read-mode opens and status text. No enable, disable, validate, subprocess, sudo, logfile write or workload path is reached. The local source-copy one-LF digest difference is explicitly reconciled in vm-source-copy-reconciliation-01.json.

Add VM-STATUS-01: on the same strict-trust Ada SSH target, verify the installed helper still has SHA-256 bb7c5922931aacbdff85528fcfb52733639db00361ae00b232f3cbfad0d251de, then invoke exactly python3 /var/lib/vastai_kaalia/enable_vms.py check with a 10-second child timeout. Abort on digest change. Retain exit, exact status token, source digest and default-user state-file readability booleans only; never config contents. The query fits existing read-only authority, not new privilege/workload authority.

PASS can establish only exact diagnostic invocation/token, not VM enablement success or the Retry Enablement procedure. pending/off can mask state-file read errors because the helper catches them; keep this limitation visible. Source remains installed-artifact evidence rather than an authenticated upstream revision. No other helper mode may run.
