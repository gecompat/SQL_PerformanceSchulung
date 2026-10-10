#!/usr/bin/env python3
"""Fokussierte Runner-Fehlerpfade ohne SQL Server oder Drittbibliotheken."""
from __future__ import annotations

from contextlib import closing, redirect_stderr, redirect_stdout
from dataclasses import FrozenInstanceError, replace
import io
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests" / "Runtime"))
import run_dgn007_automated_setup as runner  # noqa: E402


def harness_result(*, contract=runner.DATA_MODEL_CONTRACT, phases=None, summary="PASS|OK", returncode=0, timed_out=False):
    if phases is None:
        phases = [(phase, "PASS", "OK") for phase in contract.expected_phases]
    lines = [f"SQLPERF_SUMMARY|{summary}"]
    lines.extend(f"{phase}: {outcome}/{code} (0.001s) - Synthetisches Ergebnis."
                 for phase, outcome, code in phases)
    return runner.SqlcmdResult((), returncode, "\n".join(lines), "", timed_out, 0.001)


def target():
    return runner.execution_target.docker_target(container="synthetic-test", sqlcmd_path="/opt/mssql-tools18/bin/sqlcmd")


class HarnessContractTests(unittest.TestCase):
    def test_complete_pass_only(self):
        runner.check_harness(harness_result())

    def test_skip_warn_and_unrecognised_success_code_fail(self):
        for outcome, code in (("SKIP", "SKIP_PERMISSION"), ("WARN", "WARN_EMPIRICAL_VARIANCE"), ("PASS", "OTHER")):
            with self.subTest(outcome=outcome, code=code):
                phases = [(phase, "PASS", "OK") for phase in runner.EXPECTED_PHASES]
                phases[2] = ("DATA_ASSERTION", outcome, code)
                with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                    runner.check_harness(harness_result(phases=phases, summary=f"{outcome}|{code}"))

    def test_missing_duplicate_reordered_phase_or_summary_fail(self):
        phases = [(phase, "PASS", "OK") for phase in runner.EXPECTED_PHASES]
        for invalid in (phases[:2] + phases[3:], phases + phases[-1:], phases[::-1]):
            with self.subTest(phases=invalid), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                runner.check_harness(harness_result(phases=invalid))
        result = harness_result()
        for output in (result.stdout.replace("SQLPERF_SUMMARY|PASS|OK", ""),
                       result.stdout + "\nSQLPERF_SUMMARY|PASS|OK",
                       result.stdout + "\nSQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE"):
            with self.subTest(output=output), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                runner.check_harness(replace(result, stdout=output))

    def test_timeout_and_nonzero_exit_fail(self):
        for result, code in ((harness_result(timed_out=True), "FAIL_TIMEOUT"),
                             (harness_result(summary="FAIL|FAIL_TIMEOUT", returncode=3), "FAIL_TIMEOUT"),
                             (harness_result(returncode=1), "FAIL_EXECUTION")):
            with self.subTest(code=code), self.assertRaisesRegex(runner.RunnerFailure, code):
                runner.check_harness(result)

    def test_cleanup_failure_dominates_prior_timeout(self):
        result = harness_result(
            phases=[("PREFLIGHT", "PASS", "OK"), ("SETUP", "FAIL", "FAIL_TIMEOUT"),
                    ("CLEANUP", "FAIL", "FAIL_CLEANUP")],
            summary="FAIL|FAIL_TIMEOUT", returncode=3,
        )
        with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CLEANUP"):
            runner.check_harness(result)

    def test_manifest_is_existing_bounded_data_model(self):
        runner.validate_manifest()
        manifest = runner.load_manifest(runner.MANIFEST)
        for invalid in (replace(manifest, run_token="LOCAL"),
                        replace(manifest, timeout_seconds=181),
                        replace(manifest, phases=manifest.phases[:2]),
                        replace(manifest, cleanup=None)):
            with self.subTest(manifest=invalid), patch.object(runner, "load_manifest", return_value=invalid):
                with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                    runner.validate_manifest()


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.redirect = redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def test_absence_is_checked_after_success_and_each_failure(self):
        failures = (None, runner.RunnerFailure("FAIL_CONTRACT"),
                    subprocess.TimeoutExpired("synthetic", 260, output="synthetic-raw-output"),
                    OSError("synthetic-raw-output"), KeyboardInterrupt())
        for failure in failures:
            with self.subTest(failure=type(failure).__name__), \
                 patch.object(runner, "run_harness", return_value=harness_result(), side_effect=failure), \
                 patch.object(runner, "assert_absent") as absent, \
                 patch.object(runner, "recover") as recovery:
                if failure is None:
                    self.assertEqual(runner.run_one(target(), 1).outcome, "PASS")
                else:
                    with self.assertRaises(runner.RunnerFailure):
                        runner.run_one(target(), 1)
                absent.assert_called_once()
                recovery.assert_not_called()
        self.assertNotIn("synthetic-raw-output", self.output.getvalue())

    def test_cleanup_failure_dominates_and_recovery_does_not_grant_pass(self):
        with patch.object(runner, "run_harness", side_effect=runner.RunnerFailure("FAIL_TIMEOUT")), \
             patch.object(runner, "assert_absent", side_effect=[runner.RunnerFailure("FAIL_CLEANUP"), None]) as absent, \
             patch.object(runner, "recover") as recovery:
            with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CLEANUP"):
                runner.run_one(target(), 1)
            recovery.assert_called_once()
            self.assertEqual(absent.call_count, 2)
        self.assertIn("DGN007_CLEANUP|RUN_1|FAIL|FAIL_CLEANUP", self.output.getvalue())

    def test_failed_recovery_still_runs_final_absence_check(self):
        with patch.object(runner, "run_harness", return_value=harness_result()), \
             patch.object(runner, "assert_absent", side_effect=runner.RunnerFailure("FAIL_CLEANUP")) as absent, \
             patch.object(runner, "recover", side_effect=subprocess.TimeoutExpired("synthetic", 60)) as recovery:
            with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CLEANUP"):
                runner.run_one(target(), 1)
            recovery.assert_called_once()
            self.assertEqual(absent.call_count, 2)

    def test_harness_reported_cleanup_failure_remains_failure_when_absent(self):
        result = harness_result(phases=[("CLEANUP", "FAIL", "FAIL_CLEANUP")], summary="FAIL|FAIL_CLEANUP", returncode=4)
        with patch.object(runner, "run_harness", return_value=result), \
             patch.object(runner, "assert_absent") as absent, patch.object(runner, "recover") as recovery:
            with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CLEANUP"):
                runner.run_one(target(), 1)
            absent.assert_called_once()
            recovery.assert_not_called()

    def test_absence_requires_exact_sentinel_and_bounded_read_only_query(self):
        for invalid in ("", "NOT_ABSENT", "ABSENT\nsynthetic-extra"):
            with patch.object(runner.execution_target, "run_sql", return_value=invalid), \
                 self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CLEANUP"):
                runner.assert_absent(target())
        with patch.object(runner.execution_target, "run_sql", return_value="ABSENT\n") as run_sql:
            runner.assert_absent(target())
            self.assertEqual(run_sql.call_args.kwargs["timeout_seconds"], 30)
            self.assertIn(runner.DATABASE, run_sql.call_args.kwargs["sql_text"])
            self.assertNotIn("DROP", run_sql.call_args.kwargs["sql_text"])

    def test_recovery_uses_only_marker_checked_auto_batch_and_env_password(self):
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
             patch.object(runner, "run_sqlcmd", return_value=harness_result(phases=[])) as process:
            runner.recover(target())
            command = process.call_args.args[0]
            self.assertIn(str(runner.AUTOMATED / "90_Cleanup.sql"), command)
            self.assertIn("RunToken=AUTO", command)
            self.assertIn(f"TargetDatabase={runner.DATABASE}", command)
            self.assertIn("ConfirmIsolatedLab=1", command)
            self.assertIn("HighImpactConfirmed=1", command)
            self.assertNotIn("-P", command)
            self.assertNotIn("synthetic-test-value", command)
            self.assertEqual(process.call_args.kwargs["timeout_seconds"], 60)
        for result in (harness_result(phases=[], summary="WARN|WARN_EMPIRICAL_VARIANCE"),
                       harness_result(phases=[], timed_out=True), harness_result(phases=[], returncode=1)):
            with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
                 patch.object(runner, "run_sqlcmd", return_value=result), \
                 self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CLEANUP"):
                runner.recover(target())


