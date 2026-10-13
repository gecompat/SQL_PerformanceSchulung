"""Reiner fester IDX-012-Recordvertrag; keine Clients, SQL- oder Runtimeimporte."""
from pathlib import Path
import copy
import base64
import hashlib
import json
import math
import re
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = HERE / 'Fixtures/idx012/IDX012_DML_ROLE.result-contract.json'
SCHEMA = 'IDX012_DML_ROLE_RECORD_V1'
OPERATIONS = ('UPDATE_ID_23', 'DELETE_ID_23', 'INSERT_ID_1000', 'MERGE_UPDATE_ID_23')
DURING = (999, 998, 1000, 999)
CHECKPOINTS = ('ROLE_START', 'ADMIN_BUILD', 'ROLE_RESTORED', 'ROLE_END')
ACTIONS = ('CREATE', 'REVOKE_CREATE', 'GRANT_CREATE', 'REVOKE_PERF', 'GRANT_PERF')
INPUT_PINS = {
    'DML_BOUNDARY': {'utf8_bytes': 28420, 'sha256': '9c9f9614f52d4d769c0b59e5caa95b15de327de59f94dcd3eb6952a734548bf6'},
    'REBUILD': {'utf8_bytes': 27610, 'sha256': '557a2b256ff88a8582d1d5ab24209f4e851896fe04aacb03c870ed12846c8217'},
}
CLAIMS = {
    'runtime_qualification': 'NOT_ESTABLISHED', 'tp_perf': 'NOT_ESTABLISHED',
    'minimum_roles': 'NOT_ESTABLISHED', 'non_sysadmin_build': 'NOT_ESTABLISHED',
    'public_multi_login_producer': 'NOT_ESTABLISHED', 'generation': 'UNKNOWN',
    'freshness': 'NOT_ESTABLISHED_BY_THIS_CONTRACT',
    'caller_provenance': 'DECLARED_NOT_INDEPENDENTLY_ATTESTED',
}
EXPECTED_CONTRACT = {
    'contract': SCHEMA, 'profile': {'build': '17.0.5005.3', 'engine': 3, 'os': 'Linux', 'cl': 170,
        'rows': 999, 'peak_rows': 1000, 'dimension': 3, 'base_type': 'float32',
        'metric': 'COSINE', 'generation': 'UNKNOWN', 'stale_option': 'ABSENT'},
    'expected_counts': {'positive_dml': 4, 'rejected_dml': 4, 'role_contexts': 8,
        'permission_negatives': 2, 'principal_audits': 5, 'source_rows_per_readback': 999},
    'claims': CLAIMS,
}
INDEX_TYPES = {
    'object_id': int, 'name': str, 'index_id': int, 'type': int, 'type_desc': str,
    'is_unique': bool, 'data_space_id': int, 'ignore_dup_key': bool, 'is_primary_key': bool,
    'is_unique_constraint': bool, 'fill_factor': int, 'is_padded': bool, 'is_disabled': bool,
    'is_hypothetical': bool, 'is_ignored_in_optimization': bool, 'allow_row_locks': bool,
    'allow_page_locks': bool, 'has_filter': bool, 'filter_definition': type(None),
    'auto_created': bool, 'vector_index_type': str, 'distance_metric': str, 'build_parameters': str,
}
DML_KEYS = set('kind Stage Operation Ordinal RunToken DatabaseId Context StaleOptionState Succeeded AffectedRows DuringRowCount ExpectedChange ErrorNumber ErrorState ErrorMessage SourceRestored RolledBack TransactionCount TransactionState RestoredRowCount IndexMetadataUnchanged'.split())
SNAPSHOT_KEYS = set('DatabaseId context build edition fixture_object vector_indexes baseline tables markers host scoped options files'.split())
OPTION_FIELDS = set('compatibility_level recovery_model collation_name is_read_only is_auto_close_on is_auto_shrink_on is_auto_create_stats_on is_auto_update_stats_on is_auto_update_stats_async_on is_ansi_null_default_on is_ansi_nulls_on is_ansi_padding_on is_ansi_warnings_on is_arithabort_on is_concat_null_yields_null_on is_quoted_identifier_on is_numeric_roundabort_on is_recursive_triggers_on is_cursor_close_on_commit_on is_local_cursor_default is_fulltext_enabled is_trustworthy_on is_db_chaining_on is_parameterization_forced is_read_committed_snapshot_on page_verify_option is_broker_enabled is_honor_broker_priority_on is_query_store_on containment target_recovery_time_in_seconds delayed_durability is_accelerated_database_recovery_on'.split())


