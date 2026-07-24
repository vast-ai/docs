# HOST-2752: Host & client SLA documentation

**Branch:** `HOST-2752-SLA-API-Documentation`  
**Base:** `origin/main`  
**Scope:** User-facing SLA docs aligned to v5 ask/search model and compliance wording.

## Summary

Documents SLA for hosts and clients under the current design: hosts publish a **claim** and **confidence** (`sla_r_claim`, `sla_sigma_x`); clients choose **target** at search/rent (`target_reliability`). User-facing copy uses **SLA charge** (not premium) and avoids insurance/betting language.

## Details

### Guides

| Page | Path | Audience |
| --- | --- | --- |
| SLA Offers | `/host/sla-offers` | Hosts — claim/confidence listing, economics, monitoring |
| SLA Earnings Backtester | `/host/sla-backtester` | Hosts — historical replay (`r` = claim=target in sim) |
| SLA Coverage | `/guides/instances/choosing/sla-coverage` | Clients — search filters, charges, credits |

### Model corrections vs earlier drafts

- `sla_r_target` is **not** host-settable on asks (ignored if sent).
- SLA activates on `sla_r_claim > 0`; disable with `sla_r_claim = 0`.
- Optional `sla_max_beta` documented for advanced hosts.
- Backtester `beta` is derived from `r` for non-admins.
- Billing note: intended compute billed; compensation via settlement credits.

### OpenAPI / nav

- `list_machine.yaml`, `show_machines.yaml`, `sla_backtest.yaml`, `show_earnings.yaml` updated; `openapi.yaml` regenerated.
- `docs.json` adds client SLA Coverage under Find & rent.
- Search CLI docs list `has_sla`, `expected_reliability`, `target_reliability`.

## Compliance wording

Forbidden in user docs: insurance, premium (prefer **SLA charge**), betting, gambling, bet. API field names such as `slaPremiumPerHour` are documented as the SLA charge rate without using “premium” as prose.
