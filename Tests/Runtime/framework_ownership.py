#!/usr/bin/env python3
"""Vollständige Eigentumsmarker der Frameworkreferenz im eigenen Container prüfen."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

import cleanup_ownership as ownership
import run_framework_sql_matrix as matrix
from execution_target import ExecutionTarget,ExecutionTargetError,docker_target,run_sql,verify_engine

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'Demos/00_Framework/Sql/FWK_TestDatabaseLifecycle.sql'
DEMO='QRY-001'
ACTIONS=('CREATE','VALIDATE','DROP')


def render(source: str,action: str,major: int,*,invalid_demo: bool=False) -> str:
    if action not in ACTIONS or major not in (15,16,17): raise ValueError('Bekannte Aktion und Version erforderlich')
    return matrix._replace_declarations(source,{
        'Action':ownership.literal(action),'DemoId':ownership.literal('XXX-000' if invalid_demo else DEMO),
        'RunToken':ownership.literal('LOCAL'),'RequestedCompatibilityLevel':str(major*10),
        'ConfirmLabUse':'1' if action in ('CREATE','DROP') else '0',
        'ConfirmDrop':'1' if action=='DROP' else '0','EmitEnvironmentDetails':'0',
    })


def control_batch(source: str) -> str:
    commands=re.findall(r'(?im)^[\t ]*GO\b[^\r\n]*',source)
    if len(commands)!=1 or not re.fullmatch(r'[\t ]*GO[\t ]*',commands[0],re.I):
        raise RuntimeError('Unbekannte Framework-Batchform')
    before,after=re.split(r'(?im)^[\t ]*GO[\t ]*$',source)
    if not re.fullmatch(r'\s*/\*.*?\*/\s*USE\s+\[master\];\s*',before,re.S|re.I):
        raise RuntimeError('Unbekannter Framework-Vorspann')
    return before+'\n'+after


def rows(output: str) -> list[list[str]]:
    result=[line.strip().split('|') for line in output.splitlines() if line.strip()]
    if any(len(row)!=8 or not row[0].isdigit() for row in result):
        raise RuntimeError('Unbekannter Framework-Ergebnisrecord')
    return result


def require_preserved(output: str,*,invalid_demo: bool=False) -> None:
    lines=[line.strip() for line in output.splitlines() if line.strip()]
    if not lines or lines[-1]!='PRESERVED' or lines.count('PRESERVED')!=1:
        raise RuntimeError('Eindeutiger Erhaltungsrecord fehlt')
    records=rows('\n'.join(lines[:-1])); code='FAIL_CONTRACT' if invalid_demo else 'FAIL_STATE'
    check='DEMO_ID' if invalid_demo else 'OWNERSHIP_MARKERS'
    for wanted in (check,'SUMMARY'):
        found=[r for r in records if r[2]==wanted]
        if len(found)!=1 or found[0][1:5]!=['LIFECYCLE',wanted,'FAIL',code]:
            raise RuntimeError('Spezifischer Framework-Ablehnungsrecord fehlt')


def fixture(target: ExecutionTarget,major: int) -> None:
    ownership.fixture(target,DEMO)
    run_sql(target,database='master',sql_text=f'ALTER DATABASE [{ownership.database(DEMO)}] SET COMPATIBILITY_LEVEL={major*10}; ALTER DATABASE [{ownership.database(DEMO)}] SET AUTO_SHRINK OFF;')


def snapshot(target: ExecutionTarget) -> str:
    # Ein SQL-seitiger vollständiger Vergleich wird für alle Negativfälle benutzt.
    # Positive Wiederverwendung liefert ebenfalls den gesamten XML-Wert in Hexform.
    output=run_sql(target,database='master',sql_text=f"""
SET NOCOUNT ON;
DECLARE @Bytes varbinary(max)={ownership.state_expression(DEMO)},@Offset int=1;
SELECT 'LENGTH',DATALENGTH(@Bytes);
WHILE @Offset<=DATALENGTH(@Bytes) BEGIN
 SELECT 'BYTES',@Offset,CONVERT(varchar(200),SUBSTRING(@Bytes,@Offset,100),2);
 SET @Offset+=100;
