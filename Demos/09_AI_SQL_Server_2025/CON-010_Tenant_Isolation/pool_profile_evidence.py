"""Fester öffentlicher Poolprofilvertrag; reine Identitäts-/State-/Ergebnisprüfung."""
import hashlib,json,math,re,uuid
from pathlib import Path
from datetime import datetime
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
DATABASE='SQLPERF_LAB_CON010_POOLPUBLIC';CANONICAL='Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md'
LOGINS={'A':('CON010_LoginA','CON010_TenantA'),'B':('CON010_LoginB','CON010_TenantB'),'U':('CON010_LoginUnmapped','CON010_Unmapped')}
def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Duplicate native JSON key')
        result[key]=value
    return result
def decode(output):
    lines=[s.strip() for s in output.splitlines() if s.strip()]
    if not lines or lines[-1]!='SQLPERF_SUMMARY|PASS|OK':raise ValueError('Full native summary required')
    frames=[s.split('|',4) for s in lines[:-1]]
    if not frames or any(len(f)!=5 or f[0]!='CON010_POOL_CAPTURE_PART' for f in frames):raise ValueError('Full native frame required')
    count,chars=int(frames[0][2]),int(frames[0][3])
    if not 1<=chars<=200000 or count!=(chars+199)//200 or len(frames)!=count:raise ValueError('Native frame bound')
    for n,frame in enumerate(frames,1):
        if frame[1:4]!=[str(n),str(count),str(chars)] or len(frame[4])!=min(200,chars-(n-1)*200)*4 or not re.fullmatch('[A-F0-9]+',frame[4]):raise ValueError('Native ordinal/full-byte binding')
    return json.loads(bytes.fromhex(''.join(f[4] for f in frames)).decode('utf-16-le'),object_pairs_hook=unique)
def integer(value,expected):
    if type(value) is not int or value!=expected:raise ValueError('Actual integer binding differs')
def sid(value):
    if type(value) is not str or not re.fullmatch('[A-F0-9]{32}',value):raise ValueError('Full recorded 16-byte SID required')
    return value
def identity(data,lane,sids,dbid):
    fields={'DatabaseId','DatabaseName','SuserName','OriginalLogin','UserName','ServerSid','OriginalSid','UserSid','SessionId'}
    if type(data) is not dict or set(data)!=fields or lane not in LOGINS:raise ValueError('Full actual authenticated identity required')
    integer(data['DatabaseId'],dbid)
    login,user=LOGINS[lane]
    for field,expected in (('DatabaseName',DATABASE),('SuserName',login),('OriginalLogin',login),('UserName',user)):
        if type(data[field]) is not str or data[field]!=expected:raise ValueError('Fresh login context differs')
    for key in ('ServerSid','OriginalSid','UserSid'):
        if sid(data[key])!=sids[lane]:raise ValueError('Full server/original/user SID mapping differs')
    if type(data['SessionId']) is not int or data['SessionId']<1:raise ValueError('Actual session ID required')
def rowset(data,lane,sids,dbid,spoof=False):
    if type(data) is not dict or set(data)!={'Identity','Rows','SessionTenantBefore','SessionTenantAfter'}:raise ValueError('Full authenticated rowset required')
    identity(data['Identity'],lane,sids,dbid)
    if data['SessionTenantAfter'] is not None:raise ValueError('Actual context reset missing')
    if spoof:
        integer(data['SessionTenantBefore'],2)
    elif data['SessionTenantBefore'] is not None:raise ValueError('Unexpected session context')
    rows=data['Rows'];expected_id={'A':1,'B':2,'U':None}[lane]
    if type(rows) is not list or len(rows)!=(0 if expected_id is None else 1):raise ValueError('Actual tenant full-row population differs')
    if expected_id is not None:
        row=rows[0]
        if type(row) is not dict or set(row)!={'Id','TenantId','Content','ContentBytes','ContentHex','VectorJson','Dimensions','BaseType','Distance'}:raise ValueError('Complete source/vector row required')
        integer(row['Id'],expected_id);integer(row['TenantId'],expected_id);integer(row['Dimensions'],3)
        text='Synthetische Quelle '+lane;raw=text.encode('utf-16-le')
        if row['Content']!=text or type(row['Content']) is not str or row['ContentHex']!=raw.hex().upper():raise ValueError('Full original source bytes differ')
        integer(row['ContentBytes'],len(raw))
        if row['BaseType']!='float32' or type(row['VectorJson']) is not str:raise ValueError('Actual VECTOR type missing')
        vector=json.loads(row['VectorJson'])
        if type(vector) is not list or len(vector)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v!=ref for v,ref in zip(vector,(1,0,0))):raise ValueError('All actual vector coordinates differ')
        if type(row['Distance']) not in (int,float) or not math.isfinite(row['Distance']) or row['Distance']!=0:raise ValueError('Actual exact cosine differs')
    return data
def denial(data,lane,sids,dbid,kind,severities):
    codes={'ALTER':33268,'IMPERSONATE':15517,'REVOKED_SELECT':229}
    if type(data) is not dict or set(data)!={'Identity','Kind','ErrorNumber','ErrorSeverity','ErrorState','ErrorLine','ErrorProcedure','MessageBytes','MessageHex'} or kind not in codes or data['Kind']!=kind:raise ValueError('Full actual denial record required')
    identity(data['Identity'],lane,sids,dbid);integer(data['ErrorNumber'],codes[kind]);integer(data['ErrorSeverity'],severities[codes[kind]])
    for field,minimum,maximum in (('ErrorState',0,255),('ErrorLine',1,2147483647),('MessageBytes',2,8000)):
        if type(data[field]) is not int or not minimum<=data[field]<=maximum:raise ValueError('Actual error metadata required')
    if data['ErrorProcedure'] is not None and type(data['ErrorProcedure']) is not str:raise ValueError('Actual procedure metadata')
    if type(data['MessageHex']) is not str or not re.fullmatch('(?:[A-F0-9]{2})+',data['MessageHex']) or len(bytes.fromhex(data['MessageHex']))!=data['MessageBytes']:raise ValueError('Full native UTF16 message required')
    bytes.fromhex(data['MessageHex']).decode('utf-16-le')
    return data
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def same(a,b):
    if canonical(a)!=canonical(b):raise ValueError('Full source/RLS/principal/state continuity differs')
