from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "Demos/00_Framework/Tools"), str(ROOT / "Tests/Runtime")]
import run_demo
from run_optsp_paired import IMAGE, OwnedPilot, recover_framework_container


MANIFEST = ROOT / "Demos/04_Optimizer_Statistics_Plans/OPT-018_Optimized_Sp_Executesql/manifest.json"


class Opt018DemoPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.phase = run_demo.load_manifest(MANIFEST).phases[0]

    def test_copied_manifest_cannot_launch_container(self) -> None:
        self.assertEqual(self.phase.kind, "opt018_container")
        with TemporaryDirectory() as directory:
            copy = Path(directory) / MANIFEST.name
            shutil.copyfile(MANIFEST, copy)
            shutil.copyfile(self.phase.path, copy.with_name(self.phase.path.name))
            with self.assertRaisesRegex(ValueError, "self-cleaning OPT-018"):
                run_demo.load_manifest(copy)

    @patch("run_demo._execute_opt018_container_phase")
    def test_confirmation_precedes_container_launch(self, launch) -> None:
        result = run_demo.run_demo(
            manifest_path=MANIFEST, server=None, auth="integrated", username=None, sqlcmd_path=None,
            confirm_isolated_lab=False, allow_red=False, show_output=False,
        )
        self.assertEqual(result.code, "FAIL_SAFETY")
        launch.assert_not_called()

    @patch.dict("os.environ", {"SQLCMDPASSWORD": "must-not-cross", "SQLPERF_SQL_USERNAME": "must-not-cross"})
    @patch("run_demo.subprocess.run")
    def test_harness_accepts_only_one_matching_summary(self, process) -> None:
        marker = "SQLPERF_SUMMARY|PASS|OK\n"
        for status, output, expected in (
            (0, marker, "OK"), (0, marker * 2, "FAIL_CONTRACT"), (1, marker, "FAIL_CONTRACT"),
            (1, "SQLPERF_SUMMARY|FAIL|FAIL_NOT_PROVEN\n", "FAIL_NOT_PROVEN"),
            (3, "SQLPERF_SUMMARY|FAIL|FAIL_CLEANUP\n", "FAIL_CLEANUP"),
        ):
            with self.subTest(status=status, expected=expected):
                process.return_value = subprocess.CompletedProcess([], status, output, "")
                result = run_demo._execute_opt018_container_phase(self.phase, timeout_seconds=1)
                self.assertEqual(result.code, expected)
        args, options = process.call_args
        self.assertEqual(args[0], [sys.executable, str(self.phase.path)])
        self.assertNotIn("SQLCMDPASSWORD", options["env"])
        self.assertNotIn("SQLPERF_SQL_USERNAME", options["env"])

    @patch("run_demo.subprocess.run")
    def test_timeout_recovers_with_same_owner_and_never_passes(self, process) -> None:
        for recovery_status, expected in ((0, "FAIL_TIMEOUT"), (3, "FAIL_CLEANUP")):
            with self.subTest(recovery_status=recovery_status):
                process.reset_mock()
                process.side_effect = [
                    subprocess.TimeoutExpired(["python"], 1),
                    subprocess.CompletedProcess([], recovery_status, "", ""),
                ]
                result = run_demo._execute_opt018_container_phase(self.phase, timeout_seconds=1)
                self.assertEqual((result.outcome, result.code), ("FAIL", expected))
                original, recovery = process.call_args_list
                self.assertEqual(recovery.args[0], [*original.args[0], "--recover"])
                owner = original.kwargs["env"]["SQLPERF_OPT018_OWNER_TOKEN"]
                self.assertRegex(owner, r"^[0-9a-f]{32}$")
                self.assertEqual(recovery.kwargs["env"]["SQLPERF_OPT018_OWNER_TOKEN"], owner)

    @patch.object(OwnedPilot, "_bind_local_context")
    @patch.object(OwnedPilot, "_owned_container")
    @patch.object(OwnedPilot, "_docker")
    def test_recovery_requires_matching_ownership_and_image(self, docker, owned, bind) -> None:
        token, container = "a" * 32, "b" * 64
        image_id = "sha256:" + "c" * 64
        owned.return_value = container
        docker.side_effect = [image_id, "sha256:" + "d" * 64]
        self.assertFalse(recover_framework_container(token))
        self.assertEqual([call.args[0] for call in docker.call_args_list], ["image", "inspect"])

        docker.reset_mock()
        owned.side_effect = [container, container, None]
        docker.side_effect = [image_id, image_id, container]
        self.assertTrue(recover_framework_container(token))
        self.assertEqual(docker.call_args_list[0].args, ("image", "inspect", "--format", "{{.Id}}", IMAGE))
        self.assertEqual(docker.call_args.args, ("rm", "--force", "--volumes", container))
        bind.assert_called()


if __name__ == "__main__":
    unittest.main()
