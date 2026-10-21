---
name: plan-this
description: Plan phase for agreed work, in three modes. Spec mode writes agreed behavior, scope and acceptance checks into the project's spec document. Plan mode writes an implementation plan of end-to-end slices with real dependencies, checks and an editable Mermaid flow, then stops for approval. Review mode checks a proposed plan against the real repository and reports findings. Use when the user asks to write up the spec or requirements, plan a feature, or review, check or critique a plan or design doc. Do not use to settle open questions, build, or review finished code.
---

# Plan this

Turn settled requirements into a document the user can approve before anything is built. Follow the house rules at `../work-my-way/references/house-rules.md`, resolved from this skill's folder (read it directly; don't search for it). Planning writes no product code, tests or configuration, and runs no step that changes the project.

## Pick the mode and say it first

| Request | Mode |
| --- | --- |
| "write the spec", "capture the requirements", "record what we agreed" | **spec** |
| "plan this", "how do we build it", "break it into steps" | **plan** |
| "review this plan", "check this design", "poke holes in the plan" | **review** |

Stop early if behavior is not agreed: list the open choices that change what gets built and hand back to the Clarify step in `work-my-way`. Do not invent answers to fill a document. A small bounded fix needs no document; say so, or give a two-line plan.

## Spec mode

1. **Destination.** Use the path the user names, or the project's established spec location (check the README and `docs/`). Read the whole file first. If none exists, propose one path and ask. Never start a parallel spec tree.
2. **Collect agreement** from the conversation, decision records, approved plans and the existing spec. When sources disagree and no record says which controls, list the conflict as an open item naming both.
3. **Write** only the section for this work, using [spec-shape.md](references/spec-shape.md). Leave unrelated sections unchanged byte for byte. Each statement traces to a source. Anything not agreed goes under **Open items**. A default you suggest is labelled "proposed, not agreed". Acceptance checks are observable results at a public seam. If you change an already-approved section, list each change and mark the section as needing re-approval.
4. **Read back** the file. Publishing an issue, opening a PR or sending the spec are separate actions for later.

## Plan mode

1. **Starting point.** Read the agreed behavior, the project instructions, the code areas the work touches and the existing tests. Look for an existing plan (in the plans location, the path the user named, and any plan the spec links). If an approved plan already covers the work, point to it and stop. Update an unapproved draft in place. Never write a second plan beside one.
2. **Write the plan** where the user asked, or in the project's plans location, using [plan-shape.md](references/plan-shape.md): goal and source of agreement; slices (thin end-to-end paths, each with one observable acceptance check, ordered by real blockers); real dependencies (exists now? who provides? what the check does if missing; no secret values); verification (each requirement mapped to a check); risks, open decisions and fog; an editable Mermaid flow; and the approval request. No ticket quotas, task counts or time estimates unless asked. When the plan adds a scheduled, repeating or self-running job, apply the [loop check](references/loop-check.md) and put its answers in the plan.
3. **Confirm** the file is saved where you said.

## Review mode

Report only, unless the user asks you to edit the plan. If asked to implement it, decline that part and name Build as a separate phase.

1. Read the plan, the requirements it claims to meet and any recorded approvals. List the **settled choices** and keep them. Reopen one only when evidence contradicts it or its assumption changed, and name the evidence. Your preference is not evidence.
2. Check feasibility by inspection (every tool, file, script, service and credential exists or has a stated source), acceptance coverage (requirement → check table), slices and order, risks, and open decisions. See [review-checks.md](references/review-checks.md) for the full list, the finding format and the optional business, design and developer-experience lenses.
3. Give one finding per issue, most consequential first, each with its evidence, the current text, the proposed change, and whether it needs the user's decision. A review does not approve the plan.

## Stop

End with the stop card. Spec → next is Plan. Plan → "Approve this plan?", then Build. Review → "Accept which findings?" Approving a plan covers its scope only.
