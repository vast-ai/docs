# Refreshed offer binding — before new creation attempt

The original collector stopped before create because its fixed offer50363390
was unavailable. rental-error-01.json preserves that guard failure. No create
request, paid instance or cleanup was invoked. The diagnostic
offer-refresh-02.json independently returns offer50363393 on the same machine,
oneGPU, is_bid=false and the same approved client quote.

Apply rental-inventory-01.md unchanged except: selected offer is50363393;
unique label is host-docs-vv-150296-20260909-attempt02-run02; all new execution
records are under rental-run-02/. The collector now retains the fresh quote
before evaluating its guard, so later quote failures also retain their inputs.
No prior request, expectation or failure record is overwritten.

Safety fixes from rental-safety-review-02.md remain: pre-create reconciliation
watchdog, owner/machine/GPU/label/absent-before guards, is_bid=false and fresh
distinct accounts. Same pinned image, tiny workload,10GB, operational USD5
budget and20minute ceiling; early cleanup watchdog at10minutes. No new scope.
