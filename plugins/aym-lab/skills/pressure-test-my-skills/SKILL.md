---
name: pressure-test-my-skills
description: Pressure-test one existing agent skill directory. Designs a frozen case set (normal, ambiguous, failure, unavailable-tool, inappropriate-trigger) with evaluator-held expected facts, runs fresh worker sessions within a stated allowance, grades the files and traces they leave, and writes a reproducible results record. Use when the user asks to pressure-test, stress-test, evaluate or find failures in a named skill. Do not use to build or fix a skill, fix ordinary code, or judge writing style.
---

# Pressure-test my skills

Find out what one skill actually does under realistic pressure, and leave a record another person can re-check. This skill reports findings. It does not edit the target, install it, publish results, or supply tools the environment lacks.

## 1. Set the target and limits

Confirm four things before any run:

- **Target**: one directory containing `SKILL.md`. Read `SKILL.md` and every file it links. Record the tree hash with `python3 scripts/grade_cases.py hash-target <target>` (path relative to this skill's directory).
- **Intended job**: what the skill should produce, where, and which nearby requests it should decline. Take this from the skill's description and the user's words. When the skill text contradicts itself or the user, record that as a finding before any run.
- **Allowance**: the number of fresh worker runs in total and per host. If the user gave none, propose a small one and wait. Failed, errored and retried runs all count.
- **Destination**: where `cases.json`, `runs.json`, `results.json` and `results.md` go. Use the location the user named, otherwise the owning project's evidence or scratch location under its policy.

A request to build, revise or repair the skill belongs to the building workflow, not here. Writing quality, tone and taste are out of scope; test contract facts.

## 2. Design and freeze the case set

Read [case design](references/case-design.md). Write one case per kind unless the user narrows the set: normal, ambiguous, failure, unavailable-tool and inappropriate-trigger. Each case has a worker prompt, the input files the worker gets, and expected facts written as checks on artifacts. Derive expected facts from the intended job, not from what the skill happens to do.

Save `cases.json` in the destination, outside every worker fixture. Then record its hash with `python3 scripts/grade_cases.py hash-file <cases.json>` into `runs.json` as `cases_sha256`. From this point the case set is frozen. If a case turns out wrong after a run has used it, do not edit it. Grade the record as it stands, note the problem in `results.md`, and start a new record in a fresh destination for the corrected set. Any change to `cases.json` after freezing keeps that record's verdict from `pass`.

## 3. Check availability before running

For each host you plan to use (native subagent, `claude -p`, `codex exec`), confirm it can start. For each command a case needs, run `command -v <name>`. When something is missing, record those runs as `unavailable` with the reason. Never create a stand-in script, mock binary or fake output to fill the gap, and never count an unavailable run as a correct decline.

If a blocker stops the protocol itself, for example no working shell to hash, freeze or grade, still write `results.md` in the destination. Give the verdict `incomplete`, list what you read and what ran, quote the exact error, and name what the user must change. Do not compute hashes or grades by hand.

## 4. Run fresh workers within the allowance

Read [running and grading](references/running-and-grading.md). Give each run its own fixture directory and a fresh context with no access to `cases.json`. Expose the target the way the case needs: named path for explicit use, or fixture `.claude/skills/` and `.agents/skills/` links for catalog routing. Add the attempt to `runs.json` before you look at its output. When a case lists `requires_commands`, have the worker report `command -v` for each one and store the missing names in that run's `missing_commands`. Keep the target unchanged during the runs. Stop at the allowance even when coverage is incomplete.

## 5. Grade artifacts

Run `python3 scripts/grade_cases.py grade --cases <cases.json> --runs <runs.json> --out <results.json>`. Then open the actual files the checks name and confirm the grader saw what you see. A worker's claim of success is not evidence; the file, its location, its contents and the trace are. Statuses mean:

- `pass`: the run completed and every check held.
- `fail`: the run completed and at least one check did not hold.
- `error`: the worker crashed, timed out or exited non-zero.
- `unavailable`: a host, tool, fixture or trace needed for grading was missing.
- `not_run`: the case had no attempt, for example after the allowance ran out.

## 6. Report reproducible findings

For each failing check, write a finding with the case id, the check, the artifact path, the failing run ids and the command that re-grades it. Call a finding reproduced only when runs in two or more separate fixtures failed the same check; one failing run is "observed once". Write `results.md` with the target path and hash, hosts and models, allowance used, a case table, findings, unavailable coverage, protocol errors and limits.

The verdict is `pass` only when every planned case ran and passed with no protocol error. Report `fail` when any case failed and `incomplete` otherwise. A pass covers these cases on these hosts; it does not establish general reliability, routing on hosts that did not run, or filesystem containment.
