"""Reiner CON-010-Poolrecordvertrag; keine Ausführung oder Callerattestierung.

InMemory-API report(record, *, binding). Alle Rohdaten bleiben beim Caller.
Fehlende Einzelhandle-/Inputcaptures bleiben ausdrücklich NOT_ESTABLISHED.
"""
import hashlib,json,math,re,uuid
from datetime import datetime
from pathlib import Path
DATABASE='SQLPERF_LAB_CON010_TENANTPOOL'
LOGINS={'A':('CON010_LoginA','CON010_TenantA'),'B':('CON010_LoginB','CON010_TenantB'),'U':('CON010_LoginUnmapped','CON010_Unmapped')}
ORDER=('A','B','U','A','B','U')
CONTRACT_PATH=Path(__file__).resolve().parent/'Fixtures/con010/pool-record-contract.json'
def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Ungültige vollständige Recordbindung: unique')
        result[key]=value
    return result

def decode(output):
    lines=[s.strip() for s in output.splitlines() if s.strip()]
    if not lines or lines[-1]!='SQLPERF_SUMMARY|PASS|OK':raise ValueError('Ungültige vollständige Recordbindung: decode')
    frames=[s.split('|',4) for s in lines[:-1]]
    if not frames or any(len(f)!=5 or f[0]!='TENANTPOOL_PART' for f in frames):raise ValueError('Ungültige vollständige Recordbindung: decode')
    count,chars=int(frames[0][2]),int(frames[0][3])
    if not 1<=chars<=200000 or count!=(chars+199)//200 or len(frames)!=count:raise ValueError('Ungültige vollständige Recordbindung: decode')
    for n,frame in enumerate(frames,1):
        if frame[1:4]!=[str(n),str(count),str(chars)] or len(frame[4])!=min(200,chars-(n-1)*200)*4 or not re.fullmatch('[A-F0-9]+',frame[4]):raise ValueError('Ungültige vollständige Recordbindung: decode')
    return json.loads(bytes.fromhex(''.join(f[4] for f in frames)).decode('utf-16-le'),object_pairs_hook=unique)

def integer(value,expected):
    if type(value) is not int or value!=expected:raise ValueError('Ungültige vollständige Recordbindung: integer')

def sid(value):
    if type(value) is not str or not re.fullmatch('[A-F0-9]{32}',value):raise ValueError('Ungültige vollständige Recordbindung: sid')
    return value

def identity(data,lane,sids,dbid):
    fields={'DatabaseId','DatabaseName','SuserName','OriginalLogin','UserName','ServerSid','OriginalSid','UserSid','SessionId'}
    if type(data) is not dict or set(data)!=fields or lane not in LOGINS:raise ValueError('Ungültige vollständige Recordbindung: identity')
    integer(data['DatabaseId'],dbid)
    login,user=LOGINS[lane]
    for field,expected in (('DatabaseName',DATABASE),('SuserName',login),('OriginalLogin',login),('UserName',user)):
        if type(data[field]) is not str or data[field]!=expected:raise ValueError('Ungültige vollständige Recordbindung: identity')
    for key in ('ServerSid','OriginalSid','UserSid'):
        if sid(data[key])!=sids[lane]:raise ValueError('Ungültige vollständige Recordbindung: identity')
    if type(data['SessionId']) is not int or data['SessionId']<1:raise ValueError('Ungültige vollständige Recordbindung: identity')

def rowset(data,lane,sids,dbid,spoof=False):
    if type(data) is not dict or set(data)!={'Identity','Rows','SessionTenantBefore','SessionTenantAfter'}:raise ValueError('Ungültige vollständige Recordbindung: rowset')
    identity(data['Identity'],lane,sids,dbid)
    if data['SessionTenantAfter'] is not None:raise ValueError('Ungültige vollständige Recordbindung: rowset')
    if spoof:
        integer(data['SessionTenantBefore'],2)
    elif data['SessionTenantBefore'] is not None:raise ValueError('Ungültige vollständige Recordbindung: rowset')
    rows=data['Rows'];expected_id={'A':1,'B':2,'U':None}[lane]
    if type(rows) is not list or len(rows)!=(0 if expected_id is None else 1):raise ValueError('Ungültige vollständige Recordbindung: rowset')
    if expected_id is not None:
        row=rows[0]
        if type(row) is not dict or set(row)!={'Id','TenantId','Content','ContentBytes','ContentHex','VectorJson','Dimensions','BaseType','Distance'}:raise ValueError('Ungültige vollständige Recordbindung: rowset')
        integer(row['Id'],expected_id);integer(row['TenantId'],expected_id);integer(row['Dimensions'],3)
        text='Synthetische Quelle '+lane;raw=text.encode('utf-16-le')
        if row['Content']!=text or type(row['Content']) is not str or row['ContentHex']!=raw.hex().upper():raise ValueError('Ungültige vollständige Recordbindung: rowset')
        integer(row['ContentBytes'],len(raw))
        if row['BaseType']!='float32' or type(row['VectorJson']) is not str:raise ValueError('Ungültige vollständige Recordbindung: rowset')
        vector=json.loads(row['VectorJson'])
        if type(vector) is not list or len(vector)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v!=ref for v,ref in zip(vector,(1,0,0))):raise ValueError('Ungültige vollständige Recordbindung: rowset')
        if type(row['Distance']) not in (int,float) or not math.isfinite(row['Distance']) or row['Distance']!=0:raise ValueError('Ungültige vollständige Recordbindung: rowset')
    return data

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)

