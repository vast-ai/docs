# Host Docs command V&V coverage

Coverage is counted over the 165 command carriers frozen in
`host-docs-test-sets.json`. Commands are grouped in page/procedure context; a
help check proves only that a CLI signature is registered, not that its runtime
behavior supports the page.

| Latest evidence available | Command carriers |
| --- | ---: |
| Behavior `PASS` | 15 |
| Behavior attempted but `BLOCKED` | 14 |
| Behavior `FAIL` | 1 |
| Behavior `NOT_APPLICABLE` | 1 |
| CLI signature only | 55 |
| No signature or behavior evidence | 79 |
| **Total** | **165** |

The installed CLI passed all 42 leaf-signature help checks. Thirty-eight of
those signatures occur in the Host-page command population and map to 68
carriers. Host-account retesting resolved the seven earlier credential or
ownership blockers and reproduced the `/host/not-in-search` sequence under the
correct account. A live read-only SSH snapshot added behavior for 18 Host-shell
carriers across hardware, services, Docker, storage, GPU/kernel, Fabric Manager,
and VM status.

Thirty-one carriers now have page-context scores: twelve score `3`, eighteen
score `2`, and one scores `1`. The score-1 carrier is the non-root
`docker info | grep -i runtime` instruction on `/host/machine-errors`; it failed
on Docker-socket permission while adjacent privileged Docker checks use
`sudo`. The remaining 134 carriers stay unscored; static syntax evidence must
not be promoted to behavioral support.

## Highest-value next runs

1. Complete the short interactive-privilege queue: exact `sudo` log checks,
   `sudo docker ps`, `sudo docker system df`, and a privileged retest of
   `docker info | grep -i runtime` before correcting the score-1 instruction.
2. Separately authorize and bound Docker GPU-injection, paid self-test, and
   external TCP/UDP reachability if those live branches are required for this
   review. Record instance, cost, image digest, cleanup, and WAN evidence.
3. Exercise maintenance/report/fault branches only when a representative safe
   state exists. Empty current results validate access, not known-record fields
   or report-to-log correlation.
4. Keep Host Teams' catalog static: the page presents it as reference material,
   not as a workflow to execute for coverage.

Mutating, destructive, paid, installer, reboot, listener, packet-capture,
container-load, and source-defect-blocked branches remain excluded until their
specific prerequisites and authority are satisfied.
