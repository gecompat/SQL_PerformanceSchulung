"""Feste Rollen-/Sessionkomposition; keine SQL-Ausführung beim Import."""
from dataclasses import dataclass,field
import hashlib,json,math,os,re,sys,tempfile,time,types
from pathlib import Path

FOLDER=Path(__file__).resolve().parent;ROOT=FOLDER.parents[2]
MODE='operator-admin-build'
BUILD="EXEC(N'CREATE VECTOR INDEX IDX012_OwnVector ON lab.VectorFixture(V)\n   WITH (METRIC=''cosine'',TYPE=''diskann'');');"
STAGES={'30_CostBoundary.sql':'DML_BOUNDARY','50_CostRebuild.sql':'REBUILD'}
PHASES={'00_Preflight.sql','10_Setup.sql','11_EnablePreview.sql','12_EnableMaxdop.sql','20_Baseline.sql','21_Snapshot.sql','22_Storage.sql','30_CostBoundary.sql','40_SourceAfter.sql','50_CostRebuild.sql','90_Restore.sql','91_AttestDrop.sql','92_Absence.sql'}

def hex_sid(value,operator=False):
    if type(value)is not str or not re.fullmatch('[A-F0-9]{32}'if operator else '(?:[A-F0-9]{2}){1,85}',value):raise ValueError('FIXED_ROLE_SID')
    return value

@dataclass(frozen=True)
class Binding:
    token:str
    operator_sid:str
    admin_sid:str
    operator_secret:str=field(repr=False)
    admin_secret:str=field(repr=False)
    def __post_init__(self):
        if type(self.token)is not str or not re.fullmatch('[A-F0-9]{16}',self.token):raise ValueError('FIXED_ROLE_TOKEN')
        hex_sid(self.operator_sid,True);hex_sid(self.admin_sid)
        if any(type(v)is not str or not re.fullmatch('[A-Za-z0-9!]{40,80}',v)for v in (self.operator_secret,self.admin_secret))or self.operator_secret==self.admin_secret:raise ValueError('FIXED_ROLE_CREDENTIALS')
    @property
    def operator(self):return 'SQLPERF_IDX012_ROLE_'+self.token
    @property
    def database(self):return 'SQLPERF_LAB_IDX012_'+self.token
    @property
    def secrets(self):return (self.operator_secret,self.admin_secret)

def bind(token,operator_sid,admin_sid,environment):
    if type(token)is not str or not re.fullmatch('[A-F0-9]{16}',token)or type(environment)is not dict:raise ValueError('FIXED_ROLE_BINDING')
    hex_sid(operator_sid,True);hex_sid(admin_sid)
    grouped={}
    for key,value in environment.items():
        if type(key)is not str or type(value)is not str:raise ValueError('FIXED_ROLE_ENV_TYPE')
        grouped.setdefault(key.casefold(),[]).append(value)
    values=[]
    for key in ('idx012_operator_password','sqlcmdpassword'):
        candidates=grouped.get(key,[])
        if len(candidates)!=1 or not re.fullmatch('[A-Za-z0-9!]{40,80}',candidates[0]):raise ValueError('FIXED_ROLE_CREDENTIAL_ENV')
        values.append(candidates[0])
    if values[0]==values[1]:raise ValueError('DISTINCT_ROLE_CREDENTIALS')
    return Binding(token,operator_sid,admin_sid,*values)

def private_environment(binding,parent,admin):
    if type(admin)is not bool:raise ValueError('FIXED_ROLE_ENV_CHOICE')
    keys={'path':'PATH','systemroot':'SystemRoot','windir':'WINDIR','comspec':'COMSPEC','temp':'TEMP','tmp':'TMP','appdata':'APPDATA','localappdata':'LOCALAPPDATA','home':'HOME','userprofile':'USERPROFILE'}
    result={};seen=set()
    for key,value in parent.items():
        folded=key.casefold()
        if folded in keys:
            if folded in seen or type(value)is not str:raise ValueError('FIXED_ROLE_ENV_ROOT')
            seen.add(folded);result[keys[folded]]=value
    result['SQLCMDPASSWORD']=binding.admin_secret if admin else binding.operator_secret
    return result

