"""Expliziter RED-Poolproducer für genau einen neuen eigenen Wegwerfnamespace."""
import argparse,hashlib,json,os,re,secrets,shutil,subprocess,sys,time,uuid
from dataclasses import dataclass
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE))
import pool_client as client
import pool_profile_inputs as inputs
import pool_profile_evidence as evidence
if any(Path(module.__file__).resolve()!=HERE/name for module,name in ((client,'pool_client.py'),(inputs,'pool_profile_inputs.py'),(evidence,'pool_profile_evidence.py'))):raise ValueError('FAIL_SOURCE_BINDING')
capture=client.capture
IMAGE='78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726'
OWNER='CON010-Pool-Public'
CANONICAL='Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md'
CONTROL=ROOT/'Runtime/AI_POOL_PUBLIC'
DLL=Path('C:/Program Files/PowerShell/7/System.Data.SqlClient.dll')
PWSH=Path('C:/Program Files/PowerShell/7/pwsh.exe')
DLL_SHA='c37a712c5e0b4f2d388611b0ceb9bceca902fe8751075aba4f5dcdcc291eda03'
PWSH_SHA='bfb46af89433268872ddb43d1ca7a3f433452ee91ed356a9786940f90118e285'
# Konfigurierte Namespacecaps: Lookup3 + Inspect3 + Remove8 + CID3 + Name3.
NAMESPACE_RESERVE=20
SOURCE_KEYS=(*client.SOURCE_KEYS,*('Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/'+n for n in ('run_pool_profile.py','pool_profile_inputs.py','pool_profile_evidence.py','pool_profile.ps1','Expected/pool-profile-contract.json')),'Tests/Static/test_con010_pool_profile.py','Documentation/HowTo/SQL_SERVER_2025_AI_POOL_PUBLIC.md')
INSPECT='{"Id":{{json .ID}},"Name":{{json .Name}},"Image":{{json .Image}},"Owner":{{json (index .Config.Labels "sqlperf.owner")}},"Memory":{{.HostConfig.Memory}},"NanoCpus":{{.HostConfig.NanoCpus}},"Mounts":{{json .Mounts}},"Binds":{{json .HostConfig.Binds}},"VolumesFrom":{{json .HostConfig.VolumesFrom}},"Ports":{{json .NetworkSettings.Ports}}}'
@dataclass(frozen=True)
class Result:
    status:str
    code:str
    counts:dict
    evidence:object=None
class Unknown(client.ClientEndUnknown):pass
class Failure(ValueError):
    def __init__(self,code):super().__init__(code)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def source_map():return {name:digest(ROOT/name) for name in SOURCE_KEYS}
def provider_available():
    # Nur vorhandene feste Dateien prüfen; keine CLR-/Transportprobe oder Installation.
    return os.name=='nt' and DLL.is_file() and PWSH.is_file() and digest(DLL)==DLL_SHA and digest(PWSH)==PWSH_SHA and shutil.which('sqlcmd') is not None and shutil.which('podman') is not None

def projected_container(data,name,cid=None,port=None):
    fields={'Id','Name','Image','Owner','Memory','NanoCpus','Mounts','Binds','VolumesFrom','Ports'}
    if type(data) is not dict or set(data)!=fields or type(data['Id']) is not str or not re.fullmatch('[a-f0-9]{64}',data['Id']) or data['Name']!=name or data['Image']!=IMAGE or data['Owner']!=OWNER or type(data['Memory']) is not int or data['Memory']!=6*1024**3 or type(data['NanoCpus']) is not int or data['NanoCpus']!=4*10**9 or data['Mounts']!=[] or data['Binds'] not in (None,[]) or data['VolumesFrom'] not in (None,[]):raise Failure('FAIL_OWN_NAMESPACE')
    if cid is not None and data['Id']!=cid:raise Failure('FAIL_OWN_NAMESPACE')
    ports=data['Ports']
    if type(ports) is not dict or set(ports)!={'1433/tcp'} or type(ports['1433/tcp']) is not list or len(ports['1433/tcp'])!=1:raise Failure('FAIL_OWN_PORT')
    binding=ports['1433/tcp'][0]
    if type(binding) is not dict or set(binding)!={'HostIp','HostPort'} or binding['HostIp']!='127.0.0.1' or type(binding['HostPort']) is not str or not re.fullmatch('[1-9][0-9]{0,4}',binding['HostPort']) or int(binding['HostPort'])>65535 or (port is not None and binding['HostPort']!=port):raise Failure('FAIL_OWN_PORT')
    return data['Id'],binding['HostPort']

def namespace_environment(inherited):
    # APPDATA ist die einzige zusätzliche tatsächlich read-only belegte Konfigurationswurzel.
    keys={'systemroot':'SYSTEMROOT','windir':'WINDIR','systemdrive':'SYSTEMDRIVE','path':'PATH','pathext':'PATHEXT','temp':'TEMP','tmp':'TMP','home':'HOME','userprofile':'USERPROFILE','lang':'LANG','lc_all':'LC_ALL','ld_library_path':'LD_LIBRARY_PATH','appdata':'APPDATA'}
    if type(inherited) is not dict or any(type(k) is not str or type(v) is not str for k,v in inherited.items()):raise Failure('FAIL_NAMESPACE_ENV')
    return {keys[k.casefold()]:v for k,v in inherited.items() if k.casefold() in keys}

