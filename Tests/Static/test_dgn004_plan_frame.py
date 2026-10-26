"""Static boundary tests for the fixed DGN-004 plan frame."""
from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dgn004_plan_frame import PlanFrameError, decode_plan_frame, encode_plan_frame


RUN = "run-20261026-a1"
ROLE = "R"
CALL = 3
PAYLOAD = "<plan>ok</plan>".encode("utf-16-le")
SHA = hashlib.sha256(PAYLOAD).hexdigest()


def make_frame(*, run: str = RUN, role: str = ROLE, call: int = CALL,
               payload: bytes = PAYLOAD, chunks: list[bytes] | None = None,
               end_run: str | None = None, end_role: str | None = None,
               end_call: int | None = None) -> str:
    parts = chunks if chunks is not None else [payload[i:i + 100] for i in range(0, len(payload), 100)]
    digest = hashlib.sha256(payload).hexdigest()
    common = f"{run}|{role}|{call}|{len(payload)}|{len(parts)}|{digest}"
    start = f"DGN004_PLAN_START|{common}"
    end = (f"DGN004_PLAN_END|{end_run or run}|{end_role or role}|"
           f"{call if end_call is None else end_call}|{len(payload)}|{len(parts)}|{digest}")
    lines = [start]
    lines.extend(f"DGN004_PLAN_CHUNK|{index}|{part.hex()}" for index, part in enumerate(parts, 1))
    lines.append(end)
    return "\n".join(lines)


