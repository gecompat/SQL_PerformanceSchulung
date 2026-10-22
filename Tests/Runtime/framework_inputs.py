#!/usr/bin/env python3
"""Vollständige Frameworkeingaben vor Kürzung im eigenen SQL-Container prüfen."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

import framework_ownership as fwk
import cleanup_ownership as ownership
from execution_target import ExecutionTarget,ExecutionTargetError,docker_target,run_sql,verify_engine


def cases(action: str) -> tuple[tuple[str,str,str|None],...]:
    return (
        ('DEMO_SUFFIX','DemoId','QRY-001X'),
        ('DEMO_LONG_SUFFIX','DemoId','QRY-001'+' '*5000+'X'),
        ('DEMO_TRAILING_SPACE','DemoId','QRY-001 '),
        ('DEMO_LOWER','DemoId','qry-001'),
        ('DEMO_FULLWIDTH','DemoId','ＱＲＹ-001'),
        ('DEMO_NULL','DemoId',None),
        ('ACTION_SUFFIX','Action',action+' '*(10-len(action))+'X'),
        ('ACTION_LONG_SUFFIX','Action',action+' '*5000+'X'),
        ('ACTION_FULLWIDTH','Action',''.join(chr(ord(c)+0xFEE0) for c in action)),
        ('ACTION_NULL','Action',None),
        ('ACTION_EMPTY','Action',''),
        ('RUN_SUFFIX','RunToken','LOCAL'+' '*11+'X'),
        ('RUN_LONG_SUFFIX','RunToken','LOCAL'+' '*5000+'X'),
        ('RUN_FULLWIDTH','RunToken','ＬＯＣＡＬ'),
        ('RUN_NONASCII','RunToken','LOCAı'),
        ('RUN_NULL','RunToken',None),
        ('RUN_EMPTY','RunToken',''),
        ('RUN_LENGTH17','RunToken','A'*17),
    )


def render(source: str,action: str,major: int,values: dict[str,str|None]) -> str:
    if set(values)-{'Action','DemoId','RunToken'}:raise ValueError('Unbekannter Rohparameter')
    return fwk.matrix._replace_declarations(fwk.render(source,action,major),{
        key:'NULL' if value is None else ownership.literal(value) for key,value in values.items()
    })


def state_expression() -> str:
    # Die vollständige Fixture und das Inventar aller Benutzerdatenbanken:
    # Auch eine irrtümlich unter anderem Namen erzeugte Datenbank muss auffallen.
    return f"""CONVERT(varbinary(max),(
 SELECT {ownership.state_expression(fwk.DEMO)} AS Fixture,
  (SELECT database_id,name,create_date,state_desc,user_access_desc,is_read_only,
          compatibility_level,recovery_model_desc,is_auto_close_on,is_auto_shrink_on
   FROM master.sys.databases WHERE database_id>4 ORDER BY database_id
   FOR XML PATH('database'),ROOT('inventory'),TYPE) AS Inventory
 FOR XML PATH('InputState'),BINARY BASE64,TYPE))"""


def snapshot(target: ExecutionTarget) -> str:
    return fwk.snapshot(target,expression=state_expression())


def require_preserved(output: str,check: str) -> None:
    lines=[s.strip() for s in output.splitlines() if s.strip()]
    if not lines or lines[-1]!='PRESERVED' or lines.count('PRESERVED')!=1:
        raise RuntimeError('Eindeutiger Eingabe-Erhaltungsrecord fehlt')
    records=[]
    for line in lines[:-1]:
        # Die ersten fünf typisierten Felder sind das Oracle. Freie Diagnosefelder
        # bleiben ungeteilt erhalten und dürfen selbst Pipezeichen enthalten.
        match=re.fullmatch(r'(\d+)\|(LIFECYCLE|SAFETY)\|([A-Z0-9_]+)\|(PASS|FAIL|SKIP|WARN)\|([A-Z0-9_]+)\|(.*)',line)
        if not match or match[6].count('|')<2:raise RuntimeError('Unbekannter Eingaberecord: '+repr(line[:300]))
        records.append(match.groups())
    for name in (check,'DATABASE_NAME','SUMMARY'):
        found=[r for r in records if r[1:3]==('LIFECYCLE',name)]
        if len(found)!=1 or found[0][3:5]!=('FAIL','FAIL_CONTRACT'):
            raise RuntimeError('Spezifischer Eingabe-Vertragsfehler fehlt')
    for record in records:
        if record[1]=='SAFETY':
            if record[2] not in ('LAB_CONFIRMATION','DROP_CONFIRMATION') or record[3:5]!=('PASS','OK'):
                raise RuntimeError('Unbekannter oder fehlgeschlagener Sicherheitsrecord')
        elif (record[3:5]!=('PASS','OK')
                and not (record[2] in (check,'DATABASE_NAME','SUMMARY') and record[3:5]==('FAIL','FAIL_CONTRACT'))):
            raise RuntimeError('Unerwarteter Teilbefund statt Eingabeablehnung')


def reject_batch(target: ExecutionTarget,phase: str,check: str) -> None:
    if re.search(r'(?im)^[\t ]*GO\b',phase):raise RuntimeError('Ungeprüfter Eingabebatch')
    expression=state_expression();db=ownership.database(fwk.DEMO)
    output=run_sql(target,database='master',sql_text=f"""
