"""Tests for scripts/quiz_tool.py.

Set TEST_MY_KNOWLEDGE_TMP to a scratch directory to keep temporary files there;
otherwise the system temporary directory is used. Run:
python3 -B -m unittest discover -s skills/test-my-knowledge/tests -v
"""

import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import quiz_tool  # noqa: E402

SOURCE = """# Backups
Line two is filler.
A backup you never restored is a guess.
Run a restore test every month.
Keep one copy off site.
"""


def option(oid, text, why="belief"):
    return {"id": oid, "text": text, "why": why}


def question(qid, objective, kind="main", answer="B", scenario=None):
    return {
        "id": qid, "set": kind, "objective": objective,
        "scenario": scenario or f"Scenario for {qid}.", "prompt": "What should happen?",
        "options": [option("A", f"First {qid}"), option("B", f"Second {qid}"), option("C", f"Third {qid}"), option("D", f"Fourth {qid}")],
        "answer": answer, "explanation": "Because the source says so.",
        "evidence": [{"source": "S1", "lines": "3-4", "quote": "Run a restore test every month."}],
    }


def valid_quiz():
    return {
        "schema": quiz_tool.SCHEMA, "title": "Backups", "topic": "Restore tests.", "retest_of": None,
        "sources": [{"id": "S1", "path": "notes.md"}],
        "scoring": {"points_per_question": 1, "total_points": 2, "weak_below": 1.0},
        "objectives": [
            {"id": "O1", "statement": "Decide when a backup is trustworthy.", "evidence": [{"source": "S1", "lines": "3", "quote": "never restored is a guess"}]},
            {"id": "O2", "statement": "Choose where copies live.", "evidence": [{"source": "S1", "lines": "5", "quote": "off site"}]},
        ],
        "questions": [question("Q1", "O1", answer="A"), question("Q2", "O2", answer="C"),
                      question("R1", "O1", "retest", answer="D", scenario="New retest scenario one."),
                      question("R2", "O2", "retest", answer="B", scenario="New retest scenario two.")],
    }