class CliTests(unittest.TestCase):
    BASE = ["--container", "synthetic-test", "--expected-major", "17"]
    CONFIRMED = BASE + ["--confirm-disposable-instance"]

    def test_explicit_container_supported_major_and_docker_only(self):
        invalid = (["--expected-major", "17"], ["--container", "synthetic-test"],
                   self.BASE + ["--target", "host"],
                   ["--container", "synthetic-test", "--expected-major", "14"],
                   self.CONFIRMED + ["--repeats", "1"])
        for arguments in invalid:
            with self.subTest(arguments=arguments), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                runner.main(arguments)
            self.assertEqual(exc.exception.code, 2)

    def test_disposable_confirmation_is_required_before_any_connection(self):
        for arguments in (self.BASE, self.BASE + ["--confirm-isolated-lab"]):
            with self.subTest(arguments=arguments), \
                 patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value",
                                         "SQLPERF_HOST_DISPOSABLE_INSTANCE": "1"}), \
                 patch.object(runner, "resolve_target") as resolve, redirect_stdout(io.StringIO()) as output:
                self.assertEqual(runner.main(arguments), 1)
                resolve.assert_not_called()
                self.assertIn("FAIL|FAIL_SAFETY", output.getvalue())

    def test_missing_password_fails_before_connection(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(runner, "resolve_target") as resolve, redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(self.CONFIRMED), 1)
            resolve.assert_not_called()

    def test_version_mismatch_or_foreign_database_prevents_manifest_execution(self):
        for stage in ("engine", "empty"):
            with self.subTest(stage=stage), patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
                 patch.object(runner, "resolve_target", return_value=target()), \
                 patch.object(runner.execution_target, "verify_engine", side_effect=runner.ExecutionTargetError("synthetic-raw-output") if stage == "engine" else None) as engine, \
                 patch.object(runner, "assert_empty_instance", side_effect=runner.RunnerFailure("FAIL_SAFETY") if stage == "empty" else None), \
                 patch.object(runner, "run_one") as run_one, redirect_stdout(io.StringIO()) as output:
                self.assertEqual(runner.main(self.CONFIRMED), 1)
                run_one.assert_not_called()
                self.assertEqual(engine.call_args.kwargs["expected_major"], 17)
                self.assertNotIn("synthetic-raw-output", output.getvalue())

    def test_developer_edition_ids_and_fail_closed_null_guard(self):
        with patch.object(runner.execution_target, "run_sql", return_value="EMPTY_DEVELOPER\n") as run_sql:
            runner.assert_empty_instance(target())
        sql = run_sql.call_args.kwargs["sql_text"]
        self.assertIn("TRY_CONVERT(int,SERVERPROPERTY('EditionID'))", sql)
        self.assertNotIn("SERVERPROPERTY('Edition')", sql)
        self.assertIn("database_id>4", sql)
        self.assertEqual(run_sql.call_args.kwargs["timeout_seconds"], 30)
        # Die unveränderte skalare SQL-Bedingung mit SQL-NULL-Semantik prüfen;
        # hierfür genügt SQLite aus der Standardbibliothek ohne SQL Server.
        match = re.search(r"IF (@EditionId .*?) THROW", sql)
        self.assertIsNotNone(match)
        with closing(sqlite3.connect(":memory:")) as connection:
            for edition_id, rejected in ((-2117995310, 0), (-1785266663, 0),
                                         (1804890536, 1), (-1534726760, 1),
                                         (-1592396055, 1), (0, 1), (None, 1)):
                with self.subTest(edition_id=edition_id):
                    result = connection.execute(
                        f"SELECT CASE WHEN {match.group(1)} THEN 1 ELSE 0 END",
                        {"EditionId": edition_id},
                    ).fetchone()[0]
                    self.assertEqual(result, rejected)

    def test_two_complete_runs_and_scope_summary(self):
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
             patch.object(runner, "resolve_target", return_value=target()), \
             patch.object(runner.execution_target, "verify_engine", return_value=17), \
             patch.object(runner, "assert_empty_instance"), \
             patch.object(runner, "run_harness", return_value=harness_result()) as harness, \
             patch.object(runner, "assert_absent") as absent, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(runner.main(self.CONFIRMED), 0)
            self.assertEqual(harness.call_count, 2)
            self.assertEqual(absent.call_count, 2)
            self.assertIn("DGN007_SUMMARY|PASS|OK|major=17; runs=2; target=docker; scope=DGN-007_DATA_MODEL", output.getvalue())

    def test_harness_process_budget_environment_and_no_raw_output_option(self):
        with patch.object(runner, "run_sqlcmd", return_value=harness_result()) as process:
            runner.run_harness(target())
            self.assertEqual(process.call_args.kwargs["timeout_seconds"], 260)
            self.assertNotIn("--show-output", process.call_args.args[0])
            self.assertIn("--confirm-isolated-lab", process.call_args.args[0])
            self.assertEqual(process.call_args.kwargs["environment"]["SQLPERF_SQL_CONTAINER"], "synthetic-test")


