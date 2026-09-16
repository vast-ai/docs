# HIST-04 source inspection 02 — updater and self-test helper

## Scope, provenance, and method

This follow-up reconciles the public installer’s opaque helper call from `source-inspection-01` with the two exact publicly downloadable scripts it names. On 2026-09-08, the updater and self-test helper were fetched as data only into the non-publishable `.orchestra/h100x4-install-history/source-inspection-02-restricted/` directory (directory mode `0700`, files mode `0600`). They were not made executable or executed. No Host/API/SSH action, credential use, installation, listing, self-test, workload, or reboot occurred.

| Artifact | SHA-256 | Static identification |
|---|---|---|
| `update_scripts.sh` | `8b7f973b2f4b62d293c3078ce0d2c108c6e1556149877680ca7c723183c61714` | UTF-8 Bash script |
| `start_self_test.sh` | `b44cfb52802f0fe44535cba8b6d78365a6672418e89574c87d34f05aa197151f` | ASCII Bash script |

The public updater has a direct source link to the helper: `update_scripts.sh:17-19` downloads a named script, and `:27-35` includes `fetch_update start_self_test.sh`. This ties the two downloaded artifacts together at retrieval time, but does not establish that either is the version a future host would download or run.

The helper runs `/var/lib/vastai_kaalia/vast`, whose source/binary identity is not supplied by either downloaded script. A local source-only crosswalk at `vast-ai/vast-cli@18c4f2ccd6da587d5352f8741c71805a9a18e1ae` labels `-g` as per-GPU $/hour, `-s` as $/GB/month, `-b` as per-GPU minimum bid $/hour, and `-e` as offer expiry (`vast.py:8150-8172`). That crosswalk is not provenance for the helper’s on-host executable and therefore does not upgrade its flag semantics to a deployed guarantee.

## Exact retained excerpts

### Installer argument surface and helper launch (artifact SHA-256 `6b00488c…ac6c`)

```python
# public-install:1397-1411
parser.add_argument("--reset-machine", action="store_true", help="Reset machine id")
parser.add_argument("--no-daemon", action="store_true", help="don't run vast.ai daemon installer, just set up necessary environment")
parser.add_argument("--no-docker", action="store_true", help="assume docker is configured in exactly the way needed by vast.ai already")
parser.add_argument("--no-libvirt", action="store_true", help="assume libvirt is configured in exactly the way needed by vast.ai already")
parser.add_argument("--storage-size", default=None, type=float, help="set size of loopback file in GiB for loopback case (not preferred)")
parser.add_argument("--update-server", default=None)
parser.add_argument("--vast-server", default=None)
parser.add_argument("--package", default=None, help="path to local daemon package tar.gz, skips S3 download")
parser.add_argument("-l", "--logfile", default="vast_host_install.log")
parser.add_argument("-d", "--dev", nargs="?", default=None, const=True)
parser.add_argument("-v", "--verbose", action="count", default=0)
parser.add_argument('--amd', action='store_true', help='install for AMD GPUs.')
parser.add_argument('--raidgpt', action='store_true', help='edit udev rules to enable support for gpt-partitioned RAID (e.g., /dev/md#) drives.')
parser.add_argument('--interactive', action='store_true', help='Interactive machine installation setup. Recommended for new hosts.', default=False)
parser.add_argument("--ports", help="Define open port range for this machine.", nargs="+")

# public-install:1963-1967
_gpu_count = get_gpu_count() or 1
_gpu_pph = str(max(1, int(96 // _gpu_count)))
process_open(["sudo","/var/lib/vastai_kaalia/start_self_test.sh", str(machine_id), _gpu_pph, "1", "0", server_url, machine_api_key, args.api_key], preexec_fn=os.setpgrp)
```

No parser control for on-demand GPU price, minimum bid, storage price, exact end date, or self-test suppression appears in this complete argument section. For an observed four-GPU count, the code expression yields `24`; source-inspection alone does not establish that the on-host `-g` consumer has the local-reference units or that this price is acceptable.

The first `--no-daemon` block is narrow; it ends after the updater setup call, before driver and other install phases:

```python
# public-install:1658-1665
if not args.no_daemon:
    with green():
        log("=> Update Vast.ai daemon", level=0)
    process_check_call(["su", DAEMON_USER, "-c", 'VAST_DEBUG={} bash update_launcher.sh setup'.format(str(args.verbose))])

with green():
    log('=> Checking for installed nvidia driver', level=2)
```

The later `if not args.no_daemon` at `1777-1926` separately gates Docker testing and daemon start. Neither block governs the earlier identify registration (`public-install:1586-1607`) or the post-install helper invocation (`1943-1969`).

### Public updater fetch link (artifact SHA-256 `8b7f973b…1714`)

