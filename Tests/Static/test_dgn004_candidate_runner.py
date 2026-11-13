"""Synthetic-process tests for bounded plan-cache snapshot execution."""
from __future__ import annotations

import os
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests" / "Runtime"))
sys.path.insert(0, str(ROOT / "Tests" / "Static"))

from dgn004_candidate_runner import (  # noqa: E402
    CandidateRunnerError,
    MODULE_HEX_TOKEN,
    build_candidate_command,
    run_candidate_snapshot,
)
from dgn004_capture_runner import BoundedProcessResult, CaptureRunnerError  # noqa: E402
from dgn004_identity_snapshot import registered_text_views  # noqa: E402
from dgn004_plan_candidates import PlanCandidateInput  # noqa: E402
from execution_target import DOCKER, ExecutionTarget  # noqa: E402


def target() -> ExecutionTarget:
    return ExecutionTarget(
        kind=DOCKER,
        server="localhost",
        auth="sql",
        username="sa",
        shim=Path("unused-proxy.py"),
        sqlcmd_path="/opt/mssql-tools18/bin/sqlcmd",
        container="dgn004-throwaway-2026",
    )


def empty_frame(value: PlanCandidateInput) -> bytes:
    source = registered_text_views()[value.role].module_text.encode("utf-16le")
    digest = hashlib.sha256(source).hexdigest().upper()
    marker = f"{value.run}|{value.role}|{value.call}|0|{len(source)}|{digest}"
    return f"DGN004_CACHE_START|{marker}\r\nDGN004_CACHE_END|{marker}\r\n".encode("ascii")


class Dgn004CandidateRunnerTests(unittest.TestCase):
    def test_builder_uses_only_validated_values_and_streams_expected_source_as_stdin(self) -> None:
        value = PlanCandidateInput("dgn004-run-1", "R", 3, 73, 101)
        fake_password = "synthetic-only-password"
        with patch.dict(os.environ, {"SQLCMDPASSWORD": fake_password}):
            command, sql_source, environment = build_candidate_command(
                target(), database="DGN004_Test_DB", inputs=value
            )
        expected_module = registered_text_views()["R"].module_text.encode("utf-16le").hex().upper()
        self.assertIn("-t", command)
        self.assertIn("15", command)
        self.assertIn("DGN004_DATABASE_ID=73", command)
        self.assertIn("DGN004_OBJECT_ID=101", command)
        self.assertNotIn(fake_password, command)
        self.assertEqual(environment["SQLCMDPASSWORD"], fake_password)
        self.assertIn(expected_module.encode("ascii"), sql_source)
        self.assertNotIn(MODULE_HEX_TOKEN.encode("ascii"), sql_source)

    def test_builder_rejects_host_and_option_like_database(self) -> None:
        value = PlanCandidateInput("dgn004-run-1", "R", 3, 73, 101)
        host = ExecutionTarget(
            kind="host", server="localhost", auth="integrated", username=None,
            shim=Path("unused-host.py"), sqlcmd_path="sqlcmd", container=None,
        )
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-only-password"}):
            with self.assertRaisesRegex(CandidateRunnerError, "disposable Docker"):
                build_candidate_command(host, database="DGN004_Test_DB", inputs=value)
            with self.assertRaisesRegex(CandidateRunnerError, "invalid target database"):
                build_candidate_command(target(), database="-danger", inputs=value)

    def test_runner_parses_complete_frame_from_bounded_process(self) -> None:
        value = PlanCandidateInput("dgn004-run-1", "R", 3, 73, 101)
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-only-password"}), patch(
            "dgn004_candidate_runner.collect_bounded_process",
            return_value=BoundedProcessResult(0, empty_frame(value), b"", 0.02),
        ):
            result = run_candidate_snapshot(target(), database="DGN004_Test_DB", inputs=value)
        self.assertEqual((result.run, result.role, result.call), ("dgn004-run-1", "R", 3))
        self.assertEqual(result.rows, ())

    def test_runner_rejects_process_failure_diagnostics_and_wrong_frame(self) -> None:
        value = PlanCandidateInput("dgn004-run-1", "R", 3, 73, 101)
        cases = (
            (BoundedProcessResult(7, b"", b"synthetic-secret", 0.02), "ended unsuccessfully"),
            (BoundedProcessResult(0, b"", b"warning", 0.02), "wrote diagnostics"),
            (BoundedProcessResult(0, b"\xff", b"", 0.02), "not ASCII"),
            (BoundedProcessResult(0, empty_frame(PlanCandidateInput("other", "R", 3, 73, 101)), b"", 0.02),
             "incomplete or misbound"),
        )
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-only-password"}):
            for result, message in cases:
                with self.subTest(message=message), patch(
                    "dgn004_candidate_runner.collect_bounded_process", return_value=result
                ):
                    with self.assertRaisesRegex(CaptureRunnerError, message):
                        run_candidate_snapshot(target(), database="DGN004_Test_DB", inputs=value)


if __name__ == "__main__":
    unittest.main()