class QueryStoreWindowTests(unittest.TestCase):
    CONTRACT = runner.QUERY_STORE_WINDOWS_CONTRACT
    ARGUMENTS = CliTests.CONFIRMED + ["--scope", "query-store-windows"]

    def test_scopes_are_immutable_and_unknown_scope_is_rejected_before_connection(self):
        self.assertIs(runner.scope_contract("data-model"), runner.DATA_MODEL_CONTRACT)
        self.assertIs(runner.scope_contract("query-store-windows"), self.CONTRACT)
        with self.assertRaises(FrozenInstanceError):
            self.CONTRACT.scope = "DGN-007_DATA_MODEL"
        with self.assertRaises(ValueError):
            runner.scope_contract("unknown")
        with patch.object(runner, "resolve_target") as resolve, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
            runner.main(CliTests.CONFIRMED + ["--scope", "unknown"])
        self.assertEqual(exc.exception.code, 2)
        resolve.assert_not_called()

    def test_window_manifest_is_exact_and_rejects_phase_budget_script_or_database_drift(self):
        runner.validate_manifest(contract=self.CONTRACT)
        manifest = runner.load_manifest(self.CONTRACT.manifest)
        self.assertEqual(self.CONTRACT.expected_phases,
                         ("PREFLIGHT", "SETUP", "DATA_ASSERTION", "QUERY_STORE_WINDOWS", "CLEANUP"))
        window = manifest.phases[3]
        invalid_manifests = [
            replace(manifest, timeout_seconds=181),
            replace(manifest, cleanup_timeout_seconds=61),
            replace(manifest, phases=manifest.phases[:3]),
            replace(manifest, phases=manifest.phases + (window,)),
            replace(manifest, cleanup=None),
        ]
        for invalid_window in (
            replace(window, timeout_seconds=149),
            replace(window, path=runner.AUTOMATED / "40_Data_Assertion.sql"),
            replace(window, database_selector="master"),
            replace(window, required=False),
            replace(window, require_summary=False),
        ):
            invalid_manifests.append(replace(manifest, phases=manifest.phases[:3] + (invalid_window,)))
        for invalid in invalid_manifests:
            with self.subTest(manifest=invalid), patch.object(runner, "load_manifest", return_value=invalid):
                with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                    runner.validate_manifest(contract=self.CONTRACT)

    def test_window_requires_all_five_phases_once_in_order(self):
        runner.check_harness(harness_result(contract=self.CONTRACT), contract=self.CONTRACT)
        phases = [(phase, "PASS", "OK") for phase in self.CONTRACT.expected_phases]
        for invalid in (phases[:3] + phases[4:], phases[:4] + phases[3:], phases[::-1]):
            with self.subTest(phases=invalid), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                runner.check_harness(harness_result(phases=invalid), contract=self.CONTRACT)
        with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
            runner.check_harness(harness_result(), contract=self.CONTRACT)
        with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
            runner.check_harness(harness_result(contract=self.CONTRACT))

    def test_window_warning_skip_missing_or_duplicate_summary_never_pass(self):
        for outcome, code in (("WARN", "WARN_EMPIRICAL_VARIANCE"), ("SKIP", "SKIP_EVIDENCE_MISSING")):
            phases = [(phase, "PASS", "OK") for phase in self.CONTRACT.expected_phases]
            phases[3] = ("QUERY_STORE_WINDOWS", outcome, code)
            for summary in ("PASS|OK", f"{outcome}|{code}"):
                with self.subTest(summary=summary), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                    runner.check_harness(harness_result(phases=phases, summary=summary), contract=self.CONTRACT)
        result = harness_result(contract=self.CONTRACT)
        for output in (result.stdout.replace("SQLPERF_SUMMARY|PASS|OK", ""),
                       result.stdout + "\nSQLPERF_SUMMARY|PASS|OK"):
            with self.subTest(output=output), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                runner.check_harness(replace(result, stdout=output), contract=self.CONTRACT)

    def test_actual_scope_dispatch_runs_each_manifest_twice_without_changing_the_default(self):
        original_defaults = (runner.MANIFEST, runner.SCOPE, runner.EXPECTED_PHASES)

        def result_for_command(command, **kwargs):
            self.assertEqual(kwargs["timeout_seconds"], 260)
            contract = self.CONTRACT if command[2] == str(self.CONTRACT.manifest) else runner.DATA_MODEL_CONTRACT
            self.assertEqual(command[2], str(contract.manifest))
            self.assertNotIn("--show-output", command)
            return harness_result(contract=contract)

        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
             patch.object(runner, "resolve_target", return_value=target()), \
             patch.object(runner.execution_target, "verify_engine", return_value=17), \
             patch.object(runner, "assert_empty_instance") as empty, \
             patch.object(runner, "run_sqlcmd", side_effect=result_for_command) as process, \
             patch.object(runner, "assert_absent") as absent, redirect_stdout(io.StringIO()) as output:
            for arguments in (CliTests.CONFIRMED, self.ARGUMENTS, CliTests.CONFIRMED):
                self.assertEqual(runner.main(arguments), 0)
            self.assertEqual([call.args[0][2] for call in process.call_args_list],
                             [str(runner.MANIFEST)] * 2 + [str(self.CONTRACT.manifest)] * 2 + [str(runner.MANIFEST)] * 2)
            self.assertEqual(absent.call_count, 6)
            self.assertEqual(empty.call_count, 3)
            self.assertEqual(output.getvalue().count("scope=DGN-007_QUERY_STORE_WINDOWS"), 1)
            self.assertEqual(output.getvalue().count("scope=DGN-007_DATA_MODEL"), 2)
        self.assertEqual((runner.MANIFEST, runner.SCOPE, runner.EXPECTED_PHASES), original_defaults)

    def test_window_failure_preserves_cleanup_priority_and_scope(self):
        result = harness_result(contract=self.CONTRACT, phases=[
            ("QUERY_STORE_WINDOWS", "FAIL", "FAIL_TIMEOUT"), ("CLEANUP", "FAIL", "FAIL_CLEANUP")
        ], summary="FAIL|FAIL_TIMEOUT", returncode=3)
        with patch.object(runner, "run_harness", return_value=result) as harness, \
             patch.object(runner, "assert_absent") as absent, redirect_stdout(io.StringIO()) as output:
            with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CLEANUP"):
                runner.run_one(target(), 1, contract=self.CONTRACT)
            harness.assert_called_once_with(target(), contract=self.CONTRACT)
            absent.assert_called_once()
            self.assertIn("DGN007_STAGE|DGN-007_QUERY_STORE_WINDOWS|RUN_1|FAIL|FAIL_CLEANUP", output.getvalue())

    def test_internal_window_deadline_is_timeout_even_when_the_process_exits_normally(self):
        phases = [(phase, "PASS", "OK") for phase in self.CONTRACT.expected_phases]
        phases[3] = ("QUERY_STORE_WINDOWS", "FAIL", "FAIL_TIMEOUT")
        for returncode in (0, 3):
            with self.subTest(returncode=returncode), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_TIMEOUT"):
                runner.check_harness(harness_result(phases=phases, summary="FAIL|FAIL_TIMEOUT", returncode=returncode),
                                     contract=self.CONTRACT)


