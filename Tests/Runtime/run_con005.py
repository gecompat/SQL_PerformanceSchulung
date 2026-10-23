#!/usr/bin/env python3
"""CON-005: Schemasperren, Schutzablehnung und Abbruch in einer eigenen Instanz prüfen."""
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
DEMO = 'CON-005'
DIRECTORY = ROOT / 'Demos/07_Concurrency/CON-005_Schema_Locks'
DATABASE = ownership.database(DEMO)
TOOLS = ROOT / 'Demos/00_Framework/Tools'
SUMMARY = re.compile(r'^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$', re.M)
VARIABLES = {'DemoId': DEMO, 'RunToken': 'LOCAL', 'TargetDatabase': DATABASE,
             'ConfirmIsolatedLab': '1', 'HighImpactConfirmed': '1', 'MaximumRuntimeSeconds': '120'}


def render(source: str, **overrides: str) -> str:
    """Nur synthetische Testeingaben; kein SQL-Text aus Teilnehmerdaten."""
    for name, value in {**VARIABLES, **overrides}.items():
        source = source.replace('$(' + name + ')', value)
    if re.search(r'\$\([^)]+\)', source):
        raise ValueError('Unaufgelöster sqlcmd-Platzhalter')
    return source


def source(name: str) -> str:
    return render((DIRECTORY / name).read_text(encoding='utf-8-sig'))


def require_error(target: ExecutionTarget, text: str, code: int, *, database: str = 'master') -> None:
    try:
        run_sql(target, database=database,
                sql_text=text + "\nGO\nTHROW 51999,'UNREACHED_BATCH',1;\n", timeout_seconds=45)
    except ExecutionTargetError as exc:
        diagnostic = str(exc)
        if re.search(rf'\b{code}\b', diagnostic) and 'UNREACHED_BATCH' not in diagnostic:
            return
        raise RuntimeError('Spezifische Schutzablehnung fehlt: ' + diagnostic) from exc
    raise RuntimeError('Erwartete Ablehnung blieb aus')


def execute(target: ExecutionTarget, name: str, *, database: str = 'master') -> str:
    output = run_sql(target, database=database, sql_text=source(name), timeout_seconds=120)
    records = [line.strip().split('|') for line in output.splitlines()]
    if not any(len(row) == 8 and row[2:5] == ['SUMMARY', 'PASS', 'OK'] for row in records):
        # Der idempotente Abwesenheitspfad meldet nur PRINT auf stderr.
        # Sein Ergebnis wird deshalb zusätzlich direkt in master geprüft.
        if name == '90_Cleanup.sql' and not output.strip():
            ownership.absent(target, DEMO)
            return output
        raise RuntimeError(name + ': vollständiger Erfolgsmarker fehlt')
    return output


def command(target: ExecutionTarget, manifest: Path, *, show_output: bool = False) -> list[str]:
    result = [sys.executable, str(TOOLS / 'run_demo.py'), str(manifest),
              *target.connection_arguments(), '--confirm-isolated-lab']
    if show_output:
        result.append('--show-output')
    return result


def require_harness(result: subprocess.CompletedProcess[str], expected: tuple[str, str]) -> None:
    output = result.stdout + '\n' + result.stderr
    if SUMMARY.findall(output)[-1:] != [expected] or (result.returncode == 0) != (expected[0] == 'PASS'):
        raise RuntimeError('Unerwarteter Harnessausgang: ' + ownership_execution_redact(output[-7000:]))
    phases = re.findall(r'^([A-Z]+): ([A-Z]+)/([A-Z_]+) ', output, re.M)
    if not phases or phases[-1] != ('CLEANUP', 'PASS', 'OK'):
        raise RuntimeError('Eigenständiger Cleanup-Erfolg fehlt')
    if expected[0] == 'PASS':
        wanted = ['PREFLIGHT', 'SETUP', 'BASELINE', 'DEMONSTRATION', 'OBSERVATION', 'COMPARISON', 'CLEANUP']
        if [p[0] for p in phases] != wanted or any(p[1:] != ('PASS', 'OK') for p in phases):
            raise RuntimeError('Nicht alle regulären Phasen wurden erfolgreich ausgeführt')
    elif ('DEMONSTRATION', 'FAIL', 'FAIL_TIMEOUT') not in phases:
        raise RuntimeError('Der erzwungene Orchestrierungstimeout ist nicht nachgewiesen')


