#!/usr/bin/env python3
"""Echte Cleanup-Gegenproben ausschließlich in einer eigenen Dockerinstanz."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

from execution_target import ExecutionTarget, ExecutionTargetError, docker_target, run_sql, verify_engine

ROOT = Path(__file__).resolve().parents[2]
DEMO_IDS = (
    'STL-008', 'STL-009', 'OPT-002', 'OPT-003', 'OPT-005', 'OPT-009',
    'OPT-010', 'OPT-013', 'OPT-015', 'OPT-016', 'OPT-017', 'IDX-006',
    'IDX-010', 'CON-009', 'QRY-004', 'QRY-013', 'RES-007', 'CON-004',
    'CON-006', 'DGN-003', 'DGN-005', 'DGN-007',
)
PROPERTIES = ('Project', 'ContractVersion', 'DemoId', 'RunToken')


def literal(value: str) -> str:
    return "N'" + value.replace("'", "''") + "'"


def markers(demo: str) -> dict[str, str]:
    return dict(zip(PROPERTIES, ('SQL_PerformanceSchulung', '1.0', demo, 'LOCAL')))


def database(demo: str) -> str:
    return 'SQLPERF_LAB_' + demo.replace('-', '') + '_LOCAL'


def source_path(demo: str, root: Path = ROOT) -> Path:
    matches = list((root / 'Demos').glob(f'**/{demo}_*/90_Cleanup.sql'))
    if len(matches) != 1:
        raise RuntimeError(f'{demo}: eindeutige Cleanupquelle fehlt')
    return matches[0]


def render(source: str, demo: str, *, wrong_target: bool = False) -> str:
    values = {'DemoId': demo, 'RunToken': 'LOCAL',
              'TargetDatabase': database(demo) + ('X' if wrong_target else '')}
    for name, value in values.items():
        source = source.replace('$(' + name + ')', value)
    if re.search(r'\$\([^)]+\)', source):
        raise RuntimeError('Unaufgelöster sqlcmd-Platzhalter')
    return source


def negative_cases(demo: str) -> list[tuple[str, dict[str, str | None], bool, bool]]:
    good = markers(demo)
    cases: list[tuple[str, dict[str, str | None], bool, bool]] = [('ALL_MISSING', {}, False, False)]
    for name, value in good.items():
        cases.append(('MISSING_' + name, {k: v for k, v in good.items() if k != name}, False, False))
        variants = {'NULL': None, 'WRONG': 'WRONG', 'EMPTY': '', 'SPACE': value + ' ', 'LONG': value + 'X' * 200}
        if value != value.lower():
            variants['CASE'] = value.lower()
        for kind, replacement in variants.items():
            cases.append((kind + '_' + name, {**good, name: replacement}, False, False))
    cases.extend([('OBJECT_ONLY', good, True, False), ('WRONG_TARGET', good, False, True)])
    return cases


def absent(target: ExecutionTarget, demo: str) -> None:
    output = run_sql(target, database='master', sql_text=(
        f"SET NOCOUNT ON; IF DB_ID({literal(database(demo))}) IS NOT NULL THROW 51004,'FIXTURE_NOT_ABSENT',1; SELECT 'ABSENT';"))
    if output.split() != ['ABSENT']:
        raise RuntimeError('Unabhängiger Absenznachweis fehlt')


def reset_markers(target: ExecutionTarget, demo: str, values: dict[str, str | None], object_only: bool = False) -> None:
    scope = ",@level0type=N'SCHEMA',@level0name=N'dbo',@level1type=N'TABLE',@level1name=N'OwnershipProbe'"
    statements = []
    for name in PROPERTIES:
        prop = literal('SQLPERF.' + name)
        statements.append(f"IF EXISTS(SELECT 1 FROM sys.extended_properties WHERE class=0 AND name={prop}) EXEC sys.sp_dropextendedproperty @name={prop};")
        statements.append(f"IF EXISTS(SELECT 1 FROM sys.extended_properties WHERE class=1 AND major_id=OBJECT_ID(N'dbo.OwnershipProbe') AND name={prop}) EXEC sys.sp_dropextendedproperty @name={prop}{scope};")
    for name, value in values.items():
        statements.append(f"EXEC sys.sp_addextendedproperty @name={literal('SQLPERF.' + name)},@value={'NULL' if value is None else literal(value)}{scope if object_only else ''};")
    run_sql(target, database=database(demo), sql_text='\n'.join(statements))


def fixture(target: ExecutionTarget, demo: str) -> None:
    absent(target, demo)
    run_sql(target, database='master', sql_text=f'CREATE DATABASE [{database(demo)}];')
    run_sql(target, database=database(demo), sql_text="""
