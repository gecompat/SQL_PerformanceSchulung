#!/usr/bin/env python3
"""Synthetische Receipt-Bindungsprüfungen; kein SQL-Lauf."""
from __future__ import annotations

from dataclasses import replace
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
from Tests.Runtime.run_dgn007_automated_setup import _CaptureReceipt
from test_dgn007_collector_transport import encode, payload
from validate_dgn007_prospective_acceptance import CONTRACT


class ReceiptBindingTests(unittest.TestCase):
    def setUp(self):
        self.contract = acceptance.contract_from_mapping(
            json.loads(CONTRACT.read_text(encoding="utf-8")))
        value = payload(self.contract, major=16, sequence="BA")
        self.body = transport.decode_capture(encode(value), self.contract)
        self.receipt = _CaptureReceipt(
            7, self.body,
            tuple((name, "PASS", "OK") for name in acceptance.PHASE_IDS),
            "PASS", "OK", 1_000_000_000, 8_000_000_000, 9_000_000_000)
        self.observed = tuple(coordinator.TimedPhase(
            name, 1_000_000_000 + index * 900_000_000,
            1_000_000_000 + (index + 1) * 900_000_000, "PASS", "OK")
            for index, name in enumerate(coordinator.PHASES[:-1]))

    def bind(self, **overrides):
        args = dict(expected_major=16, block=1, slot=2, lifecycle_id=41,
                    observed_phases=self.observed, configured_cpus=4,
                    configured_memory_mb=8192, active_sql_sessions=1,
                    active_versions_on_host=1, source_freeze_verified=True)
        args.update(overrides)
        return binding.bind_receipt(self.contract, self.receipt, **args)

    def test_binds_outer_lifecycle_and_cleanup_from_receipt(self):
        result = self.bind()
        self.assertEqual((result.started_ns, result.finished_ns), (1_000_000_000, 9_000_000_000))
        self.assertEqual((result.phases[-1].started_ns, result.phases[-1].finished_ns),
                         (8_000_000_000, 9_000_000_000))
        self.assertTrue(result.cleanup_independently_confirmed)
        self.assertEqual(result.record.windows, self.body.windows)

    def test_rejects_caller_supplied_cleanup_or_incomplete_receipt_phases(self):
        with self.assertRaises(coordinator.CoordinatorError):
            self.bind(observed_phases=(*self.observed,
                         coordinator.TimedPhase("CLEANUP", 8_000_000_000, 9_000_000_000, "PASS", "OK")))
        self.receipt = replace(self.receipt, phases=self.receipt.phases[:-1])
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            self.bind()
        self.assertEqual(raised.exception.code, "FAIL_RESULT_CONTRACT")

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
        self.assertIn("Ressourcen und Source-Freeze bleiben Eingaben", binding.__doc__)

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
                "PASS", "OK", start, start + 8_000_000_000, start + 9_000_000_000))
            phases = tuple(coordinator.TimedPhase(
                name, start + phase_index * 900_000_000,
                start + (phase_index + 1) * 900_000_000, "PASS", "OK")
                for phase_index, name in enumerate(coordinator.PHASES[:-1]))
            observations.append(binding.ReceiptObservation(
                index + 1, phases, 4, 8192, 1, 1, True))
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
