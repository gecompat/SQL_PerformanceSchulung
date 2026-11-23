from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from optsp_compile_evidence import (  # noqa: E402
    ActorRequest, Arm, ArmRun, ArmState, EventTime, FirstCompile, Interval, LCK_M_X, LockHold,
    Request, ResourceKey, TimeBounds, Wait, evaluate_arm, evaluate_pair,
)


WINNER = ActorRequest(9, 51, 0)
WAITER = ActorRequest(9, 52, 0)
BATCH = "a" * 64
REQUESTS = (
    Request(WINNER, BATCH, Interval(1, 17), 14, "statement-plan-a"),
    Request(WAITER, BATCH, Interval(2, 19), 16, "statement-plan-a"),
)
FIRST = FirstCompile(WINNER, Interval(4, 9), "statement-plan-a")
RESOURCE = ResourceKey(9, "synthetic-lock-key", "77")
WAIT = Wait(WAITER, Interval(6, 10), LCK_M_X, RESOURCE)
HOLD = LockHold(WINNER, RESOURCE, Interval(3, 11), True)
ON = Arm("ON", 9, BATCH, frozenset({WINNER, WAITER}), REQUESTS, (FIRST,), (WAIT,), (HOLD,), True)
OFF = replace(
    ON,
    mode="OFF",
    first_compiles=(FIRST, FirstCompile(WAITER, Interval(8, 12), "statement-plan-b")),
    requests=(REQUESTS[0], replace(REQUESTS[1], statement_plan_handle="statement-plan-b")),
    waits=(),
    lock_holds=(),
)


