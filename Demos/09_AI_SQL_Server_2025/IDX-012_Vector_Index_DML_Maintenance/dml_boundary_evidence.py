"""Fester lokaler DML-Vertrag; kein SQL-Aufruf und keine Generationsableitung."""
import re

OPERATIONS = ('UPDATE_ID_23', 'DELETE_ID_23', 'INSERT_ID_1000', 'MERGE_UPDATE_ID_23')
DURING_ROWS = {'UPDATE_ID_23': 999, 'DELETE_ID_23': 998,
               'INSERT_ID_1000': 1000, 'MERGE_UPDATE_ID_23': 999}


def validate_dml_boundary(rows, *, token, database_id):
    if (not isinstance(token, str) or not re.fullmatch('[A-F0-9]{16}', token)
            or type(database_id) is not int or database_id < 5):
        raise ValueError('Independent complete own identity required')
    selected = [r for r in rows if r.get('kind') == 'DML_BOUNDARY']
    expected = [(stage, operation) for stage in ('NO_INDEX', 'WITH_INDEX') for operation in OPERATIONS]
    if len(selected) != len(expected):
        raise ValueError('Complete eight-operation coverage missing')
    errors = []
    for ordinal, (r, (stage, operation)) in enumerate(zip(selected, expected), 1):
        if (r.get('Stage') != stage or r.get('Operation') != operation
                or type(r.get('Ordinal')) is not int or r['Ordinal'] != ordinal
                or r.get('RunToken') != token or type(r.get('DatabaseId')) is not int
                or r['DatabaseId'] != database_id
                or r.get('Context') != 'SQLPERF_LAB_IDX012_' + token
                or r.get('StaleOptionState') != 'ABSENT'):
            raise ValueError('Fixed operation order, own identity or no-stale profile changed')
        if (r.get('SourceRestored') is not True or r.get('RolledBack') is not True
                or any(type(r.get(k)) is not int or r[k] != 0
                       for k in ('TransactionCount', 'TransactionState'))
                or type(r.get('RestoredRowCount')) is not int or r['RestoredRowCount'] != 999):
            raise ValueError('Full actual rollback/source restoration missing')
        if stage == 'NO_INDEX':
            if (r.get('Succeeded') is not True or r.get('ExpectedChange') is not True
                    or type(r.get('AffectedRows')) is not int or r['AffectedRows'] != 1
                    or type(r.get('DuringRowCount')) is not int
                    or r['DuringRowCount'] != DURING_ROWS[operation]
                    or any(r.get(k) is not None for k in ('ErrorNumber', 'ErrorState', 'ErrorMessage'))):
                raise ValueError('Actual successful pre-index positive control missing')
        else:
            if (r.get('Succeeded') is not False
                    or any(r.get(k) is not None for k in ('AffectedRows', 'DuringRowCount', 'ExpectedChange'))
                    or type(r.get('ErrorNumber')) is not int or r['ErrorNumber'] != 42231
                    or type(r.get('ErrorState')) is not int or r['ErrorState'] != 1
                    or not isinstance(r.get('ErrorMessage'), str)
                    or not 1 <= len(r['ErrorMessage']) <= 4000
                    or r.get('IndexMetadataUnchanged') is not True):
                raise ValueError('Actual fixed-profile SQL rejection or index preservation missing')
            errors.append({'operation': operation, 'number': r['ErrorNumber'], 'state': r['ErrorState']})
    return {'kind': 'DML_BOUNDARY_SUMMARY', 'operations': list(OPERATIONS),
            'positive_controls': 4, 'rejected_with_index': errors,
            'source_restored': True, 'stale_option': 'ABSENT', 'generation': 'UNKNOWN',
            'freshness': 'NOT_TESTED', 'runtime_qualification': 'NOT_ESTABLISHED'}
