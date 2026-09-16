# Inventory amendment 02 — readable installed VM helper

Before execution: HOST-04 established that the exact VM helper is readable to the authorized default SSH user on the Ada target. Add SOURCE-01: read only this installed source file, bounded to 128 KiB, retain a digest and restricted local source copy for inspection. Do not import or execute it. Inspect top-level code, check/enable/disable dispatch and dependencies before considering any check-mode invocation. Readable source does not grant root or workload authority. No helper execution is authorized by this amendment.

Source contents are an installed-artifact observation, not a proven upstream revision or complete backend implementation. Any statements retain that limitation. Do not copy machine addresses, account data, secrets or renter material into public evidence.
