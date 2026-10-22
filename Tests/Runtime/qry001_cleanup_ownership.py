"""Eigentumsgegenproben ausschließlich im wegwerfbaren Gate-B-Dockerziel."""
from __future__ import annotations

from pathlib import Path
import re

from execution_target import DOCKER, ExecutionTarget, ExecutionTargetError, run_sql

ROOT = Path(__file__).resolve().parents[2]
CLEANUP = ROOT / "Demos/05_Query_Patterns/QRY-001_SARGability/90_Cleanup.sql"
TOKEN = "OWNERSHIP"
DATABASE = f"SQLPERF_LAB_QRY001_{TOKEN}"
MARKERS = {
    "SQLPERF.Project": "SQL_PerformanceSchulung",
    "SQLPERF.ContractVersion": "1.0",
    "SQLPERF.DemoId": "QRY-001",
    "SQLPERF.RunToken": TOKEN,
}


class OwnershipFailure(RuntimeError):
    pass


def literal(value: str) -> str:
    return "N'" + value.replace("'", "''") + "'"


def render_cleanup(source: str, target: str = DATABASE) -> str:
    for key, value in {"DemoId": "QRY-001", "RunToken": TOKEN, "TargetDatabase": target}.items():
        source = source.replace(f"$({key})", value)
    if re.search(r"\$\([^)]+\)", source):
        raise OwnershipFailure("Unaufgelöster sqlcmd-Platzhalter in der Gegenprobe")
    return source


def require_absent(target: ExecutionTarget, database: str = DATABASE) -> None:
    output = run_sql(target, database="master", sql_text=(
        f"IF DB_ID({literal(database)}) IS NOT NULL "
        "THROW 51004, 'FAIL_CLEANUP: Probe-Datenbank ist noch vorhanden.', 1; "
        "SELECT N'OWNERSHIP_ABSENT';"))
    if "OWNERSHIP_ABSENT" not in output.split():
        raise OwnershipFailure("Unabhängiger Absenznachweis fehlt")


def snapshot(target: ExecutionTarget) -> str:
    # ID, Zugriffszustand, Sentinel und alle Property-Werte einschließlich
    # Typ und vollständigen Unicodebytes müssen vor/nach Ablehnung gleich sein.
    # Begrenzte Fixtures: maximal 4000 Bytes, also höchstens 8000 Hexzeichen.
    # varchar(8000) vermeidet sqlcmds 256-Zeichen-Limit für varchar(max).
    output = run_sql(target, database="master", sql_text=f"""
IF DB_ID(N'{DATABASE}') IS NULL
    THROW 51004, 'FAIL_CLEANUP: Probe-Datenbank wurde entfernt.', 1;
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name=N'{DATABASE}'
               AND state_desc=N'ONLINE' AND user_access_desc=N'MULTI_USER')
    THROW 51004, 'FAIL_CLEANUP: Probe-Datenbankzustand wurde verändert.', 1;
SELECT N'DATABASE',database_id,state_desc,user_access_desc
FROM sys.databases WHERE name=N'{DATABASE}';
SELECT N'SENTINEL',Value FROM [{DATABASE}].dbo.OwnershipProbe;
IF EXISTS(SELECT 1 FROM [{DATABASE}].sys.extended_properties
          WHERE DATALENGTH(CONVERT(nvarchar(max),value))>4000)
    THROW 51004, 'FAIL_CLEANUP: Probe-Marker überschreitet die Snapshotgrenze.', 1;
SELECT N'MARKER',class,major_id,minor_id,name,
       SQL_VARIANT_PROPERTY(value,'BaseType'),
       CONVERT(varchar(8000),CONVERT(varbinary(max),CONVERT(nvarchar(max),value)),2)
FROM [{DATABASE}].sys.extended_properties ORDER BY class,major_id,minor_id,name;
""")
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if "SENTINEL|73" not in lines:
        raise OwnershipFailure("Synthetischer Sentinel fehlt")
    return "\n".join(lines)


def set_markers(target: ExecutionTarget, values: dict[str, str], *, object_only: bool = False) -> None:
    scope = (",@level0type=N'SCHEMA',@level0name=N'dbo',"
             "@level1type=N'TABLE',@level1name=N'OwnershipProbe'") if object_only else ""
    statements = [
        f"EXEC sys.sp_addextendedproperty @name={literal(name)},@value={literal(value)}{scope};"
        for name, value in values.items()
    ]
    if statements:
        run_sql(target, database=DATABASE, sql_text="\n".join(statements))


def require_rejection(target: ExecutionTarget, sql: str, code: int) -> None:
    try:
        run_sql(target, database="master", sql_text=sql)
    except ExecutionTargetError as exc:
        text = str(exc)
        expected = "FAIL_CONTRACT" if code == 51000 else "FAIL_CLEANUP"
        if re.search(rf"\b{code}\b", text) and expected in text:
            return
        raise OwnershipFailure("Gegenprobe lieferte nicht den erwarteten Schutzfehler") from exc
    # Auch ein erfolgreicher Aufruf muss zuerst die reale Absenz/Veränderung
    # feststellen können. Die alte Quelle scheitert hier am Datenbankverlust.
    snapshot(target)
    raise OwnershipFailure("Ungültige Marker wurden ohne Schutzfehler akzeptiert")


