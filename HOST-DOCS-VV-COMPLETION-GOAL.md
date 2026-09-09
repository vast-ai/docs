# GOAL: Complete Host Docs procedure V&V and expose an independently reviewable result

> **Current-state correction (2026-09-03):** This file preserves the original
> completion prompt as planning history. The current repository-local projection
> is 128 PASS, 95 BLOCKED, 749 UNVALIDATED, 5 FAIL, and 27 N/A across 1,004
> targets. At command level it is 84 PASS, 7 BLOCKED, 60 UNVALIDATED, 1 FAIL,
> and 27 N/A, with semantic counts of 12 score-1, 119 score-2, 21 score-3, and 27
> approved N/A.
> Applicable command PASS coverage is 84 of 152 (55.3%); 68 of 152 (44.7%)
> remains non-passing. The primary scope is 40 Host pages (39 authored and one
> generated); 33 CLI/SDK routes are central-reference support wrappers rather
> than Host workflows. The broad source inventory covers 73 routable files, 501
> unique targets, 565 occurrences, and 193 commands.
>
> The repository-local structure is complete for traceability review. This does
> not establish semantic acceptance, complete either external workstream, or
> record human approval.
>
> The historical "paid Self-Test" model below is superseded. Official Host
> self-test runs on the Host's own hardware and requires a securely supplied
> Host-owner credential with `machine_read`, a protected workload window, a
> positive runtime limit, and cleanup authority, but no paid-test budget. Paid
> renter testing is separate. Further Host execution is paused because
> transient workload activity made the environment uncontrolled.

## Operating mode

Use the installed `$vv-evidence` skill in `PLAN_AND_EXECUTE` mode.

- Repository: `/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk`
- Review target: `vast-ai/docs` PR #185
- Jira: `CON-1518`
- Local reviewer: `http://127.0.0.1:4000/host/hosting-overview`
- Current planning revision: `14d9af2`; confirm the exact revision and Host-page hashes
  again before execution.

The objective is to finish the existing page/procedure V&V package, not to design a new
testing framework. Continue safe independent work when one execution class is blocked.

## Current baseline to reconcile

The existing inventory contains:

- 39 primary Host pages;
- 97 logical test sets;
- 203 branches;
- 468 ordered or conditional steps;
- 165 command carriers across 43 command-bearing test sets;
- 54 test sets with no command carrier, requiring inspection, browser/manual checks, or
  authoritative-source review instead of shell execution.

Existing evidence contains 37 retained observations. At current carrier level there are
15 behavior `PASS`, 16 `BLOCKED`, 3 `UNVALIDATED`, 1 `NOT_APPLICABLE`, 53 with CLI
signature evidence only, and 77 with no signature or behavior evidence. Thirty-two
carriers are scored: twelve score 3 and twenty score 2.

All 97 test sets and all 203 branches currently display `UNVALIDATED` because the frozen
inventory status has not been reconciled with the later observations. No set, branch, or
step has an attempt link. This is both a status-projection gap and a real coverage gap.
Do not bulk-promote parent statuses from command counts.

## Canonical working artifacts

Reuse and minimally extend the existing package:

- `verification/host-docs-test-sets.json` — page/procedure/branch/step inventory;
- `verification/host-docs-test-results.json` — attempts and observations;
- `verification/host-docs-command-scores.json` — contextual scores;
- `verification/evidence/<attempt-id>/` — append-only evidence;
- `verification/HOST-DOCS-COMMAND-COVERAGE.md` and `HOST-DOCS-QA-SUMMARY.md` — generated
  or reconciled reviewer summaries;
- `review-server.mjs` — the existing port-4000 reviewer.

Do not introduce another workflow, production harness, command runner, runbook system,
identity framework, or parallel evidence ledger. Small read-only utilities are allowed
only when they directly reconcile or validate these existing artifacts.

## Work plan

### Phase 1 — Reconcile the baseline and existing evidence

1. Pin the current docs revision, Host-page hashes, test-set snapshot, and material CLI,
   Self-Test, dependency, and environment identities. If a source changed, record the
   change and mark affected evidence `STALE` until reviewed or retested.
2. Keep the existing 97 logical test sets. Change grouping only when the source proves a
   real sequence, branch, or ownership error; record the reason rather than regenerating
   the inventory from scratch.
3. Map every retained observation to the exact applicable command, step, branch, and test
   set. Add explicit attempt/evidence links and a current/supersedes relationship where
   more than one observation exists.
