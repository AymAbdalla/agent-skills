#!/usr/bin/env python3
"""Agent records gate: keeps builder and checker records honest before a merge.

  agents_gate.py init  [--repo DIR]
      Create docs/agents/build.md, checks.md and status.md from templates.
      An existing file is kept as it is, never overwritten.

  agents_gate.py check [--repo DIR] [--base REF] [--json]
      Refuse a merge (exit 1) when, for the slices this branch added or changed
      in build.md since BASE:
        1. a slice has no independent pass in checks.md, or its latest check failed;
        2. a pass was recorded for older code: its checked commit is not the latest
           commit that changed anything outside docs/agents/;
        3. a commit that changed rows in checks.md also changed any other file;
        4. a builder row's State is not "built" or "fixed (round N)", or its
           results are not labelled "self-check";
        5. the branch changed code (or added slices) and checks.md has no passing
           "security" row for the latest code commit.
      Exit 0 when every slice and the security check pass, or when the project has no docs/agents/build.md
      (the gate does not apply). Exit 2 on bad input (no git repo, unknown base).

It reads files and git history only. It never edits, commits or contacts a service.
Record format: ../references/agent-records.md.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RECORDS = "docs/agents"
TEMPLATES = {
    "build.md": ("# Build log\n\nWritten only by the builder's main agent, one row per slice. "
                 "State is `built` or `fixed (round N)`; results start with `self-check:`. Never write `checked` here.\n\n"
                 "| Slice | Workstream | Branch | Commit | Acceptance checks | Builder results | State | Date |\n"
                 "| --- | --- | --- | --- | --- | --- | --- | --- |\n"),
    "checks.md": ("# Check log\n\nWritten only by an independent checker, in a commit that changes this file and nothing else. "
                  "One row per slice per check round, with the commit that was checked.\n\n"
                  "| Slice | Checked commit | Result | Evidence | Mismatch | Checker | Date |\n"
                  "| --- | --- | --- | --- | --- | --- | --- |\n"),
    "status.md": ("# Status\n\nOne line per workstream. Each builder edits only its own line; the checker does not edit this file.\n\n"
                  "| Workstream | Tool | Branch | Owns | Phase | Next |\n"
                  "| --- | --- | --- | --- | --- | --- |\n"),
}
STATE_OK = re.compile(r"^(built|fixed \(round \d+\))$", re.I)


class GateError(Exception):
    pass


def git(repo, *args, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise GateError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def table_rows(text):
    """Rows of the first markdown table in text, as lists of stripped cells (header and separator dropped)."""
    rows, seen_header = [], False
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if seen_header and rows:
                break
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not seen_header:
            seen_header = True
            continue
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def slice_key(cell):
    """The slice's number or id: the first word of the cell, without trailing punctuation ("1 low_stock" -> "1")."""
    words = cell.split()
    return words[0].rstrip(".:,") if words else ""


def file_at(repo, ref, rel):
    out = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{rel}"], capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else ""


def init(repo):
    folder = Path(repo) / RECORDS
    folder.mkdir(parents=True, exist_ok=True)
    lines = []
    for name, text in TEMPLATES.items():
        path = folder / name
        if path.exists():
            lines.append(f"kept {RECORDS}/{name} (already exists)")
        else:
            path.write_text(text, encoding="utf-8")
            lines.append(f"created {RECORDS}/{name}")
    return lines


def check(repo, base):
    repo = Path(repo)
    if not (repo / RECORDS / "build.md").is_file():
        return {"ok": True, "applies": False, "problems": [], "slices": [],
                "summary": f"gate not applicable: no {RECORDS}/build.md in this project"}
    git(repo, "rev-parse", "--git-dir")
    if subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", base], capture_output=True).returncode != 0:
        raise GateError(f"unknown base ref: {base}")
    merge_base = git(repo, "merge-base", base, "HEAD").strip()

    build_now = table_rows((repo / RECORDS / "build.md").read_text(encoding="utf-8"))
    build_then = {tuple(r) for r in table_rows(file_at(repo, merge_base, f"{RECORDS}/build.md"))}
    branch_rows = [r for r in build_now if tuple(r) not in build_then]
    checks_path = repo / RECORDS / "checks.md"
    checks = table_rows(checks_path.read_text(encoding="utf-8")) if checks_path.exists() else []

    problems = []
    code_head = git(repo, "log", "-1", "--format=%H", "HEAD", "--", ".", f":(exclude){RECORDS}").strip()

    slices = []
    for row in branch_rows:
        if len(row) < 8:
            problems.append(f"builder row has {len(row)} columns, expected 8: {' | '.join(row)}")
            continue
        slice_id, results, state = slice_key(row[0]), row[5], row[6]
        if not STATE_OK.match(state):
            problems.append(f"builder row for slice {slice_id} has State '{state}'; only 'built' or 'fixed (round N)' is allowed")
        if not results.lower().startswith("self-check"):
            problems.append(f"builder row for slice {slice_id} must label its results 'self-check:'")
        if slice_id not in slices:
            slices.append(slice_id)

    def require_pass(key, label, missing):
        rows = [r for r in checks if len(r) >= 3 and slice_key(r[0]).lower() == key]
        if not rows:
            problems.append(f"{label}: {missing} in {RECORDS}/checks.md")
            return
        latest = rows[-1]
        result, checked = latest[2].lower(), latest[1]
        if result != "pass":
            problems.append(f"{label}: latest check result is '{latest[2]}', not pass")
        elif not (len(checked) >= 7 and code_head.startswith(checked.lower())):
            problems.append(f"{label}: pass is stale: it checked {checked}, but the latest code commit is {code_head[:7]}")

    for slice_id in slices:
        require_pass(slice_id.lower(), f"slice {slice_id}", "no independent pass")
    code_changed = bool(git(repo, "log", "-1", "--format=%H", f"{merge_base}..HEAD", "--", ".", f":(exclude){RECORDS}").strip())
    if slices or code_changed:
        require_pass("security", "security", "no security pass for this branch")

    log = git(repo, "log", "--format=%H", f"{merge_base}..HEAD", "--", f"{RECORDS}/checks.md").split()
    for sha in log:
        before = table_rows(file_at(repo, f"{sha}^", f"{RECORDS}/checks.md"))
        after = table_rows(file_at(repo, sha, f"{RECORDS}/checks.md"))
        if before == after:
            continue  # no check rows changed (for example the empty template being created)
        files = [f for f in git(repo, "show", "--name-only", "--format=", sha).splitlines() if f]
        others = [f for f in files if f != f"{RECORDS}/checks.md"]
        if others:
            problems.append(f"commit {sha[:7]} changed {RECORDS}/checks.md together with other files ({', '.join(others)}); "
                            "a check must be recorded in a commit of its own")

    ok = not problems
    summary = (f"pass: {len(slices)} slice(s) on this branch and the security check have an independent pass on {code_head[:7]}"
               if ok else f"refused: {len(problems)} problem(s)")
    return {"ok": ok, "applies": True, "problems": problems, "slices": slices,
            "code_head": code_head, "base": base, "summary": summary}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init", help="create the three record files if missing")
    p_init.add_argument("--repo", default=".")
    p_check = sub.add_parser("check", help="refuse a merge that breaks the record rules")
    p_check.add_argument("--repo", default=".")
    p_check.add_argument("--base", default="main", help="branch the work will merge into (default: main)")
    p_check.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            print("\n".join(init(args.repo)))
            return 0
        result = check(args.repo, args.base)
    except GateError as exc:
        print(f"agents_gate.py: error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["summary"])
        for problem in result["problems"]:
            print(f"- {problem}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
