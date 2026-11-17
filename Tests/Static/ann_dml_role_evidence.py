"""Bounded offline contract for the recorded ANN UPDATE rejection; no SQL/runtime imports."""
from pathlib import Path
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = HERE / 'Fixtures/ann/ANN_DML_ROLE.result-contract.json'
SCHEMA = 'ANN_DML_ROLE_RECORD_V1'
EXPECTED = {
    'contract': SCHEMA,
    'profile': {
        'build': '17.0.5005.3', 'engine_edition': 3, 'os': 'Linux',
        'compatibility_level': 170, 'index_type': 'DiskANN', 'metric': 'COSINE',
        'dimension': 3, 'generation': 'UNKNOWN',
    },
    'expected': {
        'completed_update_lifecycles': 2, 'rejected_update_lifecycles': 2,
        'target_id': 23, 'error_number': 42231, 'error_state': 1,
        'transaction_count_after_rollback': 0, 'transaction_state_after_rollback': 0,
    },
    'claims': {
        'ann_update_support': 'NOT_ESTABLISHED',
        'ann_role_runtime_qualification': 'NOT_ESTABLISHED',
        'freshness': 'NOT_ESTABLISHED', 'generation': 'UNKNOWN',
        'record_origin': 'DECLARED_NOT_INDEPENDENTLY_ATTESTED',
    },
    'source_pins': {
        'qualify_build.py': '5142919355817A2866EBDA9A1C35E7CB57D5989432A70F9917C6491245CAA9AA',
        'sql_build.py': '43F29045E6DFB617B8300EA631C63ACCFEA0A86EBD2010EA3FADF8BA0850A2A3',
        'dml_evidence.py': '4A7765629B0BECD60AD269CE882104B1C0BA0EFA98AC323B980BC9C698B6A4DB',
        'test_dml.py': 'BB529020933695604C266D4EE1F4C2288C61BC3C4BAC69AB9F485BC525F092AC',
        'lifecycle01.log': '05D93292BBB4C5762C7747CA8F6F1FD02EB93EDB512CE603CF4B90F612DAB4B6',
        'lifecycle02.log': '1A0FA5FB6F9A765E6B65BA78D10005F531EC7162400EA2D39E0E649480541918',
    },
}


def _fail(code):
    raise ValueError(code)


def _exact(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        _fail('EXACT_SCHEMA_REQUIRED')


def _plain(value, depth=0):
    if depth > 8:
        _fail('BOUNDED_RECORD_DEPTH')
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            _fail('STRING_KEYS_REQUIRED')
        for item in value.values():
            _plain(item, depth + 1)
    elif type(value) is list:
        if len(value) > 20:
            _fail('BOUNDED_RECORD_LIST')
        for item in value:
            _plain(item, depth + 1)
    elif type(value) is float:
        if not math.isfinite(value):
            _fail('FINITE_NUMBERS_REQUIRED')
    elif type(value) is str:
        if len(value) > 4000:
            _fail('BOUNDED_RECORD_STRING')
    elif type(value) not in (int, bool, type(None)):
        _fail('PLAIN_BUILTIN_TYPES_REQUIRED')


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail('DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def _read_contract():
    raw = CONTRACT.read_bytes()
    if len(raw) > 10000:
        _fail('BOUNDED_CONTRACT_REQUIRED')
    actual = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique,
                        parse_constant=lambda _: _fail('FINITE_JSON_REQUIRED'))
    _plain(actual)
    if _canonical(actual) != _canonical(EXPECTED):
        _fail('FIXED_CONTRACT_DRIFT')
    return actual


def source_binding():
    """Bind consumer and fixed contract bytes only; this does not attest record origin."""
    paths = (Path(__file__).resolve(), CONTRACT)
    return {str(path.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def report(record, binding):
    """Validate two supplied historical lifecycle summaries and return a bounded WARN."""
    _read_contract()
    _plain(record)
    _plain(binding)
    _exact(binding, ('consumer_sources', 'provenance', 'generation'))
    if binding['consumer_sources'] != source_binding():
        _fail('ACTUAL_CONSUMER_SOURCE_BINDING_REQUIRED')
    if binding['provenance'] not in ('PUREFIXTURE_ONLY', 'DECLARED_HISTORICAL_CAPTURE'):
        _fail('EXPLICIT_RECORD_ORIGIN_REQUIRED')
    if binding['generation'] != 'UNKNOWN':
        _fail('GENERATION_MUST_REMAIN_UNKNOWN')
    _exact(record, ('contract', 'profile', 'source_pins', 'lifecycles', 'role_evidence'))
    if record['contract'] != SCHEMA or record['profile'] != EXPECTED['profile']:
        _fail('FIXED_PROFILE_REQUIRED')
    if record['source_pins'] != EXPECTED['source_pins']:
        _fail('HISTORICAL_SOURCE_PINS_REQUIRED')
    lifecycles = record['lifecycles']
    if type(lifecycles) is not list or len(lifecycles) != 2:
        _fail('TWO_RECORDED_LIFECYCLES_REQUIRED')
    for ordinal, row in enumerate(lifecycles, 1):
        _exact(row, ('ordinal', 'operation', 'target_id', 'outcome', 'error_number',
                     'error_state', 'transaction_count', 'transaction_state',
                     'rolled_back', 'source_unchanged', 'index_metadata_unchanged',
                     'cleanup_status'))
        if type(row['ordinal']) is not int or row['ordinal'] != ordinal:
            _fail('FIXED_LIFECYCLE_ORDER_REQUIRED')
        if row['operation'] != 'UPDATE' or type(row['target_id']) is not int or row['target_id'] != 23:
            _fail('ONLY_FIXED_UPDATE_TARGET_IS_SUPPORTED')
        if row['outcome'] != 'REJECTED' or type(row['error_number']) is not int or row['error_number'] != 42231:
            _fail('OBSERVED_UPDATE_REJECTION_REQUIRED')
        if type(row['error_state']) is not int or row['error_state'] != 1:
            _fail('OBSERVED_ERROR_STATE_REQUIRED')
        for key in ('transaction_count', 'transaction_state'):
            if type(row[key]) is not int or row[key] != 0:
                _fail('CLOSED_TRANSACTION_REQUIRED')
        if any(row[key] is not True for key in ('rolled_back', 'source_unchanged', 'index_metadata_unchanged')):
            _fail('ROLLBACK_AND_UNCHANGED_STATE_REQUIRED')
        if row['cleanup_status'] != 'PASS':
            _fail('RECORDED_CLEANUP_REQUIRED')
    _exact(record['role_evidence'], ('status', 'reason'))
    if record['role_evidence'] != {
            'status': 'NOT_ESTABLISHED', 'reason': 'NO_ANN_ROLE_CAPTURE'}:
        _fail('ANN_ROLE_CLAIM_MUST_REMAIN_UNESTABLISHED')
    return {
        'schema': SCHEMA,
        'record_validation': 'COHERENT',
        'outcome': 'WARN',
        'profile': {'build': '17.0.5005.3', 'os': 'Linux', 'compatibility_level': 170,
                    'index_type': 'DiskANN', 'metric': 'COSINE', 'generation': 'UNKNOWN'},
        'counts': {'rejected_update_lifecycles': 2, 'role_records': 0},
        'claims': dict(EXPECTED['claims']),
        'limits': ['NO_GENERAL_DML_SUPPORT', 'NO_ROLE_QUALIFICATION', 'NO_FRESHNESS_PROOF',
                   'NO_GENERATION_CLAIM', 'RECORD_ORIGIN_NOT_INDEPENDENTLY_ATTESTED'],
    }
