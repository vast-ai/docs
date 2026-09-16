# Host H100 read-only connection — BLOCKED

The bounded SSH attempt at 2026-09-08T13:45:03Z stopped with exit code 255
because the remote host identification differs from the saved trusted key.
No remote GPU command executed. See [the exact sanitized observation](execution.json)
and [the frozen plan](plan.md).

Specific unavailable prerequisite: independently authenticated confirmation of
the changed SSH server identity. This may result from an authorized rebuild/key
rotation, a reassigned address, or an unexpected endpoint; this attempt does not
establish which explanation applies.

The endpoint presented an ED25519 fingerprint of:

`SHA256:f974AWafc8Sv/C587crquZTGt2+R06jTs8YbC2+UHTo`

This is an untrusted observation, not an accepted fingerprint. The existing
trust entry was reported as ECDSA. No known_hosts entries were removed or added,
no key was accepted automatically, and no alternative credential was tried.

Next action: the user or Host administrator verifies the ED25519 fingerprint
directly at the trusted server console or through an independently trusted
administrative channel. For example, read the server's public host-key fingerprint
at its console with `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`.
If that trusted value matches and the key change is expected, authorize updating
only the affected saved Host entry, then repeat the same read-only check as a new
attempt. Do not weaken StrictHostKeyChecking or infer trust from this connection.

Claim impact: no new GPU identity or renter execution evidence was obtained.
MCL-e12ac9f6be2ce502 remains unchanged / UNVALIDATED in the current package;
this specific SSH check is BLOCKED, not the whole Host documentation project.
Its proposed product-description evidence binding does not require this SSH
connection and remains separate documentation work.

No sudo, Host/API call, self-test, process/container inspection, storage access,
service or workload mutation, paid operation, commit, push, or acceptance occurred.
