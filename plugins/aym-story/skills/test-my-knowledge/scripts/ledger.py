#!/usr/bin/env python3
"""Read and update the learner ledger shared by explain-it-my-way and test-my-knowledge.

record: add or update concept rows by the ledger rules, then print JSON
show:   print the ledger rows (plain text, or JSON with --json)

Rules: one row per concept (case, spacing and a simple trailing "s" do not make
a new concept); "shown" only adds rows; "passed" and "missed" need the learner's
own evidence (a source starting with "quiz:" or "said:"); "declined" needs a
source starting with "user:"; older evidence never replaces newer evidence;
rows are never deleted; every other line of the file stays byte for byte.

Exit codes: 0 ok, 1 the file could not be read or written, 2 bad input.
Standard library only, Python 3.8 or later.
"""

import argparse
import datetime
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path

STATUSES = ("shown", "passed", "missed", "declined")
COLUMNS = ("concept", "status", "date", "source", "note")
EVIDENCE = {"passed": ("quiz:", "said:"), "missed": ("quiz:", "said:"), "declined": ("user:",)}
EVIDENCE_STATUSES = ("passed", "missed", "declined")
TITLE = "# Learner ledger"
HEADER = "| Concept | Status | Date | Source | Note |"
SEPARATOR = "| --- | --- | --- | --- | --- |"
NOTE_LIMIT = 120
CONCEPT_LIMIT = 80
DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
SEPARATOR_CELL = re.compile(r"\s*:?-+:?\s*\Z")
LINE = re.compile(r"[^\n]*\n|[^\n]+\Z")
SINGULAR_ENDINGS = ("ss", "us", "is")


class InputError(Exception):
    """Bad input. Nothing is written."""


# Text helpers

def clean(text):
    """One line with single spaces (newlines and tabs become spaces)."""
    return " ".join(str(text).split())


def escape(text):
    return text.replace("|", "\\|")


def unescape(text):
    return text.replace("\\|", "|")


def concept_key(name):
    """Matching key: case and spacing ignored, a simple trailing "s" plural folded."""
    key = clean(unescape(name)).casefold()
    last = key.rsplit(" ", 1)[-1]
    if len(last) >= 3 and last.endswith("s") and not last.endswith(SINGULAR_ENDINGS):
        key = key[:-1]
    return key


def parse_date(value):
    if not DATE.match(value or ""):
        return None
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def short_note(note):
    note = clean(note)
    if len(note) > NOTE_LIMIT:
        note = note[:NOTE_LIMIT - 3].rstrip() + "..."
    return note


# Markdown table lines

def body_of(line):
    """Split a line into its text and its line ending."""
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def is_table_line(body):
    return body.lstrip().startswith("|")


def split_row(body):
    """Split a table line into (lead, raw cells, trail). trail is None without a closing pipe."""
    parts, buf, i = [], [], 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            buf.append(body[i:i + 2])
            i += 2
            continue
        if ch == "|":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    parts.append("".join(buf))
    if len(parts) > 2 and not parts[-1].strip():
        return parts[0], parts[1:-1], parts[-1]
    return parts[0], parts[1:], None


def join_row(lead, cells, trail):
    return lead + "|" + "|".join(cells) + ("" if trail is None else "|" + trail)


def cell_value(cells, index):
    return unescape(cells[index].strip()) if index < len(cells) else ""


def cell_text(value):
    return " " + escape(value) + " " if value else " "


