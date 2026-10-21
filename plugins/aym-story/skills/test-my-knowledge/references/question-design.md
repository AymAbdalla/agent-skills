# Question design

Read this while writing objectives and questions. The goal is a quiz that shows whether someone can use an idea, and that teaches them when they get it wrong.

## Objectives

An objective names an action the learner can take with the idea. Good verbs: predict, choose, explain why, spot the mistake, decide when. Weak verbs: know, remember, be familiar with.

- Weak: "Know what an environment variable is."
- Better: "Decide whether a value belongs in code or in an environment variable, and say why."

Keep objectives separate enough that a wrong answer points to one gap. Three to six objectives fit a short quiz. Attach a pointer to the lines that teach each one.

## Scenario stems

Put the learner in a concrete situation from the source's world, then ask a question that needs the idea to answer.

- Recall stem: "What does the source call a value stored outside the code?"
- Scenario stem: "Maya pushes her app to a public repository. The payment key is written inside `config.py`. A teammate says to move it to an environment variable. What problem does that move solve?"

Change surface details between questions on the same objective so the learner cannot match words. A retest question needs a new situation, not the old question reworded.

Questions that only ask for the source's exact wording test memory of phrasing. Use at most one per quiz, and only when the term itself is the objective.

## Distractors

Each wrong option should be an answer a person could reasonably choose if they held a specific wrong belief. Write that belief in the option's `why`. Useful sources of distractors:

- The step before or after the right one (right idea, wrong moment).
- A true statement that does not answer this question.
- The common shortcut the source warns against.
- The opposite rule applied in the wrong situation.

Avoid joke options, "all of the above", "none of the above", and options that differ by one word. Keep lengths and grammar similar so the form does not give the answer away. Spread correct answers across positions.

## Source checking

The answer key must agree with the source, and the source must actually say it. For each question:

1. Find the lines that make the keyed answer correct. Quote a short exact phrase from them.
2. Confirm each wrong option conflicts with the source or with nothing the source says (not merely "less good").
3. If two parts of the source disagree, or a claim looks wrong, record a flag. Leave that claim out of scoring until the user resolves it. Do not key the doubtful claim, and do not quietly replace it with your own answer.

Separate what the source says, what you inferred, and what you checked elsewhere. An outside fact needs a primary source you read; otherwise label it unverified and keep it out of the answer key.

## Explanations

Write the explanation for someone who just chose a wrong option. Say what the right answer does in the scenario, name the idea, and point to the source. Keep it to two or three sentences. The option `why` texts carry the per-option reasoning.

## Worked example (unrelated topic)

Source: a team README, lines 40 to 52, explaining that secrets live in a `.env` file excluded by `.gitignore`, and the app reads them at start-up.

```json
{
  "id": "Q2",
  "set": "main",
  "objective": "O1",
  "scenario": "Sam adds a new email-service password to the project. He puts it in `.env`, but the `.gitignore` line for `.env` was deleted last week.",
  "prompt": "What will happen the next time Sam commits all changed files?",
  "options": [
    {"id": "A", "text": "The password stays private because it is in .env.", "why": "Believes the file name alone keeps a secret out of Git."},
    {"id": "B", "text": "The password is committed along with the file.", "why": "Correct: without the ignore rule, Git tracks .env like any other file."},
    {"id": "C", "text": "The app refuses to start until the rule is restored.", "why": "Mixes up what Git tracks with what the app reads at start-up."},
    {"id": "D", "text": "Git encrypts .env before it uploads the commit.", "why": "Assumes Git protects secrets on its own."}
  ],
  "answer": "B",
  "explanation": "The `.gitignore` rule is what keeps `.env` out of commits. Remove the rule and Git treats `.env` as a normal file, so the password goes into history.",
  "evidence": [{"source": "S1", "lines": "44-46", "quote": "keeps .env out of every commit"}]
}
```
