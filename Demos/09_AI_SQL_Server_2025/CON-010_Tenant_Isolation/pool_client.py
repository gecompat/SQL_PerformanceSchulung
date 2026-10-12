"""Gebundener SQLcmd-Bibliotheksadapter; kein Producer, Provisioner oder CLI."""
import hashlib,os,re,sys,time
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tests/Static'))
import con010_pool_capture as capture
if Path(capture.__file__).resolve()!=ROOT/'Tests/Static/con010_pool_capture.py':raise ValueError('Fremde Capturequelle')
DATABASE='SQLPERF_LAB_CON010_POOLPUBLIC'
INPUT_ROOT=ROOT/'Runtime/CON010_POOL_CLIENT_INPUTS'
SOURCE_KEYS=(*capture.SOURCE_KEYS,'Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_client.py','Tests/Static/test_con010_pool_client.py','Documentation/HowTo/SQL_SERVER_2025_AI_POOL_CLIENT.md')
PHASES={'PREFLIGHT':'master','SETUP':'master','IDENTITY':DATABASE,'STATE':DATABASE,'PHYSICAL_ABSENCE':DATABASE,'DROP_LOGIN':DATABASE,'DROP_DATABASE':DATABASE,'SQL_ABSENCE':'master'}
RECOVERY=frozenset(('DROP_LOGIN','DROP_DATABASE','SQL_ABSENCE'))
_SEAL=object()
class ClientFailure(ValueError):
    def __init__(self,code):super().__init__(code)
class ClientEndUnknown(ClientFailure):
    def __init__(self):super().__init__('CLIENT_END_UNKNOWN')
@dataclass(frozen=True)
class ClientResult:
    capture:dict
    stdout:str
    stderr:str
@dataclass(frozen=True)
class _CallerBinding:
    seal:object
    source:object
    token:str
    server:str
    executable:Path
    executable_sha256:str
    inputs:object
    normal_end:float
    cleanup_reserve:float

def source_map():
    values=capture.sources()
    values.update({name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_KEYS if name not in values})
    return values

def source_gate(expected):
    if type(expected) is not dict or set(expected)!=set(SOURCE_KEYS) or any(type(v) is not str or not re.fullmatch('[a-f0-9]{64}',v) for v in expected.values()) or expected!=source_map():raise ClientFailure('FAIL_SOURCE_BINDING')
    return expected

def _bind_caller(*,caller_scope,source_binding,token,server,executable,executable_sha256,input_plan,normal_end,required_cleanup_reserve_seconds):
    """Nur deklarierte interne Callerbindung, keine unabhängige RED-/CIDattestierung."""
    source_gate(source_binding)
    if caller_scope!='CON010_POOL_OWNER_SQLCMD' or type(caller_scope) is not str or type(token) is not str or not re.fullmatch('[A-F0-9]{16}',token) or type(server) is not str or not re.fullmatch(r'tcp:127\.0\.0\.1,[1-9][0-9]{0,4}',server) or int(server.rsplit(',',1)[1])>65535:raise ClientFailure('FAIL_CALLER_BINDING')
    if not isinstance(executable,Path) or executable.name.lower() not in ('sqlcmd','sqlcmd.exe') or not executable.is_absolute() or executable.is_symlink() or not executable.is_file():raise ClientFailure('FAIL_EXECUTABLE_BINDING')
    capture.sha(executable_sha256)
    if hashlib.sha256(executable.read_bytes()).hexdigest()!=executable_sha256:raise ClientFailure('FAIL_EXECUTABLE_BINDING')
    capture.number(normal_end,0,float('inf'))
    capture.number(normal_end-time.monotonic(),0,300);capture.number(required_cleanup_reserve_seconds,0,60)
    if required_cleanup_reserve_seconds<=0 or type(input_plan) is not dict or not 1<=len(input_plan)<=64:raise ClientFailure('FAIL_INPUT_PLAN')
    planned={}
    for ordinal,value in input_plan.items():
        capture.integer(ordinal,0,63)
        if type(value) is not dict or set(value)!={'Phase','InputSha256'} or type(value['Phase']) is not str or value['Phase'] not in PHASES:raise ClientFailure('FAIL_INPUT_PLAN')
        capture.sha(value['InputSha256']);planned[ordinal]=(value['Phase'],value['InputSha256'])
    return _CallerBinding(_SEAL,MappingProxyType(dict(source_binding)),token,server,executable,executable_sha256,MappingProxyType(planned),normal_end,required_cleanup_reserve_seconds)

