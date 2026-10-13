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
    def test_unknown_fault_is_rejected_before_any_client(self):
        for value in ('after_index_build ', 'other', True, 1):
            client=Client()
            with self.assertRaises(ValueError):
                run(client,fault=value)
            self.assertEqual(client.files,[])

    def test_build_fault_does_not_trigger_before_qualified_index_and_source(self):
        client=Client()
        result=run(client,fault='after_index_build')
        self.assertEqual((result.outcome,result.code),('FAIL','FAIL_CONTRACT'))
        self.assertTrue(result.cleanup_ok)
        self.assertNotIn('controlled_fault',result.evidence)
        self.assertFalse(any(row[0]=='CONTROLLED_FAULT_AFTER_INDEX_BUILD' for row in result.phases))
        self.assertNotIn('50_DropRebuild.sql',client.files)

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

    def test_permission_skip_never_enters_setup_or_recovery(self):
        client=Client(lambda name,out:'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION')
        result=run(client)
        self.assertEqual((result.outcome,result.code),('SKIP','SKIP_PERMISSION'))
        self.assertEqual(client.files,['00_Preflight.sql'])
        self.assertIsNone(result.original_preview)
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


class RoleApiTests(unittest.TestCase):
    OPERATOR='SyntheticOperator!'+('X'*40)
    ADMIN='SyntheticAdmin!'+('Y'*40)
    SID='A'*32
    def setUp(self):
        self.environment={'SQLCMDPASSWORD':self.ADMIN,'IDX012_OPERATOR_PASSWORD':self.OPERATOR,'SYSTEMROOT':'synthetic-root','PATH':'synthetic-path','SQLCMDINI':'foreign','ARBITRARY':'foreign'}
        self.env=patch.dict(os.environ,self.environment,clear=True);self.env.start();self.addCleanup(self.env.stop)
        self.role=profile.role_profile
        self.binding=self.role.bind(TOKEN,self.SID,'01',dict(os.environ))
    def client(self):
        client=self.role._RoleClient(profile,self.binding,'sqlcmd','localhost,1433')
        def clean():
            for item in client.inputs:
                path=Path(item['Path'])
                if path.exists():
                    self.assertEqual(path.parent,ROOT/'Runtime');self.assertTrue(path.name.startswith('idx012-role-'));self.assertEqual(__import__('hashlib').sha256(path.read_bytes()).hexdigest(),item['InputSha256']);path.unlink()
        self.addCleanup(clean);return client
    def command(self,name):return profile.phase_command('sqlcmd','localhost,1433','sql',self.binding.operator,FOLDER/name,TOKEN,0)
    def contexts(self,stage='DML_BOUNDARY',session=12):
        rows=[]
        for checkpoint in ('ROLE_START','ADMIN_BUILD','ROLE_RESTORED','ROLE_END'):
            admin=checkpoint=='ADMIN_BUILD'
            rows.append(dict(kind='ROLE_CONTEXT',Stage=stage,Checkpoint=checkpoint,LoginName='sa'if admin else self.binding.operator,Sid='0x01'if admin else '0x'+self.SID,OriginalLogin='sa',OriginalSid='0x01',Sysadmin=int(admin),ControlServer=int(admin),AlterAnyLogin=int(admin),SessionId=session,DatabaseId=5,RunToken=TOKEN))
        frames=[dict(Frame=position,Stage=stage,SessionId=session,DatabaseId=5,RunToken=TOKEN)for position in ('BEFORE','AFTER')]
        return rows,frames
    def test_role_mode_and_credentials_reject_free_executor_folder_and_aliases_before_start(self):
        args=dict(executable='sqlcmd',server='localhost,1433',auth='sql',username=self.binding.operator,token=TOKEN,confirmed=True,high_impact=True,mode='drop-rebuild',capture_storage=True,capture_costs=True,role_mode=self.role.MODE,role_sid=self.SID,admin_sid='01')
        with patch.object(profile,'start_sqlcmd')as start:
            for changes in ({'executor':Mock()},{'folder':ROOT},{'username':'sa'},{'auth':'windows'},{'capture_costs':False},{'role_sid':True},{'admin_sid':None},{'role_mode':True},{'server':'foreign'},{'mode':'dml-boundary'}):
                with self.subTest(change=list(changes)),self.assertRaises(ValueError):profile.run_profile(**(args|changes))
            start.assert_not_called()
        for env in (self.environment|{'sqlcmdpassword':self.ADMIN},self.environment|{'IDX012_OPERATOR_PASSWORD':self.ADMIN},self.environment|{'SQLCMDPASSWORD':True}):
            with self.assertRaises(ValueError):self.role.bind(TOKEN,self.SID,'01',env)
        for sid in (self.SID[:-1],self.SID+'A','0x'+self.SID,True):
            with self.assertRaises(ValueError):self.role.bind(TOKEN,sid,'01',self.environment)
        self.assertNotIn(self.OPERATOR,repr(self.binding));self.assertNotIn(self.ADMIN,repr(self.binding))
    def test_role_composition_preserves_core_and_rejects_other_build_or_impersonation(self):
        for name,stage in self.role.STAGES.items():
            source=profile.cost_source(FOLDER/name);left,right=source.split(self.role.BUILD)
            rendered=self.role._decorate(source,self.binding,stage)
            self.assertIn(left,rendered);self.assertIn(right,rendered);self.assertEqual(rendered.count(self.role.BUILD),1)
            self.assertLess(rendered.index(left),rendered.index(self.role.BUILD));self.assertLess(rendered.index(self.role.BUILD),rendered.index(right))
            self.assertIn('CREATE TABLE #IDX012CostContext',rendered);self.assertIn("CostFrame BEFORE",rendered);self.assertIn("CostFrame AFTER",rendered)
            for changed in (source.replace(self.role.BUILD,''),source+self.role.BUILD,source+"\nEXECUTE AS LOGIN=N'foreign';",source+'\nREVERT;',source+'\n'*170000):
                with self.assertRaises(ValueError):self.role._decorate(changed,self.binding,stage)
    def test_role_context_schema_sid_privilege_order_and_cost_session_binding(self):
        for stage in self.role.STAGES.values():
            rows,frames=self.contexts(stage);self.assertEqual(len(self.role.validate_context(rows,self.binding,stage,5,frames)),4)
            for index,change in ((0,{'Sid':'0x'+'B'*32}),(1,{'Sid':'0x'+self.SID}),(2,{'OriginalLogin':self.binding.operator}),(3,{'SessionId':13}),(0,{'Sysadmin':False}),(1,{'AlterAnyLogin':False}),(0,{'DatabaseId':True}),(0,{'Extra':1}),(0,{'OriginalSid':'0x02'})):
                bad=copy.deepcopy(rows);bad[index].update(change)
                with self.subTest(index=index,change=list(change)),self.assertRaises(ValueError):self.role.validate_context(bad,self.binding,stage,5,frames)
            for bad in (rows[:-1],rows+rows[:1],list(reversed(rows))):
                with self.assertRaises(ValueError):self.role.validate_context(bad,self.binding,stage,5,frames)
            for change in ({'SessionId':13},{'SessionId':True},{'RunToken':'B'*16},{'Frame':'BEFORE'}):
                bad=copy.deepcopy(frames);bad[1].update(change)
                with self.assertRaises(ValueError):self.role.validate_context(rows,self.binding,stage,5,bad)
    def test_role_actual_one_client_cost_routing_private_env_and_source_capture(self):
        class Handle:
            pid=123;returncode=0
            def poll(self):return 0
            def communicate(self,timeout):return ('SQLPERF_SUMMARY|PASS|OK','')
        for name in ('00_Preflight.sql','30_CostBoundary.sql','50_CostRebuild.sql'):
            client=self.client();handle=Handle()
            import sqlcmd_process as collector
            with patch.object(collector.subprocess,'Popen',return_value=handle)as start:
                result=client.execute(self.command(name),timeout_seconds=10)
                self.assertEqual(start.call_count,1);args,kwargs=start.call_args
                command=args[0];environment=kwargs['env'];cost=name in self.role.STAGES
                self.assertEqual(command[command.index('-U')+1],'sa'if cost else self.binding.operator)
                self.assertEqual(environment['SQLCMDPASSWORD'],self.ADMIN if cost else self.OPERATOR)
                self.assertEqual(environment['SystemRoot'],'synthetic-root');self.assertNotIn('IDX012_OPERATOR_PASSWORD',environment);self.assertNotIn('SQLCMDINI',environment);self.assertNotIn('ARBITRARY',environment)
                self.assertNotIn(self.ADMIN,' '.join(command));self.assertNotIn(self.OPERATOR,' '.join(command))
            cap=client.captures[0];self.assertEqual(cap['Pid'],123);self.assertEqual(cap['FinalPoll'],0);self.assertEqual(cap['ReturnCode'],0);self.assertFalse(cap['UnknownSticky']);self.assertEqual(cap['ServerRequestEnd'],'NOT_ATTESTED')
            self.assertEqual(cap['SourceBefore'],cap['SourceAfter']);self.assertEqual(cap['Stdout'],result.stdout);self.assertEqual(cap['ChannelStatus'],'SAFE');self.assertFalse(Path(client.inputs[0]['Path']).exists())
            self.assertNotIn(self.ADMIN,cap['InputText']);self.assertNotIn(self.OPERATOR,cap['InputText'])
        client=self.client();base=self.command('00_Preflight.sql')
        for changed in (base+['-Q','SELECT 1;'],base+['-v','RunToken='+('B'*16)],base+['-e'],['foreign-executable',*base[1:]]):
            with patch.object(collector.subprocess,'Popen')as start,self.assertRaises(ValueError):client.execute(changed,timeout_seconds=10)
            start.assert_not_called()
        self.assertEqual(client.captures,[]);self.assertEqual(client.inputs,[])
    def test_role_unknown_precedes_privacy_and_no_follow_sql_or_input_deletion(self):
        import sqlcmd_process as collector
        class Handle:
            pid=123;returncode=0
            def __init__(self,poll,output):self.status=poll;self.output=output
            def poll(self):return self.status
            def communicate(self,timeout):return (self.output,'')
        for poll,output in ((None,'SQLPERF_SUMMARY|PASS|OK'),(True,'SQLPERF_SUMMARY|PASS|OK'),(0,self.ADMIN),(0,json.dumps({'MessageHex':self.OPERATOR.encode('utf-16-le').hex().upper()}))):
            client=self.client()
            with patch.object(collector.subprocess,'Popen',return_value=Handle(poll,output))as start,self.assertRaises(profile.ClientEndUnknown):client.execute(self.command('00_Preflight.sql'),timeout_seconds=10)
            self.assertTrue(client.unknown);cap=client.captures[0];self.assertTrue(cap['UnknownSticky']);self.assertTrue(Path(client.inputs[0]['Path']).exists())
            if poll==0:
                self.assertEqual(cap['ChannelStatus'],'REJECTED');self.assertIsNone(cap['Stdout']);self.assertIsNone(cap['Stderr'])
            with patch.object(collector.subprocess,'Popen')as next_start,self.assertRaises(profile.ClientEndUnknown):client.execute(self.command('92_Absence.sql'),timeout_seconds=10)
            next_start.assert_not_called()
    def test_role_full_controller_restore_unknown_returns_captures_and_retained_inputs(self):
        fixture=Client()
        capture={'Phase':'90_Restore.sql','Pid':123,'FinalPoll':None,'ReturnCode':None,'UnknownSticky':True,'Stdout':'','Stderr':''}
        retained={'Path':str(ROOT/'Runtime'/'idx012-role-pure-retained.sql'),'InputSha256':'A'*64,'Retained':True}
        class HeldRoleClient:
            def __init__(self):
                self.unknown=False;self.captures=[];self.inputs=[]
            def execute(self,command,timeout_seconds):
                name=Path(command[command.index('-i')+1]).name
                if name=='90_Restore.sql':
                    fixture.files.append(name);self.unknown=True;self.captures.append(capture);self.inputs.append(retained)
                    raise profile.ClientEndUnknown()
                return fixture(command,timeout_seconds)
        held=HeldRoleClient()
        with patch.object(self.role,'_RoleClient',return_value=held):
            result=profile.run_profile(executable='sqlcmd',server='localhost,1433',auth='sql',username=self.binding.operator,
                token=TOKEN,confirmed=True,high_impact=True,mode='drop-rebuild',capture_storage=True,capture_costs=True,
                role_mode=self.role.MODE,role_sid=self.SID,admin_sid='01',fault='after_setup')
        self.assertEqual(fixture.files,['00_Preflight.sql','10_Setup.sql','21_Snapshot.sql','90_Restore.sql'])
        self.assertEqual((result.outcome,result.code,result.cleanup_ok),('FAIL','FAIL_CLEANUP',False))
        self.assertEqual(result.evidence['client_end'],'UNKNOWN')
        self.assertEqual(result.evidence['temporary_source_cleanup'],'NOT_ESTABLISHED')
        self.assertIs(result.evidence['role_captures'],held.captures);self.assertIs(result.evidence['role_inputs'],held.inputs)
        self.assertEqual(result.evidence['role_captures'],[capture]);self.assertEqual(result.evidence['role_inputs'],[retained])
        self.assertEqual(result.phases[-1],('RESTORE','FAIL','FAIL_CLEANUP'));self.assertTrue(held.unknown)
        self.assertEqual(result.evidence['role_runtime_qualification'],'NOT_ESTABLISHED')

    def test_role_imported_module_api_and_source_binding_before_effect(self):
        import types,sqlcmd_process as collector
        foreign=types.ModuleType('sqlcmd_process');foreign.__file__='foreign.py'
        with patch.dict(sys.modules,{'sqlcmd_process':foreign}),self.assertRaises(ValueError):self.client()
        with patch.object(profile,'role_profile',types.SimpleNamespace(__file__='foreign.py')),self.assertRaises(ValueError):self.client()
        with patch.object(profile,'SqlcmdResult',object),self.assertRaises(ValueError):self.client()
        client=self.client();changed=client.sources|{next(iter(client.sources)):'0'*64}
        with patch.object(client,'source_map',return_value=changed),patch.object(collector.subprocess,'Popen')as start,self.assertRaises(ValueError):client.execute(self.command('00_Preflight.sql'),timeout_seconds=10)
        start.assert_not_called();self.assertEqual(client.captures,[])
        with patch.object(profile,'__name__','__main__'),patch.object(profile,'__spec__',None),patch.dict(sys.modules,{'__main__':profile}):
            main_client=self.client();self.assertEqual(main_client.sources,client.sources)
        with patch.object(profile,'__spec__',None),self.assertRaises(ValueError):self.client()


