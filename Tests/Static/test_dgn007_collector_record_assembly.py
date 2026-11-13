"""Synthetische Recordabbildung; keine Herkunfts- oder Runtimeattestation."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from Tests.Contracts import dgn007_collector_record_assembly as assembly
from Tests.Contracts import dgn007_collector_transport as transport
from Tests.Contracts import dgn007_prospective_acceptance as acceptance
from test_dgn007_collector_transport import encode, payload
from validate_dgn007_prospective_acceptance import CONTRACT


class CollectorRecordAssemblyTests(unittest.TestCase):
    def setUp(self):
        mapping = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.contract = acceptance.contract_from_mapping(mapping)
        value = payload(self.contract, major=16, sequence="BA")
        self.body = transport.decode_capture(encode(value), self.contract)
        self.phases = tuple(acceptance.PhaseResult(name, "PASS", "OK")
                            for name in acceptance.PHASE_IDS)
        self.absence = acceptance.PhaseResult("CLEANUP_ABSENCE", "PASS", "OK")

    def assemble(self, **overrides):
        args = dict(expected_major=16, block=1, slot=2, lifecycle_id=41,
                    phases=self.phases, absence=self.absence)
        args.update(overrides)
        body = args.pop("body", self.body)
        return assembly.assemble_run(body, self.contract, **args)

    def reject(self, code="FAIL_CONTRACT", **overrides):
        with self.assertRaises(assembly.AssemblyError) as raised:
            self.assemble(**overrides)
        self.assertEqual(raised.exception.code, code)
        self.assertEqual(str(raised.exception), code)
        self.assertIsNone(raised.exception.__cause__)
        self.assertIsNone(raised.exception.__context__)

    def test_maps_all_scalars_without_rounding_or_record_loss(self):
        run = self.assemble()
        self.assertIs(type(run), acceptance.RunRecord)
        self.assertEqual(run.scope, "DGN-007_CONTROL_BA")
        self.assertEqual(run.block, 1)
        self.assertEqual(run.slot, 2)
        self.assertEqual(run.lifecycle_id, 41)
        self.assertEqual(run.windows, self.body.windows)
        self.assertEqual(run.families, self.body.families)
        self.assertEqual(run.plans, self.body.plans)
        self.assertEqual(run.plan_union, self.body.plan_union)
        self.assertEqual(tuple((row.window_id, row.ordinal, row.request_log_id,
                                row.group_key, row.status_code, row.returned_rows)
                               for row in run.requests),
                         tuple((row.window_id, row.ordinal, row.request_log_id,
                                row.group_key, row.status_code, row.returned_rows)
                               for row in self.body.requests))
        self.assertEqual(run.windows[0].avg_duration_us, self.body.windows[0].avg_duration_us)
        self.assertFalse(getattr(run, "runtime_attested", False))

    def test_does_not_fill_missing_request_result_counts(self):
        value = payload(self.contract, major=16, sequence="BA", measured=False)
        body = transport.decode_capture(encode(value), self.contract)
        with self.assertRaises(assembly.AssemblyError) as raised:
            assembly.assemble_run(body, self.contract, expected_major=16, block=1, slot=2, lifecycle_id=41,
                                  phases=self.phases, absence=self.absence)
        self.assertEqual(raised.exception.code, "FAIL_RESULT_CONTRACT")

    def test_rejects_declared_sequence_mismatch(self):
        self.reject("FAIL_RESULT_CONTRACT", slot=1)
        self.reject("FAIL_RESULT_CONTRACT", expected_major=15)

    def test_revalidates_body_records_after_transport(self):
        broken_window = replace(self.body.windows[0], request_count=3)
        broken_body = replace(self.body, windows=(broken_window, self.body.windows[1]))
        self.reject("FAIL_RESULT_CONTRACT", body=broken_body)

    def test_rejects_nonpassing_phase_and_cleanup_evidence(self):
        phases = list(self.phases)
        phases[-1] = replace(phases[-1], outcome="FAIL", code="FAIL_CLEANUP")
        self.reject(phases=tuple(phases))
        self.reject(absence=replace(self.absence, outcome="FAIL", code="FAIL_CLEANUP"))

    def test_rejects_duplicate_or_nonpositive_lifecycle_id(self):
        self.reject(lifecycle_id=0)
        self.reject(lifecycle_id=True)

    def test_mapper_explicitly_does_not_attest_runtime_or_source(self):
        self.assertFalse(self.body.runtime_attested)
        self.assertEqual(self.body.validation_scope, "PROJECT_SEMANTIC")
        self.assertIn("Herkunft", assembly.__doc__)


if __name__ == "__main__":
    unittest.main()
