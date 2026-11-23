from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from optsp_compile_evidence import (  # noqa: E402
    ActorRequest, Arm, FirstCompile, Interval, LCK_M_X, LockHold,
    Request, ResourceKey, TimeBounds, Wait, evaluate_arm,
)


WINNER = ActorRequest(9, 51, 0)
WAITER = ActorRequest(9, 52, 0)
BATCH = "synthetic-batch-and-parameters"
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

    def test_on_timing_ambiguity_cannot_supply_a_missing_order(self):
        earlier_completion = replace(REQUESTS[1], statement_completed_at=TimeBounds(8, 16))
        self.assert_unproven(replace(ON, requests=(REQUESTS[0], earlier_completion)), "statement_plan_reuse")
        uncertain_rpc = replace(REQUESTS[1], rpc=Interval(TimeBounds(2, 7), 19))
        self.assert_unproven(replace(ON, requests=(REQUESTS[0], uncertain_rpc)), "no_bound_compile_wait")
        wait_overlapping_start = replace(WAIT, interval=Interval(TimeBounds(3, 7), 10))
        self.assert_unproven(replace(ON, waits=(wait_overlapping_start,)), "no_bound_compile_wait")
        no_proven_hold = replace(HOLD, interval=Interval(TimeBounds(3, 7), 11))
        self.assert_unproven(replace(ON, lock_holds=(no_proven_hold,)), "no_bound_compile_wait")

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
            replace(WAIT, interval=Interval(3, 10)),
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


if __name__ == "__main__":
    unittest.main()