4. Reclassify the 31 currently blocked steps. A corrected documentation defect must link
   to its correction and retest; an authorization, environment, or safety blocker must use
   that real blocker class instead of `SOURCE_DEFECT_BLOCKED`.
5. Classify every branch as an ordered required phase, applicable alternative, optional
   modifier, failure-only path, or not applicable to the tested target.
6. Validate non-command steps through the method appropriate to their claim: rendered
   journey, UI/manual observation, source inspection, generated-source comparison,
   authoritative owner confirmation, or explicit blocker.
7. Derive current command, step, branch, and test-set statuses from linked evidence. Show
   partial coverage numerically while retaining the correct V&V status.
8. Produce a reconciliation checkpoint showing status counts, evidence coverage, scoring
   coverage, unresolved blockers, stale evidence, and the next executable queue.

### Phase 2 — Execute the remaining representative checks

Run procedures in documented order, with prerequisites, checkpoints, expected final
observable, and cleanup. Do not execute carriers independently merely to increase counts.

#### A. Safe local, browser, and read-only account/API work

- Replay repository-native static, rendered, link, persona, OpenAPI, CLI-signature, and
  review-context checks against the pinned final source.
- Complete applicable read-only REST/CLI and browser journeys using the correct Host or
  client role.
- Treat catalogs, option fragments, examples, and generated references as static/source
  validation where that is the page's actual claim; do not manufacture runtime tests.

#### B. Read-only and privileged-read Host work

- Reuse current GPU, service, PCIe, ECC, storage, mount, and CLI evidence only when its
  target and surrounding page claim match.
- Complete the narrow bounded privileged-read queue, including the applicable exact
  `journalctl`/`dmesg`/Host-log forms, `sudo docker ps`, and
  `sudo docker system df`.
- Bound follow/watch commands interactively; never leave `tail -f` or `journalctl -f`
  unattended.

#### C. Paid client procedure

Run at most one paid attempt at a time. A single carefully mapped attempt may support the
paid Self-Test, first-client rental, diagnostic-bundle, result, and cleanup claims where
the exact applicability is recorded.

Before launch require a fresh client-role credential through secure non-chat injection,
an approved machine/offer, numeric spend and runtime caps, exact CLI/Self-Test/image
identities, stop conditions, and a tested cleanup/escalation path. Retain actual cost,
instance state, result, deletion, and post-cleanup confirmation.

#### D. WAN and Docker GPU procedures

- Test TCP and UDP separately from a genuinely external client using one approved unused
  forwarded port, a temporary listener or bounded capture, and verified cleanup.
- Run Docker GPU injection or bounded GPU load only with explicit idle/load authorization
  and capture the expected GPU result and end state.

#### E. VM procedure

The earlier VM observations remain `UNVALIDATED` because the target's IOMMU setup was not
representative. Retest only after BIOS/kernel IOMMU repair and reboot, rental prevention,
an idle Host check, and operation-specific approval. Execute:

```text
check -> off -> check -> on -f -> check
```

Retain output and exit state at every step. Accept only exact `off` after disablement and
exact `on` after enablement, together with expected GPU visibility, active Host/Docker
services, no abort/error output, and a confirmed safe final state.

#### F. Destructive or production-changing procedures

Installer, package, reboot, storage format/mount, daemon-range mutation, listing,
repricing, maintenance, default-job, defrag, cleanup, decommission, team deletion, and
similar operations run only on a disposable/rebuildable target or for a genuine approved
operational need with before/after and rollback evidence. Otherwise record `BLOCKED` with
the exact claim impact and continue other work.

## Phase 3 — Functional and semantic assessment

Audit each user-facing command, error string, factual threshold, and external-behavior
claim in the page and procedure context where it appears.

Keep execution status and semantic score separate:

- `1` — the command failed, the result was irrelevant, or the wording is wrong, unsafe,
  obsolete, misleading, or materially unsupported;
- `2` — the command or evidence is relevant but only partially supports the wording,
  depends on an unstated condition, or does not address the full documented claim;
- `3` — current representative evidence shows that the command works and directly,
  strongly supports the exact wording, prerequisites, sequence, outcome, exceptions, and
  cleanup.

Do not assign a score merely from command help when the page claims runtime behavior. Do
not infer execution `PASS` from score 3, or score 3 from execution `PASS`. An item not yet
assessed remains unscored; by final reconciliation every in-scope occurrence must have a
1–3 assessment or an approved `NOT_APPLICABLE` rationale.

For score-1 or material score-2 findings, preserve the original observation, classify the
cause, correct only authorized Host Docs wording, and create a linked retest/rescore. A
source-owner gap remains visible even if the observed behavior otherwise scores well.

