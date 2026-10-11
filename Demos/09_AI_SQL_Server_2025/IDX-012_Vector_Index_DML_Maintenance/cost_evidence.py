"""Reine Prüfung zweier vollständiger Punktaufnahmen einer eigenen Phasenverbindung.

Kein isolierter Build-, vollständiger Worker- oder IO-Nachweis aus Session-writes.
"""
import re

MAX=2**63-1
SESSION=('cpu_time','reads','writes','logical_reads')
TEMPDB=('user_objects_alloc_page_count','user_objects_dealloc_page_count',
        'internal_objects_alloc_page_count','internal_objects_dealloc_page_count')
FILE=('sample_ms','num_of_writes','num_of_bytes_written','io_stall_write_ms')


def integer(value,minimum=0,maximum=MAX):
    if type(value) is not int or not minimum<=value<=maximum:
        raise ValueError('Tatsächlicher begrenzter Kosteninteger fehlt')
    return value


def validate_costs(rows,*,token,database_id,stage,file_ids):
    if (not isinstance(token,str) or not re.fullmatch('[A-F0-9]{16}',token)
            or type(database_id) is not int or database_id<5
            or stage not in ('DML_BOUNDARY','REBUILD') or not isinstance(file_ids,set)
            or len(file_ids)!=2 or any(type(i) is not int or i<1 for i in file_ids)
            or not isinstance(rows,list) or len(rows)!=2):
        raise ValueError('Fester vollständiger eigener Kostenkontext fehlt')
    sid=None
    frames=[]
    for ordinal,row in enumerate(rows):
        if (row.get('kind')!='PHASE_COST' or row.get('Stage')!=stage
                or row.get('Frame')!=('BEFORE','AFTER')[ordinal] or row.get('RunToken')!=token
                or type(row.get('DatabaseId')) is not int or row['DatabaseId']!=database_id
                or row.get('Context')!='SQLPERF_LAB_IDX012_'+token):
            raise ValueError('Vollständige tatsächliche Kostenaufnahmebindung fehlt')
        actual_sid=integer(row.get('SessionId'),1,32767)
        sid=actual_sid if sid is None else sid
        if actual_sid!=sid:raise ValueError('Eigene Phasenverbindung wechselte')
        for name,expected in [('SourceRows',999),('VectorIndexes',0 if stage=='DML_BOUNDARY' and ordinal==0 else 1),
                              ('TransactionCount',0),('TransactionState',0)]:
            if type(row.get(name)) is not int or row[name]!=expected:
                raise ValueError('Tatsächlicher fester Phasenzustand fehlt')
        arrays=[]
        for key,count_key,count in [('session','SessionCount',1),('tempdb','TempdbCount',1),('files','FileCount',2)]:
            values=row.get(key)
            if not isinstance(values,list) or len(values)!=count or type(row.get(count_key)) is not int or row[count_key]!=count:
                raise ValueError('Tatsächliche vollständige Kostenkatalogabdeckung fehlt')
            arrays.append(values)
        session,tempdb,files=arrays
        for actual in (session[0],tempdb[0]):
            if type(actual.get('session_id')) is not int or actual['session_id']!=sid:
                raise ValueError('Fremde Sessiondaten abgewiesen')
        if type(tempdb[0].get('database_id')) is not int or tempdb[0]['database_id']!=2:
            raise ValueError('Tatsächlicher TempDB-Kontext fehlt')
        for name in SESSION:integer(session[0].get(name),maximum=2**31-1 if name=='cpu_time' else MAX)
        for name in TEMPDB:integer(tempdb[0].get(name))
        identities=set()
        for file in files:
            identity=integer(file.get('file_id'),1)
            if identity in identities or identity not in file_ids or type(file.get('database_id')) is not int or file['database_id']!=database_id:
                raise ValueError('Vollständige eigene Dateistatistikbindung fehlt')
            identities.add(identity)
            for name in FILE:integer(file.get(name))
        frames.append({'session':session[0],'tempdb':tempdb[0],'files':{f['file_id']:f for f in files}})

    def delta(before,after,names):
        if any(after[n]<before[n] for n in names):
            raise ValueError('Counterreset oder nicht monotone Punktaufnahme')
        return {n:after[n]-before[n] for n in names}
    first,last=frames
    return {'stage':stage,'frames':rows,
            'session_delta':delta(first['session'],last['session'],SESSION),
            'tempdb_delta':delta(first['tempdb'],last['tempdb'],TEMPDB),
            'file_delta':{i:delta(first['files'][i],last['files'][i],FILE) for i in sorted(file_ids)},
            'session_writes_meaning':'DIRTY_PAGE_MARKINGS_NOT_ACTUAL_FILE_WRITES',
            'tempdb_scope':'COMPLETED_SESSION_TASKS_EXCLUDES_IAM_AND_IN_FLIGHT',
            'file_scope':'OWN_DATABASE_ALL_WRITERS_POINT_SNAPSHOTS',
            'phase_scope':'WHOLE_PHASE_INCLUDING_CONTROLS_AND_OBSERVATION',
            'isolated_build_costs':'NOT_ESTABLISHED','full_worker_costs':'NOT_ESTABLISHED'}
