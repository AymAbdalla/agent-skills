---
name: ship-this
description: Prepare and perform the Git operation the user asked for, a commit, a commit and push, a sync with GitHub (pull, commit, push), a pull request, or a merge they name, after checking the exact content being sent and staging only related files. Use when the user asks to commit, push, sync, open a PR, or "push and merge" finished work. Do not use for deploying, releasing, or watching a PR; those are separate actions.
---

# Ship this

Turn finished, authorized work into the exact Git result the user asked for, and nothing beyond it. Follow the house rules at `../work-my-way/references/house-rules.md`, resolved from this skill's folder (read it directly; don't search for it); shipping is the one phase that writes to Git history and remotes, so the rules below are stricter, not looser.

## Set the ceiling

Read the request and name the highest operation it authorizes:

| Request | Allowed | Not allowed |
| --- | --- | --- |
| commit | local commit | push, PR |
| push | commit if needed, push current branch | PR, merge |
| sync ("sync with GitHub", "bring GitHub up to date", "pull push") | pull the current branch's upstream (fast-forward or rebase of your own unpushed commits only), commit if needed, push current branch | PR, merge, force push |
| open a PR | commit if needed, push, create PR | merge, auto-merge |
| merge ("push and merge", "merge it", "merge the PR") | everything above that the request needs, then merge the named branch or PR into its base and push the base | deploy, release, deleting branches unless asked |

Merge is allowed only when the user's current request says "merge". "Ship it" or "push it" never includes a merge. Deploy, release tags, version bumps, changelog edits, enabling auto-merge and watching a PR or its CI are outside this skill. If the user asks for one, say it is a separate action that needs its own authorization and tooling, and do not perform it here. A request to deploy is not a request to commit or push. When the operation is unclear, ask before any write.

## Select the final state

1. Inspect with separate read-only commands: `git status --short`, `git branch --show-current`, `git diff`, `git diff --cached` and `git log --oneline -5`. Note the remote and upstream only if pushing.
2. Decide which files belong to the requested change, using the request, the task's plan and the diff. List every other dirty path, including files someone already staged, as unrelated. If a file mixes related and unrelated edits, or membership is unclear, ask.
3. Check the branch. Follow the project's branch rules. If you are on the default branch or a detached HEAD and the project expects feature branches, or the rule is unclear, ask before committing.

## Verify the exact content

Run the project's relevant checks against the files you will commit, after the last edit. A result from before a later edit does not count. If unrelated dirty files could affect the result, say so. A failing or unavailable check stops the commit unless the user, told the result, still asks to proceed; record that choice in the message body or report. Do not edit code to make a check pass unless that edit is part of the authorized task.

## Commit

1. Check who the commit will be authored by: read `git config user.name` and `git config user.email`. If either is an AI or tool name (for example Claude, Codex, an assistant or a bot) and the project or the user bans AI attribution, stop and ask which identity to use. With the user's answer, set it for this commit only (`git -c user.name=... -c user.email=... commit ...`). Never change git config without a yes.
2. Stage only the related files by name. Never use `git add -A`, `git add .` or `git commit -a`.
3. Write the message to a file in the session's task scratch folder (the host temp area if none): an imperative subject that names the outcome, then a short body when the reason is not obvious. Match the project's message conventions and any required trailers. Describe only what the staged diff contains.
4. Commit with an explicit pathspec so other staged files stay out: `git commit -F <message-file> -- <file> ...`.
5. Read back: `git show --stat HEAD` must list exactly the selected files and the author you checked in step 1; `git status --short` must still show the unrelated paths. Then delete the message file.
6. Do not amend, rebase or squash commits that already exist on a remote unless the user asks.

## Sync, only when requested

1. Run `git fetch` and compare the branch with its upstream (`git status -sb`). If the upstream has new commits, pull them before committing: `git pull --ff-only`. If that refuses because both sides moved, rebase only your own unpushed commits (`git pull --rebase`). If a conflict appears, stop and report the conflicting files; never resolve a conflict by discarding someone's changes.
2. Commit related files as in Commit above, then push as in Push and PR below.
3. Report what came down from GitHub (commit count and subjects) and what went up.

## Merge, only when the user says "merge"

1. Prefer the host's PR merge (for example `gh pr merge <n> --merge`, or the repo's usual method) when a PR exists. With no PR, merge locally: update the base branch from its upstream, `git merge --no-ff <branch>`, rerun the project's checks on the merged result, then push the base.
2. Before merging, confirm checks passed on the exact content and the PR or branch has no conflicts. A failing check or a conflict stops the merge; report it.
3. After merging, confirm the base branch on the remote contains the merge (`git ls-remote` against the local base). Do not delete branches unless asked.

## Push and PR, only when requested

- Before pushing, confirm the checks ran on content identical to the commits being pushed. If unrelated dirty files were present during the checks, or a commit predates this session, rerun the checks or report the gap and ask.
- Push the current branch to its configured upstream with `git push`. With no upstream, use `git push -u <remote> <branch>`; if more than one remote exists, ask which one. Do not force push unless the user asks for it by name. Confirm with `git ls-remote <remote> refs/heads/<branch>` that the remote ref equals local `HEAD`.
- Create a PR only when asked. Check for an existing PR for the branch first. Write the body to a file from the actual diff and check results, scan it for secrets and private paths, then create it with the host's PR tool. Report the URL. Do not merge (unless the user said "merge"), enable auto-merge, request merge queues or start watching the PR.

## Report

List each state separately with its evidence: checks run and results, commit hash and files, push target and verified remote ref, PR URL, sync pull results, merge result if any, and actions not taken (deploy, watch). Name unrelated files left unstaged or uncommitted. End with the stop card. When shipping is the last phase, its "Next" line says "nothing further" unless the user asked for another operation. See [operations detail](references/operations.md) for edge cases.