class ProfileComparisonRunnerTests(unittest.TestCase):
    CONTRACT = runner.PROFILE_COMPARISON_CONTRACT

    def test_profile_manifest_is_immutable_exact_and_bounded(self):
        self.assertIs(runner.scope_contract("profile-comparison"), self.CONTRACT)
        with self.assertRaises(FrozenInstanceError):
            self.CONTRACT.scope = "OTHER"
        runner.validate_manifest(contract=self.CONTRACT)
        self.assertEqual(self.CONTRACT.expected_phases,
                         ("PREFLIGHT", "SETUP", "DATA_ASSERTION", "QUERY_STORE_WINDOWS", "PROFILE_COMPARISON", "CLEANUP"))
        manifest = runner.load_manifest(self.CONTRACT.manifest)
        profile = manifest.phases[-1]
        invalid = [replace(manifest, timeout_seconds=181), replace(manifest, cleanup_timeout_seconds=61),
                   replace(manifest, phases=manifest.phases[:-1]), replace(manifest, phases=manifest.phases + (profile,))]
        for phase in (replace(profile, timeout_seconds=11), replace(profile, database_selector="master"),
                      replace(profile, path=runner.AUTOMATED / "20_Query_Store_Windows.sql"),
                      replace(profile, required=False), replace(profile, require_summary=False)):
            invalid.append(replace(manifest, phases=manifest.phases[:-1] + (phase,)))
        for changed in invalid:
            with self.subTest(manifest=changed), patch.object(runner, "load_manifest", return_value=changed), \
                 self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                runner.validate_manifest(contract=self.CONTRACT)

    def test_profile_requires_six_ordered_pass_phases_and_one_summary(self):
        runner.check_harness(harness_result(contract=self.CONTRACT), contract=self.CONTRACT)
        phases = [(phase, "PASS", "OK") for phase in self.CONTRACT.expected_phases]
        invalid = [phases[:-2] + phases[-1:], phases + phases[-2:-1], phases[::-1]]
        for outcome, code in (("WARN", "WARN_EMPIRICAL_VARIANCE"), ("SKIP", "SKIP_EVIDENCE_MISSING")):
            changed = phases.copy()
            changed[-2] = ("PROFILE_COMPARISON", outcome, code)
            invalid.append(changed)
        for changed in invalid:
            with self.subTest(phases=changed), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                runner.check_harness(harness_result(phases=changed), contract=self.CONTRACT)
        result = harness_result(contract=self.CONTRACT)
        with self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
            runner.check_harness(replace(result, stdout=result.stdout + "\nSQLPERF_SUMMARY|PASS|OK"), contract=self.CONTRACT)

    def test_profile_actual_dispatch_twice_hides_report_and_preserves_default(self):
        raw = "SYNTHETIC_PROFILE_RAW_METRIC"
        result = harness_result(contract=self.CONTRACT)
        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
             patch.object(runner, "resolve_target", return_value=target()), \
             patch.object(runner.execution_target, "verify_engine", return_value=17), \
             patch.object(runner, "assert_empty_instance"), \
             patch.object(runner, "run_sqlcmd", return_value=replace(result, stdout=result.stdout + "\n" + raw)) as process, \
             patch.object(runner, "assert_absent") as absent, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(runner.main(CliTests.CONFIRMED + ["--scope", "profile-comparison"]), 0)
            self.assertEqual(process.call_count, 2)
            self.assertEqual(absent.call_count, 2)
            for call in process.call_args_list:
                self.assertEqual(call.args[0][2], str(self.CONTRACT.manifest))
                self.assertNotIn("--show-output", call.args[0])
                self.assertEqual(call.kwargs["timeout_seconds"], 260)
            self.assertNotIn(raw, output.getvalue())
            self.assertIn("scope=DGN-007_PROFILE_COMPARISON", output.getvalue())
        self.assertEqual(runner.build_parser().parse_args(CliTests.BASE).scope, "data-model")

    def test_profile_timeout_and_cleanup_priority_remain_independent(self):
        for cleanup, expected in (("PASS", "FAIL_TIMEOUT"), ("FAIL", "FAIL_CLEANUP")):
            phases = [(phase, "PASS", "OK") for phase in self.CONTRACT.expected_phases]
            phases[-2] = ("PROFILE_COMPARISON", "FAIL", "FAIL_TIMEOUT")
            phases[-1] = ("CLEANUP", cleanup, "OK" if cleanup == "PASS" else "FAIL_CLEANUP")
            result = harness_result(phases=phases, summary="FAIL|FAIL_TIMEOUT")
            with self.subTest(cleanup=cleanup), patch.object(runner, "run_harness", return_value=result), \
                 patch.object(runner, "assert_absent") as absent, redirect_stdout(io.StringIO()), \
                 self.assertRaisesRegex(runner.RunnerFailure, expected):
                runner.run_one(target(), 1, contract=self.CONTRACT)
            absent.assert_called_once()


