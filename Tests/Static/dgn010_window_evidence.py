"""Reine begrenzte native Transport-/Identitäts-/Counter-/Rowdigestprüfung."""
import datetime,hashlib,json,re,uuid
IDENTITY=('SessionId','RequestId','RequestStartTime','ConnectionId','DatabaseId')
COUNTERS=('CpuMs','Reads','LogicalReads','Writes')
KEYS=set(IDENTITY)|set(COUNTERS)|{'Path','Label','Statements','ElapsedUs','StartedUtc','EndedUtc','CountersBefore','CountersAfter','Queries'}
DIGEST=hashlib.sha256(';'.join(f'{i}|{i*3}|'+('46'*100) for i in range(101,111)).encode('utf-16le')).hexdigest().upper()
PREFIXES={'SELECT':'DGN010_SELECTPART|','DML':'DGN010_DMLPART|'}

def query_digest(scope,ordinal):
    offset=ordinal if scope=='DML' else 0
    return hashlib.sha256(';'.join(f'{i}|{i*3+offset}|'+('46'*100) for i in range(101,111)).encode('utf-16le')).hexdigest().upper()

def scope_prefix(scope):
    if type(scope) is not str or scope not in PREFIXES:raise ValueError('Fixed SELECT/DML scope required')
    return PREFIXES[scope]
def integer(value,minimum=0):
    if type(value) is not int or not minimum<=value<=9223372036854775807:raise ValueError('Bounded actual integer required')
    return value
def stamp(value):
    if not isinstance(value,str):raise ValueError('Actual SQL UTC stamp required')
    result=datetime.datetime.fromisoformat(value)
    if result.tzinfo is not None:raise ValueError('Fixed SQL UTC stamp required')
    return result
def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Duplicate native JSON field')
        result[key]=value
    return result
def decode(output,scope):
    prefix=scope_prefix(scope)
    if type(output) is not str:raise ValueError('Native text required')
    if len(output.encode('utf-8'))>1000000:raise ValueError('Bounded native output required')
    lines=output.splitlines();parts=[];summary=0
    for line in lines:
        if not line.strip():continue
        if line=='SQLPERF_SUMMARY|PASS|OK':summary+=1;continue
        if not line.startswith(prefix):raise ValueError('Unknown native window line')
        parts.append(line)
    if summary!=1 or not 1<=len(parts)<=250:raise ValueError('Complete bounded native parts/summary required')
    pieces=[];total=None
    for ordinal,line in enumerate(parts,1):
        f=line.split('|',4)
        if len(f)!=5 or any(not re.fullmatch('[0-9]+',v) for v in f[1:4]):raise ValueError('Fixed actual part header required')
        index,count,size=map(int,f[1:4])
        if index!=ordinal or count!=len(parts) or not 0<size<=50000 or (total is not None and size!=total) or count!=(size+199)//200:raise ValueError('Complete ordered actual parts required')
        total=size
        if not f[4].isascii() or len(f[4])!=min(200,total-(ordinal-1)*200):raise ValueError('Full native part bytes required')
        pieces.append(f[4])
    raw=''.join(pieces)
    if len(raw)!=total:raise ValueError('Complete actual scalar required')
    return json.loads(raw,object_pairs_hook=unique)
def validate(record,path,label,statements,database_id,scope):
    scope_prefix(scope)
    if type(path) is not int or type(statements) is not int or type(label) is not str:raise ValueError('Fixed typed caller controls required')
    keys=KEYS|({'TransactionBefore','TransactionAfter'} if scope=='DML' else set())
    if type(record) is not dict or set(record)!=keys:raise ValueError('Complete fixed native schema required')
    if type(record['Path']) is not int or record['Path']!=path or path not in (0,1) or type(record['Statements']) is not int or record['Statements']!=statements or statements not in (1,100):raise ValueError('Fixed path/query population differs')
    if record['Label']!=label or type(record['Label']) is not str or not re.fullmatch('[A-Z0-9_]{1,32}',label):raise ValueError('Fixed native label differs')
    integer(record['SessionId'],1);integer(record['RequestId']);integer(record['DatabaseId'],5)
    if type(database_id) is not int or record['DatabaseId']!=database_id:raise ValueError('Independent DB binding differs')
    if scope=='DML' and any(type(record[k]) is not int or record[k]!=0 for k in ('TransactionBefore','TransactionAfter')):raise ValueError('Actual closed own transaction required')
    stamp(record['RequestStartTime'])
    if not isinstance(record['ConnectionId'],str) or str(uuid.UUID(record['ConnectionId'])).lower()!=record['ConnectionId'].lower():raise ValueError('Complete actual connection binding required')
    for field in ('CountersBefore','CountersAfter'):
        value=record[field]
        if not isinstance(value,dict) or set(value)!=set(IDENTITY)|set(COUNTERS) or any(type(value[k]) is not type(record[k]) or value[k]!=record[k] for k in IDENTITY):raise ValueError('Actual request counter identity differs')
        for key in COUNTERS:integer(value[key])
    for key in COUNTERS:
        integer(record[key])
        if record['CountersAfter'][key]-record['CountersBefore'][key]!=record[key]:raise ValueError('Actual monotonic counter difference missing')
    integer(record['ElapsedUs']);start,end=stamp(record['StartedUtc']),stamp(record['EndedUtc']);delta=end-start
    elapsed=(delta.days*86400+delta.seconds)*1000000+delta.microseconds
    if elapsed<0 or elapsed!=record['ElapsedUs']:raise ValueError('Actual same-clock elapsed differs')
    # DMV request_start_time is a coarse identity; no cross-clock ordering assertion.
    rows=record['Queries']
    if not isinstance(rows,list) or len(rows)!=statements:raise ValueError('Full per-query coverage required')
    for ordinal,row in enumerate(rows,1):
        if not isinstance(row,dict) or set(row)!={'Ordinal','Rows','FirstId','LastId','Digest'}:raise ValueError('Full query digest schema required')
        if any(type(row[k]) is not int or row[k]!=v for k,v in [('Ordinal',ordinal),('Rows',10),('FirstId',101),('LastId',110)]) or row['Digest']!=query_digest(scope,ordinal):raise ValueError('Actual full-row query oracle differs')
    return tuple(record[k] for k in IDENTITY)
def slots():
    for block in range(1,4):
        for order,paths in [('AB',(0,1)),('BA',(1,0)),('AA',(0,0))]:
            for slot,path in enumerate(paths,1):yield block,order,slot,path
