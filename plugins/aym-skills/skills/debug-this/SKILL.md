---
name: debug-this
description: Diagnose a reported defect by reproducing the exact symptom, tracing and testing its cause, and rechecking the original case after any fix. Covers wrong output, crashes, flaky and slow behavior. Use when the user says something is broken, failing, throwing, flaky or slow, or asks to debug or diagnose it. Do not use to add features, refactor working code, or commit, push or ship a fix.
---

# Debug this

Find out why the reported symptom happens, with evidence, and fix it when asked. Follow the house rules at `../work-my-way/references/house-rules.md`, resolved from this skill's folder (read it directly; don't search for it). Their secret-redaction and working-tree rules matter most here: redact every log, command and capture you show, and use a copy or a separate worktree for baselines and bisection.

If the request is a new feature, a refactor of working code, or shipping a fix, decline it under this skill and name the skill that owns it.

## Reproduce the exact symptom first

Write down the symptom: the input, the observed result and the expected result. Build one command that drives the real code path and checks that exact symptom, then run it and watch it fail on the symptom before acting on any theory. A command that only proves "it didn't crash" doesn't count when the symptom is a wrong value. If it reproduces a different failure, keep working on the reproduction, because a different bug leads to the wrong fix. Read [diagnosis](references/diagnosis.md) for ways to build the command and for the flaky and slow branches.

If you can't reproduce it, stop. Report what you tried and ask for what's missing: access to the failing environment, a redacted log or captured input, exact versions or steps, or permission for temporary instrumentation. Don't guess a fix.

## Trace and test the cause

Shrink the reproduction until every remaining part matters. Read the error and the code along the failing path, check recent changes, and compare with a case that works. If the cause is visible on the failing line, state that one hypothesis and its prediction. Otherwise list two to five falsifiable hypotheses, each with a prediction ("if X is the cause, changing Y makes the symptom disappear"). Test them one variable at a time, tagging temporary logs with a unique prefix. For a broken AI agent run, sort the failure into its bucket first (see the diagnosis guide).

After three failed hypothesis tests without new evidence, stop. Report what each test ruled out and ask before widening the search. Escalate when the next step needs access, production changes or a decision you don't have.

## Fix and recheck, when asked

For a diagnosis-only request, report the cause and a proposed fix, then stop. If a fix is requested and the cause is shown:

1. Write a regression test first, using the test-first method in `implement-this`, at a seam that exercises the real failing pattern. Watch it fail on the symptom's assertion, not on a missing name.
2. Apply the smallest fix, then watch the test pass.
3. Rerun the original, unminimised reproduction and the project's tests.
4. Sweep for siblings: search for the same pattern elsewhere and label each look-alike exposed, protected or unknown (see [diagnosis](references/diagnosis.md)).

Propose, rather than add, behavior the requirement doesn't cover. Don't hide the cause with retries, sleeps or broad exception handling unless the user accepts that as a labelled mitigation.

## Finish

Remove tagged instrumentation and throwaway files. Report the symptom, the reproduction command and its redacted before and after output, the confirmed cause and its evidence, the fix and tests, and what remains uncertain. End with the stop card: after a diagnosis, next is "fix it?"; after a fix, next is Check (`check-this`).
