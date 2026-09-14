# Payout and invoice guidance: selected corrections completed locally

CON-1518 / PR185 · 14 September 2026 · macOS local source and reviewer checks.

Four missing-citation findings are corrected. Two repeated timing descriptions
are updated and source-bound too. **26 corrections remain** elsewhere; the
separate pending reviews and external prerequisites are not completed.

## What changed

| Exact Payment passage | Current supported description | Prior → current |
| --- | --- | --- |
| Payout Schedule, line53 · MCL-e2b956d14494e470 | Published invoice threshold: at least $20 USD | FAIL → scoped PASS |
| Payout Schedule, line54 · MCL-df7b287adb0df683 | Published weekly Friday schedule; no unsupported noon-Pacific time | FAIL → scoped PASS |
| Payout Schedule, line58 · MCL-5936430d1b2d8de9 | Published rollover below $20 until the threshold is reached | FAIL → scoped PASS |
| Why are invoices not generating?, line106 · MCL-bbd64c772e9b4693 | Published valid-connected-method and at-least-$20 prerequisites | FAIL → scoped PASS |
| Payout Schedule, line55 · MCL-3d796f5ae7f2020e | Qualified first-payout estimate, separately cited Agreement clock | UNVALIDATED → scoped PASS |
| When will I get paid?, line84 · MCL-3afd93ae0b6cf8a4 | Same qualified estimate and separate contractual clock | UNVALIDATED → scoped PASS |

Each current finding says **Published guidance checked**. The scope is what Vast
publishes—not invoice generation, backend scheduling, account enforcement,
payment processing, final settlement or a guaranteed deadline. No Finance or
Legal approval is invented. The two timing cards retain separate source controls
for the guidance and Agreement; neither source is used to prove the other clock.

The [public capture](published-invoice-guidance-01.json) was retrieved from
https://docs.vast.ai/host/payment at 2026-09-14T15:34:50.914Z. SHA-256:
`9e4a9ff965510e9c08f6c45c929ab5a180d882e7dfe6c14bd65b7b30cef5814c`.
Its edit link points to this docs repository. It supports an attributed account
of the published guidance, **not independent product corroboration**. The prior
Agreement capture remains bound for its weekly billing/14-day clause only.
See the [source decision and exact section pointers](source-review.md).

## Checks and retained retests

- [93 Python tests](integrated-python-02.json) and [68 JavaScript tests](integrated-js-02.json) pass, including frozen-history, source-hash, exact-transition and reviewer tests.
- [All 38 Payment passage locators](rendered-payment-01/summary.json) pass; no fallback or missing passage.
- [Six current source mappings](context-03.json) pass on localhost4000, including the separate Agreement basis on both timing cards.
- [Six-card localhost and offline checks](after-03.json) pass for exact passages and source dialogs. Offline checks observed no remote resource requests.
- [Visible-control retest](root-visible-check-02.json) passes on the root offline timing card: browser clicks open/close its disclosure and open both distinct source dialogs. DOM scrolling only positions the controls; it does not activate them. This is separate from the broader programmatic DOM checks.
- [Queue classification retest](queue-02.json) confirms all 11 supported payout findings leave “Needs triage.” The four recognized classifications change presentation only; unknown future types still require triage.
- [Integrity audit](final-audit-01.json) confirms exactly six complete claim changes, 2,007 unchanged claims and 3,822 unchanged prior evidence files. HEAD and index are unchanged; only Payment lines53,54,55,58,84,106 changed. Final export/integrity readbacks are retained separately in this attempt.

Initial failures remain distinct: [before](before-01.json), [Python fixture failure](integrated-python-01.json), [JavaScript fixture failures](integrated-js-01.json), [raw-filename test mismatch](after-01.json), [queue defect](queue-01.json) and [URL-fragment test mismatch](root-visible-check-01.json). Their corrected retests are linked above. The original test scripts and preliminary result are retained. A worker-only browser review initially overstated programmatic activation; its correction is preserved in the extra worker archive. Root's separate visible-click result is the applicable check.

## Current handoff

**319 PASS / 26 FAIL / 23 BLOCKED / 87 NOT_APPLICABLE / 1,558 UNVALIDATED**
across 2,013 passages on 44 Host pages. The 18 CLI and 15 SDK references remain
support layers, not additional Host workflows.

The work queue has 10 documentation checks, 532 source checks, 1,016 technical
checks, 23 unavailable prerequisites, 26 corrections, 0 unclassified items and
406 completed/not-applicable records. These are passage counts, not independent
product facts or an acceptance score.

Next: [four tax-information/Vast-services corrections](../../host-corrections-walkthrough.md#4-tax-information-and-vasts-tax-services--4-entries).
Use existing official sources first. Resolve only the exact supported wording;
ask an owner only about remaining gaps or ambiguity.

The [runtime/operator register](../../current-runtime-operator-blockers.md) and
[source/owner register](../../current-source-owner-blockers.md) remain open and
separate. This attempt performs no Host/API, account, payment, rental, reboot,
push, merge, publication or human acceptance. It does not claim all safe Host
Docs work is exhausted. Tests here cover local macOS, not Linux/Windows runtime.

Task-created worker changes, repaired fixtures and worker evidence were archived
and hash-verified before removing only that disposable checkout; the main tree
was preserved. See [archive verification](worker-archive-check-01.json) and
[supplemental archive verification](worker-extra-archive-check-01.json).

The [AST-only graph update](graph-update-01.json) completed with 13,129 nodes,
16,672 edges and 1,074 communities. This is code navigation, not claim evidence
or semantic document validation. It reports 2,571 zero-node files and omits the
HTML graph visualization because the graph exceeds the size limit.

Final handoff readback: the first check incorrectly requested this new result
through the legacy evidence endpoint, which correctly returned 404 for an
unregistered reference. It was not a link exposed by the current claim cards.
The corrected check uses the actual current-review context API for localhost
and the embedded result control for the offline HTML. Both exact claim-source
controls were already tested above. See final-handoff-01.json and its corrected
final-handoff-02.json; export readback is final-export-check-02.json.
