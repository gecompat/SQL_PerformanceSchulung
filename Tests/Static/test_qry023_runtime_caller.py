"""Offline regressions for the isolated QRY-023 resource-bounded caller."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import contextlib
import io
import json
import os
import sys
import tempfile
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
NEGATIVE_PROXY_PATH = ROOT / "Tests/Runtime/qry023_negative_permission_proxy.py"
negative_proxy_spec = importlib.util.spec_from_file_location("qry023_negative_permission_proxy_test", NEGATIVE_PROXY_PATH)
assert negative_proxy_spec and negative_proxy_spec.loader
negative_proxy = importlib.util.module_from_spec(negative_proxy_spec)
negative_proxy_spec.loader.exec_module(negative_proxy)
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

    def test_proxy_inlines_repository_local_sqlcmd_includes(self) -> None:
        wrapper = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/15_Framework.sql"
        expanded = proxy.expand_sqlcmd_includes(wrapper, ROOT)
        self.assertNotIn(":r Demos/00_Framework/Sql/FWK_Measurement.sql", expanded)
        self.assertIn("FWK-004 reference implementation", expanded)

    def test_proxy_rejects_sqlcmd_include_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            repository = parent / "repository"
            repository.mkdir()
            outside = parent / "outside.sql"
            outside.write_text("SELECT 1;", encoding="utf-8")
            wrapper = repository / "wrapper.sql"
            wrapper.write_text(":r ../outside.sql\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                proxy.expand_sqlcmd_includes(wrapper, repository)

    def test_negative_permission_proxy_only_injects_before_bound_admin_inventory(self) -> None:
        base = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        self.assertEqual(negative_proxy.injection_target(base), "SQLPERF_LAB_QRY023_LOCAL")
        unrelated = base.copy()
        unrelated[unrelated.index("-i") + 1] = str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/25_Qualification_Preflight.sql")
        self.assertIsNone(negative_proxy.injection_target(unrelated))
        with tempfile.TemporaryDirectory() as temporary:
            same_name = Path(temporary) / "22_Admin_Permission_Inventory.sql"
            same_name.write_text("SELECT 1;", encoding="utf-8")
            unrelated[unrelated.index("-i") + 1] = str(same_name)
            self.assertIsNone(negative_proxy.injection_target(unrelated))

    def test_negative_permission_proxy_uses_password_environment_and_fixed_grant(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0) as forward, \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        command = run.call_args.args[0]
        self.assertIn("SQLCMDPASSWORD", command)
        self.assertNotIn("synthetic-secret", command)
        self.assertEqual(run.call_args.kwargs["input"],
                         "GRANT SELECT ON OBJECT::lab.MeasurementWaitSnapshot TO [READER];\n"
                         "ALTER ROLE [db_datareader] ADD MEMBER [READER];\n")
        self.assertIn("QRY023_NEGATIVE_PERMISSION|EXTRA_GRANT_AND_ROLE_INJECTED", output.getvalue())
        forward.assert_called_once_with()

    def test_negative_permission_proxy_reports_bounded_sqlcmd_failure_details(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        errors = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(
                 returncode=1, stdout="Msg 15151, Level 16: permission grant failed", stderr=""
             )), \
             mock.patch.object(negative_proxy.proxy, "main") as forward, \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stderr(errors):
            self.assertEqual(negative_proxy.main(), 1)
        self.assertIn("Msg 15151, Level 16: permission grant failed", errors.getvalue())
        self.assertNotIn("synthetic-secret", errors.getvalue())
        forward.assert_not_called()

    def test_negative_permission_proxy_has_only_fixed_direct_deny_mode(self) -> None:
        sql, marker = negative_proxy.injection_for_mode("DIRECT_DENY")
        self.assertEqual(sql, "DENY SELECT ON OBJECT::dbo.Person TO [READER];\n")
        self.assertEqual(marker, "QRY023_NEGATIVE_PERMISSION|DIRECT_DENY_INJECTED")
        with self.assertRaises(ValueError):
            negative_proxy.injection_for_mode("arbitrary SQL")

    def test_negative_permission_proxy_corrupts_only_runner_valid_preflight_token(self) -> None:
        run_token = "QRY023VALID1"
        args = [
            "-S", "localhost", "-d", "master", "-U", "sa", "-b", "-v",
            "DemoId=QRY-023", f"RunToken={run_token}",
            f"TargetDatabase=SQLPERF_LAB_QRY023_{run_token}",
            "-i", str(negative_proxy.PREFLIGHT_SCRIPT),
        ]
        rewritten = negative_proxy.corrupt_preflight_run_token_trailing_space(args)
        self.assertIn(f"RunToken={run_token} ", rewritten)
        self.assertNotIn(f"TargetDatabase=SQLPERF_LAB_QRY023_{run_token} ", rewritten)
        with self.assertRaises(ValueError):
            negative_proxy.corrupt_preflight_run_token_trailing_space(
                [*args[:args.index(f"RunToken={run_token}")], f"RunToken={run_token} ", *args[args.index(f"RunToken={run_token}") + 1:]]
            )
        with self.assertRaises(ValueError):
            negative_proxy.corrupt_preflight_run_token_trailing_space(
                [*args[:args.index("-i")], str(negative_proxy.INVENTORY_SCRIPT), *args[args.index("-i") + 1:]]
            )

    def test_negative_permission_proxy_corrupts_only_runner_bound_target_name(self) -> None:
        run_token = "QRY023VALID1"
        target = f"SQLPERF_LAB_QRY023_{run_token}"
        args = [
            "-S", "localhost", "-d", "master", "-U", "sa", "-b", "-v",
            "DemoId=QRY-023", f"RunToken={run_token}", f"TargetDatabase={target}",
            "-i", str(negative_proxy.PREFLIGHT_SCRIPT),
        ]
        rewritten = negative_proxy.corrupt_preflight_target_database_trailing_space(args)
        self.assertIn(f"TargetDatabase={target} ", rewritten)
        self.assertIn(f"RunToken={run_token}", rewritten)
        with self.assertRaises(ValueError):
            negative_proxy.corrupt_preflight_target_database_trailing_space(
                [*args[:args.index(f"TargetDatabase={target}")], f"TargetDatabase={target} ",
                 *args[args.index(f"TargetDatabase={target}") + 1:]]
            )
        with self.assertRaises(ValueError):
            negative_proxy.corrupt_preflight_target_database_trailing_space(
                [*args[:args.index("-i")], str(negative_proxy.INVENTORY_SCRIPT), *args[args.index("-i") + 1:]]
            )

    def test_negative_permission_proxy_corrupts_only_runner_demo_id(self) -> None:
        run_token = "QRY023VALID1"
        target = f"SQLPERF_LAB_QRY023_{run_token}"
        args = [
            "-S", "localhost", "-d", "master", "-U", "sa", "-b", "-v",
            "DemoId=QRY-023", f"RunToken={run_token}", f"TargetDatabase={target}",
            "-i", str(negative_proxy.PREFLIGHT_SCRIPT),
        ]
        rewritten = negative_proxy.corrupt_preflight_demo_id_trailing_space(args)
        self.assertIn("DemoId=QRY-023 ", rewritten)
        self.assertIn(f"RunToken={run_token}", rewritten)
        self.assertIn(f"TargetDatabase={target}", rewritten)
        with self.assertRaises(ValueError):
            negative_proxy.corrupt_preflight_demo_id_trailing_space(
                [*args[:args.index("DemoId=QRY-023")], "DemoId=QRY-023 ",
                 *args[args.index("DemoId=QRY-023") + 1:]]
            )
        with self.assertRaises(ValueError):
            negative_proxy.corrupt_preflight_demo_id_trailing_space(
                [*args[:args.index("-i")], str(negative_proxy.INVENTORY_SCRIPT), *args[args.index("-i") + 1:]]
            )

    def test_negative_permission_proxy_binds_demo_id_case_variant_to_matching_target(self) -> None:
        run_token = "QRY023VALID1"
        args = [
            "-S", "localhost", "-d", "master", "-U", "sa", "-b", "-v",
            "DemoId=QRY-023", f"RunToken={run_token}",
            f"TargetDatabase=SQLPERF_LAB_QRY023_{run_token}",
            "-i", str(negative_proxy.PREFLIGHT_SCRIPT),
        ]
        rewritten = negative_proxy.corrupt_preflight_demo_id_case_variant(args)
        self.assertIn("DemoId=qry-023", rewritten)
        self.assertIn(f"TargetDatabase=SQLPERF_LAB_qry023_{run_token}", rewritten)
        with self.assertRaises(ValueError):
            negative_proxy.corrupt_preflight_demo_id_case_variant(
                [*args[:args.index("-i")], str(negative_proxy.INVENTORY_SCRIPT), *args[args.index("-i") + 1:]]
            )

    def test_negative_permission_proxy_server_role_mode_is_fixed(self) -> None:
        sql, marker = negative_proxy.injection_for_mode("SERVER_ROLE")
        self.assertEqual(sql, "ALTER SERVER ROLE [dbcreator] ADD MEMBER [READER];\n")
        self.assertEqual(marker, "QRY023_NEGATIVE_PERMISSION|SERVER_ROLE_INJECTED")
        securityadmin_sql, securityadmin_marker = negative_proxy.injection_for_mode("SECURITYADMIN_ROLE")
        self.assertIn("DECLARE @membership int=IS_SRVROLEMEMBER(N'securityadmin',N'READER')", securityadmin_sql)
        self.assertIn("ALTER SERVER ROLE [securityadmin] ADD MEMBER [READER]", securityadmin_sql)
        self.assertEqual(securityadmin_marker, "QRY023_NEGATIVE_PERMISSION|SECURITYADMIN_ROLE_INJECTED")

    def test_negative_permission_proxy_missing_object_mode_is_fixed(self) -> None:
        sql, marker = negative_proxy.injection_for_mode("MISSING_OBJECT")
        self.assertEqual(sql, "DROP TABLE lab.MeasurementWaitSnapshot;\n")
        self.assertEqual(marker, "QRY023_NEGATIVE_PERMISSION|EXPECTED_OBJECT_REMOVED")

    def test_negative_permission_proxy_server_permission_mode_is_fixed(self) -> None:
        sql, marker = negative_proxy.injection_for_mode("SERVER_PERMISSION")
        self.assertEqual(sql, "GRANT VIEW SERVER STATE TO [READER];\n")
        self.assertEqual(marker, "QRY023_NEGATIVE_PERMISSION|SERVER_PERMISSION_INJECTED")
        deny_sql, deny_marker = negative_proxy.injection_for_mode("SERVER_PERMISSION_DENY")
        self.assertEqual(deny_sql, "DENY VIEW SERVER STATE TO [READER];\n")
        self.assertEqual(deny_marker, "QRY023_NEGATIVE_PERMISSION|SERVER_PERMISSION_DENY_INJECTED")
        view_any_database_sql, view_any_database_marker = negative_proxy.injection_for_mode("VIEW_ANY_DATABASE_GRANT")
        self.assertEqual(view_any_database_sql, "GRANT VIEW ANY DATABASE TO [READER];\n")
        self.assertEqual(view_any_database_marker, "QRY023_NEGATIVE_PERMISSION|VIEW_ANY_DATABASE_GRANT_INJECTED")
        view_any_database_deny_sql, view_any_database_deny_marker = negative_proxy.injection_for_mode("VIEW_ANY_DATABASE_DENY")
        self.assertEqual(view_any_database_deny_sql, "DENY VIEW ANY DATABASE TO [READER];\n")
        self.assertEqual(view_any_database_deny_marker, "QRY023_NEGATIVE_PERMISSION|VIEW_ANY_DATABASE_DENY_INJECTED")
        connect_sql_deny, connect_sql_deny_marker = negative_proxy.injection_for_mode("CONNECT_SQL_DENY")
        self.assertIn("permission_name=N'CONNECT SQL' AND state=N'G'", connect_sql_deny)
        self.assertIn("DENY CONNECT SQL TO [READER]", connect_sql_deny)
        self.assertEqual(connect_sql_deny_marker, "QRY023_NEGATIVE_PERMISSION|CONNECT_SQL_DENY_INJECTED")
        database_sql, database_marker = negative_proxy.injection_for_mode("DATABASE_PERMISSION")
        self.assertEqual(database_sql, "GRANT VIEW DEFINITION TO [READER];\n")
        self.assertEqual(database_marker, "QRY023_NEGATIVE_PERMISSION|DATABASE_PERMISSION_INJECTED")
        database_deny_sql, database_deny_marker = negative_proxy.injection_for_mode("DATABASE_PERMISSION_DENY")
        self.assertEqual(database_deny_sql, "DENY VIEW DEFINITION TO [READER];\n")
        self.assertEqual(database_deny_marker, "QRY023_NEGATIVE_PERMISSION|DATABASE_PERMISSION_DENY_INJECTED")
        endpoint_sql, endpoint_marker = negative_proxy.injection_for_mode("ENDPOINT_PERMISSION")
        self.assertIn("WHERE name=N'TSQL Default TCP'", endpoint_sql)
        self.assertIn("GRANT CONNECT ON ENDPOINT::[TSQL Default TCP] TO [READER]", endpoint_sql)
        self.assertEqual(endpoint_marker, "QRY023_NEGATIVE_PERMISSION|ENDPOINT_PERMISSION_INJECTED")
        endpoint_deny_sql, endpoint_deny_marker = negative_proxy.injection_for_mode("ENDPOINT_PERMISSION_DENY")
        self.assertIn("DENY CONNECT ON ENDPOINT::[TSQL Default TCP] TO [READER]", endpoint_deny_sql)
        self.assertEqual(endpoint_deny_marker, "QRY023_NEGATIVE_PERMISSION|ENDPOINT_PERMISSION_DENY_INJECTED")
        custom_endpoint_sql, custom_endpoint_marker = negative_proxy.injection_for_mode("CUSTOM_ENDPOINT")
        self.assertIn("endpoint_id>=65536", custom_endpoint_sql)
        self.assertIn("CREATE ENDPOINT [QRY023_NEGATIVE_ENDPOINT] STATE=STOPPED", custom_endpoint_sql)
        self.assertIn("LISTENER_PORT=25032", custom_endpoint_sql)
        self.assertEqual(custom_endpoint_marker, "QRY023_NEGATIVE_PERMISSION|CUSTOM_ENDPOINT_INJECTED")

    def test_negative_server_permission_is_injected_from_master_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "SERVER_PERMISSION",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        self.assertEqual(run.call_args.args[0][run.call_args.args[0].index("-d") + 1], "master")
        self.assertEqual(run.call_args.kwargs["input"], "GRANT VIEW SERVER STATE TO [READER];\n")
        self.assertIn("QRY023_NEGATIVE_PERMISSION|SERVER_PERMISSION_INJECTED", output.getvalue())

    def test_negative_server_permission_deny_uses_master_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "SERVER_PERMISSION_DENY",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        self.assertEqual(run.call_args.args[0][run.call_args.args[0].index("-d") + 1], "master")
        self.assertEqual(run.call_args.kwargs["input"], "DENY VIEW SERVER STATE TO [READER];\n")
        self.assertIn("QRY023_NEGATIVE_PERMISSION|SERVER_PERMISSION_DENY_INJECTED", output.getvalue())

    def test_negative_view_any_database_grant_uses_master_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "VIEW_ANY_DATABASE_GRANT",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        self.assertEqual(run.call_args.args[0][run.call_args.args[0].index("-d") + 1], "master")
        self.assertEqual(run.call_args.kwargs["input"], "GRANT VIEW ANY DATABASE TO [READER];\n")
        self.assertIn("QRY023_NEGATIVE_PERMISSION|VIEW_ANY_DATABASE_GRANT_INJECTED", output.getvalue())

    def test_negative_view_any_database_deny_uses_master_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "VIEW_ANY_DATABASE_DENY",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        self.assertEqual(run.call_args.args[0][run.call_args.args[0].index("-d") + 1], "master")
        self.assertEqual(run.call_args.kwargs["input"], "DENY VIEW ANY DATABASE TO [READER];\n")
        self.assertIn("QRY023_NEGATIVE_PERMISSION|VIEW_ANY_DATABASE_DENY_INJECTED", output.getvalue())

    def test_negative_connect_sql_deny_uses_master_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "CONNECT_SQL_DENY",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        self.assertEqual(run.call_args.args[0][run.call_args.args[0].index("-d") + 1], "master")
        self.assertIn("DENY CONNECT SQL TO [READER];\n", run.call_args.kwargs["input"])
        self.assertIn("QRY023_NEGATIVE_PERMISSION|CONNECT_SQL_DENY_INJECTED", output.getvalue())

    def test_negative_database_permission_uses_bound_target_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "DATABASE_PERMISSION",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        self.assertEqual(run.call_args.args[0][run.call_args.args[0].index("-d") + 1], "SQLPERF_LAB_QRY023_LOCAL")
        self.assertEqual(run.call_args.kwargs["input"], "GRANT VIEW DEFINITION TO [READER];\n")
        self.assertIn("QRY023_NEGATIVE_PERMISSION|DATABASE_PERMISSION_INJECTED", output.getvalue())

    def test_negative_endpoint_permission_uses_master_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "ENDPOINT_PERMISSION",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("-d") + 1], "master")
        self.assertIn("GRANT CONNECT ON ENDPOINT::[TSQL Default TCP]", run.call_args.kwargs["input"])
        self.assertIn("QRY023_NEGATIVE_PERMISSION|ENDPOINT_PERMISSION_INJECTED", output.getvalue())

    def test_negative_endpoint_permission_deny_uses_master_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "ENDPOINT_PERMISSION_DENY",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("-d") + 1], "master")
        self.assertIn("DENY CONNECT ON ENDPOINT::[TSQL Default TCP]", run.call_args.kwargs["input"])
        self.assertIn("QRY023_NEGATIVE_PERMISSION|ENDPOINT_PERMISSION_DENY_INJECTED", output.getvalue())

    def test_negative_custom_endpoint_uses_master_context(self) -> None:
        args = [
            "-S", "localhost", "-d", "SQLPERF_LAB_QRY023_LOCAL", "-i",
            str(ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"),
            "-U", "sa", "-v", "DemoId=QRY-023", "RunToken=LOCAL",
            "TargetDatabase=SQLPERF_LAB_QRY023_LOCAL", "ReaderLogin=READER",
        ]
        output = io.StringIO()
        with mock.patch.dict(os.environ, {
            "SQLPERF_SQL_CONTAINER": "synthetic-container",
            "SQLCMDPASSWORD": "synthetic-secret",
            "SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE": "CUSTOM_ENDPOINT",
        }, clear=True), \
             mock.patch.object(negative_proxy.proxy, "_sqlcmd_path", return_value="/synthetic/sqlcmd"), \
             mock.patch.object(negative_proxy.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run, \
             mock.patch.object(negative_proxy.proxy, "main", return_value=0), \
             mock.patch.object(sys, "argv", ["negative-proxy", *args]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(negative_proxy.main(), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("-d") + 1], "master")
        self.assertIn("CREATE ENDPOINT [QRY023_NEGATIVE_ENDPOINT] STATE=STOPPED", run.call_args.kwargs["input"])
        self.assertIn("QRY023_NEGATIVE_PERMISSION|CUSTOM_ENDPOINT_INJECTED", output.getvalue())

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
        self.assertIn("@file_count NOT BETWEEN 2 AND 16", sql)
        self.assertIn("WHILE @stable_passes<2 AND @attempt<16", sql)
        self.assertIn("IF @current_file_count=@file_count AND NOT EXISTS", sql)
        self.assertIn("WAITFOR DELAY '00:00:01'", sql)
        self.assertIn("file set did not stabilize within the bounded configuration attempts", sql)
        self.assertIn("SET @max_file_mib=1024/@file_count", sql)
        self.assertIn("FILEGROWTH = 64MB", sql)
        self.assertIn("WHERE max_size<>@max_file_mib*128 OR growth<>8192 OR is_percent_growth<>0", sql)
        self.assertIn("IF @total_max_mib > 1024", sql)

    def test_runtime_workflow_requires_negative_permission_rejection_and_cleanup(self) -> None:
        workflow = (ROOT / ".github/workflows/qry023-proposed-runtime.yml").read_text(encoding="utf-8")
        self.assertLess(workflow.index("Prove the permission inventory rejects an unexpected READER grant"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects an explicit READER DENY"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects an unexpected READER server role"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects READER securityadmin membership"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects a missing expected object"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects an unexpected READER server permission"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects a denied READER server permission"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects an unexpected READER database permission"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects a denied READER database permission"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects an unexpected READER endpoint permission"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the permission inventory rejects a denied READER endpoint permission"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Run the full proposed FWK-010 lifecycle"),
                        workflow.index("Prove the permission inventory rejects an unregistered custom endpoint"))
        self.assertIn("Tests/Runtime/qry023_negative_permission_proxy.py", workflow)
        self.assertIn("SQLPERF_SUMMARY|FAIL|FAIL_NOT_PROVEN", workflow)
        self.assertIn("DATABASE_ROLE;", workflow)
        self.assertIn("DATABASE_PERMISSION;", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: RUNTOKEN_TRAILING_SPACE", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: TARGETDATABASE_TRAILING_SPACE", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: DEMOID_TRAILING_SPACE", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: DEMOID_CASE_VARIANT", workflow)
        self.assertEqual(workflow.count("Prove the SQL preflight rejects a trailing-space DemoId"), 1)
        self.assertEqual(workflow.count("Prove the SQL preflight rejects a case-variant DemoId"), 1)
        self.assertEqual(workflow.count("Prove the SQL preflight rejects a trailing-space target database name"), 1)
        self.assertEqual(workflow.count("Prove the SQL preflight rejects a trailing-space RunToken"), 1)
        self.assertLess(workflow.index("Prove the SQL preflight rejects a trailing-space target database name"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the SQL preflight rejects a trailing-space RunToken"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the SQL preflight rejects a trailing-space DemoId"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertLess(workflow.index("Prove the SQL preflight rejects a case-variant DemoId"),
                        workflow.index("Run the full proposed FWK-010 lifecycle"))
        self.assertIn("FAIL_CONTRACT: Demo-ID, Run-Token oder Ziel-Datenbank entsprechen nicht dem QRY-023-Vertrag.", workflow)
        run_token_case = workflow[
            workflow.index("Prove the SQL preflight rejects a trailing-space RunToken"):
            workflow.index("Prove the permission inventory rejects an unexpected READER grant")
        ]
        self.assertIn("QRY023_RUN_TOKEN_NEGATIVE|NO_DATABASE_CREATED", run_token_case)
        self.assertIn("CLEANUP: PASS/OK", run_token_case)
        target_case = workflow[
            workflow.index("Prove the SQL preflight rejects a trailing-space target database name"):
            workflow.index("Prove the permission inventory rejects an unexpected READER grant")
        ]
        self.assertIn("QRY023_TARGET_DATABASE_NEGATIVE|NO_DATABASE_CREATED", target_case)
        self.assertIn("CLEANUP: PASS/OK", target_case)
        demo_id_case = workflow[
            workflow.index("Prove the SQL preflight rejects a trailing-space DemoId"):
            workflow.index("Prove the permission inventory rejects an unexpected READER grant")
        ]
        self.assertIn("QRY023_DEMO_ID_NEGATIVE|NO_DATABASE_CREATED", demo_id_case)
        self.assertIn("CLEANUP: PASS/OK", demo_id_case)
        demo_id_case_variant = workflow[
            workflow.index("Prove the SQL preflight rejects a case-variant DemoId"):
            workflow.index("Prove the permission inventory rejects an unexpected READER grant")
        ]
        self.assertIn("QRY023_DEMO_ID_NEGATIVE|NO_DATABASE_CREATED", demo_id_case_variant)
        self.assertIn("CLEANUP: PASS/OK", demo_id_case_variant)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: DIRECT_DENY", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: SERVER_ROLE", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: SECURITYADMIN_ROLE", workflow)
        self.assertIn("QRY023_SECURITYADMIN_ROLE_ATTEMPTED=1", workflow)
        self.assertIn("if: always() && env.QRY023_SECURITYADMIN_ROLE_ATTEMPTED == '1'", workflow)
        self.assertIn("ALTER SERVER ROLE [securityadmin] DROP MEMBER [READER]", workflow)
        self.assertIn("QRY023_NEGATIVE_PERMISSION|SECURITYADMIN_ROLE_RESTORED", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: MISSING_OBJECT", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: SERVER_PERMISSION", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: SERVER_PERMISSION_DENY", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: VIEW_ANY_DATABASE_GRANT", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: VIEW_ANY_DATABASE_DENY", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: CONNECT_SQL_DENY", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: DATABASE_PERMISSION", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: DATABASE_PERMISSION_DENY", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: ENDPOINT_PERMISSION", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: ENDPOINT_PERMISSION_DENY", workflow)
        self.assertIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE: CUSTOM_ENDPOINT", workflow)
        self.assertIn("QRY023_ENDPOINT_PERMISSION_GRANTED=1", workflow)
        self.assertIn("if: always() && env.QRY023_ENDPOINT_PERMISSION_GRANTED == '1'", workflow)
        self.assertIn("if: always() && env.QRY023_CUSTOM_ENDPOINT_CREATED == '1'", workflow)
        self.assertIn("DROP ENDPOINT [QRY023_NEGATIVE_ENDPOINT]", workflow)
        self.assertIn("if: always() && env.QRY023_SERVER_ROLE_ATTEMPTED == '1'", workflow)
        self.assertIn("if: always() && env.QRY023_SERVER_PERMISSION_ATTEMPTED == '1'", workflow)
        self.assertIn("if: always() && env.QRY023_SERVER_PERMISSION_DENY_ATTEMPTED == '1'", workflow)
        self.assertIn("if: always() && env.QRY023_VIEW_ANY_DATABASE_ATTEMPTED == '1'", workflow)
        self.assertIn("if: always() && env.QRY023_VIEW_ANY_DATABASE_DENY_ATTEMPTED == '1'", workflow)
        self.assertIn("if: always() && env.QRY023_CONNECT_SQL_DENY_ATTEMPTED == '1'", workflow)
        self.assertIn("QRY023_NEGATIVE_PERMISSION|VIEW_ANY_DATABASE_GRANT_INJECTED", workflow)
        self.assertIn("QRY023_NEGATIVE_PERMISSION|VIEW_ANY_DATABASE_DENY_INJECTED", workflow)
        self.assertIn("QRY023_NEGATIVE_PERMISSION|CONNECT_SQL_DENY_INJECTED", workflow)
        self.assertIn("REVOKE CONNECT SQL FROM [READER]", workflow)
        self.assertIn("GRANT CONNECT SQL TO [READER]", workflow)
        self.assertIn("IF @had_deny=1 AND NOT EXISTS", workflow)
        connect_sql_deny_case = workflow[
            workflow.index("Prove the permission inventory rejects direct READER CONNECT SQL DENY"):
            workflow.index("Restore direct READER CONNECT SQL baseline")
        ]
        self.assertLess(
            connect_sql_deny_case.index("QRY023_NEGATIVE_PERMISSION|CONNECT_SQL_DENY_INJECTED"),
            connect_sql_deny_case.index("QRY023_CONNECT_SQL_DENY_ATTEMPTED=1"),
        )
        self.assertLess(
            connect_sql_deny_case.index("QRY023_CONNECT_SQL_DENY_ATTEMPTED=1"),
            connect_sql_deny_case.index('[[ "$result" == 2 ]]'),
        )
        self.assertIn("REVOKE VIEW ANY DATABASE FROM [READER]", workflow)
        self.assertLess(
            workflow.index("Prove the permission inventory rejects direct READER VIEW ANY DATABASE"),
            workflow.index("Run the full proposed FWK-010 lifecycle"),
        )
        self.assertLess(
            workflow.index("Prove the permission inventory rejects direct READER VIEW ANY DATABASE DENY"),
            workflow.index("Run the full proposed FWK-010 lifecycle"),
        )
        self.assertLess(
            workflow.index("Prove the permission inventory rejects direct READER CONNECT SQL DENY"),
            workflow.index("Run the full proposed FWK-010 lifecycle"),
        )
        endpoint_case = workflow[
            workflow.index("Prove the permission inventory rejects an unexpected READER endpoint permission"):
            workflow.index("Restore endpoint-permission baseline after negative control")
        ]
        self.assertLess(
            endpoint_case.index("QRY023_NEGATIVE_PERMISSION|ENDPOINT_PERMISSION_INJECTED"),
            endpoint_case.index("QRY023_ENDPOINT_PERMISSION_GRANTED=1"),
        )
        self.assertLess(
            endpoint_case.index("QRY023_ENDPOINT_PERMISSION_GRANTED=1"),
            endpoint_case.index('[[ "$result" == 2 ]]'),
        )
        endpoint_deny_case = workflow[
            workflow.index("Prove the permission inventory rejects a denied READER endpoint permission"):
            workflow.index("Restore denied endpoint-permission baseline after negative control")
        ]
        self.assertLess(
            endpoint_deny_case.index("QRY023_NEGATIVE_PERMISSION|ENDPOINT_PERMISSION_DENY_INJECTED"),
            endpoint_deny_case.index("QRY023_ENDPOINT_PERMISSION_DENY_GRANTED=1"),
        )
        self.assertLess(
            endpoint_deny_case.index("QRY023_ENDPOINT_PERMISSION_DENY_GRANTED=1"),
            endpoint_deny_case.index('[[ "$result" == 2 ]]'),
        )
        self.assertIn(
            "if: always() && env.QRY023_ENDPOINT_PERMISSION_DENY_GRANTED == '1'",
            workflow,
        )
        custom_endpoint_case = workflow[
            workflow.index("Prove the permission inventory rejects an unregistered custom endpoint"):
            workflow.index("Remove custom endpoint after negative control")
        ]
        self.assertLess(
            custom_endpoint_case.index("QRY023_NEGATIVE_PERMISSION|CUSTOM_ENDPOINT_INJECTED"),
            custom_endpoint_case.index("QRY023_CUSTOM_ENDPOINT_CREATED=1"),
        )
        self.assertLess(
            custom_endpoint_case.index("QRY023_CUSTOM_ENDPOINT_CREATED=1"),
            custom_endpoint_case.index('[[ "$result" == 2 ]]'),
        )
        custom_endpoint_cleanup = workflow[
            workflow.index("Remove custom endpoint after negative control"):
            workflow.index("Remove only the owned SQL Server container")
        ]
        self.assertIn("Required custom-endpoint cleanup ownership context is unavailable.", custom_endpoint_cleanup)
        self.assertLess(
            custom_endpoint_cleanup.index("Required custom-endpoint cleanup ownership context is unavailable."),
            custom_endpoint_cleanup.index("docker inspect --format '{{.Id}}'"),
        )
        self.assertLess(
            workflow.index("QRY023_NEGATIVE_PERMISSION|CUSTOM_ENDPOINT_REMOVED"),
            workflow.index("Remove only the owned SQL Server container"),
        )
        post_endpoint_steps = workflow[
            workflow.index("Remove custom endpoint after negative control"):
            workflow.index("Remove only the owned SQL Server container")
        ]
        self.assertEqual(post_endpoint_steps.count("      - name:"), 1)
        timeout_case = workflow[
            workflow.index("Prove a SQL timeout suppresses cleanup and preserves the marked target"):
            workflow.index("Prove the permission inventory rejects an unregistered custom endpoint")
        ]
        self.assertNotIn("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE", timeout_case)
        self.assertIn("plan[\"timeout_seconds\"] = 5", timeout_case)
        self.assertIn("WAITFOR DELAY '00:00:30'", timeout_case)
        self.assertIn('plan["script"] = ".qry023_timeout_probe.sql"', timeout_case)
        self.assertIn("Tests/Runtime/qry023_docker_sqlcmd_proxy.py", timeout_case)
        self.assertIn("PLAN_EVIDENCE: FAIL/FAIL_TIMEOUT", timeout_case)
        self.assertIn("CLEANUP: FAIL/FAIL_CLEANUP", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|MARKED_DATABASE_RETAINED", timeout_case)
        self.assertIn("python Demos/00_Framework/Tools/run_demo.py", timeout_case)
        self.assertIn("runner_pid=$!", timeout_case)
        self.assertIn('[[ "$result" != 4 ]]', timeout_case)
        self.assertIn("t.text LIKE N'%QRY023_TIMEOUT_PROBE|STARTED%'", timeout_case)
        self.assertIn("[[ \"$active\" == 1 ]]", timeout_case)
        self.assertIn("seq 1 1200", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|DMV_POLL_RESULT", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|PROBE_REQUEST_NOT_OBSERVED", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|RUNNER_EXIT", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|REQUEST_ENDED", timeout_case)
        self.assertIn("seq 1 45", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|REQUEST_STILL_ACTIVE", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|EXTERNAL_RECOVERY_STARTED", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|EXTERNAL_RECOVERY_STATUS", timeout_case)
        self.assertIn("grep -Fq 'SQLPERF_SUMMARY|PASS|OK' <<< \"$recovery_output\"", timeout_case)
        self.assertIn("QRY023_TIMEOUT_NEGATIVE|RECOVERY_CLEANUP_PASS", timeout_case)
        self.assertIn("CLEANUP: PASS/EXTERNAL_RECOVERY", timeout_case)
        self.assertIn("QRY023_TIMEOUT_HARNESS_LOG=${log}", timeout_case)
        self.assertIn("grep -Eq '^CLEANUP: PASS/'", timeout_case)
        self.assertIn('log="${QRY023_HARNESS_LOG:-${QRY023_TIMEOUT_HARNESS_LOG:-}}"', workflow)
        self.assertLess(workflow.index("Prove a SQL timeout suppresses cleanup and preserves the marked target"),
                        workflow.index("Prove the permission inventory rejects an unregistered custom endpoint"))
        self.assertLess(timeout_case.index("QRY023_TIMEOUT_NEGATIVE|REQUEST_ENDED"), workflow.index("Remove only the owned SQL Server container"))
        self.assertIn("DIRECT_DENY_INJECTED", workflow)
        self.assertIn("SERVER_ROLE_INJECTED", workflow)
        self.assertIn("EXPECTED_OBJECT_REMOVED", workflow)
        self.assertIn("OBJECT_INVENTORY;", workflow)
        self.assertIn("SERVER_PERMISSION_RESTORED", workflow)
        self.assertIn("SERVER_ROLE_RESTORED", workflow)
        self.assertIn("QRY023_HARNESS_LOG=${log}", workflow)
        self.assertIn("@membership IS NULL OR @membership<>0", workflow)
        self.assertIn("grep -F 'QRY023_NEGATIVE_PERMISSION|SERVER_ROLE_RESTORED'", workflow)
        self.assertIn("CLEANUP: PASS/OK", workflow)
        self.assertIn("CORRECTNESS|MEASUREMENT|PLAN_EVIDENCE", workflow)

    def test_readme_distinguishes_live_and_remaining_negative_permissions(self) -> None:
        readme = (ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/README.md").read_text(encoding="utf-8")
        self.assertIn("Live-Gegenprobe mit zusätzlichem direktem READER-`SELECT`-Grant", readme)
        self.assertIn("Mitgliedschaft in `db_datareader`", readme)
        self.assertIn("`VIEW SERVER STATE`-Grant", readme)
        self.assertIn("`securityadmin`", readme)
        self.assertIn("`25_Qualification_Preflight.sql`", readme)
        self.assertIn("`22_Admin_Permission_Inventory.sql`", readme)
        self.assertNotIn("nicht serverseitig verifiziert", readme)
        self.assertNotIn("Der Offlineentwurf für die Effektivrechteprüfung", readme)
        permission_design = (ROOT / "Documentation/Project_Planning/QRY023_EFFECTIVE_PERMISSION_DESIGN.md").read_text(encoding="utf-8")
        self.assertIn("PRs #566–#581", permission_design)
        self.assertNotIn("absichtlich fehlerhafte Live-Rechte wurden nicht", permission_design)
        self.assertIn("SQL-Kataloge wurden nicht ausgeführt", readme)
        self.assertNotIn("negative Live-Berechtigungsvarianten und absichtlich beschädigte SQL-Kataloge wurden nicht\nausgeführt", readme)

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
        self.assertIn("runs-on: ubuntu-latest", workflow)
        self.assertIn("login_ready=0", workflow)
        self.assertIn("-Q 'SELECT 1;'", workflow)
        self.assertIn("docker exec -e SQLCMDPASSWORD", workflow)
        self.assertIn("--env-file \"$env_file\"", workflow)
        self.assertNotIn('"MSSQL_SA_PASSWORD=${password}"', workflow)
        self.assertIn("provision_qry023_reader_login.py", workflow)
        self.assertEqual(workflow.count("'Tests/Runtime/provision_qry023_reader_login.py'"), 2)
        self.assertIn("if: always()", workflow)
        self.assertIn("sqlperf.ci.owner", workflow)
        self.assertIn("runtime_authorized", lock)
        self.assertIs(lock["runtime_authorized"], False)


if __name__ == "__main__":
    unittest.main()
