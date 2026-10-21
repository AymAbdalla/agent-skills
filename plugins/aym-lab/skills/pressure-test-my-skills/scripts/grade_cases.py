#!/usr/bin/env python3
"""Grade pressure-test runs against a frozen case set.

Reads cases.json (evaluator-only expected facts) and runs.json (attempt ledger),
inspects files left in each run's fixture directory, and writes one deterministic
JSON result. It never starts a model, runs target code or edits fixtures.

  grade_cases.py hash-target DIR
  grade_cases.py hash-file FILE
  grade_cases.py grade --cases CASES --runs RUNS [--out RESULTS]
"""

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

KINDS = ("normal", "ambiguous", "failure", "unavailable-tool", "inappropriate-trigger")
RUN_STATES = ("completed", "error", "unavailable", "not_run")
SEVERITY = {"fail": 4, "error": 3, "unavailable": 2, "not_run": 1, "pass": 0}
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_FILES = {".DS_Store"}
CHECK_FIELDS = {
    "exists": ("path",), "absent": ("path",),
    "contains": ("path", "text"), "not_contains": ("path", "text"),
    "unchanged": ("path", "sha256"), "json_field": ("path", "field"),
    "glob_exists": ("pattern",), "glob_absent": ("pattern",),
    "trace_contains": ("text",), "trace_absent": ("text",),
}


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_tree(root):
    """Hash relative paths and file bytes; symlinks hash their link text."""
    root = Path(root)
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    lines = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if name in SKIP_FILES or name.endswith(".pyc"):
                continue
            path = Path(current) / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                lines.append(f"{rel}\0link:{os.readlink(path)}\n")
            else:
                lines.append(f"{rel}\0{sha256_file(path)}\n")
        for name in list(dirs):
            path = Path(current) / name
            if path.is_symlink():
                lines.append(f"{path.relative_to(root).as_posix()}\0link:{os.readlink(path)}\n")
                dirs.remove(name)
    digest = hashlib.sha256()
    for line in sorted(lines):
        digest.update(line.encode("utf-8"))
    return digest.hexdigest()


def inside(root, rel):
    """Resolve rel under root; return None if it is absolute or escapes root."""
    if not isinstance(rel, str) or not rel or os.path.isabs(rel):
        return None
    candidate = (root / rel).resolve()
    real_root = root.resolve()
    if candidate == real_root or real_root in candidate.parents:
        return candidate
    return None


def walk_files(root):
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files) + sorted(d for d in dirs if (Path(current) / d).is_symlink()):
            yield (Path(current) / name).relative_to(root).as_posix()


def field(data, dotted):
    for part in dotted.split("."):
        if isinstance(data, dict) and part in data:
            data = data[part]
        elif isinstance(data, list) and part.isdigit() and int(part) < len(data):
            data = data[int(part)]
        else:
            raise KeyError(dotted)
    return data


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def check_problem(check):
    """Return why a check is malformed, or None when it can be evaluated."""
    if not isinstance(check, dict):
        return "check is not an object"
    kind = check.get("type")
    if kind not in CHECK_FIELDS:
        return f"unknown check type {kind!r}"
    for name in CHECK_FIELDS[kind]:
        if not isinstance(check.get(name), str) or not check.get(name):
            return f"{kind} needs a non-empty string {name!r}"
    if kind == "json_field":
        if not any(key in check for key in ("equals", "in", "not_equals")):
            return "json_field needs equals, in or not_equals"
        if "in" in check and not isinstance(check["in"], list):
            return "json_field 'in' must be a list"
    return None


def run_check(check, root, transcript):
    """Return (result, detail). result is True, False or None (not evaluable)."""
    problem = check_problem(check)
    if problem:
        return None, problem
    kind = check["type"]
    if kind in ("trace_contains", "trace_absent"):
        if not isinstance(transcript, str) or not Path(transcript).is_file():
            return None, "transcript unavailable"
        found = check["text"] in Path(transcript).read_text(errors="replace")
        return (found if kind == "trace_contains" else not found), f"text {'found' if found else 'not found'}"
    if kind in ("glob_exists", "glob_absent"):
        hits = [p for p in walk_files(root) if fnmatch.fnmatch(p, check["pattern"])]
        detail = f"matches: {hits[:5]}" if hits else "no matches"
        return (bool(hits) if kind == "glob_exists" else not hits), detail
    path = inside(root, check["path"])
    if path is None:
        return None, "path is absolute or outside the fixture"
    if kind == "exists":
        return path.is_file(), "present" if path.is_file() else "missing"
    if kind == "absent":
        return not path.exists(), "absent" if not path.exists() else "present"
    if not path.is_file():
        return False, "file missing"
    if kind in ("contains", "not_contains"):
        found = check["text"] in path.read_text(errors="replace")
        return (found if kind == "contains" else not found), "text found" if found else "text not found"
    if kind == "unchanged":
        actual = sha256_file(path)
        return actual == check["sha256"], f"sha256 {actual}"
    try:
        value = field(json.loads(path.read_text()), check["field"])
    except (ValueError, KeyError) as exc:
        return False, f"unreadable field: {exc}"
    if "equals" in check:
        return value == check["equals"], f"value {value!r}"
    if "in" in check:
        return value in check["in"], f"value {value!r}"
    return value != check["not_equals"], f"value {value!r}"


