#!/usr/bin/env bash

# One-time, read-only Host Docs V&V plan. This file is evidence, not a reusable
# execution harness. It performs no installation, restart, mutation, workload,
# listener, WAN probe, credentialed API call, or paid action.

set -u
export LC_ALL=C

run_check() {
  check_id="$1"
  command_text="$2"
  printf '\n=== BEGIN %s ===\n' "$check_id"
  printf 'command=%s\n' "$command_text"
  timeout 30s bash -o pipefail -lc "$command_text"
  exit_code=$?
  printf 'exit_code=%s\n' "$exit_code"
  printf '=== END %s ===\n' "$check_id"
}

printf 'attempt_started_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

run_check META-001 'hostname; id; date -u +%Y-%m-%dT%H:%M:%SZ'
run_check AUTH-001 'sudo -n true'

run_check HWP-E01-S02-OS 'lsb_release -a'
run_check HWP-E01-S02-KERNEL 'uname -a'
run_check HWP-E01-S02-CPU "lscpu | sed -n '1,25p'"
run_check HWP-E01-S02-PCI "lspci | grep -i nvidia"
run_check HWP-E01-S02-BLOCK 'lsblk -f'
run_check HWP-E01-S02-FINDMNT-EXACT 'findmnt / /data0 /var/lib/docker'
run_check HWP-E01-S02-ROOT 'findmnt /; df -h /'
run_check HWP-E01-S02-DATA0 'findmnt /data0'
run_check HWP-E01-S02-DOCKER-MOUNT 'findmnt /var/lib/docker -no SOURCE,FSTYPE,OPTIONS'
run_check HWP-E01-S02-NETWORK 'ip -brief address'

run_check HWP-C01-S03-GPU-LIST 'nvidia-smi -L'
run_check HWP-C01-S03-GPU-HEALTH 'nvidia-smi'
run_check ERR-T03-B03-S01-PCI-GPU "lspci | grep -i nvidia; nvidia-smi -L"
run_check ERR-T03-B04-S01-ECC 'nvidia-smi -q -d ECC'
run_check ERR-T03-B04-S01-REMAP "nvidia-smi -q | grep -iE 'Xid|Remapped|Pending'"
run_check ERR-T04-B02-S03-TOPOLOGY 'nvidia-smi topo -m'

run_check DAY1-E01-B01-S02-ACTIVE 'systemctl is-active vastai.service vast_metrics.service docker nvidia-persistenced.service'
run_check DAY1-E01-B01-S02-STATUS 'systemctl --no-pager --full status vastai.service vast_metrics.service docker nvidia-persistenced.service'
run_check DIA-E02-B01-S01-VAST-JOURNAL 'sudo -n journalctl -u vastai.service -n 80 --no-pager'
run_check DIA-E02-B01-S01-METRICS-JOURNAL 'sudo -n journalctl -u vast_metrics.service -n 80 --no-pager'
run_check DIA-E02-B01-S01-KAALIA 'sudo -n tail -n 100 /var/lib/vastai_kaalia/kaalia.log'
run_check DIA-E02-B01-S01-PORT-RANGE 'sudo -n cat /var/lib/vastai_kaalia/host_port_range'

run_check ERR-T02-B02-S01-DOCKER-TYPE 'type docker; docker --version'
run_check ERR-T02-B02-S01-DOCKER-RUNTIME-HELP 'docker create --help | grep -- --runtime'
run_check ERR-T02-B02-S01-DOCKER-RUNTIMES "sudo -n docker info | grep -i runtime"
run_check ERR-T02-B03-S01-DOCKER-ACTIVE 'systemctl is-active docker'
run_check ERR-T02-B03-S01-DOCKER-JOURNAL 'sudo -n journalctl -u docker -n 100 --no-pager'
run_check ERR-T02-B03-S01-DOCKER-PS 'sudo -n docker ps'
run_check DIA-E02-B02-S01-DOCKER-CAPACITY 'df -h /var/lib/docker'
run_check DIA-E02-B02-S01-DOCKER-USAGE 'sudo -n docker system df'

run_check DIA-E03-B01-S02-CURRENT-BOOT "sudo -n journalctl -k -b --no-pager | grep -Ei 'AER|PCIe Bus Error|pcieport|NVRM|Xid|fallen|GPU has fallen'"
run_check DIA-E03-B01-S02-PREVIOUS-BOOT "sudo -n journalctl -k -b -1 --no-pager | grep -Ei 'AER|PCIe Bus Error|pcieport|NVRM|Xid|fallen|GPU has fallen'"
run_check DIA-E03-B01-S02-DMESG "sudo -n dmesg -T | grep -Ei 'AER|PCIe Bus Error|pcieport|NVRM|Xid|fallen|GPU has fallen'"
run_check DIA-E03-B01-S02-LOGFILES "sudo -n grep -Ei 'AER|PCIe Bus Error|pcieport|NVRM|Xid' /var/log/syslog /var/log/syslog.1 /var/log/kern.log /var/log/kern.log.1 2>/dev/null"
run_check DIA-E03-B01-S02-COMPRESSED "sudo -n zgrep -Ei 'AER|PCIe Bus Error|pcieport|NVRM|Xid' /var/log/syslog.*.gz /var/log/kern.log.*.gz 2>/dev/null"
run_check ERR-T03-B04-S01-XID "sudo -n journalctl -k -b --no-pager | grep -i xid"

run_check ERR-T04-B02-S03-FABRIC-STATUS 'systemctl --no-pager --full status nvidia-fabricmanager'
run_check ERR-T04-B02-S03-FABRIC-JOURNAL 'journalctl -u nvidia-fabricmanager --since "-24h" --no-pager'
run_check ERR-T04-B02-S03-FABRIC-STATE "nvidia-smi -q | grep -i -A 2 Fabric"

printf 'attempt_finished_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
