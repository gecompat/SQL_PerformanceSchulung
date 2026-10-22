"""Gegenproben gegen falsche Erfolgsmeldungen des Eigentumsprüfers, ohne SQL."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))
import qry001_cleanup_ownership as probe


class OwnershipOracleTests(unittest.TestCase):
    def setUp(self):
        self.target = probe.ExecutionTarget("docker", "localhost", "sql", "sa", Path("shim"), "sqlcmd", "synthetic-probe")

    def test_host_is_rejected_before_any_sql(self):
        target = probe.ExecutionTarget("host", "synthetic", "integrated", None, Path("shim"), "sqlcmd")
        with patch.object(probe, "run_sql") as sql, self.assertRaises(probe.OwnershipFailure):
            probe.run_ownership_probes(target)
        sql.assert_not_called()

    def test_arbitrary_sql_error_is_not_a_successful_guard(self):
        for message in ("Msg 208 FAIL_CLEANUP", "Msg 51004 permission denied", "connection failed"):
            with self.subTest(message=message), patch.object(probe, "run_sql", side_effect=probe.ExecutionTargetError(message)):
                with self.assertRaises(probe.OwnershipFailure):
                    probe.require_rejection(self.target, "synthetic", 51004)

    def test_only_expected_error_code_and_category_are_accepted(self):
        for code, category in ((51004, "FAIL_CLEANUP"), (51000, "FAIL_CONTRACT")):
            with patch.object(probe, "run_sql", side_effect=probe.ExecutionTargetError(f"Msg {code} {category}")):
                probe.require_rejection(self.target, "synthetic", code)

    def test_successful_cleanup_cannot_pass_a_negative_case(self):
        with patch.object(probe, "run_sql", return_value="SQLPERF_SUMMARY|PASS|OK"), patch.object(probe, "snapshot", return_value="preserved"):
            with self.assertRaises(probe.OwnershipFailure):
                probe.require_rejection(self.target, "synthetic", 51004)

    def test_absence_and_sentinel_require_evidence(self):
        with patch.object(probe, "run_sql", return_value=""):
            with self.assertRaises(probe.OwnershipFailure):
                probe.require_absent(self.target)
            with self.assertRaises(probe.OwnershipFailure):
                probe.snapshot(self.target)
        with patch.object(probe, "run_sql", return_value="SENTINEL|730"):
            with self.assertRaises(probe.OwnershipFailure):
                probe.snapshot(self.target)

    def test_replaced_sqlcmd_parameters_leave_no_unknown_variable(self):
        with self.assertRaises(probe.OwnershipFailure):
            probe.render_cleanup("SELECT '$(Unknown)';")

    def test_structured_cleanup_row_is_required_instead_of_print_channel(self):
        row = '1|CLEANUP|SUMMARY|PASS|OK|synthetic|ownership|done'
        probe.require_cleanup_success(row)
        for output in ('', 'SQLPERF_SUMMARY|PASS|OK', row + '\n' + row, row.replace('|PASS|', '|FAIL|')):
            with self.subTest(output=output), self.assertRaises(probe.OwnershipFailure):
                probe.require_cleanup_success(output)


if __name__ == "__main__":
    unittest.main()