END;
""")
    # Gemeinsame strikte Dekodierung ohne Abhängigkeit vom Setup-Prüflauf.
    records=[s.strip().split('|') for s in output.splitlines() if s.strip()]
    if not records or len(records[0])!=2 or records[0][0]!='LENGTH' or not records[0][1].isdigit():raise RuntimeError('Snapshotlänge fehlt')
    size=int(records[0][1]);data=b''
    if not 0<size<=1048576:raise RuntimeError('Snapshot außerhalb der Grenze')
    for row in records[1:]:
        if len(row)!=3 or row[0]!='BYTES' or not row[1].isdigit() or int(row[1])!=len(data)+1 or not re.fullmatch(r'(?:[0-9A-F]{2}){1,100}',row[2]):raise RuntimeError('Snapshotrecord unvollständig')
        chunk=bytes.fromhex(row[2])
        if len(chunk)!=min(100,size-len(data)):raise RuntimeError('Snapshot gekürzt oder erweitert')
        data+=chunk
    if len(data)!=size:raise RuntimeError('Snapshotbytes fehlen')
    return data.hex()


def reject_file(target: ExecutionTarget,source: str,action: str,major: int) -> None:
    try:run_sql(target,database='master',sql_text=render(source,action,major)+"\nGO\nTHROW 51999,'UNREACHED_BATCH',1;\n")
    except ExecutionTargetError as exc:
        if re.search(r'\b51002\b',str(exc)) and 'UNREACHED_BATCH' not in str(exc):return
        raise RuntimeError('Falscher Fehler der Framework-Gesamtdatei') from exc
    raise RuntimeError('Framework-Gesamtdatei wurde nicht abgewiesen')


def reject_batch(target: ExecutionTarget,phase: str,values: dict[str,str|None],*,object_only: bool=False,invalid_demo: bool=False) -> None:
    if re.search(r'(?im)^[\t ]*GO\b',phase):raise RuntimeError('Ungeprüfter Framework-Batchtrenner')
    db=ownership.database(DEMO);expression=ownership.state_expression(DEMO)
    output=run_sql(target,database='master',sql_text=f"""
SET NOCOUNT ON;
{ownership.marker_sql(DEMO,values,object_only)}
IF DB_ID(N'{db}') IS NULL OR DB_ID(N'SQLPERF_LAB_XXX000_LOCAL') IS NOT NULL THROW 51991,'FIXTURE_IDENTITY_MISSING',1;
IF (SELECT COUNT(*) FROM [{db}].dbo.OwnershipProbe WHERE Value=73)<>1 THROW 51991,'SENTINEL_MISSING',1;
DECLARE @Before varbinary(max)={expression},@After varbinary(max),@ActualError int=NULL;
BEGIN TRY
 EXEC sys.sp_executesql {ownership.literal(phase)};
END TRY
BEGIN CATCH
 SET @ActualError=ERROR_NUMBER();
END CATCH;
IF @ActualError IS NULL OR @ActualError<>{51000 if invalid_demo else 51002} THROW 51992,'SPECIFIC_FRAMEWORK_REJECTION_MISSING',1;
IF DB_ID(N'{db}') IS NULL OR DB_ID(N'SQLPERF_LAB_XXX000_LOCAL') IS NOT NULL THROW 51993,'DATABASE_IDENTITY_CHANGED',1;
SET @After={expression};
IF @Before IS NULL OR @After IS NULL OR DATALENGTH(@Before)<>DATALENGTH(@After) OR @Before<>@After THROW 51994,'FRAMEWORK_STATE_WAS_CHANGED',1;
SELECT 'PRESERVED';
""")
    require_preserved(output,invalid_demo=invalid_demo)


def reject_missing(target: ExecutionTarget,source: str,phase: str,action: str,major: int) -> None:
    ownership.reset_markers(target,DEMO,{})
    before=snapshot(target)
    reject_file(target,source,action,major)
    if before!=snapshot(target):raise RuntimeError('Gesamtdatei veränderte Zustand vor Markerprüfung')
    # Dieselbe Markerbedingung benötigt auch die spezifischen Ergebnisrecords;
    # der Fehlertext der echten sqlcmd-Dateiform allein reicht dafür nicht.
    reject_batch(target,render(phase,action,major),{})


def verify_oracles(target: ExecutionTarget) -> None:
    expression=ownership.state_expression(DEMO)
    output=run_sql(target,database='master',sql_text=f"""
