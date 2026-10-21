# Make aym-skills the default

Nothing in this folder is active until you copy or register it yourself. There are three layers, from weakest to strongest. Each one makes Claude or Codex more likely to use `work-my-way`. None of them can force it, because skill choice is always the model's call.

| Layer | What it does | Covers |
| --- | --- | --- |
| 1. Skill descriptions | Already in the plugin | Claude Code, Codex, desktop app |
| 2. Standing instruction | Read at the start of every session | Claude Code ([CLAUDE.md.snippet](CLAUDE.md.snippet)), Codex ([AGENTS.md.snippet](AGENTS.md.snippet)) |
| 3. Prompt hook | Adds a one-line reminder next to **every** message you send | Claude Code only ([claude-hook/](claude-hook/)) |

If you keep one shared instructions file for both tools (for example with `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` linked to it), add the lines there once.

## Layer 2: standing instruction

- **Claude Code:** append the contents of `CLAUDE.md.snippet` to `~/.claude/CLAUDE.md` (create the file if it doesn't exist).
- **Codex:** append `AGENTS.md.snippet` to Codex's global `AGENTS.md`, usually `~/.codex/AGENTS.md`. Check the current Codex docs if that path has moved.

## Layer 3: Claude Code prompt hook (optional)

`claude-hook/work_my_way_nudge.py` reads nothing and writes nothing. It always exits 0, so it can never block a message. It prints one factual sentence, which Claude Code adds as context next to your prompt. To turn it on:

1. Copy the `hooks` block from `claude-hook/settings.snippet.json` into `~/.claude/settings.json`. Merge it with any hooks you already have; don't replace the file.
2. Replace `/ABSOLUTE/PATH/TO/aym-skills` with your checkout's real path.
3. Start a new `claude` session, then type `/hooks` to confirm it's listed.

To turn it off, remove that block. Reference: [Claude Code hooks](https://code.claude.com/docs/en/hooks).

## How to tell it worked

- Every phase ends with the stop card (`✔ … Next: …`). No card means the skill didn't run. Say "use work-my-way" to pick it up.
- In Claude Code, the transcript shows a `Skill(aym-skills:work-my-way)` step.
- `/plugin` lists `aym-skills` as installed and enabled.
- For a repeatable check, run `pressure-test-my-skills` (in `aym-lab`) on `work-my-way` with a handful of everyday requests.
