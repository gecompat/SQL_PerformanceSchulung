"""Synthetic counterexamples for the DGN-004 narrowed acceptance contract."""
from __future__ import annotations

from dataclasses import replace
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dgn004_acceptance_contract import (  # noqa: E402
    CALL_SEQUENCE,
    EXPECTED_SCOPE,
    FIXTURE_FORMULAS,
    ROWS_PER_CALL,
    TARGET_BUILDS,
    BuildEvidence,
    CallEvidence,
    Verdict,
    form_a_expected_rows,
    evaluate_build,
    evaluate_matrix,
)


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_ROWS = form_a_expected_rows()


def good_call(index: int) -> CallEvidence:
    role, forced = CALL_SEQUENCE[index - 1]
    is_r = role == "R"
    plan = 901 if is_r else 902
    compile_counts = {
        1: (None, 1), 2: (1, 2), 3: (2, 3), 4: (None, 1),
        5: (1, 2), 6: (2, 3), 7: (3, 4), 8: (3, 4), 9: (4, 5),
    }
    compile_before, compile_after = compile_counts[index]
    strict_compile = index in (2, 3, 5, 6, 7)
    return CallEvidence(
        role=role,
        call_number=index,
        database_id=73,
        object_id=101 if is_r else 102,
        query_id=201 if is_r else 202,
        query_text_id=301 if is_r else 302,
        context_settings_id=100,
        query_hash=b"\x01\x02\x03\x04\x05\x06\x07\x08",
        query_plan_hash=b"\x11\x12\x13\x14\x15\x16\x17\x18",
        parameterization_type=0,
        target_plan_id=plan,
        actual_plan_id=plan if forced else plan + 10 + index,
        source_bound=True,
        current_plan=True,
        fresh_compilation_proven=True,
        compile_count_before=compile_before,
        compile_count_after=compile_after,
        compile_epoch_before=f"{role}-epoch" if strict_compile else None,
        compile_epoch_after=f"{role}-epoch" if strict_compile else None,
        recompile_marked=strict_compile,
        compile_flush_complete=strict_compile,
        context_bound=True,
        transport_complete=True,
        rows=EXPECTED_ROWS,
        execution_delta=1,
        force_accepted=True if forced else None,
        is_forced_plan_after_request=True if forced else None,
        use_plan=True if forced else None,
        force_error_epoch=f"{role}-force-{index}" if forced else None,
        force_failure_count_after_request=0 if forced else None,
        force_failure_count_after_execution=0 if forced else None,
        unforce_confirmed=True if forced else None,
        is_forced_plan=False,
        hint_state="FIXED_TERMINAL" if role == "H" else "ABSENT",
        external_override_absent=True,
        replay_marker=None,
    )


def good_build(build: str = TARGET_BUILDS[0]) -> BuildEvidence:
    return BuildEvidence(
        build=build,
        acceptance_scope=EXPECTED_SCOPE,
        calls=tuple(good_call(index) for index in range(1, len(CALL_SEQUENCE) + 1)),
        cleanup_ok=True,
    )


