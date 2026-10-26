---
name: create-my-portfolio
description: Turn one selected piece of the user's work into an evidence-checked portfolio case, saved as one editable Markdown draft. Use when the user asks for a portfolio case, a case study of a project, or a portfolio write-up from Blog-it articles or a named repository. Does not publish, build or deploy a site, schedule posts, apply for jobs, send outreach, or write blog articles.
---

# Create my portfolio

Write one portfolio case that a careful reader can trust. Each factual claim in the draft traces to evidence the reader could inspect. The draft covers the problem, the decisions the user made, the work the assistant did, how the workflow runs, a failure and its correction when the evidence shows one, the result at its real proof level, and the limits. This skill writes a draft and stops.

## Choose the case

Accept one of two inputs:

- **Blog-it articles.** Treat each article as a lead. Its claims still need project evidence.
- **A named project or repository.** Read its README, decision log or ledger, Git history, tests and recorded results. This route does not need Blog-it.

When the request names no article, project or repository, ask which work to use and stop. Write no draft and no case files until the user names one; several projects being visible in the workspace is not a choice. Select exactly one case. Only when the user named one source that itself holds several cases (an article set, a repository with several projects) may you choose the one with the strongest evidence; name the others in your report. Do not merge two stories into one case.

Before you write, resolve and state:

- **Owner and task.** The owner is the short project name, or `personal`. The task is the current task name.
- **Case ID.** Use `<project>-<subject>` in lowercase kebab case, with no date. Search `<outputs>/<owner>/` for a `portfolio/<case-id>/` folder, where `<outputs>` is the outputs folder named in the user's instructions (CLAUDE.md or AGENTS.md; default `~/agent-outputs/`). When one exists, revise that draft instead of creating a second story.
- **Destination.** `portfolio/<case-id>/case.md` under `<outputs>/<owner>/<task>/`. When the owning project keeps private work in its own area, save there instead. Put scratch files in the scratch folder the user's instructions name, or in the system temp directory when none is named.

Stop and report when the material is employer material or the user has not authorized its use.

## Verify the claims

Read the [case contract](references/case-contract.md) before you verify anything. Then:

1. List each factual claim you plan to make: counts, results, decisions, failures, comparisons and outcomes.
2. Find primary evidence for each claim: a file, a commit, a recorded result or the output of a command you ran. A summary that repeats a claim is not evidence for it.
3. Copy numbers exactly from their source. Name the source of each number.
4. Give each claim one proof label and one status from the contract. Use the lowest label that fits. Never raise a label to make the story stronger.
5. When the project has a safe, cheap and in-scope verification command, run it and record the result. Otherwise write "not run" and the reason.
6. Give a decision to the user only when the evidence shows they made it. Name the work the assistant did. Write "attribution not confirmed" when the record is silent.

A claim without evidence stays out of the results. Either leave it out, or keep it in qualified words and list it as a gap under Limits. When no result claim reaches `verified` or `qualified`, do not write a draft. Report that the case has no defensible result yet and list the gaps.

## Write the draft

Start from the [case template](assets/case-template.md). Keep the sections in plain English and put technical detail in the evidence table.

Write about the user and the assistant in the third person unless the user asks for first person. Name the user the way the request or their instructions do; when neither gives a name, write "the author". Report your own verification as facts about the draft, for example "This draft did not rerun the tests", so a reader cannot mistake the drafting assistant for the user.

Add one visual that helps a reader understand the work. Use an editable Mermaid flow, or copy a real screenshot or render from the project when its rights are settled. Do not generate images.

Include a failure or constraint only when the evidence records one. Compare before and after only under comparable conditions. When a baseline produced the same result, say that no advantage was measured.

When the user wants to show the work live (an interview, a recruiter call, a demo video), add the optional **Demo scripts** section from the template: a 2-minute and a 10-minute walkthrough. Each starts from nothing (a fresh folder or an empty screen), runs on made-up data, and shows each claimed result being used, in the same order as the Results section. Budget about 150 spoken words per minute, so roughly 300 and 1,500 words. Name the exact command or screen for each step. A step you could not run stays marked "not run" with the reason.

Keep raw transcripts, credentials, customer details and home-directory paths out of the draft. Cite evidence by repository-relative path with a commit, or by a public link.

## Boundaries

Publishing, building or deploying a website, scheduling, job applications and outreach are separate actions. When a request asks for one of them, say so plainly and do not start it. Write the draft only when the request also asks for portfolio content, such as a case for a site; otherwise offer it. Article writing belongs to Blog-it. Do not commit, push or upload the draft.

## Report

Give the draft path, the case ID, the overall proof label, the counts of verified, qualified and gap claims, each command you ran and its result, and what you could not check.

## Independent check

When a run is substantial (more than a quick answer: files the user will rely on, send from or share), only a fresh chat, or the other tool (Codex for Claude's work, or the reverse), counts as an independent check of its output. A helper this chat starts gives a "helper review" and this chat's own look is "self-review"; neither counts. So end by saving the output and giving the user one line to paste into a fresh chat: what to check, where it is, what it must match (the brief, the sources, the rules above), "treat this chat's report as claims to verify, not evidence", and "report only".
