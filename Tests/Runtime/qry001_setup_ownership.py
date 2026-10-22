"""Setup-Eigentumsgegenproben für indexfreundliche Suchbedingungen im Dockerziel."""
from __future__ import annotations

from pathlib import Path
import re

import qry001_cleanup_ownership as ownership
from execution_target import DOCKER, ExecutionTarget, ExecutionTargetError, run_sql

ROOT = Path(__file__).resolve().parents[2]
SETUP = ROOT / "Demos/05_Query_Patterns/QRY-001_SARGability/10_Setup.sql"
DATABASE = ownership.DATABASE


def require_setup_success(output: str) -> None:
    expected = ["1", "SETUP", "SUMMARY", "PASS", "OK"]
    rows = [line.strip().split("|") for line in output.splitlines()]
    if sum(row[:5] == expected for row in rows) != 1:
        raise ownership.OwnershipFailure("Eindeutige strukturierte Setup-Ergebniszeile fehlt")


def require_setup_rejection(target: ExecutionTarget, sql: str, code: int = 51002) -> None:
    expected = {51000: "FAIL_CONTRACT", 51002: "FAIL_STATE"}[code]
    try:
        run_sql(target, database="master", sql_text=sql)
    except ExecutionTargetError as exc:
        if re.search(rf"\b{code}\b", str(exc)) and expected in str(exc):
            return
        raise ownership.OwnershipFailure("Setup lieferte nicht den erwarteten Eigentumsfehler") from exc
    raise ownership.OwnershipFailure("Setup akzeptierte eine ungültige Eigentumskennung")


def config_snapshot(target: ExecutionTarget) -> str:
    output = run_sql(target, database="master", sql_text=f"""
SET NOCOUNT ON;
SELECT N'CONFIG',database_id,recovery_model_desc,is_auto_close_on,is_auto_shrink_on,
       page_verify_option,compatibility_level
FROM sys.databases WHERE name=N'{DATABASE}';
""")
    rows = [line.strip() for line in output.splitlines() if line.strip()]
    if len(rows) != 1 or len(rows[0].split("|")) != 7 or not rows[0].startswith("CONFIG|"):
        raise ownership.OwnershipFailure(f"Eindeutiger Konfigurationsnachweis fehlt: {rows!r}")
    return rows[0]


def lab_snapshot(target: ExecutionTarget) -> str:
    output = run_sql(target, database="master", sql_text=f"""
SELECT N'LAB_SEARCH',SentinelValue FROM [{DATABASE}].lab.SearchData;
SELECT N'LAB_EVIDENCE',SentinelValue FROM [{DATABASE}].lab.Qry001Evidence;
SELECT N'TABLE',s.schema_id,s.name,t.name,t.object_id
FROM [{DATABASE}].sys.tables t JOIN [{DATABASE}].sys.schemas s ON s.schema_id=t.schema_id
WHERE s.name=N'lab' ORDER BY t.name;
SELECT N'COLUMN',c.object_id,c.column_id,c.name,c.user_type_id,c.max_length,c.is_nullable
FROM [{DATABASE}].sys.columns c JOIN [{DATABASE}].sys.tables t ON t.object_id=c.object_id
JOIN [{DATABASE}].sys.schemas s ON s.schema_id=t.schema_id
WHERE s.name=N'lab' ORDER BY t.name,c.column_id;
""")
    rows = [line.strip() for line in output.splitlines() if line.strip()]
    if rows.count("LAB_SEARCH|919") != 1 or rows.count("LAB_EVIDENCE|919") != 1:
        raise ownership.OwnershipFailure("Synthetische Prüfzeilen vor/nach Ablehnung fehlen")
    return "\n".join(rows)


def preservation_snapshot(target: ExecutionTarget) -> str:
    return "\n".join((ownership.snapshot(target), config_snapshot(target), lab_snapshot(target)))


def prepare_fixture(target: ExecutionTarget, values: dict[str, str], *, object_only=False, auto_close=False) -> None:
    ownership.require_absent(target)
    ownership.require_absent(target, DATABASE + "X")
    run_sql(target, database="master", sql_text=f"""
CREATE DATABASE [{DATABASE}];
ALTER DATABASE [{DATABASE}] SET RECOVERY FULL;
ALTER DATABASE [{DATABASE}] SET AUTO_SHRINK ON;
ALTER DATABASE [{DATABASE}] SET PAGE_VERIFY NONE;
ALTER DATABASE [{DATABASE}] SET COMPATIBILITY_LEVEL=140;
""")
    run_sql(target, database=DATABASE, sql_text="""
EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
CREATE TABLE dbo.OwnershipProbe(Value int NOT NULL);
INSERT dbo.OwnershipProbe VALUES(73);
-- Die Basisspalten erhalten die Kompilierbarkeit des vollständigen Setup-
-- Batches. Zusätzliche Sentinelspalten und eigene Zeilen weisen Ersatz nach.
CREATE TABLE lab.SearchData(
    SearchId int NOT NULL, EventDateTime datetime2(0) NOT NULL,
    MeasureValue int NOT NULL, Payload char(40) NOT NULL,
    SentinelValue int NOT NULL DEFAULT 919);
INSERT lab.SearchData VALUES(919,'20230101',73,REPLICATE('X',40),919);
CREATE TABLE lab.Qry001Evidence(
    Phase varchar(20) NOT NULL, ResultValue bigint NOT NULL,
    LogicalReads bigint NOT NULL, AccessMethod varchar(32) NOT NULL,
    CapturedAtUtc datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
    SentinelValue int NOT NULL DEFAULT 919);
INSERT lab.Qry001Evidence(Phase,ResultValue,LogicalReads,AccessMethod,SentinelValue)
VALUES('SYNTHETIC',73,0,'SYNTHETIC',919);
""")
    ownership.set_markers(target, values, object_only=object_only)
    if auto_close:
        run_sql(target, database="master", sql_text=f"ALTER DATABASE [{DATABASE}] SET AUTO_CLOSE ON;")


