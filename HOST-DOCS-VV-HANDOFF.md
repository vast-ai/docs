# Host Docs V&V handoff: PR #185 / CON-1518

This draft reviewer update supersedes the older pre-execution counts in previous
PR and Jira comments. The repository-local evidence structure is reconciled for
the current scope. The repository-local closeout suite is complete, external
V&V work is not complete, and the documentation is not self-approved.

## Draft update — repository-local closeout complete

The Host Docs repository-local V&V package has a reconciled disposition for
every projected target and retains both failed attempts and successful
corrections. This establishes structural traceability, not semantic acceptance.

- Primary scope: 40 top-level Host pages (39 authored and one generated), 101
  test sets, 207 branches, 477 steps, and 179 command carriers, for 1,004
  projected targets.
- Support scope: 33 central-reference support layers represented by 18 CLI and
  15 SDK wrapper routes. They are not separate Host workflows.
- Broad source inventory: 73 routable files, 501 unique targets, 565 occurrences,
  and 193 commands. The commands reconcile as 0 paid+root, 2 paid-only, 54
  Host-root, 22 Host-machine without root, and 115 requiring neither; five
  require an external client.
- Current target status: 128 PASS, 97 BLOCKED, 747 UNVALIDATED, 5 FAIL, and
  27 N/A.
- Material-claim status: 167 PASS, 153 FAIL, 23 BLOCKED, and 1,344 UNVALIDATED
  across 1,687 claims. One hundred fifty-three required citations are absent; 19
  required citations are present but not yet verified; 1,515 claims do not
  require one.
- Command functional status: 84 PASS, 7 BLOCKED, 60 UNVALIDATED, 1 FAIL, and
  27 N/A.
- Command semantic assessment: 12 score 1, 119 score 2, 21 score 3, and 27
  approved display-only N/A.
- Evidence model: 58 retained attempts hash-bound to 57 unique artifacts, 50
  command results, 42 procedure results, 38 direct-proof ceilings, and 101
  direct bindings, plus three material-claim result manifests and one
  support-layer result with 33 exact bindings.
- Reviewer-context integrity: 24/24 tests pass, including fail-closed package,
  sanitation, exact scope/evidence links, support-layer, Jira-snapshot, and
  feedback-import contracts.

Functional command validation is now 84 of 152 applicable carriers (55.3%).
The remaining 68 of 152 (44.7%) comprise 7 BLOCKED, 60 UNVALIDATED, and one
FAIL. The 27 approved display-only carriers are excluded from that completion
rate.

Functional status and semantic score remain separate. A command can run but
still receive score 2 when the observation only partly supports the page's
claim. Score 3 requires current command-level PASS evidence with an exact-full
or explicitly equivalent-full proof role. Command evidence does not promote a
parent step, branch, test set, or page automatically.

The reviewer now also separates canonical source/signature support from
retained runtime behavior for every exact command. The command itself links to
the pinned handler when available; its page/heading and retained-evidence links
preserve the exact binding. Reconciliation records are labeled accounting only,
not command proof. The pinned source revision and the runtime attempt's own
build/environment must be compared rather than treated as one result.

Completed or advanced in the latest pass:

- The documented Docker GPU-injection command using `--gpus all` failed with
  exit 125 on the authorized idle Host. Docker required the registered NVIDIA
  runtime. Both affected pages now use `--runtime=nvidia`; a candidate run and
  the corrected published form passed and showed the same four GPUs. The three
  corrected carriers are PASS with score 3. The separate GPU-burn command and
  parent troubleshooting procedures remain non-passing.
- Manual `vastai dump-logs <machine>` passed for two carriers and created a
  parseable four-file bundle with zero collection errors. The raw archive stays
  restricted until a human reviews it for external sharing.
- The exact installer-log read command passed from the confirmed launch
  directory. Its raw output stays private because automated scans found
  possible sensitive markers.
- The bounded self-test log follower passed for two carriers. It proved the
  path, privileges, follow behavior, interruption, and cleanup. No self-test
  was active, so both carriers remain score 2 and no parent was promoted.
- The exact kernel-log follower passed at command-mechanics level after a
  bounded Host run. Unrelated transient workload activity then made the
  environment non-controlled, so Host execution was paused. No kernel event
  was reproduced, the score remains 2, and no parent was promoted.
