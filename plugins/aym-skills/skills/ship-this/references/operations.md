# Operations detail

Read this when an edge case below applies.

## Already-staged files

Someone may have staged files before you started. `git commit -- <paths>` commits only the named paths and leaves other index entries staged. Do not unstage the user's files unless asked. Report them as "staged, not committed".

## Mixed files

If one file holds both related and unrelated edits, do not split it with interactive staging on your own judgment. Ask whether to include the whole file, leave it out, or let the user split it.

## Nothing to commit

If the related files have no changes, say so and stop. For a push request with an existing unpushed commit, confirm it is the intended one and that checks ran on exactly that content. If the checks are older than the commit or ran with unrelated dirty files present, rerun them on a clean view of the commit, or report the gap and ask before pushing.

## Remote state

Before pushing, run `git remote -v` and check the upstream with `git rev-parse --abbrev-ref --symbolic-full-name @{u}`; a non-zero exit means no upstream is set. With no upstream and more than one remote, ask which remote to use. A rejected non-fast-forward push means the remote moved. In a sync request, pull as the Sync section says and push again. Otherwise report it; do not pull, rebase or force push without the user's direction. Never force push unless the user asks for it by name.

## PR body

Build the body from `git diff <base>...HEAD --stat`, the commit messages and the checks you ran. Include what changed, why, how it was checked and known limits. Do not claim a check that did not run. Pass the body by file. The PR tool may need network access and credentials the session lacks; if creation fails, report the error and leave the pushed branch as is.

## Author identity

Use the identity the user's or project's instructions name, passed per command with `git -c`, so the machine's config stays unchanged. With none named, confirm the configured identity with the user before the session's first commit, as Commit step 1 says. If an existing unpushed commit carries the wrong author, report it and ask before amending.

## Hooks

Repository hooks may run on commit or push. Report their output. If a hook fails, the operation did not happen; fix only within the authorized task, then rerun checks before trying again. Do not bypass hooks with `--no-verify` unless the user asks.

## Effects that stay out of scope

Merging, deploying, tagging a release, publishing a package, enabling auto-merge, closing issues and watching CI or reviews each need their own request. Completing a push or PR does not imply any of them.
