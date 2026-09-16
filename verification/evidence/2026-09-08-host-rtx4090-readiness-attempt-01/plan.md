# RTX4090 candidate — read-only readiness, attempt 01

Mode: PLAN_AND_EXECUTE for a bounded prerequisite check; broader live validation is PLAN ONLY until specific operations and credentials are established.

The user selected the RTX4090 machine and supplied its SSH target, then identified the existing Vast CLI credential as probably the client key and mentioned a separate Host key store. Public evidence uses alias HOST-RTX4090-01; private targets and credential contents must not be retained here. This is a different target from the H100; evidence cannot be carried between them as proof of the same machine.

## Scope and expected observations

Use strict SSH with batch mode, no forwarding, no sudo and a 30-second timeout. Read only GPU index/model/driver via `nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader,nounits`, locate `vastai` with `command -v vastai`, and query installed package version using Python standard-library distribution metadata. Successful observations establish only hardware/CLI availability. A missing tool or permission has a specific prerequisite; GPU discovery does not establish idle status or rental eligibility.

After inspecting the installed CLI's documented credential-path logic, check existence/readability only at those exact paths, never their values. Do not recursively search home directories, histories, logs or key stores. Do not execute the CLI merely to find its key if initialization might migrate credentials or create directories. The Host key location still needs the user's exact path or store name. No API request or credential read is included in this first prerequisite check.

Follow-up read-only API checks will require an explicit method and pinned CLI/schema basis: verify Host/client account identity, query this Host's machine state, query client-visible offers for this machine, and compare existing instance identities/state with the dashboard. Record sanitized outputs and exact claim bindings; access alone is not proof.

No rental, self-test, storage/volume mutation, VM changes, host maintenance, service restart, installation, privilege escalation or credential rewrite. A future rental requires explicit workload, exact offer, spending/duration limits, monitoring and cleanup authorization. Code/source and Product/Finance/Legal claims remain separate.

Baseline: same HEAD, current claim-package, staged-diff and index digests as [the prior plan](../2026-09-08-host-instance-correlation-attempt-01/plan.md). Additive plan/evidence edits from that attempt are present. Existing current claim records, historical evidence and HTML remain unchanged.

## Addendum before credential/API checks

The user explicitly identified the Host credential's exact macOS Keychain service and account. Retrieve only that entry in memory using the native Keychain command; do not log its value, put it in command arguments, copy it into the repository or change the configured CLI key. The configured client key may be read only at the candidate's installed CLI credential path after its source/path logic is confirmed; the user has authorized use of that credential but its account role remains an assumption until checked.

Canonical request basis inspected locally: `vast-ai/vast-cli` checkout HEAD `18c4f2ccd6da587d5352f8741c71805a9a18e1ae`, `vast.py` lines 75, 580–635, 4328–4415, 5722–5765, 6474–6492, 8907–8950. Request defaults use `https://console.vast.ai/api/v0` and Bearer authorization. Record source file digest and dirty state before relying on revision identity. Use only these bounded read-only requests: GET `/users/current`; GET `/machines?owner=me` (retain only selected machine); GET `/instances?owner=me` (retain only selected-machine IDs/state); and the source-defined offer search POST `/bundles/` with an exact machine filter. Offer search is a read-only query despite its HTTP method. Disable redirects, set a timeout, omit credentials from URLs, never dump response bodies or auth headers.

Keep identity as a digest and role/access booleans; keep only the selected machine's GPU/state fields and pseudonymized matching instance/offer identifiers. Do not retain email, credit, SSH keys, renter metadata, environment, templates or command strings returned incidentally by the API. Do not interpret successful authentication as proof of all permissions or a successful search as a completed rental. A failed original default-filter search must remain recorded before any deliberate filter change.

These requests are API observations, not execution of the documented CLI command. CLI command PASS requires its own exact command run. A denied/missing credential or scope is a specific prerequisite; absent runtime proof remains UNVALIDATED. No paid or mutating lifecycle operation has been authorized.

### Retest amendment — same-origin trailing-slash routing

The first credentialed requests failed under the deliberately strict no-redirect policy. A credential-free diagnostic observed a 301 from `/api/v0/users/current` to `/api/v0/users/current/` on the same official origin. Inspect the equivalent machines redirect, and retest only the exact same-origin trailing-slash destinations. This is a request-path correction, not a change to credentials or server trust. Preserve first-attempt errors and the diagnostic; do not enable arbitrary redirect following or infer an authorization failure from the earlier transport error.
