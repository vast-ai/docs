# Host Docs command V&V coverage

Coverage is counted over the 165 command carriers frozen in
`host-docs-test-sets.json`. Commands are grouped in page/procedure context; a
help check proves only that a CLI signature is registered, not that its runtime
behavior supports the page.

| Evidence available | Command carriers | Context units |
| --- | ---: | ---: |
| Behavior PASS | 5 | 5 |
| Behavior attempted but BLOCKED | 8 | 7 |
| CLI signature only | 55 | 55 |
| No signature or behavior evidence | 97 | 91 |
| **Total** | **165** | **158** |

The installed CLI passed all 42 leaf-signature help checks. Thirty-eight of
those signatures occur in the Host-page command population and map to 68
carriers; 13 of those carriers also have behavioral attempts. Of the 55
signature-only carriers, 33 are display-only, 15 are executable but not yet
run, and 7 are already source-defect blocked.

Thirteen carriers currently have page-context scores: two score `3` and eleven
score `2`. No carrier has score `1`. The remaining 152 carriers stay unscored;
static syntax evidence must not be promoted to behavioral support.

## Highest-value next runs

1. Repeat the seven blocked read-only CLI contexts with a Host-capable
   `machine_read` key and an owned machine target. This addresses eight carriers
   across fleet operations, maintenance, market metrics, and workload policy.
2. Run the frozen read-only Host snapshot from a network context that can reach
   the authorized machine. Its nine procedure contexts cover 22 carriers in 21
   context units across hardware, services, Docker, storage, GPU, kernel/ECC,
   fabric, and VM status.
3. Keep Host Teams' 32-carrier catalog static: the page presents it as reference
   material, not as a workflow to execute for coverage.

Mutating, destructive, paid, installer, reboot, listener, packet-capture,
container-load, and source-defect-blocked branches remain excluded until their
specific prerequisites and authority are satisfied.
