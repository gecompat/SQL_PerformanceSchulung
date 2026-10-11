"""Synthetische DML-Evidenzgegenproben; kein SQL oder Container."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'Demos/09_AI_SQL_Server_2025/IDX-012_Vector_Index_DML_Maintenance'))
from dml_boundary_evidence import DURING_ROWS, OPERATIONS, validate_dml_boundary

TOKEN = 'ABCDEF0123456789'


def fixture():
    rows = []
    for stage in ('NO_INDEX', 'WITH_INDEX'):
        for operation in OPERATIONS:
            success = stage == 'NO_INDEX'
            rows.append({'kind': 'DML_BOUNDARY', 'Stage': stage, 'Operation': operation,
                         'Ordinal': len(rows) + 1, 'RunToken': TOKEN, 'DatabaseId': 5,
                         'Context': 'SQLPERF_LAB_IDX012_' + TOKEN, 'StaleOptionState': 'ABSENT',
                         'Succeeded': success, 'AffectedRows': 1 if success else None,
                         'DuringRowCount': DURING_ROWS[operation] if success else None,
                         'ExpectedChange': True if success else None,
                         'ErrorNumber': None if success else 42231, 'ErrorState': None if success else 1,
                         'ErrorMessage': None if success else 'Synthetic vector index rejection',
                         'SourceRestored': True, 'RolledBack': True, 'RestoredRowCount': 999,
                         'TransactionCount': 0, 'TransactionState': 0,
                         'IndexMetadataUnchanged': True if not success else None})
    return rows


def validate(rows, **changes):
    return validate_dml_boundary(rows, **dict({'token': TOKEN, 'database_id': 5}, **changes))


class DmlBoundaryTests(unittest.TestCase):
    def test_complete_fixed_profile_is_not_generation_or_freshness_proof(self):
        result = validate(fixture())
        self.assertEqual(result['positive_controls'], 4)
        self.assertEqual(len(result['rejected_with_index']), 4)
        self.assertEqual(result['generation'], 'UNKNOWN')
        self.assertEqual(result['freshness'], 'NOT_TESTED')
        self.assertEqual(result['runtime_qualification'], 'NOT_ESTABLISHED')

    def test_missing_duplicate_and_reordered_operations_rejected(self):
        original = fixture()
        for rows in (original[:-1], original + [original[0]], original[::-1], original[:4] + original[:4]):
            with self.assertRaises(ValueError):
                validate(rows)

    def test_foreign_context_token_or_database_rejected(self):
        for field, value in (('RunToken', TOKEN + ' '), ('Context', 'SQLPERF_LAB_IDX012_FOREIGN'),
                             ('DatabaseId', 6), ('DatabaseId', True), ('Ordinal', True)):
            rows = fixture(); rows[4][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(rows)

    def test_untrusted_expected_identity_rejected(self):
        for changes in ({'token': TOKEN + ' '}, {'database_id': True}, {'database_id': 4}):
            with self.assertRaises(ValueError):
                validate(fixture(), **changes)

    def test_real_positive_change_and_affected_row_required(self):
        for field, value in (('Succeeded', False), ('ExpectedChange', None), ('AffectedRows', 0),
                             ('AffectedRows', True), ('DuringRowCount', 1001), ('ErrorNumber', 42231)):
            rows = fixture(); rows[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(rows)

    def test_insert_never_uses_a_duplicate_or_zero_row_control(self):
        for value in (998, 999, 1001, None, True):
            rows = fixture(); rows[2]['DuringRowCount'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate(rows)

    def test_changed_actual_error_is_a_failure_not_inferred_expected_error(self):
        for field, value in (('ErrorNumber', 2627), ('ErrorNumber', True), ('ErrorState', 0),
                             ('ErrorState', True), ('ErrorMessage', ''), ('ErrorMessage', 'x' * 4001)):
            rows = fixture(); rows[4][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(rows)

    def test_unexpected_success_does_not_qualify_readonly_profile(self):
        rows = fixture(); rows[4].update(Succeeded=True, AffectedRows=1, DuringRowCount=999,
                                        ExpectedChange=True, ErrorNumber=None, ErrorState=None, ErrorMessage=None)
        with self.assertRaises(ValueError):
            validate(rows)

    def test_missing_or_open_transaction_and_source_rejected(self):
        for field in ('TransactionCount', 'TransactionState', 'RestoredRowCount'):
            for value in (None, True, -1, 1):
                rows = fixture(); rows[7][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    validate(rows)
        for field in ('RolledBack', 'SourceRestored', 'IndexMetadataUnchanged'):
            rows = fixture(); rows[7][field] = 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(rows)

    def test_rejection_cannot_have_conflicting_success_evidence(self):
        for field, value in (('AffectedRows', 0), ('DuringRowCount', 999), ('ExpectedChange', False)):
            rows = fixture(); rows[5][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(rows)

    def test_stale_option_and_operation_changes_rejected(self):
        for field, value in (('Operation', 'INSERT_OTHER'), ('Stage', 'AFTER_DROP'), ('StaleOptionState', 'ON')):
            rows = fixture(); rows[6][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(rows)


if __name__ == '__main__':
    unittest.main()
