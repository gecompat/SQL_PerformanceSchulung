"""Synthetische Gegenfälle für den begrenzten Markerconsumer."""
import copy,importlib.util,json,os,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Tests/Static'),str(ROOT/'Tests/Runtime')]
from test_dgn010_profile import p,full_executor,response
SOURCE=ROOT/'Tests/Runtime/dgn010_marker_controls.py'
spec=importlib.util.spec_from_file_location('marker_control_test_source',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def state():
    data={k:[] for k in ('db','config','files','schemas','objects','indexes','index_columns','columns','reader','permissions','roles','rows','properties')}
    data['rows']=[{'Id':i,'Value':i*3,'Payload':'F'*100,'payload_bytes':100} for i in range(1,1001)]
    data['properties']=[{'name_hex':k.encode('utf-16-le').hex(),'value_hex':v.encode('utf-16-le').hex()} for k,v in m.MARKERS.items()]
    return data
def frame(data):
    raw=json.dumps(data,separators=(',',':'));n=(len(raw)+199)//200
    return '\n'.join(f'DGN010_STATEPART|{i+1}|{n}|{len(raw)}|'+raw[i*200:(i+1)*200].encode('utf-16-le').hex().upper() for i in range(n))

def executor(*,fault=None,clock=None):
    baseline=state();snapshots=[baseline]
    for marker,value,name,invalid in m.cases():
        changed=copy.deepcopy(baseline);changed['properties']=[s for s in changed['properties'] if s['name_hex']!=marker.encode('utf-16-le').hex()]
        if invalid is not None:changed['properties'].append({'name_hex':name.encode('utf-16-le').hex(),'value_hex':invalid.encode('utf-16-le').hex()})
        snapshots.extend([changed]*9+[baseline])
    good=full_executor('SELECT');calls=[];indexes=[0];negative=[0]
    def execute(command,*,timeout_seconds):
        filename=Path(command[command.index('-i')+1]).name;calls.append((filename,timeout_seconds))
        if filename.startswith('dgn010-marker-'):
            text=Path(command[command.index('-i')+1]).read_text(encoding='utf-8')
            if 'DECLARE @J' in text:
                data=snapshots[indexes[0]];indexes[0]+=1
                if fault in ('mixed','timeout') and negative[0]>=1:data=baseline
                if fault=='snapshot_changed' and indexes[0]==3:data=copy.deepcopy(data);data['rows'][998]['Value']=0
                if fault=='snapshot_changed' and indexes[0]>3:data=baseline
                return response(frame(data))
            return response('')
        if filename in m.PHASES and indexes[0]>=2 and indexes[0]<len(snapshots):
            negative[0]+=1
            if fault is not None and negative[0]>1 and filename=='90_Cleanup.sql':return response('SQLPERF_SUMMARY|PASS|OK')
            if fault=='unknown':raise p.ClientEndUnknown('synthetic unknown')
            if fault=='timeout':clock[0]=301;return SimpleNamespace(stdout='',stderr='',returncode=1,timed_out=True)
            text='Msg 51004, Level 16, State 1, Line 1\nFAIL_STATE: Synthetic marker negative.'
            if fault=='mixed':text+='\nSqlcmd: Error: Additional synthetic failure.'
            if filename=='90_Cleanup.sql' and negative[0]>192:return response('SQLPERF_SUMMARY|PASS|OK')
            return response(text,1)
        return good(command,timeout_seconds=timeout_seconds)
    execute.calls=calls;return execute

class MarkerCases(unittest.TestCase):
    def test_hex_snapshot_preserves_spaces_and_empty_role_array(self):
        data=state();data['objects']=[{'type':'U ','name':'Synthetic object '}];self.assertEqual(data['roles'],[])
        output='\n'.join(s.rstrip() for s in frame(data).splitlines());self.assertEqual(m.decode(output),data)
        self.assertIn("N'[]'",m.STATE_SQL)
    def test_full_variant_config_bytes_types_and_null_remain_distinct(self):
        data=state();data['config']=[{'configuration_id':1,'value_type':'nvarchar','value_bytes':8,'value_hex':'4E004F004E004500','secondary_type':None,'secondary_hex':None},{'configuration_id':2,'value_type':'int','value_bytes':4,'value_hex':'00000000','secondary_type':'int','secondary_hex':'00000000'}]
        self.assertEqual(m.decode(frame(data)),data)
        other=copy.deepcopy(data);other['config'][0]['value_hex']+='2000';other['config'][0]['value_bytes']+=2
        self.assertNotEqual(m.digest(data),m.digest(other))
    def test_exact_setup_information_preserves_complete_controls(self):
        base=executor()
        def execute(command,**kwargs):
            result=base(command,**kwargs)
            if Path(command[command.index('-i')+1]).name=='10_Setup.sql' and result.returncode==0:
                result.stderr="Changed database context to 'SQLPERF_LAB_DGN010_LOCAL'."
            return result
        result=self.run_case(execute);self.assertEqual(result.outcome,'PASS');self.assertTrue(result.cleanup_ok)
    def test_setup_info_mixed_with_error_fails_before_marker_mutation(self):
        base=executor()
        def execute(command,**kwargs):
            result=base(command,**kwargs)
            if Path(command[command.index('-i')+1]).name=='10_Setup.sql' and result.returncode==0:
                result.stderr="Changed database context to 'SQLPERF_LAB_DGN010_LOCAL'.\nSqlcmd: Error: synthetic extra."
            return result
        result=self.run_case(execute);self.assertEqual(result.outcome,'FAIL');self.assertTrue(result.cleanup_ok);self.assertEqual(result.evidence['completed_negative_count'],0)
    def run_case(self,execute,**kwargs):
        with patch.dict(os.environ,SQLCMDPASSWORD='synthetic-only'):
            return m.run(p,executable='synthetic-sqlcmd',server='synthetic-server',confirmed=True,high_impact=True,executor=execute,**kwargs)
    def test_all_192_controls_and_24_restores_are_bounded(self):
        result=self.run_case(executor());self.assertEqual((result.outcome,result.code),('PASS','OK'));self.assertTrue(result.cleanup_ok)
        self.assertEqual(result.evidence['negative_count'],192);self.assertEqual(result.evidence['restored_cases'],24)
        self.assertTrue(all(c['before']==c['after'] for c in result.evidence['controls']))
        self.assertEqual(result.evidence['runtime_qualification'],'NOT_ESTABLISHED')
    def test_case_matrix_preserves_full_names_and_values(self):
        cases=list(m.cases());self.assertEqual(len(cases),24);self.assertNotIn('00_Preflight.sql',m.PHASES)
        self.assertEqual(len(m.PHASES),8);self.assertTrue(any(len(value or '')>256 for _,_,_,value in cases))
        self.assertTrue(any(name.endswith(' ') for _,_,name,_ in cases));self.assertTrue(any(value and value.endswith(' ') for _,_,_,value in cases))
    def test_snapshot_requires_whole_ordered_frames(self):
        raw=frame(state());self.assertEqual(m.decode(raw),state());lines=raw.splitlines()
        for wrong in ('\n'.join(lines[:-1]),'\n'.join([lines[1],lines[0],*lines[2:]]),raw+'\n'+lines[-1],raw.replace('DGN010_STATEPART|1|','OTHER|1|',1)):
            with self.subTest(wrong=wrong[:60]),self.assertRaises(ValueError):m.decode(wrong)
    def test_full_row_change_after_rejection_fails(self):
        result=self.run_case(executor(fault='snapshot_changed'));self.assertEqual(result.outcome,'FAIL');self.assertNotIn('negative_count',result.evidence)
    def test_mixed_native_error_never_attests_rejection(self):
        result=self.run_case(executor(fault='mixed'));self.assertEqual(result.outcome,'FAIL');self.assertEqual(result.evidence['completed_negative_count'],0)
    def test_unknown_stops_repair_cleanup_and_following_sql(self):
        execute=executor(fault='unknown');result=self.run_case(execute);self.assertTrue(result.client_end_unknown);self.assertFalse(result.cleanup_ok)
        self.assertEqual((result.outcome,result.code),('FAIL','FAIL_CLEANUP'));self.assertEqual(execute.calls[-1][0],'10_Setup.sql')
    def test_timeout_uses_one_recovery_budget_for_restore_and_cleanup(self):
        now=[0];starts=[];execute=executor(fault='timeout',clock=now)
        def begin():starts.append(now[0]);return now[0]+12
        result=self.run_case(execute,clock=lambda:now[0],cleanup_started=begin)
        self.assertEqual(len(starts),1);self.assertEqual(result.outcome,'FAIL')
        self.assertTrue(result.cleanup_ok);self.assertTrue(all(seconds<=12 for _,seconds in execute.calls[-4:]))
    def test_no_confirmation_stops_before_native(self):
        for confirmed,high in ((False,True),(True,False),(1,True)):
            with self.subTest(confirmed=confirmed,high=high),self.assertRaises(ValueError):m.run(p,executable='unused',server='unused',confirmed=confirmed,high_impact=high,executor=lambda *a,**k:self.fail('native'))
    def test_invalid_parent_deadline_stops_before_native(self):
        for value in (True,float('nan'),float('inf'),'300'):
            with self.subTest(value=value),self.assertRaises(ValueError):self.run_case(lambda *a,**k:self.fail('native'),normal_deadline=value)

if __name__=='__main__':unittest.main()
