# Coverage and report format

## Find the base

Use the base the user names. Otherwise try, in order: the PR's base branch, then the repository's default branch (`origin/HEAD`, `main` or `master`). Use the current branch's upstream only when it tracks a different branch. An upstream with the same name holds the pushed copy of this work, so using it as the base would hide every pushed commit. Find the fork point with `git merge-base <base> HEAD`. If no base exists (a new repository, a detached state without a branch), review the uncommitted changes and the files the user named, and record that the committed range is unavailable.

## Collect the four categories

Run these read-only commands from the repository root:

| Category | Command | What to record |
| --- | --- | --- |
| Committed | `git log --oneline <merge-base>..HEAD` and `git diff <merge-base>...HEAD --stat` | Commit list and changed files |
| Staged | `git diff --cached --stat` | Files in the index |
| Unstaged | `git diff --stat` | Modified tracked files not yet staged |
| Untracked | `git ls-files --others --exclude-standard` | New files that Git does not ignore |

`git --no-optional-locks status --porcelain` gives a quick cross-check without refreshing the index. Read the full diff for each category (`git diff <merge-base>...HEAD`, `git diff --cached`, `git diff`) and read untracked files directly, because no diff shows their content.

A file can appear in more than one category, such as a committed file with further unstaged edits. Review the newest content and say which categories it came from.

An untracked file counts as relevant when the changed code imports, calls, configures or documents it, or when it sits in the changed area. Name untracked files you skip and why. Never skip a file only because it is uncommitted.

Do not run `git stash`, `git add`, `git commit`, `git checkout`, `git restore`, `git reset`, `git clean` or any command that rewrites the index, the working tree or refs. Fetching from a remote also changes local refs; skip it unless the user asks.

Untracked files can hold secrets, such as a `.env` file that is not ignored. Name such a file and its risk in the report without quoting its values.

If a command cannot run (no shell, no Git, a sandbox refusal), use what the host already shows, such as a status snapshot it supplied at session start, and say so. Mark each category you could not collect as a coverage gap rather than empty.

## Test changes

When the change touches test files, coverage settings or test configuration, scan that diff for checks that got weaker:

- an assertion loosened or removed, or a tolerance widened;
- a new skip, only, xfail or similar marker;
- a test case deleted or renamed away;
- the code under test newly mocked or stubbed;
- a coverage or quality threshold lowered.

Each such change needs a reason tied to a requirement. Without one, report it as a finding, because a weaker test can turn a real failure green.

## Comments from other reviewers

For each comment from a bot or a person, record two separate things:

- **Truth:** true, false, uncertain, or stale (it describes code that the current head no longer has).
- **Action:** fix, defer or ignore. A defer names where it goes. An uncertain names the test or check that would settle it.

Never repeat a comment as your own finding until you have checked it against the code.

## Helper review receipts

When a helper wrote the review, check its receipt before you use it:

- the reviewed commit;
- a files-read list that equals the changed files;
- a file:line, or "N/A" with a reason, for each review area;
- each requirement tied to a line.

A gap means the review runs again. Never fill in the receipt yourself. If the review cannot run again (the helper is unavailable or the budget is spent), report each uncovered area as not reviewed; never count it as clean. After fixes, review only the range from the old reviewed commit to the new one, and put anything about older code in a separate out-of-range note so settled code is not reopened.

## Report format

```text
Review of <repository> at <HEAD short SHA> on <branch>
Reviewer: <independent helper | self-review by the author session>

Reviewed state
- Base: <ref> (merge base <SHA>) | unavailable: <reason>
- Committed: <n commits>: <files>
- Staged: <files | none>
- Unstaged: <files | none>
- Untracked included: <files | none>
- Excluded: <file: reason | none>
- Commands run: <list>

Intent source: <path or quoted request> | unavailable

Requirements track
| Requirement | Status | Evidence |
| R1 ... | met / partly met / missing / not checkable | file:line or input -> result |

Standards track
| Severity | Location | Finding | Evidence | Confirmed? |

Security (see security-review.md)
| Severity | Location | Finding | Evidence | Fix |
or: Security: no findings. Covered: <checklist items>. Ran: <commands>.

Coverage gaps
- <what was not reviewed or could not run, and its effect>
```

Keep each finding short and specific. Write "none found" for an empty track rather than leaving it out, and say what that track covered.

## Independence

An independent review comes from a session or helper that did not write the change. When the host offers a fresh helper, give it the intent, the reviewed-state list and this format, and keep the main session as integrator. When no helper is available, the author's review is self-review and the report says so.

## Applying fixes on request

Only when the user asks in the same task: list the findings you will fix, edit only those locations, rerun the checks that cover them and report the before and after. Leave unaccepted findings as report items.
