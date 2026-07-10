# The 8 blocking inputs — what we need from reviewers

> Temporary review aid — removed before merge, like `review-server.mjs`.
>
> These are the eight decisions/confirmations that finish the Host Docs epic
> (CON-1187). The writing is done; every item below is a **decision, review, or
> confirmation from your side** — nothing here is writing work. The first two
> unblock everything else.
>
> **Three ways to answer — pick whichever is easiest:**
> 1. Comment inline on this file in the [PR #185 diff](https://github.com/vast-ai/docs/pull/185/files).
> 2. In the local review kit, open `http://localhost:4000/review-questions`, select a question, and comment — it lands in the same feedback export as your page comments.
> 3. Reply on the linked Jira ticket.

## Input 1. IA approval

**Owner: Michele + docs owners · Round 0 · unblocks everything**

Approve or modify the information architecture (CON-1518 decision points a–d):

- (a) **Lifecycle sidebar** — Before You Host → Set Up → Verify & List → Operate → Reference, vs. some other top-level grouping.
- (b) **P0/P1/P2 priority order** — the ticket-volume-driven ordering of new docs.
- (c) **Supported Hardware as the #1 prevention doc** — even though it isn't the largest ticket bucket.
- (d) **Persona tags** — keep the visible chips (top-right of each page), restyle them, or drop to frontmatter-only convention.

Blocks: every other review round. Detail: CON-1518.

## Input 2. Review mechanics

**Owner: Michele + docs owners**

How do you want to review the content: one small PR per sidebar group (round), or staged review of [PR #185](https://github.com/vast-ai/docs/pull/185) with per-round checklists? PR #185 now contains all the work (former #153 is an ancestor of it). Either way, **#152 and #153 should be closed as superseded**.

Blocks: scheduling of every content round. Detail: CON-1518, CON-1584.

## Input 3. Pricing content review

**Owner: Gobind / Solutions Engineering · Round 3 · CON-1256**

Review the business/pricing positioning: [Pricing Your Listing](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/host/pricing-your-listing.mdx), [Market Metrics](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/host/market-metrics.mdx), [Optimize Your Earnings](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/host/optimization-guide.mdx) — in the preview: `/host/pricing-your-listing`, `/host/market-metrics`, `/host/optimization-guide`.

Blocks: CON-1256 sign-off. Detail: CON-1256.

## Input 4. Machine-error platform behavior

**Owner: Backend source owner (Hanran) · CON-1531**

Seven confirmations that set the "how long it persists" copy on [Machine Error Reference](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/host/machine-errors.mdx) (`/host/machine-errors` in the preview):

1. Is the 2026-06-24 error catalog complete for host-visible machine errors?
2. For each error, which field displays it to hosts (`error_msg`, `error_note`, `error_description`, `vm_error_msg`, `vm_error_level`, other)?
3. Which errors appear on the Machines page vs. only in a failed rental/instance detail?
4. For machine-deverifying errors, what clears the error — next clean heartbeat, successful self-test, admin action, time decay?
5. For VM-offer-only errors, what is the approximate clean-report/TTL before VM offers return?
6. Should logged-only rental-attempt messages be public host docs, or internal/support-only?
7. Should the console deep-link docs by raw error string, normalized category, or both?

Blocks: final wording on Machine Error Reference. Detail: CON-1531.

## Input 5. Installer Wizard screenshot

**Owner: Product · Rounds 0/2**

Approve the Host Installer Wizard (TUI) screenshot in [Installing Host Software](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/host/installing-host-software.mdx) (`/host/installing-host-software#host-installer-wizard` in the preview) — or supply a replacement asset.

Blocks: production merge (flagged since 2026-06-17). Detail: CON-1518 Jira attachment `image-20260617-135801.png`.

## Input 6. Supported Hardware sign-off

**Owner: Product · Round 1**

Confirm [Supported Hardware](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/host/supported-hardware.mdx) (`/host/supported-hardware` in the preview): exact GPU-family coverage, OS/cgroup guidance, and alignment of the CPU rule between docs, self-test #6, and vast-cli #413. Related product asks on the radar: payment/tax edge cases (incl. W-8 for non-US hosts) and datacenter requirements wording.

Blocks: CON-1516 sign-off; the highest-prevention doc going live. Detail: CON-1516.

## Input 7. Host Teams engineering answers

**Owner: Engineering · Round 6 · CON-1581**

Five answers that gate publishing [Host Teams](https://github.com/jjziets/docs/blob/CON-1584-host-cli-api-sdk/host/host-teams.mdx) (`/host/host-teams` in the preview):

1. Individual→team migration: what happens to existing machines and accrued earnings?
2. Install-command `undefined` bug in team context — status?
3. What is the exact flow for granting machine-registration rights to a team API key? (Flagged inside the draft page itself.)
4. Are `billing_read`-only roles viable for host teams?
5. Who owns billing/payouts when machines move into a team?

Blocks: Host Teams page publication. Detail: CON-1581.

## Input 8. Persona scope ruling

**Owner: Docs team · Round 5**

Do the generated `host/cli/*` and `host/sdk/*` reference pages need persona chips, or are generated reference pages exempt? All 39 authored pages are tagged and chip-synced (now lint-enforced via `npm run check-persona-chips`); the 33 generated pages are currently exempt by convention.

Blocks: the literal reading of CON-1518's "tag every page"; the only remaining implementation wrinkle. Detail: CON-1518 (2026-06-29 comment).

---

*Non-blocking follow-ups already ticketed elsewhere: `vastai verify-status` / queue-position-by-GPU-tier (product/CLI feature), CLI error-string deep-linking (docs anchors are ready).*
