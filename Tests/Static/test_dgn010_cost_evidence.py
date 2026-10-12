"""Synthetische öffentliche Kostenrecords, keine Runtime oder Privatinhalte."""
import copy,hashlib,json,unittest
import dgn010_cost_evidence as c

def lease():
    index={'object_id':100,'index_id':2,'name':c.CANDIDATE,'type':2,'is_unique':False,'is_primary_key':False,'is_disabled':False,'has_filter':False,'filter_definition':None}
    cols=[{'object_id':100,'index_id':2,'index_column_id':n,'column_id':n,'key_ordinal':1 if n==1 else 0,'is_descending_key':False,'is_included_column':n!=1} for n in (1,2,3)]
    return json.dumps({'indexes':[index],'columns':cols},separators=(',',':'))

def state(present,second):
    defaults={'str':'LAB','int':0,'bool':False,'NoneType':None}
    data={name:[{field:defaults[type_name] for field,type_name in c.STATE_TYPES[name].items()} for _ in range(count)] for name,count in c.STATE_POPULATIONS.items() if count}
    data.update(roles=[],rows=[{'Id':n,'Value':n*3,'Payload':'F'*100,'payload_bytes':100} for n in range(1,1001)])
    data['db']=[{'database_id':7,'name':'SQLPERF_LAB_DGN010_LOCAL','compatibility_level':170,'recovery_model_desc':'SIMPLE','is_auto_close_on':False,'is_auto_shrink_on':False,'is_read_only':False,'state_desc':'ONLINE'}]
    for n,row in enumerate(data['config'],1):row.update(configuration_id=n,name=f'LAB_CFG_{n}',value_hex='00',secondary_hex=None)
    for row in data['columns']:row.update(default_object_id=0)
    data['schemas'][0]['name']='lab';data['reader'][0].update(name='DGN010_reader',sid='00')
    data['objects']=[{'object_id':100,'schema_id':2,'name':'SourceRows','type':'U','create_date':'2026-10-12T10:00:00.000','modify_date':f'2026-10-12T10:00:0{second}.000'},
        {'object_id':200,'schema_id':2,'name':c.PK,'type':'PK','create_date':'2026-10-12T10:00:00.000','modify_date':'2026-10-12T10:00:00.000'}]
    pk={'object_id':100,'index_id':1,'name':c.PK,'type':1,'is_unique':True,'is_primary_key':True,'is_disabled':False,'has_filter':False,'filter_definition':None}
    pkcol={'object_id':100,'index_id':1,'index_column_id':1,'column_id':1,'key_ordinal':1,'is_descending_key':False,'is_included_column':False}
    own=json.loads(lease()) if present else {'indexes':[],'columns':[]}
    data['indexes']=[pk]+own['indexes'];data['index_columns']=[pkcol]+own['columns']
    data['properties']=[]
    for name,value in {'SQLPERF.Project':'SQL_PerformanceSchulung','SQLPERF.ContractVersion':'1.0','SQLPERF.DemoId':'DGN-010','SQLPERF.RunToken':'LOCAL'}.items():
        a,b=name.encode('utf-16-le'),value.encode('utf-16-le')
        data['properties'].append({'class':0,'major_id':0,'minor_id':0,'name_bytes':len(a),'name_hex':a.hex().upper(),'value_bytes':len(b),'value_hex':b.hex().upper(),'base_type':'nvarchar'})
    return data

