# Changelog

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
