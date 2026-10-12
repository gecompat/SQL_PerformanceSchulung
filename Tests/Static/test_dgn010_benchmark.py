"""Synthetische vollständige Recordgegenfälle; keine SQL-/Runtimequalifikation."""
import copy,datetime,json,unittest
from pathlib import Path
import dgn010_benchmark_evidence as b,dgn010_window_evidence as w

def native_window(scope,path,label,count,serial):
    start=datetime.datetime(2026,10,12)+datetime.timedelta(seconds=serial)
    identity={'SessionId':60+serial,'RequestId':0,'RequestStartTime':start.isoformat(),'ConnectionId':f'00000000-0000-0000-0000-{serial+1:012x}','DatabaseId':5}
    before={**identity,'CpuMs':0,'Reads':0,'LogicalReads':0,'Writes':0}
    after={**identity,'CpuMs':0,'Reads':0,'LogicalReads':3+path,'Writes':0}
    result={**identity,'Path':path,'Label':label,'Statements':count,'CpuMs':0,'Reads':0,'LogicalReads':3+path,'Writes':0,
            'ElapsedUs':0,'StartedUtc':start.isoformat(),'EndedUtc':start.isoformat(),'CountersBefore':before,'CountersAfter':after,
            'Queries':[{'Ordinal':i,'Rows':10,'FirstId':101,'LastId':110,'Digest':w.query_digest(scope,i)} for i in range(1,count+1)]}
    if scope=='DML':result.update(TransactionBefore=0,TransactionAfter=0)
    return result

def fixture(scope='SELECT'):
    records=[];serial=1
    for path in (0,1):
        for ordinal in range(5):
            label=f'WARMUP_{path}_{ordinal}'
            records.append({'kind':'WARMUP','path':path,'label':label,'data':native_window(scope,path,label,1,serial)});serial+=1
    for block,order,slot,path in w.slots():
        label=f'{order}_{block}_{slot}_{path}'
        records.append({'kind':'MEASURED','path':path,'label':label,'block':block,'order':order,'slot':slot,'data':native_window(scope,path,label,100,serial)});serial+=1
    source=[[i,i*3,100,b.SOURCE_DIGEST] for i in range(1,1001)]
    snapshots=[[copy.deepcopy(source),{'DGN010_OwnPK':[1000,18,25],**({'DGN010_OwnCandidate':[1000,17,25]} if p else {})}] for p in b.source_states()]
    return {'database_id':5,'records':records,'query_control':native_window(scope,0,'CONTROL_0',1,0),'source_snapshots':snapshots,
            'candidate_transitions':[1,0,1,0,1,0,1,0],**{k:True for k in b.FLAGS},'coverage':b.SCOPES[scope]}

