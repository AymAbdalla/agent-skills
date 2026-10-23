---
name: explain-it-my-way
description: "Use whenever the user asks how their code, project, product decision or workflow works, or why it was done that way (\"explain\", \"walk me through\", \"how does this work\", \"in plain English\"). Answering directly loses what this skill adds, which is fifth-grade plain English with a diagram, the industry terms taught afterwards, a sourced comparison with professional practice, and a learner ledger so known concepts are not re-taught (the user can turn tracking off). Not for general-knowledge questions, building, redesigning or auditing."
---

# Explain It My Way

Help an adult learning through real projects understand the idea first, see it work, learn its professional name, and judge why the approach fits or differs from professional practice.

## Ground the explanation

- Follow the user's subject and depth. Use the current conversation before asking for context. Ask one focused question only when different interpretations would change the explanation.
- For "our approach," read the relevant code, decisions, or supplied artifacts. Separate observed implementation, intended design, and unknown behavior. Keep inspection limited to what the explanation needs.
- For a general concept, use a labeled teaching example. Do not present invented example behavior as a fact about the user's project.
- Explain and prepare visuals within existing authorization. Suggestions remain suggestions; do not start a refactor, rollout, configuration change, or another project lifecycle.

## Check what the learner already knows

Read the [learner ledger](references/learner-ledger.md) before explaining (`python3 <skill-dir>/scripts/ledger.py show --ledger <path> --json`). For a concept marked `passed`, mention it in one line instead of re-teaching it. For `declined`, leave it out unless the user asks. When the ledger shows a concept as `shown` in the last two weeks and not yet passed, open with one line: "Last time I showed you X. Did it stick?" If the user explains all of it correctly in their own words, record it right away with `record --status passed --source "said: <their words, short>"`. If the answer is wrong or only half right, use `--status missed` and put the missing part in `--note`, so the next quiz brings it back. Then continue.

After the explanation, record the main industry terms you taught (at most about five) without asking: `python3 <skill-dir>/scripts/ledger.py record --ledger <path> --status shown --source "explanation: <topic>" "<term>" ...`. List the added and changed rows from the script's JSON in one line. If the user says not to track, skip the ledger for that session or topic. If the ledger's location cannot be reached from this session, skip it and say so in one line.

## Teach in this order

### 1. Say it in plain English

Start with what the thing does and why a person would need it. Use familiar words, short sentences, active voice, and one concrete example. Aim at a fifth-grade reading level while treating the reader as an adult.

Introduce the familiar meaning before its technical name. Replace "persist the payload" with "save the message so it is still there after the app closes." Explain necessary words such as "server" or "database" when they first appear: "the computer that saves your tasks, called the server." Keep this reading level in every layer, including the professional comparison. Avoid unexplained acronyms, code-level detail in the opening, baby talk, and technical words disguised as definitions.

Keep the real cause and effect. Simplifying language must not invent a guarantee or hide a material limitation. If an analogy helps, map its parts to the actual system and name where the analogy stops being accurate. Do not force an analogy when a real example is clearer.

### 2. Show what happens

Make the visual a main part of the explanation. For a substantive explanation with steps, relationships, or tradeoffs, render and display at least one useful illustration, diagram, or visualization. Choose the form by what the user needs to understand:

- Steps or messages: a short flow or sequence.
- An abstract concept: a labeled concrete example or side-by-side illustration.
- A tradeoff: a before/after view or a comparison the user can inspect.
- A changing rule: a small interactive example where one action changes a visible result.

Use plain-word labels first. Tie each visual part to the same example used in the prose. Walk the reader through the visual in a few sentences. Technical labels can appear in a second view or alongside the plain labels after their meaning is established.

Read [the visual guide](references/visual-guide.md) when producing a visual. Use the available renderer or visualization tool; this skill has no required external service. Keep editable source with saved visuals. Verify rendering and meaningful interactions before claiming they work. If rendering is unavailable, provide the best readable fallback, include the source when useful, and say which part could not be verified. Honor a request for text only; a one-sentence definition does not need an artifact.

### 3. Teach the industry words

Use a compact mapping: **plain meaning -> industry term -> what that term refers to here**. A small table usually works well. Include only terms that help explain the subject, usually three to six for a substantial explanation.

For example: "Trying the same request again -> retry -> sending the same save request after the first reply went missing." Expand acronyms and distinguish similar terms when confusing them would change the meaning. Keep the professional term precise even when the plain explanation is short. Check what a term applies to: a number for one intended save is different from a new number for each attempt. The same intended save keeps its number across retries.

### 4. Explain professional practice and compare

Answer all of these in plain English:

- How do professionals commonly use this approach, and what problem does it solve?
- Which parts of our approach match that practice?
- Which parts differ, and why? Is the difference a deliberate tradeoff, a missing safeguard, or something we cannot confirm?
- What makes the approach suitable or unsuitable for this project's size, users, cost, reliability needs, and stage?

Verify claims about industry standards and best practices using current primary sources: official documentation, actual standards, original research, or documented engineering practice. Keep private project details out of public searches. Link each source near the claim it supports.

Distinguish a **formal standard**, **documented recommendation**, **documented engineering example**, and **your inference**. One vendor's choice does not establish industry consensus. Say when credible approaches differ. If the subject has no universal best practice, explain the conditions that drive the choice instead of inventing one. When browsing is unavailable or the user forbids it, explain the concept, mark the practice comparison as unverified, and avoid claiming it is a confirmed current standard.

Compare the same kind of system and workload. A solo prototype and a high-volume service can make different sensible choices. Judge meaningful safeguards and consequences rather than recommending enterprise complexity by default. If our implementation is unknown, compare the supplied proposal and label it as a proposal.

### 5. Connect it back to the user's work

End with what this means for the user: what gets easier, what could go wrong, and the decision or next check that matters. Say whether to keep the approach, adjust it, or gather missing evidence, with a reason tied to the project. An explanation does not authorize making that change.

## Size and delivery

Keep one concept focused. Default to a short explanation and one visual, with terms and source detail in a later or expandable layer. For a broad system, give a simple overview and expose detail through labeled panels, expandable sections, or a few linked visuals. Keep the plain explanation, term mapping, and professional comparison easy to find. Do not turn a small question into a course or a glossary dump.

Answer in chat by default and show the visual where the environment supports it. Save an HTML or other artifact when interaction, export, or reuse helps; save lasting project visuals in the owning repository's documentation paths and standalone deliverables in `<outputs>/<owner>/<task>/`, where `<outputs>` is the outputs folder named in the user's instructions (CLAUDE.md or AGENTS.md; default `~/agent-outputs/`); keep scratch in the scratch folder those instructions name (otherwise the system temp directory) and link the result. A useful explanation includes words the user can read even if the visual viewer fails.

## Before delivering

- Can someone understand the first explanation without knowing the industry words?
- Does the visual teach the same idea as the prose, including important limits?
- Are technical names accurate and connected to concrete examples?
- Does the professional comparison have relevant primary-source support and a clear same/different explanation?
- Have you kept observed behavior, examples, recommendations, and unknowns distinct?
- Have you verified the saved visual and described its actual editability?
- Unless the user said not to track, did you record the terms you taught in the learner ledger?

Apply these checks to meaning and behavior. A reading-level score or valid diagram syntax alone does not establish a good explanation.
