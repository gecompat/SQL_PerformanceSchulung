#!/usr/bin/env python3
"""Prueft QRY-014 bis QRY-019 und DGN-008/009 zweimal mit FWK-010 und FWK-011."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "Demos/00_Framework/Tools"
sys.path.insert(0, str(TOOLS))
import evaluate_result_contract as evaluator
import execution_target as targets

DEMOS = {
    "QRY-014": "QRY-014_Vector_Type",
    "QRY-015": "QRY-015_Vector_Metrics",
    "QRY-016": "QRY-016_Chunk_Provenance",
    "QRY-017": "QRY-017_Search_Comparison",
    "QRY-018": "QRY-018_Offline_RAG",
    "QRY-019": "QRY-019_SQL_Input_Policy",
    "DGN-009": "DGN-009_Offline_Injection",
    "DGN-008": "DGN-008_Offline_Model_Rights",
    "CON-010": "CON-010_Tenant_Isolation",
}
SUMMARY = re.compile(r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$", re.MULTILINE)
RECORD = re.compile(r"^AI_ASSERT\|(baseline|comparison)\|([a-z][a-z0-9_]*)\|([^|]+)$")


class AiFailure(RuntimeError):
    """Fehlender oder verletzter Runtime-Nachweis."""


def evidence_from_output(output: str, demo_id: str) -> dict:
    evidence = {"contract_version": "1.0", "demo_id": demo_id,
                "profile": "LOCAL", "baseline": {}, "comparison": {}}
    for line in output.splitlines():
        # FWK-010 beschriftet den Output jeder SQL-Phase.
        line = re.sub(r"^\[[A-Z_]+:(?:stdout|stderr)\] ", "", line.strip())
        if not line.startswith("AI_ASSERT|"):
            continue
        match = RECORD.fullmatch(line)
        if not match:
            raise AiFailure("ungueltiger AI_ASSERT-Datensatz")
        phase, metric, value = match.groups()
        if metric in evidence[phase]:
            raise AiFailure("doppelte Assertion-Evidenz")
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise AiFailure("Assertion-Evidenz ist nicht numerisch") from exc
        if not number.is_finite():
            raise AiFailure("Assertion-Evidenz ist nicht endlich")
        evidence[phase][metric] = number
    return evidence


def assert_result(output: str, returncode: int, major: int, demo_id: str, contract: dict) -> int:
    summaries = SUMMARY.findall(output)
    final = summaries[-1] if summaries else None
    if major in (15, 16):
        if returncode != 0 or final != ("SKIP", "SKIP_VERSION"):
            raise AiFailure(f"{demo_id}: erwarteter Versions-Skip fehlt: {final}")
        if "AI_ASSERT|" in output or "[SETUP:" in output:
            raise AiFailure("Versions-Skip hat fachliche Folgephasen ausgefuehrt")
        return 0
    allowed = {("PASS", "OK")}
    if demo_id == "QRY-017":
        allowed.add(("WARN", "WARN_OPTIONAL_EVIDENCE_SKIPPED"))
    if major != 17 or returncode != 0 or final not in allowed:
        raise AiFailure(f"{demo_id}: unerwartetes Ergebnis: {final}, rc={returncode}")
    evidence = evidence_from_output(output, demo_id)
    if demo_id == "QRY-017":
        installed = evidence["comparison"].get("fulltext_installed")
        if installed not in (Decimal(0), Decimal(1)):
            raise AiFailure("Full-Text-Voraussetzung fehlt oder ist ungueltig")
        expected = (("WARN", "WARN_OPTIONAL_EVIDENCE_SKIPPED") if installed == 0 else ("PASS", "OK"))
        if final != expected:
            raise AiFailure("Full-Text-Ergebnis stimmt nicht mit der gemessenen Voraussetzung ueberein")
    evaluator.validate_metadata(contract, evidence)
    assertions = contract.get("assertions", [])
    if not assertions:
        raise AiFailure("leerer Ergebnisvertrag")
    results = [evaluator.evaluate_assertion(assertion, evidence) for assertion in assertions]
    failures = [result.assertion_id for result in results if result.outcome != "PASS"]
    if failures:
        raise AiFailure("verletzte Ergebnisassertionen: " + ", ".join(failures))
    return len(results)


def assert_absent(target: targets.ExecutionTarget, demo_id: str) -> None:
    name = "SQLPERF_LAB_" + demo_id.replace("-", "") + "_LOCAL"
    output = targets.run_sql(target, database="master", timeout_seconds=30,
        sql_text=f"SET NOCOUNT ON; IF DB_ID(N'{name}') IS NOT NULL THROW 51004, 'FAIL_STATE: Ziel ist vorhanden.', 1; SELECT N'AI_DB_ABSENT';")
    if output.strip() != "AI_DB_ABSENT":
        raise AiFailure("unabhaengiger Abwesenheitsnachweis fehlt")


def run_demo(target: targets.ExecutionTarget, major: int, demo_id: str, repetition: int) -> tuple[str, str]:
    directory = ROOT / "Demos/09_AI_SQL_Server_2025" / DEMOS[demo_id]
    assert_absent(target, demo_id)  # Keine Uebernahme vorhandener Datenbanken.
    command = [sys.executable, str(TOOLS / "run_demo.py"), str(directory / "manifest.json"),
               *target.connection_arguments(), "--show-output"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=target.child_environment(), timeout=300)
    output = result.stdout + "\n" + result.stderr
    # Cleanup wird auch bei einem fachlichen FAIL unabhaengig geprueft.
    assert_absent(target, demo_id)
    try:
        count = assert_result(output, result.returncode, major, demo_id,
                              evaluator.load_json(directory / "Expected/result-contract.json"))
    except (AiFailure, evaluator.ContractError) as exc:
        raise AiFailure(f"{exc}\n{targets.redact(output[-7000:])}") from exc
    status, code = SUMMARY.findall(output)[-1]
    print(f"AI_LOCAL|{demo_id}|RUN_{repetition}|{status}|{code}|ASSERTIONS_{count}|CLEANUP_ABSENT")
    return status, code


def ownership_controls(target: targets.ExecutionTarget, demo_id: str) -> None:
    """Prueft NULL-/Falschmarker vor Preflight, Setup und Cleanup auf eigener Fixture."""
    directory = ROOT / "Demos/09_AI_SQL_Server_2025" / DEMOS[demo_id]
    if demo_id == "CON-010":
        from con010_controls import run
        run(target, directory)
        return
    name = "SQLPERF_LAB_" + demo_id.replace("-", "") + "_LOCAL"
    markers = {"SQLPERF.Project": "SQL_PerformanceSchulung",
               "SQLPERF.ContractVersion": "1.0", "SQLPERF.DemoId": demo_id,
               "SQLPERF.RunToken": "LOCAL"}

    def phase(filename: str) -> str:
        text = (directory / filename).read_text(encoding="utf-8")
        for key, value in {"DemoId": demo_id, "RunToken": "LOCAL", "TargetDatabase": name}.items():
            text = text.replace("$(" + key + ")", value)
        database = "master" if filename[:2] in ("00", "10", "90") else name
        return targets.run_sql(target, database=database, sql_text=text, timeout_seconds=60)

    def state(*, stable_setup: bool = False) -> str:
        if demo_id == "DGN-008":
            times = "" if stable_setup else ",external_model_id,create_time,modify_time"
            return targets.run_sql(target, database=name, sql_text="SET NOCOUNT ON; SELECT Id,FactDays FROM lab.Sources ORDER BY Id; SELECT Id,CONVERT(varchar(max),CONVERT(varbinary(max),Location),2),CONVERT(varchar(max),CONVERT(varbinary(max),CredentialAlias),2) FROM lab.EndpointPolicy ORDER BY Id; SELECT Id,CONVERT(varchar(max),CONVERT(varbinary(max),Location),2) FROM lab.EndpointCandidates ORDER BY Id; SELECT name,USER_NAME(principal_id),location,api_format,model_type_id,model_type_desc,model,credential_id,CONVERT(nvarchar(max),parameters)" + times + " FROM sys.external_models ORDER BY name; SELECT name,USER_NAME(principal_id),location,api_format,model_type_id,model_type_desc,model,credential_id,ParametersText" + times + " FROM lab.ModelBinding ORDER BY name; SELECT USER_NAME(grantee_principal_id),class,CASE WHEN class=110 THEN (SELECT name FROM sys.external_models WHERE external_model_id=major_id) WHEN class=1 THEN OBJECT_NAME(major_id) ELSE CONVERT(nvarchar(20),major_id) END,minor_id,permission_name,state,USER_NAME(grantor_principal_id) FROM sys.database_permissions WHERE grantee_principal_id IN(USER_ID(N'DGN008_setup'),USER_ID(N'DGN008_ingestion'),USER_ID(N'DGN008_reader'),DATABASE_PRINCIPAL_ID(N'DGN008_setupRole'),DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole')) ORDER BY USER_NAME(grantee_principal_id),class,permission_name,major_id; SELECT USER_NAME(role_principal_id),USER_NAME(member_principal_id) FROM sys.database_role_members ORDER BY USER_NAME(role_principal_id),USER_NAME(member_principal_id); SELECT NameBytes,ConfiguredValue,ActiveValue FROM lab.HostOptions ORDER BY NameBytes; SELECT CONVERT(varbinary(256),name),value,value_in_use FROM sys.configurations ORDER BY name; SELECT compatibility_level,recovery_model_desc FROM sys.databases WHERE database_id=DB_ID(); SELECT file_id,size,max_size,growth FROM sys.database_files ORDER BY file_id;", timeout_seconds=30)
        if demo_id == "DGN-009":
            return targets.run_sql(target, database=name, sql_text="SET NOCOUNT ON; SELECT SourceId,Version,IsCurrent,Trusted,FactDays,CONVERT(varchar(max),HASHBYTES('SHA2_256',CONVERT(varbinary(max),Content)),2),CONVERT(varchar(max),V) FROM lab.Documents ORDER BY SourceId; SELECT USER_NAME(grantee_principal_id),class,OBJECT_NAME(major_id),minor_id,permission_name,state FROM sys.database_permissions WHERE grantee_principal_id IN(USER_ID(N'DGN009_reader'),USER_ID(N'DGN009_sink')) ORDER BY USER_NAME(grantee_principal_id),class,permission_name; SELECT compatibility_level,recovery_model_desc FROM sys.databases WHERE database_id=DB_ID(); SELECT file_id,size,max_size,growth FROM sys.database_files ORDER BY file_id;", timeout_seconds=30)
        fixture = "Inventory" if demo_id == "QRY-019" else "VectorFixture"
        return targets.run_sql(target, database="master", sql_text=f"SET NOCOUNT ON; SELECT compatibility_level,recovery_model_desc FROM sys.databases WHERE name=N'{name}'; SELECT COUNT(*) FROM [{name}].lab.{fixture}; SELECT file_id,size,max_size,growth FROM sys.master_files WHERE database_id=DB_ID(N'{name}') ORDER BY file_id;", timeout_seconds=30)

    assert_absent(target, demo_id)
    try:
        phase("10_Setup.sql")
        before = state(stable_setup=True)
        phase("10_Setup.sql")
        if state(stable_setup=True) != before:
            raise AiFailure("idempotentes Setup hat Fixture oder Konfiguration veraendert")
        # Frisch angelegte Modell-IDs/Zeitstempel duerfen beim Setup wechseln;
        # alle Markergegenproben binden danach auch diese vollstaendigen Werte.
        before = state()
        negatives = ("00_Preflight.sql", "10_Setup.sql", "90_Cleanup.sql")
        if demo_id in ("QRY-016", "QRY-018", "QRY-019", "DGN-008", "DGN-009"):
            negatives += ("20_Baseline.sql", "30_Demonstration.sql")
        for marker, value in markers.items():
            for invalid in (None, "FOREIGN", value + " ", value + "X" * 256):
                missing = invalid is None
                mutation = (f"EXEC sys.sp_dropextendedproperty @name=N'{marker}';" if missing else
                            f"EXEC sys.sp_updateextendedproperty @name=N'{marker}',@value=N'{invalid}';")
                targets.run_sql(target, database=name, sql_text=mutation, timeout_seconds=30)
                try:
                    for filename in negatives:
                        try:
                            phase(filename)
                        except targets.ExecutionTargetError as exc:
                            if "51004" not in str(exc) or "FAIL_STATE" not in str(exc):
                                raise AiFailure("Marker-Gegenprobe scheiterte an anderem Fehler") from exc
                        else:
                            raise AiFailure("fehlender/falscher Marker wurde akzeptiert")
                        if state() != before:
                            raise AiFailure("Marker-Gegenprobe hat Daten oder Konfiguration veraendert")
                finally:
                    # Reparatur ausschliesslich an der hier neu erzeugten Fixture:
                    # alle drei unveraenderten Marker und die erwartete Abweichung pruefen.
                    checks = []
                    for other, expected in markers.items():
                        if other != marker:
                            checks.append(f"(SELECT CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND name=N'{other}')=CONVERT(varbinary(max),N'{expected}')")
                    changed = (f"NOT EXISTS(SELECT 1 FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND name=N'{marker}')" if missing else
                               f"(SELECT CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND name=N'{marker}')=CONVERT(varbinary(max),N'{invalid}')")
                    repair = ("sp_addextendedproperty" if missing else "sp_updateextendedproperty")
                    sql = "IF CASE WHEN (" + " AND ".join(checks + [changed]) + ") THEN 1 ELSE 0 END<>1 THROW 51004,'FAIL_STATE: Fixturebindung verloren.',1; "
                    sql += f"EXEC sys.{repair} @name=N'{marker}',@value=N'{value}';"
                    targets.run_sql(target, database=name, sql_text=sql, timeout_seconds=30)
        # Fachliche Negativkontrollen an genau dieser neu erzeugten und markierten Fixture.
        checks = [f"(SELECT CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND name=N'{key}')=CONVERT(varbinary(max),N'{value}')" for key, value in markers.items()]
        binding = "IF CASE WHEN (" + " AND ".join(checks) + ") THEN 1 ELSE 0 END<>1 THROW 51004,'FAIL_STATE: Fixturebindung verloren.',1; "

        def mutate(sql: str) -> None:
            targets.run_sql(target, database=name, sql_text=binding + sql, timeout_seconds=30)

        def rejected(filename: str) -> None:
            try:
                phase(filename)
            except targets.ExecutionTargetError as exc:
                if "51003" not in str(exc) or "FAIL_RESULT_CONTRACT" not in str(exc):
                    raise AiFailure("fachliche Gegenprobe scheiterte an anderem Fehler") from exc
            else:
                raise AiFailure("fehlende/falsche fachliche Daten wurden akzeptiert")

        if demo_id == "DGN-008":
            mutations = (
                "DELETE FROM lab.Sources;",
                "UPDATE lab.Sources SET FactDays=99 WHERE Id=1;",
                "UPDATE lab.EndpointPolicy SET CredentialAlias=N'wrong';",
                "UPDATE lab.EndpointCandidates SET Location=Location+N' ' WHERE Id=1;",
                "UPDATE lab.ModelBinding SET location=location+N' ';",
                "DROP EXTERNAL MODEL DGN008_OfflineModel;",
                "GRANT UPDATE ON OBJECT::lab.Sources TO DGN008_retrievalRole;",
                "GRANT SELECT ON OBJECT::lab.EndpointPolicy TO DGN008_retrievalRole;",
                "ALTER ROLE DGN008_ingestionRole ADD MEMBER DGN008_reader;",
                "REVOKE UPDATE ON OBJECT::lab.Sources FROM DGN008_ingestionRole;",
            )
            for mutation in mutations:
                phase("10_Setup.sql")
                phase("50_Mitigation.sql")
                mutate(mutation)
                rejected("60_Comparison.sql")
            print(f"AI_LOCAL|{demo_id}|RESULT_NEGATIVE_{len(mutations)}|PASS")
        elif demo_id == "DGN-009":
            mutations = (
                "DELETE FROM lab.Documents;",
                "UPDATE lab.Documents SET FactDays=99 WHERE SourceId=1;",
                "UPDATE lab.Documents SET Content=N'wrong' WHERE SourceId=2;",
                "UPDATE lab.Documents SET V='[0,1,0]' WHERE SourceId=1;",
                "UPDATE lab.Documents SET IsCurrent=1 WHERE SourceId=3;",
                "UPDATE lab.Documents SET Trusted=1 WHERE SourceId=2;",
                "UPDATE lab.Documents SET Version=1 WHERE SourceId=3;",
                "GRANT UPDATE ON OBJECT::lab.Documents TO [DGN009_reader];",
                "GRANT CONTROL TO [DGN009_sink];",
                "REVOKE SELECT ON OBJECT::lab.Documents FROM [DGN009_reader];",
            )
            for mutation in mutations:
                phase("10_Setup.sql")
                mutate(mutation)
                rejected("60_Comparison.sql")
            print(f"AI_LOCAL|{demo_id}|RESULT_NEGATIVE_{len(mutations)}|PASS")
        elif demo_id == "QRY-019":
            mutations = (
                "DELETE FROM lab.Candidates;",
                "DELETE FROM lab.Inventory;",
                "UPDATE lab.Inventory SET Colour=N'wrong' WHERE ModuleCode=N'MOD-A';",
                "UPDATE lab.Candidates SET StatementText=StatementText+N' ' WHERE Id=1;",
                "UPDATE lab.Candidates SET ValueText=REPLICATE(N'X',201) WHERE Id=1;",
                "UPDATE lab.Candidates SET ValueText=N'MOD-B' WHERE Id=2;",
                "GRANT UPDATE ON OBJECT::lab.Inventory TO [QRY019_reader];",
                "UPDATE lab.Candidates SET StatementText=NULL WHERE Id BETWEEN 3 AND 8;",
            )
            for mutation in mutations:
                phase("10_Setup.sql")
                mutate(mutation)
                rejected("60_Comparison.sql")
            print(f"AI_LOCAL|{demo_id}|RESULT_NEGATIVE_{len(mutations)}|PASS")
        elif demo_id == "QRY-018":
            # Jede Mutation hat eine neue volle Fixture; keine stillen Sollwertkorrekturen.
            mutations = (
                "UPDATE lab.Replay SET ClaimDays=99 WHERE ReplayId=1;",
                "UPDATE lab.Replay SET CitedSourceId=10 WHERE ReplayId=1;",
                "DELETE FROM lab.Chunks;",
                "UPDATE lab.Chunks SET ChunkText=N'Falsche synthetische Quelle' WHERE SourceId=11;",
                "UPDATE lab.Documents SET IsCurrent=0 WHERE SourceId=11;",
                "DELETE FROM lab.Replay;",
                "UPDATE lab.Documents SET FactDays=8 WHERE SourceId=11;",
            )
            for mutation in mutations:
                phase("10_Setup.sql")
                phase("30_Demonstration.sql")
                mutate(mutation)
                rejected("60_Comparison.sql")
            print(f"AI_LOCAL|{demo_id}|RESULT_NEGATIVE_{len(mutations)}|PASS")
        elif demo_id == "QRY-016":
            phase("20_Baseline.sql")
            phase("30_Demonstration.sql")
            mutate("UPDATE lab.Chunks SET ChunkText=N'Falscher synthetischer Quellenbeleg' WHERE ChunkOrder=1;")
            rejected("60_Comparison.sql")
            mutate("DELETE FROM lab.Chunks;")
            rejected("60_Comparison.sql")
        elif demo_id == "QRY-015":
            mutate("DELETE FROM lab.VectorFixture;")
            rejected("20_Baseline.sql")
            rejected("30_Demonstration.sql")
        elif demo_id == "QRY-017":
            mutate("DELETE FROM lab.SearchDocuments;")
            rejected("60_Comparison.sql")
    finally:
        phase("90_Cleanup.sql")  # Auch hier gelten alle vier vollstaendigen Marker.
        assert_absent(target, demo_id)
    print(f"AI_LOCAL|{demo_id}|OWNERSHIP_NEGATIVE_{16 * len(negatives)}|IDEMPOTENCE|PASS|CLEANUP_ABSENT")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=targets.TARGET_KINDS, default=targets.DOCKER)
    parser.add_argument("--container")
    parser.add_argument("--server")
    parser.add_argument("--username")
    parser.add_argument("--sqlcmd")
    parser.add_argument("--expected-major", choices=(15, 16, 17), type=int, required=True)
    parser.add_argument("--confirm-disposable-instance", action="store_true")
    parser.add_argument("--demo", choices=DEMOS)
    args = parser.parse_args()
    try:
        target = (targets.docker_target(container=args.container, sqlcmd_path=args.sqlcmd)
                  if args.target == targets.DOCKER else
                  targets.host_target(server=args.server, username=args.username, sqlcmd_path=args.sqlcmd))
        targets.require_disposable_instance(target, args.confirm_disposable_instance)
        major = targets.verify_engine(target, expected_major=args.expected_major)
        outcomes = []
        for demo_id in ([args.demo] if args.demo else DEMOS):
            for repetition in (1, 2):
                outcomes.append(run_demo(target, major, demo_id, repetition))
            if major == 17:
                ownership_controls(target, demo_id)
    except (AiFailure, targets.ExecutionTargetError, evaluator.ContractError,
            OSError, subprocess.TimeoutExpired) as exc:
        print(targets.redact(str(exc)), file=sys.stderr)
        print("SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT")
        return 1
    priority = {"PASS": 0, "WARN": 1, "SKIP": 2, "FAIL": 3}
    status, code = max(outcomes, key=lambda item: priority[item[0]])
    print(f"SQLPERF_SUMMARY|{status}|{code}")
    print("AI_LOCAL_QUALIFICATION|PASS|EXPECTED_CONTRACTS_AND_CLEANUP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
