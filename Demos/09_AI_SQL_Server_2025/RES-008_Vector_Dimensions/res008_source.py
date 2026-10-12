"""Vollständige synthetische Quellen-/Storageoracles des begrenzten Profils."""
import math
from pathlib import Path

DIMS=(32,384,768,1536)

def evidence(output):
    groups={d:[] for d in DIMS};storage={};queries={};config={}
    for line in output.splitlines():
        if not line.startswith('RES008_'):continue
        fields=line.split('|')
        if fields[0]=='RES008_SOURCE':
            if len(fields)!=5:raise ValueError('Unvollstaendige Quellenaufnahme')
            d,row,size=map(int,fields[1:4]);digest=fields[4]
            if d not in groups or size<=0 or len(digest)!=64 or any(c not in '0123456789ABCDEF' for c in digest):raise ValueError('Ungueltige Quellenaufnahme')
            groups[d].append((row,size,digest))
        elif fields[0]=='RES008_STORAGE':
            if len(fields)!=8:raise ValueError('Unvollstaendige Storageaufnahme')
            d,rows,data,used,reserved,minimum,maximum=map(int,fields[1:])
            if d in storage or d not in DIMS or rows!=100 or not 0<data<=used<=reserved or minimum<=0 or minimum!=maximum:raise ValueError('Ungueltige Storageaufnahme')
            storage[d]=(rows,data,used,reserved,minimum,maximum)
        elif fields[0]=='RES008_QUERY':
            if len(fields)!=4:raise ValueError('Unvollstaendige Suchaufnahme')
            d,row=int(fields[1]),int(fields[2]);distance=float(fields[3])
            if d in queries or d not in DIMS or row!=1 or not math.isfinite(distance) or abs(distance)>1e-6:raise ValueError('Ungueltige positive Source-/Suchkontrolle')
            queries[d]=(row,distance)
        elif fields[0]=='RES008_DB_CONFIG':
            if len(fields)!=3 or fields[1] in config or fields[1] not in ('MAXDOP','PREVIEW_FEATURES'):raise ValueError('Ungueltige Konfigurationsaufnahme')
            config[fields[1]]=int(fields[2])
        else:raise ValueError('Unbekannte Aufnahmeklasse')
    if set(storage)!=set(DIMS) or set(queries)!=set(DIMS) or config!={'MAXDOP':0,'PREVIEW_FEATURES':0}:raise ValueError('Unvollstaendige Aufnahme oder geaenderte Optionen')
    for rows in groups.values():
        if len(rows)!=100 or [r[0] for r in rows]!=list(range(1,101)):raise ValueError('Unvollstaendige eindeutige Sourcepopulation')
    if 'SQLPERF_SUMMARY|PASS|OK' not in output:raise ValueError('Probe nicht positiv abgeschlossen')
    return groups,storage,queries,config