class ControlCaptureRunnerTests(unittest.TestCase):
    CONTRACTS = (runner.CONTROL_AB_CONTRACT, runner.CONTROL_BA_CONTRACT, runner.CONTROL_AA_CONTRACT)

    def test_all_control_contracts_are_immutable_and_have_exact_eight_phases(self):
        for order, contract in zip(("AB", "BA", "AA"), self.CONTRACTS):
            with self.subTest(order=order):
                self.assertIs(runner.scope_contract("control-" + order.lower()), contract)
                self.assertEqual(contract.scope, "DGN-007_CONTROL_" + order)
                self.assertEqual(contract.expected_phases,
                                 ("PREFLIGHT", "SETUP", "DATA_ASSERTION", "CONTROL_CONFIG", "CONTROL_WINDOWS",
                                  "PROFILE_COMPARISON", "CONTROL_EVIDENCE", "CLEANUP"))
                with self.assertRaises(FrozenInstanceError):
                    contract.scope = "OTHER"
                runner.validate_manifest(contract=contract)

    def test_each_control_manifest_rejects_budget_sequence_and_script_drift(self):
        for contract in self.CONTRACTS:
            manifest = runner.load_manifest(contract.manifest)
            invalid = [replace(manifest, timeout_seconds=181), replace(manifest, cleanup_timeout_seconds=61),
                       replace(manifest, phases=manifest.phases[:-1]), replace(manifest, phases=manifest.phases[::-1]),
                       replace(manifest, phases=manifest.phases + (manifest.phases[-1],)), replace(manifest, cleanup=None)]
            for index in (3, 4, 6):
                phase = manifest.phases[index]
                for changed in (replace(phase, timeout_seconds=phase.timeout_seconds + 1),
                                replace(phase, database_selector="master"), replace(phase, required=False),
                                replace(phase, path=runner.AUTOMATED / "20_Query_Store_Windows.sql")):
                    phases = list(manifest.phases)
                    phases[index] = changed
                    invalid.append(replace(manifest, phases=tuple(phases)))
            for changed in invalid:
                with self.subTest(scope=contract.scope), patch.object(runner, "load_manifest", return_value=changed), \
                     self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                    runner.validate_manifest(contract=contract)

    def test_control_harness_rejects_missing_duplicate_skip_warn_or_foreign_scope(self):
        for contract in self.CONTRACTS:
            runner.check_harness(harness_result(contract=contract), contract=contract)
            phases = [(phase, "PASS", "OK") for phase in contract.expected_phases]
            invalid = [phases[:6] + phases[7:], phases + phases[-2:-1], phases[::-1]]
            for outcome, code in (("SKIP", "SKIP_EVIDENCE_MISSING"), ("WARN", "WARN_EMPIRICAL_VARIANCE")):
                changed = phases.copy()
                changed[6] = ("CONTROL_EVIDENCE", outcome, code)
                invalid.append(changed)
            invalid.append([(phase, "PASS", "OK") for phase in runner.PROFILE_COMPARISON_CONTRACT.expected_phases])
            for changed in invalid:
                with self.subTest(scope=contract.scope), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
                    runner.check_harness(harness_result(phases=changed), contract=contract)

    def test_all_controls_dispatch_twice_and_hide_scalar_reports(self):
        contracts = {str(contract.manifest): contract for contract in self.CONTRACTS}

        def synthetic_result(command, **kwargs):
            contract = contracts[command[2]]
            self.assertNotIn("--show-output", command)
            self.assertEqual(kwargs["timeout_seconds"], 260)
            result = harness_result(contract=contract)
            return replace(result, stdout=result.stdout + "\nSYNTHETIC_CONTROL_PLAN_HASH_REPORT")

        with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
             patch.object(runner, "resolve_target", return_value=target()), \
             patch.object(runner.execution_target, "verify_engine", return_value=17), \
             patch.object(runner, "assert_empty_instance"), \
             patch.object(runner, "run_sqlcmd", side_effect=synthetic_result) as process, \
             patch.object(runner, "assert_absent") as absent, redirect_stdout(io.StringIO()) as output:
            for order in ("ab", "ba", "aa"):
                self.assertEqual(runner.main(CliTests.CONFIRMED + ["--scope", "control-" + order]), 0)
            self.assertEqual([call.args[0][2] for call in process.call_args_list],
                             [str(contract.manifest) for contract in self.CONTRACTS for _ in (1, 2)])
            self.assertEqual(absent.call_count, 6)
            self.assertNotIn("SYNTHETIC_CONTROL_PLAN_HASH_REPORT", output.getvalue())
        self.assertEqual(runner.build_parser().parse_args(CliTests.BASE).scope, "data-model")

    def test_control_timeout_skip_and_cleanup_failure_keep_cleanup_priority(self):
        for contract in self.CONTRACTS:
            for outcome, code in (("FAIL", "FAIL_TIMEOUT"), ("SKIP", "SKIP_EVIDENCE_MISSING")):
                result = harness_result(phases=[("CONTROL_WINDOWS", outcome, code), ("CLEANUP", "FAIL", "FAIL_CLEANUP")],
                                        summary=f"{outcome}|{code}")
                with self.subTest(scope=contract.scope, code=code), \
                     patch.object(runner, "run_harness", return_value=result), patch.object(runner, "assert_absent") as absent, \
                     redirect_stdout(io.StringIO()), self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CLEANUP"):
                    runner.run_one(target(), 1, contract=contract)
                absent.assert_called_once()

    def test_control_confirmation_is_required_before_target_resolution(self):
        for order in ("ab", "ba", "aa"):
            with self.subTest(order=order), patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
                 patch.object(runner, "resolve_target") as resolve, redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(CliTests.BASE + ["--scope", "control-" + order]), 1)
                resolve.assert_not_called()


