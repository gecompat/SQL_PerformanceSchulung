#!/usr/bin/env python3
"""Setup-Eigentum vor Änderungen ausschließlich in einer eigenen Dockerinstanz prüfen."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

import cleanup_ownership as ownership
from execution_target import ExecutionTarget, ExecutionTargetError, docker_target, run_sql, verify_engine

ROOT=Path(__file__).resolve().parents[2]
DEMO_IDS=('OPT-002','OPT-009','OPT-010','OPT-013','OPT-015','OPT-016','OPT-017','QRY-004','QRY-013','CON-004')
MIN_MAJOR={'OPT-009':16,'OPT-010':17}


def source_path(demo: str,root: Path=ROOT) -> Path:
    matches=list((root/'Demos').glob(f'**/{demo}_*/10_Setup.sql'))
    if len(matches)!=1: raise RuntimeError('Eindeutige Setupquelle fehlt: '+demo)
    return matches[0]


def control_phase(source: str) -> str:
    commands=re.findall(r'(?im)^[\t ]*GO\b[^\r\n]*',source)
    if not commands or any(not re.fullmatch(r'[\t ]*GO[\t ]*',s,re.I) for s in commands):
        raise RuntimeError('Unbekannter GO-Befehl')
    batches=re.split(r'(?im)^[\t ]*GO[\t ]*$',source)
    if len(batches)<4 or not re.fullmatch(r'\s*(?:/\*.*?\*/\s*)?USE\s+\[master\];\s*',batches[0],re.S|re.I):
        raise RuntimeError('Unbekannter Setup-Einstieg')
    if batches[2].strip()!='USE [$(TargetDatabase)];':
        raise RuntimeError('Unbekannte Grenze zum Datenmodell')
    # Nur der variablefreie USE-master-Vorspann wird mit dem unveränderten
    # ersten Kontrollbatch verbunden. Die echte Gesamtdatei wird separat geprüft.
    return batches[0]+'\n'+batches[1]


def initial_config(demo: str,auto_close: bool=False) -> str:
    db=ownership.database(demo)
    return f"""
ALTER DATABASE [{db}] SET RECOVERY FULL;
ALTER DATABASE [{db}] SET AUTO_CLOSE {'ON' if auto_close else 'OFF'};
ALTER DATABASE [{db}] SET AUTO_SHRINK ON;
ALTER DATABASE [{db}] SET PAGE_VERIFY NONE;
ALTER DATABASE [{db}] SET COMPATIBILITY_LEVEL=140;
EXEC sys.sp_executesql N'USE [{db}]; ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS=OFF;';
"""


def fixture(target: ExecutionTarget,demo: str) -> None:
    ownership.fixture(target,demo)
    db=ownership.database(demo)
    run_sql(target,database=db,sql_text='CREATE SCHEMA lab; CREATE TABLE lab.OwnershipSetupSentinel(Value int NOT NULL); INSERT lab.OwnershipSetupSentinel VALUES(919);')
    run_sql(target,database='master',sql_text=initial_config(demo))


def state_expression(demo: str) -> str:
    db=ownership.database(demo)
    parts=[
        ('BaseState',f'SELECT CONVERT(varchar(max),{ownership.state_expression(demo)},2) AS FullBytes'),
        ('LabSentinel',f'SELECT Value FROM [{db}].lab.OwnershipSetupSentinel ORDER BY Value'),
        ('UserTables',f'SELECT s.name AS SchemaName,t.name,t.object_id FROM [{db}].sys.tables t JOIN [{db}].sys.schemas s ON s.schema_id=t.schema_id WHERE t.is_ms_shipped=0 ORDER BY t.object_id'),
        ('UserColumns',f'SELECT c.object_id,c.column_id,c.name,c.user_type_id,c.max_length,c.is_nullable,c.default_object_id FROM [{db}].sys.columns c JOIN [{db}].sys.tables t ON t.object_id=c.object_id WHERE t.is_ms_shipped=0 ORDER BY c.object_id,c.column_id'),
        ('Modules',f'SELECT object_id,CONVERT(varchar(max),CONVERT(varbinary(max),definition),2) AS FullBytes FROM [{db}].sys.sql_modules ORDER BY object_id'),
        ('ScopedConfig',f'SELECT configuration_id,name,CONVERT(nvarchar(max),value) AS Value,CONVERT(nvarchar(max),value_for_secondary) AS SecondaryValue FROM [{db}].sys.database_scoped_configurations ORDER BY configuration_id'),
    ]
    projection=','.join(f'({query} FOR XML RAW,TYPE) AS [{section}]' for section,query in parts)
    return f"CONVERT(varbinary(max),CONVERT(nvarchar(max),(SELECT {projection} FOR XML PATH('SetupSnapshot'),TYPE)))"


def decode_snapshot(output: str) -> bytes:
    rows=[line.strip().split('|') for line in output.splitlines() if line.strip()]
    if not rows or len(rows[0])!=2 or rows[0][0]!='LENGTH' or not rows[0][1].isdigit():
        raise RuntimeError('Snapshotlänge fehlt')
    length=int(rows[0][1])
    if not 0<length<=1048576: raise RuntimeError('Snapshot außerhalb der Ausgabebegrenzung')
    result=b''
    for row in rows[1:]:
        if len(row)!=3 or row[0]!='BYTES' or not row[1].isdigit() or int(row[1])!=len(result)+1:
            raise RuntimeError('Snapshotlücke oder doppelter Record')
        if not re.fullmatch(r'(?:[0-9A-F]{2}){1,100}',row[2]):
            raise RuntimeError('Ungültige Snapshotbytes')
        value=bytes.fromhex(row[2])
        if len(result)+len(value)>length: raise RuntimeError('Zusätzliche Snapshotbytes')
        if len(value)!=min(100,length-len(result)): raise RuntimeError('Gekürztes Snapshotstück')
        result+=value
    if len(result)!=length: raise RuntimeError('Unvollständiger Snapshot')
    return result


def snapshot(target: ExecutionTarget,demo: str,*,identity_only: bool=False) -> bytes:
    db=ownership.database(demo)
    if identity_only:
        expression=f"""CONVERT(varbinary(max),CONVERT(nvarchar(max),(SELECT
 (SELECT database_id FROM sys.databases WHERE name=N'{db}' FOR XML RAW,TYPE) AS [Identity],
 (SELECT Value FROM [{db}].dbo.OwnershipProbe ORDER BY Value FOR XML RAW,TYPE) AS [Probe],
 (SELECT Value FROM [{db}].lab.OwnershipSetupSentinel ORDER BY Value FOR XML RAW,TYPE) AS [LabProbe],
 (SELECT class,major_id,minor_id,name,CONVERT(nvarchar(max),SQL_VARIANT_PROPERTY(value,'BaseType')) AS BaseType,CONVERT(varchar(max),CONVERT(varbinary(max),CONVERT(nvarchar(max),value)),2) AS FullBytes FROM [{db}].sys.extended_properties ORDER BY class,major_id,minor_id,name FOR XML RAW,TYPE) AS [Markers]
 FOR XML PATH('SetupIdentity'),TYPE)))"""
    else: expression=state_expression(demo)
    output=run_sql(target,database='master',sql_text=f"""