CREATE TABLE dbo.OwnershipProbe(Value int NOT NULL);
INSERT dbo.OwnershipProbe VALUES(73);
""")
    if demo == 'DGN-007':
        run_sql(target, database=database(demo), sql_text="""
CREATE SCHEMA lab;
GO
CREATE PROCEDURE lab.OwnershipRestore AS SELECT 2 AS Value;
GO
CREATE TABLE lab.Dgn007ReferenceState(StateId int, OriginalProcedureDefinition nvarchar(max), OriginalChecksum int, MitigationApplied bit, T2Utc datetime2, XeStartedUtc datetime2);
INSERT lab.Dgn007ReferenceState VALUES(1,N'CREATE PROCEDURE lab.OwnershipRestore AS SELECT 1 AS Value;',31,1,'20260101','20260101');
CREATE TABLE lab.IncidentQueryStoreProfile(IncidentPhase nvarchar(30));
INSERT lab.IncidentQueryStoreProfile VALUES(N'T2_COMPARISON');
CREATE TABLE lab.IncidentState(IncidentPhase nvarchar(30));
INSERT lab.IncidentState VALUES(N'T2_COMPARISON');
""")
    reset_markers(target, demo, markers(demo))


def xe_name(demo: str) -> str:
    return 'SQLPERF_' + demo.replace('-', '') + '_LOCAL'


def create_xe(target: ExecutionTarget, demo: str, *, running: bool) -> None:
    name = xe_name(demo)
    run_sql(target, database='master', sql_text=f"""
IF EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=N'{name}') THROW 51004,'XE_FIXTURE_ALREADY_EXISTS',1;
CREATE EVENT SESSION [{name}] ON SERVER ADD EVENT sqlserver.error_reported ADD TARGET package0.ring_buffer WITH(STARTUP_STATE=OFF);
""" + (f'ALTER EVENT SESSION [{name}] ON SERVER STATE=START;' if running else ''))


def snapshot(target: ExecutionTarget, demo: str) -> str:
    name = database(demo)
    output = run_sql(target, database='master', sql_text=f"""
SET NOCOUNT ON;
IF DB_ID(N'{name}') IS NULL THROW 51004,'FIXTURE_WAS_REMOVED',1;
SELECT N'DATABASE',database_id,state_desc,user_access_desc,is_read_only,recovery_model_desc,is_auto_close_on,is_auto_shrink_on,page_verify_option,compatibility_level FROM sys.databases WHERE name=N'{name}';
SELECT N'SENTINEL',Value FROM [{name}].dbo.OwnershipProbe;
SELECT N'COLUMN',object_id,column_id,name,user_type_id,max_length,is_nullable FROM [{name}].sys.columns WHERE object_id=OBJECT_ID(N'{name}.dbo.OwnershipProbe') ORDER BY column_id;
IF EXISTS(SELECT 1 FROM [{name}].sys.extended_properties WHERE DATALENGTH(CONVERT(nvarchar(max),value))>4000) THROW 51004,'MARKER_SNAPSHOT_TOO_WIDE',1;
SELECT N'MARKER',class,major_id,minor_id,name,SQL_VARIANT_PROPERTY(value,'BaseType'),CONVERT(varchar(8000),CONVERT(varbinary(max),CONVERT(nvarchar(max),value)),2) FROM [{name}].sys.extended_properties ORDER BY class,major_id,minor_id,name;
SELECT N'XE',event_session_id,name,event_retention_mode,max_dispatch_latency,max_memory,max_event_size,memory_partition_mode,track_causality,startup_state FROM sys.server_event_sessions WHERE name=N'{xe_name(demo)}';
SELECT N'XE_RUNNING',name,CONVERT(varchar(max),address,2) FROM sys.dm_xe_sessions WHERE name=N'{xe_name(demo)}';
SELECT N'XE_EVENT',e.event_session_id,e.event_id,e.name,e.package,e.predicate FROM sys.server_event_session_events e JOIN sys.server_event_sessions s ON s.event_session_id=e.event_session_id WHERE s.name=N'{xe_name(demo)}';
SELECT N'XE_TARGET',t.event_session_id,t.target_id,t.name,t.package FROM sys.server_event_session_targets t JOIN sys.server_event_sessions s ON s.event_session_id=t.event_session_id WHERE s.name=N'{xe_name(demo)}';
""")
    if demo == 'DGN-007':
        output += run_sql(target, database=name, sql_text="""
