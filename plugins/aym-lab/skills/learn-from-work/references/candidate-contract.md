# Lesson candidate contract

A candidate is a proposal for a later, separately authorized skill change. It does not change any skill. Write one Markdown file per candidate.

## Fields

Put these fields at the top of the file, in this order, as a Markdown list or a YAML block.

| Field | Content |
| --- | --- |
| `status` | `candidate` when written. Later states belong to the reviewer and builder: `accepted`, `rejected`, `stale`, `built`. |
| `created` | Date of capture, `YYYY-MM-DD`. |
| `rule` | One or two sentences a later agent can follow. State it as a procedure or a pitfall, not a story. |
| `reason` | The cause the evidence shows, in one or two sentences. |
| `applies_when` | The situations where the rule helps. |
| `does_not_apply_when` | At least one counterexample, where following the rule would be wrong or useless. |
| `evidence` | Pointers to the files, logs, commands and check output that support the rule, with the check result quoted briefly. Use paths relative to the project root. Quote no private data and no secrets. |
| `target_owner` | The skill that owns the lesson, or `pending` with the reason when ownership is unclear. |
| `change_kind` | `extend` an existing skill, or `new-skill` with the reason no existing skill fits. |
| `target_files` | Each file the change would touch, with the SHA-256 of its full contents at the moment you read it. For a new skill, list the proposed path and `new`. |
| `proposed_change` | A short description of the edit or addition, with the section it belongs in. Do not paste a full patch. |
| `privacy` | `general` when the rule names no private detail, or `owner-private` with the private area that holds it. |
| `handoff` | Copy this text exactly: `Before drafting, build-skill re-hashes every target_files entry. Any mismatch or missing file means stale: re-read and reconcile first. See learn-from-work references/candidate-contract.md, "Handoff to build-skill".` |

## Sanitized example

```markdown
- status: candidate
- created: 2026-10-09
- rule: When passing tracked file names to another command, use `git ls-files -z` with `xargs -0` so names that contain spaces stay whole.
- reason: The lint step skipped two files whose names contained spaces; after switching to null-separated names, the lint run covered all 31 files and passed.
- applies_when: A script feeds Git file lists to another command in a repository that may contain spaces or newlines in file names.
- does_not_apply_when: The command reads Git's file list itself, or the target platform's `xargs` has no `-0` option.
- evidence: notes/lint-run.md (steps 3 to 5); `make lint` reported `31 files checked, 0 problems` after the change.
- target_owner: repo-scripts
- change_kind: extend
- target_files:
  - skills/repo-scripts/SKILL.md sha256 9b1e...04c7 (record the full 64-character hash in a real candidate)
- proposed_change: Add one rule under "Passing file lists" with the null-separator pattern and its counterexample.
- privacy: general
- handoff: Before drafting, build-skill re-hashes every target_files entry. Any mismatch or missing file means stale: re-read and reconcile first. See learn-from-work references/candidate-contract.md, "Handoff to build-skill".
```

## Destination rules

1. The owning project is the project that owns the target skill. Use the location it names for lesson candidates or proposals in its README, AGENTS.md or equivalent instructions.
2. When the project names none, propose a location inside that project's existing documents area and ask before creating a new folder.
3. Use `<outputs>/<plugin>/learn-from-work/` only for a sanitized general method with no project owner. `<outputs>` is the outputs folder named in the user's instructions (CLAUDE.md or AGENTS.md; default `~/agent-outputs/`), and `<plugin>` is the plugin that holds the target skill, for example `aym-skills`.
4. Keep private and employer material in the environment where the work happened. Never write a candidate into a skill's source folder, an installed skill copy, loose in a home directory, memory files or a new top-level folder.
5. Name each file `YYYY-MM-DD-<short-rule-slug>.md`. Before writing, search the destination for a candidate with the same evidence and target. Treat a differently worded rule with the same meaning as the same candidate. Reuse it when its hashes match; report it as stale when they do not, and do not write a second record unless the user asks.

## Handoff to build-skill

A candidate starts no build. The user reviews it and may ask build-skill to make the change. Before drafting, build-skill must:

1. Re-compute the SHA-256 of every file in `target_files`.
2. Compare each hash with the recorded hash. If any differs, or a listed file is missing, treat the candidate as stale. Do not draft from it.
3. For a stale candidate, re-read the current files, reconcile the rule with what changed, and record new hashes. Proceed only after that reconciliation and with the requested approval.
4. Verify the resulting change with a fresh behavior check and independent review, as build-skill requires.

Candidate, reviewed source change and enabled installation are separate states. A saved candidate does not mean the skill changed, and a source change does not mean an installed copy changed.