def load_cases(case_doc, errors):
    """Validate cases.json content; return {id: normalized case}."""
    raw = case_doc.get("cases")
    if not isinstance(raw, list):
        errors.append("cases.json 'cases' must be a list")
        raw = []
    cases = {}
    for number, case in enumerate(raw):
        if not isinstance(case, dict):
            errors.append(f"case #{number} is not an object")
            continue
        cid = case.get("id")
        if not isinstance(cid, str) or not cid or cid in cases:
            errors.append(f"case #{number}: id missing, not a string or duplicated: {cid!r}")
            continue
        if case.get("kind") not in KINDS:
            errors.append(f"case {cid}: kind must be one of {list(KINDS)}")
        checks = case.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append(f"case {cid}: checks must be a non-empty list; expected facts are required")
            checks = []
        for index, check in enumerate(checks):
            problem = check_problem(check)
            if problem:
                errors.append(f"case {cid} check {index}: {problem}")
        requires = case.get("requires_commands", [])
        if not isinstance(requires, list) or not all(isinstance(c, str) and c for c in requires):
            errors.append(f"case {cid}: requires_commands must be a list of command names")
            requires = []
        cases[cid] = {"kind": case.get("kind"), "checks": checks, "requires": requires}
    return cases


def load_allowance(run_doc, errors):
    allowance = run_doc.get("allowance")
    if not isinstance(allowance, dict):
        allowance = {}
    if not is_int(allowance.get("total")):
        errors.append("runs.json allowance.total must be an integer; the allowance is required")
    per_host = allowance.get("per_host", {})
    if not isinstance(per_host, dict) or not all(is_int(v) for v in per_host.values()):
        errors.append("runs.json allowance.per_host must map host names to integers")
        per_host = {}
    return allowance, per_host