SET NOCOUNT ON;
{ownership.marker_sql(DEMO,{'Project':'X'*128+'A'},False)}
DECLARE @Before varbinary(max)={expression},@After varbinary(max);
{ownership.marker_sql(DEMO,{'Project':'X'*128+'B'},False)}
SET @After={expression};
IF @Before IS NULL OR @After IS NULL OR @Before=@After THROW 51995,'FRAMEWORK_ORACLE_CROPPED',1;
SELECT 'ORACLE_COMPLETE';
""")
    if output.split()!=['ORACLE_COMPLETE']:raise RuntimeError('Vollständige Marker-Gegenprobe fehlt')
    db=ownership.database(DEMO)
    for harm,repair in ((f'UPDATE [{db}].dbo.OwnershipProbe SET Value=72;',f'UPDATE [{db}].dbo.OwnershipProbe SET Value=73;'),(f'ALTER DATABASE [{db}] SET AUTO_SHRINK ON;',f'ALTER DATABASE [{db}] SET AUTO_SHRINK OFF;')):
        try:reject_batch(target,harm+"THROW 51002,'SYNTHETIC_BAD_FRAMEWORK',1;",ownership.markers(DEMO))
        except ExecutionTargetError as exc:
            if '51994' not in str(exc) or 'FRAMEWORK_STATE_WAS_CHANGED' not in str(exc):raise RuntimeError('Falscher Fehler der Oracle-Gegenprobe') from exc
        else:raise RuntimeError('Schädigender Frameworkpfad wurde akzeptiert')
        run_sql(target,database='master',sql_text=repair)


def positive(target: ExecutionTarget,source: str,action: str,major: int,*,existing: bool=True) -> None:
    output=run_sql(target,database='master',sql_text=render(source,action,major))
    records=rows(output)
    if any(r[3:5]!=['PASS','OK'] for r in records):raise RuntimeError('Unerwarteter positiver Framework-Teilbefund')
    summary=[r for r in records if r[2]=='SUMMARY']
    if len(summary)!=1 or summary[0][1:5]!=['LIFECYCLE','SUMMARY','PASS','OK']:raise RuntimeError('Eindeutiger positiver Frameworkrecord fehlt')
    if existing:
        matched=[r for r in records if r[2]=='OWNERSHIP_MARKERS']
        if len(matched)!=1 or matched[0][1:5]!=['LIFECYCLE','OWNERSHIP_MARKERS','PASS','OK']:raise RuntimeError('Positiver Eigentumsrecord fehlt')


def finish(target: ExecutionTarget,source: str,major: int) -> None:
    positive(target,source,'DROP',major)
    ownership.absent(target,DEMO)
    # Der bestehende Frameworkvertrag meldet bei bereits fehlender Datenbank FAIL_STATE.
    reject_file(target,source,'DROP',major)
    ownership.absent(target,DEMO)


def run_probes(target: ExecutionTarget,major: int,*,old_source: Path|None=None,repetitions: int=2) -> int:
    if target.kind!='docker' or not target.container or major not in (15,16,17) or repetitions!=2:
        raise ValueError('Eigener Container, bekannte Version und zwei Profile erforderlich')
    source=SOURCE.read_text(encoding='utf-8-sig');phase=control_batch(source);count=0
    if old_source:
        old=old_source.read_text(encoding='utf-8-sig');control_batch(old)
        for action in ACTIONS:
            fixture(target,major)
            ownership.reset_markers(target,DEMO,{**ownership.markers(DEMO),'Project':ownership.markers(DEMO)['Project']+' '})
            positive(target,old,action,major)
            if action=='DROP':ownership.absent(target,DEMO)
            else:
                ownership.reset_markers(target,DEMO,ownership.markers(DEMO));finish(target,source,major)
            print(f'FRAMEWORK_OWNERSHIP_OLD|{action}|ACTUAL_FALSE_ACCEPTANCE',flush=True)
    for repetition in (1,2):
        for action in ACTIONS:
            fixture(target,major)
            if action=='CREATE':verify_oracles(target)
            cases=[c for c in ownership.negative_cases(DEMO) if not c[3]]
            if len(cases)!=29:raise RuntimeError('Vollständiges Markerfallinventar fehlt')
            for label,values,obj,_ in cases:
                if label=='ALL_MISSING':
                    if values or obj:raise RuntimeError('Unbekannte Form des Falls ohne Marker')
                    reject_missing(target,source,phase,action,major)
                else:reject_batch(target,render(phase,action,major),values,object_only=obj)
                count+=1
            reject_batch(target,render(phase,action,major,invalid_demo=True),ownership.markers(DEMO),invalid_demo=True);count+=1
            ownership.reset_markers(target,DEMO,ownership.markers(DEMO))
            if action=='DROP':finish(target,source,major)
            else:
                before=snapshot(target)
                for _ in (1,2):
                    positive(target,source,action,major)
                    if before!=snapshot(target):raise RuntimeError('Positive Wiederverwendung änderte Zustand')
                finish(target,source,major)
            print(f'FRAMEWORK_OWNERSHIP_FIXED|{action}|{repetition}|PASS|negative=30',flush=True)
        positive(target,source,'CREATE',major,existing=False)
        # Eine echte Prüfzeile macht unbeabsichtigte spätere Neuerstellung sichtbar.
        run_sql(target,database=ownership.database(DEMO),sql_text='CREATE TABLE dbo.OwnershipProbe(Value int NOT NULL); INSERT dbo.OwnershipProbe VALUES(73);')
        before=snapshot(target)
        for action in ('CREATE','VALIDATE'):
            positive(target,source,action,major)
            if before!=snapshot(target):raise RuntimeError('Neue Datenbank änderte sich bei Wiederverwendung')
        finish(target,source,major)
    return count


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container',required=True);parser.add_argument('--expected-major',type=int,choices=(15,16,17),required=True)
    parser.add_argument('--confirm-disposable',action='store_true',required=True);parser.add_argument('--old-source',type=Path)
    args=parser.parse_args();target=docker_target(container=args.container)
    major=verify_engine(target,expected_major=args.expected_major)
    count=run_probes(target,major,old_source=args.old_source)
    print(f'FRAMEWORK_OWNERSHIP_COMPLETE|PASS|actions=3|profiles=6|negative={count}|version={major}',flush=True)


if __name__=='__main__':main()
