# Spec section shape and acceptance checks

Use this shape inside the project's existing document. Match the document's heading levels and style. Omit a part that has nothing agreed; do not pad it.

## Section parts

1. **Purpose.** The problem and who has it, in one or two sentences.
2. **Behavior.** What a user does and what they observe, written as plain statements. Cover the normal path, empty or missing input and error cases that were agreed.
3. **Scope.** In scope and out of scope. Out-of-scope items prevent later scope creep; list the ones the user or records named.
4. **Acceptance checks.** Observable results someone can verify without reading the code (see below).
5. **Terms.** Agreed meanings for words the section relies on, when the project has no glossary or the glossary lacks them.
6. **Decisions and sources.** Each decision with where it was agreed: a message, a decision record and date, or an approved plan.
7. **Open items.** Each unresolved choice with its known options, what it blocks and who decides. Write "Open" plainly; do not phrase an open item as a rule.

## Write acceptance checks

- Describe an input or action and the expected observable result: output text, exit status, file contents, visible page state.
- Use the highest public seam that shows the behavior. Avoid checks on private helpers or internal structure.
- Take expected values from the agreed decisions. Do not invent thresholds, limits or messages; if a value was not agreed, record it under open items.
- Include the empty, missing and error cases that the agreement covers.
- Keep each check independent and short enough to run or read in a minute.

## Keep agreement and suggestion apart

| Kind | How to write it |
| --- | --- |
| Agreed | Plain statement with a source in the decisions part. |
| Proposed default | "Proposed, not agreed:" followed by the suggestion and its reason. |
| Derived by you | Same label as a proposed default, unless a source states it. |
| Unresolved | Listed under open items only. |
| Conflicting records | Open item naming both sources. |

## Separate actions

Writing the document saves the agreed state. Publishing a tracker issue, opening a PR, posting to a channel or sending the spec are each their own external action with their own confirmation. Report them as next actions with the text ready. Each can happen later, as its own action outside this skill, after the user confirms it.