def require_cleanup_success(output: str) -> None:
    # sqlcmd -r 1 leitet PRINT nach stderr. run_sql liefert im Erfolgsfall
    # stdout; deshalb die strukturierte SELECT-Zeile statt PRINT auswerten.
    expected = ["1", "CLEANUP", "SUMMARY", "PASS", "OK"]
    rows = [line.strip().split("|") for line in output.splitlines()]
    if sum(row[:5] == expected for row in rows) != 1:
        raise OwnershipFailure("Eindeutige strukturierte Cleanup-Ergebniszeile fehlt")


def negative_cases() -> list[tuple[str, dict[str, str], bool, bool]]:
    cases = [("ALL_MISSING", {}, False, False)]
    for name, value in MARKERS.items():
        cases.append(("MISSING_" + name, {k: v for k, v in MARKERS.items() if k != name}, False, False))
        variants = {"WRONG": "WRONG", "EMPTY": "", "SPACE": value + " ", "LONG": value + "X" * 128}
        if value.lower() != value:
            variants["CASE"] = value.lower()
        for kind, replacement in variants.items():
            cases.append((kind + "_" + name, {**MARKERS, name: replacement}, False, False))
    cases.extend([("OBJECT_ONLY", dict(MARKERS), True, False),
                  ("WRONG_TARGET", dict(MARKERS), False, True)])
    return cases


def verify_snapshot_width(target: ExecutionTarget, cleanup: str) -> None:
    # Zwei Werte mit gleichem ersten 128-Zeichen-Präfix müssen sich im
    # transportierten Snapshot unterscheiden. Ein gekürztes Oracle scheitert.
    require_absent(target)
    run_sql(target, database="master", sql_text=f"CREATE DATABASE [{DATABASE}];")
    run_sql(target, database=DATABASE, sql_text=(
        "CREATE TABLE dbo.OwnershipProbe(Value int NOT NULL); INSERT dbo.OwnershipProbe VALUES(73);"))
    set_markers(target, {"SQLPERF.Project": "X" * 128 + "A"})
    before = snapshot(target)
    run_sql(target, database=DATABASE, sql_text=(
        "EXEC sys.sp_updateextendedproperty @name=N'SQLPERF.Project',"
        f"@value={literal('X' * 128 + 'B')};"))
    if snapshot(target) == before:
        raise OwnershipFailure("Markerunterschied hinter der Anzeigegrenze wurde nicht erkannt")
    run_sql(target, database=DATABASE, sql_text=(
        "EXEC sys.sp_dropextendedproperty @name=N'SQLPERF.Project';"))
    set_markers(target, MARKERS)
    for _ in range(2):
        require_cleanup_success(run_sql(target, database="master", sql_text=render_cleanup(cleanup)))
        require_absent(target)
    print("GATE_B_OWNERSHIP|SNAPSHOT_SUFFIX|PASS|COMPLETE_MARKER_BYTES")


def run_ownership_probes(target: ExecutionTarget, *, source: str | None = None) -> int:
    if target.kind != DOCKER or not target.container:
        raise OwnershipFailure("Destruktive Eigentumsgegenproben benötigen ein eigenes Dockerziel")
    cleanup = CLEANUP.read_text(encoding="utf-8") if source is None else source
    verify_snapshot_width(target, cleanup)
    cases = [("MATCHING", dict(MARKERS), False, False), *negative_cases()]
    for label, values, object_only, wrong_target in cases:
        require_absent(target)
        require_absent(target, DATABASE + "X")
        run_sql(target, database="master", sql_text=f"CREATE DATABASE [{DATABASE}];")
        run_sql(target, database=DATABASE, sql_text=(
            "CREATE TABLE dbo.OwnershipProbe(Value int NOT NULL); "
            "INSERT dbo.OwnershipProbe VALUES(73);"))
        set_markers(target, values, object_only=object_only)
        if label != "MATCHING":
            before = snapshot(target)
            sql = render_cleanup(cleanup, DATABASE + "X" if wrong_target else DATABASE)
            require_rejection(target, sql, 51000 if wrong_target else 51004)
            if snapshot(target) != before:
                raise OwnershipFailure(f"{label}: Datenbank oder Marker nach Ablehnung verändert")
            # Erst NACH dem Erhaltungsnachweis die eigenen synthetischen Marker
            # passend setzen; keine alternative ungeprüfte DROP-Anweisung.
            drops = "\n".join(
                f"IF EXISTS(SELECT 1 FROM sys.extended_properties WHERE class=0 AND name={literal(name)}) "
                f"EXEC sys.sp_dropextendedproperty @name={literal(name)};" for name in MARKERS)
            run_sql(target, database=DATABASE, sql_text=drops)
            set_markers(target, MARKERS)
        for _ in range(2):
            output = run_sql(target, database="master", sql_text=render_cleanup(cleanup))
            require_cleanup_success(output)
            require_absent(target)
        print(f"GATE_B_OWNERSHIP|{label}|PASS|PRESERVED_AND_CLEANED")
    return len(cases)
