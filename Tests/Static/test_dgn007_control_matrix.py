from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
import unittest
from unittest.mock import call, patch

from Tests.Runtime import run_dgn007_control_matrix as matrix


CONTAINER_ID = "a" * 64
PROCESS = ((CONTAINER_ID, 4321),)


class DockerInventoryTests(unittest.TestCase):
    def test_uses_the_existing_runner_execution_target_module_identity(self):
        self.assertIs(matrix.execution_target, matrix.runner.execution_target)

    def test_resolved_target_passes_the_runner_session_type_guard(self):
        target = matrix.execution_target.docker_target(
            container="fake-container", sqlcmd_path="/opt/mssql-tools18/bin/sqlcmd")
        with patch.object(matrix.execution_target, "run_sql", return_value="1\n"):
            self.assertEqual(matrix.runner._active_sql_session_snapshot(target), 1)

    def test_resolves_only_supported_sqlcmd_paths_with_bounded_docker(self):
        target = object()
        with patch.object(matrix, "_docker", return_value="/opt/mssql-tools18/bin/sqlcmd\n") as docker, \
             patch.object(matrix.execution_target, "docker_target", return_value=target) as resolve:
            self.assertIs(matrix.resolve_target("sql-container"), target)
        self.assertEqual(docker.call_args.args[0][0:3], ["docker", "exec", "sql-container"])
        resolve.assert_called_once_with(
            container="sql-container", sqlcmd_path="/opt/mssql-tools18/bin/sqlcmd")

    def test_rejects_unexpected_sqlcmd_path(self):
        with patch.object(matrix, "_docker", return_value="/tmp/sqlcmd"), \
             patch.object(matrix.execution_target, "docker_target") as resolve:
            with self.assertRaisesRegex(matrix.CoordinatorRuntimeError, "FAIL_EXECUTION"):
                matrix.resolve_target("sql-container")
        resolve.assert_not_called()

    def test_requires_exactly_the_target_sql_server_process(self):
        with patch.object(matrix, "_docker", side_effect=(
                CONTAINER_ID, CONTAINER_ID + "\n",
                "UID PID PPID C STIME TTY TIME CMD\nmssql 4321 1 0 10:00 ? 00:01:00 /opt/mssql/bin/sqlservr\n"
                "root 800 1 0 10:00 ? 00:00:00 bash -c /opt/mssql/bin/sqlservr\n")) as docker:
            self.assertEqual(matrix.observe_sqlserver_processes("sql-container"), PROCESS)
        self.assertEqual(docker.call_args_list, [
            call(["docker", "inspect", "--format", "{{.Id}}", "sql-container"],
                 failure_code="FAIL_DOCKER_INSPECT"),
            call(["docker", "ps", "--no-trunc", "--quiet"],
                 failure_code="FAIL_DOCKER_INVENTORY"),
            call(["docker", "top", CONTAINER_ID],
                 failure_code="FAIL_DOCKER_INVENTORY"),
        ])

    def test_rejects_a_second_sql_server_container(self):
        second_id = "b" * 64
        with patch.object(matrix, "_docker", side_effect=(
                CONTAINER_ID, f"{CONTAINER_ID}\n{second_id}\n",
                "UID PID PPID C STIME TTY TIME CMD\nmssql 4321 1 0 10:00 ? 00:01:00 sqlservr\n",
                "UID PID PPID C STIME TTY TIME CMD\nmssql 9876 1 0 10:00 ? 00:01:00 sqlservr\n")):
            with self.assertRaisesRegex(matrix.CoordinatorRuntimeError,
                                         "FAIL_SQLSERVER_PROCESS_OUTSIDE_TARGET"):
                matrix.observe_sqlserver_processes("sql-container")

    def test_allows_multiple_server_processes_in_the_single_target_container(self):
        output = (
            "UID PID PPID C STIME TTY TIME CMD\n"
            "mssql 4321 1 0 10:00 ? 00:01:00 /opt/mssql/bin/sqlservr\n"
            "mssql 4322 4321 0 10:00 ? 00:00:01 sqlservr\n"
        )
        with patch.object(matrix, "_docker", side_effect=(
                CONTAINER_ID, CONTAINER_ID + "\n", output)):
            self.assertEqual(
                matrix.observe_sqlserver_processes("sql-container"),
                ((CONTAINER_ID, 4321), (CONTAINER_ID, 4322)))

    def test_requires_sqlservr_in_the_process_inventory(self):
        with patch.object(matrix, "_docker", side_effect=(
                CONTAINER_ID, f"{CONTAINER_ID}\n",
                "UID PID PPID C STIME TTY TIME CMD\nroot 8 1 0 10:00 ? 00:00:00 bash\n")):
            with self.assertRaisesRegex(matrix.CoordinatorRuntimeError,
                                         "FAIL_SQLSERVER_PROCESS_MISSING"):
                matrix.observe_sqlserver_processes("sql-container")

    def test_rejects_an_uninspectable_container(self):
        with patch.object(matrix, "_docker", side_effect=(
                CONTAINER_ID, f"{CONTAINER_ID}\n", matrix.CoordinatorRuntimeError("FAIL_DOCKER_INVENTORY"))):
            with self.assertRaisesRegex(matrix.CoordinatorRuntimeError, "FAIL_DOCKER_INVENTORY"):
                matrix.observe_sqlserver_processes("sql-container")

    def test_docker_command_failures_use_bounded_operation_codes(self):
        failure_codes = (
            "FAIL_DOCKER_INSPECT", "FAIL_DOCKER_INVENTORY",
            "FAIL_SQLCMD_RESOLUTION",
        )
        for code in failure_codes:
            with self.subTest(code=code), patch.object(matrix.subprocess, "run",
                    return_value=SimpleNamespace(returncode=1, stdout="", stderr="sensitive")):
                with self.assertRaises(matrix.CoordinatorRuntimeError) as raised:
                    matrix._docker(["docker", "synthetic"], failure_code=code)
                self.assertEqual(raised.exception.code, code)
                self.assertNotIn("sensitive", str(raised.exception))

    def test_rejects_invalid_or_oversized_inventory_before_inspection(self):
        with patch.object(matrix, "_docker", side_effect=("not-an-id",)):
            with self.assertRaises(matrix.CoordinatorRuntimeError):
                matrix.observe_sqlserver_processes("sql-container")
        with patch.object(matrix, "_docker", side_effect=(
                CONTAINER_ID, "\n".join(f"{value:064x}" for value in range(1, 10)))) as docker:
            with self.assertRaises(matrix.CoordinatorRuntimeError):
                matrix.observe_sqlserver_processes("sql-container")
            self.assertEqual(docker.call_count, 2)


