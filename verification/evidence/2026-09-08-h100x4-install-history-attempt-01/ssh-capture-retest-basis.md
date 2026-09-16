# SSH collector retest basis

The first strict SSH attempt returned `No ED25519 host key is known` before remote execution. The approved installed-host pin does exist and its fingerprint exactly matches the console-verified fingerprint in the September 8 rebuild record. Its original pathname contains spaces, which is suspected to be parsed as multiple UserKnownHostsFile paths.

Retest 02 uses a byte-identical task-local copy of that approved pin at a no-space path, preserving StrictHostKeyChecking, key-only BatchMode, exact address and approved operations-key fingerprint. It does not accept a new host key or change the trusted source file. The original collector and failed record are retained. The captured source-pin digest must match the original before the result can be accepted.
