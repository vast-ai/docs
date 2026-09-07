# Host Docs QA summary

## Current repository-local V&V status — 2026-09-03

**Repository-local evidence structure: complete for the current scope.** Every
projected Host target has an ancestry-bound status, a structured evidence basis,
and an exact next action. Every command carrier has either a numeric semantic
assessment or an approved display-only `NOT_APPLICABLE` disposition.

This is not semantic acceptance, runtime completion, product/source-owner
confirmation, or human approval. Those external workstreams remain open, and
the documentation is not yet a `TARGET_ACCEPTANCE_CANDIDATE`.

### Reconciled scope and current status

| Level | Total | `PASS` | `FAIL` | `BLOCKED` | `UNVALIDATED` | `NOT_APPLICABLE` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pages | 40 | 1 | 1 | 12 | 26 | 0 |
| Test sets | 101 | 8 | 1 | 16 | 76 | 0 |
| Branches | 207 | 9 | 1 | 27 | 170 | 0 |
| Steps | 477 | 26 | 1 | 35 | 415 | 0 |
| Command carriers | 179 | 84 | 1 | 7 | 60 | 27 |
| **All targets** | **1004** | **128** | **5** | **97** | **747** | **27** |

The separate 1,687-item material-claim register contains 167 PASS, 153 FAIL, 23
BLOCKED, and 1,344 UNVALIDATED dispositions. Its citation states are 153
required-and-absent, 19 required-and-present-but-unverified, and 1,515 not
required. Its page rollup is 3 BLOCKED, 26 FAIL, and 11 UNVALIDATED.
Claim-register counts are not added to the 1,004 hierarchy total, and a
procedure-page status must
not be presented as the page's material-claim disposition.

One command carrier is current `FAIL`: Vast CLI 1.5.6 created the credential
file written by `vastai set api-key` with mode `0644` under normal umask `022`.
Earlier FAQ and Hardware Prep failures remain in attempt history with their
successful correction retests. This is an audit-trail statement, not a claim
that blocked or unvalidated behavior passed.

Excluding the 27 approved display-only carriers, 84 of 152 applicable command
carriers are current PASS (55.3%). The remaining command-validation work is 68
of 152 (44.7%): 7 BLOCKED, 60 UNVALIDATED, and one FAIL. Hierarchy totals must
not be used as a pass rate because the same procedure is represented at
command, step, branch, test-set, and page levels.

### Functional status and semantic support remain separate

All 179 command carriers are assessed in page and procedure context:

- 12 score `1`: failed, irrelevant, unsafe, obsolete, or materially unsupported
  for the exact surrounding claim;
- 119 score `2`: useful or relevant, but incomplete, conditional, statically
  supported only, or still missing representative runtime behavior;
- 21 score `3`: current representative evidence strongly supports the exact
  documented command and context;
- 27 approved `NOT_APPLICABLE`: canonical non-executable/display carriers.

The semantic-assessment attempt did not execute 179 commands. Its evidence is
kept separate from the functional projection: command execution status is
derived from retained current evidence and exact blockers, while the 1–3 score
describes how well that evidence supports the page wording.

The port-4000 reviewer presents a third necessary distinction: canonical
source/signature support and retained runtime behavior are separate lanes. An
immutable handler link proves only the registered form at its pinned revision;
it cannot make the runtime lane pass. Status-reconciliation records are shown
as accounting only, and every evidence link carries its exact page, heading,
target, command, proof role, and limitation.

Every numeric score now has a distinct `direct_evidence_ids` field. It is
explicitly empty when no direct observation is claimed. Every direct link has
a command-specific proof role and must match an evidence-owned proof ceiling,
so a static or partial result cannot be promoted by relabelling the score. All
21 score-3 records link to exact-full or explicitly equivalent-full functional
PASS observations and separately retain current command PASS; 69 score-2
records also expose direct
evidence. Three Market Metrics carriers were downgraded from score 3 to score 2
because only one alternative in each multi-command carrier ran. Contextual,
partial functional, and bounded static evidence cannot satisfy the score-3
direct-proof rule.

### Evidence retained in this pass

- 58 attempts, 50 command observations, and 42 procedure evidence records are
  joined to the final test-set snapshot. All 58 attempt records are hash-bound
  to 57 unique retained artifacts. The three reviewer/packaging records are
  retained history only and do not add status-bearing procedure evidence.
- The direct-proof model contains 38 evidence ceilings and 101
  command-specific bindings.
- Three material-claim result manifests provide 1,687 exact dispositions,
  local-navigation bindings, and exact command-claim bindings. One
  support-layer result binds all 33 CLI/SDK wrapper routes. These are bounded
  structural/source or exact retained-evidence records, not runtime or owner
  acceptance beyond their declared evidence lanes.