def _private_environment(secret_values):
    # Kein freies ENVargument, keine SQLCMDINI-/Casecollision oder Secretargv.
    safe={'systemroot','windir','systemdrive','path','pathext','temp','tmp','home','userprofile','lang','lc_all','ld_library_path'}
    environment={k:v for k,v in os.environ.items() if k.casefold() in safe}
    environment.update(SQLCMDPASSWORD=secret_values[0],TenantSecretA=secret_values[1],TenantSecretB=secret_values[2],TenantSecretU=secret_values[3])
    return environment

class PoolSqlcmdClient:
    def __init__(self,binding):
        if type(binding) is not _CallerBinding or binding.seal is not _SEAL:raise ClientFailure('FAIL_CALLER_BINDING')
        self.binding=binding;self.unknown=False;self.failed=False;self.deadline_exceeded=False;self.cleanup_end=None;self.used=set()
    def begin_cleanup(self,end):
        if self.cleanup_end is not None:
            if type(end) not in (int,float) or end!=self.cleanup_end:raise ClientFailure('FAIL_CLEANUP_CLOCK_RESET')
            return self.cleanup_end
        capture.number(end,0,float('inf'));capture.number(end-time.monotonic(),0,60)
        self.cleanup_end=end;return end
    def _deadline(self,recovery):
        if recovery:
            if self.cleanup_end is None:raise ClientFailure('FAIL_CLEANUP_CLOCK_MISSING')
            end=self.cleanup_end
        else:end=min(self.binding.normal_end,self.cleanup_end) if self.cleanup_end is not None else self.binding.normal_end
        return end
    def _remaining(self,recovery):return self._deadline(recovery)-time.monotonic()
    def _input(self,ordinal,secret_values):
        path=INPUT_ROOT/self.binding.token/f'phase-{ordinal:02}.sql'
        for parent in (INPUT_ROOT,path.parent,path):
            if parent.is_symlink() or getattr(parent.lstat(),'st_file_attributes',0)&0x400:raise ClientFailure('FAIL_INPUT_BINDING')
        if path.resolve().parent!=(INPUT_ROOT/self.binding.token).resolve() or not path.is_file():raise ClientFailure('FAIL_INPUT_BINDING')
        raw=path.read_bytes()
        if not 1<=len(raw)<=160000:raise ClientFailure('FAIL_INPUT_BOUND')
        text=raw.decode('utf-8')
        capture.credential_gate(text,'','',(),secret_values)
        if '\ufeff' in text or '\x00' in text or re.search(r'(?m)^\s*(?::|!!)',text) or any(name not in ('TenantSecretA','TenantSecretB','TenantSecretU') for name in re.findall(r'\$\(([^)]*)\)',text)):raise ClientFailure('FAIL_INPUT_BINDING')
        if hashlib.sha256(raw).hexdigest()!=self.binding.inputs[ordinal][1]:raise ClientFailure('FAIL_INPUT_BINDING')
        return path,raw
    def execute(self,ordinal,*,secret_values,recovery=False):
        if self.unknown:raise ClientEndUnknown()
        if self.deadline_exceeded:raise ClientFailure('FAIL_DEADLINE_AFTER_CLIENT')
        if type(recovery) is not bool or type(ordinal) is not int or ordinal not in self.binding.inputs or ordinal in self.used:raise ClientFailure('FAIL_INPUT_PLAN')
        phase=self.binding.inputs[ordinal][0]
        if recovery!=(phase in RECOVERY) or (self.failed and not recovery):raise ClientFailure('FAIL_PHASE_ORDER')
        process=None;started=False;response=None;final_poll=None;pid=None;code=None;phase_end=None
        try:
            source_gate(dict(self.binding.source));path,raw=self._input(ordinal,secret_values)
            if os.environ.get('SQLCMDPASSWORD')!=secret_values[0]:raise ClientFailure('FAIL_ENV_BINDING')
            if hashlib.sha256(self.binding.executable.read_bytes()).hexdigest()!=self.binding.executable_sha256:raise ClientFailure('FAIL_EXECUTABLE_BINDING')
            capture.collector_type();collector=sys.modules['sqlcmd_process']
            command=collector.build_sqlcmd_command(executable=str(self.binding.executable),server=self.binding.server,database=PHASES[phase],script=path,auth='sql',username='sa')
            command.extend(('-C','-l','2'))
            capture.credential_gate(raw.decode('utf-8'),'','',tuple(command),secret_values)
            environment=_private_environment(secret_values)
            # Erneut aktuelle Quellen/Input/Restzeit unmittelbar vor Popen.
            source_gate(dict(self.binding.source))
            if self._input(ordinal,secret_values)[1]!=raw:raise ClientFailure('FAIL_INPUT_BINDING')
            now=time.monotonic();effective_end=self._deadline(recovery)
            remaining=effective_end-now
            phase_end=min(effective_end-self.binding.cleanup_reserve,now+40)
            wait=capture.collector_wait_seconds(remaining,40,required_cleanup_reserve_seconds=self.binding.cleanup_reserve)
            started=True;self.used.add(ordinal)
            process=collector.start_sqlcmd(command,environment=environment)
            pid=process.pid;capture.integer(pid,1)
            # Startoverhead verbraucht dieselbe Phase. Ein bereits verbrauchtes
            # primäres Fenster wird mit demselben Handle und Timeout0 gesammelt.
            primary_wait=max(0,min(wait,phase_end-time.monotonic()-26))
            if primary_wait<=0:self.unknown=True
            response=collector.collect_process(process,command,timeout_seconds=primary_wait)
        except capture.CredentialOutputRejected:code='FAIL_CREDENTIAL_OUTPUT'
        except BaseException:
            code='FAIL_CLIENT_ADAPTER'
            if started:self.unknown=True
        finally:
            if process is not None:
                try:
                    final_poll=process.poll()
                    if type(final_poll) is not int:self.unknown=True
                except BaseException:self.unknown=True
            elif started:self.unknown=True
        if started and response is None:self.unknown=True
        # Endstatus vor Privacy-/Source-/Digestgates festhalten. Ein abgelehnter
        # Capture darf Timeout, Signal oder inkohärente Enden nicht verdecken.
        if response is not None:
            if type(response) is not capture._collector.SqlcmdResult or type(response.timed_out) is not bool or type(response.returncode) is not int or response.timed_out or response.returncode<0 or final_poll!=response.returncode:self.unknown=True
        if phase_end is not None and time.monotonic()>phase_end:self.deadline_exceeded=True
        if self.unknown:
            self.failed=True;raise ClientEndUnknown()
        if code:
            self.failed=True;raise ClientFailure(code)
        # Kein ursprünglicher Fehlertext/Command/ENV am Fehlerobjekt.
        try:
            source_gate(dict(self.binding.source))
            if type(response) is not capture.collector_type() or response.command!=tuple(command):raise ValueError('Collectorbindung')
            item=capture.capture_sqlcmd(response,ordinal=ordinal,pid=pid,final_poll=final_poll,input_bytes=raw,secret_values=secret_values,source_binding={k:self.binding.source[k] for k in capture.SOURCE_KEYS})
            self.unknown=item['UnknownSticky']
            if self._remaining(recovery)<=0 or self.deadline_exceeded:
                self.deadline_exceeded=True;code='FAIL_DEADLINE_AFTER_CLIENT'
            if response.returncode!=0:self.failed=True
        except capture.CredentialOutputRejected:code='FAIL_CREDENTIAL_OUTPUT'
        except BaseException:code='FAIL_CAPTURE';self.unknown=True
        if self.unknown:
            self.failed=True;raise ClientEndUnknown()
        if code:
            self.failed=True;raise ClientFailure(code)
        return ClientResult(item,response.stdout,response.stderr)
