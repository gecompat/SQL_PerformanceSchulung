#!/usr/bin/env python3
"""OPT-007: begrenzte Cachezuordnung, Ergebnisvertrag und Recovery qualifizieren."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

import cleanup_ownership as ownership
import setup_ownership
from execution_target import ExecutionTarget, ExecutionTargetError, docker_target, run_sql, verify_engine

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / 'Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache'
TOOLS = ROOT / 'Demos/00_Framework/Tools'
DEMO = 'OPT-007'
DATABASE = ownership.database(DEMO)
VARIABLES = dict(DemoId=DEMO, RunToken='LOCAL', TargetDatabase=DATABASE,
                 ConfirmIsolatedLab='1', HighImpactConfirmed='1', MaximumRuntimeSeconds='120')
SUMMARY = re.compile(r'^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z_]+)$', re.M)
STANDARD = ('SET NOCOUNT ON;SET XACT_ABORT ON;SET LOCK_TIMEOUT 15000;SET ANSI_NULLS ON;SET ANSI_PADDING ON;SET ANSI_WARNINGS ON;SET ARITHABORT ON;'
            'SET CONCAT_NULL_YIELDS_NULL ON;SET QUOTED_IDENTIFIER ON;SET NUMERIC_ROUNDABORT OFF;'
            'SET LANGUAGE us_english;SET DATEFORMAT mdy;SET DATEFIRST 7;')
sys.path.insert(0, str(TOOLS))
import evaluate_result_contract as evaluator  # noqa: E402


def render(text: str, **overrides: str) -> str:
    for name, value in {**VARIABLES, **overrides}.items():
        text = text.replace('$(' + name + ')', value)
    if re.search(r'\$\([^)]+\)', text):
        raise RuntimeError('Unaufgelöster sqlcmd-Platzhalter')
    return text


def source(name: str) -> str:
    return render((DIRECTORY / name).read_text(encoding='utf-8-sig'))


def execute(target: ExecutionTarget, name: str) -> str:
    return run_sql(target, database='master', sql_text=source(name), timeout_seconds=15)


def require_error(target: ExecutionTarget, text: str, code: int, database: str = 'master') -> None:
    try:
        run_sql(target, database=database, sql_text=text+"\nGO\nTHROW 51999,'UNREACHED_BATCH',1;", timeout_seconds=20)
    except ExecutionTargetError as exc:
        if re.search(rf'\b{code}\b', str(exc)) and 'UNREACHED_BATCH' not in str(exc):
            return
        raise RuntimeError('Spezifische Ablehnung fehlt: '+str(exc)) from exc
    raise RuntimeError('Erwartete Ablehnung fehlt')


def numeric_evidence(output: str) -> dict:
    """Erst nach erfolgreicher vollständiger SQL-Metadaten-/Tupelprüfung normalisieren."""
    metrics: dict[str, int] = {}
    for arm, calls, count, cache_bytes in re.findall(r'OPT007_METRIC\s*\|\s*([LP])\s*\|\s*(20|40)\s*\|\s*(\d+)\s*\|\s*(\d+)', output):
        key = ('literal' if arm == 'L' else 'parameter') + calls
        if key in metrics or int(cache_bytes) <= 0:
            raise RuntimeError('Mehrdeutige oder ungültige numerische Cacheevidenz')
        metrics[key] = int(count)
    for arm, rows, keys, total in re.findall(r'OPT007_RESULT\s*\|\s*([LP])\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)', output):
        prefix = 'literal' if arm == 'L' else 'parameter'
        for name, value in [('rows', rows), ('keys', keys), ('sum', total)]:
            if prefix+'_'+name in metrics:
                raise RuntimeError('Doppelte Ergebnisevidenz')
            metrics[prefix+'_'+name] = int(value)
    return dict(contract_version='1.0', demo_id=DEMO, profile='BOUNDED_FULL_PLAN', comparison=metrics)


def require_harness(result: subprocess.CompletedProcess, expected: tuple[str, str]) -> None:
    text = result.stdout + '\n' + result.stderr
    if SUMMARY.findall(text)[-1:] != [expected] or (result.returncode == 0) != (expected[0] != 'FAIL'):
        raise RuntimeError('Harness: '+text[-6500:])
    phases = re.findall(r'^([A-Z]+): ([A-Z]+)/([A-Z_]+) ', text, re.M)
    if not phases or phases[-1] != ('CLEANUP', 'PASS', 'OK'):
        raise RuntimeError('Unabhängiger Cleanup-Erfolg fehlt: '+text[-4000:])
    if expected[0] == 'PASS' and ([p[0] for p in phases] != ['PREFLIGHT','SETUP','BASELINE','DEMONSTRATION','OBSERVATION','MITIGATION','COMPARISON','CLEANUP'] or any(p[1:] != ('PASS','OK') for p in phases)):
        raise RuntimeError('Nicht alle Pflichtphasen erfolgreich')


def harness(target: ExecutionTarget, directory: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOLS/'run_demo.py'), str(directory/'manifest.json'),
                           *target.connection_arguments(), '--confirm-isolated-lab', '--show-output'],
                          env=target.child_environment(), text=True, encoding='utf-8', errors='replace',
                          capture_output=True, timeout=170)


def lifecycles(target: ExecutionTarget) -> None:
    temp = ROOT/'Runtime/Temp'
    temp.mkdir(parents=True, exist_ok=True)
    for repetition in (1, 2):
        token = f'QUAL{repetition}'
        db = 'SQLPERF_LAB_OPT007_'+token
        with tempfile.TemporaryDirectory(prefix='opt007-', dir=temp) as temporary:
            directory = Path(temporary)/'demo'
            shutil.copytree(DIRECTORY, directory)
            manifest = json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
            manifest['run_token'] = token
            (directory/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            run_sql(target, database='master', sql_text=f"IF DB_ID(N'{db}') IS NOT NULL THROW 51990,'EXISTING_QUALIFICATION_DATABASE',1;")
            result = harness(target, directory)
            require_harness(result, ('PASS', 'OK'))
            evidence = directory/'evidence.json'
            evidence.write_text(json.dumps(numeric_evidence(result.stdout)), encoding='utf-8')
            records, code = evaluator.run(DIRECTORY/'Expected/result-contract.json', evidence)
            if code or records[-1]['outcome'] != 'PASS':
                raise RuntimeError('FWK-011-Ergebnisvertrag verletzt')
            run_sql(target, database='master', sql_text=f"IF DB_ID(N'{db}') IS NOT NULL THROW 51994,'QUALIFICATION_DATABASE_REMAINS',1;")
        print(f'OPT007_TEST|LIFECYCLE_{repetition}|PASS|FWK011|DATABASE_ABSENT', flush=True)


def protection(target: ExecutionTarget) -> None:
    setup_ownership.fixture(target, DEMO)
    control = setup_ownership.control_phase((DIRECTORY/'10_Setup.sql').read_text(encoding='utf-8'))
    cleanup = (DIRECTORY/'90_Cleanup.sql').read_text(encoding='utf-8')
    # Gemeinsame Oracle prüft komplette Katalog-/Modul-/Marker-/Sentinelbytes.
    for label, raw in [('SETUP', control), ('CLEANUP', cleanup)]:
        phase = raw
        for key in ('ConfirmIsolatedLab','HighImpactConfirmed','MaximumRuntimeSeconds'):
            phase = phase.replace('$('+key+')', VARIABLES[key])
        for _, markers, object_only, wrong_target in ownership.negative_cases(DEMO):
            setup_ownership.batch_rejection(target, DEMO, phase, markers, object_only, wrong_target)
        print(f'OPT007_TEST|{label}_OWNERSHIP|PASS|CASES={len(ownership.negative_cases(DEMO))}', flush=True)
    ownership.reset_markers(target, DEMO, {})
    setup_ownership.file_rejection(target, DEMO, source('10_Setup.sql'))
    ownership.reset_markers(target, DEMO, ownership.markers(DEMO))
    execute(target, '10_Setup.sql')
    execute(target, '10_Setup.sql')
    execute(target, '90_Cleanup.sql')
    execute(target, '90_Cleanup.sql')
    ownership.absent(target, DEMO)


def inputs(target: ExecutionTarget) -> None:
    bad = [{'DemoId': 'OPT-007X'}, {'DemoId': 'opt-007'}, {'DemoId': 'OPT-007 '},
           {'RunToken': 'A'*17}, {'RunToken': 'Ä'}, {'RunToken': 'ＬＯＣＡＬ'},
           {'RunToken': 'LOCAL\t'}, {'RunToken': ''}, {'TargetDatabase': DATABASE+'X'},
           {'TargetDatabase': DATABASE+' '}, {'TargetDatabase': DATABASE+'X'*140}]
    for file in ('00_Preflight.sql', '10_Setup.sql', '90_Cleanup.sql'):
        raw = (DIRECTORY/file).read_text(encoding='utf-8')
        for case in bad:
            require_error(target, render(raw, **case), 51000)
    for key, value in [('ConfirmIsolatedLab','0'),('HighImpactConfirmed','0'),('MaximumRuntimeSeconds','0'),('MaximumRuntimeSeconds','121')]:
        require_error(target, render((DIRECTORY/'10_Setup.sql').read_text(encoding='utf-8'), **{key:value}),51001)
    ownership.absent(target, DEMO)
    print('OPT007_TEST|RAW_INPUT_SAFETY|PASS|CASES=37', flush=True)


def evidence_rejections(target: ExecutionTarget) -> None:
    execute(target, '10_Setup.sql')
    try:
        execute(target, '20_Baseline.sql')
        execute(target, '30_Demonstration.sql')
        execute(target, '40_Observation.sql')
        execute(target, '50_Mitigation.sql')
        comparison = source('60_Comparison.sql')
        execute(target, '60_Comparison.sql')
        run_sql(target,database=DATABASE,sql_text='UPDATE lab.CacheState SET Stage=3;')
        # Jede Mutation wird unabhängig restauriert, der ursprüngliche Nachweis bleibt erhalten.
        mutations = [
            "UPDATE lab.CacheResult SET Payload=Payload+1 WHERE Arm='P' AND KeyValue=1;",
            "UPDATE lab.CacheResult SET Payload=CASE WHEN KeyValue=1 THEN 2 ELSE 1 END WHERE Arm='P' AND KeyValue IN(1,2);",
            "DELETE lab.CacheResult WHERE Arm='L' AND KeyValue=40;",
            "DELETE lab.CacheSnapshot WHERE Arm='L' AND Calls=20 AND BatchKey=20;",
            "UPDATE lab.CacheSnapshot SET Created=DATEADD(second,1,Created) WHERE Arm='P' AND Calls=20;",
            "UPDATE lab.CacheSnapshot SET Generation=Generation+1 WHERE Arm='P' AND Calls=20;",
            "UPDATE lab.CacheSnapshot SET ExecutionCount=19 WHERE Arm='P' AND Calls=20;",
            "UPDATE lab.CacheSnapshot SET SetOptions=SetOptions+1 WHERE Arm='P' AND Calls=20;",
            "UPDATE lab.CacheSnapshot SET Handle=0x1234 WHERE Arm='P' AND Calls=20;",
        ]
        # Beobachtungsprüfung braucht keinen offenen Transaktionskontext; Sicherung in Temp-Tabellen.
        save = "SELECT * INTO #R FROM lab.CacheResult; SELECT * INTO #S FROM lab.CacheSnapshot;"
        restore = "DELETE lab.CacheResult;INSERT lab.CacheResult SELECT * FROM #R;DELETE lab.CacheSnapshot;INSERT lab.CacheSnapshot SELECT * FROM #S;"
        for mutation in mutations:
            batch = save+mutation+"DECLARE @Error int; BEGIN TRY EXEC sys.sp_executesql "+ownership.literal(comparison)+"; END TRY BEGIN CATCH SET @Error=ERROR_NUMBER(); END CATCH;"+restore+"IF @Error IS NULL OR @Error<>51006 THROW 51992,'WEAK_EVIDENCE_ACCEPTED',1;"
            run_sql(target, database=DATABASE, sql_text=batch, timeout_seconds=15)
        require_error(target, STANDARD+"EXEC lab.USP_Workload N'LOCAL','P';",51002,DATABASE)
        require_error(target, STANDARD+"EXEC lab.USP_Capture N'LOCAL','L',41,0;",51000,DATABASE)
        run_sql(target, database=DATABASE, sql_text="UPDATE lab.CacheState SET StartedAt=DATEADD(second,-121,SYSUTCDATETIME());")
        require_error(target, source('40_Observation.sql'),51005)
        print(f'OPT007_TEST|EVIDENCE_AND_BUDGET|PASS|MUTATIONS={len(mutations)}', flush=True)
    finally:
        execute(target, '90_Cleanup.sql')
        ownership.absent(target, DEMO)


def plan_rejections(target: ExecutionTarget) -> None:
    """Nur synthetische Gegenbelege in Kopien der echten Erfassungsprozedur."""
    execute(target,'10_Setup.sql')
    try:
        execute(target,'20_Baseline.sql')
        execute(target,'30_Demonstration.sql')
        execute(target,'50_Mitigation.sql')
        raw=(DIRECTORY/'10_Setup.sql').read_text(encoding='utf-8')
        capture=raw.split('CREATE OR ALTER PROCEDURE lab.USP_Capture',1)[1].split('\nGO\n',1)[0]
        capture='CREATE OR ALTER PROCEDURE lab.USP_Capture'+capture
        plan_anchor=' IF (SELECT COUNT(*) FROM @Plans)'
        stats_anchor=' IF EXISTS(SELECT 1 FROM @Stats WHERE StatementText IS NULL'
        wrong_xml='<ShowPlanXML xmlns="http://schemas.microsoft.com/sqlserver/2004/07/showplan"><BatchSequence><Batch><Statements><StmtSimple StatementType="SELECT" StatementText="SELECT 99"><QueryPlan><RelOp PhysicalOp="Constant Scan"/></QueryPlan></StmtSimple></Statements></Batch></BatchSequence></ShowPlanXML>'
        cases=[
            (plan_anchor,"UPDATE @Plans SET PlanXml=NULL;",51006),
            (plan_anchor,"UPDATE @Plans SET PlanXml="+ownership.literal(wrong_xml)+";",51006),
            (plan_anchor,"UPDATE @Plans SET CacheType=N'Compiled Plan Stub',PlanXml=NULL;",51006),
            (plan_anchor,"UPDATE @Plans SET PlanXml.modify('declare default element namespace \"http://schemas.microsoft.com/sqlserver/2004/07/showplan\"; delete //RelOp');",51006),
            (plan_anchor,"UPDATE @Plans SET PlanXml.modify('declare default element namespace \"http://schemas.microsoft.com/sqlserver/2004/07/showplan\"; insert <ParameterList><ColumnReference Column=\"@1\"/></ParameterList> into (/ShowPlanXML/BatchSequence/Batch/Statements/StmtSimple[@StatementType=\"SELECT\"]/QueryPlan)[1]');",51006),
            (plan_anchor,"UPDATE @Plans SET PlanXml.modify('declare default element namespace \"http://schemas.microsoft.com/sqlserver/2004/07/showplan\"; insert attribute ParameterizedPlanHandle {\"0x01\"} into (/ShowPlanXML/BatchSequence/Batch/Statements/StmtSimple[@StatementType=\"SELECT\"])[1]');",51006),
            (plan_anchor,"UPDATE @Plans SET Text=Text+N' ';",51006),
            (plan_anchor,"DELETE FROM @Plans WHERE Handle=(SELECT TOP(1) Handle FROM @Plans);",51006),
            (plan_anchor,"UPDATE @Plans SET DatabaseId=DatabaseId+1;",51006),
            (plan_anchor,"UPDATE @Plans SET ObjType=N'Prepared';",51006),
            (plan_anchor,"UPDATE @Plans SET SetOptions=NULL;",51006),
            (' IF ISNULL((SELECT SUM(Bytes)',"UPDATE @Plans SET Bytes=16777217;",51001),
            (stats_anchor,"UPDATE @Stats SET StatementText=NULL;",51006),
            (stats_anchor,"UPDATE @Stats SET BatchMatches=0;",51006),
            (stats_anchor,"UPDATE @Stats SET ValidOffsets=0;",51006),
            (stats_anchor,"UPDATE @Stats SET ExecutionCount=2;",51006),
        ]
        for anchor,injection,error in cases:
            assert capture.count(anchor)==1
            altered=capture.replace(anchor,' '+injection+'\n'+anchor)
            run_sql(target,database=DATABASE,sql_text=STANDARD+'\nGO\n'+altered,timeout_seconds=15)
            require_error(target,STANDARD+"EXEC lab.USP_Capture N'LOCAL','L',40,0;",error,DATABASE)
        # Die echte Gesamtsummen-Schutzprüfung mit kleinerer synthetischer Schwelle.
        altered=capture.replace('>16777216','>1')
        run_sql(target,database=DATABASE,sql_text=STANDARD+'\nGO\n'+altered,timeout_seconds=15)
        require_error(target,STANDARD+"EXEC lab.USP_Capture N'LOCAL','L',40,0;",51001,DATABASE)
        # Beide Arme einzeln unter der synthetischen Schwelle, gemeinsam darüber.
        totals=run_sql(target,database=DATABASE,sql_text="""SET NOCOUNT ON;
