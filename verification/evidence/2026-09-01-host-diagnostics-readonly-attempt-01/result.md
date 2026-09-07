# Host diagnostics privileged-read verification — attempt 01

- Attempt ID: `ATTEMPT-2026-09-01-HOST-DIAGNOSTICS-READONLY-01`
- Evidence ID: `EV-DIAG-READONLY-01`
- Procedures: `TS-DIA-E02`, `TS-DIA-E03`, `TS-ERR-T02`, `TS-ERR-T03`,
  `TS-ERR-T04`, `TS-ERR-T05`, `TS-ERR-T06`
- Target: restricted alias `HOST_VV_TARGET`
- Transport: restricted alias `HOST_VV_SSH`
- Started at: `2026-09-01T15:13:31Z`
- Repository revision/tree: `7a8a2c4c571dcf64341055e8277083e5aea380bf` /
  `0208322af8aa3217f90f7f6879d70f8eb0b62862`
- Test-set snapshot SHA-256:
  `a61a9f23ff2e24c6daf8763c123efcf1190715045037e0b202d09e4ac1f3ea77`
- Execution class: authorized Host privileged read-only
- Service, Docker, VM, network, account, offer, paid, load, and filesystem mutation:
  none

## Safety and evidence handling

The supplied SSH key completed non-interactive root authentication. Only bounded reads
from the exact documented diagnostic groups ran. Raw journal, daemon, PCI, GPU, device,
container, network, and filesystem output is not published. Where output could contain
target-specific detail, this record retains only exit state, counts, or SHA-256. No
credential was requested, printed, or retained.

Docker GPU injection, GPU burn, live-follow reproduction, external WAN probes, paid
self-test, VM operations, and every mutating command were deliberately excluded.

## `DIA-E02` service, port, and storage snapshot

The commands were executed in their documented groups against one time-local Host
snapshot.

| Documented observation | Exit | Sanitized result |
| --- | ---: | --- |
| `systemctl is-active vastai.service vast_metrics.service docker nvidia-persistenced.service` | 0 | All four requested units reported `active`. |
| `sudo journalctl -u vastai.service -n 80 --no-pager` | 0 | 80 bounded lines; SHA-256 `69392caccff1de83aebe781e56aa83e57978051a4378793e905b90b7304efd25`. |
| `sudo journalctl -u vast_metrics.service -n 80 --no-pager` | 0 | 80 bounded lines; SHA-256 `c9351a1c110cb66ce746c96d06f46e68e0c95f6ed4fa318b2950ab58fc240a91`. |
| `sudo tail -n 100 /var/lib/vastai_kaalia/kaalia.log` | 0 | 100 bounded lines; SHA-256 `de2c232386f49c94f69b57d57a99e98ad3305756d035b7149a7d93f3bebab847`. |
| `sudo cat /var/lib/vastai_kaalia/host_port_range` | 0 | Configured range exactly matched the separately supplied forwarding specification; values omitted. |
| `df -h /var/lib/docker` | 0 | Docker-filesystem capacity returned normally; device and volume values omitted. |
| `sudo docker system df` | 0 | Docker usage categories returned normally. |
| `findmnt /var/lib/docker -no SOURCE,FSTYPE,OPTIONS` | 0 | Separate XFS Docker mount with project quota; source device omitted. |

A narrow follow-up scan over only those three bounded log windows found zero selected
`fatal`, `panic`, `failed`, `restart loop`, or `restarting` tokens. This is not a general
health guarantee and does not replace review of a reported incident window.

Current disposition:

- `DIA-E02-B01-S01` and `DIA-E02-B01-S02`: `PASS` for the documented same-target
  service/log/range snapshot and comparison.
- `DIA-E02-B01`: `PASS`.
- `DIA-E02-B02-S01`: `PASS` for Host-local port/storage collection.
- `DIA-E02-B02-S02`: `BLOCKED`; the user-supplied forwarding specification matches the
  Host file, but router/firewall/provider state was not independently observed.
- `DIA-E02-B02` and `TS-DIA-E02`: `BLOCKED`; Host-local evidence cannot prove the
  external forwarding boundary.

## Docker daemon and storage diagnostic groups

| Documented observation | Exit | Sanitized result |
| --- | ---: | --- |
| `systemctl is-active docker` | 0 | Docker reported `active`. |
| `sudo journalctl -u docker -n 100 --no-pager` | 0 | Bounded output retained as SHA-256 `ad9585936c828ed75922d557dc30561bd550008ac20febc2b53c5b4b8582a18c`. |
| `sudo docker ps` | 0 | Exact command succeeded; output SHA-256 `f95becc007e273e85566e7ed2126c0fec7ebe43307f85564bcb1537f50aa0a98`; zero running containers. |
| `df -h /var/lib/docker` / `sudo docker system df` / `findmnt /var/lib/docker -no SOURCE,FSTYPE,OPTIONS` | 0 | Capacity, Docker-object usage, and XFS/project-quota mount facts were all observable. |

`ERR-T02-B03-S01` passes as a Docker-daemon collection step on this snapshot.
`ERR-T05-B02-S01` passes as a storage collection step. Their parent symptom procedures
remain `UNVALIDATED`: no Docker-daemon outage or full-storage failure was reproduced.

## Kernel, PCI, GPU, and ECC diagnostic groups

The exact current-boot and previous-boot `journalctl` pipelines returned matching output
with exit 0. Their retained SHA-256 values are
`8e8d247a5d7940015b2f83d7ef0b46389004eef9f48488c99962cf4b3606fd56`
and `bca62a6037e0237f6bf90651a4eb57798046b8bea5715ff72a82dcfe233705ae`.

The remaining sources produced the documented evidence gaps rather than being coerced to
PASS:

- exact `sudo dmesg -T | grep ...` returned exit 1 with no match;
- the current plain syslog and kern.log files were readable, but both `.1` inputs were
  absent, so the exact multi-file grep returned exit 2 while still emitting current-file
  matches;
- no matching compressed history was present, so exact `zgrep` returned exit 2;
- the focused current-boot count contained no `Xid`, no `fallen`, and no
  `PCIe Bus Error` match; broader `NVRM`, `AER`, or `PCIe` tokens were present and are not
  interpreted as a fault without incident-time context.

The exact `lspci | grep -i nvidia`, `nvidia-smi -L`, kernel-journal, `nvidia-smi -q -d
ECC`, and `nvidia-smi -q | grep -iE 'Xid|Remapped|Pending'` reads all exited 0. The PCI
and NVIDIA inventories were mutually consistent, volatile corrected and uncorrected ECC
totals were zero for every observed GPU, and no row-remap repair was pending. The exact
Xid-only journal grep returned exit 1 with no match. Hardware identifiers are omitted.

These results pass the bounded collection behavior of the applicable read-only command
carriers. They do not pass `TS-DIA-E03`, `TS-ERR-T03`, `TS-ERR-T04`, `TS-ERR-T05`, or
`TS-ERR-T06`: there was no exact reported symptom/time correlation, Docker GPU-injection
result, load reproduction, NVSwitch target, full-storage condition, missing-GPU condition,
or repeated rental failure.

## Claim limits and remaining gates

This attempt proves that the bounded privileged-read forms return useful observations on
one authorized Host and records their exception behavior when optional historical logs
or grep matches are absent. It does not prove external network reachability, a failure
path that was not present, container GPU injection, behavior under load, marketplace
acceptance, paid self-test behavior, or VM readiness. Those claims remain separately
`BLOCKED`, `UNVALIDATED`, or `NOT_APPLICABLE` as their context requires.
