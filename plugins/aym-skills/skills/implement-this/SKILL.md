---
name: implement-this
description: "Use whenever the user asks to build, implement or execute an approved plan, spec or ticket, or to add or fix tests. Editing code directly skips what this skill guarantees, which is slice-by-slice building, a failing test seen before each fix, a check after each slice, and a stop card that keeps done and verified apart. Also covers regression tests and deciding when an edit needs no test. Not for writing the plan, reviewing code, diagnosing an unexplained bug, or committing."
---

# Implement this

Turn an approved plan into working, checked changes, with tests that would catch a real regression. Follow the house rules at `../work-my-way/references/house-rules.md`, resolved from this skill's folder (read it directly; don't search for it).

## Pick the mode and say it first

- **build:** "implement", "build", "execute the plan". Needs an approved plan for substantial work. A small, clear change can go ahead with a one-line plan.
- **tests:** "add tests", "write a regression test", "test this behavior". The same test-first method, without new product behavior.

If there is no approved plan and the work is substantial, say so and route to Plan. Route an unexplained crash or failure to `debug-this`, because a test needs a known expected behavior. Route review, explanation or shipping to the skill that owns it.

## Confirm what is approved

Read the plan, spec or ticket and the current source it touches before editing. Note the agreed behavior, files, acceptance checks and anything the plan rules out. Before each step, compare it with the approved scope. Stop and ask before any step that adds behavior, files, dependencies, data changes or external effects the plan did not cover, or that contradicts it. Describe the step, why it seems needed and the options. Keep going with in-scope slices that don't depend on the answer.

## Each slice: one behavior, red, then green

1. **Decide whether a test belongs.** Name the behavior and who relies on it. Prose, comments, formatting or a rename with no callers needs a lighter check (readback, build, lint, the existing suite), not a manufactured test.
2. **Choose the seam.** Test at the highest public place a caller observes behavior that is fast and reliable: a public function, CLI or HTTP endpoint. Reuse a seam the plan, spec or existing suite already settled; ask only when the seam is an open design choice. Asked to test a private helper? Test the public behavior it serves and explain why. Use the project's existing test runner; a new framework needs the user's approval.
3. **Write the test.** Before the first new test, run one existing test green to prove the test command works. Take the expected value from an independent source: the requirement, a worked example or a known-good literal. Never compute it the way the code does. Read [good tests](references/good-tests.md), and read [mocking](references/mocking.md) before replacing any dependency.
4. **Show red for the right reason.** Run it and see an assertion fail on the missing or wrong behavior. An import error, typo or setup crash is not red. For a brand-new function, add a stub returning a placeholder that differs from every expected value, so the run reaches the assertion. If the behavior already exists, show sensitivity by breaking a copy you saved aside, then restore it and confirm the diff is clean. If no red run is possible, say so and state what the test still proves.
5. **Make the smallest change**, then rerun to green and run the surrounding suite.

**Fix budget.** A slice gets at most 3 tries to reach green, each with a new hypothesis. Then leave the slice open, write the tries, the exact error and the best next idea into the plan, and stop for the user. If the same slice blocks twice, go back to Plan. Never weaken a test to get green; see [good tests](references/good-tests.md).

## Helpers only for independent parts

Use a helper when parts touch separate files with no blockers between them and parallel work saves real time. Give each helper one write surface, and never give two writers the same file. Read [helpers](references/helpers.md) first. You integrate the results, read the combined diff and rerun the checks yourself.

## Finish

Run the plan's acceptance checks and the project's normal test command on the integrated result. Remove temporary scaffolding. Report the changed files, each check with its state, each test with the requirement its expected value came from, deviations from the plan, open decisions, and anything not run or left untested. End with the stop card: next is Check (`check-this`). Commit, push and PR belong to Ship.
