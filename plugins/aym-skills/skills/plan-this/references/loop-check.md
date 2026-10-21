# Loop check

Use this when a plan adds a job that runs on a schedule, repeats on its own, or retries until something passes. A loop that should not exist costs money and attention every time it runs.

## Four questions before building it

Build the loop only when all four answers are yes. Otherwise plan it as a manual step and say why.

1. **Does it repeat often?** About weekly or more. A one-time or rare task is cheaper done by hand.
2. **Can a check fail the work automatically?** A test, a script or a rule that a different agent or program runs. "The agent says it looks good" is not a check.
3. **Can the budget absorb retries?** Name the cap on runs, time and cost per run.
4. **Can it see its own results?** It can read logs, run its code and read the files it changes.

## Build order

1. Do the job once by hand and watch it succeed.
2. Turn the working steps into a skill or script.
3. Wrap that in the loop with its stop rules.
4. Schedule it last.

## What the plan must state

- **Trigger:** what starts each run.
- **Scope:** the files, records or systems each run may change; anything outside them stops the run.
- **State file:** where each run records what it did, so the next run resumes instead of starting over. Include a "do not retry" list for anything that failed in a way a retry cannot fix, and the budget used so far.
- **Stop rules:** a cap on attempts, time and cost, and what happens when one is hit.
- **Progress test:** judge progress by outcomes (fewer failing checks, a changed review state), not activity (a new commit, a reworded query). After a set number of runs with the same outcome, retire that item as needing a person. Cap total runs at about 2 x items + 10 to catch loops that bounce back and forth. Each run ends as done, stuck (with each item's reason) or paused.
- **The check and who owns it:** the gate is objective and is not judged by the agent that did the work.
- **Human approval:** anything that cannot be undone (sending, publishing, pushing, paying, deleting) waits for a person.
- **How to judge it:** the share of runs whose changes were accepted. When fewer than about half are accepted, fix the loop or turn it off.
