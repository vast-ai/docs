# Host Docs QA summary

## Current procedure-based V&V status — 2026-09-01

**Evidence package outcome: `EVIDENCE_PACKAGE_COMPLETE`.** Every current Host
target has an ancestry-bound status, retained method/evidence or explicit
blocker, and a sanitized rationale. Every command carrier has either a numeric
semantic assessment or an approved display-only `NOT_APPLICABLE` disposition.

**Acceptance outcome: not yet `TARGET_ACCEPTANCE_CANDIDATE`.** The package is
complete enough to review independently, but it deliberately contains blocked
and unvalidated behavior. Final acceptance belongs to the human reviewer.

### Reconciled scope and current status

| Level | Total | `PASS` | `BLOCKED` | `UNVALIDATED` | `NOT_APPLICABLE` |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pages | 39 | 1 | 30 | 8 | 0 |
| Test sets | 97 | 5 | 68 | 24 | 0 |
| Branches | 203 | 6 | 148 | 49 | 0 |
| Steps | 468 | 20 | 309 | 138 | 1 |
| Command carriers | 165 | 46 | 34 | 58 | 27 |
| **All targets** | **972** | **78** | **589** | **277** | **28** |

No current target is `FAIL`; the initial FAQ route failure and the original
Hardware Prep mount-form failure remain in attempt history and are linked to
their successful correction retests. This is an audit-trail statement, not a
claim that blocked or unvalidated behavior passed.

### Functional status and semantic support remain separate

All 165 command carriers are assessed in page and procedure context:

- 15 score `1`: failed, irrelevant, unsafe, obsolete, or materially unsupported
  for the exact surrounding claim;
- 112 score `2`: useful or relevant, but incomplete, conditional, statically
  supported only, or still missing representative runtime behavior;
- 11 score `3`: current representative evidence strongly supports the exact
  documented command and context;
- 27 approved `NOT_APPLICABLE`: canonical non-executable/display carriers.

The semantic-assessment attempt did not execute 165 commands. Its evidence is
kept separate from the functional projection: command execution status is
derived from retained current evidence and exact blockers, while the 1–3 score
describes how well that evidence supports the page wording.

### Evidence retained in this pass

- 30 attempts, 37 command observations, and 14 procedure evidence records are
  joined to the final test-set snapshot.
- Authorized read-only Host collection covered service state, bounded logs,
  configured port range, Docker daemon/storage, kernel history, PCI/GPU state,
  and ECC state. It did not run a GPU container, GPU load, WAN probe, paid
  rental, VM transition, or Host mutation.
- The invalid multi-target Hardware Prep mount check was preserved as a failed
  attempt, split into observable checks, and retested successfully.
- Three FAQ ownership defects were preserved, corrected, and fully retested.
- Two live-follow instructions now require a bounded window, `Ctrl+C`, and exit
  confirmation. Static retest supports score `2`; runtime remains blocked.
- The third-party GPU-burn manifest and entrypoint were checked statically. The
  mutable tag and unexecuted GPU workload remain explicit limitations.
- The bare `tcpdump` prose token is correctly treated as display-only N/A; its
  owning external TCP/UDP capture procedure remains blocked.

Raw sensitive outputs remain outside Git. Committed evidence contains sanitized
observations, hashes, opaque evidence IDs, and target aliases only.

### Reviewer verification

- Review-context suite: 17/17 passing, including fail-closed malformed, stale,
  incomplete, ancestry, score/status, N/A, withdrawal, and sanitization cases.
- Persona/frontmatter check: 39/39 pages passing.
- Canonical JSON, exact 972-target joins, all 39 current page hashes, JavaScript
  syntax, and Git whitespace checks pass.
- Browser QA confirms current status, evidence, rationales, scores, blockers,
  and retained attempt history on Hosting Overview, Hardware Prep, Common Host
  Questions, Host Diagnostics, and Machine Errors.
- The Pricing Your Listing image loads successfully from
  `/images/host-listing-pricing-controls.webp` with descriptive alt text.

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
open a test set to inspect branches, steps, commands, observations, current
status, limitations, and semantic scores. Use **Comment on selection** or
**Page note** for anything questionable; export with **Save JSON**, Markdown,
or Jira CSV.

### Remaining execution and acceptance gates

- paid Self-Test/rental: fresh client credential through secure non-chat
  injection, numeric spend/runtime caps, and cleanup authority;
- external TCP/UDP: an approved unused forwarded port, external client, bounded
  listener/capture, and verified cleanup;