def full_name(row,key,bytekey,hexkey):
    if type(row[key]) is not str:raise ValueError('Full Unicode name required')
    raw=row[key].encode('utf-16-le');integer(row[bytekey],len(raw))
    if type(row[hexkey]) is not str or row[hexkey]!=raw.hex().upper():raise ValueError('Full Unicode name bytes differ')

def principals(data,sids,object_id):
    if type(object_id) is not int or object_id<5:raise ValueError('Independent own ObjectId required')
    if type(data) is not dict or set(data)!={'Logins','ServerPermissions','ServerRoles','Users','DatabasePermissions','DatabaseRoles'}:raise ValueError('Full principal baseline required')
    if any(type(v) is not list for v in data.values()) or len(data['Logins'])!=3 or len(data['Users'])!=3 or len(data['ServerPermissions'])!=3 or len(data['DatabasePermissions'])!=6 or data['ServerRoles']!=[] or data['DatabaseRoles']!=[]:raise ValueError('Full principal/positive permission populations differ')
    login_fields={'principal_id','name','name_bytes','name_hex','sid','type','type_desc','is_disabled','create_date','modify_date','default_database_name','default_language_name','credential_id','is_fixed_role','is_policy_checked','is_expiration_checked'}
    user_fields={'principal_id','name','name_bytes','name_hex','sid','type','authentication_type','default_schema_name','is_fixed_role','create_date','modify_date'}
    for rows,fields in ((data['Logins'],login_fields),(data['Users'],user_fields)):
        for row in rows:
            if type(row) is not dict or set(row)!=fields:raise ValueError('Complete principal schema required')
            full_name(row,'name','name_bytes','name_hex');sid(row['sid'])
            for field in ('type','create_date','modify_date'):
                if type(row[field]) is not str:raise ValueError('Full actual principal fields required')
    perm_fields={'class','major_id','grantee_principal_id','grantor_principal_id','type','permission_name','permission_bytes','permission_hex','state'}
    for key in ('ServerPermissions','DatabasePermissions'):
        for p in data[key]:
            if type(p) is not dict or set(p)!=(perm_fields|({'minor_id'} if key=='DatabasePermissions' else set())):raise ValueError('Complete permission schema required')
            full_name(p,'permission_name','permission_bytes','permission_hex')
            for field in ('class','major_id','grantee_principal_id','grantor_principal_id',*(['minor_id'] if key=='DatabasePermissions' else [])):
                if type(p[field]) is not int or p[field]<0:raise ValueError('Actual permission integer required')
            if type(p['type']) is not str or type(p['state']) is not str:raise ValueError('Actual permission type/state required')
    for lane in LOGINS:
        login,user=LOGINS[lane];rows=[r for r in data['Logins'] if r['name']==login];users=[r for r in data['Users'] if r['name']==user]
        if len(rows)!=1 or len(users)!=1:raise ValueError('Exact own login/user absent')
        r=rows[0];u=users[0]
        if r['sid']!=sids[lane] or u['sid']!=sids[lane] or r['type']!='S' or r['type_desc']!='SQL_LOGIN' or u['type']!='S' or r['is_disabled'] is not False or r['is_fixed_role'] is not False or r['credential_id'] is not None or r['default_database_name']!=DATABASE or r['default_language_name']!='us_english' or r['is_policy_checked'] is not False or r['is_expiration_checked'] is not False or u['authentication_type']!=1 or type(u['authentication_type']) is not int or u['default_schema_name']!='dbo' or u['is_fixed_role'] is not False:raise ValueError('Full name/SID/type/defaults/policy/mapping differ')
        for obj in (r,u):
            if type(obj['principal_id']) is not int or obj['principal_id']<1 or type(obj['create_date']) is not str or type(obj['modify_date']) is not str:raise ValueError('Actual full principal IDs/timestamps missing')
        permissions=[p for p in data['ServerPermissions'] if p['grantee_principal_id']==r['principal_id']]
        expected_server={(100,0,'COSQ','CONNECT SQL','G',1)}
        actual_server={(p['class'],p['major_id'],p['type'],p['permission_name'],p['state'],p['grantor_principal_id']) for p in permissions}
        if actual_server!=expected_server or len(permissions)!=1:raise ValueError('Actual positive CONNECT SQL tuple differs')
        permissions=[p for p in data['DatabasePermissions'] if p['grantee_principal_id']==u['principal_id']]
        if len(permissions)!=2 or {(p['class'],p['major_id'],p['minor_id'],p['type'],p['permission_name'],p['state'],p['grantor_principal_id']) for p in permissions}!={(0,0,0,'CO  ','CONNECT','G',1),(1,object_id,0,'SL  ','SELECT','G',1)}:raise ValueError('Actual complete CONNECT/SELECT tuple differs')
    return data

