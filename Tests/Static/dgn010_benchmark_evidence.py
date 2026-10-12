"""Begrenzte DGN-010-Recordauswertung; kein SQL und keine Runtimeattestation."""
import hashlib,importlib.util,json,sys
from decimal import Decimal
from pathlib import Path
import dgn010_window_evidence as window

METRICS=(*window.COUNTERS,'ElapsedUs')
SCOPES={'SELECT':'INDEX_ABSENT_PRESENT_UNFORCED_READER_BATCHES_WITH_BUFFER_AND_IMPERSONATION_OVERHEAD',
        'DML':'INDEX_ABSENT_PRESENT_OWNER_UPDATE_BATCHES_WITH_OUTPUT_AND_ROLLBACK_OVERHEAD'}
RECORD_KEYS={'database_id','records','query_control','source_snapshots','candidate_transitions','source_negative_51003','query_negative_51003','source_config_equal','reader_rights_unchanged','coverage'}
FLAGS=('source_negative_51003','query_negative_51003','source_config_equal','reader_rights_unchanged')
SOURCE_DIGEST=hashlib.sha256(b'F'*100).hexdigest().upper()
INVARIANTS={'source_rows':1000,'source_snapshots':46,'warmup_windows':10,'measured_windows':18,
            'baseline_windows':6,'comparison_windows':6,'aa_pairs':3,'statements_per_window':100,
            'statement_oracles':1810,'full_row_controls':18100,'positive_control_statements':1,'actual_negative_controls':2}
PHASE_METRICS={'source_rows':1000,'measured_windows':6,'statement_oracles':600,
               'full_row_controls':6000,'rows_per_statement':10,'statements_per_window':100}
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('dgn010_fwk011',ROOT/'Demos/00_Framework/Tools/evaluate_result_contract.py')
fwk=importlib.util.module_from_spec(spec);sys.modules[spec.name]=fwk;spec.loader.exec_module(fwk)

def source_states():
    return [0]*7+[1]*2+[p for b,o,s,p in window.slots() for _ in (0,1)]+[0]

def validate_source(snapshot,path):
    if type(snapshot) not in (list,tuple) or len(snapshot)!=2:raise ValueError('Full source snapshot required')
    rows,indexes=snapshot
    if type(rows) is not list or len(rows)!=1000 or type(indexes) is not dict:raise ValueError('Full source population required')
    for expected,row in enumerate(rows,1):
        if type(row) not in (list,tuple) or len(row)!=4 or any(type(row[i]) is not int or row[i]!=v for i,v in enumerate((expected,expected*3,100))) or type(row[3]) is not str or row[3]!=SOURCE_DIGEST:raise ValueError('Full ordered source bytes/values differ')
    names={'DGN010_OwnPK'}|({'DGN010_OwnCandidate'} if path else set())
    if set(indexes)!=names:raise ValueError('Actual own index state differs')
    for values in indexes.values():
        if type(values) not in (list,tuple) or len(values)!=3 or any(type(v) is not int for v in values) or values[0]!=1000 or not 0<values[1]<=values[2]:raise ValueError('Actual bounded rows/pages differ')
        window.integer(values[1],1);window.integer(values[2],1)

