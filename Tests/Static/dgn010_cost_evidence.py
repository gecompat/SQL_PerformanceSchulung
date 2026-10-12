"""Öffentliche reine DDL-/Allokationsrecords, keine Nativeausführung."""
import hashlib,json,re,uuid
from decimal import Decimal
import dgn010_benchmark_evidence as benchmark
import dgn010_window_evidence as window
CREATE='CREATE NONCLUSTERED INDEX DGN010_OwnCandidate ON lab.SourceRows(Id) INCLUDE(Value,Payload) WITH(MAXDOP=1);'
DROP='DROP INDEX DGN010_OwnCandidate ON lab.SourceRows;'
DDL={'CREATE':CREATE,'DROP':DROP}
EMPTY='{"indexes":[],"columns":[]}'
KEYS=set(window.IDENTITY)|set(window.COUNTERS)|{'Kind','Cycle','DdlSha256','StartedUtc','EndedUtc','ElapsedUs','CountersBefore','CountersAfter','LeaseBefore','LeaseAfter'}
PREFIX='DGN010_BUILDPART|'

def decode(output):
    if type(output) is not str:raise ValueError('Actual native text required')
    lines=[]
    for line in output.splitlines():
        if not line.strip() or line=='SQLPERF_SUMMARY|PASS|OK':lines.append(line)
        elif line.startswith(PREFIX):lines.append('DGN010_SELECTPART|'+line[len(PREFIX):])
        else:raise ValueError('Foreign native prefix')
    return window.decode('\n'.join(lines),'SELECT')

def lease(text,object_id,present):
    if type(text) is not str or len(text.encode('utf-16-le'))>16000:raise ValueError('Full bounded native lease required')
    data=json.loads(text,object_pairs_hook=window.unique)
    if type(data) is not dict or set(data)!={'indexes','columns'} or any(type(data[k]) is not list for k in data):raise ValueError('Full lease schema required')
    if not present:
        if text!=EMPTY:raise ValueError('Exact native absence lease required')
        return data
    if len(data['indexes'])!=1 or len(data['columns'])!=3:raise ValueError('Fixed own index population required')
    row=data['indexes'][0];index_id=row.get('index_id');window.integer(index_id,2)
    expected={'object_id':object_id,'index_id':index_id,'name':'DGN010_OwnCandidate','type':2,'is_unique':False,'is_primary_key':False,'is_disabled':False,'has_filter':False,'filter_definition':None}
    if row!=expected or any(type(row[k]) is not type(v) for k,v in expected.items()):raise ValueError('Actual complete own index definition differs')
    columns=[{'object_id':object_id,'index_id':index_id,'index_column_id':n,'column_id':n,'key_ordinal':1 if n==1 else 0,'is_descending_key':False,'is_included_column':n!=1} for n in (1,2,3)]
    if data['columns']!=columns or any(any(type(row[k]) is not type(v) for k,v in expected.items()) for row,expected in zip(data['columns'],columns)):raise ValueError('Actual complete own index columns differ')
    return data

