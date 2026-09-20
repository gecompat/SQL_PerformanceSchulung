#!/usr/bin/env python3
"""Regressionen für CL-Nachweis, Manifest-Cleanup und zwei QRY-006-Läufe."""
from __future__ import annotations

import contextlib
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests/Runtime"))
import run_qry006_null_semantics as runner
import run_demo as harness


class RuntimeOrderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.target = runner.execution_target.docker_target(
            container="synthetic-qry006", sqlcmd_path="sqlcmd"
        )

    def test_compatibility_evidence_requires_one_matching_assertion_marker(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            for major, level in ((15, 150), (16, 160), (17, 170)):
                for channel in ("stdout", "stderr"):
                    with self.subTest(major=major, channel=channel):
                        runner.assert_target_database_compatibility(
                            f"[ASSERTION:{channel}] QRY006_DATABASE_CL|{level}\n", major
                        )
            for output in (
                "", "150\n", "[SETUP:stdout] QRY006_DATABASE_CL|150\n",
                "[SETUP:stderr] QRY006_DATABASE_CL|150\n",
                "[ASSERTION:stdout] QRY006_DATABASE_CL|160\n",
                "[ASSERTION:stderr] QRY006_DATABASE_CL|160\n",
                "[ASSERTION:stdout] QRY006_DATABASE_CL|150\n" * 2,
                "[ASSERTION:stderr] QRY006_DATABASE_CL|150\n" * 2,
                "[ASSERTION:stdout] QRY006_DATABASE_CL|150\n"
                "[ASSERTION:stderr] QRY006_DATABASE_CL|150\n",
            ):
                with self.subTest(output=output), self.assertRaises(runner.Qry006Failure):
                    runner.assert_target_database_compatibility(output, 15)

    def test_real_harness_stderr_marker_is_accepted_before_absence_check(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            harness._emit_raw_output("ASSERTION", "", "QRY006_DATABASE_CL|150\n")
            print("SQLPERF_SUMMARY|PASS|OK")
        result = subprocess.CompletedProcess([], 0, stdout.getvalue(), stderr.getvalue())
        with patch.object(runner.subprocess, "run", return_value=result), \
             patch.object(runner, "assert_database_absent") as absent, \
             contextlib.redirect_stdout(io.StringIO()):
            runner.run_demo(target=self.target, repetition=1, major=15)
        absent.assert_called_once_with(self.target)

    def test_two_full_runs_query_only_absence_after_cleanup(self) -> None:
        events: list[str] = []

        def manifest_run(*args, **kwargs):
            self.assertIn(str(runner.MANIFEST), args[0])
            self.assertIn("--show-output", args[0])
            events.append("manifest-with-cleanup")
            return subprocess.CompletedProcess(args[0], 0,
                "[ASSERTION:stdout] QRY006_DATABASE_CL|150\nSQLPERF_SUMMARY|PASS|OK\n", "")

        def query(*args, **kwargs):
            self.assertEqual(kwargs["database"], "master")
            self.assertIn("IF DB_ID", kwargs["sql_text"])
            self.assertNotIn("compatibility_level", kwargs["sql_text"])
            events.append("independent-absence")
            return "ABSENT\n"

        with patch.object(runner.subprocess, "run", side_effect=manifest_run), \
             patch.object(runner.execution_target, "run_sql", side_effect=query), \
             patch.object(runner.execution_target, "docker_target", return_value=self.target), \
             patch.object(runner.execution_target, "verify_engine", return_value=15), \
             patch.object(sys, "argv", ["runner", "--container", "synthetic-qry006"]), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(), 0)
        self.assertEqual(events, ["manifest-with-cleanup", "independent-absence"] * 2)

    def test_manifest_assertion_precedes_cleanup_even_on_failed_compatibility(self) -> None:
        for assertion_outcome in ("PASS", "FAIL"):
            events: list[str] = []

            def execute(**kwargs):
                phase = kwargs["phase"]
                events.append(phase.phase_id)
                if phase.phase_id == "ASSERTION":
                    self.assertEqual(phase.database_selector, "target")
                    sql = phase.path.read_text(encoding="utf-8")
                    self.assertIn("FROM sys.databases WHERE database_id = DB_ID()", sql)
                    self.assertIn("@ActualCompatibility IS NULL", sql)
                    self.assertLess(sql.index("QRY006_DATABASE_CL|"), sql.index("SQLPERF_SUMMARY|PASS|OK"))
                    return harness.PhaseResult("ASSERTION", assertion_outcome,
                        "OK" if assertion_outcome == "PASS" else "FAIL_EXECUTION", "", 0)
                return harness.PhaseResult(phase.phase_id, "PASS", "OK", "", 0)

            with self.subTest(assertion_outcome=assertion_outcome), \
                 patch.object(harness, "resolve_sqlcmd", return_value="synthetic-sqlcmd"), \
                 patch.object(harness, "_execute_sql_phase", side_effect=execute):
                result = harness.run_demo(manifest_path=runner.MANIFEST, server="synthetic",
                    auth="integrated", username=None, sqlcmd_path=None,
                    confirm_isolated_lab=False, allow_red=False, show_output=False)
            self.assertEqual(result.outcome, assertion_outcome)
            self.assertEqual(events, ["PREFLIGHT", "SETUP", "DEMONSTRATION", "ASSERTION", "CLEANUP"])


if __name__ == "__main__":
    unittest.main()
