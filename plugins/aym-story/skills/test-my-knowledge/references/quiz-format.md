# Quiz format

`quiz.json` is the single editable source. The helper builds the page and the answer key from it.

## Shape

```json
{
  "schema": "test-my-knowledge/quiz-v1",
  "title": "Short title",
  "topic": "One sentence on what the quiz covers.",
  "retest_of": null,
  "sources": [
    {"id": "S1", "path": "docs/save-flow.md", "description": "What this file is"}
  ],
  "scoring": {"points_per_question": 1, "total_points": 8, "weak_below": 1.0},
  "objectives": [
    {"id": "O1", "statement": "Predict ...", "evidence": [{"source": "S1", "lines": "12-14", "quote": "exact short phrase"}]}
  ],
  "questions": [
    {
      "id": "Q1", "set": "main", "objective": "O1",
      "scenario": "A concrete situation.", "prompt": "The question.",
      "options": [{"id": "A", "text": "...", "why": "The belief behind this option."}],
      "answer": "A",
      "explanation": "Why the answer fits, in two or three sentences.",
      "evidence": [{"source": "S1", "lines": "12-14", "quote": "exact short phrase"}]
    }
  ],
  "flags": [
    {"source": "S1", "lines": "30", "quote": "exact phrase", "note": "Conflicts with lines 12-14; not scored."}
  ]
}
```

Field rules the helper enforces:

- `sources[].path` is relative to `--source-root` (or absolute). It must stay inside that root when relative.
- `lines` is `"N"` or `"N-M"`. The range must exist in the file. A `quote` must appear in those lines after whitespace is collapsed; HTML tags and entities are ignored for matching.
- Each question has 3 to 5 options with unique ids and texts, a `why` on every option, and one `answer` that names an existing option id.
- `set` is `main` or `retest`. Every objective needs at least one main question. A first quiz (`retest_of` is null) also needs at least one retest question per objective, and a retest question cannot repeat a main question's scenario and prompt.
- IDs (sources, objectives, questions, options) use letters, digits, `.`, `_` or `-`, with no spaces.
- `flags` is optional. Each flag needs a pointer and a note. No question may cite lines that overlap a flag in the same source: a flagged claim stays out of scoring.

## Scoring

- `points_per_question`: positive integer, the same for every question.
- `total_points`: must equal `points_per_question` times the number of main questions.
- `weak_below`: a number above 0 and at most 1, preferably a whole percentage such as `0.5`, `0.75` or `1.0` (the helper warns otherwise, because the page states the rule as a percentage). An objective needs review when its share of correct main answers is below this value. With two questions per objective, `1.0` means any miss marks the objective for review; `0.5` means only two misses do.

The page computes the score from these declared values. Unanswered questions count as incorrect. Retest scoring uses the same points per question over the retest questions shown.

## The page

`build` copies `assets/quiz-template.html` and embeds the JSON in a `<script type="application/json" id="quiz-data">` block. The page writes quiz text with text-only DOM calls and has no network references. `check --html` requires the page to match a fresh build byte for byte, so a hand-edited or stale page fails; it also runs a heuristic scan for network references outside the data block as a backstop.

Controls:

| Control | Effect |
| --- | --- |
| Option buttons | One choice per question. |
| Check my answers | Scores the visible questions, locks choices, shows each verdict, the reason a wrong choice does not fit, the answer, the explanation and the source pointer, then lists each objective as Solid or Review this. |
| Retest weak areas | Enabled after checking the main quiz when a weak objective has reserve questions. Shows only those reserve questions and is disabled once the retest starts. |
| Start over | Clears choices, results and retest state and shows the main quiz again. |

Stable hooks for automated checks: `fieldset[data-qid][data-set][data-objective]`, radio `name="q-<id>"` with `value=<option id>`, `#score-points`, `#score-total`, `li[data-objective-status][data-state]`, and the button ids `check`, `retest`, `reset`.

## The answer key

`answer-key.md` lists sources, flags, objectives with pointers, then each question under a `### <id>` heading with its options, a `- Correct answer: **<id>**` line, the explanation, why each wrong option is wrong, and the source pointer. `check --key` reports any answer line that disagrees with the JSON and fails a key that differs in any way from a fresh build. Edit the JSON and rebuild rather than hand-editing the key.

## Commands

```sh
python3 <skill-dir>/scripts/quiz_tool.py build quiz.json --out-dir <out> [--name retest-1] [--source-root <root>] [--force]
python3 <skill-dir>/scripts/quiz_tool.py check quiz.json [--html quiz.html] [--key answer-key.md] [--source-root <root>]
```

Both print JSON with `ok`, `errors`, `warnings` and `limits`, and exit 1 on any error. `build` refuses to overwrite existing outputs unless `--force` is given. `--name` must be a plain file stem; with `--name retest-1` the outputs are `retest-1.html` and `retest-1-answer-key.md`, and the JSON should be saved as `retest-1.json` (the helper warns otherwise). Without `--source-root`, line ranges and quotes are not checked and a warning says so.