SET NOCOUNT ON;
IF DB_ID(N'{db}') IS NULL THROW 51991,'FIXTURE_MISSING',1;
IF (SELECT COUNT(*) FROM [{db}].dbo.OwnershipProbe WHERE Value=73)<>1 THROW 51991,'SENTINEL_MISSING',1;
IF (SELECT COUNT(*) FROM [{db}].lab.OwnershipSetupSentinel WHERE Value=919)<>1 THROW 51991,'LAB_SENTINEL_MISSING',1;
DECLARE @Bytes varbinary(max)={expression},@Offset int=1;
SELECT 'LENGTH',DATALENGTH(@Bytes);
WHILE @Offset<=DATALENGTH(@Bytes) BEGIN
 SELECT 'BYTES',@Offset,CONVERT(varchar(200),SUBSTRING(@Bytes,@Offset,100),2);
 SET @Offset+=100;
END;
""")
    return decode_snapshot(output)


def file_rejection(target: ExecutionTarget,demo: str,source: str) -> None:
    try:
        run_sql(target,database='master',sql_text=ownership.render(source,demo)+"\nGO\nTHROW 51999,'UNREACHED_BATCH',1;\n")
    except ExecutionTargetError as exc:
        if re.search(r'\b51002\b',str(exc)) and 'FAIL_STATE' in str(exc) and 'UNREACHED_BATCH' not in str(exc): return
        raise RuntimeError('Falscher Setupfehler oder Batch nach Fehler ausgeführt') from exc
    raise RuntimeError('Eigentumsablehnung der vollständigen Datei fehlt')


def batch_rejection(target: ExecutionTarget,demo: str,phase: str,values: dict[str,str|None],object_only: bool=False,wrong_target: bool=False,auto_close: bool=False) -> None:
    if re.search(r'(?im)^[\t ]*GO\b',phase): raise RuntimeError('Kontrollphase enthält Batchtrenner')
    db=ownership.database(demo)
    code=51000 if wrong_target else 51002
    expression=state_expression(demo)
    output=run_sql(target,database='master',sql_text=f"""