def fail(code):
    raise ValueError(code)


def exact(value, keys):
    if type(value) is not dict or set(value) != set(keys): fail('EXACT_SCHEMA_REQUIRED')


def integer(value, expected=None, minimum=0):
    if type(value) is not int or value < minimum or expected is not None and value != expected:
        fail('EXACT_INTEGER_REQUIRED')
    return value


def plain(value, depth=0):
    if depth > 12: fail('BOUNDED_RECORD_DEPTH')
    if type(value) is dict:
        if any(type(k) is not str for k in value): fail('PLAIN_STRING_KEYS')
        for item in value.values(): plain(item, depth+1)
    elif type(value) is list:
        if len(value) > 2000: fail('BOUNDED_RECORD_LIST')
        for item in value: plain(item, depth+1)
    elif type(value) is float:
        if not math.isfinite(value): fail('FINITE_NUMBER_REQUIRED')
    elif type(value) is str:
        if len(value) > 160000: fail('BOUNDED_RECORD_STRING')
    elif type(value) not in (int, bool, type(None)): fail('PLAIN_BUILTIN_TYPES_REQUIRED')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def same(before, after):
    if canonical(before) != canonical(after): fail('COMPLETE_RECORD_CHANGED')


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result: fail('DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def loads(text):
    return json.loads(text, object_pairs_hook=unique, parse_constant=lambda _: fail('FINITE_JSON_REQUIRED'))


def source_binding():
    """Nur tatsächlich vorhandene Consumer-/Expectedbytes, keine Producerattestierung."""
    return {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__).resolve(), CONTRACT)}


def validate_contract(data):
    plain(data)
    if canonical(data) != canonical(EXPECTED_CONTRACT): fail('FIXED_CONTRACT_DRIFT')
    return data


def read_contract():
    raw = CONTRACT.read_bytes()
    if len(raw) > 10000: fail('BOUNDED_FIXED_CONTRACT')
    return validate_contract(loads(raw.decode('utf-8')))


def sid(value, size=None):
    if type(value) is not str or not re.fullmatch(r'0x(?:[0-9A-F]{2}){1,85}', value): fail('FULL_SID_REQUIRED')
    raw = bytes.fromhex(value[2:])
    if size is not None and len(raw) != size: fail('FULL_SID_SIZE')
    return raw


def identity(binding):
    exact(binding, ['token', 'database_id', 'fixture_object', 'operator_sid', 'admin_sid',
                    'original_preview', 'consumer_sources', 'provenance'])
    if type(binding['token']) is not str or not re.fullmatch('[A-F0-9]{16}', binding['token']): fail('FULL_TOKEN_REQUIRED')
    integer(binding['database_id'], minimum=5); integer(binding['fixture_object'], minimum=1)
    sid(binding['operator_sid'], 16); sid(binding['admin_sid'])
    if sid(binding['operator_sid']) == sid(binding['admin_sid']): fail('DISTINCT_ROLE_SIDS')
    if type(binding['original_preview']) is not int or binding['original_preview'] not in (0, 1): fail('ORIGINAL_PREVIEW_REQUIRED')
    if binding['consumer_sources'] != source_binding(): fail('ACTUAL_CONSUMER_EXPECTED_SOURCE_BINDING')
    if binding['provenance'] not in ('PUREFIXTURE_ONLY', 'DECLARED_PRIVATE_CAPTURE'): fail('EXPLICIT_PROVENANCE_REQUIRED')
    return 'SQLPERF_LAB_IDX012_' + binding['token'], 'SQLPERF_IDX012_ROLE_' + binding['token']