def same(a,b):
    if canonical(a)!=canonical(b):raise ValueError('Ungültige vollständige Recordbindung: same')

def full_name(row,key,bytekey,hexkey):
    if type(row[key]) is not str:raise ValueError('Ungültige vollständige Recordbindung: full_name')
    raw=row[key].encode('utf-16-le');integer(row[bytekey],len(raw))
    if type(row[hexkey]) is not str or row[hexkey]!=raw.hex().upper():raise ValueError('Ungültige vollständige Recordbindung: full_name')

def principals(data,sids,object_id):
    if type(object_id) is not int or object_id<5:raise ValueError('Ungültige vollständige Recordbindung: principals')
    if type(data) is not dict or set(data)!={'Logins','ServerPermissions','ServerRoles','Users','DatabasePermissions','DatabaseRoles'}:raise ValueError('Ungültige vollständige Recordbindung: principals')
    if any(type(v) is not list for v in data.values()) or len(data['Logins'])!=3 or len(data['Users'])!=3 or len(data['ServerPermissions'])!=3 or len(data['DatabasePermissions'])!=6 or data['ServerRoles']!=[] or data['DatabaseRoles']!=[]:raise ValueError('Ungültige vollständige Recordbindung: principals')
    login_fields={'principal_id','name','name_bytes','name_hex','sid','type','type_desc','is_disabled','create_date','modify_date','default_database_name','default_language_name','credential_id','is_fixed_role','is_policy_checked','is_expiration_checked'}
    user_fields={'principal_id','name','name_bytes','name_hex','sid','type','authentication_type','default_schema_name','is_fixed_role','create_date','modify_date'}
    for rows,fields in ((data['Logins'],login_fields),(data['Users'],user_fields)):
        for row in rows:
            if type(row) is not dict or set(row)!=fields:raise ValueError('Ungültige vollständige Recordbindung: principals')
            full_name(row,'name','name_bytes','name_hex');sid(row['sid'])
            for field in ('type','create_date','modify_date'):
                if type(row[field]) is not str:raise ValueError('Ungültige vollständige Recordbindung: principals')
    perm_fields={'class','major_id','grantee_principal_id','grantor_principal_id','type','permission_name','permission_bytes','permission_hex','state'}
    for key in ('ServerPermissions','DatabasePermissions'):
        for p in data[key]:
            if type(p) is not dict or set(p)!=(perm_fields|({'minor_id'} if key=='DatabasePermissions' else set())):raise ValueError('Ungültige vollständige Recordbindung: principals')
            full_name(p,'permission_name','permission_bytes','permission_hex')
            for field in ('class','major_id','grantee_principal_id','grantor_principal_id',*(['minor_id'] if key=='DatabasePermissions' else [])):
                if type(p[field]) is not int or p[field]<0:raise ValueError('Ungültige vollständige Recordbindung: principals')
            if type(p['type']) is not str or type(p['state']) is not str:raise ValueError('Ungültige vollständige Recordbindung: principals')
    for lane in LOGINS:
        login,user=LOGINS[lane];rows=[r for r in data['Logins'] if r['name']==login];users=[r for r in data['Users'] if r['name']==user]
        if len(rows)!=1 or len(users)!=1:raise ValueError('Ungültige vollständige Recordbindung: principals')
        r=rows[0];u=users[0]
        if r['sid']!=sids[lane] or u['sid']!=sids[lane] or r['type']!='S' or r['type_desc']!='SQL_LOGIN' or u['type']!='S' or r['is_disabled'] is not False or r['is_fixed_role'] is not False or r['credential_id'] is not None or r['default_database_name']!=DATABASE or r['default_language_name']!='us_english' or r['is_policy_checked'] is not False or r['is_expiration_checked'] is not False or u['authentication_type']!=1 or type(u['authentication_type']) is not int or u['default_schema_name']!='dbo' or u['is_fixed_role'] is not False:raise ValueError('Ungültige vollständige Recordbindung: principals')
        for obj in (r,u):
            if type(obj['principal_id']) is not int or obj['principal_id']<1 or type(obj['create_date']) is not str or type(obj['modify_date']) is not str:raise ValueError('Ungültige vollständige Recordbindung: principals')
        permissions=[p for p in data['ServerPermissions'] if p['grantee_principal_id']==r['principal_id']]
        expected_server={(100,0,'COSQ','CONNECT SQL','G',1)}
        actual_server={(p['class'],p['major_id'],p['type'],p['permission_name'],p['state'],p['grantor_principal_id']) for p in permissions}
        if actual_server!=expected_server or len(permissions)!=1:raise ValueError('Ungültige vollständige Recordbindung: principals')
        permissions=[p for p in data['DatabasePermissions'] if p['grantee_principal_id']==u['principal_id']]
        if len(permissions)!=2 or {(p['class'],p['major_id'],p['minor_id'],p['type'],p['permission_name'],p['state'],p['grantor_principal_id']) for p in permissions}!={(0,0,0,'CO  ','CONNECT','G',1),(1,object_id,0,'SL  ','SELECT','G',1)}:raise ValueError('Ungültige vollständige Recordbindung: principals')
    return data

