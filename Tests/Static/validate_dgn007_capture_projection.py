#!/usr/bin/env python3
"""Prüft den skalaren SQL-Producervertrag; keine Incident-/Herkunftsabnahme."""
from __future__ import annotations
import ast
import hashlib
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
AUTO=ROOT/'Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated'
WINDOWS=AUTO/'21_Controlled_Query_Store_Windows.sql'
EVIDENCE=AUTO/'35_Control_Evidence.sql'
MODULE=ROOT/'Tests/Contracts/dgn007_capture_projection.py'
RUNNER=ROOT/'Tests/Runtime/run_dgn007_automated_setup.py'
WORKFLOW=ROOT/'.github/workflows/dgn007-automated-setup.yml'


def uncomment(sql):
    # SQL-Literale einschließlich des festen Statementmarkers erhalten.
    token=re.compile(r"N?'(?:''|[^'])*'|/\*.*?\*/|--[^\n]*",re.DOTALL)
    return token.sub(lambda m:m[0] if not m[0].startswith(('/*','--')) else ' ',sql)


def normalized(sql): return ' '.join(uncomment(sql).split())


G13_RAW_SHA256 = '9b2a63cfb7d20fe428e87e0a7c7d92be8511b69e60e80800bac5b7348375d00c'
G13_BASE_SQL_SHA256 = '7d51b7bf3f444683ca2360595df24abf0214512c8794c50bcf5432f5fceae29f'


def strip_g13_raw_diagnostic(sql, *, check_baseline=False):
    """Nur die exakt geprüfte Fehlerdiagnose aus dem bekannten SQL35 entfernen."""
    sql = sql.replace('\r\n', '\n')
    begin, end = '/* G13_RAW_DIAGNOSTIC_BEGIN */', '/* G13_RAW_DIAGNOSTIC_END */'
    if sql.count(begin) != 1 or sql.count(end) != 1:
        raise ValueError('FAIL_CONTRACT')
    start, finish = sql.index(begin), sql.index(end) + len(end) + 1
    block = sql[start:finish]
    if (hashlib.sha256(block.encode('utf-8')).hexdigest() != G13_RAW_SHA256
            or not sql[:start].endswith('WHERE p.FirstExecutionTime<w.ExecutionStarted OR p.LastExecutionTime>w.ExecutionFinished)\nBEGIN\n')
            or not sql[finish:].startswith("    PRINT 'DGN007_CONTROL_GUARD|G13';\n    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;\nEND;")):
        raise ValueError('FAIL_CONTRACT')
    stripped = sql[:start] + sql[finish:]
    if check_baseline and hashlib.sha256(stripped.encode('utf-8')).hexdigest() != G13_BASE_SQL_SHA256:
        raise ValueError('FAIL_CONTRACT')
    return stripped


def canonical_guard_diagnostics(sql):
    """Nur 17 validierte konstante IDs vor denselben Ergebnisfehlern entfernen."""
    if 'G13_RAW_DIAGNOSTIC' in sql:
        sql = strip_g13_raw_diagnostic(sql)
    code=uncomment(sql)
    summary="PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT';"
    pattern=re.compile(r"\bPRINT 'DGN007_CONTROL_GUARD\|(G(?:0[1-9]|1[0-7]))';\s*"
                       +re.escape(summary)+r"\s*RETURN;")
    expected=tuple(f'G{i:02}' for i in range(1,18))
    if (tuple(match[1] for match in pattern.finditer(code))!=expected
            or code.count('DGN007_CONTROL_GUARD')!=17
            or len(re.findall(re.escape(summary)+r'\s*RETURN;',code))!=17):
        raise ValueError('FAIL_CONTRACT')
    canonical,count=re.subn(r"\bPRINT 'DGN007_CONTROL_GUARD\|G(?:0[1-9]|1[0-7])';",'',sql)
    if count!=17:
        raise ValueError('FAIL_CONTRACT')
    return canonical


def capture_section(sql,name):
    begin,end=f'/* CAPTURE_{name}_BEGIN */',f'/* CAPTURE_{name}_END */'
    if sql.count(begin)!=1 or sql.count(end)!=1 or sql.index(begin)>=sql.index(end):
        raise ValueError('FAIL_CONTRACT')
    return uncomment(sql.split(begin,1)[1].split(end,1)[0]).strip()


