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


def public_v2_fixture():
    """Vollständig synthetische APIform; kein historischer Rawrecord."""
    import idx012_public_role_evidence_v2 as v2
    r, old = fixture()
    b = {k: old[k] for k in ('token', 'database_id', 'fixture_object', 'operator_sid', 'admin_sid', 'original_preview', 'provenance')}
    b.update(execution_sources=v2.execution_sources(), consumer_sources=v2.source_binding())
    token, db = b['token'], b['database_id']
    base = dict(generation='UNKNOWN', runtime_qualification='NOT_ESTABLISHED',
        role_runtime_qualification='NOT_ESTABLISHED', role_server_request_end='NOT_ATTESTED',
        role_profile='operator-admin-build', role_cost_scope='WHOLE_PHASE_INCLUDING_CONTEXT_AND_ATTESTATION',
        role_collector_mode='FIXED_ABSOLUTE_CALL_DEADLINE', role_reap_reserve_seconds=2)
    def cap(script, ordinal):
        text = 'SET NOCOUNT ON; -- ausschließlich synthetische Capturefixture\n'
        return dict(Auth='ADMIN_ORIGINAL_OPERATOR_CONTEXT' if script in ('30_CostBoundary.sql', '50_CostRebuild.sql') else 'OPERATOR_AUTH',
            Budget=dict(AbsoluteDeadline=1000.0, ChannelsObserved=True, CollectorCode=None, CollectorFailed=False,
                ObservedOverrun=False, PreReapPoll=0, PrimaryWaitSeconds=4.0, ReapReserveSeconds=2),
            ChannelStatus='SAFE', CollectorCode=None, CollectorDurationSeconds=0.1, CollectorFailed=False,
            CollectorMode='FIXED_ABSOLUTE_CALL_DEADLINE', ElapsedSeconds=0.2, FinalPoll=0,
            InputSha256=m.hashlib.sha256(text.encode()).hexdigest(), InputText=text, Phase=script, Pid=100+ordinal,
            ProcessReturnCode=0, ProcessStartAttempted=True, ProcessStarted=True, RejectCode=None,
            ReturnCode=0, ServerRequestEnd='NOT_ATTESTED', SourceBefore=copy.deepcopy(b['execution_sources']),
            SourceAfter=copy.deepcopy(b['execution_sources']), Stdout='', Stderr='', TimedOut=False, UnknownSticky=False)
    def inputs(captures):
        return [dict(Path='PUREFIXTURE/role-'+str(i)+'.sql', InputSha256=c['InputSha256'], Retained=False) for i,c in enumerate(captures)]
    profiles = []
    for i, detail in enumerate(('MISSING_CREATE_DATABASE', 'MISSING_SERVER_PERFORMANCE_STATE')):
        c = cap('00_Preflight.sql', i)
        c['Stdout'] = 'IDX012_DETAIL|'+detail+'\n'
        e = copy.deepcopy(base); e.update(role_captures=[c], role_inputs=inputs([c]), shared_cleanup_window={'DeadlineMonotonic':None,'Seconds':60,'StartedMonotonic':None,'Status':'NOT_STARTED'})
        profiles.append(dict(outcome='SKIP', code='SKIP_PERMISSION', phases=[['PREFLIGHT','SKIP','SKIP_PERMISSION']], original_preview=None, cleanup_ok=False, evidence=e))
    captures = [cap(script, i+2) for i,script in enumerate(v2.SCRIPTS)]
    def put(position, rows, extra=''):
        captures[position]['Stdout'] = '\n'.join(json.dumps(row, separators=(',',':')) for row in rows)+'\n'+extra
    def source(data, changed=False):
        vectors=copy.deepcopy(data['vectors']); distances=copy.deepcopy(data['rows'])
        if changed: vectors[-1]['JsonValue']='[1,0,0]'; distances[-1]['DistanceValue']=0
        rows=[dict(kind='SOURCE_DISTANCES',DatabaseId=db,rows=distances)]
        for i in range(10): rows.append(dict(kind='SOURCE_VECTOR_BLOCK',DatabaseId=db,BlockId=i+1,vectors=vectors[i*100:(i+1)*100]))
        return rows, {item['Id']:item['DistanceValue'] for item in distances}
    baseline, distances=source(r['source_before'])
    rebuilt, after_distances=source(r['source_before'],True)
    put(7,baseline);put(13,baseline);put(17,rebuilt)
    index=dict(kind='INDEX',DatabaseId=db,RunToken=token,BuildElapsedUs=10,metadata=r['index_metadata']['before'])
    def contexts(stage, session):
        return [dict(kind='ROLE_CONTEXT',Stage=stage,Checkpoint=k,
            LoginName='sa' if k=='ADMIN_BUILD' else 'SQLPERF_IDX012_ROLE_'+token,
            Sid=b['admin_sid'] if k=='ADMIN_BUILD' else b['operator_sid'],OriginalLogin='sa',OriginalSid=b['admin_sid'],
            Sysadmin=int(k=='ADMIN_BUILD'),ControlServer=int(k=='ADMIN_BUILD'),AlterAnyLogin=int(k=='ADMIN_BUILD'),
            SessionId=session,DatabaseId=db,RunToken=token) for k in m.CHECKPOINTS]
    def frames(stage,session):
        rows=[]
        for i,frame in enumerate(('BEFORE','AFTER')):
            rows.append(dict(kind='PHASE_COST',Stage=stage,Frame=frame,DatabaseId=db,Context='SQLPERF_LAB_IDX012_'+token,RunToken=token,
                SessionId=session,SourceRows=999,VectorIndexes=0 if stage=='DML_BOUNDARY' and i==0 else 1,
                TransactionCount=0,TransactionState=0,SessionCount=1,TempdbCount=1,FileCount=2,
                session=[dict(session_id=session,cpu_time=i,reads=i,writes=i,logical_reads=i)],
                tempdb=[dict(session_id=session,database_id=2,user_objects_alloc_page_count=i,user_objects_dealloc_page_count=0,internal_objects_alloc_page_count=i,internal_objects_dealloc_page_count=0)],
                files=[dict(database_id=db,file_id=f,sample_ms=i,num_of_writes=i,num_of_bytes_written=i,io_stall_write_ms=i) for f in(1,2)]))
        return rows
    ctx1=contexts('DML_BOUNDARY',77);ctx2=contexts('REBUILD',78)
    f1=frames('DML_BOUNDARY',77);f2=frames('REBUILD',78)
    put(10,ctx1+f1+r['dml']+[index])
    lifecycle=[dict(kind='LIFECYCLE_DROP',DatabaseId=db,RunToken=token,IndexCount=0,RowCount=999,TransactionCount=0,TransactionState=0),
        dict(kind='LIFECYCLE_CHANGE',DatabaseId=db,RunToken=token,AffectedRows=1,RowCount=999,TransactionCount=0,TransactionState=0,Committed=True,OtherSourceUnchanged=True,NewVector='[1,0,0]',IndexCount=0),
        dict(kind='LIFECYCLE_REBUILD',DatabaseId=db,RunToken=token,BuildElapsedUs=11,BeforeMetadata=index['metadata'],AfterMetadata=index['metadata'])]
    for i,(stage,path) in enumerate((('BASELINE','EXACT'),('BASELINE','ANN'),('AFTER_CHANGE','EXACT'),('REBUILT','EXACT'),('REBUILT','ANN')),1):
        d=distances if stage=='BASELINE' else after_distances
        ids=sorted(d,key=lambda k:(d[k],k))[:5]
        lifecycle.append(dict(kind='LIFECYCLE_QUERY',DatabaseId=db,RunToken=token,Ordinal=i,Stage=stage,Path=path,rows=[dict(Id=k,DistanceValue=d[k])for k in ids]))
    put(15,ctx2+f2+lifecycle)
    storage=[]
    for position,stage in((9,'BASELINE'),(12,'INDEXED'),(19,'REBUILT')):
        raw=dict(kind='STORAGE',Stage=stage,DatabaseId=db,Context='SQLPERF_LAB_IDX012_'+token,RunToken=token,FixtureObject=b['fixture_object'],
            SourceRows=999,VectorIndexes=0 if stage=='BASELINE' else 1,TransactionCount=0,TransactionState=0,FileCount=2,InternalCount=0,PartitionCount=1,
            files=[dict(file_id=1,type=0,size=128,space_used_pages=10),dict(file_id=2,type=1,size=128,space_used_pages=None)],internal_tables=[],
            partitions=[dict(partition_id=1,object_id=b['fixture_object'],index_id=1,partition_number=1,row_count=999,used_page_count=10,reserved_page_count=12,in_row_used_page_count=10,lob_used_page_count=0,row_overflow_used_page_count=0)])
        put(position,[raw]);storage.append(v2.pure_helper('storage').validate_storage(raw,token=token,database_id=db,fixture_object=b['fixture_object'],stage=stage))
    for position in(2,4,6,8,11,14,16,18):
        state=copy.deepcopy(r['snapshots']['after' if position>=11 else 'before'])
        if position<8:
            state['fixture_object']=None;state['tables']=[t for t in state['tables']if t['TableName']=='PreviewState']
            for row in state['scoped']:
                if row['name']=='PREVIEW_FEATURES':row['value']=int(position>=4)
                if row['name']=='MAXDOP':row['value']=int(position>=6)
        put(position,[state])
    captures[20]['Stdout']=f'ANN_RESTORE|{token}|0|0\n'
    captures[21]['Stdout']=f'ANN_ATTEST|{token}|0|0\nANN_RECOVERY|DROP_CONFIRMED\n'
    captures[22]['Stdout']='ANN_DB|ABSENT\n'
    e=copy.deepcopy(base);e.update(role_captures=captures,role_inputs=inputs(captures),database_id=db,
        shared_cleanup_window=dict(Status='ACTUAL_STARTED',StartedMonotonic=900.0,DeadlineMonotonic=960.0,Seconds=60),
        role_contexts=ctx1+ctx2,phase_costs=[v2.pure_helper('cost').validate_costs(f,token=token,database_id=db,stage=stage,file_ids={1,2})for f,stage in((f1,'DML_BOUNDARY'),(f2,'REBUILD'))],
        dml_boundary=v2.pure_helper('dml_boundary').validate_dml_boundary(r['dml'],token=token,database_id=db),index=index,
        independent_source_comparison=dict(rows=999,full_text_equal=True,distance_equal=True),
        rebuild_source_comparison=dict(rows=999,only_changed_id=999,other_998_texts_equal=True),storage=storage,
        lifecycle=v2.pure_helper('lifecycle').validate_lifecycle(lifecycle,token=token,database_id=db,before_distances=distances,after_distances=after_distances,before_metadata=index['metadata']))
    profiles.append(dict(outcome='WARN',code='WARN_OPTIONAL_EVIDENCE_SKIPPED',phases=[[p,'WARN'if i==0 else 'PASS','WARN_OPTIONAL_EVIDENCE_SKIPPED'if i==0 else 'OK']for i,p in enumerate(v2.PHASES)],original_preview=0,cleanup_ok=True,evidence=e))
    return json.loads(json.dumps({'contract':v2.SCHEMA,'profiles':profiles})),b


