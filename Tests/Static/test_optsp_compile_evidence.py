from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from optsp_compile_evidence import (  # noqa: E402
    ActorRequest, Arm, FirstCompile, Interval, LCK_M_X, Request, Wait, evaluate_arm,
)


WINNER = ActorRequest(9, 51, 0)
WAITER = ActorRequest(9, 52, 0)
BATCH = "synthetic-batch-and-parameters"
REQUESTS = (
    Request(WINNER, BATCH, Interval(1, 17), 14, "statement-plan-a"),
    Request(WAITER, BATCH, Interval(2, 19), 16, "statement-plan-a"),
)
FIRST = FirstCompile(WINNER, Interval(4, 9), "statement-plan-a")
WAIT = Wait(WAITER, WINNER, Interval(6, 10), LCK_M_X, "verified-synthetic-compile-resource")
ON = Arm("ON", 9, BATCH, frozenset({WINNER, WAITER}), REQUESTS, (FIRST,), (WAIT,), True)
OFF = replace(
    ON,
    mode="OFF",
    first_compiles=(FIRST, FirstCompile(WAITER, Interval(8, 12), "statement-plan-b")),
    requests=(REQUESTS[0], replace(REQUESTS[1], statement_plan_handle="statement-plan-b")),
    waits=(),
)


class CompileEvidenceTests(unittest.TestCase):
    def test_positive_arms(self):
        self.assertEqual(evaluate_arm(OFF).reason, "overlapping_first_compiles")
        self.assertEqual(evaluate_arm(ON).reason, "compile_wait_and_statement_plan_reuse")

    def test_touching_compiles_do_not_prove_overlap_even_if_both_rpcs_overlap(self):
        later = replace(OFF.first_compiles[1], interval=Interval(9, 12))
        self.assert_unproven(replace(OFF, first_compiles=(FIRST, later)), "no_compile_overlap")

    def test_wait_requires_owned_compile_resource_and_overlap(self):
        foreign_actor = replace(WINNER, database_id=12)
        for detached_wait in (
            replace(WAIT, blocker=foreign_actor),
            replace(WAIT, actor=replace(WAITER, request_id=1)),
            replace(WAIT, verified_compile_resource=None),
            replace(WAIT, wait_type_key=0),
            replace(WAIT, interval=Interval(9, 12)),
            replace(WAIT, interval=Interval(1, 10)),
            replace(WAIT, interval=Interval(3, 10)),
            replace(WAIT, interval=Interval(6, 8)),
            replace(WAIT, interval=Interval(6, 17)),
        ):
            with self.subTest(detached_wait=detached_wait):
                self.assert_unproven(replace(ON, waits=(detached_wait,)), "no_bound_compile_wait")

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
