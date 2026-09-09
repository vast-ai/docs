# Pre-execution safety review and correction

The first private runner was not executed against Vast. Five static predicates
passed but independent source review found three missing safeguards: cleanup
was armed only after a successful create response, the offer response did not
require is_bid=false, and fresh Host/client identities were not compared.

The original runner is preserved privately as rental-pre-review.py. The
corrected version arms an independent reconciliation watchdog BEFORE the PUT,
restricts fallback discovery to a unique new owned id with exact machine150296,
oneGPU and previously absent attempt label, verifies is_bid=false, and requires
fresh distinct named-account IDs. Zero or ambiguous watchdog matches never
authorize deletion. Unknown create results must be reconciled, never retried.

Independent read-only re-review inspected actual source SHA
2f5840fb478ce2e7e99b5d19e5d5bdd40918298a59dee769f5a3437421caea3a
and found no remaining must-fix for this bounded run. Root inspected the actual
code and retained [eleven static checks](rental-static-retest-02.json).
This is safety/code review, not rental execution evidence or human acceptance.

The five-dollar ceiling remains operational monitoring, not a platform-enforced
spend cap. No SSH, stress, broad traffic, host repair or other-instance mutation.
If cleanup is not confirmed, stop further work and reconcile the exact contract.
