# Handoff record template

These headings are the field groups of the work-my-way task contract (`skills/work-my-way/references/task-contract.md` in the aym-skills collection), plus its pause fields: completed results and next action. That file is the authority. This copy exists so handoff-this works when installed alone; if the two differ, follow the task contract and report the difference.

Add the record as a dated section in the owning document. Keep earlier handoff sections; do not overwrite them. Leave out fields with nothing useful to say, and keep each one short. Use repository-relative paths for tracked files. Label absolute machine-local paths as machine-local.

```markdown
## Handoff: <short title> (<YYYY-MM-DD>)

Status: paused | blocked | ready for review | complete

### Result and scope
- Goal: <requested behavior or deliverable, in one or two lines>
- Acceptance: <observable conditions>
- Excluded: <explicit exclusions>

### Decisions and authorization
- <decision> (user, <date>, covers <scope>) | (my inference)
- Approved: <what was approved, by whom, when, and its scope>
- Needs separate authorization: <commit, push, install, publish, other>
- Open decisions: <question for the user and why it matters>

### Inputs and method
- Rules read: <project rule files>
- Sources: <paths or revisions that matter, and what matters in each>
- Runtime facts: <fact> (checked <date> with `<command that re-checks it>`)
- Method or specialist: <skill or approach in use>

### Destination and ownership
- Repository: <path or name>  Branch: <branch>  HEAD: <full or short sha>
- Committed work: <commit range and one line on what it contains>
- Dirty state: <each staged, unstaged and untracked path that matters, a one-line summary of its change, and whether it belongs to this task>
- Outputs: <paths written or to be written>; writer: <one owner per edit surface>

### Checks and evidence
- Completed: <result> -> <evidence path or check that shows it>
- <command> -> pass | fail | error | not run (<date>; what it covered)
- Defect (if any): symptom <...>; reproduction <...>; check that tells the intended failure apart from setup errors <...>
- Review: <who reviewed what, or "not reviewed">
- Known environment limits: <missing tools, access, sandbox limits>

### Next action
- <the single next step, its file paths, and the check that will show it worked>
```

Mark where each claim came from: **checked this session** (you ran or read it now) or **inherited** (copied from an earlier note without checking). Give each environment fact a date and the command that re-checks it. Write facts the next session can verify. Prefer "tests/test_x.py fails 1 of 4: expected 3, got 2" over "tests are mostly passing". A status marker such as "approved" without who, when and scope is not approval.

On resume, compare at least: branch, HEAD, dirty paths, the files named in "Next action" and any check marked pass that the next step relies on. Record what you compared, and anything you could not compare, in the next handoff entry.