class CompileEvidenceTests(unittest.TestCase):
    def test_positive_arms(self):
        self.assertEqual(evaluate_arm(OFF).reason, "overlapping_first_compiles")
        self.assertEqual(evaluate_arm(ON).reason, "compile_wait_and_statement_plan_reuse")
        release_during_wait = replace(HOLD, interval=Interval(3, 9))
        self.assertEqual(evaluate_arm(replace(ON, lock_holds=(release_during_wait,))).status, "PROVEN")

    def test_touching_compiles_do_not_prove_overlap_even_if_both_rpcs_overlap(self):
        later = replace(OFF.first_compiles[1], interval=Interval(9, 12))
        self.assert_unproven(replace(OFF, first_compiles=(FIRST, later)), "no_compile_overlap")

    def test_off_overlap_must_survive_the_endpoint_uncertainty(self):
        first = replace(FIRST, interval=Interval(4, TimeBounds(8, 9)))
        ambiguous = replace(OFF.first_compiles[1], interval=Interval(TimeBounds(8, 9), 12))
        self.assertTrue(first.interval.possibly_overlaps(ambiguous.interval))
        self.assert_unproven(replace(OFF, first_compiles=(first, ambiguous)), "no_compile_overlap")

        definite = replace(ambiguous, interval=Interval(TimeBounds(6, 7), 12))
        self.assertEqual(evaluate_arm(replace(OFF, first_compiles=(first, definite))).status, "PROVEN")

    def test_duration_start_bounds_do_not_assume_rounding_or_clock_alignment(self):
        interval = Interval.from_end_and_duration(TimeBounds(100, 102), TimeBounds(5, 6))
        self.assertEqual(interval, Interval(TimeBounds(94, 97), TimeBounds(100, 102)))
        with self.assertRaises(ValueError):
            Interval.from_end_and_duration(TimeBounds(100, 102), TimeBounds(-1, 1))
        with self.assertRaises(ValueError):
            TimeBounds(5, 4)

    def test_equal_labels_preserve_compile_wait_and_exclude_successor_ownership(self):
        def event(ticks, sequence):
            return EventTime(ticks, sequence, "owned-ring")

        requests = (
            replace(REQUESTS[0], rpc=Interval(event(1, 1), event(17, 14)), statement_completed_at=event(14, 12)),
            replace(REQUESTS[1], rpc=Interval(event(2, 3), event(19, 15)), statement_completed_at=event(16, 13)),
        )
        compile_ = replace(FIRST, interval=Interval(event(4, 5), event(9, 6)))
        hold = replace(HOLD, interval=Interval(event(1, 2), event(9, 7)))
        wait = replace(WAIT, interval=Interval(event(2, 4), event(9, 9)))
        successor = replace(HOLD, owner=WAITER, interval=Interval(event(9, 10), event(9, 11)))
        arm = replace(ON, requests=requests, first_compiles=(compile_,), waits=(wait,), lock_holds=(hold, successor))
        self.assertTrue(successor.interval.valid())
        self.assertFalse(wait.interval.possibly_overlaps(successor.interval))
        self.assertEqual(evaluate_arm(arm).reason, "compile_wait_and_statement_plan_reuse")

        competing = replace(successor, interval=Interval(event(9, 8), event(9, 10)))
        self.assertTrue(wait.interval.possibly_overlaps(competing.interval))
        self.assert_unproven(replace(arm, lock_holds=(hold, competing)), "no_bound_compile_wait")

    def test_equal_onset_label_with_acquire_recorded_after_wait_proves_only_later_overlap(self):
        def event(ticks, sequence):
            return EventTime(ticks, sequence, "owned-ring")

        requests = (
            replace(REQUESTS[0], rpc=Interval(event(0, 1), event(14, 12)), statement_completed_at=event(13, 10)),
            replace(REQUESTS[1], rpc=Interval(event(0, 2), event(15, 13)), statement_completed_at=event(14, 11)),
        )
        compile_ = replace(FIRST, interval=Interval(event(2, 5), event(11, 6)))
        wait = replace(WAIT, interval=Interval(event(0, 3), event(11, 8)))
        hold = replace(HOLD, interval=Interval(event(0, 4), event(11, 7)))
        arm = replace(ON, requests=requests, first_compiles=(compile_,), waits=(wait,), lock_holds=(hold,))
        self.assertEqual(evaluate_arm(arm).reason, "compile_wait_and_statement_plan_reuse")

        late = replace(hold, interval=Interval(event(1, 4), hold.interval.end))
        self.assert_unproven(replace(arm, lock_holds=(late,)), "no_bound_compile_wait")
        early_compile = replace(compile_, interval=Interval(event(0, 4), compile_.interval.end))
        late_sequence = replace(hold, interval=Interval(event(0, 5), hold.interval.end))
        self.assert_unproven(
            replace(arm, first_compiles=(early_compile,), lock_holds=(late_sequence,)), "no_bound_compile_wait",
        )
        other_ring = replace(hold, interval=Interval(EventTime(0, 4, "other-ring"), hold.interval.end))
        self.assert_unproven(replace(arm, lock_holds=(other_ring,)), "invalid_lock_ownership")
        flat = replace(compile_, interval=Interval(event(11, 5), event(11, 6)))
        self.assert_unproven(replace(arm, first_compiles=(flat,)), "no_bound_compile_wait")

    def test_sequence_cannot_measure_duration_or_bind_another_recording(self):
        first = Interval(EventTime(5, 1, "ring-a"), EventTime(8, 4, "ring-a"))
        touching = Interval(EventTime(8, 3, "ring-a"), EventTime(10, 5, "ring-a"))
        self.assertTrue(first.possibly_overlaps(touching))
        self.assertFalse(first.overlaps(touching))

        foreign = Interval(EventTime(8, 5, "ring-b"), EventTime(10, 6, "ring-b"))
        self.assertTrue(first.possibly_overlaps(foreign))
        self.assertFalse(first.overlaps(foreign))
        self.assertFalse(Interval(EventTime(8, 1, "ring-a"), EventTime(8, 2, "ring-b")).valid())
        self.assertFalse(Interval(EventTime(5, 4, "ring-a"), EventTime(8, 1, "ring-a")).valid())

    def test_on_timing_ambiguity_cannot_supply_a_missing_order(self):
        earlier_completion = replace(REQUESTS[1], statement_completed_at=TimeBounds(8, 16))
        self.assert_unproven(replace(ON, requests=(REQUESTS[0], earlier_completion)), "statement_plan_reuse")
        uncertain_rpc = replace(REQUESTS[1], rpc=Interval(TimeBounds(2, 7), 19))
        self.assert_unproven(replace(ON, requests=(REQUESTS[0], uncertain_rpc)), "no_bound_compile_wait")
        wait_might_start_at_compile_end = replace(WAIT, interval=Interval(TimeBounds(8, 9), 10))
        self.assert_unproven(replace(ON, waits=(wait_might_start_at_compile_end,)), "no_bound_compile_wait")
        no_proven_hold = replace(HOLD, interval=Interval(TimeBounds(3, 7), 11))
        self.assert_unproven(replace(ON, lock_holds=(no_proven_hold,)), "no_bound_compile_wait")

    def test_wait_can_begin_before_the_observed_compile_phase_if_covered_by_the_lock(self):
        early_wait = replace(WAIT, interval=Interval(3, 10))
        confirmed = replace(ON, waits=(early_wait,))
        self.assertEqual(evaluate_arm(confirmed).reason, "compile_wait_and_statement_plan_reuse")
        late_acquire = replace(HOLD, interval=Interval(4, 11))
        self.assert_unproven(replace(confirmed, lock_holds=(late_acquire,)), "no_bound_compile_wait")

    def test_on_excludes_possible_competing_ownership_but_accepts_a_proven_sequence(self):
        compile_ = replace(FIRST, interval=Interval(TimeBounds(3, 4), TimeBounds(8, 9)))
        wait = replace(WAIT, interval=Interval(TimeBounds(5, 6), TimeBounds(10, 11)))
        hold = replace(HOLD, interval=Interval(TimeBounds(2, 3), TimeBounds(10, 12)))
        timed = replace(ON, first_compiles=(compile_,), waits=(wait,), lock_holds=(hold,))
        self.assertEqual(evaluate_arm(timed).status, "PROVEN")

        other = replace(HOLD, owner=replace(WINNER, session_id=53), interval=Interval(TimeBounds(10, 13), 15))
        self.assertFalse(other.interval.overlaps(wait.interval))
        self.assertTrue(other.interval.possibly_overlaps(wait.interval))
        self.assert_unproven(replace(timed, lock_holds=(hold, other)), "no_bound_compile_wait")

    def test_wait_requires_owned_compile_resource_and_overlap(self):
        for detached_wait in (
            replace(WAIT, resource=replace(RESOURCE, database_id=12)),
            replace(WAIT, actor=replace(WAITER, request_id=1)),
            replace(WAIT, resource=None),
            replace(WAIT, wait_type_key=0),
            replace(WAIT, interval=Interval(9, 12)),
            replace(WAIT, interval=Interval(1, 10)),
            replace(WAIT, interval=Interval(2, 10)),
            replace(WAIT, interval=Interval(6, 8)),
            replace(WAIT, interval=Interval(6, 17)),
        ):
            with self.subTest(detached_wait=detached_wait):
                self.assert_unproven(replace(ON, waits=(detached_wait,)), "no_bound_compile_wait")

    def test_wait_requires_one_unique_compile_owner_with_matching_resource_and_interval(self):
        other_actor = replace(WINNER, session_id=53)
        for holds in (
            (),
            (replace(HOLD, owner=other_actor),),
            (replace(HOLD, resource=replace(RESOURCE, namespace="other-type")),),
            (replace(HOLD, resource=replace(RESOURCE, identity="88")),),
            (replace(HOLD, verified_compile=False),),
            (replace(HOLD, interval=Interval(7, 11)),),
            (replace(HOLD, interval=Interval(3, 8)),),
            (replace(HOLD, interval=Interval(0, 11)),),
            (HOLD, replace(HOLD, owner=other_actor, interval=Interval(9, 13))),
            (HOLD, HOLD),
        ):
            with self.subTest(holds=holds):
                self.assert_unproven(replace(ON, lock_holds=holds), "no_bound_compile_wait")

    def test_ownership_on_unrelated_resource_and_nonoverlapping_time_does_not_conflict(self):
        other_actor = replace(WINNER, session_id=53)
        unrelated = replace(HOLD, owner=other_actor, resource=replace(RESOURCE, identity="88"))
        # A successor that acquires after this wait cannot account for it.
        later = replace(HOLD, owner=other_actor, interval=Interval(11, 14))
        result = evaluate_arm(replace(ON, lock_holds=(HOLD, unrelated, later)))
        self.assertEqual(result.status, "PROVEN")

    def test_invalid_ownership_span_is_rejected(self):
        malformed = replace(HOLD, interval=Interval(9, 9))
        wrong_db = replace(HOLD, owner=replace(WINNER, database_id=12))
        for hold in (malformed, wrong_db):
            with self.subTest(hold=hold):
                self.assert_unproven(replace(ON, lock_holds=(hold,)), "invalid_lock_ownership")

    def test_different_batch_is_rejected_even_with_same_plan_handle(self):
        different = replace(REQUESTS[1], batch_digest="different-batch")
        self.assert_unproven(replace(ON, requests=(REQUESTS[0], different)), "request_binding")

    def test_distinct_or_premature_statement_plan_is_not_reuse(self):
        for waiter in (
            replace(REQUESTS[1], statement_plan_handle="statement-plan-b"),
            replace(REQUESTS[1], statement_completed_at=8),
        ):
            with self.subTest(waiter=waiter):
                self.assert_unproven(replace(ON, requests=(REQUESTS[0], waiter)), "statement_plan_reuse")

    def test_loss_duplicates_and_invalid_compile_binding_fail_closed(self):
        cases = (
            (replace(ON, complete=False), "incomplete_capture"),
            (replace(ON, requests=REQUESTS + (REQUESTS[1],)), "request_set"),
            (replace(ON, requests=REQUESTS[:1]), "request_set"),
            (replace(ON, first_compiles=(FIRST, FIRST)), "duplicate_first_compile"),
            (replace(ON, first_compiles=(replace(FIRST, plan_handle="rpc-plan"),)), "compile_binding"),
            (replace(ON, first_compiles=(replace(FIRST, interval=Interval(4, 15)),)), "compile_binding"),
            (replace(OFF, mode="ON"), "expected_single_first_compile"),
        )
        for arm, reason in cases:
            with self.subTest(reason=reason):
                self.assert_unproven(arm, reason)

    def assert_unproven(self, arm, reason):
        result = evaluate_arm(arm)
        self.assertEqual(result.status, "NOT_PROVEN")
        self.assertEqual(result.reason, reason)


