# Strategy, buying group and top accounts

## Buying group lanes

Each persona in `gtm.json` has a lane (for example finance, tech, ops) and a role:

- **decision_maker** signs.
- **champion** wants it and pushes it inside.
- **influencer** shapes the choice.
- **technical_gatekeeper** can block it on security or systems.

The Account Book shows which lanes have a contact and which do not. A missing lane is a prospecting task, not a reason to skip the account. Pain stays a hypothesis until someone hears it on a call.

## Readiness

| Level | When |
|---|---|
| ready | at least `book.ready_min` (default 2) buyers pass the send gate |
| enrich | there are buyers, but too few pass the gate |
| prospect | no buyers in the book yet |

## Strategy ladder

Each account gets exactly one strategy. The rules run top to bottom, and the first match wins.

| # | Strategy | When |
|---|---|---|
| 0 | your override | `strategy_override` is set. It sticks until you clear it. |
| 1 | hold | the parent company decides (relationship parent_decides) |
| 2 | excluded | the relationship is in `icp.exclude_relationships` (default competitor, customer, partner) |
| 2b | hold | the account is on hold, it is below the ICP size floor, or it is archived |
| 3 | re-engage | the account is tagged `lost_deal`, or someone there is tagged `past_reply` |
| 4 | live | a deal is open (`status` live_deal). The deal owner leads; outbound stays out. |
| 5 | signal | signal-score marked the account playable |
| 6 | priority | the tier is in `book.priority_tiers` (default P1, P2) |
| 7 | automated | nothing stronger matched |

Tier and similar labels only change the sort order; they never move an account above a hold or a live deal.

Excluded, hold and live turn outbound off for everyone at the account: the send gate and the call gate both block them, and an export leaves them out with the reason.

## Sticky top-N

`rank_accounts.py` scores eligible accounts with additive points from `gtm.json` → `ranking`:

- tier points
- readiness points
- one point per send-ready buyer, up to a cap
- one point per lane covered
- a bonus for a tech-lane contact
- points for a playable signal

Accounts whose relationship is in `icp.exclude_relationships`, accounts where the parent decides, and accounts on hold or excluded are never ranked.

The first run freezes the top N in `book/top.json`. Later runs do not reshuffle it. They:

- apply your `overrides.add` and `overrides.remove`
- report **challengers**: accounts outside the list now scoring above the lowest account on it
- list accounts on the list that are no longer eligible, without removing them

Changing the list is your call. Edit the overrides, or rerun with `--reset` to start over on purpose. A list that reshuffles every day never gets worked deeply; a frozen list with a challenger report does.
