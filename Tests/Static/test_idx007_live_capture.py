from __future__ import annotations

import inspect
import unittest
from unittest.mock import patch

from Tests.Runtime.idx007_hot_leaf_pilot import (PilotError, overlaps_capture_window,
                                                  page_metadata_sql, parse_chain_markers, parse_wait_pairs,
                                                  run_bounded_trials, run_live_pilot, wait_page_probe_sql)


DATABASE_ID = 7
BINDINGS = {51: 0, 52: 0}


def event(name: str, timestamp: str, sequence: int, session: int, page: int = 900,
          request: int = 0, *, success: str = "", duration: int = 0) -> str:
    return (f"XE_ROW|1|{name}|{timestamp}|{sequence}|{session}|{request}|7|1|{page}|"
            f"EX|BUF|{success}|{duration}")


def output(*rows: str, stats: str = "XE_STATS|1|0|0|4|0") -> str:
    return "\n".join((stats, *rows))


class LiveCaptureParserTests(unittest.TestCase):
    @patch("Tests.Runtime.idx007_hot_leaf_pilot.run_live_pilot", side_effect=[2, 0, 2])
    def test_bounded_trials_accept_one_complete_pass_and_keep_attempt_count(self, pilot) -> None:
        self.assertEqual(run_bounded_trials(15), 0)
        self.assertEqual(pilot.call_count, 3)

    @patch("Tests.Runtime.idx007_hot_leaf_pilot.run_live_pilot", side_effect=[2, 2, 2])
    def test_bounded_trials_fail_when_every_attempt_is_not_proven(self, pilot) -> None:
        self.assertEqual(run_bounded_trials(17), 2)
        self.assertEqual(pilot.call_count, 3)

    def test_bounded_trials_reject_unbounded_attempt_limits(self) -> None:
        with self.assertRaisesRegex(ValueError, "between one and three"):
            run_bounded_trials(15, attempts=4)

    def test_wait_page_probe_targets_only_observed_addresses(self) -> None:
        query = wait_page_probe_sql({(1, 360), (2, 489)}, 2)
        self.assertIn("WAIT_PAGE_PROBE|2|", query)
        self.assertIn("(1,360),(2,489)", query)
        self.assertIn("sys.dm_db_page_info(DB_ID(),a.FileId,a.PageId,'DETAILED')", query)
        with self.assertRaisesRegex(PilotError, "over its fixed cap"):
            wait_page_probe_sql({(1, page) for page in range(1, 130)}, 1)

    def test_actor_progress_does_not_write_during_measured_bursts(self) -> None:
        source = inspect.getsource(run_live_pilot)
        self.assertNotIn("UPDATE lab.ActorSessions", source)
        self.assertIn("COUNT_BIG(*)-501", source)

    def test_live_chain_capture_markers_bracket_leaf_scan(self) -> None:
        query = page_metadata_sql({(1, 489)}, 1, actor_count=56)
        self.assertLess(query.index("lab.Start WHERE Stage=1"), query.index("lab.ActorReady WHERE Stage=1"))
        self.assertLess(query.index("lab.ActorReady WHERE Stage=1"), query.index("IDX007_CHAIN_CAPTURE_BEGIN"))
        self.assertLess(query.index("IDX007_CHAIN_CAPTURE_BEGIN"), query.index("DECLARE @candidate"))
        self.assertLess(query.index("IDX007_CHAIN_CAPTURE_BEGIN"), query.index("INSERT lab.Go(Stage)"))
        self.assertLess(query.index("INSERT lab.Go(Stage)"), query.index("DECLARE @candidate"))
        self.assertLess(query.index("DECLARE @candidate"), query.index("IDX007_CHAIN_CAPTURE_END"))
        self.assertIn("WAITFOR DELAY '00:00:00.050'", query)
        self.assertIn("WAITFOR DELAY '00:00:00.001'", query)
        source = inspect.getsource(run_live_pilot)
        self.assertIn("INSERT lab.Start(Stage) VALUES({stage})", source)
        self.assertLess(source.index("INSERT lab.ActorReady(Stage,SessionId) VALUES(1,@spid)"),
                        source.index("WHILE @i<{ROWS_PER_BURST} BEGIN INSERT dbo.Hot DEFAULT VALUES"))
        self.assertEqual(inspect.getmodule(run_live_pilot).GATE_POLL_DELAY, "00:00:00.001")
        self.assertIn("LATCH_EVENT|stage=", source)
        self.assertIn("window_rows[:64]", source)
        self.assertIn("LATCH_EVENT_TRUNCATED|stage=", source)

    def test_shared_wait_interval_must_intersect_chain_capture(self) -> None:
        left = {"begin_seq": 2, "end_seq": 9}
        right = {"begin_seq": 4, "end_seq": 8}
        self.assertTrue(overlaps_capture_window(left, right, 5, 7))
        self.assertFalse(overlaps_capture_window(left, right, 9, 12))
        self.assertFalse(overlaps_capture_window(left, right, 3, 4))

    def test_chain_markers_define_ordered_capture_window(self) -> None:
        capture = "\n".join((
            "XE_MARK|1|sql_statement_starting|10|51|0|BEGIN",
            "XE_MARK|1|sql_statement_completed|20|51|0|END",
        ))
        self.assertEqual(parse_chain_markers(capture, 1), (10, 20))

    def test_missing_or_reversed_chain_markers_are_rejected(self) -> None:
        with self.assertRaisesRegex(PilotError, "missing, duplicated, or unordered"):
            parse_chain_markers("XE_MARK|1|sql_statement_starting|20|51|0|BEGIN\n"
                                "XE_MARK|1|sql_statement_completed|10|51|0|END", 1)
        with self.assertRaisesRegex(PilotError, "missing, duplicated, or unordered"):
            parse_chain_markers("XE_MARK|1|sql_statement_starting|10|51|0|BEGIN\n"
                                "XE_MARK|1|sql_statement_completed|20|52|0|END", 1)

    def test_overlapping_exclusive_wait_intervals_on_same_page_are_found(self) -> None:
        capture = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51),
            event("latch_suspend_begin", "2026-11-22T10:00:00.100Z", 2, 52),
            event("latch_suspend_end", "2026-11-22T10:00:00.250Z", 3, 51, success="1", duration=250000),
            event("latch_suspend_end", "2026-11-22T10:00:00.300Z", 4, 52, success="1", duration=200000),
        )
        _, pairs, overlaps = parse_wait_pairs(capture, 1, BINDINGS, DATABASE_ID)
        self.assertEqual(len(pairs), 2)
        self.assertEqual(len(overlaps), 1)

    def test_sequential_waits_do_not_count_as_overlap(self) -> None:
        capture = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51),
            event("latch_suspend_end", "2026-11-22T10:00:00.100Z", 2, 51, success="1", duration=100000),
            event("latch_suspend_begin", "2026-11-22T10:00:00.101Z", 3, 52),
            event("latch_suspend_end", "2026-11-22T10:00:00.200Z", 4, 52, success="1", duration=99000),
        )
        _, _, overlaps = parse_wait_pairs(capture, 1, BINDINGS, DATABASE_ID)
        self.assertEqual(overlaps, [])

    def test_event_sequence_finds_overlap_when_timestamps_are_equal(self) -> None:
        stamp = "2026-11-22T10:00:00.100Z"
        capture = output(
            event("latch_suspend_begin", stamp, 1, 51),
            event("latch_suspend_begin", stamp, 2, 52),
            event("latch_suspend_end", stamp, 3, 51, success="1", duration=1000),
            event("latch_suspend_end", stamp, 4, 52, success="1", duration=500),
        )
        _, _, overlaps = parse_wait_pairs(capture, 1, BINDINGS, DATABASE_ID)
        self.assertEqual(len(overlaps), 1)

    def test_non_page_latch_is_not_counted_as_page_contention(self) -> None:
        capture = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51).replace("BUF", "OTHER"),
            event("latch_suspend_end", "2026-11-22T10:00:00.100Z", 2, 51, success="1", duration=100000).replace("BUF", "OTHER"),
        )
        _, pairs, overlaps = parse_wait_pairs(capture, 1, BINDINGS, DATABASE_ID)
        self.assertEqual(pairs, [])
        self.assertEqual(overlaps, [])

    def test_incomplete_or_mismatched_actor_pairs_are_rejected(self) -> None:
        incomplete = output(event("latch_suspend_begin", "2026-11-22T10:00:00Z", 1, 51))
        with self.assertRaisesRegex(PilotError, "counts do not balance"):
            parse_wait_pairs(incomplete, 1, BINDINGS, DATABASE_ID)
        wrong_request = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51, request=4),
            event("latch_suspend_end", "2026-11-22T10:00:00.100Z", 2, 51, request=4, success="1", duration=100000),
        )
        with self.assertRaisesRegex(PilotError, "binding differs"):
            parse_wait_pairs(wrong_request, 1, BINDINGS, DATABASE_ID)

    def test_non_chronological_event_sequence_is_rejected(self) -> None:
        reversed_interval = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 2, 51),
            event("latch_suspend_end", "2026-11-22T10:00:00.100Z", 1, 51, success="1", duration=100000),
        )
        with self.assertRaisesRegex(PilotError, "not chronological by event sequence"):
            parse_wait_pairs(reversed_interval, 1, BINDINGS, DATABASE_ID)

    def test_duplicate_event_sequence_is_rejected(self) -> None:
        duplicated = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51),
            event("latch_suspend_end", "2026-11-22T10:00:00.100Z", 1, 51, success="1", duration=100000),
        )
        with self.assertRaisesRegex(PilotError, "duplicate values"):
            parse_wait_pairs(duplicated, 1, BINDINGS, DATABASE_ID)

    def test_event_order_proves_overlap_when_rounded_timestamps_do_not(self) -> None:
        rounded = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51),
            event("latch_suspend_begin", "2026-11-22T10:00:00.002Z", 2, 52),
            event("latch_suspend_end", "2026-11-22T10:00:00.003Z", 3, 51, success="1", duration=1000),
            event("latch_suspend_end", "2026-11-22T10:00:00.004Z", 4, 52, success="1", duration=1000),
        )
        _, _, overlaps = parse_wait_pairs(rounded, 1, BINDINGS, DATABASE_ID)
        self.assertEqual(len(overlaps), 1)

    def test_capture_loss_and_changed_resource_are_rejected(self) -> None:
        rows = (
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51),
            event("latch_suspend_end", "2026-11-22T10:00:00.100Z", 2, 51, success="1", duration=100000),
        )
        with self.assertRaisesRegex(PilotError, "loss, truncation, or cap"):
            parse_wait_pairs(output(*rows, stats="XE_STATS|1|1|0|2|0"), 1, BINDINGS, DATABASE_ID)
        changed = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51, page=900),
            event("latch_suspend_end", "2026-11-22T10:00:00.100Z", 2, 51, page=901, success="1", duration=100000),
        )
        with self.assertRaisesRegex(PilotError, "resource binding changed"):
            parse_wait_pairs(changed, 1, BINDINGS, DATABASE_ID)


if __name__ == "__main__":
    unittest.main()
