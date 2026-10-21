"""Behavioral checks for the bounded, read-only build-skill helpers."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "skills" / "build-skill" / "scripts"


def entry(eid):
    return {
        "id": eid, "shelf": "make", "need": "Create a reusable skill",
        "mechanic": "Write a bounded instruction", "use_when": "Authoring a skill",
        "avoid_when": "Only discussing an idea", "counterexample": "A file check is not a behavior check",
        "conflicts": ["May require host testing"], "cost": "One review", "decision": "proposed",
        "date": "2026-10-09", "review": "pending", "examples": [{
            "role": "best", "source_id": f"source-{eid}", "component_type": "skill",
            "author": "Fixture author", "license": "fixture", "revision": "fixture-1",
            "locator": "fixture/example", "evidence": "source-inspected",
            "limits": "No runtime check", "dissection": "library/dissections/example.md",
            "files": [{"path": "SKILL.md", "sha256": "a" * 64}],
        }],
    }


class HelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = os.environ.get("BUILD_THIS_TEST_TMP")
        if not base:
            raise RuntimeError("set BUILD_THIS_TEST_TMP to an existing approved scratch directory")
        task_scratch = Path(base)
        if task_scratch.is_symlink() or not task_scratch.is_dir():
            raise RuntimeError("BUILD_THIS_TEST_TMP must name an existing real directory")
        cls.scratch = task_scratch / "test-helpers"
        cls.scratch.mkdir()

    @classmethod
    def tearDownClass(cls):
        cls.scratch.rmdir()

    def setUp(self):
        self.base = self.scratch / self._testMethodName
        self.base.mkdir()
        self.files = {}
        self.links = {}
        self.dirs = [self.base]

    def tearDown(self):
        for path, expected in self.files.items():
            self.assertEqual(path.read_bytes(), expected, f"fixture changed before cleanup: {path}")
            path.unlink()
        for path, target in self.links.items():
            self.assertTrue(path.is_symlink())
            self.assertEqual(os.readlink(path), target)
            path.unlink()
        for path in sorted(self.dirs, key=lambda p: len(p.parts), reverse=True):
            path.rmdir()

    def directory(self, rel):
        path = self.base / rel
        missing = []
        cursor = path
        while not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        for item in reversed(missing):
            item.mkdir()
            self.dirs.append(item)
        return path

    def write(self, rel, content):
        path = self.base / rel
        self.directory(str(path.parent.relative_to(self.base)))
        payload = content.encode() if isinstance(content, str) else content
        path.write_bytes(payload)
        self.files[path] = payload
        return path

    def symlink(self, rel, target):
        path = self.base / rel
        self.directory(str(path.parent.relative_to(self.base)))
        path.symlink_to(target)
        self.links[path] = target

    def library(self, entries):
        catalog = "# Fixture catalog\n\n" + "\n".join(
            "```json\n" + json.dumps(item) + "\n```\n" for item in entries
        )
        self.write("library/LIBRARY.md", catalog)

    def run_helper(self, script, *args):
        process = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / script), *map(str, args)],
            capture_output=True, text=True, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertFalse(process.stderr, process.stderr)
        return process.returncode, json.loads(process.stdout)

    def test_select_preserves_example_fields_and_source_identity(self):
        original = entry("skill-authoring")
        self.library([original])
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--id", "skill-authoring")
        self.assertEqual(code, 0)
        self.assertEqual(result["entries"], [original])
        self.assertEqual(result["entries"][0]["examples"][0]["source_id"], "source-skill-authoring")
        self.assertIn("unavailable", result["source_verification"])

    def test_select_query_is_bounded_and_no_match_is_distinct(self):
        self.library([entry(f"mechanic-{n}") for n in range(8)])
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--query", "reusable skill")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "matched")
        self.assertEqual(len(result["entries"]), 6)
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--query", "unmatched wording")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "no_match")
        self.assertEqual(result["entries"], [])

    def test_select_ids_narrow_a_query_and_unknown_id_fails(self):
        self.library([entry("one"), entry("two")])
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--query", "reusable skill", "--id", "two")
        self.assertEqual(code, 0)
        self.assertEqual([item["id"] for item in result["entries"]], ["two"])
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--id", "unknown")
        self.assertEqual(code, 1)
        self.assertIn("unknown mechanic IDs", result["errors"][0])

    def test_select_rejects_missing_library_and_bad_limit(self):
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--id", "missing")
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "no_library")
        self.assertIn("no library found; start one with dissect-this", result["errors"][0])
        self.library([entry("known")])
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--id", "known", "--limit", "7")
        self.assertEqual(code, 1)
        self.assertIn("between 1 and 6", result["errors"][0])

    def test_select_rejects_duplicate_and_malformed_catalog(self):
        self.library([entry("same"), entry("same")])
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--query", "skill")
        self.assertEqual(code, 1)
        self.assertIn("duplicate ID", result["errors"][0])
        path = self.base / "library" / "LIBRARY.md"
        path.write_text("```json\n{bad\n```\n")
        self.files[path] = path.read_bytes()
        code, result = self.run_helper("select_mechanics.py", "--library-root", self.base,
                                       "--query", "skill")
        self.assertEqual(code, 1)
        self.assertIn("malformed catalog data", result["errors"][0])

    def test_check_accepts_valid_package_and_labels_extra_metadata(self):
        self.write("skill/references/guide.md", "# Guide\n")
        self.write("skill/SKILL.md", "---\nname: sample-skill\ndescription: A narrow job\nallowed-tools: Read\n---\n[Guide](references/guide.md#step)\n")
        code, result = self.run_helper("check_skill.py", self.base / "skill")
        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])
        self.assertEqual(result["checked_local_links"], 1)
        self.assertEqual(result["unsupported_metadata"], ["allowed-tools"])

    def test_check_rejects_missing_escaping_and_symlinked_links(self):
        self.write("outside.md", "outside")
        self.write("skill/SKILL.md", "---\nname: sample-skill\ndescription: A job\n---\n[missing](references/no.md) [escape](../outside.md) [linked](linked.md)\n")
        self.symlink("skill/linked.md", "../outside.md")
        code, result = self.run_helper("check_skill.py", self.base / "skill")
        self.assertEqual(code, 1)
        self.assertEqual(len(result["errors"]), 3)
        self.assertTrue(any("missing" in error for error in result["errors"]))
        self.assertTrue(any("escapes" in error for error in result["errors"]))
        self.assertTrue(any("symlink" in error for error in result["errors"]))

    def test_check_rejects_malformed_frontmatter(self):
        self.write("skill/SKILL.md", "---\nname: sample-skill\ndescription: >\n  multiline\n---\n")
        code, result = self.run_helper("check_skill.py", self.base / "skill")
        self.assertEqual(code, 1)
        self.assertTrue(any("unsupported multiline" in error for error in result["errors"]))

    def test_check_rejects_file_url_and_symlinked_skill_directory(self):
        self.write("skill/SKILL.md", "---\nname: sample-skill\ndescription: A job\n---\n[bad](file:///tmp/readme.md)\n")
        code, result = self.run_helper("check_skill.py", self.base / "skill")
        self.assertEqual(code, 1)
        self.assertIn("safe relative path", result["errors"][0])
        self.symlink("linked-skill", "skill")
        code, result = self.run_helper("check_skill.py", self.base / "linked-skill")
        self.assertEqual(code, 1)
        self.assertIn("symlink", result["errors"][0])

    def test_check_follows_reference_links_and_rejects_indirect_failures(self):
        self.write("outside.md", "outside")
        self.write("skill/SKILL.md", "---\nname: sample-skill\ndescription: A job\n---\n[Guide](references/guide.md)\n")
        self.write("skill/references/guide.md", "[gone](missing.md) [escape](../../outside.md) [linked](linked.md)\n")
        self.symlink("skill/references/linked.md", "../../outside.md")
        code, result = self.run_helper("check_skill.py", self.base / "skill")
        self.assertEqual(code, 1)
        self.assertEqual(result["checked_markdown_files"], 2)
        self.assertEqual(len(result["errors"]), 3)
        self.assertTrue(all("references/guide.md:" in error for error in result["errors"]))
        self.assertTrue(any("missing" in error for error in result["errors"]))
        self.assertTrue(any("escapes" in error for error in result["errors"]))
        self.assertTrue(any("symlink" in error for error in result["errors"]))

    def test_check_allows_parent_link_within_skill_and_deduplicates_cycle(self):
        self.write("skill/SKILL.md", "---\nname: sample-skill\ndescription: A job\n---\n[Guide](references/deep/guide.md)\n")
        self.write("skill/references/deep/guide.md", "[Shared](../shared.md) [Back](../../SKILL.md) [Web](https://example.org/info)\n")
        self.write("skill/references/shared.md", "[Guide](deep/guide.md)\n")
        code, result = self.run_helper("check_skill.py", self.base / "skill")
        self.assertEqual(code, 0)
        self.assertEqual(result["checked_markdown_files"], 3)
        self.assertEqual(result["checked_local_links"], 4)
        self.assertEqual(result["external_links"], ["https://example.org/info"])

    def test_check_rejects_yaml_collection_and_boolean_metadata(self):
        path = self.write("skill/SKILL.md", "---\nname: sample-skill\ndescription: [bad, YAML, sequence]\n---\n")
        for value in ("[bad, YAML, sequence]", "true", "2026-10-09", "0x10", ".inf", ".nan", "&alias", "*alias", "!tag", "123", "null"):
            with self.subTest(value=value):
                path.write_text(f"---\nname: sample-skill\ndescription: {value}\n---\n")
                self.files[path] = path.read_bytes()
                code, result = self.run_helper("check_skill.py", self.base / "skill")
                self.assertEqual(code, 1)
                self.assertIn("ambiguous YAML", result["errors"][0])
        path.write_text('---\nname: sample-skill\ndescription: "2026-10-09"\n---\n')
        self.files[path] = path.read_bytes()
        code, result = self.run_helper("check_skill.py", self.base / "skill")
        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
