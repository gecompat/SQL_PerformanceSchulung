"""Drei numerische Ebenengegenproben und begrenzte malformed Fixtures; kein SQL."""

import ast
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal, localcontext, ROUND_DOWN, ROUND_UP
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Tests.Contracts import dgn007_numeric_pipeline_countermodel as m
from Tests.Contracts import dgn007_saturation_countermodel as existing
from Tests.Contracts import dgn007_collector_transport as transport


VALUES = tuple(F(value) for value in (1, 2, 3, 4))
WHOLE = (m.Fragment((0, 1, 2, 3), F(5, 2), "2.5000000000000000e+000"),)
PARTITION = (m.Fragment((0, 1), F(3, 2), "1.5000000000000000e+000"),
             m.Fragment((2, 3), F(7, 2), "3.5000000000000000e+000"))
ROUNDING_VALUES = tuple(F(value) for value in (1, 2, 2, 2))
ROUNDED = (m.Fragment((0, 1, 2), F(7505999378950827, 4503599627370496), "1.6666666666666667e+000"),
           m.Fragment((3,), F(2), "2.0000000000000000e+000"))


class NumericTests(unittest.TestCase):
    def valid(self, values=VALUES, fragments=WHOLE):
        result = m.analyze_partition(values, fragments)
        self.assertTrue(result.valid_model)
        self.assertEqual(result.issues, ())
        self.assertEqual(result.scope, "PROJECT_SEMANTIC")
        self.assertEqual(result.text_origin, "GIVEN_SYNTHETIC")
        self.assertFalse(result.runtime_attested or result.method_approved or result.sql_conversion_emulated)
        return result

    def bad(self, values=VALUES, fragments=WHOLE, issue=m.Issue.INVALID_RECORD):
        result = m.analyze_partition(values, fragments)
        self.assertFalse(result.valid_model)
        self.assertEqual(result.issues, (issue,))
        self.assertIsNone(result.oracle_mean)
        self.assertIsNone(result.consumer_weighted_mean)
        self.assertIsNone(result.oracle_matches_consumer)
        self.assertEqual(result.fragments, ())
        self.assertFalse(result.runtime_attested or result.method_approved or result.sql_conversion_emulated)
        return result

    def test_exact_population_partition_preserves_each_level(self):
        whole = self.valid()
        partition = self.valid(fragments=PARTITION)
        for result in (whole, partition):
            self.assertEqual((result.oracle_mean, result.rounded_weighted_mean, result.consumer_weighted_mean), (F(5, 2),) * 3)
            self.assertEqual((result.rounded_minus_oracle, result.text_minus_rounded, result.consumer_minus_oracle), (F(0),) * 3)
            self.assertTrue(result.oracle_matches_consumer)
            for fragment in result.fragments:
                self.assertEqual(fragment.rounded_minus_oracle, 0)
                self.assertEqual(fragment.text_minus_rounded, 0)
                self.assertEqual(fragment.text_minus_oracle, 0)

    def test_declared_rounding_and_given_text_errors_are_separate(self):
        whole = self.valid(ROUNDING_VALUES, (m.Fragment((0, 1, 2, 3), F(7, 4), "1.7500000000000000e+000"),))
        result = self.valid(ROUNDING_VALUES, ROUNDED)
        self.assertEqual(result.oracle_mean, F(7, 4))
        self.assertEqual(result.rounded_minus_oracle, F(1, 18014398509481984))
        self.assertEqual(result.consumer_minus_oracle, F(1, 40000000000000000))
        self.assertEqual(result.text_minus_rounded, result.consumer_minus_oracle - result.rounded_minus_oracle)
        self.assertEqual(result.fragments[0].oracle_mean, F(5, 3))
        self.assertEqual(result.fragments[0].rounded_minus_oracle, F(1, 13510798882111488))
        self.assertNotEqual(result.fragments[0].text_minus_rounded, 0)
        self.assertNotEqual(whole.consumer_weighted_mean, result.consumer_weighted_mean)
        self.assertFalse(result.oracle_matches_consumer)

    def test_distinct_populations_have_identical_consumer_result(self):
        other = tuple(F(value) for value in (1, 1, 2, 3))
        fragment = (m.Fragment((0, 1, 2, 3), F(7, 4), "1.7500000000000000e+000"),)
        a, b = self.valid(ROUNDING_VALUES, fragment), self.valid(other, fragment)
        self.assertNotEqual(sorted(ROUNDING_VALUES), sorted(other))
        self.assertEqual(a.count, b.count)
        self.assertEqual(a.consumer_weighted_mean, b.consumer_weighted_mean)
        self.assertTrue(a.oracle_matches_consumer and b.oracle_matches_consumer)
        # Aggregate equality does not export a population-identity claim.
        self.assertNotIn("population_unchanged", m.Report.__dataclass_fields__)

    def test_given_text_can_differ_from_exact_declared_mean(self):
        result = self.valid((F(1),), (m.Fragment((0,), F(1), "1.0000000000000001"),))
        self.assertEqual(result.rounded_minus_oracle, 0)
        self.assertEqual(result.text_minus_rounded, F(1, 10**16))
        self.assertEqual(result.consumer_minus_oracle, F(1, 10**16))

    def test_opposite_local_deltas_can_cancel_without_loss_disappearing(self):
        result = self.valid((F(1), F(3)), (m.Fragment((0,), F(2), "2"), m.Fragment((1,), F(2), "2")))
        self.assertTrue(result.oracle_matches_consumer)
        self.assertEqual(tuple(fragment.rounded_minus_oracle for fragment in result.fragments), (F(1), F(-1)))
        self.assertEqual(result.rounded_minus_oracle, 0)
        text_only = self.valid((F(1), F(3)), (m.Fragment((0,), F(1), "2"), m.Fragment((1,), F(3), "2")))
        self.assertTrue(text_only.oracle_matches_consumer)
        self.assertEqual(tuple(fragment.text_minus_rounded for fragment in text_only.fragments), (F(1), F(-1)))

    def test_nonterminating_oracle_is_exact_without_decimal_rounding(self):
        result = self.valid((F(1), F(2), F(2)), (m.Fragment((0, 1, 2), F(5, 3), "1.6666666666666667"),))
        self.assertEqual(result.oracle_mean, F(5, 3))
        self.assertEqual(result.rounded_minus_oracle, 0)
        self.assertNotEqual(result.consumer_minus_oracle, 0)

    def test_all_three_corecases_agree_with_actual_existing_ledger(self):
        for values, fragments in ((VALUES, WHOLE), (VALUES, PARTITION), (ROUNDING_VALUES, ROUNDED),
                                  (ROUNDING_VALUES, (m.Fragment((0, 1, 2, 3), F(7, 4), "1.75"),)),
                                  (tuple(F(v) for v in (1, 1, 2, 3)), (m.Fragment((0, 1, 2, 3), F(7, 4), "1.75"),))):
            result = self.valid(values, fragments)
            binding = existing.Binding(1, 1, "a" * 64)
            raw = tuple(existing.RawFragment(12, 3, 10, 0, len(fragment.indices),
                                             tuple(index + 1 for index in fragment.indices),
                                             existing.Metrics(*(Decimal(fragment.synthetic_style3_text) for _ in range(4))),
                                             10, 20, binding, 1) for fragment in fragments)
            snapshot = existing.Snapshot(existing.SnapshotKind.FINAL, 1, 21, 22, binding, 1, 1, 1,
                                         (existing.FamilyMember(12, 12),), (), raw)
            ledger = existing._ledger(snapshot)
            actual = ledger[(12, 3, 10, 0)]
            self.assertEqual(actual[0], frozenset(range(1, len(values) + 1)))
            self.assertEqual(actual[1], (result.consumer_weighted_mean * result.count,) * 4)

    def test_core_given_texts_match_actual_transport_metric_parser(self):
        for fragment in WHOLE + PARTITION + ROUNDED:
            result = self.valid((F(1),), (replace(fragment, indices=(0,)),))
            self.assertEqual(result.fragments[0].given_text_mean, F(transport._metric(fragment.synthetic_style3_text)))

    def test_ambient_decimal_context_precision_rounding_flags_unchanged(self):
        expected = self.valid(ROUNDING_VALUES, ROUNDED)
        for precision, rounding in ((1, ROUND_DOWN), (2, ROUND_UP), (50, ROUND_DOWN)):
            with localcontext() as context:
                context.prec = precision
                context.rounding = rounding
                before = (context.prec, context.rounding, dict(context.flags))
                self.assertEqual(self.valid(ROUNDING_VALUES, ROUNDED), expected)
                self.assertEqual((context.prec, context.rounding, dict(context.flags)), before)

    def test_partition_missing_duplicate_outside_negative_bool(self):
        for indices, issue in (((0, 1, 2), m.Issue.INVALID_PARTITION), ((0, 1, 2, 2), m.Issue.INVALID_PARTITION),
                               ((0, 1, 2, 4), m.Issue.INVALID_PARTITION), ((-1, 1, 2, 3), m.Issue.INVALID_PARTITION),
                               ((True, 1, 2, 3), m.Issue.INVALID_RECORD)):
            self.bad(fragments=(replace(WHOLE[0], indices=indices),), issue=issue)

    def test_duplicate_across_fragments_not_repaired_by_correct_total_count(self):
        self.bad(fragments=(PARTITION[0], replace(PARTITION[1], indices=(1, 3))), issue=m.Issue.INVALID_PARTITION)

    def test_huge_outside_index_rejected_before_text_or_hash_work(self):
        with patch.object(m, "_given_text", side_effect=AssertionError("must not parse")):
            self.bad(fragments=(replace(WHOLE[0], indices=(0, 1, 2, 1 << 100_000)),), issue=m.Issue.INVALID_PARTITION)

    def test_repeated_numeric_values_are_valid_distinct_indices(self):
        result = self.valid((F(2),) * 4, (m.Fragment((0, 1, 2, 3), F(2), "2"),))
        self.assertTrue(result.oracle_matches_consumer)

    def test_index_and_fragment_order_do_not_change_weighting(self):
        expected = self.valid(fragments=PARTITION)
        actual = self.valid(fragments=tuple(replace(row, indices=row.indices[::-1]) for row in PARTITION[::-1]))
        self.assertEqual(actual.consumer_weighted_mean, expected.consumer_weighted_mean)
        self.assertEqual(actual.oracle_mean, expected.oracle_mean)

    def test_zero_population_values_and_means_are_valid(self):
        result = self.valid((F(0),), (m.Fragment((0,), F(0), "0.0000000000000000e+000"),))
        self.assertEqual(result.consumer_weighted_mean, 0)

    def test_empty_or_mutable_containers_and_bounds(self):
        for values in ((), list(VALUES), VALUES * 5):
            self.bad(values=values)
        for fragments in ((), list(WHOLE), WHOLE * 17, (replace(WHOLE[0], indices=()),),
                          (replace(WHOLE[0], indices=tuple(range(17))),)):
            self.bad(fragments=fragments)
        self.bad(fragments=(replace(WHOLE[0], indices=list(WHOLE[0].indices)),))

    def test_exact_sixteen_value_fragment_limit(self):
        values = tuple(F(i) for i in range(16))
        fragments = tuple(m.Fragment((i,), F(i), str(i)) for i in range(16))
        self.assertTrue(self.valid(values, fragments).oracle_matches_consumer)

    def test_rational_bit_limits_before_arithmetic(self):
        maximum = F((1 << 256) - 1)
        self.valid((maximum,), (m.Fragment((0,), maximum, "1"),))
        self.valid((F(1, (1 << 256) - 1),), (m.Fragment((0,), F(0), "0"),))
        for value in (F(1 << 256), F(1, (1 << 256) + 1), F(-1)):
            self.bad(values=(value,))
            self.bad(fragments=(replace(WHOLE[0], declared_rounded_mean=value),))

    def test_float_decimal_bool_integer_and_fraction_subclasses_reject(self):
        class SubFraction(F):
            pass
        for value in (1.0, Decimal("1"), True, 1, SubFraction(1), None):
            self.bad(values=(value,))
            self.bad(fragments=(replace(WHOLE[0], declared_rounded_mean=value),))

    def test_forged_unreduced_fraction_rejected_without_normalization(self):
        for numerator, denominator in ((0, 2), (2, 2)):
            forged = object.__new__(F)
            object.__setattr__(forged, "_numerator", numerator)
            object.__setattr__(forged, "_denominator", denominator)
            self.bad(values=(forged,))
            self.bad(fragments=(replace(WHOLE[0], declared_rounded_mean=forged),))
        self.assertTrue(self.valid((F(0),), (m.Fragment((0,), F(0), "0"),)).oracle_matches_consumer)

    def test_record_tuple_string_and_integer_subclasses_reject(self):
        class SubFragment(m.Fragment):
            pass
        class SubTuple(tuple):
            pass
        class SubStr(str):
            pass
        class SubInt(int):
            pass
        self.bad(fragments=(SubFragment((0, 1, 2, 3), F(5, 2), "2.5"),))
        self.bad(values=SubTuple(VALUES))
        self.bad(fragments=SubTuple(WHOLE))
        self.bad(fragments=(replace(WHOLE[0], indices=SubTuple((0, 1, 2, 3))),))
        self.bad(fragments=(replace(WHOLE[0], indices=(SubInt(0), 1, 2, 3)),))
        self.bad(fragments=(replace(WHOLE[0], synthetic_style3_text=SubStr("2.5")),), issue=m.Issue.INVALID_TEXT)

    def test_unknown_and_unconstructed_records_fail_closed(self):
        self.bad(fragments=(None,))
        self.bad(fragments=(m.Fragment.__new__(m.Fragment),))
        self.bad(values=(object.__new__(F),))

    def test_invalid_text_forms_are_not_sql_conversion_results(self):
        for text in ("", "NaN", "sNaN", "Infinity", "-1", "+1", " 1", "1 ", "01", ".5", "1.",
                     "1,5", "1e1000", "1e-1000", "1e99", "1e-31", "1e21", "١", "1\n", "1\x00", "1" * 65):
            self.bad(fragments=(replace(WHOLE[0], synthetic_style3_text=text),), issue=m.Issue.INVALID_TEXT)
        for text in (None, True, 1.0, Decimal("1")):
            self.bad(fragments=(replace(WHOLE[0], synthetic_style3_text=text),), issue=m.Issue.INVALID_TEXT)

    def test_text_boundaries_and_precision_are_model_limits(self):
        for text in ("1e-30", "1e20", "0." + "0" * 29 + "1", "1234.123456789012345678901234567890"):
            self.valid((F(1),), (m.Fragment((0,), F(1), text),))
        for text in ("0." + "0" * 30 + "1", "1234.1234567890123456789012345678901"):
            self.bad(fragments=(replace(WHOLE[0], synthetic_style3_text=text),), issue=m.Issue.INVALID_TEXT)
        # Length64 is within the defensive byte-free text cap, but not the precision bound.
        self.bad(fragments=(replace(WHOLE[0], synthetic_style3_text="1." + "0" * 62),), issue=m.Issue.INVALID_TEXT)
        self.assertEqual(m.MAX_TEXT, 64)

    def test_text_rejected_before_decimal_constructor(self):
        for text in ("1" * 65, "1e1000", "1e99", "1" * 35):
            with patch.object(m, "Decimal", side_effect=AssertionError("must not construct")):
                self.bad(fragments=(replace(WHOLE[0], synthetic_style3_text=text),), issue=m.Issue.INVALID_TEXT)

    def test_foreign_getters_and_comparisons_never_executed(self):
        class Foreign:
            def __getattr__(self, name):
                raise RuntimeError("must not execute getter")

            def __eq__(self, other):
                raise RuntimeError("must not execute equality")
        foreign = Foreign()
        self.bad(values=foreign)
        self.bad(fragments=foreign)
        self.bad(fragments=(foreign,))
        for field in fields(m.Fragment):
            issue = m.Issue.INVALID_TEXT if field.name == "synthetic_style3_text" else m.Issue.INVALID_RECORD
            self.bad(fragments=(replace(WHOLE[0], **{field.name: foreign}),), issue=issue)
        forged = object.__new__(F)
        object.__setattr__(forged, "_numerator", foreign)
        object.__setattr__(forged, "_denominator", 1)
        self.bad(values=(forged,))

    def test_frozen_records_and_fixed_attestation_flags(self):
        report = self.valid()
        for record, name in ((WHOLE[0], "indices"), (report, "oracle_mean"), (report.fragments[0], "oracle_mean")):
            with self.assertRaises(FrozenInstanceError):
                setattr(record, name, None)
        for name in ("runtime_attested", "method_approved", "sql_conversion_emulated", "scope", "text_origin"):
            with self.assertRaises(ValueError):
                replace(report, **{name: True})

    def test_module_pure_no_runtime_conversion_or_production_imports(self):
        source = Path(m.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imported, {"dataclasses", "decimal", "enum", "fractions", "math"})
        self.assertEqual({alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}, {"re"})
        prohibited = {"open", "eval", "exec", "compile", "__import__", "print", "float", "round"}
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                             and node.func.id in prohibited for node in ast.walk(tree)))
        self.assertNotIn("quantize", source)
        self.assertNotIn("RunRecord", source)
        self.assertNotIn("decode_capture", source)


if __name__ == "__main__":
    unittest.main()
