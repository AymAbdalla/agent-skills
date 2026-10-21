#!/usr/bin/env python3
"""Validate mechanics-library shape and local evidence without running sources."""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit

ENUMS = {
    "shelf": {"gather", "decide", "make", "check", "stop", "trigger", "layout", "safety"},
    "decision": {"proposed", "adopted", "rejected", "adapted", "deferred"},
    "evidence": {"source-inspected", "runtime-observed", "behavior-verified"},
    "review": {"pending", "approved", "rejected"},
    "component_type": {"skill", "plugin", "hook", "mcp", "tool", "software", "workflow", "document"},
    "role": {"best", "alternative"},
}
ENTRY = set("id shelf need mechanic use_when avoid_when counterexample conflicts cost decision date review examples".split())
EXAMPLE = set("role source_id component_type author license revision locator evidence limits dissection files".split())
FENCE = re.compile(r"(?ms)^```json[ \t]*\r?\n(.*?)^```[ \t]*$")
LINK = re.compile(r"!?\[[^\]]*\]\((<[^>]+>|[^)\s]+)(?:\s+[^)]*)?\)")


class Checker:
    def __init__(self, root, library, sources):
        self.root_arg, self.library_arg, self.sources_arg = map(Path, (root, library, sources)) if sources else (Path(root), Path(library), None)
        self.errors, self.entries, self.checks, self.ids, self.reports, self.sources = [], 0, 0, set(), set(), {}

    def check(self, ok, message):
        self.checks += 1
        if not ok:
            self.errors.append(message)
        return ok

    @staticmethod
    def safe_file(base, rel, boundary):
        if not isinstance(rel, str):
            return None, "path must be a string"
        p = Path(rel)
        if not rel or p.is_absolute() or "\x00" in rel:
            return None, "path must be nonempty and relative"
        cur = Path(base)
        if cur.is_symlink():
            return None, "base directory is a symlink"
        try:
            for part in p.parts:
                cur = cur.parent if part == ".." else cur / part
                if cur.is_symlink():
                    return None, "path contains a symlink"
            real = (Path(base) / p).resolve(strict=True)
            real.relative_to(Path(boundary).resolve(strict=True))
            if not real.is_file():
                return None, "path does not name a file"
            return real, None
        except ValueError:
            return None, "path escapes its allowed root"
        except (OSError, RuntimeError):
            return None, "file is missing or inaccessible"

    def string_fields(self, obj, keys, label):
        for key in keys:
            self.check(key in obj, f"{label}: missing field {key!r}")
            if key in obj:
                self.check(isinstance(obj[key], str) and bool(obj[key].strip()), f"{label}: {key!r} must be a nonempty string")

    def links(self, text, origin, root, label):
        for found in LINK.findall(text):
            target = found[1:-1] if found.startswith("<") else found
            try:
                u = urlsplit(target)
            except ValueError as exc:
                self.errors.append(f"{label}: malformed local link {target!r}: {exc}")
                continue
            if u.scheme or u.netloc or not u.path:
                continue
            path, reason = self.safe_file(origin, unquote(u.path), root)
            self.check(path is not None, f"{label}: broken or unsafe local link {target!r}: {reason}")

    def example(self, x, n, eid, root):
        label = f"entry {eid!r} example {n}"
        if not self.check(isinstance(x, dict), f"{label}: must be an object"):
            return
        self.check(not (set(x) - EXAMPLE), f"{label}: unknown fields {sorted(set(x) - EXAMPLE)}")
        self.string_fields(x, EXAMPLE - {"files"}, label)
        for key, allowed in ENUMS.items():
            if key in x:
                self.check(isinstance(x[key], str) and x[key] in allowed, f"{label}: invalid {key} {x[key]!r}")
        report = x.get("dissection")
        if isinstance(report, str) and report.strip():
            self.reports.add(report)
            p, why = self.safe_file(root, report, root)
            self.check(p is not None, f"{label}: dissection report {report!r} is missing or unsafe ({why})")
        files = x.get("files")
        self.check(isinstance(files, list) and bool(files), f"{label}: files must be a nonempty array")
        if not isinstance(files, list):
            return
        for i, f in enumerate(files, 1):
            fl = f"{label} file {i}"
            if not self.check(isinstance(f, dict), f"{fl}: must be an object"):
                continue
            self.check(not (set(f) - {"path", "sha256"}), f"{fl}: unknown fields {sorted(set(f) - {'path', 'sha256'})}")
            self.string_fields(f, {"path", "sha256"}, fl)
            source_id = x.get("source_id")
            if not isinstance(source_id, str):
                self.errors.append(f"{fl}: source_id must be a nonempty string")
                continue
            src = self.sources.get(source_id)
            if not isinstance(src, dict):
                self.errors.append(f"{fl}: no source map for {x.get('source_id')!r}")
                continue
            sr = src.get("root")
            if not isinstance(sr, str) or not Path(sr).is_absolute():
                self.errors.append(f"{fl}: source map root must be an absolute path")
                continue
            base = Path(sr)
            if base.is_symlink():
                self.errors.append(f"{fl}: mapped source root is a symlink")
                continue
            try:
                base = base.resolve(strict=True)
                if not base.is_dir():
                    raise OSError("not a directory")
            except (OSError, RuntimeError) as exc:
                self.errors.append(f"{fl}: mapped source root is unavailable: {exc}")
                continue
            path, why = self.safe_file(base, f.get("path", ""), base)
            if why:
                self.errors.append(f"{fl}: source file {f.get('path')!r} is missing or unsafe: {why}")
                continue
            self.check(src.get("revision") == x.get("revision"), f"{fl}: revision mismatch for {x.get('source_id')!r}: entry={x.get('revision')!r}, map={src.get('revision')!r}")
            digest = f.get("sha256", "")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                self.check(False, f"{fl}: sha256 must be 64 hexadecimal characters")
            else:
                try:
                    actual = hashlib.sha256(path.read_bytes()).hexdigest()
                except OSError as exc:
                    self.errors.append(f"{fl}: cannot read source file {f.get('path')!r}: {exc}")
                    continue
                self.check(actual == digest.lower(), f"{fl}: SHA-256 mismatch for {f.get('path')!r}: recorded {digest}, actual {actual}")

    def entry(self, obj, n, root):
        label = f"JSON block {n}"
        if not self.check(isinstance(obj, dict), f"{label}: must contain an object"):
            return
        self.entries += 1
        self.check(not (set(obj) - ENTRY), f"{label}: unknown fields {sorted(set(obj) - ENTRY)}")
        self.string_fields(obj, ENTRY - {"conflicts", "examples"}, label)
        eid = obj.get("id")
        if isinstance(eid, str):
            self.check(bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", eid)), f"{label}: id must be a lowercase kebab identifier")
            self.check(eid not in self.ids, f"{label}: duplicate ID {eid!r}")
            self.ids.add(eid)
        for key, allowed in ENUMS.items():
            if key in obj:
                self.check(isinstance(obj[key], str) and obj[key] in allowed, f"{label}: invalid {key} {obj[key]!r}")
        if isinstance(obj.get("date"), str):
            try:
                date.fromisoformat(obj["date"])
                good = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", obj["date"]))
            except ValueError:
                good = False
            self.check(good, f"{label}: date must be a valid YYYY-MM-DD date")
        self.check(isinstance(obj.get("conflicts"), list) and all(isinstance(v, str) and v.strip() for v in obj["conflicts"] if isinstance(obj.get("conflicts"), list)), f"{label}: conflicts must be an array of nonempty strings (empty is allowed)")
        examples = obj.get("examples")
        self.check(isinstance(examples, list) and bool(examples), f"{label}: examples must be a nonempty array")
        if not isinstance(examples, list):
            return
        best = sum(isinstance(v, dict) and v.get("role") == "best" for v in examples)
        self.check(best == 1, f"{label}: expected exactly one best example, found {best}")
        seen = set()
        for i, x in enumerate(examples, 1):
            if isinstance(x, dict):
                key = tuple(x.get(k) for k in ("source_id", "component_type", "locator"))
                if all(isinstance(value, str) for value in key):
                    self.check(key not in seen, f"{label}: duplicate example {key!r}")
                    seen.add(key)
            self.example(x, i, eid if isinstance(eid, str) else "?", root)

    def run(self):
        try:
            root = self.root_arg.resolve(strict=True)
            if not root.is_dir():
                raise OSError("not a directory")
        except (OSError, RuntimeError):
            self.errors.append(f"catalog root is missing or inaccessible: {self.root_arg}")
            return self.result()
        lib, why = self.safe_file(self.library_arg.parent.resolve(), self.library_arg.name, root)
        if why:
            self.errors.append(f"library is missing or outside catalog root: {self.library_arg} ({why})")
            return self.result()
        try:
            text = lib.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.errors.append(f"cannot read library: {exc}")
            return self.result()
        if self.sources_arg:
            try:
                if self.sources_arg.is_symlink():
                    raise OSError("source map is a symlink")
                self.sources = json.loads(self.sources_arg.read_text(encoding="utf-8"))
                if not isinstance(self.sources, dict):
                    raise ValueError("top-level JSON value must be an object")
                self.checks += 1
            except (OSError, UnicodeError, ValueError) as exc:
                self.errors.append(f"source map is missing or invalid: {exc}")
        matches = list(FENCE.finditer(text))
        openers = list(re.finditer(r"(?m)^```json[ \t]*\r?$", text))
        if len(openers) > len(matches):
            self.errors.append(f"JSON block {len(matches) + 1}: opening ```json fence has no closing fence")
        for i, match in enumerate(matches, 1):
            try:
                self.entry(json.loads(match.group(1)), i, root)
            except json.JSONDecodeError as exc:
                self.errors.append(f"JSON block {i}: malformed JSON: {exc}")
        self.links(text, lib.parent, root, "library")
        for report in sorted(self.reports):
            p, why = self.safe_file(root, report, root)
            if p:
                try:
                    self.links(p.read_text(encoding="utf-8"), p.parent, root, f"report {report!r}")
                except (OSError, UnicodeError) as exc:
                    self.errors.append(f"cannot read report {report!r}: {exc}")
        return self.result()

    def result(self):
        return {"entries": self.entries, "checks": self.checks, "errors": self.errors, "ok": not self.errors}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--library", required=True, type=Path)
    ap.add_argument("--sources", type=Path)
    a = ap.parse_args()
    result = Checker(a.root, a.library, a.sources).run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