def native_error(output,code,detail):
    frame='\n'.join(line.strip() for line in output.splitlines() if line.strip())
    return re.fullmatch(r'Msg '+re.escape(str(code))+r', Level [0-9]+, State [0-9]+(?:, [^\r\n]*)?\n'+re.escape(detail)+r':[^\r\n]*',frame) is not None

def state(data,dbid,object_id,sids,complete=True):
    fields={'Principals','PrincipalBytes','PrincipalHex','db','config','files','schemas','objects','indexes','index_columns','columns','policies','predicates','modules','rows','properties'}
    if type(data) is not dict or set(data)!=fields:raise ValueError('Full state schema required')
    raw=bytes.fromhex(data['PrincipalHex'])
    integer(data['PrincipalBytes'],len(raw));same(json.loads(raw.decode('utf-16-le'),object_pairs_hook=unique),data['Principals'])
    if complete:principals(data['Principals'],sids,object_id)
    for key,n in (('db',1),('config',41),('files',2),('schemas',2),('objects',4),('indexes',1),('index_columns',1),('columns',4),('policies',1),('predicates',1),('modules',1),('rows',2),('properties',4)):
        if type(data[key]) is not list or len(data[key])!=n:raise ValueError('Full state population missing: '+key)
    integer(data['db'][0]['database_id'],dbid)
    if data['db'][0]['name']!=DATABASE or data['db'][0]['compatibility_level']!=170 or data['db'][0]['recovery_model_desc']!='SIMPLE':raise ValueError('Actual own DB options differ')
    for row,lane,id in zip(data['rows'],('A','B'),(1,2)):
        if set(row)!={'Id','TenantId','ContentBytes','ContentHex','VectorJson'}:raise ValueError('Full source row required')
        integer(row['Id'],id);integer(row['TenantId'],id)
        raw=('Synthetische Quelle '+lane).encode('utf-16-le');integer(row['ContentBytes'],len(raw))
        if row['ContentHex']!=raw.hex().upper() or type(row['VectorJson']) is not str:raise ValueError('Full original source lost')
        vector=json.loads(row['VectorJson'])
        if type(vector) is not list or len(vector)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v!=e for v,e in zip(vector,(1,0,0))):raise ValueError('Full source VECTOR differs')
    v=data['columns'][3]
    integer(v['object_id'],object_id);integer(v['vector_dimensions'],3);integer(v['vector_base_type'],0)
    if v['name']!='V' or v['is_nullable'] is not False:raise ValueError('Actual VECTOR column shape lost')
    for column,name in zip(data['columns'],('Id','TenantId','Content','V')):
        integer(column['object_id'],object_id)
        if column['name']!=name or column['is_nullable'] is not False:raise ValueError('Full own column shape lost')
    if data['policies'][0]['is_enabled'] is not True or data['policies'][0]['is_schema_bound'] is not True or data['modules'][0]['is_schema_bound'] is not True:raise ValueError('Actual enabled schema-bound RLS lost')
    integer(data['predicates'][0]['target_object_id'],object_id)
    schemas={}
    for schema in data['schemas']:
        if set(schema)!={'schema_id','name','principal_id'} or type(schema['schema_id']) is not int or schema['schema_id']<1 or schema['name'] not in ('lab','sec') or schema['name'] in schemas:raise ValueError('Full own schemas differ')
        integer(schema['principal_id'],1);schemas[schema['name']]=schema['schema_id']
    if len(set(schemas.values()))!=2:raise ValueError('Distinct own schemas required')
    objects={};ids=set()
    for obj in data['objects']:
        if type(obj) is not dict or set(obj)!={'object_id','schema_id','parent_object_id','name','type','create_date','modify_date'}:raise ValueError('Full declared object schema required')
        for field in ('object_id','schema_id','parent_object_id'):
            if type(obj[field]) is not int or obj[field]<0:raise ValueError('Actual object IDs required')
        if obj['object_id']<1 or obj['object_id'] in ids or type(obj['name']) is not str or not obj['name'] or type(obj['type']) is not str or any(type(obj[f]) is not str or not obj[f] for f in ('create_date','modify_date')):raise ValueError('Full unique object IDs/metadata required')
        ids.add(obj['object_id'])
        # sys.objects.type is char(2); retain its actual representation in the state.
        kind={'U ':'U','PK':'PK','IF':'IF','SP':'SP'}.get(obj['type'])
        if kind is None or kind in objects:raise ValueError('Exactly table/PK/inlineTF/securitypolicy required')
        objects[kind]=obj
    for kind,name,schema in (('U','Documents','lab'),('IF','TenantPredicate','sec'),('SP','TenantPolicy','sec')):
        obj=objects[kind]
        if obj['name']!=name:raise ValueError('Full own object name differs')
        integer(obj['schema_id'],schemas[schema]);integer(obj['parent_object_id'],0)
    integer(objects['U']['object_id'],object_id);integer(objects['PK']['schema_id'],schemas['lab']);integer(objects['PK']['parent_object_id'],object_id)
    index=data['indexes'][0];integer(index['object_id'],object_id);integer(index['index_id'],1);integer(index['type'],1)
    if index['name']!=objects['PK']['name'] or index['is_unique'] is not True or index['is_primary_key'] is not True or index['is_disabled'] is not False:raise ValueError('Actual PK/index reference differs')
    for field,value in (('object_id',object_id),('index_id',1),('column_id',1),('key_ordinal',1)):integer(data['index_columns'][0][field],value)
    integer(data['modules'][0]['object_id'],objects['IF']['object_id']);integer(data['policies'][0]['object_id'],objects['SP']['object_id']);integer(data['predicates'][0]['object_id'],objects['SP']['object_id'])
    return data