def unique(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('ROLE_DUPLICATE_JSON')
        value[key]=item
    return value

def safe_texts(binding,*texts):
    forms=[]
    for secret in binding.secrets:forms.extend((secret,secret.encode().hex(),secret.encode().hex().upper(),secret.encode('utf-16-le').hex(),secret.encode('utf-16-le').hex().upper()))
    def walk(value):
        if type(value)is str:return any(form in value for form in forms)
        if type(value)is dict:return any(walk(k)or walk(v)for k,v in value.items())
        if type(value)is list:return any(walk(v)for v in value)
        return False
    for text in texts:
        if type(text)is not str:raise ValueError('ROLE_CHANNEL_TYPE')
        if walk(text):raise ValueError('FAIL_CREDENTIAL_OUTPUT')
        for line in text.splitlines():
            if line.lstrip().startswith('{'):
                try:value=json.loads(line,object_pairs_hook=unique)
                except (ValueError,UnicodeError):raise ValueError('ROLE_CHANNEL_NOT_SAFE')from None
                if walk(value):raise ValueError('FAIL_CREDENTIAL_OUTPUT')
            elif re.search(r'\\(?:u[0-9A-Fa-f]{4}|x[0-9A-Fa-f]{2})',line):raise ValueError('ROLE_CHANNEL_NOT_SAFE')

def identity_guard(binding,admin=False,impersonated=False,owner=False):
    name='sa'if admin else binding.operator;sid=binding.admin_sid if admin else binding.operator_sid
    original='sa'if impersonated or admin else binding.operator;original_sid=binding.admin_sid if impersonated or admin else binding.operator_sid
    flags=1 if admin else 0
    text=f"""IF DATALENGTH(SUSER_SNAME())<>DATALENGTH(N'{name}') OR CONVERT(varbinary(max),SUSER_SNAME())<>CONVERT(varbinary(max),N'{name}')
 OR SUSER_SID()<>0x{sid} OR DATALENGTH(ORIGINAL_LOGIN())<>DATALENGTH(N'{original}') OR CONVERT(varbinary(max),ORIGINAL_LOGIN())<>CONVERT(varbinary(max),N'{original}')
 OR SUSER_SID(ORIGINAL_LOGIN())<>0x{original_sid} OR COALESCE(IS_SRVROLEMEMBER(N'sysadmin'),-1)<>{flags}
 OR COALESCE(HAS_PERMS_BY_NAME(NULL,NULL,N'CONTROL SERVER'),-1)<>{flags} OR COALESCE(HAS_PERMS_BY_NAME(NULL,NULL,N'ALTER ANY LOGIN'),-1)<>{flags}
 THROW 51003,'Fixed actual role identity failed.',1;
"""
    if owner:
        text+=f"IF DB_ID(N'{binding.database}') IS NOT NULL AND NOT EXISTS(SELECT 1 FROM sys.databases WHERE name=N'{binding.database}' AND DATALENGTH(name)=DATALENGTH(N'{binding.database}') AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'{binding.database}') AND owner_sid=0x{binding.operator_sid}) THROW 51003,'Fixed actual operator owner failed.',1;\n"
    return text

def ownership_guard(binding):
    return f"""IF DB_NAME()<>N'{binding.database}' OR DATALENGTH(DB_NAME())<>DATALENGTH(N'{binding.database}') OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'{binding.database}')
 OR NOT EXISTS(SELECT 1 FROM sys.databases WHERE database_id=DB_ID() AND owner_sid=0x{binding.operator_sid})
 THROW 51003,'Fixed own role database failed.',1;
IF (SELECT COUNT(*) FROM (VALUES(N'SQLPERF.Project',N'SQL_PerformanceSchulung'),(N'SQLPERF.ContractVersion',N'1.0'),(N'SQLPERF.DemoId',N'IDX-012'),(N'SQLPERF.RunToken',N'{binding.token}')) e(Name,ExpectedValue)
 JOIN sys.extended_properties p ON p.class=0 AND p.major_id=0 AND p.minor_id=0 AND DATALENGTH(p.name)=DATALENGTH(e.Name) AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 WHERE DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.ExpectedValue) AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=CONVERT(varbinary(max),e.ExpectedValue))<>4
 THROW 51001,'Full fixed role ownership lost.',1;
"""

def attest(binding,stage,checkpoint,admin=False):
    return identity_guard(binding,admin,True)+ownership_guard(binding)+f"""IF @@TRANCOUNT<>0 OR XACT_STATE()<>0 THROW 51003,'Role checkpoint transaction state changed.',1;
SELECT (SELECT N'ROLE_CONTEXT' kind,N'{stage}' Stage,N'{checkpoint}' [Checkpoint],
 SUSER_SNAME() LoginName,CONVERT(varchar(170),SUSER_SID(),1) Sid,ORIGINAL_LOGIN() OriginalLogin,
 CONVERT(varchar(170),SUSER_SID(ORIGINAL_LOGIN()),1) OriginalSid,IS_SRVROLEMEMBER(N'sysadmin') Sysadmin,
 HAS_PERMS_BY_NAME(NULL,NULL,N'CONTROL SERVER') ControlServer,HAS_PERMS_BY_NAME(NULL,NULL,N'ALTER ANY LOGIN') AlterAnyLogin,
 CONVERT(int,@@SPID) SessionId,CONVERT(int,DB_ID()) DatabaseId,N'{binding.token}' RunToken FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
"""

def _decorate(source,binding,stage):
    if stage not in STAGES.values()or type(source)is not str:raise ValueError('FIXED_ROLE_PHASE')
    source=source.replace('\r\n','\n').replace('\r','\n')
    if source.count(BUILD)!=1 or re.search(r'\b(?:EXECUTE\s+AS|REVERT)\b',source,re.I):raise ValueError('FIXED_SINGLE_ROLE_BUILD')
    enter=f"EXECUTE AS LOGIN=N'{binding.operator}';\n"
    privilege='REVERT;\n'+attest(binding,stage,'ADMIN_BUILD',True)+BUILD+'\n'+enter+attest(binding,stage,'ROLE_RESTORED')
    output='SET NOCOUNT ON;\n'+enter+attest(binding,stage,'ROLE_START')+'GO\n'+source.replace(BUILD,privilege)+'\nGO\n'+attest(binding,stage,'ROLE_END')+'REVERT;\n'
    if len(output.encode())>160000:raise ValueError('ROLE_INPUT_CAP')
    safe_texts(binding,output)
    return output

def validate_context(rows,binding,stage,database_id,cost_frames):
    fields={'kind','Stage','Checkpoint','LoginName','Sid','OriginalLogin','OriginalSid','Sysadmin','ControlServer','AlterAnyLogin','SessionId','DatabaseId','RunToken'}
    if type(rows)is not list or type(database_id)is not int or database_id<5 or stage not in STAGES.values():raise ValueError('ROLE_CONTEXT_INPUT')
    actual=[r for r in rows if type(r)is dict and r.get('kind')=='ROLE_CONTEXT']
    if len(actual)!=4 or [r.get('Checkpoint')for r in actual]!=['ROLE_START','ADMIN_BUILD','ROLE_RESTORED','ROLE_END']:raise ValueError('ROLE_CONTEXT_POPULATION_ORDER')
    session=None
    for row in actual:
        if set(row)!=fields:raise ValueError('ROLE_CONTEXT_SCHEMA')
        admin=row['Checkpoint']=='ADMIN_BUILD';expected={'kind':'ROLE_CONTEXT','Stage':stage,'OriginalLogin':'sa','OriginalSid':'0x'+binding.admin_sid,'RunToken':binding.token,'LoginName':'sa'if admin else binding.operator,'Sid':'0x'+(binding.admin_sid if admin else binding.operator_sid)}
        if any(type(row[k])is not str or row[k]!=v for k,v in expected.items()):raise ValueError('ROLE_CONTEXT_IDENTITY')
        for k in ('Sysadmin','ControlServer','AlterAnyLogin'):
            if type(row[k])is not int or row[k]!=int(admin):raise ValueError('ROLE_CONTEXT_PRIVILEGE')
        if type(row['DatabaseId'])is not int or row['DatabaseId']!=database_id or type(row['SessionId'])is not int or not 1<=row['SessionId']<=32767:raise ValueError('ROLE_CONTEXT_SESSION_DB')
        session=row['SessionId']if session is None else session
        if row['SessionId']!=session:raise ValueError('ROLE_CONTEXT_SESSION_CHANGED')
    if type(cost_frames)is not list or len(cost_frames)!=2:raise ValueError('ROLE_COST_FRAMES')
    for frame,position in zip(cost_frames,('BEFORE','AFTER')):
        if type(frame)is not dict or frame.get('Frame')!=position or frame.get('Stage')!=stage or frame.get('RunToken')!=binding.token or type(frame.get('DatabaseId'))is not int or frame['DatabaseId']!=database_id or type(frame.get('SessionId'))is not int or frame['SessionId']!=session:raise ValueError('ROLE_COST_SESSION_CHANGED')
    return actual

def _module_guard(module,path,names):
    if module is None or type(getattr(module,'__file__',None))is not str or Path(module.__file__).resolve()!=path or sys.modules.get(getattr(module,'__name__',None))is not module:raise ValueError('ROLE_IMPORTED_MODULE_PATH')
    spec=getattr(module,'__spec__',None)
    direct=spec is None and getattr(module,'__name__',None)=='__main__' and path==FOLDER/'run_profile.py'
    if not direct and (type(getattr(spec,'origin',None))is not str or Path(spec.origin).resolve()!=path):raise ValueError('ROLE_IMPORTED_MODULE_PATH')
    code=compile(path.read_bytes(),str(path),'exec',dont_inherit=True)
    for name in names:
        expected=[c for c in code.co_consts if type(c)is types.CodeType and c.co_name==name]
        actual=getattr(module,name,None)
        if len(expected)!=1 or type(actual)is not types.FunctionType or actual.__code__!=expected[0] or actual.__globals__ is not module.__dict__ or Path(actual.__code__.co_filename).resolve()!=path:raise ValueError('ROLE_IMPORTED_MODULE_BYTES')

def imported_guard(controller):
    own=sys.modules.get(__name__);collector=sys.modules.get('sqlcmd_process')
    _module_guard(controller,FOLDER/'run_profile.py',('run_profile','cost_source','phase_command','execute_client','records'))
    _module_guard(own,FOLDER/'role_profile.py',('bind','_decorate','validate_context','safe_texts'))
    _module_guard(collector,ROOT/'Demos/00_Framework/Tools/sqlcmd_process.py',('start_sqlcmd','collect_process','build_sqlcmd_command'))
    if getattr(controller,'role_profile',None)is not own or getattr(controller,'SqlcmdResult',None)is not collector.SqlcmdResult or any(getattr(controller,name,None)is not getattr(collector,name,None)for name in ('start_sqlcmd','collect_process','build_sqlcmd_command')):raise ValueError('ROLE_IMPORTED_API_IDENTITY')

class _RoleClient:
    def __init__(self,controller,binding,executable,server):
        if Path(controller.__file__).resolve()!=FOLDER/'run_profile.py' or type(binding)is not Binding:raise ValueError('FIXED_ROLE_IMPLEMENTATION')
        if type(executable)is not str or Path(executable).name not in ('sqlcmd','sqlcmd.exe') or type(server)is not str or not re.fullmatch(r'(?:tcp:)?(?:127\.0\.0\.1|localhost),[1-9][0-9]{0,4}',server)or int(server.rsplit(',',1)[1])>65535:raise ValueError('FIXED_ROLE_CLIENT_TARGET')
        self.executable=executable;self.server=server
        imported_guard(controller)
        self.controller=controller;self.binding=binding;self.unknown=False;self.captures=[];self.inputs=[]
        self.sources=self.source_map()
    def source_map(self):
        files=[FOLDER/n for n in ('run_profile.py','role_profile.py','dml_boundary_evidence.py','lifecycle_evidence.py','storage_evidence.py','cost_evidence.py')]+sorted(FOLDER.glob('*.sql'))+[ROOT/'Demos/00_Framework/Tools/sqlcmd_process.py']
        if any(p.is_symlink()or not p.resolve().is_relative_to(ROOT)for p in files):raise ValueError('ROLE_SOURCE_PATH')
        return {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
    def execute(self,command,*,timeout_seconds):
        p=self.controller;b=self.binding
        if self.unknown:raise p.ClientEndUnknown('ROLE_CLIENT_END_UNKNOWN')
        imported_guard(p)
        if self.source_map()!=self.sources:raise ValueError('ROLE_SOURCE_CHANGED')
        script=Path(command[command.index('-i')+1]).resolve()
        if script.parent!=FOLDER or script.name not in PHASES or command[command.index('-U')+1]!=b.operator or '-P'in command:raise ValueError('FIXED_ROLE_COMMAND')
        variables=[{'StorageStage':stage}for stage in ('BASELINE','INDEXED','REBUILT')]if script.name=='22_Storage.sql'else [None]
        permitted=[p.phase_command(self.executable,self.server,'sql',b.operator,script,b.token,original,values)for original in (None,0,1)for values in variables]
        if type(command)is not list or any(type(v)is not str for v in command)or command not in permitted:raise ValueError('FIXED_ROLE_FULL_COMMAND')
        stage=STAGES.get(script.name);source=_decorate(p.cost_source(script),b,stage)if stage else 'SET NOCOUNT ON;\n'+identity_guard(b,owner=True)+'GO\n'+script.read_bytes().decode('utf-8')
        raw=source.encode('utf-8');safe_texts(b,source,*command)
        if len(raw)>160000:raise ValueError('ROLE_INPUT_CAP')
        process=None;response=None;poll=None;collector_failed=False;collector_code=None;capture=None;own=None
        actual=list(command);environment=private_environment(b,os.environ,stage is not None)
        try:
            runtime=ROOT/'Runtime';runtime.mkdir(exist_ok=True)
            with tempfile.NamedTemporaryFile('wb',prefix='idx012-role-',suffix='.sql',dir=runtime,delete=False)as stream:own=Path(stream.name).resolve();stream.write(raw)
            self.inputs.append({'Path':str(own),'InputSha256':hashlib.sha256(raw).hexdigest(),'Retained':True})
            actual[actual.index('-i')+1]=str(own);actual[actual.index('-U')+1]='sa'if stage else b.operator
            safe_texts(b,*actual)
            imported_guard(p)
            if self.source_map()!=self.sources:raise ValueError('ROLE_SOURCE_CHANGED')
            started=time.monotonic()
            try:
                process=p.start_sqlcmd(actual,environment=environment)
                response=p.collect_process(process,actual,timeout_seconds=timeout_seconds)
            except BaseException:
                self.unknown=True;collector_failed=True;collector_code='COLLECTOR_FAILED'
            finally:
                if process is not None:
                    try:poll=process.poll()
                    except BaseException:self.unknown=True
            pid=getattr(process,'pid',None);rc=getattr(process,'returncode',None)
            valid=type(response)is p.SqlcmdResult
            result_rc=response.returncode if valid and type(response.returncode)is int else None
            timed_out=response.timed_out if valid and type(response.timed_out)is bool else None
            duration=response.duration_seconds if valid and type(response.duration_seconds)in (int,float)and math.isfinite(response.duration_seconds)and response.duration_seconds>=0 else None
            if type(pid)is not int or pid<1 or type(poll)is not int or type(rc)is not int or poll!=rc or collector_failed or not valid or timed_out is not False or result_rc!=poll or result_rc is None or result_rc<0 or duration is None or type(response.command)is not tuple or response.command!=tuple(actual):self.unknown=True
            capture={'Phase':script.name,'Auth':'ADMIN_ORIGINAL_OPERATOR_CONTEXT'if stage else 'OPERATOR_AUTH','Pid':pid if type(pid)is int and pid>0 else None,'FinalPoll':poll if type(poll)is int else None,'ProcessReturnCode':rc if type(rc)is int else None,'ReturnCode':result_rc,'TimedOut':timed_out,'CollectorDurationSeconds':duration,'ElapsedSeconds':time.monotonic()-started,'CollectorFailed':collector_failed,'CollectorCode':collector_code,'UnknownSticky':self.unknown,'ServerRequestEnd':'NOT_ATTESTED','SourceBefore':self.sources,'SourceAfter':None,'InputText':None,'InputSha256':None,'Stdout':None,'Stderr':None,'ChannelStatus':'UNOBSERVED','RejectCode':None}
            self.captures.append(capture)
            try:capture['SourceAfter']=self.source_map()
            except BaseException:self.unknown=True;capture['UnknownSticky']=True
            if capture['SourceAfter']!=self.sources:self.unknown=True;capture['UnknownSticky']=True
            try:
                safe_texts(b,source)
                capture.update(InputText=source,InputSha256=hashlib.sha256(raw).hexdigest())
                if valid:
                    if type(response.stdout)is not str or type(response.stderr)is not str or len(response.stdout.encode())+len(response.stderr.encode())>1000000:raise ValueError('ROLE_CHANNEL_CAP_TYPE')
                    safe_texts(b,response.stdout,response.stderr)
                    capture.update(Stdout=response.stdout,Stderr=response.stderr,ChannelStatus='SAFE')
            except (ValueError,UnicodeError):
                capture.update(ChannelStatus='REJECTED',RejectCode='FAIL_CREDENTIAL_OR_CHANNEL_SAFETY');self.unknown=True;capture['UnknownSticky']=True
                raise p.ClientEndUnknown('ROLE_CHANNEL_NOT_SAFE')from None
            if self.unknown:raise p.ClientEndUnknown('ROLE_CLIENT_END_UNKNOWN')
            return response
        finally:
            if own is not None and not self.unknown:
                if own.parent!=ROOT/'Runtime' or own.is_symlink()or hashlib.sha256(own.read_bytes()).digest()!=hashlib.sha256(raw).digest():raise ValueError('ROLE_INPUT_CLEANUP_BINDING')
                own.unlink();self.inputs[-1]['Retained']=False
