# Live Host Docs V&V authorization

`verification/live-vv-authorization.schema.json` defines the restricted record that must
exist before a frozen procedure uses SSH, sudo, a temporary WAN listener, a Host mutation,
the official Host self-test, or paid rental activity.

The completed record belongs in an approved restricted location outside Git. It must not
contain a Host key, client key, cookie, token, password, private key, or other secret. It
records only whether role-correct credentials are available through a secure non-chat
injection path. The public evidence package may retain the record digest, authorization
ID, time window, target alias, approved operation classes, numeric paid limits, and
sanitized outcome; it must not retain raw target coordinates or private identifiers.

## Required decisions

Record the approving human's full name and exact role, the start/end window and timezone,
and separate decisions for:

1. Host read-only SSH;
2. Host privileged read-only inspection;
3. bounded TCP and/or UDP listener plus external probe;
4. exact Host mutations;
5. bounded Host self-test activity; and
6. bounded paid rental activity.

An approved class must satisfy its schema conditions. In particular, WAN approval needs
an external client, an unused approved port, protocol-specific listener authority, and
cleanup authority.

Host self-test approval is separate from paid rental approval. It needs an authorized
Host-owner credential with `machine_read`, confirmation that the role is correct and the
credential can be injected securely outside chat, explicit workload-impact authorization,
a positive runtime limit, an automatic stop path, one attempt at a time, and cleanup
authority. It does not require `max_spend_usd`, a client/renter role, or a client
credential. The `--class host-self-test` validator class enforces this boundary.

Paid approval applies only to `paid_rental`. It needs positive `max_spend_usd` and
`max_runtime_minutes`, a confirmed client/renter role, one attempt at a time, an automatic
stop path, cleanup escalation, and either a provider hard cap or explicit approval for
bounded monitored execution without one. The `--class paid` validator class does not
authorize Host self-test.

On an active or shared Host, installer, package, firewall, service restart, reboot,
storage, network, removal, or workload-impacting procedures remain blocked unless the
record also confirms a disposable/isolated target, no affected workloads, a recovery
plan, exact operation approval, and cleanup authority.

Schema version `host-docs-live-vv-authorization/1.1` intentionally rejects version 1.0
records and the removed `paid_self_test` operation. Migrate by recording separate
`host_self_test` and `paid_rental` decisions; do not infer Host self-test approval from an
older paid approval.

## Current disposition

No completed restricted authorization record is yet bound to Procedure Baseline P1.
Local application or filesystem “full access” removes tooling friction but does not by
itself authorize live operations, Host self-test, spend, or destructive actions. Safe
local/static work continues while P1 is reconciled.
