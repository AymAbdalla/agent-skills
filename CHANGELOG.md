# Changelog

## 0.6.1 (2026-10-26)

- One rule for who checks: every substantial job (code, research, writing, data, a skill) ends with its Check in a fresh chat or the other tool, labelled independent. A helper the working chat starts is labelled "helper review" and never counts as independent; the chat that did the work labels its own look self-review. check-this, the task contract, build-skill, learn-from-work and dissect-this now all say the same thing. Skills in the other plugins that end a substantial job (the GTM skills, blog-it, create-my-portfolio, test-my-knowledge, build-skill, dissect-this, learn-from-work) carry the rule in their own "Independent check" section, and "run all phases" now stops before Check. The rule applies to substantial runs only (files you'll rely on, send from or share); explain-it-my-way, install-check and pressure-test-my-skills say in one line why they need no separate check.

## 0.6.0 (2026-10-25)

Independent checks you can trust, and security reviews in every phase.

### New

- **Builder and checker records.** Work built in slices keeps three files in `docs/agents/`: `build.md` (the builder's own rows, always labelled self-check), `checks.md` (written only by an independent checker in a fresh chat or another tool, against an exact commit) and `status.md` (one line per workstream).
- **A merge gate.** `check-this/scripts/agents_gate.py check` refuses a merge while a slice has no independent pass, a pass is for older code, a check was committed together with other files, a builder row claims more than `built`, or the branch changed code without a passing security check. `ship-this` runs it before every merge.
- **Security reviews in every phase.** Every `check-this` mode runs an 8-point security pass (secrets, injection, logins and permissions, outside input, dependencies, data exposure, settings, AI and agent risks) and reports findings with file and line, or "no findings" with what it covered. Every plan gets a Security section, a short list of what could go wrong. The house rules gain five secure-coding rules.
- **A paste-back block.** A check that finds problems ends with a numbered "Paste into the build chat" block (file, line, what's wrong, suggested fix), and "recheck" runs the same check on the new commit.
- **Fresh-chat prompts.** The stop card gains a `New chat:` line at natural breaks, with a complete line to paste, so long sessions move to a fresh chat without losing state.
- **Parallel work rules.** Claude Code and Codex can build at once: one worktree, branch, plan file and test database per workstream, and `status.md` says who owns which files.
- **A security policy.** The repository ships a `SECURITY.md` that says how to report a problem privately.

### Changed

- An independent check never fixes the work it checks, even when asked; it sends the fixes back to the build chat. Fixes stay available for a plain review of your own file and for simplify.
- Agents may commit finished slices on their own feature branch without asking; committing to `main`, pushing and merging still need a yes.
- `ship-this` commits as the identity your instructions name, and confirms the configured identity before a session's first commit when none is named.
- AI-attribution rules are out of the skills; they belong in your own personal and project instructions.
- `aym-gtm` is no longer part of this collection.

### Upgrading

Projects that already use agent records need one security check recorded in `checks.md` before their next merge, or the gate refuses it.

## 0.5.0 (2026-10-22)

- Skills stop instead of guessing. When a step says ask or confirm and nobody can answer, a skill writes nothing that depends on the answer and puts the question in its reply; a read-only report may use a default it names. Questions come one at a time.
- `ship-this` checks the commit author before committing and stops if it is an AI or tool name in a project that bans AI attribution.
- `create-my-portfolio` asks which work to use when none is named, instead of picking one.
- `dissect-this` saves its report and adds the lessons it finds to the mechanics library, marked for review; a plain "explain" saves the report only.
- Sharper descriptions for `work-my-way`, `implement-this`, `check-this`, `explain-it-my-way` and `build-skill`, so they are picked when a request doesn't name them. In a 26-skill routing test the right skill was chosen for 25 of 26 plain requests, and no skill for 6 of 6 ordinary questions.
- `aym-gtm`: one shared ICP-fit rule across four skills, open deals protected from the CRM export through to play-build and daily-plan, and fixes from a quality review.
- Smaller fixes: one proof-level scale shared by `blog-it` and `create-my-portfolio`; the learner ledger says what to do when its helper reports an error; `check-this`, `install-check`, `build-skill` and `test-my-knowledge` descriptions match what they do.

## 0.4.0-rc.2 (2026-10-21)

- The public copy lives in the `agent-skills` repository (README title to match) and its marketplace is named `aymabdalla`, so plugins install as `<plugin>@aymabdalla` and the plugin and marketplace names no longer repeat.
- Release copies are exported from one source: the export swaps the source's default folders and install rules for generic ones and refuses to publish if any source default is left or a skill's wording has drifted.

## 0.4.0-rc.1 (2026-10-20, updated 2026-10-21)

- New plugin `aym-gtm` with ten GTM engineering skills: `icp-define`, `data-quality`, `account-book`, `signal-score`, `play-build`, `outreach-draft`, `daily-plan`, `crm-sync`, `funnel-review` and `motion-map`. They read and write plain files, work with any CRM, never send, and ship with made-up example data.
- `install-check` gained a review mode for what is already installed.
- The core plugin moved into `plugins/aym-skills`, so every plugin folder holds only its own manifests and skills.
- The learner ledger shared by `explain-it-my-way` and `test-my-knowledge` updates through a helper script; a half-right answer counts as missed.
- Generic wording: the skills speak about "the user" and read personal folders (outputs, scratch, library, toolkit file) from the user's own instructions, with defaults. `build-skill` works without a mechanics library and says how to start one. `work-my-way` works when `aym-lab` is not installed. Each plugin folder has its own LICENSE and README.

## 0.3.1-rc.1 (2026-10-19)

- The stop card lists saved paths and "Needs from you". "Run all phases" goes straight through and still prints every card.
- `ship-this` can sync (pull, commit, push) and merges only when the user says "merge".
- New `install-check` skill in `aym-lab`: download, build your own, or skip, before installing anything.
- Setup snippets for making `work-my-way` the default, and a Codex marketplace file.

## 0.3.0 (2026-10-18)

- Consolidated into a core plugin of seven skills routed by `work-my-way`, with a stop after every phase, plus two side plugins: `aym-story` (explanations, quizzes, articles, portfolio cases) and `aym-lab` (dissecting systems and building, testing and improving skills).
