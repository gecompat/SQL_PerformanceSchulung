"""Gegenproben gegen falsche Setup-Erfolgsmeldungen, ohne SQL-Zugriff."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))
import qry001_setup_ownership as probe


class SetupOracleTests(unittest.TestCase):
    def setUp(self):
        self.target = probe.ExecutionTarget("docker", "localhost", "sql", "sa", Path("shim"), "sqlcmd", "synthetic-probe")

    def test_unsupported_target_or_version_stops_before_sql(self):
        host = probe.ExecutionTarget("host", "synthetic", "integrated", None, Path("shim"), "sqlcmd")
        for target, major in ((host, 17), (self.target, 14)):
            with self.subTest(major=major, target=target.kind), patch.object(probe, "run_sql") as sql:
                with self.assertRaises(probe.ownership.OwnershipFailure):
                    probe.run_setup_ownership_probes(target, major)
                sql.assert_not_called()

    def test_unrelated_or_wrong_sql_error_cannot_pass(self):
        for message in ("Msg 208 FAIL_STATE", "Msg 51002 permission denied", "Msg 51000 FAIL_CONTRACT", "connection failed"):
            with self.subTest(message=message), patch.object(probe, "run_sql", side_effect=probe.ExecutionTargetError(message)):
                with self.assertRaises(probe.ownership.OwnershipFailure):
                    probe.require_setup_rejection(self.target, "synthetic")

    def test_expected_code_and_category_are_both_required(self):
        for code, category in ((51002, "FAIL_STATE"), (51000, "FAIL_CONTRACT")):
            with patch.object(probe, "run_sql", side_effect=probe.ExecutionTargetError(f"Msg {code} {category}")):
                probe.require_setup_rejection(self.target, "synthetic", code)

    def test_return_code_zero_cannot_pass_a_negative_case(self):
        with patch.object(probe, "run_sql", return_value="1|SETUP|SUMMARY|PASS|OK"):
            with self.assertRaises(probe.ownership.OwnershipFailure):
                probe.require_setup_rejection(self.target, "synthetic")

    def test_exactly_one_structured_setup_row_is_required(self):
        row = "1|SETUP|SUMMARY|PASS|OK|synthetic|ownership|done"
        probe.require_setup_success(row)
        for output in ("", "SQLPERF_SUMMARY|PASS|OK", row + "\n" + row,
                       row.replace("|PASS|", "|FAIL|"), row.replace("|SETUP|", "|CLEANUP|")):
            with self.subTest(output=output), self.assertRaises(probe.ownership.OwnershipFailure):
                probe.require_setup_success(output)

    def test_configuration_cannot_be_inferred_from_missing_or_duplicate_rows(self):
        row = "CONFIG|7|SIMPLE|0|0|2|170"
        for output in ("", "CONFIG|7|SIMPLE", row + "\n" + row, row.replace("CONFIG", "OTHER")):
            with self.subTest(output=output), patch.object(probe, "run_sql", return_value=output):
                with self.assertRaises(probe.ownership.OwnershipFailure):
                    probe.config_snapshot(self.target)
        with patch.object(probe, "run_sql", return_value=row.replace("SIMPLE", "FULL")):
            with self.assertRaises(probe.ownership.OwnershipFailure):
                probe.verify_configuration(self.target, 17)

    def test_both_table_sentinels_are_required(self):
        for output in ("", "LAB_SEARCH|919", "LAB_SEARCH|919\nLAB_EVIDENCE|920",
                       "LAB_SEARCH|919\nLAB_SEARCH|919\nLAB_EVIDENCE|919"):
            with self.subTest(output=output), patch.object(probe, "run_sql", return_value=output):
                with self.assertRaises(probe.ownership.OwnershipFailure):
                    probe.lab_snapshot(self.target)


if __name__ == "__main__":
    unittest.main()
