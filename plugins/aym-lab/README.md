# aym-lab

Build and improve agent skills: dissect how a system works, build a skill from what you learned, pressure-test it, capture lessons from finished work, and check a plugin before you install it. Nothing here installs, enables or removes anything on its own.

## Install

Claude Code:

```
/plugin marketplace add AymAbdalla/agent-skills
/plugin install aym-lab@aym-skills
```

On Claude Code 2.1.275 or later, one line also works: `/plugin install aym-lab --marketplace AymAbdalla/agent-skills`.

Codex:

```
codex plugin marketplace add AymAbdalla/agent-skills
```

Then install `aym-lab` from the Codex plugin list.

## The five skills

| Skill | Say | What it does |
| --- | --- | --- |
| `dissect-this` | "dissect this", "how is this built" | Explains how a skill, plugin, hook, MCP system, tool or project works from its source, and pulls out the reusable mechanics. |
| `build-skill` | "build a skill for…" | Creates or revises one skill, looks up fitting mechanics in your library, writes a design record and checks the result. |
| `pressure-test-my-skills` | "pressure-test this skill" | Runs a frozen set of normal, ambiguous, failure, unavailable-tool and wrong-trigger cases in fresh sessions and grades what they leave behind. |
| `learn-from-work` | "learn from this work" | Saves one reviewable lesson for the skill that owns it, or explains why nothing should be kept. |
| `install-check` | "should I install this?", "what can I remove?" | Decides download, build your own, or skip before you install something, and reviews what is already installed one item at a time. |

## The mechanics library

`build-skill` looks up reusable mechanics in a library: a folder named `library` that holds `LIBRARY.md` and a `dissections/` folder. This plugin ships without one. You start your own: run `dissect-this` on a skill or tool you admire and save what it finds. Until then, `build-skill` says "no library found; start one with dissect-this or pass --library-root" and builds from an original design.

## Settings (optional)

The skills read these from your own instructions file (`~/.claude/CLAUDE.md` for Claude Code, `~/.codex/AGENTS.md` for Codex):

```
## aym-skills settings
- Outputs folder: ~/agent-outputs/
- Library folder: ~/agent-outputs/library/
- Toolkit file: ~/TOOLKIT.md
```

Without them, reports go to `~/agent-outputs/<owner>/<task>/`, `install-check` uses `~/TOOLKIT.md` (your list of what you keep and why), and `build-skill` works without a library.

## License

MIT. See `LICENSE`.
