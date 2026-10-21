#!/usr/bin/env python3
"""Select a small set of mechanics from a mechanics library (library/LIBRARY.md).

The library is optional. Without one, the result has status "no_library" and says
how to start one, so build-skill can carry on with a bounded original design.
"""

import argparse
import json
import re
import sys
from pathlib import Path


FENCE = re.compile(r"(?ms)^```json[ \t]*\r?\n(.*?)^```[ \t]*$")
OPENER = re.compile(r"(?m)^```json[ \t]*\r?$")
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
ENTRY_FIELDS = set("id shelf need mechanic use_when avoid_when counterexample conflicts cost decision date review examples".split())
EXAMPLE_FIELDS = set("role source_id component_type author license revision locator evidence limits dissection files".split())
FILE_FIELDS = {"path", "sha256"}
SEARCH_FIELDS = ("id", "shelf", "need", "mechanic", "use_when", "avoid_when", "counterexample")


NO_LIBRARY = "no library found; start one with dissect-this or pass --library-root"


class CatalogError(ValueError):
    pass


class NoLibrary(CatalogError):
    """The library folder or its LIBRARY.md does not exist."""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CatalogError(f"duplicate JSON field {key!r}")
        result[key] = value
    return result


def require_fields(value, fields, label):
    if not isinstance(value, dict):
        raise CatalogError(f"{label} must be a JSON object")
    missing = fields - value.keys()
    extra = value.keys() - fields
    if missing or extra:
        raise CatalogError(f"{label} fields: missing={sorted(missing)}, unexpected={sorted(extra)}")


def validate_entry(entry, number, seen):
    label = f"JSON block {number}"
    require_fields(entry, ENTRY_FIELDS, label)
    for key in ENTRY_FIELDS - {"conflicts", "examples"}:
        if not isinstance(entry[key], str) or not entry[key].strip():
            raise CatalogError(f"{label}: {key} must be a nonempty string")
    eid = entry["id"]
    if not ID.fullmatch(eid):
        raise CatalogError(f"{label}: invalid ID {eid!r}")
    if eid in seen:
        raise CatalogError(f"{label}: duplicate ID {eid!r}")
    seen.add(eid)
    if not isinstance(entry["conflicts"], list) or any(not isinstance(x, str) or not x.strip() for x in entry["conflicts"]):
        raise CatalogError(f"{label}: conflicts must be an array of nonempty strings")
    examples = entry["examples"]
    if not isinstance(examples, list) or not examples:
        raise CatalogError(f"{label}: examples must be a nonempty array")
    if sum(isinstance(x, dict) and x.get("role") == "best" for x in examples) != 1:
        raise CatalogError(f"{label}: exactly one example must have role 'best'")
    for index, example in enumerate(examples, 1):
        ex_label = f"{label} example {index}"
        require_fields(example, EXAMPLE_FIELDS, ex_label)
        for key in EXAMPLE_FIELDS - {"files"}:
            if not isinstance(example[key], str) or not example[key].strip():
                raise CatalogError(f"{ex_label}: {key} must be a nonempty string")
        if example["role"] not in {"best", "alternative"}:
            raise CatalogError(f"{ex_label}: invalid role {example['role']!r}")
        if not isinstance(example["files"], list) or not example["files"]:
            raise CatalogError(f"{ex_label}: files must be a nonempty array")
        for file_number, file_record in enumerate(example["files"], 1):
            require_fields(file_record, FILE_FIELDS, f"{ex_label} file {file_number}")
            if any(not isinstance(v, str) or not v.strip() for v in file_record.values()):
                raise CatalogError(f"{ex_label} file {file_number}: values must be nonempty strings")
            if not re.fullmatch(r"[0-9a-fA-F]{64}", file_record["sha256"]):
                raise CatalogError(f"{ex_label} file {file_number}: sha256 must be 64 hexadecimal characters")


def load_catalog(root):
    """Read the catalog under root.

    root is the folder that holds library/LIBRARY.md, or the library folder
    itself (a folder named "library" that holds LIBRARY.md).
    """
    if root.is_symlink():
        raise CatalogError(f"library root is a symlink: {root}")
    try:
        root = root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise NoLibrary(f"{NO_LIBRARY} (looked in {root})") from exc
    try:
        if not root.is_dir():
            raise CatalogError(f"library root is not a directory: {root}")
        if (root.name == "library" and (root / "LIBRARY.md").is_file()
                and not (root / "library" / "LIBRARY.md").exists()):
            root = root.parent
        library = root / "library" / "LIBRARY.md"
        if library.parent.is_symlink() or library.is_symlink():
            raise CatalogError(f"library path contains a symlink: {library}")
        if not library.exists():
            raise NoLibrary(f"{NO_LIBRARY} (looked in {root})")
        source = library.read_text(encoding="utf-8")
    except (OSError, UnicodeError, RuntimeError) as exc:
        raise CatalogError(f"library is missing or unreadable under {root}: {exc}") from exc
    blocks = list(FENCE.finditer(source))
    openers = list(OPENER.finditer(source))
    if len(openers) != len(blocks):
        raise CatalogError("catalog has an unclosed or malformed JSON fence")
    if not blocks:
        raise CatalogError("catalog contains no JSON entries")
    entries = []
    seen = set()
    for number, block in enumerate(blocks, 1):
        try:
            entry = json.loads(block.group(1), object_pairs_hook=unique_object)
        except (json.JSONDecodeError, CatalogError) as exc:
            raise CatalogError(f"JSON block {number}: malformed catalog data: {exc}") from exc
        validate_entry(entry, number, seen)
        entries.append(entry)
    return root, entries


