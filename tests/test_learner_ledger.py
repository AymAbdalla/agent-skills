"""Learner ledger helper shared by explain-it-my-way and test-my-knowledge: matching, statuses, evidence, preservation."""
import contextlib
import datetime
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [ROOT / "plugins/aym-story/skills/explain-it-my-way", ROOT / "plugins/aym-story/skills/test-my-knowledge"]
spec = importlib.util.spec_from_file_location("ledger", SKILLS[0] / "scripts/ledger.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)

HEADER = "# Learner ledger\n\n| Concept | Status | Date | Source | Note |\n| --- | --- | --- | --- | --- |\n"
QUIZ = "quiz: save-flow/quiz.json, obj-1"


class LedgerTest(unittest.TestCase):
    def setUp(self):
        base = os.environ.get("AYM_TEST_TMPDIR")
        self.tmp = tempfile.TemporaryDirectory(prefix="ledger-check-", dir=base if base and Path(base).is_dir() else None)
        self.dir = Path(self.tmp.name)
        self.path = self.dir / "ledger.md"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = ledger.main([str(a) for a in args])
            except SystemExit as exc:
                code = exc.code
        text = out.getvalue()
        return code, (json.loads(text) if text.strip().startswith("{") else text), err.getvalue()

    def rec(self, status, source, *concepts, date="2026-10-20", note=None, path=None):
        args = ["record", "--ledger", path or self.path, "--status", status, "--source", source]
        if date:
            args += ["--date", date]
        if note is not None:
            args += ["--note", note]
        return self.run_cli(*(args + list(concepts)))

    def rows(self):
        code, result, _ = self.run_cli("show", "--ledger", self.path, "--json")
        self.assertEqual(code, 0)
        return result["rows"]

    def write(self, text, newline="\n"):
        self.path.write_bytes(text.replace("\n", newline).encode("utf-8"))


class CopiesTests(unittest.TestCase):
    def test_script_and_reference_identical_in_both_skills(self):
        for rel in ("scripts/ledger.py", "references/learner-ledger.md"):
            first, second = (s / rel for s in SKILLS)
            self.assertEqual(first.read_bytes(), second.read_bytes(), rel)

    def test_each_copy_runs_from_the_command_line(self):
        base = os.environ.get("AYM_TEST_TMPDIR")
        with tempfile.TemporaryDirectory(dir=base if base and Path(base).is_dir() else None) as tmp:
            for n, skill in enumerate(SKILLS):
                path = Path(tmp) / "l{}.md".format(n)
                ok = subprocess.run([sys.executable, "-B", str(skill / "scripts/ledger.py"), "record", "--ledger", str(path),
                                     "--status", "shown", "--source", "explanation: t", "retry"],
                                    capture_output=True, text=True)
                self.assertEqual(ok.returncode, 0, ok.stderr)
                self.assertEqual(json.loads(ok.stdout)["added"], ["retry"])
                bad = subprocess.run([sys.executable, "-B", str(skill / "scripts/ledger.py"), "record", "--ledger", str(path),
                                      "--status", "passed", "--source", "explanation: t", "retry"],
                                     capture_output=True, text=True)
                self.assertEqual(bad.returncode, 2)


class MatchingTests(unittest.TestCase):
    def test_case_spacing_and_trailing_s_are_one_concept(self):
        key = ledger.concept_key
        self.assertEqual(key("Idempotency  Keys"), key("idempotency key"))
        self.assertEqual(key("RETRY"), key("retry"))
        self.assertEqual(key("API keys"), key("api key"))

    def test_words_ending_in_ss_us_is_are_not_folded(self):
        for word in ("process", "class", "status", "analysis", "redis"):
            self.assertEqual(ledger.concept_key(word), word)


class RecordTests(LedgerTest):
    def test_creates_file_with_header_and_parent_folders(self):
        path = self.dir / "personal" / "learning" / "ledger.md"
        code, result, _ = self.rec("shown", "explanation: save flow", "Retry", path=path)
        self.assertEqual(code, 0)
        self.assertTrue(result["created"])
        self.assertEqual(path.read_text(), HEADER + "| retry | shown | 2026-10-20 | explanation: save flow | |\n")

    def test_output_shape(self):
        code, result, _ = self.rec("shown", "explanation: x", "retry")
        self.assertEqual(code, 0)
        self.assertEqual(set(result), {"path", "created", "added", "changed", "unchanged"})
        self.assertEqual(result["path"], str(self.path))

    def test_new_concepts_stored_lowercase_with_single_spaces(self):
        self.rec("shown", "explanation: x", "  Retry   Budget ")
        self.assertEqual(self.rows()[0]["concept"], "retry budget")

    def test_shown_only_adds_and_never_changes_existing_rows(self):
        self.rec("missed", QUIZ, "retry", date="2026-10-18")
        before = self.path.read_bytes()
        code, result, _ = self.rec("shown", "explanation: later", "RETRY", "send gate", date="2026-10-21")
        self.assertEqual(code, 0)
        self.assertEqual(result["unchanged"], ["retry"])
        self.assertEqual(result["added"], ["send gate"])
        rows = {r["concept"]: r for r in self.rows()}
        self.assertEqual(rows["retry"], {"concept": "retry", "status": "missed", "date": "2026-10-18", "source": QUIZ, "note": ""})
        self.assertTrue(self.path.read_bytes().startswith(before))

    def test_plural_matches_existing_row_instead_of_adding(self):
        self.rec("shown", "explanation: x", "idempotency key")
        code, result, _ = self.rec("passed", QUIZ, "Idempotency Keys")
        self.assertEqual(result["added"], [])
        self.assertEqual(result["changed"], [{"concept": "idempotency key", "from": "shown", "to": "passed"}])
        self.assertEqual(len(self.rows()), 1)

    def test_duplicate_concepts_in_one_call_make_one_row(self):
        code, result, _ = self.rec("shown", "explanation: x", "retry", "Retry", "retrys")
        self.assertEqual(result["added"], ["retry"])
        self.assertEqual(len(self.rows()), 1)

    def test_passed_and_missed_update_status_date_and_source(self):
        self.rec("shown", "explanation: x", "send gate", note="first look", date="2026-10-18")
        self.rec("missed", "quiz: gtm/quiz.json, obj-3", "send gate", date="2026-10-19")
        row = self.rows()[0]
        self.assertEqual((row["status"], row["date"], row["source"], row["note"]),
                         ("missed", "2026-10-19", "quiz: gtm/quiz.json, obj-3", "first look"))
        code, result, _ = self.rec("passed", "said: it blocks risky sends", "send gate", note="explained it back")
        self.assertEqual(result["changed"], [{"concept": "send gate", "from": "missed", "to": "passed"}])
        row = self.rows()[0]
        self.assertEqual((row["status"], row["date"], row["note"]), ("passed", "2026-10-20", "explained it back"))

    def test_passed_without_learner_evidence_is_refused(self):
        self.rec("shown", "explanation: x", "retry")
        before = self.path.read_bytes()
        for status in ("passed", "missed"):
            for source in ("explanation: save flow", "the project uses retries", "said:", "quiz:  "):
                code, _, err = self.rec(status, source, "retry")
                self.assertEqual(code, 2, (status, source))
                self.assertIn("ledger.py: error", err)
        self.assertEqual(self.path.read_bytes(), before)

    def test_refused_record_does_not_create_the_file(self):
        code, _, _ = self.rec("passed", "explanation: x", "retry")
        self.assertEqual(code, 2)
        self.assertFalse(self.path.exists())

    def test_quiz_and_said_sources_accepted(self):
        for source in (QUIZ, "said: same number for the same save", "Quiz: q.json, O1"):
            code, _, err = self.rec("passed", source, "retry")
            self.assertEqual(code, 0, err)

    def test_declined_needs_user_source(self):
        self.rec("shown", "explanation: x", "retry")
        code, _, _ = self.rec("declined", "said: skip it", "retry")
        self.assertEqual(code, 2)
        code, result, _ = self.rec("declined", "user: asked to skip retries", "retry")
        self.assertEqual(code, 0)
        self.assertEqual(result["changed"], [{"concept": "retry", "from": "shown", "to": "declined"}])

    def test_bad_dates_refused(self):
        for bad in ("2026-13-01", "20-10-2026", "2026-02-30", "2026-1-5", "yesterday"):
            code, _, _ = self.rec("shown", "explanation: x", "retry", date=bad)
            self.assertEqual(code, 2, bad)
        self.assertFalse(self.path.exists())

    def test_default_date_is_today(self):
        self.rec("shown", "explanation: x", "retry", date=None)
        self.assertEqual(self.rows()[0]["date"], datetime.date.today().isoformat())

    def test_bad_status_refused(self):
        code, _, _ = self.rec("learned", "said: x", "retry")
        self.assertEqual(code, 2)
        self.assertFalse(self.path.exists())

    def test_rerunning_the_same_record_is_a_no_op(self):
        self.rec("shown", "explanation: x", "retry", "send gate")
        self.rec("passed", QUIZ, "retry", note="got it")
        before, inode = self.path.read_bytes(), self.path.stat().st_ino
        for args in (("shown", "explanation: x", "retry", "send gate"), ("passed", QUIZ, "retry")):
            code, result, _ = self.rec(*args)
            self.assertEqual(code, 0)
            self.assertEqual((result["added"], result["changed"]), ([], []))
        code, result, _ = self.rec("passed", QUIZ, "retry", note="got it")
        self.assertEqual(result["unchanged"], ["retry"])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.path.stat().st_ino, inode, "an unchanged ledger must not be rewritten")

    def test_older_evidence_does_not_replace_newer(self):
        self.rec("passed", QUIZ, "retry", date="2026-10-20")
        code, result, _ = self.rec("missed", "quiz: old/quiz.json, obj-1", "retry", date="2026-10-01")
        self.assertEqual(result["unchanged"], ["retry"])
        self.assertEqual(self.rows()[0]["status"], "passed")

    def test_evidence_replaces_a_newer_shown_row(self):
        self.rec("shown", "explanation: x", "retry", date="2026-10-21")
        code, result, _ = self.rec("passed", QUIZ, "retry", date="2026-10-20")
        self.assertEqual(result["changed"][0]["to"], "passed")

    def test_note_escaped_single_line_and_capped(self):
        note = "uses | pipes\nand a newline " + "x" * 200
        self.rec("shown", "explanation: x", "retry", note=note)
        line = self.path.read_text().splitlines()[-1]
        self.assertIn("uses \\| pipes and a newline", line)
        stored = self.rows()[0]["note"]
        self.assertLessEqual(len(stored), 120)
        self.assertTrue(stored.startswith("uses | pipes and a newline"))
        self.assertEqual(len(self.path.read_text().splitlines()), 5)

    def test_note_kept_unless_given(self):
        self.rec("shown", "explanation: x", "retry", note="keep me")
        self.rec("passed", QUIZ, "retry")
        self.assertEqual(self.rows()[0]["note"], "keep me")
        self.rec("passed", "quiz: other.json, O2", "retry", note="")
        self.assertEqual(self.rows()[0]["note"], "")

    def test_concept_too_long_refused(self):
        code, _, _ = self.rec("shown", "explanation: x", "a " * 60)
        self.assertEqual(code, 2)


