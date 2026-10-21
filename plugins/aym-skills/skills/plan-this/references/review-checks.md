# Review checks

Use this list when reviewing a plan. Scale it to the plan: a short plan gets a short review. Skip a check only when it has nothing to examine, and say so.

## Feasibility

- Every named file, directory, script, Makefile target, package script, CLI, service, account, credential and dataset either exists now or the plan states who provides it and when. Check by inspection: list the directory, search for the target, read the package or build file, run a read-only `--version` or `which` when safe.
- Steps that need network, paid services, production data or another person's action are marked as such.
- Ordering works: no slice uses something a later slice creates.
- The plan respects the repository's existing structure, languages and conventions unless it states a reason to change them.

## Acceptance coverage

Build a small table while reviewing:

| Requirement (source) | Plan check | Covers it? |
| --- | --- | --- |

A requirement is uncovered when no check exercises it, or the only check would pass without the behavior (for example a test that reads an internal value instead of the output). Edge cases the requirements name explicitly, such as empty input, errors or permissions, count as separate requirements.

## Slices

- Each slice ends in something observable.
- Layer-only slices (schema, types, helpers with no caller) are flagged for merging into a user-visible slice.
- Blockers are real; independent slices are not chained.
- Slices are sized to finish and check in one sitting; no quota.

## Risks

- Data loss, migration or rollback gaps.
- Secrets in plan text, logs or committed config.
- Security or privacy exposure, including new external calls.
- Hidden scope growth beyond the agreed requirements.
- Checks that cannot run in the current environment and what that leaves unproven.

## Open decisions

- Choices the plan leaves open that block a slice.
- Choices the plan makes without a recorded decision that change user-visible behavior, cost or scope. Ask; do not decide.

## Settled choices

Carry forward every choice the record marks as approved, decided or rejected. Reopen one only with:

- evidence in the repository or environment that contradicts it, or
- a changed assumption it depended on.

Name the evidence when reopening. A preference, a popular alternative or a general best practice alone does not reopen a settled choice. When a settled choice creates a real risk, report the risk and leave the decision with the user.

## Finding format

```markdown
### F<n>: <short title>  [needs decision | proposed fix, needs acceptance]
Evidence: <file:line, command output, or requirement id>
Current: <plan text or "missing">
Proposed: <specific change>
```

Number findings in order of consequence. Keep each remedy independently acceptable. End with: settled choices preserved, checks not performed and why, and a note that the review does not approve the plan.

## Optional lenses

Use one only when the user asks or the plan's goal depends on it.

- **Business:** who pays or benefits, what result would show the work was worth it, cost of the dependencies.
- **Design:** user journey covered end to end, empty/error/loading states, accessibility.
- **Developer experience:** setup steps, error messages, docs a new contributor would need.

A lens adds findings in the same format. It does not change scope by itself; scope changes are open decisions for the user.
