# Runtime/operator register — after successful listing and one client rental

## Resolved in this attempt

- Listing prerequisites: explicit lower network prices approved;0.10 rejected,
 0.01 accepted. Final owned-machine readback matches GPU3, bid0.30,
 storage0.50, bandwidth0.01each, discount0, min_chunk1, fixed expiry1789423200,
 durationnull and no separate volume offer. [Final Host observation](rate-001/host-read-09.json).
- Distinct Host/client accounts and sufficient client credit observed via the
 two named credential entries. No missing client-key blocker remains here.
- One-GPU client create/visibility/runtime/cleanup observed. Instance50364501
 was the only new contract created; only it was deleted. Its owner-scoped
 absence is retained in [cleanup](rental-run-03/cleanup-main.json).
- [Tiny GPU computation](rental-run-03/gpu-result-01.json) passed; independent
 watchdog finished without duplicate deletion. No active test rental remains.

## Still unvalidated, not automatically BLOCKED

| Work | Missing proof / impact | Exact next action and responsible role |
| --- | --- | --- |
| Final instance billing | Immediate account credit delta is not settled or attributable cost; no claim of free run or exact bill. | Authorized client operator retrieves a settled invoice/cost record scoped to50364501 and records attribution limits. No additional paid run is needed merely to attach existing billing. |
| SSH and independent external connectivity | This run used args-mode and own-container logs; it did not open SSH or test WAN/public-self routing. | Authorized operator defines an exact networking/SSH test and retains client route/host correlation, using separate scope and safety checks. |
| Full marketplace self-test and diagnostic paths | Tiny CUDA result does not establish all tests, flags, support bundle or cleanup branches. | Freeze selected documented command/CLI/image version, network location, paid bounds and cleanup before a separately approved self-test. |
| Stock TUI/standard/update-fallback installer routes | Prior modified direct route plus this later rental is not execution of the three stock routes. | Installer owner supplies canonical release/provenance; an authorized operator tests the selected unmodified route on an appropriate fresh host without disturbing this listed host or customers. |
| Persistence, load/stability, public-self fix, backup access | No reboot, stress test, router repair or new jump server was performed. | Scope those acceptance operations separately with an operator and appropriate maintenance authorization; do not infer them from the rental. |

Machine150296 remains publicly listed until the fixed approved expiry. Customers
may subsequently arrive; recheck occupancy before any future host operation.
No current missing-price or sudo-authentication blocker is carried forward from
the earlier attempts. No broader Host Docs completion is asserted.
