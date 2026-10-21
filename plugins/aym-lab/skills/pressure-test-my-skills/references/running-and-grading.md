# Running and grading

## Fresh workers

A fresh worker starts without this conversation's context and without `cases.json`. Pick the option the allowance and environment support, and record which one each run used.

| Option | Use for | Notes |
| --- | --- | --- |
| Native subagent | Explicit use of the target by path | Cheapest. Tests whether a worker follows the skill, not whether a host catalog selects it. |
| `claude -p` with a verified worker boundary | Explicit use and Claude catalog routing | Expose the target through the fixture's `.claude/skills/<name>` link. Verify shell, filesystem and network containment before starting. A tool allowlist or `dontAsk` permission mode does not provide that boundary; tool refusal can also make a negative case look like a clean decline. Mark execution unavailable if containment cannot start. |
| `codex exec` with workspace sandboxing | Explicit use and Codex catalog routing | Expose the target through `.agents/skills/<name>`. Example shell boundary: `codex exec --json --skip-git-repo-check -s workspace-write -c sandbox_workspace_write.network_access=false -m <model> -C <fixture> - < prompt.txt > <transcript>`. Review connectors, inherited hooks and host settings separately; a shell sandbox does not constrain connected tools. |

Routing cases need a real catalog exposure. If only subagents are available, an `inappropriate-trigger` case tests a prompt adaptation ("this skill exists at PATH; use it only if it fits"). Label it that way, or mark host routing `unavailable`.

Save each transcript when the host can produce one. Trace checks need it, and it shows which files the worker read. A correct artifact alone does not prove the worker loaded the skill. Some hosts expand an explicitly invoked skill's body without any visible event: Claude's stream-json output did not show the body in the W2 pilot. So the absence of the body text proves nothing. Check for the Skill-tool call and for reads of `SKILL.md` instead.

Fresh workers usually inherit user-level settings: global instructions, other installed skills, hooks and plugins. Record what the worker inherited (the Claude init event lists tools and skills). Inherited hooks can add turns and cost, and a failing hook can loop. Claude's `--setting-sources` limits which settings files load. Check the init event for what still loads.

Keep evaluator jobs, allowance ledgers and receipts outside writable worker paths.
The working directory does not enforce this separation. Pass only the environment
variables the host needs; do not inherit unrelated credentials. Count retries and
paid child calls against the allowance. Unknown usage does not establish a
remaining budget. These requirements do not claim read isolation from a host's
managed authentication state.

## runs.json

```json
{
  "allowance": {"total": 4, "per_host": {"claude-subagent": 2, "codex-cli": 2}},
  "cases_sha256": "<hash-file output for cases.json>",
  "runs": [
    {"id": "r1", "case": "normal-1", "host": "claude-subagent", "model": "sonnet",
     "status": "completed", "exit_code": 0,
     "fixture": "/abs/scratch/r1", "transcript": "/abs/scratch/logs/r1.jsonl",
     "missing_commands": [],
     "note": "free text, e.g. timeout after 300 s"}
  ]
}
```

`status` is one of `completed`, `error`, `unavailable` or `not_run`. Write the entry when the run starts and update it when it ends. A non-zero exit code turns `completed` into `error`. Use `unavailable` for a host that could not start at all. Runs marked `not_run` do not count against the allowance; every other status does. Run ids must be unique. `missing_commands` lists required commands the worker found absent in its own environment.

## Grading

The grader below reads files and does not execute submitted code. When a case
needs execution, inspect the submitted source first and hold pristine test code
outside the worker fixture. Freeze each test input in an evaluator manifest with
`entrypoint` and a `files` map of relative paths to SHA-256 digests. Check hashes
immediately before use. Separation and hashes alone do not contain imported code.

On a Mac with Apple's Xcode Python, `scripts/sandbox_eval.py --fixture <fixture>
--manifest <evaluator/manifest.json> --output <new-result-directory>` runs the
frozen entrypoint under a default-deny policy with fixture/test reads, writes to
`<new-result-directory>/artifacts/`, and denied network and child processes.
`EVAL_OUTPUT` points to `artifacts/`. The host keeps `profile.sb` and `receipt.json`
outside that writable area, applies the policy from memory, and checks policy and
declared input hashes after execution. Resolve symlinks before making its profile. Run
benign allowed/denied probes on the actual machine first; keep the receipt. If
the sandbox or runtime cannot start, record unavailable execution. There is no
unsandboxed fallback. The policy permits system/runtime reads, metadata for
ancestor directories and a literal read of `/` for interpreter startup. It grants
no Mach lookup, signals, sysctl or IOKit operations; local probes do not establish
complete OS isolation. It is not a worker read-isolation mechanism.
Use a short timeout and external artifact checks as well: submitted code can
exit early, so a zero exit status alone is not behavioral proof.

`python3 scripts/grade_cases.py grade --cases cases.json --runs runs.json --out results.json`

The grader reads files only. It reports per-run check results, case statuses, findings, coverage, `missing_kinds`, allowance use and protocol errors. Protocol errors include:

- `cases.json` changed after freezing
- target files changed
- `cases.json` inside a worker fixture
- unknown case ids or duplicate run ids
- a missing or malformed allowance, or an allowance overrun
- malformed cases, checks or runs

Any protocol error keeps the verdict from `pass`. A `cases.json` or `runs.json` that is not a JSON object stops the grader with exit code 2 and no result.

The output is deterministic for the same inputs and files, so rerunning the command is the first reproduction step. A finding is `reproduced` when a second worker run, in a separate fixture, fails the same check.

After grading, open the artifacts the findings name. If the grader and your reading disagree, record both and treat the case as unresolved.

## results.md template

```markdown
# Pressure test: <skill name>

Target: <path>, tree hash <sha256> (unchanged: yes/no)
Hosts and models: <list with requested and resolved model where known>
Allowance: <used>/<total>; per host <...>
Verdict: pass | fail | incomplete

| Case | Kind | Status | Runs |
| --- | --- | --- | --- |

## Findings
- <case> check <n> (<type> <path>): failed in <runs>; reproduced yes/no. Artifact: <path>. Re-grade: <command>

## Unavailable and missing coverage
- <what did not run and why>

## Limits
- <sample size, hosts not tested, routing not tested, manual judgments>
```

## Cleanup

Keep the four record files. Remove worker fixtures you created only after the results record points to whatever it needs, following the owning project's file policy; delete individual files you created and remove empty folders.