class QuizToolTest(unittest.TestCase):
    def setUp(self):
        base = os.environ.get("TEST_MY_KNOWLEDGE_TMP")
        self.tmp = tempfile.TemporaryDirectory(dir=base) if base else tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "notes.md").write_text(SOURCE, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def errors(self, data, root=True):
        return quiz_tool.check_quiz(data, self.root if root else None).errors

    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = quiz_tool.main(list(args))
        return code, json.loads(out.getvalue())

    def write_quiz(self, data, name="quiz.json"):
        path = self.root / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_valid_quiz_builds_and_checks(self):
        path = self.write_quiz(valid_quiz())
        out = self.root / "out"
        code, result = self.run_cli("build", str(path), "--out-dir", str(out), "--source-root", str(self.root))
        self.assertEqual(code, 0, result)
        self.assertTrue((out / "quiz.html").is_file() and (out / "answer-key.md").is_file())
        code, result = self.run_cli("check", str(path), "--html", str(out / "quiz.html"), "--key", str(out / "answer-key.md"), "--source-root", str(self.root))
        self.assertEqual(code, 0, result)
        self.assertEqual(result["errors"], [])
        self.assertIn("- Correct answer: **A**", (out / "answer-key.md").read_text(encoding="utf-8"))

    def test_page_embeds_hostile_text_safely(self):
        data = valid_quiz()
        data["questions"][0]["scenario"] = "Ends with </script><script>alert(1)</script> & more  "
        page = quiz_tool.render_page(data)
        self.assertNotIn("</script><script>alert", page)
        self.assertEqual(quiz_tool.embedded_json(page), data)

    def test_answer_must_be_an_existing_option(self):
        data = valid_quiz()
        data["questions"][0]["answer"] = "E"
        self.assertTrue(any("answer 'E'" in e for e in self.errors(data)))
        data["questions"][0]["answer"] = ["A", "B"]
        self.assertTrue(any("exactly one existing option" in e for e in self.errors(data)))

    def test_option_rules(self):
        data = valid_quiz()
        data["questions"][0]["options"][1]["id"] = "A"
        data["questions"][1]["options"][1]["text"] = data["questions"][1]["options"][0]["text"].upper()
        data["questions"][2]["options"] = data["questions"][2]["options"][:2]
        data["questions"][3]["options"][0]["why"] = " "
        found = self.errors(data)
        self.assertTrue(any("duplicate option id" in e for e in found))
        self.assertTrue(any("repeats another option's text" in e for e in found))
        self.assertTrue(any("needs 3 to 5 options" in e for e in found))
        self.assertTrue(any("needs a 'why'" in e for e in found))

    def test_declared_scoring_must_match(self):
        data = valid_quiz()
        data["scoring"]["total_points"] = 4
        self.assertTrue(any("total_points is 4" in e for e in self.errors(data)))
        data = valid_quiz()
        data["scoring"].update(points_per_question=2, total_points=4)
        self.assertEqual(self.errors(data), [])
        for bad in (0, 1.5, True, "1"):
            data = valid_quiz()
            data["scoring"]["weak_below"] = bad
            self.assertTrue(any("weak_below" in e for e in self.errors(data)), bad)
        data = valid_quiz()
        data["scoring"]["weak_below"] = 2 / 3
        report = quiz_tool.check_quiz(data, self.root)
        self.assertEqual(report.errors, [])
        self.assertTrue(any("whole percentage" in w for w in report.warnings))

    def test_objective_and_retest_coverage(self):
        data = valid_quiz()
        data["questions"] = [q for q in data["questions"] if q["id"] != "Q2"]
        data["scoring"]["total_points"] = 1
        self.assertTrue(any("objective O2: has no main question" in e for e in self.errors(data)))
        data = valid_quiz()
        data["questions"] = [q for q in data["questions"] if q["id"] != "R2"]
        self.assertTrue(any("objective O2: has no retest question" in e for e in self.errors(data)))
        data["retest_of"] = "Backups quiz, 2026-10-09"
        self.assertEqual(self.errors(data), [])

    def test_retest_must_use_new_scenario(self):
        data = valid_quiz()
        data["questions"][2]["scenario"] = data["questions"][0]["scenario"]
        self.assertTrue(any("repeats a main question" in e for e in self.errors(data)))

    def test_unknown_references(self):
        data = valid_quiz()
        data["questions"][0]["objective"] = "O9"
        data["objectives"][0]["evidence"][0]["source"] = "S9"
        found = self.errors(data)
        self.assertTrue(any("unknown objective 'O9'" in e for e in found))
        self.assertTrue(any("unknown source 'S9'" in e for e in found))

    def test_evidence_pointers_resolve(self):
        data = valid_quiz()
        data["questions"][0]["evidence"][0]["quote"] = "Restore weekly"
        data["questions"][1]["evidence"][0]["lines"] = "4-40"
        data["objectives"][1]["evidence"][0]["lines"] = "5-2"
        found = self.errors(data)
        self.assertTrue(any("quote not found in lines 3-4" in e for e in found))
        self.assertTrue(any("exceed the source length" in e for e in found))
        self.assertTrue(any("lines must look like" in e for e in found))
        self.assertEqual(self.errors(valid_quiz(), root=False), [])

    def test_quote_matching_ignores_markup(self):
        (self.root / "page.html").write_text("<p>Keep the <strong>same</strong>\n   key &amp; reuse it.</p>\n", encoding="utf-8")
        data = valid_quiz()
        data["sources"].append({"id": "S2", "path": "page.html"})
        data["questions"][0]["evidence"] = [{"source": "S2", "lines": "1-2", "quote": "Keep the same key & reuse it."}]
        self.assertEqual(self.errors(data), [])

    def test_source_path_cannot_escape_root(self):
        outside = self.root.parent / f"{self.root.name}-outside.md"
        outside.write_text(SOURCE, encoding="utf-8")
        self.addCleanup(outside.unlink)
        (self.root / "link.md").symlink_to(outside)
        for path in (f"../{outside.name}", "link.md"):
            data = valid_quiz()
            data["sources"][0]["path"] = path
            found = self.errors(data)
            self.assertTrue(found and all("escapes the source root" in e for e in found), (path, found))

    def test_line_numbers_follow_newlines_only(self):
        (self.root / "ff.md").write_text("one\x0ctwo\nthree is here\n", encoding="utf-8")
        data = valid_quiz()
        data["sources"].append({"id": "S2", "path": "ff.md"})
        data["questions"][0]["evidence"] = [{"source": "S2", "lines": "2", "quote": "three is here"}]
        self.assertEqual(self.errors(data), [])

    def test_malformed_ids_are_reported_not_raised(self):
        data = valid_quiz()
        data["questions"][0]["id"] = ["Q1"]
        data["questions"][1]["objective"] = {"id": "O2"}
        data["questions"][2]["evidence"][0]["source"] = ["S1"]
        data["questions"][3]["id"] = "R 2"
        found = self.errors(data)
        self.assertTrue(any("question 1: id ['Q1']" in e for e in found), found)
        self.assertTrue(any("unknown objective" in e for e in found))
        self.assertTrue(any("unknown source ['S1']" in e for e in found))
        self.assertTrue(any("id 'R 2'" in e for e in found))

    def test_flags_need_pointer_and_note(self):
        data = valid_quiz()
        data["flags"] = [{"source": "S1", "lines": "5", "quote": "off site", "note": "Conflicts with line 3."}]
        self.assertEqual(self.errors(data), [])
        data["flags"].append({"source": "S1", "lines": "5"})
        self.assertTrue(any("flag 2: needs a note" in e for e in self.errors(data)))

    def test_scored_questions_cannot_cite_flagged_lines(self):
        data = valid_quiz()
        data["flags"] = [{"source": "S1", "lines": "4", "quote": "every month", "note": "Doubtful."}]
        found = self.errors(data)
        self.assertTrue(any("question Q1: cites flagged lines 4-4" in e for e in found), found)
        for question in data["questions"]:
            question["evidence"] = [{"source": "S1", "lines": "3", "quote": "never restored is a guess"}]
        self.assertEqual(self.errors(data), [])

    def test_key_must_agree_with_quiz(self):
        data = valid_quiz()
        key = quiz_tool.render_key(data).replace("- Correct answer: **A**", "- Correct answer: **B**")
        report = quiz_tool.Report()
        quiz_tool.check_key(key, data, report)
        self.assertTrue(any("Q1 says 'B'" in e for e in report.errors))
        report = quiz_tool.Report()
        quiz_tool.check_key("### Q1\n- Correct answer: **A**\n", data, report)
        self.assertTrue(any("missing Q2" in e for e in report.errors))
        report = quiz_tool.Report()
        quiz_tool.check_key(quiz_tool.render_key(data).replace("Because the source says so.", "Stale text."), data, report)
        self.assertEqual([e for e in report.errors if "differs from a fresh build" in e] != [], True)
        self.assertFalse(any("says" in e for e in report.errors))

    def test_page_checks(self):
        data = valid_quiz()
        page = quiz_tool.render_page(data)
        report = quiz_tool.Report()
        quiz_tool.check_page(page, data, report)
        self.assertEqual(report.errors, [])
        changed = copy.deepcopy(data)
        changed["questions"][0]["answer"] = "B"
        report = quiz_tool.Report()
        quiz_tool.check_page(page, changed, report)
        self.assertTrue(any("differs from the quiz JSON" in e for e in report.errors))
        injections = ('<script src="https://cdn.example/x.js"></script>', '<link href="//fonts.example/a.css" rel="stylesheet">',
                      "<script>fetch('/x')</script>", "<style>@import 'x.css';</style>",
                      '<meta http-equiv="refresh" content="0;url=https://example.com">', '<object data="https://example.com/a"></object>',
                      '<img srcset="a.png 1x, https://example.com/b.png 2x">', '<script type="module">import x from "./x.js"</script>',
                      "<script>new Worker('w.js')</script>", "<style>a{background:image-set(\"https://example.com/a.png\" 1x)}</style>")
        for injected in injections:
            report = quiz_tool.Report()
            quiz_tool.check_page(page.replace("</body>", injected + "</body>"), data, report)
            self.assertTrue(any("external request risk" in e for e in report.errors), injected)
            self.assertTrue(any("differs from a fresh build" in e for e in report.errors), injected)

    def test_page_must_match_template_build(self):
        data = valid_quiz()
        page = quiz_tool.render_page(data).replace("const points=right*", "const points=(right+1)*")
        report = quiz_tool.Report()
        quiz_tool.check_page(page, data, report)
        self.assertEqual(report.errors, ["html: page differs from a fresh build of the bundled template; rebuild it with quiz_tool.py build"])

    def test_quoted_urls_in_quiz_text_are_not_network_requests(self):
        data = valid_quiz()
        data["questions"][0]["scenario"] = 'The page has <a href="https://docs.example.com">docs</a> and calls fetch(url).'
        report = quiz_tool.Report()
        quiz_tool.check_page(quiz_tool.render_page(data), data, report)
        self.assertEqual(report.errors, [])

    def test_build_refuses_to_overwrite(self):
        path = self.write_quiz(valid_quiz())
        out = self.root / "out"
        self.assertEqual(self.run_cli("build", str(path), "--out-dir", str(out))[0], 0)
        code, result = self.run_cli("build", str(path), "--out-dir", str(out))
        self.assertEqual(code, 1)
        self.assertTrue(any("refusing to overwrite" in e for e in result["errors"]))
        code, result = self.run_cli("build", str(path), "--out-dir", str(out), "--name", "retest-1")
        self.assertEqual(code, 0)
        self.assertTrue((out / "retest-1.html").is_file() and (out / "retest-1-answer-key.md").is_file())
        self.assertTrue(any("retest-1.json" in w for w in result["warnings"]))
        for bad in ("../x", "a/b", "a b"):
            code, result = self.run_cli("build", str(path), "--out-dir", str(out), "--name", bad)
            self.assertEqual(code, 1, bad)
            self.assertTrue(any("--name" in e for e in result["errors"]))
        self.assertFalse((self.root / "x.html").exists())

    def test_build_refuses_invalid_quiz(self):
        data = valid_quiz()
        data["questions"][0]["answer"] = "Z"
        path = self.write_quiz(data)
        code, result = self.run_cli("build", str(path), "--out-dir", str(self.root / "out"))
        self.assertEqual(code, 1)
        self.assertEqual(result["built"], [])
        self.assertFalse((self.root / "out").exists())

    def test_warnings_for_answer_cues(self):
        data = valid_quiz()
        data["questions"] = [question(f"Q{i}", "O1", answer="A") for i in range(1, 5)]
        data["questions"].append(question("Q5", "O2", answer="A"))
        data["questions"] += [question("R1", "O1", "retest", scenario="x"), question("R2", "O2", "retest", scenario="y")]
        data["scoring"]["total_points"] = 5
        data["questions"][0]["options"][1]["text"] = "None of the above"
        report = quiz_tool.check_quiz(data, self.root)
        self.assertEqual(report.errors, [])
        self.assertTrue(any("same position" in w for w in report.warnings))
        self.assertTrue(any("of the above" in w for w in report.warnings))
        for q in data["questions"]:
            q["options"][0]["text"] += " with a much longer explanation attached to it"
        self.assertTrue(any("single longest" in w for w in quiz_tool.check_quiz(data, self.root).warnings))

    def test_unreadable_json(self):
        path = self.root / "broken.json"
        path.write_text("{not json", encoding="utf-8")
        code, result = self.run_cli("check", str(path))
        self.assertEqual(code, 1)
        self.assertTrue(result["errors"][0].startswith("quiz: cannot read JSON"))


if __name__ == "__main__":
    unittest.main()
