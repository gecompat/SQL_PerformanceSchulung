"""Controller-Gegenproben; keine SQL-Provisionierung und keine Runtimeabnahme."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'Demos/09_AI_SQL_Server_2025/IDX-011_Exact_Approximate_Search'
spec=importlib.util.spec_from_file_location('idx011_profile',FOLDER/'run_profile.py')
profile=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=profile
spec.loader.exec_module(profile)
from sqlcmd_process import SqlcmdResult
TOKEN='ABCDEF0123456789'


def snapshot():
    return {'DatabaseId':5,'context':'SQLPERF_LAB_IDX011_'+TOKEN,'build':'17.0.5005.3','edition':3,
            'baseline':[{'Id':1,'OriginalValue':0,'RunToken':TOKEN,'MaxDopOriginal':0}],
            'scoped':[{'name':'PREVIEW_FEATURES','value':0,'is_value_default':True},
                      {'name':'MAXDOP','value':0,'is_value_default':True}],
            'tables':[{'SchemaName':'dbo','TableName':'PreviewState','object_id':100}],
            'fixture_object':None,'vector_indexes':0,
            'options':[{'compatibility_level':170,'recovery_model':3}],
            'files':[{'type':i,'max_size':32768 if i==0 else 8192,'growth':2048,'is_percent_growth':False} for i in (0,1)],
            'host':[{'name':'placeholder','value':0}],'markers':[{'name':'placeholder','value':0}]}


class Client:
    def __init__(self,change=None):
        self.files=[]
        self.change=change

    def __call__(self,command,timeout_seconds):
        name=Path(command[command.index('-i')+1]).name
        self.files.append(name)
        outputs={'00_Preflight.sql':'SQLPERF_SUMMARY|WARN|WARN_OPTIONAL_EVIDENCE_SKIPPED',
                 '10_Setup.sql':f'ANN_BUILD_BASELINE|{TOKEN}|0|0\nIDX011_DATABASE|{TOKEN}|5\nSQLPERF_SUMMARY|PASS|OK',
                 '21_Snapshot.sql':json.dumps(snapshot())+'\nSQLPERF_SUMMARY|PASS|OK',
                 '90_Restore.sql':f'ANN_RESTORE|{TOKEN}|0|0\nSQLPERF_SUMMARY|PASS|OK',
                 '91_AttestDrop.sql':f'ANN_ATTEST|{TOKEN}|0|0\nANN_RECOVERY|DROP_CONFIRMED\nSQLPERF_SUMMARY|PASS|OK',
                 '92_Absence.sql':'ANN_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK'}
        output=outputs.get(name,'SQLPERF_SUMMARY|FAIL|FAIL_EXECUTION')
        if self.change:
            output=self.change(name,output)
        return SqlcmdResult(tuple(command),0,output,'',False,0.01)


def run(client,**kw):
    return profile.run_profile(executable='sqlcmd',server='localhost,1433',auth='sql',username='sa',
                               token=TOKEN,confirmed=True,high_impact=True,executor=client,**kw)


class ControllerBoundaries(unittest.TestCase):
    def setUp(self):
        environment=patch.dict(os.environ,{'SQLCMDPASSWORD':'synthetic-fixture'},clear=False)
        environment.start()
        self.addCleanup(environment.stop)

    def test_version_skip_never_enters_setup_or_recovery(self):
        client=Client(lambda name,out:'SQLPERF_SUMMARY|SKIP|SKIP_VERSION')
        result=run(client)
        self.assertEqual((result.outcome,result.code),('SKIP','SKIP_VERSION'))
        self.assertEqual(client.files,['00_Preflight.sql'])
        self.assertFalse(result.cleanup_ok)

    def test_controlled_setup_fault_restores_attests_and_checks_absence(self):
        client=Client()
        result=run(client,fault='after_setup')
        self.assertEqual(result.outcome,'FAIL')
        self.assertTrue(result.cleanup_ok)
        self.assertEqual(client.files[-3:],['90_Restore.sql','91_AttestDrop.sql','92_Absence.sql'])
        self.assertNotIn('11_EnablePreview.sql',client.files)

    def test_missing_or_foreign_baseline_never_claims_cleanup(self):
        for invalid in ('ANN_BUILD_BASELINE|FOREIGN|0|0','ANN_BUILD_BASELINE|'+TOKEN+'|0|0\nANN_BUILD_BASELINE|'+TOKEN+'|0|0'):
            client=Client(lambda name,out:invalid+'\nSQLPERF_SUMMARY|PASS|OK' if name=='10_Setup.sql' else out)
            result=run(client,fault='after_setup')
            self.assertEqual(result.code,'FAIL_CLEANUP')
            self.assertNotIn('91_AttestDrop.sql',client.files)
            self.assertIn('92_Absence.sql',client.files)

    def test_restore_failure_prevents_drop_and_preserves_absence_attempt(self):
        client=Client(lambda name,out:'SQLPERF_SUMMARY|FAIL|FAIL_CLEANUP' if name=='90_Restore.sql' else out)
        result=run(client,fault='after_setup')
        self.assertEqual(result.code,'FAIL_CLEANUP')
        self.assertNotIn('91_AttestDrop.sql',client.files)
        self.assertIn('92_Absence.sql',client.files)

    def test_foreign_restore_attestation_or_missing_drop_is_failure(self):
        for phase,prefix in [('90_Restore.sql','ANN_RESTORE'),('91_AttestDrop.sql','ANN_ATTEST'),('92_Absence.sql','ANN_DB')]:
            client=Client(lambda name,out,p=phase,s=prefix:out.replace(s+'|',s+'|FOREIGN|') if name==p else out)
            self.assertEqual(run(client,fault='after_setup').code,'FAIL_CLEANUP')

    def test_duplicate_missing_and_unknown_summaries_fail_before_setup(self):
        for output in ('','SQLPERF_SUMMARY|PASS|OK\nSQLPERF_SUMMARY|PASS|OK','SQLPERF_SUMMARY|PASS|INVENTED'):
            client=Client(lambda name,out:output)
            self.assertEqual(run(client).code,'FAIL_CONTRACT')
            self.assertEqual(client.files,['00_Preflight.sql'])

    def test_unsafe_flags_and_token_suffix_fail_without_client(self):
        for token,confirmed,high in [(TOKEN+' ',True,True),(TOKEN,1,True),(TOKEN,True,False)]:
            client=Client()
            with self.assertRaises(ValueError):
                profile.run_profile(executable='sqlcmd',server='localhost',auth='sql',username='sa',token=token,
                                    confirmed=confirmed,high_impact=high,executor=client)
            self.assertEqual(client.files,[])
        for variables in ({'RunToken':TOKEN},{'TargetDatabase':'master'},{'Path':"EXACT'; DROP DATABASE master;--"}):
            with self.assertRaises(ValueError):
                profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/'00_Preflight.sql',TOKEN,None,variables)

    def test_full_snapshot_detects_unrelated_state_and_marker_changes(self):
        for key in ('host','markers','options','files','baseline','DatabaseId'):
            after=copy.deepcopy(snapshot())
            after[key]=6 if key=='DatabaseId' else []
            with self.subTest(key=key),self.assertRaises(ValueError):
                profile.same_snapshot(snapshot(),after)

    def test_only_selected_configuration_may_change(self):
        before=snapshot()
        after=copy.deepcopy(before)
        after['scoped'][0].update(value=1,is_value_default=False)
        profile.same_snapshot(before,after,enable='PREVIEW_FEATURES')
        after['scoped'][1]['value']=1
        with self.assertRaises(ValueError):profile.same_snapshot(before,after,enable='PREVIEW_FEATURES')

    def test_actual_source_rejects_missing_rows_wrong_db_and_changed_vector(self):
        import math
        vectors=[]
        distances=[]
        for i in range(1,1001):
            v=[1,i/1000,(((i*17)%97)*1000000//97)/1000000]
            vectors.append({'Id':i,'JsonValue':json.dumps(v)})
            distances.append({'Id':i,'DistanceValue':1-1/math.sqrt(sum(x*x for x in v))})
        row={'DatabaseId':5,'vectors':vectors,'rows':distances}
        self.assertEqual(len(profile.source_distances(row,5)),1000)
        for mutation in ('rows','db','vector','distance'):
            bad=copy.deepcopy(row)
            if mutation=='rows':bad['vectors'].pop()
            if mutation=='db':bad['DatabaseId']=6
            if mutation=='vector':bad['vectors'][0]['JsonValue']='[1,0,0]'
            if mutation=='distance':bad['rows'][0]['DistanceValue']=0.5
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):profile.source_distances(bad,5)

    def test_full_output_options_and_password_never_in_argv(self):
        command=profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/'00_Preflight.sql',TOKEN,None)
        self.assertNotIn('-P',command)
        self.assertNotIn('-W',command)
        self.assertNotIn('-h',command)
        self.assertEqual(command[command.index('-y')+1],'0')
        self.assertEqual(command[command.index('-d')+1],'master')
        for filename in ('11_EnablePreview.sql','12_EnableMaxdop.sql','20_Baseline.sql','40_Observation.sql','50_Mitigation.sql','60_Comparison.sql'):
            command=profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/filename,TOKEN,0)
            self.assertEqual(command[command.index('-d')+1],'SQLPERF_LAB_IDX011_'+TOKEN)

    def test_bounded_source_chunks_reject_duplicate_missing_and_foreign_blocks(self):
        import math
        blocks=[]
        distances=[]
        for block in range(1,11):
            vectors=[]
            for i in range((block-1)*100+1,block*100+1):
                v=[1,i/1000,(((i*17)%97)*1000000//97)/1000000]
                vectors.append({'Id':i,'JsonValue':json.dumps(v)})
                distances.append({'Id':i,'DistanceValue':1-1/math.sqrt(sum(x*x for x in v))})
            blocks.append({'kind':'SOURCE_VECTOR_BLOCK','DatabaseId':5,'BlockId':block,'vectors':vectors})
        rows=[{'kind':'SOURCE_DISTANCES','DatabaseId':5,'rows':distances},*blocks]
        encode=lambda records:'\n'.join(json.dumps(r) for r in records)
        self.assertEqual(len(profile.combine_source(encode(rows),5)),1000)
        for mutation in ('missing','duplicate','foreign','id','bool'):
            bad=copy.deepcopy(rows)
            if mutation=='missing':bad.pop()
            if mutation=='duplicate':bad[-1]=copy.deepcopy(bad[-2])
            if mutation=='foreign':bad[-1]['DatabaseId']=6
            if mutation=='id':bad[-1]['vectors'][0]['Id']=1
            if mutation=='bool':bad[1]['BlockId']=True
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):profile.combine_source(encode(bad),5)


if __name__=='__main__':
    unittest.main()
