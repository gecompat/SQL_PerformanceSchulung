"""Neue Poolproducergegenfälle; ausschließlich Fakehandles und synthetische Records."""
import copy,hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
ROOT=Path(__file__).resolve().parents[2];FOLDER=ROOT/'Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation'
sys.path.insert(0,str(FOLDER))
import run_pool_profile as p
import pool_profile_evidence as e
import pool_profile_inputs as s
SECRETS=tuple('Synthetic'+lane+'!'+('X'*40) for lane in 'ABCD')
TOKEN='0123456789ABCDEF';SIDS={'A':'A'*32,'B':'B'*32,'U':'C'*32}

def container():return {'Id':'a'*64,'Name':'sqlperf-pool-public-'+TOKEN.lower(),'Image':p.IMAGE,'Owner':p.OWNER,'Memory':6*1024**3,'NanoCpus':4*10**9,'Mounts':[],'Binds':None,'VolumesFrom':None,'Ports':{'1433/tcp':[{'HostIp':'127.0.0.1','HostPort':'12345'}]}}
def operations():
    forms=e.public_sql_forms();h=lambda text:hashlib.sha256(text.encode()).hexdigest()
    owner=h(forms['OwnGuard']+'SELECT 1;');read=h(forms['Read']);view=h(forms['OwnGuard']+forms['OwnerRead']);spoof=h("EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=@Tenant;SELECT 1;")
    refs=[('OPEN','OWNER',0,None)]
    for n,lane in enumerate(e.ORDER,1):refs.extend((a,b,n,d) for a,b,d in (('SCALAR','OWNER',owner),('OPEN',lane,None),('SCALAR',lane,read),('SCALAR','OWNER',owner),('SCALAR',lane,spoof),('SCALAR',lane,read),('SCALAR','OWNER',view),('CLOSE',lane,None)))
    refs.extend(('CLOSE',lane,0,None) for lane in e.ORDER)
    absent="DECLARE @J nvarchar(max)=(SELECT LOWER(CONVERT(varchar(36),connection_id)) ConnectionId FROM sys.dm_exec_connections WHERE connection_id IN(CONVERT(uniqueidentifier,@Id1),CONVERT(uniqueidentifier,@Id2),CONVERT(uniqueidentifier,@Id3)) ORDER BY connection_id FOR JSON PATH);SELECT COALESCE(@J,N'[]');"
    refs.extend((('SCALAR','OWNER',0,h(forms['OwnGuard']+absent)),('CLOSE','OWNER',0,None)))
    return [dict(Ordinal=n,Operation=kind,Lane=lane,Checkout=checkout,Returned=True,RequestEnd='RETURNED_TO_CALLER',ConfiguredTextSha256=digest,TextScope='CLIENT_CONFIGURED_SECRET_FREE_TEXT' if kind=='SCALAR' else 'NOT_APPLICABLE') for n,(kind,lane,checkout,digest) in enumerate(refs)]