def dml(rows, b, database):
    if type(rows) is not list or len(rows) != 8: fail('EIGHT_DML_RECORDS_REQUIRED')
    for i, row in enumerate(rows):
        exact(row, DML_KEYS); integer(row['Ordinal'], i+1); integer(row['DatabaseId'], b['database_id'])
        stage = 'NO_INDEX' if i < 4 else 'WITH_INDEX'
        if row['kind'] != 'DML_BOUNDARY' or row['Stage'] != stage or row['Operation'] != OPERATIONS[i % 4] or row['RunToken'] != b['token'] or row['Context'] != database or row['StaleOptionState'] != 'ABSENT': fail('FIXED_DML_ORDER_IDENTITY')
        integer(row['TransactionCount'], 0); integer(row['TransactionState'], 0); integer(row['RestoredRowCount'], 999)
        if row['SourceRestored'] is not True or row['RolledBack'] is not True: fail('ACTUAL_ROLLBACK_RECORD_REQUIRED')
        if i < 4:
            integer(row['AffectedRows'], 1); integer(row['DuringRowCount'], DURING[i])
            if row['Succeeded'] is not True or row['ExpectedChange'] is not True or any(row[k] is not None for k in ('ErrorNumber', 'ErrorState', 'ErrorMessage', 'IndexMetadataUnchanged')): fail('POSITIVE_DML_REQUIRED')
        else:
            integer(row['ErrorNumber'], 42231); integer(row['ErrorState'], 1)
            if row['Succeeded'] is not False or row['IndexMetadataUnchanged'] is not True or any(row[k] is not None for k in ('AffectedRows', 'DuringRowCount', 'ExpectedChange')) or type(row['ErrorMessage']) is not str or not 1 <= len(row['ErrorMessage']) <= 4000: fail('FIXED_NATIVE_DML_REJECTION_REQUIRED')


def contexts(rows, b, operator):
    if type(rows) is not list or len(rows) != 8: fail('EIGHT_CONTEXT_RECORDS_REQUIRED')
    for i, row in enumerate(rows):
        exact(row, ['kind', 'Stage', 'Checkpoint', 'LoginName', 'Sid', 'OriginalLogin', 'Sysadmin', 'ControlServer'])
        admin = i % 4 == 1
        if row['kind'] != 'ROLE_CONTEXT' or row['Stage'] != ('DML_BOUNDARY' if i < 4 else 'REBUILD') or row['Checkpoint'] != CHECKPOINTS[i % 4] or row['OriginalLogin'] != 'sa' or row['LoginName'] != ('sa' if admin else operator): fail('BOUNDED_ROLE_CONTEXT_ORDER')
        integer(row['Sysadmin'], int(admin)); integer(row['ControlServer'], int(admin))
        if sid(row['Sid']) != sid(b['admin_sid'] if admin else b['operator_sid']): fail('FULL_CONTEXT_SID_BINDING')


def audits(rows, b, operator):
    if type(rows) is not list or len(rows) != 5: fail('FIVE_PRINCIPAL_AUDITS_REQUIRED')
    original_permissions = None
    for row, action in zip(rows, ACTIONS):
        exact(row, ['action', 'name', 'sid', 'roles', 'permissions']); integer(row['roles'], 0)
        if row['action'] != action or row['name'] != operator or sid(row['sid'], 16) != sid(b['operator_sid']): fail('FULL_OWN_PRINCIPAL_BINDING')
        permissions = row['permissions']
        if type(permissions) is not list or not 1 <= len(permissions) <= 3: fail('FULL_PERMISSION_POPULATION')
        seen = set()
        for permission in permissions:
            exact(permission, ['class', 'major_id', 'state', 'permission_name'])
            integer(permission['class'], 100); integer(permission['major_id'], 0)
            name = permission['permission_name']
            if type(name) is not str or name in seen or name not in ('CONNECT SQL', 'CREATE ANY DATABASE', 'VIEW SERVER PERFORMANCE STATE') or permission['state'] != 'G': fail('EXACT_PERMISSION_TUPLES')
            seen.add(name)
        expected = {'CREATE ANY DATABASE', 'VIEW SERVER PERFORMANCE STATE'}
        if action == 'REVOKE_CREATE': expected.remove('CREATE ANY DATABASE')
        if action == 'REVOKE_PERF': expected.remove('VIEW SERVER PERFORMANCE STATE')
        if seen - {'CONNECT SQL'} != expected: fail('ACTUAL_REVOKE_RESTORE_PERMISSION_RECORDS')
        if action == 'CREATE': original_permissions = seen
        else:
            target = original_permissions - ({'CREATE ANY DATABASE'} if action == 'REVOKE_CREATE' else {'VIEW SERVER PERFORMANCE STATE'} if action == 'REVOKE_PERF' else set())
            if seen != target: fail('FULL_PRINCIPAL_GRANTS_RESTORED')


