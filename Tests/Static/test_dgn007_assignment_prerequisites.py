#!/usr/bin/env python3
"""Synthetische PROJECT_SEMANTIC-Fixtures, ohne SQL oder Runtimeattestation."""

import ast
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal, localcontext, ROUND_DOWN
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Tests.Contracts import dgn007_assignment_prerequisites as model


BOUND = model.Binding(1, 1, "a" * 64)
DECLARED = model.Assumption.DECLARED_MODEL_ASSUMPTION


def fixture(major=16, control="AB", baseline=True, variant=False):
    """Vollständig deklarierte Modellwelt; keine tatsächliche Captureherkunft."""
    family = (model.Family(100, 100, 50, model.MARKER),)
    if variant:
        family += (model.Family(101, 100, 50, model.MARKER),)
    query = 101 if variant else 100
    base = (model.Fragment(100, 1, 1, 0, 2, Decimal("7"), 40, 50, 1),) if baseline else ()
    row0 = model.Fragment(query, 2, 10, 0, 4, Decimal("1057.25"), 1110, 1190, 1)
    row1 = model.Fragment(query, 2, 11, 0, 4, Decimal("1057.25"), 2110, 2190, 1)
    sequences = (5, 6, 11, 12, 17, 18)
    rowsets = (base, base, base + (row0,), base + (row0,), base + (row0, row1), base + (row0, row1))
    snapshots = []
    for index, kind in enumerate(model.SnapshotKind):
        generation = 100 + index
        coverage = tuple(model.Coverage(f.query_id,
                           model.CoverageState.DECLARED_ABSENT if variant and f.query_id == 101 and index < 2
                           else model.CoverageState.PRESENT_COMPLETE, generation) for f in family)
        snapshots.append(model.Snapshot(kind, sequences[index], BOUND, generation, coverage,
                                       tuple(replace(r, capture_generation=generation) for r in rowsets[index])))
    requests = []
    for index, stage in enumerate(model.Stage):
        condition = "A" if stage is model.Stage.PRIOR else control[index - 1]
        pairs = model.PAIRS if condition == "A" else (model.PAIRS[1], model.PAIRS[0], model.PAIRS[2], model.PAIRS[3])
        for ordinal, (group, status, rows) in enumerate(pairs, 1):
            sequence = ordinal if index == 0 else 6 + ordinal if index == 1 else 12 + ordinal
            requests.append(model.Request(stage, ordinal, sequence, BOUND, index * 4 + ordinal,
                                          group, status, None if index == 0 else rows))
    windows = tuple(model.Window(stage, control[index], 10 + index, 1000 + index * 1000,
                                 2000 + index * 1000, 1100 + index * 1000, 1200 + index * 1000)
                    for index, stage in enumerate((model.Stage.T0, model.Stage.T1)))
    return model.ModelCase(BOUND, major, major * 10, 50, control,
                           model.Premises(*((DECLARED,) * 6)),
                           model.Completion(model.DeclaredState.SUCCESS, model.DeclaredState.SUCCESS,
                                            model.DeclaredState.SUCCESS, model.DeclaredState.NOT_ATTEMPTED, False),
                           family, tuple(snapshots), tuple(requests), windows)


def snapshots(case, indexes, transform):
    return replace(case, snapshots=tuple(transform(s) if index in indexes else s
                                        for index, s in enumerate(case.snapshots)))


def change_stage(case, interval, **changes):
    return snapshots(case, range(6), lambda s: replace(s, fragments=tuple(
        replace(r, **changes) if r.interval_id == interval else r for r in s.fragments)))


