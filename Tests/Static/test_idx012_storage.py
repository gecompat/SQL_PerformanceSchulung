import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'Demos/09_AI_SQL_Server_2025/IDX-012_Vector_Index_DML_Maintenance'))
from storage_evidence import validate_storage
TOKEN='ABCDEF0123456789'


def fixture(stage='BASELINE'):
    return {'kind':'STORAGE','Stage':stage,'RunToken':TOKEN,'DatabaseId':5,'Context':'SQLPERF_LAB_IDX012_'+TOKEN,
            'FixtureObject':100,'SourceRows':999,'VectorIndexes':0 if stage=='BASELINE' else 1,
            'TransactionCount':0,'TransactionState':0,
            'FileCount':2,'InternalCount':0,'PartitionCount':1,
            'files':[{'file_id':1,'type':0,'size':8192,'space_used_pages':20},
                     {'file_id':2,'type':1,'size':1024,'space_used_pages':None}],
            'internal_tables':[],
            'partitions':[{'partition_id':1000,'object_id':100,'index_id':1,'partition_number':1,'row_count':800,
                           'used_page_count':10,'reserved_page_count':16,'in_row_used_page_count':8,
                           'lob_used_page_count':2,'row_overflow_used_page_count':0}]}


def run(row,stage='BASELINE'):
    return validate_storage(row,token=TOKEN,database_id=5,fixture_object=100,stage=stage)


class Storage(unittest.TestCase):
    def test_complete_frames_keep_nullable_and_approximate_fields(self):
        for stage in ('BASELINE','INDEXED','REBUILT'):
            result=run(fixture(stage),stage)
            self.assertIsNone(result['record']['files'][1]['space_used_pages'])
            self.assertEqual(result['record']['partitions'][0]['row_count'],800)
            self.assertEqual(result['index_storage_attribution'],'NOT_ESTABLISHED')

    def test_wrong_token_suffix_db_context_or_fixture_rejected(self):
        for key,value in [('RunToken',TOKEN+' '),('DatabaseId',6),('Context','foreign'),('FixtureObject',101),('Stage','INDEXED')]:
            row=fixture();row[key]=value
            with self.assertRaises(ValueError):run(row)

    def test_transaction_row_and_index_state_are_actual_strict_integers(self):
        for key,value in [('SourceRows',998),('VectorIndexes',1),('TransactionCount',True),('TransactionState',1)]:
            row=fixture();row[key]=value
            with self.assertRaises(ValueError):run(row)

    def test_missing_duplicate_wrong_type_or_oversized_files_rejected(self):
        for mutation in (lambda r:r['files'].pop(),lambda r:r['files'][1].update(file_id=1),
                         lambda r:r['files'][1].update(type=True),lambda r:r['files'][0].update(size=32769)):
            row=fixture();mutation(row)
            with self.assertRaises(ValueError):run(row)

    def test_nullable_is_distinct_from_missing_zero_and_invalid(self):
        row=fixture();row['files'][1]['space_used_pages']=0
        self.assertEqual(run(row)['record']['files'][1]['space_used_pages'],0)
        for mutation in (lambda r:r['files'][1].pop('space_used_pages'),
                         lambda r:r['files'][0].update(space_used_pages=-1),
                         lambda r:r['files'][0].update(space_used_pages=8193)):
            row=fixture();mutation(row)
            with self.assertRaises(ValueError):run(row)

    def test_partition_coverage_duplicates_and_size_caps(self):
        for parts in ([],fixture()['partitions']*2,fixture()['partitions']*129):
            row=fixture();row['partitions']=parts
            with self.assertRaises(ValueError):run(row)

    def test_used_pages_must_equal_component_sum_and_not_exceed_reserved(self):
        for key,value in [('used_page_count',11),('reserved_page_count',9),('lob_used_page_count',3)]:
            row=fixture();row['partitions'][0][key]=value
            with self.assertRaises(ValueError):run(row)

    def test_partition_numeric_missing_negative_bool_float_rejected(self):
        for value in (None,-1,True,1.5):
            row=fixture();row['partitions'][0]['row_count']=value
            with self.assertRaises(ValueError):run(row)

    def test_internal_parent_fields_are_retained_without_attribution_claim(self):
        row=fixture();row['internal_tables']=[{'object_id':200,'parent_id':100,'parent_minor_id':1152000,
                                             'internal_type':200,'internal_type_desc':'SyntheticInternal'}]
        row['InternalCount']=1
        result=run(row)
        self.assertEqual(result['record']['internal_tables'],row['internal_tables'])
        self.assertEqual(result['index_storage_attribution'],'NOT_ESTABLISHED')

    def test_internal_duplicates_invalid_ids_and_caps_rejected(self):
        item={'object_id':200,'parent_id':100,'parent_minor_id':1,'internal_type':200,'internal_type_desc':'SyntheticInternal'}
        for values in ([item,item],[dict(item,object_id=0)],[dict(item,internal_type=256)],[item]*65):
            row=fixture();row['internal_tables']=values
            with self.assertRaises(ValueError):run(row)

    def test_system_partition_id_can_be_signed_but_not_zero(self):
        row=fixture();row['partitions'].append(dict(row['partitions'][0],partition_id=1001,object_id=-100))
        row['PartitionCount']=2
        run(row)
        row['partitions'][1]['object_id']=0
        with self.assertRaises(ValueError):run(row)

    def test_actual_catalog_counts_and_fixture_pk_coverage_required(self):
        for mutation in (lambda r:r.update(PartitionCount=2),lambda r:r.update(InternalCount=True),
                         lambda r:r.update(FileCount=1),lambda r:r['partitions'][0].update(object_id=-100),
                         lambda r:r['partitions'][0].update(index_id=0),
                         lambda r:r['partitions'][0].update(partition_number=2)):
            row=fixture();mutation(row)
            with self.assertRaises(ValueError):run(row)

    def test_no_missing_catalog_becomes_zero_measurement(self):
        for key in ('files','partitions','internal_tables'):
            row=fixture();row.pop(key)
            with self.assertRaises(ValueError):run(row)


if __name__=='__main__':unittest.main()
