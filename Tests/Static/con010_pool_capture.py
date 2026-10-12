"""Reine öffentliche V2-Clientcaptures; keine Prozesse, SQL- oder Provideraufrufe."""
import hashlib,importlib.util,json,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CONTRACT_PATH=ROOT/'Tests/Static/Fixtures/con010/pool-capture-contract-v2.json'
COLLECTOR_PATH=ROOT/'Demos/00_Framework/Tools/sqlcmd_process.py'
COLLECTOR_SHA='d8b553419bb34e4bafe7d0a7baee55ca28a5b97d1ad64710e131674aa6ca9757'
COLLECTOR_SHAS=frozenset((COLLECTOR_SHA,'ef33fbeb4436044ac2fd490b90b0608e4743f0f8accbbd3e3a2ee762fc2ac09d'))
SOURCE_KEYS=('Tests/Static/con010_pool_capture.py','Tests/Static/test_con010_pool_capture.py','Tests/Static/Fixtures/con010/pool-capture-contract-v2.json','Documentation/HowTo/SQL_SERVER_2025_AI_POOL_CAPTURE_V2.md','Demos/00_Framework/Tools/sqlcmd_process.py')
INPUT_SCOPE='CLIENT_INPUT_FILE_UTF8_BEFORE_SQLCMD_ENV_EXPANSION'
OUTPUT_SCOPE='COLLECTOR_DECODED_TEXT_UTF8_REENCODED'
PREFIX='CON010_POOL_CAPTURE_PART|'
_collector=None
class CredentialOutputRejected(ValueError):
    """Keine Rawdaten, Digests oder Credentialwerte am Fehlerobjekt."""
    def __init__(self):super().__init__('FAIL_CREDENTIAL_OUTPUT')
class ClientEndUnknown(ValueError):pass
CAPTURE_TYPES={'Contract':str,'Ordinal':int,'Kind':str,'Pid':int,'ReturnCode':int,'FinalPoll':(int,type(None)),'TimedOut':bool,'DurationSeconds':(int,float),'ClientProcessEnd':str,'ServerRequestEnd':str,'UnknownSticky':bool,'FollowupPolicy':str,'InputFileBytes':int,'InputFileSha256':str,'InputDigestScope':str,'StdoutTextBytes':int,'StdoutTextSha256':str,'StderrTextBytes':int,'StderrTextSha256':str,'OutputDigestScope':str,'CollectorSourceSha256':str,'CredentialSafety':str,'CaptureProvenance':str}

def number(value,minimum=0,maximum=360):
    if type(value) not in (int,float) or not math.isfinite(value) or not minimum<=value<=maximum:raise ValueError('Begrenzte tatsächliche Zahl erforderlich')
    return value

def integer(value,minimum=0,maximum=2147483647):
    if type(value) is not int or not minimum<=value<=maximum:raise ValueError('Plain Integer ohne Boolalias erforderlich')
    return value

def sha(value):
    if type(value) is not str or not re.fullmatch('[a-f0-9]{64}',value):raise ValueError('Vollständiger SHA256 erforderlich')
    return value

def sources():
    result={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_KEYS}
    result[SOURCE_KEYS[-1]]=collector_raw_sha()
    return result

def collector_raw_sha():
    value=hashlib.sha256(COLLECTOR_PATH.read_bytes()).hexdigest()
    if value not in COLLECTOR_SHAS:raise ValueError('Geprüfter öffentlicher Collector verändert')
    return value

def source_gate(expected):
    if type(expected) is not dict or set(expected)!=set(SOURCE_KEYS):raise ValueError('Nur vollständige vorhandene öffentliche Quellen zulässig')
    for value in expected.values():sha(value)
    if expected!=sources():raise ValueError('Tatsächliche öffentliche Sourcebytes abweichend')
    return expected

def collector_type():
    global _collector
    collector_raw_sha()
    if _collector is None:
        name='sqlcmd_process'
        module=sys.modules.get(name)
        if module is not None:
            if Path(module.__file__).resolve()!=COLLECTOR_PATH:raise ValueError('Fremde öffentliche Collectorauflösung')
        else:
            spec=importlib.util.spec_from_file_location(name,COLLECTOR_PATH)
            module=importlib.util.module_from_spec(spec);sys.modules[name]=module
            exec(compile(COLLECTOR_PATH.read_bytes(),str(COLLECTOR_PATH),'exec'),module.__dict__)
        _collector=module
    return _collector.SqlcmdResult

