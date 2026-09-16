# Real account and hardware evidence for the overlay demonstration

Read-only trace against signed `bb8f85b6bdbf5c4c083f1baa0bed536e77a396b7`, model SHA-256 `4df6d2589f3370ed7799f7007f1b08202239e5829cb8f9ecfeaa34c12d2da104`. No new hardware, account, API or browser operations. The [JSON](/Users/hanneszietsman/VastAi/research/host-docs-meeting-20260914/presentation-overlay-20260915/runtime-account-evidence.json) pins every cited artifact and the full current claims.

**Useful story:** We matched documentation to real Host and Client accounts, actual command output, and a real GPU rental. Each observation is linked to the precise statement it supports; the overlay exposes the original failures and the limits alongside the result.

| Show in port4000 | Current passage(s) | What actually happened |
|---|---|---|
| [First24Hours — Test Like a Client](http://127.0.0.1:4000/host/first-24-hours#test-like-a-client) | `MCL-7d10fc61bf9a884b`, `MCL-92edb99129fc96c9`; Monitor `MCL-fabfbad844e625b4` | September9: distinct authenticated Host/client accounts; listing accepted/read back; client rented one H100; CUDA computation returned1240.0; instance destroyed and independently absent. These three remain current PASS. |
| [Not In Search — Comparing your ranking](http://127.0.0.1:4000/host/not-in-search#comparing-your-ranking) | `MCL-c36fc6f15087d072` | September14: exact `vastai search offers 'gpu_name=RTX_4090 cpu_ram>257 cpu_ram<258'` ran on macOS/Python3.12.12 against existing Client account; exit0, empty stderr, eight RTX4090 rows. |
| [Notifications — Where to Find Notification Settings](http://127.0.0.1:4000/host/notifications#where-to-find-notification-settings) | `CUR-c8657007c73f9603` | September15: real signed-in owner-team, joined-manager-team and individual contexts were inspected. Corrected `/account/` to `/settings/`, the exact section name to **Notification and Webhook Settings**, and scoped availability to account context. No settings saved. |

## H100 chain: concrete evidence to open

The four-H100 host was machine150296; the bounded client run used offer50363390, instance50364501 and **one NVIDIA H100 PCIe**. Image pinned to `pytorch/pytorch@sha256:11691e035a3651d25a87116b4f6adc113a27a29d8f5a6a583f8569e0ee5ff897`.

1. [Distinct account authentication](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/fresh-account-identity-01.json), September9 08:53:06UTC: both200; only identity hashes retained.
2. [Listing readback](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-readback-verification-01.json), 08:38:00UTC: all11 expected settings matched. Earlier `$1/GB` and `$0.10/GB` attempts were rejected; the explicitly approved `$0.01/GB` retry succeeded. Do not infer a general price bound from this.
3. [Create request](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/rental-create-request-01.json), 08:53:08UTC: direct `PUT /asks/50363390/`; [independent running-contract read](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/instance-read-03.json).
4. [GPU result](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/gpu-result-01.json), 08:53:37UTC: CUDA available, exactly oneGPU, unique nonce, sum of squares1240.0.
5. [Cleanup](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/cleanup-main.json): `DELETE` acknowledged; owned GET and independent owned-instance list establish absence by08:53:44UTC. [Watchdog](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rental-run-03/watchdog-finished.json) exited without duplicate deletion.

This was **direct API execution**, with request source pinned to CLI revision`18c4f2ccd6da587d5352f8741c71805a9a18e1ae`. Do not label it as execution of the adjacent CLI/Jupyter command. It proves a tiny GPU calculation and this lifecycle, not full self-test, stress/performance/stability, stock installation, SSH/Jupyter or settled billing. The old result's partial cleanup passage has since received a separate scoped source/runtime adjudication; current `MCL-da591d84b7d08317` is PASS, not the old result's UNVALIDATED status.

## Separate real CLI proof

[Runtime capture](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-14-host-unvalidated-evidence-attempt-02/offer-search-current.json) and [output review](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-14-host-unvalidated-evidence-attempt-02/offer-search-current-review.json) bind the exact current fence to CLI revision`1c6f8b61d3929a7ae423f89a3a0a53e4e9be02bc`, imported module hashes and Python3.12.12, September14 20:31:27–31UTC. This was the actual canonical CLI entrypoint, not merely an equivalent request. The first parser did not recognize ANSI column groups; reviewing the same output established eight indexed rows without another run. Printed RAM258.0 is rounded display, not proof that strict RAM filtering failed. No rental/mutation occurred in this search.

## Sanitized real console proof

[Current observation JSON](/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914/verification/evidence/2026-09-15-host-continuation-88-attempt-01/d-console/observations.json) records September15 12:58–13:09UTC production-console navigation. Machine cards/list/expanded fields and listing controls were observed in a joined Host team with manager role; Members/owner options and Escalation Contact in an owner team; notifications in individual-account context. The names/IDs of people and teams are deliberately excluded. Build ID was not exposed. No invitation, contact save, listing update, ownership change or notification save/delivery test took place.

Open `/observations/notifications/text` for the cleanest actual-UI correction. `/observations/escalation/text` shows why wording now avoids pretending that all team contexts expose the same controls. Role and team changed together, so this is not a universal role-permission test.

The optional [Market Metrics](http://127.0.0.1:4000/host/market-metrics) example has three distinct forms of evidence: September8 real Host-key CLI commands, three successful API GETs with claim IDs`CUR-a5b27de02fca3c9a`, `CUR-6c8062ab1c766957`, `CUR-2de1188bec6c9f72`, and September15 current Host-team Market UI observations. The JSON maps exact artifacts. These were not a synchronized data-equality test and do not prove market accuracy/freshness.

## What can be shown safely

Use **sanitized current observation JSON in the overlay**, not the raw September15 screenshots/DOM: the latter are local-only and contain account, machine and earnings information.

I visually inspected three existing images. `host-console-host-navigation.webp` is already tightly cropped with no personal identity, machineID, email, key or balance, though it retains an instance-count badge. `console-notifications-settings.png` is a cropped historical settings panel with no personal identity, but shows account/billing/instance preferences and does not show the Host group. Neither has a recorded original capture date/account/build. **`host-listing-pricing-controls.webp` is not redacted: machineID145020 remains visible.** The prior nine-image mask map was only a specification; no completed redacted replacement was identified in this bounded trace. Do not describe those originals as approved redacted captures.

The contextual work belongs to **CON1187 Host Docs++**, with the listing/runtime package explicitly tied to **CON1518** and the original account/screenshot requirement tied to **CON1584**. Root's [ticket map](/Users/hanneszietsman/VastAi/research/host-docs-meeting-20260914/presentation-overlay-20260915/ticket-demo-map.json) supplies exact Jira sources. Its historical counts/statuses are not current model totals or new acceptance.

## Confirmed existing overlay evidence URLs

[Open the actual GPU result in the overlay](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-09-h100x4-listing-rental-attempt-02%2Frental-run-03%2Fgpu-result-01.json&page=%2Fhost%2Ffirst-24-hours&claim=MCL-e6fb82f7e167fdc8) — local readback **200 HTML**. This belongs to **MCL-e6fb82f7e167fdc8**, First24Hours line55, “Use a separate client account or the CLI to rent a small test instance on your own machine.” The existing current claim points directly to the retained `cuda_available: true`, one H100 and `sum_squares: 1240.0` result. This is the best workload-output screen for the demonstration.

[Open that rental's cleanup record](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-09-h100x4-listing-rental-attempt-02%2Frental-run-03%2Fcleanup-main.json) — local readback **200 text/plain** through the existing unscoped, hash-guarded artifact route. It shows instance50364501 deletion and both absence checks. It is historical artifact access, not a new claim binding. The current cleanup claim's later evidence refers to a different instance50386523; do not conflate them.

The follow-up performed only these two local reviewer GETs. All local Markdown links were corrected and checked for existence. No external API, Host or account operation occurred.