def ownership_execution_redact(text: str) -> str:
    password = os.environ.get('SQLCMDPASSWORD')
    return text.replace(password, '***') if password else text


def lifecycles(target: ExecutionTarget) -> None:
    for repetition in (1, 2):
        ownership.absent(target, DEMO)
        result = subprocess.run(command(target, DIRECTORY / 'manifest.json'),
                                capture_output=True, text=True, encoding='utf-8', errors='replace',
                                env=target.child_environment(), timeout=180)
        require_harness(result, ('PASS', 'OK'))
        ownership.absent(target, DEMO)
        print(f'CON005_TEST|LIFECYCLE_{repetition}|PASS|CLEANUP_ABSENT', flush=True)


def protection(target: ExecutionTarget) -> None:
    setup_ownership.fixture(target, DEMO)
    setup = source('10_Setup.sql').split('\nGO\n', 1)[0]
    cleanup = source('90_Cleanup.sql')
    cases = ownership.negative_cases(DEMO)
    for phase_name, phase in [('SETUP', setup), ('CLEANUP', cleanup)]:
        for label, markers, object_only, wrong_target in cases:
            # Diese bestehende Gegenprobe vergleicht vollständige Katalog-,
            # Modul-, Marker- und Sentinelbytes vor und nach der echten Ablehnung.
            setup_ownership.batch_rejection(target, DEMO, phase.replace(DATABASE, '$(TargetDatabase)'),
                                            markers, object_only, wrong_target)
        print(f'CON005_TEST|{phase_name}_OWNERSHIP|PASS|CASES={len(cases)}', flush=True)
    ownership.reset_markers(target, DEMO, {})
    setup_ownership.file_rejection(target, DEMO, source('10_Setup.sql'))
    require_error(target, cleanup, 51002)
    ownership.reset_markers(target, DEMO, ownership.markers(DEMO))
    identity_before = setup_ownership.snapshot(target, DEMO, identity_only=True)
    execute(target, '10_Setup.sql')
    execute(target, '10_Setup.sql')
    if setup_ownership.snapshot(target, DEMO, identity_only=True) != identity_before:
        raise RuntimeError('Idempotentes Setup verändert fremde Fixture-/Identitätsdaten')
    execute(target, '90_Cleanup.sql')
    execute(target, '90_Cleanup.sql')
    ownership.absent(target, DEMO)
    print('CON005_TEST|WHOLE_FILE_AND_IDEMPOTENCE|PASS', flush=True)


def inventory_snapshot(target: ExecutionTarget) -> bytes:
    """Vollständige Inventarbytes statt sqlcmd-Standardkürzung variabler Felder."""
    output = run_sql(target, database='master', sql_text="""
SET NOCOUNT ON;
DECLARE @Bytes varbinary(max)=CONVERT(varbinary(max),CONVERT(nvarchar(max),
 (SELECT (SELECT database_id,name,state,user_access,is_read_only,recovery_model,compatibility_level
  FROM sys.databases WHERE database_id>4 ORDER BY database_id FOR XML RAW,TYPE) AS [Databases]
  FOR XML PATH('Inventory'),TYPE))),@Offset int=1;
SELECT 'LENGTH',DATALENGTH(@Bytes);
WHILE @Offset<=DATALENGTH(@Bytes)
BEGIN
 SELECT 'BYTES',@Offset,CONVERT(varchar(200),SUBSTRING(@Bytes,@Offset,100),2);
 SET @Offset+=100;
END;
""")
    return setup_ownership.decode_snapshot(output)


