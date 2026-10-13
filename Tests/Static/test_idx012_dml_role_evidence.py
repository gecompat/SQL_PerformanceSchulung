"""Gezielte reine Gegenfälle; synthetische Daten, keine historischen Replays."""
from pathlib import Path
import copy
import base64
import json
import math
import tempfile
import unittest
from unittest.mock import patch
import idx012_dml_role_evidence as m


def fixture():
    b = {'token': 'ABCDEF0123456789', 'database_id': 5, 'fixture_object': 1000,
         'operator_sid': '0x'+'A1'*16, 'admin_sid': '0x01', 'original_preview': 0,
         'consumer_sources': m.source_binding(), 'provenance': 'PUREFIXTURE_ONLY'}
    database, operator = 'SQLPERF_LAB_IDX012_'+b['token'], 'SQLPERF_IDX012_ROLE_'+b['token']
    source = {'DatabaseId': 5, 'vectors': [], 'rows': []}
    for i in range(1, 1000):
        values = [1, i/1000, ((i*17)%97)*1000000//97/1000000]
        source['vectors'].append({'Id': i, 'JsonValue': json.dumps(values)})
        source['rows'].append({'Id': i, 'DistanceValue': 1-1/math.sqrt(sum(x*x for x in values))})
    dml = []
    for i in range(8):
        success = i < 4
        dml.append({'kind': 'DML_BOUNDARY', 'Stage': 'NO_INDEX' if success else 'WITH_INDEX', 'Operation': m.OPERATIONS[i%4], 'Ordinal': i+1, 'RunToken': b['token'], 'DatabaseId': 5, 'Context': database, 'StaleOptionState': 'ABSENT', 'Succeeded': success, 'AffectedRows': 1 if success else None, 'DuringRowCount': m.DURING[i] if success else None, 'ExpectedChange': True if success else None, 'ErrorNumber': None if success else 42231, 'ErrorState': None if success else 1, 'ErrorMessage': None if success else 'Synthetische Vector-Index-DML-Verweigerung.', 'SourceRestored': True, 'RolledBack': True, 'TransactionCount': 0, 'TransactionState': 0, 'RestoredRowCount': 999, 'IndexMetadataUnchanged': None if success else True})
    contexts = []
    for i in range(8):
        admin = i%4 == 1
        contexts.append({'kind': 'ROLE_CONTEXT', 'Stage': 'DML_BOUNDARY' if i<4 else 'REBUILD', 'Checkpoint': m.CHECKPOINTS[i%4], 'LoginName': 'sa' if admin else operator, 'Sid': b['admin_sid'] if admin else b['operator_sid'], 'OriginalLogin': 'sa', 'Sysadmin': int(admin), 'ControlServer': int(admin)})
    audits = []
    for action in m.ACTIONS:
        names = ['CREATE ANY DATABASE', 'VIEW SERVER PERFORMANCE STATE']
        if action == 'REVOKE_CREATE': names.remove('CREATE ANY DATABASE')
        if action == 'REVOKE_PERF': names.remove('VIEW SERVER PERFORMANCE STATE')
        audits.append({'action': action, 'name': operator, 'sid': b['operator_sid'], 'roles': 0,
            'permissions': [{'class': 100, 'major_id': 0, 'state': 'G', 'permission_name': n} for n in names]})
    markers = {'SQLPERF.Project': 'SQL_PerformanceSchulung', 'SQLPERF.ContractVersion': '1.0', 'SQLPERF.DemoId': 'IDX-012', 'SQLPERF.RunToken': b['token']}
    options = {k: False if k.startswith('is_') else 0 for k in m.OPTION_FIELDS}
    options.update(compatibility_level=170, recovery_model=3, collation_name='SYNTHETIC_COLLATION')
    snapshot = {'DatabaseId': 5, 'context': database, 'build': '17.0.5005.3', 'edition': 3,
        'fixture_object': 1000, 'vector_indexes': 0, 'baseline': [{'Id': 1, 'OriginalValue': 0, 'RunToken': b['token'], 'MaxDopOriginal': 0}],
        'tables': [{'SchemaName': s, 'TableName': n, 'object_id': 1000+i} for i,(s,n) in enumerate([('lab','VectorFixture'),('dbo','PreviewState'),('lab','FrozenSource'),('lab','ExactOracle')])],
        'markers': [{'name': n, 'ValueBytes': base64.b64encode(v.encode('utf-16-le')).decode('ascii'), 'ByteLength': len(v.encode('utf-16-le'))} for n,v in markers.items()],
        'host': [{'configuration_id': 1, 'name': 'SYNTHETIC_HOST_CONFIG', 'value': 0, 'value_in_use': 0, 'minimum': 0, 'maximum': 1, 'description': 'Synthetische Fixture', 'is_dynamic': True, 'is_advanced': False}],
        'scoped': [{'configuration_id': i+1, 'name': ('PREVIEW_FEATURES','MAXDOP')[i] if i<2 else 'SYNTHETIC_CONFIG_'+str(i), 'value': 1 if i<2 else 0, 'value_for_secondary': 0, 'is_value_default': i>=2} for i in range(41)],
        'options': [options], 'files': [{'file_id': i+1, 'type': i, 'NameBytes': base64.b64encode((database+('_log' if i==1 else '')).encode('utf-16-le')).decode('ascii'), 'max_size': 32768 if i==0 else 8192, 'growth': 2048, 'is_percent_growth': False} for i in range(2)]}
    after = copy.deepcopy(snapshot); after['vector_indexes'] = 1
    index = {k: 0 if t is int else False if t is bool else '' if t is str else None for k,t in m.INDEX_TYPES.items()}
    index.update(object_id=1000, name='IDX012_OwnVector', index_id=2, type=8, type_desc='VECTOR', vector_index_type='DiskANN', distance_metric='COSINE', build_parameters='{}')
    negatives = [{'withdrawn': a, 'outcome': 'SKIP', 'code': 'SKIP_PERMISSION', 'phases': [['PREFLIGHT','SKIP','SKIP_PERMISSION']], 'original_preview': None, 'cleanup_ok': False, 'detail': d, 'database_absence_frame': 'ANN_DB|ABSENT'} for a,d in [('REVOKE_CREATE','MISSING_CREATE_DATABASE'),('REVOKE_PERF','MISSING_SERVER_PERFORMANCE_STATE')]]
    r = {'contract': m.SCHEMA, 'profile': copy.deepcopy(m.EXPECTED_CONTRACT['profile']), 'source_inputs': copy.deepcopy(m.INPUT_PINS), 'dml': dml, 'contexts': contexts, 'audits': audits, 'permission_negatives': negatives, 'source_before': source, 'source_after': copy.deepcopy(source), 'snapshots': {'before': snapshot, 'after': after}, 'index_metadata': {'before': [index], 'after': [copy.deepcopy(index)]}, 'owner_frame': 'IDX012_ROLE|OWN_DATABASE_OWNER',
        'cleanup': {'restore_frame': 'ANN_RESTORE|'+b['token']+'|0|0', 'attest_frame': 'ANN_ATTEST|'+b['token']+'|0|0', 'drop_frame': 'ANN_RECOVERY|DROP_CONFIRMED', 'database_absence_frame': 'ANN_DB|ABSENT', 'role_drop_frame': 'IDX012_ROLE|ABSENT', 'role_absence_frame': 'IDX012_ROLE|ABSENT', 'cid_query_stdout': None, 'name_query_stdout': None, 'active_inputs': None},
        'capture': {'individual_client_end_input': None, 'server_request_end': None, 'dml_severity_line_procedure': None}}
    return r, b


class RecordTests(unittest.TestCase):
    def rejected(self, mutate):
        r,b = fixture(); mutate(r,b)
        with self.assertRaises((ValueError, TypeError, OverflowError)): m.report(r,b)

    def test_complete_fixture_is_bounded_warn_without_raw_identity_exports(self):
        r,b = fixture(); result = m.report(r,b)
        self.assertEqual(result['outcome'], 'WARN'); self.assertEqual(result['counts']['positive_dml'], 4)
        self.assertEqual(result['individual_end_input_capture'], 'NOT_ESTABLISHED')
        self.assertEqual(result['namespace_capture'], 'NOT_ESTABLISHED')
        text = m.canonical(result)
        for raw in (b['token'], b['operator_sid'], r['contexts'][0]['LoginName'], r['source_before']['vectors'][20]['JsonValue']): self.assertNotIn(raw,text)
        self.assertTrue(all(value == 'NOT_ESTABLISHED' for key,value in result['claims'].items() if key in ('runtime_qualification','tp_perf','minimum_roles')))

    def test_missing_extra_schema_nonbuiltin_and_source_binding_fail_closed(self):
        self.rejected(lambda r,b:r.pop('dml')); self.rejected(lambda r,b:r.update(raw_export='UNEXPECTED'))
        self.rejected(lambda r,b:b['consumer_sources'].update(extra='a'*64))
        self.rejected(lambda r,b:b.update(database_id=True))
        with self.assertRaises(ValueError): m.report([], {})
        subtype = type('dict', (dict,), {})
        r,b = fixture()
        with self.assertRaises(ValueError): m.report(subtype(r),b)

    def test_dml_population_order_duplicate_and_complete_error_fields(self):
        self.rejected(lambda r,b:r['dml'].pop())
        self.rejected(lambda r,b:r['dml'].__setitem__(1,copy.deepcopy(r['dml'][0])))
        self.rejected(lambda r,b:r['dml'][0].update(Operation='INSERT_ID_1000'))
        self.rejected(lambda r,b:r['dml'][4].update(ErrorNumber=229))
        self.rejected(lambda r,b:r['dml'][4].update(ErrorMessage=None))
        self.rejected(lambda r,b:r['dml'][4].update(ErrorState=True))

    def test_full_source_population_float_bool_nan_and_distance_oracle(self):
        self.rejected(lambda r,b:r['source_before']['vectors'].pop())
        self.rejected(lambda r,b:r['source_before']['vectors'][1].update(Id=1))
        self.rejected(lambda r,b:r['source_after']['vectors'][0].update(JsonValue='[true,0.001,0.1]'))
        self.rejected(lambda r,b:r['source_after']['rows'][1].update(DistanceValue=float('nan')))
        self.rejected(lambda r,b:r['source_after']['rows'][1].update(DistanceValue=0.99))
        self.rejected(lambda r,b:r['source_after']['vectors'][1].update(JsonValue='[1,2,3]'))

    def test_context_full_sid_privilege_and_admin_boundary(self):
        self.rejected(lambda r,b:r['contexts'][0].update(Sysadmin=True))
        self.rejected(lambda r,b:r['contexts'][2].update(Sid='0x'+'A2'*16))
        self.rejected(lambda r,b:r['contexts'][1].update(Sid=b['operator_sid']))
        self.rejected(lambda r,b:r['contexts'][0].update(LoginName='sa'))
        self.rejected(lambda r,b:r['contexts'][1].update(Checkpoint='ROLE_END'))
        self.rejected(lambda r,b:r['contexts'].append(copy.deepcopy(r['contexts'][1])))

    def test_principal_audit_permission_tuples_revocation_and_restore(self):
        self.rejected(lambda r,b:r['audits'][0].update(roles=False))
        self.rejected(lambda r,b:r['audits'][0]['permissions'][0].update(major_id=False))
        self.rejected(lambda r,b:r['audits'][0]['permissions'][0].update(permission_name='CONTROL SERVER'))
        self.rejected(lambda r,b:r['audits'][1]['permissions'].append({'class':100,'major_id':0,'state':'G','permission_name':'CREATE ANY DATABASE'}))
        self.rejected(lambda r,b:r['audits'][2]['permissions'].append({'class':100,'major_id':0,'state':'G','permission_name':'CONNECT SQL'}))
        self.rejected(lambda r,b:r['audits'][0].update(name=r['audits'][0]['name']+' '))

    def test_rollback_peak_and_source_restoration_never_default_true(self):
        for key,value in [('TransactionCount',False),('TransactionState',1),('SourceRestored',None),('RolledBack',False),('RestoredRowCount',998),('DuringRowCount',1001)]:
            self.rejected(lambda r,b,k=key,v=value:r['dml'][0].update(**{k:v}))
        self.rejected(lambda r,b:r['dml'][4].update(IndexMetadataUnchanged=False))

    def test_full_snapshot_markers_options_tables_and_serial_continuity(self):
        self.rejected(lambda r,b:r['snapshots']['before']['markers'][0].update(ValueBytes='0x00'))
        self.rejected(lambda r,b:r['snapshots']['before']['markers'][0].update(name='SQLPERF.project'))
        self.rejected(lambda r,b:r['snapshots']['after']['scoped'][2].update(value=7))
        self.rejected(lambda r,b:r['snapshots']['after']['options'][0].pop('is_trustworthy_on'))
        self.rejected(lambda r,b:r['snapshots']['before']['tables'][1].update(object_id=1000))

    def test_canonical_base64_marker_bytes_lengths_and_owned_file_names(self):
        r,b = fixture(); self.assertEqual(m.report(r,b)['outcome'], 'WARN')
        for value in ('0x31002E003000', 'MQAuADAA ', 'MQAuADAA=', 'BAD', ''):
            self.rejected(lambda r,b,v=value:r['snapshots']['before']['markers'][1].update(ValueBytes=v))
        for length in (True, 6.0, 0, 7):
            self.rejected(lambda r,b,v=length:r['snapshots']['before']['markers'][1].update(ByteLength=v))
        raw='1.0'.encode('utf-16-le')+b'\x00\x00'
        self.rejected(lambda r,b:r['snapshots']['before']['markers'][1].update(ValueBytes=base64.b64encode(raw).decode('ascii'),ByteLength=len(raw)))
        for index in (0,1):
            for text in ('FOREIGN_DATABASE', 'SQLPERF_LAB_IDX012_'+b['token']+' ', 'SQLPERF_LAB_IDX012_'+b['token']+('_log' if index==0 else '')):
                value=base64.b64encode(text.encode('utf-16-le')).decode('ascii')
                self.rejected(lambda r,b,i=index,v=value:r['snapshots']['before']['files'][i].update(NameBytes=v))
        self.rejected(lambda r,b:r['snapshots']['before']['files'][0].update(NameBytes='0x00'))

    def test_complete_index_metadata_missing_version_and_foreign_object(self):
        self.rejected(lambda r,b:r['index_metadata']['before'][0].pop('allow_page_locks'))
        self.rejected(lambda r,b:r['index_metadata']['before'][0].update(object_id=9999))
        self.rejected(lambda r,b:r['index_metadata']['after'][0].update(build_parameters='{"Version":2}'))
        self.rejected(lambda r,b:r['index_metadata']['after'][0].update(fill_factor=1))

    def test_permission_skip_before_setup_and_actual_sql_cleanup_required(self):
        self.rejected(lambda r,b:r['permission_negatives'][0]['phases'].append(['SETUP','PASS','OK']))
        self.rejected(lambda r,b:r['permission_negatives'][1].update(cleanup_ok=True))
        self.rejected(lambda r,b:r['cleanup'].update(restore_frame='ANN_RESTORE|ALREADY_ABSENT'))
        self.rejected(lambda r,b:r['cleanup'].update(role_absence_frame=None))
        self.rejected(lambda r,b:r['cleanup'].update(cid_query_stdout=False))
        self.rejected(lambda r,b:r['cleanup'].update(active_inputs=0))

    def test_missing_capture_cannot_be_replaced_by_flags_or_fake_ends(self):
        for key in ('individual_client_end_input','server_request_end','dml_severity_line_procedure'):
            self.rejected(lambda r,b,k=key:r['capture'].update(**{k:True}))
            self.rejected(lambda r,b,k=key:r['capture'].update(**{k:0}))
        r,b = fixture(); r['cleanup'].update(cid_query_stdout='',name_query_stdout='',active_inputs=[])
        result=m.report(r,b);self.assertEqual(result['outcome'],'WARN');self.assertEqual(result['claims']['runtime_qualification'],'NOT_ESTABLISHED')

    def test_rebound_contract_claim_count_extra_raw_and_input_pin_drift(self):
        self.rejected(lambda r,b:r['source_inputs']['DML_BOUNDARY'].update(sha256='f'*64))
        with tempfile.TemporaryDirectory(dir=m.ROOT/'Runtime') as folder:
            contract=Path(folder)/'contract.json'
            for change in [lambda x:x['claims'].update(runtime_qualification='PASS'),lambda x:x['expected_counts'].update(positive_dml=True),lambda x:x.update(raw_export='UNEXPECTED')]:
                data=copy.deepcopy(m.EXPECTED_CONTRACT);change(data);contract.write_bytes(json.dumps(data).encode())
                with patch.object(m,'CONTRACT',contract):
                    r,b=fixture()
                    with self.assertRaisesRegex(ValueError,'FIXED_CONTRACT_DRIFT'):m.report(r,b)


if __name__ == '__main__': unittest.main()