def state(data,dbid,object_id,sids):
    fields={'Principals','PrincipalBytes','PrincipalHex','db','config','files','schemas','objects','indexes','index_columns','columns','policies','predicates','modules','rows','properties'}
    if type(data) is not dict or set(data)!=fields:raise ValueError('Ungültige vollständige Recordbindung: state')
    raw=bytes.fromhex(data['PrincipalHex'])
    integer(data['PrincipalBytes'],len(raw));same(json.loads(raw.decode('utf-16-le'),object_pairs_hook=unique),data['Principals'])
    principals(data['Principals'],sids,object_id)
    for key,n in (('db',1),('config',41),('files',2),('schemas',2),('objects',4),('indexes',1),('index_columns',1),('columns',4),('policies',1),('predicates',1),('modules',1),('rows',2),('properties',4)):
        if type(data[key]) is not list or len(data[key])!=n:raise ValueError('Vollständige Statepopulation fehlt: '+key)
    integer(data['db'][0]['database_id'],dbid)
    if data['db'][0]['name']!=DATABASE or data['db'][0]['compatibility_level']!=170 or data['db'][0]['recovery_model_desc']!='SIMPLE':raise ValueError('Ungültige vollständige Recordbindung: state')
    for row,lane,id in zip(data['rows'],('A','B'),(1,2)):
        if set(row)!={'Id','TenantId','ContentBytes','ContentHex','VectorJson'}:raise ValueError('Ungültige vollständige Recordbindung: state')
        integer(row['Id'],id);integer(row['TenantId'],id)
        raw=('Synthetische Quelle '+lane).encode('utf-16-le');integer(row['ContentBytes'],len(raw))
        if row['ContentHex']!=raw.hex().upper() or type(row['VectorJson']) is not str:raise ValueError('Ungültige vollständige Recordbindung: state')
        vector=json.loads(row['VectorJson'])
        if type(vector) is not list or len(vector)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v!=e for v,e in zip(vector,(1,0,0))):raise ValueError('Ungültige vollständige Recordbindung: state')
    v=data['columns'][3]
    integer(v['object_id'],object_id);integer(v['vector_dimensions'],3);integer(v['vector_base_type'],0)
    if v['name']!='V' or v['is_nullable'] is not False:raise ValueError('Ungültige vollständige Recordbindung: state')
    for column,name in zip(data['columns'],('Id','TenantId','Content','V')):
        integer(column['object_id'],object_id)
        if column['name']!=name or column['is_nullable'] is not False:raise ValueError('Ungültige vollständige Recordbindung: state')
    if data['policies'][0]['is_enabled'] is not True or data['policies'][0]['is_schema_bound'] is not True or data['modules'][0]['is_schema_bound'] is not True:raise ValueError('Ungültige vollständige Recordbindung: state')
    integer(data['predicates'][0]['target_object_id'],object_id)
    schemas={}
    for schema in data['schemas']:
        if set(schema)!={'schema_id','name','principal_id'} or type(schema['schema_id']) is not int or schema['schema_id']<1 or schema['name'] not in ('lab','sec') or schema['name'] in schemas:raise ValueError('Ungültige vollständige Recordbindung: state')
        integer(schema['principal_id'],1);schemas[schema['name']]=schema['schema_id']
    if len(set(schemas.values()))!=2:raise ValueError('Ungültige vollständige Recordbindung: state')
    objects={};ids=set()
    for obj in data['objects']:
        if type(obj) is not dict or set(obj)!={'object_id','schema_id','parent_object_id','name','type','create_date','modify_date'}:raise ValueError('Ungültige vollständige Recordbindung: state')
        for field in ('object_id','schema_id','parent_object_id'):
            if type(obj[field]) is not int or obj[field]<0:raise ValueError('Ungültige vollständige Recordbindung: state')
        if obj['object_id']<1 or obj['object_id'] in ids or type(obj['name']) is not str or not obj['name'] or type(obj['type']) is not str or any(type(obj[f]) is not str or not obj[f] for f in ('create_date','modify_date')):raise ValueError('Ungültige vollständige Recordbindung: state')
        ids.add(obj['object_id'])
        # sys.objects.type ist char(2); vollständige Darstellung erhalten.
        kind={'U ':'U','PK':'PK','IF':'IF','SP':'SP'}.get(obj['type'])
        if kind is None or kind in objects:raise ValueError('Ungültige vollständige Recordbindung: state')
        objects[kind]=obj
    for kind,name,schema in (('U','Documents','lab'),('IF','TenantPredicate','sec'),('SP','TenantPolicy','sec')):
        obj=objects[kind]
        if obj['name']!=name:raise ValueError('Ungültige vollständige Recordbindung: state')
        integer(obj['schema_id'],schemas[schema]);integer(obj['parent_object_id'],0)
    integer(objects['U']['object_id'],object_id);integer(objects['PK']['schema_id'],schemas['lab']);integer(objects['PK']['parent_object_id'],object_id)
    index=data['indexes'][0];integer(index['object_id'],object_id);integer(index['index_id'],1);integer(index['type'],1)
    if index['name']!=objects['PK']['name'] or index['is_unique'] is not True or index['is_primary_key'] is not True or index['is_disabled'] is not False:raise ValueError('Ungültige vollständige Recordbindung: state')
    for field,value in (('object_id',object_id),('index_id',1),('column_id',1),('key_ordinal',1)):integer(data['index_columns'][0][field],value)
    integer(data['modules'][0]['object_id'],objects['IF']['object_id']);integer(data['policies'][0]['object_id'],objects['SP']['object_id']);integer(data['predicates'][0]['object_id'],objects['SP']['object_id'])
    return data

