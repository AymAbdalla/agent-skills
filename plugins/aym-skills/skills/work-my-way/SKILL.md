---
name: work-my-way
description: "Use first whenever the user describes work to do or wants to think it through (an idea to scope, a feature to add, or something to fix, plan, check, ship, pause or resume), even when no skill is named. Doing it by hand skips the user's required workflow, which is to check the project's records before asking, ask consequential questions one at a time, route each phase to the right skill (aym-lab for skill building and dissections), and stop after every phase with a status card. Not for a plain factual question or a request that names another skill."
---

# Work my way

The user describes the result. You pick the phase, run it with the right skill, and stop. They should never need to remember a skill name.

First read [house rules](references/house-rules.md). They apply to every phase: authority, the stop card, working-tree and secret safety, result states, and actions that need their own yes.

## Route

| The user says… | Phase | Skill (mode) |
| --- | --- | --- |
| a vague idea, "clarify", "scope", "think through" | Clarify | this skill (below) |
| "write the spec", "plan it", "review this plan" | Plan | `plan-this` (spec / plan / review) |
| "build it", "implement the plan", "add tests" | Build | `implement-this` (build / tests) |
| "it's broken", "failing", "flaky", "slow" | Debug | `debug-this` |
| "check it", "review this PR", "is it really done", "QA the page", "simplify" | Check | `check-this` (review / verify / qa / simplify) |
| "commit", "push", "open a PR" | Ship | `ship-this` |
| "pause", "hand off", "resume", "pick up where we left off" | Continue | `handoff-this` |
| "build a skill", "make a plugin", "change this skill", "turn this into a skill" | Build (skills) | `build-skill` (aym-lab), always, even inside a larger job |
| "dissect this", "how is this built", "what can we learn" | Study | `dissect-this` (aym-lab), which saves what it learns to the library |

Skill and plugin work always goes through `build-skill`, so every new or changed skill starts from the mechanics library (when one is set up) and leaves a design record. A typo or wording-only fix in a skill is small work under Size the job: edit it and run the structure check. When studies are needed first, `dissect-this` saves them to the library before `build-skill` reads it.

If the aym-lab plugin is not installed (no `build-skill` or `dissect-this` skill is available), say so once and do the work without it. For skill work, read the skill's current files, make the agreed change, and check that `SKILL.md` starts with a `name` and a `description` and that every linked file exists. For a study, read the source and explain it in chat or in the project's docs. Installing aym-lab adds the library lookup, the structure checker and design records.

When the request names no phase, start at the earliest one that is not settled yet. A raw idea starts at Clarify. A settled spec starts at Plan. An approved plan starts at Build. Finished work starts at Check. Read the chosen skill's current instructions before running it, and pass it the goal, the agreed decisions, the inputs, the destination and the limits of authorization.

## Size the job

- **Small and clear:** a typo, a rename with no callers, a one-line fix with an obvious check. Do it, run the check, and end with one card. No interview, no plan document.
- **Substantial:** follow the phases in order (Clarify → Plan → Build → Check → Ship) and stop after each. Build needs an approved plan. Approval covers the plan's scope; a material change needs the user's decision again.
- **Research, writing or review:** run that job, verify it by its own standard, and stop.

For multi-session work, a substantial handoff or a review of settled changes, read the [task contract](references/task-contract.md) and carry its fields in the project's existing documents.

## Clarify

1. Read the request, the conversation and the project's decision records: specs, plans, decision logs, glossaries, README and `docs/`. Name the paths you checked. Treat each recorded answer as settled, with its source. If the new request contradicts one, quote both sides and ask about that one conflict.
2. Sort each unknown into a group:
   - **Checkable fact.** Look it up and cite the source. Never ask the user for a fact you can check.
   - **Consequential choice.** It changes visible behavior, scope, data handling, cost, or something hard to undo. These go to the user. Two choices always count when the request leaves them open: which items a feature covers (when the request, the docs and the code describe the set differently), and the format of output other people or systems will consume.
   - **Minor detail.** Any reasonable answer works and it is cheap to change later. Pick a default and state it.
3. Ask the consequential choices one at a time, most consequential first, as the house rules say. For each, give the options, what each changes, and your recommendation with its reason. Hold a choice that depends on an unanswered one. List the remaining questions in the report so the user sees what is still coming. Read [clarify.md](references/clarify.md) for the question test, approach comparison and terms.
4. Report the settlement: settled answers and facts with their sources, agreed terms, the defaults you chose, and open questions with what each blocks. Then show the stop card with Plan as the next phase.

Clarify does not write the spec, plan or code, even when the same message asks. It names that next phase on the card.

## Finish

When the last phase ends, report what changed, the evidence from each check with its state, the limits, the remaining work, and where the records live. Completion never authorizes shipping or automatic learning. If the user pauses or changes direction, keep the useful decisions and next action in the owning document. On resume, inspect the current state before relying on the record.
