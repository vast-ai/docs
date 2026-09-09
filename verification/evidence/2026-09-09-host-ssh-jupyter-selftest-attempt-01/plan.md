# Approved SSH/Jupyter and self-test — attempt 01

Mode: vv-evidence PLAN_AND_EXECUTE. PR185 / CON-1518. Inventory frozen before
live inspection; exact pre-action tree retained at 2026-09-09T12:20:07.700Z in
.orchestra/host-ssh-jupyter-selftest-01/baseline.json (3,106 Git-visible paths,
HEAD bfa926c9421521767fa7411718bd31ea38b38528, original staged diff unchanged).
Earlier attempts are immutable history; this plan records new authority.

User approves **machine 150296 only if idle**, one-GPU SSH/Jupyter up to
20 minutes / USD5 estimated, separate self-test up to 30 minutes / USD15
estimated, automatic cleanup and no reboot. Budgets are not a provider-enforced
cap. Host/customer configuration, listing terms, unrelated instances and other
machines are out of scope. Approval of these tests is not PR acceptance.

## Frozen sequence and evidence inventory

| ID | Claim / purpose and exact target | Method, expected result, retained evidence | Gate and limit |
| --- | --- | --- | --- |
| LIVE-BASE | Current source and working tree | Exact private manifest/index/diffs; retain source and collector hashes. | No baseline evidence is reused as current machine state. |
| LIVE-IDLE | Machine150296 currently owned and idle; operational prerequisite, not a documentation claim | Named Host credential GET of exact owned machine; require four H100, zero running/resident rentals and no occupancy. Then strictly pinned SSH read-only identity, registration, GPU compute-process count, Docker counts, service states and boot hash. Retain selected fields, exact argv, timestamps, exits and limits; no renter content. | Stop if busy, unreadable, wrong identity or unsafe. No create before fresh repeat immediately preceding each paid phase. |
| LIVE-IDENTITY | Two approved account contexts and budget prerequisites | Read only the named Host/client Keychain entries in memory; GET current identities and relevant offers. Retain identity hashes, distinctness and sufficient-credit boolean; credentials never in argv, evidence or terminal output. | Do not use setup tokens from chat, dump Keychain or infer permissions from labels. |
| LIVE-SEARCH | First 24 Hours / Test Like A Client; COR-01-MCL-323c8fb8180f5f62-REPLACEMENT | Execute exact documented query with machine150296 in client context and pinned modular CLI. Retain sanitized input/response and revision. | Visibility only, not future search/rental success. |
| LIVE-SSH-JUPYTER | First 24 Hours / Test Like A Client; exact SSH works, Jupyter opens and connection bullets; MCL-da591d84b7d08317 compound cleanup/troubleshooting occurrence | One uniquely labelled one-GPU rental with inspected image pinned by immutable digest; actual public SSH command plus benign output, Jupyter UI/kernel result, timestamps, quoted price and cleanup/absence. Freeze concrete create/image/cleanup choices in an addendum before create. | 20min/$5 including startup; early-stop reserve and pre-armed independent exact-owner/id/label/machine cleanup. No deliberate host fault; successful connection cannot validate every conditional troubleshooting assertion. |
| LIVE-SELFTEST | How to Self-Test / Run The Test; MCL-eeaf6da83da9eca7 and exact related invocation/result occurrences | After first phase cleanup and fresh idle checks, inspect pinned CLI ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd, compatible immutable image identity and quote. Freeze exact invocation before execution; retain result/progress, failure bundle if produced, CLI/image/platform identity and independent cleanup. | 30min/$15, one attempt, no ignored-requirements fallback without an explicit scope decision. Initialization/cleanup alone is not full diagnostic PASS; self-test is separate from Jupyter. |
| LIVE-CLEANUP | This attempt's resources absent | Narrow cleanup in finally and independent deadline process armed before create; delete only unique new owned exact machine/GPU/label/id match, retain delete response and independent GET/list absence plus unchanged Host boot. | Never delete an unrelated instance or blindly retry an uncertain create. Cleanup persists even if a test fails. |
| REVIEW | Findings readable on port4000 and offline HTML | Bind exact new evidence conservatively; retain earlier failures; source/status consistency, sanitation and browser checks; two separate remaining-work registers. | No full-page/compound PASS transfer, invented authority or claim count laundering. |

PASS requires actual suitable retained execution for the exact claim. Confirmed
incorrect results are FAIL; no evidence is UNVALIDATED. A suitable check unable
to proceed due to busy host, unavailable access, permission, safe route, budget
or environment is BLOCKED with the exact prerequisite and claim impact.

Client origin will be recorded accurately. Local LAN/VPN or public-IP hairpin is
not independent outside-LAN evidence. Only the actual execution platform gets
credit; Linux/macOS/Windows are not assumed equivalent. An external runner,
network-policy change or unsafe workaround requires a separate scope decision.
No authority is invented for the 149 Product/Finance/Legal/citation defects.

Canonical CLI/schema/image sources establish implementation only. Current docs
locate the claim; they are not evidence for themselves. Independent read-only
safety review is advisory; root verifies gates and owns execution/cleanup.
