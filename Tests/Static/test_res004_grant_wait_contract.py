from __future__ import annotations

import unittest

from res004_grant_wait_contract import Grant, RequestWait, Verdict, evaluate_grant_wait


STAMP = "2026-11-06T10:00:00Z"


def fixture() -> tuple[RequestWait, tuple[Grant, ...]]:
    request = RequestWait(51, 0, "RESOURCE_SEMAPHORE", 120, STAMP)
    grants = (
        Grant(51, 0, None, 120, 8192, 0, 1, 1, STAMP),
        Grant(52, 0, "2026-11-06T09:59:50Z", None, 4096, 4096, 1, 1, STAMP),
    )
    return request, grants


class GrantWaitContractTests(unittest.TestCase):
    def test_waiter_and_same_pool_grantee_pass(self) -> None:
        self.assertEqual(evaluate_grant_wait(*fixture()).verdict, Verdict.PASS)

    def test_missing_request_is_not_proven(self) -> None:
        self.assertEqual(evaluate_grant_wait(None, fixture()[1]).verdict, Verdict.NOT_PROVEN)

    def test_no_grants_is_not_proven(self) -> None:
        self.assertEqual(evaluate_grant_wait(fixture()[0], ()).verdict, Verdict.NOT_PROVEN)

    def test_other_wait_type_fails(self) -> None:
        _, grants = fixture()
        request = RequestWait(51, 0, "THREADPOOL", 120, STAMP)
        self.assertEqual(evaluate_grant_wait(request, grants).verdict, Verdict.FAIL)

    def test_request_and_grant_identity_mismatch_fails(self) -> None:
        request, grants = fixture()
        altered = (Grant(51, 1, None, 120, 8192, 0, 1, 1, STAMP), grants[1])
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.FAIL)

    def test_granted_waiter_fails(self) -> None:
        request, grants = fixture()
        altered = (Grant(51, 0, STAMP, 120, 8192, 8192, 1, 1, STAMP), grants[1])
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.FAIL)

    def test_missing_wait_duration_is_not_proven(self) -> None:
        request, grants = fixture()
        altered = (Grant(51, 0, None, None, 8192, 0, 1, 1, STAMP), grants[1])
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.NOT_PROVEN)

    def test_independently_sampled_positive_wait_durations_need_not_match(self) -> None:
        request, grants = fixture()
        altered = (Grant(51, 0, None, 119, 8192, 0, 1, 1, STAMP), grants[1])
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.PASS)

    def test_null_granted_memory_is_valid_for_ungranted_request(self) -> None:
        request, grants = fixture()
        altered = (Grant(51, 0, None, 120, 8192, None, 1, 1, STAMP), grants[1])
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.PASS)

    def test_malformed_capture_timestamp_fails(self) -> None:
        request, grants = fixture()
        request = RequestWait(51, 0, "RESOURCE_SEMAPHORE", 120, "not-a-time")
        self.assertEqual(evaluate_grant_wait(request, grants).verdict, Verdict.FAIL)

    def test_grant_time_and_memory_contradiction_fails(self) -> None:
        request, grants = fixture()
        altered = (Grant(51, 0, None, 120, 8192, 512, 1, 1, STAMP), grants[1])
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.FAIL)

    def test_different_capture_time_fails(self) -> None:
        request, grants = fixture()
        altered = (grants[0], Grant(52, 0, "t", None, 4096, 4096, 1, 1, "later"))
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.FAIL)

    def test_different_pool_or_semaphore_is_not_competition_evidence(self) -> None:
        request, grants = fixture()
        altered = (grants[0], Grant(52, 0, "t", None, 4096, 4096, 2, 1, STAMP))
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.NOT_PROVEN)

    def test_missing_concurrent_grantee_is_not_proven(self) -> None:
        request, grants = fixture()
        self.assertEqual(evaluate_grant_wait(request, grants[:1]).verdict, Verdict.NOT_PROVEN)

    def test_boolean_is_not_an_integer_duration(self) -> None:
        request, grants = fixture()
        altered = (Grant(51, 0, None, True, 8192, 0, 1, 1, STAMP), grants[1])
        self.assertEqual(evaluate_grant_wait(request, altered).verdict, Verdict.FAIL)

    def test_wrong_container_type_fails(self) -> None:
        request, grants = fixture()
        self.assertEqual(evaluate_grant_wait(request, list(grants)).verdict, Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