def decode_supported_frames(text):
    lines=text.splitlines();selected=[line for line in lines if line.startswith(PREFIX)]
    if not selected:return None
    # Es ist ausschließlich dieser feste Transport erlaubt, keine Encodingpipeline.
    if any(line.strip() and not line.startswith(PREFIX) and line!='SQLPERF_SUMMARY|PASS|OK' for line in lines):raise ValueError('Gemischter oder fremder Resultframe')
    parts=[line.split('|',4) for line in selected]
    if any(len(p)!=5 for p in parts):raise ValueError('Unvollständiger Resultframe')
    count,units=int(parts[0][2]),int(parts[0][3])
    if not 1<=units<=200000 or count!=(units+199)//200 or len(parts)!=count:raise ValueError('Vollständige begrenzte Framepopulation fehlt')
    for n,p in enumerate(parts,1):
        if p[1:4]!=[str(n),str(count),str(units)] or len(p[4])!=min(200,units-(n-1)*200)*4 or not re.fullmatch('[A-F0-9]+',p[4]):raise ValueError('Vollständige Frameordinals/-bytes fehlen')
    return bytes.fromhex(''.join(p[4] for p in parts)).decode('utf-16-le')

def credential_gate(input_text,stdout,stderr,command,secret_values):
    if type(secret_values) is not tuple or len(secret_values)!=4 or len(set(secret_values))!=4 or any(type(s) is not str or not re.fullmatch('[A-Za-z0-9!]{40,80}',s) for s in secret_values):raise ValueError('Vier vollständige private Callercredentials erforderlich')
    forms=[]
    for value in secret_values:forms.extend((value,value.encode('utf-8').hex(),value.encode('utf-8').hex().upper(),value.encode('utf-16-le').hex(),value.encode('utf-16-le').hex().upper()))
    texts=[input_text,stdout,stderr,*command]
    if any(form in text for text in texts for form in forms):raise CredentialOutputRejected()
    for text in (stdout,stderr):
        try:decoded=decode_supported_frames(text)
        except (ValueError,UnicodeError):raise ValueError('Ungültiger unterstützter Resulttransport') from None
        if decoded is not None:texts.append(decoded)
    if any(form in text for text in texts for form in forms):raise CredentialOutputRejected()

def collector_wait_seconds(remaining_seconds,phase_cap_seconds,*,required_cleanup_reserve_seconds):
    """Konfigurierte Nachlaufcaps, keine native Laufzeit-/OSgarantie."""
    number(remaining_seconds,0,360);number(phase_cap_seconds,0,300)
    number(required_cleanup_reserve_seconds,0,60)
    if required_cleanup_reserve_seconds<=0:raise ValueError('Erforderliche eigene Cleanupreserve darf nicht fehlen')
    available=min(remaining_seconds-required_cleanup_reserve_seconds,phase_cap_seconds)
    # Windows: zweimal(taskkill5+wait2), zweimalcommunicate5, letzterwait2=26.
    if available<=26:raise TimeoutError('Gemeinsames Budget vor Collector verbraucht')
    return available-26

