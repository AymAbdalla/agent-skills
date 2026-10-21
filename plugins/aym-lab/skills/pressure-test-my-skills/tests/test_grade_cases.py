"""Behavior checks for the read-only pressure-test grader.

Set PRESSURE_TEST_TMP to an existing scratch directory; otherwise the system temp
directory is used. Each test removes only the files and folders it created.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "grade_cases.py"
sys.path.insert(0, str(SCRIPT.parent))
import grade_cases  # noqa: E402


class GraderTests(unittest.TestCase):
    def setUp(self):
        base = os.environ.get("PRESSURE_TEST_TMP") or None
        if base and not Path(base).is_dir():
            raise RuntimeError("PRESSURE_TEST_TMP must name an existing directory")
        self.root = Path(tempfile.mkdtemp(prefix=f"{self._testMethodName}-", dir=base))
        self.files, self.dirs = [], [self.root]
        self.target = self.mkdir("target")
        self.write("target/SKILL.md", "---\nname: save-note\ndescription: Save notes.\n---\n")
        self.evaluator = self.mkdir("evaluator")

    def tearDown(self):
        for path in reversed(self.files):
            if path.is_symlink() or path.exists():
                path.unlink()
        for path in sorted(self.dirs, key=lambda p: len(p.parts), reverse=True):
            path.rmdir()

    def mkdir(self, rel):
        path = self.root / rel
        for parent in reversed([path, *path.parents]):
            if parent not in self.dirs and self.root in parent.parents:
                parent.mkdir()
                self.dirs.append(parent)
        return path

    def write(self, rel, text):
        path = self.root / rel
        self.mkdir(str(Path(rel).parent)) if Path(rel).parent != Path(".") else None
        path.write_text(text)
        self.files.append(path)
        return path

    def freeze(self, cases, runs, allowance=None):
        doc = {"target": {"path": str(self.target), "sha256": grade_cases.hash_tree(self.target)}, "cases": cases}
        cases_path = self.write("evaluator/cases.json", json.dumps(doc))
        run_doc = {"allowance": allowance or {"total": 4, "per_host": {"claude": 2, "codex": 2}},
                   "cases_sha256": grade_cases.sha256_file(cases_path), "runs": runs}
        runs_path = self.write("evaluator/runs.json", json.dumps(run_doc))
        return cases_path, runs_path

    def note_case(self):
        return {"id": "normal-1", "kind": "normal", "prompt": "Save a note titled Standup.",
                "checks": [{"type": "exists", "path": "notes/standup.md"},
                           {"type": "contains", "path": "notes/standup.md", "text": "# Standup"}]}

    def test_pass_when_artifact_matches(self):
        self.write("run1/notes/standup.md", "# Standup\n")
        cases, runs = self.freeze([self.note_case()], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1"), "exit_code": 0}])
        result = grade_cases.grade(cases, runs)
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["target"]["unchanged"])

    def test_seeded_wrong_destination_fails_and_reproduces(self):
        self.write("run1/tmp-notes/standup.md", "# Standup\n")
        self.write("run2/tmp-notes/standup.md", "# Standup\n")
        cases, runs = self.freeze([self.note_case()], [
            {"id": f"r{i}", "case": "normal-1", "host": host, "status": "completed", "fixture": str(self.root / f"run{i}")}
            for i, host in ((1, "claude"), (2, "codex"))])
        result = grade_cases.grade(cases, runs)
        self.assertEqual(result["verdict"], "fail")
        first = result["findings"][0]
        self.assertEqual(first["check"]["path"], "notes/standup.md")
        self.assertEqual(first["failed_runs"], ["r1", "r2"])
        self.assertTrue(first["reproduced"])

    def test_single_failure_is_not_marked_reproduced(self):
        self.write("run1/tmp-notes/standup.md", "# Standup\n")
        cases, runs = self.freeze([self.note_case()], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")}])
        self.assertFalse(grade_cases.grade(cases, runs)["findings"][0]["reproduced"])

    def test_missing_required_command_is_unavailable_not_pass(self):
        case = {"id": "normal-1", "kind": "normal", "prompt": "Stamp the receipt.",
                "requires_commands": ["receipt-stamp-not-installed-w2"],
                "checks": [{"type": "exists", "path": "receipts/receipt.stamp"}]}
        self.write("run1/receipts/receipt.stamp", "faked\n")
        cases, runs = self.freeze([case], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")}])
        result = grade_cases.grade(cases, runs)
        self.assertEqual(result["runs"][0]["status"], "unavailable")
        self.assertIn("receipt-stamp-not-installed-w2", result["runs"][0]["reason"])
        self.assertEqual(result["verdict"], "incomplete")

    def test_errored_negative_run_is_not_a_correct_decline(self):
        case = {"id": "neg-1", "kind": "inappropriate-trigger", "prompt": "Fix this bug.",
                "checks": [{"type": "glob_absent", "pattern": "*results.json"}]}
        self.mkdir("run1")
        cases, runs = self.freeze([case], [
            {"id": "r1", "case": "neg-1", "host": "codex", "status": "completed", "exit_code": 1, "fixture": str(self.root / "run1")},
            {"id": "r2", "case": "neg-1", "host": "claude", "status": "error", "fixture": str(self.root / "run1"), "note": "timeout"}])
        result = grade_cases.grade(cases, runs)
        self.assertEqual([r["status"] for r in result["runs"]], ["error", "error"])
        self.assertEqual(result["verdict"], "incomplete")

    def test_missing_transcript_makes_trace_check_unavailable(self):
        case = {"id": "neg-1", "kind": "inappropriate-trigger", "prompt": "Fix this bug.",
                "checks": [{"type": "trace_absent", "text": "pressure-test-my-skills/SKILL.md"}]}
        self.mkdir("run1")
        cases, runs = self.freeze([case], [
            {"id": "r1", "case": "neg-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1"),
             "transcript": str(self.root / "missing.jsonl")}])
        result = grade_cases.grade(cases, runs)
        self.assertEqual(result["runs"][0]["status"], "unavailable")
        self.assertNotEqual(result["verdict"], "pass")

    def test_trace_checks_read_transcript(self):
        case = {"id": "neg-1", "kind": "inappropriate-trigger", "prompt": "Fix this bug.",
                "checks": [{"type": "trace_absent", "text": "pressure-test-my-skills/SKILL.md"}]}
        self.mkdir("run1")
        log = self.write("logs/r1.jsonl", '{"tool":"Read","file_path":".claude/skills/pressure-test-my-skills/SKILL.md"}\n')
        cases, runs = self.freeze([case], [
            {"id": "r1", "case": "neg-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1"), "transcript": str(log)}])
        self.assertEqual(grade_cases.grade(cases, runs)["verdict"], "fail")

    def test_unrun_case_keeps_verdict_incomplete(self):
        self.write("run1/notes/standup.md", "# Standup\n")
        second = dict(self.note_case(), id="normal-2")
        cases, runs = self.freeze([self.note_case(), second], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")}])
        result = grade_cases.grade(cases, runs)
        self.assertEqual(result["coverage"]["not_run"], 1)
        self.assertEqual(result["verdict"], "incomplete")

    def test_case_change_after_freeze_is_protocol_error(self):
        self.write("run1/notes/standup.md", "# Standup\n")
        cases, runs = self.freeze([self.note_case()], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")}])
        doc = json.loads(cases.read_text())
        doc["cases"][0]["checks"] = [{"type": "exists", "path": "notes/standup.md"}]
        cases.write_text(json.dumps(doc))
        result = grade_cases.grade(cases, runs)
        self.assertTrue(any("changed after freezing" in e for e in result["protocol_errors"]))
        self.assertEqual(result["verdict"], "incomplete")

    def test_target_change_is_protocol_error(self):
        self.write("run1/notes/standup.md", "# Standup\n")
        cases, runs = self.freeze([self.note_case()], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")}])
        self.write("target/extra.md", "edited during the run\n")
        result = grade_cases.grade(cases, runs)
        self.assertFalse(result["target"]["unchanged"])
        self.assertEqual(result["verdict"], "incomplete")

    def test_expected_facts_inside_fixture_are_flagged(self):
        cases, runs = self.freeze([self.note_case()], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.evaluator)}])
        result = grade_cases.grade(cases, runs)
        self.assertTrue(any("leaked" in e for e in result["protocol_errors"]))

    def test_allowance_overrun_is_protocol_error(self):
        self.write("run1/notes/standup.md", "# Standup\n")
        runs = [{"id": f"r{i}", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")} for i in range(3)]
        cases, runs_path = self.freeze([self.note_case()], runs, allowance={"total": 2, "per_host": {"claude": 2}})
        result = grade_cases.grade(cases, runs_path)
        self.assertEqual(result["used"]["total"], 3)
        self.assertEqual(result["verdict"], "incomplete")
        self.assertEqual(len(result["protocol_errors"]), 2)

    def test_paths_outside_fixture_are_not_evaluated(self):
        case = {"id": "normal-1", "kind": "normal", "prompt": "x",
                "checks": [{"type": "absent", "path": "../evaluator/cases.json"}]}
        self.mkdir("run1")
        cases, runs = self.freeze([case], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")}])
        result = grade_cases.grade(cases, runs)
        self.assertIsNone(result["runs"][0]["checks"][0]["result"])
        self.assertEqual(result["runs"][0]["status"], "unavailable")

    def test_json_field_and_glob_checks(self):
        self.write("run1/out/results.json", json.dumps({"verdict": "fail", "cases": [{"status": "unavailable"}]}))
        case = {"id": "normal-1", "kind": "normal", "prompt": "x", "checks": [
            {"type": "json_field", "path": "out/results.json", "field": "verdict", "not_equals": "pass"},
            {"type": "json_field", "path": "out/results.json", "field": "cases.0.status", "in": ["unavailable", "error"]},
            {"type": "glob_exists", "pattern": "*results.json"},
            {"type": "glob_absent", "pattern": "*receipt-stamp"}]}
        cases, runs = self.freeze([case], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")}])
        self.assertEqual(grade_cases.grade(cases, runs)["verdict"], "pass")

    def test_cli_output_is_byte_identical_across_reruns(self):
        self.write("run1/tmp-notes/standup.md", "# Standup\n")
        cases, runs = self.freeze([self.note_case()], [
            {"id": "r1", "case": "normal-1", "host": "claude", "status": "completed", "fixture": str(self.root / "run1")}])
        command = [sys.executable, "-B", str(SCRIPT), "grade", "--cases", str(cases), "--runs", str(runs)]
        first = subprocess.run(command, capture_output=True, check=True).stdout
        second = subprocess.run(command, capture_output=True, check=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["verdict"], "fail")

    def completed(self, rid="r1", case="normal-1", fixture="run1", **extra):
        return dict({"id": rid, "case": case, "host": "claude", "status": "completed",
                     "fixture": str(self.root / fixture)}, **extra)

    def test_checks_missing_their_text_are_never_a_pass(self):
        self.write("run1/notes/standup.md", "# Standup\n")
        log = self.write("logs/r1.jsonl", "anything\n")
        for check in ({"type": "contains", "path": "notes/standup.md"},
                      {"type": "trace_contains"}, {"type": "trace_absent", "text": ""}):
            with self.subTest(check=check):
                case = {"id": "normal-1", "kind": "normal", "prompt": "x", "checks": [check]}
                cases, runs = self.freeze([case], [self.completed(transcript=str(log))])
                result = grade_cases.grade(cases, runs)
                self.assertEqual(result["runs"][0]["status"], "unavailable")
                self.assertEqual(result["verdict"], "incomplete")
                self.assertTrue(any("non-empty string" in e for e in result["protocol_errors"]))

    def test_missing_or_malformed_allowance_blocks_pass(self):
        self.write("run1/notes/standup.md", "# Standup\n")
        cases, runs = self.freeze([self.note_case()], [self.completed()])
        doc = json.loads(runs.read_text())
        del doc["allowance"]
        runs.write_text(json.dumps(doc))
        self.assertEqual(grade_cases.grade(cases, runs)["verdict"], "incomplete")
        doc["allowance"] = {"total": 2, "per_host": {"claude": "2"}}
        runs.write_text(json.dumps(doc))
        result = grade_cases.grade(cases, runs)
        self.assertEqual(result["verdict"], "incomplete")
        self.assertTrue(any("per_host" in e for e in result["protocol_errors"]))

    def test_malformed_entries_become_protocol_errors(self):
        self.write("run1/notes/standup.md", "# Standup\n")
        bad_cases = [self.note_case(), "not a case", {"id": "no-checks", "kind": "normal", "prompt": "x"},
                     {"id": "bad-check", "kind": "normal", "prompt": "x", "checks": ["nope"]}]
        bad_runs = [self.completed(), "not a run", self.completed(rid="r2", case=["list"]),
                    self.completed(rid="r3", case="bad-check"), {"case": "normal-1", "status": "completed"}]
        cases, runs = self.freeze(bad_cases, bad_runs)
        result = grade_cases.grade(cases, runs)
        self.assertEqual(result["verdict"], "incomplete")
        self.assertGreaterEqual(len(result["protocol_errors"]), 5)
        statuses = {row["id"]: row["status"] for row in result["cases"]}
        self.assertEqual(statuses, {"bad-check": "unavailable", "no-checks": "not_run", "normal-1": "pass"})

    def test_top_level_shape_error_exits_without_result(self):
        cases = self.write("evaluator/cases.json", "[]")
        runs = self.write("evaluator/runs.json", "{}")
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "grade", "--cases", str(cases), "--runs", str(runs)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")

    def test_duplicate_run_ids_and_shared_fixtures_do_not_reproduce(self):
        self.write("run1/tmp-notes/standup.md", "# Standup\n")
        cases, runs = self.freeze([self.note_case()], [self.completed(), self.completed(),
                                                       self.completed(rid="r2")])
        result = grade_cases.grade(cases, runs)
        self.assertTrue(any("duplicated" in e for e in result["protocol_errors"]))
        finding = result["findings"][0]
        self.assertEqual(finding["failed_runs"], ["r1", "r2"])
        self.assertFalse(finding["reproduced"])

    def test_worker_reported_missing_command_wins_over_grader_environment(self):
        present = Path(sys.executable).name
        case = {"id": "normal-1", "kind": "normal", "prompt": "x", "requires_commands": [present],
                "checks": [{"type": "exists", "path": "out.txt"}]}
        self.write("run1/out.txt", "faked\n")
        cases, runs = self.freeze([case], [self.completed(missing_commands=[present])])
        result = grade_cases.grade(cases, runs)
        self.assertEqual(result["runs"][0]["status"], "unavailable")
        self.assertEqual(result["runs"][0]["availability_source"], "worker report and grader environment")

    def test_hash_target_ignores_bytecode_and_tracks_edits(self):
        before = grade_cases.hash_tree(self.target)
        self.write("target/__pycache__/x.cpython-39.pyc", "cache")
        self.assertEqual(grade_cases.hash_tree(self.target), before)
        self.write("target/references/new.md", "new\n")
        self.assertNotEqual(grade_cases.hash_tree(self.target), before)


if __name__ == "__main__":
    unittest.main()