REQUEST_SECTIONS={
 'FRESH_GUARD':"OR OBJECT_ID(N'lab.RequestResultCapture',N'U') IS NOT NULL",
 'REQUEST_SCHEMA':"""CREATE TABLE lab.RequestResultCapture(
 WindowId tinyint NOT NULL,Ordinal tinyint NOT NULL,RequestLogId bigint NOT NULL UNIQUE,
 ReturnedRows bigint NOT NULL,PRIMARY KEY(WindowId,Ordinal),
 FOREIGN KEY(RequestLogId) REFERENCES dbo.CaseRequestLog(RequestLogId),
 CHECK(WindowId IN (0,1) AND Ordinal BETWEEN 1 AND 4 AND ReturnedRows>0));
 DECLARE @MeasuredReturnedRows bigint;""",
 'REQUEST_MEASUREMENT':"""SELECT @MeasuredReturnedRows=COUNT_BIG(*) FROM #Actual;
 IF @MeasuredReturnedRows IS NULL OR @MeasuredReturnedRows<=0 OR @MeasuredReturnedRows<>@ExpectedCount
 BEGIN PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN; END;
 INSERT lab.RequestResultCapture(WindowId,Ordinal,RequestLogId,ReturnedRows)
 VALUES(@WindowId,@Sequence,@LastRequestId,@MeasuredReturnedRows);""",
}


def request_capture_findings(sql):
    findings=[]
    try:
        for name,expected in REQUEST_SECTIONS.items():
            if normalized(capture_section(sql,name)).replace(" ","")!=normalized(expected).replace(" ",""):
                findings.append('Messquellen-/Schema-/Fresh-Guard-Vertrag verletzt: '+name)
        if not (sql.index('SET @LastRequestId=')<sql.index('/* CAPTURE_REQUEST_MEASUREMENT_BEGIN */')<sql.index('SET @Sequence+=1')):
            findings.append('Messung muss nach Requestprüfung und vor Sequenzfortschritt stehen')
        if sql.index('/* CAPTURE_REQUEST_SCHEMA_END */')>sql.index('SET QUERY_STORE=ON'):
            findings.append('Messschema muss vor den Suchrequests bereitstehen')
    except (ValueError,IndexError): findings.append('Capture-Messabschnitt fehlt oder ist mehrfach vorhanden')
    return findings