def guid(value):
    if type(value) is not str or not re.fullmatch('[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}',value) or uuid.UUID(value).int==0:raise ValueError('Ungültige vollständige Poolbindung: guid')
    return value

def rows(value,lane,sids,dbid):
    if type(value) is not dict or set(value)!={'Identity','Rows','Context'}:raise ValueError('Ungültige vollständige Poolbindung: rows')
    identity(value['Identity'],lane,sids,dbid)
    # Vollständige Quellenprüfung; tatsächlicher Kontext ist separat gebunden.
    rowset({'Identity':value['Identity'],'Rows':value['Rows'],'SessionTenantBefore':None,'SessionTenantAfter':None},lane,sids,dbid)
    return value

def pool_record(data,sids,dbid,token):
    if type(token) is not str or not re.fullmatch('[A-F0-9]{16}',token):raise ValueError('Ungültige vollständige Poolbindung: validate')
    if type(data) is not dict or set(data)!={'Status','RequestEnd','PoolCleanup','Records','RemainingConnections','Token','Fault'} or data['Status']!='PASS' or data['RequestEnd']!='RESPONSE_RECEIVED' or data['PoolCleanup']!='ACTUAL_CLEAR_CLOSE_AND_NEW_ABSENCE' or data['Token']!=token:raise ValueError('Ungültige vollständige Poolbindung: validate')
    if data['Fault'] is not None:raise ValueError('Ungültige vollständige Poolbindung: validate')
    if type(data['Records']) is not list or len(data['Records'])!=6 or data['RemainingConnections']!=[] or type(data['RemainingConnections']) is not list:raise ValueError('Ungültige vollständige Poolbindung: validate')
    held={};sessions=set();poolkeys=set()
    for ordinal,(record,lane) in enumerate(zip(data['Records'],ORDER),1):
        fields={'Ordinal','Lane','ClientConnectionId','ConnectionState','PoolKeySha','CredentialOrdinal','Before','After','Owner'}
        if type(record) is not dict or set(record)!=fields or record['Lane']!=lane or record['ConnectionState']!='Open':raise ValueError('Ungültige vollständige Poolbindung: validate')
        integer(record['Ordinal'],ordinal);integer(record['CredentialOrdinal'],{'A':1,'B':2,'U':3}[lane]);guid(record['ClientConnectionId'])
        if type(record['PoolKeySha']) is not str or not re.fullmatch('[A-F0-9]{64}',record['PoolKeySha']):raise ValueError('Ungültige vollständige Poolbindung: validate')
        before=rows(record['Before'],lane,sids,dbid);after=rows(record['After'],lane,sids,dbid)
        if before['Context'] is not None:raise ValueError('Ungültige vollständige Poolbindung: validate')
        integer(after['Context'],2 if lane=='A' else 1);same(before['Identity'],after['Identity']);same(before['Rows'],after['Rows'])
        owner=record['Owner']
        expected={'SessionId','ConnectionId','ConnectTime','LoginTime','LoginName','OriginalLoginName','Sid','DatabaseId','ProgramName','NetTransport','AuthScheme'}
        if type(owner) is not dict or set(owner)!=expected:raise ValueError('Ungültige vollständige Poolbindung: validate')
        integer(owner['SessionId'],before['Identity']['SessionId']);integer(owner['DatabaseId'],dbid);guid(owner['ConnectionId'])
        if owner['LoginName']!=LOGINS[lane][0] or owner['OriginalLoginName']!=LOGINS[lane][0] or owner['Sid']!=sids[lane] or owner['ProgramName']!='SQLPERF_TENANTPOOL_'+token+'_'+lane or owner['NetTransport']!='TCP' or owner['AuthScheme']!='SQL':raise ValueError('Ungültige vollständige Poolbindung: validate')
        for key in ('ConnectTime','LoginTime'):
            if type(owner[key]) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?',owner[key]):raise ValueError('Ungültige vollständige Poolbindung: validate')
            datetime.fromisoformat(owner[key])
        physical=(owner['ConnectionId'],owner['ConnectTime'])
        if lane in held:
            previous=held[lane]
            if physical!=previous['physical'] or record['PoolKeySha']!=previous['pool_key']:raise ValueError('Ungültige vollständige Poolbindung: validate')
        else:
            if owner['ConnectionId'] in sessions:raise ValueError('Ungültige vollständige Poolbindung: validate')
            if record['PoolKeySha'] in poolkeys:raise ValueError('Ungültige vollständige Poolbindung: validate')
            poolkeys.add(record['PoolKeySha'])
            sessions.add(owner['ConnectionId']);held[lane]={'physical':physical,'pool_key':record['PoolKeySha']}
    return data


