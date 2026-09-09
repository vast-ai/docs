# Host Docs V&V — local independent-review handover

This handover is for a reviewer using the same Mac as the current checkout. It
asks for an independent evidence review, not a rubber-stamp approval and not a
rerun of paid, destructive, mutating, WAN, VM, or GPU-load procedures.

## Copy-paste request to the reviewer

Hi — could you please independently review the Host Docs V&V package on this
Mac? I have tried to make every result traceable and to leave anything that was
not safely demonstrated as blocked or unvalidated. I would especially value you
challenging the score-3 claims, the score-1 findings, and whether the remaining
blockers are clear and appropriately conservative.

You do not need to run commands against a Vast host or spend money. The review
tool shows the documented procedures, retained evidence records, functional status,
semantic score, limitations, and correction/retest history. Please comment on
anything that looks wrong, unclear, unsupported, overstated, or incomplete. The
setup and suggested review order are below.

## Review target

- Existing checkout:
  `/Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk`
- Branch: `CON-1584-host-cli-api-sdk`
- Tracked baseline commit: `3b7e56f0db6588953589e0692e75b7274526d5f9`
- Short baseline commit: `3b7e56f` — `docs(host): refresh V&V inventory provenance`
- Main V&V package commit: `2ea65a0` —
  `docs(host): complete procedure V&V evidence`
- Previous commit/base for this package: `7a8a2c4`
- GitHub review target: `vast-ai/docs` PR #185
- Jira context: CON-1518

Important: the current canonical V&V records and the counts below include later
working-tree updates beyond baseline commit `3b7e56f`. They have not been
pushed. A fresh `gh pr checkout 185` or a detached worktree from `3b7e56f` will
not show the latest package until those updates are committed and pushed. For
the current local review, use the existing checkout.

The existing checkout contains untracked internal planning and orchestration
artifacts. They are not part of the review commit. Use
`git diff 7a8a2c4..3b7e56f` to inspect the complete committed package, or use the
optional clean worktree below.

## What is being claimed

The repository-local evidence structure is complete for independent review of
its traceability and classifications. This is not semantic acceptance or
completion of the external workstreams:

- 40 top-level Host pages: 39 authored plus one generated Self-Test reference;
- 33 CLI/SDK central-reference support wrappers, not separate Host workflows;
- 101 logical test sets;
- 207 branches;
- 477 ordered or conditional steps;
- 179 command carriers;
- 1,004 total projected targets with one current disposition each.

Current functional disposition:

| Level | Total | PASS | FAIL | BLOCKED | UNVALIDATED | N/A |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pages | 40 | 1 | 1 | 12 | 26 | 0 |
| Test sets | 101 | 8 | 1 | 16 | 76 | 0 |
| Branches | 207 | 9 | 1 | 26 | 171 | 0 |
| Steps | 477 | 26 | 1 | 34 | 416 | 0 |
| Commands | 179 | 84 | 1 | 7 | 60 | 27 |
| **All targets** | **1004** | **128** | **5** | **95** | **749** | **27** |

The separate material-claim register contains 1,687 claims: 167 PASS, 153 FAIL,
23 BLOCKED, and 1,344 UNVALIDATED. One hundred fifty-three required citations are
absent, 19 are present but unverified, and 1,515 claims do not require a
citation.

Contextual command assessment:

- 12 commands score 1;
- 119 commands score 2;
- 21 commands score 3;
- 27 display-only carriers are approved N/A.

The package retains 54 attempts hash-bound to 53 unique artifacts, 50
command-result records, and 41 procedure evidence records, with 38 direct-proof
ceilings and 101 direct bindings. It also contains three material-claim result
manifests and one support-layer result with 33 exact bindings. The dashboard shows 95
reviewer-visible retained evidence
records. This includes command evidence plus procedure/history evidence; it is
not a second command-result count.

Current functional completion is 84 of 152 applicable command carriers
(55.3%). The remaining 68 (44.7%) comprise 7 BLOCKED, 60 UNVALIDATED, and one
FAIL; the 27 approved display-only carriers are excluded from this rate.

