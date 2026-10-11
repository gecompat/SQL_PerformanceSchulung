"""Reine Prüfung begrenzter DB-Speicherkatalogaufnahmen; keine Indexkostenzuordnung."""
import re


def integer(value,minimum=0,maximum=2**63-1):
    if type(value) is not int or not minimum<=value<=maximum:
        raise ValueError('Tatsächlicher begrenzter Kataloginteger fehlt')
    return value


def validate_storage(record,*,token,database_id,fixture_object,stage):
    if (not isinstance(token,str) or not re.fullmatch('[A-F0-9]{16}',token)
            or type(database_id) is not int or database_id<5 or type(fixture_object) is not int
            or fixture_object<1 or stage not in ('BASELINE','INDEXED','REBUILT')):
        raise ValueError('Fester eigener Speicherkontext fehlt')
    if (record.get('kind')!='STORAGE' or record.get('Stage')!=stage or record.get('RunToken')!=token
            or type(record.get('DatabaseId')) is not int or record['DatabaseId']!=database_id
            or record.get('Context')!='SQLPERF_LAB_IDX012_'+token
            or type(record.get('FixtureObject')) is not int or record['FixtureObject']!=fixture_object):
        raise ValueError('Vollständige tatsächliche Aufnahmebindung fehlt')
    for name,value in [('SourceRows',999),('VectorIndexes',0 if stage=='BASELINE' else 1),
                       ('TransactionCount',0),('TransactionState',0)]:
        if type(record.get(name)) is not int or record[name]!=value:
            raise ValueError('Tatsächlicher Speicherphasenstatus fehlt')
    files,internal,parts=record.get('files'),record.get('internal_tables'),record.get('partitions')
    if (not isinstance(files,list) or len(files)!=2 or {r.get('type') for r in files}!={0,1}
            or not isinstance(internal,list) or len(internal)>64
            or not isinstance(parts,list) or not 1<=len(parts)<=512):
        raise ValueError('Vollständiger begrenzter eigener Katalog fehlt')
    for name,rows in [('FileCount',files),('InternalCount',internal),('PartitionCount',parts)]:
        if type(record.get(name)) is not int or record[name]!=len(rows):
            raise ValueError('Tatsächliche vollständige Katalogcountbindung fehlt')
    identities=set()
    for row in files:
        identity=integer(row.get('file_id'),1)
        if identity in identities:raise ValueError('Doppelte Dateizuordnung')
        identities.add(identity)
        kind=integer(row.get('type'),0,1)
        size=integer(row.get('size'),1,32768 if kind==0 else 8192)
        if 'space_used_pages' not in row:raise ValueError('Fehlender nullable Rohwert')
        if row.get('space_used_pages') is not None:
            integer(row['space_used_pages'],0,size)
    identities=set()
    for row in internal:
        identity=integer(row.get('object_id'),1)
        if identity in identities:raise ValueError('Doppelte interne Objektzuordnung')
        identities.add(identity)
        integer(row.get('parent_id'))
        integer(row.get('parent_minor_id'))
        integer(row.get('internal_type'),0,255)
        if not isinstance(row.get('internal_type_desc'),str) or not 1<=len(row['internal_type_desc'])<=60:
            raise ValueError('Tatsächlicher interner Typ fehlt')
    identities=set()
    for row in parts:
        identity=integer(row.get('partition_id'),1)
        if identity in identities:raise ValueError('Doppelte Partitionzuordnung')
        identities.add(identity)
        if integer(row.get('object_id'),-2**31,2**31-1)==0:
            raise ValueError('Ungültige Partitionobjekt-ID')
        integer(row.get('index_id'))
        integer(row.get('partition_number'),1)
        integer(row.get('row_count'))
        used=integer(row.get('used_page_count'))
        reserved=integer(row.get('reserved_page_count'))
        components=[integer(row.get(n)) for n in ('in_row_used_page_count','lob_used_page_count','row_overflow_used_page_count')]
        if used!=sum(components) or used>reserved:
            raise ValueError('Tatsächliche dokumentierte Seitenbilanz verletzt')
    if sum(row['object_id']==fixture_object and row['index_id']==1 and row['partition_number']==1 for row in parts)!=1:
        raise ValueError('Tatsächliche eigene unpartitionierte Fixture-PK fehlt')
    return {'stage':stage,'record':record,'page_unit_bytes':8192,'partition_row_count':'APPROXIMATE',
            'index_storage_attribution':'NOT_ESTABLISHED','writes_tempdb_worker_costs':'NOT_CAPTURED'}