class Ledger:
    """The ledger file as a list of lines, each kept with its own line ending."""

    def __init__(self, path):
        self.path = path
        self.exists = path.exists()
        text = ""
        if self.exists:
            try:
                text = path.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                raise InputError("{} is not UTF-8 text".format(path))
        self.lines = LINE.findall(text)
        self.newline = "\r\n" if self.lines and self.lines[0].endswith("\r\n") else "\n"
        self.columns, self.header_at, self.end = self.find_table()

    def find_table(self):
        """Return (column names, header line index, index after the last row), or (None, None, None)."""
        for i, line in enumerate(self.lines):
            body = body_of(line)[0]
            if not is_table_line(body) or i + 1 >= len(self.lines):
                continue
            names = [clean(c).lower() for c in split_row(body)[1]]
            separator = body_of(self.lines[i + 1])[0]
            if ("concept" in names and "status" in names and is_table_line(separator)
                    and all(SEPARATOR_CELL.match(c) for c in split_row(separator)[1])):
                end = i + 2
                while end < len(self.lines) and is_table_line(body_of(self.lines[end])[0]):
                    end += 1
                return names, i, end
        return None, None, None

    def index(self, name):
        return self.columns.index(name)

    def rows(self):
        """Yield (line index, values by column name, raw cells) for each data row."""
        if self.columns is None:
            return
        for i in range(self.header_at + 2, self.end):
            cells = split_row(body_of(self.lines[i])[0])[1]
            values = {}
            for n, name in enumerate(self.columns):
                if name and name not in values:
                    values[name] = cell_value(cells, n)
            yield i, values, cells

    def ensure_table(self):
        """Add the standard header when the file has no ledger table yet."""
        if self.columns is not None:
            missing = [c for c in COLUMNS if c not in self.columns]
            if missing:
                raise InputError("the ledger table at line {} has no {} column; add it to the header".format(
                    self.header_at + 1, ", ".join(missing)))
            return
        nl = self.newline
        block = []
        if not self.lines:
            block += [TITLE + nl, nl]
        else:
            self.end_with_newline(len(self.lines))
            if body_of(self.lines[-1])[0].strip():
                block.append(nl)
        block += [HEADER + nl, SEPARATOR + nl]
        self.lines += block
        self.columns, self.header_at, self.end = self.find_table()

    def end_with_newline(self, end):
        if end and not body_of(self.lines[end - 1])[1]:
            self.lines[end - 1] += self.newline

    def add_row(self, values):
        cells = [cell_text(values.get(name, "")) for name in self.columns]
        self.end_with_newline(self.end)
        self.lines.insert(self.end, join_row("", cells, "") + self.newline)
        self.end += 1

    def set_cells(self, line_index, updates):
        body, ending = body_of(self.lines[line_index])
        lead, cells, trail = split_row(body)
        for name, value in updates.items():
            n = self.index(name)
            while len(cells) <= n:
                cells.append(" ")
            cells[n] = cell_text(value)
        self.lines[line_index] = join_row(lead, cells, trail) + ending

    def text(self):
        return "".join(self.lines)


# File writing

def default_mode():
    mask = os.umask(0)
    os.umask(mask)
    return 0o666 & ~mask


def write_atomic(path, text):
    """Write to a temporary file beside the target, then rename it into place."""
    target = Path(os.path.realpath(str(path)))
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else default_mode()
    fd, tmp = tempfile.mkstemp(prefix=".ledger-", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, str(target))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# Commands

def ledger_path(value):
    return Path(os.path.abspath(os.path.expanduser(value)))


def check_source(status, source):
    source = clean(source)
    if not source:
        raise InputError("--source is empty")
    prefixes = EVIDENCE.get(status)
    if prefixes:
        lowered = source.lower()
        found = next((p for p in prefixes if lowered.startswith(p)), None)
        if found is None:
            if status == "declined":
                raise InputError('declined needs the user\'s own request: --source must start with "user:"')
            raise InputError('{} needs the learner\'s own evidence: --source must start with "quiz:" or "said:"'.format(status))
        if not source[len(found):].strip():
            raise InputError('--source says "{}" but names no evidence after it'.format(found))
    return source


def check_concepts(concepts):
    seen, result = set(), []
    for raw in concepts:
        name = clean(raw)
        if not name:
            raise InputError("a concept is empty")
        if len(name) > CONCEPT_LIMIT:
            raise InputError('concept "{}..." is {} characters; use the short plain name (at most {})'.format(
                name[:30], len(name), CONCEPT_LIMIT))
        key = concept_key(name)
        if key not in seen:
            seen.add(key)
            result.append(name)
    return result


def check_date(value):
    if value is None:
        return datetime.date.today().isoformat()
    if parse_date(value) is None:
        raise InputError('--date "{}" is not a real date in YYYY-MM-DD form'.format(value))
    return value


