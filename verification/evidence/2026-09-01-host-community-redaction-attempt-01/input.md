# Synthetic Host help request under review

This is a synthetic review fixture. It does not describe a real account, machine,
rental, network address, or customer workload.

## Draft

**Symptom:** The Host console shows the exact error `Port Networking Issues`, and the
outside-LAN UDP check times out while the bounded TCP check succeeds.

**Safe context:** Host alias `TEST-HOST`; account context `TEST-HOST-ACCOUNT`; tested
endpoint `PUBLIC_IP:PORT`. These are placeholders, not real identifiers.

**Checks already completed:**

- Confirmed the documented router forwarding range targets the intended Host LAN address.
- Confirmed the temporary TCP listener was stopped after the bounded check.
- Confirmed no UDP result was inferred from the successful TCP result.
- Compared the visible error with the Host Machine Error Reference and Network & Ports
  guidance.

**Reviewed excerpt:** `UDP packet was not observed during the bounded outside-LAN test.`

**Request:** Please suggest the next safe Host-side or router-side observation. No API
key, installer command, account token, renter file, renter output, unrestricted log, or
diagnostic bundle is attached.

## Required review

Reject this fixture if it contains a credential, account-specific installation material,
real machine/account/network identifiers, renter data, or an unreviewed log/bundle.