def validate(data,kind,cycle,dbid,object_id,expected_lease):
    if type(data) is not dict or set(data)!=KEYS:raise ValueError('Full fixed native cost schema required')
    if kind not in DDL or type(cycle) is not int or cycle not in (1,2) or type(dbid) is not int or type(object_id) is not int:raise ValueError('Fixed typed caller binding required')
    if data['Kind']!=kind or type(data['Cycle']) is not int or data['Cycle']!=cycle or data['DatabaseId']!=dbid:raise ValueError('Actual DDL/cycle/DB binding differs')
    digest=hashlib.sha256(DDL[kind].encode('utf-16-le')).hexdigest().upper()
    if data['DdlSha256']!=digest or data['LeaseBefore']!=expected_lease:raise ValueError('Complete actually executed DDL/held lease differs')
    window.integer(data['SessionId'],1);window.integer(data['RequestId']);window.integer(data['DatabaseId'],5)
    window.stamp(data['RequestStartTime']);uuid.UUID(data['ConnectionId'])
    for name in ('CountersBefore','CountersAfter'):
        counter=data[name]
        if type(counter) is not dict or set(counter)!=set(window.IDENTITY)|set(window.COUNTERS):raise ValueError('Full native request counter schema required')
        if any(type(counter[k]) is not type(data[k]) or counter[k]!=data[k] for k in window.IDENTITY):raise ValueError('Counter identity differs')
        for k in window.COUNTERS:window.integer(counter[k])
    for k in window.COUNTERS:
        window.integer(data[k])
        if data['CountersAfter'][k]-data['CountersBefore'][k]!=data[k]:raise ValueError('Actual monotone counter delta differs')
    if any(type(data[k]) is not str or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{7}',data[k]) for k in ('StartedUtc','EndedUtc')):raise ValueError('Full native datetime2(7) UTC required')
    start,end=window.stamp(data['StartedUtc']),window.stamp(data['EndedUtc']);delta=end-start
    if data['EndedUtc']<data['StartedUtc']:raise ValueError('Full datetime2(7) interval reversed')
    actual=(delta.days*86400+delta.seconds)*1000000+delta.microseconds
    window.integer(data['ElapsedUs'])
    if actual!=data['ElapsedUs']:raise ValueError('Actual same-clock UTC elapsed differs')
    lease(data['LeaseBefore'],object_id,kind=='DROP');lease(data['LeaseAfter'],object_id,kind=='CREATE')
    return tuple(data[k] for k in window.IDENTITY)

def transition(before,after,kind,data):
    if set(before)!=set(after) or len(before)!=13:raise ValueError('Full thirteen-key state required')
    for key in set(before)-{'objects','indexes','index_columns'}:
        if json.dumps(before[key],sort_keys=True)!=json.dumps(after[key],sort_keys=True):raise ValueError('Foreign Source/config/file/reader/marker state change')
    if len(before['objects'])!=len(after['objects']):raise ValueError('Foreign object population change')
    for a,b in zip(before['objects'],after['objects']):
        if a['name']!='SourceRows':
            if a!=b:raise ValueError('Foreign object change')
        elif {k:v for k,v in a.items() if k!='modify_date'}!={k:v for k,v in b.items() if k!='modify_date'} or window.stamp(b['modify_date'])<window.stamp(a['modify_date']):raise ValueError('Foreign source definition change')
    for state,raw in ((before,data['LeaseBefore']),(after,data['LeaseAfter'])):
        held=json.loads(raw,object_pairs_hook=window.unique);own=held['indexes'];ids={x['index_id'] for x in own}
        if [r for r in state['indexes'] if r['name']=='DGN010_OwnCandidate']!=own or [r for r in state['index_columns'] if r['index_id'] in ids]!=held['columns']:raise ValueError('Independent native state/held catalog differs')
    a=[r for r in before['indexes'] if r['name']!='DGN010_OwnCandidate'];b=[r for r in after['indexes'] if r['name']!='DGN010_OwnCandidate']
    if a!=b:raise ValueError('Original PK changed')
    pkids={r['index_id'] for r in a}
    if [r for r in before['index_columns'] if r['index_id'] in pkids]!=[r for r in after['index_columns'] if r['index_id'] in pkids]:raise ValueError('Original PK columns changed')


KINDS=('A','B','A','B','A')
PK='DGN010_OwnPK';CANDIDATE='DGN010_OwnCandidate'
def integer(value):
    if type(value) is not int or not 0<=value<=9223372036854775807:raise ValueError('Actual bounded integer required')
    return value
def allocation(indexes,path):
    if type(path) is not int or path not in (0,1) or type(indexes) is not dict or set(indexes)!=({PK,CANDIDATE} if path else {PK}):raise ValueError('Fixed complete own index population required')
    rows={}
    for name,values in indexes.items():
        if type(values) is not list or len(values)!=3:raise ValueError('Full row/used/reserved native tuple required')
        for value in values:integer(value)
        count,used,reserved=values
        if count!=1000 or reserved<used:raise ValueError('Actual row-count/counter invariant differs')
        rows[name]={'catalog_row_count':count,'used_pages':used,'reserved_pages':reserved}
    return {'pk':rows[PK],'candidate':rows.get(CANDIDATE),'selected_used_pages':sum(v['used_pages'] for v in rows.values()),'selected_reserved_pages':sum(v['reserved_pages'] for v in rows.values())}
def profile(snapshots):
    if type(snapshots) is not list or len(snapshots)!=8:raise ValueError('Full original eight source snapshots required')
    result=[]
    for position,path in zip((3,4,5,6,7),(0,1,0,1,0)):
        item=snapshots[position]
        if type(item) is not list or len(item)!=2:raise ValueError('Full original source/index snapshot required')
        result.append({'source_snapshot':position,'state':KINDS[len(result)],**allocation(item[1],path)})
    if any(row['pk']!=result[0]['pk'] for row in result):raise ValueError('Original PK allocation changed')
    return result

RECORD_KEYS={'database_id','object_id','preflight','records','source_snapshots','full_states','negative_states','source_negative_51003','drop_absent_negative_51003','scope','full_worker_costs','index_net_benefit','runtime_qualification'}
STATE_KEYS={'db','config','files','schemas','objects','indexes','index_columns','columns','reader','permissions','roles','rows','properties'}

STATE_FIELDS={'db': ['compatibility_level', 'database_id', 'is_auto_close_on', 'is_auto_shrink_on', 'is_read_only', 'name', 'recovery_model_desc', 'state_desc'], 'config': ['configuration_id', 'is_value_default', 'name', 'secondary_bytes', 'secondary_collation', 'secondary_hex', 'secondary_max_length', 'secondary_precision', 'secondary_scale', 'secondary_type', 'value_bytes', 'value_collation', 'value_hex', 'value_max_length', 'value_precision', 'value_scale', 'value_type'], 'files': ['file_id', 'growth', 'guid', 'is_percent_growth', 'is_read_only', 'max_size', 'name', 'size', 'type'], 'schemas': ['name', 'principal_id', 'schema_id'], 'objects': ['create_date', 'modify_date', 'name', 'object_id', 'schema_id', 'type'], 'indexes': ['filter_definition', 'has_filter', 'index_id', 'is_disabled', 'is_primary_key', 'is_unique', 'name', 'object_id', 'type'], 'index_columns': ['column_id', 'index_column_id', 'index_id', 'is_descending_key', 'is_included_column', 'key_ordinal', 'object_id'], 'columns': ['collation_name', 'column_id', 'default_object_id', 'is_computed', 'is_identity', 'is_nullable', 'max_length', 'name', 'object_id', 'precision', 'scale', 'system_type_id', 'user_type_id'], 'reader': ['authentication_type', 'default_schema_name', 'is_fixed_role', 'name', 'principal_id', 'sid', 'type'], 'permissions': ['class', 'grantee_principal_id', 'grantor_principal_id', 'major_id', 'minor_id', 'state', 'type'], 'rows': ['Id', 'Payload', 'Value', 'payload_bytes'], 'properties': ['base_type', 'class', 'major_id', 'minor_id', 'name_bytes', 'name_hex', 'value_bytes', 'value_hex']}
STATE_TYPES={'db': {'database_id': 'int', 'name': 'str', 'compatibility_level': 'int', 'recovery_model_desc': 'str', 'is_auto_close_on': 'bool', 'is_auto_shrink_on': 'bool', 'is_read_only': 'bool', 'state_desc': 'str'}, 'config': {'configuration_id': 'int', 'name': 'str', 'is_value_default': 'bool', 'value_type': 'str', 'value_precision': 'int', 'value_scale': 'int', 'value_max_length': 'int', 'value_collation': 'NoneType', 'value_bytes': 'int', 'value_hex': 'str', 'secondary_type': 'NoneType', 'secondary_precision': 'NoneType', 'secondary_scale': 'NoneType', 'secondary_max_length': 'NoneType', 'secondary_collation': 'NoneType', 'secondary_bytes': 'NoneType', 'secondary_hex': 'NoneType'}, 'files': {'file_id': 'int', 'name': 'str', 'type': 'int', 'size': 'int', 'max_size': 'int', 'growth': 'int', 'is_percent_growth': 'bool', 'is_read_only': 'bool', 'guid': 'str'}, 'schemas': {'schema_id': 'int', 'name': 'str', 'principal_id': 'int'}, 'objects': {'object_id': 'int', 'schema_id': 'int', 'name': 'str', 'type': 'str', 'create_date': 'str', 'modify_date': 'str'}, 'indexes': {'object_id': 'int', 'index_id': 'int', 'name': 'str', 'type': 'int', 'is_unique': 'bool', 'is_primary_key': 'bool', 'is_disabled': 'bool', 'has_filter': 'bool', 'filter_definition': 'NoneType'}, 'index_columns': {'object_id': 'int', 'index_id': 'int', 'index_column_id': 'int', 'column_id': 'int', 'key_ordinal': 'int', 'is_descending_key': 'bool', 'is_included_column': 'bool'}, 'columns': {'object_id': 'int', 'column_id': 'int', 'name': 'str', 'system_type_id': 'int', 'user_type_id': 'int', 'max_length': 'int', 'precision': 'int', 'scale': 'int', 'collation_name': 'NoneType', 'is_nullable': 'bool', 'is_identity': 'bool', 'is_computed': 'bool', 'default_object_id': 'int'}, 'reader': {'principal_id': 'int', 'name': 'str', 'sid': 'str', 'type': 'str', 'authentication_type': 'int', 'default_schema_name': 'str', 'is_fixed_role': 'bool'}, 'permissions': {'class': 'int', 'major_id': 'int', 'minor_id': 'int', 'grantee_principal_id': 'int', 'grantor_principal_id': 'int', 'type': 'str', 'state': 'str'}, 'rows': {'Id': 'int', 'Value': 'int', 'Payload': 'str', 'payload_bytes': 'int'}, 'properties': {'class': 'int', 'major_id': 'int', 'minor_id': 'int', 'name_bytes': 'int', 'name_hex': 'str', 'value_bytes': 'int', 'value_hex': 'str', 'base_type': 'str'}}
STATE_POPULATIONS={'db': 1, 'config': 41, 'files': 2, 'schemas': 1, 'objects': 2, 'columns': 3, 'reader': 1, 'permissions': 2, 'roles': 0, 'properties': 4}
NULLABLE_TYPES={'config':{'value_collation':'str','secondary_type':'str','secondary_precision':'int','secondary_scale':'int','secondary_max_length':'int','secondary_collation':'str','secondary_bytes':'int','secondary_hex':'str'},'indexes':{'filter_definition':'str'},'columns':{'collation_name':'str'}}

def full_state(value,dbid,object_id):
    if type(value) is not dict or set(value)!=STATE_KEYS or any(type(v) is not list for v in value.values()):raise ValueError('Full typed thirteen-key native state required')
    for name,count in STATE_POPULATIONS.items():
        if len(value[name])!=count:raise ValueError('Full fixed profile state population differs')
    for name,fields in STATE_FIELDS.items():
        if any(type(row) is not dict or sorted(row)!=fields for row in value[name]):raise ValueError('Full native state field shape differs')
        for row in value[name]:
            for field,item in row.items():
                expected_type=STATE_TYPES[name][field]
                if expected_type=='NoneType' and item is not None and type(item).__name__!=NULLABLE_TYPES[name][field]:raise ValueError('Nullable native state scalar type differs')
                if expected_type!='NoneType' and type(item).__name__!=expected_type:raise ValueError('Full native state scalar type differs')
                if item is not None and type(item) not in (str,int,bool):raise ValueError('Unexpected native state scalar')
                if field.startswith(('is_','has_')) and type(item) is not bool:raise ValueError('Native state Boolean alias')
                numeric=field.endswith('_id') or field in {'class','minor_id','major_id','value_precision','value_scale','value_max_length','value_bytes','secondary_precision','secondary_scale','secondary_max_length','secondary_bytes','file_id','size','max_size','growth','index_column_id','column_id','key_ordinal','max_length','precision','scale','authentication_type','name_bytes','compatibility_level'}
                if numeric and item is not None and type(item) is not int:raise ValueError('Native state integer alias')
                if field.endswith('_hex') and item is not None and (type(item) is not str or not re.fullmatch(r'(?:[A-F0-9]{2})*',item)):raise ValueError('Full native state bytes required')
    if len(value['indexes']) not in (1,2) or len(value['index_columns'])!=(1 if len(value['indexes'])==1 else 4):raise ValueError('Full actual index/column population differs')
    rows=value['rows']
    if len(rows)!=1000:raise ValueError('Full independent actual source rows required')
    for n,row in enumerate(rows,1):
        expected={'Id':n,'Value':n*3,'Payload':'F'*100,'payload_bytes':100}
        if type(row) is not dict or row!=expected or any(type(row[k]) is not type(v) for k,v in expected.items()):raise ValueError('Full source values/bytes differ')
    db=value['db']
    if len(db)!=1 or type(db[0].get('database_id')) is not int or db[0]['database_id']!=dbid or db[0].get('name')!='SQLPERF_LAB_DGN010_LOCAL':raise ValueError('Independent state DB differs')
    expected_db={'database_id':dbid,'name':'SQLPERF_LAB_DGN010_LOCAL','compatibility_level':170,'recovery_model_desc':'SIMPLE','is_auto_close_on':False,'is_auto_shrink_on':False,'is_read_only':False,'state_desc':'ONLINE'}
    if db[0]!=expected_db:raise ValueError('Fixed original DB configuration differs')
    configurations=[r['configuration_id'] for r in value['config']]
    if any(type(n) is not int for n in configurations) or len(set(configurations))!=len(configurations):raise ValueError('Complete unique configuration population required')
    expected_pk={'object_id':object_id,'index_id':1,'name':'DGN010_OwnPK','type':1,'is_unique':True,'is_primary_key':True,'is_disabled':False,'has_filter':False,'filter_definition':None}
    if [r for r in value['indexes'] if r['index_id']==1]!=[expected_pk]:raise ValueError('Original PK definition differs')
    expected_pk_column={'object_id':object_id,'index_id':1,'index_column_id':1,'column_id':1,'key_ordinal':1,'is_descending_key':False,'is_included_column':False}
    if [r for r in value['index_columns'] if r['index_id']==1]!=[expected_pk_column]:raise ValueError('Original PK column differs')
    if value['schemas'][0]['name']!='lab' or value['reader'][0]['name']!='DGN010_reader' or value['reader'][0]['is_fixed_role'] is not False:raise ValueError('Fixed own schema/reader differs')
    expected_markers={'SQLPERF.Project':'SQL_PerformanceSchulung','SQLPERF.ContractVersion':'1.0','SQLPERF.DemoId':'DGN-010','SQLPERF.RunToken':'LOCAL'}
    actual_markers={}
    for prop in value['properties']:
        if (prop['class'],prop['major_id'],prop['minor_id'],prop['base_type'])!=(0,0,0,'nvarchar'):raise ValueError('Actual marker type/scope differs')
        raw_name=bytes.fromhex(prop['name_hex']);raw_value=bytes.fromhex(prop['value_hex'])
        if len(raw_name)!=prop['name_bytes'] or len(raw_value)!=prop['value_bytes']:raise ValueError('Full marker byte count differs')
        name=raw_name.decode('utf-16-le');value_text=raw_value.decode('utf-16-le')
        if name in actual_markers:raise ValueError('Duplicate full marker')
        actual_markers[name]=value_text
    if actual_markers!=expected_markers:raise ValueError('Complete byte-exact own markers differ')
    objects=value['objects']
    own=[r for r in objects if r.get('name')=='SourceRows']
    if len(own)!=1 or type(own[0].get('object_id')) is not int or own[0]['object_id']!=object_id:raise ValueError('Original actual source object differs')

def invariant_state(state):
    normalized={key:value for key,value in state.items() if key not in ('indexes','index_columns')}
    normalized['objects']=[{k:v for k,v in obj.items() if not (obj['name']=='SourceRows' and k=='modify_date')} for obj in state['objects']]
    return json.dumps(normalized,sort_keys=True,separators=(',',':'))

def report(record,*,expected_database_id):
    window.integer(expected_database_id,5)
    if type(record) is not dict or set(record)!=RECORD_KEYS or type(record['database_id']) is not int or record['database_id']!=expected_database_id:raise ValueError('Full fixed record/independent caller DB binding required')
    object_id=window.integer(record['object_id'],1)
    if type(record['preflight']) is not str or len(record['preflight'].encode('utf-8'))>65536 or record['preflight'].splitlines().count('SQLPERF_SUMMARY|PASS|OK')!=1:raise ValueError('Full bounded declared preflight required')
    if record['scope']!='TWO_OWN_CREATE_DROP_CYCLES_ONLY' or any(record[k] is not True for k in ('source_negative_51003','drop_absent_negative_51003')):raise ValueError('Fixed declared scope/controls differ')
    if any(record[k]!='NOT_ESTABLISHED' for k in ('full_worker_costs','index_net_benefit','runtime_qualification')):raise ValueError('Record cannot assert broader qualification')
    sources=record['source_snapshots'];states=record['full_states'];negative=record['negative_states'];records=record['records']
    if type(sources) is not list or len(sources)!=8 or type(states) is not list or len(states)!=4 or type(negative) is not list or len(negative)!=2 or type(records) is not list or len(records)!=4:raise ValueError('Full fixed native population required')
    for snapshot,path in zip(sources,(0,0,0,0,1,0,1,0)):benchmark.validate_source(snapshot,path)
    for state in negative:full_state(state,expected_database_id,object_id)
    if json.dumps(negative[0],sort_keys=True)!=json.dumps(negative[1],sort_keys=True):raise ValueError('Full rejected-DROP state differs')
    held=EMPTY;identities=set();previous=None;previous_state=negative[1]
    for ordinal,data in enumerate(records):
        kind=('CREATE','DROP')[ordinal%2];cycle=ordinal//2+1
        identity=validate(data,kind,cycle,expected_database_id,object_id,held)
        if identity in identities or (previous is not None and data['StartedUtc']<previous):raise ValueError('Unique serial native DDL windows required')
        identities.add(identity);previous=data['EndedUtc']
        pair=states[ordinal]
        if type(pair) is not list or len(pair)!=2:raise ValueError('Full independent state pair required')
        for state in pair:full_state(state,expected_database_id,object_id)
        if json.dumps(pair[0],sort_keys=True)!=json.dumps(previous_state,sort_keys=True):raise ValueError('Full state continuity between native windows differs')
        if any(invariant_state(state)!=invariant_state(negative[0]) for state in pair):raise ValueError('Original Source/config/file/reader/marker state drifts between windows')
        transition(*pair,kind,data);held=data['LeaseAfter'];previous_state=pair[1]
    if held!=EMPTY:raise ValueError('Final actual candidate absence missing')
    distributions={}
    for kind in ('CREATE','DROP'):
        selected=[r for r in records if r['Kind']==kind];distributions[kind]={}
        for metric in ('ElapsedUs',*window.COUNTERS):
            values=[r[metric] for r in selected];ordered=sorted(values)
            distributions[kind][metric]={'n':2,'samples':values,'min':ordered[0],'max':ordered[1],'median_exact':str(Decimal(sum(ordered))/Decimal(2)),'zero_count':sum(v==0 for v in values)}
    return {'record_validation':'PASS','scope':'TWO_OWN_CREATE_DROP_CYCLES_ONLY','ddl_windows':4,'source_rows':8000,'full_state_rows':10000,'operations':distributions,'index_allocations':profile(sources),
        'controller_flags':'DECLARED_NOT_INDEPENDENTLY_ATTESTED','provenance':'CALLER_ATTESTATION_REQUIRED','runtime_qualification':'NOT_ESTABLISHED','tp_perf':'NOT_ESTABLISHED','full_worker_costs':'NOT_ESTABLISHED','index_net_benefit':'NOT_ESTABLISHED','whole_database_or_file_size':'NOT_ESTABLISHED'}
