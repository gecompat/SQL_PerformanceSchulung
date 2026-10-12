"""Gezielte Adaptergegenfälle mit tatsächlichen APIs und ausschließlich Fakehandles."""
import hashlib,importlib.util,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('con010_pool_client',ROOT/'Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_client.py')
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
SECRETS=tuple('Synthetic'+lane+'!'+('X'*40) for lane in 'ABCD')
TOKEN='0123456789ABCDEF'
TEXT=b"SELECT N'$(TenantSecretA)' AS Placeholder;"

class Handle:
    pid=123;returncode=0
    def __init__(self,status=0):self.status=status;self.polls=0;self.communications=[]
    def poll(self):
        self.polls+=1
        if isinstance(self.status,BaseException):raise self.status
        return self.status
    def communicate(self,timeout):self.communications.append(timeout);return ('SYNTHETIC_RESPONSE\n','')

class ClientTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name);self.inputs=self.folder/'inputs';(self.inputs/TOKEN).mkdir(parents=True)
        self.exe=self.folder/'sqlcmd.exe';self.exe.write_bytes(b'PURE_FAKE_EXECUTABLE')
        for n in range(3):(self.inputs/TOKEN/f'phase-{n:02}.sql').write_bytes(TEXT)
        self.clock=[100.0]
        for context in (patch.object(p,'INPUT_ROOT',self.inputs),patch.object(p.time,'monotonic',side_effect=lambda:self.clock[0]),patch.dict(os.environ,{'SQLCMDPASSWORD':SECRETS[0],'SqlcmdIni':'foreign','tenantsecreta':'foreign'})):
            context.start();self.addCleanup(context.stop)
        p.capture.collector_type();self.collector=p.capture._collector
        self.plan={0:{'Phase':'STATE','InputSha256':hashlib.sha256(TEXT).hexdigest()},1:{'Phase':'IDENTITY','InputSha256':hashlib.sha256(TEXT).hexdigest()},2:{'Phase':'DROP_DATABASE','InputSha256':hashlib.sha256(TEXT).hexdigest()}}
    def bind(self,**changes):
        values=dict(caller_scope='CON010_POOL_OWNER_SQLCMD',source_binding=p.source_map(),token=TOKEN,server='tcp:127.0.0.1,12345',executable=self.exe,executable_sha256=hashlib.sha256(self.exe.read_bytes()).hexdigest(),input_plan=self.plan,normal_end=400.0,required_cleanup_reserve_seconds=20)
        return p._bind_caller(**(values|changes))
    def client(self):return p.PoolSqlcmdClient(self.bind())
    def response(self,command,**changes):
        values=dict(command=tuple(command),returncode=0,stdout='SYNTHETIC_RESPONSE\n',stderr='',timed_out=False,duration_seconds=0.1)
        return self.collector.SqlcmdResult(**(values|changes))
    def execute(self,client,handle=None,**response_changes):
        handle=Handle() if handle is None else handle
        with patch.object(self.collector,'start_sqlcmd',return_value=handle) as start,patch.object(self.collector,'collect_process',side_effect=lambda actual,cmd,**kwargs:self.response(cmd,**response_changes)) as collect:
            result=client.execute(0,secret_values=SECRETS)
        return result,handle,start,collect
    def test_actual_builder_collects_same_handle_and_final_poll(self):
        handle=Handle();client=self.client()
        with patch.object(self.collector,'start_sqlcmd',return_value=handle) as start:
            result=client.execute(0,secret_values=SECRETS)
        command=start.call_args.args[0];environment=start.call_args.kwargs['environment']
        self.assertEqual(handle.polls,1);self.assertEqual(handle.communications,[14])
        self.assertEqual(command[command.index('-d')+1],p.DATABASE);self.assertEqual(command[command.index('-l')+1],'2')
        self.assertEqual(command[command.index('-U')+1],'sa');self.assertNotIn('-P',command)
        self.assertFalse(any(s in ' '.join(command) for s in SECRETS));self.assertFalse(any(k.casefold()=='sqlcmdini' for k in environment))
        self.assertEqual({k:v for k,v in environment.items() if k.casefold()=='tenantsecreta'},{'TenantSecretA':SECRETS[1]})
        self.assertEqual(result.capture['InputFileSha256'],hashlib.sha256(TEXT).hexdigest());self.assertEqual(result.capture['ServerRequestEnd'],'NOT_CAPTURED')
    def test_plain_target_source_and_caller_checks_before_start(self):
        for changes in ({'token':'BAD'},{'server':'tcp:localhost,12345'},{'normal_end':True},{'required_cleanup_reserve_seconds':True},{'source_binding':p.source_map()|{p.SOURCE_KEYS[0]:'0'*64}},{'caller_scope':'UNBOUND'}):
            with self.subTest(keys=list(changes)),self.assertRaises(ValueError):self.bind(**changes)
        with self.assertRaises(p.ClientFailure):p.PoolSqlcmdClient({})
        client=self.client()
        with patch.object(p,'source_map',return_value={}),patch.object(self.collector,'start_sqlcmd') as start,self.assertRaises(p.ClientFailure):client.execute(0,secret_values=SECRETS)
        start.assert_not_called()
    def test_input_and_environment_rejected_before_start(self):
        inputs=((TEXT+b'changed',False),(b':r other.sql',True),(b'!! forbidden',True),(b'\xef\xbb\xbf:r other.sql',True),(b'\xef\xbb\xbf!! forbidden',True),(b'SELECT $(Unexpected);',True),(SECRETS[0].encode(),True),(b'X'*160001,True))
        for raw,bind_actual in inputs:
            (self.inputs/TOKEN/'phase-00.sql').write_bytes(raw)
            self.plan[0]['InputSha256']=hashlib.sha256(raw if bind_actual else TEXT).hexdigest()
            client=self.client()
            with patch.object(self.collector,'start_sqlcmd') as start,self.assertRaises(p.ClientFailure):client.execute(0,secret_values=SECRETS)
            start.assert_not_called();self.assertFalse(client.unknown)
        (self.inputs/TOKEN/'phase-00.sql').write_bytes(TEXT);self.plan[0]['InputSha256']=hashlib.sha256(TEXT).hexdigest();client=self.client()
        with patch.dict(os.environ,{'SQLCMDPASSWORD':'foreign'}),patch.object(self.collector,'start_sqlcmd') as start,self.assertRaises(p.ClientFailure):client.execute(0,secret_values=SECRETS)
        start.assert_not_called()
    def test_budget_reserve_and_cleanup_clock_are_not_reset(self):
        client=self.client();client.begin_cleanup(146)
        with patch.object(self.collector,'start_sqlcmd') as start,self.assertRaises(p.ClientFailure):client.execute(0,secret_values=SECRETS)
        start.assert_not_called()
        with self.assertRaises(p.ClientFailure):client.begin_cleanup(160)
        self.assertEqual(client.begin_cleanup(146),146)
        for end in (True,None,float('nan')):
            with self.assertRaises((ValueError,TypeError)):self.client().begin_cleanup(end)
    def test_final_poll_exceptions_live_and_bool_are_sticky(self):
        for status in (None,True,OSError('private'),KeyboardInterrupt()):
            client=self.client()
            with self.subTest(status=type(status).__name__),self.assertRaises(p.ClientEndUnknown):self.execute(client,Handle(status))
            client.begin_cleanup(160)
            with patch.object(self.collector,'start_sqlcmd') as start,self.assertRaises(p.ClientEndUnknown):client.execute(2,secret_values=SECRETS,recovery=True)
            start.assert_not_called()
    def test_unknown_receipt_precedes_privacy_failure(self):
        for changes,status in (({'timed_out':True},0),({'returncode':-9},-9),({'returncode':1},0)):
            client=self.client()
            with self.subTest(changes=changes),self.assertRaises(p.ClientEndUnknown) as error:self.execute(client,Handle(status),stdout=SECRETS[0],**changes)
            self.assertNotIn(SECRETS[0],str(error.exception));self.assertIsNone(error.exception.__context__)
            client.begin_cleanup(160)
            with patch.object(self.collector,'start_sqlcmd') as start,self.assertRaises(p.ClientEndUnknown):client.execute(2,secret_values=SECRETS,recovery=True)
            start.assert_not_called()
    def test_credential_failure_never_returns_raw_or_digests(self):
        client=self.client()
        with self.assertRaises(p.ClientFailure) as error:self.execute(client,stdout=SECRETS[2].encode('utf-16-le').hex().upper())
        self.assertEqual(str(error.exception),'FAIL_CREDENTIAL_OUTPUT');self.assertEqual(error.exception.__dict__,{})
        self.assertFalse(client.unknown);self.assertTrue(client.failed)
    def test_collector_exception_or_missing_handle_never_allows_recovery(self):
        for failure in (OSError(SECRETS[0]),KeyboardInterrupt()):
            client=self.client();handle=Handle(0)
            with patch.object(self.collector,'start_sqlcmd',return_value=handle),patch.object(self.collector,'collect_process',side_effect=failure),self.assertRaises(p.ClientEndUnknown) as error:client.execute(0,secret_values=SECRETS)
            self.assertEqual(handle.polls,1);self.assertIsNone(error.exception.__context__);self.assertNotIn(SECRETS[0],str(error.exception))
        client=self.client()
        with patch.object(self.collector,'start_sqlcmd',side_effect=OSError(SECRETS[0])),self.assertRaises(p.ClientEndUnknown):client.execute(0,secret_values=SECRETS)
        self.assertTrue(client.unknown)
    def test_actual_phase_overrun_blocks_new_phase_even_before_total_deadline(self):
        client=self.client();handle=Handle()
        def completed(process,command,**kwargs):self.clock[0]=141;return self.response(command)
        with patch.object(self.collector,'start_sqlcmd',return_value=handle),patch.object(self.collector,'collect_process',side_effect=completed),self.assertRaises(p.ClientFailure) as error:client.execute(0,secret_values=SECRETS)
        self.assertEqual(str(error.exception),'FAIL_DEADLINE_AFTER_CLIENT');self.assertTrue(client.deadline_exceeded);self.assertFalse(client.unknown)
        client.begin_cleanup(201)
        with patch.object(self.collector,'start_sqlcmd') as start:
            for ordinal,recovery in ((1,False),(2,True)):
                with self.assertRaises(p.ClientFailure):client.execute(ordinal,secret_values=SECRETS,recovery=recovery)
        start.assert_not_called()
    def test_start_overhead_consumes_same_absolute_primary_window(self):
        client=self.client();handle=Handle()
        def started(command,**kwargs):self.clock[0]=107;return handle
        with patch.object(self.collector,'start_sqlcmd',side_effect=started),patch.object(self.collector,'collect_process',side_effect=lambda actual,cmd,**kwargs:self.response(cmd)) as collect:
            client.execute(0,secret_values=SECRETS)
        self.assertEqual(collect.call_args.kwargs['timeout_seconds'],7)
        self.clock[0]=100;client=self.client();client.begin_cleanup(160)
        def exhausted(command,**kwargs):self.clock[0]=115;return handle
        with patch.object(self.collector,'start_sqlcmd',side_effect=exhausted),patch.object(self.collector,'collect_process',side_effect=lambda actual,cmd,**kwargs:self.response(cmd)) as collect,self.assertRaises(p.ClientEndUnknown):client.execute(0,secret_values=SECRETS)
        self.assertEqual(collect.call_args.kwargs['timeout_seconds'],0)
        self.assertIs(collect.call_args.args[0],handle)
    def test_clock_snapshot_keeps_cleanup_reserve_absolute(self):
        client=self.client();client.begin_cleanup(150);handle=Handle();calls=[100]
        def ticking():value=calls[0];calls[0]+=1;return value
        def completed(actual,cmd,**kwargs):calls[0]=131;return self.response(cmd)
        with patch.object(p.time,'monotonic',side_effect=ticking),patch.object(self.collector,'start_sqlcmd',return_value=handle),patch.object(self.collector,'collect_process',side_effect=completed) as collect,self.assertRaises(p.ClientFailure) as error:client.execute(0,secret_values=SECRETS)
        self.assertEqual(str(error.exception),'FAIL_DEADLINE_AFTER_CLIENT')
        self.assertEqual(collect.call_args.kwargs['timeout_seconds'],3)
        self.assertTrue(client.deadline_exceeded)
    def test_post_return_source_or_collector_binding_failure_is_unknown(self):
        client=self.client();handle=Handle()
        def changed(process,command,**kwargs):return self.response(command,command=('foreign',))
        with patch.object(self.collector,'start_sqlcmd',return_value=handle),patch.object(self.collector,'collect_process',side_effect=changed),self.assertRaises(p.ClientEndUnknown):client.execute(0,secret_values=SECRETS)
        self.assertTrue(client.unknown)
    def test_nonzero_known_response_requires_explicit_recovery_clock(self):
        client=self.client();result,handle,start,collect=self.execute(client,Handle(1),returncode=1)
        self.assertEqual(result.capture['ReturnCode'],1);self.assertFalse(client.unknown);self.assertTrue(client.failed)
        with self.assertRaises(p.ClientFailure):client.execute(1,secret_values=SECRETS)
        with patch.object(self.collector,'start_sqlcmd') as start,self.assertRaises(p.ClientFailure):client.execute(2,secret_values=SECRETS,recovery=True)
        start.assert_not_called()

if __name__=='__main__':unittest.main()