def source(data, b):
    exact(data, ['DatabaseId', 'vectors', 'rows']); integer(data['DatabaseId'], b['database_id'])
    if type(data['vectors']) is not list or type(data['rows']) is not list or len(data['vectors']) != 999 or len(data['rows']) != 999: fail('FULL_999_SOURCE_RECORDS')
    f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
    for i, (vector, distance) in enumerate(zip(data['vectors'], data['rows']), 1):
        exact(vector, ['Id', 'JsonValue']); exact(distance, ['Id', 'DistanceValue'])
        integer(vector['Id'], i); integer(distance['Id'], i)
        if type(vector['JsonValue']) is not str: fail('FULL_SOURCE_JSON_REQUIRED')
        values = loads(vector['JsonValue']); expected = [1, f32(i/1000), f32(((i*17)%97)*1000000//97/1000000)]
        if type(values) is not list or len(values) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) or abs(v-e) > 1e-7 for v, e in zip(values, expected)): fail('FROZEN_FULL_FLOAT32_COORDINATES')
        actual = distance['DistanceValue']; reference = 1-values[0]/math.sqrt(sum(v*v for v in values))
        if type(actual) not in (int, float) or not math.isfinite(actual) or not 0 <= actual <= 2 or abs(actual-reference) > 1e-6: fail('INDEPENDENT_FULL_SOURCE_COSINE')


def snapshot(data, b, database, index_count):
    exact(data, SNAPSHOT_KEYS)
    for key, expected in [('DatabaseId', b['database_id']), ('fixture_object', b['fixture_object']), ('edition', 3), ('vector_indexes', index_count)]: integer(data[key], expected)
    if data['context'] != database or data['build'] != '17.0.5005.3': fail('OWN_BUILD_SNAPSHOT_REQUIRED')
    for key in ('baseline', 'tables', 'markers', 'host', 'scoped', 'options', 'files'):
        if type(data[key]) is not list: fail('FULL_SNAPSHOT_ARRAYS')
    same(data['baseline'], [{'Id': 1, 'OriginalValue': b['original_preview'], 'RunToken': b['token'], 'MaxDopOriginal': 0}])
    markers = {'SQLPERF.Project': 'SQL_PerformanceSchulung', 'SQLPERF.ContractVersion': '1.0', 'SQLPERF.DemoId': 'IDX-012', 'SQLPERF.RunToken': b['token']}
    if len(data['markers']) != 4: fail('FOUR_FULL_MARKERS_REQUIRED')
    seen = set()
    for row in data['markers']:
        exact(row, ['name', 'ValueBytes', 'ByteLength']); name = row['name']
        if type(name) is not str or name not in markers or name in seen: fail('FULL_MARKER_NAMES')
        seen.add(name); raw = markers[name].encode('utf-16-le'); integer(row['ByteLength'], len(raw))
        if type(row['ValueBytes']) is not str or row['ValueBytes'] != base64.b64encode(raw).decode('ascii'): fail('FULL_MARKER_VALUE_BYTES')
    if len(data['scoped']) != 41 or len(data['files']) != 2 or len(data['options']) != 1 or not data['host']: fail('FULL_SNAPSHOT_CATALOG_POPULATION')
    for rows, fields in [(data['scoped'], {'configuration_id', 'name', 'value', 'value_for_secondary', 'is_value_default'}), (data['host'], {'configuration_id', 'name', 'value', 'value_in_use', 'minimum', 'maximum', 'description', 'is_dynamic', 'is_advanced'})]:
        ids = set()
        for row in rows:
            exact(row, fields); integer(row['configuration_id'], minimum=1)
            if row['configuration_id'] in ids or type(row['name']) is not str: fail('UNIQUE_FULL_CONFIG_IDENTITIES')
            ids.add(row['configuration_id'])
            for key in fields - {'configuration_id', 'name', 'description', 'is_value_default', 'is_dynamic', 'is_advanced'}:
                if row[key] is not None and type(row[key]) is not int: fail('CAPTURED_CONFIG_INTEGER_OR_NULL')
            for key in fields & {'is_value_default', 'is_dynamic', 'is_advanced'}:
                if type(row[key]) is not bool: fail('CAPTURED_CONFIG_BOOL')
            if 'description' in fields and row['description'] is not None and type(row['description']) is not str: fail('CAPTURED_CONFIG_DESCRIPTION')
    for name in ('PREVIEW_FEATURES', 'MAXDOP'):
        matches = [r for r in data['scoped'] if r['name'] == name]
        if len(matches) != 1: fail('EXACT_OWN_OPTIONS')
        integer(matches[0]['value'], 1)
    options = data['options'][0]; exact(options, OPTION_FIELDS); integer(options['compatibility_level'], 170); integer(options['recovery_model'], 3)
    for key in OPTION_FIELDS:
        if key == 'collation_name':
            if type(options[key]) is not str or not options[key]: fail('FULL_COLLATION_REQUIRED')
        elif key.startswith('is_'):
            if type(options[key]) is not bool: fail('FULL_OPTION_BOOL')
        else: integer(options[key])
    for row, file_id in zip(data['files'], (1, 2)):
        exact(row, ['file_id', 'type', 'NameBytes', 'max_size', 'growth', 'is_percent_growth']); integer(row['file_id'], file_id); integer(row['type'], file_id-1); integer(row['max_size'], 32768 if file_id == 1 else 8192); integer(row['growth'], 2048)
        if row['is_percent_growth'] is not False or type(row['NameBytes']) is not str or row['NameBytes'] != base64.b64encode((database + ('_log' if file_id == 2 else '')).encode('utf-16-le')).decode('ascii'): fail('FULL_OWN_FILE_CAPTURE')
    expected_tables = {('dbo', 'PreviewState'), ('lab', 'VectorFixture'), ('lab', 'FrozenSource'), ('lab', 'ExactOracle')}
    if len(data['tables']) != 4: fail('FULL_TABLE_POPULATION')
    actual_tables = set(); object_ids = set()
    for row in data['tables']:
        exact(row, ['SchemaName', 'TableName', 'object_id']); integer(row['object_id'], minimum=1)
        if row['object_id'] in object_ids or type(row['SchemaName']) is not str or type(row['TableName']) is not str: fail('UNIQUE_FULL_OWN_TABLE_IDENTITIES')
        object_ids.add(row['object_id'])
        actual_tables.add((row['SchemaName'], row['TableName']))
        if row['TableName'] == 'VectorFixture': integer(row['object_id'], b['fixture_object'])
    if actual_tables != expected_tables: fail('EXACT_OWN_TABLES')


