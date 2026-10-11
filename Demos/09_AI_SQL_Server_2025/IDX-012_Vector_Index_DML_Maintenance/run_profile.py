#!/usr/bin/env python3
"""Begrenzter IDX-012-Controller; Import führt weder SQL noch Provisionierung aus.

Der Aufrufer stellt ein eigenes isoliertes Lab und SQLCMDPASSWORD bereit. Der
Controller schreibt keinen Rohoutput auf Datenträger und meldet keine vollständige
TP-PERF-Qualifikation. Alle Clients verwenden die öffentlichen Framework-APIs.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'Demos/00_Framework/Tools'))
from sqlcmd_process import build_sqlcmd_command, collect_process, extract_summary, resolve_sqlcmd, start_sqlcmd
sys.path.insert(0, str(FOLDER))
from dml_boundary_evidence import validate_dml_boundary
from lifecycle_evidence import validate_lifecycle
from storage_evidence import validate_storage
from cost_evidence import validate_costs


@dataclass(frozen=True)
class Result:
    outcome: str
    code: str
    phases: tuple
    original_preview: int | None
    cleanup_ok: bool
    evidence: dict


class Deadline:
    def __init__(self, seconds, clock):
        self.clock, self.end = clock, clock()+seconds

    def remaining(self, cap):
        remaining = min(cap, self.end-self.clock())
        if remaining <= 0:
            raise TimeoutError('Gemeinsames tatsächliches Zeitbudget verbraucht')
        return remaining


def execute_client(command, *, timeout_seconds):
    with execution_input(command) as lease:
        process = lease.start(environment=client_environment(command))
        return collect_process(process, lease.command, timeout_seconds=timeout_seconds)


def cost_context(script):
    script=Path(script).resolve()
    phases={'30_CostBoundary.sql':('DML_BOUNDARY','30_DmlBoundary.sql'),
            '50_CostRebuild.sql':('REBUILD','50_DropRebuild.sql')}
    if script.name not in phases:
        return None,{}
    if script.parent!=FOLDER.resolve():
        raise ValueError('Kostenquelle außerhalb des festen öffentlichen Demoordners')
    stage,filename=phases[script.name]
    work=(script.parent/filename).resolve()
    frame=(script.parent/'23_CostFrame.sql').resolve()
    if work.parent!=script.parent or frame.parent!=script.parent or not work.is_file() or not frame.is_file():
        raise ValueError('Fester eigener SQLCMD-Includepfad fehlt')
    if any(char in str(path) for path in (work,frame) for char in ('"','\r','\n','\0','$(')):
        raise ValueError('SQLCMD-Includepfad enthält freie Syntax')
    return stage,{'PhaseWorkFile':str(work),'CostFrameFile':str(frame)}


def client_environment(command,environment=None):
    # Feste Pfadwerte bleiben für Executoradapter eindeutig gebunden; die
    # tatsächliche Kostenquelle verwendet keine nativen :r-Includes mehr.
    # Geerbte Startupskripte dürfen die gebundene SQL-Quelle nicht ergänzen.
    result=dict(os.environ if environment is None else environment)
    _,paths=cost_context(Path(command[command.index('-i')+1]))
    reserved={name.casefold() for name in paths}|{'sqlcmdini'}
    result={name:value for name,value in result.items() if name.casefold() not in reserved}
    result.update(paths)
    return result


def cost_source(script):
    stage,paths=cost_context(script)
    if stage is None:
        raise ValueError('Feste eigene Kostenphase erforderlich')
    files=[Path(script).resolve(),Path(paths['CostFrameFile']),Path(paths['PhaseWorkFile'])]
    if sum(p.stat().st_size*(2 if i==1 else 1) for i,p in enumerate(files))+512>160000:
        raise ValueError('Temporäre eigene SQL-Quelle außerhalb Grenze')
    wrapper,frame,work=(p.read_text(encoding='utf-8') for p in files)
    if any(re.search(r'(?im)^\s*(?::|!!|GO(?:\s|$))',text) for text in (wrapper,frame,work)):
        raise ValueError('Freier SQLCMD-Aufruf in eigener Kostenquelle abgewiesen')
    text=(wrapper+'\nGO\n:setvar CostFrame BEFORE\n'+frame+'\nGO\n'+work
          +'\nGO\n:setvar CostFrame AFTER\n'+frame+'\nGO\n')
    if len(text.encode('utf-8'))>160000:
        raise ValueError('Temporäre eigene SQL-Quelle außerhalb Grenze')
    return text


@dataclass
class ExecutionInput:
    command: list
    process: object | None = None

    def start(self, *, environment):
        if self.process is not None:
            raise ValueError('Eigene Eingabe bereits an einen Client gebunden')
        self.process=start_sqlcmd(self.command,environment=environment)
        return self.process


class ClientEndUnknown(RuntimeError):
    pass


@contextmanager
def execution_input(command):
    script=Path(command[command.index('-i')+1])
    stage,_=cost_context(script)
    if stage is None:
        yield ExecutionInput(command)
        return
    source=cost_source(script)
    runtime=(ROOT/'Runtime').resolve()
    if runtime.parent!=ROOT.resolve() or runtime.name!='Runtime':
        raise ValueError('Temporäre SQL-Datei verlässt das eigene Repository')
    runtime.mkdir(exist_ok=True)
    own_file=None
    lease=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',newline='\n',
                                         prefix='idx012-cost-',suffix='.sql',dir=runtime,delete=False) as stream:
            own_file=Path(stream.name).resolve()
            if own_file.parent!=runtime or not own_file.name.startswith('idx012-cost-'):
                raise ValueError('Temporäre eigene SQL-Dateibindung fehlt')
            stream.write(source)
        actual=list(command)
        actual[actual.index('-i')+1]=str(own_file)
        lease=ExecutionInput(actual)
        yield lease
    finally:
        if own_file is not None:
            if own_file.parent!=runtime or not own_file.name.startswith('idx012-cost-'):
                raise ValueError('Temporäre eigene Cleanupbindung fehlt')
            if lease is not None and lease.process is not None:
                try:
                    status=lease.process.poll()
                except BaseException as error:
                    raise ClientEndUnknown('FAIL_CLEANUP: Clientstatus nicht prüfbar; eigene SQL-Datei erhalten') from error
                if type(status) is not int:
                    raise ClientEndUnknown('FAIL_CLEANUP: Native Clientende ungeklärt; eigene SQL-Datei erhalten')
            own_file.unlink(missing_ok=True)


def phase_command(executable, server, auth, username, script, token, original, variables=None):
    if not isinstance(token,str) or not re.fullmatch('[A-F0-9]{16}',token):
        raise ValueError('Vollständige Tokenbindung fehlt')
    if original is not None and (type(original) is not int or original not in (0,1)):
        raise ValueError('Tatsächlich erfasste Previewbaseline fehlt')
    permitted={'FaultAfterIndexBuild':{'0','1'},'WarmupOrdinal':{str(i) for i in range(6)},
               'Block':{str(i) for i in range(4)},'Slot':{'0','1','2'},
               'Order':{'WARMUP','AB','BA','AA'},'Path':{'EXACT','VECTOR_SEARCH'},
               'StorageStage':{'BASELINE','INDEXED','REBUILT'}}
    if any(k not in permitted or v not in permitted[k] for k,v in (variables or {}).items()):
        raise ValueError('Freie oder eigentumsüberschreibende SQL-Variable abgewiesen')
    values = {'DemoId':'IDX-012', 'RunToken':token, 'TargetDatabase':'SQLPERF_LAB_IDX012_'+token,
              'ConfirmIsolatedLab':'1', 'HighImpactConfirmed':'1', 'MaximumRuntimeSeconds':'300',
              'OriginalPreview':str(original if original is not None else -1), 'FaultAfterIndexBuild':'0'}
    values.update(variables or {})
    stage,_=cost_context(script)
    if stage is not None:
        values['CostStage']=stage
    master_phases={'00_Preflight.sql','10_Setup.sql','90_Restore.sql','91_AttestDrop.sql','92_Absence.sql'}
    database='master' if script.name in master_phases else 'SQLPERF_LAB_IDX012_'+token
    command = build_sqlcmd_command(executable=executable, server=server, auth=auth,
                                  username=username, database=database, script=script, variables=values)
    command.remove('-W')
    at = command.index('-h')
    del command[at:at+2]
    command.extend(['-C','-l','2','-m','1','-y','0'])
    return command


def marker(output, prefix):
    return [line.strip() for line in output.splitlines() if line.strip().startswith(prefix+'|')]


def records(output):
    result = []
    for line in output.splitlines():
        if line.strip().startswith('{'):
            row = json.loads(line.strip())
            if not isinstance(row, dict):
                raise ValueError('Begrenzte JSON-Objekte erforderlich')
            result.append(row)
    return result


def one_record(output, kind):
    selected = [row for row in records(output) if row.get('kind') == kind]
    if len(selected) != 1:
        raise ValueError('Ein vollständiger Datensatz fehlt: '+kind)
    return selected[0]


def source_distances(row, database_id, *, changed=False):
    if type(changed) is not bool:
        raise ValueError('Festes boolesches Quellenprofil erforderlich')
    if row.get('DatabaseId') != database_id:
        raise ValueError('Unabhängig attestierte eigene Quellen-DB fehlt')
    vectors, distances = row.get('vectors'), row.get('rows')
    if not isinstance(vectors, list) or not isinstance(distances, list) or len(vectors)!=999 or len(distances)!=999:
        raise ValueError('Vollständige 999-Row-Quelle fehlt')
    calculated = {}
    for item in vectors:
        identity = item.get('Id')
        if type(identity) is not int or not 1<=identity<=999 or identity in calculated:
            raise ValueError('Vollständige eindeutige Quellen-IDs fehlen')
        v = json.loads(item['JsonValue'])
        # Ausschließlich der vollständig beobachtete DEC-074-Korpus: seine
        # T-SQL-Division liefert sechs Dezimalstellen, bevor float32 entsteht.
        # Die unabhängige rationale Ganzzahlrechnung vermeidet Python-round.
        expected = (1,0,0) if changed and identity==999 else (1,identity/1000,(((identity*17)%97)*1000000//97)/1000000)
        if (not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v)
                or any(abs(x-y)>0.000001 for x,y in zip(v,expected))):
            raise ValueError('Tatsächliche float32-VECTOR(3)-Quelle verändert')
        calculated[identity] = 1-v[0]/math.sqrt(sum(x*x for x in v))
    actual = {}
    for item in distances:
        identity, distance = item.get('Id'), item.get('DistanceValue')
        if (type(identity) is not int or identity not in calculated or identity in actual
                or type(distance) not in (int,float) or not math.isfinite(distance)
                or not 0<=distance<=2 or abs(distance-calculated[identity])>0.000001):
            raise ValueError('Tatsächliche vollständige Quellendistanz verändert')
        actual[identity] = distance
    return actual


def combine_source(output,database_id,*,changed=False):
    row=one_record(output,'SOURCE_DISTANCES')
    blocks=[r for r in records(output) if r.get('kind')=='SOURCE_VECTOR_BLOCK']
    if (len(blocks)!=10 or any(type(r.get('BlockId')) is not int for r in blocks)
            or {r['BlockId'] for r in blocks}!=set(range(1,11))):
        raise ValueError('Vollständige begrenzte Quellenblockabdeckung fehlt')
    vectors=[]
    for block in blocks:
        items=block.get('vectors')
        if (block.get('DatabaseId')!=database_id or not isinstance(items,list) or len(items)!=(99 if block['BlockId']==10 else 100)
                or any(type(r.get('Id')) is not int for r in items)
                or {r['Id'] for r in items}!=set(range((block['BlockId']-1)*100+1,min(999,block['BlockId']*100)+1))):
            raise ValueError('Tatsächliche eigene Quellenblockidentität verletzt')
        vectors.extend(items)
    row['vectors']=vectors
    return source_distances(row,database_id,changed=changed)


def validate_snapshot(data, token, original, preview, maxdop):
    if (type(data.get('DatabaseId')) is not int or data['DatabaseId']<5
            or data.get('context')!='SQLPERF_LAB_IDX012_'+token or data.get('build')!='17.0.5005.3'
            or data.get('edition')!=3
            or data.get('baseline')!=[{'Id':1,'OriginalValue':original,'RunToken':token,'MaxDopOriginal':0}]):
        raise ValueError('Eigene vollständige DB-/Build-/Baselinebindung fehlt')
    for name,value in [('PREVIEW_FEATURES',preview),('MAXDOP',maxdop)]:
        matches=[row for row in data.get('scoped',[]) if row.get('name')==name]
        if len(matches)!=1 or type(matches[0].get('value')) is not int or matches[0]['value']!=value:
            raise ValueError('Tatsächliche Konfiguration fehlt: '+name)
    options,files=data.get('options',[]),data.get('files',[])
    if (len(options)!=1 or options[0].get('compatibility_level')!=170 or options[0].get('recovery_model')!=3
            or len(files)!=2 or {r.get('type') for r in files}!={0,1}
            or any(r.get('max_size')!=(32768 if r['type']==0 else 8192)
                   or r.get('growth')!=2048 or r.get('is_percent_growth') is not False for r in files)):
        raise ValueError('Tatsächliche Ressourcen-/Optionsbindung fehlt')


def same_snapshot(before, after, *, enable=None, table_names=None, indexes=None):
    expected=copy.deepcopy(before)
    if enable:
        for row in expected['scoped']:
            if row['name']==enable:
                row['value'],row['is_value_default']=1,False
    if table_names is not None:
        tables=after.get('tables',[])
        if len(tables)!=len(table_names) or {(r.get('SchemaName'),r.get('TableName')) for r in tables}!=set(table_names):
            raise ValueError('Tatsächlicher eigener Tabellensatz verändert')
        old={(r['SchemaName'],r['TableName']):r for r in before['tables']}
        if any(r!=old[(r['SchemaName'],r['TableName'])] for r in tables if (r['SchemaName'],r['TableName']) in old):
            raise ValueError('Vorhandene eigene Tabellenidentität verändert')
        expected['tables'],expected['fixture_object']=tables,after['fixture_object']
    if indexes is not None:
        if type(after.get('vector_indexes')) is not int or after['vector_indexes']!=indexes:
            raise ValueError('Tatsächlicher eigener Vektorindexbestand verändert')
        expected['vector_indexes']=indexes
    if expected!=after:
        raise ValueError('Vollständiger Host-/Scoped-/Marker-/Baseline-/Options-/Dateistand verändert')


def run_profile(*, executable, server, auth, username, token, confirmed, high_impact,
                folder=FOLDER, executor=execute_client, clock=time.monotonic, fault=None, normal_deadline=None, mode="dml-boundary", capture_storage=False, capture_costs=False):
    if (confirmed is not True or high_impact is not True or not isinstance(token,str)
            or not re.fullmatch('[A-F0-9]{16}',token) or fault not in (None,'after_setup','after_index_build')
            or mode not in ('dml-boundary','drop-rebuild') or type(capture_storage) is not bool
            or (capture_storage and mode!='drop-rebuild') or type(capture_costs) is not bool
            or (capture_costs and (mode!='drop-rebuild' or not capture_storage))):
        raise ValueError('Lokale YELLOW-Bestätigung und vollständige Tokenbindung erforderlich')
    folder=Path(folder).resolve()
    regular=Deadline(300,clock)
    if normal_deadline is not None:
        if type(normal_deadline) not in (int,float) or not math.isfinite(normal_deadline):
            raise ValueError('Tatsächliche übergeordnete Deadline erforderlich')
        regular.end=min(regular.end,normal_deadline)
    started=False
    client_end_unknown=False
    original=None
    phases=[]
    evidence={'generation':'UNKNOWN','runtime_qualification':'NOT_ESTABLISHED'}
    outcome,code,cleanup_ok='WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED',False

    def execute(identity,filename,budget,cap=60,variables=None):
        nonlocal started
        script=(folder/filename).resolve()
        if script.parent!=folder:
            raise ValueError('SQL-Pfad verlässt das eigene Phasenverzeichnis')
        command=phase_command(executable,server,auth,username,script,token,original,variables)
        timeout=budget.remaining(cap)
        if identity=='SETUP':
            started=True
        response=executor(command,timeout_seconds=timeout)
        output=response.stdout+'\n'+response.stderr
        if len(output.encode('utf-8'))>1000000:
            raise ValueError('Vollständiger Output überschreitet den begrenzten Vertrag')
        summaries=re.findall(r'^SQLPERF_SUMMARY\|(?:PASS|WARN|SKIP|FAIL)\|[A-Z][A-Z0-9_]*$',output,re.M)
        actual=(('FAIL','FAIL_TIMEOUT') if response.timed_out else
                ('FAIL','FAIL_EXECUTION') if response.returncode!=0 else
                ('FAIL','FAIL_CONTRACT') if len(summaries)!=1 else extract_summary(response.stdout,response.stderr))
        if actual is None:
            actual=('FAIL','FAIL_CONTRACT')
        accepted={('PASS','OK'),('WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED')}
        if identity=='PREFLIGHT':
            accepted|={('SKIP','SKIP_VERSION'),('SKIP','SKIP_CONFIGURATION'),('SKIP','SKIP_PERMISSION')}
        if response.returncode==0 and not response.timed_out and actual not in accepted:
            actual=('FAIL','FAIL_CONTRACT')
        phases.append((identity,*actual))
        return actual,output

    def normal(identity,filename,variables=None):
        actual,output=execute(identity,filename,regular,variables=variables)
        if actual[0] in ('FAIL','SKIP'):
            raise PhaseStop(*actual)
        return output

    def snapshot(preview,maxdop,before=None,**changes):
        data=records(normal('SNAPSHOT','21_Snapshot.sql'))
        if len(data)!=1:
            raise ValueError('Vollständiger einzelner Snapshot fehlt')
        data=data[0]
        validate_snapshot(data,token,original,preview,maxdop)
        if before is not None:
            same_snapshot(before,data,**changes)
        return data

    def storage(stage):
        if capture_storage:
            output=normal('STORAGE_'+stage,'22_Storage.sql',variables={'StorageStage':stage})
            actual=validate_storage(one_record(output,'STORAGE'),token=token,database_id=database_id,
                                    fixture_object=state['fixture_object'],stage=stage)
            evidence.setdefault('storage',[]).append(actual)

    def costs(output,stage):
        if capture_costs:
            own_files={f['file_id'] for f in evidence['storage'][0]['record']['files']}
            actual=validate_costs([r for r in records(output) if r.get('kind')=='PHASE_COST'],
                                  token=token,database_id=database_id,stage=stage,file_ids=own_files)
            evidence.setdefault('phase_costs',[]).append(actual)

    try:
        normal('PREFLIGHT','00_Preflight.sql')
        output=normal('SETUP','10_Setup.sql')
        baselines=marker(output,'ANN_BUILD_BASELINE')
        if baselines not in ([f'ANN_BUILD_BASELINE|{token}|0|0'],[f'ANN_BUILD_BASELINE|{token}|1|0']):
            raise ValueError('Tatsächliche vollständige duale Baseline fehlt')
        original=int(baselines[0].split('|')[2])
        state=snapshot(original,0)
        database_id=state['DatabaseId']
        if marker(output,'IDX012_DATABASE')!=[f'IDX012_DATABASE|{token}|{database_id}']:
            raise ValueError('Unabhängige tatsächliche eigene DB-ID fehlt')
        evidence['database_id']=database_id
        if fault=='after_setup':
            evidence['controlled_fault']='AFTER_SETUP'
            phases.append(('CONTROLLED_FAULT_AFTER_SETUP','FAIL','FAIL_EXECUTION'))
            raise PhaseStop('FAIL','FAIL_EXECUTION')
        normal('ENABLE_PREVIEW','11_EnablePreview.sql')
        state=snapshot(1,0,state,enable='PREVIEW_FEATURES')
        normal('ENABLE_MAXDOP','12_EnableMaxdop.sql')
        state=snapshot(1,1,state,enable='MAXDOP')
        baseline_output=normal('BASELINE','20_Baseline.sql')
        distances=combine_source(baseline_output,database_id)
        names=[('dbo','PreviewState'),('lab','VectorFixture'),('lab','FrozenSource'),('lab','ExactOracle')]
        state=snapshot(1,1,state,table_names=names,indexes=0)
        storage('BASELINE')
        before_vectors={row['Id']:row['JsonValue'] for block in records(baseline_output)
                        if block.get('kind')=='SOURCE_VECTOR_BLOCK' for row in block['vectors']}
        output=normal('DML_BOUNDARY','30_CostBoundary.sql' if capture_costs else '30_DmlBoundary.sql')
        costs(output,'DML_BOUNDARY')
        index=one_record(output,'INDEX')
        if (index.get('RunToken')!=token or type(index.get('DatabaseId')) is not int
                or index['DatabaseId']!=database_id
                or type(index.get('BuildElapsedUs')) is not int or index['BuildElapsedUs']<0):
            raise ValueError('Actual bounded own build evidence missing')
        metadata=index.get('metadata')
        if not isinstance(metadata,list) or len(metadata)!=1:
            raise ValueError('Complete single own index metadata missing')
        own_index=metadata[0]
        if (type(own_index.get('object_id')) is not int or own_index['object_id']!=state['fixture_object']
                or type(own_index.get('index_id')) is not int or own_index['index_id']<1
                or own_index.get('name')!='IDX012_OwnVector'
                or type(own_index.get('type')) is not int or own_index['type']!=8
                or own_index.get('type_desc')!='VECTOR' or own_index.get('is_disabled') is not False
                or own_index.get('is_hypothetical') is not False
                or own_index.get('vector_index_type')!='DiskANN' or own_index.get('distance_metric')!='COSINE'):
            raise ValueError('Actual current own vector index profile changed')
        evidence['dml_boundary']=validate_dml_boundary(records(output),token=token,database_id=database_id)
        evidence['index']=index
        state=snapshot(1,1,state,indexes=1)
        storage('INDEXED')
        after=normal('SOURCE_AFTER','40_SourceAfter.sql')
        after_distances=combine_source(after,database_id)
        after_vectors={row['Id']:row['JsonValue'] for block in records(after)
                       if block.get('kind')=='SOURCE_VECTOR_BLOCK' for row in block['vectors']}
        after_index=one_record(after,'INDEX_AFTER')
        if (before_vectors!=after_vectors or distances!=after_distances
                or after_index.get('RunToken')!=token or type(after_index.get('DatabaseId')) is not int
                or after_index['DatabaseId']!=database_id or after_index.get('metadata')!=metadata):
            raise ValueError('Independent complete actual source or index state changed')
        snapshot(1,1,state)
        evidence['independent_source_comparison']={'rows':999,'full_text_equal':True,'distance_equal':True}
        if fault=='after_index_build':
            evidence['controlled_fault']='AFTER_INDEX_BUILD_AND_SOURCE_CHECK'
            phases.append(('CONTROLLED_FAULT_AFTER_INDEX_BUILD','FAIL','FAIL_EXECUTION'))
            raise PhaseStop('FAIL','FAIL_EXECUTION')
        if mode=='drop-rebuild':
            lifecycle_output=normal('DROP_CHANGE_REBUILD','50_CostRebuild.sql' if capture_costs else '50_DropRebuild.sql')
            costs(lifecycle_output,'REBUILD')
            state=snapshot(1,1,state)
            final_output=normal('SOURCE_REBUILT','40_SourceAfter.sql')
            final_distances=combine_source(final_output,database_id,changed=True)
            final_vectors={row['Id']:row['JsonValue'] for block in records(final_output)
                           if block.get('kind')=='SOURCE_VECTOR_BLOCK' for row in block['vectors']}
            if (set(final_vectors)!=set(before_vectors) or final_vectors[999]==before_vectors[999]
                    or json.loads(final_vectors[999])!=[1,0,0]
                    or any(final_vectors[i]!=before_vectors[i] for i in range(1,999))):
                raise ValueError('Unabhängige vollständige Ein-Row-Quellenänderung fehlt')
            lifecycle=validate_lifecycle(records(lifecycle_output),token=token,database_id=database_id,
                                         before_distances=distances,after_distances=final_distances,
                                         before_metadata=metadata)
            final_index=one_record(final_output,'INDEX_AFTER')
            if (final_index.get('RunToken')!=token or type(final_index.get('DatabaseId')) is not int
                    or final_index['DatabaseId']!=database_id or final_index.get('metadata')!=lifecycle['metadata']):
                raise ValueError('Unabhängige vollständige aktuelle Rebuildmetadaten fehlen')
            snapshot(1,1,state)
            evidence['lifecycle']=lifecycle
            evidence['rebuild_source_comparison']={'rows':999,'only_changed_id':999,'other_998_texts_equal':True}
            storage('REBUILT')
    except ClientEndUnknown:
        client_end_unknown=True
        outcome,code='FAIL','FAIL_CLEANUP'
        evidence.update(client_end='UNKNOWN',temporary_source_cleanup='NOT_ESTABLISHED')
    except PhaseStop as stopped:
        outcome,code=stopped.outcome,stopped.code
    except TimeoutError:
        outcome,code='FAIL','FAIL_TIMEOUT'
    except (OSError,ValueError,RuntimeError,KeyError,TypeError,json.JSONDecodeError):
        outcome,code='FAIL','FAIL_RESULT_CONTRACT'
    except KeyboardInterrupt:
        outcome,code='FAIL','FAIL_EXECUTION'
    finally:
        if started and not client_end_unknown:
            recovery=Deadline(20,clock)
            successes=set()
            for identity,filename,cap in [('RESTORE','90_Restore.sql',6),('ATTEST_DROP','91_AttestDrop.sql',6),('ABSENCE','92_Absence.sql',4)]:
                if identity=='ATTEST_DROP' and 'RESTORE' not in successes:
                    continue
                try:
                    actual,output=execute(identity,filename,recovery,cap)
                    if actual!=('PASS','OK'):
                        continue
                    if identity in ('RESTORE','ATTEST_DROP'):
                        prefix='ANN_RESTORE' if identity=='RESTORE' else 'ANN_ATTEST'
                        if original is None or marker(output,prefix)!=[f'{prefix}|{token}|{original}|0']:
                            continue
                        if identity=='ATTEST_DROP' and marker(output,'ANN_RECOVERY')!=['ANN_RECOVERY|DROP_CONFIRMED']:
                            continue
                    elif marker(output,'ANN_DB')!=['ANN_DB|ABSENT']:
                        continue
                    successes.add(identity)
                except (OSError,TimeoutError,ValueError,KeyboardInterrupt):
                    phases.append((identity,'FAIL','FAIL_CLEANUP'))
            cleanup_ok=successes=={'RESTORE','ATTEST_DROP','ABSENCE'} and clock()<=recovery.end
            if not cleanup_ok:
                outcome,code='FAIL','FAIL_CLEANUP'
    return Result(outcome,code,tuple(phases),original,cleanup_ok,evidence)


class PhaseStop(Exception):
    def __init__(self,outcome,code):
        self.outcome,self.code=outcome,code


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server',required=True)
    parser.add_argument('--sqlcmd')
    parser.add_argument('--mode',choices=('dml-boundary','drop-rebuild'),default='dml-boundary')
    parser.add_argument('--capture-storage',action='store_true')
    parser.add_argument('--capture-costs',action='store_true')
    parser.add_argument('--username',default='sa')
    parser.add_argument('--run-token',required=True)
    parser.add_argument('--confirm-isolated-lab',action='store_true')
    parser.add_argument('--high-impact-confirmed',action='store_true')
    args=parser.parse_args()
    result=run_profile(executable=resolve_sqlcmd(args.sqlcmd),server=args.server,auth='sql',username=args.username,
                       token=args.run_token,confirmed=args.confirm_isolated_lab,high_impact=args.high_impact_confirmed,mode=args.mode,capture_storage=args.capture_storage,capture_costs=args.capture_costs)
    print(json.dumps(result.__dict__,ensure_ascii=False))
    return 1 if result.outcome=='FAIL' else 0


if __name__=='__main__':
    raise SystemExit(main())