def fixture():
    records=[];states=[]
    for n,kind in enumerate(('CREATE','DROP','CREATE','DROP')):
        identity={'SessionId':51,'RequestId':0,'RequestStartTime':'2026-10-12T10:00:00.123','ConnectionId':f'00000000-0000-0000-0000-{n+1:012}','DatabaseId':7}
        before,after=(c.EMPTY,lease()) if kind=='CREATE' else (lease(),c.EMPTY)
        counter=identity|dict.fromkeys(c.window.COUNTERS,0)
        records.append(identity|{'Kind':kind,'Cycle':n//2+1,'DdlSha256':hashlib.sha256(c.DDL[kind].encode('utf-16-le')).hexdigest().upper(),
            'StartedUtc':f'2026-10-12T10:00:0{n}.1234567','EndedUtc':f'2026-10-12T10:00:0{n}.1234577','ElapsedUs':1,
            'CountersBefore':counter.copy(),'CountersAfter':counter.copy(),'LeaseBefore':before,'LeaseAfter':after}|dict.fromkeys(c.window.COUNTERS,0))
        states.append([state(kind=='DROP',n),state(kind=='CREATE',n+1)])
    rows=[[n,n*3,100,c.benchmark.SOURCE_DIGEST] for n in range(1,1001)]
    snapshots=[[copy.deepcopy(rows),{c.PK:[1000,18,33],**({c.CANDIDATE:[1000,17,33]} if path else {})}] for path in (0,0,0,0,1,0,1,0)]
    return {'database_id':7,'object_id':100,'preflight':'SQLPERF_SUMMARY|PASS|OK','records':records,'source_snapshots':snapshots,'full_states':states,'negative_states':[state(False,0),state(False,0)],
        'source_negative_51003':True,'drop_absent_negative_51003':True,'scope':'TWO_OWN_CREATE_DROP_CYCLES_ONLY','runtime_qualification':'NOT_ESTABLISHED','full_worker_costs':'NOT_ESTABLISHED','index_net_benefit':'NOT_ESTABLISHED'}