def receipt():
    result={'Status':'PASS','RequestEnd':'RESPONSE_RECEIVED','PoolCleanup':'ACTUAL_CLEAR_CLOSE_AND_NEW_ABSENCE','Records':[],'Operations':operations(),'RemainingConnections':[],'Token':TOKEN,'Fault':None}
    for n,lane in enumerate(e.ORDER,1):
        index={'A':1,'B':2,'U':3}[lane];login,user=e.LOGINS[lane]
        identity=dict(DatabaseId=42,DatabaseName=e.DATABASE,SuserName=login,OriginalLogin=login,UserName=user,ServerSid=SIDS[lane],OriginalSid=SIDS[lane],UserSid=SIDS[lane],SessionId=10+index)
        rows=[]
        if lane!='U':
            text='Synthetische Quelle '+lane;raw=text.encode('utf-16-le')
            rows=[dict(Id=index,TenantId=index,Content=text,ContentBytes=len(raw),ContentHex=raw.hex().upper(),VectorJson='[1,0,0]',Dimensions=3,BaseType='float32',Distance=0)]
        before=dict(Identity=identity,Rows=rows,Context=None);after=dict(Identity=copy.deepcopy(identity),Rows=copy.deepcopy(rows),Context=2 if lane=='A' else 1)
        owner=dict(SessionId=10+index,ConnectionId=f'{index:08x}-0000-4000-8000-000000000001',ConnectTime='2026-10-13T00:00:00.000',LoginTime='2026-10-13T00:00:00.000',LoginName=login,OriginalLoginName=login,Sid=SIDS[lane],DatabaseId=42,ProgramName='SQLPERF_POOLPUBLIC_'+TOKEN+'_'+lane,NetTransport='TCP',AuthScheme='SQL')
        result['Records'].append(dict(Ordinal=n,Lane=lane,ClientConnectionId=f'{n:08x}-0000-4000-8000-000000000002',ConnectionState='Open',PoolKeySha=str(index)*64,CredentialOrdinal=index,Before=before,After=after,Owner=owner))
    return result
class Handle:
    pid=123
    def __init__(self,status=0):self.status=status;self.polls=0
    def poll(self):
        self.polls+=1
        if isinstance(self.status,BaseException):raise self.status
        return self.status

class ProducerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.folder=Path(self.temp.name)
        p.capture.collector_type();self.collector=p.capture._collector
        self.time=100.0
        patcher=patch.object(p.time,'monotonic',side_effect=lambda:self.time);patcher.start();self.addCleanup(patcher.stop)
    def producer(self):
        q=p.Producer.__new__(p.Producer)
        q.candidate=1;q.token=TOKEN;q.name='sqlperf-pool-public-'+TOKEN.lower();q.values=SECRETS;q.sids=SIDS;q.dbid=42;q.oid=100;q.held=None;q.baseline={};q.sources=p.source_map();q.normal_end=400;q.cleanup_end=None;q.unknown=False;q.deadline_failed=False;q.cid='a'*64;q.port='12345';q.ordinal=0;q.captures=[];q.transcripts=[];q.negative_states=[];q.namespace_witness=None;q.create_unknown=False;q.remove_unknown=False;q.remove_attempted=False;q.create_attempts=0;q.namespace_calls=[];q.no_create_witness=None;q.child_evidence=None;q.extra_inputs=[];q.pool_ready=False;q.sql_absent=False;q.namespace_absent=False;q.inputs_absent=False;q.started=True;q.clients=[]
        q.folder=self.folder/(TOKEN+str(len(list(self.folder.iterdir()))));q.folder.mkdir();q.gate=lambda:(_ for _ in ()).throw(p.Unknown()) if q.unknown else None
        q.inspect=lambda cleanup=False:(q.cid,q.port)
        return q
    def child_response(self,q,data,handle=None):
        handle=Handle() if handle is None else handle
        response=lambda process,command,**kwargs:self.collector.SqlcmdResult(tuple(command),0,json.dumps(data),'',False,0.1)
        return patch.object(self.collector,'start_sqlcmd',return_value=handle),patch.object(self.collector,'collect_process',side_effect=response)
    def test_actual_namespace_cleanup_preserves_full_inspect_and_two_absence_outputs(self):
        q=self.producer();q.bound_at_start=container();q.inspect=p.Producer.inspect.__get__(q)
        q.podman=Mock(side_effect=['a'*64+'\n',json.dumps(container()),'a'*64+'\n','',''])
        q.namespace_cleanup()
        self.assertTrue(q.namespace_absent);self.assertEqual(q.last_inspect,container())
        self.assertEqual(q.namespace_witness['CidQuery'],'');self.assertEqual(q.namespace_witness['NameQuery'],'')
        e.validate_namespace(q.namespace_witness,TOKEN,'a'*64,'12345')
        self.assertEqual([call.args[1] for call in q.podman.call_args_list],[3,3,8,3,3])
        self.assertEqual(q.podman.call_args_list[2].args[0],['rm','-f','--time=0','a'*64])
        q=self.producer();q.bound_at_start=container();q.inspect=p.Producer.inspect.__get__(q)
        q.podman=Mock(side_effect=['b'*64+'\n',json.dumps(container())])
        with self.assertRaises(p.Failure):q.namespace_cleanup()
        self.assertEqual(q.podman.call_count,2);self.assertFalse(q.namespace_absent)
    def test_rebound_namespace_resources_label_mount_and_complete_sources_rejected(self):
        sources=p.source_map();self.assertEqual(set(sources),set(e.PROFILE_SOURCE_KEYS));self.assertEqual(len(e.profile_sources(sources)),15)
        for replacement in ({key:value for key,value in sources.items() if key!=next(iter(sources))},sources|{'Runtime/InventedSource.py':'0'*64},sources|{next(iter(sources)):'0'*64}):
            with self.assertRaises(ValueError):e.profile_sources(replacement)
        original={'BoundAtStart':container(),'BoundBeforeRemove':container(),'CidQuery':'','NameQuery':'','InputFiles':[]}
        e.validate_namespace(original,TOKEN,'a'*64,'12345')
        for changes in ({'NanoCpus':2*10**9},{'NanoCpus':True},{'Owner':'FOREIGN'},{'Mounts':[{}]},{'Name':'foreign'},{'Id':'b'*64},{'Ports':{'1433/tcp':[{'HostIp':'localhost','HostPort':'12345'}]}}):
            rebound=copy.deepcopy(original)
            # Beide Aufnahmen kohärent rebinden; nicht nur ein einfacher Vor/Nachvergleich.
            rebound['BoundAtStart'].update(changes);rebound['BoundBeforeRemove'].update(changes)
            with self.subTest(keys=list(changes)),self.assertRaises(ValueError):e.validate_namespace(rebound,TOKEN,'a'*64,'12345')
        for field in ('CidQuery','NameQuery'):
            rebound=copy.deepcopy(original);rebound[field]='a'*64
            with self.assertRaises(ValueError):e.validate_namespace(rebound,TOKEN,'a'*64,'12345')
    def test_namespace_env_keeps_only_observed_appdata_root_and_no_credentials(self):
        inherited={'Path':'synthetic-path','APPDATA':'synthetic-config','LOCALAPPDATA':'unused-config','SQLCMDPASSWORD':SECRETS[0],'TenantSecretA':SECRETS[1],'ARBITRARY':'foreign','SQLCMDINI':'foreign'}
        before=dict(inherited);environment=p.namespace_environment(inherited)
        self.assertEqual(environment,{'PATH':'synthetic-path','APPDATA':'synthetic-config'});self.assertEqual(inherited,before)
        self.assertEqual(p.client._private_environment(SECRETS)['SQLCMDPASSWORD'],SECRETS[0])
    def test_namespace_known_failure_captures_actual_channels_before_semantics(self):
        q=self.producer();q.cli='PURE_FAKE_PODMAN'
        command=['PURE_FAKE_PODMAN','ps','-a'];response=p.subprocess.CompletedProcess(command,125,'','synthetic-configuration-error')
        with patch.object(p.subprocess,'run',return_value=response),self.assertRaises(p.Failure):q.podman(['ps','--no-trunc','-a'],3)
        self.assertFalse(q.unknown);self.assertEqual(q.create_attempts,0)
        self.assertEqual(q.namespace_calls[0]['Command'],command);self.assertEqual(q.namespace_calls[0]['ReturnCode'],125);self.assertEqual(q.namespace_calls[0]['Stderr'],'synthetic-configuration-error');self.assertEqual(q.namespace_calls[0]['ProcessEnd'],'SUBPROCESS_RUN_RETURNED')
    def test_not_created_failure_has_fresh_name_input_proof_without_cid(self):
        q=self.producer();q.cid=None;q.started=False
        q.start_namespace=Mock(side_effect=p.Failure('FAIL_NAMESPACE_COMMAND'));q.sql_cleanup=Mock();q.namespace_cleanup=Mock()
        response=p.subprocess.CompletedProcess(['PURE_FAKE'],0,'','');q.cli='PURE_FAKE_PODMAN'
        with patch.object(p.subprocess,'run',return_value=response):result=q.run()
        q.sql_cleanup.assert_not_called();q.namespace_cleanup.assert_not_called()
        self.assertEqual(result.status,'FAIL');self.assertEqual(result.counts['create_end'],'NOT_STARTED');self.assertEqual(result.evidence['NoCreate']['State'],'NOT_CREATED');self.assertIsNone(q.cid);self.assertTrue(q.inputs_absent);self.assertEqual(result.counts['sql_absence'],'NOT_ESTABLISHED')
    def test_typed_source_bound_prior_no_create_supplement_preserves_history(self):
        directory=self.folder/'controls'/'candidate1';directory.mkdir(parents=True)
        sources=p.source_map();entry={'candidate':1,'status':'FAIL','closed':False,'unknown':False,'namespace_absent':False,'inputs_absent':True,'source_sha256':sources,'cid':None,'name':'sqlperf-pool-public-'+TOKEN.lower(),'image':p.IMAGE,'owner':p.OWNER,'sql_absence':'NOT_ESTABLISHED'}
        original={'status':'FAIL','code':'FAIL_NAMESPACE_COMMAND','source_sha256':sources,'actual_snapshot':{'cid':None,'unknown':False,'sql_calls':[],'child':None,'token':TOKEN}}
        dump=lambda name,data:(directory/name).write_bytes(json.dumps(data).encode())
        dump('actual-result.json',original);dump('public-ledger.json',[entry]);dump('namespace-env-diagnosis.json',[{'kind':'LATER_READ_ONLY_DIAGNOSIS'}])
        for key in sources:
            path=directory/'source-archive'/key;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/key).read_bytes())
        checkpoint={'status':'KNOWN_PRE_EFFECT_FAIL_RECORDED','candidate':1,'result_sha256':p.digest(directory/'actual-result.json'),'diagnosis_sha256':p.digest(directory/'namespace-env-diagnosis.json'),'sqlcmd_calls':0,'pool_children':0,'containers_created':0,'create_call_reached':False,'client_end_unknown':False,'fresh_name_query':'ACTUAL_EMPTY_READ_ONLY_DIAGNOSIS','cid':'NOT_CREATED','sql_cleanup':'NOT_ESTABLISHED','ledger_historical_closed':False,'retry':'ONLY_CHANGED_SOURCE_NEW_BOUND_ADMISSION'}
        dump('root-fail-checkpoint.json',checkpoint)
        inputroot=self.folder/'inputs'
        proof={'contract':'CON010_POOLPUBLIC_NOT_CREATED_V1','candidate':1,'original_ledger_sha256':p.digest(directory/'public-ledger.json'),'original_result_sha256':p.digest(directory/'actual-result.json'),'checkpoint_sha256':p.digest(directory/'root-fail-checkpoint.json'),'diagnosis_sha256':p.digest(directory/'namespace-env-diagnosis.json'),'current_source_sha256':sources,'namespace_query':{'Command':[p.shutil.which('podman'),'ps','-a','--filter','name=^'+entry['name']+'$','--format','{{.ID}}'],'ReturnCode':0,'Stdout':'','Stderr':'','ProcessEnd':'SUBPROCESS_RUN_RETURNED'},'input_folder':str(inputroot/TOKEN),'input_files':[],'create_attempts':0,'cid':'NOT_CREATED','sql_absence':'NOT_ESTABLISHED'}
        def admission(data):dump('no-created-closure.json',data);return {'prior_no_create_sha256':{'1':p.digest(directory/'no-created-closure.json')}}
        with patch.object(p,'CONTROL',directory.parent),patch.object(p.client,'INPUT_ROOT',inputroot):
            self.assertTrue(p.prior_no_create(entry,1,admission(proof)))
            for changed in (proof|{'candidate':True},proof|{'create_attempts':True},proof|{'sql_absence':'PASS'},proof|{'current_source_sha256':sources|{next(iter(sources)):'0'*64}},proof|{'namespace_query':proof['namespace_query']|{'ReturnCode':True}},proof|{'cid':'a'*64}):
                with self.assertRaises(p.Failure):p.prior_no_create(entry,1,admission(changed))
            # Nach Kandidat2-Reservation zählt nur das archivierte historische Prefix.
            (directory.parent/'public-ledger.json').write_bytes(json.dumps([entry,{'candidate':2,'status':'RESERVED'}]).encode())
            self.assertTrue(p.prior_no_create(entry,1,admission(proof)))
        self.assertFalse(entry['closed']);self.assertEqual(json.loads((directory/'public-ledger.json').read_bytes()),[entry])
    def test_supported_container_id_case_full_ps_and_immediate_rm_argv(self):
        q=self.producer();q.bound_at_start=container();q.inspect=p.Producer.inspect.__get__(q)
        self.assertIn('"Id":{{json .ID}}',p.INSPECT);self.assertNotIn('{{json .Id}}',p.INSPECT)
        q.podman=Mock(side_effect=['a'*64+'\n',json.dumps(container()),'a'*64+'\n','',''])
        q.namespace_cleanup()
        for call in q.podman.call_args_list:
            argv=call.args[0]
            if argv[0]=='ps':self.assertIn('--no-trunc',argv);self.assertEqual(argv[-1],'{{.ID}}')
            elif argv[0]=='rm':self.assertEqual(argv,['rm','-f','--time=0','a'*64]);self.assertEqual(call.args[1],8)
        q=self.producer();q.folder.rmdir();q.podman=Mock(side_effect=['',p.IMAGE,'a'*64+'\n',json.dumps(container())]);q.inspect=p.Producer.inspect.__get__(q)
        q.start_namespace()
        self.assertEqual(q.podman.call_args_list[1].args[0][-1],'{{.Id}}')
    def test_mutative_remove_missing_end_is_sticky_and_no_second_remove_or_sql(self):
        for failure in (p.subprocess.TimeoutExpired('PURE_FAKE',8),OSError('synthetic'),None):
            q=self.producer();q.cli='PURE_FAKE_PODMAN'
            mock=patch.object(p.subprocess,'run',side_effect=failure) if failure is not None else patch.object(p.subprocess,'run',return_value=None)
            with mock as native,self.assertRaises(p.Failure):q.podman(['rm','-f','--time=0',q.cid],8,True)
            self.assertTrue(q.unknown);self.assertTrue(q.remove_unknown);self.assertTrue(q.remove_attempted)
            with patch.object(p.subprocess,'run') as follow,self.assertRaises(p.Unknown):q.podman(['rm','-f','--time=0',q.cid],8,True)
            follow.assert_not_called()
            with self.assertRaises(p.Unknown):q.sql('SELECT 1;')
    def test_recorded_unknown_wave_stop_cannot_admit_native_candidate(self):
        control=self.folder/'stopped';(control/'candidate2').mkdir(parents=True)
        (control/'candidate2/namespace-recovery-unknown.json').write_bytes(json.dumps({'contract':'CON010_POOLPUBLIC_NAMESPACE_RECOVERY_UNKNOWN_V1','status':'RESOURCE_ABSENT_REQUEST_END_UNKNOWN','mutative_request_end':'UNKNOWN_STICKY'}).encode())
        with patch.object(p,'CONTROL',control),self.assertRaises(p.Failure) as error:p.admitted(3,{},[])
        self.assertEqual(str(error.exception),'FAIL_WAVE_STOP_AFTER_UNKNOWN')
    def test_provider_skip_has_no_admission_or_native_effect(self):
        with patch.object(p,'provider_available',return_value=False),patch.object(p,'admitted',side_effect=AssertionError('Keine Admission')),patch.object(p.subprocess,'run',side_effect=AssertionError('Kein Native')):
            result=p.run(1,{})
        self.assertEqual((result.status,result.code),('SKIP','SKIP_PROVIDER_UNAVAILABLE'));self.assertEqual(result.counts['containers'],0)
    def test_mutative_namespace_create_timeout_is_sticky(self):
        for failure in (p.subprocess.TimeoutExpired('PURE_FAKE',1),OSError('synthetic'),KeyboardInterrupt()):
            q=self.producer();q.cli='PURE_FAKE_PODMAN';q.admission={};q.ledger=[]
            with patch.object(p.subprocess,'run',side_effect=failure),self.assertRaises(p.Failure):q.podman(['run'],1,creating=True)
            self.assertTrue(q.unknown);self.assertTrue(q.create_unknown)
            with self.assertRaises(p.Unknown):q.sql('SELECT 1;')
    def test_projected_namespace_full_identity_port_resources_and_no_env(self):
        data=container();self.assertEqual(p.projected_container(data,data['Name']),('a'*64,'12345'))
        for changes in ({'Id':'b'*64},{'Memory':True},{'Mounts':[{}]},{'Owner':'FOREIGN'},{'Image':'tag'},{'Env':[SECRETS[0]]}):
            bad=data|changes
            with self.subTest(keys=list(changes)),self.assertRaises(p.Failure):p.projected_container(bad,data['Name'],'a'*64,'12345')
        bad=copy.deepcopy(data);bad['Ports']['1433/tcp'][0]['HostIp']='localhost'
        with self.assertRaises(p.Failure):p.projected_container(bad,data['Name'])
    def test_declared_admission_protected_types_fail_before_effect(self):
        for candidate,admission in ((True,{}),(0,{}),(7,{}),(1,{}),(1,{'status':'ADMITTED','candidate':True})):
            with self.assertRaises(p.Failure):p.admitted(candidate,admission,[])
    def test_startup_known_transient_only_and_mixed_errors_rejected(self):
        tcp='Sqlcmd: Error: Microsoft ODBC Driver 18 for SQL Server : TCP Provider: synthetic refused.'
        self.assertTrue(p.startup_retry('',tcp+'\n.\nSqlcmd: Error: Microsoft ODBC Driver 18 for SQL Server : Login timeout expired.'))
        for stdout,stderr in ((tcp,'Msg 51003, Level 16, State 1\nFAIL'),(tcp,'extra'),(tcp+'\nunknown',''),('','.')):
            self.assertFalse(p.startup_retry(stdout,stderr))
    def test_actual_sql_startup_branch_retains_known_connect_capture(self):
        q=self.producer();q.sqlcmd=self.folder/'sqlcmd.exe';q.sqlcmd.write_bytes(b'PURE_FAKE')
        text="SET NOCOUNT ON;SELECT 'POOLPUBLIC_READY';"
        stderr='Sqlcmd: Error: Microsoft ODBC Driver 18 for SQL Server : Login timeout expired.'
        raw=self.collector.SqlcmdResult(('sqlcmd',),1,'',stderr,False,0.1)
        cap=p.capture.capture_sqlcmd(raw,ordinal=0,pid=123,final_poll=1,input_bytes=text.encode(),secret_values=SECRETS,source_binding=p.capture.sources())
        adapter=Mock();adapter.unknown=False;adapter.deadline_exceeded=False;adapter.execute.return_value=p.client.ClientResult(cap,'',stderr)
        with patch.object(p.client,'_bind_caller',return_value=object()),patch.object(p.client,'PoolSqlcmdClient',return_value=adapter):
            self.assertIsNone(q.sql(text,'PREFLIGHT',startup=True))
        self.assertFalse(q.unknown);e.validate_call(q.transcripts[0]);self.assertEqual(q.transcripts[0]['InputText'],text)
        self.assertFalse((q.folder/'phase-00.sql').exists())
    def test_full_operations_text_return_type_and_order_bound(self):
        rows=operations();self.assertEqual(len(e.validate_operations(rows)),57)
        for changes in ({'ConfiguredTextSha256':'0'*64},{'Returned':False},{'Ordinal':True},{'Checkout':True},{'RequestEnd':'KNOWN'}):
            bad=copy.deepcopy(rows);bad[1].update(changes)
            with self.subTest(keys=list(changes)),self.assertRaises(ValueError):e.validate_operations(bad)
        bad=copy.deepcopy(rows);bad[1]['ConfiguredTextSha256']=bad[3]['ConfiguredTextSha256']
        with self.assertRaises(ValueError):e.validate_operations(bad)
    def test_pool_physical_reuse_reset_sid_and_client_guid_metadata(self):
        data=receipt();e.validate_pool(data,SIDS,42,TOKEN)
        # Client-GUIDs sind absichtlich beim zweiten Checkout verschieden.
        for change in (lambda r:r['Records'][3]['Owner'].update(ConnectionId='ffffffff-0000-4000-8000-000000000001'),lambda r:r['Records'][3]['Before'].update(Context=2),lambda r:r['Records'][0]['Before']['Identity'].update(ServerSid='D'*32),lambda r:r['Records'][1].update(PoolKeySha='1'*64)):
            bad=copy.deepcopy(data);change(bad)
            with self.assertRaises(ValueError):e.validate_pool(bad,SIDS,42,TOKEN)
    def test_receipt_unknown_precedes_nested_credential_capture_failure(self):
        q=self.producer();data={'RequestEnd':'UNKNOWN','MessageHex':SECRETS[0].encode('utf-16-le').hex().upper()}
        a,b=self.child_response(q,data)
        with a,b,self.assertRaises(p.capture.CredentialOutputRejected):q.child()
        self.assertTrue(q.unknown)
        with self.assertRaises(p.Unknown):q.sql('SELECT 1;')
        self.assertTrue((q.folder/'child-plan.json').exists())
    def test_child_poll_unknown_or_timeout_never_allows_sql(self):
        for status in (None,True,OSError('synthetic'),KeyboardInterrupt()):
            q=self.producer();a,b=self.child_response(q,receipt(),Handle(status))
            with a,b,self.assertRaises(p.Unknown):q.child()
            self.assertTrue(q.unknown)
            q.folder.rmdir() if not any(q.folder.iterdir()) else None
            # Eigene unbekannte Inputakte bleibt erhalten, separater Testtokenordner.
            q.folder.rename(q.folder.with_name(q.folder.name+'held'))
    def test_child_semantic_fail_preserved_and_known_input_closes_after_namespace(self):
        q=self.producer();data=receipt();data.update(Status='FAIL',Records=[],PoolCleanup='NOT_ESTABLISHED',Fault={'Phase':'OWNER_OPEN','Types':['System.Exception'],'Code':None})
        q.start_namespace=Mock();q.setup=Mock();q.negatives=Mock();q.sql_cleanup=Mock(side_effect=p.Failure('FAIL_CLEANUP_LEASE'))
        def cleanup():q.namespace_absent=True;q.namespace_witness={'BoundBeforeRemove':container(),'CidQuery':'','NameQuery':'','InputFiles':None}
        q.namespace_cleanup=cleanup;a,b=self.child_response(q,data)
        with a,b:result=q.run()
        self.assertEqual(result.status,'FAIL');self.assertFalse(q.unknown);self.assertTrue(q.inputs_absent)
        self.assertEqual(result.evidence['Child']['Receipt'],data);self.assertEqual(result.counts['primary_code'],'FAIL_RESULT_CONTRACT');self.assertEqual(result.counts['sql_cleanup_code'],'FAIL_SQL_CLEANUP');self.assertIsNone(result.counts['namespace_cleanup_code'])
    def test_actual_child_source_input_channel_digest_bindings(self):
        q=self.producer();a,b=self.child_response(q,receipt())
        with a,b:returned,envelope=q.child()
        self.assertEqual(envelope['Kind'],'POWERSHELL_POOL_CHILD');e.validate_child(envelope,returned)
        self.assertEqual(envelope['StdoutSha256'],hashlib.sha256(q.child_evidence['Stdout'].encode()).hexdigest());self.assertEqual(envelope['ScriptSha256'],p.digest(FOLDER/'pool_profile.ps1'))
        self.assertFalse((q.folder/'child-plan.json').exists())
        for changes in ({'Pid':True},{'ReturnCode':True},{'ServerRequestEnd':'TDS_CONFIRMED'},{'TimedOut':True}):
            with self.assertRaises(ValueError):e.validate_child(envelope|changes,returned)
    def test_expired_same_clock_before_child_and_after_return_blocks_progress(self):
        q=self.producer();q.cleanup_end=120
        with patch.object(self.collector,'start_sqlcmd') as start,self.assertRaises(TimeoutError):q.child()
        start.assert_not_called()
        q=self.producer();handle=Handle()
        def late(process,command,**kwargs):self.time=141;return self.collector.SqlcmdResult(tuple(command),0,json.dumps(receipt()),'',False,0.1)
        with patch.object(self.collector,'start_sqlcmd',return_value=handle),patch.object(self.collector,'collect_process',side_effect=late),self.assertRaises(p.Failure):q.child()
        self.assertTrue(q.deadline_failed)
    def test_composer_inputs_sid_bool_override_and_full_output_transport(self):
        for value in (True,None,'5;DROP DATABASE master'):
            with self.assertRaises(ValueError):s.checked(value)
        with self.assertRaises(ValueError):s.create_logins(42,SIDS|{'A':"A';DROP LOGIN sa;--"})
        with self.assertRaises(ValueError):s.bound(42,{'SQLPERF.Project':'x'})
        self.assertEqual(e.decode('CON010_POOL_CAPTURE_PART|1|1|2|7B007D00\nSQLPERF_SUMMARY|PASS|OK'),{})
        with self.assertRaises(ValueError):e.decode('CON010_POOL_CAPTURE_PART|1|1|2|7B007D00\nextra\nSQLPERF_SUMMARY|PASS|OK')
    def test_failure_cleanup_codes_stay_separate_and_unknown_skips_sql(self):
        q=self.producer();q.start_namespace=Mock(side_effect=p.Unknown());q.setup=Mock();q.negatives=Mock();q.unknown=True;q.sql_cleanup=Mock();q.namespace_cleanup=Mock(side_effect=p.Failure('FAIL_NAMESPACE_COMMAND'))
        result=q.run();q.sql_cleanup.assert_not_called()
        self.assertEqual(result.counts['primary_code'],'CLIENT_END_UNKNOWN');self.assertEqual(result.counts['namespace_cleanup_code'],'FAIL_NAMESPACE_CLEANUP')
    def test_full_call_capture_cannot_alias_returncode_or_original_bytes(self):
        p.capture.collector_type();raw=b'SELECT 1;';result=self.collector.SqlcmdResult(('sqlcmd',),0,'SYNTHETIC','',False,0.1)
        cap=p.capture.capture_sqlcmd(result,ordinal=0,pid=123,final_poll=0,input_bytes=raw,secret_values=SECRETS,source_binding=p.capture.sources())
        call=dict(Ordinal=0,Phase='STATE',InputText=raw.decode(),Stdout='SYNTHETIC',Stderr='',Capture=cap,ExpectedError=None);e.validate_call(call)
        for changes in ({'InputText':'SELECT 2;'},{'Stdout':'other'},{'Ordinal':True},{'ExpectedError':51003}):
            with self.assertRaises(ValueError):e.validate_call(call|changes)

if __name__=='__main__':unittest.main()
