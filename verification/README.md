# Host Docs verification and validation evidence

This package applies the [Oxiom Systems V&V Evidence procedure](https://github.com/Oxiom-Systems/vv-evidence)
at commit `a0b49e328777b85c635016c7f5920ce270ade759` to the Host Docs
review in [PR #185](https://github.com/vast-ai/docs/pull/185).

It is the reviewer entry point for fresh, retained evidence. The detailed
population remains in [`HOST-DOCS-VERIFICATION.md`](../HOST-DOCS-VERIFICATION.md),
its 193 commands are grouped by execution access in
[`HOST-DOCS-COMMAND-ACCESS.md`](../HOST-DOCS-COMMAND-ACCESS.md), and the CLI
population remains in
[`HOST-DOCS-CLI-COMMAND-CHECK.md`](../HOST-DOCS-CLI-COMMAND-CHECK.md). This
package does not duplicate those 501 targets.

## Current evidence state

- Primary procedure projection: 40 top-level Host pages (39 authored and one
  generated), 101 test sets, 207 branches, 477 steps, and 179 command carriers,
  for 1,004 targets in total.
- Generated support scope: 33 central-reference support layers represented by
  18 CLI and 15 SDK wrapper routes. They are not separate Host workflows.
- Target status: 128 PASS, 97 BLOCKED, 747 UNVALIDATED, 5 FAIL, and 27 N/A.
- Material-claim status: 167 PASS, 153 FAIL, 23 BLOCKED, and 1,344 UNVALIDATED
  across 1,687 claims. Citation status is 153 required-and-absent, 19
  required-and-present-but-unverified, and 1,515 not required.
- Command status: 84 PASS, 7 BLOCKED, 60 UNVALIDATED, 1 FAIL, and 27 N/A.
- Command semantics: 12 score 1, 119 score 2, 21 score 3, and 27 approved
  display-only N/A.
- Evidence model: 58 retained attempts hash-bound to 57 unique artifacts, 50
  command results, 42 procedure results, 38 direct-proof ceilings, and 101
  direct bindings, plus three material-claim result manifests and one
  support-layer result with 33 exact bindings.
- Reviewer-context integrity: 24/24 tests pass, including fail-closed malformed
  packages, sanitation, exact claim/citation accounting, support layers,
  reviewer links, Jira snapshot labeling, and feedback import.

The repository-local evidence structure is complete for this scope. These
numbers describe traceability and evidence disposition, not semantic
acceptance, external-workstream completion, or human approval. Command evidence
is not automatically promoted to a parent step, branch, test set, or page.

## Validation plan

- **Scope and target:** corrected Host Docs content and V&V package in the
  working tree after `3b7e56f0db6588953589e0692e75b7274526d5f9`; historical
  source and QA revisions remain recorded in individual attempts.
- **Population and coverage:** 73 routable files comprising 40 primary Host
  pages and 33 generated CLI/SDK support wrappers, plus all 33 imported Host
  snippets, all 501 unique inventory targets and 565 occurrences, all 193
  commands classified into five execution-access groups, all 201 documented
  Vast CLI occurrences, and the separate 1,004-target procedure projection for
  the 40 primary pages.
  Generated inventories establish the population; freshness and reviewer
  checks establish that they still describe the target.
- **Local-safe verification:** inventory freshness and structural parsing, CLI
  registry conformance, persona synchronization, reviewer-context tests,
  review-server syntax, OpenAPI validation, link analysis, accessibility
  analysis, and whitespace checks.
- **Authorized-Host verification:** bounded read-only inspection, documented
  GPU-injection diagnostics, installer-log access, and bounded log following.
  Every attempt records cleanup and retains command-level limitations. The
  current Host evidence does not promote broader procedures or pages.
- **Validation requiring more authority or environment:** official Host
  self-test runtime, Host-local artifact bundling, external-WAN tests,
  NVSwitch-specific behavior, GPU burn/load, repaired VM/IOMMU sequences,
  incident paths, storage or listing changes, and other disruptive or mutating
  operations. These remain `BLOCKED` or `UNVALIDATED` unless a linked retained
  attempt supplies claim-suitable proof.
- **Separate paid renter-side validation:** paid client behavior remains its
  own class with its own client authority, budget, marketplace, and cleanup
  gates. It is not the official Host self-test.
- **Environment and prerequisites:** macOS arm64; Python 3; Bash; Git;
  repository dependencies from `npm ci`; supported Node 24 for Mint; a clean
  official Vast CLI checkout whose full revision is retained; and, where
  stated, an authorized idle Vast Host.
- **Evidence retained:** exact command, timestamps, captured exit status when
  available, stdout, stderr, environment, docs and CLI Git identities,
  package-lock hash, result interpretation, known failures, and reviewer-facing
  status reconciliation. Missing fields remain explicit and are never
  reconstructed.
- **Status criteria:** `PASS` requires retained current output from a method
  suitable for the claim; `FAIL` is an observed discrepancy; `BLOCKED` is a
  suitable check prevented by missing authority, access, or environment;
  `UNVALIDATED` has no claim-suitable execution; `STALE` no longer applies to
  the named target; `N/A` requires a rationale.
- **Safety:** local-safe checks contain no paid, credential-bearing,
  privileged, destructive, account-mutating, or production-changing command.
  Authorized-Host attempts use separate frozen plans, bounded execution, and
  cleanup checks. Restricted raw evidence must never be committed or shared
  without a human secret review.

## Host self-test authorization

The official Host self-test is run by a Host owner against that Host's own
hardware. It is not a paid renter test and does not need a paid-test budget
approval. The current workflow still needs a Host-owner API credential because
it selects and creates a temporary diagnostic workload through the control
plane. The available client credential lacks that permission, so the
end-to-end self-test remains BLOCKED. Billing was not assessed.

Do not replace this missing Host-owner evidence with a paid client run. Paid
renter-side behavior has different claims and authorization gates.

## Reviewer workflow

After checking out the evidence baseline and installing dependencies:

```bash
npm ci
./verification/run-local-safe-checks.sh \
  <unique-run-id> \
  /path/to/clean/official/vast-cli
```

The run ID creates a new append-only directory under `verification/evidence/`;
the script refuses to overwrite an existing attempt. Start with
[`summary.md`](./summary.md), then review [`inventory.md`](./inventory.md), the
[`issue and retest ledger`](./issues.md), and the linked attempt results.

For the browser review, start the docs and review proxy, open a Host page on
port 4000, click **Review**, and expand **V&V evidence for this page**. The
panel separates non-command checks, executable-intent command targets, and
display-only command references. It shows retained evidence, limitations,
derived current status, inventory baseline, history, and semantic scores only
where they apply. A page can still show BLOCKED or UNVALIDATED even when one of
its child commands has passed.

For each exact executable command, read the two proof lanes independently:

- **Source/signature support** links the command itself to the immutable Vast
  CLI registration and its generated static-check record. A PASS here proves
  syntax and option registration only; no API or Host operation was run.
- **Runtime behavior** links only retained execution that is bound to that
  command, page, and heading. It states the observed result, proof role,
  limitations, missing prerequisite, and next action. Reconciliation records
  are labeled as status accounting and are never presented as runtime proof.

The generated source/signature index is
[`HOST-DOCS-CLI-COMMAND-CHECK.md`](../HOST-DOCS-CLI-COMMAND-CHECK.md). Evidence
links opened from the panel include a generated navigation header naming the
exact page, heading, command or target, current status, and proof limitation;
the retained artifact follows underneath and remains the evidence itself.

The most recent operational evidence is indexed in
[`summary.md`](./summary.md), including the documented GPU-injection failure
and corrected retest, manual CLI bundle, installer-log access, bounded
self-test and kernel-log followers, CLI installation attempts, the Market
Metrics authorization blocker, and the Host-local bundle setup blocker. Host
execution was paused when unrelated transient workload activity made the
kernel-follower environment non-controlled.

The latest local-only check also records a CLI credential-permission failure:
Vast CLI 1.5.6 created the file written by `vastai set api-key` with mode
`0644` under normal umask `022`. The carrier is current FAIL with score 1 and
is linked from the issue ledger; it used only a synthetic value in an isolated
configuration directory.

This package supports technical review; it does not constitute acceptance or
certification. An authorized reviewer makes that decision.
