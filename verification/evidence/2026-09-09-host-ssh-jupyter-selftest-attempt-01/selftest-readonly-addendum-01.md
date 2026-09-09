# Normal self-test preflight — fail-closed execution scope

The approved normal self-test has an observed prerequisite failure: machine 150296 reliability is about 85.1%, below its CLI's >90% requirement. The Host account's available funds have not been established as sufficient for the approved maximum. Do not bypass requirements or attempt a paid self-test.

After independent cleanup and fresh idle checks, invoke the exact pinned CLI's normal `self-test machine 150296 --support-bundle-dir <private-0700-directory>` with the named Host account. A disposable transport allowlist permits only the real offer search POST and exact machine GET. All other API requests, especially create/update/delete, are rejected before transmission. This guard is not a product modification and is an explicit limitation of the observation.

Retain the actual structured result and local failure-bundle inventory. CLI exit zero in raw mode is not PASS: evaluate `success` and `stage`. A preflight failure proves only that failure path and any actual bundle creation, not an image launch, completed diagnostics, machine verification, or full runtime acceptance. If the guard blocks an unexpected create, record that separately. No `--ignore-requirements`, reboot, image publication, or paid self-test is permitted by this addendum.