- Docker GPU injection/load: explicit idle/load authorization and a trusted,
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

Date checked: 2026-08-27
Docs revision: `5088d76b89856185f3ab15a628e4152ff140ab26`
Review target: [vast-ai/docs PR #185](https://github.com/vast-ai/docs/pull/185)

## Outcome

The repeatable audit covers all 72 Host pages plus all 33 imported Host CLI/SDK snippets. It found three concrete publication problems; all three are corrected in this checkout. One low-risk generated-metadata drift and several areas that require named source-owner confirmation remain.

No paid rental, destructive command, privileged host change, production mutation, or credential-bearing operation was executed.

Fresh evidence now follows the [Oxiom V&V Evidence procedure](./verification/README.md). The current retained result is eight passing local-safe items, one failing accessibility item, and two blocked validation classes. This is strong evidence for the stated local/static claims, not a claim that paid-host runtime or private product behavior is fully validated. See the [current V&V summary](./verification/summary.md) and the preserved [failure/retest ledger](./verification/issues.md).

## Corrections made

| Priority | Problem | Evidence | Resolution |
|---|---|---|---|
| High | The three rendered Self-Test examples used `vast` instead of the supported `vastai` executable. | [`snippets/host/cli/self-test-machine.mdx:49`](./snippets/host/cli/self-test-machine.mdx#L49), lines 49–51 | All three examples now use `vastai self-test machine ...`; the registry verifier passes all 181 occurrences. |
| Medium | Host Notifications linked to an API-reference route Mint could not resolve. | [`host/notifications.mdx:64`](./host/notifications.mdx#L64); clean `mint broken-links` comparison | The Host page now links to the stable Notification Type Keys guide. The clean scan dropped from 100 links in 11 files to 99 links in 10 files, with no Host Docs link failure. |
| Medium | The Host Payouts image had empty alt text. | [`host/payment.mdx:19`](./host/payment.mdx#L19) | Added concise alt text verified against the image; `host/payment.mdx` no longer has a missing-alt finding. |
| Improvement | Host CLI setup did not link directly to the official installer. | [`host/cli-api-sdk.mdx:22`](./host/cli-api-sdk.mdx#L22), [`host/how-to-self-test.mdx:22`](./host/how-to-self-test.mdx#L22) | Added the official [Vast CLI installation page](https://cloud.vast.ai/cli/) while retaining the local authentication and verification guide. |

Repository-level accessibility also fails because the shared `#315FFF` light color has 3.94:1 contrast on the dark background. Mint reports 97 additional Host warnings for empty `<a id="..." />` named anchors; these should be triaged as an anchor/linter pattern rather than bulk-edited blindly.

## Verified results

| Check | Result |
|---|---|
| Rendered scope | 72 Host pages + 33 imported Host snippets |
| Full inventory | 474 unique targets / 529 occurrences: 176 command snippets, 77 error strings/categories, 18 thresholds, 203 behavior-claim candidates |
| Command execution access | All 176 commands reconcile into 5 mutually exclusive groups: 6 paid-only, 52 Host-root, 14 Host-context without root, 104 needing neither, and 0 needing both paid spend and Host root |
| Bash structure | 123/123 fenced Bash snippets parse with `bash -n` after inert placeholder substitution; nothing executed |
| CLI registry | 179 occurrences pass against clean current `vast-cli master@ecf32efa...`; 2 are command-family references; 0 actionable defects |
| Local Host images/routes/fences | No missing local images, missing `/host` routes, empty fences, or unclosed fences |
| Previously missing Pricing image | Present as `/images/host-listing-pricing-controls.webp` with descriptive alt text |
| Self-Test generated reference | Exact match at declared sources `vast-cli@d4316fb...` + `self-test@6f93fc4...` |
| Current Self-Test sources | Current CLI `ecf32efa...` + self-test `6f93fc4...` change only the embedded CLI SHA comment; rendered content is unchanged |
| Persona validation | 39/39 authored pages pass |
| Review-context tests | 9/9 pass |
| Review-server JavaScript syntax | Pass |
| OpenAPI validity/build drift | Valid; rebuild produces the same SHA-256 |
| Clean Mint broken links | 99 repository-wide across 10 files; 0 are in Host Docs |
| Clean Mint accessibility | Fails: 97 Host named-anchor findings plus shared color contrast; the Host Payouts missing-alt finding is fixed |
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

- `vastai self-test machine ...` creates a paid temporary instance. Run only with approved machine/account/budget and record CLI SHA, image digest, machine, instance, cost, and result.
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