class MatrixExecutionTests(unittest.TestCase):
    def setUp(self):
        self.target = object()
        self.receipts = tuple(SimpleNamespace(lifecycle_started_ns=1000 + index)
                              for index in range(6))
        self.contract = object()

    def _configure(self, inventory=None):
        stack = patch.multiple(
            matrix,
            resolve_target=unittest.mock.DEFAULT,
        )
        values = stack.start()
        self.addCleanup(stack.stop)
        values["resolve_target"].return_value = self.target
        engine_patch = patch.object(matrix.execution_target, "verify_engine")
        engine = engine_patch.start()
        self.addCleanup(engine_patch.stop)
        engine.return_value = 17
        inventory_mock = patch.object(matrix, "observe_sqlserver_processes",
                                       side_effect=inventory or [PROCESS] * 13)
        observer = inventory_mock.start()
        self.addCleanup(inventory_mock.stop)
        runner_patches = patch.multiple(
            matrix.runner,
            validate_manifest=unittest.mock.DEFAULT,
            assert_empty_instance=unittest.mock.DEFAULT,
            _run_capture_one=unittest.mock.DEFAULT,
        )
        runner_values = runner_patches.start()
        self.addCleanup(runner_patches.stop)
        runner_values["_run_capture_one"].side_effect = self.receipts
        return values, observer, runner_values

    @patch.dict("os.environ", {"SQLCMDPASSWORD": "synthetic"})
    def test_runs_six_captures_in_frozen_dec068_order_before_evaluation(self):
        same_container_processes = ((CONTAINER_ID, 4321), (CONTAINER_ID, 4322))
        _target_values, observer, runner_values = self._configure(
            [same_container_processes] * 13)
        with patch.object(matrix, "load_acceptance_contract", return_value=self.contract), \
             patch.object(matrix, "bind_sequence", return_value=tuple(
                 SimpleNamespace(record=index) for index in range(6))) as bind, \
             patch.object(matrix, "evaluate_version",
                          return_value=SimpleNamespace(outcome="PASS", code="OK")) as evaluate:
            decision = matrix.run_control_matrix("sql-container", 17)
        expected = tuple("DGN-007_CONTROL_" + label
                         for _block, _slot, label in matrix.EXPECTED_SEQUENCE)
        self.assertEqual(tuple(call.kwargs["contract"].scope
                               for call in runner_values["_run_capture_one"].call_args_list),
                         expected)
        self.assertEqual(tuple(call.args[1] for call in
                               runner_values["_run_capture_one"].call_args_list), (1, 2, 3, 4, 5, 6))
        self.assertTrue(all(call.kwargs["check_phase_diagnostics"]
                            for call in runner_values["_run_capture_one"].call_args_list))
        self.assertEqual(bind.call_args.kwargs["observations"], tuple(
            matrix.ReceiptObservation(1000 + index, 1) for index in range(6)))
        self.assertEqual(evaluate.call_args.args[2], tuple(range(6)))
        self.assertEqual(decision.code, "OK")
        self.assertEqual(observer.call_count, 13)
        self.assertEqual(runner_values["assert_empty_instance"].call_count, 7)

    @patch.dict("os.environ", {"SQLCMDPASSWORD": "synthetic"})
    def test_stops_after_host_sql_process_identity_changes(self):
        changed = (("b" * 64, 4322),)
        _target_values, observer, runner_values = self._configure(
            [PROCESS, PROCESS, changed])
        with patch.object(matrix, "load_acceptance_contract", return_value=self.contract), \
             patch.object(matrix, "bind_sequence") as bind:
            with self.assertRaisesRegex(matrix.CoordinatorRuntimeError,
                                         "FAIL_DOCKER_PROCESS_ID_CHANGED"):
                matrix.run_control_matrix("sql-container", 17)
        self.assertEqual(runner_values["_run_capture_one"].call_count, 1)
        bind.assert_not_called()
        self.assertEqual(observer.call_count, 3)


