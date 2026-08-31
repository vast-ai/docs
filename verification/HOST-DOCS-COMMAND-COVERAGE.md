# Host Docs command V&V coverage

Coverage is counted over the 165 command carriers frozen in
`host-docs-test-sets.json`. Commands are grouped in page/procedure context; a
help check proves only that a CLI signature is registered, not that its runtime
behavior supports the page.

| Latest evidence available | Command carriers |
| --- | ---: |
| Behavior `PASS` | 15 |
| Behavior attempted but `BLOCKED` | 16 |
| Behavior observed on a non-representative target and therefore `UNVALIDATED` | 3 |
| Behavior `FAIL` | 0 |
| Behavior `NOT_APPLICABLE` | 1 |
| CLI signature only | 53 |
| No signature or behavior evidence | 77 |
| **Total** | **165** |

The installed CLI passed all 42 leaf-signature help checks. Thirty-eight of
those signatures occur in the Host-page command population and map to 68
carriers. Host-account retesting resolved the seven earlier credential or
ownership blockers and reproduced the `/host/not-in-search` sequence under the
correct account. A live read-only SSH snapshot added behavior across hardware,
services, Docker, storage, GPU/kernel, and Fabric Manager. VM status and
state-transition outputs were also captured, but the Host owner later confirmed
that the target's VM/IOMMU setup was improper. Those three VM carriers are
retained as observations only and remain `UNVALIDATED`.

Thirty-two carriers now have page-context scores: twelve score `3`, twenty
score `2`, and none score `1`. A privileged retest of
`sudo docker info | grep -i runtime` passed and remains score `3`. The three VM
scores were withdrawn because their target was not representative; they remain
unscored pending a repaired-Host retest. The remaining 133 carriers stay
unscored; static syntax and disqualified observations must not be promoted to
behavioral support.

## Highest-value next runs

1. After repairing and rebooting the Host's BIOS/kernel IOMMU setup, run the
   controlled VM sequence `check → off → check → on -f → check` with the Host
   idle and capture state, health, and cleanup evidence.
2. Complete the remaining short interactive-privilege queue: exact `sudo` log
   checks, `sudo docker ps`, and `sudo docker system df`.
3. Separately authorize and bound Docker GPU-injection, paid self-test, and
   external TCP/UDP reachability if those live branches are required for this
   review. Record instance, cost, image digest, cleanup, and WAN evidence.
4. Exercise maintenance/report/fault branches only when a representative safe
   state exists. Empty current results validate access, not known-record fields
   or report-to-log correlation.
5. Keep Host Teams' catalog static: the page presents it as reference material,
   not as a workflow to execute for coverage.

Mutating, destructive, paid, installer, reboot, listener, packet-capture,
container-load, and source-defect-blocked branches remain excluded until their
specific prerequisites and authority are satisfied.
