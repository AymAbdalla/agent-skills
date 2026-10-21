# Evidence rules

## Match the scope

Evidence supports a claim only at its own scope. Compare these dimensions:

| Claim says | Evidence must cover | Common mismatch |
| --- | --- | --- |
| "All tests pass" | The full suite the project defines | One test file, or a filtered run |
| "Fixed the bug" | The original symptom rechecked after the change | A new test that passes but never failed before |
| "Works on both hosts" | A run on each host | One host's run |
| "Only X changed" | `git status` and `git diff` for the whole tree, including untracked files | A diff of one file |
| "Lint and types clean" | Each tool's own run | A test run, which checks neither |
| "Requirement R met" | An observed input and result for R; reading the code path line by line counts only as "verified by reading" | Tests passing in general |

When the evidence is narrower, mark the claim partly verified and say what is missing. When any observed evidence contradicts the claim, mark it contradicted instead, even if other parts held.

## Fresh or stale

Evidence from earlier counts only when nothing relevant changed since it was produced. Compare the commit, file hashes or modification times of the files the check covers. If the code changed, or you cannot tell, rerun the check or mark the claim unverified with the reason "evidence predates changes".

## Kinds of failure

Report which kind occurred; none of them is a pass.

- **Behavior failure:** the check ran and the code gave the wrong result, such as an assertion error showing 81 where 80 was expected. The claim is contradicted.
- **Environment or tool failure:** the check could not judge the behavior, such as a missing module, a missing command, no network, a timeout or a crash in the test runner. The claim is unverified.
- **Not run:** nobody ran the check, or the report gives no command or output. The claim is unverified.

A check that exits 0 but collected zero tests, or skipped the relevant tests, has not verified anything. Read the output, not only the exit code.

## Can the check fail?

A quiet result proves something only if the check could have failed. Before you trust one:

- Ask what the check would show if the code were broken. When it is cheap, prove it fires on a known-bad case.
- Read the real exit code of the command itself, not of a pipe after it (`cmd | tail` reports the exit code of `tail`).
- Check the counts: 0 tests run, skipped files, 0 rows read or written.
- Never trust a server, watcher or process that another session started. Start your own or mark the claim unverified.

## Helper and agent reports

Treat "done", "all passing" or "updated three files" from any agent as a claim. Check it against:

- `git --no-optional-locks status --porcelain` and `git diff` for changed files, plus untracked files;
- the actual contents of the files the report names;
- a fresh run of any check the report says passed, when safe.

Record where the report and the files disagree.

## Safe commands

Prefer commands that read state: `git --no-optional-locks status`, `git diff`, `git log`, reading files, and the project's existing test or lint commands in a non-fixing mode.

Read a script before you run it, in a separate step. Run it only if it writes nowhere except ignored build or cache paths and the system temporary directory, and uses no network, installation, deployment, migration or credentials. Otherwise do not run it: mark the claim unverified and give the user the command.

Do not install packages, fetch remotes, change configuration or edit files to make a check runnable. If a check needs something missing, record the missing piece and mark the claim unverified. Compare the porcelain status before and after any check, and report any file it changed.

## Report format

```text
Claim audit for <what was claimed> at <commit or state>

| # | Claim | Status | Evidence | Note |
| 1 | ... | verified / partly verified / contradicted / unverified | command + exit code + key output, or path:line | scope or gap |

Requirements without a claim or evidence: <list | none>
Commands run: <list>
Could not check: <item: reason>
```