def prior_no_create(entry,ordinal,admission):
    directory=CONTROL/f'candidate{ordinal}';path=directory/'no-created-closure.json'
    pins=admission.get('prior_no_create_sha256')
    if type(pins) is not dict or type(pins.get(str(ordinal))) is not str or not path.is_file() or path.stat().st_size>100000 or digest(path)!=pins[str(ordinal)]:raise Failure('FAIL_NO_CREATE_PROOF')
    proof=json.loads(path.read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
    fields={'contract','candidate','original_ledger_sha256','original_result_sha256','checkpoint_sha256','diagnosis_sha256','current_source_sha256','namespace_query','input_folder','input_files','create_attempts','cid','sql_absence'}
    if type(proof) is not dict or set(proof)!=fields or proof['contract']!='CON010_POOLPUBLIC_NOT_CREATED_V1' or type(proof['candidate']) is not int or proof['candidate']!=ordinal or type(proof['create_attempts']) is not int or proof['create_attempts']!=0 or proof['cid']!='NOT_CREATED' or proof['sql_absence']!='NOT_ESTABLISHED' or proof['current_source_sha256']!=source_map():raise Failure('FAIL_NO_CREATE_PROOF')
    for name,field in (('public-ledger.json','original_ledger_sha256'),('actual-result.json','original_result_sha256'),('root-fail-checkpoint.json','checkpoint_sha256'),('namespace-env-diagnosis.json','diagnosis_sha256')):
        if not (directory/name).is_file() or proof[field]!=digest(directory/name):raise Failure('FAIL_NO_CREATE_PROOF')
    original=json.loads((directory/'actual-result.json').read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
    archived=json.loads((directory/'public-ledger.json').read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
    checkpoint=json.loads((directory/'root-fail-checkpoint.json').read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
    if type(archived) is not list or len(archived)!=ordinal or archived[-1]!=entry or original.get('source_sha256')!=entry.get('source_sha256') or original.get('status')!='FAIL' or original.get('code')!='FAIL_NAMESPACE_COMMAND' or original.get('actual_snapshot',{}).get('cid') is not None or original['actual_snapshot'].get('unknown') is not False or original['actual_snapshot'].get('sql_calls')!=[] or original['actual_snapshot'].get('child') is not None:raise Failure('FAIL_NO_CREATE_PROOF')
    expected={'status':'KNOWN_PRE_EFFECT_FAIL_RECORDED','candidate':ordinal,'result_sha256':proof['original_result_sha256'],'diagnosis_sha256':proof['diagnosis_sha256'],'sqlcmd_calls':0,'pool_children':0,'containers_created':0,'create_call_reached':False,'client_end_unknown':False,'fresh_name_query':'ACTUAL_EMPTY_READ_ONLY_DIAGNOSIS','cid':'NOT_CREATED','sql_cleanup':'NOT_ESTABLISHED','ledger_historical_closed':False,'retry':'ONLY_CHANGED_SOURCE_NEW_BOUND_ADMISSION'}
    if type(checkpoint) is not dict or set(checkpoint)!=set(expected) or any(type(checkpoint[k]) is not type(v) or checkpoint[k]!=v for k,v in expected.items()):raise Failure('FAIL_NO_CREATE_PROOF')
    if type(entry.get('source_sha256')) is not dict or set(entry['source_sha256'])!=set(SOURCE_KEYS) or any(type(v) is not str or not re.fullmatch('[a-f0-9]{64}',v) for v in entry['source_sha256'].values()):raise Failure('FAIL_NO_CREATE_PROOF')
    for key,value in entry['source_sha256'].items():
        archived_path=directory/'source-archive'/key
        if not archived_path.is_file() or digest(archived_path)!=value:raise Failure('FAIL_NO_CREATE_PROOF')
    token=original['actual_snapshot'].get('token')
    if type(token) is not str or not re.fullmatch('[A-F0-9]{16}',token) or entry.get('name')!='sqlperf-pool-public-'+token.lower():raise Failure('FAIL_NO_CREATE_PROOF')
    command=[shutil.which('podman'),'ps','-a','--filter','name=^'+entry['name']+'$','--format','{{.ID}}']
    query=proof['namespace_query']
    if type(query) is not dict or set(query)!={'Command','ReturnCode','Stdout','Stderr','ProcessEnd'} or query['Command']!=command or type(query['ReturnCode']) is not int or query['ReturnCode']!=0 or query['Stdout']!='' or query['Stderr']!='' or query['ProcessEnd']!='SUBPROCESS_RUN_RETURNED':raise Failure('FAIL_NO_CREATE_PROOF')
    folder=client.INPUT_ROOT/token
    if proof['input_folder']!=str(folder) or type(proof['input_files']) is not list or proof['input_files']!=[] or (folder.exists() and (folder.is_symlink() or any(folder.iterdir()))):raise Failure('FAIL_NO_CREATE_PROOF')
    return True

def admitted(candidate,admission,ledger):
    stopped=CONTROL/'candidate2/namespace-recovery-unknown.json'
    if stopped.is_file():
        try:
            if stopped.stat().st_size>100000:raise Failure('FAIL_WAVE_STOP_RECORD')
            observed=json.loads(stopped.read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
            if observed.get('contract')!='CON010_POOLPUBLIC_NAMESPACE_RECOVERY_UNKNOWN_V1' or observed.get('status')!='RESOURCE_ABSENT_REQUEST_END_UNKNOWN' or observed.get('mutative_request_end')!='UNKNOWN_STICKY':raise Failure('FAIL_WAVE_STOP_RECORD')
        except (ValueError,UnicodeError):raise Failure('FAIL_WAVE_STOP_RECORD') from None
        raise Failure('FAIL_WAVE_STOP_AFTER_UNKNOWN')

    if type(candidate) is not int or not 1<=candidate<=6 or type(admission) is not dict or admission.get('status')!='ADMITTED' or type(admission.get('candidate')) is not int or admission['candidate']!=candidate or admission.get('scope')!='CON010_OPT_IN_RED_POOLPUBLIC' or admission.get('allow_red') is not True or admission.get('confirm_isolated_lab') is not True:raise Failure('FAIL_ROOT_ADMISSION')
    if admission.get('canonical_scope')!=CANONICAL or admission.get('canonical_scope_sha256')!=digest(ROOT/CANONICAL) or admission.get('source_sha256')!=source_map():raise Failure('FAIL_SOURCE_BINDING')
    for name,field in (('root-review.json','root_review_sha256'),('source-proof.json','source_proof_sha256'),('budget.json','budget_sha256')):
        path=CONTROL/name
        if not path.is_file() or path.stat().st_size>100000 or admission.get(field)!=digest(path):raise Failure('FAIL_ROOT_ADMISSION')
    review=json.loads((CONTROL/'root-review.json').read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
    proof=json.loads((CONTROL/'source-proof.json').read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
    budget=json.loads((CONTROL/'budget.json').read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
    if review.get('status')!='SOURCE_REVIEW_CLOSED' or review.get('source_sha256')!=source_map() or proof.get('source_sha256')!=source_map() or proof.get('status')!='REGISTERED':raise Failure('FAIL_ROOT_ADMISSION')
    expected={'max_candidates':6,'max_containers':6,'containers_per_candidate':1,'checkpoint':3,'hard_stop':6,'normal_seconds':300,'cleanup_seconds':60,'namespace_reserve_seconds':20,'child_cap_seconds':40,'cleanup_starts_before_child':True,'database':inputs.DATABASE,'run_token':'POOLPUBLIC','image':IMAGE,'build':'17.0.5005.3','model_calls':0,'max_logins':3,'rows':2,'dimension':3,'checkouts':6}
    if type(budget) is not dict or set(budget)!=set(expected) or any(type(budget[k]) is not type(v) or budget[k]!=v for k,v in expected.items()):raise Failure('FAIL_BUDGET_BINDING')
    if type(ledger) is not list or len(ledger)!=candidate-1:raise Failure('FAIL_SERIAL_BUDGET')
    for n,entry in enumerate(ledger,1):
        if type(entry) is not dict or type(entry.get('candidate')) is not int or entry['candidate']!=n or entry.get('unknown') is not False or entry.get('inputs_absent') is not True or entry.get('status')!='FAIL' or entry.get('image')!=IMAGE or entry.get('owner')!=OWNER:raise Failure('FAIL_SERIAL_BUDGET')
        complete=entry.get('closed') is True and entry.get('namespace_absent') is True and type(entry.get('cid')) is str and re.fullmatch('[a-f0-9]{64}',entry['cid']) is not None
        not_created=entry.get('closed') is False and entry.get('cid') is None and prior_no_create(entry,n,admission)
        if not complete and not not_created:raise Failure('FAIL_SERIAL_BUDGET')
    if ledger:
        old=ledger[-1]['source_sha256'];now=source_map()
        relevant=lambda values:{k:v for k,v in values.items() if Path(k).suffix in ('.py','.ps1','.sql')}
        if relevant(old)==relevant(now):raise Failure('FAIL_UNCHANGED_RETRY')
    if candidate>=4:
        cp=CONTROL/'checkpoint3.json'
        if not cp.is_file():raise Failure('FAIL_CHECKPOINT')
        marker=json.loads(cp.read_bytes().decode('utf-8'))
        if marker.get('status')!='REGISTERED' or marker.get('first_three_sha256')!=hashlib.sha256(evidence.canonical(ledger[:3]).encode()).hexdigest():raise Failure('FAIL_CHECKPOINT')
    return source_map()

def startup_retry(stdout,stderr):
    streams=(stdout,stderr);count=0
    for stream in streams:
        if type(stream) is not str:return False
        dot=False
        for line in stream.splitlines():
            line=line.strip()
            if not line:dot=False;continue
            if line=='.' and dot:dot=False;continue
            dot=False
            if not line.startswith('Sqlcmd: Error: Microsoft ODBC Driver '):return False
            if not any(marker in line for marker in ('TCP Provider:','Login timeout expired','A network-related or instance-specific error','Client unable to establish connection','Server is not found or not accessible')):return False
            count+=1;dot='TCP Provider:' in line
    return count>0

class Producer:
    def __init__(self,candidate,admission,ledger):
        self.candidate=candidate;self.admission=admission;self.ledger=ledger
        self.sources=admitted(candidate,admission,ledger)
        self.normal_end=time.monotonic()+300;self.cleanup_end=None;self.unknown=False;self.deadline_failed=False
        self.token=uuid.uuid4().hex[:16].upper();self.name='sqlperf-pool-public-'+self.token.lower();self.cid=None;self.port=None
        self.values=tuple(secrets.token_hex(32)+'!' for _ in range(4))
        self.sids={lane:secrets.token_hex(16).upper() for lane in evidence.LOGINS}
        self.folder=client.INPUT_ROOT/self.token;self.ordinal=0;self.captures=[];self.clients=[];self.extra_inputs=[]
        self.dbid=None;self.oid=None;self.held=None;self.baseline=None;self.pool_ready=False;self.record=None;self.controls=[]
        self.transcripts=[];self.negative_states=[];self.namespace_witness=None;self.bound_at_start=None;self.create_unknown=False;self.remove_unknown=False;self.remove_attempted=False;self.create_attempts=0;self.namespace_calls=[];self.no_create_witness=None;self.child_evidence=None;self.sql_absent=False;self.namespace_absent=False;self.inputs_absent=False;self.started=False;self.cli=shutil.which('podman');self.sqlcmd=Path(shutil.which('sqlcmd') or '')
    def gate(self):
        if admitted(self.candidate,self.admission,self.ledger)!=self.sources:raise Failure('FAIL_SOURCE_BINDING')
        if self.unknown:raise Unknown()
    def begin_cleanup(self):
        if self.cleanup_end is None:self.cleanup_end=time.monotonic()+60
        return self.cleanup_end
    def remaining(self,cleanup=False):
        end=self.begin_cleanup() if cleanup else min(self.normal_end,self.cleanup_end) if self.cleanup_end is not None else self.normal_end
        value=end-time.monotonic()
        if value<=0:raise Failure('FAIL_DEADLINE')
        return value
    def podman(self,args,cap,cleanup=False,*,creating=False):
        # Ausschließlich feste eigene CLIoperationen; keine Inspect-ENV/Rawpersistenz.
        if source_map()!=self.sources:raise Failure('FAIL_SOURCE_BINDING')
        if not cleanup:self.gate()
        timeout=min(cap,self.remaining(cleanup));environment=namespace_environment(dict(os.environ))
        if creating:environment['MSSQL_SA_PASSWORD']=self.values[0]
        command=[self.cli,*args];began=time.monotonic();mutative=creating or args[0] in ('run','rm')
        if args[0]=='rm':
            if self.remove_attempted:raise Unknown()
            self.remove_attempted=True
        if creating:self.create_attempts+=1
        try:
            response=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',env=environment,timeout=timeout,check=False)
            capture.credential_gate('',response.stdout,response.stderr,tuple(command),self.values)
            if type(response.returncode) is not int or type(response.stdout) is not str or type(response.stderr) is not str:raise Failure('FAIL_NAMESPACE_COMMAND')
            self.namespace_calls.append({'Command':command,'ReturnCode':response.returncode,'Stdout':response.stdout,'Stderr':response.stderr,'ProcessEnd':'SUBPROCESS_RUN_RETURNED','DurationSeconds':time.monotonic()-began})
            if self.remaining(cleanup)<=0 or response.returncode!=0:raise Failure('FAIL_NAMESPACE_COMMAND')
            return response.stdout
        except capture.CredentialOutputRejected:raise Failure('FAIL_CREDENTIAL_OUTPUT') from None
        except BaseException:
            if mutative:self.unknown=True
            if creating:self.create_unknown=True
            if args[0]=='rm':self.remove_unknown=True
            raise Failure('FAIL_NAMESPACE_COMMAND') from None
    def inspect(self,cleanup=False):
        text=self.podman(['inspect','--format',INSPECT,self.name],3 if cleanup else 10,cleanup)
        data=json.loads(text,object_pairs_hook=evidence.unique);cid,port=projected_container(data,self.name,self.cid,self.port)
        self.last_inspect=dict(data)
        return cid,port
    def start_namespace(self):
        self.gate()
        if self.podman(['ps','--no-trunc','-a','--filter','name=^'+self.name+'$','--format','{{.ID}}'],5).strip():raise Failure('FAIL_OWN_NAMESPACE')
        if self.podman(['image','inspect',IMAGE,'--format','{{.Id}}'],5).strip()!=IMAGE:raise Failure('FAIL_IMAGE_BINDING')
        self.started=True
        self.podman(['run','--detach','--pull=never','--name',self.name,'--label','sqlperf.owner='+OWNER,'--cpus','4','--memory','6g','--publish','127.0.0.1::1433','--env','ACCEPT_EULA=Y','--env','MSSQL_PID=Developer','--env','MSSQL_SA_PASSWORD',IMAGE],20,creating=True)
        self.cid,self.port=self.inspect();self.bound_at_start=dict(self.last_inspect);self.folder.mkdir(parents=True,exist_ok=False)
    def sql(self,text,phase='STATE',*,expected=None,recovery=False,startup=False):
        self.gate()
        if self.deadline_failed:raise Failure('FAIL_DEADLINE')
        self.inspect(cleanup=recovery)
        raw=text.encode('utf-8');ordinal=self.ordinal;self.ordinal+=1
        if ordinal>63:raise Failure('FAIL_INPUT_POPULATION')
        path=self.folder/f'phase-{ordinal:02}.sql'
        capture.credential_gate(text,'','',(),self.values)
        with path.open('xb') as stream:stream.write(raw)
        plan={ordinal:{'Phase':phase,'InputSha256':hashlib.sha256(raw).hexdigest()}}
        binding=client._bind_caller(caller_scope='CON010_POOL_OWNER_SQLCMD',source_binding=client.source_map(),token=self.token,server='tcp:127.0.0.1,'+self.port,executable=self.sqlcmd,executable_sha256=digest(self.sqlcmd),input_plan=plan,normal_end=self.normal_end,required_cleanup_reserve_seconds=NAMESPACE_RESERVE)
        adapter=client.PoolSqlcmdClient(binding);self.clients.append(adapter)
        if self.cleanup_end is not None:adapter.begin_cleanup(self.cleanup_end)
        try:
            result=adapter.execute(ordinal,secret_values=self.values,recovery=recovery)
            self.captures.append(result.capture);self.transcripts.append({'Ordinal':ordinal,'Phase':phase,'InputText':text,'Stdout':result.stdout,'Stderr':result.stderr,'Capture':result.capture,'ExpectedError':expected})
            if startup and result.capture['ReturnCode']!=0:
                if startup_retry(result.stdout,result.stderr):return None
                raise Failure('FAIL_STARTUP_DIAGNOSTICS')
            if expected is None:
                if result.capture['ReturnCode']!=0:raise Failure('FAIL_EXECUTION')
            elif result.capture['ReturnCode']==0 or not evidence.native_error(result.stdout+'\n'+result.stderr,expected,'FAIL_STATE' if expected==51004 else 'FAIL_RESULT_CONTRACT'):raise Failure('FAIL_NATIVE_NEGATIVE')
            return result.stdout+'\n'+result.stderr
        except client.ClientEndUnknown:self.unknown=True;raise Unknown() from None
        except client.ClientFailure:
            if adapter.deadline_exceeded:self.deadline_failed=True
            raise
        finally:
            if not adapter.unknown:
                try:path.unlink()
                except OSError:raise Failure('FAIL_INPUT_CLEANUP') from None
    def scalar(self,text,phase='STATE',**kwargs):return evidence.decode(self.sql(text,phase,**kwargs))
    def state(self,values=None,recovery=False):return self.scalar(inputs.state(self.dbid,values),recovery=recovery)
    def ok(self,text,phase='STATE',**kwargs):
        if self.sql(text,phase,**kwargs).strip()!='SQLPERF_SUMMARY|PASS|OK':raise Failure('FAIL_SUMMARY')
    def setup(self):
        # Bounded reine Startupqueries; nur bekannte ODBC-Verbindungsfehler sind retrybar.
        for attempt in range(20):
            result=self.sql("SET NOCOUNT ON;SELECT 'POOLPUBLIC_READY';",'PREFLIGHT',startup=True)
            if result is not None and result.strip()=='POOLPUBLIC_READY':break
            if result is not None:raise Failure('FAIL_STARTUP_DIAGNOSTICS')
            time.sleep(min(2,self.remaining()))
        else:raise Failure('FAIL_STARTUP')
        if self.sql(inputs.absence(self.sids),'PREFLIGHT').strip()!='POOLPUBLIC_ALL|ABSENT':raise Failure('FAIL_INITIAL_ABSENCE')
        output=self.sql(inputs.setup(self.sids),'SETUP')
        lines=[v.strip() for v in output.splitlines() if v.strip()]
        if lines!=['POOLPUBLIC_ALL|ABSENT',"Changed database context to '"+inputs.DATABASE+"'.",'SQLPERF_SUMMARY|PASS|OK'] and lines!=['POOLPUBLIC_ALL|ABSENT','SQLPERF_SUMMARY|PASS|OK']:raise Failure('FAIL_SETUP_SUMMARY')
        identity=self.scalar(inputs.creator()+"DECLARE @J nvarchar(max)=(SELECT DB_ID() DatabaseId,OBJECT_ID(N'lab.Documents',N'U') ObjectId FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);"+inputs.OUTPUT)
        if type(identity) is not dict or set(identity)!={'DatabaseId','ObjectId'}:raise Failure('FAIL_IDENTITY')
        self.dbid=identity['DatabaseId'];self.oid=identity['ObjectId'];inputs.checked(self.dbid);inputs.checked(self.oid)
        self.ok(inputs.create_logins(self.dbid,self.sids));self.baseline=evidence.state(self.state(),self.dbid,self.oid,self.sids);self.held=self.baseline['PrincipalHex']
    def negatives(self):
        self.ok(inputs.source_assertion(self.dbid));self.ok(inputs.source_delete(self.dbid))
        self.sql(inputs.source_assertion(self.dbid),expected=51003);self.controls.append('SOURCE_DELETE_51003')
        self.ok(inputs.source_restore(self.dbid));self.ok(inputs.source_assertion(self.dbid));evidence.same(self.baseline,self.state());self.controls.append('SOURCE_RESTORED')
        wrong=self.sids|{'A':('0' if self.sids['A'][0]!='0' else '1')+self.sids['A'][1:]}
        self.sql(inputs.drop_login(self.dbid,'A',self.held,wrong,tuple(evidence.LOGINS)),expected=51004);after=self.state();evidence.same(self.baseline,after);self.negative_states.append({'Before':self.baseline,'After':after,'Restored':after});self.controls.append('HELD_SID_51004')
        for n,key in enumerate(inputs.MARKERS):
            self.ok(inputs.marker_change(self.dbid,key));values=inputs.MARKERS|{key:'FOREIGN'}
            before=self.state(values)
            self.sql(inputs.source_delete(self.dbid),expected=51004)
            after=self.state(values);evidence.same(before,after)
            self.ok(inputs.marker_restore(self.dbid,key));restored=self.state();evidence.same(self.baseline,restored);self.negative_states.append({'Before':before,'After':after,'Restored':restored});self.controls.append(f'MARKER_{n}_51004')
    def child(self):
        self.gate();end=self.begin_cleanup();now=time.monotonic()
        phase_end=min(end-NAMESPACE_RESERVE,now+40)
        primary=capture.collector_wait_seconds(end-now,40,required_cleanup_reserve_seconds=NAMESPACE_RESERVE)
        plan={'status':'OWN_POOL_ADMITTED','token':self.token,'server':'tcp:127.0.0.1,'+self.port,'database':inputs.DATABASE,'dbid':self.dbid,'seconds':primary,'repo':str(ROOT),'source':self.sources|{'HOST/SqlClient':DLL_SHA,'HOST/PowerShell':PWSH_SHA},'logins':evidence.LOGINS,'sids':self.sids}
        raw=json.dumps(plan,ensure_ascii=True,allow_nan=False).encode('utf-8');path=self.folder/'child-plan.json'
        if len(raw)>160000:raise Failure('FAIL_CHILD_INPUT')
        capture.credential_gate(raw.decode(),'','',(),self.values)
        with path.open('xb') as stream:stream.write(raw)
        self.extra_inputs.append((path,hashlib.sha256(raw).hexdigest()))
        capture.collector_type();collector=capture._collector;process=None;attempted=False;response=None;poll=None;error=False
        command=[str(PWSH),'-NoProfile','-File',str(HERE/'pool_profile.ps1'),'-Admission',str(path),'-AdmissionSha',hashlib.sha256(raw).hexdigest()]
        self.gate()
        try:
            attempted=True;process=collector.start_sqlcmd(command,environment=client._private_environment(self.values))
            wait=max(0,min(primary,phase_end-time.monotonic()-26))
            if wait<=0:self.unknown=True
            response=collector.collect_process(process,command,timeout_seconds=wait)
        except BaseException:error=True;self.unknown=True
        finally:
            if process is not None:
                try:
                    poll=process.poll()
                    if type(poll) is not int:self.unknown=True
                except BaseException:self.unknown=True
            elif attempted:self.unknown=True
        if response is None:self.unknown=True
        if response is not None and (type(response.returncode) is not int or type(response.timed_out) is not bool or response.timed_out or response.returncode<0 or response.returncode!=poll):self.unknown=True
        if time.monotonic()>phase_end:self.deadline_failed=True
        if self.unknown:raise Unknown()
        if len(response.stdout.encode())+len(response.stderr.encode())>1000000:self.unknown=True;raise Unknown()
        try:receipt=json.loads(response.stdout,object_pairs_hook=evidence.unique)
        except (ValueError,UnicodeError):self.unknown=True;raise Unknown() from None
        if type(receipt) is not dict or receipt.get('RequestEnd')!='RESPONSE_RECEIVED':self.unknown=True
        capture.credential_gate(raw.decode(),response.stdout,response.stderr,tuple(command),self.values)
        evidence.credential_safe(receipt,self.values)
        if self.unknown:raise Unknown()
        envelope={'Kind':'POWERSHELL_POOL_CHILD','Pid':process.pid,'ReturnCode':response.returncode,'FinalPoll':poll,'TimedOut':response.timed_out,'DurationSeconds':response.duration_seconds,'InputBytes':len(raw),'InputSha256':hashlib.sha256(raw).hexdigest(),'StdoutBytes':len(response.stdout.encode()),'StdoutSha256':hashlib.sha256(response.stdout.encode()).hexdigest(),'StderrBytes':len(response.stderr.encode()),'StderrSha256':hashlib.sha256(response.stderr.encode()).hexdigest(),'ScriptSha256':digest(HERE/'pool_profile.ps1'),'ClientProcessEnd':'KNOWN','ServerRequestEnd':'API_RETURN_RECORDS_ONLY','CredentialSafety':'CHECKED_AGAINST_PRIVATE_CALLER_LIST'}
        self.child_evidence={'Envelope':envelope,'Receipt':receipt,'InputText':raw.decode('utf-8'),'Stdout':response.stdout,'Stderr':response.stderr}
        if self.deadline_failed:raise Failure('FAIL_DEADLINE')
        evidence.validate_pool(receipt,self.sids,self.dbid,self.token);evidence.validate_child(envelope,receipt)
        if response.stderr.strip():raise Failure('FAIL_CHILD_DIAGNOSTICS')
        path.unlink();self.extra_inputs.remove((path,hashlib.sha256(raw).hexdigest()))
        return receipt,envelope
    def sql_cleanup(self):
        self.begin_cleanup()
        if self.unknown or self.deadline_failed:raise Unknown()
        if not self.pool_ready or self.dbid is None or self.held is None:raise Failure('FAIL_CLEANUP_LEASE')
        # Eine feste Clientphase, alle gehaltenen Loginleases vor DB-Drop; keine Adoption.
        remaining=list(evidence.LOGINS);text=''
        for lane in tuple(remaining):
            block=inputs.drop_login(self.dbid,lane,self.held,self.sids,tuple(remaining)).replace(inputs.SUMMARY,'')
            text+='EXEC('+inputs.literal(block)+');';remaining.remove(lane)
        text+='EXEC('+inputs.literal(inputs.cleanup_db(self.dbid,self.sids).replace(inputs.SUMMARY,''))+');'+inputs.SUMMARY
        self.ok(text,'DROP_DATABASE',recovery=True)
        if self.sql(inputs.absence(self.sids),'SQL_ABSENCE',recovery=True).strip()!='POOLPUBLIC_ALL|ABSENT':raise Failure('FAIL_SQL_ABSENCE')
        self.sql_absent=True
    def namespace_cleanup(self):
        self.begin_cleanup()
        # Ownerbinding bleibt notwendig, auch nach fehlgeschlagenem Create-Return.
        found=self.podman(['ps','--no-trunc','-a','--filter','name=^'+self.name+'$','--format','{{.ID}}'],3,True).strip()
        if found:
            cid,port=self.inspect(True)
            if found!=cid:raise Failure('FAIL_OWN_NAMESPACE')
            self.cid=cid;self.port=port
            self.namespace_witness={'BoundAtStart':self.bound_at_start,'BoundBeforeRemove':dict(self.last_inspect),'CidQuery':None,'NameQuery':None,'InputFiles':None}
            self.podman(['rm','-f','--time=0',self.cid],8,True)
        if self.cid is None:raise Failure('FAIL_CID_ABSENCE')
        cid_output=self.podman(['ps','--no-trunc','-a','--filter','id='+self.cid,'--format','{{.ID}}'],3,True)
        name_output=self.podman(['ps','--no-trunc','-a','--filter','name=^'+self.name+'$','--format','{{.ID}}'],3,True)
        if cid_output!='':raise Failure('FAIL_CID_ABSENCE')
        if name_output!='':raise Failure('FAIL_NAME_ABSENCE')
        if self.namespace_witness is not None:self.namespace_witness.update(CidQuery=cid_output,NameQuery=name_output,InputFiles=[] if not self.folder.exists() else [p.name for p in self.folder.iterdir()])
        self.namespace_absent=True
    def run(self):
        primary=None;sql_failure=None;namespace_failure=None;input_failure=None;pool=None;child=None;after=None
        try:
            self.start_namespace();self.setup();self.negatives();pool,child=self.child()
            ids=list(dict.fromkeys(r['Owner']['ConnectionId'] for r in pool['Records']))
            if self.sql(inputs.pool_absence(self.dbid,ids)).strip()!='POOLPUBLIC_PHYSICAL|ABSENT':raise Failure('FAIL_PHYSICAL_ABSENCE')
            self.pool_ready=True;after=self.state();evidence.same(self.baseline,after)
        except BaseException as failure:
            primary='CLIENT_END_UNKNOWN' if self.unknown else str(failure) if type(failure) is Failure else 'FAIL_RESULT_CONTRACT'
        finally:
            self.begin_cleanup()
            if self.started and not self.unknown:
                try:self.sql_cleanup()
                except BaseException:sql_failure='FAIL_SQL_CLEANUP'
            if not self.started and not self.unknown and self.create_attempts==0:
                try:
                    command=['ps','--no-trunc','-a','--filter','name=^'+self.name+'$','--format','{{.ID}}']
                    output=self.podman(command,3,True)
                    if output!='':raise Failure('FAIL_NAME_ABSENCE')
                    self.no_create_witness={'State':'NOT_CREATED','CreateAttempts':0,'Name':self.name,'Query':self.namespace_calls[-1],'InputFolder':str(self.folder),'InputFiles':[] if not self.folder.exists() else [p.name for p in self.folder.iterdir()]}
                    self.namespace_absent=self.no_create_witness['InputFiles']==[]
                except BaseException:namespace_failure='FAIL_NAMESPACE_CLEANUP'
            if self.started:
                try:self.namespace_cleanup()
                except BaseException:namespace_failure='FAIL_NAMESPACE_CLEANUP'
            if not self.unknown and self.namespace_absent:
                for path,expected in tuple(self.extra_inputs):
                    try:
                        if path.parent!=self.folder or path.is_symlink() or digest(path)!=expected:raise Failure('FAIL_INPUT_BINDING')
                        path.unlink();self.extra_inputs.remove((path,expected))
                    except BaseException:input_failure='FAIL_INPUT_CLEANUP'
            remaining_inputs=[] if not self.folder.exists() else [v.name for v in self.folder.iterdir()]
            self.inputs_absent=remaining_inputs==[]
            if self.namespace_witness is not None:self.namespace_witness['InputFiles']=remaining_inputs
        if primary is None and sql_failure is None and namespace_failure is None and input_failure is None and self.sql_absent and self.namespace_absent and self.inputs_absent:
            record={'PoolReceipt':pool,'Child':child,'Baseline':self.baseline,'After':after,'DatabaseId':self.dbid,'ObjectId':self.oid,'Sids':self.sids,'Token':self.token,'Controls':self.controls,'PhysicalAbsence':'ACTUAL_NEW_OWNER_QUERY','SqlAbsence':'ACTUAL_NEW_DB_AND_PRINCIPAL_QUERY','NamespaceAbsence':'ACTUAL_FULL_CID_AND_NAME_QUERY','InputsAbsent':self.inputs_absent,'ContainerId':self.cid,'Port':self.port,'Actual':{'SqlCalls':self.transcripts,'NegativeStates':self.negative_states,'ChildInputText':self.child_evidence['InputText'],'ChildStdout':self.child_evidence['Stdout'],'ChildStderr':self.child_evidence['Stderr'],'SourceSha256':self.sources,'Namespace':self.namespace_witness,'NamespaceCalls':self.namespace_calls}}
            return Result('WARN','BOUNDED_POOL_PROFILE',evidence.summary(record),record)
        return Result('FAIL',input_failure or namespace_failure or sql_failure or primary or 'FAIL_CLOSURE',{'primary_code':primary,'sql_cleanup_code':sql_failure,'namespace_cleanup_code':namespace_failure,'input_cleanup_code':input_failure,'runtime_qualification':'NOT_ESTABLISHED','sql_absence':'ACTUAL_NEW_QUERY' if self.sql_absent else 'NOT_ESTABLISHED','namespace_absence':self.namespace_absent,'remove_end':'UNKNOWN' if self.remove_unknown else 'RETURNED_TO_CALLER' if self.remove_attempted else 'NOT_STARTED','create_end':'UNKNOWN' if self.create_unknown else 'NOT_STARTED' if self.create_attempts==0 else 'RETURNED_TO_CALLER','unknown':self.unknown},{'SqlCaptures':self.captures,'SqlCalls':self.transcripts,'NegativeStates':self.negative_states,'Child':self.child_evidence,'Namespace':self.namespace_witness,'Baseline':self.baseline,'NamespaceCalls':self.namespace_calls,'NoCreate':self.no_create_witness})

def run(candidate,admission):
    # Fehlender Provider vor Dateianlage, Container-/Login-/SQLeffekten.
    if not provider_available():return Result('SKIP','SKIP_PROVIDER_UNAVAILABLE',{'native_sql':0,'containers':0})
    ledger_path=CONTROL/'public-ledger.json';ledger=json.loads(ledger_path.read_bytes().decode('utf-8')) if ledger_path.exists() else []
    producer=Producer(candidate,admission,ledger)
    entry={'candidate':candidate,'status':'RESERVED','closed':False,'unknown':False,'namespace_absent':False,'inputs_absent':False,'source_sha256':producer.sources}
    if candidate==1:
        with ledger_path.open('x',encoding='utf-8') as stream:json.dump([entry],stream)
    else:
        ledger_path.write_text(json.dumps([*ledger,entry]),encoding='utf-8')
    # Der Collectorbuilder benötigt SQLCMDPASSWORD; vorherigen Hostwert vollständig zurückstellen.
    previous=os.environ.get('SQLCMDPASSWORD');had='SQLCMDPASSWORD' in os.environ
    try:
        os.environ['SQLCMDPASSWORD']=producer.values[0];result=producer.run()
    finally:
        if had:os.environ['SQLCMDPASSWORD']=previous
        else:os.environ.pop('SQLCMDPASSWORD',None)
        entry.update(status=result.status if 'result' in locals() else 'FAIL',closed=(producer.cid is not None or producer.no_create_witness is not None) and producer.namespace_absent and producer.inputs_absent and not producer.unknown,unknown=producer.unknown,cid=producer.cid,name=producer.name,image=IMAGE,owner=OWNER,namespace_absent=producer.namespace_absent,inputs_absent=producer.inputs_absent,sql_absence='ACTUAL_NEW_QUERY' if producer.sql_absent else 'NOT_ESTABLISHED')
        ledger_path.write_text(json.dumps([*ledger,entry]),encoding='utf-8')
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description='Explizites eigenes RED-Poolprofil; Default führt es nicht aus.')
    parser.add_argument('--allow-red',action='store_true');parser.add_argument('--confirm-isolated-lab',action='store_true');parser.add_argument('--candidate',type=int);parser.add_argument('--source-manifest',action='store_true')
    args=parser.parse_args(argv)
    if args.source_manifest:print(json.dumps(source_map(),indent=2));return 0
    if not args.allow_red or not args.confirm_isolated_lab or args.candidate is None:parser.error('Explizite RED-/Lab-/Kandidatenzulassung erforderlich')
    try:
        path=CONTROL/'Root-admission.json'
        if not path.is_file() or path.stat().st_size>100000:raise Failure('FAIL_ROOT_ADMISSION')
        admission=json.loads(path.read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
        result=run(args.candidate,admission);print(json.dumps({'status':result.status,'code':result.code,'counts':result.counts},sort_keys=True));return 1 if result.status=='FAIL' else 0
    except BaseException:
        print('SQLPERF_SUMMARY|FAIL|FAIL_POOL_PROFILE');return 1
if __name__=='__main__':raise SystemExit(main())