- The Phase 24 authorized-Host batch accepted 12 bounded read-only command
  carriers. It retained no parent promotion: 11 records are partial point-in-
  time proof, while the exact VM `check` query is the sole exact-full result.
- A separate Host self-test attempt reached `select_offer` but stopped with
  `api_permission_failed` before the create-instance stage. Its exact
  support-bundle-directory form is retained as partial score-2 evidence for two
  command carriers; neither a runtime result nor a parent procedure passed.
  Billing was not assessed.
- The original GPU-injection form is retained as a Docker exit-125 failure. A
  candidate registered-runtime correction and separate published-form retest
  support three exact command-carrier PASS records; their parent procedures and
  the unrun GPU-burn load command remain non-passing.
- Restricted CLI dump-logs, installer-log, self-test-log-follow, and isolated
  CLI-install results add carrier-level evidence only. The installer raw log is
  restricted; no active self-test, Host authentication, query permissions, or
  parent procedure success is inferred.
- A bounded Host run passed the exact kernel-log follower at command-mechanics
  level. Unrelated transient workload activity then made the environment
  non-controlled, so Host execution was paused. No matching kernel event or
  parent result is claimed.
- The exact Market Metrics REST request returned structured JSON but was
  blocked because the configured client credential lacks machine-read access.
  The curl transport exit of zero is not treated as application success.
- An isolated macOS execution of `vastai set api-key <API_KEY>` with a
  synthetic value completed, but Vast CLI 1.5.6 created the credential file
  with mode `0644` under normal umask `022`. The carrier is current FAIL with
  score 1; no real credential or Host operation was used.
- Host-local bundle setup remains BLOCKED because isolated Python venv support
  is absent. Its two command carriers remain UNVALIDATED because bundle
  execution never started.
- A restricted v1.1 installation record now supplies equivalent-full proof for
  five duplicate `nvidia-smi` GPU-visibility carriers. The source did not
  serialize the nested numeric exit, so no exit code is invented; continuation
  under `set -euo pipefail`, affirmative output, and post-reboot query forms are
  retained with that limitation. No parent step or page was promoted.
- Authorized read-only Host collection covered service state, bounded logs,
  configured port range, Docker daemon/storage, kernel history, PCI/GPU state,
  and ECC state. The separate corrected Docker-runtime retest ran a bounded GPU
  container, but no GPU load, WAN probe, paid rental, VM transition, or Host
  mutation was performed.
- The invalid multi-target Hardware Prep mount check was preserved as a failed
  attempt, split into observable checks, and retested successfully.
- Three FAQ ownership defects were preserved, corrected, and fully retested.
- Two live-follow instructions now require a bounded window, `Ctrl+C`, and exit
  confirmation. Bounded Host runs passed their follow, interruption, and
  cleanup mechanics at score `2`; neither run reproduced the surrounding live
  self-test or kernel-event behavior, so no parent was promoted.
- The third-party GPU-burn manifest and entrypoint were checked statically. The
  mutable tag and unexecuted GPU workload remain explicit limitations.
- The bare `tcpdump` prose token is correctly treated as display-only N/A; its
  owning external TCP/UDP capture procedure remains blocked.

Raw sensitive outputs remain outside Git. Committed evidence contains sanitized
observations, hashes, opaque evidence IDs, and target aliases only.

### Reviewer verification

- Review-context suite: 24/24 pass after the scope and reviewer-contract rebase,
  including 56 malformed-package modes plus the wholly missing package,
  sanitation, exact claim/citation accounting, support layers, and feedback
  import.
- Persona/frontmatter check: the latest check covers all 40 top-level pages.
- Canonical JSON accounts for exactly 1,004 targets and all 40 current page
  hashes. Final JavaScript, review-context, and Git-whitespace replays remain
  part of repository-local closeout.
- The earlier browser pass is retained as history. The final loopback replay
  rendered all 40 primary pages and all 33 CLI/SDK support routes. It confirmed
  exact section/evidence links, the Volume Offers ledger, central-reference
  destinations, and separate procedure/material dispositions; it did not run
  or validate Host product behavior.

### How to review

```bash
gh repo clone vast-ai/docs vast-docs-pr185
cd vast-docs-pr185
gh pr checkout 185
npm ci
```

Start the plain preview in one terminal:

```bash
npm run dev:review
```

Start the review proxy in a second terminal:

```bash
node review-server.mjs --port 4000 --target http://127.0.0.1:3000
```

Then open:

- review interface: `http://127.0.0.1:4000/host/hosting-overview`;
- review dashboard/export: `http://127.0.0.1:4000/__review__/`;
- plain documentation: `http://127.0.0.1:3000/host/hosting-overview`.