class PhaseDiagnosticsTests(unittest.TestCase):
    SCOPES = ("data-model", "query-store-windows", "profile-comparison",
              "control-ab", "control-ba", "control-aa")

    def test_private_bounded_command_for_all_six_scopes_and_combined_flags(self):
        for contract in runner.KNOWN_CONTRACTS:
            with self.subTest(scope=contract.scope), \
                 patch.object(runner, "start_sqlcmd") as start, \
                 patch.object(runner, "collect_capture_process", return_value=harness_result(contract=contract)) as collect, \
                 patch.object(runner, "run_sqlcmd") as unbounded:
                runner.run_harness(target(), contract=contract, check_phase_diagnostics=True)
                command = start.call_args.args[0]
                self.assertEqual(command[:2], [sys.executable, "-u"])
                self.assertEqual(command.count("--show-output"), 1)
                self.assertEqual(start.call_args.kwargs["environment"]["PYTHONUNBUFFERED"], "1")
                self.assertEqual(collect.call_args.kwargs, {"contract": contract})
                self.assertNotIn("-P", command)
                unbounded.assert_not_called()
        with patch.object(runner, "start_sqlcmd") as start, \
             patch.object(runner, "collect_capture_process"):
            runner.run_harness(target(), contract=runner.CONTROL_AB_CONTRACT,
                               check_phase_diagnostics=True, check_capture_projection=True)
            self.assertEqual(start.call_args.args[0].count("--show-output"), 1)
        foreign = replace(runner.DATA_MODEL_CONTRACT, scope="DGN-007_UNKNOWN")
        with patch.object(runner, "start_sqlcmd") as start, self.assertRaisesRegex(runner.RunnerFailure, "FAIL_CONTRACT"):
            runner.run_harness(target(), contract=foreign, check_phase_diagnostics=True)
        start.assert_not_called()

    def test_cli_dispatches_two_runs_without_capture_abnahme_or_success_diagnostics(self):
        for scope, contract in zip(self.SCOPES, runner.KNOWN_CONTRACTS):
            result = harness_result(contract=contract)
            result = replace(result, stderr="[SETUP:stderr] synthetic-private-error-text")
            with self.subTest(scope=scope), patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
                 patch.object(runner, "resolve_target", return_value=target()), \
                 patch.object(runner.execution_target, "verify_engine", return_value=17), \
                 patch.object(runner, "assert_empty_instance"), \
                 patch.object(runner, "run_harness", return_value=result) as process, \
                 patch.object(runner, "assert_absent") as absent, \
                 patch.object(runner, "decode_projection") as decode, redirect_stdout(io.StringIO()) as output:
                self.assertEqual(runner.main(CliTests.CONFIRMED + ["--scope", scope, "--check-phase-diagnostics"]), 0)
                self.assertEqual(process.call_count, 2)
                self.assertEqual(absent.call_count, 2)
                self.assertTrue(all(call.kwargs == {"contract": contract, "check_phase_diagnostics": True}
                                    for call in process.call_args_list))
                decode.assert_not_called()
                for forbidden in ("DGN007_CAPTURE|", "DGN007_FAILURE|", "synthetic-private", "synthetic-test-value"):
                    self.assertNotIn(forbidden, output.getvalue())
        for scope in self.SCOPES[:3]:
            with patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic-test-value"}), \
                 patch.object(runner, "resolve_target") as connect, redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(CliTests.CONFIRMED + ["--scope", scope,
                    "--check-phase-diagnostics", "--check-capture-projection"]), 1)
                connect.assert_not_called()
        self.assertFalse(runner.build_parser().parse_args(CliTests.BASE).check_phase_diagnostics)

    def test_default_failure_retains_result_and_emits_only_outer_fields_for_every_scope(self):
        for contract in runner.KNOWN_CONTRACTS:
            result = harness_result(contract=contract,
                phases=[("SETUP", "FAIL", "FAIL_EXECUTION"), ("CLEANUP", "PASS", "OK")],
                summary="FAIL|FAIL_EXECUTION", returncode=2)
            result = replace(result, stdout=result.stdout + "\nsynthetic-private SELECT secret FROM source")
            with self.subTest(scope=contract.scope), patch.object(runner, "run_harness", return_value=result) as process, \
                 patch.object(runner, "assert_absent") as absent, redirect_stdout(io.StringIO()) as output, \
                 self.assertRaisesRegex(runner.RunnerFailure, "FAIL_EXECUTION"):
                runner.run_one(target(), 1, contract=contract)
            process.assert_called_once_with(target(), contract=contract)
            absent.assert_called_once()
            text = output.getvalue()
            self.assertIn("DGN007_FAILURE|OUTER_PHASE|SETUP|FAIL|FAIL_EXECUTION", text)
            self.assertIn("DGN007_FAILURE|OUTER_SUMMARY|FAIL|FAIL_EXECUTION", text)
            self.assertLess(text.index("DGN007_CLEANUP|"), text.index("DGN007_FAILURE|"))
            self.assertNotIn("synthetic-private", text)

    def test_failed_phase_and_actual_stderr_binding_for_every_scope(self):
        for contract in runner.KNOWN_CONTRACTS:
            phase = "QUERY_STORE_WINDOWS" if contract == runner.QUERY_STORE_WINDOWS_CONTRACT else "DATA_ASSERTION"
            result = harness_result(contract=contract, phases=[(phase, "FAIL", "FAIL_EXECUTION"), ("CLEANUP", "PASS", "OK")],
                                    summary="FAIL|FAIL_EXECUTION", returncode=2)
            result = replace(result, stderr="\n".join((
                f"[{phase}:stderr] Msg 51002, Level 16, State 1, Server synthetic-private, Line 391",
                f"[{phase}:stderr] SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT",
                f"[{phase}:stderr] synthetic-private query_plan_xml password",
                f"[{phase}:stdout] Msg 51002, Level 16, State 1, Line 999",
                "[UNKNOWN:stderr] Msg 51002, Level 16, State 1, Line 999",
                "[SETUP:stderr] Msg 51002, Level 16, State 1, Line 999")))
            with self.subTest(scope=contract.scope), patch.object(runner, "run_harness", return_value=result), \
                 patch.object(runner, "assert_absent"), redirect_stdout(io.StringIO()) as output, \
                 self.assertRaisesRegex(runner.RunnerFailure, "FAIL_EXECUTION"):
                runner.run_one(target(), 1, contract=contract, check_phase_diagnostics=True)
            self.assertIn(f"DGN007_FAILURE|SQL_MESSAGE|{phase}|msg=51002; line=391", output.getvalue())
            self.assertIn(f"DGN007_FAILURE|SQL_STATUS|{phase}|FAIL|FAIL_RESULT_CONTRACT", output.getvalue())
            for forbidden in ("synthetic-private", "query_plan_xml", "password", "line=999", "SQL_GUARD"):
                self.assertNotIn(forbidden, output.getvalue())

    def test_scope_bound_limit_priority_with_actual_private_python_pipe(self):
        contract = runner.QUERY_STORE_WINDOWS_CONTRACT
        for phase, channel, code, expected in (
            ("QUERY_STORE_WINDOWS", "stderr", "FAIL_TIMEOUT", "FAIL_TIMEOUT"),
            ("CONTROL_WINDOWS", "stderr", "FAIL_TIMEOUT", "FAIL_CONTRACT"),
            ("QUERY_STORE_WINDOWS", "stdout", "FAIL_TIMEOUT", "FAIL_CONTRACT"),
            ("CLEANUP", "stderr", "FAIL_CLEANUP", "FAIL_CLEANUP"),
        ):
            line = f"[{phase}:{channel}] SQLPERF_SUMMARY|FAIL|{code}\n"
            command = [sys.executable, "-c", "import sys; sys.stderr.write(" + repr(line) + "); sys.stderr.flush(); sys.stderr.write('x'*9000); sys.stderr.flush()"]
            with self.subTest(phase=phase, channel=channel), self.assertRaisesRegex(runner.RunnerFailure, expected):
                runner.collect_capture_process(runner.start_sqlcmd(command), command, contract=contract)

    def test_sql_message_diagnostics_require_fail_not_warn_skip_or_pass(self):
        for outcome, code in (("WARN", "WARN_EMPIRICAL_VARIANCE"), ("SKIP", "SKIP_EVIDENCE_MISSING"), ("PASS", "OK")):
            result = harness_result(phases=[("SETUP", outcome, code)], summary=f"{outcome}|{code}")
            result = replace(result, stderr="[SETUP:stderr] Msg 51002, Level 16, State 1, Line 391")
            diagnostics = runner.capture_failure_diagnostics(result, contract=runner.DATA_MODEL_CONTRACT)
            self.assertFalse(any("|SQL_MESSAGE|" in line for line in diagnostics))

    def test_sql20_raw_evidence_requires_failed_phase_and_complete_numeric_block(self):
        contract = runner.QUERY_STORE_WINDOWS_CONTRACT
        result = harness_result(contract=contract,
            phases=[('QUERY_STORE_WINDOWS', 'FAIL', 'FAIL_EXECUTION'), ('CLEANUP', 'PASS', 'OK')],
            summary='FAIL|FAIL_EXECUTION', returncode=2)
        records = (
            'DGN007_SQL20_RAW|1|BEGIN|COMPLETE|1',
            'DGN007_SQL20_RAW|1|WINDOW|0|4|4|0',
            'DGN007_SQL20_RAW|1|WINDOW|1|4|3|3',
            'DGN007_SQL20_RAW|1|ROW|1|1|10|10|20|30|0|3|2026-10-10T12:00:00.0000000+00:00|2026-10-10T12:00:01.0000000+00:00',
            'DGN007_SQL20_RAW|1|END|1',
        )
        result = replace(result, stderr='\n'.join(f'[QUERY_STORE_WINDOWS:stderr] {line}' for line in records))
        found = runner._query_store_raw_diagnostics(result, contract=contract)
        self.assertEqual(found[0], 'DGN007_FAILURE|SQL20_RAW|COMPLETE|rows=1')
        self.assertIn('DGN007_FAILURE|SQL20_RAW|WINDOW|1|4|3|3', found)
        self.assertEqual(runner._query_store_raw_diagnostics(replace(result, stderr=result.stderr.replace(
            'QUERY_STORE_WINDOWS:stderr', 'SETUP:stderr')), contract=contract),
            ('DGN007_FAILURE|SQL20_RAW|INSUFFICIENT|MALFORMED',))

    def test_g13_raw_evidence_preserves_zero_count_and_rejects_private_text(self):
        contract = runner.CONTROL_BA_CONTRACT
        result = harness_result(contract=contract,
            phases=[('CONTROL_EVIDENCE', 'FAIL', 'FAIL_RESULT_CONTRACT'), ('CLEANUP', 'PASS', 'OK')],
            summary='FAIL|FAIL_RESULT_CONTRACT', returncode=2)
        records = (
            'DGN007_G13_RAW|1|BEGIN|COMPLETE|1',
            'DGN007_G13_RAW|1|ROW|1|1|10|10|20|30|0|0|2026-10-10T12:00:00.0000000+00:00|2026-10-10T12:00:00.0000000+00:00',
            'DGN007_G13_RAW|1|END|1',
            'DGN007_CONTROL_GUARD|G13',
        )
        result = replace(result, stderr='\n'.join(f'[CONTROL_EVIDENCE:stderr] {line}' for line in records))
        found = runner._query_store_raw_diagnostics(result, contract=contract)
        self.assertEqual(found[0], 'DGN007_FAILURE|G13_RAW|COMPLETE|rows=1')
        self.assertIn('|0|0|2026-10-10T12:00:00', found[1])
        poisoned = replace(result, stderr=result.stderr.replace('20|30|0|0|', '20|secret|0|0|'))
        self.assertEqual(runner._query_store_raw_diagnostics(poisoned, contract=contract),
                         ('DGN007_FAILURE|G13_RAW|INSUFFICIENT|MALFORMED',))

    def test_raw_evidence_source_failure_and_overflow_are_explicit(self):
        contract = runner.CONTROL_BA_CONTRACT
        result = harness_result(contract=contract,
            phases=[('CONTROL_EVIDENCE', 'FAIL', 'FAIL_RESULT_CONTRACT'), ('CLEANUP', 'PASS', 'OK')],
            summary='FAIL|FAIL_RESULT_CONTRACT', returncode=2)
        for status, count, expected in (('INSUFFICIENT', 0, 'SOURCE'), ('OVERFLOW', 17, 'OVERFLOW')):
            lines = [f'DGN007_G13_RAW|1|BEGIN|{status}|{count}']
            if status == 'OVERFLOW':
                lines += [f'DGN007_G13_RAW|1|ROW|{i}|1|10|10|{i}|30|0|0|N|N'
                          for i in range(1, 17)]
            lines += ['DGN007_G13_RAW|1|END|0', 'DGN007_CONTROL_GUARD|G13']
            changed = replace(result, stderr='\n'.join(f'[CONTROL_EVIDENCE:stderr] {line}' for line in lines))
            self.assertEqual(runner._query_store_raw_diagnostics(changed, contract=contract),
                             (f'DGN007_FAILURE|G13_RAW|INSUFFICIENT|{expected}',))

    def test_new_flag_preserves_sticky_cleanup_and_timeout_priority(self):
        contract = runner.QUERY_STORE_WINDOWS_CONTRACT
        result = harness_result(contract=contract, phases=[("QUERY_STORE_WINDOWS", "FAIL", "FAIL_TIMEOUT"), ("CLEANUP", "PASS", "OK")],
                                summary="FAIL|FAIL_TIMEOUT", returncode=3)
        for absence_failure, expected in ((None, "FAIL_TIMEOUT"), (runner.RunnerFailure("FAIL_CLEANUP"), "FAIL_CLEANUP")):
            with self.subTest(expected=expected), patch.object(runner, "run_harness", return_value=result), \
                 patch.object(runner, "assert_absent", side_effect=[absence_failure, None] if absence_failure else [None]) as absent, \
                 patch.object(runner, "recover"), redirect_stdout(io.StringIO()) as output, \
                 self.assertRaisesRegex(runner.RunnerFailure, expected):
                runner.run_one(target(), 1, contract=contract, check_phase_diagnostics=True)
            self.assertEqual(absent.call_count, 2 if absence_failure else 1)
            self.assertIn(f"DGN007_STAGE|{contract.scope}|RUN_1|FAIL|{expected}", output.getvalue())


if __name__ == "__main__":
    unittest.main()
