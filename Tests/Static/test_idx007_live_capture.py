from __future__ import annotations

import unittest

from Tests.Runtime.idx007_hot_leaf_pilot import PilotError, parse_wait_pairs


DATABASE_ID = 7
BINDINGS = {51: 0, 52: 0}


def event(name: str, timestamp: str, sequence: int, session: int, page: int = 900,
          request: int = 0, *, success: str = "", duration: int = 0) -> str:
    return (f"XE_ROW|1|{name}|{timestamp}|{sequence}|{session}|{request}|7|1|{page}|"
            f"EX|BUF|{success}|{duration}")


def output(*rows: str, stats: str = "XE_STATS|1|0|0|4|0") -> str:
    return "\n".join((stats, *rows))


class LiveCaptureParserTests(unittest.TestCase):
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

    def test_equal_millisecond_stamps_use_measured_microsecond_durations(self) -> None:
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

    def test_non_chronological_pair_is_rejected(self) -> None:
        reversed_interval = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.100Z", 1, 51),
            event("latch_suspend_end", "2026-11-22T10:00:00.000Z", 2, 51, success="1", duration=100000),
        )
        with self.assertRaisesRegex(PilotError, "not chronological"):
            parse_wait_pairs(reversed_interval, 1, BINDINGS, DATABASE_ID)

    def test_duration_must_align_with_begin_timestamp(self) -> None:
        inconsistent = output(
            event("latch_suspend_begin", "2026-11-22T10:00:00.000Z", 1, 51),
            event("latch_suspend_end", "2026-11-22T10:00:00.100Z", 2, 51, success="1", duration=1000),
        )
        with self.assertRaisesRegex(PilotError, "does not align"):
            parse_wait_pairs(inconsistent, 1, BINDINGS, DATABASE_ID)

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
