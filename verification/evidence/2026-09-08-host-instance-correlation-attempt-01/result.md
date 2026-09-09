# Existing-instance correlation — bounded result

Claim under consideration: `MCL-e12ac9f6be2ce502`, Hosting Overview / Introduction. Current claim remains UNVALIDATED; this attempt does not change the current JSON or exported HTML.

## Observations

- The authenticated Host Machines UI at `https://cloud.vast.ai/host/machines/` displayed four listed machines. The H100 row, matched visually to the user's supplied machine identity, showed `#Running : D: 0, I: 0, R: 0` and `#Stored: D: 1, I: 0, R: 0`. This is PASS only for observing that UI state, not an actual workload execution or backend ownership proof.
- The original full accessibility tree was returned immediately before the SSH observation below. A follow-up accessibility delta was captured at `2026-09-08T14:14:22.505Z`; it reported changing hardware metrics but no count changes. A helper initially treated this delta as a full tree, producing empty excerpts and false identity flags. Those helper results are invalid, not observations that the machines disappeared; the earlier full tree remains the basis for the counts. No independently timestamped full-tree file was retained, so this UI excerpt has that provenance limitation.
- SSH reached the H100 at `2026-09-08T14:13:25.067Z`–`14:13:26.142Z`, but the Docker metadata query exited 1: permission denied on `/var/run/docker.sock`. See [execution.json](execution.json). No container state or IDs were returned. No sudo, permission change, workload action or retry bypass occurred.

## Disposition and next action

The planned Host-side correlation is BLOCKED by the default user's Docker socket permission. This does not establish zero containers and does not make the documentation false. The full introductory claim still lacks its current evidence bindings and remains UNVALIDATED.

The user subsequently selected a different, available RTX4090 machine and said Host/client keys are available on that Host. Read-only API inventory is an alternative; it requires locating the specifically authorized credentials and verifying their account scopes. Do not modify Docker permissions merely for this check. An authorized operator may alternatively provide a narrowly scoped Docker metadata listing.

Independent reasoning review agreed that stored/running state is not proof of useful renter computation, and a paid rental is unnecessary solely for this broad marketplace description. Correcting its runtime-only classification and binding suitable authoritative product sources is a separate repository action, not yet performed here.

No remote files, permissions, credentials or workloads were changed; the single SSH process exited. Raw private identifiers were not copied into this record. Historical read-only attempts remain intact.