def metadata(data, b):
    exact(data, ['before', 'after'])
    for rows in data.values():
        if type(rows) is not list or len(rows) != 1: fail('SINGLE_FULL_VECTOR_INDEX')
        row = rows[0]; exact(row, INDEX_TYPES)
        if any(type(row[k]) is not expected for k, expected in INDEX_TYPES.items()): fail('FULL_INDEX_FIELD_TYPES')
        integer(row['object_id'], b['fixture_object']); integer(row['index_id'], minimum=1); integer(row['type'], 8)
        if row['name'] != 'IDX012_OwnVector' or row['type_desc'] != 'VECTOR' or row['is_disabled'] is not False or row['is_hypothetical'] is not False or row['vector_index_type'] != 'DiskANN' or row['distance_metric'] != 'COSINE': fail('FIXED_OWN_LEGACY_INDEX')
        parameters = loads(row['build_parameters'])
        if type(parameters) is not dict or any(k.casefold() == 'version' for k in parameters): fail('GENERATION_MUST_REMAIN_UNKNOWN')
    same(data['before'], data['after'])


def report(record, binding):
    """Validiert feste InMemory-Records; fehlende individuelle Captures bleiben offen."""
    if type(record) is not dict or type(binding) is not dict: fail('PLAIN_RECORD_BINDING_REQUIRED')
    plain(record); plain(binding)
    if len(canonical(record).encode('utf-8')) > 3000000: fail('BOUNDED_FULL_RECORD')
    database, operator = identity(binding); contract = read_contract()
    exact(record, ['contract', 'profile', 'source_inputs', 'dml', 'contexts', 'audits', 'permission_negatives', 'source_before', 'source_after', 'snapshots', 'index_metadata', 'owner_frame', 'cleanup', 'capture'])
    if record['contract'] != SCHEMA: fail('FIXED_RECORD_VERSION')
    same(record['profile'], contract['profile']); same(record['source_inputs'], INPUT_PINS)
    dml(record['dml'], binding, database); contexts(record['contexts'], binding, operator); audits(record['audits'], binding, operator)
    negatives = record['permission_negatives']
    if type(negatives) is not list or len(negatives) != 2: fail('TWO_PERMISSION_NEGATIVES_REQUIRED')
    for item, action, detail in zip(negatives, ('REVOKE_CREATE', 'REVOKE_PERF'), ('MISSING_CREATE_DATABASE', 'MISSING_SERVER_PERFORMANCE_STATE')):
        exact(item, ['withdrawn', 'outcome', 'code', 'phases', 'original_preview', 'cleanup_ok', 'detail', 'database_absence_frame'])
        if item['withdrawn'] != action or item['outcome'] != 'SKIP' or item['code'] != 'SKIP_PERMISSION' or item['phases'] != [['PREFLIGHT', 'SKIP', 'SKIP_PERMISSION']] or item['original_preview'] is not None or item['cleanup_ok'] is not False or item['detail'] != detail or item['database_absence_frame'] != 'ANN_DB|ABSENT': fail('EXACT_PRESETUP_PERMISSION_SKIP')
    source(record['source_before'], binding); source(record['source_after'], binding); same(record['source_before'], record['source_after'])
    exact(record['snapshots'], ['before', 'after'])
    snapshot(record['snapshots']['before'], binding, database, 0); snapshot(record['snapshots']['after'], binding, database, 1)
    expected = copy.deepcopy(record['snapshots']['before']); expected['vector_indexes'] = 1; same(expected, record['snapshots']['after'])
    metadata(record['index_metadata'], binding)
    if record['owner_frame'] != 'IDX012_ROLE|OWN_DATABASE_OWNER': fail('SOURCE_BOUND_OWNER_FRAME_REQUIRED')
    cleanup = record['cleanup']
    exact(cleanup, ['restore_frame', 'attest_frame', 'drop_frame', 'database_absence_frame', 'role_drop_frame', 'role_absence_frame', 'cid_query_stdout', 'name_query_stdout', 'active_inputs'])
    required = {'restore_frame': f"ANN_RESTORE|{binding['token']}|{binding['original_preview']}|0", 'attest_frame': f"ANN_ATTEST|{binding['token']}|{binding['original_preview']}|0", 'drop_frame': 'ANN_RECOVERY|DROP_CONFIRMED', 'database_absence_frame': 'ANN_DB|ABSENT', 'role_drop_frame': 'IDX012_ROLE|ABSENT', 'role_absence_frame': 'IDX012_ROLE|ABSENT'}
    for key, text in required.items():
        if type(cleanup[key]) is not str or cleanup[key] != text: fail('ACTUAL_SQL_PRINCIPAL_CLOSURE_TEXT_REQUIRED')
    for key in ('cid_query_stdout', 'name_query_stdout'):
        if cleanup[key] is not None and (type(cleanup[key]) is not str or cleanup[key] != ''): fail('NAMESPACE_ABSENCE_NOT_ESTABLISHED')
    if cleanup['active_inputs'] is not None and (type(cleanup['active_inputs']) is not list or cleanup['active_inputs'] != []): fail('OWN_INPUT_ABSENCE_NOT_ESTABLISHED')
    exact(record['capture'], ['individual_client_end_input', 'server_request_end', 'dml_severity_line_procedure'])
    if any(v is not None for v in record['capture'].values()): fail('V1_MISSING_CAPTURES_MUST_NOT_BE_FABRICATED')
    return {'outcome': 'WARN', 'record_validation': 'COHERENT', 'profile': 'SQL17_0_5005_3_LEGACY_ONLY',
        'counts': dict(contract['expected_counts']), 'claims': dict(CLAIMS),
        'dml_guard_provenance': 'DECLARED_NOT_INDEPENDENTLY_ATTESTED',
        'individual_end_input_capture': 'NOT_ESTABLISHED', 'server_request_end': 'NOT_ESTABLISHED',
        'dml_full_error_capture': 'NOT_ESTABLISHED',
        'namespace_capture': 'NOT_ESTABLISHED' if any(cleanup[k] is None for k in ('cid_query_stdout', 'name_query_stdout', 'active_inputs')) else 'TEXTS_COHERENT_NOT_INDEPENDENTLY_ATTESTED',
        'fixture_provenance': binding['provenance']}