def record(path, status, source, concepts, date=None, note=None):
    """Apply one record command. Returns the result dictionary; writes only when something changed."""
    if status not in STATUSES:
        raise InputError("--status must be one of " + ", ".join(STATUSES))
    source = check_source(status, source)
    concepts = check_concepts(concepts)
    day = check_date(date)
    note = None if note is None else short_note(note)

    ledger = Ledger(path)
    created = not ledger.exists
    ledger.ensure_table()
    existing = {}
    for i, values, _ in ledger.rows():
        key = concept_key(values["concept"]) if values["concept"] else ""
        if key and key not in existing:
            existing[key] = (i, values)

    added, changed, unchanged = [], [], []
    for name in concepts:
        key = concept_key(name)
        if key not in existing:
            stored = name.lower()
            ledger.add_row({"concept": stored, "status": status, "date": day,
                            "source": source, "note": note or ""})
            existing[key] = (ledger.end - 1, {"concept": stored, "status": status})
            added.append(stored)
            continue
        i, old = existing[key]
        if status == "shown":
            unchanged.append(old["concept"])
            continue
        old_status = old.get("status", "").lower()
        old_date = parse_date(old.get("date", ""))
        if old_status in EVIDENCE_STATUSES and old_date and old_date > parse_date(day):
            unchanged.append(old["concept"])
            continue
        updates = {"status": status, "date": day, "source": source}
        if note is not None:
            updates["note"] = note
        updates = {k: v for k, v in updates.items() if old.get(k, "") != v}
        if not updates:
            unchanged.append(old["concept"])
            continue
        ledger.set_cells(i, updates)
        changed.append({"concept": old["concept"], "from": old.get("status", ""), "to": status})

    if added or changed or created:
        write_atomic(path, ledger.text())
    return {"path": str(path), "created": created, "added": added,
            "changed": changed, "unchanged": unchanged}


def show(path):
    ledger = Ledger(path)
    rows = [values for _, values, _ in ledger.rows()] if ledger.exists else []
    return {"path": str(path), "exists": ledger.exists, "rows": rows}


def show_text(result):
    if not result["exists"]:
        return "No ledger yet at {}".format(result["path"])
    rows = result["rows"]
    counts = {}
    for row in rows:
        counts[row.get("status", "")] = counts.get(row.get("status", ""), 0) + 1
    summary = ", ".join("{} {}".format(n, s or "no status") for s, n in sorted(counts.items()))
    lines = ["Learner ledger: {}".format(result["path"]),
             "{} concepts{}".format(len(rows), ": " + summary if summary else "")]
    for row in rows:
        line = "- {}: {}, {}, {}".format(row.get("concept", ""), row.get("status", ""),
                                         row.get("date", ""), row.get("source", ""))
        if row.get("note"):
            line += " ({})".format(row["note"])
        lines.append(line)
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record", help="add or update concept rows")
    rec.add_argument("--ledger", required=True, help="path to the ledger Markdown file")
    rec.add_argument("--status", required=True, choices=STATUSES)
    rec.add_argument("--source", required=True,
                     help='"explanation: <topic>", "quiz: <quiz path>, <objective id>", "said: <words>" or "user: <request>"')
    rec.add_argument("--date", help="day of the evidence, YYYY-MM-DD (default: today)")
    rec.add_argument("--note", help="short optional note; on passed, missed or declined it replaces the old note")
    rec.add_argument("concepts", nargs="+", metavar="CONCEPT")
    sh = sub.add_parser("show", help="print the ledger rows")
    sh.add_argument("--ledger", required=True, help="path to the ledger Markdown file")
    sh.add_argument("--json", action="store_true", help="print the rows as JSON")
    args = parser.parse_args(argv)
    path = ledger_path(args.ledger)
    try:
        if args.command == "record":
            result = record(path, args.status, args.source, args.concepts, args.date, args.note)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            result = show(path)
            print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else show_text(result))
    except InputError as exc:
        print("ledger.py: error: {}".format(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print("ledger.py: could not read or write the ledger: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