BUILTIN_TYPES={'str':str,'int':int,'bool':bool,'dict':dict,'list':list,'float':float,'NoneType':type(None)}

def schema(value,fields):
    if type(value) is not dict or set(value)!=set(fields):raise ValueError('Vollständiges festes Feldschema fehlt')
    for key,typename in fields.items():
        if typename not in BUILTIN_TYPES or type(value[key]) is not BUILTIN_TYPES[typename]:raise ValueError('Falscher Feldtyp: '+key)

def bounded_int(value,minimum=0,maximum=2147483647):
    if type(value) is not int or not minimum<=value<=maximum:raise ValueError('Gebundener Integer ohne Boolalias erforderlich')
    return value

def sha(value):
    if type(value) is not str or not re.fullmatch('[a-f0-9]{64}',value):raise ValueError('Vollständiger kanonischer SHA256 erforderlich')
    return value

def source_map(value):
    if type(value) is not dict or not 1<=len(value)<=64:raise ValueError('Vollständige begrenzte Quellenkarte erforderlich')
    for key,digest in value.items():
        if type(key) is not str or not 1<=len(key)<=256:raise ValueError('Begrenzte Quellenkennung erforderlich')
        sha(digest)
    return value

def profile_state(value,binding,contract):
    state(value,binding['database_id'],binding['object_id'],binding['sids'])
    for group,fields in contract['state_types'].items():
        for row in value[group]:
            if type(row) is not dict or set(row)!=set(fields):raise ValueError('Vollständiges Katalogschema fehlt: '+group)
            for key,item in row.items():
                typename=fields[key]
                if typename=='NoneType':
                    permitted=contract['nullable_types'].get(group,{}).get(key)
                    if item is not None and type(item) is not BUILTIN_TYPES.get(permitted):raise ValueError('Falscher nullable Katalogtyp')
                elif type(item) is not BUILTIN_TYPES.get(typename):raise ValueError('Falscher Katalogtyp: '+key)
                if type(item) is str and len(item)>10000:raise ValueError('Katalogscalar überschreitet feste Grenze')
                if key.endswith('_hex') and item is not None and not re.fullmatch('(?:[A-F0-9]{2})*',item):raise ValueError('Vollständige Katalogbytes fehlen')
    if len({r['configuration_id'] for r in value['config']})!=41 or len({r['name'] for r in value['config']})!=41:raise ValueError('Eindeutige vollständige Konfigurationen fehlen')
    if {r['file_id'] for r in value['files']}!={1,2} or len({r['guid'] for r in value['files']})!=2:raise ValueError('Beide eigenen Katalogdateien fehlen')
    for row in value['files']:
        guid(row['guid'].lower())
        for key in ('size','growth'):bounded_int(row[key])
        if type(row['max_size']) is not int or row['max_size']<-1:raise ValueError('Dateigrenze fehlt')
    markers={}
    for row in value['properties']:
        if (row['class'],row['major_id'],row['minor_id'],row['base_type'])!=(0,0,0,'nvarchar'):raise ValueError('Markertyp/-scope abweichend')
        name=bytes.fromhex(row['name_hex']);val=bytes.fromhex(row['value_hex'])
        integer(row['name_bytes'],len(name));integer(row['value_bytes'],len(val))
        text=name.decode('utf-16-le')
        if text in markers:raise ValueError('Doppelter Eigentumsmarker')
        markers[text]=val.decode('utf-16-le')
    if markers!={'SQLPERF.Project':'SQL_PerformanceSchulung','SQLPERF.ContractVersion':'1.0','SQLPERF.DemoId':'CON-010','SQLPERF.RunToken':'TENANTPOOL'}:raise ValueError('Vollständige bytegenaue Eigentumsbindung fehlt')
    return value

