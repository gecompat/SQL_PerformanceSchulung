import os
import unittest
from unittest.mock import patch

from Tests.Runtime import run_dgn007_compile_value_probe as probe


class CompileProbeTests(unittest.TestCase):
    @patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic"}, clear=True)
    def test_independent_absence_is_still_checked_after_cleanup_failure(self):
        outputs = ["EMPTY_DEVELOPER", probe.SETUP_SUMMARY, probe.SUMMARY + "\nDGN007_WAIT_CONTEXT|4|no_grant_wait|no_page_io_wait|no_physical_reads",
                   probe.runner.RunnerFailure("NOT_PROVEN"), "ABSENT"]
        with patch.object(probe.runner, "resolve_target", return_value=object()), \
             patch.object(probe, "_batch", side_effect=outputs) as run:
            with self.assertRaisesRegex(probe.runner.RunnerFailure, "FAIL_CLEANUP"):
                probe.run_probe("synthetic-container")
        self.assertEqual(run.call_args.args[1], probe.ABSENCE)

    @patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic"}, clear=True)
    def test_wrong_target_is_not_modified(self):
        with patch.object(probe.runner, "resolve_target", return_value=object()), \
             patch.object(probe, "_batch", return_value="NOT_EMPTY") as run:
            with self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
                probe.run_probe("synthetic-container")
        run.assert_called_once()
        self.assertEqual(run.call_args.args[1], probe.PREFLIGHT)


class WaitContextTests(unittest.TestCase):
    def test_requires_one_complete_summary_and_preserves_nonzero_signals(self):
        observed = "DGN007_WAIT_CONTEXT|4|grant_wait_present|io_wait_present|physical_reads_present"
        self.assertEqual(probe._read_wait_context(observed), observed)
        for output in ("", observed + "\n" + observed, observed.replace("|4|", "|3|"),
                       observed.replace("grant_wait_present", "unverified")):
            with self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
                probe._read_wait_context(output)


class MitigationOutputTests(unittest.TestCase):
    @staticmethod
    def output(stages=None):
        values = {"BASELINE1": 12, "BASELINE2": 12, "MITIGATION1": 6, "MITIGATION2": 7, "RESTORE": 12}
        values.update(stages or {})
        lines = []
        for stage, reads in values.items():
            lines.append(f"DGN007_IO_BEGIN|{stage}")
            for table in ("CaseItem", "CaseGroup", "CaseItemDetail"):
                lines.append(f"Table '{table}'. Scan count 1, logical reads {reads}, physical reads 0.")
            lines.append(f"DGN007_IO_END|{stage}")
        return "\n".join([*lines, probe.MITIGATION_SQL_SUMMARY])

    def test_accepts_only_a_lower_workload_with_equal_baseline_and_restore(self):
        probe._verify_mitigation(self.output())
        for mutation in (
            {"BASELINE2": 13}, {"MITIGATION1": 12}, {"MITIGATION2": 0}, {"RESTORE": 13},
        ):
            with self.subTest(mutation=mutation), self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
                probe._verify_mitigation(self.output(mutation))

    def test_requires_exact_stage_order_and_one_io_message_per_source_table(self):
        valid = self.output()
        row = "Table 'CaseItem'. Scan count 1, logical reads 12, physical reads 0.\n"
        for invalid in (
            valid.replace(row, "", 1), valid.replace(row, row + row, 1),
            valid.replace("DGN007_IO_BEGIN|BASELINE1", "DGN007_IO_BEGIN|BASELINE2"),
            valid.replace(probe.MITIGATION_SQL_SUMMARY, ""),
        ):
            with self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
                probe._verify_mitigation(invalid)


if __name__ == "__main__":
    unittest.main()