# Small words that carry no meaning in a need; they are ignored when matching.
STOP_WORDS = frozenset("a an and are as at be by do does for from how in into is it of on or so that the this to what when with".split())


def rank(entry, query):
    """Score an entry for a plain-language query.

    At least half of the meaningful query words must appear in the entry's
    searchable fields. More matching words, a full match, and matches in the
    need or id rank higher. A natural phrase therefore finds entries that use
    most of its words, instead of only entries that use every word.
    """
    tokens = re.findall(r"[a-z0-9]+", query.casefold())
    words = [w for w in tokens if w not in STOP_WORDS] or tokens
    if not words:
        return 0
    fields = [entry[key].casefold() for key in SEARCH_FIELDS]
    joined = " ".join(fields)
    stems = [stem(word) for word in words]
    matched = [s for s in stems if s in joined]
    if len(matched) * 2 < len(words):
        return 0
    head = entry["need"].casefold() + " " + entry["id"]
    phrase = query.casefold().strip()
    return (3 * len(matched) + (5 if len(matched) == len(words) else 0)
            + (30 if phrase in head else 0)
            + 2 * sum(s in head for s in matched))


def stem(word):
    """Drop a common ending so "rebuilding" matches "rebuild" and "edits" matches "edit"."""
    for ending in ("ing", "ies", "ed", "es", "s"):
        if word.endswith(ending) and len(word) - len(ending) >= 4:
            return word[: -len(ending)]
    return word


def select(entries, query, ids, limit):
    chosen = []
    requested = set(ids)
    for entry in entries:
        if requested and entry["id"] in requested:
            chosen.append((1000, entry))
        elif query and not requested:
            score = rank(entry, query)
            if score:
                chosen.append((score, entry))
    chosen.sort(key=lambda item: -item[0])
    return [entry for _, entry in chosen[:limit]]


def default_library_root():
    """Nearest ancestor of this script that holds library/LIBRARY.md, or None.

    A clone of the source repository keeps library/ at its root, so a run from
    a clone finds it. An installed aym-lab plugin carries no library: pass the
    library folder named in the user's instructions with --library-root.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "library" / "LIBRARY.md").is_file():
            return parent
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library-root", type=Path, default=default_library_root(), help="the library folder, or the folder that holds library/LIBRARY.md (default: nearest ancestor that has one)")
    parser.add_argument("--query", help="words to find in entry fields")
    parser.add_argument("--id", action="append", default=[], help="exact mechanic ID; may be repeated")
    parser.add_argument("--limit", type=int, default=6, help="maximum entries to return (1–6)")
    args = parser.parse_args(argv)
    root = str(args.library_root.absolute()) if args.library_root else None
    result = {"ok": False, "status": "error", "library_root": root, "entries": [], "errors": [],
              "source_verification": "unavailable: no raw-source map supplied; use the full library checker separately"}
    if not args.query and not args.id:
        result["errors"].append("provide --query or at least one --id")
    if args.query is not None and not args.query.strip():
        result["errors"].append("--query must contain text")
    if not 1 <= args.limit <= 6:
        result["errors"].append("--limit must be between 1 and 6")
    if len(args.id) > 6:
        result["errors"].append("request at most six IDs")
    if result["errors"]:
        print(json.dumps(result, indent=2))
        return 1
    if args.library_root is None:
        result["status"] = "no_library"
        result["errors"].append(NO_LIBRARY)
        print(json.dumps(result, indent=2))
        return 1
    try:
        resolved, entries = load_catalog(args.library_root)
        result["library_root"] = str(resolved)
        found = {entry["id"] for entry in entries}
        missing_ids = sorted(set(args.id) - found)
        if missing_ids:
            result["errors"].append(f"unknown mechanic IDs: {', '.join(missing_ids)}")
        else:
            result["entries"] = select(entries, args.query, args.id, args.limit)
            result["ok"] = True
            result["status"] = "matched" if result["entries"] else "no_match"
    except NoLibrary as exc:
        result["status"] = "no_library"
        result["errors"].append(str(exc))
    except CatalogError as exc:
        result["errors"].append(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
