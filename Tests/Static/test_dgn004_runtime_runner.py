"""Pure tests for DGN-004 runtime orchestration boundaries."""
from __future__ import annotations

import json
import contextlib
import io
import time
import unittest
from unittest.mock import patch

from Tests.Runtime import dgn004_runtime_runner as runner
from Tests.Runtime import dgn004_container as container
from Tests.Runtime.dgn004_capture_runner import BoundedProcessResult


class Dgn004RuntimeRunnerTests(unittest.TestCase):
    def test_budget_fails_closed_at_batch_ceiling_and_deadline(self):
        budget = runner.BuildBudget(time.monotonic() + 10)
        budget.batches = runner.MAX_BATCHES_PER_BUILD - 1
        budget.reserve()
        with self.assertRaises(runner.Dgn004RuntimeError):
            budget.reserve()
        with self.assertRaises(runner.Dgn004TimeoutError):
            runner.BuildBudget(time.monotonic() - 1).reserve()

    def test_sqlcmd_diagnostic_is_classified_without_echoing_raw_text(self):
        raw = b"Login failed for user 'sa'; resource=sentinel-abc"
        category = runner._safe_sqlcmd_diagnostic(1, raw)
        self.assertEqual(category, "authentication-failed")
        self.assertNotIn("sentinel-abc", category)
        self.assertEqual(runner._safe_sqlcmd_diagnostic(1, b""), "nonzero-exit-1")
        self.assertEqual(
            runner._safe_sqlcmd_diagnostic(1, b"Msg 5808, Level 16, Server secret, Line 2"),
            "sql-server-error-5808",
        )
        self.assertEqual(
            runner._safe_sqlcmd_diagnostic(1, b"Msg 207, Level 16, Invalid column name 'count_compiles'."),
            "sql-server-error-207-column-count_compiles",
        )

    def test_sqlcmd_accepts_success_exit_with_routed_informational_stderr(self):
        target = runner.ExecutionTarget("docker", "localhost", "sql", "sa", runner.Path("shim"),
                                        "/opt/mssql-tools18/bin/sqlcmd", "owned")
        budget = runner.BuildBudget(time.monotonic() + 5)
        process = BoundedProcessResult(0, b"SAFE\n", b"informational diagnostic", 0.01)
        with patch.dict(runner.os.environ, {"SQLCMDPASSWORD": "ephemeral"}):
            with patch.object(runner, "collect_bounded_process", return_value=process) as collect:
                self.assertEqual(runner._sql_command(
                    target, database="master", source="SET NOCOUNT ON; SELECT 'SAFE';", budget=budget
                ), "SAFE\n")
        args = collect.call_args.args[0]
        self.assertEqual(args[args.index("-y") + 1], "8000")
        self.assertNotIn("-W", args)
        with patch.dict(runner.os.environ, {"SQLCMDPASSWORD": "ephemeral"}):
            with patch.object(runner, "collect_bounded_process", return_value=BoundedProcessResult(
                1, b"Msg 5808, Level 16, Server secret, Line 2", b"", 0.01
            )):
                with self.assertRaisesRegex(runner.Dgn004RuntimeError, "sql-server-error-5808"):
                    runner._sql_command(
                        target, database="master", source="SET NOCOUNT ON; SELECT 'SAFE';",
                        budget=runner.BuildBudget(time.monotonic() + 5),
                    )

    def test_generated_password_has_required_character_classes_and_safe_symbol(self):
        password = container._password()
        self.assertEqual(len(password), 32)
        self.assertTrue(any(char.isupper() for char in password))
        self.assertTrue(any(char.islower() for char in password))
        self.assertTrue(any(char.isdigit() for char in password))
        self.assertEqual(password.count("!"), 1)
        self.assertTrue(set(password) <= set("ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!"))

    def test_engine_preflight_binds_all_six_returned_fields(self):
        profile = container.BUILD_PROFILES[0]
        frame = "ENGINE|16.0.4265.3|Developer Edition (64-bit)|3|16|1|0\n"
        with patch.object(runner, "_sql_command", return_value=frame):
            runner._engine_preflight(None, profile, runner.BuildBudget(time.monotonic() + 5))
        with patch.object(runner, "_sql_command", return_value=frame.rstrip("\n") + "|extra\n"):
            with self.assertRaisesRegex(runner.Dgn004RuntimeError, "frame is malformed"):
                runner._engine_preflight(None, profile, runner.BuildBudget(time.monotonic() + 5))

    def test_engine_identity_queries_documented_host_platform_dmv(self):
        with patch.object(runner, "_sql_command", return_value="ENGINE|16.0.4265.3|Developer Edition (64-bit)|3|16|1|0\n") as sql:
            runner._server_identity(None, runner.BuildBudget(time.monotonic() + 5))
        query = sql.call_args.kwargs["source"]
        self.assertIn("FROM sys.dm_os_host_info", query)
        self.assertNotIn("SERVERPROPERTY('HostPlatform')", query)

    def test_module_probe_binds_source_through_sql_modules_catalog(self):
        sql = runner._module_probe_sql("R")
        self.assertIn("OBJECT_ID(N'[dgn004].[ReplayReference]')", sql)
        self.assertIn("FROM sys.sql_modules WHERE object_id=@ObjectId", sql)
        self.assertIn("DGN004_MODULE|", sql)
        self.assertNotIn("OBJECT_DEFINITION", sql)
        self.assertIn("DATALENGTH(@Definition)", sql)

    def test_module_definition_comparison_allows_only_server_terminal_lf(self):
        self.assertTrue(runner._module_definition_matches("CREATE PROC x AS SELECT 1", "CREATE PROC x AS SELECT 1"))
        self.assertTrue(runner._module_definition_matches("CREATE PROC x AS SELECT 1\n", "CREATE PROC x AS SELECT 1"))
        self.assertFalse(runner._module_definition_matches("CREATE PROC x AS SELECT 1\n\n", "CREATE PROC x AS SELECT 1"))
        self.assertFalse(runner._module_definition_matches("CREATE PROC X AS SELECT 1", "CREATE PROC x AS SELECT 1"))

    def test_actual_call_parser_accepts_sqlcmd_right_aligned_integer_columns(self):
        start = "DGN004_EXEC_START|R|1|42"
        end = "DGN004_EXEC_END|R|1|42"
        row = " | ".join(f"{value:>10}" for value in range(1, 11))
        output = "\n".join([start, *([row] * 768), end])
        parsed = runner._parse_call_output(output, "R", 1)
        self.assertEqual(len(parsed), 768)
        self.assertEqual(parsed[0], tuple(range(1, 11)))

    def test_query_store_metadata_binds_database_id_from_current_database(self):
        sql = runner._metadata_sql("R")
        self.assertIn("SELECT DB_ID() AS database_id,q.object_id", sql)
        self.assertNotIn("q.database_id", sql)
        self.assertIn("q.query_parameterization_type AS parameterization_type", sql)
        self.assertNotIn("q.parameterization_type", sql)
        self.assertIn("DGN004_META_CHUNK|", sql)
        self.assertIn("SUBSTRING(@Frame,((Ordinal-1)*@ChunkChars)+1,@ChunkChars)", sql)

    def test_query_store_metadata_reassembles_complete_ordered_chunks(self):
        row = {
            "database_id": 7, "object_id": 10, "query_id": 11, "query_text_id": 12,
            "context_settings_id": 13, "parameterization_type": 0, "query_hash": "0102030405060708",
            "query_text_hex": "41" * 9000, "count_compiles": 1,
            "last_compile_start_time": "2026-01-01T00:00:00", "engine_start_time": "2026-01-01T00:00:00",
        }
        frame = "DGN004_META|" + json.dumps([row]) + "|[]|[]"
        pieces = [frame[index:index + 3000] for index in range(0, len(frame), 3000)]
        chunked = "\n".join(
            f"DGN004_META_CHUNK|{index + 1}|{len(pieces)}|{piece}"
            for index, piece in enumerate(pieces)
        )
        self.assertEqual(len(runner._decode_meta(chunked).queries), 1)
        short_middle = "\n".join((
            "DGN004_META_CHUNK|1|2|short",
            "DGN004_META_CHUNK|2|2|DGN004_META|[]|[]|[]",
        ))
        with self.assertRaisesRegex(runner.Dgn004RuntimeError, "chunk sequence"):
            runner._decode_meta(short_middle)
        with self.assertRaisesRegex(runner.Dgn004RuntimeError, "chunk sequence"):
            runner._decode_meta("\n".join(reversed(chunked.splitlines())))

    def test_flush_snapshot_keeps_all_metadata_chunk_rows_after_flush_marker(self):
        frame = "DGN004_META|[]|[]|[]"
        pieces = [frame]
        chunked = "\n".join(
            f"DGN004_META_CHUNK|{index + 1}|{len(pieces)}|{piece}"
            for index, piece in enumerate(pieces)
        )
        budget = runner.BuildBudget(time.monotonic() + 5)
        with patch.object(runner, "_sql_command", return_value="DGN004_FLUSH|PASS\n" + chunked):
            snapshot = runner._flush_snapshot(None, "db", "R", budget)
        self.assertEqual((snapshot.queries, snapshot.plans, snapshot.executions), ((), (), ()))

    def test_control_response_consumes_all_following_metadata_chunks(self):
        with self.assertRaisesRegex(runner.Dgn004RuntimeError, "incomplete"):
            runner._metadata_after_control(["DGN004_FORCE|1|2|0|1"], "DGN004_FORCE|1|2|0|1", "Force")
        snapshot = runner._metadata_after_control(
            ["DGN004_FORCE|1|2|0|1", "DGN004_META|[]|[]|[]"],
            "DGN004_FORCE|1|2|0|1", "Force",
        )
        self.assertEqual((snapshot.queries, snapshot.plans, snapshot.executions), ((), (), ()))

    def test_query_store_restore_uses_current_option_nesting_and_names(self):
        baseline = {
            "compatibility_level": 160,
            "last_query_plan_stats": 1,
            "optimized_plan_forcing": 1,
            "query_store": [{
                "desired_state_desc": "READ_WRITE", "actual_state_desc": "READ_WRITE",
                "max_storage_size_mb": 1000, "flush_interval_seconds": 900,
                "interval_length_minutes": 60, "stale_query_threshold_days": 30,
                "size_based_cleanup_mode_desc": "AUTO", "query_capture_mode_desc": "ALL",
                "wait_stats_capture_mode_desc": "ON",
            }],
            "files": [{"file_id": 1, "name": "data", "type": 0, "max_size": -1}],
        }
        sql = runner._restore_database_sql("SQLPERF_LAB_DGN004_ABCDEF012345", baseline)
        self.assertIn("DATA_FLUSH_INTERVAL_SECONDS = 900", sql)
        self.assertIn("CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30)", sql)
        self.assertNotIn("\n    FLUSH_INTERVAL_SECONDS =", sql)

    def test_removed_mount_free_container_completes_pre_database_cleanup(self):
        self.assertTrue(runner._cleanup_is_sufficient(
            database_created=False, database_cleanup_ok=False, container_cleanup_ok=True))
        self.assertFalse(runner._cleanup_is_sufficient(
            database_created=False, database_cleanup_ok=True, container_cleanup_ok=False))
        self.assertFalse(runner._cleanup_is_sufficient(
            database_created=True, database_cleanup_ok=False, container_cleanup_ok=True))
        self.assertTrue(runner._cleanup_is_sufficient(
            database_created=True, database_cleanup_ok=True, container_cleanup_ok=True))

    def test_engine_mismatch_reports_only_field_categories(self):
        profile = container.BUILD_PROFILES[0]
        mismatches = runner._engine_mismatch_fields(
            (profile.product_version, profile.edition, "3", "16", "1", "1"), profile
        )
        self.assertEqual(mismatches, ("hadr-enabled",))

    def test_setup_configuration_scopes_last_plan_stats_to_owned_database(self):
        sql = runner._configure_database_sql("SQLPERF_LAB_DGN004_ABCDEF012345", 160)
        self.assertIn("USE [SQLPERF_LAB_DGN004_ABCDEF012345]", sql)
        self.assertIn("ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS = ON", sql)
        self.assertIn("actual_state_desc=N'READ_WRITE'", sql)

    def test_cleanup_requires_exact_four_markers_before_drop(self):
        sql = runner._drop_database_sql("SQLPERF_LAB_DGN004_ABCDEF012345", "ABCDEF012345")
        self.assertIn("@MarkerCount<>4", sql)
        self.assertIn("SQLPERF.Project", sql)
        self.assertIn("SQLPERF.ContractVersion", sql)
        self.assertIn("SQLPERF.DemoId", sql)
        self.assertIn("SQLPERF.RunToken", sql)
        self.assertLess(sql.index("IF @MarkerCount<>4"), sql.index("DROP DATABASE"))
        self.assertNotIn("IF (SELECT COUNT(*) FROM ' + QUOTENAME", sql)

    def test_call_plan_and_resource_limits_remain_fixed(self):
        self.assertEqual(
            runner.CALL_SEQUENCE,
            (("R", False), ("R", False), ("R", True), ("H", False),
             ("H", True), ("H", True), ("R", True), ("H", False), ("R", False)),
        )
        self.assertEqual(runner.MAX_BATCHES_PER_BUILD, 100)
        self.assertEqual(runner.MAX_FLUSHES_PER_BUILD, 9)
        self.assertEqual(runner.TOTAL_BUDGET_SECONDS, 900)
        self.assertEqual(runner.SQLCMD_SERVER_ADDRESS, "127.0.0.1")

    def test_startup_wait_polls_owned_logs_then_returns_on_readiness(self):
        name = "sqlperf_dgn004_2022_abcdef012345"
        with patch.object(container, "_docker", side_effect=["starting", container.SQL_READY_MARKER]) as docker:
            with patch.object(container.time, "sleep") as sleep:
                container.wait_until_sql_server_ready(name=name, deadline=time.monotonic() + 10)
        self.assertEqual(docker.call_count, 2)
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(sleep.call_args_list[-1].args[0], 1.5)

    def test_docker_logs_accept_server_output_routed_to_stderr(self):
        process = BoundedProcessResult(0, b"ordinary stdout\n", b"SQL Server is now ready for client connections.\n", 0.01)
        with patch.object(container, "collect_bounded_process", return_value=process):
            logs = container._docker(
                ["container", "logs", "--tail", "100", "sqlperf_dgn004_2022_abcdef012345"],
                allow_stderr=True,
            )
        self.assertIn(container.SQL_READY_MARKER, logs)

    def test_container_identity_requires_the_two_core_cpu_affinity(self):
        profile = container.BUILD_PROFILES[0]
        name = "sqlperf_dgn004_2022_abcdef012345"
        frame = "|".join((
            "a" * 64, f"{profile.image}@{profile.digest}", "SQL_PerformanceSchulung",
            "DGN-004", "ABCDEF012345", container.OWNER_VALUE,
            str(container.CPU_NANOCORES), "0-1", str(container.MEMORY_BYTES),
            str(container.MEMORY_BYTES), "none", "{}", "0", "running",
        ))
        with patch.object(container, "_docker", return_value=frame):
            self.assertEqual(container._inspect_identity(
                name, expected_profile=profile, expected_run_token="ABCDEF012345",
            ), ("a" * 64, "running"))
        with patch.object(container, "_docker", return_value=frame.replace("|0-1|", "|0-23|")):
            with self.assertRaisesRegex(container.ContainerError, "complete owned"):
                container._inspect_identity(
                    name, expected_profile=profile, expected_run_token="ABCDEF012345",
                )

    def test_startup_wait_is_bounded_and_never_runs_sql(self):
        name = "sqlperf_dgn004_2025_abcdef012345"
        with patch.object(container, "_docker", return_value="still starting"):
            with patch.object(container.time, "monotonic", side_effect=[1, 1, 2, 2, 3, 3, 4, 4]):
                with patch.object(container.time, "sleep"):
                    with self.assertRaises(container.ContainerError):
                        container.wait_until_sql_server_ready(name=name, deadline=4, startup_limit=3)

    def test_uncertain_container_start_proves_absence_or_removes_only_verified_owner(self):
        profile = container.BUILD_PROFILES[0]
        name = "sqlperf_dgn004_2022_abcdef012345"
        deadline = time.monotonic() + 10
        with patch.object(container, "_docker", return_value="") as docker:
            container._recover_uncertain_start(
                name=name, profile=profile, run_token="ABCDEF012345", deadline=deadline,
                settle_seconds=0,
            )
        self.assertEqual(docker.call_count, 2)
        self.assertIn("container ls", " ".join(docker.call_args.args[0]))

        with patch.object(container, "_docker", side_effect=[name, ""]):
            with patch.object(container, "_inspect_identity", return_value=("a" * 64, "created")) as inspect:
                with patch.object(container, "cleanup_owned_container") as cleanup:
                    container._recover_uncertain_start(
                        name=name, profile=profile, run_token="ABCDEF012345", deadline=deadline,
                        settle_seconds=0,
                    )
        inspect.assert_called_once_with(
            name, expected_profile=profile, expected_run_token="ABCDEF012345",
        )
        self.assertEqual(cleanup.call_args.kwargs["expected_id"], "a" * 64)

    def test_uncertain_container_start_fails_closed_when_reconciliation_fails(self):
        profile = container.BUILD_PROFILES[0]
        with patch.object(container, "verify_pinned_image"):
            with patch.object(container, "_password", return_value="A" * 32):
                with patch.object(container, "_docker", side_effect=container.ContainerError("timeout")):
                    with patch.object(container, "_recover_uncertain_start", side_effect=container.ContainerError("unknown")):
                        with self.assertRaises(container.UncertainContainerStartError) as raised:
                            container.start_owned_container(
                                profile, deadline=time.monotonic() + 10,
                                run_token="ABCDEF012345",
                            )
        self.assertFalse(raised.exception.cleanup_ok)

    def test_malformed_container_id_enters_recovery_before_reporting_failure(self):
        profile = container.BUILD_PROFILES[0]
        with patch.object(container, "verify_pinned_image"):
            with patch.object(container, "_password", return_value="A" * 32):
                with patch.object(container, "_docker", return_value="truncated-id"):
                    with patch.object(container, "_recover_uncertain_start") as recover:
                        with self.assertRaisesRegex(container.ContainerError, "complete container identity"):
                            container.start_owned_container(
                                profile, deadline=time.monotonic() + 10,
                                run_token="ABCDEF012345",
                            )
        self.assertEqual(recover.call_args.kwargs["settle_seconds"], container.START_RESPONSE_SETTLE_SECONDS)

    def test_startup_failure_with_acknowledged_container_reports_cleanup_unknown(self):
        profile = container.BUILD_PROFILES[0]
        container_id = "a" * 64
        with patch.object(container, "verify_pinned_image"):
            with patch.object(container, "_password", return_value="A" * 32):
                with patch.object(container, "_docker", return_value=container_id):
                    with patch.object(container, "_inspect_identity", return_value=(container_id, "running")):
                        with patch.object(container, "_resolve_sqlcmd", side_effect=container.ContainerError("exec failed")):
                            with patch.object(container, "_recover_uncertain_start", side_effect=container.ContainerError("cleanup unknown")) as recover:
                                with self.assertRaises(container.UncertainContainerStartError) as raised:
                                    container.start_owned_container(
                                        profile, deadline=time.monotonic() + 10,
                                        run_token="ABCDEF012345",
                                    )
        self.assertFalse(raised.exception.cleanup_ok)
        self.assertEqual(recover.call_args.kwargs["expected_id"], container_id)

    def test_recovery_refuses_to_remove_a_different_container_id(self):
        profile = container.BUILD_PROFILES[0]
        name = "sqlperf_dgn004_2022_abcdef012345"
        with patch.object(container, "_docker", return_value=name):
            with patch.object(container, "_inspect_identity", return_value=("b" * 64, "created")):
                with patch.object(container, "cleanup_owned_container") as cleanup:
                    with self.assertRaisesRegex(container.ContainerError, "ID differs"):
                        container._recover_uncertain_start(
                            name=name, profile=profile, run_token="ABCDEF012345",
                            expected_id="a" * 64, deadline=time.monotonic() + 10,
                            settle_seconds=0,
                        )
        cleanup.assert_not_called()

    def test_null_force_failure_count_is_retained_without_false_zero_claim(self):
        row = {
            "database_id": 7, "object_id": 10, "query_id": 11, "query_text_id": 12,
            "context_settings_id": 13, "parameterization_type": 0, "query_hash": "0102030405060708",
            "query_text_hex": "41004200", "count_compiles": 1,
            "last_compile_start_time": "2026-01-01T00:00:00", "engine_start_time": "2026-01-01T00:00:00",
        }
        meta = "DGN004_META|" + json.dumps([row]) + "|" + json.dumps([{
            "plan_id": 21, "is_forced_plan": False, "force_failure_count": None,
            "query_plan_hash": "1112131415161718",
        }]) + "|[]"
        decoded = runner._decode_meta(meta)
        self.assertIsNone(decoded.plan(21).force_failure_count)

    def test_identity_binding_allows_compile_counters_to_advance(self):
        query_text = runner.registered_text_views()["R"].statement_text.encode("utf-16le")
        first = runner.QueryIdentity(
            7, 10, 11, 12, 13, 0, bytes.fromhex("0102030405060708"),
            query_text, 1, "2026-01-01T00:00:00", "2026-01-01T00:00:00",
        )
        after_compile = runner.QueryIdentity(
            7, 10, 11, 12, 13, 0, first.query_hash, first.query_text_bytes,
            2, "2026-01-01T00:01:00", first.engine_start_time,
        )
        self.assertTrue(runner._identity_matches(
            after_compile, dbid=7, object_id=10, expected=first, role="R"
        ))

    def test_matrix_runs_each_authorized_build_after_clean_non_pass(self):
        evidence = runner.BuildEvidence(build="stub", acceptance_scope="CLASSICAL_FORCING_AND_HINT_CONTROL",
                                         calls=(), cleanup_ok=True)
        def not_proven(profile, *, deadline):
            return evidence, {"build": profile.name, "product_version": profile.product_version,
                              "verdict": runner.Verdict.NOT_PROVEN.value, "reasons": ["preflight"],
                              "calls_observed": 0, "sql_batches": 1, "query_store_flushes": 0,
                              "elapsed_seconds": 1.0, "cleanup_ok": True}
        with patch.object(runner, "run_build", side_effect=not_proven) as run_build:
            with contextlib.redirect_stdout(io.StringIO()):
                result = runner.main(["--build", "matrix"])
        self.assertEqual(result, 2)
        self.assertEqual(run_build.call_count, 2)

    def test_matrix_stops_after_cleanup_failure(self):
        evidence = runner.BuildEvidence(build="stub", acceptance_scope="CLASSICAL_FORCING_AND_HINT_CONTROL",
                                         calls=(), cleanup_ok=False)
        failure = {"build": "2022", "product_version": "16.0.4265.3",
                   "verdict": runner.Verdict.FAIL_CLEANUP.value, "reasons": ["cleanup"],
                   "calls_observed": 0, "sql_batches": 1, "query_store_flushes": 0,
                   "elapsed_seconds": 1.0, "cleanup_ok": False}
        with patch.object(runner, "run_build", return_value=(evidence, failure)) as run_build:
            with contextlib.redirect_stdout(io.StringIO()):
                result = runner.main(["--build", "matrix"])
        self.assertEqual(result, 1)
        self.assertEqual(run_build.call_count, 1)


if __name__ == "__main__":
    unittest.main()
