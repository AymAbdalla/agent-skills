#!/usr/bin/env python3
"""Build and check a test-my-knowledge quiz.

build: quiz.json -> page (from the bundled template) and Markdown answer key
check: validate quiz structure, declared scoring, evidence pointers, flags, the page and the key

Standard library only. The checks cover structure and source locations; they do
not judge whether a keyed answer is true or whether a distractor is useful.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

SCHEMA = "test-my-knowledge/quiz-v1"
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "quiz-template.html"
DATA_SLOT = "/*QUIZ_DATA*/null"
DATA_SCRIPT = re.compile(
    r'<script type="application/json" id="quiz-data">(.*?)</script>', re.S)
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
LINES = re.compile(r"(\d+)(?:-(\d+))?\Z")
KEY_HEADING = re.compile(r"^###\s+(\S+)\s*$")
KEY_ANSWER = re.compile(r"^- Correct answer:\s+\*\*([^*]+)\*\*")
# Heuristic backstop; the page is also compared byte for byte with a fresh template build.
EXTERNAL = [
    (re.compile(r"[a-z][a-z0-9+.-]*://", re.I), "absolute URL in markup or script"),
    (re.compile(r"(?<![\w:/])//[\w-]+(?:\.[\w-]+)+", re.I), "protocol-relative URL"),
    (re.compile(r"@import", re.I), "CSS @import"),
    (re.compile(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|Worker|SharedWorker)\s*\(", re.I),
     "script network call"),
    (re.compile(r"\bimport\s*[(\s'\"{*]", re.I), "script import"),
    (re.compile(r"http-equiv\s*=\s*[\"']?refresh", re.I), "meta refresh"),
]
OPTION_COUNT = (3, 5)


def text_of(value):
    return value.strip() if isinstance(value, str) else ""


def valid_id(value):
    return isinstance(value, str) and bool(ID.fullmatch(value))


def norm(value):
    return re.sub(r"\s+", " ", value).strip().lower()


def plain(value):
    """Text with tags removed and entities decoded, for quote matching."""
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", value)))


def parse_lines(raw):
    match = LINES.fullmatch(str(raw).strip())
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if start < 1 or end < start:
        return None
    return start, end


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, message):
        self.errors.append(f"{where}: {message}")

    def warn(self, where, message):
        self.warnings.append(f"{where}: {message}")


class Context:
    def __init__(self, sources, source_root):
        self.sources = sources
        self.root = source_root
        self.cache = {}


def check_evidence(items, where, ctx, report):
    """Validate pointers and return the (source, start, end) spans that passed basic checks."""
    spans = []
    if not isinstance(items, list) or not items:
        report.error(where, "needs at least one evidence pointer")
        return spans
    for index, item in enumerate(items, 1):
        label = f"{where} evidence {index}"
        if not isinstance(item, dict):
            report.error(label, "must be an object")
            continue
        source = item.get("source")
        if not isinstance(source, str) or source not in ctx.sources:
            report.error(label, f"names unknown source {source!r}")
            continue
        span = parse_lines(item.get("lines", ""))
        if span is None:
            report.error(label, "lines must look like '12' or '12-15'")
            continue
        spans.append((source, *span))
        if ctx.root is None:
            continue
        if source not in ctx.cache:
            ctx.cache[source] = load_source(ctx.sources[source], ctx.root, report, label)
        lines = ctx.cache[source]
        if lines is False:
            continue
        start, end = span
        if end > len(lines):
            report.error(label, f"lines {start}-{end} exceed the source length ({len(lines)} lines)")
            continue
        quote = text_of(item.get("quote"))
        if quote:
            window = "\n".join(lines[start - 1:end])
            if norm(quote) not in norm(window) and plain(quote) not in plain(window):
                report.error(label, f"quote not found in lines {start}-{end}")
        else:
            report.warn(label, "has no quote; a reviewer cannot confirm the pointer quickly")
    return spans


def load_source(source, root, report, label):
    rel = text_of(source.get("path"))
    if not rel:
        report.error(label, "source has no path")
        return False
    candidate = Path(rel)
    path = candidate if candidate.is_absolute() else root / candidate
    try:
        resolved = path.resolve(strict=True)
        if not candidate.is_absolute():
            resolved.relative_to(root.resolve(strict=True))
        text = resolved.read_text(encoding="utf-8")
    except ValueError:
        report.error(label, f"source path {rel!r} escapes the source root")
        return False
    except (OSError, UnicodeError) as exc:
        report.error(label, f"source path {rel!r} is unreadable: {exc}")
        return False
    # Count lines the way editors do: only newline characters end a line.
    lines = [line[:-1] if line.endswith("\r") else line for line in text.split("\n")]
    if lines and lines[-1] == "" and text.endswith("\n"):
        lines.pop()
    return lines


def check_ids(items, kind, report):
    seen = {}
    for index, item in enumerate(items, 1):
        item_id = item.get("id") if isinstance(item, dict) else None
        if not valid_id(item_id):
            report.error(f"{kind} {index}", f"id {item_id!r} must be letters, digits, '.', '_' or '-' with no spaces")
            continue
        if item_id in seen:
            report.error(f"{kind} {item_id}", "duplicate id")
            continue
        seen[item_id] = item
    return seen


def answer_cues(questions, label, report):
    positions, longest = [], 0
    for question in questions:
        options = [o for o in question.get("options") or [] if isinstance(o, dict)]
        ids = [o.get("id") for o in options]
        if question.get("answer") not in ids:
            continue
        position = ids.index(question["answer"])
        positions.append(position)
        lengths = [len(text_of(o.get("text"))) for o in options]
        if lengths[position] == max(lengths) and lengths.count(max(lengths)) == 1:
            longest += 1
    if len(positions) >= 4 and len(set(positions)) == 1:
        report.warn(label, "every correct answer is in the same position")
    if len(positions) >= 4 and longest / len(positions) >= 0.5:
        report.warn(label, f"the correct option is the single longest in {longest} of {len(positions)} questions; length can give the answer away")


def check_quiz(data, source_root=None):
    report = Report()
    if not isinstance(data, dict):
        report.error("quiz", "must be a JSON object")
        return report
    if data.get("schema") != SCHEMA:
        report.error("quiz", f"schema must be {SCHEMA!r}")
    if not text_of(data.get("title")):
        report.error("quiz", "needs a title")
    retest_of = data.get("retest_of")
    if retest_of is not None and not text_of(retest_of):
        report.error("quiz", "retest_of must be null or a nonempty string")
    is_retest = retest_of is not None

    raw_sources = data.get("sources") if isinstance(data.get("sources"), list) else []
    sources = check_ids(raw_sources, "source", report)
    for sid, source in sources.items():
        if not text_of(source.get("path")):
            report.error(f"source {sid}", "needs a path")
    if not sources:
        report.error("quiz", "needs at least one source")
    ctx = Context(sources, source_root)

    flagged = []
    flags = data.get("flags") or []
    if not isinstance(flags, list):
        report.error("flags", "must be a list")
        flags = []
    for index, flag in enumerate(flags, 1):
        if not isinstance(flag, dict) or not text_of(flag.get("note")):
            report.error(f"flag {index}", "needs a note")
            continue
        flagged += check_evidence([flag], f"flag {index}", ctx, report)

    raw_objectives = data.get("objectives") if isinstance(data.get("objectives"), list) else []
    objectives = check_ids(raw_objectives, "objective", report)
    for oid, objective in objectives.items():
        if not text_of(objective.get("statement")):
            report.error(f"objective {oid}", "needs a statement")
        check_evidence(objective.get("evidence"), f"objective {oid}", ctx, report)
    if not objectives:
        report.error("quiz", "needs at least one objective")

    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        report.error("quiz", "needs at least one question")
        questions = []
    check_ids(questions, "question", report)
    main_count = {oid: 0 for oid in objectives}
    retest_count = {oid: 0 for oid in objectives}
    main_stems = set()
    retest_stems = []
    by_set = {"main": [], "retest": []}
    for index, question in enumerate(questions, 1):
        if not isinstance(question, dict):
            report.error(f"question {index}", "must be an object")
            continue
        qid = question.get("id")
        where = f"question {qid if valid_id(qid) else index}"
        kind = question.get("set", "main")
        if kind not in ("main", "retest"):
            report.error(where, "set must be 'main' or 'retest'")
        else:
            by_set[kind].append(question)
        oid = question.get("objective")
        if not isinstance(oid, str) or oid not in objectives:
            report.error(where, f"names unknown objective {oid!r}")
        elif kind == "main":
            main_count[oid] += 1
        elif kind == "retest":
            retest_count[oid] += 1
        for field in ("scenario", "prompt", "explanation"):
            if not text_of(question.get(field)):
                report.error(where, f"needs a {field}")
        stem = norm(f"{text_of(question.get('scenario'))} {text_of(question.get('prompt'))}")
        (main_stems.add(stem) if kind == "main" else retest_stems.append((where, stem)))
        options = question.get("options")
        if not isinstance(options, list):
            report.error(where, "options must be a list")
            continue
        if not OPTION_COUNT[0] <= len(options) <= OPTION_COUNT[1]:
            report.error(where, f"needs {OPTION_COUNT[0]} to {OPTION_COUNT[1]} options, found {len(options)}")
        option_ids, option_texts = [], set()
        for position, option in enumerate(options, 1):
            label = f"{where} option {position}"
            if not isinstance(option, dict):
                report.error(label, "must be an object")
                continue
            opt_id, opt_text = option.get("id"), text_of(option.get("text"))
            if not valid_id(opt_id):
                report.error(label, f"id {opt_id!r} must be letters, digits, '.', '_' or '-' with no spaces")
            elif opt_id in option_ids:
                report.error(label, f"duplicate option id {opt_id!r}")
            option_ids.append(opt_id)
            if not opt_text:
                report.error(label, "needs text")
            elif norm(opt_text) in option_texts:
                report.error(label, "repeats another option's text")
            option_texts.add(norm(opt_text))
            if not text_of(option.get("why")):
                report.error(label, "needs a 'why' (the reasoning or misconception it represents)")
            if re.search(r"\b(all|none) of the above\b", opt_text, re.I):
                report.warn(label, "'all/none of the above' tests elimination, not understanding")
        answer = question.get("answer")
        if not isinstance(answer, str) or answer not in option_ids:
            report.error(where, f"answer {answer!r} must be exactly one existing option id")
        for source, start, end in check_evidence(question.get("evidence"), where, ctx, report):
            for f_source, f_start, f_end in flagged:
                if source == f_source and start <= f_end and f_start <= end:
                    report.error(where, f"cites flagged lines {f_start}-{f_end} of {source}; keep flagged claims out of scored questions")

    for where, stem in retest_stems:
        if stem in main_stems:
            report.error(where, "retest question repeats a main question; use a new scenario")
    for oid, count in main_count.items():
        if count == 0:
            report.error(f"objective {oid}", "has no main question")
        if not is_retest and retest_count[oid] == 0:
            report.error(f"objective {oid}", "has no retest question for the in-page retest")

    scoring = data.get("scoring")
    if not isinstance(scoring, dict):
        report.error("scoring", "must be an object")
    else:
        points = scoring.get("points_per_question")
        total = scoring.get("total_points")
        weak = scoring.get("weak_below")
        mains = sum(main_count.values())
        if not isinstance(points, int) or isinstance(points, bool) or points < 1:
            report.error("scoring", "points_per_question must be a positive integer")
        elif total != points * mains:
            report.error("scoring", f"total_points is {total!r} but {mains} main questions x {points} points = {points * mains}")
        if not isinstance(weak, (int, float)) or isinstance(weak, bool) or not 0 < weak <= 1:
            report.error("scoring", "weak_below must be a number greater than 0 and at most 1")
        elif abs(weak * 100 - round(weak * 100)) > 1e-9:
            report.warn("scoring", "weak_below should be a whole percentage (for example 0.5, 0.75 or 1.0) so the page can state the rule exactly")

    answer_cues(by_set["main"] + by_set["retest"], "questions (all sets)", report)
    for kind in ("main", "retest"):
        answer_cues(by_set[kind], f"questions ({kind})", report)
    return report


def embedded_json(page):
    match = DATA_SCRIPT.search(page)
    if not match:
        raise ValueError("page has no <script type=\"application/json\" id=\"quiz-data\"> block")
    return json.loads(match.group(1))


def check_page(page, data, report):
    try:
        embedded = embedded_json(page)
    except (ValueError, json.JSONDecodeError) as exc:
        report.error("html", str(exc))
        return
    if embedded != data:
        report.error("html", "embedded quiz data differs from the quiz JSON; rebuild the page")
    try:
        if page != render_page(data):
            report.error("html", "page differs from a fresh build of the bundled template; rebuild it with quiz_tool.py build")
    except (OSError, ValueError) as exc:
        report.error("html", f"cannot render the bundled template: {exc}")
    markup = DATA_SCRIPT.sub("", page)  # quiz text may quote URLs or code; only markup and script can load them
    for pattern, label in EXTERNAL:
        if pattern.search(markup):
            report.error("html", f"external request risk: {label}")


def parse_key(text):
    answers, current = {}, None
    for line in text.splitlines():
        heading = KEY_HEADING.match(line)
        if heading:
            current = heading.group(1)
            continue
        answer = KEY_ANSWER.match(line)
        if answer and current:
            answers[current] = answer.group(1).strip()
            current = None
    return answers


def check_key(text, data, report):
    found = parse_key(text)
    questions = [q for q in data.get("questions") or [] if isinstance(q, dict)]
    for question in questions:
        qid = question.get("id")
        if qid not in found:
            report.error("answer key", f"missing {qid}")
        elif found[qid] != question.get("answer"):
            report.error("answer key", f"{qid} says {found[qid]!r}; the quiz JSON says {question.get('answer')!r}")
    for qid in sorted(set(found) - {q.get("id") for q in questions}):
        report.error("answer key", f"lists {qid}, which is not in the quiz JSON")
    if text != render_key(data):
        report.error("answer key", "differs from a fresh build of the quiz JSON (text, explanations or pointers changed); rebuild it")


def pointer(item, sources):
    source = sources.get(item.get("source"), {})
    span = str(item.get("lines"))
    text = f"`{source.get('path', item.get('source'))}` {'lines' if '-' in span else 'line'} {span}"
    quote = text_of(item.get("quote"))
    return f"{text}: \"{quote}\"" if quote else text


def render_key(data):
    sources = {s["id"]: s for s in data.get("sources", [])}
    scoring = data.get("scoring", {})
    out = [f"# Answer key: {data.get('title')}", ""]
    if data.get("retest_of"):
        out += [f"Retest of: {data['retest_of']}", ""]
    out += [
        "Practice quiz for self-study. The score describes this quiz, not a certified skill level.",
        "",
        f"Scoring: {scoring.get('points_per_question')} point(s) per main question, "
        f"{scoring.get('total_points')} total. An objective needs review when its share of "
        f"correct main answers is below {scoring.get('weak_below')}.",
        "",
        "## Sources",
        "",
    ]
    for source in data.get("sources", []):
        note = f" ({source['description']})" if source.get("description") else ""
        out.append(f"- {source['id']}: `{source.get('path')}`{note}")
    if data.get("flags"):
        out += ["", "## Source flags (not scored)", ""]
        for flag in data["flags"]:
            out.append(f"- {pointer(flag, sources)}. {flag.get('note')}")
    out += ["", "## Objectives", ""]
    for objective in data.get("objectives", []):
        out.append(f"- **{objective['id']}**: {objective.get('statement')}")
        for item in objective.get("evidence", []):
            out.append(f"  - Source: {pointer(item, sources)}")
    for kind, heading in (("main", "Questions"), ("retest", "Retest questions")):
        chosen = [q for q in data.get("questions", []) if q.get("set", "main") == kind]
        if not chosen:
            continue
        out += ["", f"## {heading}", ""]
        for question in chosen:
            out += [f"### {question['id']}", "",
                    f"Objective: {question.get('objective')}", "",
                    f"{question.get('scenario')} {question.get('prompt')}", ""]
            for option in question.get("options", []):
                out.append(f"- {option.get('id')}. {option.get('text')}")
            correct = next((o for o in question.get("options", []) if o.get("id") == question.get("answer")), {})
            out += ["", f"- Correct answer: **{question.get('answer')}**. {correct.get('text', '')}",
                    f"- Why: {question.get('explanation')}"]
            for option in question.get("options", []):
                if option.get("id") != question.get("answer"):
                    out.append(f"- {option.get('id')} is wrong: {option.get('why')}")
            for item in question.get("evidence", []):
                out.append(f"- Source: {pointer(item, sources)}")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_page(data):
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(DATA_SLOT) != 1:
        raise ValueError("template must contain exactly one data slot")
    payload = json.dumps(data, ensure_ascii=False, indent=1)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    payload = payload.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace(DATA_SLOT, payload)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def emit(report, extra=None):
    result = {"ok": not report.errors, "errors": report.errors, "warnings": report.warnings,
              "limits": "Checks structure, declared scoring, pointer locations and quotes, flagged lines, that the page and key match a fresh build, and a heuristic network scan. It does not judge whether answers are true or questions are good, and it does not run the page."}
    if extra:
        result.update(extra)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def read_quiz(path):
    try:
        return load_json(path), None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report = Report()
        report.error("quiz", f"cannot read JSON: {exc}")
        return None, report


def command_check(args):
    data, failed = read_quiz(args.quiz)
    if failed:
        return emit(failed)
    root = Path(args.source_root) if args.source_root else None
    report = check_quiz(data, root)
    if args.html:
        try:
            check_page(Path(args.html).read_text(encoding="utf-8"), data, report)
        except (OSError, UnicodeError) as exc:
            report.error("html", f"cannot read page: {exc}")
    if args.key:
        try:
            check_key(Path(args.key).read_text(encoding="utf-8"), data, report)
        except (OSError, UnicodeError) as exc:
            report.error("answer key", f"cannot read key: {exc}")
    if root is None:
        report.warn("sources", "no --source-root given; pointer lines and quotes were not checked")
    return emit(report)


def command_build(args):
    if not valid_id(args.name):
        report = Report()
        report.error("build", "--name must be a plain file stem: letters, digits, '.', '_' or '-'")
        return emit(report, {"built": []})
    data, failed = read_quiz(args.quiz)
    if failed:
        return emit(failed, {"built": []})
    root = Path(args.source_root) if args.source_root else None
    report = check_quiz(data, root)
    if report.errors:
        return emit(report, {"built": []})
    out_dir = Path(args.out_dir)
    page_path = out_dir / f"{args.name}.html"
    key_path = out_dir / ("answer-key.md" if args.name == "quiz" else f"{args.name}-answer-key.md")
    targets = [page_path, key_path]
    existing = [str(p) for p in targets if p.exists()]
    if existing and not args.force:
        report.error("build", f"refusing to overwrite {existing}; choose a new --name or --out-dir, or pass --force")
        return emit(report, {"built": []})
    if Path(args.quiz).stem != args.name:
        report.warn("build", f"save the quiz JSON as {args.name}.json beside the page so each quiz keeps its own editable source")
    out_dir.mkdir(parents=True, exist_ok=True)
    page = render_page(data)
    key = render_key(data)
    page_path.write_text(page, encoding="utf-8")
    key_path.write_text(key, encoding="utf-8")
    check_page(page, data, report)
    check_key(key, data, report)
    if root is None:
        report.warn("sources", "no --source-root given; pointer lines and quotes were not checked")
    return emit(report, {"built": [str(p) for p in targets]})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="write the page and answer key from the quiz JSON")
    build.add_argument("quiz")
    build.add_argument("--out-dir", required=True)
    build.add_argument("--name", default="quiz", help="file stem for the page (default: quiz)")
    build.add_argument("--source-root", help="directory that source paths are relative to")
    build.add_argument("--force", action="store_true", help="overwrite existing outputs")
    build.set_defaults(func=command_build)
    check = sub.add_parser("check", help="validate the quiz JSON and optional page and key")
    check.add_argument("quiz")
    check.add_argument("--html")
    check.add_argument("--key")
    check.add_argument("--source-root", help="directory that source paths are relative to")
    check.set_defaults(func=command_check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