On any Host page, click **Review**, expand **V&V evidence for this page**, and
open a test set to inspect branches, steps, command carriers, retained evidence records, current
status, limitations, and semantic scores. Use **Comment on selection** or
**Page note** for anything questionable; export with **Save JSON**, Markdown,
or Jira CSV.

### Remaining execution and acceptance gates

- official Host self-test: the Host's own hardware, a securely injected
  Host-owner credential with `machine_read`, a protected workload window, a
  positive runtime limit, and cleanup authority. It does not require a paid
  test budget; billing was not assessed;
- paid renter testing: a separate client credential through secure non-chat
  injection, numeric spend/runtime caps, and cleanup authority;
- external TCP/UDP: an approved unused forwarded port, external client, bounded
  listener/capture, and verified cleanup;
- remaining Docker GPU load: explicit idle/load authorization and a trusted,
  pinned image;
- VM sequence: repaired BIOS/kernel IOMMU state, reboot, idle/rental prevention,
  and operation-specific approval;
- install, storage, listing, pricing, maintenance, and other mutations: a
  disposable/rebuildable target or explicit operational risk decision;
- product/source-owner confirmation for private behavior and independent human
  acceptance.

Canonical detail is in [command coverage](./verification/HOST-DOCS-COMMAND-COVERAGE.md),
[test sets](./verification/host-docs-test-sets.json),
[results](./verification/host-docs-test-results.json), and
[scores](./verification/host-docs-command-scores.json).

---

## Historical baseline QA outcome

The section below preserves the earlier local/static baseline. Its counts are
historical and do not supersede the current procedure projection above.

