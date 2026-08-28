#!/usr/bin/env python3
"""Regression tests for QRY-004 runtime outcome handling."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
sys.path.insert(0, str(RUNTIME))

import run_adv008_qry004 as runner  # noqa: E402


class FakeTarget:
    kind = "docker"

    def connection_arguments(self) -> list[str]:
        return ["--server", "synthetic"]

    def child_environment(self) -> dict[str, str]:
        return {}


class Qry004RunnerTests(unittest.TestCase):
    def execute(self, summary: str, *, returncode: int = 0) -> tuple[tuple[str, str], str]:
        completed = subprocess.CompletedProcess(
            args=["synthetic"], returncode=returncode, stdout=summary + "\n", stderr=""
        )
        output = io.StringIO()
        with (
            mock.patch.object(runner.subprocess, "run", return_value=completed),
            mock.patch.object(runner, "assert_database_absent"),
            redirect_stdout(output),
        ):
            result = runner.run_demo(target=FakeTarget(), repetition=1)
        return result, output.getvalue()

    def test_pass_is_preserved(self) -> None:
        result, output = self.execute("SQLPERF_SUMMARY|PASS|OK")
        self.assertEqual(("PASS", "OK"), result)
        self.assertIn("|PASS|OK|", output)

    def test_warning_is_accepted_and_preserved(self) -> None:
        result, output = self.execute(
            "SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE"
        )
        self.assertEqual(("WARN", "WARN_EMPIRICAL_VARIANCE"), result)
        self.assertIn("|WARN|WARN_EMPIRICAL_VARIANCE|", output)

    def test_controlled_skip_is_accepted_and_preserved(self) -> None:
        result, output = self.execute(
            "SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING"
        )
        self.assertEqual(("SKIP", "SKIP_EVIDENCE_MISSING"), result)
        self.assertIn("|SKIP|SKIP_EVIDENCE_MISSING|", output)

    def test_fail_summary_is_rejected(self) -> None:
        with self.assertRaises(runner.Qry004Failure):
            self.execute("SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT")

    def test_missing_summary_is_rejected(self) -> None:
        with self.assertRaises(runner.Qry004Failure):
            self.execute("synthetic output without summary")

    def test_nonzero_exit_is_rejected(self) -> None:
        with self.assertRaises(runner.Qry004Failure):
            self.execute("SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE", returncode=1)


if __name__ == "__main__":
    unittest.main()
