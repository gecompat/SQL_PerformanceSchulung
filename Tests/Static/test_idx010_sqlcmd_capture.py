from __future__ import annotations

from time import monotonic
from unittest import TestCase, main
from unittest.mock import patch

from test_idx010_query_evidence import IO, PLAN

from dgn004_capture_runner import BoundedProcessResult, CaptureTimeoutError
from idx010_pilot_sequence import Arm, Target
from idx010_query_evidence import QUERY, verify_query_evidence
from idx010_sqlcmd_capture import (
    COMPLETE,
    LANGUAGE_MESSAGE,
    MeasurementConnection,
    PLAN_DISPLAY_WIDTH,
    capture_query,
    decode_capture,
)


TARGET = Target("RUN8", Arm.CONTROL)
CONNECTION = MeasurementConnection("a" * 64, "idx010_reader_RUN8", "ephemeral-test-value")
XML = " ".join(line.strip() for line in PLAN.splitlines()).replace("[Idx010_control]", f"[{TARGET.database_name}]")
OUT = f"   4096 | 4303353856  \n\n{XML}\n\n{COMPLETE} \n".encode()
ERR = f"{LANGUAGE_MESSAGE}\n{IO}\n".encode()


class SqlcmdCaptureTests(TestCase):
    def test_frames_plan_result_and_information_stream(self):
        capture = decode_capture(OUT, ERR)
        counts = verify_query_evidence(
            plan_xml=capture.plan_xml,
            info_messages=capture.info_messages,
            result_rows=capture.result_rows,
            database_name=TARGET.database_name,
            index_name="IX_Events",
        )
        self.assertEqual((counts.reads, counts.skipped), (1, 3))

    def test_rejects_truncated_wrapped_or_extra_stdout(self):
        for stdout in (
            OUT.replace(COMPLETE.encode(), b""),
            OUT.replace(b"</ShowPlanXML>", b""),
            OUT.replace(b"<BatchSequence>", b"\n<BatchSequence>"),
            OUT + b"42\n",
            OUT.replace(b"4096", b"NULL", 1),
            OUT.replace(b"<BatchSequence>", b" " * PLAN_DISPLAY_WIDTH + b"<BatchSequence>"),
        ):
            with self.subTest(length=len(stdout)), self.assertRaises(ValueError):
                decode_capture(stdout, ERR)

    def test_rejects_missing_duplicate_or_unexpected_info(self):
        for stderr in (b"", ERR + ERR, ERR + b"Warning\n", b"\xff", b"Table 'Other'.\n"):
            with self.subTest(length=len(stderr)), self.assertRaises(ValueError):
                decode_capture(OUT, stderr)

    @patch("idx010_sqlcmd_capture.collect_bounded_process", return_value=BoundedProcessResult(0, OUT, ERR, 0.1))
    def test_calls_fixed_query_once_without_password_in_arguments(self, collect):
        result = capture_query(CONNECTION, TARGET, QUERY, monotonic() + 30)
        self.assertEqual(result.result_rows, ((4096, 4303353856),))
        collect.assert_called_once()
        argv, = collect.call_args.args
        options = collect.call_args.kwargs
        self.assertEqual(argv[:3], ["docker", "exec", "-i"])
        self.assertIn("127.0.0.1", argv)
        self.assertNotIn(CONNECTION.password, argv)
        self.assertEqual(options["environment"]["SQLCMDPASSWORD"], CONNECTION.password)
        batch = options["input_bytes"].decode("ascii")
        self.assertEqual(batch.count(QUERY), 1)
        self.assertEqual(batch.count("\nGO\n"), 1)
        self.assertLess(batch.index("SET STATISTICS XML ON"), batch.index(QUERY))
        self.assertLess(batch.index(QUERY), batch.index("SET STATISTICS XML OFF"))

    @patch("idx010_sqlcmd_capture.collect_bounded_process")
    def test_rejects_wrong_connection_query_or_deadline_without_a_process(self, collect):
        invalid = MeasurementConnection("display-name", CONNECTION.login, CONNECTION.password)
        with self.assertRaises(ValueError):
            capture_query(invalid, TARGET, QUERY, monotonic() + 30)
        with self.assertRaises(ValueError):
            capture_query(CONNECTION, Target("WRONG", Arm.CONTROL), QUERY, monotonic() + 30)
        with self.assertRaises(ValueError):
            capture_query(CONNECTION, TARGET, "SELECT 1", monotonic() + 30)
        with self.assertRaises(TimeoutError):
            capture_query(CONNECTION, TARGET, QUERY, monotonic() - 1)
        collect.assert_not_called()

    @patch("idx010_sqlcmd_capture.collect_bounded_process")
    def test_process_failure_and_timeout_are_sanitized(self, collect):
        collect.return_value = BoundedProcessResult(1, b"", b"raw-client-error", 0.1)
        with self.assertRaisesRegex(OSError, "^SQL measurement request failed$"):
            capture_query(CONNECTION, TARGET, QUERY, monotonic() + 30)
        collect.side_effect = CaptureTimeoutError("raw-client-timeout")
        with self.assertRaisesRegex(TimeoutError, "^SQL measurement deadline exceeded$"):
            capture_query(CONNECTION, TARGET, QUERY, monotonic() + 30)


if __name__ == "__main__":
    main()
