#!/usr/bin/env python3
"""Extrahierte Kontroll-SQL-Reihenfolgen und aktive Planmengen auf SQLite-Fixtures.

Die Syntaxadaption betrifft Tabellenbezeichner, VALUES-Alias und Hexformatierung.
Prädikate, ROW_NUMBER, Counts, positive reguläre Planbasis und Mengenunion stammen
aus den SQL-Dateien. Dies ist kein Query-Store-Runtime- oder Incidentnachweis.
"""
from __future__ import annotations

import re
import sqlite3
import unittest

import test_dgn007_profile_comparison as profile_fixture
from validate_dgn007_capture_projection import canonical_guard_diagnostics

portable = profile_fixture.portable
from validate_dgn007_control_capture import (
    AUTO, WINDOWS, EVIDENCE, BASE_WINDOWS, section, config_findings,
    window_sql_findings, evidence_sql_findings,
)


def predicate(sql: str, name: str) -> str:
    block = section(canonical_guard_diagnostics(sql), name)
    if name == "SEQUENCE_GUARD":
        block = block[block.index("IF (SELECT COUNT_BIG(*)"):]
    match = re.fullmatch(r"IF\s+(.*?)\s+BEGIN\s+PRINT 'SQLPERF_SUMMARY\|FAIL\|FAIL_RESULT_CONTRACT';\s+RETURN;\s+END;",
                         block, re.DOTALL)
    if match is None:
        raise AssertionError("Kontrollguard muss FAIL_RESULT_CONTRACT unmittelbar zurückgeben")
    return portable(match[1])


def select_into(sql: str, table: str) -> str:
    return "CREATE TABLE " + table + " AS " + re.sub(r"\bINTO " + table + r"\s*", "", portable(sql))


