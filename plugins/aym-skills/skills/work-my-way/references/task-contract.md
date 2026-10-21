# Task contract, review and continuation

Read this for a substantial handoff, multi-session continuation or review of settled changes. Use the fields that matter in the owning project's existing plan, ledger or handoff. A short task can keep its contract in the conversation.

## Carry the agreed job

- **Result and scope:** requested behavior or deliverable, acceptance conditions and explicit exclusions. Name observable units when there are real dependencies.
- **Decisions and authorization:** settled choices, approval source and covered scope, unresolved user decisions and actions needing separate authorization. A progress marker does not prove approval.
- **Inputs and method:** current project rules, relevant source paths or revision, runtime facts, selected specialist and its current instructions. Include only needed resources; private inputs stay in their owning area.
- **Destination and ownership:** actual repository/worktree, branch, output paths and one writer per edit surface. Record unrelated dirty files to preserve. Resolve paths and symlinks before writing.
- **Checks and evidence:** expected facts independent of the implementation, relevant behavior checks, review coverage and known environment limits. For defects, record the original symptom, reproduction and a check that can distinguish the intended failure from setup errors.

## Review the settled state

Give a fresh independent reviewer the agreed requirements, repository standards, relevant artifacts and exact review scope. Inspect the base and current revision plus staged, unstaged and relevant untracked changes; a commit-only diff can omit task work. Record exclusions and whether files changed during review. Recheck affected coverage after corrections or state drift.

Keep two finding groups: missing or incorrect requirements, and violations of repository standards or quality expectations. A clean standards review cannot cover a missing requirement. Record each finding with evidence, its effect, correction and recheck. Record security-hook invocation and its findings separately; configured hooks alone prove no execution. An unavailable reviewer or failed check leaves a named acceptance gap. Report-only review does not authorize edits.

## Pause and resume

On pause, stop dependent work and retain useful state without expanding the task. Record the goal, current repository/branch and relevant dirty state, completed results, decisions and approval evidence, checks with their outcomes, unresolved questions and next action. Preserve earlier evidence and link it instead of copying private data into shared indexes. Do not create a memory store or automatic capture flow.

On resume, reread the latest request and the owning record. Compare current files, branch, runtime and permissions with the recorded facts. Revalidate stale checks that the next action relies on. Reuse approval when its scope still fits; resolve changed requirements or missing approval before dependent work. A pause remains in force until the user resumes or redirects the job.

## Completion evidence

Report what changed and which acceptance conditions the actual checks cover. Separate pass, behavior failure, environment error, unavailable coverage and work not attempted. Name the independent review scope and outstanding findings. If evidence cannot support completion, continue authorized corrections or state the missing capability and preserve the remaining work. Sending messages, spending money, installing, committing, pushing, merging, deploying and publishing each depend on current authorization.
