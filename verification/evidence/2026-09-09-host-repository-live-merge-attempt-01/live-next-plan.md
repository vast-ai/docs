# SSH/Jupyter and self-test: next bounded checks, not completed

The proposed budget is awaiting a new user decision. No Host/API credentials,
SSH session, rental or self-test was used by this repository-only attempt.

## First: the SSH/Jupyter client workflow

Proposed limit: one GPU, one create attempt, twenty minutes, USD5 estimated all-in.
Use only the user's currently idle, owner-confirmed machine150296; do not assume
the previous public listing is still idle, unchanged or affordable. Fresh reads
must establish the distinct Host/client account roles, offer ID, GPU quantity,
full current pricing, adequate funds and absence of other workloads. An earlier
successful rental is neither a reservation nor renewed authorization.

Before create: select a Jupyter-enabled image by immutable digest, retain its
source/provenance, bind a unique label, and arm an independent owner-scoped
deadline/cleanup observer. No operation on unrelated contracts is permitted.
Retain actual public SSH endpoint/command and command output; actual Jupyter
page/kernel result; source/runner/image identities; start/end timestamps;
destruction response and independent absence readback. Record whether the
client is genuinely outside the Host LAN; a VPN or public-IP hairpin alone is
not independent external-network evidence.

First24Hours / Test Like A Client, COR-01-MCL-323c8fb8180f5f62-REPLACEMENT:
run the exact documented client offer query with the concrete machine ID and
retain the parsed result. This can address offer visibility, not future ranking.
MCL-da591d84b7d08317 also contains a conditional SSH/Jupyter troubleshooting
clause. A successful connection and cleanup alone do not validate that whole
compound statement or all failure diagnoses. Do not deliberately break a
customer Host to obtain that branch; retain a suitable source/owner analysis or
an independently authorized disposable reproduction instead.

## Second: self-test, separately

Proposed limit: one attempt, thirty minutes, USD15 estimated all-in, one run at
a time and only an independently confirmed idle target. Pin the selected offer
and resulting GPU count before create. No provider-side hard spending cap is
claimed; monitored limits, early stop and cleanup are required.

The docs' checked CLI is ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd at
`/private/tmp/host-vv-cli-ecf32ef`. Its packaged command dispatches through
vastai.cli.main and modular commands/machines.py. Do not confuse this with
root vast.py or the different current checkout18c4f2c. The pinned modular CLI
supports --support-bundle-dir and --test-image; it launches direct SSH without
Jupyter. A source check therefore does not prove either command execution or
Jupyter access. Select a verified compatible immutable image index/platform
digest deliberately; historical image tags or earlier paid runs are not fresh
provenance for this target.

How to Self-Test / Run The Test, MCL-eeaf6da83da9eca7 (lines84–87): retain the
actual CLI invocation with a restricted output directory, progress and diagnostic
result, exit code, a sanitized bundle inventory/content check, and independent
instance cleanup. Keep source-only signature proof distinct from this runtime
lane. A run that fails in initialization must not be called a diagnostic PASS.

No reboot, listing-price change, unrelated renter access, Host reconfiguration,
candidate publication or CLI release change is authorized by this plan. Further
TCP/UDP listener or external-observer work needs its own exact authorization and
cleanup scope. macOS/Linux/Windows coverage must name what actually ran; a
single-platform result is not cross-platform validation.

## Then: PR185 integration

PR185 currently requires review and is a draft. Its old green checks cover the
remote starting revision, not the dirty local package. Before push/merge, review
an explicit publication manifest (never git add all), scan selected files for
restricted material, commit only the approved scope, rerun required CI at that
commit and obtain required human review. Retained149 missing-citation FAILs and
other unvalidated claims need an explicit source-owner resolution or scoped
human risk decision; tests do not constitute acceptance. Do not bypass branch
protection or invent approval.