ORDER=('A','B','U','A','B','U')
PHASES={'ASSEMBLY','OWNER_CREDENTIAL','OWNER_CONNECTION','OWNER_OPEN','LANE_CREDENTIAL','CHECKOUT_CONNECTION','CHECKOUT_MARKERS','CHECKOUT_OPEN','CHECKOUT_BEFORE','CHECKOUT_SPOOF','CHECKOUT_AFTER','CHECKOUT_OWNER','CHECKOUT_CLOSE','POOL_CLEAR','OWNER_CLOSE','SECURE_DISPOSE','COMPLETE'}
FAULT_CODES={'POOL_ASSEMBLY_PATH','POOL_CREDENTIAL_BINDING','POOL_CREDENTIAL_INSTANCE','POOL_SECRET_CONNECTIONSTRING','POOL_SOURCE_PATH','POOL_SOURCE_CHANGED','POOL_AUTHORITY_CHANGED','POOL_ADMISSION_CHANGED','POOL_DEADLINE','POOL_OPEN_STATE','POOL_OPEN_REQUEST_UNKNOWN','POOL_COMMAND_DEADLINE','POOL_COMMAND_REQUEST_UNKNOWN','POOL_TYPED_VALUE','POOL_OWNER_POPULATION','POOL_CLOSE_STATE','POOL_PHYSICAL_POPULATION','POOL_PHYSICAL_RESIDUE'}

def fault(value,status):
    if status=='PASS':
        if value is not None:raise ValueError('Positive receipt has failure diagnostics')
        return
    if type(value) is not dict or set(value)!={'Phase','Types','Code'} or type(value['Phase']) is not str or value['Phase'] not in PHASES or type(value['Types']) is not list or not 1<=len(value['Types'])<=6 or any(type(v) is not str or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]{0,159}',v) for v in value['Types']) or (value['Code'] is not None and (type(value['Code']) is not str or value['Code'] not in FAULT_CODES)):raise ValueError('Bounded fixed failure diagnostic required')
def guid(value):
    if type(value) is not str or not re.fullmatch('[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}',value) or uuid.UUID(value).int==0:raise ValueError('Actual nonempty typed GUID required')
    return value
def rows(value,lane,sids,dbid):
    if type(value) is not dict or set(value)!={'Identity','Rows','Context'}:raise ValueError('Full pooled query schema required')
    identity(value['Identity'],lane,sids,dbid)
    # Source-only reuse of C5's exact row oracle; context is a separate actual field.
    rowset({'Identity':value['Identity'],'Rows':value['Rows'],'SessionTenantBefore':None,'SessionTenantAfter':None},lane,sids,dbid)
    return value
def validate_pool(data,sids,dbid,token):
    if type(token) is not str or not re.fullmatch('[A-F0-9]{16}',token):raise ValueError('Own token required')
    if type(data) is not dict or set(data)!={'Status','RequestEnd','PoolCleanup','Records','Operations','RemainingConnections','Token','Fault'} or data['Status']!='PASS' or data['RequestEnd']!='RESPONSE_RECEIVED' or data['PoolCleanup']!='ACTUAL_CLEAR_CLOSE_AND_NEW_ABSENCE' or data['Token']!=token:raise ValueError('Complete known positive pool receipt required')
    fault(data['Fault'],data['Status'])
    if type(data['Records']) is not list or len(data['Records'])!=6 or data['RemainingConnections']!=[] or type(data['RemainingConnections']) is not list:raise ValueError('Actual six checkouts/new connection absence required')
    held={};sessions=set();poolkeys=set()
    for ordinal,(record,lane) in enumerate(zip(data['Records'],ORDER),1):
        fields={'Ordinal','Lane','ClientConnectionId','ConnectionState','PoolKeySha','CredentialOrdinal','Before','After','Owner'}
        if type(record) is not dict or set(record)!=fields or record['Lane']!=lane or record['ConnectionState']!='Open':raise ValueError('Exact checkout/order/Open receipt required')
        integer(record['Ordinal'],ordinal);integer(record['CredentialOrdinal'],{'A':1,'B':2,'U':3}[lane]);guid(record['ClientConnectionId'])
        if type(record['PoolKeySha']) is not str or not re.fullmatch('[A-F0-9]{64}',record['PoolKeySha']):raise ValueError('Stable exact own pool key required')
        before=rows(record['Before'],lane,sids,dbid);after=rows(record['After'],lane,sids,dbid)
        if before['Context'] is not None:raise ValueError('Actual reset must precede explicit repair')
        integer(after['Context'],2 if lane=='A' else 1);same(before['Identity'],after['Identity']);same(before['Rows'],after['Rows'])
        owner=record['Owner']
        expected={'SessionId','ConnectionId','ConnectTime','LoginTime','LoginName','OriginalLoginName','Sid','DatabaseId','ProgramName','NetTransport','AuthScheme'}
        if type(owner) is not dict or set(owner)!=expected:raise ValueError('Full owner physical/session binding required')
        integer(owner['SessionId'],before['Identity']['SessionId']);integer(owner['DatabaseId'],dbid);guid(owner['ConnectionId'])
        if owner['LoginName']!=LOGINS[lane][0] or owner['OriginalLoginName']!=LOGINS[lane][0] or owner['Sid']!=sids[lane] or owner['ProgramName']!='SQLPERF_POOLPUBLIC_'+token+'_'+lane or owner['NetTransport']!='TCP' or owner['AuthScheme']!='SQL':raise ValueError('Full SID/DB/App/nonce/transport binding differs')
        for key in ('ConnectTime','LoginTime'):
            if type(owner[key]) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?',owner[key]):raise ValueError('Actual server timestamps required')
            datetime.fromisoformat(owner[key])
        physical=(owner['ConnectionId'],owner['ConnectTime'])
        if lane in held:
            previous=held[lane]
            if physical!=previous['physical'] or record['PoolKeySha']!=previous['pool_key']:raise ValueError('Physical reuse/exact pool key missing')
        else:
            if owner['ConnectionId'] in sessions:raise ValueError('Cross-lane physical connection reused')
            if record['PoolKeySha'] in poolkeys:raise ValueError('Three distinct actual App/nonce pool keys required')
            poolkeys.add(record['PoolKeySha'])
            sessions.add(owner['ConnectionId']);held[lane]={'physical':physical,'pool_key':record['PoolKeySha']}
    return data