SET NOCOUNT ON;
IF DB_ID(N'{db}') IS NULL THROW 51991,'INPUT_FIXTURE_MISSING',1;
DECLARE @Before varbinary(max)={expression},@After varbinary(max),@ActualError int=NULL;
BEGIN TRY EXEC sys.sp_executesql {ownership.literal(phase)}; END TRY
BEGIN CATCH SET @ActualError=ERROR_NUMBER(); END CATCH;
IF @ActualError IS NULL OR @ActualError<>51000 THROW 51992,'SPECIFIC_INPUT_REJECTION_MISSING',1;
IF DB_ID(N'{db}') IS NULL THROW 51993,'INPUT_FIXTURE_REMOVED',1;
SET @After={expression};
IF @Before IS NULL OR @After IS NULL OR DATALENGTH(@Before)<>DATALENGTH(@After) OR @Before<>@After
 THROW 51994,'INPUT_STATE_WAS_CHANGED',1;
SELECT 'PRESERVED';
""")
    require_preserved(output,check)


def reject_file(target: ExecutionTarget,text: str) -> None:
    before=snapshot(target)
    try:run_sql(target,database='master',sql_text=text+"\nGO\nTHROW 51999,'UNREACHED_BATCH',1;\n")
    except ExecutionTargetError as exc:
        if not re.search(r'\b51000\b',str(exc)) or 'UNREACHED_BATCH' in str(exc):
            raise RuntimeError('Falscher Eingabe-Dateifehler') from exc
    else:raise RuntimeError('Ungültige Gesamteingabe wurde akzeptiert')
    if before!=snapshot(target):raise RuntimeError('Gesamtdatei veränderte Zustand oder Inventar')


def verify_oracles(target: ExecutionTarget) -> None:
    db=ownership.database(fwk.DEMO);extra='SQLPERF_LAB_QRY001_UNEXPECTED'
    run_sql(target,database='master',sql_text=f"IF DB_ID(N'{extra}') IS NOT NULL THROW 51991,'EXTRA_FIXTURE_EXISTS',1;")
    original=snapshot(target)
    for mutation,repair in (
        (f'UPDATE [{db}].dbo.OwnershipProbe SET Value=72;',f'UPDATE [{db}].dbo.OwnershipProbe SET Value=73;'),
        (f'CREATE DATABASE [{extra}];',f'ALTER DATABASE [{extra}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [{extra}];'),
    ):
        try:reject_batch(target,mutation+" THROW 51000,'SYNTHETIC_CONTRACT',1;",'ACTION')
        except ExecutionTargetError as exc:
            if '51994' not in str(exc) or 'INPUT_STATE_WAS_CHANGED' not in str(exc):raise RuntimeError('Falsche Eingabe-Oraclegegenprobe') from exc
        else:raise RuntimeError('Schädigende Eingabegegenprobe wurde akzeptiert')
        run_sql(target,database='master',sql_text=repair)
        if original!=snapshot(target):raise RuntimeError('Oraclegegenprobe nicht vollständig restauriert')


def positive(target: ExecutionTarget,text: str,*,existing: bool=True) -> None:
    # Bereits gerenderte Rohwerte unverändert ausführen, nicht erneut kanonisieren.
    records=fwk.rows(run_sql(target,database='master',sql_text=text))
    if any(r[3:5]!=['PASS','OK'] for r in records):raise RuntimeError('Unerwarteter positiver Eingabebefund')
    summary=[r for r in records if r[2]=='SUMMARY']
    if len(summary)!=1 or summary[0][1:5]!=['LIFECYCLE','SUMMARY','PASS','OK']:raise RuntimeError('Positiver Eingabeabschluss fehlt')
    if existing:
        matched=[r for r in records if r[2]=='OWNERSHIP_MARKERS']
        if len(matched)!=1 or matched[0][1:5]!=['LIFECYCLE','OWNERSHIP_MARKERS','PASS','OK']:raise RuntimeError('Positives Eingabeeigentum fehlt')


def run_probes(target: ExecutionTarget,major: int,*,old_source: Path|None=None,repetitions: int=2) -> int:
    if target.kind!='docker' or not target.container or major not in (15,16,17) or repetitions!=2:
        raise ValueError('Eigener Container, bekannte Version und zwei Profile erforderlich')
    source=fwk.SOURCE.read_text(encoding='utf-8-sig');phase=fwk.control_batch(source);count=0
    if old_source:
        old=old_source.read_text(encoding='utf-8-sig');fwk.control_batch(old)
        for action in fwk.ACTIONS:
            for label,field,value in (cases(action)[0],cases(action)[6],cases(action)[11]):
                fwk.fixture(target,major);before=snapshot(target)
                output=run_sql(target,database='master',sql_text=render(old,action,major,{field:value}))
                records=fwk.rows(output)
                if any(r[3:5]!=['PASS','OK'] for r in records) or len([r for r in records if r[2]=='SUMMARY'])!=1:
                    raise RuntimeError('Alte Eingabe wurde nicht tatsächlich falsch akzeptiert')
                if action=='DROP':ownership.absent(target,fwk.DEMO)
                else:
                    if before!=snapshot(target):raise RuntimeError('Unerwartete alte Wiederverwendungsänderung')
                    fwk.finish(target,source,major)
                print(f'FRAMEWORK_INPUT_OLD|{action}|{field}|ACTUAL_FALSE_ACCEPTANCE',flush=True)
    for repetition in (1,2):
        for action in fwk.ACTIONS:
            fwk.fixture(target,major)
            if action=='CREATE':verify_oracles(target)
            for label,field,value in cases(action):
                check={'DemoId':'DEMO_ID','Action':'ACTION','RunToken':'RUN_TOKEN'}[field]
                if label in ('DEMO_SUFFIX','ACTION_SUFFIX','RUN_SUFFIX'):
                    reject_file(target,render(source,action,major,{field:value}))
                try:reject_batch(target,render(phase,action,major,{field:value}),check)
                except Exception as exc:raise RuntimeError(f'Eingabegegenprobe {action}/{repetition}/{label} fehlgeschlagen') from exc
                count+=1
            normalized=render(source,action,major,{'Action':' '+action.lower()+' ','RunToken':' local '})
            if action=='DROP':
                positive(target,normalized);ownership.absent(target,fwk.DEMO)
                fwk.reject_file(target,source,'DROP',major);ownership.absent(target,fwk.DEMO)
            else:
                before=snapshot(target)
                for _ in (1,2):
                    positive(target,normalized)
                    if before!=snapshot(target):raise RuntimeError('Normalisierte Eingabe veränderte Wiederverwendung')
                fwk.finish(target,source,major)
            print(f'FRAMEWORK_INPUT_FIXED|{action}|{repetition}|PASS|negative={len(cases(action))}',flush=True)
        # Auch normalisierte Neuanlage mit anschließendem echten Eigentums-Cleanup.
        positive(target,render(source,'CREATE',major,{'Action':' create ','RunToken':' local '}),existing=False)
        fwk.finish(target,source,major)
    return count


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container',required=True)
    parser.add_argument('--expected-major',type=int,required=True)
    parser.add_argument('--confirm-disposable',action='store_true',required=True)
    parser.add_argument('--old-source',type=Path)
    args=parser.parse_args();target=docker_target(container=args.container)
    major=verify_engine(target,expected_major=args.expected_major)
    count=run_probes(target,major,old_source=args.old_source)
    print(f'FRAMEWORK_INPUT_COMPLETE|PASS|profiles=6|negative={count}|version={major}',flush=True)


if __name__=='__main__':main()
