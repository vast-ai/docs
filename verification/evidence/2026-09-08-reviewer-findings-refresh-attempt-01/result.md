# Reviewer panel findings — targeted refresh check

Date: 2026-09-08. PR: vast-ai/docs#185. Jira: CON-1518.

The running localhost:4000 panel already serves the latest V&V data and reviewer code. No restart, code change, claim-status change or new product validation was necessary. This follow-up checks the presentation of existing findings; it does not close those findings.

## Target and retained checks

- [Plan](plan.md) and [dirty working-tree/index baseline](baseline.json). HEAD `bfa926c9421521767fa7411718bd31ea38b38528`; dirty state is part of the target.
- [Server identity](server-identity-01.json): HTTP200, current review available, running source digest matches local `review-server.mjs` (`dfdea55d5a85c9aa3f8a75e954829f4860bcbac509c4e525df03ac62a2b6a472`).
- [Actual browser retest](browser-01/summary.json) and [target hashes/method](browser-01/metadata.json): four pages, 145 statements, all statuses/section filters/passage locators match; zero failures or masking fallbacks. Owned browser sessions were closed; existing user tabs and both local services were left untouched.
- [Eight proof-link GETs](proof-link-retest-01.json): HTTP200 and nonempty artifacts for all eight links rendered in the four selected claim cards. This establishes link accessibility, not sufficiency of the underlying product evidence.
- [Visible VM finding](visible-vm-finding-01.json): exact page heading/text, “Correction needed,” owner, next correction, retained proofs and limitations are present.
- [Independent four-claim projection inspection](independent-projection-check-01.md): all retained fields match the repository model after the documented display projection. This is a retained inspector report, not raw HTTP evidence. PANEL-01 through PANEL-04 are accounted for; the interface checks pass within their stated scope.

| Selected finding | Current panel status | Meaning retained |
|---|---|---|
| `MCL-dfebca7edafe9c59` · VMs / Check VM Status | FAIL | Correct the unconditional `off` meaning; configuration-read failure made the observed `off` inconclusive. |
| `MCL-323c8fb8180f5f62` · First 24 Hours / Test Like A Client | FAIL | Host-owned inventory is not renter offer discovery; page correction remains open. |
| `MCL-96ee15f730e698d8` · Not in Search / Check the machine directly | PASS | Exact retained `show user` invocation support; not a complete workflow or universal runtime claim. |
| `MCL-eeaf6da83da9eca7` · Self-Test / Run The Test | BLOCKED | Present-key availability does not grant workload/create permission, a controlled window or cleanup authority. |

## Freshness, preservation and limitations

`node scripts/export_host_review_html.mjs --check` passed: 2,005 claims, 130 embedded files, unchanged HTML SHA256 `7576bc002524cbb42ac153a707344f00a16ea6c179d6c1511d51cda6e80ffb1b`. `python3 scripts/build_current_host_vv_overlay.py --check` passed: 44 primary pages and 33 support layers. `git diff --check -- REVIEW-TRACEABILITY.md` passed. Final identity comparison at 18:30:52 UTC confirmed reviewer source, current model, HTML and staged diff unchanged.

The initial baseline capture exceeded Node's default subprocess buffer; [original failure and bounded retry](capture-failure-01.md) are retained. It made no index/product changes.

The earlier [unexplained intermittent localhost fetch](../2026-09-08-host-client-unblocking-attempt-01/browser-reconciliation-01.json) remains UNVALIDATED; this selected successful retest is not a blanket stability PASS. The sample is four of 44 pages, not a fresh all-page sweep. No external Host/API request, rental, instance change, secret access, push, merge, post or human acceptance occurred.

## Handoff requirement

After any further evidence/content changes, regenerate and freshness-check the current review model and shareable HTML. Check the running port4000 source identity, restart only the local proxy if its code changed, and retest affected finding cards: exact passage, current result, evidence/limitations, owner and next action. This requirement is recorded in `task_plan.md` and `REVIEW-TRACEABILITY.md`.

Unresolved documentation corrections, runtime/operator prerequisites and Product/Finance/Legal/source-owner work remain open. Displaying a finding does not resolve it.
