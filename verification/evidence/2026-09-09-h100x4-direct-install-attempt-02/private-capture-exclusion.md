# Local raw-evidence staging protection

Read-only `git check-ignore` initially returned exit 1 for the current restricted installation, postcheck and Host API captures. Their modes were 0600, and `git ls-files` confirmed none of the four task-private directories was tracked, but default staging could still have included them. No private content was committed or pushed by this attempt.

Corrected only the repository's local Git `info/exclude` metadata by appending these exact directory rules:

```gitignore
/.orchestra/h100x4-install-history/
/.orchestra/h100x4-safe-installer/
/.orchestra/h100x4-direct-install/
/.orchestra/h100x4-direct-install-02/
```

The existing exclude comments were preserved. These local exclusions cover task-created private captures, credentials-bearing raw logs and temporary implementation/archive worktrees; they do not remove evidence or alter the tracked/staged patch. Shareable projections remain under `verification/evidence/`. Final integrity records the corrected `git check-ignore`, 0600 modes and unchanged staged-content hash. Ignore rules reduce accidental staging risk; they do not prevent an explicit force-add or substitute for secret review before publication.
