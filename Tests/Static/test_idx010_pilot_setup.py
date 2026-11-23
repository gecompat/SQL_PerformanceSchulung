from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from idx010_pilot_setup import (  # noqa: E402
    Arm,
    FIXTURE_ROWS,
    FIXTURE_SHA256,
    fixture_chunk_batch,
    fixture_identity_batch,
    fixture_setup_batch,
    index_build_batch,
    target_database,
    verify_fixture_identity,
)


class PilotSetupTests(unittest.TestCase):
    def test_targets_are_distinct_from_each_other_and_the_cci_demo(self):
        self.assertEqual(target_database("RUN8", Arm.CONTROL), "SQLPERF_LAB_IDX010_NCCI_RUN8_CONTROL")
        self.assertEqual(target_database("RUN8", Arm.ORDERED), "SQLPERF_LAB_IDX010_NCCI_RUN8_ORDERED")
        for token in ("", "run", "A_B", "A'B", "A" * 21, "Å", "AA\n"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                target_database(token, Arm.CONTROL)
        with self.assertRaises(ValueError):
            target_database("RUN8", "CONTROL")

    def test_mutation_follows_build_target_and_all_ownership_guards(self):
        for batch, mutation in (
            (fixture_setup_batch("RUN8", Arm.CONTROL), "CREATE TABLE"),
            (fixture_chunk_batch("RUN8", Arm.CONTROL, 0), "INSERT dbo.Events"),
            (index_build_batch("RUN8", Arm.CONTROL), "CREATE NONCLUSTERED"),
        ):
            guard, delimiter, _ = batch.partition(mutation)
            self.assertTrue(delimiter)
            for marker in (
                "@@TRANCOUNT",
                "17.0.5065.9",
                "Enterprise Developer Edition (64-bit)",
                "SQLPERF_LAB_IDX010_NCCI_RUN8_CONTROL",
                "compatibility_level = 170 AND recovery_model = 3",
                "SQLPERF.Project",
                "SQLPERF.ContractVersion",
                "SQLPERF.DemoId",
                "SQLPERF.RunToken",
                "SQLPERF.PilotProfile",
                "ORDERED_NCCI_CONTROL",
                ") <> 5",
            ):
                self.assertIn(marker, guard)

    def test_fixture_chunks_fill_four_contiguous_ranges(self):
        for chunk, (start, end) in enumerate((
            (0, 1048575), (1048576, 2097151), (2097152, 3145727), (3145728, 4194303),
        )):
            batch = fixture_chunk_batch("RUN8", Arm.CONTROL, chunk)
            self.assertIn(f"GENERATE_SERIES(CONVERT(bigint, {start}), CONVERT(bigint, {end})", batch)
            self.assertIn(f"COUNT_BIG(*) FROM dbo.Events) <> {start}", batch)
            self.assertIn("SELECT value, (value * 1048573) % 4194304", batch)
        for invalid in (-1, 4, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                fixture_chunk_batch("RUN8", Arm.CONTROL, invalid)

    def test_only_index_order_differs_between_builds(self):
        control = index_build_batch("RUN8", Arm.CONTROL).partition("CREATE NONCLUSTERED")[2]
        ordered = index_build_batch("RUN8", Arm.ORDERED).partition("CREATE NONCLUSTERED")[2]
        self.assertIn("WITH (MAXDOP = 1, ONLINE = OFF)", control)
        self.assertEqual(ordered.replace(" ORDER (EventDayKey)", "", 1), control)

    def test_fixture_stream_matches_fixed_independent_digest(self):
        self.assertIn("ORDER BY EventId", fixture_identity_batch("RUN8", Arm.CONTROL))
        rows = ((i, (i * 1048573) % 4194304) for i in range(FIXTURE_ROWS))
        self.assertEqual(verify_fixture_identity(rows), FIXTURE_SHA256)

    def test_fixture_stream_rejects_incomplete_or_wrong_rows(self):
        for rows in ((), ((0, 0),), ((1, 1048573),), ((0, 1),), ((0, False),)):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                verify_fixture_identity(rows)


if __name__ == "__main__":
    unittest.main()
