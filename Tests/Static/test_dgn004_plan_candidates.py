"""Synthetic tests for DGN-004 plan-cache snapshot parsing and delta binding."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
import hashlib
from pathlib import Path
import unittest

from dgn004_identity_snapshot import registered_text_views
from dgn004_plan_candidates import (
    CandidateSnapshot,
    CacheCandidate,
    PlanCandidateError,
    PlanCandidateInput,
    bind_unique_execution,
    parse_candidate_snapshot,
)


ROOT = Path(__file__).resolve().parents[2]
SQL_SOURCE = ROOT / "Tests" / "Fixtures" / "DGN004_SourcePair" / "SnapshotPlanCandidates.sql"
INPUT = PlanCandidateInput("dgn004-run-1", "R", 3, 73, 101)
CREATED = datetime(2026, 11, 13, 9, 0, 0, 0)
EXECUTED = datetime(2026, 11, 13, 10, 0, 0, 0)


def _registered_bytes(role: str = "R") -> bytes:
    return registered_text_views()[role].module_text.encode("utf-16le")


def _row_line(
    *,
    role: str = "R",
    plan_handle: str = "AA" * 64,
    sql_handle: str = "BB" * 64,
    database_id: int = 73,
    object_id: int = 101,
    start_offset: int | None = None,
    end_offset: int | None = None,
    generation: int = 1,
    created: str = "2026-11-13T09:00:00.000",
    last_execution: str = "2026-11-13T10:00:00.000",
    execution_count: int = 1,
    query_hash: str = "CC" * 8,
    plan_hash: str = "DD" * 8,
) -> str:
    views = registered_text_views()[role]
    if start_offset is None:
        start_offset = views.statement_start_offset
    if end_offset is None:
        end_offset = start_offset + views.statement_bytes - 2
    module = _registered_bytes(role)
    return "|".join((
        "DGN004_CACHE_ROW", plan_handle, sql_handle,
        str(database_id), str(object_id), str(start_offset), str(end_offset),
        str(generation), created, last_execution, str(execution_count),
        query_hash, plan_hash, str(len(module)), hashlib.sha256(module).hexdigest().upper(),
    ))


def _frame(rows: list[str], *, expected: PlanCandidateInput = INPUT, declared_count: int | None = None) -> str:
    module = _registered_bytes(expected.role)
    digest = hashlib.sha256(module).hexdigest().upper()
    count = len(rows) if declared_count is None else declared_count
    marker = f"{expected.run}|{expected.role}|{expected.call}|{count}|{len(module)}|{digest}"
    return "\r\n".join((f"DGN004_CACHE_START|{marker}", *rows, f"DGN004_CACHE_END|{marker}", ""))


def _snapshot(rows: tuple[CacheCandidate, ...]) -> CandidateSnapshot:
    module = _registered_bytes(INPUT.role)
    return CandidateSnapshot(
        INPUT.run, INPUT.role, INPUT.call, INPUT.database_id, INPUT.object_id,
        len(module), hashlib.sha256(module).digest(), rows,
    )


class Dgn004PlanCandidateTests(unittest.TestCase):
    def test_complete_empty_and_single_row_snapshots_parse(self) -> None:
        empty = parse_candidate_snapshot(_frame([]), expected=INPUT)
        self.assertEqual(empty.rows, ())
        one = parse_candidate_snapshot(_frame([_row_line()]), expected=INPUT)
        self.assertEqual(len(one.rows), 1)
        self.assertEqual(one.rows[0].plan_handle, bytes.fromhex("AA" * 64))

    def test_accepts_variable_length_binary_handles_without_zero_padding(self) -> None:
        handle = "06000100A27E7C1FA821B10600"
        row = parse_candidate_snapshot(
            _frame([_row_line(plan_handle=handle, sql_handle="1234567890ABCDEF")]),
            expected=INPUT,
        ).rows[0]
        self.assertEqual(row.plan_handle, bytes.fromhex(handle))
        self.assertEqual(row.sql_handle, bytes.fromhex("1234567890ABCDEF"))

    def test_frame_binds_invocation_module_database_object_and_statement_offsets(self) -> None:
        views = registered_text_views()[INPUT.role]
        bad_inputs = (
            replace(INPUT, run="other-run"),
            replace(INPUT, role="H"),
            replace(INPUT, call=4),
            replace(INPUT, database_id=74),
            replace(INPUT, object_id=102),
        )
        for expected in bad_inputs:
            with self.subTest(expected=expected), self.assertRaises(PlanCandidateError):
                parse_candidate_snapshot(_frame([_row_line()]), expected=expected)
        with self.assertRaisesRegex(PlanCandidateError, "registered module binding"):
            parse_candidate_snapshot(
                _frame([_row_line(start_offset=views.statement_start_offset + 2)]), expected=INPUT
            )

    def test_rejects_incomplete_or_malformed_snapshot_frames(self) -> None:
        valid = _frame([_row_line()])
        cases = (
            valid.replace("DGN004_CACHE_END", "DGN004_CACHE_START"),
            _frame([_row_line()], declared_count=2),
            _frame([_row_line().replace("AA" * 64, "AA" * 63 + "A")]),
            _frame([_row_line(query_hash="GG" * 8)]),
            _frame([_row_line(created="2026-14-13T09:00:00.000")]),
            valid.replace("\r\n", "\n").replace("DGN004_CACHE_ROW|", "DGN004_CACHE_ROW|Ω|", 1),
            valid + "\r\n\r\n",
        )
        for frame in cases:
            with self.subTest(frame=frame[:80]), self.assertRaises(PlanCandidateError):
                parse_candidate_snapshot(frame, expected=INPUT)

    def test_rejects_duplicate_composite_row_key(self) -> None:
        row = _row_line()
        with self.assertRaisesRegex(PlanCandidateError, "duplicate composite"):
            parse_candidate_snapshot(_frame([row, row]), expected=INPUT)

    def test_sql_enumerates_all_exact_cache_rows_without_arbitrary_first_match(self) -> None:
        source = SQL_SOURCE.read_text(encoding="ascii")
        self.assertIn("sys.dm_exec_query_stats AS qs", source)
        self.assertIn("CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st", source)
        self.assertIn("st.dbid = @DatabaseId", source)
        self.assertIn("st.objectid = @ObjectId", source)
        self.assertIn("CONVERT(varbinary(max), st.text) = @ExpectedModule", source)
        self.assertIn("qs.statement_start_offset = @StatementStartOffset", source)
        self.assertIn("COUNT_BIG(*)", source)
        self.assertIn("@CandidateCount > 4096", source)
        self.assertNotRegex(source, r"(?i)\bTOP\s*\(?")
        self.assertNotRegex(source, r"(?i)\bSELECT\s+DISTINCT\b")

    def test_binds_one_existing_row_with_exactly_one_execution_increment(self) -> None:
        before = parse_candidate_snapshot(
            _frame([_row_line(last_execution="2026-11-13T09:59:00.000", execution_count=4)]),
            expected=INPUT,
        )
        after = parse_candidate_snapshot(
            _frame([_row_line(last_execution="2026-11-13T10:00:00.000", execution_count=5)]),
            expected=INPUT,
        )
        result = bind_unique_execution(before, after)
        self.assertEqual(result.plan_handle_hex, "AA" * 64)

    def test_binds_one_newly_cached_plan_only_when_its_count_is_one(self) -> None:
        before = parse_candidate_snapshot(_frame([]), expected=INPUT)
        after = parse_candidate_snapshot(_frame([_row_line(execution_count=1)]), expected=INPUT)
        self.assertEqual(bind_unique_execution(before, after).plan_handle_hex, "AA" * 64)

    def test_rejects_zero_multiple_or_multi_execution_deltas(self) -> None:
        row_a = _row_line(plan_handle="AA" * 64, sql_handle="BB" * 64)
        row_b = _row_line(plan_handle="EE" * 64, sql_handle="FF" * 64)
        unchanged = parse_candidate_snapshot(_frame([row_a]), expected=INPUT)
        same = parse_candidate_snapshot(_frame([row_a]), expected=INPUT)
        with self.assertRaisesRegex(PlanCandidateError, "does not identify"):
            bind_unique_execution(unchanged, same)
        before = parse_candidate_snapshot(_frame([row_a, row_b]), expected=INPUT)
        after = parse_candidate_snapshot(
            _frame([
                _row_line(plan_handle="AA" * 64, sql_handle="BB" * 64, execution_count=2),
                _row_line(plan_handle="EE" * 64, sql_handle="FF" * 64, execution_count=2),
            ]), expected=INPUT,
        )
        with self.assertRaisesRegex(PlanCandidateError, "does not identify"):
            bind_unique_execution(before, after)
        too_many = parse_candidate_snapshot(
            _frame([_row_line(execution_count=3)]), expected=INPUT
        )
        with self.assertRaisesRegex(PlanCandidateError, "exact execution delta"):
            bind_unique_execution(unchanged, too_many)

    def test_rejects_eviction_and_unrelated_candidate_mutations(self) -> None:
        row_a = _row_line(plan_handle="AA" * 64, sql_handle="BB" * 64)
        row_b = _row_line(plan_handle="EE" * 64, sql_handle="FF" * 64)
        before = parse_candidate_snapshot(_frame([row_a, row_b]), expected=INPUT)
        after_missing = parse_candidate_snapshot(
            _frame([_row_line(plan_handle="AA" * 64, sql_handle="BB" * 64, execution_count=2)]),
            expected=INPUT,
        )
        with self.assertRaisesRegex(PlanCandidateError, "disappeared"):
            bind_unique_execution(before, after_missing)
        after_foreign_change = parse_candidate_snapshot(
            _frame([
                _row_line(plan_handle="AA" * 64, sql_handle="BB" * 64, execution_count=2),
                _row_line(plan_handle="EE" * 64, sql_handle="FF" * 64, execution_count=2,
                          plan_hash="AB" * 8),
            ]), expected=INPUT,
        )
        with self.assertRaisesRegex(PlanCandidateError, "changed outside"):
            bind_unique_execution(before, after_foreign_change)


if __name__ == "__main__":
    unittest.main()