class CostRecordTests(unittest.TestCase):
    def rejects(self,changes):
        for change in changes:
            with self.subTest(change=change):
                data=fixture();change(data)
                with self.assertRaises((ValueError,KeyError,TypeError)):c.report(data,expected_database_id=7)
    def test_complete_record_and_honest_claims(self):
        output=c.report(fixture(),expected_database_id=7)
        self.assertEqual((output['ddl_windows'],output['source_rows'],output['full_state_rows']),(4,8000,10000))
        self.assertEqual(output['operations']['CREATE']['Writes']['zero_count'],2)
        for key in ('runtime_qualification','tp_perf','full_worker_costs','index_net_benefit','whole_database_or_file_size'):self.assertEqual(output[key],'NOT_ESTABLISHED')
        self.assertEqual(output['provenance'],'CALLER_ATTESTATION_REQUIRED')
        self.assertNotIn('ConnectionId',json.dumps(output));self.assertNotIn('SQLPERF.Project',json.dumps(output));self.assertNotIn('Payload',json.dumps(output))
    def test_exact_large_integer_median(self):
        data=fixture()
        for n,value in ((0,9007199254740992),(2,9007199254740993)):
            data['records'][n]['CpuMs']=value;data['records'][n]['CountersAfter']['CpuMs']=value
        self.assertEqual(c.report(data,expected_database_id=7)['operations']['CREATE']['CpuMs']['median_exact'],'9007199254740992.5')
    def test_missing_population_or_scope(self):
        self.rejects([lambda d:d['records'].pop(),lambda d:d['source_snapshots'].pop(),lambda d:d['full_states'].pop(),lambda d:d['negative_states'].pop(),lambda d:d.update(scope='FOREIGN'),lambda d:d.update(Extra=0)])
    def test_identity_counter_alias_and_source_digest(self):
        self.rejects([lambda d:d['records'][0].update(SessionId=True),lambda d:d['records'][0]['CountersAfter'].update(DatabaseId=8),lambda d:d['records'][0].update(CpuMs=1),lambda d:d['records'][0].update(DdlSha256='0'*64),lambda d:d['records'][0].update(Cycle=True)])
    def test_native_lease_and_order(self):
        self.rejects([lambda d:d['records'][1].update(LeaseBefore=c.EMPTY),lambda d:d['records'].reverse(),lambda d:d['records'][2].update(ConnectionId=d['records'][0]['ConnectionId']),lambda d:d['records'][2].update(StartedUtc=d['records'][0]['StartedUtc'])])
    def test_source_bytes_and_states(self):
        self.rejects([lambda d:d['source_snapshots'][0][0][0].__setitem__(1,0),lambda d:d['full_states'][0][0]['rows'][0].update(Payload='X'*100),lambda d:d['full_states'][0][1]['files'][0].update(size=1),lambda d:d['full_states'][1][0]['config'][0].update(value_hex='FF')])
    def test_complete_metadata_and_scalar_types(self):
        self.rejects([lambda d:d['full_states'][0][0]['config'].pop(),lambda d:d['full_states'][0][0]['files'][0].pop('guid'),lambda d:d['full_states'][0][0]['files'][0].update(is_read_only=0),lambda d:d['full_states'][0][0]['config'][0].update(configuration_id=True)])
    def test_negative_state_and_native_flags(self):
        self.rejects([lambda d:d['negative_states'][1]['rows'][0].update(Value=0),lambda d:d.update(source_negative_51003=1),lambda d:d.update(runtime_qualification='PASS'),lambda d:d.update(full_worker_costs='PASS')])
    def test_marker_bytes_and_original_pk(self):
        self.rejects([lambda d:d['full_states'][0][0]['properties'][0].update(value_hex='00'),lambda d:d['full_states'][0][0]['properties'][0].update(name_hex='00'),lambda d:d['full_states'][0][0]['indexes'][0].update(name='FOREIGN')])
    def test_allocations_and_absence(self):
        self.rejects([lambda d:d['source_snapshots'][4][1].pop(c.CANDIDATE),lambda d:d['source_snapshots'][4][1].update(FOREIGN=[1000,1,1]),lambda d:d['source_snapshots'][4][1][c.CANDIDATE].__setitem__(2,0),lambda d:d['source_snapshots'][5][1][c.PK].__setitem__(1,19)])
    def test_foreign_and_truncated_transport(self):
        for output in ('DGN010_SELECTPART|1|1|2|{}\nSQLPERF_SUMMARY|PASS|OK','DGN010_BUILDPART|1|2|300|{}\nSQLPERF_SUMMARY|PASS|OK'):
            with self.assertRaises(ValueError):c.decode(output)
    def test_independent_database_argument(self):
        for actual in (True,8):
            with self.assertRaises(ValueError):c.report(fixture(),expected_database_id=actual)

    def test_full_seventh_digit_interval_and_serial_boundary(self):
        data=fixture();row=data['records'][0]
        row.update(StartedUtc='2026-10-12T10:00:00.1234569',EndedUtc='2026-10-12T10:00:00.1234561',ElapsedUs=0)
        with self.assertRaises(ValueError):c.report(data,expected_database_id=7)
        row.update(StartedUtc='2026-10-12T10:00:00.1234561',EndedUtc='2026-10-12T10:00:00.1234569')
        self.assertEqual(c.report(data,expected_database_id=7)['record_validation'],'PASS')
        data['records'][1].update(StartedUtc='2026-10-12T10:00:00.1234568',EndedUtc='2026-10-12T10:00:00.1234578')
        with self.assertRaises(ValueError):c.report(data,expected_database_id=7)

    def test_consistently_wrong_nullable_scalar_type(self):
        for field,item in (('value_collation',False),('secondary_type',1),('secondary_precision',True)):
            data=fixture()
            for state in data['negative_states']+[s for pair in data['full_states'] for s in pair]:state['config'][0][field]=item
            with self.subTest(field=field),self.assertRaises(ValueError):c.report(data,expected_database_id=7)

    def test_full_state_continuity_including_modify_date(self):
        data=fixture()
        for state in data['full_states'][1]:state['objects'][0]['modify_date']='2026-10-12T10:00:00.000'
        with self.assertRaises(ValueError):c.report(data,expected_database_id=7)
        data=fixture();data['full_states'][0][0]['objects'][0]['modify_date']='2026-10-12T10:00:00.001'
        with self.assertRaises(ValueError):c.report(data,expected_database_id=7)

if __name__=='__main__':unittest.main()
