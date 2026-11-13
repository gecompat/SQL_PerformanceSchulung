"""Offline regressions for the isolated QRY-023 resource-bounded caller."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import contextlib
import io
import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
PROXY_PATH = ROOT / "Tests/Runtime/qry023_docker_sqlcmd_proxy.py"
spec = importlib.util.spec_from_file_location("qry023_docker_sqlcmd_proxy_test", PROXY_PATH)
assert spec and spec.loader
proxy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proxy)
PROVISION_PATH = ROOT / "Tests/Runtime/provision_qry023_reader_login.py"
provision_spec = importlib.util.spec_from_file_location("qry023_reader_provision_test", PROVISION_PATH)
assert provision_spec and provision_spec.loader
provision = importlib.util.module_from_spec(provision_spec)
provision_spec.loader.exec_module(provision)
TOOLS = ROOT / "Demos/00_Framework/Tools"
sys.path.insert(0, str(TOOLS))
import run_demo  # noqa: E402


class Qry023RuntimeCallerTests(unittest.TestCase):
    def test_parser_binds_profile_username_without_password_arguments(self) -> None:
        database, script, username, variables, passthrough = proxy.parse_args([
            "-b", "-r", "1", "-W", "-s", "|", "-h", "-1", "-w", "65535",
            "-S", "localhost", "-d", "master", "-i",
            str(ROOT / "Tests/Runtime/qry023_tempdb_resource_guard.sql"),
            "-U", "ADMIN", "-v", "DemoId=QRY023", "RunToken=LOCAL",
        ])
        self.assertEqual((database, username), ("master", "ADMIN"))
        self.assertTrue(script.is_file())
        self.assertEqual(variables, ["DemoId=QRY023", "RunToken=LOCAL"])
        self.assertEqual(passthrough, ["-b", "-r", "1", "-W", "-s", "|", "-h", "-1", "-w", "65535"])

    def test_rejects_unexpected_flags(self) -> None:
        with self.assertRaises(ValueError):
            proxy.parse_args(["--password", "never-accepted"])

    def test_qry023_timeout_after_setup_suppresses_sql_cleanup(self) -> None:
        calls: list[str] = []

        def execute(*, phase, **_kwargs):
            calls.append(phase.phase_id)
            if phase.phase_id == "SETUP":
                return run_demo.PhaseResult(phase.phase_id, "FAIL", "FAIL_TIMEOUT", "timeout", 1.0)
            return run_demo.PhaseResult(phase.phase_id, "PASS", "OK", "done", 0.1)

        manifest = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/manifest.proposed.json"
        environment = {
            "SQLPERF_SQL_USERNAME_ADMIN": "sa",
            "SQLPERF_SQL_PASSWORD_ADMIN": "x",
            "SQLPERF_SQL_USERNAME_READER": "READER",
            "SQLPERF_SQL_PASSWORD_READER": "y",
            "SQLCMDPASSWORD": "x",
        }
        output = io.StringIO()
        with mock.patch.dict(os.environ, environment, clear=True), \
             mock.patch.object(run_demo, "resolve_sqlcmd", return_value="synthetic-sqlcmd"), \
             mock.patch.object(run_demo, "_execute_sql_phase", side_effect=execute), \
             contextlib.redirect_stdout(output):
            result = run_demo.run_demo(
                manifest_path=manifest, server="localhost", auth="sql", username="sa",
                sqlcmd_path="synthetic-sqlcmd", confirm_isolated_lab=True,
                allow_red=False, show_output=False,
            )
        self.assertEqual(calls, ["PREFLIGHT", "SETUP"])
        self.assertEqual(result.code, "FAIL_CLEANUP")
        self.assertEqual((result.phases[-1].phase_id, result.phases[-1].code), ("CLEANUP", "FAIL_CLEANUP"))
        self.assertIn("serverseitiges Ende und TempDB-Freigabe sind nicht bewiesen", result.phases[-1].message)

    def test_tempdb_guard_is_fail_closed_and_capped(self) -> None:
        sql = (ROOT / "Tests/Runtime/qry023_tempdb_resource_guard.sql").read_text(encoding="utf-8")
        self.assertIn("database_id > 4", sql)
        self.assertIn("@file_count <> 9", sql)
        self.assertIn("MAXSIZE = 96MB, FILEGROWTH = 64MB", sql)
        self.assertIn("SUM(CONVERT(bigint, max_size)) FROM tempdb.sys.database_files) > 131072", sql)

    def test_reader_login_is_created_from_stdin_without_password_argv(self) -> None:
        password = "QRY" + "023!" + "1" * 24 + "Read"
        admin_password = "A1!"
        sql = provision.build_sql(password)
        self.assertIn("CREATE LOGIN [READER]", sql)
        self.assertIn("QUOTENAME(@password, '''')", sql)
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLPERF_SQL_PASSWORD_READER": password,
            "SQLCMDPASSWORD": admin_password,
        }, clear=True), \
             mock.patch.object(provision, "sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(provision.subprocess, "run", return_value=SimpleNamespace(
                 returncode=0, stdout="QRY023_READER_LOGIN|PASS\n", stderr="")) as run, \
             contextlib.redirect_stdout(output):
            self.assertEqual(provision.main(), 0)
        command = run.call_args.args[0]
        self.assertNotIn(password, command)
        self.assertIn(password, run.call_args.kwargs["input"])
        self.assertEqual(run.call_args.kwargs["env"]["SQLCMDPASSWORD"], admin_password)
        with self.assertRaises(ValueError):
            provision.build_sql("short")

    def test_runtime_workflow_pins_images_and_bounds_disposable_resources(self) -> None:
        workflow = (ROOT / ".github/workflows/qry023-proposed-runtime.yml").read_text(encoding="utf-8")
        lock = json.loads(
            (ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/container-images.proposed.json")
            .read_text(encoding="utf-8")
        )
        for profile in lock["profiles"]:
            self.assertIn(profile["image"], workflow)
        self.assertIn("--cpus 2 --memory 4g", workflow)
        self.assertIn("MSSQL_MEMORY_LIMIT_MB=3072", workflow)
        self.assertIn("--env-file \"$env_file\"", workflow)
        self.assertNotIn('"MSSQL_SA_PASSWORD=${password}"', workflow)
        self.assertIn("provision_qry023_reader_login.py", workflow)
        self.assertIn("if: always()", workflow)
        self.assertIn("sqlperf.ci.owner", workflow)
        self.assertIn("runtime_authorized", lock)
        self.assertIs(lock["runtime_authorized"], False)


if __name__ == "__main__":
    unittest.main()
