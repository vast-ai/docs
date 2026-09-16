# SSH public-key projection correction, before create

The first public-key readiness probe looked for ssh_key/key in response rows.
The actual GET /ssh/ response names its public key field public_key. The initial
BLOCKED result therefore reflects a collector field mismatch, not proof that
the approved SSH key is missing. No key was added and no rental was created.

Preserve client-public-key-readiness-01.json. Retest the exact type/base64 public
key comparison against public_key; do not inspect or retain private-key fields.
Apply the same field correction to the still-unexecuted rental prerequisite.
All later launch preconditions and cleanup guards remain unchanged.