def credential_safe(data,secrets):
    forms=[]
    for value in secrets:
        forms.extend((value,value.encode().hex(),value.encode().hex().upper(),value.encode('utf-16-le').hex(),value.encode('utf-16-le').hex().upper()))
    def walk(value):
        if type(value) is str:return any(form in value for form in forms)
        if type(value) is dict:return any(walk(k) or walk(v) for k,v in value.items())
        if type(value) is list:return any(walk(v) for v in value)
        return False
    if walk(data):raise ValueError('FAIL_CREDENTIAL_OUTPUT')


def public_sql_forms():
    raw=(HERE/'pool_profile.ps1').read_bytes().decode('utf-8')
    result={}
    for name in ('Read','OwnGuard','OwnerRead'):
        pattern=r'(?m)^\$'+name+r"=@'\r?\n(.*?)\r?\n'@"
        found=re.findall(pattern,raw,re.S)
        if len(found)!=1:raise ValueError('Feste öffentliche SQLtextpopulation fehlt')
        result[name]=found[0]
    return result

def validate_operations(records):
    # Tatsächlich erwartete APIfolge; jeder Returned-Wert ist ein eigener Endrecord.
    forms=public_sql_forms();own=hashlib.sha256((forms['OwnGuard']+'SELECT 1;').encode()).hexdigest();read=hashlib.sha256(forms['Read'].encode()).hexdigest();owner=hashlib.sha256((forms['OwnGuard']+forms['OwnerRead']).encode()).hexdigest();spoof=hashlib.sha256("EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=@Tenant;SELECT 1;".encode()).hexdigest()
    expected=[('OPEN','OWNER',0,None)]
    for checkout,lane in enumerate(ORDER,1):
        expected.extend((kind,who,checkout,digest) for kind,who,digest in (('SCALAR','OWNER',own),('OPEN',lane,None),('SCALAR',lane,read),('SCALAR','OWNER',own),('SCALAR',lane,spoof),('SCALAR',lane,read),('SCALAR','OWNER',owner),('CLOSE',lane,None)))
    expected.extend(('CLOSE',lane,0,None) for lane in ORDER)
    absent="DECLARE @J nvarchar(max)=(SELECT LOWER(CONVERT(varchar(36),connection_id)) ConnectionId FROM sys.dm_exec_connections WHERE connection_id IN(CONVERT(uniqueidentifier,@Id1),CONVERT(uniqueidentifier,@Id2),CONVERT(uniqueidentifier,@Id3)) ORDER BY connection_id FOR JSON PATH);SELECT COALESCE(@J,N'[]');"
    expected.extend((('SCALAR','OWNER',0,hashlib.sha256((forms['OwnGuard']+absent).encode()).hexdigest()),('CLOSE','OWNER',0,None)))
    if type(records) is not list or len(records)!=len(expected):raise ValueError('Vollständige einzelne APIpopulation fehlt')
    for ordinal,(record,ref) in enumerate(zip(records,expected)):
        fields={'Ordinal','Operation','Lane','Checkout','Returned','RequestEnd','ConfiguredTextSha256','TextScope'}
        if type(record) is not dict or set(record)!=fields:raise ValueError('Vollständiger APIrecord fehlt')
        integer(record['Ordinal'],ordinal);integer(record['Checkout'],ref[2])
        if any(type(record[k]) is not str for k in ('Operation','Lane','RequestEnd','TextScope')) or (record['Operation'],record['Lane'])!=ref[:2] or record['Returned'] is not True or record['RequestEnd']!='RETURNED_TO_CALLER':raise ValueError('APIfolge oder tatsächliches Ende fehlt')
        digest=record['ConfiguredTextSha256']
        if ref[0]=='SCALAR':
            if type(digest) is not str or digest!=ref[3] or record['TextScope']!='CLIENT_CONFIGURED_SECRET_FREE_TEXT':raise ValueError('Tatsächliche konfigurierte SQLtextbindung fehlt')
        elif digest is not None or record['TextScope']!='NOT_APPLICABLE':raise ValueError('Open/Close enthalten keinen SQLtextdigest')
    return records