Host execution is currently paused because transient container and GPU activity
appeared during a bounded read-only check. That check did not create the
workload, but the environment was no longer controlled enough for further Host
V&V.

## What is not being claimed

This is **not** a claim that all Host behavior passed, that all 179 command
carriers were executed, or that the documentation is accepted. Repository-local
traceability is structurally complete; runtime/operator work, Product/Finance/
Legal or source-owner confirmation, and human acceptance remain incomplete.

One command carrier is current FAIL because Vast CLI 1.5.6 created the file
written by `vastai set api-key` with mode `0644` under normal umask `022`.
The retained FAQ and Hardware Prep failures were corrected and successfully
retested; their superseded results remain visible in history. BLOCKED,
UNVALIDATED, and FAIL targets all remain non-passing.

## Start the reviewer from the existing checkout

First verify that the checkout is on the intended commit:

```bash
cd /Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk
git rev-parse --short HEAD
git log -1 --oneline
```

Expected short SHA: `3b7e56f`.

If dependencies are already present, start the plain documentation preview in
terminal 1:

```bash
cd /Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk
npm run dev:review
```

Start the review proxy in terminal 2:

```bash
cd /Users/hanneszietsman/VastAi/CON-1584/docs-pr153-host-cli-api-sdk
node review-server.mjs --port 4000 \
  --target http://127.0.0.1:3000 \
  --dir /private/tmp/host-docs-vv-feedback-3b7e56f
```

The separate `--dir` prevents earlier feedback already present in the working
checkout from influencing the independent reviewer. Use a different empty
directory name if more than one person reviews independently.

If dependencies are missing, run `npm ci` before starting the first terminal.

Do not create a detached review copy from `3b7e56f` yet. That commit predates
the current canonical evidence and would silently omit the latest results. Use
the existing checkout until these working-tree updates are committed. After a
containing commit exists, a detached worktree at that exact revision will be
the preferred way to isolate a review from planning files and prior feedback.

## Use the review interface

Open:

- Review interface: `http://127.0.0.1:4000/host/hosting-overview`
- Combined dashboard/export: `http://127.0.0.1:4000/__review__/`
- Plain documentation without the overlay:
  `http://127.0.0.1:3000/host/hosting-overview`

On a Host page:

1. Click **Review**.
2. Set your reviewer name.
3. Expand **V&V evidence for this page**.
4. Expand a test set, then inspect its branches, steps, command carriers,
   retained evidence records, current status, limitations, history, and score.
5. Select questionable wording and click **Comment on selection** for an exact
   text comment. Use **Page note** for a page-wide concern.
6. Mark whether the issue is blocking or non-blocking in the comment text.
7. Export the finished review with **Save JSON**. Markdown and Jira CSV are also
   available.

With the command above, feedback is saved under
`/private/tmp/host-docs-vv-feedback-3b7e56f`. Without `--dir`, the default is
`review-feedback/`. Please export a JSON copy before stopping the server so the
review can be shared or restored.

## Status and score meanings

Functional status and semantic score answer different questions:

- `PASS`: current evidence from a suitable method supports the exact functional
  claim represented by that target.
- `BLOCKED`: the procedure was not safely or authoritatively executable because
  a stated prerequisite, permission, environment, or risk gate was missing.
- `UNVALIDATED`: no claim-suitable evidence currently proves the behavior. A
  healthy-host observation does not prove an error or recovery branch.
- `NOT_APPLICABLE`: only for an approved non-executable/display carrier, with a
  recorded rationale.
- Score 1: failed, irrelevant, unsafe, obsolete, wrong, or materially
  unsupported for the surrounding wording.
- Score 2: relevant or useful, but evidence is partial, conditional,
  static-only, or not representative enough for the complete wording.
- Score 3: representative evidence strongly supports both the command behavior
  and the exact page context.

A command can run successfully but score 2 because its result does not prove the
whole surrounding claim. A blocked command can still score 2 for relevant static
support. Score 3 must agree with a current functional PASS.

## Suggested review order

A focused review of the integrity checks and representative pages should take
about 45–60 minutes. A fuller review of every score-1 and score-3 carrier, plus
a cross-page sample of score-2 and N/A carriers, will likely take 90 minutes or
more.

