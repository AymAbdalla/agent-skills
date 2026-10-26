# Agent records

Three files in `docs/agents/` keep a project's work honest across chats, tools and helpers. They are the only record files the core skills create (house rules). Create them with `python3 <check-this>/scripts/agents_gate.py init`, which never overwrites an existing file.

| File | Who writes it | What it holds |
| --- | --- | --- |
| `build.md` | The builder's main agent only (never a helper, never the checker) | One row per slice it built |
| `checks.md` | An independent checker only (a fresh chat or the other tool, as the house rules' Independent checks define it) | One row per slice per check round |
| `status.md` | Each builder, its own line only | One line per workstream |

Never put a `|` inside a cell: it splits the cell and the gate reads the wrong column.

## build.md

`| Slice | Workstream | Branch | Commit | Acceptance checks | Builder results | State | Date |`

- **Slice:** the slice's number from the plan only, for example `2` (the gate matches on the first word).
- **Commit:** the commit that contains the slice's code.
- **Acceptance checks:** copied from the plan, not invented.
- **Builder results:** starts with `self-check:`, for example `self-check: npm test, 12 pass`.
- **State:** `built`, or `fixed (round N)` after a failed check. Never `checked`, `pass` or `verified`.
- A fix adds a new row; it doesn't edit the old one.

## checks.md

`| Slice | Checked commit | Result | Evidence | Mismatch | Checker | Date |`

- **Slice:** the same number the builder used, for example `2`.
- **Checked commit:** at least 7 characters of the latest code commit when the check ran (`git log -1 --format=%h -- . ':(exclude)docs/agents'`).
- **Result:** `pass` or `fail`.
- **Evidence:** what the checker ran and saw, for example `npm test: 12 pass; walked beach route, energy 80 -> 72`.
- **Mismatch:** where the builder's row disagrees with what the checker saw, or `none`.
- **Checker:** who checked, for example `fresh Claude Code chat` or `Codex`.
- When a batch is checked, record a row for **every** slice on the branch at the current commit, plus one row with the slice `security` for the security pass (`fail` when it found a blocker or a should-fix). A pass recorded for older code no longer counts.
- Commit `checks.md` on its own, with nothing else in that commit, for example `docs(checks): slices 1-3`.

## status.md

`| Workstream | Tool | Branch | Owns | Phase | Next |`

- **Owns:** the files or folders this workstream may change. A new workstream reads this first and never claims files another one owns.
- **Phase / Next:** the phase just finished and the next step, including the line to paste into a new chat.

## The gate

`python3 <check-this>/scripts/agents_gate.py check --base main` reads these files and git history. It refuses a merge when a slice on the branch has no independent pass, a pass is for older code, a commit changed rows in `checks.md` together with other files, a builder row claims more than `built` or `fixed (round N)` with `self-check:` results, or the branch changed code and there is no passing `security` row for the latest code commit. A project with no `docs/agents/build.md` is unaffected. The gate runs on the branch before merging: after a squash merge, `main` keeps the files but not the per-commit history.

What the gate can't catch: a checker that writes `pass` without doing the work, or a builder that writes its own row into `checks.md` in a commit of its own (both use the same git identity, so the history can't tell them apart). The fixed check order and the user's own spot checks guard against that.