SELECT N'PROCEDURE',CONVERT(varchar(8000),CONVERT(varbinary(max),OBJECT_DEFINITION(OBJECT_ID(N'lab.OwnershipRestore'))),2);
SELECT N'REFERENCE',StateId,CONVERT(varchar(8000),CONVERT(varbinary(max),OriginalProcedureDefinition),2),OriginalChecksum,MitigationApplied,T2Utc,XeStartedUtc FROM lab.Dgn007ReferenceState;
SELECT N'PROFILE',IncidentPhase FROM lab.IncidentQueryStoreProfile;
SELECT N'STATE',IncidentPhase FROM lab.IncidentState;
""")
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if lines.count('SENTINEL|73') != 1 or sum(line.startswith('DATABASE|') for line in lines) != 1:
        raise RuntimeError('Vollständiger Fixture-Snapshot fehlt')
    return '\n'.join(lines)


def assert_restored(target: ExecutionTarget, demo: str) -> None:
    expected = 'CREATE PROCEDURE lab.OwnershipRestore AS SELECT 1 AS Value;'
    output = run_sql(target, database=database(demo), sql_text=f"""
SET NOCOUNT ON;
IF (SELECT COUNT(*) FROM lab.Dgn007ReferenceState)<>1
 OR NOT EXISTS(SELECT 1 FROM lab.Dgn007ReferenceState WHERE StateId=1 AND OriginalProcedureDefinition IS NULL AND OriginalChecksum IS NULL AND MitigationApplied=0 AND T2Utc IS NULL AND XeStartedUtc IS NULL)
 OR OBJECT_ID(N'lab.OwnershipRestore',N'P') IS NULL
 OR OBJECT_DEFINITION(OBJECT_ID(N'lab.OwnershipRestore')) IS NULL
 OR CONVERT(varbinary(max),OBJECT_DEFINITION(OBJECT_ID(N'lab.OwnershipRestore')))<>CONVERT(varbinary(max),{literal(expected)})
 OR EXISTS(SELECT 1 FROM lab.IncidentState)
 OR EXISTS(SELECT 1 FROM lab.IncidentQueryStoreProfile)
 OR EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=N'{xe_name(demo)}')
 OR EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=N'{xe_name(demo)}')
 THROW 51004,'RESTORE_NOT_COMPLETE',1;
