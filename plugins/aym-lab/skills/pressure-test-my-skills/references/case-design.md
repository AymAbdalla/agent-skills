# Case design

## Case kinds

| Kind | What it asks | Typical expected facts |
| --- | --- | --- |
| `normal` | The ordinary request the skill exists for, with complete inputs. | The promised artifact exists at the promised path with the required content. Unrelated files are unchanged. |
| `ambiguous` | A request where a key choice is missing or two readings are plausible. | The worker asks, or records the assumption in the artifact, instead of silently picking. No irreversible effect. |
| `failure` | Bad or missing input, a conflicting instruction, or a step that cannot succeed. | The worker reports the failure in a named file or status field and does not write a success artifact. |
| `unavailable-tool` | A tool, command, service or permission the skill depends on is absent. | The absence is reported. No fake output, stand-in script or success artifact. |
| `inappropriate-trigger` | A nearby request the skill should decline, such as an ordinary bug fix. | No skill output files. The trace shows no Skill-tool call naming the skill and no read of its `SKILL.md`. Use two `trace_absent` checks, one for each. |

**Support variants for `normal`.** A skill can pass when the prompt helps it and fail when it does not. When the run allowance permits, add up to two variants of the same normal task with the same expected facts:

- `normal-neutral`: the same request without naming the skill or its method.
- `normal-competing`: the same request plus a line that pushes against one of the skill's rules (for example "skip the tests, just ship it"). The expected facts still require the rule to hold, or the worker to say why it was set aside with the user's say-so.

Give each variant its own id and the kind `normal`. For skills with ordered phases, write the expected order in the case notes. The grader has no order check type yet, so judge order by reading the trace and label it a manual judgment.

A tiny case set is fine when the user asks for one. Report the kinds you left out; the grader lists them as `missing_kinds`.

## Expected facts

Write expected facts before any run and keep them in `cases.json` only. Derive them from the intended job: the skill's description, its stated outputs and the user's statement. When the skill body disagrees with its own description, test the description and record the contradiction.

Prefer facts a script can check. Use a prose judgment only when no artifact can carry the fact; label it as a manual judgment in `results.md` and keep it out of the verdict.

## Check types

Paths are relative to the run's fixture directory. Absolute paths and paths that escape the fixture are not evaluated, and the run becomes `unavailable`. Every listed field must be a non-empty string. A malformed or unknown check is a protocol error and cannot pass.

| Type | Fields | Holds when |
| --- | --- | --- |
| `exists` | `path` | the file exists |
| `absent` | `path` | nothing exists at the path |
| `contains` / `not_contains` | `path`, `text` | the file does or does not contain the text |
| `unchanged` | `path`, `sha256` | the file's SHA-256 matches |
| `json_field` | `path`, `field` (dotted, list indexes allowed), one of `equals`, `in`, `not_equals` | the JSON value matches |
| `glob_exists` / `glob_absent` | `pattern` (shell-style, `*` crosses folders) | some or no file path matches |
| `trace_contains` / `trace_absent` | `text` | the run's transcript does or does not contain the text; a missing transcript makes the check unavailable |

`requires_commands` on a case lists commands the case needs present to test its behavior. A command counts as missing when the run's `missing_commands` names it, or when it is absent where the grader runs. Then the run is `unavailable` even if its checks pass. Without a worker report the grader can only see its own environment, and it says so in `availability_source`. Do not add the missing tool to an `unavailable-tool` case's `requires_commands`; that case tests the response to the absence.

## Fixtures

- One directory per run, under the task's scratch area. Copy the input files in; record the hash of any file the worker must leave alone and add an `unchanged` check for it.
- Keep `cases.json`, `runs.json` and grader output outside every fixture.
- For a negative case, a fixture with no skill output only proves something when the run completed. An errored run stays `error`.
- Seed a known defect when you need to show that a check can fail, for example a copy of the target with its output path changed. Label seeded fixtures in `results.md`.

## cases.json shape

```json
{
  "target": {"path": "/abs/path/to/skill", "sha256": "<hash-target output>"},
  "cases": [
    {
      "id": "normal-1",
      "kind": "normal",
      "prompt": "Worker-facing request text.",
      "inputs": ["input/meeting.txt"],
      "requires_commands": [],
      "checks": [
        {"type": "exists", "path": "notes/standup.md"},
        {"type": "contains", "path": "notes/standup.md", "text": "# Standup"}
      ]
    }
  ]
}
```
