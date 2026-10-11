"""Reine Prüfung des festen IDX-012-Drop-/Änderungs-/Rebuildbefunds."""
import json
import math
import re


def validate_lifecycle(records, *, token, database_id, before_distances, after_distances, before_metadata):
    if (not isinstance(token,str) or not re.fullmatch('[A-F0-9]{16}',token)
            or type(database_id) is not int or database_id<5
            or set(before_distances)!=set(range(1,1000)) or set(after_distances)!=set(range(1,1000))
            or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=2
                   for source in (before_distances,after_distances) for v in source.values())):
        raise ValueError('Vollständiger eigener Lifecyclekontext fehlt')
    selected=[r for r in records if r.get('kind','').startswith('LIFECYCLE_')]
    if len(selected)!=8 or [r['kind'] for r in selected]!=['LIFECYCLE_DROP','LIFECYCLE_CHANGE','LIFECYCLE_REBUILD']+['LIFECYCLE_QUERY']*5 or any(r.get('RunToken')!=token or type(r.get('DatabaseId')) is not int
                              or r['DatabaseId']!=database_id for r in selected):
        raise ValueError('Vollständige eigene Lifecycleaufnahme fehlt')
    drop=selected[0]
    for key,value in [('IndexCount',0),('RowCount',999),('TransactionCount',0),('TransactionState',0)]:
        if type(drop.get(key)) is not int or drop[key]!=value:
            raise ValueError('Tatsächlicher No-Index-Pre-DML-Zustand fehlt')
    changes=[r for r in selected if r['kind']=='LIFECYCLE_CHANGE']
    rebuilds=[r for r in selected if r['kind']=='LIFECYCLE_REBUILD']
    if len(changes)!=1 or len(rebuilds)!=1:
        raise ValueError('Eindeutiger Änderungs-/Rebuildnachweis fehlt')
    change=changes[0]
    for key,value in [('AffectedRows',1),('RowCount',999),('TransactionCount',0),('TransactionState',0),('IndexCount',0)]:
        if type(change.get(key)) is not int or change[key]!=value:
            raise ValueError('Tatsächlicher Drop-/Commitzustand fehlt')
    vector=json.loads(change.get('NewVector','null'))
    if (change.get('Committed') is not True or change.get('OtherSourceUnchanged') is not True
            or not isinstance(vector,list) or len(vector)!=3
            or any(type(v) not in (int,float) for v in vector) or vector!=[1,0,0]):
        raise ValueError('Exakte feste Ein-Row-Änderung fehlt')
    if (after_distances[999]!=0 or before_distances[999]==0
            or any(before_distances[i]!=after_distances[i] for i in range(1,999))):
        raise ValueError('Unabhängiger vollständiger Distanzvergleich fehlt')
    rebuild=rebuilds[0]
    metadata=rebuild.get('AfterMetadata')
    if (type(rebuild.get('BuildElapsedUs')) is not int or rebuild['BuildElapsedUs']<0
            or rebuild.get('BeforeMetadata')!=before_metadata
            or not isinstance(metadata,list) or len(metadata)!=1 or len(before_metadata)!=1):
        raise ValueError('Vollständige eigene Rebuildaufnahme fehlt')
    own=metadata[0]
    if (type(own.get('object_id')) is not int or own['object_id']!=before_metadata[0]['object_id']
            or type(own.get('index_id')) is not int or own['index_id']<1
            or own.get('name')!='IDX012_OwnVector' or type(own.get('type')) is not int or own['type']!=8
            or own.get('type_desc')!='VECTOR' or own.get('is_disabled') is not False
            or own.get('is_hypothetical') is not False or own.get('vector_index_type')!='DiskANN'
            or own.get('distance_metric')!='COSINE'):
        raise ValueError('Tatsächlicher eigener aktiver Rebuildindex fehlt')
    queries=[r for r in selected if r['kind']=='LIFECYCLE_QUERY']
    phases=[('BASELINE','EXACT'),('BASELINE','ANN'),('AFTER_CHANGE','EXACT'),('REBUILT','EXACT'),('REBUILT','ANN')]
    if len(queries)!=5:
        raise ValueError('Fünf vollständige Suchkontrollen fehlen')
    observed=[]
    for ordinal,(record,(stage,path)) in enumerate(zip(queries,phases),1):
        source=before_distances if stage=='BASELINE' else after_distances
        expected=sorted(source,key=lambda identity:(source[identity],identity))[:5]
        rows=record.get('rows')
        if (type(record.get('Ordinal')) is not int or record['Ordinal']!=ordinal
                or (record.get('Stage'),record.get('Path'))!=(stage,path)
                or not isinstance(rows,list) or len(rows)!=5):
            raise ValueError('Feste tatsächliche Suchphase verletzt')
        identities=[]
        for row in rows:
            identity,distance=row.get('Id'),row.get('DistanceValue')
            if (type(identity) is not int or identity not in source or identity in identities
                    or type(distance) not in (int,float) or not math.isfinite(distance)
                    or abs(distance-source[identity])>0.000001):
                raise ValueError('Tatsächliche eindeutige distanzgeprüfte Suchrow fehlt')
            identities.append(identity)
        if set(identities)!=set(expected) or (path=='EXACT' and identities!=expected):
            raise ValueError('Feste Exact-/Recall@5-Kontrolle verletzt')
        if stage=='BASELINE' and 999 in identities:
            raise ValueError('Geänderter Zielvektor war bereits im Baseline-Top-k')
        if stage!='BASELINE' and (identities[0]!=999 or rows[0]['DistanceValue']!=0):
            raise ValueError('Tatsächlicher geänderter Top-1-Treffer fehlt')
        observed.append({'stage':stage,'path':path,'ids':identities,'recall_at_5':1.0 if path=='ANN' else None})
    return {'kind':'LIFECYCLE_SUMMARY','changed_id':999,'queries':observed,
            'build_elapsed_us':rebuild['BuildElapsedUs'],'metadata':metadata,
            'freshness':'OBSERVED_AFTER_REBUILD_ONLY','generation':'UNKNOWN',
            'runtime_qualification':'NOT_ESTABLISHED'}