def validate_child(envelope,receipt):
    fields={'Kind','Pid','ReturnCode','FinalPoll','TimedOut','DurationSeconds','InputBytes','InputSha256','StdoutBytes','StdoutSha256','StderrBytes','StderrSha256','ScriptSha256','ClientProcessEnd','ServerRequestEnd','CredentialSafety'}
    if type(envelope) is not dict or set(envelope)!=fields or envelope['Kind']!='POWERSHELL_POOL_CHILD':raise ValueError('Eigener vollständiger Childenvelope fehlt')
    for k in ('Pid','InputBytes','StdoutBytes','StderrBytes'):
        if type(envelope[k]) is not int or envelope[k]<0:raise ValueError('Tatsächliche Childzahlen fehlen')
    if envelope['Pid']<1 or not 1<=envelope['InputBytes']<=160000 or envelope['StdoutBytes']+envelope['StderrBytes']>1000000:raise ValueError('Childcapturegrenze')
    integer(envelope['ReturnCode'],0);integer(envelope['FinalPoll'],0)
    if envelope['TimedOut'] is not False or envelope['ClientProcessEnd']!='KNOWN' or envelope['ServerRequestEnd']!='API_RETURN_RECORDS_ONLY' or envelope['CredentialSafety']!='CHECKED_AGAINST_PRIVATE_CALLER_LIST':raise ValueError('Bekannte Child-/Requestgrenze fehlt')
    if type(envelope['DurationSeconds']) not in (int,float) or not math.isfinite(envelope['DurationSeconds']) or not 0<=envelope['DurationSeconds']<=40:raise ValueError('Childdauer fehlt')
    for key in ('InputSha256','StdoutSha256','StderrSha256','ScriptSha256'):
        if type(envelope[key]) is not str or not re.fullmatch('[a-f0-9]{64}',envelope[key]):raise ValueError('Vollständige Childbytes fehlen')
    validate_operations(receipt['Operations'])
    return envelope

def validate_call(call):
    import sys
    sys.path.insert(0,str(ROOT/'Tests/Static'))
    import con010_pool_capture as captured
    fields={'Ordinal','Phase','InputText','Stdout','Stderr','Capture','ExpectedError'}
    if type(call) is not dict or set(call)!=fields or type(call['InputText']) is not str or type(call['Stdout']) is not str or type(call['Stderr']) is not str:raise ValueError('Vollständige unveränderte Clientbytes fehlen')
    captured.validate_capture(call['Capture']);integer(call['Ordinal'],call['Capture']['Ordinal'])
    for raw,bytekey,shakey in ((call['InputText'].encode('utf-8'),'InputFileBytes','InputFileSha256'),(call['Stdout'].encode('utf-8'),'StdoutTextBytes','StdoutTextSha256'),(call['Stderr'].encode('utf-8'),'StderrTextBytes','StderrTextSha256')):
        integer(call['Capture'][bytekey],len(raw))
        if call['Capture'][shakey]!=hashlib.sha256(raw).hexdigest():raise ValueError('ActualCapture-/Originalbytebindung verloren')
    if call['ExpectedError'] is not None:
        code=call['ExpectedError']
        if type(code) is not int or code not in (51003,51004) or call['Capture']['ReturnCode']==0 or not native_error(call['Stdout']+'\n'+call['Stderr'],code,'FAIL_STATE' if code==51004 else 'FAIL_RESULT_CONTRACT'):raise ValueError('Tatsächlicher Nativefehler fehlt')
    return call

PROFILE_SOURCE_KEYS=('Tests/Static/con010_pool_capture.py','Tests/Static/test_con010_pool_capture.py','Tests/Static/Fixtures/con010/pool-capture-contract-v2.json','Documentation/HowTo/SQL_SERVER_2025_AI_POOL_CAPTURE_V2.md','Demos/00_Framework/Tools/sqlcmd_process.py','Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_client.py','Tests/Static/test_con010_pool_client.py','Documentation/HowTo/SQL_SERVER_2025_AI_POOL_CLIENT.md',*('Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/'+n for n in ('run_pool_profile.py','pool_profile_inputs.py','pool_profile_evidence.py','pool_profile.ps1','Expected/pool-profile-contract.json')),'Tests/Static/test_con010_pool_profile.py','Documentation/HowTo/SQL_SERVER_2025_AI_POOL_PUBLIC.md')

def profile_sources(values):
    if type(values) is not dict or set(values)!=set(PROFILE_SOURCE_KEYS) or any(type(v) is not str or not re.fullmatch('[a-f0-9]{64}',v) for v in values.values()):raise ValueError('Vollständige feste öffentliche Sourcepopulation fehlt')
    actual={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in PROFILE_SOURCE_KEYS}
    if values!=actual:raise ValueError('Tatsächliche öffentliche Sourcebytes abweichend')
    return actual

def namespace_binding(data,token,cid,port):
    fields={'Id','Name','Image','Owner','Memory','NanoCpus','Mounts','Binds','VolumesFrom','Ports'}
    if type(token) is not str or not re.fullmatch('[A-F0-9]{16}',token) or type(cid) is not str or not re.fullmatch('[a-f0-9]{64}',cid) or type(port) is not str or not re.fullmatch('[1-9][0-9]{0,4}',port) or int(port)>65535:raise ValueError('Gehaltene vollständige Namespaceidentität fehlt')
    if type(data) is not dict or set(data)!=fields or any(type(data[k]) is not str for k in ('Id','Name','Image','Owner')) or data['Id']!=cid or data['Name']!='sqlperf-pool-public-'+token.lower() or data['Image']!='78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726' or data['Owner']!='CON010-Pool-Public' or type(data['Memory']) is not int or data['Memory']!=6*1024**3 or type(data['NanoCpus']) is not int or data['NanoCpus']!=4*10**9 or type(data['Mounts']) is not list or data['Mounts']!=[] or data['Binds'] not in (None,[]) or data['VolumesFrom'] not in (None,[]):raise ValueError('Vollständige eigene Namespacebindung fehlt')
    ports=data['Ports']
    if type(ports) is not dict or set(ports)!={'1433/tcp'} or type(ports['1433/tcp']) is not list or len(ports['1433/tcp'])!=1 or type(ports['1433/tcp'][0]) is not dict or ports['1433/tcp'][0]!={'HostIp':'127.0.0.1','HostPort':port}:raise ValueError('Eigene vollständige Loopbackbindung fehlt')
    return data