PROJECTION_MARKERS=(
 'FROM #CaptureRequestSource r LEFT JOIN lab.RequestResultCapture c',
 'ON c.WindowId=r.WindowId AND c.Ordinal=r.Ordinal AND c.RequestLogId=r.RequestLogId',
 '(SELECT COUNT_BIG(*) FROM lab.RequestResultCapture)<>8',
 '(SELECT COUNT_BIG(*) FROM #CaptureRequests)<>8',
 'p.WindowId IS NULL OR r.ReturnedRows IS NULL OR r.ReturnedRows<=0',
 'r.ReturnedRows<>p.ExpectedCount OR r.GroupKey<>p.GroupKey OR r.StatusCode<>p.StatusCode',
 'GROUP BY WindowId,Ordinal HAVING COUNT_BIG(*)<>1',
 'GROUP BY RequestLogId HAVING COUNT_BIG(*)<>1',
 'p.FirstExecutionTime<w.ExecutionStarted OR p.LastExecutionTime>w.ExecutionFinished',
 'WHERE EXISTS(SELECT 1 FROM lab.IncidentProfile p WHERE p.QueryId=s.QueryId)',
 'OR EXISTS(SELECT 1 FROM lab.IncidentProfile p WHERE p.ParentQueryId=s.QueryId AND s.ParentQueryId=s.QueryId)',
 'SUM(p.ExecutionCount*p.AvgDurationUs)/NULLIF(SUM(p.ExecutionCount),0)',
 'SUM(p.ExecutionCount*p.AvgCpuUs)/NULLIF(SUM(p.ExecutionCount),0)',
 'SUM(p.ExecutionCount*p.AvgLogicalReads)/NULLIF(SUM(p.ExecutionCount),0)',
 'SUM(p.ExecutionCount*p.AvgRowCount)/NULLIF(SUM(p.ExecutionCount),0)',
 'SUM(p.ExecutionCount*p.AvgRowCount) AS TotalRows',
 'AvgDurationUs IS NULL OR AvgDurationUs<0', 'AvgCpuUs IS NULL OR AvgCpuUs<0',
 'AvgLogicalReads IS NULL OR AvgLogicalReads<0','AvgRowCount IS NULL OR AvgRowCount<0',
 'TotalRows IS NULL OR ABS(TotalRows-4229.0)>0.000001',
 "SWITCHOFFSET(t.TimeValue,'+00:00')", "DATEDIFF_BIG(day,CONVERT(datetime2(7),'0001-01-01'),u.UtcTime)*CONVERT(bigint,864000000000)",
 'DATEDIFF_BIG(nanosecond,CONVERT(datetime2(7),CONVERT(date,u.UtcTime)),u.UtcTime)/100',
 'Ticks IS NULL OR Ticks<0 OR Ticks>3155378975999999999',
 'q.plan_id=p.PlanId AND q.query_id=p.QueryId',
 'WHERE @Major>=16 AND (PlanType IS NULL OR PlanType NOT IN (0,2))',
 'IF @Major>=16 EXEC sys.sp_executesql',
 "'MEASURED' AS row_evidence", 'ReturnedRows AS returned_rows',
 'INCLUDE_NULL_VALUES,WITHOUT_ARRAY_WRAPPER',
 "@ProjectionJson IS NULL OR LEN(@ProjectionJson) NOT BETWEEN 1 AND 32000",
 "@ProjectionJson COLLATE Latin1_General_100_BIN2 LIKE N'%[^ -~]%'",
 'DATALENGTH(@ProjectionJson)<>2*LEN(@ProjectionJson) OR ISJSON(@ProjectionJson)<>1',
 'DECLARE @Frame varchar(8000)', '(DATALENGTH(@ProjectionAscii)+ 511)/512',
 "'DGN007_CAPTURE_FRAME|1|'", 'SUBSTRING(@ProjectionAscii,(@FrameOrdinal-1)*512+1,512)',
 'PRINT @Frame;', 'SET @FrameOrdinal+=1;',
)
PROJECTION_SECTIONS=('PROJECTION','REQUEST_ROWS','REQUEST_GUARD','EXECUTION_BOUNDS','FAMILY_ROWS',
 'WEIGHTED_TOTALS','TOTALS_GUARD','TIME_ROWS','TIME_GUARD','JSON','FRAME_GUARD','FRAMES')


def projection_sql_findings(sql):
    findings=[]
    try:
        # Ganze bisherige SQL35-Datei bleibt nach exakt geprüftem Strip identisch.
        sql = strip_g13_raw_diagnostic(sql, check_baseline=True)
        sql=canonical_guard_diagnostics(sql)
        if normalized(capture_section(sql,'REQUIRED_GUARD'))!="OR OBJECT_ID(N'lab.RequestResultCapture',N'U') IS NULL":
            findings.append('Producer benötigt exakt den zusätzlichen Messschema-Existenzschutz')
        code=normalized(capture_section(sql,'PROJECTION'))
        for name in PROJECTION_SECTIONS: capture_section(sql,name)
        for marker in PROJECTION_MARKERS:
            if marker not in code: findings.append('Skalarprojektion-Vertrag fehlt: '+marker)
        for metric in ('AvgDurationUs','AvgCpuUs','AvgLogicalReads','AvgRowCount','TotalRows'):
            if f'CONVERT(varchar(64),t.{metric},3)' not in code:
                findings.append('Verlustfreier float-Style3 fehlt: '+metric)
        if code.count('JSON_QUERY(')!=5 or code.count('FOR JSON PATH,INCLUDE_NULL_VALUES')!=6:
            findings.append('Genau fünf skalare Recordarrays und ein Body erforderlich')
        if code.count("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;")!=2:
            findings.append('Producer benötigt zwei eigene bounded Timeoutguards')
        if sql.index('/* CAPTURE_PROJECTION_END */')>sql.rindex("PRINT 'SQLPERF_SUMMARY|PASS|OK'"):
            findings.append('Projektion muss vor der Evidenz-PASS-Summary stehen')
        for forbidden in ('query_sql_text','query_plan AS','contract_digest','source_digest','phase_result','absence_outcome','NOT_CAPTURED'):
            if forbidden in code: findings.append('Unzulässige Rohdaten oder künstliche Metadaten im SQL-Body')
        executable=re.sub(r"N?'(?:''|[^'])*'","''",code)
        if re.search(r'\b(?:ALTER|DROP|CREATE|DELETE|TRUNCATE|INSERT|DBCC|RECONFIGURE|BACKUP|RESTORE)\b',executable,re.IGNORECASE):
            findings.append('Skalarprojektion darf nur lesen und eigene temporäre Projektionen bilden')
        dynamic="IF @Major>=16 EXEC sys.sp_executesql N' UPDATE c SET PlanType=p.plan_type FROM #CapturePlans c JOIN sys.query_store_plan p ON p.plan_id=c.PlanId AND p.query_id=c.QueryId;'"
        if dynamic not in code or len(re.findall(r'\bEXEC(?:UTE)?\b',executable,re.IGNORECASE))!=1:
            findings.append('Einzige dynamische Projektion muss fest und auf PlanType ab Major16 begrenzt sein')
    except (ValueError,IndexError): findings.append('Projectionabschnitt fehlt oder ist mehrfach vorhanden')
    return findings


