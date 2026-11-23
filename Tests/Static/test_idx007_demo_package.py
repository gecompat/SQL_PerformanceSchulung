from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Demos/00_Framework/Tools"))
import run_demo


MANIFEST = ROOT / "Demos/04_Rowstore_Columnstore/IDX-007_Last_Page_Insert_Contention/manifest.json"


class Idx007DemoPackageTests(unittest.TestCase):
    def test_manifest_is_a_yellow_single_container_phase_with_a_bounded_run(self) -> None:
        manifest = run_demo.load_manifest(MANIFEST)
        self.assertEqual((manifest.demo_id, manifest.safety_level), ("IDX-007", "YELLOW"))
        self.assertEqual(len(manifest.phases), 1)
        self.assertEqual(manifest.phases[0].kind, "idx007_container")
        self.assertIsNone(manifest.cleanup)
        self.assertEqual(manifest.phases[0].timeout_seconds, 3500)

    def test_container_runtime_rejects_another_demo_id(self) -> None:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        payload["demo_id"] = "IDX-006"
        temporary = MANIFEST.parent / "manifest.invalid-test.json"
        try:
            temporary.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "restricted to the self-cleaning IDX-007"):
                run_demo.load_manifest(temporary)
        finally:
            temporary.unlink(missing_ok=True)

    @patch("run_demo.subprocess.run")
    def test_runtime_invokes_only_the_pinned_local_wrapper(self, process) -> None:
        process.return_value = __import__("subprocess").CompletedProcess([], 0, "WAIT_OVERLAP|PASS\nSQLPERF_SUMMARY|PASS|OK\n", "")
        phase = run_demo.load_manifest(MANIFEST).phases[0]
        result = run_demo._execute_idx007_container_phase(phase, major=17, timeout_seconds=300, show_output=False)
        self.assertEqual((result.outcome, result.code), ("PASS", "OK"))
        command = process.call_args.args[0]
        self.assertEqual(command[:2], [sys.executable, str(phase.path)])
        self.assertEqual(command[2:], ["--major", "17"])
        self.assertNotIn("shell", process.call_args.kwargs)
        child_environment = process.call_args.kwargs["env"]
        self.assertRegex(child_environment["SQLPERF_IDX007_OWNER_TOKEN"], r"^[0-9a-f]{32}$")
        self.assertNotIn("SQLCMDPASSWORD", child_environment)

    @patch.dict(os.environ, {"SQLCMDPASSWORD": "must-not-cross", "SQLPERF_SQL_PASSWORD_ADMIN": "must-not-cross"})
    @patch("run_demo.subprocess.run")
    def test_runtime_does_not_forward_host_sql_credentials(self, process) -> None:
        process.return_value = __import__("subprocess").CompletedProcess([], 0, "SQLPERF_SUMMARY|PASS|OK\n", "")
        phase = run_demo.load_manifest(MANIFEST).phases[0]
        run_demo._execute_idx007_container_phase(phase, major=15, timeout_seconds=300, show_output=False)
        environment = process.call_args.kwargs["env"]
        self.assertNotIn("SQLCMDPASSWORD", environment)
        self.assertNotIn("SQLPERF_SQL_PASSWORD_ADMIN", environment)

    @patch("run_demo.subprocess.run")
    def test_not_proven_is_a_visible_warning_not_a_success_claim(self, process) -> None:
        process.return_value = __import__("subprocess").CompletedProcess([], 0, "NOT_PROVEN|stage=2|no-overlap\nSQLPERF_SUMMARY|WARN|WARN_NOT_PROVEN\n", "")
        phase = run_demo.load_manifest(MANIFEST).phases[0]
        result = run_demo._execute_idx007_container_phase(phase, major=17, timeout_seconds=300, show_output=False)
        self.assertEqual((result.outcome, result.code), ("WARN", "WARN_NOT_PROVEN"))

    @patch("run_demo.resolve_sqlcmd", side_effect=AssertionError("sqlcmd must not be resolved"))
    def test_yellow_confirmation_is_enforced_before_starting_container(self, resolve_sqlcmd) -> None:
        manifest = run_demo.load_manifest(MANIFEST)
        result = run_demo.run_demo(manifest_path=MANIFEST, server=None, auth="integrated", username=None,
                                   sqlcmd_path=None, confirm_isolated_lab=False, allow_red=False,
                                   show_output=False, idx007_major=None)
        self.assertEqual((result.outcome, result.code), ("FAIL", "FAIL_SAFETY"))
        resolve_sqlcmd.assert_not_called()

    @patch("run_demo.os.urandom", return_value=bytes.fromhex("aa" * 16))
    @patch("run_demo.subprocess.run")
    def test_timeout_cleanup_is_limited_to_owned_isolated_containers(self, process, random_bytes) -> None:
        import subprocess

        process.side_effect = [
            subprocess.TimeoutExpired(["python"], 1),
            subprocess.CompletedProcess([], 0, "0123456789ab\n", ""),
            subprocess.CompletedProcess([], 0, json.dumps([{"Config": {"Labels": {"sqlperf.demo.id": "IDX-007", "sqlperf.demo.owner": "aa" * 16}}, "HostConfig": {"NetworkMode": "none"}}]), ""),
            subprocess.CompletedProcess([], 0, "0123456789ab\n", ""),
        ]
        phase = run_demo.load_manifest(MANIFEST).phases[0]
        result = run_demo._execute_idx007_container_phase(phase, major=15, timeout_seconds=1, show_output=False)
        self.assertEqual((result.outcome, result.code), ("FAIL", "FAIL_TIMEOUT"))
        self.assertIn("label=sqlperf.demo.owner=" + "aa" * 16, process.call_args_list[1].args[0])
        self.assertEqual(process.call_args_list[3].args[0][:3], ["docker", "rm", "--force"])

    @patch("run_demo.subprocess.run")
    def test_recovery_refuses_a_container_with_another_owner_token(self, process) -> None:
        import subprocess

        process.side_effect = [
            subprocess.CompletedProcess([], 0, "0123456789ab\n", ""),
            subprocess.CompletedProcess([], 0, json.dumps([{"Config": {"Labels": {"sqlperf.demo.id": "IDX-007", "sqlperf.demo.owner": "b" * 32}}, "HostConfig": {"NetworkMode": "none"}}]), ""),
        ]
        self.assertFalse(run_demo._cleanup_idx007_owned_container("a" * 32))
        self.assertEqual(process.call_count, 2)


if __name__ == "__main__":
    unittest.main()