ARTIFACTS=('build','pool_receipt','parent_result','state_before','state_after','physical_absence','sql_absence_probe','sql_absence_parent')
PARENT_TYPES={'candidate':'int','slot':'str','token':'str','name':'str','image':'str','source':'dict','closed':'bool','version':'str','phase':'str','measurement_path':'str','cid':'str','db_absent':'bool','cid_absent':'bool','client_end_unknown':'bool','principal_absent':'bool','inputs_absent':'bool','name_absent':'bool','no_mounts':'bool','namespace_destroyed':'bool','sql_absence_evidence':'str','native_count':'int','native_count_semantics':'str','cleanup_seconds':'float','failure':'NoneType'}
IMAGE='78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726'

def artifact(value,expected):
    schema(value,{'RawText':'str','Sha256':'str'})
    raw=value['RawText'].encode('utf-8')
    if len(raw)>1000000 or sha(value['Sha256'])!=sha(expected) or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Vollständige Rawbytes-/Callerbindung abweichend')
    return value['RawText']

def captures(record,native,receipt,binding):
    missing=[];total=len(native)+1
    ends=record['capture_ends']
    if ends is None:missing.append('INDIVIDUAL_END_CAPTURE')
    else:
        if type(ends) is not list or len(ends)!=total:raise ValueError('Vollständige Einzelhandlepopulation fehlt')
        for n,end in enumerate(ends):
            schema(end,{'Ordinal':'int','Kind':'str','ReturnCode':'int','ProcessEnd':'str','RequestEnd':'str','RawSha256':'str'})
            integer(end['Ordinal'],n);bounded_int(end['ReturnCode'],0,255)
            expected=receipt if n==len(native) else native[n]['Sha256']
            if end['Kind']!=('POOL_CHILD' if n==len(native) else 'SQLCMD') or end['ProcessEnd']!='KNOWN' or end['RequestEnd']!='RESPONSE_RECEIVED' or sha(end['RawSha256'])!=expected:raise ValueError('Vollständige deklarierte End-/Rawbindung fehlt')
            if n==len(native) and end['ReturnCode']!=0:raise ValueError('Positiver Childstatus inkohärent')
    inputs=record['input_sha256']
    if inputs is None:missing.append('EXECUTED_INPUT_CAPTURE')
    else:
        if type(inputs) is not list or len(inputs)!=total or binding['input_sha256'] is None or inputs!=binding['input_sha256']:raise ValueError('Vollständige ausgeführte Input-/Callerbindung fehlt')
        for n,item in enumerate(inputs):
            schema(item,{'Ordinal':'int','Kind':'str','InputSha256':'str'})
            integer(item['Ordinal'],n);sha(item['InputSha256'])
            if item['Kind']!=('POOL_CHILD' if n==len(native) else 'SQLCMD'):raise ValueError('Feste Inputreihenfolge abweichend')
    return missing

