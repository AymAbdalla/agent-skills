# aym-skills

A daily build loop for AI-assisted work in Claude Code and Codex. Describe the job, and `work-my-way` picks the phase, runs it with the right skill, and stops after each phase with a short card: what was done, what was saved, what it needs from you, and what comes next. Nothing commits, pushes, merges, deploys, installs or sends unless you ask for that action.

## Install

Claude Code:

```
/plugin marketplace add AymAbdalla/agent-skills
/plugin install aym-skills@aym-skills
```

On Claude Code 2.1.275 or later, one line also works: `/plugin install aym-skills --marketplace AymAbdalla/agent-skills`.

Codex:

```
codex plugin marketplace add AymAbdalla/agent-skills
```

Then install `aym-skills` from the Codex plugin list.

## The seven skills

| Skill | Phase | What it does |
| --- | --- | --- |
| `work-my-way` | Clarify, and the entry point | Sizes the job, asks only the questions that change the result, routes each phase and stops after it. |
| `plan-this` | Plan | Writes a spec or an implementation plan in thin end-to-end slices, or reviews a plan against the real repository. |
| `implement-this` | Build | Builds an approved plan slice by slice, test-first, with a check after each slice. |
| `debug-this` | Debug | Reproduces the exact symptom, tests the cause, and rechecks the original case after a fix. |
| `check-this` | Check | Reviews changes, verifies "done" claims against fresh evidence, QAs a page in a real browser, or simplifies code without changing behavior. Report-only unless you ask for fixes. |
| `ship-this` | Ship | Commits, pushes, syncs or opens a pull request after checking exactly what is being sent. Merges only when you say "merge". |
| `handoff-this` | Continue | Writes a handoff note so another session can pick up the work, or resumes from one after checking the repository. |

The shared rules every skill follows (the stop card, honest result states, working-tree and secret safety, and the actions that need your own yes) are in `skills/work-my-way/references/house-rules.md`.

## Companion plugins

From the same marketplace: `aym-story` (explanations, quizzes, blog articles, portfolio cases), `aym-lab` (dissect systems, build and test skills) and `aym-gtm` (GTM engineering on plain files). `work-my-way` sends skill work to `aym-lab` when it is installed and does the work directly when it is not.

To make `work-my-way` the default for every session, see `setup/always-use/` in the repository.

## License

MIT. See `LICENSE`.
