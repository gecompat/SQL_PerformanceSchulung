"""Offline chunk, checksum, size, and UTF-16 checks for the DGN-004 decoder."""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parent))
import dgn004_plan_transport as transport  # noqa: E402


def records(payload: bytes, *, chunk_size: int = 100, start: int = 0) -> list[tuple[int, str]]:
    return [
        (start + index, payload[offset : offset + chunk_size].hex().upper())
        for index, offset in enumerate(range(0, len(payload), chunk_size))
    ]


def decode(payload: bytes, values: list[tuple[int, str]] | None = None, **overrides) -> str:
    chunks = records(payload) if values is None else values
    arguments = {
        "declared_chunk_count": len(chunks),
        "declared_byte_length": len(payload),
        "server_sha256": hashlib.sha256(payload).hexdigest(),
    }
    arguments.update(overrides)
    return transport.decode_plan_chunks(chunks, **arguments)


class Dgn004PlanTransportTests(unittest.TestCase):
    def test_complete_numbered_plan_decodes_with_zero_or_one_based_sequence(self):
        raw = "<ShowPlanXML><StmtSimple /></ShowPlanXML>".encode("utf-16-le")
        for start in (0, 1):
            with self.subTest(start=start):
                self.assertEqual(
                    "<ShowPlanXML><StmtSimple /></ShowPlanXML>",
                    transport.decode_plan_chunks(
                        records(raw, start=start),
                        declared_chunk_count=len(records(raw)),
                        declared_byte_length=len(raw),
                        server_sha256=hashlib.sha256(raw).hexdigest(),
                    ),
                )

    def test_internal_sequence_start_rejects_other_bases(self):
        raw = "<Plan/>".encode("utf-16-le")
        for start in (2, 42):
            with self.subTest(start=start), self.assertRaisesRegex(
                transport.PlanTransportError, "unsupported internal sequence start"
            ):
                decode(raw, records(raw, start=start))

    def test_iterator_consumption_is_bounded_to_declared_count_plus_one(self):
        raw = "<ShowPlanXML/>".encode("utf-16-le")
        items = records(raw)

        class GuardedIterator:
            def __init__(self):
                self.index = 0
                self.calls = 0

            def __iter__(self):
                return self

            def __next__(self):
                self.calls += 1
                if self.calls > len(items) + 1:
                    raise AssertionError("decoder advanced past declared_count + 1")
                if self.index >= len(items):
                    raise StopIteration
                item = items[self.index]
                self.index += 1
                return item

        guarded = GuardedIterator()
        result = transport.decode_plan_chunks(
            guarded,
            declared_chunk_count=len(items),
            declared_byte_length=len(raw),
            server_sha256=hashlib.sha256(raw).hexdigest(),
        )
        self.assertEqual("<ShowPlanXML/>", result)
        self.assertEqual(len(items) + 1, guarded.calls)

    def test_boolean_values_are_not_accepted_as_counts_or_sequence_numbers(self):
        raw = "<Plan/>".encode("utf-16-le")
        chunks = records(raw)
        cases = (
            ({"declared_chunk_count": True}, "invalid declared chunk count"),
            ({"declared_byte_length": True}, "invalid declared plan byte length"),
        )
        for overrides, message in cases:
            with self.subTest(overrides=overrides), self.assertRaisesRegex(transport.PlanTransportError, message):
                decode(raw, chunks, **overrides)
        with self.assertRaisesRegex(transport.PlanTransportError, "invalid plan chunk record"):
            decode(raw, [(True, chunks[0][1])])

    def test_missing_duplicate_reordered_extra_and_wrong_payload_chunks_fail(self):
        raw = ("<Plan>" + "x" * 150 + "</Plan>").encode("utf-16-le")
        chunks = records(raw)
        cases = (
            ("missing", chunks[:-1], {"declared_chunk_count": len(chunks)}, "missing plan chunk"),
            ("duplicate", chunks[:-1] + [chunks[-2]], {}, "sequence has a gap"),
            ("reordered", [chunks[1], chunks[0], *chunks[2:]], {}, "sequence has a gap"),
            ("extra", chunks + [chunks[-1]], {"declared_chunk_count": len(chunks)}, "unexpected extra"),
            ("wrong payload association", [(chunks[0][0], chunks[1][1]), (chunks[1][0], chunks[0][1]), *chunks[2:]], {}, "checksum mismatch"),
        )
        for label, changed, overrides, message in cases:
            with self.subTest(label=label), self.assertRaisesRegex(transport.PlanTransportError, message):
                decode(raw, changed, **overrides)

    def test_truncation_hex_encoding_byte_count_and_checksum_fail(self):
        raw = "<Plan>complete</Plan>".encode("utf-16-le")
        chunks = records(raw)
        cases = (
            (chunks[:-1] + [(chunks[-1][0], chunks[-1][1][:-2])], {}),
            ([(chunks[0][0], chunks[0][1][:-1] + "G")], {}),
            (chunks, {"declared_byte_length": len(raw) - 2}),
            (chunks, {"server_sha256": "0" * 64}),
            (chunks, {"server_sha256": "not-a-digest"}),
        )
        for changed, overrides in cases:
            with self.subTest(overrides=overrides), self.assertRaises(transport.PlanTransportError):
                decode(raw, changed, **overrides)

    def test_chunk_larger_than_capture_design_limit_fails(self):
        raw = b"a" * 202
        oversized = records(raw, chunk_size=101)
        with self.assertRaisesRegex(transport.PlanTransportError, "plan chunk hex"):
            decode(raw, oversized)

    def test_invalid_utf16_is_rejected_after_valid_bytes_and_checksum(self):
        raw = b"\x00\xd8"
        with self.assertRaisesRegex(transport.PlanTransportError, "invalid UTF-16"):
            decode(raw)

    def test_raw_and_utf8_plan_limits_are_enforced(self):
        with self.assertRaisesRegex(transport.PlanTransportError, "byte length"):
            transport.decode_plan_chunks(
                (), declared_chunk_count=1,
                declared_byte_length=transport.MAX_RAW_PLAN_BYTES + 2,
                server_sha256="0" * 64,
            )
        text = "€" * (transport.MAX_UTF8_PLAN_BYTES // 3 + 1)
        raw = text.encode("utf-16-le")
        self.assertLessEqual(len(raw), transport.MAX_RAW_PLAN_BYTES)
        with self.assertRaisesRegex(transport.PlanTransportError, "UTF-8 plan exceeds"):
            decode(raw)


if __name__ == "__main__":
    unittest.main()