EXPECTED_COUNTS={'checkouts': 6, 'lanes': 3, 'physical_reuse': 3, 'second_checkout_resets': 3, 'identity_result_records': 12, 'query_source_rows': 8, 'full_states': 2, 'state_source_rows': 4, 'parent_physical_absence_texts': 1, 'fresh_sql_absence_texts': 2}
EXPECTED_CLAIMS={'caller_provenance': 'NOT_INDEPENDENTLY_ATTESTED', 'runtime_qualification': 'NOT_ESTABLISHED', 'public_con010_qualification': 'NOT_ESTABLISHED', 'tp_con': 'NOT_ESTABLISHED', 'portable_provider_support': 'NOT_ESTABLISHED'}
CONTRACT_KEYS={'artifact_bound_utf8', 'profile_build', 'database', 'state_types', 'contract', 'record_bound_utf8', 'nullable_types', 'expected_counts', 'claims', 'purpose', 'source_keys', 'marker_run', 'scope'}
CONTRACT_SHAPE_SHA256='0dbd74f23df26cfd65367b4d5e690a0f6eb8b91c8bf7c4343dfdd6ad20ea3c56'

def validate_contract(contract):
    if type(contract) is not dict or set(contract)!=CONTRACT_KEYS:raise ValueError('Vollständiges festes Expectedschema fehlt')
    if contract['expected_counts']!=EXPECTED_COUNTS or type(contract['expected_counts']) is not dict or any(type(contract['expected_counts'].get(k)) is not int for k in EXPECTED_COUNTS):raise ValueError('Feste numerische Sollpopulation abweichend')
    if contract['claims']!=EXPECTED_CLAIMS or type(contract['claims']) is not dict or any(type(contract['claims'].get(k)) is not str for k in EXPECTED_CLAIMS):raise ValueError('Ungeprüfte oder erweiterte Expectedclaims unzulässig')
    fixed={'contract':'CON010_POOL_RECORD_V1','profile_build':'17.0.5005.3','database':DATABASE,'marker_run':'TENANTPOOL','scope':'PRIVATE_THREE_POOLS_SIX_CHECKOUTS_ONLY','record_bound_utf8':3000000,'artifact_bound_utf8':1000000}
    if any(type(contract[k]) is not type(v) or contract[k]!=v for k,v in fixed.items()) or type(contract['purpose']) is not str or not 1<=len(contract['purpose'])<=256:raise ValueError('Fester Expectedprofilrahmen abweichend')
    shape={k:contract[k] for k in ('state_types','nullable_types','source_keys')}
    if hashlib.sha256(canonical(shape).encode()).hexdigest()!=CONTRACT_SHAPE_SHA256:raise ValueError('Vollständiges eingefrorenes Expectedtypen-/Quellenschema abweichend')
    return contract

