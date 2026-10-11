"""Synthetische Methodengegenproben; keine SQL-/Provideraufrufe."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'Demos/09_AI_SQL_Server_2025/IDX-012_Vector_Index_DML_Maintenance'))
from cost_evidence import validate_costs
TOKEN='ABCDEF0123456789'


def fixture(stage='DML_BOUNDARY'):
    rows=[]
    for ordinal,frame in enumerate(('BEFORE','AFTER')):
        rows.append({'kind':'PHASE_COST','Stage':stage,'Frame':frame,'RunToken':TOKEN,'DatabaseId':5,
                     'Context':'SQLPERF_LAB_IDX012_'+TOKEN,'SessionId':60,'SourceRows':999,
                     'VectorIndexes':0 if stage=='DML_BOUNDARY' and ordinal==0 else 1,
                     'TransactionCount':0,'TransactionState':0,'SessionCount':1,'TempdbCount':1,'FileCount':2,
                     'session':[{'session_id':60,'cpu_time':10+ordinal,'reads':0,'writes':10*ordinal,'logical_reads':100+ordinal}],
                     'tempdb':[{'session_id':60,'database_id':2,'user_objects_alloc_page_count':8*ordinal,
                                'user_objects_dealloc_page_count':8*ordinal,'internal_objects_alloc_page_count':0,
                                'internal_objects_dealloc_page_count':0}],
                     'files':[{'database_id':5,'file_id':i,'sample_ms':1000+ordinal,'num_of_writes':0,
                               'num_of_bytes_written':0,'io_stall_write_ms':0} for i in (1,2)]})
    return rows


def run(rows,stage='DML_BOUNDARY'):
    return validate_costs(rows,token=TOKEN,database_id=5,stage=stage,file_ids={1,2})


class Costs(unittest.TestCase):
    def test_both_stages_preserve_whole_phase_and_counter_meanings(self):
        for stage in ('DML_BOUNDARY','REBUILD'):
            result=run(fixture(stage),stage)
            self.assertEqual(result['session_delta']['writes'],10)
            self.assertEqual(result['file_delta'][1]['num_of_bytes_written'],0)
            self.assertEqual(result['session_writes_meaning'],'DIRTY_PAGE_MARKINGS_NOT_ACTUAL_FILE_WRITES')
            self.assertEqual(result['isolated_build_costs'],'NOT_ESTABLISHED')

    def test_no_missing_counter_becomes_measured_zero(self):
        for key,field in [('session','cpu_time'),('tempdb','internal_objects_alloc_page_count'),('files','num_of_bytes_written')]:
            rows=fixture();rows[1][key][0].pop(field)
            with self.assertRaises(ValueError):run(rows)

    def test_actual_zero_is_preserved(self):
        self.assertEqual(run(fixture())['file_delta'][2]['num_of_bytes_written'],0)

    def test_negative_bool_float_and_null_counters_rejected(self):
        for value in (-1,True,1.5,None):
            rows=fixture();rows[1]['files'][0]['num_of_writes']=value
            with self.assertRaises(ValueError):run(rows)

    def test_counter_reset_is_failure_not_negative_cost_or_zero(self):
        for key,field in [('session','cpu_time'),('tempdb','user_objects_alloc_page_count'),('files','sample_ms')]:
            rows=fixture();rows[0][key][0][field]=100;rows[1][key][0][field]=1
            with self.assertRaises(ValueError):run(rows)

    def test_full_frame_order_and_stage_binding(self):
        for mutation in (lambda r:r.reverse(),lambda r:r.pop(),lambda r:r.append(copy.deepcopy(r[0])),
                         lambda r:r[1].update(Stage='OTHER')):
            rows=fixture();mutation(rows)
            with self.assertRaises(ValueError):run(rows)

    def test_foreign_owner_database_context_or_session_rejected(self):
        for key,value in [('RunToken',TOKEN+' '),('DatabaseId',6),('Context','foreign'),('SessionId',61)]:
            rows=fixture();rows[1][key]=value
            with self.assertRaises(ValueError):run(rows)

    def test_inner_session_and_tempdb_identity_required(self):
        for key,field,value in [('session','session_id',61),('tempdb','session_id',61),('tempdb','database_id',5)]:
            rows=fixture();rows[1][key][0][field]=value
            with self.assertRaises(ValueError):run(rows)

    def test_file_coverage_duplicates_and_foreign_db_rejected(self):
        for mutation in (lambda r:r[1]['files'].pop(),lambda r:r[1]['files'][1].update(file_id=1),
                         lambda r:r[1]['files'][1].update(file_id=3),lambda r:r[1]['files'][0].update(database_id=6)):
            rows=fixture();mutation(rows)
            with self.assertRaises(ValueError):run(rows)

    def test_actual_catalog_counts_cannot_be_missing_or_coerced(self):
        for key,value in [('SessionCount',True),('TempdbCount',0),('FileCount',3)]:
            rows=fixture();rows[1][key]=value
            with self.assertRaises(ValueError):run(rows)

    def test_actual_transaction_row_and_index_states(self):
        for key,value in [('TransactionCount',1),('TransactionState',True),('SourceRows',998),('VectorIndexes',0)]:
            rows=fixture();rows[1][key]=value
            with self.assertRaises(ValueError):run(rows)

    def test_cpu_integer_width_is_bounded(self):
        rows=fixture();rows[1]['session'][0]['cpu_time']=2**31
        with self.assertRaises(ValueError):run(rows)


if __name__=='__main__':unittest.main()