def capture_sqlcmd(result,*,ordinal,pid,final_poll,input_bytes,secret_values,source_binding):
    source_gate(source_binding)
    if type(result) is not collector_type():raise ValueError('Tatsächlicher öffentlicher SqlcmdResulttyp erforderlich')
    integer(ordinal,0,63);integer(pid,1);integer(result.returncode,-2147483648)
    if final_poll is not None:integer(final_poll,-2147483648)
    if type(result.timed_out) is not bool or type(result.stdout) is not str or type(result.stderr) is not str or type(result.command) is not tuple or not result.command or any(type(s) is not str for s in result.command):raise ValueError('Vollständiger typisierter Collectorrecord erforderlich')
    number(result.duration_seconds)
    if type(input_bytes) is not bytes or not 1<=len(input_bytes)<=160000:raise ValueError('Vollständiger eigener UTF8-Input erforderlich')
    text=input_bytes.decode('utf-8')
    if '\x00' in text or any(s=='-P' or s.startswith('-P') for s in result.command):raise ValueError('Credentialargument oder ungültiger Input verboten')
    if len(result.stdout.encode('utf-8'))+len(result.stderr.encode('utf-8'))>1000000:raise ValueError('Vollcapture überschreitet Grenze')
    # Vor JEDEM Input-/Outputdigest; keine Secret- oder PasswordderivedHashes.
    credential_gate(text,result.stdout,result.stderr,result.command,secret_values)
    known=type(final_poll) is int and final_poll==result.returncode
    unknown=result.timed_out or not known or result.returncode<0
    return {'Contract':'CON010_POOL_CAPTURE_V2','Ordinal':ordinal,'Kind':'SQLCMD','Pid':pid,'ReturnCode':result.returncode,'FinalPoll':final_poll,'TimedOut':result.timed_out,'DurationSeconds':result.duration_seconds,'ClientProcessEnd':'KNOWN' if known else 'UNKNOWN','ServerRequestEnd':'UNKNOWN' if unknown else 'NOT_CAPTURED','UnknownSticky':unknown,'FollowupPolicy':'NO_FOLLOWUP_SQL' if unknown else 'REQUIRES_SEMANTIC_AND_SCOPE_GATE','InputFileBytes':len(input_bytes),'InputFileSha256':hashlib.sha256(input_bytes).hexdigest(),'InputDigestScope':INPUT_SCOPE,'StdoutTextBytes':len(result.stdout.encode('utf-8')),'StdoutTextSha256':hashlib.sha256(result.stdout.encode('utf-8')).hexdigest(),'StderrTextBytes':len(result.stderr.encode('utf-8')),'StderrTextSha256':hashlib.sha256(result.stderr.encode('utf-8')).hexdigest(),'OutputDigestScope':OUTPUT_SCOPE,'CollectorSourceSha256':source_binding[SOURCE_KEYS[-1]],'CredentialSafety':'CHECKED_AGAINST_PRIVATE_CALLER_LIST','CaptureProvenance':'NOT_INDEPENDENTLY_ATTESTED'}

def require_followup(previous_unknown,capture):
    if type(previous_unknown) is not bool or type(capture) is not dict or type(capture.get('UnknownSticky')) is not bool:raise ClientEndUnknown('Unvollständige sticky-Endbindung')
    if previous_unknown or capture['UnknownSticky']:raise ClientEndUnknown('UNKNOWN sperrt jedes Folge-SQL')
    validate_capture(capture)
    # Kein Ausführungsrecht: Semantik-/Scope-/Ownnamespacegate bleibt beim Producer.
    return 'REQUIRES_SEMANTIC_AND_SCOPE_GATE'

def validate_capture(item):
    if type(item) is not dict or set(item)!=set(CAPTURE_TYPES) or any(type(item[k]) not in (t if type(t) is tuple else (t,)) for k,t in CAPTURE_TYPES.items()):raise ValueError('Vollständige plain-typed Clientcapture fehlt')
    integer(item['Ordinal'],0,63);integer(item['Pid'],1);integer(item['ReturnCode'],-2147483648)
    if item['FinalPoll'] is not None:integer(item['FinalPoll'],-2147483648)
    number(item['DurationSeconds']);integer(item['InputFileBytes'],1,160000)
    for prefix in ('StdoutText','StderrText'):
        integer(item[prefix+'Bytes'],0,1000000);sha(item[prefix+'Sha256'])
        if item[prefix+'Bytes']==0 and item[prefix+'Sha256']!=hashlib.sha256(b'').hexdigest():raise ValueError('Leerer Kanal-/Digest inkohärent')
    if item['StdoutTextBytes']+item['StderrTextBytes']>1000000:raise ValueError('Gesamter Output überschreitet Grenze')
    sha(item['InputFileSha256'])
    known=type(item['FinalPoll']) is int and item['FinalPoll']==item['ReturnCode']
    unknown=item['TimedOut'] or not known or item['ReturnCode']<0
    if item['CollectorSourceSha256'] not in COLLECTOR_SHAS:raise ValueError('Nicht geprüfte Collectorbytes')
    fixed={'Contract':'CON010_POOL_CAPTURE_V2','Kind':'SQLCMD','InputDigestScope':INPUT_SCOPE,'OutputDigestScope':OUTPUT_SCOPE,'CredentialSafety':'CHECKED_AGAINST_PRIVATE_CALLER_LIST','CaptureProvenance':'NOT_INDEPENDENTLY_ATTESTED','ClientProcessEnd':'KNOWN' if known else 'UNKNOWN','ServerRequestEnd':'UNKNOWN' if unknown else 'NOT_CAPTURED','UnknownSticky':unknown,'FollowupPolicy':'NO_FOLLOWUP_SQL' if unknown else 'REQUIRES_SEMANTIC_AND_SCOPE_GATE'}
    if any(item[k]!=v for k,v in fixed.items()):raise ValueError('Deklarierte End-/Timeout-/Scopebindung inkohärent')
    return item