SET NOCOUNT ON;
{initial_config(demo,auto_close)}
{ownership.marker_sql(demo,values,object_only)}
IF DB_ID(N'{db}') IS NULL OR DB_ID(N'{db}X') IS NOT NULL THROW 51991,'FIXTURE_IDENTITY_MISSING',1;
IF (SELECT COUNT(*) FROM [{db}].dbo.OwnershipProbe WHERE Value=73)<>1 OR (SELECT COUNT(*) FROM [{db}].lab.OwnershipSetupSentinel WHERE Value=919)<>1 THROW 51991,'SENTINEL_MISSING',1;
DECLARE @Before varbinary(max)={expression},@After varbinary(max),@ActualError int=NULL;
BEGIN TRY
 EXEC sys.sp_executesql {ownership.literal(ownership.render(phase,demo,wrong_target=wrong_target))};
END TRY
BEGIN CATCH
 SET @ActualError=ERROR_NUMBER();
END CATCH;
IF @ActualError IS NULL OR @ActualError<>{code} THROW 51992,'SPECIFIC_SETUP_REJECTION_MISSING',1;
IF DB_ID(N'{db}') IS NULL OR DB_ID(N'{db}X') IS NOT NULL THROW 51993,'DATABASE_IDENTITY_CHANGED',1;
SET @After={expression};
IF @Before IS NULL OR @After IS NULL OR DATALENGTH(@Before)<>DATALENGTH(@After) OR @Before<>@After THROW 51994,'SETUP_STATE_WAS_CHANGED',1;
SELECT 'PRESERVED';
""")
    if output.split()!=['PRESERVED']: raise RuntimeError('Vollständiges Setup-Erhaltungsresultat fehlt')


def verify_oracles(target: ExecutionTarget,demo: str) -> None:
    expression=state_expression(demo)
    output=run_sql(target,database='master',sql_text=f"""