- The exact Market Metrics REST request reached the endpoint and returned
  structured JSON, but the configured client credential lacks machine-read
  permission. The carrier is BLOCKED with score 2; curl exit 0 is not treated
  as a successful API result.
- `pip install --upgrade vastai` passed in a clean disposable macOS arm64
  virtual environment, and that environment's own CLI reported version 1.5.6.
  The earlier DNS-blocked attempt remains in the history and its accidental
  global-version output is explicitly rejected.
- `vastai set api-key <API_KEY>` completed with a synthetic value in an
  isolated configuration directory, but Vast CLI 1.5.6 created the credential
  file with mode `0644` under normal umask `022`. The command is current FAIL
  with score 1; no real key or Host operation was used.
- Host-local bundling setup with `--include-local-host-artifacts` remains
  BLOCKED. The two command carriers remain UNVALIDATED because execution never
  started. The Host lacks the Python venv/ensurepip component required by the
  safe isolated method; no operating-system package was installed and
  temporary attempt files were removed.
- The Network and Ports page now says to run the foreground HTTP listener and
  `ss` check in separate SSH sessions, then stop with Ctrl+C and confirm no
  listener remains. That source defect is corrected; external-WAN runtime
  validation remains BLOCKED.
- Earlier authorized read-only Host checks, restricted installation evidence,
  inventory reconciliation, and independent-review corrections remain linked
  and unchanged. No command-only result was used to promote a broader page.

The official Host self-test is a Host-owner workflow against the Host's own
hardware. It is not a paid renter test and does not require paid-test budget
approval. It still needs a Host-owner API credential because the workflow uses
the control plane to select and create its temporary diagnostic workload. The
available client credential lacks that permission, so end-to-end self-test
evidence remains BLOCKED. Billing was not assessed.

Paid renter-side behavior is a separate remaining validation class with its
own client authority, budget, marketplace, and cleanup gates.

## How to review

```bash
gh repo clone vast-ai/docs vast-docs-pr185
cd vast-docs-pr185
gh pr checkout 185
npm ci
```

Terminal 1:

```bash
npm run dev:review
```

Terminal 2:

```bash
node review-server.mjs --port 4000 --target http://127.0.0.1:3000
```

1. Open `http://127.0.0.1:4000/host/hosting-overview`.
2. Click **Review**.
3. Expand **V&V evidence for this page**.
4. Open a test set to inspect its branches, steps, command carriers, retained evidence records,
   current status, limitations, history, and scores.
5. Select questionable wording and click **Comment on selection**, or use
   **Page note**.
6. Export feedback with **Save JSON**, Markdown, or Jira CSV. The combined
   dashboard is `http://127.0.0.1:4000/__review__/`.

## Remaining gates

- Secure Host-owner API authentication for the official Host self-test.
- An approved isolated CLI method or approved venv support for the Host-local
  diagnostic bundle.
- A genuine outside-LAN client for external TCP/UDP verification.
- Suitable NVSwitch hardware for NVSwitch-specific claims.
- Repaired and explicitly approved VM/IOMMU enable, disable, and health checks.
- Explicit maintenance authorization for GPU burn/load and any service,
  storage, listing, pricing, or other state-changing procedure.
- Separate paid renter-side tests where the documentation makes renter-side
  claims.
- Product or source-owner confirmation for private-policy claims, followed by
  independent human review and acceptance.
- A documentation-governance decision defining who may approve each Product,
  Finance, Legal, and canonical-source authority class; the minimum dated,
  claim-scoped source or decision record; and when a citation is verified.
  A reply or link is candidate evidence, not acceptance; it must be bound by an
  independent reviewer to the exact current claim and required lane. Until that
  acceptance contract and its schema tests are implemented, owner input is
  retained as non-promoting context and no owner acceptance is inferred. See
  [Reviewer Input 9](./REVIEW-QUESTIONS.md#input-9-owner-evidence-acceptance-contract).

No credential, private address, machine identifier, or raw sensitive output is
included in the public reviewer documents. Temporary credentials used for
testing must still be rotated according to the agreed cleanup plan.