def capture_dotnet(*,ordinal,operation,lane,returned,configured_text,secret_values,source_binding):
    source_gate(source_binding);integer(ordinal)
    if type(operation) is not str or type(lane) is not str or operation not in ('OPEN','SCALAR','CLOSE') or lane not in ('A','B','U','OWNER') or type(returned) is not bool:raise ValueError('Feste .NET-Operation erforderlich')
    if operation=='SCALAR':
        if type(configured_text) is not str or not 1<=len(configured_text.encode('utf-8'))<=160000:raise ValueError('Vollständiger geheimerfreier Clienttext erforderlich')
        credential_gate(configured_text,'','',(),secret_values)
        digest=hashlib.sha256(configured_text.encode('utf-8')).hexdigest();scope='CLIENT_CONFIGURED_SECRET_FREE_TEXT'
    else:
        if configured_text is not None:raise ValueError('OPEN/CLOSE haben keinen SQLtext')
        credential_gate('','','',(),secret_values);digest=None;scope='NOT_APPLICABLE'
    return {'Ordinal':ordinal,'Operation':operation,'Lane':lane,'Returned':returned,'RequestEnd':'RETURNED_TO_CALLER' if returned else 'UNKNOWN','ConfiguredTextSha256':digest,'TextDigestScope':scope,'CredentialSafety':'CHECKED_AGAINST_PRIVATE_CALLER_LIST'}

def validate_dotnet_record(record):
    fields={'Ordinal','Operation','Lane','Returned','RequestEnd','ConfiguredTextSha256','TextDigestScope','CredentialSafety'}
    if type(record) is not dict or set(record)!=fields:raise ValueError('Vollständiger deklarierter .NET-Record erforderlich')
    if any(type(record[k]) is not str for k in ('Operation','Lane','RequestEnd','TextDigestScope','CredentialSafety')):raise ValueError('Plain String ohne Typalias erforderlich')
    integer(record['Ordinal'])
    if record['Operation'] not in ('OPEN','SCALAR','CLOSE') or record['Lane'] not in ('A','B','U','OWNER') or type(record['Returned']) is not bool or record['CredentialSafety']!='CHECKED_AGAINST_PRIVATE_CALLER_LIST':raise ValueError('Feste deklarierte .NET-Identität/-Safety fehlt')
    if record['Operation']=='SCALAR':
        sha(record['ConfiguredTextSha256'])
        if record['TextDigestScope']!='CLIENT_CONFIGURED_SECRET_FREE_TEXT':raise ValueError('Kein serverseitiger Executedtextclaim zulässig')
    elif record['ConfiguredTextSha256'] is not None or record['TextDigestScope']!='NOT_APPLICABLE':raise ValueError('OPEN/CLOSE enthalten keinen Textdigest')
    if record['RequestEnd']!=('RETURNED_TO_CALLER' if record['Returned'] else 'UNKNOWN'):raise ValueError('Deklariertes .NET-Ende inkohärent')
    return {'status':'WARN','record_validation':'PASS','operations':1,'unknown_operations':0 if record['Returned'] else 1,'caller_provenance':'NOT_INDEPENDENTLY_ATTESTED','runtime_qualification':'NOT_ESTABLISHED','server_request_attestation':'NOT_ESTABLISHED'}

def summary(captures):
    if type(captures) is not list or not 1<=len(captures)<=64:raise ValueError('Begrenzte Capturepopulation erforderlich')
    unknown=0;timeouts=0
    for n,item in enumerate(captures):
        validate_capture(item)
        if item['Ordinal']!=n:raise ValueError('Vollständige deklarierte Captureordnung fehlt')
        unknown+=int(item['UnknownSticky']);timeouts+=int(item['TimedOut'])
    return {'status':'WARN','captures':len(captures),'unknown_captures':unknown,'timed_out_captures':timeouts,'caller_provenance':'NOT_INDEPENDENTLY_ATTESTED','runtime_qualification':'NOT_ESTABLISHED','server_request_attestation':'NOT_ESTABLISHED','tp_con':'NOT_ESTABLISHED'}
