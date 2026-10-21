# gtm.json reference

One config file per workspace. icp-define writes it; the other aym-gtm skills read their own section and fall back to their defaults when a section is missing. Every number is an editable default, not a standard.

## Sections and who reads them

| Section | What it holds | Read by |
|---|---|---|
| `seller` | Seller name, the offer in one line, optional `average_contract_value` | icp-define, outreach-draft |
| `icp` | Size band and sweet spot, countries, industries in and out, excluded relationships | icp-define, data-quality, account-book |
| `personas` | Ordered buyer types: id, label, lane, role, title patterns, points | data-quality, account-book |
| `not_buyer_titles`, `review_titles` | Title patterns that quarantine a person, or send them to review when no persona matched | data-quality |
| `region_title_rule` | Region words that mark a title out of region, and senior patterns that are exempt | data-quality |
| `segments` | Industry group plus size range, optional market count with its source and a noise check | icp-define, account-book |
| `market_bands` | Labels for market size estimates | icp-define |
| `scoring.account` | Points for sweet spot, in band, segment match and tier | icp-define, account-book |
| `clean` | Contactability scoring and list rules: phone points, persona multiplier, size points, never-touched bonus, defect and do-not-call penalties, cap per account, stale-touch days, quarantine statuses and tags | data-quality |
| `verify` | Minimum verification score per channel (email, call, LinkedIn) | data-quality |
| `audit` | Days before a sequence counts as overdue or a flag as stale, and which tags are stale flags | data-quality |
| `book` | Source order for merging, minimum people for a ready account, priority tiers, area code to time zone hints | account-book |
| `ranking` | How many accounts the top list holds | account-book |
| `freemail_domains` | Personal email domains. An email here is never treated as a work email | data-quality, account-book |
| `stop_statuses` | Person statuses that block every channel. Must include `do_not_contact` | data-quality, account-book, outreach-draft |
| `dnc_tags` | Opt-out tags: the person asked not to be contacted. They block every channel and set status `do_not_contact` | data-quality, account-book, outreach-draft |
| `left_tags` | Tags that say the person may have left, such as `moved`. They block every channel and suggest status `left`, never `do_not_contact` | data-quality, account-book, outreach-draft |
| `channel_block_tags` | Tags that block one channel only, for example `bounced` blocks email and `dnc_phone` blocks calls | data-quality, account-book |
| `send_gate` | Email-only rules: email status, minimum score, catch-all rule, own-domain rule, countries. Stop statuses and do-not-contact tags apply on top | data-quality, account-book, outreach-draft |
| `signals` | Signal types with weight, how long they stay useful and which seat to contact; recency steps | signal-score |
| `copy` | Word band, question rule, banned items and phrases, proof line limit and age, connection note limit, message angles | outreach-draft |

## Field notes

- `icp.size`: `min <= sweet_min <= sweet_max <= max`, in employees. The check script enforces the order.
- `icp.industries_in`: lowercase names that match the `industry` column. When empty, any industry not in `industries_out` counts as in.
- `icp.exclude_relationships`: any of `competitor`, `customer`, `partner`, `parent_decides`. The example excludes all four.
- `personas[].role`: one of `decision_maker`, `champion`, `influencer`, `technical_gatekeeper`, `user`.
- `personas[].title_patterns`: regular expressions, matched without case. Order matters: the first persona that matches wins.
- `segments[].market_count`: a whole number. It must come with `market_count_source`, or the check fails.
- `segments[].noise_check`: `{"reviewed": 25, "noisy": 3}` lowers the estimate by the noisy share.
- `market_bands`: each band has a `max`; the last band's `max` is `null`.
- `signals.recency`: `[days, factor]` pairs with days going up. A signal 20 days old with `[[30, 1.0], ...]` keeps its full weight.
- `send_gate.min_email_score`: 0 to 100, or `null` to skip the score check.

## Accounts columns

`account_id, name, domain, other_domains, employees, industry, country, tier, relationship, status, owner, crm_id, notes`

- `other_domains`: semicolon list of extra email or web domains.
- `relationship`: blank, `competitor`, `customer`, `partner` or `parent_decides`.
- `status`: `active`, `hold`, `live_deal` or `archived`. Status does not change ICP fit.
- `tier`: free text such as P1, P2, P3. It only adds tier points.

## People columns

`person_id, account_id, first_name, last_name, title, email, email_status, email_score, phone, linkedin_url, country, timezone, status, last_touch_date, sequence, tags, notes, crm_id, source`

- `email_status`: `verified`, `risky`, `catch_all`, `invalid` or `unknown`.
- `status`: `active`, `nurture`, `hold`, `booked`, `not_interested`, `wrong_person`, `left`, `do_not_contact` or `archived`.
- `tags`: semicolon list, for example `opted_out;replied`.
- Dates use `YYYY-MM-DD`.
