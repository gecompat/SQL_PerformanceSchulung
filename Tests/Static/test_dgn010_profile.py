"""Neue Controller-/Clientend-/Safety-/Cleanupgegenfälle; rein synthetisch."""
import importlib.util,json,os,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from test_dgn010_benchmark import fixture
ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice'
spec=importlib.util.spec_from_file_location('dgn010_public_profile',PUBLIC/'run_profile.py')
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)

def response(value='',code=0):return SimpleNamespace(stdout=value,stderr='',returncode=code,timed_out=False)

def full_executor(scope,*,wrong_transition=False):
    record=fixture(scope);sources=iter(record['source_snapshots'])
    windows={r['label']:r['data'] for r in record['records']};windows['CONTROL_0']=record['query_control']
    def execute(command,**kwargs):
        name=Path(command[command.index('-i')+1]).name
        variables=dict(v.split('=',1) for v in command[command.index('-v')+1:] if '=' in v)
        if name=='91_Absence.sql':return response('DGN010_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
        if name=='20_Probe.sql':
            if execute.deleted:
                execute.deleted=False;return response('Msg 51003, Level 16, State 1, Line 1\nFAIL_RESULT_CONTRACT: Synthetic source negative.',1)
            rows,indexes=next(sources)
            lines=['DGN010_SOURCE|'+'|'.join(map(str,r)) for r in rows]
            lines+=['DGN010_INDEX|'+n+'|'+'|'.join(map(str,v)) for n,v in indexes.items()]
            return response('\n'.join(lines)+'\nDGN010_READER|ROWS_10|FIXED_RIGHTS_2|NO_MODEL_CALL\nSQLPERF_SUMMARY|PASS|OK')
        if name=='21_DeleteOwnRow.sql':execute.deleted=True
        if name=='22_Database.sql':return response('DGN010_DBID|5\nSQLPERF_SUMMARY|PASS|OK')
        if name=='24_Candidate.sql':return response('DGN010_CANDIDATE|STATE_'+('0' if wrong_transition else variables['Path'])+'\nSQLPERF_SUMMARY|PASS|OK')
        if name in ('40_SelectWindow.sql','50_DmlWindow.sql'):
            if variables['Negative']=='1':return response('Msg 51003, Level 16, State 1, Line 1\nFAIL_RESULT_CONTRACT: Synthetic query negative.',1)
            raw=json.dumps(windows[variables['Label']],separators=(',',':'));count=(len(raw)+199)//200
            lines=[p.measurement.scope_prefix(scope)+f'{i+1}|{count}|{len(raw)}|'+raw[i*200:(i+1)*200] for i in range(count)]
            return response('\n'.join(lines)+'\nSQLPERF_SUMMARY|PASS|OK')
        return response('SQLPERF_SUMMARY|PASS|OK')
    execute.deleted=False;return execute

class ControllerCases(unittest.TestCase):
    def test_remote_end_requires_exact_single_last_frame(self):
        from sqlcmd_process import SqlcmdResult
        good=SqlcmdResult((),1,'','Msg 51003, Level 16, State 1, Line 1\nFAIL_RESULT_CONTRACT: Synthetic.\nDGN010_REMOTE_END|1\n',False,0)
        self.assertTrue(p.native_error(p.remote_end(good).stderr,51003,'FAIL_RESULT_CONTRACT'))
        for stderr,timed in ((good.stderr,True),('',False),(good.stderr.replace('|1','|0'),False),(good.stderr+'Sqlcmd: Error: Synthetic\n',False),(good.stderr+'DGN010_REMOTE_END|1\n',False)):
            with self.subTest(stderr=stderr,timed=timed),self.assertRaises(p.ClientEndUnknown):p.remote_end(p.replace(good,stderr=stderr,timed_out=timed))
    def test_proxy_timeout_and_collector_abort_never_establish_remote_end(self):
        from sqlcmd_process import SqlcmdResult
        command=['python',str(ROOT/'Tests/Runtime/dgn010_docker_sqlcmd_proxy.py')]
        handle=SimpleNamespace(poll=lambda:0)
        for error in (KeyboardInterrupt(),RuntimeError('synthetic')):
            with self.subTest(error=type(error).__name__),patch.object(p,'start_sqlcmd',return_value=handle),patch.object(p,'collect_process',side_effect=error),self.assertRaises(p.ClientEndUnknown):p.execute_client(command,timeout_seconds=1)
        timed=SqlcmdResult((),0,'','DGN010_REMOTE_END|0\n',True,0)
        with patch.object(p,'start_sqlcmd',return_value=handle),patch.object(p,'collect_process',return_value=timed),self.assertRaises(p.ClientEndUnknown):p.execute_client(command,timeout_seconds=1)
    def test_mixed_native_client_errors_cannot_attest_negative(self):
        frame='Msg 51003, Level 16, State 1, Line 1\nFAIL_RESULT_CONTRACT: Synthetic negative.\n'
        for extra in ('Sqlcmd: Error: Synthetic failure.\n','dgn010-docker-proxy: Transport failed\n','SQLPERF_SUMMARY|PASS|OK\n'):
            with self.subTest(extra=extra):
                self.assertFalse(p.native_error(frame+extra,51003,'FAIL_RESULT_CONTRACT'))
                self.assertFalse(p.native_error(extra+frame,51003,'FAIL_RESULT_CONTRACT'))
    def test_full_scopes_remain_warn_with_46_sources_and_12_numeric_pass(self):
        for scope in ('SELECT','DML'):
            with self.subTest(scope=scope):
                result=self.run_case(full_executor(scope),scope=scope)
                self.assertEqual((result.outcome,result.code),('WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED'))
                self.assertTrue(result.cleanup_ok);self.assertFalse(result.client_end_unknown)
                self.assertEqual(len(result.evidence['record']['source_snapshots']),46)
                self.assertEqual(result.evidence['fwk011']['result']['outcome'],'PASS')
                self.assertEqual(len(result.evidence['fwk011']['assertions']),12)
                self.assertEqual(result.evidence['aggregate']['runtime_qualification'],'NOT_ESTABLISHED')
    def test_wrong_actual_candidate_state_fails_and_cleans(self):
        result=self.run_case(full_executor('SELECT',wrong_transition=True))
        self.assertEqual((result.outcome,result.code),('FAIL','FAIL_RESULT_CONTRACT'))
        self.assertTrue(result.cleanup_ok);self.assertNotIn('aggregate',result.evidence)
    def run_case(self,execute,**kwargs):
        with patch.dict(os.environ,SQLCMDPASSWORD='synthetic-test-only'):
            return p.run_profile(executable='synthetic-sqlcmd',server='synthetic-server',scope=kwargs.pop("scope","SELECT"),confirmed=True,high_impact=True,executor=execute,**kwargs)
    def test_missing_safety_stops_before_client(self):
        with self.assertRaises(ValueError):p.run_profile(executable='unused',server='unused',scope="SELECT",confirmed=False,high_impact=True,executor=lambda *a,**k:self.fail('client'))
    def test_variables_cannot_override_owner(self):
        for value in ({'RunToken':'OTHER'},{'Path':'2'},{'Statements':'101'},{'Negative':'1; SELECT 1'}):
            with self.subTest(value=value),self.assertRaises(ValueError):p.command_for('unused','unused','sql','sa','40_SelectWindow.sql',variables=value)
    def test_fixed_scopes_and_labels_reject_injection(self):
        for scope in ('INSERT',False,None):
            with self.subTest(scope=scope),self.assertRaises(ValueError):self.run_case(lambda *a,**k:self.fail('client'),scope=scope)
        for variables in ({'Label':'CONTROL_0; SELECT 1'},{'Label':'UNKNOWN_0'},{'Path':True},{'Scope':'DML'}):
            with self.subTest(variables=variables),self.assertRaises(ValueError):p.command_for('unused','unused','sql','sa','40_SelectWindow.sql',variables=variables)
    def test_version_skip_never_sets_up(self):
        called=[]
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name;called.append(filename)
            return response('SQLPERF_SUMMARY|SKIP|SKIP_VERSION' if filename=='00_Preflight.sql' else 'DGN010_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute)
        self.assertEqual((result.outcome,result.code,result.cleanup_ok),('SKIP','SKIP_VERSION',True))
        self.assertEqual(called,['91_Absence.sql','00_Preflight.sql','91_Absence.sql'])
    def test_skip_absence_uses_parent_cleanup_deadline(self):
        now=[0];ends=[];called=[]
        def begin_cleanup():ends.append(15);return ends[0]
        def execute(command,*,timeout_seconds):
            filename=Path(command[command.index('-i')+1]).name;called.append((filename,timeout_seconds))
            if filename=='00_Preflight.sql':
                now[0]=10;return response('SQLPERF_SUMMARY|SKIP|SKIP_VERSION')
            if ends:
                self.assertEqual(timeout_seconds,5);now[0]=14
            return response('DGN010_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute,clock=lambda:now[0],cleanup_started=begin_cleanup)
        self.assertTrue(result.cleanup_ok);self.assertEqual(ends,[15]);self.assertEqual(called[-1][1],5)
    def test_fault_after_setup_runs_guarded_cleanup_and_new_absence(self):
        called=[]
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name;called.append(filename)
            return response(('DGN010_DB|ABSENT\n' if filename=='91_Absence.sql' else '')+'SQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute,fault='after_setup')
        self.assertEqual((result.outcome,result.code,result.cleanup_ok),('FAIL','FAIL_EXECUTION',True))
        self.assertTrue(p.setup_fault_completed(result))
        self.assertEqual(called,['91_Absence.sql','00_Preflight.sql','10_Setup.sql','90_Cleanup.sql','91_Absence.sql'])
    def test_interrupt_before_setup_is_not_controlled_fault(self):
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name
            if filename=='00_Preflight.sql':raise KeyboardInterrupt()
            return response('DGN010_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute,fault='after_setup')
        self.assertEqual((result.outcome,result.code,result.cleanup_ok),('FAIL','FAIL_EXECUTION',True))
        self.assertFalse(p.setup_fault_completed(result));self.assertNotIn('controlled_fault',result.evidence)
    def test_unknown_end_after_setup_blocks_all_sql(self):
        called=[]
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name;called.append(filename)
            if filename=='10_Setup.sql':raise p.ClientEndUnknown('synthetic unknown')
            return response('DGN010_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute)
        self.assertEqual((result.outcome,result.code,result.cleanup_ok,result.client_end_unknown),('FAIL','FAIL_CLEANUP',False,True))
        self.assertEqual(called,['91_Absence.sql','00_Preflight.sql','10_Setup.sql'])
    def test_cleanup_failure_cannot_be_positive(self):
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name
            return response('DGN010_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK',1 if filename=='90_Cleanup.sql' else 0)
        result=self.run_case(execute,fault='after_setup')
        self.assertEqual((result.outcome,result.code),('FAIL','FAIL_CLEANUP'))
    def test_start_without_handle_is_unknown(self):
        with patch.object(p,'start_sqlcmd',side_effect=OSError('synthetic')),self.assertRaises(p.ClientEndUnknown):p.execute_client(['unused'],timeout_seconds=1)
    def test_unended_handle_is_unknown(self):
        handle=SimpleNamespace(poll=lambda:None)
        with patch.object(p,'start_sqlcmd',return_value=handle),patch.object(p,'collect_process',side_effect=KeyboardInterrupt),self.assertRaises(p.ClientEndUnknown):p.execute_client(['unused'],timeout_seconds=1)
    def test_known_collector_end_must_match(self):
        handle=SimpleNamespace(poll=lambda:1)
        with patch.object(p,'start_sqlcmd',return_value=handle),patch.object(p,'collect_process',return_value=response()),self.assertRaises(p.ClientEndUnknown):p.execute_client(['unused'],timeout_seconds=1)
    def test_poll_exception_blocks_recovery(self):
        for error in (OSError('synthetic'),KeyboardInterrupt()):
            called=[]
            def execute(command,**kwargs):
                filename=Path(command[command.index('-i')+1]).name;called.append(filename)
                if filename!='10_Setup.sql':return response('DGN010_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
                handle=SimpleNamespace(poll=lambda:(_ for _ in ()).throw(error))
                with patch.object(p,'start_sqlcmd',return_value=handle),patch.object(p,'collect_process',side_effect=RuntimeError('synthetic collector')):
                    return p.execute_client(command,**kwargs)
            with self.subTest(error=type(error).__name__):
                result=self.run_case(execute)
                self.assertTrue(result.client_end_unknown);self.assertFalse(result.cleanup_ok)
                self.assertEqual(called,['91_Absence.sql','00_Preflight.sql','10_Setup.sql'])
    def test_boolean_poll_is_unknown(self):
        with self.assertRaises(p.ClientEndUnknown):p.client_end(SimpleNamespace(poll=lambda:False))
    def test_native_error_requires_single_associated_exact_error(self):
        value='Msg 51003, Level 16, State 1, Line 1\nFAIL_RESULT_CONTRACT: Synthetic negative.\n'
        self.assertTrue(p.native_error(value,51003,'FAIL_RESULT_CONTRACT'))
        for bad in (value+value,value.replace('51003','151003'),value.replace('CONTRACT:','CONTRACTX:'),'Msg 229, Level 1, State 1, Line 2\nOther error.\n'+value):
            self.assertFalse(p.native_error(bad,51003,'FAIL_RESULT_CONTRACT'))

if __name__=='__main__':unittest.main()
