# Inventory amendment 01 — exact context and source safety

Appended before execution on 2026-09-08.

- HOST-02: additionally run exact `vastai show user` under the Host key. The not-in-search passage specifically asks for Host-account identity; a client-only run cannot establish this context.
- HOST-03: additionally run exact `vastai show machines` under Host key, to pair with HOST-01 text show-machine for the complete maintenance read-only command block. This cannot prove contracts ended or authorize maintenance.
- CLIENT-07: additionally run `vastai search offers -n 'machine_id=<selected-machine>' --limit 200 --raw` under client key and retain only selected-machine match, GPU model/count, rentable/rented/verification booleans and count. The exact documented text variants remain separate checks.
- HOST-04: strict SSH to the designated Ada target, run only Python os.access/isfile for the exact installed VM-helper path. Do not import, execute, modify or elevate to read the helper. This only determines whether source inspection is possible.
- LOCAL-01 safety refinement: canonical set-api-key deletes the legacy ~/.vast_api_key even with isolated XDG. Before running the non-secret-fixture storage test, abort if that legacy file exists; retain only presence/equality checks for real configuration. Never change HOME, never use a real key as the positional fixture, unset inherited VAST_API_KEY for this one local command. No live key save or authentication is claimed.

Both named keys have now authenticated with different nonempty stable account IDs; see account-observations-01.json. This resolves key location/authentication and distinct account identity, not workload/create permissions. The client-owned instance list is empty at capture time; no task instance exists to stop.

