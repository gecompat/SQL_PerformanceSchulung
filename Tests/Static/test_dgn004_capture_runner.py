"""Synthetic-process checks for bounded DGN-004 capture runner behavior."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))
from dgn004_capture_input import CaptureInput
from dgn004_capture_result import PlanCaptureResultError
from dgn004_capture_result import decode_plan_capture_result
from dgn004_capture_runner import (
    BoundedProcessResult,
    CaptureOutputLimitError,
    CaptureProcessEndUnknown,
    CaptureRunnerError,
    CaptureTimeoutError,
    build_capture_command,
    collect_bounded_process,
    run_plan_capture,
)
from dgn004_plan_frame import encode_plan_frame
from execution_target import DOCKER, ExecutionTarget


def child(code: str) -> list[str]:
    return [sys.executable, "-c", code]


def env() -> dict[str, str]:
    return {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}


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


class Dgn004CaptureRunnerTests(unittest.TestCase):
    def test_bounded_reader_accepts_exact_channel_limits_and_stdin(self) -> None:
        result = collect_bounded_process(
            child("import sys; d=sys.stdin.buffer.read(); sys.stdout.buffer.write(d); sys.stderr.buffer.write(b'err')"),
            input_bytes=b"data",
            environment=env(),
            timeout_seconds=2,
            stdout_limit_bytes=4,
            stderr_limit_bytes=3,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"data")
        self.assertEqual(result.stderr, b"err")

    def test_stdout_and_stderr_caps_are_enforced_while_reading(self) -> None:
        for channel, source in (("stdout", "sys.stdout.buffer.write(b'abcdef')"),
                                ("stderr", "sys.stderr.buffer.write(b'abcdef')")):
            with self.subTest(channel=channel):
                code = "import sys; " + source
                with self.assertRaisesRegex(CaptureOutputLimitError, channel):
                    collect_bounded_process(
                        child(code), input_bytes=b"", environment=env(), timeout_seconds=2,
                        stdout_limit_bytes=5, stderr_limit_bytes=5,
                    )

    def test_timeout_stops_the_synthetic_process(self) -> None:
        with self.assertRaises(CaptureTimeoutError):
            collect_bounded_process(
                child("import time; time.sleep(10)"), input_bytes=b"", environment=env(), timeout_seconds=0.1,
            )

    @unittest.skipIf(os.name == "nt", "process-group orphan proof is POSIX-specific")
    def test_parent_exit_with_inherited_pipe_kills_orphan_and_returns_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            pid_path = Path(folder) / "child.pid"
            code = (
                "import subprocess,sys; "
                "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
                "open(sys.argv[1],'w').write(str(p.pid))"
            )
            with self.assertRaises(CaptureProcessEndUnknown):
                collect_bounded_process(
                    child(code) + [str(pid_path)], input_bytes=b"", environment=env(), timeout_seconds=2,
                )
            self.assertTrue(pid_path.is_file())
            child_pid = int(pid_path.read_text(encoding="ascii"))
            time.sleep(0.05)
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                return
            stat_path = Path(f"/proc/{child_pid}/stat")
            if stat_path.exists():
                self.assertEqual(stat_path.read_text(encoding="ascii").split()[2], "Z")
            else:
                self.fail("orphan child is still running")

    def test_process_arguments_and_input_are_rejected_without_shell(self) -> None:
        for command in (("python", "bad\x00arg"), ("", "arg")):
            with self.subTest(command=command):
                with self.assertRaises(CaptureRunnerError):
                    collect_bounded_process(command, input_bytes=b"", environment=env())

    def test_builder_uses_direct_docker_exec_and_never_puts_secret_in_argv(self) -> None:
        fake_password = "synthetic-only-password"
        with patch.dict(os.environ, {"SQLCMDPASSWORD": fake_password}):
            command, sql_source, environment = build_capture_command(
                target(), database="DGN004_Test_DB",
                inputs=CaptureInput("dgn004-run-1", "R", 3, "ab" * 64),
            )
        self.assertEqual(command[1:5], ["exec", "-i", "-e", "SQLCMDPASSWORD"])
        self.assertIn("-t", command)
        self.assertIn("15", command)
        self.assertNotIn(fake_password, command)
        self.assertEqual(environment["SQLCMDPASSWORD"], fake_password)
        self.assertIn(b"sys.dm_exec_query_plan_stats", sql_source)
        self.assertIn("DGN004_PLAN_HANDLE=" + "AB" * 64, command)

    def test_runner_binds_only_invocation_labels_after_a_bounded_process_result(self) -> None:
        xml = '<ShowPlanXML xmlns="http://schemas.microsoft.com/sqlserver/2004/07/showplan"/>'
        frame = encode_plan_frame(xml.encode("utf-16-le"), run="run-1", role="H", call=4)
        result = BoundedProcessResult(0, frame.encode("ascii"), b"", 0.02)
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-only-password"}), \
             patch("dgn004_capture_runner.collect_bounded_process", return_value=result):
            capture = run_plan_capture(
                target(), database="DGN004_Test_DB",
                inputs=CaptureInput("run-1", "H", 4, "cd" * 64),
            )
        self.assertEqual((capture.run, capture.role, capture.call), ("run-1", "H", 4))
        self.assertEqual(capture, decode_plan_capture_result(
            frame, expected_run="run-1", expected_role="H", expected_call=4
        ))

    def test_runner_rejects_process_failure_stderr_non_ascii_and_wrong_binding(self) -> None:
        xml = '<ShowPlanXML xmlns="http://schemas.microsoft.com/sqlserver/2004/07/showplan"/>'
        valid_frame = encode_plan_frame(xml.encode("utf-16-le"), run="run-1", role="R", call=3)
        cases = (
            (BoundedProcessResult(7, b"", b"synthetic-secret", 0.02), "ended unsuccessfully"),
            (BoundedProcessResult(0, valid_frame.encode("ascii"), b"warning", 0.02), "diagnostic output"),
            (BoundedProcessResult(0, b"\xff", b"", 0.02), "not ASCII"),
        )
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-only-password"}):
            for result, message in cases:
                with self.subTest(message=message), patch(
                    "dgn004_capture_runner.collect_bounded_process", return_value=result
                ):
                    with self.assertRaisesRegex(CaptureRunnerError, message) as error:
                        run_plan_capture(
                            target(), database="DGN004_Test_DB",
                            inputs=CaptureInput("run-1", "R", 3, "ef" * 64),
                        )
                    self.assertNotIn("synthetic-secret", str(error.exception))

            wrong_frame = encode_plan_frame(xml.encode("utf-16-le"), run="run-1", role="R", call=4)
            with patch(
                "dgn004_capture_runner.collect_bounded_process",
                return_value=BoundedProcessResult(0, wrong_frame.encode("ascii"), b"", 0.02),
            ):
                with self.assertRaisesRegex(PlanCaptureResultError, "does not match caller run/role/call binding"):
                    run_plan_capture(
                        target(), database="DGN004_Test_DB",
                        inputs=CaptureInput("run-1", "R", 3, "ef" * 64),
                    )

    def test_builder_rejects_host_target_and_option_like_database(self) -> None:
        value = CaptureInput("run-1", "R", 1, "ab" * 64)
        host = ExecutionTarget(
            kind="host", server="localhost", auth="integrated", username=None,
            shim=Path("unused-host.py"), sqlcmd_path="sqlcmd", container=None,
        )
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-only-password"}):
            with self.assertRaisesRegex(CaptureRunnerError, "disposable Docker"):
                build_capture_command(host, database="DGN004_Test_DB", inputs=value)
            with self.assertRaisesRegex(CaptureRunnerError, "invalid target database"):
                build_capture_command(target(), database="-danger", inputs=value)


if __name__ == "__main__":
    unittest.main()