def validate_namespace(closure,token,cid,port):
    fields={'BoundAtStart','BoundBeforeRemove','CidQuery','NameQuery','InputFiles'}
    if type(closure) is not dict or set(closure)!=fields or type(closure['CidQuery']) is not str or closure['CidQuery']!='' or type(closure['NameQuery']) is not str or closure['NameQuery']!='' or type(closure['InputFiles']) is not list or closure['InputFiles']!=[]:raise ValueError('Neue vollständige Namespace-/Inputabwesenheit fehlt')
    namespace_binding(closure['BoundAtStart'],token,cid,port);namespace_binding(closure['BoundBeforeRemove'],token,cid,port)
    same(closure['BoundAtStart'],closure['BoundBeforeRemove'])
    return closure

def validate_actual(record):
    actual=record['Actual']
    fields={'SqlCalls','NegativeStates','ChildInputText','ChildStdout','ChildStderr','SourceSha256','Namespace','NamespaceCalls'}
    if type(actual) is not dict or set(actual)!=fields or type(actual['SqlCalls']) is not list or not 1<=len(actual['SqlCalls'])<=64:raise ValueError('Vollständiger Callerrecord fehlt')
    calls=actual['NamespaceCalls']
    if type(calls) is not list or not calls:raise ValueError('Tatsächliche NamespaceCLIrecords fehlen')
    validate_namespace_calls(calls,'WaveBinding'in record)
    ordinals=[]
    for call in actual['SqlCalls']:validate_call(call);ordinals.append(call['Ordinal'])
    if ordinals!=list(range(len(ordinals))):raise ValueError('Vollständige Clientcallpopulation fehlt')
    expected=[51003,51004,51004,51004,51004,51004]
    if [c['ExpectedError'] for c in actual['SqlCalls'] if c['ExpectedError'] is not None]!=expected:raise ValueError('Vollständige echte Negativcalls fehlen')
    if type(actual['NegativeStates']) is not list or len(actual['NegativeStates'])!=5:raise ValueError('Vollständige Negativstatewitnesses fehlen')
    for witness in actual['NegativeStates']:
        if type(witness) is not dict or set(witness)!={'Before','After','Restored'}:raise ValueError('Vollständiger Negativstatewitness fehlt')
        same(witness['Before'],witness['After']);same(record['Baseline'],witness['Restored'])
    profile_sources(actual['SourceSha256'])
    if actual['SourceSha256']['Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/pool_profile.ps1']!=record['Child']['ScriptSha256']:raise ValueError('Tatsächliche öffentliche Childsource fehlt')
    for field,nkey,skey in (('ChildInputText','InputBytes','InputSha256'),('ChildStdout','StdoutBytes','StdoutSha256'),('ChildStderr','StderrBytes','StderrSha256')):
        if type(actual[field]) is not str:raise ValueError('ActualChildkanal fehlt')
        raw=actual[field].encode('utf-8');integer(record['Child'][nkey],len(raw))
        if record['Child'][skey]!=hashlib.sha256(raw).hexdigest():raise ValueError('ActualChildbytebindung fehlt')
    same(json.loads(actual['ChildStdout'],object_pairs_hook=unique),record['PoolReceipt'])
    validate_namespace(actual['Namespace'],record['Token'],record['ContainerId'],record['Port'])
    # Jede tatsächliche Cleanupcallphase bleibt vollständig im Callrecord erhalten.
    if actual['SqlCalls'][-2]['Phase']!='DROP_DATABASE' or actual['SqlCalls'][-1]['Phase']!='SQL_ABSENCE' or actual['SqlCalls'][-2]['Capture']['ReturnCode']!=0 or actual['SqlCalls'][-1]['Capture']['ReturnCode']!=0 or actual['SqlCalls'][-1]['Stdout'].strip()!='POOLPUBLIC_ALL|ABSENT':raise ValueError('Neue tatsächliche SQLclosure fehlt')
    return actual
def validate_namespace_call(call):
    legacy={'Command','ReturnCode','Stdout','Stderr','ProcessEnd','DurationSeconds'}
    held=legacy|{'Pid','FinalPoll','TimedOut','CollectorFailed','ConfiguredCapSeconds','SourceBefore','SourceAfter'}
    if type(call)is not dict or set(call)not in (legacy,held) or type(call['Command'])is not list or not call['Command'] or any(type(v)is not str for v in call['Command']) or type(call['ReturnCode'])is not int or type(call['Stdout'])is not str or type(call['Stderr'])is not str or type(call['DurationSeconds'])not in (int,float) or not math.isfinite(call['DurationSeconds']) or call['DurationSeconds']<0:raise ValueError('Vollständiger NamespaceCLIreturn fehlt')
    if set(call)==legacy:
        if call['ProcessEnd']!='SUBPROCESS_RUN_RETURNED':raise ValueError('Historische Namespacegrenze abweichend')
    else:
        if type(call['Pid'])is not int or call['Pid']<1 or type(call['FinalPoll'])is not int or call['FinalPoll']!=call['ReturnCode'] or call['FinalPoll']<0 or call['TimedOut']is not False or call['CollectorFailed']is not False or call['ProcessEnd']!='HELD_PROCESS_RETURNED':raise ValueError('Gehaltenes Namespaceende fehlt')
        if type(call['ConfiguredCapSeconds'])not in (int,float) or not math.isfinite(call['ConfiguredCapSeconds']) or not 0<call['ConfiguredCapSeconds']<=20 or call['DurationSeconds']>call['ConfiguredCapSeconds']:raise ValueError('Absolutes Namespacebudget fehlt')
        profile_sources(call['SourceBefore']);same(call['SourceBefore'],call['SourceAfter'])
    return call