def inventory_oracle(target: ExecutionTarget) -> None:
    """Eine zusätzliche eigene Datenbank muss auch hinter dem Präfix auffallen."""
    extra = 'SQLPERF_LAB_CON005_ORACLE'
    run_sql(target, database='master', sql_text=f"IF DB_ID(N'{extra}') IS NOT NULL THROW 51990,'FOREIGN_ORACLE_DATABASE',1;")
    ownership.fixture(target, DEMO)
    extra_created = False
    try:
        before = inventory_snapshot(target)
        raw = (DIRECTORY / '10_Setup.sql').read_text(encoding='utf-8-sig')
        run_sql(target, database='master', sql_text=render(raw, RunToken='ORACLE', TargetDatabase=extra))
        extra_created = True
        after = inventory_snapshot(target)
        if len(before) <= 128 or before[:128] != after[:128] or before == after:
            raise RuntimeError('Inventaroracle erkennt die zusätzliche Datenbank hinter dem ersten Präfix nicht')
    finally:
        if extra_created:
            raw = (DIRECTORY / '90_Cleanup.sql').read_text(encoding='utf-8-sig')
            run_sql(target, database='master', sql_text=render(raw, RunToken='ORACLE', TargetDatabase=extra))
            run_sql(target, database='master', sql_text=f"IF DB_ID(N'{extra}') IS NOT NULL THROW 51994,'ORACLE_DATABASE_REMAINS',1;")
        execute(target, '90_Cleanup.sql')
        ownership.absent(target, DEMO)
    print('CON005_TEST|INVENTORY_ORACLE_FULL_BYTES|PASS', flush=True)


def normalized_lifecycle(target: ExecutionTarget) -> None:
    """Akzeptierte äußere Leerzeichen dürfen keine Signalparameter abschneiden."""
    temp_root = ROOT / 'Runtime/Temp'
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='con005-normalized-', dir=temp_root) as temporary:
        path = Path(temporary).resolve()
        if not path.is_relative_to(temp_root.resolve()):
            raise RuntimeError('Normalisierungsprüfpfad außerhalb des erlaubten Bereichs')
        shutil.copytree(DIRECTORY, path / 'demo')
        fixture = path / 'demo'
        raw_token = ' ' * 24 + 'local' + ' ' * 24
        for sql_file in fixture.rglob('*.sql'):
            text = render(sql_file.read_text(encoding='utf-8-sig'), RunToken=raw_token)
            if raw_token not in text:
                raise RuntimeError('Normalisierungsgegenprobe übergibt den Rohwert nicht vollständig')
            sql_file.write_text(text, encoding='utf-8')
        ownership.absent(target, DEMO)
        result = subprocess.run(command(target, fixture / 'manifest.json'), capture_output=True,
                                text=True, encoding='utf-8', errors='replace',
                                env=target.child_environment(), timeout=180)
        require_harness(result, ('PASS', 'OK'))
        ownership.absent(target, DEMO)
    print('CON005_TEST|NORMALIZED_FULL_LIFECYCLE|PASS|OUTER_SPACES=48', flush=True)


def inputs_and_permissions(target: ExecutionTarget) -> None:
    inventory_oracle(target)
    raw_setup = (DIRECTORY / '10_Setup.sql').read_text(encoding='utf-8-sig')
    raw_cleanup = (DIRECTORY / '90_Cleanup.sql').read_text(encoding='utf-8-sig')
    invalid = [('DemoId', 'CON-005X'), ('DemoId', 'con-005'), ('DemoId', 'CON-005 '),
               ('DemoId', 'CON-００５'), ('RunToken', 'A' * 17), ('RunToken', 'LOCAL!'),
               ('RunToken', 'LOCＡL'), ('TargetDatabase', DATABASE + 'X'),
               ('TargetDatabase', DATABASE + ' '), ('TargetDatabase', DATABASE.lower()),
               ('DemoId', 'CON-005' + ' ' * 5000 + 'X'),
               ('RunToken', 'LOCAL' + ' ' * 5000 + 'X'),
               ('TargetDatabase', DATABASE + ' ' * 5000 + 'X')]
    folding_target = 'SQLPERF_LAB_CON005_LOCIL'
    for raw in (raw_setup, raw_cleanup):
        for name, value in invalid:
            require_error(target, render(raw, **{name: value}), 51000)
        before = inventory_snapshot(target)
        # U+0131 kann durch UPPER zu ASCII-I werden. Das dazu passende Ziel
        # verhindert, dass eine bloße Namensabweichung den Zeichensatzfehler verdeckt.
        require_error(target, render(raw, RunToken='locıl', TargetDatabase=folding_target), 51000)
        after = inventory_snapshot(target)
        if not before or before != after:
            raise RuntimeError('Unicode-Rohwertablehnung änderte das Datenbankinventar')
    preflight = (DIRECTORY / '00_Preflight.sql').read_text(encoding='utf-8-sig')
    for values in ({'ConfirmIsolatedLab': '0'}, {'HighImpactConfirmed': '0'},
                   {'MaximumRuntimeSeconds': '0'}, {'MaximumRuntimeSeconds': '121'}):
        require_error(target, render(preflight, **values), 51001)
    ownership.absent(target, DEMO)
    login = 'SQLPERF_CON005_LIMITED'
    password = os.environ.get('SQLCMDPASSWORD')
    if not password:
        raise RuntimeError('SQLCMDPASSWORD für die eigene Instanz fehlt')
    run_sql(target, database='master', sql_text=(
        f"IF SUSER_ID(N'{login}') IS NOT NULL THROW 51990,'FOREIGN_LOGIN_EXISTS',1; "
        f"CREATE LOGIN [{login}] WITH PASSWORD={ownership.literal(password)},CHECK_POLICY=OFF;"))
    try:
        output = run_sql(target, database='master', sql_text=(
            f"EXECUTE AS LOGIN=N'{login}';\n" + render(preflight) + '\nGO\nREVERT;'))
        records = [line.strip().split('|') for line in output.splitlines()]
        if not any(len(row) == 8 and row[2:5] == ['SUMMARY', 'SKIP', 'SKIP_PERMISSION'] for row in records):
            raise RuntimeError('Fehlende Diagnoseberechtigung ergibt keinen kontrollierten Skip')
    finally:
        run_sql(target, database='master', sql_text=f'DROP LOGIN [{login}];')
    ownership.absent(target, DEMO)
    print(f'CON005_TEST|INPUT_SAFETY_PERMISSION|PASS|INVALID_INPUTS={(len(invalid)+1)*2}', flush=True)
    normalized_lifecycle(target)