SELECT 'RESTORE_COMPLETE';
""")
    if output.split() != ['RESTORE_COMPLETE']:
        raise RuntimeError('Vollständiger Rückfallnachweis fehlt')


def rejection(target: ExecutionTarget, demo: str, source: str, *, wrong_target: bool = False) -> None:
    code = (51011 if demo == 'DGN-007' else 51000) if wrong_target else (51013 if demo == 'DGN-007' else 51004)
    try:
        run_sql(target, database='master' if wrong_target or demo != 'DGN-007' else database(demo),
                sql_text=render(source, demo, wrong_target=wrong_target) + "\nGO\nTHROW 51999,'UNREACHED_BATCH',1;\n")
    except ExecutionTargetError as exc:
        if re.search(rf'\b{code}\b', str(exc)) and 'UNREACHED_BATCH' not in str(exc):
            return
        raise RuntimeError(f'{demo}: falscher Schutzfehler oder Batch nach Fehler ausgeführt') from exc
    raise RuntimeError(f'{demo}: Eigentumsablehnung fehlt')


def remove_fixture(target: ExecutionTarget, demo: str) -> None:
    # Nur die zuvor selbst angelegte und jetzt vollständig markierte Fixture.
    checks = []
    for name, expected in markers(demo).items():
        checks.append(f"IF NOT EXISTS(SELECT 1 FROM [{database(demo)}].sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND name={literal('SQLPERF.'+name)} AND CONVERT(nvarchar(max),value) COLLATE Latin1_General_100_BIN2={literal(expected)} AND DATALENGTH(CONVERT(nvarchar(max),value))=DATALENGTH({literal(expected)})) THROW 51004,'FIXTURE_OWNERSHIP_MISSING',1;")
    run_sql(target, database='master', sql_text='\n'.join(checks) + f'\nALTER DATABASE [{database(demo)}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [{database(demo)}];')
    absent(target, demo)



def state_expression(demo: str) -> str:
    """Ungekürzte strukturierte Katalog-/Datenrecords als unabhängiges Oracle."""
    db=database(demo)
    xe=xe_name(demo)
    parts=[
        ("DatabaseState",f"SELECT database_id,state_desc,user_access_desc,is_read_only,recovery_model_desc,is_auto_close_on,is_auto_shrink_on,page_verify_option,compatibility_level FROM sys.databases WHERE name=N'{db}'"),
        ("Sentinel",f"SELECT * FROM [{db}].dbo.OwnershipProbe ORDER BY Value"),
        ("Columns",f"SELECT object_id,column_id,name,user_type_id,max_length,is_nullable FROM [{db}].sys.columns WHERE object_id=OBJECT_ID(N'{db}.dbo.OwnershipProbe') ORDER BY column_id"),
        ("Markers",f"SELECT class,major_id,minor_id,name,CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value,'BaseType')) AS BaseType,CONVERT(varchar(max),CONVERT(varbinary(max),CONVERT(nvarchar(max),value)),2) AS FullBytes FROM [{db}].sys.extended_properties ORDER BY class,major_id,minor_id,name"),
        ("XeDefinition",f"SELECT * FROM sys.server_event_sessions WHERE name=N'{xe}' ORDER BY event_session_id"),
        ("XeRuntime",f"SELECT name,CONVERT(varchar(max),address,2) AS FullAddress FROM sys.dm_xe_sessions WHERE name=N'{xe}' ORDER BY name"),
        ("XeEvents",f"SELECT e.* FROM sys.server_event_session_events e JOIN sys.server_event_sessions s ON s.event_session_id=e.event_session_id WHERE s.name=N'{xe}' ORDER BY e.event_id"),
        ("XeTargets",f"SELECT t.* FROM sys.server_event_session_targets t JOIN sys.server_event_sessions s ON s.event_session_id=t.event_session_id WHERE s.name=N'{xe}' ORDER BY t.target_id"),
        ("XeFields",f"SELECT f.event_session_id,f.object_id,f.name,CONVERT(varchar(max),CONVERT(varbinary(max),CONVERT(nvarchar(max),f.value)),2) AS FullBytes FROM sys.server_event_session_fields f JOIN sys.server_event_sessions s ON s.event_session_id=f.event_session_id WHERE s.name=N'{xe}' ORDER BY f.object_id,f.name"),
    ]
    if demo=='DGN-007':
        parts.extend([
            ("Procedure",f"SELECT CONVERT(varchar(max),CONVERT(varbinary(max),definition),2) AS FullBytes FROM [{db}].sys.sql_modules WHERE object_id=OBJECT_ID(N'{db}.lab.OwnershipRestore')"),
            ("Reference",f"SELECT * FROM [{db}].lab.Dgn007ReferenceState ORDER BY StateId"),
            ("Profile",f"SELECT * FROM [{db}].lab.IncidentQueryStoreProfile ORDER BY IncidentPhase"),
            ("State",f"SELECT * FROM [{db}].lab.IncidentState ORDER BY IncidentPhase"),
        ])
    projection=','.join(f"({query} FOR XML RAW,TYPE) AS [{section}]" for section,query in parts)
    return f"CONVERT(varbinary(max),CONVERT(nvarchar(max),(SELECT {projection} FOR XML PATH('Snapshot'),TYPE)))"


def marker_sql(demo: str, values: dict[str,str|None], object_only: bool) -> str:
    scope=",@level0type=N'SCHEMA',@level0name=N'dbo',@level1type=N'TABLE',@level1name=N'OwnershipProbe'"
    statements=[]
    for name in PROPERTIES:
        prop=literal('SQLPERF.'+name)
        statements.append(f"IF EXISTS(SELECT 1 FROM sys.extended_properties WHERE class=0 AND name={prop}) EXEC sys.sp_dropextendedproperty @name={prop};")
        statements.append(f"IF EXISTS(SELECT 1 FROM sys.extended_properties WHERE class=1 AND major_id=OBJECT_ID(N'dbo.OwnershipProbe') AND name={prop}) EXEC sys.sp_dropextendedproperty @name={prop}{scope};")
    for name,value in values.items():
        statements.append(f"EXEC sys.sp_addextendedproperty @name={literal('SQLPERF.'+name)},@value={'NULL' if value is None else literal(value)}{scope if object_only else ''};")
    return f"EXEC sys.sp_executesql {literal('USE ['+database(demo)+'];'+''.join(statements))};"


def batch_rejection(target: ExecutionTarget,demo: str,source: str,label: str,values: dict[str,str|None],object_only: bool,wrong_target: bool) -> None:
    rendered=render(source,demo,wrong_target=wrong_target)
    commands=re.findall(r'(?im)^[\t ]*GO\b[^\r\n]*',rendered)
    if len(commands)>1 or any(not re.fullmatch(r'[\t ]*GO[\t ]*',command,re.I) for command in commands):
        raise RuntimeError('Unbekannter GO-Befehl; konservative Einzelprüfung erforderlich')
    batches=re.split(r'(?im)^\s*GO\s*$',rendered)
    if len(batches)>2 or (len(batches)==2 and not re.fullmatch(r'\s*(?:/\*.*?\*/\s*)?USE\s+\[master\];\s*',batches[0],re.S|re.I)):
        raise RuntimeError('Unbekannte Batchform; konservative Einzelprüfung erforderlich')
    # Der einzige erlaubte Trenner steht zwischen USE master und dem eigentlichen
    # Cleanup. Diese beiden vollständigen Batchtexte sind zusammen dynamisch gültig.
    rendered='\n'.join(batches)
    code=(51011 if demo=='DGN-007' else 51000) if wrong_target else (51013 if demo=='DGN-007' else 51004)
    expression=state_expression(demo)
    output=run_sql(target,database='master' if wrong_target or demo!='DGN-007' else database(demo),sql_text=f"""
