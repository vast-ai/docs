# Host docs review traceability

Jira status snapshot: 2026-07-13 (not re-verified by this repository review)

Retained 40-page repository V&V reconciliation: 2026-09-03

Current upstream integration: 2026-09-07 (44 primary Host pages; freshness and
new-page review coverage are separate from the retained 40-page proof).

Review PR: [vast-ai/docs#185](https://github.com/vast-ai/docs/pull/185)

Jira epics: [CON-1187](https://vastai.atlassian.net/browse/CON-1187) and [CON-1509](https://vastai.atlassian.net/browse/CON-1509)

## Purpose

This review-only audit maps the Host documentation in PR #185 to the 16 child
tickets assigned to Hannes. It distinguishes work that is implemented from
facts, policy decisions, and sign-offs that still need an owner.

This document does not reproduce internal support source material, customer
data, credentials, or machine-local research paths. It records only the
traceability needed to review the PR.

## Ticket matrix

| Jira | Current state | Evidence in or linked from PR #185 | Review verdict |
|---|---|---|---|
| [CON-1584](https://vastai.atlassian.net/browse/CON-1584) | BLOCKED | Host Account Security and Host CLI/API/SDK orientation, with links to canonical account and developer docs | Partial: Teams ownership, setup-key wording, screenshot/redaction, and review-stack decisions remain |
| [CON-1581](https://vastai.atlassian.net/browse/CON-1581) | BLOCKED | `/host/host-teams` covers context, ownership, roles, keys, CLI use, earnings, payouts, and recovery | Partial: migration semantics, the `undefined` install failure, registration permissions, and `billing_read` behavior need engineering answers |
| [CON-1531](https://vastai.atlassian.net/browse/CON-1531) | BLOCKED | `/host/machine-errors` provides a broad lookup, impact, remediation, and public/admin distinctions | Partial: catalog completeness, field/UI mapping, clearing/TTL rules, and public-error policy need backend answers |
| [CON-1518](https://vastai.atlassian.net/browse/CON-1518) | TO REVIEW | Lifecycle IA, overview split, persona chips, installer assets, and persona consistency check | Substantially documented; IA/persona and stakeholder sign-off remain |
| [CON-1517](https://vastai.atlassian.net/browse/CON-1517) | TO REVIEW | Source review and a human-reviewed answer pass were completed; PR commit `0cb28ff` distributes the answers across 33 canonical Host pages | Implemented in PR #185; shared product confirmations remain under their topic-specific tickets |
| [CON-1515](https://vastai.atlassian.net/browse/CON-1515) | TO REVIEW | Generated `/host/self-test-reference`, source-derived thresholds, runtime stages, image matrix, stable codes, bundle guidance, generator, and CI workflow | Implemented in PR #185; authoritative verification queue/wait-time wording still needs confirmation |
| [CON-1256](https://vastai.atlassian.net/browse/CON-1256) | TO REVIEW | Pricing, earnings, market metrics, optimization, payment, datacenter, tax, and persona guidance | Partial: Solutions Engineering/business review and content ownership remain |
| [CON-1077](https://vastai.atlassian.net/browse/CON-1077) | TO REVIEW | `/host/headless-install` provides an SSH-only setup path from first login through listing and Self-Test | Implemented in docs; reviewer sign-off remains |
| [CON-1583](https://vastai.atlassian.net/browse/CON-1583) | TO REVIEW | [self-test#3](https://github.com/vast-ai/self-test/pull/3) is merged; the generated reference documents the approximately 2 TB high-VRAM cap and B300 behavior | Implemented in runtime and PR #185; reviewer sign-off remains |
| [CON-1519](https://vastai.atlassian.net/browse/CON-1519) | TO REVIEW | [vast-cli#410](https://github.com/vast-ai/vast-cli/pull/410) is merged; Host Diagnostics and the generated reference document automatic bundles, `dump-logs`, redaction, caps, and opt-in host-local artifacts | Command and docs are implemented; operations ownership and safe transfer/retention policy remain |
| [CON-1514](https://vastai.atlassian.net/browse/CON-1514) | TO REVIEW | [vast-cli#409](https://github.com/vast-ai/vast-cli/pull/409) is merged; docs cover common causes, port requirements, TCP/UDP guidance, and offline/unlisted/rented possibilities | Partial: exact failed-port/protocol evidence and authoritative offline-vs-hidden state require backend/API support |
| [CON-1513](https://vastai.atlassian.net/browse/CON-1513) | TO REVIEW | Generator plus scheduled, PR, manual, and optional dispatch drift checks; the PR check passes against both source repositories | Implemented and active in PR #185 |
| [CON-1512](https://vastai.atlassian.net/browse/CON-1512) | QA Passed | [vast-cli#407](https://github.com/vast-ai/vast-cli/pull/407) is merged; docs warn that `--ignore-requirements` does not qualify a machine for verification | Implemented |
| [CON-1510](https://vastai.atlassian.net/browse/CON-1510) | TESTING | [vast-cli#408](https://github.com/vast-ai/vast-cli/pull/408) and [self-test#2](https://github.com/vast-ai/self-test/pull/2) are merged; the generated page exposes actual/required values, purpose, remediation, stable codes, and source metadata | Implemented in runtime and PR #185; Jira testing/sign-off remains |
| [CON-1502](https://vastai.atlassian.net/browse/CON-1502) | QA Passed | [self-test#4](https://github.com/vast-ai/self-test/pull/4) is merged; the generated reference exposes the validated image/platform matrix | Implemented |
| [CON-1419](https://vastai.atlassian.net/browse/CON-1419) | TO REVIEW | [vast-cli#408](https://github.com/vast-ai/vast-cli/pull/408) selects CUDA 11.8 for pre-Volta and caps Volta at CUDA 12.8; the generated page documents the rules | Implemented in runtime and PR #185; reviewer sign-off remains |

## Implemented review corrections

- PR #185 contains the generated Self-Test reference and its source generator;
  docs PR [#145](https://github.com/vast-ai/docs/pull/145) is superseded and is
  being closed rather than treated as an integration dependency.
- The `verify-self-test-reference` check passes against Vast CLI and the private
  Self-Test source repository.
- The review panel links each page to its relevant epics, tickets, named owner
  questions, and remaining blocker count.
- The Self-Test page now has one remaining product-fact gate: authoritative
  verification queue and wait-time wording. Generated thresholds, failure
  codes, dispatch checking, B300 guidance, and older-GPU selection are present.
- Host Diagnostics documents the merged `vastai dump-logs` workflow. Remaining
  questions concern operations ownership, artifact policy, and evidence that
  only backend or host-side systems can provide.

## CON-1519: what exists and what the meeting must decide

### Implemented mechanics

- A failed `vastai self-test machine <machine_id>` creates a redacted diagnostic
  archive automatically unless support bundles are explicitly disabled.
- `vastai dump-logs <machine_id>` creates one on demand. The caller can provide
  an instance ID for API-visible instance logs and can choose the output
  directory.
- The archive is created on the machine where the CLI runs. The default
  directory is `/tmp`; nothing uploads it to Vast, Jira, or object storage.
- The archive is named `vast_selftest_<machine>_<UTC timestamp>.tar.gz` and is
  written with `0600` permissions.
- Every archive records a manifest and collection errors. Self-Test output,
  structured result data, and API-visible instance status/container/daemon
  evidence are included when available.
- Non-JSON text/log artifacts are tail-bounded; collection commands have a
  timeout; sensitive key names and explicit secrets are redacted. The user is
  told to review the archive before sharing it.
- Host-local Kaalia, Docker, kernel, NVIDIA, network, and mount evidence is
  opt-in with `--include-local-host-artifacts` and is useful only when the CLI
  is running on the actual host. A laptop cannot collect the host's local OS
  state remotely.

### Ownership decisions still required

| Decision | Question to answer in the meeting | Proposed starting point, not yet approved |
|---|---|---|
| Intake | Where should a host send a reviewed archive? | A restricted support-ticket attachment or approved private upload, never a public Jira/Slack channel |
| Accountable owner | Who owns the bundle after it is received? | Support Operations owns intake and case tracking |
| First triage | Who confirms scope, redaction, completeness, and failure category? | Support L1 uses a checklist and routes by evidence type |
| Diagnosis | Who diagnoses CLI, backend/daemon, and host-local failures? | CLI maintainers own schema/collection bugs; Backend/Daemon owns API/instance evidence; Host Engineering/SRE owns host-local runtime evidence |
| Retention and access | How long is the archive kept, who can access it, and who deletes it? | Security/Support Operations must approve a retention period and least-privilege access group |
| Escalation | What evidence and response are required when L1 cannot resolve it? | A routing matrix with named queues and a feedback path for new error codes/remediation |

The implementation cannot settle this RACI by itself. To close CON-1519
operationally, the meeting should name one accountable intake owner, approve a
transfer location and retention/access policy, and name the first diagnostic
owner for each evidence class.

## Remaining decisions by review area

- **Host Teams / account setup:** migration and earnings behavior, installation
  key semantics, registration permissions, and billing-role behavior.
- **Machine errors / network:** complete public catalog, UI fields, clearing
  behavior, exact failed-port/protocol evidence, and offline-versus-hidden state.
- **Self-Test:** verification queue and wait-time wording; CON-1519 operations
  ownership and safe artifact policy.
- **Business pages:** Solutions Engineering/business review and named content
  owner.
- **Review mechanics:** approve lifecycle IA/persona treatment and the remaining
  product assets, then choose the merge/review sequence for PR #185.

## Validation evidence

### Review wording directly on the page (2026-09-05)

The local review panel now opens with **Wording & proof**. Select a section,
read the customer-visible statement, and use **Show on page** to highlight
its exact wording. Opening a section URL selects that section's statements;
**All sections** shows the full page inventory. The review IDs and complete
evidence history remain under **Audit details** and **Technical V&V details
and history**.

For example, `MCL-f9f3ebb712a5588d` is the opening statement on Verification
Stages: “Verification is automated. There is no manual review step for
ordinary host verification.” It belongs to **Page introduction**, not to
Verification Requirements. Its **Needs evidence** label means the existing
`UNVALIDATED` status: the Self-Test and Verification source owner still needs
to supply the canonical implementation supporting that statement.

Cards distinguish proof from links in the wording and review tracking records.
Source definitions for commands are labeled as syntax support; command test
results keep their separate status. A successful highlight proves only that
the reviewer can locate the wording. Ambiguous, missing, and masked passages
show an explicit fallback instead of choosing a passage silently. Combined
passages now highlight each bound excerpt, as verified in the follow-up below. Customer
pages served without the local review proxy are unchanged.

The correction, observed failures, retests, and limits are retained in the
[reader presentation attempt](https://github.com/vast-ai/docs/blob/7d42a0d439f91e4dc2877104db807ec6fb975ce4/verification/evidence/2026-09-05-host-reviewer-reading-attempt-01/result.md).

### All Host pages: readable wording and proof (2026-09-05 follow-up)

The same view covers all **40 primary Host pages**, including Volume Offers and
the generated Self-Test Reference. The **18 CLI and 15 SDK wrappers** instead
show a readable link to the central reference, with the explicit limitation
that a reference check is not command-execution proof.

Cards quote the bound page passages, separately label a summarized assertion,
and link every declared section. Multi-section filters, multi-passage highlights,
literal shell pipelines, repeated source occurrences, and rendered prose
typography are covered. Audit IDs and historical records remain collapsed.

The final browser sweep accounted for all **1,687 statements**: **1,680 located**
and **7 explicitly masked section fallbacks**. All section filters and review
section links passed; all existing claim statuses were preserved. The 33 support
routes and 33 review-context regression tests passed. These are interface results,
not new validation of the Host claims or commands. The runner rejects stale
servers using the source identity returned by the running process.

The panel also exposes inherited issues rather than hiding them: `VOL-C35`'s
binding covers Related Pages but omits Command Map; two unbackticked Self-Test
options render with typographic dashes. Those canonical documentation/binding
repairs remain maintainer follow-ups. Masked passages are not presented as exact
quotations. Source-span navigation may omit table scaffolding; it is not proof
of a whole claim's scope or rendered CLI-token correctness.

[All-page results, original failures, corrections, retests, screenshots and limits](https://github.com/vast-ai/docs/blob/7d42a0d439f91e4dc2877104db807ec6fb975ce4/verification/evidence/2026-09-05-host-reviewer-all-pages-attempt-01/result.md)
are retained separately from the earlier single-page attempt. Neither the
runtime/operator nor Product/Finance/Legal/source-owner workstream is completed
by this presentation change; no human acceptance is recorded.

### How command proof is presented

#### Upstream integration freshness (2026-09-07)

PR #153's head is already an ancestor of PR #185; it is not a separate merge
dependency. The number **153 citation failures** elsewhere in this report is
a count of findings, not a pull-request reference.

The upstream integration adds Machine Metrics, Machine Offline, Upgrade the
Kernel, and Disable SSH Password Login to the Host lifecycle navigation. It
also changes existing source text and central references. The September 5
evidence applies to its exact tested commit, `7d42a0d`, not automatically to
these additions or changes. A changed page is **STALE** until its wording,
source bindings, procedures, and proof are re-reviewed; a new page is
**UNVALIDATED** until inventoried and checked. Neither label implies a confirmed
external blocker. Old failures and runtime/owner limitations remain visible as
history and must not be promoted by the merge.

The integration plan, initial failures, corrections, and retests are retained
in `verification/evidence/2026-09-07-host-main-integration-attempt-01/result.md`.
The current static inventory covers 44 primary pages and 33 support routes.
Reviewer source coverage is 36 unchanged primary pages, four changed pages,
four new pages, and six changed support routes. "Unchanged" preserves the
previous bounded status; it does not mean PASS. Renewing the changed/new
claim and procedure contracts remains repository work, not an external blocker.

#### Retained command evidence

The review panel now keeps two evidence lanes separate for every exact command:

- **Source/signature support** links to the immutable Vast CLI handler and to
  the repository-local argparse check. This proves only that the documented
  executable, command signature, and options exist in the pinned source. It
  does not prove execution.
- **Runtime behavior** links to the retained command attempt, identifies its
  proof role and limitations, and states the concrete next action when the
  result is incomplete.

Status-reconciliation records are shown as accounting only, not as command
proof. Every retained-evidence link carries its exact page, heading, target or
command, current status, proof role, and limitations into the evidence view.

Current examples reviewers can use:

| Page and command | Source/signature | Runtime result | Meaning |
|---|---|---|---|
| [How to Self-Test — Before You Run It](/host/how-to-self-test#before-you-run-it) — `vastai set api-key <API_KEY>` | PASS at pinned [`set__api_key` source](https://github.com/vast-ai/vast-cli/blob/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd/vastai/cli/commands/auth.py#L199-L204) | FAIL — [retained isolated result](https://github.com/vast-ai/docs/pull/185/files#diff-4f5c08df9a17c2408167b8eeb03e88105ebed7f9651672660450a59648f95d27) | The synthetic value was written, but the file was mode `0644`; this is not proof of real Host authentication. |
| [How to Self-Test — Run The Test](/host/how-to-self-test#run-the-test) — `vastai self-test machine <machine_id>` | PASS at pinned [`self_test__machine` source](https://github.com/vast-ai/vast-cli/blob/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd/vastai/cli/commands/machines.py#L699-L717) | UNVALIDATED — no direct retained runtime result | The command exists; successful rental, workload, result, and cleanup behavior are not proved. |
| [How to Self-Test — Run The Test](/host/how-to-self-test#run-the-test) — `--support-bundle-dir /path/to/output` variant | PASS at pinned [`self_test__machine` source](https://github.com/vast-ai/vast-cli/blob/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd/vastai/cli/commands/machines.py#L699-L717) | BLOCKED/PARTIAL — [retained attempt](https://github.com/vast-ai/docs/pull/185/files#diff-c886a1940ad73cc0cd932cc4661dee8a9d76e7748a9b6f15ba33f2e7292680e9) | The exact form reached offer selection and produced early-failure bundle evidence, but permission failed before instance creation. |
| [VMs — Check VM Status](/host/vms#check-vm-status) — `enable_vms.py check` | No immutable helper-source binding | PASS — [retained representative read-only result](https://github.com/vast-ai/docs/pull/185/files#diff-1e34fca669c5308f4e7359fe41ed5ca31fd991ae69f661083bd60a4a36bad660) | The exact query returned `off`; broader status interpretation and state-transition claims remain separate. |
| [VMs — Disable VM Support](/host/vms#disable-vm-support) — `enable_vms.py off` | UNVALIDATED | UNVALIDATED — prior run was [disqualified as non-representative](https://github.com/vast-ai/docs/pull/185/files#diff-47c65eaaa665010583ea2af9497f03fdb46a7d0cd487c47085ba9ac5a59e47d9) | A suitable idle VM-capable Host, mutation authorization, before/after observation, cleanup, and canonical helper source are still needed. |

The generated [Host CLI registry check](./HOST-DOCS-CLI-COMMAND-CHECK.md)
links every recognized Host Docs CLI occurrence to its pinned canonical handler
and explicitly records that no API command was executed.

The initial correction remains in
[reviewer attempt 01](https://github.com/vast-ai/docs/pull/185/files#diff-0d7ac13642ddf099b2df6fecf9c4944347be90bbde1f1b05a0f1ddab3ad11b31).
The complete post-change failure, correction, retest, and limitation chain is
retained separately in
[reviewer attempt 02](https://github.com/vast-ai/docs/pull/185/files#diff-f2f0f374040d89b371ff06383a605611cf433c0486baf421692bbafe5b2629e8).
The final repository-local package and its exact artifact identities are in
[PR-ready packaging attempt 01](https://github.com/vast-ai/docs/pull/185/files#diff-bd9dfc2ac184fc347b116686588390a790a86868cd89511469cf1e4589ad87a3).

- `npm run test-review-context` covers page-scoped Jira context and verifies that
  the overlay exists only on the port 4000 review proxy.
- `verify-self-test-reference` passes on PR #185 and guards source/docs drift.
- Vast CLI PRs #407, #408, #409, and #410 are merged.
- Self-Test PRs #2, #3, and #4 are merged.
