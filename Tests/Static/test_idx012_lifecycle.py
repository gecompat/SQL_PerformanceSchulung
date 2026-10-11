import copy
import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Demos/09_AI_SQL_Server_2025/IDX-012_Vector_Index_DML_Maintenance"))
from lifecycle_evidence import validate_lifecycle
TOKEN='ABCDEF0123456789'
BEFORE={i:i/2000 for i in range(1,1000)}
AFTER={**BEFORE,999:0}
META=[{'object_id':100,'index_id':1,'name':'IDX012_OwnVector','type':8,'type_desc':'VECTOR',
       'is_disabled':False,'is_hypothetical':False,'vector_index_type':'DiskANN','distance_metric':'COSINE'}]


def fixture():
    rows=[{'kind':'LIFECYCLE_CHANGE','DatabaseId':5,'RunToken':TOKEN,'AffectedRows':1,'RowCount':999,
           'TransactionCount':0,'TransactionState':0,'IndexCount':0,'Committed':True,
           'OtherSourceUnchanged':True,'NewVector':'[1,0,0]'},
          {'kind':'LIFECYCLE_REBUILD','DatabaseId':5,'RunToken':TOKEN,'BuildElapsedUs':10,
           'BeforeMetadata':copy.deepcopy(META),'AfterMetadata':copy.deepcopy(META)}]
    for ordinal,(stage,path) in enumerate([('BASELINE','EXACT'),('BASELINE','ANN'),('AFTER_CHANGE','EXACT'),
                                           ('REBUILT','EXACT'),('REBUILT','ANN')],1):
        source=BEFORE if stage=='BASELINE' else AFTER
        ids=sorted(source,key=lambda i:(source[i],i))[:5]
        rows.append({'kind':'LIFECYCLE_QUERY','DatabaseId':5,'RunToken':TOKEN,'Ordinal':ordinal,
                     'Stage':stage,'Path':path,'rows':[{'Id':i,'DistanceValue':source[i]} for i in ids]})
    return [{"kind":"LIFECYCLE_DROP","DatabaseId":5,"RunToken":TOKEN,"IndexCount":0,"RowCount":999,"TransactionCount":0,"TransactionState":0},*rows]


def run(rows,before=BEFORE,after=AFTER):
    return validate_lifecycle(rows,token=TOKEN,database_id=5,before_distances=before,
                              after_distances=after,before_metadata=META)


class Lifecycle(unittest.TestCase):
    def test_complete_result_keeps_narrow_freshness_and_unknown_generation(self):
        result=run(fixture())
        self.assertEqual(result['freshness'],'OBSERVED_AFTER_REBUILD_ONLY')
        self.assertEqual(result['generation'],'UNKNOWN')
        self.assertEqual(result['queries'][-1]['ids'],[999,1,2,3,4])

    def test_missing_duplicate_foreign_or_suffix_context(self):
        for mutation in (lambda r:r.pop(),lambda r:r.append(copy.deepcopy(r[0])),
                         lambda r:r[1].update(RunToken=TOKEN+' '),lambda r:r[1].update(DatabaseId=6)):
            rows=fixture();mutation(rows)
            with self.assertRaises(ValueError):run(rows)

    def test_drop_commit_transaction_and_rows_are_actual_strict_integers(self):
        for key,value in [('IndexCount',1),('Committed',False),('TransactionState',1),
                          ('TransactionCount',True),('RowCount',1000),('AffectedRows',0),('OtherSourceUnchanged',False)]:
            rows=fixture();rows[1][key]=value
            with self.assertRaises(ValueError):run(rows)

    def test_source_full_coverage_and_non_target_changes_rejected(self):
        for after in ({**AFTER,23:0},dict(list(AFTER.items())[:-1]),{**AFTER,999:0.1}):
            with self.assertRaises(ValueError):run(fixture(),after=after)

    def test_changed_target_cannot_preexist_in_baseline_top_k(self):
        before={**BEFORE,999:0.0001};rows=fixture()
        for record in rows[3:5]:record['rows']=[{'Id':i,'DistanceValue':before[i]} for i in [999,1,2,3,4]]
        with self.assertRaises(ValueError):run(rows,before=before)

    def test_before_metadata_and_active_own_rebuild_binding(self):
        for key,value in [('object_id',101),('type',True),('name','IDX012_OwnVector '),
                          ('is_disabled',True),('vector_index_type','Other'),('distance_metric','EUCLIDEAN')]:
            rows=fixture();rows[2]['AfterMetadata'][0][key]=value
            with self.assertRaises(ValueError):run(rows)
        rows=fixture();rows[2]['BeforeMetadata']=[]
        with self.assertRaises(ValueError):run(rows)

    def test_build_time_cannot_be_boolean_negative_or_missing(self):
        for value in (True,-1,None):
            rows=fixture();rows[2]['BuildElapsedUs']=value
            with self.assertRaises(ValueError):run(rows)

    def test_missing_duplicate_wrong_or_foreign_query_ids(self):
        for mutation in (lambda r:r[-1]['rows'].pop(),lambda r:r[-1]['rows'].__setitem__(1,r[-1]['rows'][0]),
                         lambda r:r[-1]['rows'][0].update(Id=998),lambda r:r[-1].update(Ordinal=4)):
            rows=fixture();mutation(rows)
            with self.assertRaises(ValueError):run(rows)

    def test_wrong_nonfinite_or_boolean_distance_rejected(self):
        for value in (0.1,float('nan'),True):
            rows=fixture();rows[-1]['rows'][0]['DistanceValue']=value
            with self.assertRaises(ValueError):run(rows)

    def test_actual_changed_top_one_required(self):
        rows=fixture();rows[-1]['rows'][0],rows[-1]['rows'][1]=rows[-1]['rows'][1],rows[-1]['rows'][0]
        with self.assertRaises(ValueError):run(rows)

    def test_exact_order_and_phase_cannot_be_relabelled(self):
        rows=fixture();rows[3]['rows'].reverse()
        with self.assertRaises(ValueError):run(rows)
        rows=fixture();rows[5]['Stage']='BASELINE'
        with self.assertRaises(ValueError):run(rows)

    def test_stale_rebuilt_answer_is_rejected(self):
        rows=fixture();rows[-1]['rows']=copy.deepcopy(rows[3]['rows'])
        with self.assertRaises(ValueError):run(rows)

    def test_drop_snapshot_requires_actual_zero_indexes_and_no_transaction(self):
        for key,value in [("IndexCount",1),("TransactionCount",True),("TransactionState",1),("RowCount",1000)]:
            rows=fixture();rows[0][key]=value
            with self.assertRaises(ValueError):run(rows)

    def test_nonfinite_or_boolean_source_values_rejected(self):
        for value in (float('nan'),True,None):
            with self.assertRaises(ValueError):run(fixture(),after={**AFTER,800:value})


if __name__=='__main__':unittest.main()
