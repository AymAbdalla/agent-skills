# agent-skills

Four plugins of agent skills for Claude Code and Codex. Describe the job in plain words, and the skills plan, build, check and ship it one phase at a time, stopping after each phase so you stay in charge. Nothing commits, pushes, deploys, installs or sends unless you ask for that action.

| Plugin | What it is for | Skills |
| --- | --- | --- |
| [aym-skills](plugins/aym-skills/) | The daily build loop | `work-my-way`, `plan-this`, `implement-this`, `debug-this`, `check-this`, `ship-this`, `handoff-this` |
| [aym-story](plugins/aym-story/) | Explanations, quizzes and write-ups | `explain-it-my-way`, `test-my-knowledge`, `blog-it`, `create-my-portfolio` |
| [aym-lab](plugins/aym-lab/) | Building and testing skills | `dissect-this`, `build-skill`, `pressure-test-my-skills`, `learn-from-work`, `install-check` |
| [aym-gtm](plugins/aym-gtm/) | GTM engineering on plain files | `icp-define`, `data-quality`, `account-book`, `signal-score`, `play-build`, `outreach-draft`, `daily-plan`, `crm-sync`, `funnel-review`, `motion-map` |

Each plugin folder has its own README with what every skill does.

## Install

Claude Code:

```
/plugin marketplace add AymAbdalla/agent-skills
/plugin install aym-skills@aymabdalla
/plugin install aym-story@aymabdalla
/plugin install aym-lab@aymabdalla
/plugin install aym-gtm@aymabdalla
```

Install only the plugins you want. On Claude Code 2.1.275 or later, one line per plugin also works, for example `/plugin install aym-skills --marketplace AymAbdalla/agent-skills`. Run a skill directly with `/aym-skills:work-my-way`, `/aym-gtm:daily-plan` and so on.

Codex:

```
codex plugin marketplace add AymAbdalla/agent-skills
```

Then install the plugins you want from the Codex plugin list. Run a skill directly with `$work-my-way`.

Claude app: Customize → Plugins → Add → Add marketplace → Add from a repository → `AymAbdalla/agent-skills`, then add each plugin from Discover.

## How it works

`work-my-way` is the entry point. Say what you want ("add a CSV export", "this test is flaky", "review this PR") and it picks the phase: clarify, plan, build, check or ship. After each phase it stops with a card like this and waits for "go":

```
✔ Plan done — CSV export plan written
Saved: docs/plans/export.md
Needs from you: nothing
Next: Build (implement-this). Say "go", or tell me what to change.
```

To make `work-my-way` the default in every session, see [setup/always-use](setup/always-use/).

## Settings (optional)

A few skills save files or read a list you keep. They take folder names from your own instructions file (`~/.claude/CLAUDE.md` for Claude Code, `~/.codex/AGENTS.md` for Codex):

```
## aym-skills settings
- Outputs folder: ~/agent-outputs/
- Scratch folder: ~/agent-work/
- Library folder: ~/agent-outputs/library/
- Toolkit file: ~/TOOLKIT.md
```

Without these lines, files go to `~/agent-outputs/<owner>/<task>/`, scratch files go to the system temp folder, `install-check` uses `~/TOOLKIT.md`, and `build-skill` runs without a mechanics library until you start one with `dissect-this`.

## Tests

The helper scripts have unit tests. From the repository root, with Python 3 (checked with 3.13):

```
python3 -m unittest discover -s tests -p "test_*.py"
```

Three skills also carry their own tests in a `tests/` folder inside the skill: `build-skill`, `pressure-test-my-skills` and `test-my-knowledge`. The `build-skill` tests need `BUILD_THIS_TEST_TMP` set to an existing scratch folder.

## License

MIT. See [LICENSE](LICENSE).
