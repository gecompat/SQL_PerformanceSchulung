from __future__ import annotations

from dataclasses import replace
from unittest import TestCase, main
from unittest.mock import patch

from test_idx010_query_evidence import EXPECTED_RESULT, IO, PLAN

from idx010_pilot_sequence import Arm, IndexEvidence, QueryCapture, run_pilot
from idx010_pilot_setup import INDEX_NAME, ROWGROUP_COUNT, ROWGROUP_ROWS


class FixtureTransport:
    def __init__(self):
        self.calls = []
        self.cleanup_ok = True
        self.same_segments = False
        self.fail_provision = None
        self.bad_index = False
        self.preflight_timeout = False
        self.closed_streams = []

    def start_verified_instance(self, token, deadline):
        self.calls.append(("start", token, deadline))
        if self.preflight_timeout:
            raise TimeoutError

    def provision(self, target, deadline):
        self.calls.append(("provision", target.arm))
        if target.arm is self.fail_provision:
            raise OSError

    def execute(self, target, sql, deadline):
        self.calls.append(("build" if "CREATE NONCLUSTERED" in sql else "setup", target.arm))

    def stream_rows(self, target, sql, deadline):
        try:
            self.calls.append(("stream", target.arm))
            yield (0, 0)
        finally:
            self.closed_streams.append(target.arm)

    def index_evidence(self, target, deadline):
        self.calls.append(("catalog", target.arm))
        ordered = target.arm is Arm.ORDERED
        metadata = IndexEvidence(
            target.database_name,
            INDEX_NAME,
            int(ordered),
            (ROWGROUP_ROWS,) * ROWGROUP_COUNT,
            False,
            ROWGROUP_COUNT,
            0 if ordered else 6,
        )
        return replace(metadata, index_name="IX_Other") if self.bad_index else metadata

    def capture_query(self, target, sql, deadline):
        self.calls.append(("capture", target.arm))
        xml = PLAN.replace("[Idx010_control]", f"[{target.database_name}]")
        messages = (IO,) if target.arm is Arm.ORDERED and not self.same_segments else (
            "Table 'Events'. Segment reads 4, segment skipped 0.",
        )
        return QueryCapture(xml, messages, (EXPECTED_RESULT,))

    def cleanup(self, token, attempted, deadline):
        self.calls.append(("cleanup", token, tuple(t.arm for t in attempted), deadline))
        return self.cleanup_ok


class PilotSequenceTests(TestCase):
    @patch("idx010_pilot_sequence.verify_fixture_identity", side_effect=lambda rows: next(rows))
    def test_full_flow_validates_both_fixtures_before_index_and_cleans(self, _verify):
        transport = FixtureTransport()
        result = run_pilot(transport, "RUN")
        self.assertEqual(result.status, "PASS")
        self.assertEqual([arm.segments.skipped for arm in result.arms], [0, 3])
        names = [call[0] for call in transport.calls]
        self.assertLess(max(i for i, name in enumerate(names) if name == "stream"), names.index("build"))
        self.assertEqual(transport.closed_streams, list(Arm))
        self.assertEqual(transport.calls[-1][:3], ("cleanup", "RUN", tuple(Arm)))

    def test_invalid_stream_blocks_all_index_builds(self):
        transport = FixtureTransport()
        result = run_pilot(transport, "RUN")
        self.assertEqual((result.status, result.stage), ("NOT_PROVEN", "identity"))
        self.assertFalse(any(call[0] == "build" for call in transport.calls))
        self.assertEqual(transport.calls[-1][:3], ("cleanup", "RUN", tuple(Arm)))

    def test_partial_provision_and_start_timeout_still_request_cleanup(self):
        partial = FixtureTransport()
        partial.fail_provision = Arm.ORDERED
        self.assertEqual(run_pilot(partial, "RUN").status, "NOT_PROVEN")
        self.assertEqual(partial.calls[-1][:3], ("cleanup", "RUN", tuple(Arm)))

        timeout = FixtureTransport()
        timeout.preflight_timeout = True
        self.assertEqual(run_pilot(timeout, "RUN").status, "NOT_PROVEN")
        self.assertEqual(timeout.calls[-1][:3], ("cleanup", "RUN", ()))

    @patch("idx010_pilot_sequence.verify_fixture_identity", side_effect=lambda rows: next(rows))
    def test_unconfirmed_cleanup_takes_priority_over_positive_evidence(self, _verify):
        transport = FixtureTransport()
        transport.cleanup_ok = False
        result = run_pilot(transport, "RUN")
        self.assertEqual(result.status, "FAIL_CLEANUP")
        self.assertEqual(len(result.arms), 2)

    @patch("idx010_pilot_sequence.verify_fixture_identity", side_effect=lambda rows: next(rows))
    def test_metadata_rejection_precedes_capture_and_no_segment_gain_fails(self, _verify):
        transport = FixtureTransport()
        transport.bad_index = True
        result = run_pilot(transport, "RUN")
        self.assertEqual((result.status, result.stage), ("NOT_PROVEN", "metadata"))
        self.assertFalse(any(call[0] == "capture" for call in transport.calls))

        transport = FixtureTransport()
        transport.same_segments = True
        result = run_pilot(transport, "RUN")
        self.assertEqual((result.status, result.stage), ("NOT_PROVEN", "comparison"))


if __name__ == "__main__":
    main()