```bash
# update_scripts.sh:17-19, 27-35
fetch_update () {
    wget https://s3.amazonaws.com/public.vast.ai/kaalia/scripts/$1 -O $DIR/$1.tmp && chmod +x $DIR/$1.tmp && mv -f $DIR/$1.tmp $DIR/$1;
}
fetch_update send_mach_info.py
...
fetch_update start_self_test.sh
fetch_update update_launcher.sh
```

### Public helper listing behavior (artifact SHA-256 `b44cfb52…151f`)

```bash
# start_self_test.sh:25-45
echo "Checking if machine $MACHINE_ID is already listed..."
if python3 /var/lib/vastai_kaalia/vast show machine $MACHINE_ID --raw --url $SERVER_URL --api-key $SESSION_API_KEY 2>&1 | grep -q '"listed": true'; then
  echo "Machine $MACHINE_ID is already listed. Exiting early."
  exit 0
fi

echo "Machine is not listed. Proceeding with self-test..."
current_time=$(date +%s)
three_hours_from_now=$((current_time + 10800))

echo "Listing machine with parameters (GPU_PPH=$GPU_PPH, min_count=$MIN_COUNT, reserved_discount=$RESERVED_DISCOUNT)..."
python3 /var/lib/vastai_kaalia/vast list machine $MACHINE_ID -g $GPU_PPH -m $MIN_COUNT -r $RESERVED_DISCOUNT -e $three_hours_from_now --url $SERVER_URL --api-key $SESSION_API_KEY 2>&1
...
python3 /var/lib/vastai_kaalia/vast self-test machine $MACHINE_ID --ignore-requirements --url $SERVER_URL --api-key $SESSION_API_KEY 2>&1

# start_self_test.sh:61-62
echo "Unlisting machine..."
python3 /var/lib/vastai_kaalia/vast unlist machine $MACHINE_ID --url $SERVER_URL --api-key $SESSION_API_KEY 2>&1
```

## Findings and standardized disposition

| Item | Status | Static observation and boundary |
|---|---|---|
| Public-updater helper retrieval | PASS | The exact public updater fetches `start_self_test.sh` by name (`17-19`, `27-35`). This is a source-retrieval observation only. |
| Unlisted-machine helper flow | PASS | The helper computes `now + 10,800` seconds and invokes `vast list machine` before `vast self-test`, then attempts `unlist` afterward (`33-45`, `61-62`). This reconciles the prior automatic-listing assertion: it is an automatic **temporary** listing path when the helper reaches that branch. No runtime outcome is claimed. |
| Existing-listed branch | UNVALIDATED | If `show machine --raw` contains `"listed": true`, the helper exits early (`25-31`). It does not establish safe ownership, correct price/expiry, a successful self-test, or an authorization to rely on an existing listing. The public installer’s existing local key/machine-ID handling likewise is not a safe substitute for fresh target identity and lifecycle authorization. |
| Exact requested initial-publication values | BLOCKED | The helper supplies only `-g`, `-m`, `-r`, and its computed `-e`; it supplies neither `-b` nor `-s`. The installer/TUI expose no requested value controls. The on-host CLI identity and full flag semantics are also unproven. Therefore source evidence cannot authorize or demonstrate the requested on-demand, minimum-bid, storage-price, or exact-end-date publication. |
| Install/list/self-test action | BLOCKED | The automatic helper listing branch uses generated values and a relative three-hour end time, while the requested safety constraints require exact bounded publication controls. No safe command sequence, fresh target state, downstream executable provenance, or authorized runtime observation is retained. No action was attempted. |
| No-reboot condition | UNVALIDATED | The public installer contains a conditional driver-install path that prints a reboot warning (`public-install:1667-1682`) and invokes an external NVIDIA installer (`1686-1736`). No direct `reboot` command was found in the inspected installer. Its default condition sets `args.no_driver` when `--install-nvdriver` is absent (`1482-1483`), and the local TUI command omits that flag, but no source-to-future-artifact/provenance or host-state evidence proves every downstream reboot-causing branch is impossible. The no-reboot guarantee remains unresolved. |

The helper has no shell `trap` around its final unlist. Thus the static source shows an unlist attempt only after the self-test command returns; it does not prove cleanup after interruption, crash, or a failed downstream process. That limitation reinforces the BLOCKED action disposition.

## Decision boundary

This is source-inspection evidence, not authority to execute or depend on the helper. The prior `source-inspection-01` `FAIL-CLOSED` wording is a safety decision, not a V&V status. For this result, the standardized action disposition is `BLOCKED`; only the explicitly scoped static observations are `PASS`, and unresolved provenance/lifecycle facts are `UNVALIDATED`.
