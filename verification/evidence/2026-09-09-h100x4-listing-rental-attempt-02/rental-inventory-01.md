# Frozen representative client rental — before creation

Selected client offer50363390, machine150296, one H100, on-demand. Client and
Host identities are independently distinct. Quote:4.0092592592592595/hour with
10GB requested storage; bandwidth0.013333333333333334/GB each direction.
This is the client quote, not the host's3/GPU-hour price. Named client credential
metadata was found at Crypto Labs Vast.ai Client API Key / cryptolabs-client.
No credential value is in this record.

Source: vast-ai/vast-cli revision18c4f2ccd6da587d5352f8741c71805a9a18e1ae,
vast.py L2340(get_runtype), L2464(create), L3093(destroy), L3637(logs),
L4328(search), L6474(account), and current sibling API instance functions.
These are source contracts, not claims of exact CLI-command execution.

| Item | Exact page/heading and claim | Observation / result required |
| --- | --- | --- |
| RENT-01 | /host/first-24-hours / Monitor / MCL-fabfbad844e625b4 — Machine visibility and active offers | Approved final listing readback plus independent client offer search matching machine150296 and one active rentable offer. Snapshot only. |
| RENT-02 | /host/first-24-hours / Test Like A Client / MCL-7d10fc61bf9a884b — Create a test instance from one available offer | Pinned offer/request, success/new_contract, independent owned-instance read matching new id, machine150296, oneGPU, unique attempt label. |
| RENT-03 | Same page/heading / MCL-92edb99129fc96c9 — Instance appears in client account | Independent post-create client owner-scoped instance GET matching exact contract, machine/GPU/label; not just create response. |
| RENT-04 | Representative bounded workload; not a broad stability claim | Args-mode python3 in pinned cached PyTorch image; one CUDA GPU, H100 name, deterministic sum of squares0..15 equals1240, unique nonce in retained own-container logs. No SSH or network reachability proof inferred. |
| RENT-05 | /host/first-24-hours / Test Like A Client / MCL-da591d84b7d08317 — Destroy test instance when done | Exact ownership guard before DELETE, successful acknowledgement, independent owned-list/instance absence or destroyed terminal. No other id may be deleted. |

All runtime-only claims retain exact model/source wording and spans in the prior
claim-impact inventory until a new formal adjudication passes. Running a test
does not silently grant source-owner or commercial/legal authority.

## Cost and cleanup controls

The API has no total-spend or TTL field. The USD5 ceiling is an operational
budget using current quoted prices, bounded work and account-credit monitoring,
not a platform-enforced guarantee. Twenty-minute quoted compute/storage is
about1.34, leaving a conservative transfer/cleanup reserve. Expected execution
is shorter: at most180seconds startup wait and a tiny computation; independent
cleanup watchdog acts at ten minutes from request start, before the20minute
outer ceiling. Cleanup begins earlier on failure, unknown identity, credit
drop above3 or failed account reads. Delayed/account-wide billing limits will
be reported; no exact attribution or hard billing cap will be fabricated.

Pinned image:
pytorch/pytorch@sha256:11691e035a3651d25a87116b4f6adc113a27a29d8f5a6a583f8569e0ee5ff897.
No package/data download, SSH setup, stress, benchmark or bulk traffic requested.
Cache observation is not a server-enforced no-pull promise. Runtime command and
body are frozen in the collector and retained before the create request.

Use one unique attempt label, record existing ids privately, never blindly retry
create. An ambiguous create is reconciled only by a new owned id with the unique
previously absent label and exact machine/GPU. Main and watchdog cleanup both
require exact ownership; preserve failed invocation, response and retest history.
