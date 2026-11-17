#!/usr/bin/env python3
"""Synthetische Receipt-Bindungsprüfungen; kein SQL-Lauf."""
from __future__ import annotations

from dataclasses import replace
import inspect
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Tests" / "Static"))
from Tests.Contracts import dgn007_collector_receipt_binding as binding
from Tests.Contracts import dgn007_collector_coordinator as coordinator
from Tests.Contracts import dgn007_collector_transport as transport
from Tests.Contracts import dgn007_prospective_acceptance as acceptance
from Tests.Runtime.run_dgn007_automated_setup import (
    _CaptureReceipt, RunnerFailure, SourceSnapshot, capture_source_snapshot,
)
from test_dgn007_collector_transport import encode, payload
from validate_dgn007_prospective_acceptance import CONTRACT


class ReceiptBindingTests(unittest.TestCase):
    def setUp(self):
        self.contract = acceptance.contract_from_mapping(
            json.loads(CONTRACT.read_text(encoding="utf-8")))
        self.source_snapshot = capture_source_snapshot(ROOT, self.contract)
        value = payload(self.contract, major=16, sequence="BA")
        self.body = transport.decode_capture(encode(value), self.contract)
        self.receipt = _CaptureReceipt(
            7, self.body,
            tuple((name, "PASS", "OK") for name in acceptance.PHASE_IDS),
            "PASS", "OK", 1_000_000_000, 8_000_000_000, 9_000_000_000,
            4, 8192, 1, 1,
            phase_timing=tuple((name, 1_000_000_000 + index * 800_000_000,
                                1_000_000_000 + (index + 1) * 800_000_000)
                               for index, name in enumerate(coordinator.PHASES[:-1])),
            source_freeze_before=self.source_snapshot,
            source_freeze_after=self.source_snapshot)

    def bind(self, **overrides):
        args = dict(expected_major=16, block=1, slot=2, lifecycle_id=41,
                    active_versions_on_host=1)
        args.update(overrides)
        return binding.bind_receipt(self.contract, self.receipt, **args)

    def test_binds_outer_lifecycle_and_cleanup_from_receipt(self):
        result = self.bind()
        self.assertEqual((result.started_ns, result.finished_ns), (1_000_000_000, 9_000_000_000))
        self.assertEqual((result.phases[-1].started_ns, result.phases[-1].finished_ns),
                         (8_000_000_000, 9_000_000_000))
        self.assertEqual(tuple((phase.phase_id, phase.started_ns, phase.finished_ns)
                               for phase in result.phases[:-1]), self.receipt.phase_timing)
        self.assertTrue(result.cleanup_independently_confirmed)
        self.assertEqual(result.record.windows, self.body.windows)

    def test_phase_times_are_receipt_bound_instead_of_caller_supplied(self):
        self.assertNotIn("observed_phases", inspect.signature(binding.bind_receipt).parameters)
        self.assertNotIn("observed_phases", binding.ReceiptObservation.__dataclass_fields__)
        self.receipt = replace(self.receipt, phases=self.receipt.phases[:-1])
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            self.bind()
        self.assertEqual(raised.exception.code, "FAIL_RESULT_CONTRACT")

    def test_source_freeze_is_receipt_bound_and_caller_cannot_assert_it(self):
        self.assertNotIn("source_freeze_verified", inspect.signature(binding.bind_receipt).parameters)
        self.receipt = replace(self.receipt, source_freeze_after=SourceSnapshot(
            self.contract.source_digest, tuple((name, "0" * 64)
                                               for name, _ in self.source_snapshot.hashes)))
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            self.bind()
        self.assertEqual(raised.exception.code, "FAIL_RESULT_CONTRACT")

    def test_docker_cpu_and_memory_limits_are_receipt_bound(self):
        result = self.bind()
        self.assertEqual((result.configured_cpus, result.configured_memory_mb), (4, 8192))
        self.assertNotIn("configured_cpus", inspect.signature(binding.bind_receipt).parameters)
        self.assertNotIn("configured_memory_mb", inspect.signature(binding.bind_receipt).parameters)
        self.assertNotIn("configured_cpus", binding.ReceiptObservation.__dataclass_fields__)
        self.assertNotIn("configured_memory_mb", binding.ReceiptObservation.__dataclass_fields__)
        self.assertNotIn("active_sql_sessions", inspect.signature(binding.bind_receipt).parameters)
        self.assertNotIn("active_sql_sessions", binding.ReceiptObservation.__dataclass_fields__)
        self.assertEqual(result.active_sql_sessions, 1)
        with self.assertRaisesRegex(RunnerFailure, "FAIL_CONTRACT"):
            replace(self.receipt, configured_cpus=3)
        with self.assertRaisesRegex(RunnerFailure, "FAIL_CONTRACT"):
            replace(self.receipt, active_sql_sessions_after=2)

    def test_rejects_outer_phase_ticks_outside_receipt_lifecycle(self):
        with self.assertRaisesRegex(RunnerFailure, "FAIL_CONTRACT"):
            replace(self.receipt, phase_timing=(
                *self.receipt.phase_timing[:-1],
                (self.receipt.phase_timing[-1][0], 7_200_000_000, 8_100_000_000)))

    def test_rejects_nonmonotone_or_failed_outer_phase_before_binding(self):
        out_of_order = (*self.receipt.phase_timing[:2],
                        (self.receipt.phase_timing[2][0], 1_500_000_000, 2_500_000_000),
                        *self.receipt.phase_timing[3:])
        with self.assertRaisesRegex(RunnerFailure, "FAIL_CONTRACT"):
            replace(self.receipt, phase_timing=out_of_order)

    def test_rejects_receipt_phases_over_regular_budget(self):
        start = 1_000_000_000
        timing = tuple((name, start + index, start + index + 1)
                       for index, name in enumerate(coordinator.PHASES[:-2])) + (
            ("CONTROL_EVIDENCE", start + 7, start + 181_000_000_000),)
        self.receipt = replace(self.receipt, lifecycle_started_ns=start,
                               cleanup_started_ns=start + 182_000_000_000,
                               lifecycle_finished_ns=start + 183_000_000_000,
                               phase_timing=timing)
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            self.bind()
        self.assertEqual(raised.exception.code, "FAIL_TIMEOUT")

    def test_rejects_unconfirmed_absence_and_invalid_outer_ticks(self):
        self.receipt = replace(self.receipt, first_absence_outcome="FAIL")
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            self.bind()
        self.assertEqual(raised.exception.code, "FAIL_CLEANUP")
        self.receipt = replace(self.receipt, first_absence_outcome="PASS",
                               lifecycle_finished_ns=8_000_000_000)
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            self.bind()
        self.assertEqual(raised.exception.code, "FAIL_CLEANUP")

    def test_explicitly_limits_claim_to_receipt_bound_fields(self):
        self.assertIn("Randproben beweisen keine", binding.__doc__)

    def make_matrix(self):
        receipts = []
        observations = []
        for index, (_block, _slot, label) in enumerate(coordinator.EXPECTED_SEQUENCE):
            start = index * 200_000_000_000 + 1_000_000_000
            body = transport.decode_capture(
                encode(payload(self.contract, major=16, sequence=label)), self.contract)
            receipts.append(_CaptureReceipt(
                index + 1, body,
                tuple((name, "PASS", "OK") for name in acceptance.PHASE_IDS),
                "PASS", "OK", start, start + 8_000_000_000, start + 9_000_000_000,
                4, 8192, 1, 1,
                phase_timing=tuple((name, start + phase_index * 900_000_000,
                                    start + (phase_index + 1) * 900_000_000)
                                   for phase_index, name in enumerate(coordinator.PHASES[:-1])),
                source_freeze_before=self.source_snapshot,
                source_freeze_after=self.source_snapshot))
            observations.append(binding.ReceiptObservation(
                index + 1, 1))
        return tuple(receipts), tuple(observations)

    def test_binds_six_receipts_in_dec068_order_and_prequalifies_sequence(self):
        receipts, observations = self.make_matrix()
        runs = binding.bind_sequence(self.contract, receipts, expected_major=16,
                                     observations=observations)
        self.assertEqual(len(runs), 6)
        self.assertEqual(tuple(run.record.scope for run in runs), tuple(
            "DGN-007_CONTROL_" + label for _block, _slot, label in coordinator.EXPECTED_SEQUENCE))
        self.assertEqual(coordinator.validate_sequence(self.contract, runs), tuple(
            run.record for run in runs))

    def test_sequence_binding_rejects_reordered_reused_and_missing_receipts(self):
        receipts, observations = self.make_matrix()
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            binding.bind_sequence(self.contract, (receipts[1], *receipts[1:]),
                                  expected_major=16, observations=observations)
        self.assertEqual(raised.exception.code, "FAIL_RESULT_CONTRACT")
        repeated = (observations[0], *observations[1:-1],
                    replace(observations[-1], lifecycle_id=observations[0].lifecycle_id))
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            binding.bind_sequence(self.contract, receipts, expected_major=16,
                                  observations=repeated)
        self.assertEqual(raised.exception.code, "FAIL_RESULT_CONTRACT")
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            binding.bind_sequence(self.contract, receipts[:-1], expected_major=16,
                                  observations=observations)
        self.assertEqual(raised.exception.code, "SKIP_EVIDENCE_MISSING")


if __name__ == "__main__":
    unittest.main()