SET NOCOUNT ON;
{marker_sql(demo,values,object_only)}
IF DB_ID(N'{database(demo)}') IS NULL THROW 51991,'FIXTURE_MISSING_BEFORE',1;
IF (SELECT COUNT(*) FROM [{database(demo)}].dbo.OwnershipProbe WHERE Value=73)<>1 THROW 51991,'SENTINEL_MISSING_BEFORE',1;
DECLARE @Before varbinary(max)={expression},@After varbinary(max),@ActualError int=NULL;
BEGIN TRY
 EXEC sys.sp_executesql {literal(rendered)};
END TRY
BEGIN CATCH
 SET @ActualError=ERROR_NUMBER();
END CATCH;
IF @ActualError IS NULL OR @ActualError<>{code} THROW 51992,'SPECIFIC_REJECTION_MISSING',1;
IF DB_ID(N'{database(demo)}') IS NULL THROW 51993,'DATABASE_WAS_REMOVED',1;
SET @After={expression};
IF @Before IS NULL OR @After IS NULL OR DATALENGTH(@Before)<>DATALENGTH(@After) OR @Before<>@After THROW 51994,'STATE_WAS_CHANGED',1;
SELECT 'PRESERVED';
""")
    if output.split()!=['PRESERVED']:
        raise RuntimeError(f'{demo}/{label}: vollständiges Erhaltungsresultat fehlt')


def verify_batch_oracle(target: ExecutionTarget, demo: str) -> None:
    expression=state_expression(demo)
    output=run_sql(target,database='master',sql_text=f"""