def pure_findings(source):
    tree=ast.parse(source); findings=[]
    allowed={'__future__','re','Tests.Contracts.dgn007_collector_transport','Tests.Contracts.dgn007_prospective_acceptance'}
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module]
            if any(name not in allowed for name in names): findings.append('Packager darf keine I/O-/Prozessmodule importieren')
        if isinstance(node,ast.Call):
            name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
            if name in {'open','print','eval','exec','RunRecord','PhaseResult','evaluate_version','read_text','write_text'}:
                findings.append('Packager darf weder I/O noch Lifecycle-/Incidentrecords erzeugen')
    return findings


def frame_contract_findings(source):
    tree=ast.parse(source); findings=[]
    assignments={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name): assignments.setdefault(target.id,[]).append(node.value)
    for name,value in (('MAX_CHUNK_CHARS',512),('MAX_PROJECTION_CHARS',32000),('MAX_FRAMES',64)):
        nodes=assignments.get(name,[])
        if len(nodes)!=1 or not isinstance(nodes[0],ast.Constant) or type(nodes[0].value) is not int or nodes[0].value!=value:
            findings.append('Feste Wire-v1-Grenze verletzt: '+name)
    nodes=assignments.get('MAX_FRAME_CHARS',[])
    expected=ast.parse('MAX_CHUNK_CHARS + 64',mode='eval').body
    if len(nodes)!=1 or ast.dump(nodes[0])!=ast.dump(expected):
        findings.append('Framegrenze muss Chunkgrenze plus exakt 64 Headerzeichen sein')
    return findings


def runner_projection_findings(source):
    tree=ast.parse(source); findings=[]
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    show=[n for n in ast.walk(tree) if isinstance(n,ast.Constant) and n.value=='--show-output']
    function=functions.get('run_harness')
    condition=ast.dump(ast.parse('check_capture_projection or check_phase_diagnostics',mode='eval').body)
    conditional=[n for n in ast.walk(function) if isinstance(n,ast.If) and ast.dump(n.test)==condition] if function else []
    allowed=[n for block in conditional for n in ast.walk(block) if isinstance(n,ast.Constant) and n.value=='--show-output']
    if len(show)!=1 or len(allowed)!=1 or show[0] is not allowed[0]:
        findings.append('show-output ist ausschließlich bei den beiden privaten begrenzten Diagnose-/Produceroptionen zulässig')
    guard=ast.dump(ast.parse('contract not in KNOWN_CONTRACTS or (check_capture_projection and contract.scope not in CONTROL_SCOPES)',mode='eval').body)
    if len(conditional)!=1 or not any(isinstance(n,ast.If) and ast.dump(n.test)==guard for n in ast.walk(conditional[0])):
        findings.append('Private Ausgabe benötigt den kanonischen Scope und die unveränderte Controls-only-Producergrenze')
    for marker in ('command.insert(1, "-u")','MAX_CAPTURE_OUTPUT_BYTES = 262144','MAX_CAPTURE_LINE_CHARS = 8192',
                   'body.major != expected_major','body.scope != contract.scope','not body.row_evidence_complete',
                   'channel != "stderr"','contract.scope not in CONTROL_SCOPES','decode_projection(tuple(frames), expected_contract)',
                   'contract not in KNOWN_CONTRACTS','--check-phase-diagnostics',
                   'collect_capture_process(process, command, contract=contract)',
                   'reported_capture_failure(result.stdout, result.stderr, contract=contract)',
                   'HARNESS_TIMEOUT = 180 + 60 + 20'):
        if marker not in source: findings.append('Producer-Runner-Vertrag fehlt: '+marker)
    for name in ('collect_capture_process','check_capture'):
        if name not in functions: findings.append('Private Producer-Prozessgrenze fehlt')
    return findings


