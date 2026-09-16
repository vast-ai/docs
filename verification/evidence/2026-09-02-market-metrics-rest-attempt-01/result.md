# Market Metrics REST attempt 01 result

- Attempt ID: `ATTEMPT-2026-09-02-MARKET-METRICS-REST-01`
- Status: `BLOCKED` with semantic score `2`
- Blocker: `CREDENTIAL_PERMISSION_MACHINE_READ`
- Scope: `CLM-c48a9b18342902bb`

The exact documented `curl` request was executed with the configured client
credential supplied through the environment. The credential value was not
written to this record or the retained response.

`curl` exited `0` and returned a 130-byte JSON object. The application response
reported `success=false` and an authorization error because the configured
client credential lacks `machine_read` access. A successful transport exit
therefore does not qualify the documented metrics query as functionally
passing.

This is direct partial evidence that the documented request reaches the
endpoint and that insufficient authorization is returned as structured JSON.
It does not prove the successful metrics response shape, freshness, caching, or
rate-limit behavior. The command is `BLOCKED` on the required permission,
retains semantic score `2`, and promotes no parent target.

| Restricted artifact | SHA-256 |
| --- | --- |
| Response | `6328aeb9aca2ca67afcc84b4fc08c0988de30b778e571850182002daec978257` |
| Standard error | `72bb1a7330695ac0e9fedeadd15444c4826ccef7fadf7fb8ee50da4a087d98a5` |
| Status | `3d5a4ccd68ea82234d60c4d6b727612f063004a5e4fa304b305095de84bb812d` |

Raw evidence remains outside the documentation checkout in restricted storage.