## Phase 4 — Status rules and roll-up

Use only `UNVALIDATED`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`, and `STALE`.

- A command or non-command claim passes only with current claim-suitable evidence.
- A step passes only when its prerequisites/dependencies, every required action or claim,
  expected observable, checkpoint, and cleanup are satisfied.
- An applicable branch passes only when every required step passes in order and its final
  observable and cleanup pass.
- A test set passes only when its branch policy is explicit, every applicable required
  branch passes, alternatives are correctly scoped, and no required child remains
  `FAIL`, `BLOCKED`, `UNVALIDATED`, or `STALE`.
- A non-applicable branch is `NOT_APPLICABLE` with rationale, never `PASS`.
- Preserve partial coverage as counts such as `4/6 steps evidenced`; partial coverage is
  not a seventh V&V status.

Apply the deterministic precedence appropriate to the required children: material
`FAIL`, then `STALE`, then `BLOCKED`, then `UNVALIDATED`; use `PASS` only when every
required applicable child passes and every excluded child has a justified disposition.

## Phase 5 — Reviewer interface, final QA, and handoff

1. Update the existing port-4000 reviewer to consume the reconciled current outcome.
2. For every Host page show procedure status, step coverage, observations, 1–3 scores,
   blockers, limitations, corrections, and retests without exposing restricted details.
3. Keep raw machine, account, offer, instance, network, credential, and unrestricted log
   details outside Git. Publish only target aliases, opaque evidence IDs, hashes, and
   sanitized observations.
4. Test normal, missing, malformed, stale, redaction, traversal/XSS, feedback
   compatibility, and narrow-sidebar rendering behavior. Missing or mismatched evidence
   must fail closed, never appear as `PASS`.
5. Resolve the Host accessibility failure or retain an explicit documentation-owner risk
   decision. Replay all final repository checks and inspect the complete diff for secrets
   and unrelated files.
6. Produce one concise reviewer entry point and ready-to-post PR #185 / Jira CON-1518
   update with exact review commands, coverage, failures, blockers, fixes/retests, tested
   environments, residual risks, and credential-rotation reminder.
7. Commit only focused repository changes. Push and post remote updates only when the
   user has explicitly authorized that final publication step.

## Required gates and user inputs

Request only the gate needed by the next blocked execution class. Continue everything
else.

- Confirmation that VM/IOMMU repair and reboot are complete before VM retest.
- Numeric paid `MAX_SPEND_USD` and `MAX_RUNTIME_MINUTES`, stop/cleanup authority, and a
  fresh client-role key supplied through secure non-chat injection.
- An approved unused forwarded port and external-client boundary for TCP/UDP testing.
- Explicit idle/load authorization for Docker GPU-container execution.
- A disposable/rebuildable Host or a decision to leave destructive install/storage/
  lifecycle procedures blocked.
- Named source owners for machine-error behavior, network semantics, verification timing,
  Host Teams roles/billing, and pricing/business claims.
- An independent human acceptance owner.

Chat-pasted API keys are not valid execution inputs. They must be rotated and replaced
through an approved secure mechanism.

## Completion outcomes

Report two outcomes separately:

### `EVIDENCE_PACKAGE_COMPLETE`

Every one of the 39 pages, 97 test sets, 203 branches, 468 steps, 165 command carriers,
and all in-scope errors, thresholds, and behavior claims has a traceable current
disposition, method, evidence or exact blocker, semantic assessment, limitation, and
applicable correction/retest. Counts reconcile and the reviewer exposes the sanitized
result. This outcome may truthfully contain non-passing items.

### `TARGET_ACCEPTANCE_CANDIDATE`

Every safe, available, and authorized procedure has current representative evidence; no
material `FAIL`, `UNVALIDATED`, `STALE`, unresolved authority gap, or unapproved residual
risk remains. Any remaining `BLOCKED` item has an explicit authorized risk/scope decision.
Human acceptance is still separate and must not be self-recorded.

## Immediate first deliverable

Before running additional live, paid, WAN, mutating, or destructive work, produce the
reconciled current-status checkpoint from existing evidence:

1. exact current source identity;
2. current command/step/branch/test-set status counts;
3. attempt/evidence linkage coverage;
4. semantic-score coverage and distribution;
5. corrected blocker classifications;
6. procedures that can already pass, procedures needing safe checks, and procedures that
   must remain blocked;
7. the next smallest safe execution batch.

Then proceed through the phases without pausing unrelated work.