def workflow_findings(source):
    findings=[]
    calls=re.findall(r'(?m)^          python Tests/Runtime/run_dgn007_automated_setup.py \\\n((?:            .*\n)+)',source)
    if len(calls)!=6 or [('--check-capture-projection' in call) for call in calls]!=[False,False,False,True,True,True]:
        findings.append('Nur dieselben sechs Controls-Lifecycles benötigen die Produceroption')
    if (len(calls)!=6 or [call.count('--check-phase-diagnostics') for call in calls]!=[1,1,1,0,0,0]):
        findings.append('Genau Datenmodell, Fenster und Profilvergleich benötigen die private Phasendiagnostik')
    for name in ('validate_dgn007_capture_projection','test_dgn007_capture_projection',
                 'validate_dgn007_collector_transport','test_dgn007_collector_transport',
                 'validate_dgn007_prospective_acceptance','test_dgn007_prospective_acceptance'):
        if 'python Tests/Static/'+name+'.py' not in source: findings.append('Producer-/Decoderstatik muss tatsächlich ausgeführt werden')
    if 'cancel-in-progress: false' not in source or 'upload-artifact' in source or '--show-output' in source:
        findings.append('Producer-CI muss Cleanup erhalten und Rohoutput privat halten')
    return findings


def main():
    windows=WINDOWS.read_text(encoding='utf-8'); evidence=EVIDENCE.read_text(encoding='utf-8')
    findings=request_capture_findings(windows)+projection_sql_findings(evidence)
    module=MODULE.read_text(encoding='utf-8')
    findings+=pure_findings(module)+frame_contract_findings(module)
    findings+=runner_projection_findings(RUNNER.read_text(encoding='utf-8'))
    findings+=workflow_findings(WORKFLOW.read_text(encoding='utf-8'))
    for i in range(1,18):
        if not projection_sql_findings(evidence.replace(f"PRINT 'DGN007_CONTROL_GUARD|G{i:02}';",'')):
            findings.append('Fehlende feste Guard-ID wurde nicht erkannt')
    for marker in PROJECTION_MARKERS:
        if not projection_sql_findings(re.sub(re.escape(marker).replace(r'\ ',r'\s*'),'REMOVED',evidence)):
            findings.append('Negative Projectionkontrolle wurde nicht erkannt')
    for name in REQUEST_SECTIONS:
        section=capture_section(windows,name)
        if not request_capture_findings(windows.replace(section,'REMOVED')):
            findings.append('Negative Messquellenkontrolle wurde nicht erkannt')
    for before,after in (('MAX_CHUNK_CHARS = 512','MAX_CHUNK_CHARS = 513'),
                         ('MAX_PROJECTION_CHARS = 32000','MAX_PROJECTION_CHARS = 32001'),
                         ('MAX_FRAMES = 64','MAX_FRAMES = 65'),
                         ('MAX_CHUNK_CHARS + 64','MAX_CHUNK_CHARS + 65')):
        if not frame_contract_findings(module.replace(before,after)):
            findings.append('Negative Wire-Grenzkontrolle wurde nicht erkannt')
    if findings:
        print('dgn007-capture-projection: FAIL\n'+'\n'.join(findings));return 1
    print('dgn007-capture-projection: PASS (PROJECT_SEMANTIC; keine Incident-/Herkunftsabnahme)');return 0

if __name__=='__main__': raise SystemExit(main())
