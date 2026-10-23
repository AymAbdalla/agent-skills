# Changelog

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
