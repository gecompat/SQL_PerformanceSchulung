#!/usr/bin/env python3
"""Regressionen gegen falsche Versions-, Skip- und Evidenzfreigaben."""
import copy
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests/Runtime"))
import run_sql2025_ai_local as runner
import con010_controls


class EvidenceTests(unittest.TestCase):
    def test_con010_native_error_requires_exact_number_and_message(self):
        for code,detail in ((51004,'FAIL_STATE'),(51003,'FAIL_RESULT_CONTRACT')):
            text=f'Msg {code}, Level 16, State 1, Server synthetic-fixture, Line 22\n{detail}: Erwartete Abweisung.\n'
            self.assertTrue(con010_controls.expected_native_error(text,code,detail))
            self.assertTrue(con010_controls.expected_native_error('sqlcmd failed in database master: '+text,code,detail))
            for wrong in (text.replace(f'Msg {code}',f'Msg 1{code}'),text.replace(detail,detail+'X'),
                          text.replace('Msg ',''),text.replace(detail,'Anderer Fehler; '+detail)):
                with self.subTest(wrong=wrong):self.assertFalse(con010_controls.expected_native_error(wrong,code,detail))

    def test_con010_mixed_or_unassociated_native_errors_fail(self):
        expected='Msg 51004, Level 16, State 1, Line 7\r\nFAIL_STATE: Erwartete Abweisung.\r\n'
        wrong='Msg 229, Level 14, State 5, Line 8\nAnderer Fehler.\n'
        for text in (wrong+expected,expected+wrong,expected+expected,expected+'Msg 229, Level 14, State 5, Line 8',
                     expected.replace('FAIL_STATE:', 'Andere Nachricht.\nFAIL_STATE:')):
            with self.subTest(text=text):self.assertFalse(con010_controls.expected_native_error(text,51004,'FAIL_STATE'))

    def test_ci_readiness_passes_environment_name_without_secret_argument(self):
        workflow = (ROOT / ".github/workflows/sql2025-ai-local.yml").read_text(encoding="utf-8")
        readiness = workflow.split("- name: Verify SQL login readiness", 1)[1].split("- name:", 1)[0]
        self.assertRegex(readiness, r"docker exec -e SQLCMDPASSWORD\s")
        self.assertNotRegex(readiness, r"docker exec[^\n]*SQLCMDPASSWORD=")
        self.assertNotRegex(readiness, r"docker exec[^\n]*\s-P\s")

    def setUp(self):
        self.contract = {"contract_version": "1.0", "demo_id": "QRY-014", "profile": "LOCAL",
                         "assertions": [{"id": "a", "kind": "EXACT", "phase": "comparison",
                                         "metric": "rows", "expected": 5, "severity": "FAIL", "on_missing": "FAIL"}]}
        self.output = "[COMPARISON:stderr] AI_ASSERT|comparison|rows|5\nSQLPERF_SUMMARY|PASS|OK\n"

    def test_phase_output_evaluated(self):
        self.assertEqual(runner.assert_result(self.output, 0, 17, "QRY-014", self.contract), 1)

    def test_missing_wrong_duplicate_and_nonfinite_metrics_fail(self):
        for output in ("SQLPERF_SUMMARY|PASS|OK\n", self.output.replace("|5", "|4"),
                       self.output + "AI_ASSERT|comparison|rows|5\n",
                       self.output.replace("|5", "|NaN"), self.output.replace("|5", "|Infinity"),
                       self.output.replace("|5", "|abc"), self.output.replace("rows|5", "rows|5|extra")):
            with self.subTest(output=output), self.assertRaises(runner.AiFailure):
                runner.assert_result(output, 0, 17, "QRY-014", self.contract)

    def test_older_engine_requires_skip_before_setup(self):
        for major in (15, 16):
            self.assertEqual(runner.assert_result("SQLPERF_SUMMARY|SKIP|SKIP_VERSION\n", 0, major, "QRY-014", self.contract), 0)
            for output in (self.output, "SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION\n",
                           "[SETUP:stderr] started\nSQLPERF_SUMMARY|SKIP|SKIP_VERSION\n"):
                with self.subTest(major=major, output=output), self.assertRaises(runner.AiFailure):
                    runner.assert_result(output, 0, major, "QRY-014", self.contract)

    def test_native_engine_rejects_all_required_skips_and_bad_exit(self):
        for code in ("SKIP_VERSION", "SKIP_PERMISSION", "SKIP_FEATURE_UNAVAILABLE", "SKIP_COMPATIBILITY_LEVEL"):
            with self.subTest(code=code), self.assertRaises(runner.AiFailure):
                runner.assert_result(f"SQLPERF_SUMMARY|SKIP|{code}\n", 0, 17, "QRY-014", self.contract)
        with self.assertRaises(runner.AiFailure):
            runner.assert_result(self.output, 2, 17, "QRY-014", self.contract)

    def test_optional_fulltext_warning_only_for_search_demo(self):
        output = self.output.replace("PASS|OK", "WARN|WARN_OPTIONAL_EVIDENCE_SKIPPED")
        with self.assertRaises(runner.AiFailure):
            runner.assert_result(output, 0, 17, "QRY-014", self.contract)
        contract = copy.deepcopy(self.contract)
        contract["demo_id"] = "QRY-017"
        output += "AI_ASSERT|comparison|fulltext_installed|0\n"
        self.assertEqual(runner.assert_result(output, 0, 17, "QRY-017", contract), 1)
        for wrong in (output.replace("WARN|WARN_OPTIONAL_EVIDENCE_SKIPPED", "PASS|OK"),
                      output.replace("installed|0", "installed|1")):
            with self.assertRaises(runner.AiFailure):
                runner.assert_result(wrong, 0, 17, "QRY-017", contract)

    def test_cli_aggregate_keeps_warn_and_version_skip_visible(self):
        for major, outcome in ((17, ("WARN", "WARN_OPTIONAL_EVIDENCE_SKIPPED")),
                               (15, ("SKIP", "SKIP_VERSION"))):
            stream = io.StringIO()
            argv = ["runner", "--container", "synthetic-fixture", "--expected-major", str(major), "--demo", "QRY-017"]
            with patch.object(sys, "argv", argv), patch.object(runner.targets, "docker_target"), \
                 patch.object(runner.targets, "require_disposable_instance"), \
                 patch.object(runner.targets, "verify_engine", return_value=major), \
                 patch.object(runner, "run_demo", return_value=outcome), \
                 patch.object(runner, "ownership_controls"), redirect_stdout(stream):
                self.assertEqual(runner.main(), 0)
            self.assertIn("SQLPERF_SUMMARY|" + "|".join(outcome), stream.getvalue())
            self.assertNotIn("SQLPERF_SUMMARY|PASS", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
