"""Synthetic fixed-contract tests; no historical report replay or SQL execution."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ann_dml_role_evidence as evidence


def fixture():
    binding = {'consumer_sources': evidence.source_binding(),
               'provenance': 'PUREFIXTURE_ONLY', 'generation': 'UNKNOWN'}
    lifecycle = {
        'ordinal': 1, 'operation': 'UPDATE', 'target_id': 23, 'outcome': 'REJECTED',
        'error_number': 42231, 'error_state': 1, 'transaction_count': 0,
        'transaction_state': 0, 'rolled_back': True, 'source_unchanged': True,
        'index_metadata_unchanged': True, 'cleanup_status': 'PASS',
    }
    record = {
        'contract': evidence.SCHEMA, 'profile': copy.deepcopy(evidence.EXPECTED['profile']),
        'source_pins': copy.deepcopy(evidence.EXPECTED['source_pins']),
        'lifecycles': [copy.deepcopy(lifecycle), {**lifecycle, 'ordinal': 2}],
        'role_evidence': {'status': 'NOT_ESTABLISHED', 'reason': 'NO_ANN_ROLE_CAPTURE'},
    }
    return record, binding


class AnnDmlRecordTests(unittest.TestCase):
    def rejected(self, mutate):
        record, binding = fixture()
        mutate(record, binding)
        with self.assertRaises((ValueError, TypeError)):
            evidence.report(record, binding)

    def test_synthetic_record_is_coherent_warn_without_claim_promotion(self):
        record, binding = fixture()
        result = evidence.report(record, binding)
        self.assertEqual(result['record_validation'], 'COHERENT')
        self.assertEqual(result['outcome'], 'WARN')
        self.assertEqual(result['counts']['rejected_update_lifecycles'], 2)
        self.assertEqual(result['counts']['role_records'], 0)
        self.assertEqual(result['claims']['ann_update_support'], 'NOT_ESTABLISHED')
        self.assertEqual(result['claims']['ann_role_runtime_qualification'], 'NOT_ESTABLISHED')

    def test_exact_schema_profile_source_and_binding_are_required(self):
        self.rejected(lambda r, b: r.update(extra='x'))
        self.rejected(lambda r, b: r.update(profile={**r['profile'], 'build': 'other'}))
        self.rejected(lambda r, b: r.update(source_pins={**r['source_pins'], 'lifecycle02.log': '0'*64}))
        self.rejected(lambda r, b: b.update(generation='2'))
        self.rejected(lambda r, b: b.update(provenance='ATTESTED'))
        self.rejected(lambda r, b: b.update(consumer_sources={'foreign.py': '0'*64}))

    def test_each_lifecycle_is_fixed_target_rejection_and_closed_rollback(self):
        changes = [
            {'operation': 'DELETE'}, {'target_id': 24}, {'outcome': 'ACCEPTED'},
            {'error_number': 229}, {'error_state': True}, {'transaction_count': False},
            {'transaction_state': 1}, {'rolled_back': False}, {'source_unchanged': False},
            {'index_metadata_unchanged': False}, {'cleanup_status': 'UNKNOWN'},
        ]
        for change in changes:
            self.rejected(lambda r, b, c=change: r['lifecycles'][0].update(c))
        self.rejected(lambda r, b: r['lifecycles'].pop())
        self.rejected(lambda r, b: r['lifecycles'][1].update(ordinal=1))

    def test_role_records_must_not_be_inferred_from_other_profile(self):
        for status in ('PASS', 'WARN', 'DECLARED'):
            self.rejected(lambda r, b, s=status: r.update(role_evidence={'status': s, 'reason': 'NO_ANN_ROLE_CAPTURE'}))
        self.rejected(lambda r, b: r.update(role_evidence={'status': 'NOT_ESTABLISHED', 'reason': 'OTHER'}))

    def test_fixed_expected_contract_rejects_drift(self):
        record, binding = fixture()
        with tempfile.TemporaryDirectory() as folder:
            contract = Path(folder) / 'contract.json'
            changed = copy.deepcopy(evidence.EXPECTED)
            changed['claims']['ann_update_support'] = 'PASS'
            contract.write_text(json.dumps(changed), encoding='utf-8')
            with patch.object(evidence, 'CONTRACT', contract):
                with self.assertRaisesRegex(ValueError, 'FIXED_CONTRACT_DRIFT'):
                    evidence.report(record, binding)


if __name__ == '__main__':
    unittest.main()