class ModelTests(unittest.TestCase):
    def result(self, case, outcome=None, issue=None, expected=BOUND):
        result = model.evaluate_model(case, expected)
        self.assertFalse(result.runtime_attested)
        self.assertFalse(result.exact_time_inclusion_claimed)
        self.assertFalse(result.method_approved)
        if outcome is not None:
            self.assertIs(result.outcome, outcome)
        if issue is not None:
            self.assertIn(issue, result.issues)
        return result

    def bad(self, case, issue):
        return self.result(case, model.Outcome.INCONSISTENT, issue)

    def test_positive_nonzero_baseline_all_controls_and_versions(self):
        for major in (15, 16, 17):
            for control in ("AB", "BA", "AA"):
                with self.subTest(major=major, control=control):
                    self.assertEqual(self.result(fixture(major, control), model.Outcome.CONDITIONAL_CONSISTENCY).issues, ())

    def test_zero_baseline_is_conditional_not_observed_freshness(self):
        self.result(fixture(baseline=False), model.Outcome.CONDITIONAL_CONSISTENCY)

    def test_all_six_necessary_assumptions_unknown_or_missing(self):
        for field in fields(model.Premises):
            for state, issue in ((model.Assumption.UNKNOWN, model.Issue.UNKNOWN_PREMISE),
                                 (model.Assumption.MISSING, model.Issue.MISSING_PREMISE)):
                case = fixture()
                with self.subTest(field=field.name, state=state):
                    self.result(replace(case, premises=replace(case.premises, **{field.name: state})),
                                model.Outcome.NOT_ESTABLISHED, issue)

    def test_compensated_unobserved_call_cannot_be_detected_by_identical_counts(self):
        case = fixture()
        unknown = replace(case, premises=replace(case.premises, execution_discipline=model.Assumption.UNKNOWN))
        self.assertEqual(case.snapshots, unknown.snapshots)
        self.result(unknown, model.Outcome.NOT_ESTABLISHED, model.Issue.UNKNOWN_PREMISE)
        # Lügenhaft vollständig deklarierte Premises sind durch pure Mathematik
        # nicht widerlegbar: die positive Folge bleibt ausdrücklich konditional.
        self.result(case, model.Outcome.CONDITIONAL_CONSISTENCY)

    def test_visible_extra_request_is_inconsistent(self):
        case = fixture()
        self.bad(replace(case, requests=case.requests + (case.requests[-1],)), model.Issue.MODEL_OVERFLOW)

    def test_unknown_premise_does_not_hide_mathematical_contradiction(self):
        case = change_stage(fixture(), 10, executions=5)
        case = replace(case, premises=replace(case.premises, complete_visibility=model.Assumption.UNKNOWN))
        result = self.bad(case, model.Issue.STAGE_DELTA_MISMATCH)
        self.assertIn(model.Issue.UNKNOWN_PREMISE, result.issues)

    def test_late_variant_requires_explicit_previous_absence(self):
        for major in (16, 17):
            case = fixture(major=major, variant=True)
            self.result(case, model.Outcome.CONDITIONAL_CONSISTENCY)
            missing = snapshots(case, (0, 1), lambda s: replace(s, coverage=s.coverage[:1]))
            self.result(missing, model.Outcome.NOT_ESTABLISHED, model.Issue.MISSING_COVERAGE)
            unknown = snapshots(case, (0, 1), lambda s: replace(s, coverage=(s.coverage[0], replace(s.coverage[1], state=model.CoverageState.UNKNOWN))))
            self.result(unknown, model.Outcome.NOT_ESTABLISHED, model.Issue.UNKNOWN_COVERAGE)

    def test_unknown_coverage_does_not_hide_known_count_or_type_contradictions(self):
        for changes in ({"executions": 5}, {"execution_type": 3}):
            case = change_stage(fixture(variant=True), 10, **changes)
            case = snapshots(case, (5,), lambda s: replace(s, coverage=(replace(s.coverage[0], state=model.CoverageState.UNKNOWN), s.coverage[1])))
            result = self.bad(case, model.Issue.STAGE_DELTA_MISMATCH)
            self.assertIn(model.Issue.UNKNOWN_COVERAGE, result.issues)
        case = change_stage(fixture(variant=True), 10, executions=5)
        case = snapshots(case, (2,), lambda s: replace(s, coverage=(s.coverage[0], replace(s.coverage[1], state=model.CoverageState.UNKNOWN))))
        self.bad(case, model.Issue.STAGE_DELTA_MISMATCH)

    def test_unknown_coverage_cannot_hide_existing_window_basis_or_partial_excess(self):
        case = change_stage(fixture(variant=True), 1, interval_id=10)
        case = snapshots(case, (5,), lambda s: replace(s, coverage=(replace(s.coverage[0], state=model.CoverageState.UNKNOWN), s.coverage[1])))
        self.bad(case, model.Issue.INTERVAL_MISMATCH)
        for changes in ({"executions": 1, "avg_rows": Decimal("100")},
                        {"executions": 1, "first_ticks": 39},
                        {"executions": 1, "last_ticks": 51}):
            case = fixture()
            case = snapshots(case, (2,), lambda s: replace(s,
                coverage=(replace(s.coverage[0], state=model.CoverageState.UNKNOWN),),
                fragments=(replace(s.fragments[0], **changes),) + s.fragments[1:]))
            self.bad(case, model.Issue.BASELINE_MUTATION)
        case = fixture()
        case = snapshots(case, (5,), lambda s: replace(s,
            coverage=(replace(s.coverage[0], state=model.CoverageState.UNKNOWN),),
            fragments=(replace(s.fragments[0], executions=1, avg_rows=Decimal("100")),) + s.fragments[1:]))
        self.bad(case, model.Issue.FINAL_CAPTURE_CHANGED)

    def test_plan_id_cannot_change_query_within_database_generation(self):
        case = fixture(variant=True)
        def mix(s):
            result = []
            for row in s.fragments:
                if row.interval_id == 10:
                    result += [replace(row, executions=2), replace(row, executions=2, query_id=100)]
                else:
                    result.append(row)
            return replace(s, fragments=tuple(result))
        self.bad(snapshots(case, range(2, 6), mix), model.Issue.BINDING_MISMATCH)
        case = change_stage(case, 11, query_id=100)
        self.bad(case, model.Issue.BINDING_MISMATCH)

    def test_declared_absence_conflicts_with_observed_fragment(self):
        case = fixture(variant=True)
        case = snapshots(case, (2,), lambda s: replace(s, coverage=(s.coverage[0], replace(s.coverage[1], state=model.CoverageState.DECLARED_ABSENT))))
        self.bad(case, model.Issue.FAMILY_MISMATCH)

    def test_family_binding_and_major15_variant_rejected(self):
        case = fixture(variant=True)
        for changes in ({"major": 15, "compatibility_level": 150},
                        {"final_family": (case.final_family[1],)},
                        {"final_family": (case.final_family[0], replace(case.final_family[1], parent_query_id=999))},
                        {"final_family": (replace(case.final_family[0], parent_object_id=999), case.final_family[1])}):
            with self.subTest(changes=tuple(changes)):
                self.bad(replace(case, **changes), model.Issue.FAMILY_MISMATCH)
        self.bad(change_stage(case, 10, query_id=999), model.Issue.FAMILY_MISMATCH)

    def test_scope_major_compatibility_marker_and_condition(self):
        case = fixture()
        for changes in ({"major": 14}, {"major": True}, {"compatibility_level": 170}, {"control_sequence": "BB"}):
            self.bad(replace(case, **changes), model.Issue.SCOPE_MISMATCH)
        self.bad(replace(case, final_family=(replace(case.final_family[0], statement_marker="other"),)), model.Issue.INVALID_RECORD)
        self.bad(replace(case, control_sequence="BA"), model.Issue.SCOPE_MISMATCH)

    def test_digest_lifecycle_and_database_generation_binding(self):
        case = fixture()
        for binding in (replace(BOUND, lifecycle_id=2), replace(BOUND, database_generation=2), replace(BOUND, source_digest="b" * 64)):
            with self.subTest(binding=binding):
                self.result(case, model.Outcome.INCONSISTENT, model.Issue.BINDING_MISMATCH, expected=binding)
                self.bad(snapshots(case, (2,), lambda s: replace(s, binding=binding)), model.Issue.BINDING_MISMATCH)
                self.bad(replace(case, requests=(replace(case.requests[0], binding=binding),) + case.requests[1:]), model.Issue.BINDING_MISMATCH)
        self.result(case, model.Outcome.INCONSISTENT, model.Issue.INVALID_RECORD, expected=replace(BOUND, source_digest="secret"))

    def test_fragment_and_coverage_generation_mix(self):
        case = fixture()
        mixed = snapshots(case, (2,), lambda s: replace(s, fragments=(replace(s.fragments[0], capture_generation=999),) + s.fragments[1:]))
        self.bad(mixed, model.Issue.BINDING_MISMATCH)
        mixed = snapshots(case, (2,), lambda s: replace(s, coverage=(replace(s.coverage[0], capture_generation=999),)))
        self.bad(mixed, model.Issue.BINDING_MISMATCH)
        self.bad(snapshots(case, (2,), lambda s: replace(s, capture_generation=case.snapshots[1].capture_generation)), model.Issue.BINDING_MISMATCH)

    def test_stage_capture_must_precede_next_calls(self):
        case = fixture()
        for ordinal in (6, 13, 17):
            self.bad(snapshots(case, (2,), lambda s: replace(s, ordinal=ordinal)), model.Issue.ORDER_MISMATCH)
        self.bad(replace(case, snapshots=(case.snapshots[0], case.snapshots[2], case.snapshots[1]) + case.snapshots[3:]), model.Issue.ORDER_MISMATCH)

    def test_request_mixes_results_ids_and_completion_order(self):
        case = fixture()
        for changes in ({"returned_rows": None}, {"returned_rows": 229}, {"group_key": 5},
                        {"ordinal": 2}, {"sequence": 20}, {"request_log_id": 1}):
            changed = replace(case, requests=case.requests[:4] + (replace(case.requests[4], **changes),) + case.requests[5:])
            self.bad(changed, model.Issue.ORDER_MISMATCH if "sequence" in changes else model.Issue.REQUEST_MISMATCH)
        self.bad(replace(case, requests=case.requests[:-1]), model.Issue.REQUEST_MISMATCH)

    def test_prior_requests_no_invented_measured_rows_or_qs_profile(self):
        case = fixture()
        reordered = tuple(replace(r, group_key=other.group_key, status_code=other.status_code)
                          for r, other in zip(case.requests[:4], reversed(case.requests[:4])))
        self.result(replace(case, requests=reordered + case.requests[4:]), model.Outcome.CONDITIONAL_CONSISTENCY)
        self.bad(replace(case, requests=(replace(case.requests[0], returned_rows=228),) + case.requests[1:]), model.Issue.REQUEST_MISMATCH)

    def test_delayed_warmup_basis_growth(self):
        case = fixture()
        changed = snapshots(case, range(2, 6), lambda s: replace(s, fragments=(replace(s.fragments[0], executions=3),) + s.fragments[1:]))
        self.bad(changed, model.Issue.BASELINE_MUTATION)

    def test_compensated_disappearing_basis_key_and_new_key(self):
        case = fixture()
        changed = snapshots(case, range(2, 6), lambda s: replace(s, fragments=(replace(s.fragments[0], plan_id=999),) + s.fragments[1:]))
        self.bad(changed, model.Issue.BASELINE_MUTATION)

    def test_baseline_cannot_already_occupy_chosen_window(self):
        self.bad(change_stage(fixture(), 1, interval_id=10), model.Issue.INTERVAL_MISMATCH)

    def test_additional_interval_or_nonregular_type_is_not_filtered(self):
        for changes in ({"interval_id": 9}, {"execution_type": 3}, {"execution_type": 4}):
            self.bad(change_stage(fixture(), 10, **changes), model.Issue.STAGE_DELTA_MISMATCH)

    def test_stage_split_across_two_intervals(self):
        case = fixture()
        def split(s):
            result = []
            for r in s.fragments:
                if r.interval_id == 10:
                    result += [replace(r, executions=2), replace(r, executions=2, interval_id=9)]
                else:
                    result.append(r)
            return replace(s, fragments=tuple(result))
        self.bad(snapshots(case, range(2, 6), split), model.Issue.STAGE_DELTA_MISMATCH)

    def test_disk_memory_fragments_sum_and_weight_exactly(self):
        case = fixture()
        def split(s):
            result = []
            for r in s.fragments:
                if r.interval_id == 10:
                    result += [replace(r, executions=1, avg_rows=Decimal("228"), last_ticks=r.first_ticks),
                               replace(r, executions=3, avg_rows=Decimal("1333.666667"), first_ticks=r.last_ticks)]
                else:
                    result.append(r)
            return replace(s, fragments=tuple(result))
        # Nicht darstellbare gedrittelte Fixturemittelwerte werden nicht gerundet.
        self.bad(snapshots(case, range(2, 6), split), model.Issue.STAGE_DELTA_MISMATCH)
        def exact_split(s):
            result = []
            for r in s.fragments:
                if r.interval_id == 10:
                    result += [replace(r, executions=2, avg_rows=Decimal("228"), last_ticks=r.first_ticks),
                               replace(r, executions=2, avg_rows=Decimal("1886.5"), first_ticks=r.last_ticks)]
                else:
                    result.append(r)
            return replace(s, fragments=tuple(result))
        self.result(snapshots(case, range(2, 6), exact_split), model.Outcome.CONDITIONAL_CONSISTENCY)

    def test_fragment_layout_change_without_aggregate_change_is_valid(self):
        case = fixture()
        def split(s):
            return replace(s, fragments=tuple(part for r in s.fragments for part in
                           ((replace(r, executions=2), replace(r, executions=2)) if r.interval_id == 10 else (r,))))
        self.result(snapshots(case, (3,), split), model.Outcome.CONDITIONAL_CONSISTENCY)

    def test_metrics_or_positive_extrema_cannot_drift_with_same_counts(self):
        case = fixture()
        for changes in ({"avg_rows": Decimal("1057.5")}, {"first_ticks": 1109}, {"last_ticks": 1191}):
            changed = snapshots(case, (5,), lambda s: replace(s, fragments=tuple(replace(r, **changes) if r.interval_id == 10 else r for r in s.fragments)))
            self.bad(changed, model.Issue.FINAL_CAPTURE_CHANGED)
        changed = snapshots(case, range(2, 6), lambda s: replace(s, fragments=(replace(s.fragments[0], first_ticks=39),) + s.fragments[1:]))
        self.bad(changed, model.Issue.BASELINE_MUTATION)

    def test_t0_must_be_unchanged_at_t1_pre(self):
        case = fixture()
        changed = snapshots(case, (3,), lambda s: replace(s, fragments=s.fragments[:1]))
        self.bad(changed, model.Issue.FINAL_CAPTURE_CHANGED)

    def test_zero_rows_not_executions_or_time_evidence(self):
        case = fixture()
        expected = self.result(case).time_relations
        def zero(s):
            return replace(s, fragments=s.fragments + tuple(replace(r, executions=0, avg_rows=None,
                                                                    first_ticks=2000, last_ticks=0)
                                                             for r in s.fragments if r.interval_id == 10))
        changed = self.result(snapshots(case, range(2, 6), zero), model.Outcome.CONDITIONAL_CONSISTENCY)
        self.assertEqual(changed.time_relations, expected)

    def test_null_negative_bool_counts_and_invalid_metrics(self):
        for changes in ({"executions": None}, {"executions": -1}, {"executions": True},
                        {"avg_rows": None}, {"avg_rows": Decimal("NaN")}, {"avg_rows": Decimal("Infinity")},
                        {"avg_rows": Decimal("-1")}, {"avg_rows": 1057.25},
                        {"first_ticks": None}, {"first_ticks": model.MAX_SQL_TICKS + 1}):
            with self.subTest(changes=changes):
                self.bad(change_stage(fixture(), 10, **changes), model.Issue.INVALID_FRAGMENT)

    def test_model_overflow_no_truncation(self):
        case = fixture()
        self.bad(snapshots(case, (2,), lambda s: replace(s, fragments=s.fragments * 33)), model.Issue.MODEL_OVERFLOW)
        self.bad(change_stage(case, 10, executions=model.MAX_MODEL_COUNT + 1), model.Issue.INVALID_FRAGMENT)
        self.bad(change_stage(case, 10, avg_rows=Decimal("1E-7")), model.Issue.MODEL_OVERFLOW)

    def test_exact_math_independent_of_decimal_context(self):
        with localcontext() as context:
            context.prec = 1
            context.rounding = ROUND_DOWN
            self.result(fixture(), model.Outcome.CONDITIONAL_CONSISTENCY)

    def test_one_tick_g13_violation_is_reported_not_healed(self):
        case = change_stage(fixture(), 10, first_ticks=1099)
        result = self.result(case, model.Outcome.CONDITIONAL_CONSISTENCY)
        self.assertEqual(result.time_relations[0].first_minus_request_start, -1)
        self.assertFalse(result.time_relations[0].qs_inside_request)
        self.assertTrue(result.time_relations[0].qs_inside_catalog)

    def test_time_relations_are_independent_and_boundary_exact(self):
        case = fixture()
        equal = change_stage(change_stage(case, 10, first_ticks=1100), 10, last_ticks=1200)
        relation = self.result(equal, model.Outcome.CONDITIONAL_CONSISTENCY).time_relations[0]
        self.assertTrue(relation.qs_inside_request)
        self.assertEqual((relation.first_minus_request_start, relation.last_minus_request_finish), (0, 0))
        catalog_end = change_stage(case, 10, last_ticks=2000)
        self.assertFalse(self.result(catalog_end).time_relations[0].qs_inside_catalog)
        shifted = replace(case, windows=(replace(case.windows[0], request_start_ticks=999), case.windows[1]))
        self.assertFalse(self.result(shifted).time_relations[0].request_inside_catalog)
        self.assertTrue(self.result(shifted).time_relations[0].qs_inside_request)

    def test_equal_request_bounds_and_tick_domain(self):
        case = change_stage(change_stage(fixture(), 10, first_ticks=1100), 10, last_ticks=1100)
        case = replace(case, windows=(replace(case.windows[0], request_finish_ticks=1100), case.windows[1]))
        self.assertTrue(self.result(case).time_relations[0].qs_inside_request)
        self.bad(replace(case, windows=(replace(case.windows[0], interval_end_ticks=model.MAX_SQL_TICKS + 1), case.windows[1])), model.Issue.INTERVAL_MISMATCH)

    def test_window_rotation_identity_overlap_and_type(self):
        case = fixture()
        for changes in ({"interval_id": 10}, {"interval_start_ticks": 1999}, {"stage": "T1"}):
            self.bad(replace(case, windows=(case.windows[0], replace(case.windows[1], **changes))), model.Issue.INTERVAL_MISMATCH)

    def test_cleanup_failure_dominates_timeout_and_invalid_records_recovery_no_heal(self):
        case = change_stage(fixture(), 10, executions=-1)
        c = replace(case.completion, first_absence=model.DeclaredState.FAILURE,
                    recovery=model.DeclaredState.SUCCESS, timed_out=True)
        result = self.bad(replace(case, completion=c), model.Issue.CLEANUP_FAILURE)
        self.assertEqual(result.issues[:2], (model.Issue.CLEANUP_FAILURE, model.Issue.TIMEOUT))
        self.assertIn(model.Issue.INVALID_FRAGMENT, result.issues)

    def test_timeout_and_unknown_completion(self):
        case = fixture()
        self.bad(replace(case, completion=replace(case.completion, timed_out=True)), model.Issue.TIMEOUT)
        self.result(replace(case, completion=replace(case.completion, cleanup=model.DeclaredState.UNKNOWN)),
                    model.Outcome.NOT_ESTABLISHED, model.Issue.UNKNOWN_COMPLETION)
        self.bad(replace(case, completion=replace(case.completion, recovery=model.DeclaredState.FAILURE)), model.Issue.CLEANUP_FAILURE)

    def test_malformed_unconstructed_records_and_bool_premises(self):
        case = fixture()
        for malformed in (None, model.ModelCase.__new__(model.ModelCase)):
            self.result(malformed, model.Outcome.INCONSISTENT, model.Issue.INVALID_RECORD)
        broken = model.Snapshot.__new__(model.Snapshot)
        self.bad(replace(case, snapshots=(broken,) + case.snapshots[1:]), model.Issue.INVALID_RECORD)
        self.bad(replace(case, premises=replace(case.premises, execution_discipline=True)), model.Issue.INVALID_RECORD)
        self.bad(replace(case, snapshots=list(case.snapshots)), model.Issue.INVALID_RECORD)

    def test_foreign_object_getters_and_equality_are_not_executed(self):
        class Foreign:
            def __getattr__(self, name):
                raise RuntimeError("must not execute getter")

            def __eq__(self, other):
                raise RuntimeError("must not execute equality")

        foreign = Foreign()
        self.result(foreign, model.Outcome.INCONSISTENT, model.Issue.INVALID_RECORD)
        case = fixture()
        self.result(case, model.Outcome.INCONSISTENT, model.Issue.INVALID_RECORD, expected=foreign)
        self.bad(replace(case, binding=replace(BOUND, source_digest=foreign)), model.Issue.INVALID_RECORD)
        malformed = snapshots(case, (2,), lambda s: replace(s, fragments=(foreign,)))
        self.bad(malformed, model.Issue.INVALID_RECORD)
        self.bad(replace(case, compatibility_level=foreign), model.Issue.SCOPE_MISMATCH)
        self.bad(replace(case, windows=(replace(case.windows[0], stage=foreign), case.windows[1])), model.Issue.INTERVAL_MISMATCH)
        self.bad(snapshots(case, (2,), lambda s: replace(s, capture_generation=foreign)), model.Issue.INVALID_RECORD)
        self.bad(change_stage(case, 10, capture_generation=foreign), model.Issue.INVALID_RECORD)

    def test_every_independent_fragment_validated_even_after_early_invalid_record(self):
        case = fixture()
        case = snapshots(case, (0,), lambda s: replace(s, binding=replace(BOUND, lifecycle_id=99)))
        case = change_stage(case, 11, executions=None)
        result = self.bad(case, model.Issue.BINDING_MISMATCH)
        self.assertIn(model.Issue.INVALID_FRAGMENT, result.issues)

    def test_frozen_records_and_results(self):
        case = fixture()
        for obj, field in ((case, "major"), (case.snapshots[0], "ordinal"), (case.requests[0], "ordinal"),
                           (self.result(case), "outcome")):
            with self.assertRaises(FrozenInstanceError):
                setattr(obj, field, None)

    def test_pure_stdlib_source_no_runtime_or_v1_import(self):
        source = Path(model.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(modules, {"dataclasses", "decimal", "enum", "fractions"})
        self.assertFalse(any(isinstance(node, ast.Import) for node in ast.walk(tree)))
        prohibited = {"open", "eval", "exec", "compile", "__import__", "print"}
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                             and node.func.id in prohibited for node in ast.walk(tree)))
        self.assertNotIn("RunRecord", source)
        self.assertNotIn("decode_capture", source)


if __name__ == "__main__":
    unittest.main()
