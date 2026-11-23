from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from optsp_paired_evidence import CONFIGURATIONS, evaluate_series
from run_optsp_paired import Database, OwnedPilot, PilotError, main


def witness(option, variant, database):
    common = "b" * 64
    other = "c" * 64
    actors = []
    for index in (0, 1):
        timings = (3, 5, 9, 13, 15) if index == 0 else (4, 6, 10, 14, 16)
        if variant == "SEQUENTIAL" and index == 1:
            timings = (20, None, None, 24, 26)
        elif option and index == 1:
            timings = (4, None, None, 14, 16)
        row = {"ordinal": index, "request_batch_digest": other if variant == "DISTINCT" and index == 1 else common}
        for name, time in zip(("rpc_start", "first_estimate", "compile_end", "statement_end", "rpc_end"), timings):
            row[name] = row[f"{name}_ordinal"] = time
        actors.append(row)
    waits = []
    locks = []
    if option:
        waits = [
            {"label": "TAB: N:N:N [COMPILE]", "numeric": [str(database), "77", "1"],
             "opcode": phase, "actor": 1, "ticks": time, "ordinal": time}
            for phase, time in (("Begin", 7), ("End", 11))
        ]
        locks = [
            {"name": f"lock_{phase}", "actor": actor, "ticks": time, "ordinal": time,
             "rawfields": ["77", "77", "2", "1"], "description": "[COMPILE]"}
            for phase, actor, time in (("acquired", 0, 4), ("released", 0, 10),
                                       ("acquired", 1, 12), ("released", 1, 13))
        ]
        # Recording sequence identities need not equal timestamp labels.
        locks[0]["ordinal"], actors[1]["rpc_start_ordinal"] = 40, 41
        for item in (*waits, *locks[1:]):
            item["ordinal"] *= 10
        for row in actors:
            for name in ("rpc_start", "first_estimate", "compile_end", "statement_end", "rpc_end"):
                key = f"{name}_ordinal"
                if row[key] is not None and row[key] != 41:
                    row[key] *= 10
    return {
        "status": "OBSERVED", "xe_cleanup": "PASS", "option": option, "variant": variant, "db_id": database,
        "actors": actors, "barrier_actors": [] if variant == "SEQUENTIAL" else [0, 1],
        "instance_before": "d" * 64, "instance_after": "d" * 64,
        "profile_before": "e" * 64, "profile_after": "e" * 64, "cache_before": 0,
        "batch_digest": common, "workload_digest": other if variant == "DISTINCT" else common,
        "wait_key_witness": waits, "object_lock_witness": locks, "prepared_entry_matches": bool(option),
    }


def series():
    return [witness(option, variant, 5 + index) for index, (option, variant) in enumerate(CONFIGURATIONS)]


class SeriesTests(unittest.TestCase):
    def test_matches_real_evidence_classes(self):
        self.assertEqual(evaluate_series(series()), (
            ("OFF_ON", "PROVEN", "matched_off_on_pair"),
            ("ON_OFF", "PROVEN", "matched_off_on_pair"),
            ("SEQUENTIAL", "NOT_PROVEN", "no_compile_overlap"),
            ("DISTINCT", "NOT_PROVEN", "request_binding"),
            ("DISTINCT_PAIR", "NOT_PROVEN", "pair_workload"),
        ))

    def test_lost_second_arm_or_reused_database_rejects_series(self):
        with self.assertRaises(ValueError):
            evaluate_series(series()[:-1])
        records = series()
        records[-1]["db_id"] = records[0]["db_id"]
        with self.assertRaises(ValueError):
            evaluate_series(records)

    def test_wait_shape_and_on_prepared_entry_must_be_bound(self):
        for field, value in (("opcode", "End"), ("label", "TAB: N:N:N")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                records = series()
                records[1]["wait_key_witness"][0][field] = value
                evaluate_series(records)
        records = series()
        records[1]["prepared_entry_matches"] = False
        with self.assertRaises(ValueError):
            evaluate_series(records)

    def test_partial_sql_cleanup_still_removes_and_verifies_only_owned_container(self):
        pilot = OwnedPilot()
        pilot.create_attempted = True
        pilot.databases = [Database("a" * 32), Database("b" * 32)]
        container = "5" * 64
        with (
            patch.object(pilot, "_owned_container", side_effect=[container, container, None]) as owned,
            patch.object(pilot, "_drop_database", side_effect=[PilotError("missing owner"), None]) as drop,
            patch.object(pilot, "_sql", return_value=""),
            patch.object(pilot, "_docker") as docker,
        ):
            self.assertFalse(pilot.cleanup())
            self.assertEqual(drop.call_count, 2)
            self.assertEqual(owned.call_count, 3)
            docker.assert_called_once_with("rm", "--force", "--volumes", container)

    def test_missing_confirmation_and_failed_cleanup(self):
        with patch("run_optsp_paired.OwnedPilot") as pilot, redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as stopped:
                main([])
        self.assertEqual(stopped.exception.code, 2)
        pilot.assert_not_called()
        output = StringIO()
        with patch("run_optsp_paired.OwnedPilot") as pilot, redirect_stdout(output):
            pilot.return_value.execute.return_value = evaluate_series(series())
            pilot.return_value.cleanup.return_value = False
            self.assertEqual(main(["--confirm-disposable-container"]), 3)
        self.assertIn("OPTSP|FAIL_CLEANUP", output.getvalue())
        self.assertNotIn("OPTSP|PASS|", output.getvalue())


if __name__ == "__main__":
    unittest.main()
