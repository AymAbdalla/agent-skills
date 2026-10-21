# Settling requirements: questions, approaches and terms

Use this when the clarification needs questions, an approach comparison or a term definition.

## Test a question before asking it

Ask a question only when all four hold:

1. No existing record or earlier answer settles it.
2. No tool or file can answer it.
3. Different answers lead to a different result: behavior a user sees, what is in or out of scope, how data is stored or shared, cost, or a step that is hard to undo. Which items a feature covers, and the format of output that leaves the tool for other people or systems, pass this test when the request leaves them open.
4. Its prerequisites are settled. If the answer to one question decides whether another matters, ask the first and hold the second.

A question that fails test 2 becomes a lookup. A question that fails test 3 becomes a stated default.

## Write each question so the user can answer quickly

- One choice per question, in plain words.
- Two to four concrete options, each with its consequence in one line.
- Your recommendation and the reason, tied to the user's stated goal or the project's facts.
- What the answer unblocks.

Number the questions so the user can reply by number. Do not pad the round with low-stakes questions to look thorough.

## Compare viable approaches

Compare only approaches that could meet the requirement. For each, cover:

| Field | Content |
| --- | --- |
| Behavior | What the user sees or gets. |
| Cost | Effort, dependencies, running cost. |
| Risk | What could go wrong and how you would notice. |
| Reversibility | How hard it is to change later. |

Label each drawback as a limitation (cannot meet the requirement) or a tradeoff (meets it with a cost). Cite current documentation for any claim about an external tool or service. When industry practice matters to the choice, say what it is and where you checked it.

## Define terms

A term needs attention when the user, the docs and the code use it differently, or when one word covers two ideas. State each meaning you found and where, then propose one. Domain terms belong in the project glossary; implementation details and general programming words do not. Edit a glossary only if one exists and current authorization covers it.

## Settlement summary shape

- **Settled:** each answer with its source (message, file and line, or decision record).
- **Facts checked:** each fact with where it came from.
- **Terms:** agreed meanings.
- **Defaults chosen:** minor details you decided, open to change.
- **Open:** each question, its options, and what it blocks.
- **Next job:** usually `plan-this` in spec mode to record the agreed behavior, or direct work for a small task.
