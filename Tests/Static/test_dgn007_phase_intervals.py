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
                (10,4,'07:24:43.500','07:24:43.560',0),
                (11,4,'07:25:01.000','07:25:01.100',0),
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
                self.assertEqual(self.phase_counts(path), [(10, 4)])

    def test_next_phase_excludes_prior_and_future_intervals(self) -> None:
        self.connection.execute("UPDATE phase SET MarkerUtc='07:25:00.000',CompletedUtc='07:25:01.098'")
        for path in (INSTALL, COMPARISON):
            with self.subTest(path=path.name):
                self.assertEqual(self.phase_counts(path), [(11, 4)])

    def test_multiple_rows_in_active_interval_are_aggregated(self) -> None:
        self.connection.execute("UPDATE runtime SET count_executions=2 WHERE runtime_stats_interval_id=10")
        self.connection.execute("INSERT INTO runtime VALUES(10,1,'07:24:43.560','07:24:43.560',0)")
        self.connection.execute("INSERT INTO runtime VALUES(10,1,'07:24:43.550','07:24:43.550',3)")
        self.assertEqual(self.phase_counts(INSTALL), [(10, 3)])

    def test_phase_crossing_interval_boundary_preserves_both_intervals(self) -> None:
        self.connection.execute("UPDATE phase SET CompletedUtc='07:25:01.098'")
        for path in (INSTALL, COMPARISON):
            with self.subTest(path=path.name):
                self.assertEqual(self.phase_counts(path), [(10, 4), (11, 4)])

    def test_extra_same_interval_execution_is_not_hidden_by_time_filter(self) -> None:
        self.connection.execute("INSERT INTO runtime VALUES(10,1,'07:24:42.000','07:24:42.000',0)")
        # Der produktive Vergleich ActualExecutions <> ExpectedExecutions lehnt 5 statt 4 ab.
        self.assertEqual(self.phase_counts(INSTALL), [(10, 5)])
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

    def test_adapter_uses_same_four_requests_in_opposite_order(self) -> None:
        text = INSTALL.read_text(encoding="utf-8")
        roster = re.search(r"INSERT @Requests VALUES(.*?);", text, re.S)
        self.assertIsNotNone(roster)
        self.assertEqual(
            tuple(tuple(map(int, row)) for row in re.findall(r"\((\d),(\d),(\d+),(\d+)\)", roster[1])),
            ((0, 1, 8, 3), (0, 2, 1, 3), (0, 3, 5, 3), (0, 4, 1, 1),
             (1, 1, 1, 3), (1, 2, 8, 3), (1, 3, 5, 3), (1, 4, 1, 1)),
        )
        self.assertIn("WHERE PhaseNumber=@PhaseNumber AND RequestOrdinal=@RequestOrdinal", text)
        self.assertIn("EXEC dbo.usp_CaseSearch @GroupKey,@StatusCode;", text)
        self.assertIn("SET @ExpectedExecutions = 4", text)
        self.assertIn("HAVING COALESCE(SUM(e.CountExecutions),0) <> 4", VALIDATE.read_text(encoding="utf-8"))

    def test_wait_reader_requires_the_full_adapter_request_roster(self) -> None:
        setup = INSTALL.read_text(encoding="utf-8")
        writer = re.search(r"INSERT @Requests VALUES(.*?);", setup, re.S)[1]
        observation = COMPARISON.with_name("40_Observation.sql").read_text(encoding="utf-8")
        reader = re.search(r"FROM \(VALUES (.*?)\)\s+AS expected", observation, re.S)[1]
        writer_rows = re.findall(r"\((\d),(\d),(\d+),(\d+)\)", writer)
        reader_rows = re.findall(r"\(N'(T[01]_(?:BASELINE|INCIDENT))',(\d),(\d+),(\d+)\)?", reader)
        self.assertEqual(
            [("T0_BASELINE" if phase == "0" else "T1_INCIDENT", ordinal, group, status)
             for phase, ordinal, group, status in writer_rows],
            reader_rows,
        )
        self.assertIn("=8", observation)
        self.assertIn("WAIT_EVIDENCE_MISSING", observation)
        self.assertIn("wait_type=N''RESOURCE_SEMAPHORE''", setup)
        self.assertIn("wait_type LIKE N''PAGEIOLATCH[_]%''", setup)
        self.assertLess(setup.index("DECLARE @WaitControlBefore"), setup.index("WHILE @PhaseNumber < 2"))

    def test_pair_uses_shared_qualified_capture_and_preserves_phase_order(self) -> None:
        install = INSTALL.read_text(encoding="utf-8")
        t2 = COMPARISON.read_text(encoding="utf-8")
        begin = install.index("INSERT lab.Dgn007T2CompileOwner")
        create = install.index("CREATE EVENT SESSION", begin)
        control = install.index("SELECT /* DGN007_COMPILE_CONTROL */", create)
        drop = install.index("DROP EVENT SESSION", control)
        record = install.index("INSERT lab.Dgn007CompileProfile", drop)
        self.assertEqual([begin, create, control, drop, record], sorted((begin, create, control, drop, record)))
        self.assertIn("CaptureSessionId=@@SPID AND IncidentPhase=@Phase", install)
        self.assertIn("@ControlSequence IS NOT NULL", install)
        self.assertIn("MIN(CompileCount)>=@RequiredPerRequest AND MAX(CompileCount)<=1", install)
        for source, phase_marker in (
            (install[install.index("WHILE @PhaseNumber < 2"):], "INSERT lab.IncidentState"),
            (t2, "SET @T2Marker=SYSUTCDATETIME()"),
        ):
            bound = [source.index(value) for value in (
                "EXEC lab.usp_BeginDgn007CompileCapture", phase_marker,
                "UPDATE lab.IncidentState SET CompletedUtc",
                "EXEC lab.usp_EndDgn007CompileCapture", "EXEC sys.sp_query_store_flush_db",
            )]
            self.assertEqual(bound, sorted(bound))
        self.assertIn("COMPILE_EVIDENCE_MISSING", t2)

    def test_t2_compares_parameters_in_the_same_order_as_t1(self) -> None:
        install = INSTALL.read_text(encoding="utf-8")
        t2 = COMPARISON.read_text(encoding="utf-8")
        baseline = re.search(r"INSERT @Requests VALUES(.*?);", install, re.S)[1]
        compared = re.search(r"INSERT #Parameters\(RequestOrdinal,GroupKey,StatusCode\) VALUES(.*?);", t2, re.S)[1]
        self.assertEqual(re.findall(r"\(1,(\d),(\d),(\d)\)", baseline),
                         re.findall(r"\((\d),(\d),(\d)\)", compared))
        self.assertIn("FROM #Parameters ORDER BY RequestOrdinal;", t2)

    def test_both_recovery_routes_use_only_the_recorded_t2_session_name(self) -> None:
        for path in (COMPARISON.with_name("90_Cleanup.sql"), INSTALL.with_name("cleanup.sql")):
            with self.subTest(path=path):
                source = path.read_text(encoding="utf-8")
                self.assertIn("lab.Dgn007T2CompileOwner", source)
                self.assertIn("DATALENGTH(@T2OwnedSession)<>(LEN(@T2Prefix)+32)*2", source)
                self.assertIn("LIKE N'%[^0-9a-f]%'", source)
                self.assertIn("DROP EVENT SESSION '+QUOTENAME(@T2OwnedSession)", source)
                self.assertIn("sys.dm_xe_sessions WHERE name=@T2OwnedSession", source)

    def test_observation_uses_phase_bound_profiles_without_minimum_plan_gate(self) -> None:
        observation = (ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/40_Observation.sql").read_text(encoding="utf-8")
        self.assertIn("FROM lab.IncidentQueryStoreProfile AS profile", observation)
        self.assertIn("profile.IncidentPhase IN(N'T0_BASELINE',N'T1_INCIDENT')", observation)
        self.assertIn("rs.execution_type=0", observation)
        self.assertIn("@ProfilePhaseCount<>2", observation)
        self.assertIn("@T0Executions<>4 OR @T1Executions<>4", observation)
        self.assertNotIn("IF @PlanCount<2", observation)
        profile_query = observation.split("SELECT @QueryId=MIN(profile.QueryId)", 1)[1].split(
            "SELECT @ParentQueryCount", 1
        )[0]
        self.assertNotIn("sys.query_store_plan", profile_query)


if __name__ == "__main__":
    unittest.main()
