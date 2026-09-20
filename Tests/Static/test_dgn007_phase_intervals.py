"""Regression der echten SQL-Intervallpraedikate mit synthetischen Zeitwerten."""
from __future__ import annotations

import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTALL = ROOT / "Scenarios/DGN-007/adapter/sql/install.sql"
VALIDATE = ROOT / "Scenarios/DGN-007/adapter/sql/validate.sql"
COMPARISON = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/60_Comparison.sql"


class PhaseIntervalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.executescript("""
            CREATE TABLE interval_bounds(runtime_stats_interval_id INT, start_time TEXT, end_time TEXT);
            CREATE TABLE phase(MarkerUtc TEXT, CompletedUtc TEXT);
            CREATE TABLE runtime(runtime_stats_interval_id INT, count_executions INT,
                                 first_execution_time TEXT, last_execution_time TEXT, execution_type INT);
            INSERT INTO interval_bounds VALUES
                (10,'07:24:00.000','07:25:00.000'),(11,'07:25:00.000','07:26:00.000'),
                (12,'07:26:00.000','07:27:00.000');
            INSERT INTO phase VALUES('07:24:43.486','07:24:43.558');
            INSERT INTO runtime VALUES
                (10,3,'07:24:43.500','07:24:43.560',0),
                (11,5,'07:25:01.000','07:25:01.100',0),
                (12,4,'07:26:01.000','07:26:01.100',0);
        """)

    def phase_counts(self, path: Path) -> list[tuple[int, int]]:
        text = path.read_text(encoding="utf-8")
        profile = text[text.index("INSERT lab.IncidentQueryStoreProfile"):]
        predicate = re.search(r"WHERE (.*?)\s+GROUP BY", profile, re.S)
        self.assertIsNotNone(predicate)
        return self.connection.execute(
            "SELECT rs.runtime_stats_interval_id,SUM(rs.count_executions) "
            "FROM runtime rs JOIN interval_bounds i USING(runtime_stats_interval_id) "
            f"CROSS JOIN phase s WHERE {predicate.group(1)} GROUP BY rs.runtime_stats_interval_id"
        ).fetchall()

    def test_observed_completion_skew_keeps_only_baseline_interval(self) -> None:
        for path in (INSTALL, COMPARISON):
            with self.subTest(path=path.name):
                self.assertEqual(self.phase_counts(path), [(10, 3)])

    def test_next_phase_excludes_prior_and_future_intervals(self) -> None:
        self.connection.execute("UPDATE phase SET MarkerUtc='07:25:00.000',CompletedUtc='07:25:01.098'")
        for path in (INSTALL, COMPARISON):
            with self.subTest(path=path.name):
                self.assertEqual(self.phase_counts(path), [(11, 5)])

    def test_multiple_rows_in_active_interval_are_aggregated(self) -> None:
        self.connection.execute("UPDATE runtime SET count_executions=2 WHERE runtime_stats_interval_id=10")
        self.connection.execute("INSERT INTO runtime VALUES(10,1,'07:24:43.560','07:24:43.560',0)")
        self.connection.execute("INSERT INTO runtime VALUES(10,1,'07:24:43.550','07:24:43.550',3)")
        self.assertEqual(self.phase_counts(INSTALL), [(10, 3)])

    def test_phase_crossing_interval_boundary_preserves_both_intervals(self) -> None:
        self.connection.execute("UPDATE phase SET CompletedUtc='07:25:01.098'")
        for path in (INSTALL, COMPARISON):
            with self.subTest(path=path.name):
                self.assertEqual(self.phase_counts(path), [(10, 3), (11, 5)])

    def test_extra_same_interval_execution_is_not_hidden_by_time_filter(self) -> None:
        self.connection.execute("INSERT INTO runtime VALUES(10,1,'07:24:42.000','07:24:42.000',0)")
        # Der produktive Vergleich ActualExecutions <> ExpectedExecutions lehnt 4 statt 3 ab.
        self.assertEqual(self.phase_counts(INSTALL), [(10, 4)])
        self.assertIn("IF @ActualExecutions <> @ExpectedExecutions", INSTALL.read_text(encoding="utf-8"))

    def test_validation_rejects_an_interval_outside_the_phase(self) -> None:
        text = VALIDATE.read_text(encoding="utf-8")
        predicate = re.search(r"OR (i\.end_time [^\n]+)", text)
        self.assertIsNotNone(predicate)
        rejected = self.connection.execute(
            f"SELECT i.runtime_stats_interval_id FROM interval_bounds i CROSS JOIN phase s WHERE {predicate.group(1)}"
        ).fetchall()
        self.assertEqual(rejected, [(11,), (12,)])

    def test_shared_interval_is_rejected_but_adjacent_intervals_are_allowed(self) -> None:
        text = INSTALL.read_text(encoding="utf-8")
        predicate = re.search(r"AND (bi\.end_time > ti\.start_time)", text)
        self.assertIsNotNone(predicate)
        for incident_interval, expected in ((10, 1), (11, 0)):
            with self.subTest(incident_interval=incident_interval):
                overlap = self.connection.execute(
                    f"SELECT COUNT(*) FROM interval_bounds bi CROSS JOIN interval_bounds ti WHERE {predicate.group(1)} "
                    "AND bi.runtime_stats_interval_id=10 AND ti.runtime_stats_interval_id=?", (incident_interval,)
                ).fetchone()[0]
                self.assertEqual(overlap, expected)


if __name__ == "__main__":
    unittest.main()
