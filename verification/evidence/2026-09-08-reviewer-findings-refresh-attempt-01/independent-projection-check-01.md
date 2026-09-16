# Independent four-claim projection inspection

Method: read-only inspection by `readonly_adjudication_impl`, separate from the main agent's browser check. This retained summary is the agent's reported observation, not raw HTTP bodies or product-runtime evidence.

All four selected context requests returned HTTP200, `currentReview.available=true`, and source header `dfdea55d5a85c9aa3f8a75e954829f4860bcbac509c4e525df03ac62a2b6a472`.

| Claim | Route | Status / basis | Stored-record parity |
|---|---|---|---|
| MCL-dfebca7edafe9c59 | /host/vms | FAIL / CONFIRMED_DOCUMENTATION_DEFECT | PASS |
| MCL-323c8fb8180f5f62 | /host/first-24-hours | FAIL / CONFIRMED_DOCUMENTATION_DEFECT | PASS |
| MCL-96ee15f730e698d8 | /host/not-in-search | PASS / RUNTIME_BEHAVIOR | PASS |
| MCL-eeaf6da83da9eca7 | /host/how-to-self-test | BLOCKED / RUNTIME_BEHAVIOR | PASS |

Parity means semantic equality after the API projection: keys are camel-cased and display-only `artifactSha256`, `sourcePassages`, and `sourceLocation` fields are added. Retained source fields, evidence/source refs, histories, text, headings, spans, status, rationale, and next action match current JSON.

The current self-test rationale/next action name workload authorization, create permission, controlled spend/window/runtime bounds and cleanup authority limited to task-created resources. They do not say the Host key is unavailable. The former missing-key state is historical.

Proof references found: VM findings registry/source-retest/status; client-context findings registry/canonical-source inspection; PASS read-only adjudications registry; BLOCKED historical self-test and Ada readiness records. No missing projection field was reported. No edits or external requests were made by the inspecting agent.
