"""Kostencontroller, ausschließlich synthetische Nativeframes und Faults."""
import copy,importlib.util,json,os,re,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from test_dgn010_cost_evidence import fixture

ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice'
spec=importlib.util.spec_from_file_location('dgn010_public_cost_profile',PUBLIC/'run_cost_profile.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

def response(text='',code=0,timed=False):return SimpleNamespace(stdout=text,stderr='',returncode=code,timed_out=timed)
NEGATIVE='Msg 51003, Level 16, State 1, Line 1\nFAIL_RESULT_CONTRACT: Synthetic own negative.'
PASS='SQLPERF_SUMMARY|PASS|OK'

def fake_executor(*,mutate=None,unknown=None,skip=None,cleanup_fail=False):
    data=fixture()
    if mutate:mutate(data)
    snapshots=iter(data['source_snapshots']);states=iter(data['negative_states']+[s for pair in data['full_states'] for s in pair]);windows=iter(data['records'])
    calls=[]
    def execute(command,*,timeout_seconds):
        path=Path(command[command.index('-i')+1]);name=path.name;sql=path.read_text(encoding='utf-8');calls.append(name)
        if unknown==name or (unknown=='RAW' and name.startswith('cost-own-')):raise p.profile.ClientEndUnknown('Synthetic unknown native end')
        if name=='91_Absence.sql':return response('DGN010_DB|ABSENT\n'+PASS)
        if name=='90_Cleanup.sql':return response('Msg 51004, Level 16, State 1, Line 1\nFAIL_STATE: Synthetic cleanup.',1) if cleanup_fail else response(PASS)
        if name=='00_Preflight.sql':return response('SQLPERF_SUMMARY|SKIP|'+skip if skip else PASS)
        if name=='21_DeleteOwnRow.sql':execute.deleted=True
        if name=='20_Probe.sql':
            if execute.deleted:execute.deleted=False;return response(NEGATIVE,1)
            rows,indexes=next(snapshots);lines=['DGN010_SOURCE|'+'|'.join(map(str,row)) for row in rows]
            lines+=['DGN010_INDEX|'+key+'|'+'|'.join(map(str,v)) for key,v in indexes.items()]
            return response('\n'.join(lines)+'\nDGN010_READER|ROWS_10|FIXED_RIGHTS_2|NO_MODEL_CALL\n'+PASS)
        if name=='22_Database.sql':return response('DGN010_DBID|7\n'+PASS)
        if name.startswith('cost-own-'):
            assert '-W' not in command and '-h' not in command and command[command.index('-y')+1]=='0'
            if 'DGN010_STATEPART|' in sql:
                raw=json.dumps(next(states),separators=(',',':')).encode('utf-16-le');chars=len(raw)//2;parts=(chars+199)//200
                return response('\n'.join(f'DGN010_STATEPART|{n+1}|{parts}|{chars}|'+raw[n*400:(n+1)*400].hex().upper() for n in range(parts)))
            if "@RawKind nvarchar(max)=N'DROP'" in sql and '@Held nvarchar(max)=N\''+p.costs.EMPTY+"'" in sql:return response(NEGATIVE,1)
            raw=json.dumps(next(windows),separators=(',',':'));parts=(len(raw)+199)//200
            return response('\n'.join(f'DGN010_BUILDPART|{n+1}|{parts}|{len(raw)}|'+raw[n*200:(n+1)*200] for n in range(parts))+'\n'+PASS)
        return response(PASS)
    execute.deleted=False;execute.calls=calls;return execute

class CostControllerTests(unittest.TestCase):
    def run_case(self,executor,**changes):
        with tempfile.TemporaryDirectory() as name,patch.dict(os.environ,SQLCMDPASSWORD='synthetic-test-only'):
            result=p.run_cost_profile(executable='synthetic-sqlcmd',server='synthetic-server',confirmed=True,high_impact=True,executor=executor,input_folder=name,**changes)
            files=list(Path(name).iterdir());return result,files
    def test_complete_profile_warn_four_ddl_and_ten_states(self):
        execute=fake_executor();result,files=self.run_case(execute)
        self.assertEqual((result.outcome,result.code),('WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED'))
        self.assertTrue(result.cleanup_ok);self.assertFalse(result.client_end_unknown);self.assertFalse(files)
        self.assertEqual(len(result.evidence['record']['records']),4)
        self.assertEqual(result.evidence['aggregate']['full_state_rows'],10000)
        self.assertEqual(result.evidence['aggregate']['runtime_qualification'],'NOT_ESTABLISHED')
        self.assertEqual(sum(phase[1]=='EXPECTED_REJECTION' for phase in result.phases),2)
        self.assertEqual(execute.calls[-2:],['90_Cleanup.sql','91_Absence.sql'])
    def test_contract_failures_cleanup_without_aggregate(self):
        for mutate in (lambda d:d['records'][0].update(DdlSha256='0'*64),lambda d:d['full_states'][0][1]['files'][0].update(size=1),lambda d:d['source_snapshots'][4][1].pop(p.costs.CANDIDATE)):
            with self.subTest(mutate=mutate):
                result,files=self.run_case(fake_executor(mutate=mutate));self.assertEqual(result.outcome,'FAIL');self.assertTrue(result.cleanup_ok);self.assertNotIn('aggregate',result.evidence);self.assertFalse(files)
    def test_unknown_raw_end_preserves_own_input_and_suppresses_cleanup(self):
        execute=fake_executor(unknown='RAW');result,files=self.run_case(execute)
        self.assertEqual((result.outcome,result.code),('FAIL','FAIL_CLEANUP'));self.assertTrue(result.client_end_unknown);self.assertFalse(result.cleanup_ok)
        self.assertEqual(len(files),1);self.assertEqual(result.evidence['own_input_files_preserved'],1)
        self.assertNotIn('90_Cleanup.sql',execute.calls);self.assertNotEqual(execute.calls[-1],'91_Absence.sql')
    def test_unknown_setup_end_suppresses_all_future_clients(self):
        execute=fake_executor(unknown='10_Setup.sql');result,files=self.run_case(execute)
        self.assertTrue(result.client_end_unknown);self.assertEqual(execute.calls,['91_Absence.sql','00_Preflight.sql','10_Setup.sql']);self.assertFalse(files)
    def test_skip_never_sets_up_and_absence_checked(self):
        for skip in ('SKIP_VERSION','SKIP_CONFIGURATION','SKIP_PERMISSION'):
            with self.subTest(skip=skip):
                execute=fake_executor(skip=skip);result,files=self.run_case(execute);self.assertEqual((result.outcome,result.code,result.cleanup_ok),('SKIP',skip,True));self.assertFalse(files)
                self.assertEqual(execute.calls,['91_Absence.sql','00_Preflight.sql','91_Absence.sql'])
    def test_controlled_setup_fault_recovers(self):
        execute=fake_executor();result,files=self.run_case(execute,fault='after_setup')
        self.assertTrue(p.profile.setup_fault_completed(result));self.assertFalse(files)
    def test_cleanup_failure_overrides_success(self):
        result,files=self.run_case(fake_executor(cleanup_fail=True));self.assertEqual((result.outcome,result.code),('FAIL','FAIL_CLEANUP'));self.assertFalse(result.cleanup_ok);self.assertFalse(files)
    def test_missing_confirmations_or_bad_deadline_never_starts_client(self):
        for changes in ({'confirmed':False},{'high_impact':1},{'fault':'free'},{'normal_deadline':True},{'normal_deadline':float('nan')}):
            values={'executable':'unused','server':'unused','confirmed':True,'high_impact':True,'executor':lambda *a,**k:self.fail('client')}|changes
            with self.subTest(changes=changes),self.assertRaises(ValueError):p.run_cost_profile(**values)
    def test_exhausted_parent_budget_and_cleanup_share_deadline(self):
        execute=fake_executor();result,files=self.run_case(execute,clock=lambda:0,normal_deadline=0,cleanup_started=lambda:0)
        self.assertEqual((result.outcome,result.code),('FAIL','FAIL_CLEANUP'));self.assertFalse(execute.calls);self.assertFalse(files)
    def test_own_input_unlink_failure_cannot_be_reported_as_clean(self):
        unlink=Path.unlink
        def fail_input(path,*args,**kwargs):
            if path.name.startswith('cost-own-'):raise PermissionError('Synthetic own input lock')
            return unlink(path,*args,**kwargs)
        with tempfile.TemporaryDirectory() as name,patch.dict(os.environ,SQLCMDPASSWORD='synthetic-test-only'):
            with patch.object(Path,'unlink',fail_input):
                result=p.run_cost_profile(executable='fake',server='synthetic',confirmed=True,high_impact=True,executor=fake_executor(),input_folder=name)
            self.assertEqual((result.outcome,result.code),('FAIL','FAIL_CLEANUP'));self.assertFalse(result.cleanup_ok)
            self.assertEqual(result.evidence['own_input_files_preserved'],1)
    def test_cli_only_emits_aggregate_after_warn_and_cleanup(self):
        execute=fake_executor();result,_=self.run_case(execute)
        import io
        for value,expected in ((result,True),(p.profile.replace(result,outcome='FAIL',code='FAIL_CLEANUP',cleanup_ok=False),False)):
            with patch.object(p,'run_cost_profile',return_value=value),patch.object(p.profile,'resolve_sqlcmd',return_value='fake'),patch.object(sys,'argv',['run_cost_profile.py','--server','synthetic','--summary']),patch('sys.stdout',new_callable=io.StringIO) as output:
                p.main();self.assertEqual('DGN010_COST_AGGREGATE|' in output.getvalue(),expected)

if __name__=='__main__':unittest.main()
