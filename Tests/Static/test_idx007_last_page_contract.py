from __future__ import annotations

import unittest

from idx007_last_page_contract import PageTarget, PageWait, Verdict, evaluate_last_page_contention


STAMP = "2026-11-06T10:00:00Z"


def fixture(*, rightmost: bool | None = True) -> tuple[tuple[PageWait, ...], PageTarget]:
    waits = (
        PageWait("PAGELATCH_EX", 51, 7, 1, 900, 12, STAMP),
        PageWait("PAGELATCH_EX", 52, 7, 1, 900, 8, STAMP),
    )
    target = PageTarget(7, 1, 900, 42, 3, 0, rightmost, STAMP)
    return waits, target


class LastPageContractTests(unittest.TestCase):
    def test_matching_two_actor_leaf_and_right_edge_passes(self) -> None:
        self.assertEqual(evaluate_last_page_contention(*fixture()).verdict, Verdict.PASS)

    def test_missing_snapshot_is_not_proven(self) -> None:
        self.assertEqual(evaluate_last_page_contention(None, fixture()[1]).verdict, Verdict.NOT_PROVEN)

    def test_no_wait_is_not_proven(self) -> None:
        self.assertEqual(evaluate_last_page_contention((), fixture()[1]).verdict, Verdict.NOT_PROVEN)

    def test_page_io_wait_is_not_latch_contention(self) -> None:
        waits, target = fixture()
        waits = tuple(PageWait("PAGEIOLATCH_EX", w.session_id, w.database_id, w.file_id,
                               w.page_id, w.wait_ms, w.captured_at) for w in waits)
        self.assertEqual(evaluate_last_page_contention(waits, target).verdict, Verdict.NOT_PROVEN)

    def test_different_page_fails(self) -> None:
        waits, target = fixture()
        waits = (waits[0], PageWait("PAGELATCH_EX", 52, 7, 1, 901, 8, STAMP))
        self.assertEqual(evaluate_last_page_contention(waits, target).verdict, Verdict.FAIL)

    def test_timestamp_mismatch_fails(self) -> None:
        waits, target = fixture()
        target = PageTarget(7, 1, 900, 42, 3, 0, True, "2026-11-06T10:00:01Z")
        self.assertEqual(evaluate_last_page_contention(waits, target).verdict, Verdict.FAIL)

    def test_one_distinct_session_is_not_concurrency(self) -> None:
        waits, target = fixture()
        waits = (waits[0], PageWait("PAGELATCH_EX", 51, 7, 1, 900, 8, STAMP))
        self.assertEqual(evaluate_last_page_contention(waits, target).verdict, Verdict.NOT_PROVEN)

    def test_non_leaf_target_fails(self) -> None:
        waits, _ = fixture()
        target = PageTarget(7, 1, 900, 42, 3, 1, True, STAMP)
        self.assertEqual(evaluate_last_page_contention(waits, target).verdict, Verdict.FAIL)

    def test_missing_rightmost_claim_is_not_proven(self) -> None:
        waits, target = fixture(rightmost=None)
        self.assertEqual(evaluate_last_page_contention(waits, target).verdict, Verdict.NOT_PROVEN)

    def test_negative_rightmost_claim_fails(self) -> None:
        waits, target = fixture(rightmost=False)
        self.assertEqual(evaluate_last_page_contention(waits, target).verdict, Verdict.FAIL)

    def test_boolean_is_not_accepted_as_integer_wait_duration(self) -> None:
        waits, target = fixture()
        waits = (PageWait("PAGELATCH_EX", 51, 7, 1, 900, True, STAMP), waits[1])
        self.assertEqual(evaluate_last_page_contention(waits, target).verdict, Verdict.FAIL)

    def test_wrong_container_type_fails(self) -> None:
        waits, target = fixture()
        self.assertEqual(evaluate_last_page_contention(list(waits), target).verdict, Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