class PublicV2Tests(unittest.TestCase):
    def rejected(self,change,secrets=None):
        import idx012_public_role_evidence_v2 as v2
        r,b=public_v2_fixture();change(r,b)
        with self.assertRaises((ValueError,TypeError)):v2.report(r,b,secrets=[]if secrets is None else secrets)

    def test_public_v2_coherent_warn_bounded_export_and_v1_preserved(self):
        import idx012_public_role_evidence_v2 as v2
        r,b=public_v2_fixture();result=v2.report(r,b,secrets=[])
        self.assertEqual(result['outcome'],'WARN');self.assertEqual(result['counts']['client_captures'],25)
        self.assertEqual(result['credential_check'],'NOT_CHECKED_FOR_UNAVAILABLE_SECRETS')
        self.assertTrue(all(result['claims'][k]=='NOT_ESTABLISHED'for k in('owner_query','server_request_end','dml_full_error_capture','runtime_qualification','principal_cleanup','namespace_cleanup')))
        text=json.dumps(result)
        for value in(b['token'],b['operator_sid'],'InputText','Stdout','Pid','sha256'):self.assertNotIn(value,text)
        self.assertEqual(m.SCHEMA,'IDX012_DML_ROLE_RECORD_V1');self.assertEqual(m.INPUT_PINS['DML_BOUNDARY']['utf8_bytes'],28420)

    def test_public_v2_plain_schema_sources_contract_and_extra_fields(self):
        import idx012_public_role_evidence_v2 as v2
        for change in(lambda r,b:r.update(extra=True),lambda r,b:b['execution_sources'].pop(next(iter(b['execution_sources']))),
            lambda r,b:b['execution_sources'].update({next(iter(b['execution_sources'])):'f'*64}),
            lambda r,b:r['profiles'][2]['evidence'].update(owner_query='PASS'),
            lambda r,b:r['profiles'][2]['evidence'].update(database_id=True)):
            self.rejected(change)
        string_alias=type('str',(str,),{})
        self.rejected(lambda r,b:r.update(contract=string_alias(v2.SCHEMA)))
        for change in(lambda x:x['counts'].update(cost_pairs=True),lambda x:x['claims'].update(runtime_qualification='PASS'),lambda x:x.update(raw='extra')):
            with tempfile.TemporaryDirectory()as folder:
                p=Path(folder)/'contract.json';data=copy.deepcopy(v2.EXPECTED);change(data);p.write_bytes(json.dumps(data).encode())
                with patch.object(v2,'CONTRACT',p),patch.object(v2,'source_binding',return_value={'PURE': 'a'*64}):
                    r,b=public_v2_fixture()
                    with self.assertRaises(ValueError):v2.report(r,b,secrets=[])

    def test_public_v2_individual_end_input_channels_and_unknown(self):
        for field,value in(('FinalPoll',None),('ReturnCode',True),('TimedOut',True),('UnknownSticky',True),('ProcessStarted',False),('ChannelStatus','SAFE_COMPLETE'),('InputSha256','f'*64),('ElapsedSeconds',float('inf'))):
            self.rejected(lambda r,b,k=field,v=value:r['profiles'][2]['evidence']['role_captures'][0].update(**{k:v}))
        self.rejected(lambda r,b:r['profiles'][2]['evidence']['role_captures'][0]['Budget'].update(ObservedOverrun=True))
        self.rejected(lambda r,b:r['profiles'][2]['evidence']['role_inputs'][0].update(Retained=True))
        self.rejected(lambda r,b:r['profiles'][2]['evidence']['role_captures'].pop())

    def test_public_v2_order_sid_privilege_and_same_cost_session(self):
        for change in(lambda r,b:r['profiles'][2]['evidence']['role_contexts'].reverse(),
            lambda r,b:r['profiles'][2]['evidence']['role_contexts'][1].update(Sid=b['operator_sid']),
            lambda r,b:r['profiles'][2]['evidence']['role_contexts'][0].update(AlterAnyLogin=True),
            lambda r,b:r['profiles'][2]['evidence']['phase_costs'][0]['frames'][1].update(SessionId=99)):
            self.rejected(change)
        # Gleichartige Manipulation im Raw UND Summary darf nicht durch Vergleich passieren.
        def rebind(r,b):
            e=r['profiles'][2]['evidence'];rows=[]
            for line in e['role_captures'][10]['Stdout'].splitlines():
                item=json.loads(line)
                if item.get('kind')=='ROLE_CONTEXT'and item['Checkpoint']=='ROLE_END':item['SessionId']=99
                rows.append(item)
            e['role_captures'][10]['Stdout']='\n'.join(json.dumps(x)for x in rows)
            e['role_contexts'][3]['SessionId']=99
        self.rejected(rebind)

    def test_public_v2_distinct_rights_negatives_cleanup_and_warn(self):
        for change in(lambda r,b:r['profiles'][1]['evidence']['role_captures'][0].update(Stdout='IDX012_DETAIL|MISSING_CREATE_DATABASE'),
            lambda r,b:r['profiles'][0]['phases'].append(['SETUP','PASS','OK']),
            lambda r,b:r['profiles'][2].update(outcome='PASS'),
            lambda r,b:r['profiles'][2]['evidence']['role_captures'][22].update(Stdout=''),
            lambda r,b:r['profiles'][2]['evidence']['shared_cleanup_window'].update(Seconds=True)):
            self.rejected(change)

    def test_public_v2_negative_window_full_not_started_contract(self):
        import idx012_public_role_evidence_v2 as v2
        r,b=public_v2_fixture()
        result=v2.report(r,b,secrets=[])
        self.assertEqual(result['outcome'],'WARN')
        self.assertEqual(result['counts']['permission_negatives'],2)
        self.assertEqual(result['claims']['runtime_qualification'],'NOT_ESTABLISHED')
        for ordinal in(0,1):
            for key in('DeadlineMonotonic','Seconds','StartedMonotonic','Status'):
                self.rejected(lambda r,b,i=ordinal,k=key:r['profiles'][i]['evidence']['shared_cleanup_window'].pop(k))
            for change in(lambda w:w.update(extra=None),lambda w:w.update(Seconds=True),lambda w:w.update(Seconds=60.0),
                lambda w:w.update(Seconds=59),lambda w:w.update(StartedMonotonic=0),lambda w:w.update(DeadlineMonotonic=False),
                lambda w:w.update(Status='ACTUAL_STARTED'),lambda w:w.update(Status=None)):
                self.rejected(lambda r,b,i=ordinal,c=change:c(r['profiles'][i]['evidence']['shared_cleanup_window']))

    def test_public_v2_credential_plain_hex_json_and_received_frames(self):
        import idx012_public_role_evidence_v2 as v2
        secrets=['SyntheticSecretOne7','SyntheticSecretTwo8']
        for value in(secrets[0],secrets[1].encode().hex(),secrets[0].encode('utf-16-le').hex().upper(),
            '{"Message":"'+''.join('\\u%04x'%ord(c)for c in secrets[0])+'"}'):
            self.rejected(lambda r,b,v=value:r['profiles'][2]['evidence']['role_captures'][0].update(Stderr=v),secrets)
        wire=secrets[0].encode('utf-16-le').hex().upper();parts=wire[:30],wire[30:]
        self.rejected(lambda r,b:r['profiles'][2]['evidence']['role_captures'][0].update(Stderr='IDX012_PART|1|'+parts[0]+'\nIDX012_PART|2|'+parts[1]),secrets)
        # Repro: Mixedcase in InputText muss vor jedem Input-/Quellendigest scheitern.
        for encoded in(secrets[0].encode().hex(),secrets[1].encode('utf-16-le').hex()):
            upper=False;letters=[]
            for c in encoded:
                if c.isalpha():upper=not upper;letters.append(c.upper()if upper else c)
                else:letters.append(c)
            mixed=''.join(letters);self.assertNotEqual(mixed,mixed.lower());self.assertNotEqual(mixed,mixed.upper())
            r,b=public_v2_fixture();r['profiles'][2]['evidence']['role_captures'][0]['InputText']=mixed
            with patch.object(v2.hashlib,'sha256',side_effect=AssertionError('DIGEST_BEFORE_PRIVACY')):
                with self.assertRaisesRegex(ValueError,'^V2_CREDENTIAL_OUTPUT$'):v2.report(r,b,secrets=secrets)
        nested=json.dumps({'ErrorMessage':{'items':['IDX012_PART|1|'+parts[0]+'\nIDX012_PART|2|'+parts[1]]}})
        r,b=public_v2_fixture();r['profiles'][2]['evidence']['role_captures'][0]['Stderr']=nested
        with patch.object(v2.hashlib,'sha256',side_effect=AssertionError('DIGEST_BEFORE_PRIVACY')):
            with self.assertRaisesRegex(ValueError,'^V2_UNSUPPORTED_RECEIVED_FRAME$'):v2.report(r,b,secrets=secrets)
        r,b=public_v2_fixture();r['profiles'][2]['evidence']['role_captures'][0]['InputText']="PRINT N'IDX012_PART|1|12345678';"
        self.assertIsNone(v2.privacy(r,secrets))

    def test_public_v2_pure_helper_fixed_names_paths_and_no_foreign_import(self):
        import idx012_public_role_evidence_v2 as v2
        import os
        def normalized(path):
            text=str(path.resolve())
            return Path(text[4:]if text.startswith('\\\\?\\')else text).resolve()
        def full_bytes(path):
            text=str(path.resolve())
            if os.name=='nt'and not text.startswith('\\\\?\\'):text='\\\\?\\'+text
            return Path(text).read_bytes()
        for name in('cost','dml_boundary','lifecycle','storage'):
            actual=Path(v2.pure_helper(name).__file__);expected=v2.FOLDER/(name+'_evidence.py')
            self.assertEqual(normalized(actual),normalized(expected))
            self.assertEqual(full_bytes(actual),full_bytes(expected))
        alias=type('str',(str,),{})
        with patch.object(v2.importlib.util,'spec_from_file_location')as loader:
            for name in(None,True,alias('cost'),'run_profile','../cost','cost.py','cost/../../role_profile'):
                with self.assertRaisesRegex(ValueError,'^V2_FIXED_PURE_HELPER_NAME$'):v2.pure_helper(name)
            with patch.object(v2,'FOLDER',Path('PURE_FOREIGN_FOLDER')):
                with self.assertRaisesRegex(ValueError,'^V2_FIXED_PURE_HELPER_PATH$'):v2.pure_helper('cost')
            with patch.object(Path,'is_symlink',return_value=True):
                with self.assertRaisesRegex(ValueError,'^V2_FIXED_PURE_HELPER_PATH$'):v2.pure_helper('cost')
            loader.assert_not_called()

    def test_public_v2_dml_rollback_source_and_cost_counter_tampering(self):
        def modify(r,b):
            e=r['profiles'][2]['evidence'];rows=[json.loads(l)for l in e['role_captures'][10]['Stdout'].splitlines()]
            next(x for x in rows if x.get('kind')=='DML_BOUNDARY')['RolledBack']=False
            e['role_captures'][10]['Stdout']='\n'.join(json.dumps(x)for x in rows)
        self.rejected(modify)
        self.rejected(lambda r,b:r['profiles'][2]['evidence']['phase_costs'][0]['session_delta'].update(cpu_time=-1))
        self.rejected(lambda r,b:r['profiles'][2]['evidence']['rebuild_source_comparison'].update(other_998_texts_equal=False))


if __name__ == '__main__': unittest.main()