### 1. Confirm package integrity

Run:

```bash
npm run test-review-context
npm run check-persona-chips
node --check review-server.mjs
node --check scripts/review-context.test.mjs
python3 -B scripts/inventory_host_docs.py --check
jq empty verification/host-docs-test-sets.json \
  verification/host-docs-test-results.json \
  verification/host-docs-command-scores.json
git diff --check
```

Expected results:

- reviewer tests: 21/21 pass, including fail-closed malformed packages,
  sanitation, exact claim/citation accounting, support layers, scope/evidence
  links, Jira snapshot labeling, and strict feedback import;
- persona/frontmatter check: 40 pages passing;
- both JavaScript syntax checks exit 0;
- inventory check reports 73 routable files (40 primary pages and 33 support
  wrappers), 501 unique source-inventory targets, 565 occurrences, and 193
  commands reconciled across five access groups;
- all three canonical JSON files parse;
- Git whitespace check emits no output and exits 0.

The source inventory's 193 unique commands is intentionally different from the
179 procedure command carriers. The 193 count is broad source-discovery
coverage across 73 routable files; the 179 count is the governed
procedure-level V&V population across the 40 top-level Host pages. The 33
CLI/SDK wrapper routes are support layers, not extra Host workflows. Do not treat
either count as a pass rate.

### 2. Confirm the dashboard accounting

The dashboard should show exactly:

`40 primary Host pages · 1,687 material claims · 101 test sets · 207 branches · 477 checks · 358 non-command checks · 126 executable command targets · 53 display-only command references · 95 retained evidence records · 152 numeric semantic scores (126 executable-intent scores, 26 display-only semantic scores) · 27 approved display-only N/A · 18 CLI and 15 SDK central-reference support layers (not Host workflows)`

Check that:

- 152 numeric scores plus 27 N/A equals all 179 command carriers;
- 128 PASS + 5 FAIL + 95 BLOCKED + 749 UNVALIDATED + 27 N/A equals all 1,004
  targets;
- no blocked or unvalidated item is displayed as passed;
- every leaf PASS has exact claim-suitable evidence; a parent PASS may instead
  be a validated rollup of all required children, and a composite target must
  expose both its own status basis and its child statuses;
- malformed, stale, incomplete, or mismatched evidence causes the panel to fail
  closed instead of quietly disappearing or appearing valid.

### 3. Review these representative pages

| Page | Current page status | What to challenge |
| --- | --- | --- |
| `/host/hosting-overview` | UNVALIDATED | Does the overview clearly identify claims that still need source or runtime evidence rather than suggesting readiness? |
| `/host/hardware-prep` | BLOCKED | Is the original invalid multi-target mount check retained, is the correction visible, and is only the clean inventory procedure passed? |
| `/host/headless-install` | BLOCKED | Do the three `nvidia-smi` carriers show PASS / score 3 with equivalent-full retained proof while their wider driver and raw-install steps remain non-passing? |
| `/host/installing-host-software` | BLOCKED | Do both `nvidia-smi` prerequisites show PASS / score 3 without implying that the wizard, raw installer, storage, ports, or setup-key flow passed? |
| `/host/common-host-questions` | PASS | Are all three original route-ownership failures visible and linked to the successful correction retest? |
| `/host/common-errors-diagnostics` | BLOCKED | Is read-only collection distinguished from reproducing a real fault, and is the live follower's stop/exit requirement clear? |
| `/host/machine-errors` | BLOCKED | Do healthy-host diagnostic results avoid claiming that Docker, GPU, storage, network, or VM failure branches were validated? |
| `/host/how-to-self-test` | FAIL | Is the confirmed source/citation defect visible alongside the separate runtime prerequisites and next action? |
| `/host/pricing-your-listing` | UNVALIDATED | Does the image load, is the command context understandable, and are unproven offer claims kept non-passing? |
| `/host/vms` | BLOCKED | Is the earlier VM observation clearly disqualified by the unsuitable IOMMU setup, with unsafe bootloader/reboot work blocked by exact prerequisites and no wider VM procedure promoted to PASS? |
| `/host/volume-offers` | BLOCKED | Are all four sets present, with source-supported static results separated from the missing runtime lifecycle check? |

