"""Unabhängige skalare Footeroracles; keine Runtimekandidaten oder Worker."""
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_session_end as footer


def fields(ordinal=1, fragments=19, stdout=100, stderr=0):
    # Eigene benannte Rollenoracle, keine Implementierungskonstanten.
    sources = {1: 8, 2: 1, 3: 3}[ordinal]
    parents = 2 if ordinal == 1 else 0
    records = fragments + 4 + 2 * (sources + parents)
    return ("SESSION_END", ordinal, "a" * 64, fragments, sources, sources,
            parents, parents, records, stdout, stderr, "b" * 64)


def literal(values):
    # Direkte ASCII-Literaloracle; kein JSONencoder als Sollwertquelle.
    pieces = tuple(('"' + v + '"') if type(v) is str else str(v) for v in values)
    return ("[" + ",".join(pieces) + "]\n").encode("ascii")


class FooterTests(unittest.TestCase):
    def rejected(self, value, issue=None, encode=False):
        call = footer.encode_footer if encode else footer.decode_footer
        with self.assertRaises(footer.FooterRejected) as caught:
            call(value)
        error = caught.exception
        if issue is not None:
            self.assertEqual(str(error), issue)
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn("private_probe", repr(error))
        return str(error)

    def test_all_roles_and_fragment_counts_preserve_literal_and_original_bytes(self):
        for ordinal in (1, 2, 3):
            for fragments in range(1, 20):
                values = fields(ordinal, fragments)
                line = literal(values)
                with self.subTest(ordinal=ordinal, fragments=fragments):
                    decoded = footer.decode_footer(line)
                    self.assertIs(decoded.line, line)
                    self.assertEqual(decoded.values, values)
                    self.assertEqual(footer.encode_footer(values), line)
                    self.assertEqual(decoded.status, "DECODED_SESSION_END_FOOTER")

    def test_width_bound_is_178_and_not_a_valid_joint_65536_case(self):
        for ordinal in (1, 2, 3):
            values = fields(ordinal, stdout=65536, stderr=65536)
            self.assertEqual(len(literal(values)), 178)
            self.rejected(literal(values), "SESSION_END_LIMIT")
            self.rejected(values, "SESSION_END_LIMIT", encode=True)

    def test_necessary_single_worker_joint_byte_boundary_includes_footer(self):
        for ordinal in (1, 2, 3):
            values = fields(ordinal, stdout=65000, stderr=358)
            self.assertEqual(len(literal(values)), 176)
            # Fester Punkt: Footerbreite berücksichtigt fünf-/dreistellige Counts.
            budget = 65536 - len(literal(values)) - values[10]
            values = values[:9] + (budget, values[10], values[11])
            self.assertEqual(values[9] + values[10] + len(literal(values)), 65536)
            self.assertEqual(footer.decode_footer(literal(values)).values, values)
            self.rejected(literal(values[:9] + (budget + 1, *values[10:])), "SESSION_END_LIMIT")

    def test_partial_result_is_frozen_private_and_never_a_full_match(self):
        decoded = footer.decode_footer(literal(fields(stdout=0)))
        self.assertEqual(repr(decoded), "DecodedFooter(PROJECT_SEMANTIC)")
        self.assertEqual(decoded.validation_scope, "PROJECT_SEMANTIC")
        for name in ("full_trace_verified", "context_verified", "channel_verified",
                     "runtime_attested", "trust_attested", "import_used_bytes_attested",
                     "method_approved"):
            self.assertIs(getattr(decoded, name), False)
        with self.assertRaises(FrozenInstanceError):
            decoded.line = b"other"
        with self.assertRaises(FrozenInstanceError):
            decoded.runtime_attested = True
        with self.assertRaises(TypeError):
            footer.DecodedFooter(b"", (), full_trace_verified=True)
        self.assertNotIn("MATCHED_DECLARED_SESSION_END", decoded.status)

    def test_all_twelve_field_types_are_checked_before_semantics(self):
        class Foreign:
            def __eq__(self, other):
                raise AssertionError("fremder Dispatch")
        for index in range(12):
            for bad in (None, Foreign(), [], {}, b"a", True, 1.0):
                values = list(fields())
                values[index] = bad
                self.rejected(tuple(values), "SESSION_END_TYPE", encode=True)
        values = list(fields()); values[0] = "wrong"; values[-1] = Foreign()
        self.rejected(tuple(values), "SESSION_END_TYPE", encode=True)

    def test_exact_outer_and_primitive_types_reject_subclasses_before_dispatch(self):
        class Bytes(bytes):
            def __len__(self): raise AssertionError("fremdes len")
        class Tuple(tuple):
            def __len__(self): raise AssertionError("fremdes len")
        class Integer(int):
            def __eq__(self, other): raise AssertionError("fremdes eq")
        class Text(str):
            def __len__(self): raise AssertionError("fremdes len")
        self.rejected(Bytes(b"x"), "SESSION_END_TYPE")
        self.rejected(Tuple(fields()), "SESSION_END_TYPE", encode=True)
        for index in range(12):
            values = list(fields())
            values[index] = Text(values[index]) if index in (0, 2, 11) else Integer(values[index])
            self.rejected(tuple(values), "SESSION_END_TYPE", encode=True)
        for value in ("text", bytearray(b"x"), memoryview(b"x"), None):
            self.rejected(value, "SESSION_END_TYPE")
        for value in (list(fields()), None, {"x": 1}):
            self.rejected(value, "SESSION_END_TYPE", encode=True)

    def test_size_is_bounded_before_parser_or_copies(self):
        with patch.object(footer.json, "loads") as parse:
            for value in (b"", b"x" * 257, b"[" * 10000):
                self.rejected(value, "SESSION_END_LIMIT")
            parse.assert_not_called()
        self.rejected(b" " * 255 + b"\n", "SESSION_END_FORM")

    def test_every_declared_count_and_role_is_exact(self):
        for ordinal in (1, 2, 3):
            for index in range(4, 9):
                values = list(fields(ordinal)); values[index] += 1
                self.rejected(literal(values), "SESSION_END_COUNTS")
            for index, bad in ((1, 0), (1, 4), (3, 0), (3, 20)):
                values = list(fields(ordinal)); values[index] = bad
                self.rejected(tuple(values), "SESSION_END_COUNTS", encode=True)

    def test_negative_and_overlarge_integers_are_bounded(self):
        for index in (1, 3, 4, 5, 6, 7, 8, 9, 10):
            for bad in (-1, 65537, 10 ** 100):
                values = list(fields()); values[index] = bad
                self.rejected(tuple(values), "SESSION_END_LIMIT", encode=True)
                self.rejected(literal(values), "SESSION_END_LIMIT")

    def test_tag_and_both_lowerhex_digests_are_exact(self):
        for index, bad in ((0, "SESSION_END_other"), (0, "private_probe"),
                           (2, "a" * 63), (2, "A" * 64), (2, "g" * 64),
                           (11, "b" * 65), (11, "B" * 64), (11, "")):
            values = list(fields()); values[index] = bad
            self.rejected(tuple(values), "SESSION_END_FORM", encode=True)
            self.rejected(literal(values), "SESSION_END_FORM")

    def test_whitespace_escapes_negative_zero_and_alternative_json_are_rejected(self):
        line = literal(fields())
        for bad in (b" " + line, line[:-1] + b" \n", line.replace(b",1,", b", 1,", 1),
                    line.replace(b"SESSION_END", b"SESSION_\\u0045ND"),
                    line.replace(b'"' + b"a" * 64 + b'"', b'"\\u0061' + b"a" * 63 + b'"'),
                    line.replace(b",0,", b",-0,", 1)):
            self.rejected(bad, "SESSION_END_CANONICAL")

    def test_bad_shapes_numbers_and_trailing_bytes_do_not_create_a_result(self):
        line = literal(fields())
        malformed = (line[:-1], line + b"\n", line.replace(b"\n", b"\r\n"),
                     line + b"private_probe", line.replace(b",1,", b",1.0,", 1),
                     line.replace(b",1,", b",true,", 1), line.replace(b",1,", b",NaN,", 1),
                     line.replace(b",1,", b",Infinity,", 1), b"null\n", b"{}\n",
                     b"[" * 100 + b"]" * 100 + b"\n", b"\xff\n",
                     literal(fields()[:-1]), literal(fields() + (0,)),
                     b'["private_probe",\n')
        for index, bad in enumerate(malformed):
            with self.subTest(case=index):
                self.rejected(bad)

    def test_unexpected_parser_and_encoder_errors_leave_no_private_chain(self):
        for operation in ("loads", "dumps"):
            with patch.object(footer.json, operation, side_effect=ValueError("private_probe")):
                self.rejected(literal(fields()), "SESSION_END_FORM")
        with patch.object(footer.json, "dumps", side_effect=RuntimeError("private_probe")):
            self.rejected(fields(), "SESSION_END_FORM", encode=True)


if __name__ == "__main__":
    unittest.main()
