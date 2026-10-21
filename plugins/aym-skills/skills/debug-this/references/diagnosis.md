# Diagnosis guide

Read this when building the reproduction command, and before handling a flaky or slow symptom.

## Ways to build a reproduction

Pick the cheapest option that reaches the failing code path.

| Situation | Reproduction |
| --- | --- |
| The failing function or command is known | A short script or test that calls it with the reported input and asserts the expected result; or the CLI with a fixture input, compared with the expected output |
| The symptom appears through a service | A request against a local server; or a captured request, payload or event log replayed through the code path |
| The code needs other services to run | A small harness that starts one component and fakes its external dependencies |
| The result is "sometimes wrong" | A loop over many generated or seeded inputs that counts failures |
| It worked before | A script that checks one commit, version or data snapshot, used to bisect between a good and a bad state (in a separate worktree); or the same input through both versions, diffing outputs |
| A person must perform a step | A guided script that prints each step and records the result, as a last resort |

A good reproduction command fails on the user's exact symptom, gives the same verdict each run, finishes in seconds and runs without supervision. Make it faster, sharper and more deterministic before moving on: narrow scope, assert the exact wrong value, pin time and random seeds, isolate files and network.

## Flaky and nondeterministic symptoms

Aim for a measurable reproduction rate, not a single clean run. Run the trigger many times (for example 100 or 1000), in parallel when safe, and record failures out of runs. Raise the rate by pinning or varying the seed, adding load, narrowing timing windows or controlling ordering. Report the method, the observed rate before and after any change, and the remaining uncertainty: "0 failures in 1000 runs after the fix, 37 in 1000 before" supports a fix; it does not prove the rate is zero. If you cannot raise the rate high enough to test hypotheses, stop and report the rate and what would help.

Do not "fix" flakiness with retries or longer sleeps unless the user accepts that as a mitigation; label it a mitigation, not a cause.

## Slow and performance symptoms

Measure first. Record a baseline with a timing harness, profiler or query plan on a stated input size and machine. Change one thing, measure again with the same harness, and report both numbers. Logs rarely locate a slowdown; a profile or bisection usually does. Treat small differences within run-to-run noise as inconclusive and say so.

## Broken AI agent runs

When an agent run fails or loops, sort the failure before changing any prompt. Put it in one bucket:

| Bucket | What went wrong |
| --- | --- |
| Tool choice | The agent picked the wrong tool, or none |
| Tool arguments | The right tool got wrong or missing inputs |
| Tool execution | The tool itself failed, timed out or returned an error |
| State | The agent worked from stale, missing or wrong state (files, memory, earlier results) |
| Retry loop | The agent kept retrying without new information |

For a loop, name its shape: the same call repeated, two calls bouncing back and forth, or retries without progress. The bucket and shape point to the fix; a prompt change fits only some of them.

## Can the check fail?

A quiet result proves something only if the check could have failed. Ask what it would show if the code were broken, and prove it fires on a known-bad case when that is cheap. Read the command's own exit code, not one through a pipe. Check the counts (0 tests run, skipped files, 0 rows). Never trust a server or process another session started.

## Instrumentation

Each probe answers one hypothesis. Prefer a debugger or REPL inspection, then targeted logs at the boundary that separates two hypotheses. Tag every temporary log with a unique prefix such as `[DBG-7c1e]` so one search finds and removes them. Do not log whole requests, environments or config objects; they carry secrets.

## The regression check

Turn the minimised reproduction into a test at a seam that exercises the real failing pattern. For a new function, stub it with a placeholder return so the first red comes from the assertion. When no reachable seam can reproduce the pattern (for example, the bug needs two callers but tests can only drive one), report that gap instead of adding a test that gives false confidence. After the fix, rerun both the regression test and the original unminimised reproduction.

## Sibling sweep

After the cause is confirmed, turn it into a search pattern (the call, the shape of the bad input, the copied block) and search the codebase. Label each look-alike: **exposed** (same bug), **protected** (something guards it) or **unknown**, each with the file:line and the reason for its label. Report the list. Fix only the reported case unless the user asks to fix the others.

## Stop report

When stopping without a confirmed cause, report:

- the symptom as stated, and whether it reproduced
- every command tried, with redacted output
- hypotheses tested and what each result ruled out
- what is missing: environment access, a captured artifact, versions, steps, permission for instrumentation, or a decision
- the smallest next step that would unblock diagnosis