class PreservationTests(LedgerTest):
    HAND = ("# Learner ledger\n\nMy notes about learning. Keep this paragraph.\n\n"
            "| Concept | Status | Date | Source | Note |\n| --- | --- | --- | --- | --- |\n"
            "|  Retry|Passed |2026-10-01| me, from a book |  read chapter 3 |\n"
            "| send gate | shown | 2026-10-18 | explanation: gtm | |\n"
            "| odd row with extra cells | shown | 2026-10-02 | hand | | extra |\n"
            "\nTrailing text after the table.\n")

    def test_hand_edited_rows_and_other_text_untouched(self):
        self.write(self.HAND)
        code, result, _ = self.rec("shown", "explanation: y", "retry", "circuit breaker")
        self.assertEqual(result["unchanged"], ["Retry"])
        code, result, _ = self.rec("passed", QUIZ, "send gate")
        text = self.path.read_text()
        old = self.HAND.splitlines(keepends=True)
        new = text.splitlines(keepends=True)
        self.assertEqual(new[6], old[6], "hand row changed")
        self.assertEqual(new[8], old[8])
        self.assertEqual(new[7], "| send gate | passed | 2026-10-20 | {} | |\n".format(QUIZ))
        self.assertEqual(new[9], "| circuit breaker | shown | 2026-10-20 | explanation: y | |\n")
        self.assertEqual(new[:7], old[:7])
        self.assertEqual(new[10:], old[9:])

    def test_evidence_changes_only_its_cells_in_a_hand_row(self):
        self.write(self.HAND)
        code, result, _ = self.rec("passed", QUIZ, "RETRY")
        self.assertEqual(result["changed"], [{"concept": "Retry", "from": "Passed", "to": "passed"}])
        line = self.path.read_text().splitlines()[6]
        self.assertEqual(line, "|  Retry| passed | 2026-10-20 | {} |  read chapter 3 |".format(QUIZ))
        code, result, _ = self.rec("passed", QUIZ, "odd row with extra cells")
        self.assertTrue(self.path.read_text().splitlines()[8].endswith("| | extra |"))

    def test_rows_never_deleted(self):
        self.write(self.HAND)
        for args in (("shown", "explanation: a", "x1", "x2"), ("missed", QUIZ, "x1"), ("declined", "user: no", "x2"),
                     ("passed", "said: yes", "x1", "send gate")):
            self.rec(*args)
            concepts = [r["concept"] for r in self.rows()]
            for name in ("Retry", "send gate", "odd row with extra cells"):
                self.assertIn(name, concepts)
        self.assertEqual(len(self.rows()), 5)

    def test_crlf_and_missing_final_newline_kept(self):
        self.write(HEADER + "| retry | shown | 2026-10-18 | explanation: x | |\nAfter.", newline="\r\n")
        self.rec("shown", "explanation: y", "send gate")
        data = self.path.read_bytes()
        self.assertNotIn(b"\r\r", data)
        self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))
        self.assertTrue(data.endswith(b"\r\nAfter."))
        self.assertIn(b"| send gate | shown | 2026-10-20 | explanation: y | |\r\n", data)

    def test_column_order_respected(self):
        self.write("| Status | Concept | Note | Source | Date |\n|---|---|---|---|---|\n| shown | retry | | explanation: x | 2026-10-18 |\n")
        self.rec("passed", QUIZ, "retry")
        self.rec("shown", "explanation: y", "send gate")
        lines = self.path.read_text().splitlines()
        self.assertEqual(lines[2], "| passed | retry | | {} | 2026-10-20 |".format(QUIZ))
        self.assertEqual(lines[3], "| shown | send gate | | explanation: y | 2026-10-20 |")

    def test_file_without_a_table_keeps_its_text_and_gains_one(self):
        self.write("My ledger\nnotes")
        code, result, _ = self.rec("shown", "explanation: x", "retry")
        self.assertFalse(result["created"])
        self.assertEqual(self.path.read_text(), "My ledger\nnotes\n\n" + HEADER.split("\n\n", 1)[1]
                         + "| retry | shown | 2026-10-20 | explanation: x | |\n")

    def test_table_missing_a_column_is_refused(self):
        self.write("| Concept | Status | Date | Note |\n| --- | --- | --- | --- |\n")
        before = self.path.read_bytes()
        code, _, err = self.rec("shown", "explanation: x", "retry")
        self.assertEqual(code, 2)
        self.assertIn("source", err)
        self.assertEqual(self.path.read_bytes(), before)

    def test_write_leaves_no_temporary_files(self):
        self.write(self.HAND)
        self.rec("shown", "explanation: x", "a", "b")
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["ledger.md"])


class ShowTests(LedgerTest):
    def test_missing_file(self):
        code, result, _ = self.run_cli("show", "--ledger", self.path, "--json")
        self.assertEqual((code, result["exists"], result["rows"]), (0, False, []))
        code, text, _ = self.run_cli("show", "--ledger", self.path)
        self.assertIn("No ledger yet", text)
        self.assertFalse(self.path.exists())

    def test_rows_as_json_and_text(self):
        self.rec("shown", "explanation: x", "retry", "send gate")
        self.rec("missed", QUIZ, "send gate", note="mixed up | two")
        rows = self.rows()
        self.assertEqual([r["concept"] for r in rows], ["retry", "send gate"])
        self.assertEqual(rows[1]["note"], "mixed up | two")
        code, text, _ = self.run_cli("show", "--ledger", self.path)
        self.assertIn("2 concepts: 1 missed, 1 shown", text)


if __name__ == "__main__":
    unittest.main()
