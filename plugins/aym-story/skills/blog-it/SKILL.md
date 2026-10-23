---
name: blog-it
description: Read a whole session or project, find its milestones, group them into ideas, and write one standalone Markdown article per idea into a single dedicated folder, each led by a lesson that transfers to other projects. Use when the user says "blog it", "blog-it", "write up what we did", "document this session", "make articles about this work", or asks for a write-up of a past round, feature, project, or fix. Reads the project's own notes and records, and its existing INDEX.md to reuse lanes; does not publish, schedule, or read posts the user has already written.
---

# Blog it

The user turns their work into posts later, by hand, when they choose. This skill gives them the raw material: a set of articles, one per idea, covering what happened, what was made, which choices were taken and why, and what someone on a different project can learn from it.

It writes files and stops. It does not publish, plan a campaign, make carousels, or read posts and articles the user has already written for publishing. It does read the project's own notes and records (step 1) and this run's `INDEX.md` (step 7). A session with a lot of work produces a lot of articles; a session with one small fix produces one short one. Never squeeze a large body of work into a single article.

## Where everything goes

All articles, pictures, maps and the index for a run live in its **home folder**: `<outputs>/<owner>/<task>/blog-it/`, where `<outputs>` is the outputs folder named in the user's instructions (CLAUDE.md or AGENTS.md; default `~/agent-outputs/`). Use the owning project name (or `personal`) and the current task name. Reuse the run directory for requested revisions. `$BLOG_IT_DIR` is an override only when the user explicitly authorized its resolved destination; its presence alone is not authorization. Follow any file map those instructions give.

```
<outputs>/<owner>/<task>/blog-it/
  INDEX.md                         every article, grouped by lane
  maps/YYYY-MM-DD-<scope>.md       one map per run
  <lane>/YYYY-MM-DD-<slug>/
    article.md
    illustration.png
```

When the owning project requires its private data to remain within the project, save articles and the map in its designated private output area. Do not copy private details into a cross-project index. An index covers only this run's home folder; do not recreate a separate home-folder library.

## Steps

1. **Read everything in scope.** Default scope: this session. If the user names a project or past work, the scope is that. Read the session from its start. When early parts have been summarized, or the work spans several sessions, also read the project's decision logs, notes, READMEs, saved memory notes, `git log`, and the session transcript files when the environment keeps them.

2. **List the milestones.** A milestone is any of:
   - something got made or finished
   - a decision, with who made it (the founder or the assistant) and why
   - an approval or a rejection
   - a rule or standard the founder set
   - a failure, and what fixed it
   - a finding that surprised someone
   - a method or check invented to solve a problem
   - a tool or environment problem, and the way around it
   - a change of scope or direction

   Use only facts you can point to. If you cannot confirm something, mark it "not confirmed".

3. **Group milestones into buckets by idea.** A bucket is one transferable idea, not one asset and not one stretch of time. Several milestones from different days can feed one bucket, and one milestone can support two.
   - The test: could someone on a different project (another game, a social app, a client website) do something differently after reading this? If yes, the bucket earns an article.
   - Merge buckets that teach the same lesson.
   - Milestones with no lesson stay in the map as "record only".

4. **Write the map.** Save `maps/YYYY-MM-DD-<scope>.md` in the home folder: one row per bucket with its lane, its one-sentence lesson, the milestones it covers, its proof level, and whether it gets an article. Show the map in chat as a short list, then carry on to step 5 without waiting. The user can stop the run or drop buckets at any point.