class CleanupBudgetTests(unittest.TestCase):
    OPERATOR=RoleApiTests.OPERATOR;ADMIN=RoleApiTests.ADMIN;SID=RoleApiTests.SID
    def setUp(self):RoleApiTests.setUp(self)
    def client(self,budgeted=True):
        client=self.role._RoleClient(profile,self.binding,'sqlcmd','localhost,1433',budgeted=budgeted)
        def clean():
            for item in client.inputs:
                path=Path(item['Path'])
                if path.exists():
                    self.assertEqual(path.parent,ROOT/'Runtime');self.assertTrue(path.name.startswith('idx012-role-'))
                    self.assertEqual(__import__('hashlib').sha256(path.read_bytes()).hexdigest(),item['InputSha256']);path.unlink()
        self.addCleanup(clean);return client
    def command(self,name='00_Preflight.sql'):return profile.phase_command('sqlcmd','localhost,1433','sql',self.binding.operator,FOLDER/name,TOKEN,0)
    def arguments(self,window):
        return dict(executable='sqlcmd',server='localhost,1433',auth='sql',username=self.binding.operator,token=TOKEN,confirmed=True,high_impact=True,mode='drop-rebuild',capture_storage=True,capture_costs=True,role_mode=self.role.MODE,role_sid=self.SID,admin_sid='01',shared_cleanup_window=window)
    def test_cleanup_window_typed_single_start_readonly_and_no_reset(self):
        budget=profile.cleanup_budget;window=profile.SharedCleanupWindow()
        self.assertEqual(window.snapshot(),{'Status':'NOT_STARTED','StartedMonotonic':None,'DeadlineMonotonic':None,'Seconds':60})
        with self.assertRaises(ValueError):window.remaining(1)
        first=window.begin();self.assertEqual(first,window.begin());self.assertEqual(first['DeadlineMonotonic'],first['StartedMonotonic']+60)
        self.assertGreater(window.remaining(10),0);self.assertLessEqual(window.remaining(10),10)
        with self.assertRaises(AttributeError):window._end=first['DeadlineMonotonic']+60
        self.assertFalse(hasattr(window,'reset'))
        for cap in (True,False,None,0,-1,61,float('nan'),float('inf'),'10'):
            with self.subTest(cap=repr(cap)),self.assertRaises(ValueError):window.remaining(cap)
        class Foreign(budget.SharedCleanupWindow):pass
        for value in (True,{},Foreign(),window):
            with patch.object(profile,'start_sqlcmd')as start,self.assertRaises(ValueError):profile.run_profile(**self.arguments(value))
            start.assert_not_called()
        with patch.object(profile,'start_sqlcmd')as start,self.assertRaises(ValueError):profile.run_profile(**(self.arguments(profile.SharedCleanupWindow())|{'clock':lambda:0}))
        start.assert_not_called()
    def test_window_reinitialization_and_constant_tampering_cannot_restart_or_start_clients(self):
        budget=profile.cleanup_budget
        for started in (False,True):
            window=profile.SharedCleanupWindow()
            if started:window.begin()
            before=window.snapshot()
            with self.assertRaises(ValueError):window.__init__()
            self.assertEqual(window.snapshot(),before)
        for name,values in (('SECONDS',(600,60.0,True,None)),('REAP_SECONDS',(0,10,2.0,True,None))):
            for value in values:
                with self.subTest(name=name,value=repr(value)):
                    window=profile.SharedCleanupWindow();before=window.snapshot()
                    with patch.object(budget,name,value):
                        with self.assertRaises(ValueError):window.begin()
                        with self.assertRaises(ValueError):window.snapshot()
                        with self.assertRaises(ValueError):budget.validate_call(110.0,10)
                        with patch.object(profile,'start_sqlcmd')as start,self.assertRaises(ValueError):
                            profile.run_profile(**self.arguments(window))
                        start.assert_not_called()
                    self.assertEqual(window.snapshot(),before)
        window=profile.SharedCleanupWindow();before=window.begin()
        for name,value in (('SECONDS',600),('REAP_SECONDS',10)):
            with patch.object(budget,name,value),self.assertRaises(ValueError):window.remaining(10)
            self.assertEqual(window.snapshot(),before)
        client=self.client()
        with patch.object(budget,'REAP_SECONDS',10),patch.object(profile,'start_sqlcmd')as start,self.assertRaises(ValueError):
            client.execute(self.command(),timeout_seconds=10,call_deadline=profile.time.monotonic()+10)
        start.assert_not_called();self.assertEqual(client.inputs,[]);self.assertEqual(client.captures,[])

    def test_shared_window_foreign_property_reset_and_module_callbacks_rejected_before_start(self):
        budget=profile.cleanup_budget
        for replacement in (property(lambda value:float('inf')),property(budget.SharedCleanupWindow.deadline.fget,lambda value,new:None)):
            with patch.object(budget.SharedCleanupWindow,'deadline',replacement),patch.object(profile,'start_sqlcmd')as start,self.assertRaises(ValueError):
                profile.run_profile(**self.arguments(profile.SharedCleanupWindow()))
            start.assert_not_called()
        with patch.object(budget.SharedCleanupWindow,'reset',lambda value:None,create=True),patch.object(profile,'start_sqlcmd')as start,self.assertRaises(ValueError):
            profile.run_profile(**self.arguments(profile.SharedCleanupWindow()))
        start.assert_not_called()
        with patch.object(budget,'validate_call',lambda *args:None),patch.object(profile,'start_sqlcmd')as start,self.assertRaises(ValueError):
            profile.run_profile(**self.arguments(profile.SharedCleanupWindow()))
        start.assert_not_called()

    def test_absolute_collector_keeps_one_handle_and_subtracts_startup_from_primary_wait(self):
        import sqlcmd_process as collector
        now=[100.0]
        class Handle:
            pid=123;returncode=0
            def __init__(self):self.waits=[]
            def poll(self):return 0
            def communicate(self,timeout):self.waits.append(timeout);now[0]=105.0;return ('SQLPERF_SUMMARY|PASS|OK','')
            def kill(self):raise AssertionError('KNOWN_HANDLE_KILL')
        handle=Handle();client=self.client()
        def start(*args,**kwargs):now[0]=103.0;return handle
        with patch.object(collector.subprocess,'Popen',side_effect=start)as popen,patch.object(self.role.time,'monotonic',side_effect=lambda:now[0]):
            response=client.execute(self.command(),timeout_seconds=10,call_deadline=110.0)
        self.assertEqual(popen.call_count,1);self.assertEqual(handle.waits,[5.0]);self.assertEqual(response.stdout,'SQLPERF_SUMMARY|PASS|OK')
        capture=client.captures[0];self.assertEqual(capture['Budget']['AbsoluteDeadline'],110.0);self.assertEqual(capture['Budget']['PrimaryWaitSeconds'],5.0)
        self.assertEqual((capture['Pid'],capture['FinalPoll'],capture['ReturnCode']),(123,0,0));self.assertFalse(capture['UnknownSticky']);self.assertFalse(capture['Budget']['ObservedOverrun'])
        self.assertEqual(capture['SourceBefore'],capture['SourceAfter']);self.assertEqual(capture['CollectorMode'],'FIXED_ABSOLUTE_CALL_DEADLINE')
        self.assertTrue(capture['Budget']['ChannelsObserved']);self.assertFalse(client.inputs[0]['Retained'])
    def test_timeout_reap_failure_and_late_known_poll_never_clear_unknown_or_privacy(self):
        import sqlcmd_process as collector
        secret_output=self.ADMIN
        for fault in ('timeout_known','reap_failure','secret','overrun','unknown_poll'):
            now=[100.0]
            class Handle:
                pid=123;returncode=0
                def __init__(self):self.waits=[];self.kills=0
                def poll(self):return None if fault=='unknown_poll'or not self.waits else 0
                def kill(self):self.kills+=1
                def communicate(self,timeout):
                    self.waits.append(timeout)
                    if len(self.waits)==1 and fault in ('timeout_known','reap_failure','secret'):
                        now[0]=108.0;raise collector.subprocess.TimeoutExpired('PURE_FAKE',timeout)
                    if fault=='reap_failure':raise OSError('PURE_FAKE')
                    if fault=='overrun':now[0]=111.0
                    return (secret_output if fault=='secret'else'SQLPERF_SUMMARY|PASS|OK','')
            handle=Handle();client=self.client()
            with patch.object(collector.subprocess,'Popen',return_value=handle),patch.object(self.role.time,'monotonic',side_effect=lambda:now[0]),self.assertRaises(profile.ClientEndUnknown):
                client.execute(self.command(),timeout_seconds=10,call_deadline=110.0)
            capture=client.captures[0];self.assertTrue(client.unknown);self.assertTrue(capture['UnknownSticky']);self.assertTrue(client.inputs[0]['Retained'])
            self.assertTrue(all(wait<=8 for wait in handle.waits))
            if len(handle.waits)==2:self.assertLessEqual(handle.waits[-1],2)
            if fault=='secret':self.assertEqual(capture['ChannelStatus'],'REJECTED');self.assertIsNone(capture['Stdout'])
            if fault=='reap_failure':self.assertFalse(capture['Budget']['ChannelsObserved']);self.assertEqual(capture['ChannelStatus'],'UNOBSERVED');self.assertIsNone(capture['Stdout']);self.assertIsNone(capture['Stderr'])
            if fault=='overrun':self.assertTrue(capture['Budget']['ObservedOverrun'])
            with patch.object(collector.subprocess,'Popen')as next_start,self.assertRaises(profile.ClientEndUnknown):
                client.execute(self.command('92_Absence.sql'),timeout_seconds=10,call_deadline=120.0)
            next_start.assert_not_called()
    def test_full_controller_shared_window_begins_before_restore_and_parent_keeps_deadline(self):
        fixture=Client();window=profile.SharedCleanupWindow();observed=[]
        class HeldRoleClient:
            unknown=False;captures=[];inputs=[]
            def execute(self,command,timeout_seconds,call_deadline):
                name=Path(command[command.index('-i')+1]).name
                if name in ('90_Restore.sql','91_AttestDrop.sql','92_Absence.sql'):
                    state=window.snapshot();observed.append(state)
                    self_outer.assertEqual(state['Status'],'ACTUAL_STARTED');self_outer.assertLessEqual(call_deadline,state['DeadlineMonotonic'])
                else:self_outer.assertEqual(window.snapshot()['Status'],'NOT_STARTED')
                return fixture(command,timeout_seconds)
        self_outer=self;held=HeldRoleClient()
        with patch.object(self.role,'_RoleClient',return_value=held)as factory:
            result=profile.run_profile(**self.arguments(window),fault='after_setup')
        self.assertTrue(factory.call_args.kwargs['budgeted']);self.assertTrue(result.cleanup_ok);self.assertEqual(len(observed),3)
        self.assertEqual(observed,[observed[0]]*3);self.assertEqual(result.evidence['shared_cleanup_window'],window.snapshot())
        self.assertEqual(window.begin(),observed[0]);self.assertGreater(window.remaining(10),0)
        self.assertEqual(result.evidence['role_runtime_qualification'],'NOT_ESTABLISHED')
    def test_full_controller_restore_unknown_returns_shared_start_and_stops_all_sql(self):
        fixture=Client();window=profile.SharedCleanupWindow();capture={'Phase':'90_Restore.sql','UnknownSticky':True};retained={'Path':'PURE_OWN_INPUT','Retained':True}
        class HeldRoleClient:
            def __init__(self):self.unknown=False;self.captures=[];self.inputs=[]
            def execute(self,command,timeout_seconds,call_deadline):
                name=Path(command[command.index('-i')+1]).name
                if name=='90_Restore.sql':
                    fixture.files.append(name);self.unknown=True;self.captures.append(capture);self.inputs.append(retained);raise profile.ClientEndUnknown()
                return fixture(command,timeout_seconds)
        held=HeldRoleClient()
        with patch.object(self.role,'_RoleClient',return_value=held):result=profile.run_profile(**self.arguments(window),fault='after_setup')
        self.assertEqual(fixture.files,['00_Preflight.sql','10_Setup.sql','21_Snapshot.sql','90_Restore.sql'])
        self.assertEqual((result.outcome,result.code,result.cleanup_ok),('FAIL','FAIL_CLEANUP',False))
        self.assertEqual(window.snapshot()['Status'],'ACTUAL_STARTED');self.assertEqual(result.evidence['shared_cleanup_window'],window.snapshot())
        self.assertEqual(result.evidence['client_end'],'UNKNOWN');self.assertEqual(result.evidence['temporary_source_cleanup'],'NOT_ESTABLISHED')
        self.assertIs(result.evidence['role_captures'],held.captures);self.assertIs(result.evidence['role_inputs'],held.inputs)
    def test_budget_prestart_boundaries_reject_without_process_and_legacy_uses_original_collector(self):
        import sqlcmd_process as collector
        client=self.client()
        for timeout,end in ((True,110.0),(float('nan'),110.0),(0,110.0),(10,None),(10,float('inf')),(10,99.0),(10,101.0),(10,111.0)):
            with patch.object(self.role.time,'monotonic',return_value=100.0),patch.object(collector.subprocess,'Popen')as start,self.assertRaises((ValueError,TimeoutError)):
                client.execute(self.command(),timeout_seconds=timeout,call_deadline=end)
            start.assert_not_called()
        self.assertEqual(client.captures,[]);self.assertEqual(client.inputs,[])
        legacy=self.client(False)
        class Handle:
            pid=123;returncode=0
            def __init__(self):self.waits=[]
            def poll(self):return 0
            def communicate(self,timeout):self.waits.append(timeout);return ('SQLPERF_SUMMARY|PASS|OK','')
        handle=Handle()
        with patch.object(collector.subprocess,'Popen',return_value=handle):legacy.execute(self.command(),timeout_seconds=10)
        self.assertEqual(handle.waits,[10]);self.assertNotIn('Budget',legacy.captures[0]);self.assertNotIn('CollectorMode',legacy.captures[0])

if __name__=='__main__':
    unittest.main()