def evaluate(record,scope='SELECT',database=5):return b.validate_benchmark(record,scope=scope,expected_database_id=database)
def contract(scope):return json.loads((Path(__file__).resolve().parent/'Fixtures/dgn010'/f'DGN010_{scope}.result-contract.json').read_text(encoding='utf-8'))
class BenchmarkTests(unittest.TestCase):
    def test_complete_both_scopes_numeric_pass_still_runtime_unknown(self):
        for scope in ('SELECT','DML'):
            a=evaluate(fixture(scope),scope);self.assertEqual(a['counts'],b.INVARIANTS)
            self.assertEqual((a['runtime_qualification'],a['tp_perf']),('NOT_ESTABLISHED','NOT_ESTABLISHED'))
            report=b.evaluate_invariants(a,contract(scope));self.assertEqual(report['result']['outcome'],'PASS');self.assertEqual(len(report['assertions']),12)
    def test_source_every_row_and_payload_byte_contract(self):
        for index,field,value in [(0,0,True),(999,0,999),(500,1,0),(200,2,99),(100,3,'0'*64)]:
            r=fixture();r['source_snapshots'][20][0][index][field]=value
            with self.subTest(index=index,field=field),self.assertRaises(ValueError):evaluate(r)
    def test_source_truncation_duplicate_and_missing_snapshot(self):
        for mutation in (lambda r:r['source_snapshots'].pop(),lambda r:r['source_snapshots'][0][0].pop(),lambda r:r['source_snapshots'][0][0].append(r['source_snapshots'][0][0][0])):
            r=fixture();mutation(r)
            with self.assertRaises(ValueError):evaluate(r)
    def test_index_foreign_state_and_missing_actual_pages(self):
        for state in ({'DGN010_OwnPK':[1000,18,25],'Foreign':[1000,1,1]}, {'DGN010_OwnPK':[1000,18,25],'DGN010_OwnCandidate':[1000,17,25]}, {'DGN010_OwnPK':[1000,0,0]}, {'DGN010_OwnPK':[True,18,25]}, {'DGN010_OwnPK':[1000,18,9223372036854775808]}):
            r=fixture();r['source_snapshots'][0][1]=state
            with self.subTest(state=state),self.assertRaises(ValueError):evaluate(r)
    def test_state_transitions_are_typed_and_complete(self):
        for states in ([True,0,1,0,1,0,1,0],[1,0],[],[1,0,1,0,1,0,1,1]):
            r=fixture();r['candidate_transitions']=states
            with self.subTest(states=states),self.assertRaises(ValueError):evaluate(r)
    def test_independent_database_binding(self):
        for database in (6,True,5.0):
            with self.subTest(database=database),self.assertRaises(ValueError):evaluate(fixture(),database=database)
    def test_flags_must_be_actual_true_and_full_schema(self):
        for key in b.FLAGS:
            for value in (False,1,None):
                r=fixture();r[key]=value
                with self.subTest(key=key,value=value),self.assertRaises(ValueError):evaluate(r)
        for key in b.RECORD_KEYS:
            r=fixture();del r[key]
            with self.subTest(missing=key),self.assertRaises(ValueError):evaluate(r)
    def test_complete_population_reorder_and_warmup_cannot_be_measured(self):
        for mutation in (lambda r:r['records'].pop(),lambda r:r['records'].append(r['records'][0]),lambda r:r['records'].__setitem__(slice(10,12),list(reversed(r['records'][10:12]))),lambda r:r['records'][0].update(kind='MEASURED')):
            r=fixture();mutation(r)
            with self.assertRaises(ValueError):evaluate(r)
    def test_query_oracle_every_ordinal_and_rows(self):
        for key,value in [('Ordinal',2),('Rows',9),('Rows',True),('FirstId',100),('Digest','0'*64)]:
            r=fixture();r['records'][10]['data']['Queries'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):evaluate(r)
    def test_dml_values_must_increment_each_ordinal(self):
        r=fixture('DML');r['records'][10]['data']['Queries'][99]['Digest']=w.query_digest('DML',1)
        with self.assertRaises(ValueError):evaluate(r,'DML')
        r=fixture('DML');r['records'][10]['data']['Queries'][0]['Digest']=w.query_digest('SELECT',1)
        with self.assertRaises(ValueError):evaluate(r,'DML')
    def test_dml_rollback_depth_and_scope_schema(self):
        for key,value in [('TransactionBefore',1),('TransactionAfter',True),('TransactionAfter',0.0)]:
            r=fixture('DML');r['records'][10]['data'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):evaluate(r,'DML')
        with self.assertRaises(ValueError):evaluate(fixture('DML'),'SELECT')
    def test_counter_identity_delta_and_missing_values(self):
        for key,value in [('SessionId',999),('ConnectionId','bad'),('DatabaseId',6),('LogicalReads',99),('CpuMs',True)]:
            r=fixture();r['records'][10]['data']['CountersAfter'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):evaluate(r)
        r=fixture();del r['records'][10]['data']['CountersBefore']['Writes']
        with self.assertRaises(ValueError):evaluate(r)
    def test_unique_requests_and_actual_time_sequence(self):
        r=fixture();first=r['records'][10]['data'];second=r['records'][11]['data']
        for key in w.IDENTITY:
            second[key]=first[key]
            for field in ('CountersBefore','CountersAfter'):second[field][key]=first[key]
        with self.assertRaises(ValueError):evaluate(r)
        r=fixture();r['records'][10]['data']['StartedUtc']='2026-10-11T00:00:00';r['records'][10]['data']['EndedUtc']='2026-10-11T00:00:00'
        with self.assertRaises(ValueError):evaluate(r)
    def test_aa_and_warmups_are_excluded_and_outliers_retained(self):
        r=fixture()
        for item in r['records']:
            if item['kind']=='WARMUP' or item.get('order')=='AA':
                item['data']['CpuMs']=999;item['data']['CountersAfter']['CpuMs']=999
        r['records'][10]['data']['CpuMs']=51;r['records'][10]['data']['CountersAfter']['CpuMs']=51
        a=evaluate(r);self.assertEqual(a['baseline']['CpuMs']['samples'],[51,0,0,0,0,0]);self.assertEqual(a['baseline']['CpuMs']['median_exact'],'0')
        self.assertEqual(a['aa_controls'][0]['first']['CpuMs'],999)
    def test_zero_elapsed_is_not_missing_work(self):
        a=evaluate(fixture());self.assertEqual(a['baseline']['ElapsedUs']['zero_count'],6);self.assertGreater(a['baseline']['LogicalReads']['min'],0)
    def test_large_valid_counters_keep_exact_median_and_samples(self):
        r=fixture()
        for item in r['records'][10:]:
            if item['order']!='AA' and item['path']==0:
                value=9223372036854775806+item['slot']%2
                item['data']['CpuMs']=value;item['data']['CountersAfter']['CpuMs']=value
        a=evaluate(r);self.assertEqual(a['baseline']['CpuMs']['median_exact'],'9223372036854775806.5');self.assertEqual(a['baseline']['CpuMs']['max'],9223372036854775807)
    def test_no_request_identity_or_source_rows_leak_to_aggregate(self):
        text=json.dumps(evaluate(fixture()));self.assertNotIn('ConnectionId',text);self.assertNotIn('SourceRows',text);self.assertNotIn('StartedUtc',text);self.assertNotIn(b.SOURCE_DIGEST,text)
    def test_contract_metadata_and_severity_cannot_change(self):
        a=evaluate(fixture())
        for key,value in [('demo_id','RES-008'),('profile','DGN010_DML'),('contract_version','9')]:
            c=contract('SELECT');c[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):b.evaluate_invariants(a,c)
        for key,value in [('severity','WARN'),('on_missing','SKIP'),('expected',True),('expected',1000.0),('metric','other'),('phase','comparison')]:
            c=contract('SELECT');c['assertions'][0][key]=value
            with self.subTest(assertion=key),self.assertRaises(ValueError):b.evaluate_invariants(a,c)
    def test_contract_alias_duplicate_missing_and_extra_fields(self):
        a=evaluate(fixture())
        for mutation in (lambda c:c['assertions'].pop(),lambda c:c['assertions'].__setitem__(1,c['assertions'][0]),lambda c:c['assertions'][0].update(extra=1)):
            c=contract('SELECT');mutation(c)
            with self.assertRaises(ValueError):b.evaluate_invariants(a,c)
    def test_transport_prefix_truncation_and_duplicate_nested_json(self):
        r=native_window('SELECT',0,'CONTROL_0',1,0);raw=json.dumps(r);parts=(len(raw)+199)//200
        output='\n'.join(f'DGN010_SELECTPART|{i+1}|{parts}|{len(raw)}|{raw[i*200:(i+1)*200]}' for i in range(parts))+'\nSQLPERF_SUMMARY|PASS|OK'
        self.assertEqual(w.decode(output,'SELECT'),r)
        for text in (output[:-1],output.replace('DGN010_SELECTPART|','DGN010_DMLPART|'),output+'\nSQLPERF_SUMMARY|PASS|OK'):
            with self.assertRaises(ValueError):w.decode(text,'SELECT')
        with self.assertRaises(ValueError):w.unique([('a',1),('a',2)])
if __name__=='__main__':unittest.main()
