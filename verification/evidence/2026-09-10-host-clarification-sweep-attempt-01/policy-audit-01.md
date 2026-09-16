# Policy-method audit — recommendation only

Reviewed all 254 exact `inventory-policy-01.json` policy-group occurrences against their current classification, status/rationale, retained authority, and source pointers. This audit changes neither status nor model and records no approval, acceptance, policy acknowledgement, or product/runtime proof.

| Recommendation | Count |
| --- | ---: |
| Keep current bounded disposition | 70 |
| Correct review method | 145 |
| Reuse a retained source candidate | 39 |

Method split: 64 advice reviews, 36 technical-source checks, 69 mixed reviews, 39 governing-source reviews, 27 already-supported published clauses, 10 real runtime checks, and 9 policy-confirmation cases. Forty-one records carry an explicit bounded retained-source pointer (two mixed advice records retain a partial pointer without being promoted to source candidates).

Strongest corrections:

- Ordinary planning/security guidance is not a runtime target: pricing, optimization, security hygiene, support handoffs, and availability planning move to `ADVICE_REVIEW` unless they contain a separable product fact.
- Account, Teams, payout-context, setup-link, and permission statements move to canonical configuration/API/code review; an observation is reserved for an asserted account-specific result, not the declared interface setting.
- Existing agreement and CLI captures are source candidates only for their literal fragments. Price-extension excerpts do not prove creation, unlisting, end-date immutability, billing enforcement, or a completed rental.
- The actual policy-confirmation set is limited to the unsupported instruction/restriction passages below. Each must use existing Terms/agreement/policy first; a responsible policy owner is needed only if that authority is absent or ambiguous. No runtime test would establish the rule.

Most useful follow-ups:

1. `MCL-b61d15c0282ef567` — local GPU-work restriction: governing policy first.
2. `MCL-c59caa4cd52bcc1f` — “should be dedicated”: preserve *should*, do not inflate to *must*.
3. `MCL-393941d0e9be9d31` — idle-container noninterference: policy scope, not runtime.
4. `MCL-af1c482a08b09316` — local workloads during rental: policy source first.
5. `MCL-03c73e4182b1e7fe` — idle rental “leave it running”: policy source first.
6. `MCL-595d905880a176c1` — retained CLI excerpt supports only current-term price wording.
7. `MCL-1998fd97e70ac6c0` — Compliance/certification sources conflict; this needs Product/Compliance applicability authority, not testing.
8. `MCL-3d796f5ae7f2020e` — agreement payment clock is partial; payout schedule estimate remains a genuine finance-operations source gap.

Financial, tax, legal, program-enforcement, and asserted backend lifecycle gaps remain open with their applicable governing-source/runtime methods. The policy-acknowledgement presentation artifact is explicitly non-authority and was not used as proof.