SET NOCOUNT ON;
{ownership.marker_sql(demo,{'Project':'X'*128+'A'},False)}
DECLARE @First varbinary(max)={expression},@Second varbinary(max);
{ownership.marker_sql(demo,{'Project':'X'*128+'B'},False)}
SET @Second={expression};
IF @First IS NULL OR @Second IS NULL OR @First=@Second THROW 51995,'SETUP_ORACLE_CROPPED',1;
SELECT 'ORACLE_COMPLETE';
""")
    if output.split()!=['ORACLE_COMPLETE']: raise RuntimeError('Vollständige Setup-Oracle-Gegenprobe fehlt')
    if demo=='OPT-002':
        db=ownership.database(demo)
        for sql in (f'UPDATE [{db}].lab.OwnershipSetupSentinel SET Value=918;',f'ALTER DATABASE [{db}] SET AUTO_SHRINK OFF;'):
            try:
                batch_rejection(target,demo,sql+" THROW 51002,'SYNTHETIC_BAD_SETUP',1;",ownership.markers(demo))
            except ExecutionTargetError as exc:
                if '51994' not in str(exc) or 'SETUP_STATE_WAS_CHANGED' not in str(exc):
                    raise RuntimeError('Setup-Oracle scheiterte am falschen Fehler') from exc
            else: raise RuntimeError('Schädigendes Setup wurde vom Oracle akzeptiert')
            run_sql(target,database=db,sql_text='UPDATE lab.OwnershipSetupSentinel SET Value=919;')


def config_snapshot(target: ExecutionTarget,demo: str) -> str:
    db=ownership.database(demo)
    output=run_sql(target,database='master',sql_text=f"SET NOCOUNT ON; SELECT database_id,recovery_model_desc,is_auto_close_on,is_auto_shrink_on,page_verify_option,compatibility_level FROM sys.databases WHERE name=N'{db}';")
    rows=[line.strip().split('|') for line in output.splitlines() if line.strip()]
    if len(rows)!=1 or len(rows[0])!=6: raise RuntimeError('Vollständiger Konfigurationsrecord fehlt')
    return '|'.join(rows[0])


def positive(target: ExecutionTarget,demo: str,source: str,major: int) -> None:
    output=run_sql(target,database='master',sql_text=ownership.render(source,demo))
    rows=[line.strip().split('|') for line in output.splitlines()]
    if sum(row[:5]==['1','SETUP','SUMMARY','PASS','OK'] for row in rows)!=1:
        raise RuntimeError('Eindeutiger positiver Setuprecord fehlt')
    if config_snapshot(target,demo).split('|')[1:]!=['SIMPLE','0','0','2',str(major*10)]:
        raise RuntimeError('Positive Setupkonfiguration fehlt')
    db=ownership.database(demo)
    checks=[]
    for name,value in ownership.markers(demo).items():
        checks.append(f"IF NOT EXISTS(SELECT 1 FROM [{db}].sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND name={ownership.literal('SQLPERF.'+name)} AND CONVERT(nvarchar(max),value) COLLATE Latin1_General_100_BIN2={ownership.literal(value)} AND DATALENGTH(CONVERT(nvarchar(max),value))=DATALENGTH({ownership.literal(value)})) THROW 51996,'POSITIVE_MARKER_MISSING',1;")
    verified=run_sql(target,database='master',sql_text='SET NOCOUNT ON;\n'+'\n'.join(checks)+"\nSELECT 'MARKERS_VERIFIED';")
    if verified.split()!=['MARKERS_VERIFIED']: raise RuntimeError('Positiver Markernachweis fehlt')


def finish_fixture(target: ExecutionTarget,demo: str) -> None:
    cleanup=ownership.source_path(demo).read_text(encoding='utf-8-sig')
    for _ in range(2):
        run_sql(target,database='master',sql_text=ownership.render(cleanup,demo))
        ownership.absent(target,demo)


def run_probes(target: ExecutionTarget,major: int,*,demos: tuple[str,...]=DEMO_IDS,old_root: Path|None=None,repetitions: int=2) -> int:
    if target.kind!='docker' or not target.container: raise RuntimeError('Eigene Dockerinstanz erforderlich')
    if major not in (15,16,17) or not demos or len(demos)!=len(set(demos)) or any(d not in DEMO_IDS for d in demos):
        raise ValueError('Bekannte Version und eindeutige Demomenge erforderlich')
    sources={d:source_path(d).read_text(encoding='utf-8-sig') for d in demos}
    phases={d:control_phase(s) for d,s in sources.items()}
    count=0
    for demo in demos:
        if major<MIN_MAJOR.get(demo,15):
            print(f'SETUP_OWNERSHIP_SKIP|{demo}|SKIP_VERSION|major={major}',flush=True)
            continue
        source=sources[demo]
        if old_root:
            fixture(target,demo)
            ownership.reset_markers(target,demo,{**ownership.markers(demo),'Project':'WRONG'})
            before=config_snapshot(target,demo)
            old=source_path(demo,old_root).read_text(encoding='utf-8-sig')
            file_rejection(target,demo,old)
            if before==config_snapshot(target,demo): raise RuntimeError('Alte Konfigurationsverletzung nicht reproduziert')
            ownership.reset_markers(target,demo,ownership.markers(demo))
            finish_fixture(target,demo)
            print(f'SETUP_OWNERSHIP_OLD|{demo}|ACTUAL_WRITE_BEFORE_REJECTION',flush=True)
        for repetition in range(1,repetitions+1):
            fixture(target,demo)
            verify_oracles(target,demo)
            cases=ownership.negative_cases(demo)
            for label,values,obj,wrong in cases:
                if label=='ALL_MISSING':
                    run_sql(target,database='master',sql_text=initial_config(demo))
                    ownership.reset_markers(target,demo,values,obj)
                    before=snapshot(target,demo)
                    file_rejection(target,demo,source)
                    if before!=snapshot(target,demo): raise RuntimeError('Gesamtdatei änderte Zustand vor Eigentumsnachweis')
                else: batch_rejection(target,demo,phases[demo],values,obj,wrong)
                count+=1
            batch_rejection(target,demo,phases[demo],{**ownership.markers(demo),'Project':'WRONG'},auto_close=True)
            count+=1
            ownership.reset_markers(target,demo,ownership.markers(demo))
            before=snapshot(target,demo,identity_only=True)
            for _ in range(2):
                positive(target,demo,source,major)
                if before!=snapshot(target,demo,identity_only=True): raise RuntimeError('Positive Wiederverwendung änderte Identität, Marker oder Prüfzeile')
            finish_fixture(target,demo)
            positive(target,demo,source,major)
            finish_fixture(target,demo)
            print(f'SETUP_OWNERSHIP_FIXED|{demo}|{repetition}|PASS|negative={len(cases)+1}',flush=True)
    return count


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container',required=True)
    parser.add_argument('--expected-major',type=int,required=True)
    parser.add_argument('--confirm-disposable',action='store_true',required=True)
    parser.add_argument('--old-root',type=Path)
    parser.add_argument('--demos',nargs='+',choices=DEMO_IDS,default=DEMO_IDS)
    args=parser.parse_args()
    target=docker_target(container=args.container)
    major=verify_engine(target,expected_major=args.expected_major)
    count=run_probes(target,major,demos=tuple(args.demos),old_root=args.old_root)
    supported=sum(major>=MIN_MAJOR.get(d,15) for d in args.demos)
    print(f'SETUP_OWNERSHIP_COMPLETE|PASS|demos={supported}|negative={count}|version={major}',flush=True)


if __name__=='__main__': main()