class Dgn004PlanFrameTests(unittest.TestCase):
    def test_serializer_produces_fixed_roundtripping_records(self) -> None:
        payload = b"a" * 100 + "λ".encode("utf-16-le")
        frame = encode_plan_frame(payload, run=RUN, role="H", call=9)
        self.assertEqual(decode_plan_frame(frame, expected_run=RUN, expected_role="H", expected_call=9), payload.decode("utf-16-le"))
        self.assertEqual(frame.splitlines()[1].split("|")[1], "1")
        self.assertEqual(frame.splitlines()[2].split("|")[1], "2")
        self.assertTrue(frame.splitlines()[0].startswith("DGN004_PLAN_START|"))
        self.assertTrue(frame.splitlines()[-1].startswith("DGN004_PLAN_END|"))

    def test_serializer_rejects_unbounded_or_unbound_payloads(self) -> None:
        cases = ((b"", RUN, ROLE, CALL), (b"x", RUN, ROLE, CALL), (b"\x00\xd8", RUN, ROLE, CALL),
                 (b"a" * (512 * 1024 + 2), RUN, ROLE, CALL), (PAYLOAD, "bad|run", ROLE, CALL),
                 (PAYLOAD, RUN, "X", CALL), (PAYLOAD, RUN, ROLE, True))
        for payload, run, role, call in cases:
            with self.subTest(size=len(payload), run=run, role=role, call=call):
                with self.assertRaises(PlanFrameError):
                    encode_plan_frame(payload, run=run, role=role, call=call)

    def test_serializer_bounds_run_before_record_formatting(self) -> None:
        class NoFormatOversizeRun(str):
            def __format__(self, spec: str) -> str:
                raise AssertionError("oversized run must be rejected before record formatting")

        with self.assertRaisesRegex(PlanFrameError, "invalid caller run binding"):
            encode_plan_frame(PAYLOAD, run=NoFormatOversizeRun("r" * 65), role=ROLE, call=CALL)

    def test_valid_frame_lf_crlf_and_optional_final_newline(self) -> None:
        self.assertEqual(decode_plan_frame(make_frame(), expected_run=RUN, expected_role=ROLE, expected_call=CALL), PAYLOAD.decode("utf-16-le"))
        crlf = make_frame().replace("\n", "\r\n") + "\r\n"
        self.assertEqual(decode_plan_frame(crlf, expected_run=RUN, expected_role=ROLE, expected_call=CALL), PAYLOAD.decode("utf-16-le"))

    def test_expected_invocation_binding_is_supplied_separately(self) -> None:
        frame = make_frame()
        for expected_run, expected_role, expected_call in (("other", ROLE, CALL), (RUN, "H", CALL), (RUN, ROLE, 4)):
            with self.subTest(expected=(expected_run, expected_role, expected_call)):
                with self.assertRaisesRegex(PlanFrameError, "caller run/role/call binding"):
                    decode_plan_frame(frame, expected_run=expected_run, expected_role=expected_role, expected_call=expected_call)
        with self.assertRaisesRegex(PlanFrameError, "end record differs"):
            decode_plan_frame(make_frame(end_run="other"), expected_run=RUN, expected_role=ROLE, expected_call=CALL)

    def test_missing_duplicate_or_reordered_chunks_rejected(self) -> None:
        payload = b"x" * 202
        good = make_frame(payload=payload)
        lines = good.splitlines()
        variants = ("\n".join([lines[0], lines[1], lines[3], lines[-1]]),
                    "\n".join([lines[0], lines[1], lines[1], lines[2], lines[-1]]),
                    "\n".join([lines[0], lines[2], lines[1], lines[3], lines[-1]]))
        for invalid in variants:
            with self.subTest(invalid=invalid[:70]):
                with self.assertRaises(PlanFrameError):
                    decode_plan_frame(invalid, expected_run=RUN, expected_role=ROLE, expected_call=CALL)

    def test_truncation_wrong_fields_and_extra_output_rejected(self) -> None:
        good = make_frame()
        variants = (good.rsplit("\n", 1)[0], good + "\nnoise", good.replace("|1|", "|2|", 1),
                    good.replace("DGN004_PLAN_START", "DGN004_PLAN_OTHER", 1),
                    good.replace("|" + SHA + "\n", "|" + "0" * 64 + "\n", 1))
        for invalid in variants:
            with self.subTest(invalid=invalid[:55]):
                with self.assertRaises(PlanFrameError):
                    decode_plan_frame(invalid, expected_run=RUN, expected_role=ROLE, expected_call=CALL)

    def test_payload_hex_and_exact_chunk_lengths_are_enforced(self) -> None:
        good = make_frame()
        chunk_line = good.splitlines()[1]
        variants = (good.replace(chunk_line, chunk_line[:-1]),
                    good.replace(chunk_line, chunk_line + " "),
                    good.replace(chunk_line, chunk_line.replace("|1|", "|01|")),
                    good.replace(chunk_line, chunk_line.replace("|", "|", 1) + "|extra"))
        for invalid in variants:
            with self.subTest(invalid=invalid[:60]):
                with self.assertRaises(PlanFrameError):
                    decode_plan_frame(invalid, expected_run=RUN, expected_role=ROLE, expected_call=CALL)

    def test_invalid_line_breaks_encoding_and_caller_arguments_rejected(self) -> None:
        for invalid in (make_frame().replace("\n", "\n\n", 1), make_frame().replace("\n", "\r", 1), make_frame() + "\u2603", make_frame() + "\r"):
            with self.subTest(invalid=repr(invalid[-12:])):
                with self.assertRaises(PlanFrameError):
                    decode_plan_frame(invalid, expected_run=RUN, expected_role=ROLE, expected_call=CALL)

    def test_oversized_text_rejected_before_any_encoded_copy(self) -> None:
        class NoEncodeOversize(str):
            def encode(self, *args: object, **kwargs: object) -> bytes:
                raise AssertionError("oversized text must be rejected before encode")

        oversized = NoEncodeOversize("A" * (2 * 1024 * 1024 + 1))
        with self.assertRaisesRegex(PlanFrameError, "exceeds the planned stdout ceiling"):
            decode_plan_frame(oversized, expected_run=RUN, expected_role=ROLE, expected_call=CALL)
        for role, call in (("X", CALL), (ROLE, True), (ROLE, 10)):
            with self.subTest(role=role, call=call):
                with self.assertRaises(PlanFrameError):
                    decode_plan_frame(make_frame(), expected_run=RUN, expected_role=role, expected_call=call)

    def test_declared_size_and_chunk_count_boundaries(self) -> None:
        # A minimal UTF-16 payload is accepted; empty or odd-byte payload declarations are not.
        for text in ("DGN004_PLAN_START|run-20261026-a1|R|3|0|0|" + "0" * 64,
                     "DGN004_PLAN_START|run-20261026-a1|R|3|3|1|" + "0" * 64):
            with self.subTest(text=text):
                with self.assertRaises(PlanFrameError):
                    decode_plan_frame(text, expected_run=RUN, expected_role=ROLE, expected_call=CALL)

    def test_extreme_decimal_field_is_a_rejected_frame(self) -> None:
        huge = "9" * 5000
        invalid = make_frame().replace(f"|{CALL}|", f"|{huge}|", 1)
        with self.assertRaisesRegex(PlanFrameError, "invalid call"):
            decode_plan_frame(invalid, expected_run=RUN, expected_role=ROLE, expected_call=CALL)


if __name__ == "__main__":
    unittest.main()