def report(record,*,binding):
    """Prüft deklarierte Records; bestätigt keine unabhängige Caller-/Runtimewahrheit."""
    if type(record) is not dict or type(binding) is not dict:raise ValueError('Plain-dict-Record und Callerbindung erforderlich')
    raw_contract=CONTRACT_PATH.read_bytes()
    if len(raw_contract)>50000:raise ValueError('Fester Expectedvertrag überschreitet Grenze')
    contract=validate_contract(json.loads(raw_contract,object_pairs_hook=unique))
    schema(binding,{'database_id':'int','object_id':'int','token':'str','sids':'dict','source_sha256':'dict','raw_sha256':'dict','native_sha256':'list','input_sha256':type(binding.get('input_sha256')).__name__,'expected_contract_sha256':'str'})
    bounded_int(binding['database_id'],5);bounded_int(binding['object_id'],5)
    if not re.fullmatch('[A-F0-9]{16}',binding['token']) or set(binding['sids'])!=set(LOGINS):raise ValueError('Feste typisierte Calleridentität fehlt')
    for value in binding['sids'].values():sid(value)
    if len(set(binding['sids'].values()))!=3:raise ValueError('Drei getrennte aufgezeichnete SIDs erforderlich')
    source_map(binding['source_sha256'])
    if set(binding['source_sha256'])!=set(contract['source_keys']):raise ValueError('Vollständige feste Sourcepopulation fehlt')
    if sha(binding['expected_contract_sha256'])!=hashlib.sha256(raw_contract).hexdigest():raise ValueError('Kanonischer Expectedvertrag nicht gebunden')
    if set(binding['raw_sha256'])!=set(ARTIFACTS):raise ValueError('Vollständige tatsächliche Rawartefaktbindung fehlt')
    schema(record,{'scope':'str','source_sha256':'dict','artifacts':'dict','native_raw':'list','capture_ends':type(record.get('capture_ends')).__name__,'input_sha256':type(record.get('input_sha256')).__name__})
    if record['capture_ends'] is not None and type(record['capture_ends']) is not list:raise ValueError('Fehlende Captures müssen explizit NULL sein')
    if record['input_sha256'] is not None and type(record['input_sha256']) is not list:raise ValueError('Fehlende Inputs müssen explizit NULL sein')
    if binding['input_sha256'] is not None and type(binding['input_sha256']) is not list:raise ValueError('Callerinputbindung falsch typisiert')
    if len(canonical(record).encode('utf-8'))>3000000:raise ValueError('Vollrecord überschreitet Grenze')
    if record['scope']!='PRIVATE_THREE_POOLS_SIX_CHECKOUTS_ONLY' or source_map(record['source_sha256'])!=binding['source_sha256']:raise ValueError('Fester Scope-/Quellenvertrag abweichend')
    if set(record['artifacts'])!=set(ARTIFACTS):raise ValueError('Vollständige Captureartefakte fehlen')
    raw={key:artifact(record['artifacts'][key],binding['raw_sha256'][key]) for key in ARTIFACTS}
    if raw['build'].strip()!='17.0.5005.3':raise ValueError('Fester beobachteter Build abweichend')
    receipt=json.loads(raw['pool_receipt'],object_pairs_hook=unique)
    pool_record(receipt,binding['sids'],binding['database_id'],binding['token'])
    before=profile_state(decode(raw['state_before']),binding,contract);after=profile_state(decode(raw['state_after']),binding,contract);same(before,after)
    for r in receipt['Records']:
        for name in ('Before','After'):
            if r[name]['Rows']:
                a=r[name]['Rows'][0];b=before['rows'][a['Id']-1]
                if any(type(a[k]) is not type(b[k]) or a[k]!=b[k] for k in b):raise ValueError('Poolrow passt nicht zur vollständigen Quelle')
    if raw['physical_absence'].strip()!='TENANTPOOL_PHYSICAL|ABSENT' or any(raw[key].strip()!='TENANTPOOL_ALL|ABSENT' for key in ('sql_absence_probe','sql_absence_parent')):raise ValueError('Vollständige frische Abwesenheitstexte fehlen')
    parent=json.loads(raw['parent_result'],object_pairs_hook=unique);schema(parent,PARENT_TYPES)
    if parent['source']!=binding['source_sha256'] or parent['token']!=binding['token'] or parent['version']!='17.0.5005.3' or parent['phase']!='PRIVATE_THREE_POOLS_SIX_CHECKOUTS_ONLY' or parent['slot']!='2025-tenant-pool-1' or parent['image']!=IMAGE:raise ValueError('Vollständige deklarierte Parent-/Quellenbindung abweichend')
    bounded_int(parent['candidate'],1,6);sha(parent['cid'])
    if not re.fullmatch('sqlperf-tenant-pool-[a-f0-9]{32}',parent['name']) or not parent['measurement_path'] or not 0<=parent['cleanup_seconds']<=60 or not math.isfinite(parent['cleanup_seconds']):raise ValueError('Fester deklarierter Parentrahmen abweichend')
    if parent['failure'] is not None or parent['client_end_unknown'] is not False or any(parent[k] is not True for k in ('closed','db_absent','cid_absent','principal_absent','inputs_absent','name_absent','no_mounts','namespace_destroyed')) or parent['sql_absence_evidence']!='ACTUAL_NEW_SQL_ABSENCE' or parent['native_count_semantics']!='CLIENT_HANDLE_STARTS':raise ValueError('Fehlende deklarierte Closure wird nicht zu PASS ergänzt')
    bounded_int(parent['native_count'],1,64)
    if type(binding['native_sha256']) is not list or len(record['native_raw'])!=parent['native_count'] or len(binding['native_sha256'])!=parent['native_count']:raise ValueError('Vollständige Native-Rawpopulation fehlt')
    for item,expected in zip(record['native_raw'],binding['native_sha256']):artifact(item,expected)
    missing=captures(record,record['native_raw'],record['artifacts']['pool_receipt']['Sha256'],binding)
    # Selbst vollständige synthetische Captures attestieren keine Ausführung.
    return {'status':'WARN','record_validation':'PASS',**EXPECTED_COUNTS,'declared_sqlcmd_handles':parent['native_count'],'pool_child_receipts':1,'missing_capture_gates':len(missing),'capture_gates':missing,'individual_request_end':'NOT_ESTABLISHED' if 'INDIVIDUAL_END_CAPTURE' in missing else 'DECLARED_NOT_INDEPENDENTLY_ATTESTED','executed_input_binding':'NOT_ESTABLISHED' if 'EXECUTED_INPUT_CAPTURE' in missing else 'DECLARED_NOT_INDEPENDENTLY_ATTESTED','complete_public_closure':'NOT_ESTABLISHED',**EXPECTED_CLAIMS}
