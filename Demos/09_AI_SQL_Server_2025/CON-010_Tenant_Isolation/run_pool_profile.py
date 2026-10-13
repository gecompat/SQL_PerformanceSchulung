"""Expliziter RED-Poolproducer für genau einen neuen eigenen Wegwerfnamespace."""
import argparse,hashlib,json,math,os,re,secrets,shutil,subprocess,sys,time,uuid
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
REQUAL_CONTROL=ROOT/'Runtime/AI_POOL_REQUALIFICATION'
REQUAL_CANONICAL='Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_REQUALIFICATION_REVIEW.md'
REQUAL_WAVE='PR226_REQUALIFICATION_V1'
OLD_HISTORY_PINS={'wave-stop.json': '8845f53d2a3c59fc32b620b507d46134c0327ddabf01066481ebf7c7ecd49676', 'public-ledger.json': '9ec27984871e0eb93d69ce27ec4410cbddbe9f4f910276787c5e59c859ef0d4c', 'candidate1/actual-result.json': 'c43269371c67dadd111907dd98d37ce313092db55d7db1af873ccc760d876067', 'candidate2/actual-result.json': 'd228ef221fd40832c38b29b91b97c34052b3d0b82fa9323aa49ac746c26f788d', 'candidate2/namespace-recovery-unknown.json': '3ac66de964b49b1ad5f7359dcbd861131db5241e54a9c0c2916660491250c693', 'candidate2/namespace-recovery-intent.json': '6003dc061b9ebb10df770c159434480d34ba7d419c6b98f94ae0359520c54299', 'closure.json': '911ea59e3e87d429687e5f74b72e3255973ceed43f3532e8b5f198591e296cc8', 'integration-proof.json': '51f2b088ce37699fdc824a8936ba47fd0044c1967b77111e889ae74820a4ca77', 'archive-proof.json': 'b1e7f2735f510c21e08dfe27f93ef97c5887a1069d6314277bb9221ebd7b8c63', 'candidate2/source-archive/Tests/Static/con010_pool_capture.py': '7c58915b1c3287d55570b8ab2190ff3d656168236632f7588d31f33eafcae4fb', 'candidate2/source-archive/Tests/Static/test_con010_pool_capture.py': '5da8a96dfe70c8c0a5eca543fa15b5e25dc86392635bd4819569f33aef2b012c', 'candidate2/source-archive/Tests/Static/Fixtures/con010/pool-capture-contract-v2.json': '73f6202c1763470262370682276254fb829c16f9725cfe5612362c00c0d283fc', 'candidate2/source-archive/Documentation/HowTo/SQL_SERVER_2025_AI_POOL_CAPTURE_V2.md': 'a06059df5226645942559b9831cd37f90c9a4df7383f9f696afb3975d4a9dbb1', 'candidate2/source-archive/Demos/00_Framework/Tools/sqlcmd_process.py': 'd8b553419bb34e4bafe7d0a7baee55ca28a5b97d1ad64710e131674aa6ca9757', 'candidate2/source-archive/Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_client.py': '3549592a6eb3ea30fc366394504a83bf7739de6116252592647a66d9e05c6232', 'candidate2/source-archive/Tests/Static/test_con010_pool_client.py': 'bfea086d28627d9be0d27c34beb9c53abb00f61b550ec8267bdae52aca2a6da3', 'candidate2/source-archive/Documentation/HowTo/SQL_SERVER_2025_AI_POOL_CLIENT.md': '5dbea159638ef105614834e626c40f36f9621b0304319c73fbc05c17df658957', 'candidate2/source-archive/Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/run_pool_profile.py': '289aab5f9f308936ac047ca4c6a4c72e35e24da8a59907f007c61a8830cf479d', 'candidate2/source-archive/Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_profile_inputs.py': '99fde1c8a9703d4d984fecf05a008a761dbc1ce733fe73ff584f7c0907d53a62', 'candidate2/source-archive/Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_profile_evidence.py': '40cf7a947269f70bdcd5dc977c45fdfe73439011ec7ddd1cb34847ec545e717b', 'candidate2/source-archive/Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_profile.ps1': '14b78abe8a0c963b3b5d000b1dc886233dd75b7358f9228232192865589fa698', 'candidate2/source-archive/Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/Expected/pool-profile-contract.json': '3d9696d86a611a760290d69ddefa094dfc7ea3cf1bd75b8f6e2073f95a82c33b', 'candidate2/source-archive/Tests/Static/test_con010_pool_profile.py': '8252ead5633f1eccd474ae20a7eb02fabdcd03bc6d0fe13f78546d99834f76f2', 'candidate2/source-archive/Documentation/HowTo/SQL_SERVER_2025_AI_POOL_PUBLIC.md': '47d7c79c3753ee69e3897d0dd1e40a4ffc8d2a4df669e7fc82e3b6b79861c4d0'}
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
def _read_bound(path,cap=100000):
    if not path.is_file() or path.is_symlink() or path.stat().st_size>cap:raise Failure('FAIL_WAVE_FILE')
    return json.loads(path.read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
def requalification_budget():
    return {'source_max':6,'source_checkpoint':3,'source_hard_stop':6,'native_prior':2,'native_additional_max':4,'native_total_max':6,'containers_prior':1,'containers_additional_max':4,'containers_total_max':5,'containers_per_candidate':1,'actual_checkpoint':3,'normal_seconds':300,'cleanup_seconds':60,'namespace_reserve_seconds':20,'namespace_reap_seconds':2,'child_cap_seconds':40,'cleanup_starts_before_child':True,'database':inputs.DATABASE,'run_token':'POOLPUBLIC','image':IMAGE,'build':'17.0.5005.3','model_calls':0,'max_logins':3,'rows':2,'dimension':3,'checkouts':6}
def requalification_history():
    data=_read_bound(REQUAL_CONTROL/'history.json')
    if type(data)is not dict or set(data)!={'contract','origin','files'} or data['contract']!='CON010_PR226_IMMUTABLE_HISTORY_V1' or type(data['origin'])is not str or not Path(data['origin']).is_absolute() or type(data['files'])is not dict or evidence.canonical(data['files'])!=evidence.canonical(OLD_HISTORY_PINS):raise Failure('FAIL_WAVE_HISTORY')
    if data['origin'].startswith(('\\\\','//')) or Path(data['origin']).is_symlink() or Path(data['origin']).name!='IntegratedRun_PR226':raise Failure('FAIL_WAVE_HISTORY')
    origin=Path(data['origin']).resolve()
    for name,value in OLD_HISTORY_PINS.items():
        path=origin/name
        if not path.resolve().is_relative_to(origin) or path.is_symlink() or digest(path)!=value:raise Failure('FAIL_WAVE_HISTORY')
    stopped=_read_bound(origin/'wave-stop.json');recovery=_read_bound(origin/'candidate2/namespace-recovery-unknown.json');old=_read_bound(origin/'public-ledger.json')
    if stopped['status']!='STOPPED_NATIVE_UNKNOWN_SOURCE_CORRECTION_ALLOWED' or recovery['status']!='RESOURCE_ABSENT_REQUEST_END_UNKNOWN' or recovery['mutative_request_end']!='UNKNOWN_STICKY' or stopped['cleanup_request_end']!='UNKNOWN_STICKY' or stopped['actual_cid_name_input_absent']is not True:raise Failure('FAIL_WAVE_HISTORY')
    for key,wanted in [('native_candidates_consumed',2),('new_own_containers',1),('sqlcmd_calls',0),('pool_children',0)]:
        if type(stopped[key])is not int or stopped[key]!=wanted:raise Failure('FAIL_WAVE_HISTORY')
    if type(old)is not list or len(old)!=2:raise Failure('FAIL_WAVE_HISTORY')
    for n,entry in enumerate(old,1):
        if type(entry)is not dict or type(entry['candidate'])is not int or entry['candidate']!=n or entry['status']!='FAIL' or entry['closed']is not False or entry['sql_absence']!='NOT_ESTABLISHED':raise Failure('FAIL_WAVE_HISTORY')
    return data,old
def requalification_input(candidate):
    if type(candidate)is not int or not 1<=candidate<=4:raise Failure('FAIL_WAVE_BUDGET')
    value=_read_bound(REQUAL_CONTROL/'input.json')
    if type(value)is not dict or type(value.get('source_candidate'))is not int or not 1<=value['source_candidate']<=6:raise Failure('FAIL_WAVE_INPUT')
    expected={'contract':'CON010_POOL_REQUALIFICATION_INPUT_V1','wave':REQUAL_WAVE,'source_candidate':value['source_candidate'],'candidate':candidate,'overall_native_candidate':2+candidate,'control':'Runtime/AI_POOL_REQUALIFICATION','canonical_scope':REQUAL_CANONICAL,'history_sha256':digest(REQUAL_CONTROL/'history.json'),'budget':requalification_budget(),'old_request_end':'UNKNOWN_STICKY','old_sql_cleanup':'NOT_ESTABLISHED','old_wave':'STOPPED_NO_C3_AFTER_UNKNOWN'}
    if evidence.canonical(value)!=evidence.canonical(expected):raise Failure('FAIL_WAVE_INPUT')
    return value
def admitted_requalification(candidate,admission,ledger):
    value=requalification_input(candidate);history,old=requalification_history();now=source_map()
    if type(admission)is not dict or admission.get('status')!='ADMITTED' or type(admission.get('candidate'))is not int or admission['candidate']!=candidate or admission.get('wave')!=REQUAL_WAVE or admission.get('scope')!='CON010_OPT_IN_RED_POOL_REQUALIFICATION' or admission.get('allow_red')is not True or admission.get('confirm_isolated_lab')is not True:raise Failure('FAIL_ROOT_ADMISSION')
    expected={'status':'ADMITTED','candidate':candidate,'source_candidate':value['source_candidate'],'wave':REQUAL_WAVE,'scope':'CON010_OPT_IN_RED_POOL_REQUALIFICATION','allow_red':True,'confirm_isolated_lab':True,'canonical_scope':REQUAL_CANONICAL,'canonical_scope_sha256':digest(ROOT/REQUAL_CANONICAL),'source_sha256':now,'input_sha256':digest(REQUAL_CONTROL/'input.json'),'history_sha256':digest(REQUAL_CONTROL/'history.json'),'delta_sha256':digest(REQUAL_CONTROL/'source-delta.json'),'root_review_sha256':digest(REQUAL_CONTROL/'root-review.json'),'source_proof_sha256':digest(REQUAL_CONTROL/'source-proof.json'),'budget_sha256':digest(REQUAL_CONTROL/'budget.json')}
    expected['checkpoint_overall3_sha256']=digest(REQUAL_CONTROL/'checkpoint-overall3.json') if candidate>1 else None
    expected['source_checkpoint3_sha256']=digest(REQUAL_CONTROL/'source-checkpoint3.json') if value['source_candidate']>=4 else None
    if evidence.canonical(admission)!=evidence.canonical(expected):raise Failure('FAIL_ROOT_ADMISSION')
    review=_read_bound(REQUAL_CONTROL/'root-review.json');proof=_read_bound(REQUAL_CONTROL/'source-proof.json');budget=_read_bound(REQUAL_CONTROL/'budget.json');delta=_read_bound(REQUAL_CONTROL/'source-delta.json')
    if review.get('status')!='SOURCE_REVIEW_CLOSED' or proof.get('status')!='REGISTERED' or review.get('source_sha256')!=now or proof.get('source_sha256')!=now or evidence.canonical(budget)!=evidence.canonical(requalification_budget()):raise Failure('FAIL_ROOT_ADMISSION')
    expected_delta={'contract':'CON010_C2_CURRENT_SOURCE_DELTA_V1','old_source_sha256':old[1]['source_sha256'],'current_source_sha256':now,'changed':sorted(k for k in now if now[k]!=old[1]['source_sha256'].get(k))}
    if evidence.canonical(delta)!=evidence.canonical(expected_delta) or not any(Path(k).suffix in ('.py','.ps1','.sql') for k in delta['changed']):raise Failure('FAIL_WAVE_DELTA')
    if type(ledger)is not list or len(ledger)!=candidate-1:raise Failure('FAIL_SERIAL_BUDGET')
    disk=REQUAL_CONTROL/'public-ledger.json'
    live=_read_bound(disk) if disk.exists() else []
    if evidence.canonical(live)!=evidence.canonical(ledger):
        reservation={'candidate':candidate,'overall_native_candidate':2+candidate,'wave':REQUAL_WAVE,'source_candidate':value['source_candidate'],'input_sha256':expected['input_sha256'],'status':'RESERVED','closed':False,'unknown':False,'namespace_absent':False,'inputs_absent':False,'source_sha256':now}
        if evidence.canonical(live)!=evidence.canonical([*ledger,reservation]):raise Failure('FAIL_SERIAL_BUDGET')
    for n,entry in enumerate(ledger,1):
        if type(entry)is not dict or entry.get('unknown')is not False:raise Failure('FAIL_NEW_WAVE_UNKNOWN_STOP')
        if type(entry.get('candidate'))is not int or entry['candidate']!=n or type(entry.get('overall_native_candidate'))is not int or entry['overall_native_candidate']!=n+2 or entry.get('wave')!=REQUAL_WAVE or entry.get('status')!='FAIL' or entry.get('closed')is not True or entry.get('namespace_absent')is not True or entry.get('inputs_absent')is not True or entry.get('image')!=IMAGE or entry.get('owner')!=OWNER:raise Failure('FAIL_SERIAL_BUDGET')
        if type(entry.get('containers_created'))is not int or not 0<=entry['containers_created']<=1 or type(entry.get('container_slots_reserved'))is not int or entry['container_slots_reserved']!=1 or entry.get('namespace_request_unknown')is not False:raise Failure('FAIL_SERIAL_BUDGET')
    if ledger and {k:v for k,v in ledger[-1]['source_sha256'].items() if Path(k).suffix in ('.py','.ps1','.sql')}=={k:v for k,v in now.items() if Path(k).suffix in ('.py','.ps1','.sql')}:raise Failure('FAIL_UNCHANGED_RETRY')
    if candidate>1:
        cp=_read_bound(REQUAL_CONTROL/'checkpoint-overall3.json')
        result_path=REQUAL_CONTROL/'candidate1/actual-result.json';review_path=REQUAL_CONTROL/'candidate1/root-result-review.json';actual=_read_bound(result_path,10*1024**2);actual_review=_read_bound(review_path)
        entry_sha=hashlib.sha256(evidence.canonical(ledger[0]).encode()).hexdigest();result_sha=digest(result_path)
        expected_review={'contract':'CON010_POOL_ACTUAL_CHECKPOINT3_REVIEW_V1','status':'ACTUAL_CHECKPOINT3_KNOWN_FAIL_CLOSED','overall_native':3,'first_new_entry_sha256':entry_sha,'history_sha256':expected['history_sha256'],'result_sha256':result_sha,'unknown':False,'stop':False}
        if evidence.canonical(actual_review)!=evidence.canonical(expected_review) or type(actual)is not dict or type(actual.get('candidate'))is not int or actual['candidate']!=1 or actual.get('status')!='FAIL' or type(actual.get('public_counts'))is not dict or actual['public_counts'].get('unknown')is not False or actual.get('source_sha256')!=ledger[0]['source_sha256']:raise Failure('FAIL_ACTUAL_CHECKPOINT')
        expected_cp={'contract':'CON010_POOL_OVERALL_CHECKPOINT3_V1','status':'REGISTERED','overall_native':3,'history_sha256':expected['history_sha256'],'first_new_entry_sha256':entry_sha,'root_result_review_sha256':digest(review_path),'actual_result_sha256':result_sha}
        if evidence.canonical(cp)!=evidence.canonical(expected_cp):raise Failure('FAIL_CHECKPOINT')
    if value['source_candidate']>=4:
        cp=_read_bound(REQUAL_CONTROL/'source-checkpoint3.json')
        ref={'contract':'CON010_POOL_SOURCE_CHECKPOINT3_V1','status':'REGISTERED','source_candidates_used':3,'source_ledger_sha256':digest(REQUAL_CONTROL/'source-ledger.json')}
        if evidence.canonical(cp)!=evidence.canonical(ref):raise Failure('FAIL_CHECKPOINT')
    return now
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

def setup_channels(call,expected_input):
    """Nur vollständige bekannte SETUP-Kanäle und deren tatsächliche Captures."""
    evidence.validate_call(call)
    if type(expected_input)is not str or type(call['Phase'])is not str or call['Phase']!='SETUP' or call['InputText']!=expected_input or call['ExpectedError']is not None:raise Failure('FAIL_SETUP_SUMMARY')
    captured=call['Capture']
    if captured['ReturnCode']!=0 or captured['UnknownSticky']is not False or captured['ClientProcessEnd']!='KNOWN':raise Failure('FAIL_SETUP_SUMMARY')
    stdout=[line for line in call['Stdout'].splitlines() if line]
    stderr=[line for line in call['Stderr'].splitlines() if line]
    first='POOLPUBLIC_ALL|ABSENT';last='SQLPERF_SUMMARY|PASS|OK'
    context="Changed database context to '"+inputs.DATABASE+"'."
    # Actual Native1: zwei stdout-Marker und genau eine separate stderr-Info.
    # Der zuvor fest erlaubte Kontext vor PASS im stdout bleibt explizit erlaubt.
    if (stdout,stderr) not in (([first,last],[]),([first,last],[context]),([first,context,last],[])):raise Failure('FAIL_SETUP_SUMMARY')
    return call

class Producer:
    def __init__(self,candidate,admission,ledger,*,wave=None):
        if wave not in (None,REQUAL_WAVE):raise Failure('FAIL_WAVE_INPUT')
        self.candidate=candidate;self.admission=admission;self.ledger=ledger;self.wave=wave
        self.sources=admitted(candidate,admission,ledger) if wave is None else admitted_requalification(candidate,admission,ledger)
        self.normal_end=time.monotonic()+300;self.cleanup_end=None;self.unknown=False;self.deadline_failed=False
        self.token=uuid.uuid4().hex[:16].upper();self.name='sqlperf-pool-public-'+self.token.lower();self.cid=None;self.port=None
        self.values=tuple(secrets.token_hex(32)+'!' for _ in range(4))
        self.sids={lane:secrets.token_hex(16).upper() for lane in evidence.LOGINS}
        self.folder=client.INPUT_ROOT/self.token;self.ordinal=0;self.captures=[];self.clients=[];self.extra_inputs=[]
        self.dbid=None;self.oid=None;self.held=None;self.baseline=None;self.pool_ready=False;self.record=None;self.controls=[]
        self.transcripts=[];self.negative_states=[];self.namespace_witness=None;self.bound_at_start=None;self.create_unknown=False;self.remove_unknown=False;self.remove_attempted=False;self.create_attempts=0;self.namespace_calls=[];self.no_create_witness=None;self.child_evidence=None;self.child_transport=None;self.sql_absent=False;self.namespace_absent=False;self.inputs_absent=False;self.started=False;self.cli=shutil.which('podman');self.sqlcmd=Path(shutil.which('sqlcmd') or '')
    def gate(self):
        if getattr(self,'wave',None) is None:current=admitted(self.candidate,self.admission,self.ledger)
        else:
            current=admitted_requalification(self.candidate,self.admission,self.ledger)
            _,old=requalification_history()
            if any(entry['name']==self.name for entry in old):raise Failure('FAIL_OLD_RESOURCE_BINDING')
        if current!=self.sources:raise Failure('FAIL_SOURCE_BINDING')
        if self.unknown:raise Unknown()
    def wave_binding(self):
        value=requalification_input(self.candidate)
        return {'Wave':REQUAL_WAVE,'SourceCandidate':value['source_candidate'],'NativeCandidate':self.candidate,'OverallNativeCandidate':self.candidate+2,'Control':'Runtime/AI_POOL_REQUALIFICATION','InputSha256':digest(REQUAL_CONTROL/'input.json'),'HistorySha256':digest(REQUAL_CONTROL/'history.json'),'PriorNativeAttempts':2,'PriorContainers':1,'PriorSqlcmd':0,'PriorPoolchildren':0,'OldRequestEnd':'UNKNOWN_STICKY'}
    def begin_cleanup(self):
        if self.cleanup_end is None:self.cleanup_end=time.monotonic()+60
        return self.cleanup_end
    def remaining(self,cleanup=False):
        end=self.begin_cleanup() if cleanup else min(self.normal_end,self.cleanup_end) if self.cleanup_end is not None else self.normal_end
        value=end-time.monotonic()
        if value<=0:raise Failure('FAIL_DEADLINE')
        return value
    def podman(self,args,cap,cleanup=False,*,creating=False):
        if getattr(self,'wave',None)==REQUAL_WAVE:return self.podman_held(args,cap,cleanup,creating=creating)
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
    def podman_held(self,args,cap,cleanup=False,*,creating=False):
        # Nur die neue Welle: dasselbe tatsächliche Objekt bis final_poll halten.
        if source_map()!=self.sources:raise Failure('FAIL_SOURCE_BINDING')
        if not cleanup:self.gate()
        if type(cap)not in (int,float) or not math.isfinite(cap) or not 0<cap<=20 or type(args)is not list or not args or any(type(x)is not str for x in args):raise Failure('FAIL_NAMESPACE_COMMAND')
        _,old=requalification_history()
        if any(any(entry['name']in arg for entry in old) for arg in args):raise Failure('FAIL_OLD_RESOURCE_BINDING')
        began=time.monotonic();end=began+min(cap,self.remaining(cleanup));environment=namespace_environment(dict(os.environ));command=[self.cli,*args]
        if creating:environment['MSSQL_SA_PASSWORD']=self.values[0]
        if args[0]=='rm':
            if self.remove_attempted:raise Unknown()
            self.remove_attempted=True
        if creating:self.create_attempts+=1
        process=None;out=err=b'';poll=None;unknown=False;timeout=False;collector=False
        try:
            process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=environment)
            try:out,err=process.communicate(timeout=max(0,end-2-time.monotonic()))
            except BaseException as failure:
                unknown=True;collector=True;timeout=isinstance(failure,subprocess.TimeoutExpired)
                try:process.kill()
                except BaseException:pass
                try:out,err=process.communicate(timeout=max(0,end-time.monotonic()))
                except BaseException:pass
            try:poll=process.poll()
            except BaseException:unknown=True
            if type(process.pid)is not int or process.pid<1 or type(poll)is not int or poll<0 or type(process.returncode)is not int or process.returncode!=poll:unknown=True
        except BaseException:unknown=True;collector=True
        duration=time.monotonic()-began
        if duration>end-began:unknown=True
        if unknown:
            self.unknown=True
            if creating:self.create_unknown=True
            if args[0]=='rm':self.remove_unknown=True
        # Ende zuerst kleben; Privacy-/UTF8-/Sourcefehler dürfen UNKNOWN nicht löschen.
        rc=process.returncode if process and type(process.returncode)is int else None
        witness={'Command':command,'Pid':process.pid if process else None,'FinalPoll':poll,'ReturnCode':rc,'TimedOut':timeout,'CollectorFailed':collector,'ProcessEnd':'UNKNOWN_STICKY' if unknown else 'HELD_PROCESS_RETURNED','DurationSeconds':duration,'ConfiguredCapSeconds':end-began,'SourceBefore':self.sources,'SourceAfter':None}
        self.namespace_calls.append(witness)
        try:
            text=out.decode('utf-8');diagnostic=err.decode('utf-8')
            capture.credential_gate('',text,diagnostic,tuple(command),self.values)
            witness.update(Stdout=text,Stderr=diagnostic)
        except capture.CredentialOutputRejected:raise Failure('FAIL_CREDENTIAL_OUTPUT') from None
        except BaseException:self.unknown=True;witness['ProcessEnd']='UNKNOWN_STICKY';raise Unknown() from None
        witness['SourceAfter']=source_map()
        if witness['SourceAfter']!=self.sources:raise Failure('FAIL_SOURCE_BINDING')
        if unknown:raise Unknown()
        if rc!=0:raise Failure('FAIL_NAMESPACE_COMMAND')
        self.remaining(cleanup)
        return text
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
        setup_input=inputs.setup(self.sids);self.sql(setup_input,'SETUP')
        if not self.transcripts:raise Failure('FAIL_SETUP_SUMMARY')
        setup_channels(self.transcripts[-1],setup_input)
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
    def capture_child_transport(self,raw,command,process,attempted,response,poll,poll_attempted,collector_failed,collector_returned,collector_error):
        """Prozessfakten vor Klassifikation; Raw erst nach konkreter Credentialprüfung."""
        observed=capture._collector is not None and type(response)is capture._collector.SqlcmdResult
        try:pid=process.pid if process is not None else None;process_rc=process.returncode if process is not None else None
        except BaseException:pid=None;process_rc=None;self.unknown=True
        pid=pid if type(pid)is int and pid>0 else None
        process_rc=process_rc if type(process_rc)is int else None
        final_poll=poll if type(poll)is int else None
        rc=response.returncode if observed and type(response.returncode)is int else None
        timeout=response.timed_out if observed and type(response.timed_out)is bool else None
        duration=response.duration_seconds if observed and type(response.duration_seconds)in (int,float) and math.isfinite(response.duration_seconds) and response.duration_seconds>=0 else None
        known=pid is not None and poll_attempted and final_poll is not None and process_rc==final_poll
        if attempted and (not known or not observed or collector_failed or timeout is not False or duration is None or rc is None or rc!=final_poll or rc<0):self.unknown=True
        item={'Contract':'CON010_POOL_CHILD_TRANSPORT_V1','Kind':'POWERSHELL_POOL_CHILD_TRANSPORT','Attempted':attempted,'HandleObserved':process is not None,'CollectorReturned':collector_returned,'CollectorResultTyped':observed,'CollectorFailed':collector_failed,'PollAttempted':poll_attempted,'Pid':pid,'ProcessReturnCode':process_rc,'FinalPoll':final_poll,'ReturnCode':rc,'TimedOut':timeout,'DurationSeconds':duration,'ClientProcessEnd':'NOT_STARTED' if not attempted else 'KNOWN' if known else 'UNKNOWN','ServerRequestEnd':'NOT_ATTESTED','UnknownSticky':self.unknown,'SourceBefore':self.sources,'SourceAfter':None,'SourceStatus':'UNOBSERVED','ScriptSha256':self.sources['Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_profile.ps1'],'InputText':None,'InputBytes':None,'InputSha256':None,'Stdout':None,'StdoutBytes':None,'StdoutSha256':None,'Stderr':None,'StderrBytes':None,'StderrSha256':None,'ChannelStatus':'UNOBSERVED','RejectCode':None}
        self.child_transport=item
        item['CollectorError']=collector_error
        try:
            item['SourceAfter']=source_map()
            item['SourceStatus']='OBSERVED' if item['SourceAfter']==self.sources else 'CHANGED'
            if item['SourceStatus']=='CHANGED':self.unknown=True;item['UnknownSticky']=True
        except BaseException:
            self.unknown=True;item['UnknownSticky']=True;item['SourceStatus']='READ_FAILED'
        try:
            text=raw.decode('utf-8');capture.credential_gate(text,'','',tuple(command),self.values)
            item.update(InputText=text,InputBytes=len(raw),InputSha256=hashlib.sha256(raw).hexdigest())
            if not observed:return None
            if type(response.stdout)is not str or type(response.stderr)is not str:raise ValueError('UNSAFE_CHANNEL_TYPE')
            stdout=response.stdout;stderr=response.stderr
            if len(stdout.encode())+len(stderr.encode())>1000000:raise ValueError('UNSAFE_CHANNEL_CAP')
            capture.credential_gate(text,stdout,stderr,tuple(command),self.values)
            try:receipt=json.loads(stdout,object_pairs_hook=evidence.unique)
            except (ValueError,UnicodeError):
                receipt=None;self.unknown=True;item['UnknownSticky']=True
                # JSON-Escapes ohne vollständig dekodierbares JSON sind nicht sicher prüfbar.
                if '\\' in stdout:raise ValueError('UNSAFE_JSON_ENCODING') from None
            if type(receipt)is dict and receipt.get('RequestEnd')!='RESPONSE_RECEIVED':self.unknown=True;item['UnknownSticky']=True
            if receipt is not None:evidence.credential_safe(receipt,self.values)
            # Auch der Diagnosekanal darf keine durch JSON-Escapes verdeckten Werte halten.
            if '\\' in stderr:
                try:diagnostic=json.loads(stderr,object_pairs_hook=evidence.unique)
                except (ValueError,UnicodeError):raise ValueError('UNSAFE_JSON_ENCODING') from None
                evidence.credential_safe(diagnostic,self.values)
            item.update(Stdout=stdout,StdoutBytes=len(stdout.encode()),StdoutSha256=hashlib.sha256(stdout.encode()).hexdigest(),Stderr=stderr,StderrBytes=len(stderr.encode()),StderrSha256=hashlib.sha256(stderr.encode()).hexdigest(),ChannelStatus='SAFE')
            return receipt
        except capture.CredentialOutputRejected:
            self.unknown=True;item['UnknownSticky']=True;item['ChannelStatus']='REJECTED';item['RejectCode']='FAIL_CREDENTIAL_OUTPUT';raise
        except BaseException as failure:
            self.unknown=True;item['UnknownSticky']=True
            item['ChannelStatus']='REJECTED';item['RejectCode']='FAIL_CREDENTIAL_OUTPUT' if str(failure)=='FAIL_CREDENTIAL_OUTPUT' else 'FAIL_CHILD_CHANNEL_SAFETY'
            raise Failure(item['RejectCode']) from None
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
        capture.collector_type();collector=capture._collector;process=None;attempted=False;response=None;poll=None;error=False;collector_returned=False;collector_error=None
        command=[str(PWSH),'-NoProfile','-File',str(HERE/'pool_profile.ps1'),'-Admission',str(path),'-AdmissionSha',hashlib.sha256(raw).hexdigest()];poll_attempted=False
        self.gate()
        try:
            attempted=True;process=collector.start_sqlcmd(command,environment=client._private_environment(self.values))
            wait=max(0,min(primary,phase_end-time.monotonic()-26))
            if wait<=0:self.unknown=True
            response=collector.collect_process(process,command,timeout_seconds=wait)
            collector_returned=True
        except BaseException as failure:
            error=True;self.unknown=True;collector_error='TIMEOUT' if isinstance(failure,subprocess.TimeoutExpired) else 'INTERRUPTED' if isinstance(failure,KeyboardInterrupt) else 'OSERROR' if isinstance(failure,OSError) else 'OTHER'
        finally:
            if process is not None:
                try:
                    poll_attempted=True
                    poll=process.poll()
                    if type(poll) is not int:self.unknown=True
                except BaseException:self.unknown=True
            elif attempted:self.unknown=True
        if time.monotonic()>phase_end:self.deadline_failed=True
        receipt=self.capture_child_transport(raw,command,process,attempted,response,poll,poll_attempted,error,collector_returned,collector_error)
        evidence.validate_child_transport(self.child_transport)
        if self.unknown:raise Unknown()
        if receipt is None:self.unknown=True;self.child_transport['UnknownSticky']=True;raise Unknown() from None
        if type(receipt) is not dict or receipt.get('RequestEnd')!='RESPONSE_RECEIVED':self.unknown=True;self.child_transport['UnknownSticky']=True
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
            record={'PoolReceipt':pool,'Child':child,'Baseline':self.baseline,'After':after,'DatabaseId':self.dbid,'ObjectId':self.oid,'Sids':self.sids,'Token':self.token,'Controls':self.controls,'PhysicalAbsence':'ACTUAL_NEW_OWNER_QUERY','SqlAbsence':'ACTUAL_NEW_DB_AND_PRINCIPAL_QUERY','NamespaceAbsence':'ACTUAL_FULL_CID_AND_NAME_QUERY','InputsAbsent':self.inputs_absent,'ContainerId':self.cid,'Port':self.port,'Actual':{'SqlCalls':self.transcripts,'NegativeStates':self.negative_states,'ChildInputText':self.child_evidence['InputText'],'ChildStdout':self.child_evidence['Stdout'],'ChildStderr':self.child_evidence['Stderr'],'ChildTransport':self.child_transport,'SourceSha256':self.sources,'Namespace':self.namespace_witness,'NamespaceCalls':self.namespace_calls}}
            if getattr(self,'wave',None)==REQUAL_WAVE:record['WaveBinding']=self.wave_binding()
            return Result('WARN','BOUNDED_POOL_PROFILE',evidence.summary(record),record)
        failed={'SqlCaptures':self.captures,'SqlCalls':self.transcripts,'NegativeStates':self.negative_states,'Child':self.child_evidence,'ChildTransport':getattr(self,'child_transport',None),'Namespace':self.namespace_witness,'Baseline':self.baseline,'NamespaceCalls':self.namespace_calls,'NoCreate':self.no_create_witness}
        if getattr(self,'wave',None)==REQUAL_WAVE:failed['WaveBinding']=self.wave_binding()
        return Result('FAIL',input_failure or namespace_failure or sql_failure or primary or 'FAIL_CLOSURE',{'primary_code':primary,'sql_cleanup_code':sql_failure,'namespace_cleanup_code':namespace_failure,'input_cleanup_code':input_failure,'runtime_qualification':'NOT_ESTABLISHED','sql_absence':'ACTUAL_NEW_QUERY' if self.sql_absent else 'NOT_ESTABLISHED','namespace_absence':self.namespace_absent,'remove_end':'UNKNOWN' if self.remove_unknown else 'RETURNED_TO_CALLER' if self.remove_attempted else 'NOT_STARTED','create_end':'UNKNOWN' if self.create_unknown else 'NOT_STARTED' if self.create_attempts==0 else 'RETURNED_TO_CALLER','unknown':self.unknown},failed)

