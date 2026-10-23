---
name: install-check
description: Check a plugin, skill, MCP connector or hook before the user installs it, and decide download, build their own, or skip. Review mode checks what is already installed against the user's toolkit file and asks keep or remove one item at a time. Use when the user pastes an install command, a marketplace or GitHub link, or asks "should I add this?", "is this worth installing?", "add these skills", "what can I remove?" or "review my plugins". Applies the user's own build-or-download rules as well as the general ones. Report-only; never installs or removes.
---

# Install check

Plugins that never get used pile up, and overlapping ones make it unpredictable which skill runs. This check runs before anything new is added, and in review mode it goes back over what is already installed. It reports verdicts and stops. It never installs, enables or removes anything.

The **toolkit file** is the user's list of what they keep and why. Use the toolkit file named in the user's instructions (CLAUDE.md or AGENTS.md); if none is named, use `~/TOOLKIT.md`. When the file does not exist, say so, work from what is installed, and give the lines that would start it.

Pick the mode first: **new item** (steps 1 to 4) or **review mode** (the section after step 4) when the user asks what to keep or remove, or when a 1-week test date in the toolkit file has passed.

## 1. Read what it is

From the link, repo or command, find: its name, who makes it, what it contains (skills, hooks, MCP servers, commands), what each part does, and whether anything runs automatically (hooks, scheduled runs, startup scripts). Read the actual files when you can reach them; otherwise say what you could not read.

## 2. Compare with what the user already has

- Read the toolkit file if it exists.
- List the skills and MCP tools available in this session. Name every one that does the same job.
- If the aym-skills core skills (work-my-way, plan-this, implement-this, debug-this, check-this, ship-this, handoff-this) already cover the job, say so plainly.

## 3. Apply the rule

| Verdict | When |
| --- | --- |
| **Download** | A common job lots of people do, made or maintained by the app's owner, and the user would use it as is. |
| **Build their own** | It's about how the user works, they have typed the same instructions 3+ times, a downloaded one would need constant correcting, or it needs their own rules (a boundary their instructions set, a stop after each phase). Hand off to `build-skill`. |
| **Skip** | It overlaps what they have, it's for a one-time task (just ask in chat), or it doesn't serve the current goals their instructions state. |

Apply any extra install rules the user's instructions add. Flag these risks regardless of verdict: hooks that run on every message or tool call, anything that sends data to an outside service, write access to email, CRM or accounts, and requests for keys.

## 4. Report

In plain English, at most 8 lines:
- What it is and who makes it.
- Overlap with what they already have.
- Verdict and the one reason that decided it.
- Risks found.
- If **Download**: the exact install command, which tool (Claude Code, Codex or both), and the line to add to the toolkit file (name, why, date, "1-week test: remove if used fewer than 3 times").
- If **Build their own**: the job the skill would do and the evidence it's worth building.

End with the aym-skills stop card when the aym-skills plugin is installed (its `work-my-way/references/house-rules.md` defines it), or with the card format the user's instructions describe. Otherwise end with these four lines:

```
✔ Install check done: <verdict for each item>
Saved: nothing saved
Needs from you: <the install or removal steps the user can take now, or "nothing">
Next: <what you suggest next>. Say "go", or tell me what to change.
```

Installing is the user's action or needs their explicit yes.

## Review mode

Use review mode to keep the toolkit small after things are installed: list what is installed, compare it with the toolkit file, check the wiring, count real use, and ask keep, remove, merge or skip one item at a time. It is report-only; the user does every removal themselves. Follow [review-mode.md](references/review-mode.md) step by step.
