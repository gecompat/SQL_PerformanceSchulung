"""Synthetic regression cases for the bounded OPTSP XE snapshot reader."""

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))
from optsp_xe_snapshot import SessionCounters, read_ring_buffer


CLEAN = SessionCounters(0, 0, 0, 0)


def event(sequence: int = 1, timestamp: str = "2026-01-01T01:02:03.1234567Z") -> str:
    return (
        f'<event name="rpc_completed" package="sqlserver" timestamp="{timestamp}">'
        f'<action name="event_sequence" package="package0"><value>{sequence}</value></action>'
        '<data name="statement"><value>SELECT 1</value></data></event>'
    )


def snapshot(*events: str, truncated: int = 0, dropped: int = 0, processed: int | None = None) -> bytes:
    count = len(events) if processed is None else processed
    return (
        f'<RingBufferTarget truncated="{truncated}" eventCount="{len(events)}" '
        f'droppedCount="{dropped}" totalEventsProcessed="{count}">'
        f'{"".join(events)}</RingBufferTarget>'
    ).encode()


class SnapshotTests(unittest.TestCase):
    def test_retains_seventh_fraction_digit_and_orders_by_sequence(self):
        xml = snapshot(event(9), event(5, "2026-01-01T01:02:03.1234568Z"))
        low, high = read_ring_buffer(xml, CLEAN)
        self.assertEqual((low.sequence, high.sequence), (5, 9))
        self.assertEqual(low.timestamp_ticks - high.timestamp_ticks, 1)
        self.assertEqual(low.payload.findtext("./data/value"), "SELECT 1")
        self.assertNotIn("SELECT 1", repr(low))

    def test_optional_fraction_and_midnight(self):
        xml = snapshot(event(1, "2025-12-31T23:59:59.9999999Z"), event(2, "2026-01-01T00:00:00Z"))
        before, after = read_ring_buffer(xml, CLEAN)
        self.assertEqual(after.timestamp_ticks - before.timestamp_ticks, 1)

    def test_rejects_loss_eviction_truncation_empty_or_wrong_count(self):
        cases = [
            snapshot(event(), truncated=1),
            snapshot(event(), dropped=1),
            snapshot(event(), processed=2),
            snapshot(),
            snapshot(event()).replace(b'eventCount="1"', b'eventCount="2"'),
            snapshot(event()).replace(b'truncated="0"', b''),
        ]
        for xml in cases:
            with self.subTest(xml=xml), self.assertRaises(ValueError):
                read_ring_buffer(xml, CLEAN)

    def test_session_counters_are_required_and_zero(self):
        for counters in (
            SessionCounters(1, 0, 0, 0),
            SessionCounters(0, 1, 0, 0),
            SessionCounters(0, 0, 1, 0),
            SessionCounters(0, 0, 0, 1),
            SessionCounters(0, 0, False, 0),
            SessionCounters(-1, 0, 0, 0),
        ):
            with self.subTest(counters=counters), self.assertRaises(ValueError):
                read_ring_buffer(snapshot(event()), counters)

    def test_rejects_ambiguous_or_unbound_sequences(self):
        row = event()
        action = row[row.index("<action"):row.index("</action>") + len("</action>")]
        cases = [
            snapshot(row, row),
            snapshot(row.replace(action, "")),
            snapshot(row.replace(action, action * 2)),
            snapshot(row.replace("package0", "other")),
            snapshot(row.replace("</value></action>", "</value><value>2</value></action>")),
        ]
        for xml in cases:
            with self.subTest(xml=xml), self.assertRaises(ValueError):
                read_ring_buffer(xml, CLEAN)

    def test_rejects_unbound_or_invalid_utc_labels(self):
        for value in ("", "2026-02-30T00:00:00Z", "2026-01-01T24:00:00Z", "2026-01-01T00:00:60Z",
                      "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00.12345678Z"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                read_ring_buffer(snapshot(event(timestamp=value)), CLEAN)

    def test_rejects_oversized_or_malformed_xml_without_echoing_it(self):
        cases = [b'x' * (4 * 1024 * 1024 + 1), b'\xff', b'<bad', b'<!DOCTYPE ring>' + snapshot(event())]
        for xml in cases:
            with self.assertRaises(ValueError) as failure:
                read_ring_buffer(xml, CLEAN)
            self.assertNotIn("DOCTYPE", str(failure.exception))


if __name__ == "__main__":
    unittest.main()