SELECT SUM(CASE WHEN CHARINDEX('/* OPT-007:LOCAL:LITERAL */',st.text)>0 THEN CONVERT(bigint,cp.size_in_bytes) ELSE 0 END),
 SUM(CASE WHEN CHARINDEX('/* OPT-007:LOCAL:PARAMETER */',st.text)>0 THEN CONVERT(bigint,cp.size_in_bytes) ELSE 0 END)
FROM sys.dm_exec_cached_plans cp CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) st
WHERE EXISTS(SELECT 1 FROM sys.dm_exec_plan_attributes(cp.plan_handle) a WHERE a.attribute='dbid' AND CONVERT(int,a.value)=DB_ID());""")
        match=re.search(r'(?m)^\s*(\d+)\|(\d+)\s*$',totals)
        if not match or min(map(int,match.groups()))<=0:raise RuntimeError('Beide Arme für die Gesamtgrenzengegenprobe fehlen')
        limit=max(map(int,match.groups()))
        altered=capture.replace('>16777216','>'+str(limit))
        run_sql(target,database=DATABASE,sql_text=STANDARD+'\nGO\n'+altered,timeout_seconds=15)
        require_error(target,STANDARD+"EXEC lab.USP_Capture N'LOCAL','P',40,0;",51001,DATABASE)
        run_sql(target,database=DATABASE,sql_text=STANDARD+'\nGO\n'+capture,timeout_seconds=15)
        print(f'OPT007_TEST|PLAN_STATS_NEGATIVES|PASS|CASES={len(cases)+2}|BOTH_ARMS_LIMIT',flush=True)
    finally:
        execute(target,'90_Cleanup.sql')
        ownership.absent(target,DEMO)


def context_and_configuration(target: ExecutionTarget) -> None:
    # Vorher erkennbare ungeeignete Konfiguration als kontrollierter Skip,
    # ohne Instanzoption oder Cachemodus umzuschalten.
    preflight=source('00_Preflight.sql')
    wrong=preflight.replace("(SELECT value_in_use FROM sys.configurations WHERE name='optimize for ad hoc workloads')<>0",'1<>0')
    output=run_sql(target,database='master',sql_text=wrong.replace("PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_CONFIGURATION';","SELECT 'CONTROLLED_CONFIGURATION_SKIP';PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_CONFIGURATION';"))
    if output.split()!=['CONTROLLED_CONFIGURATION_SKIP']:
        raise RuntimeError('Konfigurationsskip vor Setup fehlt')
    execute(target,'10_Setup.sql')
    try:
        execute(target,'20_Baseline.sql')
        for setting in ('SET DATEFORMAT dmy;','SET DATEFIRST 1;','SET LANGUAGE German;','SET ARITHABORT OFF;'):
            require_error(target,STANDARD+setting+"EXEC lab.USP_Context N'LOCAL';",51002,DATABASE)
        require_error(target,STANDARD+"EXEC lab.USP_Context N'FOREIGN';",51002,DATABASE)
        # Unerwarteter Datenbankmodus nach Setup: synthetisch veränderte echte
        # Prüfklausel, keine reale Stubausführung und keine Optionsänderung.
        context=(DIRECTORY/'10_Setup.sql').read_text(encoding='utf-8').split('CREATE OR ALTER PROCEDURE lab.USP_Context',1)[1].split('\nGO\n',1)[0]
        context='CREATE OR ALTER PROCEDURE lab.USP_Context'+context
        altered=context.replace("name='OPTIMIZE_FOR_AD_HOC_WORKLOADS' AND value=0","name='OPTIMIZE_FOR_AD_HOC_WORKLOADS' AND value=1")
        run_sql(target,database=DATABASE,sql_text=STANDARD+'\nGO\n'+altered)
        require_error(target,STANDARD+"EXEC lab.USP_Context N'LOCAL';",51002,DATABASE)
        run_sql(target,database=DATABASE,sql_text=STANDARD+'\nGO\n'+context)
        raw=(DIRECTORY/'10_Setup.sql').read_text(encoding='utf-8')
        function='CREATE OR ALTER FUNCTION lab.QueryText'+raw.split('CREATE OR ALTER FUNCTION lab.QueryText',1)[1].split('\nGO\n',1)[0]
        oversized=function.replace('RETURNS nvarchar(2048)','RETURNS nvarchar(max)').replace("RETURN N'/*", "RETURN REPLICATE(CONVERT(nvarchar(max),N'X'),2049)+N'/*")
        run_sql(target,database=DATABASE,sql_text=STANDARD+'\nGO\n'+oversized)
        require_error(target,STANDARD+"EXEC lab.USP_Workload N'LOCAL','L';",51001,DATABASE)
        run_sql(target,database=DATABASE,sql_text=STANDARD+'\nGO\n'+function)
        print('OPT007_TEST|CONFIGURATION_AND_CONTEXT|PASS|NO_OPTION_SWITCH',flush=True)
    finally:
        execute(target,'90_Cleanup.sql')
        ownership.absent(target,DEMO)


def permission_and_normalization(target: ExecutionTarget) -> None:
    login='SQLPERF_OPT007_PERMISSION'
    password=os.environ.get('SQLCMDPASSWORD')
    if not password:raise RuntimeError('Kennwort der eigenen Wegwerfinstanz fehlt')
    run_sql(target,database='master',sql_text=f"IF SUSER_ID(N'{login}') IS NOT NULL THROW 51990,'EXISTING_PERMISSION_FIXTURE',1;CREATE LOGIN [{login}] WITH PASSWORD={ownership.literal(password)},CHECK_POLICY=OFF;")
    try:
        preflight=source('00_Preflight.sql').replace("PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';","SELECT 'PERMISSION_SKIP';PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';")
        output=run_sql(target,database='master',sql_text=f"EXECUTE AS LOGIN=N'{login}';EXEC sys.sp_executesql "+ownership.literal(preflight)+";REVERT;")
        if 'PERMISSION_SKIP' not in output:raise RuntimeError('Kontrollierter Berechtigungsskip fehlt')
    finally:run_sql(target,database='master',sql_text=f'DROP LOGIN [{login}];')
    # Gleiche vollständige Rohwerte über sämtliche Phasen; keine Kürzung vor Prüfung.
    token=' '*48+'local'+' '*48
    phases=json.loads((DIRECTORY/'manifest.json').read_text(encoding='utf-8'))['phases']
    try:
        for phase in phases:
            raw=(DIRECTORY/phase['script']).read_text(encoding='utf-8')
            run_sql(target,database='master',sql_text=render(raw,RunToken=token),timeout_seconds=15)
    finally:
        raw=(DIRECTORY/'90_Cleanup.sql').read_text(encoding='utf-8')
        run_sql(target,database='master',sql_text=render(raw,RunToken=token),timeout_seconds=30)
        ownership.absent(target,DEMO)
    print('OPT007_TEST|PERMISSION_NORMALIZED_LIFECYCLE|PASS|CLEANUP_ABSENT',flush=True)


def timeout_cleanup(target: ExecutionTarget) -> None:
    with tempfile.TemporaryDirectory(prefix='opt007-timeout-', dir=ROOT/'Runtime/Temp') as temporary:
        directory = Path(temporary)/'demo'
        shutil.copytree(DIRECTORY,directory)
        script = directory/'10_Setup.sql'
        script.write_text(script.read_text(encoding='utf-8').replace("IF @Arm='L' INSERT @Result EXEC(@Text);", "IF @Arm='L' BEGIN SET @Text=REPLACE(@Text,N'DECLARE @Key',N'WAITFOR DELAY ''00:00:20'';DECLARE @Key');INSERT @Result EXEC(@Text);END;"),encoding='utf-8')
        manifest = json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
        manifest['phases'][3]['timeout_seconds']=5
        (directory/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        process=subprocess.Popen([sys.executable,str(TOOLS/'run_demo.py'),str(directory/'manifest.json'),*target.connection_arguments(),'--confirm-isolated-lab','--show-output'],
                                 env=target.child_environment(),text=True,encoding='utf-8',errors='replace',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        active=False
        try:
            deadline=time.monotonic()+35
            while process.poll() is None and time.monotonic()<deadline:
                observed=run_sql(target,database='master',timeout_seconds=5,sql_text=f"SET NOCOUNT ON;IF EXISTS(SELECT 1 FROM sys.dm_exec_requests r CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t WHERE r.database_id=DB_ID(N'{DATABASE}') AND r.wait_type='WAITFOR' AND CHARINDEX('/* OPT-007:LOCAL:LITERAL */',t.text)=1) SELECT 'ACTIVE_OWN_CALL';")
                if observed.split()==['ACTIVE_OWN_CALL']:
                    active=True;break
                time.sleep(.1)
            stdout,stderr=process.communicate(timeout=120)
        finally:
            if process.poll() is None:
                process.kill();process.communicate(timeout=30)
                execute(target,'90_Cleanup.sql')
        result=subprocess.CompletedProcess(process.args,process.returncode,stdout,stderr)
        require_harness(result,('FAIL','FAIL_TIMEOUT'))
        if not active:raise RuntimeError('Timeout ohne unabhängig beobachteten aktiven eigenen Aufruf')
        ownership.absent(target,DEMO)
    print('OPT007_TEST|ACTIVE_SQL_TIMEOUT|PASS|CLEANUP_ABSENT',flush=True)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container',required=True)
    parser.add_argument('--expected-major',type=int,choices=(15,16,17),required=True)
    parser.add_argument('--confirm-disposable-instance',action='store_true',required=True)
    parser.add_argument('--plan-contract-only',action='store_true',help='Gezielte Ergänzungsprüfung nach unveränderten Lifecycle-Quellen.')
    parser.add_argument('--supplement-only',action='store_true',help='Gezielte neue Plan-/Kontext-/Rohwertgegenproben am unveränderten Demoschnitt.')
    args=parser.parse_args()
    try:
        target=docker_target(container=args.container)
        verify_engine(target,expected_major=args.expected_major)
        if args.supplement_only:
            plan_rejections(target)
            context_and_configuration(target)
            permission_and_normalization(target)
            print(f'OPT007_TEST|SQL_{args.expected_major}|PASS|SUPPLEMENT',flush=True)
            return 0
        if args.plan_contract_only:
            plan_rejections(target)
            print(f'OPT007_TEST|SQL_{args.expected_major}|PASS|PLAN_CONTRACT_DELTA',flush=True)
            return 0
        lifecycles(target)
        protection(target)
        inputs(target)
        evidence_rejections(target)
        plan_rejections(target)
        context_and_configuration(target)
        permission_and_normalization(target)
        timeout_cleanup(target)
        print(f'OPT007_TEST|SQL_{args.expected_major}|PASS|ALL_REQUIRED_CASES',flush=True)
        return 0
    except (RuntimeError,OSError,subprocess.SubprocessError) as exc:
        text=str(exc)
        password=os.environ.get('SQLCMDPASSWORD')
        print('OPT007_TEST|FAIL|'+(text.replace(password,'***') if password else text),file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