class Dgn004AcceptanceContractTests(unittest.TestCase):
    def test_complete_nine_call_contract_passes_without_replay_markers(self) -> None:
        result = evaluate_build(good_build())
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertEqual(result.reasons, ())

    def test_contract_requires_exact_768_rows_and_384_duplicate_pairs(self) -> None:
        self.assertEqual(len(EXPECTED_ROWS), ROWS_PER_CALL)
        call = good_call(1)
        wrong = replace(call, rows=(call.rows or ())[:-1])
        build = replace(good_build(), calls=(wrong, *good_build().calls[1:]))
        self.assertEqual(evaluate_build(build).verdict, Verdict.FAIL)

        mutated = list(EXPECTED_ROWS)
        mutated[-1] = mutated[0]
        build = replace(
            good_build(),
            calls=(replace(good_call(1), rows=tuple(mutated)), *good_build().calls[1:]),
        )
        self.assertEqual(evaluate_build(build).verdict, Verdict.FAIL)

        bool_rows = list(EXPECTED_ROWS)
        bool_rows[0] = (True, *bool_rows[0][1:])
        build = replace(
            good_build(),
            calls=(replace(good_call(1), rows=tuple(bool_rows)), *good_build().calls[1:]),
        )
        self.assertEqual(evaluate_build(build).verdict, Verdict.FAIL)

    def test_expected_oracle_is_bound_to_active_registered_id_formulas(self) -> None:
        document = json.loads((ROOT / ".ai" / "identity" / "registry.json").read_text(encoding="utf-8"))
        candidate = next(
            item for item in document["artifacts"]["TSK-016"]["candidates"]
            if item["target"] == "DGN-004"
        )
        self.assertEqual(candidate["active_plan"], "classical_forcing_hint_control_plan")
        fixture = "\n".join(candidate["mapping_replay_probe_plan"]["fixture_model"])
        self.assertTrue(all(formula in fixture for formula in FIXTURE_FORMULAS))
        self.assertEqual((EXPECTED_ROWS[0], EXPECTED_ROWS[1]), (EXPECTED_ROWS[0], EXPECTED_ROWS[0]))
        self.assertEqual((1, 1, 3001, 1001, 2001, 4001, 5001, 6001, 7001, 1), EXPECTED_ROWS[0])

    def test_missing_required_evidence_is_not_proven(self) -> None:
        call = replace(good_call(3), use_plan=None)
        calls = list(good_build().calls)
        calls[2] = call
        result = evaluate_build(replace(good_build(), calls=tuple(calls)))
        self.assertEqual(result.verdict, Verdict.NOT_PROVEN)
        self.assertTrue(any("UsePlan" in reason for reason in result.reasons))

    def test_unforced_fresh_compile_counts_and_call_two_b0_b1_contract_are_required(self) -> None:
        calls = list(good_build().calls)
        calls[7] = replace(calls[7], compile_count_before=None)
        result = evaluate_build(replace(good_build(), calls=tuple(calls)))
        self.assertEqual(result.verdict, Verdict.NOT_PROVEN)
        self.assertTrue(any("call 8 compile count before" in reason for reason in result.reasons))

        calls = list(good_build().calls)
        calls[1] = replace(calls[1], compile_count_after=1)
        result = evaluate_build(replace(good_build(), calls=tuple(calls)))
        self.assertEqual(result.verdict, Verdict.FAIL)
        self.assertTrue(any("call 2 compile count delta" in reason for reason in result.reasons))

    def test_call_order_extra_call_and_scope_mutations_fail(self) -> None:
        calls = list(good_build().calls)
        calls[2] = replace(calls[2], role="H")
        self.assertEqual(
            evaluate_build(replace(good_build(), calls=tuple(calls))).verdict,
            Verdict.FAIL,
        )
        self.assertEqual(
            evaluate_build(replace(good_build(), calls=(*good_build().calls, good_call(1)))).verdict,
            Verdict.FAIL,
        )
        self.assertEqual(
            evaluate_build(replace(good_build(), acceptance_scope=None)).verdict,
            Verdict.NOT_PROVEN,
        )
        self.assertEqual(
            evaluate_build(replace(good_build(), acceptance_scope="REPLAY_COMPARISON")).verdict,
            Verdict.FAIL,
        )
        self.assertEqual(evaluate_build(good_build("2019/15.0")).verdict, Verdict.FAIL)

    def test_forced_call_requires_actual_target_use_compile_and_unforce(self) -> None:
        mutations = (
            {"force_accepted": False},
            {"is_forced_plan_after_request": False},
            {"use_plan": False},
            {"actual_plan_id": 999},
            {"compile_count_after": 4},
            {"force_failure_count_after_request": 1},
            {"force_failure_count_after_execution": 1},
            {"unforce_confirmed": False},
        )
        for changed in mutations:
            with self.subTest(changed=changed):
                calls = list(good_build().calls)
                calls[2] = replace(calls[2], **changed)
                result = evaluate_build(replace(good_build(), calls=tuple(calls)))
                self.assertEqual(result.verdict, Verdict.FAIL)

        calls = list(good_build().calls)
        calls[2] = replace(calls[2], force_error_epoch=None)
        result = evaluate_build(replace(good_build(), calls=tuple(calls)))
        self.assertEqual(result.verdict, Verdict.NOT_PROVEN)

        calls = list(good_build().calls)
        calls[4] = replace(calls[4], force_error_epoch=calls[2].force_error_epoch)
        result = evaluate_build(replace(good_build(), calls=tuple(calls)))
        self.assertEqual(result.verdict, Verdict.FAIL)
        self.assertTrue(any("force failure epoch is not unique" in reason for reason in result.reasons))

    def test_wrong_hint_or_external_override_fails(self) -> None:
        for changed in ({"hint_state": "ABSENT"}, {"external_override_absent": False}):
            with self.subTest(changed=changed):
                calls = list(good_build().calls)
                calls[3] = replace(calls[3], **changed)
                self.assertEqual(
                    evaluate_build(replace(good_build(), calls=tuple(calls))).verdict,
                    Verdict.FAIL,
                )

    def test_role_and_target_plan_identities_must_remain_distinct_and_stable(self) -> None:
        calls = list(good_build().calls)
        calls[4] = replace(calls[4], query_id=201)
        self.assertEqual(
            evaluate_build(replace(good_build(), calls=tuple(calls))).verdict,
            Verdict.FAIL,
        )

    def test_hashes_are_raw_supplemental_values_not_identity_keys(self) -> None:
        calls = list(good_build().calls)
        calls[3] = replace(
            calls[3],
            query_hash=calls[0].query_hash,
            query_plan_hash=calls[0].query_plan_hash,
        )
        calls[2] = replace(calls[2], query_hash=b"\xaa" * 8)
        self.assertEqual(
            evaluate_build(replace(good_build(), calls=tuple(calls))).verdict,
            Verdict.PASS,
        )

        calls[4] = replace(calls[4], query_hash=b"short")
        result = evaluate_build(replace(good_build(), calls=tuple(calls)))
        self.assertEqual(result.verdict, Verdict.FAIL)
        self.assertTrue(any("query_hash is not an exact 8-byte" in reason for reason in result.reasons))

    def test_object_query_text_and_context_binding_cannot_change_within_role(self) -> None:
        for field, value in (
            ("object_id", 103),
            ("query_text_id", 303),
            ("context_settings_id", 999),
        ):
            with self.subTest(field=field):
                calls = list(good_build().calls)
                calls[4] = replace(calls[4], **{field: value})
                result = evaluate_build(replace(good_build(), calls=tuple(calls)))
                self.assertEqual(result.verdict, Verdict.FAIL)
                self.assertTrue(any("identity changes within its role" in reason for reason in result.reasons))

        calls = list(good_build().calls)
        calls[6] = replace(calls[6], target_plan_id=903, actual_plan_id=903)
        self.assertEqual(
            evaluate_build(replace(good_build(), calls=tuple(calls))).verdict,
            Verdict.FAIL,
        )

    def test_unexpected_unforced_state_is_not_accepted(self) -> None:
        calls = list(good_build().calls)
        calls[0] = replace(calls[0], is_forced_plan=True)
        self.assertEqual(
            evaluate_build(replace(good_build(), calls=tuple(calls))).verdict,
            Verdict.FAIL,
        )

    def test_invalid_parameterization_and_boolean_call_ordinal_fail(self) -> None:
        calls = list(good_build().calls)
        calls[0] = replace(calls[0], parameterization_type=1)
        self.assertEqual(
            evaluate_build(replace(good_build(), calls=tuple(calls))).verdict,
            Verdict.FAIL,
        )
        calls = list(good_build().calls)
        calls[0] = replace(calls[0], call_number=True)
        self.assertEqual(
            evaluate_build(replace(good_build(), calls=tuple(calls))).verdict,
            Verdict.FAIL,
        )

    def test_cleanup_failure_has_highest_precedence(self) -> None:
        calls = list(good_build().calls)
        calls[2] = replace(calls[2], use_plan=False)
        result = evaluate_build(
            replace(good_build(), calls=tuple(calls), cleanup_ok=False),
        )
        self.assertEqual(result.verdict, Verdict.FAIL_CLEANUP)

    def test_both_target_builds_are_required_for_matrix_pass(self) -> None:
        both = tuple(good_build(build) for build in TARGET_BUILDS)
        self.assertEqual(evaluate_matrix(both).verdict, Verdict.PASS)
        self.assertEqual(evaluate_matrix(both[:1]).verdict, Verdict.NOT_PROVEN)
        self.assertEqual(
            evaluate_matrix((*both, good_build("2019/15.0"))).verdict,
            Verdict.FAIL,
        )


if __name__ == "__main__":
    unittest.main()