class PairedEvidenceTests(unittest.TestCase):
    def setUp(self):
        off_db = 8
        remap = {actor: replace(actor, database_id=off_db) for actor in OFF.expected_actors}
        off = replace(
            OFF,
            database_id=off_db,
            expected_actors=frozenset(remap.values()),
            requests=tuple(replace(request, actor=remap[request.actor]) for request in OFF.requests),
            first_compiles=tuple(replace(item, actor=remap[item.actor]) for item in OFF.first_compiles),
        )
        self.off = self.run_with_state(off)
        self.on = self.run_with_state(ON)

    def run_with_state(self, arm):
        state = ArmState("isolated-instance-start", arm.database_id, arm.mode, "b" * 64)
        return ArmRun(arm, state, state, 0, "c" * 64, arm.expected_actors)

    def test_matched_pair_binds_distinct_databases_and_both_arm_results(self):
        self.assertEqual(evaluate_pair(self.off, self.on).reason, "matched_off_on_pair")
        for off, on, reason in (
            (self.on, self.off, "pair_modes"),
            (replace(self.off, evidence=replace(self.off.evidence, complete=False)), self.on, "off_incomplete_capture"),
            (self.off, replace(self.on, evidence=replace(self.on.evidence, waits=())), "on_no_bound_compile_wait"),
            (self.run_with_state(OFF), self.on, "pair_profile"),
        ):
            with self.subTest(reason=reason):
                result = evaluate_pair(off, on)
                self.assertEqual((result.status, result.reason), ("NOT_PROVEN", reason))

    def test_detects_state_change_missing_option_or_wrong_database(self):
        before = self.off.before
        for modified in (
            replace(self.off, after=replace(before, option="ON")),
            replace(self.off, after=replace(before, profile_digest="d" * 64)),
            replace(self.off, after=replace(before, instance_incarnation="different-start")),
            replace(self.off, before=replace(before, option="ON"), after=replace(before, option="ON")),
            replace(self.off, before=replace(before, database_id=7), after=replace(before, database_id=7)),
            replace(self.off, before=replace(before, profile_digest=""), after=replace(before, profile_digest="")),
        ):
            with self.subTest(modified=modified):
                self.assertEqual(evaluate_pair(modified, self.on).reason, "arm_state")

    def test_detects_instance_or_comparison_profile_change_between_arms(self):
        for state in (
            replace(self.on.before, instance_incarnation="different-start"),
            replace(self.on.before, profile_digest="d" * 64),
        ):
            with self.subTest(state=state):
                self.assertEqual(evaluate_pair(self.off, replace(self.on, before=state, after=state)).reason, "pair_profile")

    def test_rejects_nonempty_or_unconfirmed_cache_and_partial_barrier(self):
        for cache in (1, False, None):
            with self.subTest(cache=cache):
                self.assertEqual(
                    evaluate_pair(replace(self.off, initial_database_plans=cache), self.on).reason,
                    "initial_cache_state",
                )
        self.assertEqual(evaluate_pair(self.off, replace(self.on, barrier_actors=frozenset({WINNER}))).reason,
                         "barrier_actor_set")

    def test_rejects_different_batch_workload_or_actor_count(self):
        for modified in (
            replace(self.on, workload_digest="d" * 64),
            replace(self.on, workload_digest=None),
            replace(self.on, evidence=replace(self.on.evidence, batch_digest="d" * 64)),
            replace(self.on, evidence=replace(self.on.evidence, expected_actors=frozenset({WINNER})),
                    barrier_actors=frozenset({WINNER})),
        ):
            with self.subTest(modified=modified):
                self.assertEqual(evaluate_pair(self.off, modified).reason, "pair_workload")


if __name__ == "__main__":
    unittest.main()