def distribution(records):
    result={}
    for metric in METRICS:
        values=[r[metric] for r in records];ordered=sorted(values);size=len(values)
        median=Decimal(ordered[size//2]) if size%2 else Decimal(ordered[size//2-1]+ordered[size//2])/Decimal(2)
        result[metric]={'n':size,'median_exact':str(median),'min':min(values),'max':max(values),'samples':values,'zero_count':sum(v==0 for v in values)}
    return result

def validate_benchmark(record,*,scope,expected_database_id):
    window.scope_prefix(scope);window.integer(expected_database_id,5)
    if type(record) is not dict or set(record)!=RECORD_KEYS or type(record['database_id']) is not int or record['database_id']!=expected_database_id:raise ValueError('Full fixed record/independent DB binding required')
    if record['coverage']!=SCOPES[scope] or any(record[k] is not True for k in FLAGS):raise ValueError('Complete bounded controller attestations required')
    sources=record['source_snapshots']
    if type(sources) is not list or len(sources)!=46:raise ValueError('Exactly 46 full source snapshots required')
    for snapshot,path in zip(sources,source_states()):validate_source(snapshot,path)
    transitions=record['candidate_transitions']
    if type(transitions) is not list or any(type(p) is not int for p in transitions) or transitions!=[1,0,1,0,1,0,1,0]:raise ValueError('Four actual build/drop pairs required')
    records=record['records']
    if type(records) is not list or len(records)!=28:raise ValueError('Full warmup/measurement population required')
    keys=set();previous=None
    def check(data,path,label,count):
        nonlocal previous
        key=window.validate(data,path,label,count,expected_database_id,scope)
        if key in keys or (previous is not None and window.stamp(data['StartedUtc'])<previous):raise ValueError('Unique actual serial request windows required')
        keys.add(key);previous=window.stamp(data['EndedUtc'])
    check(record['query_control'],0,'CONTROL_0',1)
    for item,(path,ordinal) in zip(records[:10],[(p,i) for p in (0,1) for i in range(5)]):
        label=f'WARMUP_{path}_{ordinal}'
        if type(item) is not dict or set(item)!={'kind','path','label','data'} or item['kind']!='WARMUP' or type(item['path']) is not int or item['path']!=path or item['label']!=label:raise ValueError('Fixed five warmups per state required')
        check(item['data'],path,label,1)
    for item,(block,order,slot,path) in zip(records[10:],window.slots()):
        label=f'{order}_{block}_{slot}_{path}'
        if type(item) is not dict or set(item)!={'kind','path','label','data','block','order','slot'} or item['kind']!='MEASURED' or any(type(item[k]) is not int or item[k]!=v for k,v in (('block',block),('slot',slot),('path',path))) or item['order']!=order or item['label']!=label:raise ValueError('Fixed complete AB/BA/AA order required')
        check(item['data'],path,label,100)
    measured=records[10:]
    baseline=[r['data'] for r in measured if r['order']!='AA' and r['path']==0]
    comparison=[r['data'] for r in measured if r['order']!='AA' and r['path']==1]
    if not any(r['LogicalReads']>0 for r in baseline) or not any(r['LogicalReads']>0 for r in comparison):raise ValueError('Active measured populations required')
    aa=[{'block':b,'first':{k:next(r['data'][k] for r in measured if r['order']=='AA' and r['block']==b and r['slot']==1) for k in METRICS},
         'second':{k:next(r['data'][k] for r in measured if r['order']=='AA' and r['block']==b and r['slot']==2) for k in METRICS}} for b in (1,2,3)]
    counts={'source_rows':len(sources[0][0]),'source_snapshots':len(sources),'warmup_windows':10,'measured_windows':len(measured),
            'baseline_windows':len(baseline),'comparison_windows':len(comparison),'aa_pairs':len(aa),'statements_per_window':measured[0]['data']['Statements'],
            'statement_oracles':sum(r['data']['Statements'] for r in records),'full_row_controls':sum(q['Rows'] for r in records for q in r['data']['Queries']),
            'positive_control_statements':record['query_control']['Statements'],'actual_negative_controls':sum(record[k] is True for k in FLAGS[:2])}
    if counts!=INVARIANTS:raise ValueError('Complete numeric invariants differ')
    return {'demo_id':'DGN-010','scope':scope,'record_validation':'PASS','counts':counts,
            'baseline':distribution(baseline),'comparison':distribution(comparison),'aa_controls':aa,
            'runtime_qualification':'NOT_ESTABLISHED','tp_perf':'NOT_ESTABLISHED','current_index_usage':'NOT_CAPTURED',
            'complete_worker_io':'NOT_ESTABLISHED','statistical_significance':'NOT_ESTABLISHED','tail_percentiles':'N/A_SMALL_BATCH_SAMPLE'}

def evaluate_invariants(aggregate,contract):
    scope=aggregate['scope'];window.scope_prefix(scope)
    if type(contract) is not dict or set(contract)!={'contract_version','demo_id','profile','assertions'} or contract['contract_version']!='1.0' or contract['demo_id']!='DGN-010' or contract['profile']!='DGN010_'+scope:raise ValueError('Exact own scope contract required')
    canonical={phase+'_'+metric:(phase,metric,value) for phase in ('baseline','comparison') for metric,value in PHASE_METRICS.items()}
    assertions=contract['assertions']
    if type(assertions) is not list or len(assertions)!=12:raise ValueError('Twelve numeric invariants required')
    seen=set();results=[]
    evidence={'contract_version':'1.0','demo_id':'DGN-010','profile':'DGN010_'+scope}
    for phase in ('baseline','comparison'):
        n=aggregate[phase]['CpuMs']['n'];count=aggregate['counts']['statements_per_window']
        evidence[phase]={'source_rows':aggregate['counts']['source_rows'],'measured_windows':n,
                         'statement_oracles':n*count,'full_row_controls':n*count*10,
                         'rows_per_statement':10,'statements_per_window':count}
    for assertion in assertions:
        if type(assertion) is not dict or set(assertion)!={'id','kind','phase','metric','expected','severity','on_missing'}:raise ValueError('Exact assertion schema required')
        key=assertion['id']
        if type(key) is not str or key not in canonical or key in seen or assertion['kind']!='EXACT' or assertion['severity']!='FAIL' or assertion['on_missing']!='FAIL' or type(assertion['expected']) is not int or (assertion['phase'],assertion['metric'],assertion['expected'])!=canonical[key]:raise ValueError('Complete phase/metric/expected/severity binding required')
        seen.add(key);results.append(fwk.evaluate_assertion(assertion,evidence))
    demo,profile=fwk.validate_metadata(contract,evidence);report=fwk.summarize(results,demo,profile)
    if report['outcome']!='PASS':raise ValueError('Numeric invariant failure')
    return {'evidence':evidence,'result':report,'assertions':[r.as_dict(i) for i,r in enumerate(results,1)]}