def finish_fixture(target: ExecutionTarget) -> None:
    # Erst nach dem Erhaltungs-/Altfehlernachweis eigene synthetische Marker
    # passend setzen. Das unveränderte kanonische Cleanup übernimmt das Löschen.
    drops = "\n".join(
        f"IF EXISTS(SELECT 1 FROM sys.extended_properties WHERE class=0 AND name={ownership.literal(name)}) "
        f"EXEC sys.sp_dropextendedproperty @name={ownership.literal(name)};" for name in ownership.MARKERS)
    run_sql(target, database=DATABASE, sql_text=drops)
    ownership.set_markers(target, ownership.MARKERS)
    cleanup = ownership.render_cleanup(ownership.CLEANUP.read_text(encoding="utf-8"))
    for _ in range(2):
        ownership.require_cleanup_success(run_sql(target, database="master", sql_text=cleanup))
        ownership.require_absent(target)


def verify_configuration(target: ExecutionTarget, major: int) -> None:
    fields = config_snapshot(target).split("|")
    if fields[2:] != ["SIMPLE", "0", "0", "2", str(major * 10)]:
        raise ownership.OwnershipFailure("Setup hat nicht die dokumentierte Konfiguration hergestellt")


def verify_data_model(target: ExecutionTarget, major: int) -> None:
    verify_configuration(target, major)
    output = run_sql(target, database=DATABASE, sql_text="""
IF (SELECT COUNT_BIG(*) FROM lab.SearchData)<>300000 OR (SELECT COUNT_BIG(*) FROM lab.Qry001Evidence)<>0
    THROW 51003, 'FAIL_EXECUTION: Setup-Datenmodell ist unvollständig.', 1;
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SearchData') AND name=N'IX_SearchData_EventDateTime')
    THROW 51003, 'FAIL_EXECUTION: Setup-Index fehlt.', 1;
SELECT N'SETUP_DATA_MODEL_VERIFIED';
""")
    if "SETUP_DATA_MODEL_VERIFIED" not in output.split():
        raise ownership.OwnershipFailure("Unabhängiger Datenmodellnachweis fehlt")


def run_setup_ownership_probes(target: ExecutionTarget, major: int) -> int:
    if target.kind != DOCKER or not target.container:
        raise ownership.OwnershipFailure("Setup-Gegenproben benötigen ein eigenes Dockerziel")
    if major not in (15, 16, 17):
        raise ownership.OwnershipFailure("Setup-Gegenprobe benötigt eine unterstützte Hauptversion")
    source = SETUP.read_text(encoding="utf-8")
    cases = [(label, values, obj, wrong, False) for label, values, obj, wrong in ownership.negative_cases()]
    cases.append(("AUTO_CLOSE_ON", {**ownership.MARKERS, "SQLPERF.Project": "WRONG"}, False, False, True))
    for label, values, object_only, wrong_target, auto_close in cases:
        prepare_fixture(target, values, object_only=object_only, auto_close=auto_close)
        before = preservation_snapshot(target)
        sql = ownership.render_cleanup(source, DATABASE + "X" if wrong_target else DATABASE)
        require_setup_rejection(target, sql, 51000 if wrong_target else 51002)
        if preservation_snapshot(target) != before:
            raise ownership.OwnershipFailure(f"{label}: Setup änderte Zustand vor Eigentumsnachweis")
        finish_fixture(target)
        print(f"GATE_B_SETUP_OWNERSHIP|{label}|PASS|PRESERVED_ACROSS_GO")

    # Die vollständige Datei einschließlich GO wird vom echten sqlcmd -b gelesen.
    prepare_fixture(target, dict(ownership.MARKERS))
    before = ownership.snapshot(target)
    for _ in range(2):
        require_setup_success(run_sql(target, database="master", sql_text=ownership.render_cleanup(source)))
        if ownership.snapshot(target) != before:
            raise ownership.OwnershipFailure("Passende Wiederverwendung änderte Datenbankidentität oder Marker")
        verify_data_model(target, major)
    finish_fixture(target)
    print("GATE_B_SETUP_OWNERSHIP|MATCHING_REPEAT|PASS|SAME_DATABASE_AND_MODEL")

    ownership.require_absent(target)
    require_setup_success(run_sql(target, database="master", sql_text=ownership.render_cleanup(source)))
    verify_data_model(target, major)
    # Bei Neuanlage Marker nicht nachträglich ergänzen: Cleanup muss die vom
    # echten Setup erzeugten Marker selbst akzeptieren.
    cleanup = ownership.render_cleanup(ownership.CLEANUP.read_text(encoding="utf-8"))
    for _ in range(2):
        ownership.require_cleanup_success(run_sql(target, database="master", sql_text=cleanup))
        ownership.require_absent(target)
    print("GATE_B_SETUP_OWNERSHIP|ABSENT_CREATE|PASS|MODEL_MARKERS_AND_ABSENCE")
    return len(cases) + 2
