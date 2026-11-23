import os
import re
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


    @patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic"}, clear=True)
    def test_compile_rejection_still_drops_session_and_verifies_database_absence(self):
        outputs = ["EMPTY_DEVELOPER", "XE_ABSENT", probe.SETUP_SUMMARY, "missing evidence",
                   "XE_ABSENT", probe.SETUP_SUMMARY, "ABSENT"]
        with patch.object(probe.runner, "resolve_target", return_value=object()), \
             patch.object(probe, "_batch", side_effect=outputs) as run:
            with self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
                probe.run_probe("synthetic-container", parameter_mix=True, compile_cost=True)
        session = re.search(r"SQLPERF_DGN007_COMPILE_[0-9a-f]{32}", run.call_args_list[1].args[1]).group()
        self.assertIn(f"DROP EVENT SESSION [{session}]", run.call_args_list[4].args[1])
        self.assertIn("sys.dm_xe_sessions", run.call_args_list[4].args[1])
        self.assertEqual(run.call_args.args[1], probe.ABSENCE)

    @patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic"}, clear=True)
    def test_existing_named_session_is_rejected_before_setup_and_never_dropped(self):
        with patch.object(probe.runner, "resolve_target", return_value=object()), \
             patch.object(probe, "_batch", side_effect=["EMPTY_DEVELOPER", "EXISTS"]) as run:
            with self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
                probe.run_probe("synthetic-container", parameter_mix=True, compile_cost=True)
        self.assertEqual(run.call_count, 2)


class CompileCostOutputTests(unittest.TestCase):
    def output(self):
        compiled_slots = {1, *range(10, 19)}
        rows = [
            f"DGN007_COMPILER_SLOT|{slot}|{int(slot in compiled_slots)}|"
            + ("2|3" if slot in compiled_slots else "0|0")
            for slot in range(1, 23)
        ]
        return "\n".join([probe._COMPILER_ROSTER, *rows])

    def test_compilation_cost_excludes_the_two_seed_requests(self):
        self.assertEqual(probe._compile_cost_report(self.output()).splitlines(), [
            "DGN007_COMPILE_COST|BASELINE1|0|0|0",
            "DGN007_COMPILE_COST|BASELINE2|0|0|0",
            "DGN007_COMPILE_COST|MITIGATION1|4|8|12",
            "DGN007_COMPILE_COST|MITIGATION2|4|8|12",
            "DGN007_COMPILE_COST|RESTORE|0|0|0",
        ])

    def test_rejects_missing_slot_reordered_rows_and_nonzero_cost_without_event(self):
        fixture = self.output()
        for bad in (
            fixture.replace("DGN007_COMPILER_SLOT|2|0|0|0\n", ""),
            fixture.replace("DGN007_COMPILER_SLOT|2|0|0|0", "DGN007_COMPILER_SLOT|4|0|0|0"),
            fixture.replace("DGN007_COMPILER_SLOT|2|0|0|0", "DGN007_COMPILER_SLOT|2|0|9|0"),
            fixture.replace("DGN007_COMPILER_SLOT|19|0|0|0", "DGN007_COMPILER_SLOT|19|1|2|3"),
        ):
            with self.subTest(case=bad), self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
                probe._compile_cost_report(bad)


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

    def test_mix_keeps_class_regression_visible_when_total_improves(self):
        by_stage = ((18, 12, 6, 3), (12, 18, 6, 3), (3, 6, 3, 6), (3, 6, 3, 6), (18, 12, 6, 3))
        parts = []
        for stage, values in zip(probe._MITIGATION_STAGES, by_stage, strict=True):
            for slot, reads in enumerate(values, 1):
                label = f"{stage}_{slot}"
                parts.append(f"DGN007_IO_BEGIN|{label}")
                parts.extend(
                    f"Table '{table}'. Scan count 1, logical reads {reads // 3}, physical reads 0."
                    for table in sorted(probe._SOURCE_TABLES)
                )
                parts.append(f"DGN007_IO_END|{label}")
        output = "\n".join([*parts, probe.MITIGATION_SQL_SUMMARY])
        self.assertEqual(probe._mitigation_mix_report(output).splitlines(), [
            "DGN007_MIX_READS|TOTAL|39|39|18|18|39",
            "DGN007_MIX_READS|1,1|18|12|3|3|18",
            "DGN007_MIX_READS|1,3|12|18|6|6|12",
            "DGN007_MIX_READS|5,3|6|6|3|3|6",
            "DGN007_MIX_READS|8,3|3|3|6|6|3",
        ])
        incomplete = output.replace("DGN007_IO_END|MITIGATION2_4", "DGN007_IO_END|MITIGATION2_3")
        with self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
            probe._mitigation_mix_report(incomplete)

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
