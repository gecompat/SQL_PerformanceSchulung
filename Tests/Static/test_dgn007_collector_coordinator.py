#!/usr/bin/env python3
"""Synthetic prequalification checks; no SQL execution or runtime attestation."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Tests" / "Static"))
from Tests.Contracts import dgn007_collector_coordinator as coordinator
from Tests.Contracts import dgn007_prospective_acceptance as acceptance
sys.modules["dgn007_prospective_acceptance"] = acceptance
from test_dgn007_prospective_acceptance import fixture_runs
from validate_dgn007_prospective_acceptance import CONTRACT


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.contract = acceptance.contract_from_mapping(
            json.loads(CONTRACT.read_text(encoding="utf-8")))
        self.records = fixture_runs(self.contract)
        self.runs = tuple(self.make_run(record, index) for index, record in enumerate(self.records))

    @staticmethod
    def make_run(record, index):
        start = index * 200_000_000_000
        phases = []
        cursor = start
        for name in coordinator.PHASES:
            duration = 1_000_000_000
            phases.append(coordinator.TimedPhase(name, cursor, cursor + duration, "PASS", "OK"))
            cursor += duration
        return coordinator.CoordinatedRun(
            record, start, cursor, tuple(phases), 4, 8192, 1, 1, True, True)

    def reject(self, runs, code="FAIL_CONTRACT"):
        with self.assertRaises(coordinator.CoordinatorError) as raised:
            coordinator.validate_sequence(self.contract, runs)
        self.assertEqual(raised.exception.code, code)
        self.assertEqual(str(raised.exception), code)
        self.assertIsNone(raised.exception.__cause__)

    def test_validates_complete_dec068_order_and_returns_full_records(self):
        self.assertEqual(coordinator.validate_sequence(self.contract, self.runs), self.records)

    def test_rejects_wrong_scope_or_order(self):
        wrong = list(self.runs)
        wrong[0] = replace(wrong[0], record=replace(wrong[0].record, scope="DGN-007_CONTROL_BA"))
        self.reject(tuple(wrong), "FAIL_RESULT_CONTRACT")
        self.reject((self.runs[1], *self.runs[1:]), "FAIL_RESULT_CONTRACT")

    def test_rejects_overlap_budget_resource_and_unconfirmed_cleanup(self):
        overlap = list(self.runs)
        overlap[1] = replace(overlap[1], started_ns=overlap[0].finished_ns - 1)
        self.reject(tuple(overlap))
        self.reject((replace(self.runs[0], configured_memory_mb=8191), *self.runs[1:]))
        self.reject((replace(self.runs[0], cleanup_independently_confirmed=False), *self.runs[1:]),
                    "FAIL_CLEANUP")
        phases = list(self.runs[0].phases)
        cursor = self.runs[0].started_ns
        for index, phase in enumerate(phases):
            duration = 30_000_000_000 if index < 7 else 1_000_000_000
            phases[index] = replace(phase, started_ns=cursor,
                                    finished_ns=cursor + duration)
            cursor += duration
        self.reject((replace(self.runs[0], finished_ns=cursor,
                             phases=tuple(phases)), *self.runs[1:]), "FAIL_TIMEOUT")

    def test_rejects_incomplete_matrix_as_missing_evidence(self):
        self.reject(self.runs[:-1], "SKIP_EVIDENCE_MISSING")

    def test_validation_is_not_runtime_attestation(self):
        self.assertEqual(coordinator.validate_sequence(self.contract, self.runs), self.records)
        self.assertFalse(getattr(self.records[0], "runtime_attested", False))
        self.assertIn("does not establish", coordinator.__doc__)


if __name__ == "__main__":
    unittest.main()