def evidence_rejections(target: ExecutionTarget) -> None:
    execute(target, '10_Setup.sql')
    try:
        require_error(target, source('40_Observation.sql'), 51006, database=DATABASE)
        require_error(target, "EXEC fwk.USP_WaitForSignal @DemoId='CON-005',@RunToken='LOCAL',@SignalName='MISSING',@TimeoutMs=100;", 51005, database=DATABASE)
        for invalid_timeout in ('NULL', '0', '30001'):
            require_error(target, "EXEC fwk.USP_WaitForSignal @DemoId='CON-005',@RunToken='LOCAL',@SignalName='MISSING',@TimeoutMs=" + invalid_timeout + ';', 51000, database=DATABASE)
        result = subprocess.run([sys.executable, str(TOOLS / 'orchestrate_sessions.py'),
                                 str(DIRECTORY / 'Sessions/problem.json'), *target.connection_arguments(),
                                 '--database', DATABASE], capture_output=True, text=True,
                                encoding='utf-8', errors='replace', env=target.child_environment(), timeout=90)
        if result.returncode or SUMMARY.findall(result.stdout)[-1:] != [('PASS', 'OK')]:
            raise RuntimeError('Evidenzgrundlage fehlt: ' + ownership_execution_redact(result.stdout + result.stderr)[-3000:])
        execute(target, '40_Observation.sql', database=DATABASE)
        mutations = {'DatabaseId': 'DatabaseId+1', 'ObjectId': 'ObjectId+1',
                     'BlockingSessionId': 'ReaderSessionId', 'ReaderSessionId': 'BlockerSessionId',
                     'WaitType': "N'LCK_M_X'", 'GrantedMode': "N'X'", 'GrantedStatus': "N'WAIT'",
                     'WaitingMode': "N'S'", 'WaitingStatus': "N'GRANT'", 'ResourceType': "N'PAGE'",
                     'BlockerSessionId': 'BlockerSessionId+1000,BlockingSessionId=BlockingSessionId+1000,ReaderSessionId=ReaderSessionId+1000'}
        for column, replacement in mutations.items():
            # Jede Gegenprobe wird zurückgerollt; danach ist der echte Beleg wieder da.
            check = source('40_Observation.sql')
            output = run_sql(target, database=DATABASE, sql_text=(
                f"SET NOCOUNT ON; BEGIN TRAN; UPDATE lab.SchemaEvidence SET {column}={replacement}; "
                "DECLARE @Error int=NULL; BEGIN TRY EXEC sys.sp_executesql " + ownership.literal(check.replace(
                    "IF @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2 THROW 51002,'FAIL_STATE: Keine explizite oder implizite Transaktion am Einstieg erlaubt.',1;", '')) +
                "; END TRY BEGIN CATCH SET @Error=ERROR_NUMBER(); END CATCH; "
                "IF XACT_STATE()<>0 ROLLBACK; IF @Error IS NULL OR @Error<>51006 THROW 51992,'WEAK_EVIDENCE_ACCEPTED',1; SELECT 'REJECTED';"))
            if output.split() != ['REJECTED']:
                raise RuntimeError('Falscher Evidenzvertrag: ' + column)
        execute(target, '40_Observation.sql', database=DATABASE)
        print(f'CON005_TEST|EVIDENCE_FAIL_CLOSED|PASS|MUTATIONS={len(mutations)}', flush=True)
    finally:
        execute(target, '90_Cleanup.sql')
        ownership.absent(target, DEMO)