def run(candidate,admission,*,wave=None):
    if wave not in (None,REQUAL_WAVE):raise Failure('FAIL_WAVE_INPUT')
    # Fehlender Provider vor Dateianlage, Container-/Login-/SQLeffekten.
    if not provider_available():return Result('SKIP','SKIP_PROVIDER_UNAVAILABLE',{'native_sql':0,'containers':0})
    control=CONTROL if wave is None else REQUAL_CONTROL
    ledger_path=control/'public-ledger.json';ledger=json.loads(ledger_path.read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique) if ledger_path.exists() else []
    producer=Producer(candidate,admission,ledger,wave=wave)
    entry={'candidate':candidate,'status':'RESERVED','closed':False,'unknown':False,'namespace_absent':False,'inputs_absent':False,'source_sha256':producer.sources}
    if wave is not None:
        value=requalification_input(candidate)
        entry.update(overall_native_candidate=2+candidate,wave=wave,source_candidate=value['source_candidate'],input_sha256=digest(control/'input.json'))
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
        if wave is not None:
            created=sum(1 for call in producer.namespace_calls if call['Command'][1]=='run' and call.get('ReturnCode')==0 and type(call.get('Stdout'))is str and re.fullmatch('[a-f0-9]{64}',call['Stdout'].strip()))
            entry.update(create_attempts=producer.create_attempts,containers_created=created,container_slots_reserved=1,namespace_request_unknown=producer.create_unknown or producer.remove_unknown)
        ledger_path.write_text(json.dumps([*ledger,entry]),encoding='utf-8')
    return result
