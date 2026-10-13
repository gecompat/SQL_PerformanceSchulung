"""Reiner V2-Recordcheck der öffentlichen IDX-012-API; keine Ausführung."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import os
import re
import idx012_dml_role_evidence as v1

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'Demos/09_AI_SQL_Server_2025/IDX-012_Vector_Index_DML_Maintenance'
CONTRACT = Path(__file__).parent / 'Fixtures/idx012/IDX012_PUBLIC_ROLE.result-contract-v2.json'
SCHEMA = 'IDX012_PUBLIC_ROLE_RECORD_V2'
SOURCE_NAMES = (
    'run_profile.py', 'role_profile.py', 'cleanup_budget.py', 'cost_evidence.py',
    'dml_boundary_evidence.py', 'storage_evidence.py', 'lifecycle_evidence.py',
    '00_Preflight.sql', '10_Setup.sql', '11_EnablePreview.sql', '12_EnableMaxdop.sql',
    '20_Baseline.sql', '21_Snapshot.sql', '22_Storage.sql', '23_CostFrame.sql',
    '30_CostBoundary.sql', '30_DmlBoundary.sql', '40_SourceAfter.sql',
    '50_CostRebuild.sql', '50_DropRebuild.sql', '90_Restore.sql',
    '91_AttestDrop.sql', '92_Absence.sql')
PHASES = ('PREFLIGHT', 'SETUP', 'SNAPSHOT', 'ENABLE_PREVIEW', 'SNAPSHOT',
    'ENABLE_MAXDOP', 'SNAPSHOT', 'BASELINE', 'SNAPSHOT', 'STORAGE_BASELINE',
    'DML_BOUNDARY', 'SNAPSHOT', 'STORAGE_INDEXED', 'SOURCE_AFTER', 'SNAPSHOT',
    'DROP_CHANGE_REBUILD', 'SNAPSHOT', 'SOURCE_REBUILT', 'SNAPSHOT',
    'STORAGE_REBUILT', 'RESTORE', 'ATTEST_DROP', 'ABSENCE')
SCRIPTS = ('00_Preflight.sql', '10_Setup.sql', '21_Snapshot.sql', '11_EnablePreview.sql',
    '21_Snapshot.sql', '12_EnableMaxdop.sql', '21_Snapshot.sql', '20_Baseline.sql',
    '21_Snapshot.sql', '22_Storage.sql', '30_CostBoundary.sql', '21_Snapshot.sql',
    '22_Storage.sql', '40_SourceAfter.sql', '21_Snapshot.sql', '50_CostRebuild.sql',
    '21_Snapshot.sql', '40_SourceAfter.sql', '21_Snapshot.sql', '22_Storage.sql',
    '90_Restore.sql', '91_AttestDrop.sql', '92_Absence.sql')
CAPTURE_KEYS = 'Auth Budget ChannelStatus CollectorCode CollectorDurationSeconds CollectorFailed CollectorMode ElapsedSeconds FinalPoll InputSha256 InputText Phase Pid ProcessReturnCode ProcessStartAttempted ProcessStarted RejectCode ReturnCode ServerRequestEnd SourceAfter SourceBefore Stderr Stdout TimedOut UnknownSticky'.split()
COMMON_EVIDENCE = 'generation role_captures role_collector_mode role_cost_scope role_inputs role_profile role_reap_reserve_seconds role_runtime_qualification role_server_request_end runtime_qualification shared_cleanup_window'.split()
POSITIVE_EVIDENCE = COMMON_EVIDENCE + 'database_id dml_boundary independent_source_comparison index lifecycle phase_costs rebuild_source_comparison role_contexts storage'.split()
CLAIMS = {name: 'NOT_ESTABLISHED' for name in (
    'owner_query', 'server_request_end', 'dml_full_error_capture', 'runtime_qualification',
    'tp_perf', 'principal_cleanup', 'namespace_cleanup')}
CLAIMS.update(generation='UNKNOWN', caller_provenance='DECLARED_NOT_INDEPENDENTLY_ATTESTED',
    credential_list_completeness='DECLARED_NOT_INDEPENDENTLY_ATTESTED',
    sql_cleanup='TEXTS_COHERENT_NOT_INDEPENDENTLY_ATTESTED')
EXPECTED = {'contract': SCHEMA, 'execution_source_count': 24,
    'counts': {'profiles': 3, 'client_captures': 25, 'role_contexts': 8,
               'cost_pairs': 2, 'permission_negatives': 2, 'positive_dml': 4, 'rejected_dml': 4},
    'claims': CLAIMS, 'record_max_utf8_bytes': 4194304}


def fail(code):
    raise ValueError(code)


def exact(value, keys):
    if type(value) is not dict or set(value) != set(keys): fail('V2_SCHEMA')


def same(value, expected):
    if v1.canonical(value) != v1.canonical(expected): fail('V2_RECORD_BINDING')


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0: fail('V2_FINITE_DURATION')


def raw_bytes(path):
    actual = Path('\\\\?\\' + str(path.resolve())) if os.name == 'nt' else path
    return actual.read_bytes()


def execution_sources():
    """Feste aktuelle Rohbytes; kein frei wählbarer Quellpfad."""
    paths = [FOLDER / name for name in SOURCE_NAMES]
    paths.append(ROOT / 'Demos/00_Framework/Tools/sqlcmd_process.py')
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(raw_bytes(p)).hexdigest() for p in paths}


def source_binding():
    paths = (Path(__file__).resolve(), CONTRACT, Path(v1.__file__).resolve())
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(raw_bytes(p)).hexdigest() for p in paths}


def privacy(value, secrets):
    if type(secrets) is not list or len(secrets) > 4 or any(type(s) is not str or not 8 <= len(s) <= 128 for s in secrets) or len(set(secrets)) != len(secrets): fail('V2_PRIVATE_SECRET_LIST')
    hex_forms = [re.compile(re.escape(f), re.IGNORECASE) for s in secrets
                 for f in (s.encode().hex(), s.encode('utf-16-le').hex())]
    def walk(item, received=False):
        if type(item) is str:
            decoded = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m[1], 16)), item)
            for text in (item, decoded):
                # Plaintext bleibt case-sensitiv; ausschließlich Hexdarstellungen
                # verwenden dieselbe Bytefolge unabhängig von der Buchstabenschreibung.
                if any(s in text for s in secrets) or any(f.search(text) for f in hex_forms): fail('V2_CREDENTIAL_OUTPUT')
                if received and any(re.fullmatch(r'[A-Z0-9_]+_PART\|[0-9]+\|[0-9A-Fa-f]+', line.strip()) for line in text.splitlines()): fail('V2_UNSUPPORTED_RECEIVED_FRAME')
        elif type(item) is dict:
            for k, v in item.items(): walk(k, received); walk(v, received)
        elif type(item) is list:
            for v in item: walk(v, received)
    walk(value)
    # Der öffentliche Transport liefert vollständige JSON-Zeilen, keine Hexframes.
    for profile in value['profiles']:
        for capture in profile['evidence']['role_captures']:
            for key in ('Stdout', 'Stderr'):
                text = capture[key]
                if type(text) is not str: fail('V2_CHANNEL_TYPE')
                walk(text, received=True)
                for line in text.splitlines():
                    if line.lstrip().startswith('{'): walk(v1.loads(line.strip()), received=True)


def records(capture):
    result = []
    for text in (capture['Stdout'], capture['Stderr']):
        for line in text.splitlines():
            if line.lstrip().startswith('{'):
                row = v1.loads(line.strip())
                if type(row) is not dict: fail('V2_CHANNEL_JSON_OBJECT')
                channel_schema(row)
                result.append(row)
    return result


def channel_schema(row):
    schemas = {
        'ROLE_CONTEXT': 'kind Stage Checkpoint LoginName Sid OriginalLogin OriginalSid Sysadmin ControlServer AlterAnyLogin SessionId DatabaseId RunToken',
        'PHASE_COST': 'kind Stage Frame DatabaseId Context RunToken SessionId SourceRows VectorIndexes TransactionCount TransactionState SessionCount TempdbCount FileCount session tempdb files',
        'COST_GUARD': 'kind Stage Frame DatabaseId RunToken SessionId SourceRows VectorIndexes TransactionCount TransactionState SessionCount TempdbCount FileCount',
        'INDEX': 'kind DatabaseId RunToken BuildElapsedUs metadata',
        'INDEX_AFTER': 'kind DatabaseId RunToken metadata',
        'SOURCE_DISTANCES': 'kind DatabaseId rows', 'SOURCE_VECTOR_BLOCK': 'kind DatabaseId BlockId vectors',
        'STORAGE': 'kind Stage DatabaseId Context RunToken FixtureObject SourceRows VectorIndexes TransactionCount TransactionState FileCount InternalCount PartitionCount files internal_tables partitions',
        'STORAGE_GUARD': 'kind Stage DatabaseId Context RunToken SourceRows VectorIndexes TransactionCount TransactionState FileCount InternalCount PartitionCount',
        'LIFECYCLE_DROP': 'kind DatabaseId RunToken IndexCount RowCount TransactionCount TransactionState',
        'LIFECYCLE_CHANGE': 'kind DatabaseId RunToken AffectedRows RowCount TransactionCount TransactionState Committed OtherSourceUnchanged NewVector IndexCount',
        'LIFECYCLE_REBUILD': 'kind DatabaseId RunToken BuildElapsedUs BeforeMetadata AfterMetadata',
        'LIFECYCLE_QUERY': 'kind DatabaseId RunToken Ordinal Stage Path rows'}
    kind = row.get('kind')
    if kind is None: exact(row, v1.SNAPSHOT_KEYS)
    elif kind == 'DML_BOUNDARY': exact(row, v1.DML_KEYS)
    elif kind in schemas: exact(row, schemas[kind].split())
    else: fail('V2_CHANNEL_RECORD_KIND')
    fields = {}
    if kind == 'PHASE_COST':
        fields = {'session': 'session_id cpu_time reads writes logical_reads', 'tempdb': 'session_id database_id user_objects_alloc_page_count user_objects_dealloc_page_count internal_objects_alloc_page_count internal_objects_dealloc_page_count', 'files': 'database_id file_id sample_ms num_of_writes num_of_bytes_written io_stall_write_ms'}
    if kind == 'STORAGE':
        fields = {'files': 'file_id type size space_used_pages', 'internal_tables': 'object_id parent_id parent_minor_id internal_type internal_type_desc', 'partitions': 'partition_id object_id index_id partition_number row_count used_page_count reserved_page_count in_row_used_page_count lob_used_page_count row_overflow_used_page_count'}
    for key, keys in fields.items():
        if type(row[key]) is not list: fail('V2_CHANNEL_ARRAY')
        for item in row[key]: exact(item, keys.split())


def selected(capture, kind, count):
    rows = [r for r in records(capture) if r.get('kind') == kind]
    if len(rows) != count: fail('V2_FULL_CHANNEL_POPULATION')
    return rows


def pure_helper(name):
    """Ausschließlich bestehende reine öffentliche Evidenzfunktionen, keine Clients."""
    if type(name) is not str or name not in ('cost', 'dml_boundary', 'lifecycle', 'storage'): fail('V2_FIXED_PURE_HELPER_NAME')
    official = Path(__file__).resolve().parents[2] / 'Demos/09_AI_SQL_Server_2025/IDX-012_Vector_Index_DML_Maintenance'
    path = FOLDER / (name + '_evidence.py')
    if FOLDER != official or FOLDER.is_symlink() or path.is_symlink() or path.resolve().parent != official: fail('V2_FIXED_PURE_HELPER_PATH')
    actual = Path('\\\\?\\' + str(path.resolve())) if os.name == 'nt' else path
    spec = importlib.util.spec_from_file_location('_idx012_v2_' + name, actual)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capture_check(capture, script, sources):
    exact(capture, CAPTURE_KEYS)
    if capture['Phase'] != script: fail('V2_CLIENT_ORDER')
    auth = 'ADMIN_ORIGINAL_OPERATOR_CONTEXT' if script in ('30_CostBoundary.sql', '50_CostRebuild.sql') else 'OPERATOR_AUTH'
    if capture['Auth'] != auth: fail('V2_AUTH_MODE')
    for key in ('FinalPoll', 'ProcessReturnCode', 'ReturnCode'): v1.integer(capture[key], 0)
    v1.integer(capture['Pid'], minimum=1)
    for key in ('TimedOut', 'CollectorFailed', 'UnknownSticky'):
        if capture[key] is not False: fail('V2_CLIENT_END_NOT_ESTABLISHED')
    for key in ('ProcessStartAttempted', 'ProcessStarted'):
        if capture[key] is not True: fail('V2_CLIENT_END_NOT_ESTABLISHED')
    for key in ('CollectorCode', 'RejectCode'):
        if capture[key] is not None: fail('V2_CLIENT_END_NOT_ESTABLISHED')
    if capture['ChannelStatus'] != 'SAFE' or capture['ServerRequestEnd'] != 'NOT_ATTESTED' or capture['CollectorMode'] != 'FIXED_ABSOLUTE_CALL_DEADLINE': fail('V2_CAPTURE_BOUNDARY')
    same(capture['SourceBefore'], sources); same(capture['SourceAfter'], sources)
    for key in ('CollectorDurationSeconds', 'ElapsedSeconds'): number(capture[key])
    budget = capture['Budget']
    exact(budget, 'AbsoluteDeadline ChannelsObserved CollectorCode CollectorFailed ObservedOverrun PreReapPoll PrimaryWaitSeconds ReapReserveSeconds'.split())
    for key in ('AbsoluteDeadline', 'PrimaryWaitSeconds'): number(budget[key])
    v1.integer(budget['PreReapPoll'], 0); v1.integer(budget['ReapReserveSeconds'], 2)
    if budget['ChannelsObserved'] is not True or budget['CollectorFailed'] is not False or budget['ObservedOverrun'] is not False or budget['CollectorCode'] is not None: fail('V2_CAPTURE_DEADLINE')
    text = capture['InputText']
    if type(text) is not str or not 1 <= len(text.encode('utf-8')) <= 160000: fail('V2_CONFIGURED_INPUT')
    if capture['InputSha256'] != hashlib.sha256(text.encode('utf-8')).hexdigest(): fail('V2_INPUT_SHA')
    if sum(len(capture[k].encode('utf-8')) for k in ('Stdout', 'Stderr')) > 1000000: fail('V2_CHANNEL_CAP')
    records(capture)


def context_check(rows, b, stage, frames):
    if type(rows) is not list or len(rows) != 4: fail('V2_CONTEXT_POPULATION')
    session = None
    for row, checkpoint in zip(rows, v1.CHECKPOINTS):
        exact(row, 'kind Stage Checkpoint LoginName Sid OriginalLogin OriginalSid Sysadmin ControlServer AlterAnyLogin SessionId DatabaseId RunToken'.split())
        admin = checkpoint == 'ADMIN_BUILD'
        expected = {'kind': 'ROLE_CONTEXT', 'Stage': stage, 'Checkpoint': checkpoint,
            'LoginName': 'sa' if admin else 'SQLPERF_IDX012_ROLE_' + b['token'],
            'Sid': b['admin_sid'] if admin else b['operator_sid'],
            'OriginalLogin': 'sa', 'OriginalSid': b['admin_sid'], 'RunToken': b['token']}
        for key, value in expected.items():
            if type(row[key]) is not str or row[key] != value: fail('V2_ROLE_IDENTITY')
        for key in ('Sysadmin', 'ControlServer', 'AlterAnyLogin'): v1.integer(row[key], int(admin))
        v1.integer(row['DatabaseId'], b['database_id']); v1.integer(row['SessionId'], minimum=1)
        if row['SessionId'] > 32767: fail('V2_SESSION')
        session = row['SessionId'] if session is None else session
        if row['SessionId'] != session: fail('V2_SAME_COST_SESSION')
    for frame in frames:
        v1.integer(frame['SessionId'], session)


def source_rows(capture, b, changed=False):
    row = selected(capture, 'SOURCE_DISTANCES', 1)[0]
    blocks = selected(capture, 'SOURCE_VECTOR_BLOCK', 10)
    vectors = []
    for i, block in enumerate(blocks, 1):
        exact(block, ['kind', 'BlockId', 'DatabaseId', 'vectors'])
        v1.integer(block['BlockId'], i); v1.integer(block['DatabaseId'], b['database_id'])
        if type(block['vectors']) is not list or len(block['vectors']) != (99 if i == 10 else 100): fail('V2_SOURCE_BLOCKS')
        vectors.extend(block['vectors'])
    exact(row, ['kind', 'DatabaseId', 'rows'])
    data = {'DatabaseId': row['DatabaseId'], 'vectors': vectors, 'rows': row['rows']}
    if not changed: v1.source(data, b)
    else:
        # Unveränderte übrige998 und genau die feste Änderung, keine neue Formel.
        import copy
        original = copy.deepcopy(data)
        expected = [1, 999 / 1000, ((999 * 17) % 97) * 1000000 // 97 / 1000000]
        if vectors[-1]['Id'] != 999 or v1.loads(vectors[-1]['JsonValue']) != [1, 0, 0] or row['rows'][-1] != {'Id': 999, 'DistanceValue': 0}: fail('V2_REBUILD_SOURCE')
        original['vectors'][-1]['JsonValue'] = json.dumps(expected)
        original['rows'][-1]['DistanceValue'] = 1 - 1 / math.sqrt(sum(v * v for v in expected))
        v1.source(original, b)
    return {r['Id']: r['DistanceValue'] for r in row['rows']}, {r['Id']: r['JsonValue'] for r in vectors}


def report(record, binding, *, secrets):
    """Prüft Recordkohärenz; Secretliste und Producerherkunft bleiben erklärt."""
    if type(record) is not dict or type(binding) is not dict: fail('V2_PLAIN_RECORD')
    v1.plain(record); v1.plain(binding)
    exact(record, ['contract', 'profiles']); exact(binding, ['token', 'database_id', 'fixture_object', 'operator_sid', 'admin_sid', 'original_preview', 'execution_sources', 'consumer_sources', 'provenance'])
    if type(record['profiles']) is not list or len(record['profiles']) != 3: fail('V2_THREE_PUBLIC_RESULTS')
    for profile in record['profiles']:
        exact(profile, ['outcome', 'code', 'phases', 'original_preview', 'cleanup_ok', 'evidence'])
        if type(profile['evidence']) is not dict or type(profile['evidence'].get('role_captures')) is not list: fail('V2_CAPTURE_POPULATION')
        for cap in profile['evidence']['role_captures']: exact(cap, CAPTURE_KEYS)
    if record['contract'] != SCHEMA or binding['provenance'] not in ('PUREFIXTURE_ONLY', 'DECLARED_PRIVATE_CAPTURE'): fail('V2_DECLARED_VERSION')
    if type(binding['token']) is not str or not re.fullmatch('[A-F0-9]{16}', binding['token']): fail('V2_TOKEN')
    v1.integer(binding['database_id'], minimum=5); v1.integer(binding['fixture_object'], minimum=1)
    v1.sid(binding['operator_sid'], 16); v1.sid(binding['admin_sid'])
    if binding['operator_sid'] == binding['admin_sid']: fail('V2_DISTINCT_SIDS')
    if type(binding['original_preview']) is not int or binding['original_preview'] not in (0, 1): fail('V2_ORIGINAL_PREVIEW')
    privacy(record, secrets)  # Vor SHA-Berechnung; kein Secret oder Secret-Digest im Ergebnis.
    if len(v1.canonical(record).encode('utf-8')) > EXPECTED['record_max_utf8_bytes']: fail('V2_RECORD_CAP')
    sources = execution_sources(); same(binding['execution_sources'], sources); same(binding['consumer_sources'], source_binding())
    raw = raw_bytes(CONTRACT)
    if len(raw) > 10000: fail('V2_CONTRACT_CAP')
    same(v1.loads(raw.decode('utf-8')), EXPECTED)
    profiles = record['profiles']
    if type(profiles) is not list or len(profiles) != 3: fail('V2_THREE_PUBLIC_RESULTS')
    for ordinal, profile in enumerate(profiles):
        exact(profile, ['outcome', 'code', 'phases', 'original_preview', 'cleanup_ok', 'evidence'])
        evidence = profile['evidence']; exact(evidence, POSITIVE_EVIDENCE if ordinal == 2 else COMMON_EVIDENCE)
        for key, value in {'generation': 'UNKNOWN', 'runtime_qualification': 'NOT_ESTABLISHED', 'role_runtime_qualification': 'NOT_ESTABLISHED', 'role_server_request_end': 'NOT_ATTESTED', 'role_profile': 'operator-admin-build', 'role_cost_scope': 'WHOLE_PHASE_INCLUDING_CONTEXT_AND_ATTESTATION', 'role_collector_mode': 'FIXED_ABSOLUTE_CALL_DEADLINE'}.items():
            if evidence[key] != value: fail('V2_FIXED_CLAIMS')
        v1.integer(evidence['role_reap_reserve_seconds'], 2)
        scripts = SCRIPTS if ordinal == 2 else ('00_Preflight.sql',)
        captures = evidence['role_captures']; inputs = evidence['role_inputs']
        if type(captures) is not list or type(inputs) is not list or len(captures) != len(scripts) or len(inputs) != len(scripts): fail('V2_CAPTURE_POPULATION')
        for cap, own, script in zip(captures, inputs, scripts):
            capture_check(cap, script, sources)
            exact(own, ['Path', 'InputSha256', 'Retained'])
            if type(own['Path']) is not str or not own['Path'] or own['Retained'] is not False or own['InputSha256'] != cap['InputSha256']: fail('V2_CONFIGURED_INPUT_CLOSURE')
        if len({cap['Pid'] for cap in captures}) != len(captures): fail('V2_DUPLICATE_CLIENT')
        if ordinal < 2:
            if profile['outcome'] != 'SKIP' or profile['code'] != 'SKIP_PERMISSION' or profile['original_preview'] is not None or profile['cleanup_ok'] is not False: fail('V2_RIGHTS_NEGATIVE')
            same(profile['phases'], [['PREFLIGHT', 'SKIP', 'SKIP_PERMISSION']])
            window = evidence['shared_cleanup_window']
            exact(window, ['DeadlineMonotonic', 'Seconds', 'StartedMonotonic', 'Status'])
            v1.integer(window['Seconds'], 60)
            if window['Status'] != 'NOT_STARTED' or window['DeadlineMonotonic'] is not None or window['StartedMonotonic'] is not None: fail('V2_NEGATIVE_WINDOW')
            detail = ('MISSING_CREATE_DATABASE', 'MISSING_SERVER_PERFORMANCE_STATE')[ordinal]
            matching = [line.strip() for key in ('Stdout', 'Stderr') for line in captures[0][key].splitlines() if line.strip().startswith('IDX012_DETAIL|')]
            if matching != ['IDX012_DETAIL|' + detail]: fail('V2_DISTINCT_RIGHTS_DETAILS')
        else:
            positive(profile, binding)
    return {'outcome': 'WARN', 'record_validation': 'COHERENT_PUBLIC_V2',
            'counts': dict(EXPECTED['counts']), 'claims': dict(CLAIMS),
            'credential_check': 'NOT_CHECKED_FOR_UNAVAILABLE_SECRETS' if not secrets else 'CHECKED_AGAINST_DECLARED_SECRET_LIST'}


def positive(profile, b):
    if profile['outcome'] != 'WARN' or profile['code'] != 'WARN_OPTIONAL_EVIDENCE_SKIPPED' or profile['cleanup_ok'] is not True or type(profile['original_preview']) is not int or profile['original_preview'] != b['original_preview']: fail('V2_POSITIVE_WARN_REQUIRED')
    same(profile['phases'], [[phase, 'WARN' if i == 0 else 'PASS', 'WARN_OPTIONAL_EVIDENCE_SKIPPED' if i == 0 else 'OK'] for i, phase in enumerate(PHASES)])
    e = profile['evidence']; c = e['role_captures']; v1.integer(e['database_id'], b['database_id'])
    states = []
    for pos in (2, 4, 6, 8, 11, 14, 16, 18):
        rows = records(c[pos])
        if len(rows) != 1 or 'kind' in rows[0]: fail('V2_FULL_SNAPSHOT_POPULATION')
        states.append(rows[0])
    for row, indexes in zip(states[3:], (0, 1, 1, 1, 1)):
        v1.snapshot(row, b, 'SQLPERF_LAB_IDX012_' + b['token'], indexes)
    baseline = states[3]
    for row, preview, maxdop in zip(states[:3], (0, 1, 1), (0, 0, 1)):
        for key in v1.SNAPSHOT_KEYS - {'fixture_object', 'tables', 'vector_indexes', 'scoped'}: same(row[key], baseline[key])
        if row['fixture_object'] is not None: fail('V2_PREBASELINE_OBJECT')
        v1.integer(row['vector_indexes'], 0)
        same(row['tables'], [r for r in baseline['tables'] if r['TableName'] == 'PreviewState'])
        if type(row['scoped']) is not list or len(row['scoped']) != 41: fail('V2_PREBASELINE_CONFIGS')
        for actual, expected in zip(row['scoped'], baseline['scoped']):
            if expected['name'] in ('PREVIEW_FEATURES', 'MAXDOP'):
                exact(actual, expected)
                for key in ('configuration_id', 'name', 'value_for_secondary'): same(actual[key], expected[key])
                v1.integer(actual['value'], preview if expected['name'] == 'PREVIEW_FEATURES' else maxdop)
                if type(actual['is_value_default']) is not bool: fail('V2_CONFIG_BOOL')
            else: same(actual, expected)
    for row in states[4:]:
        expected = dict(baseline, vector_indexes=1); same(row, expected)
    window = e['shared_cleanup_window']; exact(window, ['Status', 'StartedMonotonic', 'DeadlineMonotonic', 'Seconds'])
    number(window['StartedMonotonic']); number(window['DeadlineMonotonic']); v1.integer(window['Seconds'], 60)
    if window['Status'] != 'ACTUAL_STARTED' or abs(window['DeadlineMonotonic'] - window['StartedMonotonic'] - 60) > 1e-7: fail('V2_SHARED_CLEANUP_WINDOW')
    contexts = e['role_contexts']; costs = e['phase_costs']
    if type(contexts) is not list or len(contexts) != 8 or type(costs) is not list or len(costs) != 2: fail('V2_CONTEXT_COST_POPULATION')
    for offset, stage, cap in ((0, 'DML_BOUNDARY', c[10]), (4, 'REBUILD', c[15])):
        rows = selected(cap, 'ROLE_CONTEXT', 4); same(contexts[offset:offset+4], rows)
        frames = selected(cap, 'PHASE_COST', 2)
        actual = pure_helper('cost').validate_costs(frames, token=b['token'], database_id=b['database_id'], stage=stage, file_ids={1, 2})
        same(costs[offset//4], actual); context_check(rows, b, stage, frames)
    dml = selected(c[10], 'DML_BOUNDARY', 8)
    v1.dml(dml, b, 'SQLPERF_LAB_IDX012_' + b['token'])
    same(e['dml_boundary'], pure_helper('dml_boundary').validate_dml_boundary(dml, token=b['token'], database_id=b['database_id']))
    index = selected(c[10], 'INDEX', 1)[0]; same(e['index'], index)
    exact(index, ['kind', 'RunToken', 'DatabaseId', 'BuildElapsedUs', 'metadata'])
    if index['RunToken'] != b['token']: fail('V2_INDEX_IDENTITY')
    v1.integer(index['DatabaseId'], b['database_id']); v1.integer(index['BuildElapsedUs'])
    v1.metadata({'before': index['metadata'], 'after': index['metadata']}, b)
    before, before_text = source_rows(c[7], b)
    after, after_text = source_rows(c[13], b)
    rebuilt, rebuilt_text = source_rows(c[17], b, changed=True)
    same(before, after); same(before_text, after_text)
    if any(before_text[i] != rebuilt_text[i] for i in range(1, 999)): fail('V2_OTHER_SOURCE_CHANGED')
    same(e['independent_source_comparison'], {'rows': 999, 'full_text_equal': True, 'distance_equal': True})
    same(e['rebuild_source_comparison'], {'rows': 999, 'only_changed_id': 999, 'other_998_texts_equal': True})
    lifecycle = pure_helper('lifecycle').validate_lifecycle(records(c[15]), token=b['token'], database_id=b['database_id'], before_distances=before, after_distances=rebuilt, before_metadata=index['metadata'])
    same(e['lifecycle'], lifecycle)
    if type(e['storage']) is not list or len(e['storage']) != 3: fail('V2_STORAGE_POPULATION')
    for i, position, stage in ((0, 9, 'BASELINE'), (1, 12, 'INDEXED'), (2, 19, 'REBUILT')):
        actual = pure_helper('storage').validate_storage(selected(c[position], 'STORAGE', 1)[0], token=b['token'], database_id=b['database_id'], fixture_object=b['fixture_object'], stage=stage)
        same(e['storage'][i], actual)
    for pos, required in ((20, f"ANN_RESTORE|{b['token']}|{b['original_preview']}|0"), (21, f"ANN_ATTEST|{b['token']}|{b['original_preview']}|0"), (21, 'ANN_RECOVERY|DROP_CONFIRMED'), (22, 'ANN_DB|ABSENT')):
        lines = [line.strip() for text in (c[pos]['Stdout'], c[pos]['Stderr']) for line in text.splitlines() if line.strip().startswith(required.split('|')[0] + '|')]
        if lines != [required]: fail('V2_SQL_CLEANUP_TEXT')
