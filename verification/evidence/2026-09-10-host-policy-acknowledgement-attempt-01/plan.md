# Policy acknowledgement presentation

Mode: PLAN_AND_EXECUTE. Scope frozen before implementation on 10 September 2026.
Exact starting tree: baseline-01.json (4,018 Git-visible files).

## Intended result

Ask for the right review action in plain English. A rule needs an applicable
approved policy or a recorded decision by its responsible policy owner, not a
test rental. Use existing authority before asking for a new decision. Merely
reading or acknowledging a draft does not approve it. Keep technical behavior,
legal terms and financial promises separate.

## Exact presentation inventory

| Claim | Page / heading | Requested presentation |
| --- | --- | --- |
| MCL-b61d15c0282ef567 | Hosting Overview / Host Commitment | Confirm or correct the local-workload restriction and its scope; cite approved policy first. |
| MCL-c59caa4cd52bcc1f | Supported Hardware / Unsupported Or Discouraged Setups | Confirm whether dedication is advice or a requirement; do not turn “should” into “must”. |
| MCL-af1c482a08b09316 | Workload Policy / Host Responsibilities | Confirm or correct the local-workload restriction and its scope. |
| MCL-393941d0e9be9d31 | Workload Policy / Host Responsibilities | Confirm or correct the noninterference rule; do not imply permission to inspect renter data. |
| MCL-03c73e4182b1e7fe | Workload Policy / What To Do | Confirm the idle-rental instruction using existing applicable rules first. |
| MCL-3b10b5e64ee55003 | Fleet Operations / Default Jobs | Check the referenced policy source. No new compliance approval is needed just to point to it. |
| MCL-e12ac9f6be2ce502 | Hosting Overview / Introduction | Already-supported basic product description: official publications suffice; no test rental needed. |

Exact text, classification, evidence requirements, current status and recorded
rationale are taken from the unchanged baseline claim model. Allowlist guards
must fall back to the recorded finding when these change. The fleet instruction
is not a new policy-acknowledgement request.

## Success criteria and checks

1. Shared copy renders the same request in the HTML and localhost reviewer.
2. No acknowledgement, authority, acceptance or PASS is recorded by this change.
   Current statuses, required citation defects, source records and totals remain
   unchanged; precise recorded status is available in current record details.
3. The five rules ask for policy acknowledgement only if existing approved
   authority does not already settle them. They still require the applicable
   citation. No rental is required to establish a rule; enforcement is separate.
4. Advice, policy, technical behavior and legal/financial terms are not conflated.
   No new approval request for a link to existing policy.
5. Exact-match regression tests cover changed wording, status, evidence lanes
   and claim-specific rationale, plus all 2,013 immutable claim records.
6. Regenerate HTML; run focused renderer/integration tests, offline browser and
   all-Host reviewer checks. Preserve failed checks and any retest separately.
7. Refresh only the local reviewer service and Graphify's derived AST graph.
   Record final source/model/evidence integrity and update traceability.

No product operation, paid rental, SSH, reboot, publication, push or merge.
Earlier findings remain in retained evidence, not in the main reader view.
