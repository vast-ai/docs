# Current Host Docs review plan — CON-1518 / PR #185

## Scope and starting state

User-requested order: bring V&V up to merged content, fix known repository
defects, and work through unsupported client-facing claims. Maintain a concrete
claim worklist rather than a list of opaque audit identifiers.

Starting revision: `bfa926c9421521767fa7411718bd31ea38b38528`.
Starting tree: `b603f6ac42f2e4a2c99385fceae23a0cd2b7a036`.
Branch: `CON-1584-host-cli-api-sdk`. Tracked files/index were clean. Preserve all
31,169 pre-existing untracked paths. Exact local-only working-tree capture:
SHA-256 `0696817522e0d1a34844ccf8268bb99ca42cb7cc47641307c18e6e824082f510`.

Current navigation has 44 primary Host pages. The 18 CLI and 15 SDK wrappers are
central-reference support layers, not independent Host workflows. The earlier
40-page source/evidence package remains historical at exact snapshot `7d42a0d`.

## Work and evidence

1. Reconcile the current pages, headings, claims, ordered procedures, commands,
   and support references. Preserve historical attempts and explicitly map
   unchanged, changed, new, and retired coverage. Do not silently carry forward
   proof for changed wording or broaden partial evidence.
2. Record and correct the Volume Offers Command Map source-binding defect and
   generated Self-Test reference flag typography. Retest exact source spans,
   links, generated output, and rendered command text.
3. Review unsupported claims against available canonical Vast code, schemas,
   configuration, generators, and retained observations. Distinguish actual
   product assertions from navigation/editorial text. Keep original findings
   and explain every corrected classification and focused retest.
4. Produce a client-facing claim worklist with exact wording, page/heading
   links, existing evidence and limits, missing proof, responsible role, and
   exact next action. Keep runtime/operator and Product/Finance/Legal/source
   owner actions separately identifiable.
5. Verify current source coverage, evidence integrity, links, reviewer behavior,
   generated references, static signatures, and affected rendered pages. Retain
   failures and corrections. Update REVIEW-TRACEABILITY.md and the registers.

PASS applies only to the claim actually supported by the method and retained
evidence. Missing evidence is UNVALIDATED. A confirmed incorrect claim or missing
required citation is FAIL. Changed evidence targets are STALE until reconciled.
BLOCKED requires a specific unavailable source, owner, permission, input,
environment, or authorization. Navigation/occurrence accounting is not proof of
product behavior. A present link alone is not an authoritative citation.

## Boundaries and completion

Only repository-local checks and loopback browser tests are authorized here.
No Host/API credentials, paid runs, WAN probes, privileged, mutating, destructive,
or workload-affecting operations. No invented Product/Finance/Legal decisions,
human acceptance, or Jira/PR posting. Publishing is separate from this work.

This pass is complete when current coverage and each reviewed disposition are
traceable, known local defects have linked retests, the safe available evidence
has been assessed without overclaiming, and unresolved client-facing claims
have an understandable worklist. External runtime and owner workstreams remain
open unless their suitable independent evidence is actually supplied.
