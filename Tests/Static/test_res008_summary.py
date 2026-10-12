"""Synthetische Mutationen gegen Populations-, Nullwert- und Exportfehler."""
import copy,datetime,importlib.util,json,sys,unittest,uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions'
sys.path.insert(0,str(PUBLIC))
MODULE=PUBLIC/'res008_summary.py'
spec=importlib.util.spec_from_file_location('res008_summary_test',MODULE)
summary=importlib.util.module_from_spec(spec);spec.loader.exec_module(summary)

def fixture():
    evidence={'qualification':'BOUNDED_PROFILE_ONLY','database_id':7,
              'source_config_equal':True,'negative_source_actual':True,
              'negative_query_actual':True,'windows':[],'storage':{},'plans':[]}
    labels=[({'kind':'WARMUP','dimension':d,'ordinal':i},d,1)
            for d in summary.DIMS for i in range(1,6)]
    labels += [({'kind':'MEASURED','pair':pair,'block':block,'order':order,'slot':slot},d,100)
               for pair,block,order,slot,d in summary.measurement.slots()]
    base=datetime.datetime(2026,1,1)
    for n,(label,d,count) in enumerate(labels):
        start=base+datetime.timedelta(milliseconds=n*10)
        elapsed=1000 if d==32 else 2000
        cpu=(99999 if count==1 else (10 if d==32 else 20))
        identity={'SessionId':50+n,'RequestId':0,'RequestStartTime':start.isoformat(),
                  'ConnectionId':str(uuid.UUID(int=n+1)),'DatabaseId':7}
        actual={**identity,'Dimension':d,'Statements':count,'ElapsedUs':elapsed,
                'StartedUtc':start.isoformat(),
                'EndedUtc':(start+datetime.timedelta(microseconds=elapsed)).isoformat(),
                'CpuMs':cpu,'Reads':0,'LogicalReads':20 if d==32 else 40,'Writes':0,
                'Queries':[{'Ordinal':i,'Id':1,'DistanceValue':0.0} for i in range(1,count+1)]}
        actual['CountersBefore']={**identity,'CpuMs':100,'Reads':0,'LogicalReads':100,'Writes':0}
        actual['CountersAfter']={**identity,**{m:actual['CountersBefore'][m]+actual[m]
                                             for m in summary.measurement.COUNTERS}}
        evidence['windows'].append({'labels':label,'actual':actual})
    for d in summary.DIMS:
        evidence['storage'][d]=(100,2,4,9,8+4*d,8+4*d)
        evidence['plans'].append({'dimension':d,'coverage':'REPRESENTATIVE_STATEMENT_ONLY',
            'build':'17.0.5005.3','operators':[
                {'node':'0','physical':'Sort','logical':'Sort','actual_rows':[1],'objects':[]},
                {'node':'1','physical':'Scan','logical':'Scan','actual_rows':[100],
                 'objects':[{'Database':'[SQLPERF_LAB_RES008_LOCAL]','Schema':'[lab]',
                             'Table':'[V'+str(d)+']','Index':None,'IndexKind':None}]}],
            'statement_metrics':{'coverage':'REPRESENTATIVE_STATEMENT_ONLY',
                'numeric_units':'RAW_SHOWPLAN_ATTRIBUTES','degree_of_parallelism':0,
                'non_parallel_reason':'MaxDOPSetToOne',
                'memory_grant':{'state':'CAPTURED','attributes':dict.fromkeys(summary.MEMORY_KEYS,16)},
                'warnings':{'state':'NOT_CAPTURED','element_count':None,'child_tags':None},
                'wait_stats':{'state':'NOT_CAPTURED','entry_count':None}}})
    return evidence

def aggregate(evidence,**kwargs):
    flags=dict(outcome='WARN',code='WARN_OPTIONAL_EVIDENCE_SKIPPED',cleanup_ok=True,client_end_unknown=False)
    flags.update(kwargs)
    return summary.summarize(evidence,**flags)