def timeout_cleanup(target: ExecutionTarget) -> None:
    temp_root = ROOT / 'Runtime/Temp'
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='con005-timeout-', dir=temp_root) as temporary:
        path = Path(temporary).resolve()
        if not path.is_relative_to(temp_root.resolve()):
            raise RuntimeError('Temporärer Prüfpfad außerhalb des erlaubten Bereichs')
        shutil.copytree(DIRECTORY, path / 'demo')
        fixture = path / 'demo'
        observer = fixture / 'Sessions/30_Observer.sql'
        text = observer.read_text(encoding='utf-8-sig')
        release = "EXEC fwk.USP_Signal @DemoId='CON-005',@RunToken=@Run,@SignalName='RELEASE_BLOCKER';"
        if text.count(release) != 1:
            raise RuntimeError('Unbekannte Beobachterform für den Abbruchfall')
        observer.write_text(text.replace(release, "EXEC fwk.USP_WaitForSignal @DemoId='CON-005',@RunToken='$(RunToken)',@SignalName='NEVER_RELEASED',@TimeoutMs=15000;\n" + release), encoding='utf-8')
        manifest_path = fixture / 'manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
        for phase in manifest['phases']:
            if phase['id'] == 'DEMONSTRATION':
                phase['timeout_seconds'] = 6
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        process = subprocess.Popen(command(target, manifest_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, encoding='utf-8', errors='replace', env=target.child_environment())
        observed_held_conflict = False
        try:
            deadline = time.monotonic() + 30
            while process.poll() is None and time.monotonic() < deadline:
                output = run_sql(target, database='master', timeout_seconds=5, sql_text=f"""
SET NOCOUNT ON;
IF EXISTS(SELECT 1 FROM sys.dm_tran_locks l JOIN sys.dm_exec_requests r ON r.blocking_session_id=l.request_session_id
 WHERE l.resource_database_id=DB_ID(N'{DATABASE}') AND r.database_id=l.resource_database_id
 AND l.resource_type=N'OBJECT' AND l.request_mode=N'Sch-M' AND l.request_status=N'GRANT'
 AND r.wait_type=N'LCK_M_SCH_S') SELECT 'HELD_CONFLICT';
""")
                if output.split() == ['HELD_CONFLICT']:
                    observed_held_conflict = True
                    break
                time.sleep(0.1)
            stdout, stderr = process.communicate(timeout=120)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=30)
                execute(target, '90_Cleanup.sql')
        require_harness(subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr), ('FAIL', 'FAIL_TIMEOUT'))
        if not observed_held_conflict:
            raise RuntimeError('Timeout ohne unabhängig beobachteten gehaltenen Sch-M-/Sch-S-Konflikt')
        ownership.absent(target, DEMO)
    print('CON005_TEST|TIMEOUT_HELD_SCHEMA_LOCK|PASS|CLEANUP_ABSENT', flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True)
    parser.add_argument('--expected-major', type=int, choices=(15, 16, 17), required=True)
    parser.add_argument('--confirm-disposable-instance', action='store_true', required=True,
                        help='Bestätigt die ausschließlich eigene Wegwerfinstanz ohne fremde Daten.')
    args = parser.parse_args()
    try:
        target = docker_target(container=args.container)
        verify_engine(target, expected_major=args.expected_major)
        lifecycles(target)
        protection(target)
        inputs_and_permissions(target)
        evidence_rejections(target)
        timeout_cleanup(target)
        print(f'CON005_TEST|SQL_{args.expected_major}|PASS|ALL_REQUIRED_CASES')
        return 0
    except (ExecutionTargetError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print('CON005_TEST|FAIL|' + ownership_execution_redact(str(exc)), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
