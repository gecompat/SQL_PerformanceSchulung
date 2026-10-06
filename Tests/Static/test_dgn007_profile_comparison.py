#!/usr/bin/env python3
"""Führt extrahierte Profilaggregate und Guard-Prädikate auf SQLite-Fixtures aus.

Nur Quellenbezeichner, COUNT_BIG und temporäre Tabellennamen werden für SQLite
angepasst. Gewichtung, Delta, Ratio, Scope- und Intervallprädikate stammen aus
dem tatsächlich ausgeführten SQL; kein SQL-Server- oder Incidentnachweis.
"""
from __future__ import annotations

import re
import sqlite3
import unittest

from validate_dgn007_profile_comparison import SQL, section, sql_findings


def portable(sql: str) -> str:
    sql = re.sub(r"\bN'", "'", sql)
    sql = re.sub(r"\bCOUNT_BIG\b", "COUNT", sql)
    return re.sub(r"#([A-Za-z][A-Za-z0-9_]*)", r"\1", sql)


def predicate(sql: str, name: str) -> str:
    match = re.fullmatch(r"IF\s+(.*?)\s+BEGIN\s+PRINT 'SQLPERF_SUMMARY\|FAIL\|FAIL_RESULT_CONTRACT';\s+RETURN;\s+END;",
                         section(sql, name), re.DOTALL)
    if match is None:
        raise AssertionError("SQL-Guard besitzt keinen extrahierbaren FAIL_RESULT_CONTRACT/RETURN-Vertrag")
    return portable(match[1])


class ProfileComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sql = SQL.read_text(encoding="utf-8")
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.executescript("""
            ATTACH DATABASE ':memory:' AS lab;
            ATTACH DATABASE ':memory:' AS dbo;
            ATTACH DATABASE ':memory:' AS sys;
            CREATE TABLE lab.IncidentState(WindowId INT, RuntimeStatsIntervalId INT, IntervalStart TEXT, IntervalEnd TEXT,
                ExecutionStarted TEXT, ExecutionFinished TEXT, FirstRequestLogId INT, LastRequestLogId INT,
                RequestCount INT, CapturedExecutions INT);
            INSERT INTO lab.IncidentState VALUES
                (0,10,'00:00:00','00:01:00','00:00:10','00:00:20',5,8,4,4),
                (1,11,'00:01:00','00:02:00','00:01:10','00:01:20',9,12,4,4);
            CREATE TABLE sys.query_store_runtime_stats_interval(runtime_stats_interval_id INT,start_time TEXT,end_time TEXT);
            INSERT INTO sys.query_store_runtime_stats_interval VALUES(10,'00:00:00','00:01:00'),(11,'00:01:00','00:02:00');
            CREATE TABLE dbo.CaseRequestLog(RequestLogId INT,GroupKey INT,StatusCode INT);
            INSERT INTO dbo.CaseRequestLog VALUES
                (1,8,3),(2,1,3),(3,5,3),(4,1,1),
                (5,8,3),(6,1,3),(7,5,3),(8,1,1),
                (9,1,3),(10,8,3),(11,5,3),(12,1,1);
            CREATE TABLE ExpectedParameters(GroupKey INT,StatusCode INT);
            INSERT INTO ExpectedParameters VALUES(8,3),(1,3),(5,3),(1,1);
            CREATE TABLE ScopedQueries(QueryId INT,ParentQueryId INT);
            INSERT INTO ScopedQueries VALUES(100,100);
            CREATE TABLE sys.query_store_plan(plan_id INT,query_id INT);
            INSERT INTO sys.query_store_plan VALUES(10,100),(11,100);
            CREATE TABLE lab.IncidentProfile(WindowId INT,ParentQueryId INT,QueryId INT,PlanId INT,
                RuntimeStatsIntervalId INT,ExecutionType INT,ExecutionCount INT,AvgDurationUs REAL,AvgCpuUs REAL,
                AvgLogicalReads REAL,AvgRowCount REAL,FirstExecutionTime TEXT,LastExecutionTime TEXT);
            INSERT INTO lab.IncidentProfile VALUES
                (0,100,100,10,10,0,1,100.0,20.0,5.0,2286.0,'00:00:10','00:00:10'),
                (0,100,100,11,10,0,3,300.0,60.0,9.0,1943.0/3,'00:00:11','00:00:20'),
                (1,100,100,10,11,0,2,200.0,40.0,8.0,1257.0,'00:01:10','00:01:11'),
                (1,100,100,11,11,0,2,400.0,80.0,12.0,857.5,'00:01:12','00:01:20');
        """)

    def rejected(self, name: str) -> bool:
        return bool(self.connection.execute("SELECT CASE WHEN " + predicate(self.sql, name) + " THEN 1 ELSE 0 END").fetchone()[0])

    def totals(self) -> list[tuple]:
        weighted = portable(section(self.sql, "WEIGHTED"))
        weighted = re.sub(r"\bINTO WindowTotals\s*", "", weighted)
        self.connection.execute("DROP TABLE IF EXISTS WindowTotals")
        self.connection.execute("CREATE TABLE WindowTotals AS " + weighted)
        return self.connection.execute("SELECT * FROM WindowTotals ORDER BY WindowId").fetchall()

    def metrics(self) -> dict[str, tuple]:
        self.totals()
        result = self.connection.execute(portable(section(self.sql, "DELTA"))).fetchall()
        return {row[1]: row[2:] for row in result}

    def test_multiple_plans_use_execution_weights_and_report_neutral_deltas(self) -> None:
        for name in ("WINDOW_GUARD", "REQUEST_GUARD", "METRIC_GUARD"):
            self.assertFalse(self.rejected(name))
        t0, t1 = self.totals()
        self.assertEqual(t0[:3], (0, 4, 2))
        self.assertEqual(t1[:3], (1, 4, 2))
        for actual, expected in zip(t0[3:], (250, 50, 8, 1057.25, 4229)):
            self.assertAlmostEqual(actual, expected)
        self.assertFalse(self.rejected("TOTALS_GUARD"))
        expected_metrics = {"DurationUs": (250, 300, 50, 1.2, 0), "CpuUs": (50, 60, 10, 1.2, 0),
                            "LogicalReads": (8, 10, 2, 1.25, 0), "Rows": (1057.25, 1057.25, 0, 1, 0)}
        self.assertEqual(self.metrics(), expected_metrics)

    def test_zero_baseline_is_valid_and_ratio_is_null(self) -> None:
        self.connection.execute("UPDATE lab.IncidentProfile SET AvgDurationUs=0,AvgCpuUs=0,AvgLogicalReads=0 WHERE WindowId=0")
        self.assertFalse(self.rejected("METRIC_GUARD"))
        metrics = self.metrics()
        for name, t1 in (("DurationUs", 300), ("CpuUs", 60), ("LogicalReads", 10)):
            self.assertEqual(metrics[name], (0, t1, t1, None, 1))
        self.assertFalse(self.rejected("TOTALS_GUARD"))

    def test_lower_and_equal_t1_metrics_remain_neutral_valid_comparisons(self) -> None:
        cases = (
            ("UPDATE lab.IncidentProfile SET AvgDurationUs=AvgDurationUs/2,AvgCpuUs=AvgCpuUs/2,"
             "AvgLogicalReads=AvgLogicalReads/2 WHERE WindowId=1",
             {"DurationUs": (250, 150, -100, 0.6, 0), "CpuUs": (50, 30, -20, 0.6, 0),
              "LogicalReads": (8, 5, -3, 0.625, 0)}),
            ("UPDATE lab.IncidentProfile SET AvgDurationUs=250,AvgCpuUs=50,AvgLogicalReads=8 WHERE WindowId=1",
             {"DurationUs": (250, 250, 0, 1, 0), "CpuUs": (50, 50, 0, 1, 0),
              "LogicalReads": (8, 8, 0, 1, 0)}),
        )
        for mutation, expected in cases:
            with self.subTest(mutation=mutation):
                self.connection.execute("SAVEPOINT fixture")
                self.connection.execute(mutation)
                for name in ("WINDOW_GUARD", "REQUEST_GUARD", "METRIC_GUARD"):
                    self.assertFalse(self.rejected(name))
                actual = self.metrics()
                self.assertEqual({name: actual[name] for name in expected}, expected)
                self.assertFalse(self.rejected("TOTALS_GUARD"))
                self.connection.execute("ROLLBACK TO fixture")
                self.connection.execute("RELEASE fixture")

    def test_one_observed_plan_requires_no_incident_or_plan_diversity_gate(self) -> None:
        self.connection.execute("DELETE FROM lab.IncidentProfile")
        self.connection.executescript("""
            INSERT INTO lab.IncidentProfile VALUES
                (0,100,100,10,10,0,4,250,50,8,1057.25,'00:00:10','00:00:20'),
                (1,100,100,10,11,0,4,300,60,10,1057.25,'00:01:10','00:01:20');
        """)
        self.assertFalse(self.rejected("METRIC_GUARD"))
        self.assertEqual([row[2] for row in self.totals()], [1, 1])
        self.assertFalse(self.rejected("TOTALS_GUARD"))

    def test_null_and_negative_metrics_fail_closed(self) -> None:
        for column in ("AvgDurationUs", "AvgCpuUs", "AvgLogicalReads", "AvgRowCount"):
            for value in (None, -1):
                with self.subTest(column=column, value=value):
                    self.connection.execute("SAVEPOINT fixture")
                    self.connection.execute(f"UPDATE lab.IncidentProfile SET {column}=? WHERE WindowId=0 AND PlanId=10", (value,))
                    self.assertTrue(self.rejected("METRIC_GUARD"))
                    self.connection.execute("ROLLBACK TO fixture")
                    self.connection.execute("RELEASE fixture")

    def test_extra_or_missing_executions_and_duplicate_profiles_are_rejected(self) -> None:
        for mutation in ("UPDATE lab.IncidentProfile SET ExecutionCount=2 WHERE WindowId=0 AND PlanId=10",
                         "DELETE FROM lab.IncidentProfile WHERE WindowId=0",
                         "INSERT INTO lab.IncidentProfile SELECT * FROM lab.IncidentProfile WHERE WindowId=0 AND PlanId=10",
                         "UPDATE lab.IncidentProfile SET ExecutionCount=NULL WHERE WindowId=0 AND PlanId=10"):
            with self.subTest(mutation=mutation):
                self.connection.execute("SAVEPOINT fixture")
                self.connection.execute(mutation)
                self.assertTrue(self.rejected("METRIC_GUARD"))
                self.connection.execute("ROLLBACK TO fixture")
                self.connection.execute("RELEASE fixture")

    def test_foreign_query_wrong_plan_interval_and_parent_cannot_enter_profile(self) -> None:
        for column, value in (("QueryId", 999), ("ParentQueryId", 999), ("PlanId", 999),
                              ("RuntimeStatsIntervalId", 11), ("ExecutionType", 3)):
            with self.subTest(column=column):
                self.connection.execute("SAVEPOINT fixture")
                self.connection.execute(f"UPDATE lab.IncidentProfile SET {column}=? WHERE WindowId=0", (value,))
                self.assertTrue(self.rejected("METRIC_GUARD"))
                self.connection.execute("ROLLBACK TO fixture")
                self.connection.execute("RELEASE fixture")

    def test_overlap_and_missing_window_metadata_are_rejected(self) -> None:
        for mutation in ("UPDATE lab.IncidentState SET IntervalStart='00:00:59' WHERE WindowId=1",
                         "UPDATE lab.IncidentState SET IntervalEnd=NULL WHERE WindowId=1",
                         "UPDATE lab.IncidentState SET LastRequestLogId=9 WHERE WindowId=0",
                         "UPDATE lab.IncidentState SET CapturedExecutions=NULL WHERE WindowId=0"):
            with self.subTest(mutation=mutation):
                self.connection.execute("SAVEPOINT fixture")
                self.connection.execute(mutation)
                self.assertTrue(self.rejected("WINDOW_GUARD"))
                self.connection.execute("ROLLBACK TO fixture")
                self.connection.execute("RELEASE fixture")

    def test_equal_parameter_pairs_and_exact_rows_are_required(self) -> None:
        self.connection.execute("UPDATE dbo.CaseRequestLog SET GroupKey=8 WHERE RequestLogId=9")
        self.assertTrue(self.rejected("REQUEST_GUARD"))
        self.connection.execute("UPDATE lab.IncidentProfile SET AvgRowCount=AvgRowCount+1 WHERE WindowId=0")
        self.totals()
        self.assertTrue(self.rejected("TOTALS_GUARD"))

    def test_removed_metric_null_guard_or_deadline_cannot_validate(self) -> None:
        for old, replacement in (("p.AvgDurationUs IS NULL OR ", ""),
                                 ("IF SYSUTCDATETIME()>=@PhaseDeadline", "IF 1=0"),
                                 ("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;", "PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT';")):
            with self.subTest(mutation=old):
                mutated = self.sql.replace(old, replacement, 1)
                self.assertNotEqual(mutated, self.sql)
                self.assertTrue(sql_findings(mutated))


if __name__ == "__main__":
    unittest.main()
