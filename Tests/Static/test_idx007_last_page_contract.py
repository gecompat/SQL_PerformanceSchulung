from __future__ import annotations

import unittest

from idx007_last_page_contract import (
    PageLink, PageTarget, PageWait, Verdict,
    evaluate_last_page_wait_snapshot_consistency as _evaluate_last_page_wait_snapshot_consistency,
    evaluate_supplied_page_chain_consistency,
)


STAMP = "2026-11-06T10:00:00Z"
EXPECTED_ACTOR_REQUESTS = (("ACTOR_A", 51, 1), ("ACTOR_B", 52, 1))


def fixture(*, rightmost: bool | None = True) -> tuple[tuple[PageWait, ...], PageTarget]:
    waits = (
        PageWait("PAGELATCH_EX", 51, 7, 1, 900, 12, STAMP, 1, 0),
        PageWait("PAGELATCH_EX", 52, 7, 1, 900, 8, STAMP, 1, 0),
    )
    target = PageTarget(7, 1, 900, 42, 3, 0, rightmost, STAMP, 1)
    return waits, target


def fixture_chain(*, start: tuple[int, int] = (1, 900)) -> tuple[PageLink, ...]:
    return (
        PageLink(7, start[0], start[1], 42, 3, 1, 0, None, (1, 901)),
        PageLink(7, 1, 901, 42, 3, 1, 0, (1, 900), (1, 9999)),
    )


def evaluate_last_page_wait_snapshot_consistency(waits, target, expected_actor_requests=EXPECTED_ACTOR_REQUESTS,
                                  *, page_chain=None, expected_terminal_sentinel=(1, 9999), max_pages=2):
    if page_chain is None:
        page_chain = fixture_chain(start=(target.file_id, target.page_id))
    return _evaluate_last_page_wait_snapshot_consistency(
        waits, target, expected_actor_requests=expected_actor_requests,
        page_chain=page_chain, expected_terminal_sentinel=expected_terminal_sentinel, max_pages=max_pages,
    )