def grade(cases_path, runs_path):
    cases_path, runs_path = Path(cases_path), Path(runs_path)
    case_doc = json.loads(cases_path.read_text())
    run_doc = json.loads(runs_path.read_text())
    if not isinstance(case_doc, dict) or not isinstance(run_doc, dict):
        raise ValueError("cases.json and runs.json must each hold a JSON object")
    errors = []
    cases_sha = sha256_file(cases_path)
    if run_doc.get("cases_sha256") != cases_sha:
        errors.append("cases.json hash differs from runs.json cases_sha256: case set changed after freezing or was never frozen")

    target = case_doc.get("target") if isinstance(case_doc.get("target"), dict) else {}
    target_report = {"path": target.get("path"), "recorded_sha256": target.get("sha256"),
                     "current_sha256": None, "unchanged": None}
    if isinstance(target.get("path"), str) and Path(target["path"]).is_dir():
        target_report["current_sha256"] = hash_tree(target["path"])
        target_report["unchanged"] = target_report["current_sha256"] == target.get("sha256")
        if not target_report["unchanged"]:
            errors.append("target skill files changed after the case set recorded their hash")
    else:
        errors.append("target path missing; target identity unavailable")

    cases = load_cases(case_doc, errors)
    allowance, per_host = load_allowance(run_doc, errors)
    raw_runs = run_doc.get("runs")
    if not isinstance(raw_runs, list):
        errors.append("runs.json 'runs' must be a list")
        raw_runs = []

    used_total, used_hosts, seen = 0, {}, set()
    graded_runs, by_case = [], {cid: [] for cid in cases}
    real_cases = cases_path.resolve()
    for number, run in enumerate(raw_runs):
        if not isinstance(run, dict):
            errors.append(f"run #{number} is not an object")
            continue
        rid, cid = run.get("id"), run.get("case")
        host = run.get("host") if isinstance(run.get("host"), str) else "unknown"
        if not isinstance(rid, str) or not rid or rid in seen:
            errors.append(f"run #{number}: id missing, not a string or duplicated: {rid!r}")
            continue
        seen.add(rid)
        if not isinstance(cid, str) or cid not in cases:
            errors.append(f"run {rid}: unknown case {cid!r}")
            continue
        state = run.get("status")
        record = {"id": rid, "case": cid, "host": host, "checks": []}
        if state not in RUN_STATES:
            errors.append(f"run {rid}: status must be one of {list(RUN_STATES)}")
            state = "error"
        if state != "not_run":
            used_total += 1
            used_hosts[host] = used_hosts.get(host, 0) + 1
        fixture = Path(run["fixture"]) if isinstance(run.get("fixture"), str) and run["fixture"] else None
        record["fixture"] = str(fixture.resolve()) if fixture else None
        if fixture and fixture.is_dir() and (fixture.resolve() == real_cases.parent or fixture.resolve() in real_cases.parents):
            errors.append(f"run {rid}: cases.json sits inside the worker fixture; expected facts leaked")
        if state == "completed" and run.get("exit_code") not in (None, 0):
            state = "error"
            record["reason"] = f"exit code {run.get('exit_code')}"
        if state == "completed" and (fixture is None or not fixture.is_dir()):
            state = "unavailable"
            record["reason"] = "fixture directory missing"
        reported = run.get("missing_commands")
        requires = cases[cid]["requires"]
        if isinstance(reported, list):
            missing = sorted({c for c in requires if c in reported or shutil.which(c) is None})
            if requires:
                record["availability_source"] = "worker report and grader environment"
        else:
            missing = sorted(c for c in requires if shutil.which(c) is None)
            if requires:
                record["availability_source"] = "grader environment only; worker availability not recorded"
        if state == "completed":
            results = []
            for index, check in enumerate(cases[cid]["checks"]):
                result, detail = run_check(check, fixture, run.get("transcript"))
                results.append(result)
                record["checks"].append({"index": index, "check": check, "result": result, "detail": detail})
            if missing:
                status = "unavailable"
                record["reason"] = "required command missing: " + ", ".join(missing)
            elif False in results:
                status = "fail"
            elif None in results or not results:
                status = "unavailable"
                record["reason"] = "no checks, or one or more checks could not be evaluated"
            else:
                status = "pass"
        else:
            status = state
            note = run.get("note") if isinstance(run.get("note"), str) else None
            record["reason"] = record.get("reason") or note or state
            if missing:
                record["reason"] += "; required command missing: " + ", ".join(missing)
        record["status"] = status
        graded_runs.append(record)
        by_case[cid].append(record)

    if is_int(allowance.get("total")) and used_total > allowance["total"]:
        errors.append(f"used {used_total} runs, above the total allowance of {allowance['total']}")
    for host, cap in sorted(per_host.items()):
        if used_hosts.get(host, 0) > cap:
            errors.append(f"host {host} used {used_hosts[host]} runs, above its allowance of {cap}")

    case_rows, findings = [], []
    for cid in sorted(cases):
        runs = by_case[cid]
        status = "not_run" if not runs else max((r["status"] for r in runs), key=SEVERITY.get)
        case_rows.append({"id": cid, "kind": cases[cid]["kind"], "status": status, "runs": [r["id"] for r in runs]})
        graded = [r for r in runs if r["status"] in ("pass", "fail")]
        for index, check in enumerate(cases[cid]["checks"]):
            failed = [r for r in graded if r["checks"][index]["result"] is False]
            if failed:
                findings.append({
                    "case": cid, "check_index": index, "check": check,
                    "failed_runs": [r["id"] for r in failed], "graded_runs": len(graded),
                    "reproduced": len({r["fixture"] for r in failed}) >= 2,
                    "evidence": [{"run": r["id"], "fixture": r["fixture"], "detail": r["checks"][index]["detail"]}
                                 for r in failed],
                })

    coverage = {key: 0 for key in SEVERITY}
    for row in case_rows:
        coverage[row["status"]] += 1
    if coverage["fail"]:
        verdict = "fail"
    elif errors or not case_rows or any(row["status"] != "pass" for row in case_rows):
        verdict = "incomplete"
    else:
        verdict = "pass"
    return {
        "allowance": allowance,
        "cases": case_rows,
        "cases_sha256": cases_sha,
        "coverage": coverage,
        "findings": findings,
        "missing_kinds": [k for k in KINDS if k not in {c["kind"] for c in cases.values()}],
        "protocol_errors": errors,
        "runs": graded_runs,
        "target": target_report,
        "used": {"total": used_total, "per_host": dict(sorted(used_hosts.items()))},
        "verdict": verdict,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    tree = sub.add_parser("hash-target", help="print the tree hash of a skill directory")
    tree.add_argument("directory")
    one = sub.add_parser("hash-file", help="print the sha256 of one file, e.g. cases.json when freezing")
    one.add_argument("file")
    run = sub.add_parser("grade", help="grade runs.json against cases.json")
    run.add_argument("--cases", required=True)
    run.add_argument("--runs", required=True)
    run.add_argument("--out", help="write results here instead of stdout")
    args = parser.parse_args(argv)
    try:
        if args.command == "hash-target":
            print(json.dumps({"path": str(Path(args.directory).resolve()), "sha256": hash_tree(args.directory)}))
        elif args.command == "hash-file":
            print(json.dumps({"path": str(Path(args.file).resolve()), "sha256": sha256_file(args.file)}))
        else:
            text = json.dumps(grade(args.cases, args.runs), indent=2, sort_keys=True) + "\n"
            if args.out:
                Path(args.out).write_text(text)
            print(text if not args.out else json.dumps({"written": args.out, "verdict": json.loads(text)["verdict"]}))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