class SummaryCases(unittest.TestCase):
    def reject(self,edit):
        value=fixture();edit(value)
        with self.assertRaises((ValueError,KeyError,TypeError)):aggregate(value)
    def test_warmups_and_aa_are_excluded_from_comparisons(self):
        value=aggregate(fixture())
        self.assertEqual((value['warmup_requests_excluded'],value['measured_windows'],value['query_oracles']),(20,54,5420))
        for pair in value['pairs']:
            self.assertEqual(pair['baseline']['CpuMs'],{'n':6,'median':10.0,'min':10,'max':10,'zero_count':0})
            self.assertEqual(pair['comparison']['CpuMs']['median'],20)
            self.assertEqual(len(pair['aa_controls']),3)
            self.assertIsNone(pair['median_comparison_over_baseline']['Reads'])
    def test_no_identity_or_text_is_exported(self):
        value=json.dumps(aggregate(fixture()))
        for forbidden in ('SessionId','RequestId','RequestStartTime','ConnectionId','DatabaseId',
                          'SQLPERF_LAB','MaxDOPSetToOne','Queries','StartedUtc','EndedUtc','operators'):
            self.assertNotIn(forbidden,value)
    def test_lifecycle_skip_fail_unknown_or_unclean_cannot_aggregate(self):
        for flags in ({'outcome':'FAIL'},{'outcome':'SKIP'},{'cleanup_ok':False},
                      {'cleanup_ok':1},{'client_end_unknown':True},{'client_end_unknown':0}):
            with self.subTest(flags=flags),self.assertRaises(ValueError):aggregate(fixture(),**flags)
    def test_missing_source_or_query_attestation_is_rejected(self):
        for field in ('source_config_equal','negative_source_actual','negative_query_actual'):
            self.reject(lambda v:v.update({field:1}))
    def test_missing_window_is_rejected(self):self.reject(lambda v:v['windows'].pop())
    def test_swapped_labels_are_rejected(self):
        self.reject(lambda v:v['windows'].__setitem__(slice(20,22),v['windows'][20:22][::-1]))
    def test_boolean_label_alias_is_rejected(self):
        self.reject(lambda v:v['windows'][20]['labels'].update(block=True))
    def test_duplicate_request_is_rejected(self):
        def edit(v):
            a,b=v['windows'][20]['actual'],v['windows'][26]['actual']
            for key in summary.measurement.IDENTITY:
                b[key]=a[key];b['CountersBefore'][key]=a[key];b['CountersAfter'][key]=a[key]
        self.reject(edit)
    def test_overlapping_windows_are_rejected(self):
        def edit(v):
            a,b=v['windows'][20]['actual'],v['windows'][21]['actual']
            b['StartedUtc']=a['StartedUtc'];b['EndedUtc']=(summary.measurement.stamp(b['StartedUtc'])+datetime.timedelta(microseconds=b['ElapsedUs'])).isoformat()
        self.reject(edit)
    def test_bad_counter_or_query_is_rejected(self):
        self.reject(lambda v:v['windows'][20]['actual'].update(CpuMs=11))
        self.reject(lambda v:v['windows'][20]['actual']['Queries'][0].update(Id=2))
    def test_zero_elapsed_with_positive_cpu_is_retained(self):
        value=fixture();actual=value['windows'][20]['actual']
        actual.update(ElapsedUs=0,EndedUtc=actual['StartedUtc'])
        result=aggregate(value)['pairs'][0]['baseline']['ElapsedUs']
        self.assertEqual(result['zero_count'],1);self.assertEqual(result['min'],0)
    def test_outlier_is_retained_in_max(self):
        value=fixture();actual=value['windows'][20]['actual']
        actual['CpuMs']=1000;actual['CountersAfter']['CpuMs']=1100
        result=aggregate(value)['pairs'][0]['baseline']['CpuMs']
        self.assertEqual(result['median'],10);self.assertEqual(result['max'],1000)
    def test_missing_plan_or_foreign_source_is_rejected(self):
        self.reject(lambda v:v['plans'].pop())
        self.reject(lambda v:v['plans'][0]['operators'][1]['objects'][0].update(Table='[V384]'))
    def test_missing_actual_root_or_source_is_rejected(self):
        self.reject(lambda v:v['plans'][0]['operators'][0].update(actual_rows=None))
        self.reject(lambda v:v['plans'][0]['operators'][1].update(actual_rows=[99]))
    def test_raw_zero_dop_and_missing_memory_remain_distinct(self):
        value=fixture();value['plans'][0]['statement_metrics']['memory_grant']={'state':'NOT_CAPTURED','attributes':None}
        result=aggregate(value)['plans'][0]
        self.assertEqual(result['raw_dop'],0);self.assertEqual(result['memory_state'],'NOT_CAPTURED')
        self.assertTrue(all(v is None for v in result['raw_memory_attributes'].values()))
    def test_missing_memory_key_does_not_become_zero(self):
        self.reject(lambda v:v['plans'][0]['statement_metrics']['memory_grant']['attributes'].pop('RequestedMemory'))
    def test_storage_boolean_and_wrong_dimension_are_rejected(self):
        self.reject(lambda v:v['storage'].update({32:(True,2,4,9,136,136)}))
        self.reject(lambda v:v['storage'].update({32:(100,2,4,9,137,137)}))
    def test_json_storage_keys_are_supported(self):
        value=fixture();value['storage']={str(k):list(v) for k,v in value['storage'].items()}
        self.assertEqual(aggregate(value)['storage'][32]['vector_bytes'],136)
    def contracts(self):
        return {d:json.loads((MODULE.parent/'Expected'/('RES008_D'+str(d)+'.result-contract.json')).read_text(encoding='utf-8')) for d in summary.DIMS[1:]}
    def test_all_thirty_fwk_invariants_pass_with_separate_warn(self):
        result=aggregate(fixture());reports=summary.evaluate_invariants(result,self.contracts())
        self.assertEqual(sum(len(r['assertions']) for r in reports),30)
        self.assertTrue(all(r['result']['outcome']=='PASS' for r in reports))
        self.assertEqual(result['outcome'],'WARN')
    def test_actual_fwk_negative_and_metadata_mismatch_fail(self):
        value=aggregate(fixture());value['storage'][384]['rows']=99
        with self.assertRaises(ValueError):summary.evaluate_invariants(value,self.contracts())
        contracts=self.contracts();contracts[384]['profile']='RES008_D768'
        with self.assertRaises(ValueError):summary.evaluate_invariants(aggregate(fixture()),contracts)
    def test_missing_duplicate_or_downgraded_assertion_fails(self):
        for edit in (lambda c:c[384]['assertions'].pop(),
                     lambda c:c[384]['assertions'].__setitem__(0,copy.deepcopy(c[384]['assertions'][1])),
                     lambda c:c[384]['assertions'][0].update(severity='WARN')):
            contracts=self.contracts();edit(contracts)
            with self.assertRaises(ValueError):summary.evaluate_invariants(aggregate(fixture()),contracts)
    def test_assertion_phase_metric_expected_and_type_are_bound(self):
        for edit in ({'phase':'baseline'},{'metric':'query_result_rows'},
                     {'expected':99},{'expected':100.0},{'expected':True}):
            contracts=self.contracts()
            next(a for a in contracts[384]['assertions'] if a['id']=='comparison_source_rows').update(edit)
            with self.subTest(edit=edit),self.assertRaises(ValueError):
                summary.evaluate_invariants(aggregate(fixture()),contracts)
    def test_controller_entry_reads_only_three_own_contracts(self):
        result=SimpleNamespace(evidence=fixture(),outcome='WARN',code='WARN_OPTIONAL_EVIDENCE_SKIPPED',cleanup_ok=True,client_end_unknown=False)
        contracts=self.contracts();seen=[]
        def read(path):
            seen.append(path)
            d=int(path.name.split('.')[0].removeprefix('RES008_D'))
            return json.dumps(contracts[d]).encode('utf-8')
        with patch.object(Path,'read_bytes',read):value=summary.summarize_result(result)
        self.assertEqual(len(seen),3)
        self.assertTrue(all(p.parent==PUBLIC/'Expected' for p in seen))
        self.assertEqual(value['outcome'],'WARN');self.assertEqual(len(value['fwk011']),3)
    def test_failed_controller_does_not_read_contracts(self):
        result=SimpleNamespace(evidence=fixture(),outcome='FAIL',code='FAIL_EXECUTION',cleanup_ok=True,client_end_unknown=False)
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected read')),self.assertRaises(ValueError):
            summary.summarize_result(result)
    def test_oversized_own_contract_is_rejected(self):
        result=SimpleNamespace(evidence=fixture(),outcome='WARN',code='WARN_OPTIONAL_EVIDENCE_SKIPPED',cleanup_ok=True,client_end_unknown=False)
        with patch.object(Path,'read_bytes',return_value=b' '*10001),self.assertRaises(ValueError):
            summary.summarize_result(result)

if __name__=='__main__':unittest.main()
