# Host docs review traceability

Snapshot: 2026-07-13

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

- `npm run test-review-context` covers page-scoped Jira context and verifies that
  the overlay exists only on the port 4000 review proxy.
- `verify-self-test-reference` passes on PR #185 and guards source/docs drift.
- Vast CLI PRs #407, #408, #409, and #410 are merged.
- Self-Test PRs #2, #3, and #4 are merged.
