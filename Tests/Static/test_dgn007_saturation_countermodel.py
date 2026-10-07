"""Synthetische Oracle-Gegenproben; keine SQL-/Runtime- oder Methodenabnahme."""

import ast
import importlib
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal, localcontext
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Tests.Contracts import dgn007_saturation_countermodel as m


DECL = m.Assumption.DECLARED_MODEL_ASSUMPTION
SUPPORTED = m.Claim.CONDITIONALLY_SUPPORTED
UNKNOWN = m.Claim.NOT_ESTABLISHED
REFUTED = m.Claim.REFUTED
BINDING = m.Binding(1, 1, "a" * 64)


def fixture(major=16, excluded=False):
    calls = tuple(m.OracleCall(i + 1, stage, n + 1, base + n * 10, base + n * 10 + 1,
                              BINDING, DECL, 1)
                  for i, (stage, n, base) in enumerate((stage, n, base)
                      for stage, base in ((m.Stage.PRIOR, 10), (m.Stage.T0, 100), (m.Stage.T1, 200))
                      for n in range(4)))
    metrics = m.Metrics(*(Decimal(n) for n in (1, 2, 3, 4)))
    raw = (
        m.RawFragment(12, 1, 1, 0, 4, (1, 2, 3, 4), metrics, 40, 50, BINDING, 1),
        m.RawFragment(12, 2, 10, 0, 4, (5, 6, 7, 8), metrics, 1110, 1190, BINDING, 1),
        m.RawFragment(12, 3, 11, 0, 4, (9, 10, 11, 12), metrics, 2110, 2190, BINDING, 1),
    )
    snapshots = tuple(m.Snapshot(kind, index + 1, start, start + 1, BINDING, 1, 1, 1,
                                (m.FamilyMember(12, 12),), (m.Coverage(12, m.CoverageState.COMPLETE),),
                                tuple(replace(row, acquisition_id=index + 1)
                                      for row in raw[(1 if excluded else 0):limit]))
                      for index, (kind, start, limit) in enumerate(zip(m.SnapshotKind, (50, 140, 240, 250), (1, 2, 3, 3))))
    windows = tuple(m.Window(stage, interval, start, start + 1000, start + 100, start + 200, interval)
                    for stage, interval, start in ((m.Stage.T0, 10, 1000), (m.Stage.T1, 11, 2000)))
    return m.CounterCase(BINDING, major, major * 10, 12,
                         m.PriorMode.HISTORICALLY_EXCLUDED if excluded else m.PriorMode.READ_WRITE,
                         m.Premises(DECL, DECL, DECL, DECL, DECL, DECL), calls, snapshots, windows,
                         (m.StatePoint(1, m.QsState.READ_WRITE_ALL),), ())


def alter_snapshot(case, index, **changes):
    items = list(case.snapshots)
    items[index] = replace(items[index], **changes)
    return replace(case, snapshots=tuple(items))


def alter_row(case, snapshot_index, row_index, **changes):
    rows = list(case.snapshots[snapshot_index].fragments)
    rows[row_index] = replace(rows[row_index], **changes)
    return alter_snapshot(case, snapshot_index, fragments=tuple(rows))


