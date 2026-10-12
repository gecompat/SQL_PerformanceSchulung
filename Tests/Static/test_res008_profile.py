"""Neue Controller-/Clientend-/Safety-/Cleanupgegenfälle; rein synthetisch."""
import importlib.util,os,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions'
spec=importlib.util.spec_from_file_location('res008_public_profile',PUBLIC/'run_profile.py')
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)

def response(value='',code=0):return SimpleNamespace(stdout=value,stderr='',returncode=code,timed_out=False)

class ControllerCases(unittest.TestCase):
    def run_case(self,execute,**kwargs):
        with patch.dict(os.environ,SQLCMDPASSWORD='synthetic-test-only'):
            return p.run_profile(executable='synthetic-sqlcmd',server='synthetic-server',confirmed=True,high_impact=True,executor=execute,**kwargs)
    def test_missing_safety_stops_before_client(self):
        with self.assertRaises(ValueError):p.run_profile(executable='unused',server='unused',confirmed=False,high_impact=True,executor=lambda *a,**k:self.fail('client'))
    def test_variables_cannot_override_owner(self):
        for value in ({'RunToken':'OTHER'},{'Dimension':'33'},{'Statements':'101'},{'Negative':'1; SELECT 1'}):
            with self.subTest(value=value),self.assertRaises(ValueError):p.command_for('unused','unused','sql','sa','30_Window.sql',variables=value)
    def test_full_scalar_options_are_compatible(self):
        with patch.dict(os.environ,SQLCMDPASSWORD='synthetic-test-only'):
            command=p.command_for('unused','unused','sql','sa','40_Plan.sql',variables={'Dimension':'32'},full_scalar=True)
        self.assertIn('-y',command);self.assertNotIn('-W',command);self.assertNotIn('-h',command);self.assertNotIn('-P',command)
    def test_version_skip_never_sets_up(self):
        called=[]
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name;called.append(filename)
            return response('SQLPERF_SUMMARY|SKIP|SKIP_VERSION' if filename=='00_Preflight.sql' else 'RES008_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
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
            return response('RES008_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute,clock=lambda:now[0],cleanup_started=begin_cleanup)
        self.assertTrue(result.cleanup_ok);self.assertEqual(ends,[15]);self.assertEqual(called[-1][1],5)
    def test_fault_after_setup_runs_guarded_cleanup_and_new_absence(self):
        called=[]
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name;called.append(filename)
            return response(('RES008_DB|ABSENT\n' if filename=='91_Absence.sql' else '')+'SQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute,fault='after_setup')
        self.assertEqual((result.outcome,result.code,result.cleanup_ok),('FAIL','FAIL_EXECUTION',True))
        self.assertTrue(p.setup_fault_completed(result))
        self.assertEqual(called,['91_Absence.sql','00_Preflight.sql','10_Setup.sql','90_Cleanup.sql','91_Absence.sql'])
    def test_interrupt_before_setup_is_not_controlled_fault(self):
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name
            if filename=='00_Preflight.sql':raise KeyboardInterrupt()
            return response('RES008_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute,fault='after_setup')
        self.assertEqual((result.outcome,result.code,result.cleanup_ok),('FAIL','FAIL_EXECUTION',True))
        self.assertFalse(p.setup_fault_completed(result));self.assertNotIn('controlled_fault',result.evidence)
    def test_unknown_end_after_setup_blocks_all_sql(self):
        called=[]
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name;called.append(filename)
            if filename=='10_Setup.sql':raise p.ClientEndUnknown('synthetic unknown')
            return response('RES008_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
        result=self.run_case(execute)
        self.assertEqual((result.outcome,result.code,result.cleanup_ok,result.client_end_unknown),('FAIL','FAIL_CLEANUP',False,True))
        self.assertEqual(called,['91_Absence.sql','00_Preflight.sql','10_Setup.sql'])
    def test_cleanup_failure_cannot_be_positive(self):
        def execute(command,**kwargs):
            filename=Path(command[command.index('-i')+1]).name
            return response('RES008_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK',1 if filename=='90_Cleanup.sql' else 0)
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
                if filename!='10_Setup.sql':return response('RES008_DB|ABSENT\nSQLPERF_SUMMARY|PASS|OK')
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