class ControlCaptureTests(unittest.TestCase):
    def test_interval_selection_requires_observed_regular_pulse_capture(self):
        # Prädikat aus beiden tatsächlichen SQL-Dateien, keine Sollkopie.
        for path in (BASE_WINDOWS, WINDOWS):
            sql=path.read_text(encoding='utf-8')
            queries=re.findall(r'AND runtime_stats_interval_id IN \((.*?)\)\s*ORDER BY start_time',sql,re.S)
            self.assertEqual(len(queries),2)
            for query in queries:
                query=re.sub(r"\bN'", "'", query)
                query=re.sub(r"CHARINDEX\(N?'([^']+)',t.query_sql_text COLLATE Latin1_General_100_BIN2\)",r"instr(t.query_sql_text,'\1')",query)
                query=query.replace('COLLATE Latin1_General_100_BIN2','')
                # Nur der erfasste reguläre markierte Pollquery darf das
                # neue Intervall freigeben; leerer Katalogeintrag reicht nicht.
                connection=sqlite3.connect(':memory:')
                self.addCleanup(connection.close)
                connection.executescript("""
                    ATTACH DATABASE ':memory:' AS sys;
                    CREATE TABLE sys.query_store_runtime_stats(plan_id INT,runtime_stats_interval_id INT,execution_type INT,count_executions INT);
                    CREATE TABLE sys.query_store_plan(plan_id INT,query_id INT);
                    CREATE TABLE sys.query_store_query(query_id INT,object_id INT,query_text_id INT);
                    CREATE TABLE sys.query_store_query_text(query_text_id INT,query_sql_text TEXT);
                    INSERT INTO sys.query_store_plan VALUES(1,1);
                    INSERT INTO sys.query_store_query VALUES(1,0,1);
                    INSERT INTO sys.query_store_query_text VALUES(1,'SELECT /* DGN007_INTERVAL_PULSE */ @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;');
                """)
                self.assertEqual(connection.execute(query).fetchall(),[])
                for execution_type,count,expected in ((0,0,[]),(3,1,[]),(0,1,[(11,)])):
                    connection.execute('DELETE FROM sys.query_store_runtime_stats')
                    connection.execute('INSERT INTO sys.query_store_runtime_stats VALUES(1,11,?,?)',(execution_type,count))
                    self.assertEqual(connection.execute(query).fetchall(),expected)
                connection.execute("UPDATE sys.query_store_query_text SET query_sql_text='SELECT 1'")
                self.assertEqual(connection.execute(query).fetchall(),[])
                # Der Katalogreader enthält den Marker als Suchliteral,
                # ist jedoch nicht der feste Pollquery selbst.
                connection.execute("UPDATE sys.query_store_query_text SET query_sql_text=?",('SELECT 1 FROM sys.query_store_query_text WHERE '+queries[0],))
                self.assertEqual(connection.execute(query).fetchall(),[])

    def setUp(self) -> None:
        # Gemeinsame synthetische Tabellenbasis; keine Vererbung ihrer Testmethoden.
        self.fixture = profile_fixture.ProfileComparisonTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.connection = self.fixture.connection
        self.connection.create_collation("Latin1_General_100_BIN2", lambda a, b: (a > b) - (a < b))
        self.connection.create_function("DATALENGTH", 1, lambda value: None if value is None else len(value))
        self.connection.create_function("HASH_HEX", 1, lambda value: None if value is None else "0x" + value.hex().upper())
        self.connection.executescript("""
            CREATE TABLE lab.ControlSequence(WindowId INT,ConditionCode TEXT);
            INSERT INTO lab.ControlSequence VALUES(0,'A'),(1,'B');
            ALTER TABLE sys.query_store_plan ADD COLUMN query_plan_hash BLOB;
            ALTER TABLE sys.query_store_plan ADD COLUMN plan_type INT;
            UPDATE sys.query_store_plan SET query_plan_hash=x'0123456789abcdef',plan_type=0;
        """)
        self.sql = EVIDENCE.read_text(encoding="utf-8")
        self.windows = WINDOWS.read_text(encoding="utf-8")

    def rejected(self, name: str) -> bool:
        return bool(self.connection.execute("SELECT CASE WHEN " + predicate(self.sql, name) + " THEN 1 ELSE 0 END").fetchone()[0])

    def parameters(self) -> list[tuple]:
        block = portable(section(self.sql, "PARAMETERS"))
        ddl, insert = block.split("INSERT Parameters", 1)
        alias = re.search(r"\(VALUES(.*?)\)\s+p\((.*?)\) ON p.ConditionCode=c.ConditionCode;", insert, re.DOTALL)
        self.assertIsNotNone(alias)
        cte = "WITH p(" + alias[2] + ") AS (VALUES" + alias[1] + ") "
        insert = insert[:alias.start()] + "p ON p.ConditionCode=c.ConditionCode;"
        self.connection.execute("DROP TABLE IF EXISTS Parameters")
        self.connection.execute(ddl)
        self.connection.execute(cte + "INSERT INTO Parameters" + insert)
        return self.connection.execute("SELECT * FROM Parameters ORDER BY WindowId,Sequence").fetchall()

    def ordered(self) -> None:
        self.connection.execute("DROP TABLE IF EXISTS OrderedRequests")
        self.connection.execute(select_into(section(self.sql, "ORDER_ROWS"), "OrderedRequests"))

    def executed(self) -> list[tuple]:
        self.connection.execute("DROP TABLE IF EXISTS ExecutedPlans")
        self.connection.execute(select_into(section(self.sql, "ACTIVE_PLANS"), "ExecutedPlans"))
        return self.connection.execute("SELECT * FROM ExecutedPlans ORDER BY WindowId,PlanId").fetchall()

    def union(self) -> list[tuple]:
        sql = portable(section(self.sql, "PLAN_UNION"))
        sql = sql.replace("CONVERT(varchar(18),QueryPlanHash,1)", "HASH_HEX(QueryPlanHash)")
        return self.connection.execute(sql).fetchall()

    def one_plan_per_window(self, different: bool = False) -> None:
        self.connection.execute("DELETE FROM lab.IncidentProfile")
        self.connection.executescript("""
            INSERT INTO lab.IncidentProfile VALUES
             (0,100,100,10,10,0,4,250,50,8,1057.25,'00:00:10','00:00:20'),
             (1,100,100,10,11,0,4,250,50,8,1057.25,'00:01:10','00:01:20');
        """)
        if different:
            self.connection.execute("UPDATE lab.IncidentProfile SET PlanId=11 WHERE WindowId=1")

    def test_all_three_actual_configs_and_parameters_preserve_four_pairs_in_order(self) -> None:
        expected = {'A': [(8,3,228),(1,3,2286),(5,3,1144),(1,1,571)],
                    'B': [(1,3,2286),(8,3,228),(5,3,1144),(1,1,571)]}
        for order in ("AB", "BA", "AA"):
            with self.subTest(order=order):
                self.connection.execute("DROP TABLE lab.ControlSequence")
                config = (AUTO / f"15_Control_{order}.sql").read_text(encoding="utf-8")
                self.assertEqual(config_findings(config, order), [])
                block = portable(section(config, "CONFIG")).replace("INSERT lab.", "INSERT INTO lab.")
                self.connection.executescript(block)
                self.assertFalse(self.rejected("SEQUENCE_GUARD"))
                rows = self.parameters()
                self.assertEqual(rows, [(window, position, *pair) for window, condition in enumerate(order)
                                        for position, pair in enumerate(expected[condition], 1)])
                # Fixture setzt die ausdrücklich vorgegebene Folge, nicht den SQL-Ausgabewert.
                for window, condition in enumerate(order):
                    for position, pair in enumerate(expected[condition], 1):
                        self.connection.execute("UPDATE dbo.CaseRequestLog SET GroupKey=?,StatusCode=? WHERE RequestLogId=?",
                                                (*pair[:2], 5 + window*4 + position-1))
                self.ordered()
                self.assertFalse(self.rejected("ORDER_GUARD"))
                self.assertFalse(self.rejected("REQUEST_GUARD"))

    def test_same_pair_set_with_wrong_actual_order_fails(self) -> None:
        self.parameters()
        self.connection.executescript("UPDATE dbo.CaseRequestLog SET GroupKey=1 WHERE RequestLogId=5; UPDATE dbo.CaseRequestLog SET GroupKey=8 WHERE RequestLogId=6;")
        self.assertFalse(self.rejected("REQUEST_GUARD"))
        self.ordered()
        self.assertTrue(self.rejected("ORDER_GUARD"))

    def test_missing_extra_or_duplicate_request_is_not_an_order_capture(self) -> None:
        self.parameters()
        for mutation in ("DELETE FROM dbo.CaseRequestLog WHERE RequestLogId=5",
                         "INSERT INTO dbo.CaseRequestLog VALUES(5,8,3)",
                         "UPDATE dbo.CaseRequestLog SET GroupKey=1 WHERE RequestLogId=5"):
            with self.subTest(mutation=mutation):
                self.connection.execute("SAVEPOINT fixture")
                self.connection.execute(mutation)
                self.ordered()
                self.assertTrue(self.rejected("ORDER_GUARD"))
                self.assertTrue(self.rejected("REQUEST_GUARD"))
                self.connection.execute("ROLLBACK TO fixture")
                self.connection.execute("RELEASE fixture")

    def test_null_unknown_lowercase_bb_missing_or_extra_condition_fails(self) -> None:
        mutations = ("UPDATE lab.ControlSequence SET ConditionCode=NULL WHERE WindowId=0",
                     "UPDATE lab.ControlSequence SET ConditionCode='C' WHERE WindowId=0",
                     "UPDATE lab.ControlSequence SET ConditionCode='a' WHERE WindowId=0",
                     "UPDATE lab.ControlSequence SET ConditionCode='AA' WHERE WindowId=0",
                     "UPDATE lab.ControlSequence SET ConditionCode='B' WHERE WindowId=0",
                     "UPDATE lab.ControlSequence SET WindowId=NULL WHERE WindowId=0",
                     "DELETE FROM lab.ControlSequence WHERE WindowId=1",
                     "INSERT INTO lab.ControlSequence VALUES(2,'A')")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.connection.execute("SAVEPOINT fixture")
                self.connection.execute(mutation)
                self.assertTrue(self.rejected("SEQUENCE_GUARD"))
                self.connection.execute("ROLLBACK TO fixture")
                self.connection.execute("RELEASE fixture")

    def test_one_plan_in_both_windows_is_valid_with_neutral_union(self) -> None:
        self.one_plan_per_window()
        for name in ("WINDOW_GUARD", "REQUEST_GUARD", "METRIC_GUARD", "HASH_GUARD"):
            self.assertFalse(self.rejected(name))
        self.assertEqual([row[-1] for row in self.executed()], [4, 4])
        self.assertEqual(self.union(), [('DGN007_CONTROL_PLAN_UNION',100,100,10,'0x0123456789ABCDEF',1,1)])
        rows = self.connection.execute(portable(section(self.sql, "SEQUENCE_REPORT"))).fetchall()
        self.assertEqual([row[-1] for row in rows], [1, 1])

    def test_distinct_plan_ids_remain_visible_even_with_same_hash_and_count_one_each(self) -> None:
        self.one_plan_per_window(different=True)
        self.assertFalse(self.rejected("METRIC_GUARD"))
        self.executed()
        self.assertEqual([(row[3], row[-2:]) for row in self.union()], [(10,(1,0)),(11,(0,1))])
        rows = self.connection.execute(portable(section(self.sql, "SEQUENCE_REPORT"))).fetchall()
        self.assertEqual([row[-1] for row in rows], [1,1])

    def test_unused_historical_dispatcher_and_nonregular_or_zero_profiles_are_excluded(self) -> None:
        self.one_plan_per_window()
        self.connection.executescript("""
            INSERT INTO sys.query_store_plan VALUES(90,100,x'fedcba9876543210',1),(91,100,x'fedcba9876543210',0);
            INSERT INTO lab.IncidentProfile SELECT WindowId,ParentQueryId,QueryId,90,RuntimeStatsIntervalId,
                3,4,AvgDurationUs,AvgCpuUs,AvgLogicalReads,AvgRowCount,FirstExecutionTime,LastExecutionTime
                FROM lab.IncidentProfile WHERE WindowId=0;
            INSERT INTO lab.IncidentProfile SELECT WindowId,ParentQueryId,QueryId,91,RuntimeStatsIntervalId,
                0,0,AvgDurationUs,AvgCpuUs,AvgLogicalReads,AvgRowCount,FirstExecutionTime,LastExecutionTime
                FROM lab.IncidentProfile WHERE WindowId=0;
        """)
        self.assertEqual([row[3] for row in self.executed()], [10,10])
        # Ungültige Capture-Zeilen dürfen trotz Mengenfilter kein PASS erzeugen.
        self.assertTrue(self.rejected("METRIC_GUARD"))

    def test_dispatcher_unknown_and_null_plan_type_fail_only_when_actually_executed(self) -> None:
        self.one_plan_per_window()
        self.executed()
        query = re.search(r"IF EXISTS\((SELECT 1 FROM #ExecutedPlans.*?p.plan_type NOT IN \(0,2\))\)\s+SET @Invalid=1;",
                          self.sql, re.DOTALL)[1]
        for value, expected in ((0,False),(2,False),(1,True),(3,True),(None,True)):
            with self.subTest(value=value):
                self.connection.execute("UPDATE sys.query_store_plan SET plan_type=? WHERE plan_id=10", (value,))
                self.assertEqual(bool(self.connection.execute("SELECT EXISTS(" + portable(query) + ")").fetchone()[0]), expected)

    def test_null_or_wrong_hash_length_and_foreign_query_fail_closed(self) -> None:
        for value in (None, b'', b'1234567', b'123456789'):
            self.connection.execute("UPDATE sys.query_store_plan SET query_plan_hash=? WHERE plan_id=10", (value,))
            self.assertTrue(self.rejected("HASH_GUARD"))
        self.connection.execute("UPDATE lab.IncidentProfile SET QueryId=999 WHERE PlanId=10")
        self.assertTrue(self.rejected("METRIC_GUARD"))
        self.assertNotIn(10, [row[3] for row in self.executed()])

    def test_window_capture_budgets_and_entire_existing_safety_remain_reused(self) -> None:
        self.assertEqual(window_sql_findings(self.windows), [])
        for old, new in (("@Pulse IS NULL OR @Pulse<>12", "@Pulse<>12"),
                         ("IF SYSUTCDATETIME()>=@PollDeadline", "IF 1=0"),
                         ("ConditionCode IS NULL OR", ""),
                         ("ON p.ConditionCode=c.ConditionCode", "ON 1=1"),
                         ("('B',1,1,3,2286)", "('B',1,8,3,228)")):
            mutated = self.windows.replace(old, new, 1)
            self.assertNotEqual(mutated, self.windows)
            self.assertTrue(window_sql_findings(mutated), old)

    def test_evidence_guard_order_scope_hash_union_and_deadline_mutations_are_detected(self) -> None:
        self.assertEqual(evidence_sql_findings(self.sql), [])
        for old, new in (("ConditionCode IS NULL OR", ""), ("q.query_plan_hash IS NULL OR", ""),
                         ("ORDER BY r.RequestLogId", "ORDER BY r.RequestLogId DESC"),
                         ("WHERE p.ExecutionType=0 AND p.ExecutionCount>0", "WHERE p.ExecutionCount>=0"),
                         ("AND q.query_id=p.QueryId", ""), ("MAX(CASE WHEN WindowId=1", "MAX(CASE WHEN WindowId=0"),
                         ("IF SYSUTCDATETIME()>=@PhaseDeadline", "IF 1=0"),
                         ("@Invalid=@InvalidPlanType OUTPUT", "@Invalid=@InvalidPlanType"),
                         ("CapturedExecutions IS NULL OR CapturedExecutions<>4", "CapturedExecutions<>4")):
            mutated = self.sql.replace(old, new, 1)
            self.assertNotEqual(mutated, self.sql)
            self.assertTrue(evidence_sql_findings(mutated), old)
        self.assertTrue(evidence_sql_findings(self.sql + "\nIF ExecutedPlanCount<2 THROW 51002,'FAIL_INCIDENT',1;"))
        for leak in ("SELECT query_sql_text FROM sys.query_store_query_text;",
                     "SELECT query_plan FROM sys.query_store_plan;", "SELECT * FROM sys.query_store_plan;"):
            self.assertTrue(evidence_sql_findings(self.sql + "\n" + leak))

    def test_config_wrong_sequence_missing_marker_and_late_deadline_are_rejected(self) -> None:
        for order in ("AB", "BA", "AA"):
            sql = (AUTO / f"15_Control_{order}.sql").read_text(encoding="utf-8")
            for old, new in ((f"VALUES(0,'{order[0]}'),(1,'{order[1]}')", "VALUES(0,'B'),(1,'B')"),
                             ("@Project IS NULL", "1=0"),
                             ("IF SYSUTCDATETIME()>=@PhaseDeadline", "IF 1=0"),
                             ("'$(ConfirmIsolatedLab)'<>'1'", "'$(ConfirmIsolatedLab)'='1'"),
                             ("CHECK(WindowId IN (0,1))", "CHECK(WindowId IN (0,1,2))")):
                mutation = sql.replace(old, new, 1)
                self.assertNotEqual(mutation, sql)
                self.assertTrue(config_findings(mutation, order), old)


if __name__ == "__main__":
    unittest.main()