class LastPageContractTests(unittest.TestCase):
    def test_bounded_chain_requires_consistent_links_and_explicit_terminal(self) -> None:
        pages = (
            PageLink(7, 1, 900, 42, 3, 1, 0, (1, 899), (1, 901)),
            PageLink(7, 1, 901, 42, 3, 1, 0, (1, 900), (1, 902)),
            PageLink(7, 1, 902, 42, 3, 1, 0, (1, 901), (1, 9999)),
        )
        result = evaluate_supplied_page_chain_consistency(
            pages, database_id=7, object_id=42, index_id=3, partition_id=1,
            start_address=(1, 900), expected_terminal_sentinel=(1, 9999), max_pages=3,
        )
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertIn("SQL Server terminal meaning is not attested", result.reasons[0])

    def test_chain_does_not_assume_missing_terminal_encoding(self) -> None:
        self.assertEqual(evaluate_supplied_page_chain_consistency(
            (), database_id=7, object_id=42, index_id=3, partition_id=1,
            start_address=(1, 900), expected_terminal_sentinel=None, max_pages=3,
        ).verdict, Verdict.NOT_PROVEN)

    def test_chain_rejects_identity_level_link_cycle_and_cap_mismatches(self) -> None:
        pages = (
            PageLink(7, 1, 900, 42, 3, 1, 0, None, (1, 901)),
            PageLink(7, 1, 901, 42, 3, 1, 0, (1, 900), (1, 9999)),
        )
        variants = (
            (PageLink(7, 1, 900, 42, 4, 1, 0, None, (1, 901)), pages[1]),
            (PageLink(7, 1, 900, 42, 3, 1, 1, None, (1, 901)), pages[1]),
            (pages[0], PageLink(7, 1, 901, 42, 3, 1, 0, (1, 899), (1, 9999))),
            (pages[0], PageLink(7, 1, 901, 42, 3, 1, 0, (1, 900), (1, 900))),
        )
        for candidate in variants:
            with self.subTest(candidate=candidate):
                self.assertEqual(evaluate_supplied_page_chain_consistency(
                    candidate, database_id=7, object_id=42, index_id=3, partition_id=1,
                    start_address=(1, 900), expected_terminal_sentinel=(1, 9999), max_pages=2,
                ).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_supplied_page_chain_consistency(
            pages, database_id=7, object_id=42, index_id=3, partition_id=1,
            start_address=(1, 900), expected_terminal_sentinel=(1, 9999), max_pages=1,
        ).verdict, Verdict.NOT_PROVEN)
        self.assertEqual(evaluate_supplied_page_chain_consistency(
            pages[:1], database_id=7, object_id=42, index_id=3, partition_id=1,
            start_address=(1, 900), expected_terminal_sentinel=(1, 9999), max_pages=2,
        ).verdict, Verdict.NOT_PROVEN)

    def test_terminal_marker_cannot_alias_a_visited_page(self) -> None:
        pages = (
            PageLink(7, 1, 900, 42, 3, 1, 0, None, (1, 901)),
            PageLink(7, 1, 901, 42, 3, 1, 0, (1, 900), (1, 900)),
        )
        result = evaluate_supplied_page_chain_consistency(
            pages, database_id=7, object_id=42, index_id=3, partition_id=1,
            start_address=(1, 900), expected_terminal_sentinel=(1, 900), max_pages=2,
        )
        self.assertEqual(result.verdict, Verdict.FAIL)
        self.assertIn("loops", result.reasons[0])

    def test_matching_two_actor_leaf_and_right_edge_passes(self) -> None:
        result = evaluate_last_page_wait_snapshot_consistency(*fixture())
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertIn("multi-sample overlap", result.reasons[0])

    def test_wait_pass_requires_a_matching_bounded_page_chain(self) -> None:
        waits, target = fixture()
        self.assertEqual(_evaluate_last_page_wait_snapshot_consistency(
            waits, target, expected_actor_requests=EXPECTED_ACTOR_REQUESTS
        ).verdict, Verdict.NOT_PROVEN)
        wrong_start = fixture_chain(start=(1, 899))
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(
            waits, target, page_chain=wrong_start
        ).verdict, Verdict.FAIL)
        missing_terminal = evaluate_last_page_wait_snapshot_consistency(
            waits, target, page_chain=fixture_chain(), expected_terminal_sentinel=None
        )
        self.assertEqual(missing_terminal.verdict, Verdict.NOT_PROVEN)

    def test_wait_rows_bind_expected_actor_request_and_task(self) -> None:
        waits, target = fixture()
        wrong_request = (waits[0], PageWait(
            "PAGELATCH_EX", 52, 7, 1, 900, 8, STAMP, 2, 0
        ))
        missing_task = (PageWait(
            "PAGELATCH_EX", 51, 7, 1, 900, 12, STAMP, 1, None
        ), waits[1])
        duplicate_task = (waits[0], waits[0], waits[1])
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(wrong_request, target).verdict,
                         Verdict.FAIL)
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(missing_task, target).verdict,
                         Verdict.FAIL)
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(duplicate_task, target).verdict,
                         Verdict.FAIL)
        self.assertEqual(_evaluate_last_page_wait_snapshot_consistency(
            waits, target, expected_actor_requests=None
        ).verdict, Verdict.NOT_PROVEN)

    def test_multiple_wait_tasks_may_belong_to_one_expected_request(self) -> None:
        waits, target = fixture()
        waits = (waits[0], PageWait(
            "PAGELATCH_EX", 51, 7, 1, 900, 11, STAMP, 1, 1
        ), waits[1])
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.PASS)

    def test_missing_snapshot_is_not_proven(self) -> None:
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(None, fixture()[1]).verdict, Verdict.NOT_PROVEN)

    def test_no_wait_is_not_proven(self) -> None:
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency((), fixture()[1]).verdict, Verdict.NOT_PROVEN)

    def test_page_io_wait_is_not_latch_contention(self) -> None:
        waits, target = fixture()
        waits = tuple(PageWait("PAGEIOLATCH_EX", w.session_id, w.database_id, w.file_id,
                               w.page_id, w.wait_ms, w.captured_at, w.request_id,
                               w.exec_context_id) for w in waits)
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.NOT_PROVEN)

    def test_different_page_fails(self) -> None:
        waits, target = fixture()
        waits = (waits[0], PageWait("PAGELATCH_EX", 52, 7, 1, 901, 8, STAMP, 1, 0))
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.FAIL)

    def test_timestamp_mismatch_fails(self) -> None:
        waits, target = fixture()
        target = PageTarget(7, 1, 900, 42, 3, 0, True, "2026-11-06T10:00:01Z")
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.FAIL)

    def test_capture_timestamps_require_rfc3339_and_compare_as_instants(self) -> None:
        waits, target = fixture()
        equivalent_waits = tuple(
            PageWait(w.wait_type, w.session_id, w.database_id, w.file_id, w.page_id,
                     w.wait_ms, "2026-11-06T11:00:00+01:00", w.request_id,
                     w.exec_context_id)
            for w in waits
        )
        self.assertEqual(
            evaluate_last_page_wait_snapshot_consistency(equivalent_waits, target).verdict,
            Verdict.PASS,
        )
        for invalid in (
            "x",
            "2026-11-06T10:00:00",
            "2026-02-30T10:00:00Z",
            "2026-11-06T10:00:00Z ",
            "2026-11-06T10:00:00-00:00",
            "0001-01-01T00:00:00+23:59",
        ):
            with self.subTest(invalid=invalid):
                invalid_target = PageTarget(7, 1, 900, 42, 3, 0, True, invalid)
                self.assertEqual(
                    evaluate_last_page_wait_snapshot_consistency(waits, invalid_target).verdict,
                    Verdict.FAIL,
                )
                invalid_waits = (PageWait("PAGELATCH_EX", 51, 7, 1, 900, 12, invalid,
                                          1, 0), waits[1])
                self.assertEqual(
                    evaluate_last_page_wait_snapshot_consistency(invalid_waits, target).verdict,
                    Verdict.FAIL,
                )

        high_precision_waits = tuple(
            PageWait(w.wait_type, w.session_id, w.database_id, w.file_id, w.page_id,
                     w.wait_ms, "2026-11-06T10:00:00.1234567Z", w.request_id,
                     w.exec_context_id)
            for w in waits
        )
        high_precision_target = PageTarget(
            7, 1, 900, 42, 3, 0, True, "2026-11-06T10:00:00.12345670+00:00", 1
        )
        self.assertEqual(
            evaluate_last_page_wait_snapshot_consistency(high_precision_waits, high_precision_target).verdict,
            Verdict.PASS,
        )
        changed_fraction = (PageWait("PAGELATCH_EX", 51, 7, 1, 900, 12,
                                     "2026-11-06T10:00:00.1234568Z", 1, 0),
                            high_precision_waits[1])
        self.assertEqual(
            evaluate_last_page_wait_snapshot_consistency(changed_fraction, high_precision_target).verdict,
            Verdict.FAIL,
        )

    def test_one_distinct_session_is_not_concurrency(self) -> None:
        waits, target = fixture()
        waits = (waits[0], PageWait("PAGELATCH_EX", 51, 7, 1, 900, 8, STAMP, 1, 1))
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.NOT_PROVEN)

    def test_non_leaf_target_fails(self) -> None:
        waits, _ = fixture()
        target = PageTarget(7, 1, 900, 42, 3, 1, True, STAMP)
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.FAIL)

    def test_missing_rightmost_claim_is_not_proven(self) -> None:
        waits, target = fixture(rightmost=None)
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.NOT_PROVEN)

    def test_negative_rightmost_claim_fails(self) -> None:
        waits, target = fixture(rightmost=False)
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.FAIL)

    def test_boolean_is_not_accepted_as_integer_wait_duration(self) -> None:
        waits, target = fixture()
        waits = (PageWait("PAGELATCH_EX", 51, 7, 1, 900, True, STAMP, 1, 0), waits[1])
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(waits, target).verdict, Verdict.FAIL)

    def test_wrong_container_type_fails(self) -> None:
        waits, target = fixture()
        self.assertEqual(evaluate_last_page_wait_snapshot_consistency(list(waits), target).verdict, Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