def validate_namespace_calls(calls,new_wave=False):
    if type(calls)is not list or not calls:raise ValueError('Tatsächliche NamespaceCLIrecords fehlen')
    for call in calls:
        validate_namespace_call(call)
        if new_wave and call['ProcessEnd']!='HELD_PROCESS_RETURNED':raise ValueError('Neue Welle verlangt individuelle Namespaceenden')
    return calls

def fixed_contract():
    path=HERE/'Expected/pool-profile-contract.json'
    if path.stat().st_size>10000:raise ValueError('Expectedgrenze')
    actual=json.loads(path.read_bytes().decode('utf-8'),object_pairs_hook=unique)
    expected={'contract':'CON010_POOLPUBLIC_V2','stage':'SOURCE_PREPARATION_ONLY','database':DATABASE,'run_token':'POOLPUBLIC','order':list(ORDER),'rows':2,'dimensions':3,'logins':3,'dotnet_records':57,'physical_connections':3,'client_guid_equality':'NOT_AN_ORACLE','tds_request_attestation':'NOT_ESTABLISHED','runtime_generalization':'NOT_ESTABLISHED','tp_con':'NOT_ESTABLISHED','input_digest_scope':'CLIENT_INPUT_FILE_UTF8_BEFORE_SQLCMD_ENV_EXPANSION','collector_configured_wait_headroom_seconds':26,'namespace_cleanup_caps_seconds':[3,3,8,3,3],'namespace_cleanup_reserve_seconds':20,'wallclock_guarantee':'NO_WALLCLOCK_GUARANTEE'}
    if type(actual) is not dict or set(actual)!=set(expected) or canonical(actual)!=canonical(expected):raise ValueError('Fester Expectedvertrag abweichend')
    return expected

def summary(record):
    fixed_contract()
    fields={'PoolReceipt','Child','Baseline','After','DatabaseId','ObjectId','Sids','Token','Controls','PhysicalAbsence','SqlAbsence','NamespaceAbsence','InputsAbsent','Actual','ContainerId','Port'}
    if type(record) is not dict or set(record)not in (fields,fields|{'WaveBinding'}):raise ValueError('Vollständiger öffentlicher Poolprofilrecord fehlt')
    if 'WaveBinding'in record:validate_wave_binding(record['WaveBinding'])
    dbid,oid=record['DatabaseId'],record['ObjectId']
    if type(dbid) is not int or dbid<5 or type(oid) is not int or oid<5 or type(record['Sids']) is not dict or set(record['Sids'])!=set(LOGINS):raise ValueError('Unabhängige vollständige Identitäten fehlen')
    for value in record['Sids'].values():sid(value)
    if len(set(record['Sids'].values()))!=3:raise ValueError('Drei verschiedene SIDs erforderlich')
    validate_pool(record['PoolReceipt'],record['Sids'],dbid,record['Token']);validate_child(record['Child'],record['PoolReceipt'])
    state(record['Baseline'],dbid,oid,record['Sids']);state(record['After'],dbid,oid,record['Sids']);same(record['Baseline'],record['After'])
    if record['Controls']!=['SOURCE_DELETE_51003','SOURCE_RESTORED','HELD_SID_51004',*[f'MARKER_{n}_51004' for n in range(4)]] or type(record['Controls']) is not list:raise ValueError('Echte fest geordnete Negativ-/Restorekontrollen fehlen')
    if record['PhysicalAbsence']!='ACTUAL_NEW_OWNER_QUERY' or record['SqlAbsence']!='ACTUAL_NEW_DB_AND_PRINCIPAL_QUERY' or record['NamespaceAbsence']!='ACTUAL_FULL_CID_AND_NAME_QUERY' or record['InputsAbsent'] is not True:raise ValueError('Tatsächliche vollständige Cleanuprecords fehlen')
    validate_actual(record)
    return {'status':'WARN','record_validation':'PASS','checkouts':6,'physical_reuses':3,'dotnet_api_records':57,'control_records':7,'runtime_generalization':'NOT_ESTABLISHED','tds_request_attestation':'NOT_ESTABLISHED','tp_con':'NOT_ESTABLISHED','password_integrity':'NOT_CAPTURED'}
def validate_wave_binding(value):
    fields={'Wave','SourceCandidate','NativeCandidate','OverallNativeCandidate','Control','InputSha256','HistorySha256','PriorNativeAttempts','PriorContainers','PriorSqlcmd','PriorPoolchildren','OldRequestEnd'}
    if type(value)is not dict or set(value)!=fields:raise ValueError('Neue Wavebindung fehlt')
    for key,ref in [('Wave','PR226_REQUALIFICATION_V1'),('Control','Runtime/AI_POOL_REQUALIFICATION'),('OldRequestEnd','UNKNOWN_STICKY')]:
        if type(value[key])is not str or value[key]!=ref:raise ValueError('Neue Wavebindung abweichend')
    for key,ref in [('PriorNativeAttempts',2),('PriorContainers',1),('PriorSqlcmd',0),('PriorPoolchildren',0)]:integer(value[key],ref)
    if type(value['SourceCandidate'])is not int or not 1<=value['SourceCandidate']<=6 or type(value['NativeCandidate'])is not int or not 1<=value['NativeCandidate']<=4:raise ValueError('Gemeinsame Wavebudgetbindung fehlt')
    integer(value['OverallNativeCandidate'],value['NativeCandidate']+2)
    for key in ['InputSha256','HistorySha256']:
        if type(value[key])is not str or not re.fullmatch('[a-f0-9]{64}',value[key]):raise ValueError('Vollständige eigene Input-/Historybytes fehlen')
    return value