def run_requalification(candidate,admission):
    """Neue explizite Welle; keine Umdeklaration oder Leerung der gestoppten Akte."""
    return run(candidate,admission,wave=REQUAL_WAVE)

def main(argv=None):
    parser=argparse.ArgumentParser(description='Explizites eigenes RED-Poolprofil; Default führt es nicht aus.')
    parser.add_argument('--allow-red',action='store_true');parser.add_argument('--confirm-isolated-lab',action='store_true');parser.add_argument('--candidate',type=int);parser.add_argument('--source-manifest',action='store_true');parser.add_argument('--wave',choices=['requalification'])
    args=parser.parse_args(argv)
    if args.source_manifest:print(json.dumps(source_map(),indent=2));return 0
    if not args.allow_red or not args.confirm_isolated_lab or args.candidate is None:parser.error('Explizite RED-/Lab-/Kandidatenzulassung erforderlich')
    try:
        control=REQUAL_CONTROL if args.wave=='requalification' else CONTROL
        path=control/'Root-admission.json'
        if not path.is_file() or path.stat().st_size>100000:raise Failure('FAIL_ROOT_ADMISSION')
        admission=json.loads(path.read_bytes().decode('utf-8'),object_pairs_hook=evidence.unique)
        result=run_requalification(args.candidate,admission) if args.wave=='requalification' else run(args.candidate,admission);print(json.dumps({'status':result.status,'code':result.code,'counts':result.counts},sort_keys=True));return 1 if result.status=='FAIL' else 0
    except BaseException:
        print('SQLPERF_SUMMARY|FAIL|FAIL_POOL_PROFILE');return 1
if __name__=='__main__':raise SystemExit(main())
