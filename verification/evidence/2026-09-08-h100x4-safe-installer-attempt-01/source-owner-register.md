# Product, Finance, Legal and source-owner work — installation preparation

PR #185 / CON-1518, 2026-09-08. None of these workstreams is declared complete.
The [existing claim-level owner register](../2026-09-08-host-client-unblocking-attempt-01/source-owner-register.md)
remains open, including its separate repository-local wording defects.

| State | Claim impact | Required source / responsible role | Exact next action |
|---|---|---|---|
| UNVALIDATED | Installing Host Software / Host Installer Wizard: the observed local source has not been bound to the distributed binary | Installer release/source owner; downloaded binary digest 0d078186004a37f8d2518fced156d39caf0ae36834797f008ce79d53459c268e; inspected checkout 2d33c362bd0293f73730b258e77c9bcd1945ee14 | Obtain release provenance/build identity or inspect the exact shipped implementation; bind it before attributing local-source behavior to that binary. Source absence alone is not BLOCKED. |
| UNVALIDATED | After Install: omission of one helper is not proof of every daemon/server publication or no-reboot path | Installer/daemon/update and machine-registration source owners; exact downstream executable identities | Retain the resolved installer updater, daemon package, metadata script, diagnostic scripts and images actually used. Inspect publication/reboot controls. Escalate only a specific inaccessible source, required permission or decision, not a generic request for owner approval. |
| FAIL, scoped route compatibility | Host Installer Wizard: intended self-test omission is not a successful end state in the reviewed TUI flow | TUI implementation maintainer | If the TUI route is required, add an explicit skipped/deferred state with source tests and a retained rendered TUI run. A direct modified-installer result must not close this TUI gap. |
| UNVALIDATED / existing statuses retained | Account, contract, billing, pricing, tax and policy claims elsewhere in Host Docs | Accountable Product, Finance or Legal owner as named in the existing register | Obtain a dated authoritative source/decision for each exact claim and citation. An installation or a host account does not establish commercial/legal authority. |

The user's selected listing prices are operational settings, not evidence of
Vast's general pricing, billing or legal policy. No new Product/Finance/Legal
confirmation, citation acceptance or human sign-off was received. No Jira/PR post,
push, merge or acceptance record was created.