Date checked: 2026-09-02
Docs revision: working tree after `3b7e56f0db6588953589e0692e75b7274526d5f9`
Review target: [vast-ai/docs PR #185](https://github.com/vast-ai/docs/pull/185)

## Outcome

The repeatable audit covers all 73 Host pages plus all 33 imported Host CLI/SDK snippets. It found three concrete publication problems; all three are corrected in this checkout. One low-risk generated-metadata drift and several areas that require named source-owner confirmation remain.

No paid rental, destructive command, privileged host change, production
mutation, or real credential was used in this baseline or the later isolated
API-key file-permission check.

Fresh evidence now follows the [Oxiom V&V Evidence procedure](./verification/README.md).
Use the [current V&V summary](./verification/summary.md) for the live counts and
the preserved [failure/retest ledger](./verification/issues.md) for corrections
and open defects. The historical baseline remains evidence for its stated
local/static claims, not a claim that Host runtime or private product behavior
is fully validated.

## Corrections made

| Priority | Problem | Evidence | Resolution |
|---|---|---|---|
| High | The three rendered Self-Test examples used `vast` instead of the supported `vastai` executable. | [`snippets/host/cli/self-test-machine.mdx:49`](./snippets/host/cli/self-test-machine.mdx#L49), lines 49–51 | All three examples now use `vastai self-test machine ...`; the current registry verifier accounts for all 201 occurrences. |
| Medium | Host Notifications linked to an API-reference route Mint could not resolve. | [`host/notifications.mdx:64`](./host/notifications.mdx#L64); clean `mint broken-links` comparison | The Host page now links to the stable Notification Type Keys guide. The clean scan dropped from 100 links in 11 files to 99 links in 10 files, with no Host Docs link failure. |
| Medium | The Host Payouts image had empty alt text. | [`host/payment.mdx:19`](./host/payment.mdx#L19) | Added concise alt text verified against the image; `host/payment.mdx` no longer has a missing-alt finding. |
| Improvement | Host CLI setup did not link directly to the official installer. | [`host/cli-api-sdk.mdx:22`](./host/cli-api-sdk.mdx#L22), [`host/how-to-self-test.mdx:22`](./host/how-to-self-test.mdx#L22) | Added the official [Vast CLI installation page](https://cloud.vast.ai/cli/) while retaining the local authentication and verification guide. |

Repository-level accessibility also fails because the shared `#315FFF` light color has 3.94:1 contrast on the dark background. Mint reports 97 additional Host warnings for empty `<a id="..." />` named anchors; these should be triaged as an anchor/linter pattern rather than bulk-edited blindly.

## Verified results

| Check | Result |
|---|---|
| Rendered scope | 40 primary Host pages + 33 central CLI/SDK support routes; imported Host snippets are included in rendered-source checks |
| Full inventory | 501 unique targets / 565 occurrences: 193 command snippets, 77 error strings/categories, 18 thresholds, 213 behavior-claim candidates |
| Command execution access | All 193 commands reconcile into 5 mutually exclusive groups: 2 paid-only, 54 Host-root, 22 Host-context without root, 115 needing neither, and 0 paid+root. Five commands separately require an external client. |
| Bash structure | 126 unique command targets pass static syntax classification after inert placeholder substitution; nothing executed |
| CLI registry | 199 occurrences pass against clean `vast-cli@ecf32efa...`; 2 are command-family references; 0 actionable defects |
| Local Host images/routes/fences | No missing local images, missing `/host` routes, empty fences, or unclosed fences |
| Previously missing Pricing image | Present as `/images/host-listing-pricing-controls.webp` with descriptive alt text |
| Self-Test generated reference | Exact match at declared sources `vast-cli@d4316fb...` + `self-test@6f93fc4...` |
| Current Self-Test sources | Current CLI `ecf32efa...` + self-test `6f93fc4...` change only the embedded CLI SHA comment; rendered content is unchanged |
| Persona validation | 40/40 top-level Host pages pass |
| Review-context tests | 24/24 pass |
| Review-server JavaScript syntax | Pass |
| OpenAPI validity/build drift | Valid; rebuild produces the same SHA-256 |
| Clean Mint broken links | 99 repository-wide across 10 files; 0 are in Host Docs |
| Clean Mint accessibility | Fails: shared dark-theme color contrast plus 74 image findings in 19 non-Host files; no page-local Host finding |
| Git whitespace | Pass |

## Reproduce the audit

Use Python 3, Bash, and a supported Node runtime. Node 24 was used here; system Node 26 was not used for Mint.

```bash
python3 -B scripts/inventory_host_docs.py
python3 -B scripts/inventory_host_docs.py --check

python3 -B scripts/verify_host_cli_commands.py \
  --vast-cli /path/to/clean/current/vast-cli

npm run check-persona-chips
npm run test-review-context
node --check review-server.mjs

npx mint broken-links
npx mint a11y
npm run check-openapi
git diff --check
```

The CLI verifier exits `0` with the corrected `vastai` examples. The review-context tests bind a temporary localhost port; a restricted sandbox may need local-bind permission.

Installed Mint `4.2.234` does not have a `mint validate` command. Use `broken-links`, `a11y`, and `openapi-check`/`npm run check-openapi` explicitly.

## Commands that must not be treated as routine local tests

Use the generated [command execution access groups](./HOST-DOCS-COMMAND-ACCESS.md) to select an approved environment for every command. The grouped report preserves each stable inventory ID and source line; it is a planning aid, not authorization.

- `vastai self-test machine ...` is a Host-owner workflow that creates a temporary diagnostic contract on the selected Host. Run it only with the Host-owner credential and an approved idle machine; record the CLI SHA, image digest, machine, instance, result, and proof that the contract was removed. The current sources do not establish whether that special contract is billable, so the V&V package does not make a billing claim.
- Listing, unlisting, maintenance, cleanup, defrag, delete, and default-job commands mutate account or machine state. Use a disposable/non-production target and record before/after state.
- Installer, storage, Docker, firewall, kernel, reboot, and GPU commands require a disposable supported host and may need root access.
- API-key and setup-key examples require approved test credentials and log/history redaction.
- GPU, network, Docker, and Windows PowerShell checks require the matching environment; a macOS syntax check cannot prove their runtime behavior.

## Product/source-owner confirmation still required

Passing local tests does not settle these claims:

| Area | Confirmation needed | Tracking |
|---|---|---|
| Machine errors | Complete public catalog, visible fields, impact level, and clearing/TTL behavior | [CON-1531](https://vastai.atlassian.net/browse/CON-1531) |
| Network and ports | Per-GPU vs per-instance semantics, TCP/UDP behavior, release timing, and exact failed-port evidence | [CON-1514](https://vastai.atlassian.net/browse/CON-1514) |
| Verification | Authoritative queue and wait-time behavior | [CON-1515](https://vastai.atlassian.net/browse/CON-1515) |
| Host Teams | Migration, registration permissions, billing role, earnings, and payout ownership | [CON-1581](https://vastai.atlassian.net/browse/CON-1581) |
| Pricing/business | Pricing positioning and ongoing content ownership | [CON-1256](https://vastai.atlassian.net/browse/CON-1256) |

## Detailed artifacts

- [V&V reviewer summary](./verification/summary.md)
- [V&V inventory, raw attempts, and reviewer workflow](./verification/README.md)
- [Full verification inventory](./HOST-DOCS-VERIFICATION.md)
- [Command execution access groups](./HOST-DOCS-COMMAND-ACCESS.md)
- [CLI command registry check](./HOST-DOCS-CLI-COMMAND-CHECK.md)
- [Machine-readable inventory](./host-docs-verification-inventory.json)
- [Machine-readable command access groups](./host-docs-command-access.json)
- [Spreadsheet-friendly inventory](./host-docs-verification-inventory.csv)
- [Machine-readable CLI check](./host-docs-cli-command-check.json)

Reviewer feedback should cite the stable inventory/check ID plus the source line. That makes each correction reproducible and avoids a vague “large docs change was not QA'd” discussion.
