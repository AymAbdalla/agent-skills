# aym-story

Turn finished work into understanding and stories: plain-English explanations, practice quizzes, blog articles and portfolio cases. Every skill writes files and stops. Nothing is published, posted or sent.

## Install

Claude Code:

```
/plugin marketplace add AymAbdalla/agent-skills
/plugin install aym-story@aym-skills
```

On Claude Code 2.1.275 or later, one line also works: `/plugin install aym-story --marketplace AymAbdalla/agent-skills`.

Codex:

```
codex plugin marketplace add AymAbdalla/agent-skills
```

Then install `aym-story` from the Codex plugin list.

## The four skills

| Skill | Say | What it does |
| --- | --- | --- |
| `explain-it-my-way` | "explain it my way" | Explains software, decisions or workflows in plain English with a visual, then teaches the industry terms and compares the approach with sourced practice. |
| `test-my-knowledge` | "quiz me" | Builds a source-checked practice quiz as a local HTML page with an answer key, then retests what you missed. |
| `blog-it` | "blog it" | Reads a session or project, finds its milestones, and writes one article per transferable idea. |
| `create-my-portfolio` | "make a portfolio case" | Turns one piece of your work into an evidence-checked portfolio case draft. |

`explain-it-my-way` and `test-my-knowledge` share a small learner ledger file so they don't re-teach what you already know. Ask them not to track, and they won't.

## Settings (optional)

The skills read folder names from your own instructions file (`~/.claude/CLAUDE.md` for Claude Code, `~/.codex/AGENTS.md` for Codex). Add the lines you want:

```
## aym-skills settings
- Outputs folder: ~/agent-outputs/
- Scratch folder: ~/agent-work/
```

Without them, files go to `~/agent-outputs/<owner>/<task>/` (the owner is the project's short name, or `personal`), scratch files go to the system temp folder, and the learner ledger is `~/agent-outputs/personal/learning/ledger.md`. Each skill says where it saved.

## License

MIT. See `LICENSE`.