SET NOCOUNT ON;
{marker_sql(demo,{'Project':'X'*128+'A'},False)}
DECLARE @First varbinary(max)={expression},@Second varbinary(max);
{marker_sql(demo,{'Project':'X'*128+'B'},False)}
SET @Second={expression};
IF @First IS NULL OR @Second IS NULL OR @First=@Second THROW 51995,'BATCH_ORACLE_CROPPED',1;
SELECT 'ORACLE_COMPLETE';
""")
    if output.split()!=['ORACLE_COMPLETE']:
        raise RuntimeError('Vollständige Batch-Snapshot-Gegenprobe fehlt')
    if demo=='OPT-002':
        try:
            batch_rejection(target,demo,f"UPDATE [{database(demo)}].dbo.OwnershipProbe SET Value=74; THROW 51004,'SYNTHETIC_BAD_CLEANUP',1;",'ORACLE_MUTATION',markers(demo),False,False)
        except ExecutionTargetError as exc:
            if '51994' not in str(exc) or 'STATE_WAS_CHANGED' not in str(exc):
                raise RuntimeError('Oracle-Gegenprobe scheiterte am falschen Fehler') from exc
        else:
            raise RuntimeError('Beschädigender Cleanup wurde vom Oracle akzeptiert')
        run_sql(target,database=database(demo),sql_text='UPDATE dbo.OwnershipProbe SET Value=73;')
    if demo in ('DGN-005','DGN-007'):
        # Eine unveränderte create_time variierte in der lokalen Gegenprobe.
        # Verglichen werden vollständige Definition, Name, Adresse und Laufzustand.
        running=run_sql(target,database='master',sql_text=f"SET NOCOUNT ON; SELECT COUNT(*) FROM sys.dm_xe_sessions WHERE name=N'{xe_name(demo)}';").strip()
        if running not in ('0','1'): raise RuntimeError('XE-Laufzustand unbestimmt')
        mutation='STOP' if running=='1' else 'START'
        restore='START' if running=='1' else 'STOP'
        error=51013 if demo=='DGN-007' else 51004
        try:
            batch_rejection(target,demo,f"ALTER EVENT SESSION [{xe_name(demo)}] ON SERVER STATE={mutation}; THROW {error},'SYNTHETIC_BAD_XE_CLEANUP',1;",'ORACLE_XE_MUTATION',markers(demo),False,False)
        except ExecutionTargetError as exc:
            if '51994' not in str(exc) or 'STATE_WAS_CHANGED' not in str(exc):
                raise RuntimeError('XE-Oracle-Gegenprobe scheiterte am falschen Fehler') from exc
        else:
            raise RuntimeError('Veränderter XE-Laufzustand wurde vom Oracle akzeptiert')
        run_sql(target,database='master',sql_text=f'ALTER EVENT SESSION [{xe_name(demo)}] ON SERVER STATE={restore};')


def run_probes(target: ExecutionTarget, *, old_root: Path | None = None, repetitions: int = 2, demos: tuple[str, ...] = DEMO_IDS) -> int:
    if target.kind != 'docker' or not target.container:
        raise RuntimeError('Eigene wegwerfbare Dockerinstanz erforderlich')
    if not demos or len(demos)!=len(set(demos)) or any(demo not in DEMO_IDS for demo in demos):
        raise ValueError('Bekannte eindeutige Demomenge erforderlich')
    count = 0
    for demo in demos:
        source = source_path(demo).read_text(encoding='utf-8-sig')
        if old_root:
            fixture(target, demo)
            reset_markers(target, demo, {})
            if demo in ('DGN-005', 'DGN-007'):
                create_xe(target, demo, running=True)
            old = source_path(demo, old_root).read_text(encoding='utf-8-sig')
            run_sql(target, database=database(demo) if demo == 'DGN-007' else 'master', sql_text=render(old, demo))
            if demo == 'DGN-007':
                assert_restored(target, demo)
                reset_markers(target, demo, markers(demo))
                remove_fixture(target, demo)
            else:
                absent(target, demo)
            print(f'OWNERSHIP_OLD|{demo}|ACTUAL_VIOLATION', flush=True)
        for repetition in range(1, repetitions + 1):
            fixture(target, demo)
            if demo in ('DGN-005', 'DGN-007'):
                create_xe(target, demo, running=repetition == 1)
            # Oracle-Gegenprobe: Unterschiede hinter 128 Zeichen bleiben sichtbar.
            reset_markers(target, demo, {'Project': 'X' * 128 + 'A'})
            first = snapshot(target, demo)
            reset_markers(target, demo, {'Project': 'X' * 128 + 'B'})
            if first == snapshot(target, demo):
                raise RuntimeError('Gekürztes Marker-Oracle')
            verify_batch_oracle(target,demo)
            for label, values, object_only, wrong_target in negative_cases(demo):
                if label=='ALL_MISSING':
                    # Echte vollständige sqlcmd-Dateiform inklusive GO und -b:
                    # der nachfolgende Fehlerbatch muss unerreicht bleiben.
                    reset_markers(target, demo, values, object_only)
                    before=snapshot(target,demo)
                    rejection(target,demo,source,wrong_target=wrong_target)
                    if before!=snapshot(target,demo):
                        raise RuntimeError(f'{demo}/{label}: Zustand bei Ablehnung verändert')
                else:
                    batch_rejection(target,demo,source,label,values,object_only,wrong_target)
                count += 1
            reset_markers(target, demo, markers(demo))
            for _ in range(2):
                run_sql(target, database=database(demo) if demo == 'DGN-007' else 'master', sql_text=render(source, demo))
                if demo != 'DGN-007':
                    absent(target, demo)
            if demo == 'DGN-007':
                assert_restored(target, demo)
                remove_fixture(target, demo)
            if demo in ('DGN-005', 'DGN-007'):
                run_sql(target, database='master', sql_text=f"IF EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=N'{xe_name(demo)}') THROW 51004,'XE_NOT_REMOVED',1;")
            print(f'OWNERSHIP_FIXED|{demo}|{repetition}|PASS|negative={len(negative_cases(demo))}', flush=True)
        if demo == 'DGN-005':
            create_xe(target, demo, running=True)
            before = run_sql(target, database='master', sql_text=f"SET NOCOUNT ON; SELECT event_session_id,name FROM sys.server_event_sessions WHERE name=N'{xe_name(demo)}'; SELECT name FROM sys.dm_xe_sessions WHERE name=N'{xe_name(demo)}';")
            rejection(target, demo, source)
            after = run_sql(target, database='master', sql_text=f"SET NOCOUNT ON; SELECT event_session_id,name FROM sys.server_event_sessions WHERE name=N'{xe_name(demo)}'; SELECT name FROM sys.dm_xe_sessions WHERE name=N'{xe_name(demo)}';")
            if before != after or len(before.splitlines()) != 2:
                raise RuntimeError('Verwaiste Ereignissession bei Ablehnung verändert')
            # Dieser eigene synthetische Serverbestand ist durch den Instanzbesitz begrenzt.
            run_sql(target, database='master', sql_text=f'ALTER EVENT SESSION [{xe_name(demo)}] ON SERVER STATE=STOP; DROP EVENT SESSION [{xe_name(demo)}] ON SERVER;')
            absent(target, demo)
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True)
    parser.add_argument('--expected-major', type=int, required=True)
    parser.add_argument('--confirm-disposable', action='store_true', required=True)
    parser.add_argument('--old-root', type=Path)
    parser.add_argument('--demos', nargs='+', choices=DEMO_IDS, default=DEMO_IDS)
    args = parser.parse_args()
    target = docker_target(container=args.container)
    verify_engine(target, expected_major=args.expected_major)
    count = run_probes(target, old_root=args.old_root, demos=tuple(args.demos))
    print(f'OWNERSHIP_COMPLETE|PASS|demos={len(args.demos)}|negative={count}', flush=True)


if __name__ == '__main__':
    main()