5. **Write one article per bucket** from the template below. For each:
   - **Lesson.** The one-sentence lesson from the map leads the title, the opening and the closing.
   - **Proof level.** Pick the highest the evidence supports and claim nothing above it. These are the same labels create-my-portfolio uses, so an article can feed a portfolio case unchanged:
     - `implemented`: it exists; nobody ran it
     - `local simulation`: it ran on the build machine against synthetic data, stand-ins or a simulated service
     - `implementation tested`: the real implementation ran its tests or checks on the build machine, and they passed
     - `device checked`: it ran on the real target (phone, production host, game engine)
     - `public service`: people outside the project can reach it
     - `customer outcome`: a real user or customer used it and the result is recorded

     A milestone with no artifact behind it is marked "not confirmed" (step 2), not given a label.
   - **Visuals in proportion.** A diagram (Mermaid, twelve nodes at most, plain-word labels) when steps or structure are hard to follow in prose. An illustration when there is something to see; copy a real render or screenshot from the project into the article folder as `illustration.png`. Both when they do different jobs, neither for a small point (`illustration: none`). Give each article in a run a different picture, and do not use images whose rights are unsettled, such as third-party references.
   - **Generated images cost money.** Generate one only when no real image exists and the user has approved image generation for this project or asks for it in this request. One generation per article, with no words, numbers, logos or interface text in it. Save the prompt as `illustration-prompt.txt`. Without approval, write the prompt file and set `illustration: none`.

   With more than three buckets, and when helper agents are available, give each article to its own helper with the bucket's milestones and source paths, and have it return every fact it used with its source. Check each returned article's facts and proof level before you count it as done.

6. **Save** each article to `<lane>/YYYY-MM-DD-<slug>/article.md` in the home folder. Never overwrite an existing article folder: revise it only when the user asked for a revision, otherwise add `-2`, `-3`.

7. **Index.** Add one line per article to `INDEX.md` in the home folder, under its lane heading: `- [Title](<lane>/YYYY-MM-DD-<slug>/article.md), date, project`. Update a line whose path already exists instead of adding a duplicate. Create the file or heading if missing.

8. **Report** the map path, the count of articles, and one line per article: title, lane, proof level. Do not paste articles into chat.

## Lanes

A lane names the kind of idea, so it holds articles from many projects. Reuse a lane already in the index when one fits. Otherwise add a short kebab-case lane. Starting set:

- `directing-ai`: how to brief, review and correct work an AI does
- `decisions`: how a choice got made and what it traded away
- `quality-checks`: how the work was measured or proven
- `workflow`: how the work was organised, split or handed off
- `tooling`: setup, environment and tool problems solved
- a craft lane for the field, such as `game-art`, `product-builds`, `client-work`

## Template

```markdown
---
title:
date: YYYY-MM-DD
project:
lane:
tags: []
voice: founder
proof: implementation tested
illustration: illustration.png
status: raw
---

# <Title that states the lesson in terms any builder can use>

![<one-line description>](illustration.png)

**In short:** <one paragraph: the lesson, the case that proves it, and how far it is proven>

## The idea
## What happened
## What was made
## How it was done
<diagram if used, then the steps in prose>
## What went wrong
## Where else this applies
## For specialists
## Evidence
```

- **The idea** states the lesson without the project's vocabulary. A reader who stops here still got something.
- **Where else this applies** gives two or three concrete cases outside the project's field, such as a different kind of game, a social app, or a client website.
- **For specialists** holds the numbers, settings and technical detail a practitioner wants. Leave it out when there is none.
- **Evidence** lists the source files in the project by full path, so the article still points home from the dedicated folder.
- Leave out "What went wrong" when nothing did.
- `status: raw` means the user has not reviewed the article for publishing.

## Readers

Each article serves four readers at once: builders who use AI, non-technical founders, potential customers, and specialists in the field. Write every section except "For specialists" in plain English that assumes no technical knowledge. Put the depth in "For specialists" so it does not block the others.

## Voice

- `voice: founder` (default): call the person who directed the work "the founder". The article carries no personal name.
- `voice: first-person`: write as "I" when the user says they will publish under their own name.

In both voices keep attribution accurate. Say which decisions the founder made and which work the assistant did; first person must not claim the assistant's work as the author's own hands.

## Writing rules

- The lesson is the subject. The project is the example that proves it. Name the project, and keep its numbers and pictures, but explain or drop its internal labels (version tags, decision codes, file names).
- Write an article, not a session log. Leave out steps that do not support the lesson.
- State the proof level in plain words in the opening paragraph, such as "tested on the build machine, not yet on a phone".
- Explain each tool in a few words the first time it appears. Name the tools, models and skills that did the work.
- Plain, direct prose: active voice, concrete nouns, no filler, no em dashes. If a `stop-slop` skill is installed, apply it. Aim for 400 to 900 words before "For specialists".
- Keep file paths, usernames and machine details inside "Evidence" so the other sections lift into a post unchanged.
- Leave out keys, tokens, wallet addresses, account numbers and client private data.
