#!/usr/bin/env python3
"""Regression checks for the offline QRY-023 proposed-harness validator."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import validate_qry023_proposed_harness as validator


class Qry023ProposedHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.demo = self.root / "Demos/05_Query_Patterns/QRY-023_Graph_Tables"
        shutil.copytree(validator.DEMO, self.demo)
        (self.root / "Documentation/Demo_Catalog").mkdir(parents=True)
        (self.root / "Tests/Lab").mkdir(parents=True)
        (self.root / "Documentation/Project_Planning").mkdir(parents=True)
        shutil.copy2(validator.ROOT / "Documentation/Demo_Catalog/demo_execution_paths.json",
                     self.root / "Documentation/Demo_Catalog/demo_execution_paths.json")
        shutil.copy2(validator.ROOT / "Tests/Lab/performance-lab-matrix.json",
                     self.root / "Tests/Lab/performance-lab-matrix.json")
        shutil.copy2(validator.ROOT / "Documentation/Project_Planning/GRAPH_TABLES_BUILD_EDITION_REVIEW.md",
                     self.root / "Documentation/Project_Planning/GRAPH_TABLES_BUILD_EDITION_REVIEW.md")
        framework_sql = self.root / "Demos/00_Framework/Sql/FWK_Measurement.sql"
        framework_sql.parent.mkdir(parents=True)
        shutil.copy2(validator.ROOT / "Demos/00_Framework/Sql/FWK_Measurement.sql", framework_sql)

    def errors(self) -> list[str]:
        return validator.validate(self.demo, self.root)

    def test_current_draft_satisfies_offline_contract(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_catalog_manifest_is_rejected(self) -> None:
        (self.demo / "manifest.json").write_text("{}", encoding="utf-8")
        self.assertTrue(any("catalog manifest.json" in error for error in self.errors()))

    def test_readme_must_keep_the_caller_side_sqlcmd_input_gate(self) -> None:
        path = self.demo / "README.md"
        source = path.read_text(encoding="utf-8")
        source = source.replace("SQLCMD-Eingabeinjektion", "SQLCMD-Variablen")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("caller-side SQLCMD input-validation gate" in error
                            for error in self.errors()))

    def test_missing_required_cleanup_phase_is_rejected(self) -> None:
        path = self.demo / "manifest.proposed.json"
        text = path.read_text(encoding="utf-8").replace('"required":true,"require_summary":true,"timeout_seconds":90',
                                                       '"required":false,"require_summary":true,"timeout_seconds":90')
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("cleanup must be required" in error for error in self.errors()))

    def test_phase_script_and_database_bindings_are_exact(self) -> None:
        path = self.demo / "manifest.proposed.json"
        manifest = validator.json.loads(path.read_text(encoding="utf-8"))
        manifest["phases"][1]["script"] = "00_Preflight.sql"
        manifest["phases"][2]["database"] = "master"
        manifest["phases"][3]["timeout_seconds"] = 301
        path.write_text(validator.json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("scripts, databases, and timeouts" in error for error in self.errors()))

    def test_malformed_phase_record_fails_without_crashing(self) -> None:
        path = self.demo / "manifest.proposed.json"
        manifest = validator.json.loads(path.read_text(encoding="utf-8"))
        manifest["phases"][0] = "PREFLIGHT"
        path.write_text(validator.json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("phase must be an object" in error for error in self.errors()))

    def test_run_and_cleanup_budgets_are_exact(self) -> None:
        path = self.demo / "manifest.proposed.json"
        manifest = validator.json.loads(path.read_text(encoding="utf-8"))
        manifest["timeout_seconds"] = 901
        manifest["cleanup"]["database"] = "target"
        path.write_text(validator.json.dumps(manifest), encoding="utf-8")
        errors = self.errors()
        self.assertTrue(any("900-second run" in error for error in errors))
        self.assertTrue(any("in master with a 90-second timeout" in error for error in errors))

    def test_non_object_manifest_fails_without_crashing(self) -> None:
        (self.demo / "manifest.proposed.json").write_text("[]", encoding="utf-8")
        self.assertIn("proposed manifest root must be an object", self.errors())

    def test_cleanup_without_run_token_marker_is_rejected(self) -> None:
        path = self.demo / "90_Cleanup.sql"
        path.write_text(path.read_text(encoding="utf-8").replace("SQLPERF.RunToken", "SQLPERF.OtherToken"),
                        encoding="utf-8")
        self.assertTrue(any("cleanup must bind the sqlperf.runtoken" in error for error in self.errors()))

    def test_unpinned_product_version_is_rejected(self) -> None:
        path = self.demo / "00_Preflight.sql"
        path.write_text(path.read_text(encoding="utf-8").replace("15.0.4500.2", "15.0.4480.2"),
                        encoding="utf-8")
        self.assertTrue(any("must pin the proposed engine build 15.0.4500.2" in error
                            for error in self.errors()))

    def test_image_reference_must_use_immutable_digest(self) -> None:
        path = self.demo / "container-images.proposed.json"
        lock = validator.json.loads(path.read_text(encoding="utf-8"))
        lock["profiles"][0]["image"] = "mcr.microsoft.com/mssql/server:2019-CU32-ubuntu-20.04"
        path.write_text(validator.json.dumps(lock), encoding="utf-8")
        self.assertTrue(any("immutable manifest digest" in error for error in self.errors()))

    def test_image_build_must_match_sql_pins(self) -> None:
        path = self.demo / "container-images.proposed.json"
        lock = validator.json.loads(path.read_text(encoding="utf-8"))
        lock["profiles"][0]["product_version_label"] = "15.0.4430.1"
        path.write_text(validator.json.dumps(lock), encoding="utf-8")
        self.assertTrue(any("match preflight and setup build pins" in error for error in self.errors()))

    def test_sql_memory_limit_must_remain_below_container_limit(self) -> None:
        path = self.demo / "container-images.proposed.json"
        lock = validator.json.loads(path.read_text(encoding="utf-8"))
        lock["resources"]["container"]["sql_memory_limit_mib"] = 4096
        path.write_text(validator.json.dumps(lock), encoding="utf-8")
        self.assertTrue(any("remain below container memory" in error for error in self.errors()))

    def test_framework_begin_signature_drift_is_rejected(self) -> None:
        path = self.root / "Demos/00_Framework/Sql/FWK_Measurement.sql"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "@CaptureSessionWaits bit = 1", "@CaptureSessionWaits int = 1"), encoding="utf-8")
        self.assertTrue(any("Begin signature must retain @capturesessionwaits bit = 1" in error
                            for error in self.errors()))

    def test_missing_framework_result_column_is_rejected(self) -> None:
        path = self.root / "Demos/00_Framework/Sql/FWK_Measurement.sql"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "LogicalReads bigint NULL,", "LogicalReadsValue bigint NULL,"), encoding="utf-8")
        self.assertTrue(any("MeasurementRun must expose logicalreads" in error
                            for error in self.errors()))

    def test_framework_must_expose_reads_and_writes(self) -> None:
        path = self.root / "Demos/00_Framework/Sql/FWK_Measurement.sql"
        source = path.read_text(encoding="utf-8")
        for column in ("Reads", "Writes"):
            with self.subTest(column=column):
                changed = source.replace(f"{column} bigint NULL,", f"{column}Value bigint NULL,")
                path.write_text(changed, encoding="utf-8")
                self.assertTrue(any(f"MeasurementRun must expose {column.lower()}" in error
                                    for error in self.errors()))

    def test_measurement_requires_all_captured_deltas(self) -> None:
        path = self.demo / "40_Measurement.sql"
        measurement = path.read_text(encoding="utf-8")
        measurement = measurement.replace("OR m.Reads IS NULL", "").replace("OR m.Writes IS NULL", "")
        path.write_text(measurement, encoding="utf-8")
        self.assertTrue(any("reject incomplete or unsuccessful" in error for error in self.errors()))


    def test_plan_diagnostic_resets_statistics_xml_on_error(self) -> None:
        path = self.demo / "50_Plan_Evidence.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("BEGIN CATCH\n    SET STATISTICS XML OFF;", "BEGIN CATCH\n    THROW;")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("reset STATISTICS XML on success and error" in error
                            for error in self.errors()))

    def test_plan_graph_query_must_match_measured_shape(self) -> None:
        path = self.demo / "50_Plan_Evidence.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("MATCH(p1-(e1)->p2-(e2)->p3)", "MATCH(p1-(e1)->p2)")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("preserve the measured Graph and relational COUNT_BIG" in error
                            for error in self.errors()))

    def test_plan_relational_query_must_match_measured_shape(self) -> None:
        path = self.demo / "50_Plan_Evidence.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("p3.PersonId=e2.ToPersonId", "p2.PersonId=e2.ToPersonId")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("preserve the measured Graph and relational COUNT_BIG" in error
                            for error in self.errors()))

    def test_plan_success_summary_cannot_precede_option_cleanup(self) -> None:
        path = self.demo / "50_Plan_Evidence.sql"
        source = path.read_text(encoding="utf-8")
        marker = "    SET STATISTICS XML OFF;"
        early_summary = "SELECT 1 AS Sequence,'PLAN_EVIDENCE' AS Phase;\nPRINT 'SQLPERF_SUMMARY|PASS|OK';\n"
        source = source.replace(marker, early_summary + marker, 1)
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("success summaries must occur once after successful STATISTICS XML cleanup" in error
                            for error in self.errors()))

    def test_plan_summary_outcome_must_remain_pass(self) -> None:
        path = self.demo / "50_Plan_Evidence.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("'PASS' AS Outcome,'OK' AS Code", "'WARN' AS Outcome,'OK' AS Code")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("expected PASS/OK phase and check fields" in error for error in self.errors()))

    def test_plan_summary_code_must_remain_ok(self) -> None:
        path = self.demo / "50_Plan_Evidence.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("'PASS' AS Outcome,'OK' AS Code", "'PASS' AS Outcome,'ERR' AS Code")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("expected PASS/OK phase and check fields" in error for error in self.errors()))

    def test_plan_queries_must_stay_inside_statistics_window(self) -> None:
        path = self.demo / "50_Plan_Evidence.sql"
        source = path.read_text(encoding="utf-8")
        start = source.index("    SELECT PathCount=COUNT_BIG(*)")
        end = source.index("    SET STATISTICS XML OFF;", start)
        queries = source[start:end]
        source = source[:start] + source[end:]
        try_start = source.index("BEGIN TRY")
        source = source[:try_start] + queries + source[try_start:]
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("both plan queries must execute inside the STATISTICS XML ON/OFF window" in error
                            for error in self.errors()))

    def test_showplan_permission_must_be_scoped_to_current_target_database(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','SHOWPLAN')",
                                "HAS_PERMS_BY_NAME(N'master','DATABASE','SHOWPLAN')")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("target DATABASE/SHOWPLAN" in error for error in self.errors()))

    def test_showplan_preflight_must_check_all_query_table_select_rights(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("    AND HAS_PERMS_BY_NAME(N'dbo.RelFriend','OBJECT','SELECT')=1 THEN 1 ELSE 0 END;",
                                "    THEN 1 ELSE 0 END;")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("target DATABASE/SHOWPLAN" in error for error in self.errors()))

    def test_missing_permissions_must_skip_before_pass(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("'SKIP_PERMISSION' AS Code", "'SKIP_STATE' AS Code")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("target DATABASE/SHOWPLAN" in error for error in self.errors()))

    def test_qualification_skip_summary_must_report_skip_permission(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("'SKIP' AS Outcome,'SKIP_PERMISSION' AS Code",
                                "'FAIL' AS Outcome,'SKIP_PERMISSION' AS Code")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("summary rows and PRINT markers must match" in error for error in self.errors()))

    def test_qualification_success_summary_must_report_pass_ok(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code",
                                "'SUMMARY' AS CheckId,'WARN' AS Outcome,'OK' AS Code")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("summary rows and PRINT markers must match" in error for error in self.errors()))

    def test_qualification_skip_print_must_match_skip_row(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION",
                                "SQLPERF_SUMMARY|SKIP|SKIP_STATE")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("summary rows and PRINT markers must match" in error for error in self.errors()))

    def test_qualification_preflight_must_bind_current_database_to_target(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("DB_NAME()<>@TargetDatabase", "DB_NAME()=@TargetDatabase")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("mismatched DB_NAME()/@TargetDatabase" in error for error in self.errors()))

    def test_qualification_preflight_must_reject_system_databases(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("IF DB_ID()<=4 OR @DemoId", "IF @DemoId")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("reject system databases" in error for error in self.errors()))

    def test_qualification_preflight_must_bind_exact_project_marker(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace(
            "@Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung'",
            "@Project COLLATE Latin1_General_100_BIN2<>N'OtherProject'",
        )
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("all four exact, length-aware ownership markers" in error
                            for error in self.errors()))

    def test_qualification_preflight_must_bind_run_token_to_harness(self) -> None:
        path = self.demo / "25_Qualification_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace(
            "@MarkerRun COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@RunToken)",
            "@MarkerRun COLLATE Latin1_General_100_BIN2=CONVERT(nvarchar(max),@RunToken)",
        )
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("all four exact, length-aware ownership markers" in error
                            for error in self.errors()))

    def test_preflight_must_reject_a_weakened_run_token_length(self) -> None:
        path = self.demo / "00_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("LEN(@RunToken) NOT BETWEEN 1 AND 20",
                                "LEN(@RunToken) NOT BETWEEN 1 AND 40")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("deterministic target database name and exact RunToken format" in error
                            for error in self.errors()))

    def test_preflight_must_derive_the_expected_database_prefix(self) -> None:
        path = self.demo / "00_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("SQLPERF_LAB_", "OTHER_LAB_")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("deterministic target database name and exact RunToken format" in error
                            for error in self.errors()))

    def test_preflight_must_require_the_derived_target_database(self) -> None:
        path = self.demo / "00_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("@TargetDatabase <> @ExpectedDatabase",
                                "@TargetDatabase = @ExpectedDatabase")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("deterministic target database name and exact RunToken format" in error
                            for error in self.errors()))

    def test_preflight_guards_must_fail_closed_with_or_operators(self) -> None:
        path = self.demo / "00_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("OR @RunToken IS NULL", "AND @RunToken IS NULL")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("deterministic target database name and exact RunToken format" in error
                            for error in self.errors()))

    def test_preflight_must_keep_the_run_token_byte_length_bound(self) -> None:
        path = self.demo / "00_Preflight.sql"
        source = path.read_text(encoding="utf-8")
        source = source.replace("DATALENGTH(@RunToken) NOT BETWEEN 1 AND 20",
                                "DATALENGTH(@RunToken) NOT BETWEEN 1 AND 40")
        path.write_text(source, encoding="utf-8")
        self.assertTrue(any("deterministic target database name and exact RunToken format" in error
                            for error in self.errors()))


if __name__ == "__main__":
    unittest.main()
