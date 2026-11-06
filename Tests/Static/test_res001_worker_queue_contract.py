from __future__ import annotations

import unittest

from res001_worker_queue_contract import (
    SchedulerSample,
    Verdict,
    WorkerWait,
    evaluate_worker_queue,
)


START = "2026-11-06T10:00:00Z"
CAPTURE = "2026-11-06T10:00:05Z"
END = "2026-11-06T10:00:10Z"


def fixture() -> tuple[WorkerWait, tuple[SchedulerSample, ...], str, str]:
    wait = WorkerWait("run-7", "run-7", 51, 0, "THREADPOOL", 40, CAPTURE)
    samples = (
        SchedulerSample(0, 1, 0, CAPTURE),
        SchedulerSample(1, 0, 0, CAPTURE),
    )
    return wait, samples, START, END


class WorkerQueueContractTests(unittest.TestCase):
    def test_owned_threadpool_wait_and_pending_worker_queue_pass(self) -> None:
        self.assertEqual(evaluate_worker_queue(*fixture()).verdict, Verdict.PASS)

    def test_missing_wait_is_not_proven(self) -> None:
        _, samples, start, end = fixture()
        self.assertEqual(evaluate_worker_queue(None, samples, start, end).verdict, Verdict.NOT_PROVEN)

    def test_no_scheduler_rows_is_not_proven(self) -> None:
        wait, _, start, end = fixture()
        self.assertEqual(evaluate_worker_queue(wait, (), start, end).verdict, Verdict.NOT_PROVEN)

    def test_other_wait_type_fails(self) -> None:
        _, samples, start, end = fixture()
        wait = WorkerWait("run-7", "run-7", 51, 0, "SOS_SCHEDULER_YIELD", 40, CAPTURE)
        self.assertEqual(evaluate_worker_queue(wait, samples, start, end).verdict, Verdict.FAIL)

    def test_wrong_run_token_fails(self) -> None:
        _, samples, start, end = fixture()
        wait = WorkerWait("run-7", "run-8", 51, 0, "THREADPOOL", 40, CAPTURE)
        self.assertEqual(evaluate_worker_queue(wait, samples, start, end).verdict, Verdict.FAIL)

    def test_capture_outside_run_window_fails(self) -> None:
        wait, samples, _, end = fixture()
        self.assertEqual(evaluate_worker_queue(wait, samples, "2026-11-06T10:00:06Z", end).verdict, Verdict.FAIL)

    def test_threadpool_wait_without_worker_queue_is_not_proven(self) -> None:
        wait, samples, start, end = fixture()
        samples = tuple(SchedulerSample(s.scheduler_id, 0, 0, CAPTURE) for s in samples)
        self.assertEqual(evaluate_worker_queue(wait, samples, start, end).verdict, Verdict.NOT_PROVEN)

    def test_runnable_cpu_queue_alone_is_not_worker_queue_evidence(self) -> None:
        wait, samples, start, end = fixture()
        samples = tuple(SchedulerSample(s.scheduler_id, 0, 3, CAPTURE) for s in samples)
        result = evaluate_worker_queue(wait, samples, start, end)
        self.assertEqual(result.verdict, Verdict.NOT_PROVEN)
        self.assertTrue(result.cpu_runnable_visible)
        self.assertFalse(result.worker_queue_visible)

    def test_worker_and_cpu_queues_remain_separate_signals(self) -> None:
        wait, samples, start, end = fixture()
        samples = (
            SchedulerSample(0, 1, 3, CAPTURE),
            SchedulerSample(1, 0, 0, CAPTURE),
        )
        result = evaluate_worker_queue(wait, samples, start, end)
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertTrue(result.worker_queue_visible)
        self.assertTrue(result.cpu_runnable_visible)

    def test_capture_timestamp_mismatch_fails(self) -> None:
        wait, samples, start, end = fixture()
        samples = (SchedulerSample(0, 1, 0, START), samples[1])
        self.assertEqual(evaluate_worker_queue(wait, samples, start, end).verdict, Verdict.FAIL)

    def test_duplicate_scheduler_id_fails(self) -> None:
        wait, _, start, end = fixture()
        samples = (SchedulerSample(0, 1, 0, CAPTURE), SchedulerSample(0, 1, 0, CAPTURE))
        self.assertEqual(evaluate_worker_queue(wait, samples, start, end).verdict, Verdict.FAIL)

    def test_boolean_is_not_an_integer_queue_count(self) -> None:
        wait, samples, start, end = fixture()
        samples = (SchedulerSample(0, True, 0, CAPTURE), samples[1])
        self.assertEqual(evaluate_worker_queue(wait, samples, start, end).verdict, Verdict.FAIL)

    def test_invalid_timestamp_fails(self) -> None:
        wait, samples, _, end = fixture()
        self.assertEqual(evaluate_worker_queue(wait, samples, "bad", end).verdict, Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
