#!/usr/bin/env python3
"""Check supported skill metadata and local Markdown links without executing a skill."""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
KEY = re.compile(r"([A-Za-z][A-Za-z0-9_-]*):(?:[ \t]*(.*))?\Z")
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\((<[^>]+>|[^)\s]+)(?:\s+[^)]*)?\)")
REFERENCE_LINK = re.compile(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)")


def parse_scalar(raw, label):
    if raw is None or not raw.strip():
        raise ValueError(f"{label} must have a value")
    raw = raw.strip()
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label} has an invalid quoted value: {exc}") from exc
    elif raw.startswith("'"):
        if not raw.endswith("'") or len(raw) < 2:
            raise ValueError(f"{label} has an invalid quoted value")
        value = raw[1:-1].replace("''", "'")
    else:
        if raw in {"|", ">", "|-", ">-"}:
            raise ValueError(f"{label} uses unsupported multiline metadata")
        if (not re.match(r"[A-Za-z]", raw)
                or re.fullmatch(r"(?i:true|false|null|yes|no|on|off|y|n)", raw)
                or re.search(r"\s#|:\s", raw)):
            raise ValueError(f"{label} is ambiguous YAML; quote this string")
        value = raw
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with a --- frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("SKILL.md frontmatter has no closing --- delimiter") from exc
    metadata = {}
    for number, line in enumerate(lines[1:end], 2):
        match = KEY.fullmatch(line)
        if not match:
            raise ValueError(f"frontmatter line {number} is outside the supported single-line key: value format")
        key = match.group(1)
        if key in metadata:
            raise ValueError(f"frontmatter line {number} duplicates {key!r}")
        metadata[key] = parse_scalar(match.group(2), key)
    for key in ("name", "description"):
        if key not in metadata:
            raise ValueError(f"frontmatter is missing {key!r}")
    if not NAME.fullmatch(metadata["name"]):
        raise ValueError("name must be a lowercase kebab identifier")
    return metadata, "\n".join(lines[end + 1:])


def check_link(raw, origin, skill_dir):
    target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
    if re.match(r"^[A-Za-z]:", target):
        return None, f"local link {target!r} must use a safe relative path", True
    try:
        parsed = urlsplit(target)
    except ValueError as exc:
        return None, f"malformed link {target!r}: {exc}", True
    if parsed.scheme == "file":
        return None, f"local link {target!r} must use a safe relative path", True
    if parsed.scheme or parsed.netloc or target.startswith("#"):
        return None, None, False
    if not parsed.path:
        return None, f"local link {target!r} has no path", True
    rel = unquote(parsed.path)
    path = Path(rel)
    if path.is_absolute() or "\x00" in rel or "\\" in rel or re.match(r"^[A-Za-z]:", rel):
        return None, f"local link {target!r} must use a safe relative path", True
    cursor = origin.parent
    for part in path.parts:
        cursor = cursor.parent if part == ".." else cursor / part
        if cursor.is_symlink():
            return None, f"local link {target!r} contains a symlink", True
    try:
        actual = (origin.parent / path).resolve(strict=True)
        actual.relative_to(skill_dir.resolve(strict=True))
    except ValueError:
        return None, f"local link {target!r} escapes the skill directory", True
    except (OSError, RuntimeError):
        return None, f"local link {target!r} is missing or inaccessible", True
    if not actual.is_file():
        return None, f"local link {target!r} does not name a file", True
    return actual, None, True


def check(skill_dir):
    result = {"ok": False, "skill_dir": str(skill_dir.absolute()), "errors": [],
              "unsupported_metadata": [],
              "limits": "Checks supported frontmatter fields and local Markdown file links only; it does not verify prose behavior, host loading, schema compliance, or execution safety."}
    if skill_dir.is_symlink():
        result["errors"].append("skill directory is a symlink")
        return result
    skill_file = skill_dir / "SKILL.md"
    if skill_file.is_symlink():
        result["errors"].append("SKILL.md is a symlink")
        return result
    try:
        if not skill_dir.is_dir():
            raise OSError("skill directory does not exist")
        root = skill_dir.resolve(strict=True)
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        result["errors"].append(f"SKILL.md is missing or unreadable: {exc}")
        return result
    try:
        metadata, body = parse_frontmatter(text)
    except ValueError as exc:
        result["errors"].append(str(exc))
        return result
    result["unsupported_metadata"] = sorted(set(metadata) - {"name", "description"})
    pending = [(skill_file.resolve(), body)]
    seen = set()
    local_count = 0
    external = []
    while pending:
        origin, content = pending.pop()
        if origin in seen:
            continue
        seen.add(origin)
        for link in INLINE_LINK.findall(content) + REFERENCE_LINK.findall(content):
            target, error, is_local = check_link(link, origin, root)
            if is_local:
                local_count += 1
            elif not link.startswith("#"):
                external.append(link[1:-1] if link.startswith("<") else link)
            if error:
                result["errors"].append(f"{origin.relative_to(root)}: {error}")
            elif target is not None and target.suffix.lower() == ".md" and target not in seen:
                try:
                    pending.append((target, target.read_text(encoding="utf-8")))
                except (OSError, UnicodeError) as exc:
                    result["errors"].append(f"{target.relative_to(root)}: cannot read linked Markdown: {exc}")
    result["checked_local_links"] = local_count
    result["checked_markdown_files"] = len(seen)
    result["external_links"] = external
    result["ok"] = not result["errors"]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    args = parser.parse_args(argv)
    result = check(args.skill_dir)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
