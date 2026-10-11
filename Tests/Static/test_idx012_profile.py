"""Controller-Gegenproben; keine SQL-Provisionierung und keine Runtimeabnahme."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'Demos/09_AI_SQL_Server_2025/IDX-012_Vector_Index_DML_Maintenance'
spec=importlib.util.spec_from_file_location('idx012_profile',FOLDER/'run_profile.py')
profile=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=profile
spec.loader.exec_module(profile)
from sqlcmd_process import SqlcmdResult
TOKEN='ABCDEF0123456789'


def snapshot():
    return {'DatabaseId':5,'context':'SQLPERF_LAB_IDX012_'+TOKEN,'build':'17.0.5005.3','edition':3,
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
                 '10_Setup.sql':f'ANN_BUILD_BASELINE|{TOKEN}|0|0\nIDX012_DATABASE|{TOKEN}|5\nSQLPERF_SUMMARY|PASS|OK',
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
        for i in range(1,1000):
            v=[1,i/1000,(((i*17)%97)*1000000//97)/1000000]
            vectors.append({'Id':i,'JsonValue':json.dumps(v)})
            distances.append({'Id':i,'DistanceValue':1-1/math.sqrt(sum(x*x for x in v))})
        row={'DatabaseId':5,'vectors':vectors,'rows':distances}
        self.assertEqual(len(profile.source_distances(row,5)),999)
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
        for filename in ('11_EnablePreview.sql','12_EnableMaxdop.sql','20_Baseline.sql','40_SourceAfter.sql','30_DmlBoundary.sql','21_Snapshot.sql','50_DropRebuild.sql'):
            command=profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/filename,TOKEN,0)
            self.assertEqual(command[command.index('-d')+1],'SQLPERF_LAB_IDX012_'+TOKEN)

    def test_bounded_source_chunks_reject_duplicate_missing_and_foreign_blocks(self):
        import math
        blocks=[]
        distances=[]
        for block in range(1,11):
            vectors=[]
            for i in range((block-1)*100+1,min(999,block*100)+1):
                v=[1,i/1000,(((i*17)%97)*1000000//97)/1000000]
                vectors.append({'Id':i,'JsonValue':json.dumps(v)})
                distances.append({'Id':i,'DistanceValue':1-1/math.sqrt(sum(x*x for x in v))})
            blocks.append({'kind':'SOURCE_VECTOR_BLOCK','DatabaseId':5,'BlockId':block,'vectors':vectors})
        rows=[{'kind':'SOURCE_DISTANCES','DatabaseId':5,'rows':distances},*blocks]
        encode=lambda records:'\n'.join(json.dumps(r) for r in records)
        self.assertEqual(len(profile.combine_source(encode(rows),5)),999)
        for mutation in ('missing','duplicate','foreign','id','bool'):
            bad=copy.deepcopy(rows)
            if mutation=='missing':bad.pop()
            if mutation=='duplicate':bad[-1]=copy.deepcopy(bad[-2])
            if mutation=='foreign':bad[-1]['DatabaseId']=6
            if mutation=='id':bad[-1]['vectors'][0]['Id']=1
            if mutation=='bool':bad[1]['BlockId']=True
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):profile.combine_source(encode(bad),5)


    def test_rebuild_source_profile_changes_only_id_999(self):
        import math
        vectors=[]
        distances=[]
        for i in range(1,1000):
            v=[1,0,0] if i==999 else [1,i/1000,(((i*17)%97)*1000000//97)/1000000]
            vectors.append({'Id':i,'JsonValue':json.dumps(v)})
            distances.append({'Id':i,'DistanceValue':1-1/math.sqrt(sum(x*x for x in v))})
        row={'DatabaseId':5,'vectors':vectors,'rows':distances}
        self.assertEqual(profile.source_distances(row,5,changed=True)[999],0)
        with self.assertRaises(ValueError):profile.source_distances(row,5)
        with self.assertRaises(ValueError):profile.source_distances(row,5,changed=1)
        row['vectors'][22]['JsonValue']='[1,0,0]'
        with self.assertRaises(ValueError):profile.source_distances(row,5,changed=True)

    def test_unknown_mode_is_rejected_before_sql_client(self):
        for mode in ('drop-rebuild ',True,None,'other'):
            client=Client()
            with self.assertRaises(ValueError):run(client,mode=mode)
            self.assertEqual(client.files,[])

    def test_storage_requires_explicit_boolean_and_rebuild_before_any_client(self):
        for options in ({'capture_storage':True},{'capture_storage':1,'mode':'drop-rebuild'},
                        {'capture_storage':None,'mode':'drop-rebuild'}):
            client=Client()
            with self.assertRaises(ValueError):run(client,**options)
            self.assertEqual(client.files,[])

    def test_storage_stage_cannot_override_owner_or_accept_free_phase(self):
        for variables in ({'StorageStage':'BASELINE '},{'StorageStage':'OTHER'},
                          {'StorageStage':'INDEXED','RunToken':'0'*16}):
            with self.assertRaises(ValueError):
                profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/'22_Storage.sql',TOKEN,0,variables)
        for stage in ('BASELINE','INDEXED','REBUILT'):
            command=profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/'22_Storage.sql',TOKEN,0,{'StorageStage':stage})
            self.assertIn('StorageStage='+stage,command)
            self.assertEqual(command[command.index('-d')+1],'SQLPERF_LAB_IDX012_'+TOKEN)

    def test_costs_require_explicit_storage_and_rebuild_before_sql(self):
        for options in ({'capture_costs':True},{'capture_costs':True,'mode':'drop-rebuild'},
                        {'capture_costs':1,'capture_storage':True,'mode':'drop-rebuild'},
                        {'capture_costs':None,'capture_storage':True,'mode':'drop-rebuild'}):
            client=Client()
            with self.assertRaises(ValueError):run(client,**options)
            self.assertEqual(client.files,[])

    def test_cost_includes_are_fixed_absolute_files_inside_own_phase_folder(self):
        for wrapper,stage,work in [('30_CostBoundary.sql','DML_BOUNDARY','30_DmlBoundary.sql'),
                                   ('50_CostRebuild.sql','REBUILD','50_DropRebuild.sql')]:
            command=profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/wrapper,TOKEN,0)
            self.assertIn('CostStage='+stage,command)
            environment=profile.client_environment(command,{'SQLCMDPASSWORD':'synthetic'})
            self.assertEqual(environment['PhaseWorkFile'],str((FOLDER/work).resolve()))
            self.assertEqual(environment['CostFrameFile'],str((FOLDER/'23_CostFrame.sql').resolve()))
            self.assertFalse(any(arg.startswith(('PhaseWorkFile=','CostFrameFile=')) for arg in command))
            self.assertEqual(command[command.index('-d')+1],'SQLPERF_LAB_IDX012_'+TOKEN)

    def test_cost_include_and_stage_cannot_be_overridden_by_caller(self):
        with self.assertRaises(ValueError):
            profile.cost_source(ROOT/'Runtime'/'30_CostBoundary.sql')
        for variables in ({'CostStage':'REBUILD'},{'PhaseWorkFile':'foreign.sql'},
                          {'CostFrameFile':'foreign.sql'}):
            with self.assertRaises(ValueError):
                profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/'30_CostBoundary.sql',TOKEN,0,variables)

    def test_cost_process_env_replaces_inherited_paths_and_preserves_secret_env(self):
        command=profile.phase_command('sqlcmd','localhost','sql','sa',FOLDER/'50_CostRebuild.sql',TOKEN,0)
        inherited={'SQLCMDPASSWORD':'synthetic','PhaseWorkFile':'foreign','CostFrameFile':'foreign'}
        environment=profile.client_environment(command,inherited)
        self.assertEqual(environment['SQLCMDPASSWORD'],'synthetic')
        self.assertEqual(environment['PhaseWorkFile'],str((FOLDER/'50_DropRebuild.sql').resolve()))
        self.assertEqual(environment['CostFrameFile'],str((FOLDER/'23_CostFrame.sql').resolve()))
        self.assertEqual(inherited['PhaseWorkFile'],'foreign')

    def test_native_cost_executor_uses_fixed_process_environment(self):
        command=profile.phase_command('sqlcmd','localhost','integrated',None,FOLDER/'30_CostBoundary.sql',TOKEN,0)
        with patch.object(profile,'start_sqlcmd') as start,patch.object(profile,'collect_process') as collect:
            start.return_value.poll.return_value=0
            profile.execute_client(command,timeout_seconds=5)
            self.assertEqual(start.call_args.kwargs['environment']['PhaseWorkFile'],str((FOLDER/'30_DmlBoundary.sql').resolve()))
            self.assertEqual(collect.call_args.kwargs['timeout_seconds'],5)

    def test_windows_case_variants_cannot_duplicate_reserved_include_env_keys(self):
        command=profile.phase_command('sqlcmd','localhost','integrated',None,FOLDER/'30_CostBoundary.sql',TOKEN,0)
        inherited={'PHASEWORKFILE':'foreign-upper','PhaseWorkFile':'foreign-mixed',
                   'COSTFRAMEFILE':'foreign-upper','costframefile':'foreign-lower','SQLCMDPASSWORD':'synthetic'}
        original=inherited.copy()
        environment=profile.client_environment(command,inherited)
        for key,file in [('PhaseWorkFile','30_DmlBoundary.sql'),('CostFrameFile','23_CostFrame.sql')]:
            self.assertEqual([k for k in environment if k.casefold()==key.casefold()],[key])
            self.assertEqual(environment[key],str((FOLDER/file).resolve()))
        self.assertEqual(inherited,original)
        self.assertEqual(environment['SQLCMDPASSWORD'],'synthetic')

    def test_literal_cost_source_uses_one_original_phase_and_two_ordered_frames(self):
        for wrapper,work in [('30_CostBoundary.sql','30_DmlBoundary.sql'),('50_CostRebuild.sql','50_DropRebuild.sql')]:
            source=profile.cost_source(FOLDER/wrapper)
            original=(FOLDER/work).read_text(encoding='utf-8')
            frame=(FOLDER/'23_CostFrame.sql').read_text(encoding='utf-8')
            self.assertEqual(source.count(original),1)
            self.assertEqual(source.count(frame),2)
            before=source.index(':setvar CostFrame BEFORE')
            actual=source.index(original)
            after=source.index(':setvar CostFrame AFTER')
            self.assertLess(before,actual)
            self.assertLess(actual,after)
            self.assertEqual(source.count('\nGO\n'),4)
            self.assertNotIn(':r ',source)
            self.assertLessEqual(len(source.encode('utf-8')),160000)

    def test_prepared_native_input_is_owned_and_removed_after_exception(self):
        command=profile.phase_command('sqlcmd','localhost','integrated',None,FOLDER/'30_CostBoundary.sql',TOKEN,0)
        original=command.copy()
        actual_file=None
        with self.assertRaisesRegex(RuntimeError,'controlled'):
            with profile.execution_input(command) as lease:
                actual=lease.command
                actual_file=Path(actual[actual.index('-i')+1])
                self.assertEqual(actual_file.parent,(ROOT/'Runtime').resolve())
                self.assertTrue(actual_file.is_file())
                self.assertEqual(actual_file.read_text(encoding='utf-8'),profile.cost_source(FOLDER/'30_CostBoundary.sql'))
                raise RuntimeError('controlled')
        self.assertIsNotNone(actual_file)
        self.assertFalse(actual_file.exists())
        self.assertEqual(command,original)

    def test_collector_exception_preserves_input_only_while_client_is_alive(self):
        command=profile.phase_command('sqlcmd','localhost','integrated',None,FOLDER/'30_CostBoundary.sql',TOKEN,0)
        for status in (None,1):
            process=Mock()
            process.poll.return_value=status
            source=None
            def collector(actual_process,actual_command,**kwargs):
                nonlocal source
                self.assertIs(actual_process,process)
                source=Path(actual_command[actual_command.index('-i')+1])
                raise RuntimeError('controlled collector exception')
            with patch.object(profile,'start_sqlcmd',return_value=process),patch.object(profile,'collect_process',side_effect=collector):
                with self.assertRaisesRegex(profile.ClientEndUnknown if status is None else RuntimeError,
                                            'FAIL_CLEANUP' if status is None else 'controlled collector'):
                    profile.execute_client(command,timeout_seconds=5)
            self.assertIsNotNone(source)
            self.assertEqual(source.exists(),status is None)
            if source.exists():
                # Ausschließlich die soeben von dieser Fixture erzeugte Datei.
                source.unlink()

    def test_unknown_client_end_blocks_racing_sql_recovery(self):
        def trigger(name,output):
            if name=='21_Snapshot.sql':
                raise profile.ClientEndUnknown('controlled unknown process end')
            return output
        client=Client(trigger)
        result=run(client)
        self.assertEqual((result.outcome,result.code,result.cleanup_ok),('FAIL','FAIL_CLEANUP',False))
        self.assertEqual(result.evidence['client_end'],'UNKNOWN')
        self.assertFalse(any(name in client.files for name in ('90_Restore.sql','91_AttestDrop.sql','92_Absence.sql')))

    def test_unbound_startup_script_is_removed_from_process_env(self):
        command=profile.phase_command('sqlcmd','localhost','integrated',None,FOLDER/'00_Preflight.sql',TOKEN,None)
        original={'SQLCMDINI':'foreign','SqlCmdIni':'foreign','SQLCMDPASSWORD':'synthetic'}
        actual=profile.client_environment(command,original)
        self.assertFalse(any(key.casefold()=='sqlcmdini' for key in actual))
        self.assertEqual(actual['SQLCMDPASSWORD'],'synthetic')
        self.assertEqual(original['SQLCMDINI'],'foreign')

    def test_extra_sqlcmd_commands_and_unbounded_source_are_rejected(self):
        for content in (':r foreign.sql',' :connect foreign','!! foreign','GO 100','SELECT 1;\n'*25000):
            with patch.object(Path,'read_text',return_value=content):
                with self.assertRaises(ValueError):profile.cost_source(FOLDER/'30_CostBoundary.sql')


if __name__=='__main__':
    unittest.main()