class CountermodelTests(unittest.TestCase):
    def evaluate(self, case):
        result = m.evaluate_countermodel(case, BINDING)
        self.assertFalse(result.runtime_attested)
        self.assertFalse(result.method_approved)
        self.assertFalse(result.exact_time_inclusion_claimed)
        self.assertEqual(result.validation_scope, "PROJECT_SEMANTIC")
        return result

    def test_saturation_rw_and_explicit_off_all_versions(self):
        for major in (15, 16, 17):
            for excluded in (False, True):
                with self.subTest(major=major, excluded=excluded):
                    r = self.evaluate(fixture(major, excluded))
                    self.assertEqual((r.call_coverage, r.collective_bucket, r.permanent_state), (SUPPORTED,) * 3)
                    self.assertEqual(r.issues, ())

    def test_unknown_necessary_premises_never_support_call_claim(self):
        for name in ("actual_closed_universe", "eligible_target_statement", "truthful_successful_completion", "coherent_visible_enumeration"):
            for state in (m.Assumption.UNKNOWN, m.Assumption.MISSING):
                c = fixture()
                r = self.evaluate(replace(c, premises=replace(c.premises, **{name: state})))
                self.assertEqual(r.call_coverage, UNKNOWN)
                self.assertIn(m.Issue.UNKNOWN_PREMISE, r.issues)

    def test_off_zero_not_historical_exclusion_proof(self):
        c = fixture(excluded=True)
        for assumption in (m.Assumption.UNKNOWN, m.Assumption.MISSING):
            r = self.evaluate(replace(c, premises=replace(c.premises, historical_prior_exclusion=assumption)))
            self.assertEqual(r.call_coverage, UNKNOWN)
            self.assertIn(m.Issue.HISTORICAL_EXCLUSION_MISSING, r.issues)

    def test_planned_twelve_does_not_replace_actual_success(self):
        c = fixture()
        c = replace(c, calls=c.calls[:-1] + (replace(c.calls[-1], successful=m.Assumption.UNKNOWN),))
        self.assertEqual(self.evaluate(c).call_coverage, UNKNOWN)
        c = replace(c, calls=c.calls[:-1])
        self.assertEqual(self.evaluate(c).call_coverage, REFUTED)

    def test_one_call_must_mean_one_target_statement(self):
        for count in (0, 2):
            c = fixture()
            c = replace(c, calls=(replace(c.calls[0], target_statement_count=count),) + c.calls[1:])
            self.assertIn(m.Issue.POPULATION_MISMATCH, self.evaluate(c).issues)

    def test_repeated_historical_tokens_between_snapshots_are_valid(self):
        c = fixture()
        self.assertEqual(c.snapshots[0].fragments[0].tokens, c.snapshots[-1].fragments[0].tokens)
        self.assertEqual(self.evaluate(c).call_coverage, SUPPORTED)

    def test_duplicate_token_inside_single_fragment(self):
        r = self.evaluate(alter_row(fixture(), 1, 1, tokens=(5, 6, 7, 7)))
        self.assertEqual(r.call_coverage, REFUTED)
        self.assertIn(m.Issue.NON_INJECTIVE_COUNT, r.issues)

    def test_duplicate_join_or_fragment_overrides_correct_total(self):
        c = fixture()
        rows = c.snapshots[1].fragments
        duplicate = replace(rows[1], count=2, tokens=(5, 6))
        c = alter_snapshot(c, 1, fragments=(rows[0], duplicate, duplicate))
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, REFUTED)
        self.assertIn(m.Issue.NON_INJECTIVE_COUNT, r.issues)

    def test_foreign_compensation_is_checked_before_filtering(self):
        for changes in ({"tokens": (5, 6, 7, 99)}, {"query_id": 99, "tokens": (5, 6, 7, 99)}):
            r = self.evaluate(alter_row(fixture(), 1, 1, **changes))
            self.assertEqual(r.call_coverage, REFUTED)
            self.assertIn(m.Issue.FOREIGN_OR_FUTURE_TOKEN, r.issues)

    def test_future_t1_cannot_replace_missing_t0(self):
        r = self.evaluate(alter_row(fixture(), 1, 1, tokens=(5, 6, 7, 9)))
        self.assertIn(m.Issue.FOREIGN_OR_FUTURE_TOKEN, r.issues)
        self.assertEqual(r.call_coverage, REFUTED)

    def test_fifth_prior_contradicts_closed_oracle_population(self):
        c = fixture()
        c = alter_row(c, 0, 0, count=5, tokens=(1, 2, 3, 4, 99))
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, REFUTED)
        self.assertIn(m.Issue.FOREIGN_OR_FUTURE_TOKEN, r.issues)

    def test_delayed_prior_cannot_compensate_off_t0(self):
        c = alter_row(fixture(excluded=True), 1, 0, tokens=(5, 6, 7, 4))
        self.assertEqual(self.evaluate(c).call_coverage, REFUTED)

    def test_incomplete_injective_subset_does_not_assume_equality(self):
        c = alter_row(fixture(), 1, 1, count=3, tokens=(5, 6, 7))
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, UNKNOWN)
        self.assertIn(m.Issue.SATURATION_MISSING, r.issues)

    def test_count_token_mismatch_and_null_negative_counts(self):
        for count in (None, -1, 3):
            r = self.evaluate(alter_row(fixture(), 3, 2, count=count))
            self.assertEqual(r.call_coverage, REFUTED)
            self.assertIn(m.Issue.INVALID_FRAGMENT, r.issues)

    def test_zero_rows_do_not_add_executions_or_positive_extrema(self):
        c = fixture()
        for index in range(4):
            zero = replace(c.snapshots[index].fragments[0], count=0, tokens=(), averages=None,
                           first_ticks=0, last_ticks=m.MAX_TICKS)
            c = alter_snapshot(c, index, fragments=c.snapshots[index].fragments + (zero,))
        self.assertEqual(self.evaluate(c).collective_bucket, SUPPORTED)

    def test_original_population_replaced_across_keys(self):
        c = fixture()
        rows = list(c.snapshots[1].fragments)
        rows[0] = replace(rows[0], tokens=(1, 2, 3, 5))
        rows[1] = replace(rows[1], tokens=(4, 6, 7, 8))
        r = self.evaluate(alter_snapshot(c, 1, fragments=tuple(rows)))
        self.assertEqual(r.call_coverage, SUPPORTED)
        self.assertEqual(r.collective_bucket, REFUTED)
        self.assertIn(m.Issue.STABLE_SIGNATURE_CHANGED, r.issues)

    def test_destruction_epoch_or_explicit_operation_blocks_claim(self):
        for c in (alter_snapshot(fixture(), 2, ledger_epoch=2), replace(fixture(), destructive_ordinals=(150,))):
            r = self.evaluate(c)
            self.assertEqual(r.call_coverage, REFUTED)
            self.assertIn(m.Issue.DESTRUCTIVE_CHANGE, r.issues)

    def test_source_lifecycle_generation_binding(self):
        c = fixture()
        for binding in (replace(BINDING, lifecycle_id=2), replace(BINDING, database_generation=2), replace(BINDING, source_digest="b" * 64)):
            self.assertEqual(self.evaluate(alter_row(c, 1, 1, binding=binding)).call_coverage, REFUTED)
        for field in ("generation_before", "generation_after"):
            self.assertEqual(self.evaluate(alter_snapshot(c, 1, **{field: 2})).call_coverage, REFUTED)

    def test_acquisition_replay_or_fragment_mix(self):
        c = fixture()
        for changed in (alter_row(c, 1, 1, acquisition_id=1), alter_snapshot(c, 1, acquisition_id=1)):
            self.assertIn(m.Issue.ACQUISITION_MISMATCH, self.evaluate(changed).issues)

    def test_t0_capture_must_precede_t1(self):
        c = alter_snapshot(fixture(), 1, started=235, finished=236)
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, UNKNOWN)
        self.assertEqual(r.collective_bucket, REFUTED)

    def test_capture_finish_not_start_must_precede_next_stage(self):
        for index, finish in ((0, 100), (1, 200)):
            r = self.evaluate(alter_snapshot(fixture(), index, finished=finish))
            self.assertEqual(r.collective_bucket, REFUTED)
            self.assertIn(m.Issue.ORDER_MISMATCH, r.issues)

    def test_overlapping_acquisitions_or_call_receipts(self):
        c = fixture()
        self.assertIn(m.Issue.ACQUISITION_MISMATCH, self.evaluate(alter_snapshot(c, 2, started=141)).issues)
        c = replace(c, calls=(replace(c.calls[0], finished=20),) + c.calls[1:])
        self.assertIn(m.Issue.ORDER_MISMATCH, self.evaluate(c).issues)

    def test_split_interval_preserves_calls_but_not_bucket(self):
        c = fixture()
        r = c.snapshots[1].fragments[1]
        a = replace(r, count=2, tokens=(5, 6))
        b = replace(r, count=2, tokens=(7, 8), interval_id=20)
        for index in (1, 2, 3):
            rows = c.snapshots[index].fragments
            c = alter_snapshot(c, index, fragments=(rows[0], replace(a, acquisition_id=index + 1),
                                                    replace(b, acquisition_id=index + 1)) + rows[2:])
        result = self.evaluate(c)
        self.assertEqual(result.call_coverage, SUPPORTED)
        self.assertEqual(result.collective_bucket, REFUTED)

    def test_extra_execution_type_or_reused_interval(self):
        c = fixture()
        for execution_type in (3, 4):
            self.assertEqual(self.evaluate(alter_row(c, 1, 1, execution_type=execution_type)).collective_bucket, REFUTED)
        self.assertEqual(self.evaluate(alter_row(c, 1, 1, interval_id=1)).collective_bucket, REFUTED)

    def test_unknown_execution_type_values_are_invalid_records(self):
        for execution_type in (1, 2):
            self.assertEqual(self.evaluate(alter_row(fixture(), 1, 1, execution_type=execution_type)).issues,
                             (m.Issue.INVALID_RECORD,))

    def test_positive_aborted_types_cannot_represent_successful_oracle_calls(self):
        for execution_type in (3, 4):
            c = fixture()
            for index in range(4):
                c = alter_row(c, index, 0, execution_type=execution_type)
            r = self.evaluate(c)
            self.assertEqual((r.call_coverage, r.collective_bucket), (REFUTED, REFUTED))
            self.assertIn(m.Issue.INVALID_FRAGMENT, r.issues)

    def test_zero_aborted_fragments_do_not_claim_successful_executions(self):
        for execution_type in (3, 4):
            c = fixture()
            s = c.snapshots[-1]
            zero = replace(s.fragments[0], execution_type=execution_type, count=0, tokens=(), averages=None,
                           first_ticks=None, last_ticks=None)
            self.assertEqual(self.evaluate(alter_snapshot(c, 3, fragments=s.fragments + (zero,))).call_coverage, SUPPORTED)

    def test_common_binding_also_binds_state_claim(self):
        c = fixture()
        self.assertEqual(self.evaluate(replace(c, binding=replace(BINDING, lifecycle_id=2))).permanent_state, REFUTED)
        c = replace(c, calls=(replace(c.calls[0], binding=replace(BINDING, source_digest="b" * 64)),) + c.calls[1:])
        self.assertEqual(self.evaluate(c).permanent_state, REFUTED)

    def test_state_end_domain_requires_bound_ordered_final_acquisition(self):
        c = fixture()
        changes = ({"started": 220, "finished": 221}, {"generation_before": 2},
                   {"generation_after": 2}, {"binding": replace(BINDING, lifecycle_id=2)},
                   {"acquisition_id": 1}, {"started": 240, "finished": 241})
        for change in changes:
            self.assertEqual(self.evaluate(alter_snapshot(c, 3, **change)).permanent_state, REFUTED)
        # Reiner Ledger-/Metrikfehler verändert keinen gültigen State-Endanker.
        self.assertEqual(self.evaluate(alter_row(c, 3, 2, count=None)).permanent_state, SUPPORTED)

    def test_state_domain_requires_valid_call_population_and_serial_order(self):
        c = fixture()
        bad_calls = ((replace(c.calls[0], started=300, finished=301),) + c.calls[1:],
                     c.calls[:5] + (replace(c.calls[5], finished=9000),) + c.calls[6:],
                     (replace(c.calls[0], stage=m.Stage.T1),) + c.calls[1:],
                     (replace(c.calls[0], ordinal=2),) + c.calls[1:])
        for calls in bad_calls:
            self.assertEqual(self.evaluate(replace(c, calls=calls)).permanent_state, REFUTED)

    def test_pulse_describes_only_own_interval(self):
        c = fixture()
        c = replace(c, windows=(replace(c.windows[0], pulse_interval_id=99), c.windows[1]))
        r = self.evaluate(c)
        self.assertEqual(r.collective_bucket, SUPPORTED)
        self.assertFalse(r.time_relations[0].pulse_matches_bucket)

    def test_all_four_metrics_and_positive_extrema_are_stable(self):
        for name in ("duration", "cpu", "logical_reads", "rows"):
            c = fixture()
            old = c.snapshots[2].fragments[1].averages
            c = alter_row(c, 2, 1, averages=replace(old, **{name: Decimal("9")}))
            r = self.evaluate(c)
            self.assertEqual(r.call_coverage, SUPPORTED)
            self.assertIn(m.Issue.STABLE_SIGNATURE_CHANGED, r.issues)
        for name, value in (("first_ticks", 1109), ("last_ticks", 1191)):
            self.assertIn(m.Issue.STABLE_SIGNATURE_CHANGED, self.evaluate(alter_row(fixture(), 2, 1, **{name: value})).issues)

    def test_final_rebind_detects_t0_changes(self):
        r = self.evaluate(alter_row(fixture(), 3, 1, last_ticks=1191))
        self.assertEqual(r.collective_bucket, REFUTED)

    def test_memory_disk_fragmentation_without_rounding_is_equivalent(self):
        c = fixture()
        for index in (1, 2, 3):
            rows = c.snapshots[index].fragments
            a = replace(rows[1], count=2, tokens=(5, 6))
            b = replace(rows[1], count=2, tokens=(7, 8))
            c = alter_snapshot(c, index, fragments=(rows[0], a, b) + rows[2:])
        self.assertEqual(self.evaluate(c).collective_bucket, SUPPORTED)

    def test_float_fragment_rounding_is_not_healed_by_fraction_or_epsilon(self):
        c = fixture()
        for index in (2, 3):
            rows = c.snapshots[index].fragments
            a = replace(rows[1], count=2, tokens=(5, 6), averages=replace(rows[1].averages, cpu=Decimal("2.0000000000000004")))
            b = replace(rows[1], count=2, tokens=(7, 8))
            c = alter_snapshot(c, index, fragments=(rows[0], a, b) + rows[2:])
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, SUPPORTED)
        self.assertEqual(r.collective_bucket, REFUTED)
        with localcontext() as ctx:
            ctx.prec = 1
            self.assertEqual(self.evaluate(c), r)

    def test_late_unexecuted_variant_does_not_destroy_call_saturation(self):
        c = fixture()
        for index in range(4):
            s = c.snapshots[index]
            late = index == 3
            family = s.family + ((m.FamilyMember(13, 12),) if late else ())
            coverage = s.coverage + (m.Coverage(13, m.CoverageState.COMPLETE if late else m.CoverageState.UNKNOWN),)
            c = alter_snapshot(c, index, family=family, coverage=coverage)
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, SUPPORTED)
        self.assertEqual(r.collective_bucket, UNKNOWN)
        self.assertIn(m.Issue.UNKNOWN_COVERAGE, r.issues)

    def test_declared_historical_absence_is_explicit_not_inferred_zero(self):
        c = fixture()
        for index in range(4):
            s = c.snapshots[index]
            late = index == 3
            c = alter_snapshot(c, index, family=s.family + ((m.FamilyMember(13, 12),) if late else ()),
                               coverage=s.coverage + (m.Coverage(13, m.CoverageState.COMPLETE if late else m.CoverageState.DECLARED_ABSENT),))
        self.assertEqual(self.evaluate(c).collective_bucket, SUPPORTED)

    def test_parent_variant_version_and_plan_query_binding(self):
        c = fixture()
        self.assertEqual(self.evaluate(alter_row(c, 3, 1, query_id=13)).call_coverage, REFUTED)
        c = alter_snapshot(c, 3, family=(m.FamilyMember(12, 12), m.FamilyMember(13, 99)))
        self.assertEqual(self.evaluate(c).call_coverage, REFUTED)
        self.assertEqual(self.evaluate(alter_row(fixture(), 2, 1, plan_id=1)).call_coverage, SUPPORTED)
        # Eine gültige zusätzliche Variante darf PlanId1 nicht übernehmen.
        c = fixture()
        for index in range(4):
            s = c.snapshots[index]
            c = alter_snapshot(c, index, family=s.family + (m.FamilyMember(13, 12),),
                               coverage=s.coverage + (m.Coverage(13, m.CoverageState.COMPLETE),))
        c = alter_row(c, 3, 2, query_id=13, plan_id=1)
        self.assertEqual(self.evaluate(c).call_coverage, REFUTED)
        self.assertEqual(self.evaluate(replace(c, major=15, compatibility_level=150)).call_coverage, REFUTED)

    def test_unknown_does_not_hide_later_visible_contradictions(self):
        c = fixture()
        c = replace(c, premises=replace(c.premises, actual_closed_universe=m.Assumption.UNKNOWN))
        c = alter_row(c, 3, 2, tokens=(9, 10, 11, 99))
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, REFUTED)
        self.assertIn(m.Issue.UNKNOWN_PREMISE, r.issues)
        self.assertIn(m.Issue.FOREIGN_OR_FUTURE_TOKEN, r.issues)

    def test_state_history_unknown_or_point_captures_not_continuity(self):
        c = fixture()
        c = replace(c, premises=replace(c.premises, complete_state_history=m.Assumption.UNKNOWN))
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, SUPPORTED)
        self.assertEqual(r.permanent_state, UNKNOWN)

    def test_known_state_gap_dominates_missing_history(self):
        c = fixture()
        c = replace(c, premises=replace(c.premises, complete_state_history=m.Assumption.UNKNOWN),
                    state_history=(m.StatePoint(1, m.QsState.READ_WRITE_ALL), m.StatePoint(70, m.QsState.READ_ONLY)))
        r = self.evaluate(c)
        self.assertEqual(r.permanent_state, REFUTED)
        self.assertIn(m.Issue.STATE_HISTORY_MISSING, r.issues)
        self.assertIn(m.Issue.STATE_NOT_CONTINUOUS, r.issues)

    def test_unknown_history_does_not_extrapolate_prior_state_into_domain(self):
        for excluded in (False, True):
            c = fixture(excluded=excluded)
            c = replace(c, premises=replace(c.premises, complete_state_history=m.Assumption.UNKNOWN),
                        state_history=(m.StatePoint(1, m.QsState.READ_ONLY),))
            r = self.evaluate(c)
            self.assertEqual(r.permanent_state, UNKNOWN)
            self.assertNotIn(m.Issue.STATE_NOT_CONTINUOUS, r.issues)
            c = replace(c, premises=replace(c.premises, complete_state_history=DECL))
            self.assertEqual(self.evaluate(c).permanent_state, REFUTED)

    def test_read_only_gap_without_call_and_none_do_not_refute_coverage(self):
        for state in (m.QsState.READ_ONLY, m.QsState.READ_WRITE_NONE, m.QsState.OFF):
            c = fixture()
            c = replace(c, state_history=(m.StatePoint(1, m.QsState.READ_WRITE_ALL), m.StatePoint(70, state),
                                         m.StatePoint(90, m.QsState.READ_WRITE_ALL)))
            r = self.evaluate(c)
            self.assertEqual((r.call_coverage, r.collective_bucket), (SUPPORTED, SUPPORTED))
            self.assertEqual(r.permanent_state, REFUTED)

    def test_state_scope_includes_final_capture_after_last_call(self):
        c = fixture()
        c = replace(c, state_history=c.state_history + (m.StatePoint(245, m.QsState.READ_ONLY),))
        r = self.evaluate(c)
        self.assertEqual(r.call_coverage, SUPPORTED)
        self.assertEqual(r.permanent_state, REFUTED)

    def test_one_tick_and_equal_request_boundaries_do_not_change_bucket_claim(self):
        for start, finish in ((1111, 1200), (1110, 1190), (1190, 1190)):
            c = fixture()
            c = replace(c, windows=(replace(c.windows[0], request_start_ticks=start, request_finish_ticks=finish), c.windows[1]))
            r = self.evaluate(c)
            self.assertEqual(r.collective_bucket, SUPPORTED)
            self.assertEqual(r.time_relations[0].first_minus_start, 1110 - start)
            self.assertEqual(r.time_relations[0].within_request_bounds, start <= 1110 <= 1190 <= finish)

    def test_positive_and_zero_extrema_order_are_distinct(self):
        self.assertEqual(self.evaluate(alter_row(fixture(), 2, 1, first_ticks=1191)).call_coverage, REFUTED)
        c = fixture()
        zero = replace(c.snapshots[-1].fragments[-1], count=0, tokens=(), first_ticks=10, last_ticks=1)
        c = alter_snapshot(c, 3, fragments=c.snapshots[-1].fragments + (zero,))
        self.assertEqual(self.evaluate(c).collective_bucket, SUPPORTED)

    def test_model_bounds_and_numeric_representations(self):
        c = fixture()
        for value in (Decimal("NaN"), Decimal("Infinity"), Decimal("-1"), Decimal("1e-31"), Decimal("1e21"), 1.0, True):
            row = c.snapshots[-1].fragments[-1]
            r = self.evaluate(alter_row(c, 3, 2, averages=replace(row.averages, cpu=value)))
            self.assertEqual(r.issues, (m.Issue.INVALID_RECORD,))
        for value in (True, -1, m.MAX_TICKS + 1):
            self.assertEqual(self.evaluate(alter_row(c, 3, 2, last_ticks=value)).issues, (m.Issue.INVALID_RECORD,))
        self.assertEqual(self.evaluate(alter_snapshot(c, 3, fragments=c.snapshots[3].fragments * 22)).issues, (m.Issue.INVALID_RECORD,))

    def test_frozen_records_and_result(self):
        for record, name in ((fixture(), "major"), (self.evaluate(fixture()), "runtime_attested")):
            with self.assertRaises(FrozenInstanceError):
                setattr(record, name, True)

    def test_malformed_foreign_values_and_uninitialized_records_are_fixed(self):
        class Foreign:
            def __getattr__(self, name):
                raise RuntimeError("foreign getter")
            def __eq__(self, other):
                raise RuntimeError("foreign equality")
        bad = Foreign()
        c = fixture()
        checks = [(bad, BINDING), (c, bad), (m.CounterCase.__new__(m.CounterCase), BINDING)]
        for field in fields(m.CounterCase):
            checks.append((replace(c, **{field.name: bad}), BINDING))
        for field in fields(m.Snapshot):
            checks.append((alter_snapshot(c, 1, **{field.name: bad}), BINDING))
        for field in fields(m.RawFragment):
            checks.append((alter_row(c, 1, 1, **{field.name: bad}), BINDING))
        for field in fields(m.Binding):
            checks.append((replace(c, binding=replace(BINDING, **{field.name: bad})), BINDING))
        for field in fields(m.Premises):
            checks.append((replace(c, premises=replace(c.premises, **{field.name: bad})), BINDING))
        for field in fields(m.OracleCall):
            checks.append((replace(c, calls=(replace(c.calls[0], **{field.name: bad}),) + c.calls[1:]), BINDING))
        for field in fields(m.FamilyMember):
            checks.append((alter_snapshot(c, 1, family=(replace(c.snapshots[1].family[0], **{field.name: bad}),)), BINDING))
        for field in fields(m.Coverage):
            checks.append((alter_snapshot(c, 1, coverage=(replace(c.snapshots[1].coverage[0], **{field.name: bad}),)), BINDING))
        for field in fields(m.Metrics):
            checks.append((alter_row(c, 1, 1, averages=replace(c.snapshots[1].fragments[1].averages, **{field.name: bad})), BINDING))
        for field in fields(m.Window):
            checks.append((replace(c, windows=(replace(c.windows[0], **{field.name: bad}), c.windows[1])), BINDING))
        for field in fields(m.StatePoint):
            checks.append((replace(c, state_history=(replace(c.state_history[0], **{field.name: bad}),)), BINDING))
        checks += [(alter_snapshot(c, 1, fragments=(bad,)), BINDING),
                   (alter_snapshot(c, 1, fragments=(m.RawFragment.__new__(m.RawFragment),)), BINDING)]
        for case, binding in checks:
            with self.subTest(type=type(case)):
                self.assertEqual(m.evaluate_countermodel(case, binding).issues, (m.Issue.INVALID_RECORD,))

    def test_forged_nonmember_enums_cannot_escape_or_bypass_validation(self):
        c = fixture()
        stage = str.__new__(m.Stage, "bogus")
        cases = (
            replace(c, calls=(replace(c.calls[0], stage=stage),) + c.calls[1:]),
            replace(c, windows=(replace(c.windows[0], stage=stage), c.windows[1])),
            replace(c, prior_mode=str.__new__(m.PriorMode, "bogus")),
            replace(c, premises=replace(c.premises, actual_closed_universe=str.__new__(m.Assumption, "bogus"))),
            replace(c, calls=(replace(c.calls[0], successful=str.__new__(m.Assumption, "bogus")),) + c.calls[1:]),
            alter_snapshot(c, 1, kind=str.__new__(m.SnapshotKind, "T0_POST")),
            alter_snapshot(c, 1, coverage=(m.Coverage(12, str.__new__(m.CoverageState, "COMPLETE")),)),
            replace(c, state_history=(m.StatePoint(1, str.__new__(m.QsState, "READ_WRITE_ALL")),)),
        )
        for case in cases:
            self.assertEqual(self.evaluate(case).issues, (m.Issue.INVALID_RECORD,))

    def test_module_is_pure_stdlib_without_old_production_contracts(self):
        source = (ROOT / "Tests/Contracts/dgn007_saturation_countermodel.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        allowed = {"dataclasses", "decimal", "enum", "fractions"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(all(a.name in allowed for a in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertIn(node.module, allowed)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"open", "eval", "exec", "compile", "input", "print", "__import__"})
        self.assertIs(importlib.import_module(m.__name__), m)


if __name__ == "__main__":
    unittest.main()
