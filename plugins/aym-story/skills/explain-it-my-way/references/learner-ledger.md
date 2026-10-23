# Learner ledger

One small file that remembers what the learner has been shown and what they have proved they know, so explanations skip what is already solid and retests start from what was missed. explain-it-my-way and test-my-knowledge share it.

## Where it lives

Use a path the user names. Otherwise use `personal/learning/ledger.md` in the outputs folder named in the user's instructions (CLAUDE.md or AGENTS.md), or in `~/agent-outputs/` when none is named.

If that location cannot be reached from this session (for example, a cloud session that is not linked to the user's computer), skip tracking and say so in one line. Never start a second ledger somewhere else.

## When it updates

Tracking what the learner has learned is the point of these skills, so they update the ledger automatically, without asking first:

- After each explanation, explain-it-my-way records the main terms it taught as `shown`.
- When the user explains a concept back in their own words, it records `passed` only if they got all of it right. A wrong or half-right answer is `missed`, with the missing part in the note, so the next quiz brings it back.
- After the user shares quiz results, test-my-knowledge records each objective's concept as `passed` only when every main question on that objective was answered right (reserve retest questions don't count toward it). Anything less, including half right, is `missed`.
- When the user asks not to be taught or quizzed on something, record it as `declined`.

The user can say "don't track" for a session or a topic. Then leave the ledger alone for it.

## How to write it

Always go through the helper script in the skill's `scripts/` folder:

```sh
python3 <skill-dir>/scripts/ledger.py show --ledger <path> --json
python3 <skill-dir>/scripts/ledger.py record --ledger <path> --status <status> --source "<source>" [--note "<short note>"] "<concept>" ["<concept>" ...]
```

`show` reads the rows. `record` creates the file and its folders if needed, applies the rules below, and prints JSON with `added`, `changed` (each with `from` and `to`) and `unchanged`. List the added and changed rows in the report in one line, for example: "Ledger: added retry, send gate; idempotency key shown -> passed."

If the script cannot run (no Python), follow the same rules by hand and say so in the report.

If the script exits with code 2 and prints `ledger.py: error`, the input or the ledger file is wrong (for example a malformed table or an unknown status). Do not edit or rewrite the ledger to make it pass, and do not record by hand. Quote the error, name the ledger path, and tell the user what to fix. Exit code 1 means the file could not be read or written: report it and continue without the ledger.

## Keep it clean

- Record only the main concepts taught: the terms from the industry words section, at most about five per explanation. Not every word that came up.
- Use the short plain name the user would recognize. The script stores new names in lowercase and treats "Idempotency keys" and "idempotency key" as the same concept.
- Notes are optional and short; the script cuts them at 120 characters. No private project details or credentials.

## Format

```markdown
# Learner ledger

| Concept | Status | Date | Source | Note |
| --- | --- | --- | --- | --- |
| retry | passed | 2026-10-20 | quiz: save-flow/quiz.json, obj-2 | got the scenario right both times |
| idempotency key | shown | 2026-10-18 | explanation: save flow | |
| send gate | missed | 2026-10-20 | quiz: gtm/quiz.json, obj-3 | mixed up catch-all and risky |
```

- **Status**:
  - `shown`: explained, not yet tested.
  - `missed`: any main quiz question on it was answered wrong, or the user's own explanation was wrong or only partly right.
  - `passed`: the user answered every main quiz question on it correctly, or explained all of it correctly in their own words.
  - `declined`: the user asked not to be taught or quizzed on it.
- **Date**: the day of the evidence, `YYYY-MM-DD`. The script uses today unless `--date` is given.
- **Source**: `explanation: <topic>` for `shown`; `quiz: <quiz path>, <objective id>` or `said: <what the user said, short>` for `passed` and `missed`; `user: <their request>` for `declined`.

## Rules (the script enforces them)

- **One row per concept.** Case, extra spaces and a simple trailing "s" do not make a new concept.
- **Only the learner's own evidence marks `passed` or `missed`.** The source must start with `quiz:` or `said:`. A project that uses a tool does not prove the learner understands it.
- **An explanation only adds.** `shown` adds a row for a new concept and never changes an existing row.
- **Newer evidence wins.** A quiz result or the user's own explanation changes the row's status, date and source (and the note, if one is given). Nothing else in the row changes. Older evidence never replaces newer evidence.
- **Never delete a row.** Every other line of the file stays exactly as it was, including rows and text the user wrote by hand.
