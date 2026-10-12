"""Reine Transport-/Identitäts-/Counter-/Oracleprüfung; keine SQL-Ausführung."""
import datetime,json,math,uuid
from pathlib import Path
from res008_source import DIMS
HERE=Path(__file__).resolve().parent
IDENTITY=('SessionId','RequestId','RequestStartTime','ConnectionId','DatabaseId')
COUNTERS=('CpuMs','Reads','LogicalReads','Writes')
KEYS=set(IDENTITY)|set(COUNTERS)|{'Dimension','Statements','ElapsedUs','StartedUtc','EndedUtc','CountersBefore','CountersAfter','Queries'}
LAST_EVIDENCE=None

def decode(output):
    lines=[s for s in output.splitlines() if s.startswith('RES008_WINDOWPART|')]
    if not lines or len(lines)>250:raise ValueError('Bounded complete native parts missing')
    pieces=[];total=None
    for ordinal,line in enumerate(lines,1):
        fields=line.split('|',4)
        if len(fields)!=5 or int(fields[1])!=ordinal or int(fields[2])!=len(lines):raise ValueError('Complete ordered native parts missing')
        size=int(fields[3])
        if not 0<size<=50000 or (total is not None and size!=total):raise ValueError('Actual total native scalar length differs')
        total=size;piece=fields[4]
        if not piece.isascii() or len(piece)!=(min(200,total-(ordinal-1)*200)):raise ValueError('Actual part bytes incomplete')
        pieces.append(piece)
    value=''.join(pieces)
    if len(value)!=total:raise ValueError('Actual scalar incomplete')
    return json.loads(value)

def slots():
    for pair in DIMS[1:]:
        for block in range(1,4):
            for order,dims in (('AB',(32,pair)),('BA',(pair,32)),('AA',(32,32))):
                for slot,d in enumerate(dims,1):yield pair,block,order,slot,d

def integer(value,minimum=0):
    if type(value) is not int or value<minimum:raise ValueError('Actual nonnegative integer required')
    return value

def stamp(value):
    if not isinstance(value,str):raise ValueError('Actual timestamp required')
    result=datetime.datetime.fromisoformat(value)
    if result.tzinfo is not None:raise ValueError('Fixed SQL UTC representation required')
    return result

def validate(record,dimension,statements,database_id):
    if not isinstance(record,dict) or set(record)!=KEYS:raise ValueError('Complete fixed evidence schema required')
    if record['Dimension']!=dimension or record['Statements']!=statements or type(record['Dimension']) is not int or type(record['Statements']) is not int:raise ValueError('Actual dimension/query count differs')
    integer(record['SessionId'],1);integer(record['RequestId']);integer(record['DatabaseId'],5)
    if record['DatabaseId']!=database_id:raise ValueError('Independent database binding differs')
    stamp(record['RequestStartTime'])
    if not isinstance(record['ConnectionId'],str) or str(uuid.UUID(record['ConnectionId'])).lower()!=record['ConnectionId'].lower():raise ValueError('Actual full connection binding required')
    for key in ('CountersBefore','CountersAfter'):
        counter=record[key]
        if not isinstance(counter,dict) or set(counter)!=set(IDENTITY)|set(COUNTERS) or any(counter[k]!=record[k] or type(counter[k]) is not type(record[k]) for k in IDENTITY):raise ValueError('Actual request snapshot identity differs')
        for field in COUNTERS:integer(counter[field])
    for field in COUNTERS:
        integer(record[field])
        if record['CountersAfter'][field]-record['CountersBefore'][field]!=record[field]:raise ValueError('Actual monotonic counter delta differs')
    integer(record['ElapsedUs'])
    start,end=stamp(record['StartedUtc']),stamp(record['EndedUtc'])
    delta=end-start;actual=(delta.days*86400+delta.seconds)*1000000+delta.microseconds
    # DMV start_time is a coarse datetime identity, not the datetime2(7)
    # measurement clock. Keep its exact before/after binding; compare only
    # the actual same-type window clocks for chronology and elapsed.
    if actual<0 or actual!=record['ElapsedUs']:raise ValueError('Actual chronologic elapsed delta differs')
    rows=record['Queries']
    if not isinstance(rows,list) or len(rows)!=statements:raise ValueError('Complete per-query coverage required')
    for ordinal,row in enumerate(rows,1):
        if not isinstance(row,dict) or set(row)!={'Ordinal','Id','DistanceValue'} or type(row['Ordinal']) is not int or row['Ordinal']!=ordinal or type(row['Id']) is not int or row['Id']!=1:raise ValueError('Full actual query oracle differs')
        value=row['DistanceValue']
        if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>1e-6:raise ValueError('Actual finite query distance differs')
    return tuple(record[k] for k in IDENTITY)
