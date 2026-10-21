# Opener tests, angle tests and the quota model

## Write the test down first

A test lives in `funnel/tests.json` before any result comes in:

```json
{
  "tests": [
    {
      "id": "opener-oct",
      "kind": "opener",
      "hypothesis": "Opener B turns more connects into conversations than A or C.",
      "variable": "opener",
      "arms": ["A", "B", "C"],
      "metric": "conversations per connect",
      "min_per_arm": 20,
      "registered": "2026-09-18",
      "start": "2026-09-21",
      "script_changes": {"C": "2026-10-05"}
    }
  ]
}
```

| Field | Rule |
|---|---|
| `kind` | `opener` (cold calls; the unit is a connect, the win is a conversation) or `angle` (first-touch emails; the unit is a person's first touch, the win is that person replying later). |
| `variable` | Exactly one thing changes between arms. A list with more than one entry makes the test exploratory: no arm can be credited. |
| `registered` | The date the test was written down. After `start` means the result is exploratory. |
| `min_per_arm` | Defaults: 20 connects per opener arm, 30 first touches per angle arm. |
| `script_changes` | When an arm's script changes, its count restarts from that date. |

## Who gets which arm

Each person's arm comes from a stable hash: SHA-256 of `"<test id>:<person_id>"`, as a number, modulo the number of arms. The same person always lands in the same arm, and two tests split people independently.

The caller logs the arm used in the `opener` column (calls) or `angle` column (emails). A row whose logged arm differs from the person's assigned arm is reported apart and not counted. A person routed to a different opener because of fit is a real choice, but it is not part of the test.

## Reading a test

- **Next up**: the arm with the fewest units. Work that arm first to keep the arms even.
- **Leader**: named only when every arm has the minimum. Before that the verdict is "running".
- **Clear**: the leader's 95% range does not overlap any other arm's. A leader by point estimate only says so.
- **Angles**: after the minimum, keep the leader. A trailing angle is rewritten once; if it trails again after the rewrite (its count restarted), cut it.
- Credit an arm only when nothing else changed for that arm during the test. Log other changes in `funnel/changes.csv`.

## Quota model

`funnel/targets.json`:

```json
{"period_days": 30, "meetings_commit": 24, "meetings_stretch": 30, "work_days": 22}
```

The model works backwards from the meeting target:

- people to touch = target / measured meeting rate, rounded up
- range = target / upper end of the rate's 95% range, to target / lower end (no upper bound when the lower end is 0)
- per work day = people to touch / `work_days`

When the meeting rate is not measured (too few people, or no meetings yet), the quota is marked unknown. Do not plan from a guess; gather more data first.

Levers are ranked by meetings per hour for each channel: (booked rows on the channel / touches on the channel) x 60 / minutes per touch. Minutes per touch come from `funnel.minutes_per_touch` and are your own estimates. A channel with too few touches is listed last and labeled.

Show both numbers: commit is what you will hit; stretch is what you aim for.
