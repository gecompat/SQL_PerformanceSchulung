"""Neue reine Capture-/Privacy-/Budgetgegenfälle; keine echten Prozesse oder Provider."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import con010_pool_capture as c
SECRETS=tuple('Synthetic'+lane+'!'+('X'*40) for lane in 'ABCD')
INPUT=b"SELECT N'$(TenantSecretA)' AS Placeholder;"

def result(*,returncode=0,stdout='SYNTHETIC_RESPONSE\n',stderr='',timed_out=False,duration=0.25,command=('sqlcmd','-S','tcp:127.0.0.1,1','-i','OWN_INPUT.sql')):
    return c.collector_type()(command,returncode,stdout,stderr,timed_out,duration)
def capture(response=None,**changes):
    values={'ordinal':0,'pid':123,'final_poll':0,'input_bytes':INPUT,'secret_values':SECRETS,'source_binding':c.sources()};values.update(changes)
    return c.capture_sqlcmd(result() if response is None else response,**values)
def frames(text):
    units=len(text);count=(units+199)//200
    return ''.join(f'CON010_POOL_CAPTURE_PART|{n+1}|{count}|{units}|'+text[n*200:(n+1)*200].encode('utf-16-le').hex().upper()+'\n' for n in range(count))+'SQLPERF_SUMMARY|PASS|OK\n'

class CaptureTests(unittest.TestCase):
    def test_only_explicit_lf_crlf_collector_bytes_and_actual_capture_sha(self):
        original=c.COLLECTOR_PATH.read_bytes();lf=original.replace(b'\r\n',b'\n');crlf=lf.replace(b'\n',b'\r\n')
        self.assertEqual({hashlib.sha256(v).hexdigest() for v in (lf,crlf)},set(c.COLLECTOR_SHAS))
        contract=json.loads(c.CONTRACT_PATH.read_bytes().decode('utf-8'))
        self.assertEqual(set(contract['collector_sha256_variants']),set(c.COLLECTOR_SHAS))
        self.assertEqual(len(contract['collector_sha256_variants']),2)
        self.assertNotIn('collector_sha256',contract)
        c.collector_type()
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'sqlcmd_process.py'
            for raw in (lf,crlf):
                path.write_bytes(raw)
                with patch.object(c,'COLLECTOR_PATH',path):
                    record=capture();c.validate_capture(record)
                    self.assertEqual(record['CollectorSourceSha256'],hashlib.sha256(raw).hexdigest())
            path.write_bytes(lf+b'# foreign\n')
            with patch.object(c,'COLLECTOR_PATH',path),self.assertRaises(ValueError):capture()
    def test_actual_public_collector_result_and_configured_digest_scopes(self):
        class Process:
            pid=123;returncode=0
            def communicate(self,timeout):return ('SYNTHETIC_RESPONSE\n','')
        c.collector_type();module=c._collector
        with patch.object(module,'start_sqlcmd',side_effect=AssertionError('Kein Prozessstart')):
            response=module.collect_process(Process(),('sqlcmd','-i','OWN_INPUT.sql'),timeout_seconds=1)
            record=capture(response)
        self.assertEqual(record['InputFileSha256'],hashlib.sha256(INPUT).hexdigest())
        self.assertEqual(record['StdoutTextSha256'],hashlib.sha256(response.stdout.encode()).hexdigest())
        self.assertEqual(record['ServerRequestEnd'],'NOT_CAPTURED');self.assertEqual(record['ClientProcessEnd'],'KNOWN')
        self.assertEqual(record['InputDigestScope'],c.INPUT_SCOPE);self.assertEqual(record['OutputDigestScope'],c.OUTPUT_SCOPE)
    def test_exact_types_and_full_actual_result_fields(self):
        for changes in ({'pid':True},{'final_poll':True},{'ordinal':True},{'input_bytes':None},{'secret_values':None}):
            with self.subTest(changes=changes),self.assertRaises((ValueError,TypeError)):capture(**changes)
        for response in (result(returncode=True),result(timed_out=1),result(duration=float('nan'))):
            with self.assertRaises(ValueError):capture(response)
        with self.assertRaises(ValueError):c.capture_sqlcmd({},ordinal=0,pid=1,final_poll=0,input_bytes=INPUT,secret_values=SECRETS,source_binding=c.sources())
    def test_timeout_poll_mismatch_and_negative_exit_stay_sticky(self):
        for response,poll in ((result(timed_out=True),0),(result(),None),(result(),1),(result(returncode=-9),-9)):
            record=capture(response,final_poll=poll)
            self.assertEqual(record['ServerRequestEnd'],'UNKNOWN');self.assertTrue(record['UnknownSticky'])
            with self.assertRaises(c.ClientEndUnknown):c.require_followup(False,record)
        with self.assertRaises(c.ClientEndUnknown):c.require_followup(True,capture())
        self.assertEqual(c.require_followup(False,capture()),'REQUIRES_SEMANTIC_AND_SCOPE_GATE')
    def test_credential_rejection_precedes_capture_digests(self):
        variants=[(SECRETS[0].encode(),result()),(INPUT,result(stdout=SECRETS[1])),(INPUT,result(stderr=SECRETS[2].encode('utf-16-le').hex().upper())),(INPUT,result(stdout=SECRETS[3].encode().hex()))]
        for text,response in variants:
            with self.subTest(text_length=len(text)),patch.object(c,'source_gate'),patch.object(c,'collector_type',return_value=type(response)),patch.object(c.hashlib,'sha256',side_effect=AssertionError('Secretdigest verboten')):
                with self.assertRaises(c.CredentialOutputRejected) as error:c.capture_sqlcmd(response,ordinal=0,pid=123,final_poll=0,input_bytes=text,secret_values=SECRETS,source_binding={})
                self.assertEqual(str(error.exception),'FAIL_CREDENTIAL_OUTPUT');self.assertEqual(error.exception.__dict__,{})
    def test_outer_frame_and_inner_hex_cross_chunks_are_checked(self):
        payload=json.dumps({'Pad':'X'*189,'MessageHex':SECRETS[0].encode('utf-16-le').hex().upper()})
        wire=frames(payload)
        self.assertNotIn(SECRETS[0].encode('utf-16-le').hex().upper(),wire)
        with self.assertRaises(c.CredentialOutputRejected):capture(result(stdout=wire))
        with self.assertRaises(c.CredentialOutputRejected):capture(result(stdout='CON010_POOL_CAPTURE_PART|1|'+SECRETS[0]+'|1|00'))
        self.assertEqual(c.decode_supported_frames(frames('{"Value":"SYNTHETIC"}')),'{"Value":"SYNTHETIC"}')
        with self.assertRaises(ValueError):capture(result(stdout=wire+'unexpected'))
    def test_sources_are_existing_public_and_not_future_or_private_pins(self):
        existing=c.sources();self.assertEqual(set(existing),set(c.SOURCE_KEYS))
        for changed in (existing|{'Runtime/FutureProducer.py':'0'*64},{k:v for k,v in existing.items() if k!=c.SOURCE_KEYS[0]},existing|{c.SOURCE_KEYS[-1]:'0'*64}):
            with self.assertRaises(ValueError):capture(source_binding=changed)
    def test_full_capture_summary_rejects_numeric_and_missing_aliases(self):
        record=capture();out=c.summary([record]);self.assertEqual(out['status'],'WARN');self.assertEqual(out['captures'],1)
        self.assertEqual(out['runtime_qualification'],'NOT_ESTABLISHED')
        for change in (lambda v:v.pop('StdoutTextSha256'),lambda v:v.update(TimedOut=True),lambda v:v.update(ReturnCode=True),lambda v:v.update(InputDigestScope='SERVER_EXECUTED_SQL'),lambda v:v.update(CredentialSafety=True)):
            data=copy.deepcopy(record);change(data)
            with self.assertRaises(ValueError):c.summary([data])
        for forbidden in ('Pid','Sha256','SYNTHETIC_RESPONSE','OWN_INPUT','SQLCMDPASSWORD'):self.assertNotIn(forbidden,json.dumps(out))
    def test_reaping_caps_are_reserved_inside_remaining_budget(self):
        self.assertEqual(c.collector_wait_seconds(60,40,required_cleanup_reserve_seconds=20),14)
        self.assertEqual(c.collector_wait_seconds(50,40,required_cleanup_reserve_seconds=20),4)
        for remaining,cap,reserve in ((46,40,20),(60,26,20),(0,40,20),(True,40,20),(60,40,0),(60,40,True)):
            actions=[]
            with self.assertRaises((TimeoutError,ValueError)):
                value=c.collector_wait_seconds(remaining,cap,required_cleanup_reserve_seconds=reserve);actions.append(value)
            self.assertEqual(actions,[])
    def test_dotnet_configured_text_is_private_checked_and_only_declared(self):
        values={'ordinal':0,'operation':'SCALAR','lane':'A','returned':True,'configured_text':'SELECT 1;','secret_values':SECRETS,'source_binding':c.sources()}
        record=c.capture_dotnet(**values);out=c.validate_dotnet_record(record)
        self.assertEqual(out['runtime_qualification'],'NOT_ESTABLISHED');self.assertEqual(record['TextDigestScope'],'CLIENT_CONFIGURED_SECRET_FREE_TEXT')
        with self.assertRaises(c.CredentialOutputRejected):c.capture_dotnet(**(values|{'configured_text':SECRETS[0]}))
        for values2 in (values|{'returned':False},values|{'operation':'OPEN','configured_text':None},values|{'operation':'CLOSE','configured_text':None}):c.validate_dotnet_record(c.capture_dotnet(**values2))
        for key,value in (('Returned',True),('TextDigestScope','SERVER_EXECUTED_SQL')):
            bad=dict(record)
            if key=='Returned':bad['RequestEnd']='UNKNOWN'
            else:bad[key]=value
            with self.assertRaises(ValueError):c.validate_dotnet_record(bad)
        disguised=type('str',(str,),{})
        with self.assertRaises(ValueError):c.capture_dotnet(**(values|{'operation':disguised('SCALAR')}))
        with self.assertRaises(ValueError):c.validate_dotnet_record(record|{'Lane':disguised('A')})
    def test_public_commandbuilder_keeps_password_outside_argv(self):
        c.collector_type();module=c._collector
        with tempfile.TemporaryDirectory() as folder,patch.dict(module.os.environ,{'SQLCMDPASSWORD':SECRETS[0]}):
            path=Path(folder)/'own.sql';path.write_bytes(INPUT)
            command=module.build_sqlcmd_command(executable='sqlcmd',server='tcp:127.0.0.1,1',database='master',script=path,auth='sql',username='sa')
            self.assertNotIn('-P',command);self.assertNotIn(SECRETS[0],command)
        with self.assertRaises(ValueError):capture(result(command=('sqlcmd','-P',SECRETS[0])))
if __name__=='__main__':unittest.main()
