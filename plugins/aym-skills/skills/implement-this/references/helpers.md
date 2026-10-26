# Helpers for independent parts

Read this before handing any implementation work to a subagent or other worker.

## Decide whether to delegate

Delegate when two or more parts touch separate files, have no blockers between them, and each takes long enough that running them in parallel saves real time. Work directly when parts share a file, a schema, a migration or a central config, or when one part's design depends on another's result. Delegation adds briefing, waiting and integration work; it is not a default.

List the parts and their blockers. Start only the parts whose blockers are done. A part that depends on another waits for the integrated result, not for a helper's claim.

## Write each brief

Each brief contains:

- the goal of this part and the relevant plan section
- the exact files or directories the helper may write, and the files it may only read
- files it must not touch, including the other helpers' surfaces
- the checks to run and the result that counts as done
- the authorization limits: no commit, push, install, dependency change, permission bypass or external action, and no writes to `docs/agents/` (the main agent keeps the records)
- what to return: changed files, check output, and anything it could not do
- the standing line "stop and report if this is impossible"

Mark how you know each fact in the brief. Write "verified (command you ran)" or "belief, check it". Write a negative as a search result ("searched for X in Y, found none") rather than "there is no X". Never size a work list from a search that was cut off or truncated. Give a reviewing helper the work and the requirements, not the builder's claims about it.

Use the helper model the user or the project's instructions name; with none named, use the host's default. Record the choice in the final summary. Cheaper models skip "stop and ask" steps more often, so give them parts whose decisions are already settled.

## One writer per surface

A surface is a file, or a set of files that must change together. Assign each surface to exactly one writer for the duration of the work: you or one helper. If a helper finds it needs another surface, it stops and reports instead of editing. If two parts need the same file, do them in sequence or keep that file yourself.

## Integrate

After helpers return:

1. Read each changed file. Compare the changes with the brief and the plan.
2. Check that no file outside the assigned surfaces changed (for example `git status` and `git diff --stat`).
3. Resolve conflicts yourself, then run the full relevant checks on the combined state.
4. Treat a helper's "all tests pass" as a claim. Your own run on the integrated state is the evidence.

If a helper went outside scope, revert or discuss that part before continuing. Report helper use, including model and surface, in the final summary.