class CliSafetyTests(unittest.TestCase):
    def test_cli_reports_only_the_evaluated_preregistered_evidence_flags(self):
        for outcome, code, duration, plans, reads, expected in (
            ("PASS", "OK", True, False, True, "YES; plan_sets_differ=NO; reads_profile_separates=YES"),
            ("SKIP", "SKIP_EVIDENCE_MISSING", False, True, False, "NO; plan_sets_differ=YES; reads_profile_separates=NO"),
        ):
            with self.subTest(outcome=outcome):
                output = StringIO()
                decision = SimpleNamespace(
                    outcome=outcome, code=code, directed_symptom=duration, plan_evidence=plans,
                    profile_evidence=reads, duration_contrasts=("synthetic raw metrics",),
                )
                with redirect_stdout(output), patch.object(matrix, "run_control_matrix", return_value=decision):
                    result = matrix.main(["--container", "sql-container", "--expected-major", "17",
                                          "--confirm-disposable-instance", "--confirm-isolated-lab"])
                self.assertEqual(result, 0)
                self.assertIn(f"decision={outcome}; decision_code={code}; duration_symptom={expected}", output.getvalue())
                self.assertNotIn("synthetic raw metrics", output.getvalue())

    def test_cli_requires_both_isolation_confirmations(self):
        output = StringIO()
        with redirect_stdout(output), patch.object(matrix, "run_control_matrix") as run:
            result = matrix.main(["--container", "sql-container", "--expected-major", "17",
                                  "--confirm-disposable-instance"])
        self.assertEqual(result, 1)
        run.assert_not_called()
        self.assertIn("DGN007_COORDINATOR|FAIL|FAIL_SAFETY", output.getvalue())
        self.assertIn(
            "duration_symptom=NOT_EVALUATED; plan_sets_differ=NOT_EVALUATED; reads_profile_separates=NOT_EVALUATED",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