### 4. Challenge the semantic judgments

Please inspect at least:

- every score-3 command, because these carry the strongest support claim;
- the score-1 commands, to decide whether they are true documentation or
  evidence problems rather than extraction artifacts;
- several score-2 commands from different pages, checking that the limitation
  explains why they are not score 3;
- several N/A carriers, confirming they are genuinely display-only and that an
  owning executable procedure has not been hidden by the N/A classification;
- the retained FAQ and Hardware Prep failures and their linked retests;
- the two live-follow corrections and the static-only GPU-burn manifest result.

For each disputed item, please state:

1. page and test-set/command ID;
2. current status or score you disagree with;
3. the evidence or page wording that conflicts with it;
4. your suggested status, score, wording, or additional test;
5. whether the issue blocks repository-local structural review or requires an
   external owner/runtime workstream.

## Evidence entry points

- `HOST-DOCS-QA-SUMMARY.md` — reviewer summary, counts, methods, and gates.
- `verification/HOST-DOCS-COMMAND-COVERAGE.md` — functional and semantic
  command coverage.
- `verification/host-docs-test-sets.json` — canonical page/procedure topology
  and source bindings.
- `verification/host-docs-test-results.json` — attempts, observations,
  procedure evidence, and the 1,004-target current projection.
- `verification/host-docs-command-scores.json` — all 179 current command-carrier
  assessments (152 scored and 27 display-only `NOT_APPLICABLE`) plus withdrawn
  history.
- `verification/evidence/` — durable sanitized attempt records.
- `review-server.mjs` and `scripts/review-context.test.mjs` — reviewer joins,
  fail-closed checks, redaction, rendering, and regression tests.

Raw sensitive Host output is intentionally not in Git. Public evidence retains
sanitized observations, hashes, opaque IDs, source bindings, limitations, and
status rationale. The absence of raw sensitive output should not be treated as
proof of a result; judge whether the retained form is sufficient for the claim.

## Known remaining gates

These remain non-passing unless separately authorized and executed in a suitable
environment:

- official Host self-test behavior, using the Host's own hardware, with a fresh
  Host-owner credential that has `machine_read`, a protected workload window,
  a positive runtime limit, and cleanup authority; it does not require a paid
  test budget, and billing was not assessed;
- paid renter testing is separate and requires a fresh client credential,
  explicit spend/runtime caps, and cleanup proof;
- external TCP/UDP reachability, with an approved unused forwarded port,
  external client, bounded listener/capture, and cleanup;
- the remaining Docker GPU-load procedure, with an idle Host, explicit load
  authority, and a trusted image pinned by digest;
- VM transitions, after IOMMU repair/reboot and with an idle Host plus explicit
  operation approval;
- install, pricing, listing, maintenance, storage mutation, destructive, and
  other operational commands requiring a disposable target or explicit risk
  decision;
- private product-behavior/source-owner confirmation and final human acceptance.

Do not run any of those procedures merely to complete this review. Record them
as remaining gates unless the owner establishes a separate authorized test
window and evidence plan.

## Requested reviewer conclusion

Please return one of:

- **Evidence package acceptable for PR review** — the package accurately states
  what is proven and what remains blocked/unvalidated;
- **Changes requested** — list blocking findings and suggested corrections;
- **Unable to conclude** — state what evidence, access, or explanation is
  missing.

Please separately state whether you are accepting only the evidence package or
also recommending the documentation for merge. Those are different decisions.
The expected outcome of this review is evidence-package feedback; final merge
acceptance still belongs to the authorized PR reviewers and source owners.

## After the commit is pushed

Once `3b7e56f` or a descendant is visible on PR #185, a remote reviewer can use:

```bash
gh repo clone vast-ai/docs vast-docs-pr185
cd vast-docs-pr185
gh pr checkout 185
git log -1 --oneline
npm ci
```

They should confirm that the checked-out PR contains `3b7e56f` or an explicitly
identified descendant before relying on the results above.
