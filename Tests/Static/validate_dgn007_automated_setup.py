#!/usr/bin/env python3
"""Prüft den begrenzten DGN-007-Datenmodellvertrag ohne SQL-Server-Ausführung."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident"
AUTO = DEMO / "Automated"
RUNNER = ROOT / "Tests/Runtime/run_dgn007_automated_setup.py"
RUNNER_TEST = ROOT / "Tests/Static/test_dgn007_automated_setup_runner.py"
WORKFLOW = ROOT / ".github/workflows/dgn007-automated-setup.yml"
TRIGGER_PATHS = {
    "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/**",
    "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/40_Observation.sql",
    "Scenarios/DGN-007/adapter/sql/validate.sql",
    "Demos/00_Framework/Tools/**",
    "Tests/Contracts/dgn007_capture_projection.py",
    "Tests/Contracts/dgn007_collector_transport.py",
    "Tests/Contracts/dgn007_prospective_acceptance.py",
    "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/incident-acceptance.contract.json",
    "Tests/Static/test_dgn007_capture_projection.py",
    "Tests/Static/validate_dgn007_capture_projection.py",
    "Tests/Static/test_dgn007_collector_transport.py",
    "Tests/Static/validate_dgn007_collector_transport.py",
    "Tests/Static/test_dgn007_prospective_acceptance.py",
    "Tests/Static/validate_dgn007_prospective_acceptance.py",
    "Tests/Runtime/run_dgn007_automated_setup.py",
    "Tests/Runtime/execution_target.py",
    "Tests/Runtime/docker_sqlcmd_proxy.py",
    "Tests/Static/test_dgn007_automated_setup_runner.py",
    "Tests/Static/test_dgn007_compatibility.py",
    "Tests/Static/test_dgn007_profile_comparison.py",
    "Tests/Static/test_dgn007_control_capture.py",
    "Tests/Static/validate_dgn007_automated_setup.py",
    "Tests/Static/validate_dgn007_query_store_windows.py",
    "Tests/Static/validate_dgn007_profile_comparison.py",
    "Tests/Static/validate_dgn007_control_capture.py",
    ".github/workflows/dgn007-automated-setup.yml",
}
DATA_ASSERTION_MARKERS = (
    "SELECT compatibility_level FROM sys.databases WHERE database_id=DB_ID()",
    "@ExpectedCompatibility IS NULL", "@ActualCompatibility IS NULL",
    "@ActualCompatibility<>@ExpectedCompatibility",
    "(SELECT COUNT_BIG(*) FROM dbo.CaseGroup)<>12",
    "(SELECT COUNT_BIG(*) FROM dbo.CaseItem)<>24000",
    "(SELECT COUNT_BIG(*) FROM dbo.CaseItemDetail)<>72000",
    "ItemId NOT BETWEEN 1 AND 24000",
    "COUNT(i.ItemId)<>CASE WHEN g.GroupKey<=4 THEN 4000 WHEN g.GroupKey<=7 THEN 2000 ELSE 400 END",
    "(VALUES(8,3,228),(1,3,2286),(5,3,1144),(1,1,571))",
    "EXCEPT SELECT ItemId,SearchValue,StatusCode FROM #Actual",
    "EXCEPT SELECT ItemId,SearchValue,StatusCode FROM dbo.CaseItem WHERE GroupKey=@GroupKey AND StatusCode=@StatusCode",
    "(SELECT COUNT(*) FROM #Actual)<>@ExpectedCount",
    "(SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>4",
    "SELECT GroupKey,StatusCode FROM dbo.CaseRequestLog EXCEPT SELECT GroupKey,StatusCode FROM (VALUES(8,3),(1,3),(5,3),(1,1)) p(GroupKey,StatusCode)",
    "SELECT GroupKey,StatusCode FROM (VALUES(8,3),(1,3),(5,3),(1,1)) p(GroupKey,StatusCode) EXCEPT SELECT GroupKey,StatusCode FROM dbo.CaseRequestLog",
)
sys.path.insert(0, str(ROOT / "Demos/00_Framework/Tools"))
from run_demo import load_manifest  # noqa: E402


def ownership_findings(sql: str) -> list[str]:
    """Erzwingt NULL-, Case- und Längenschutz vor jedem destruktiven Statement."""
    findings = []
    guard = sql.split("ALTER DATABASE", 1)[0]
    for variable, expected in (("Project", "SQL_PerformanceSchulung"), ("Contract", "1.0"), ("Demo", "DGN-007"), ("Run", "AUTO")):
        for marker in (
            f"@{variable} nvarchar(max)",
            f"@{variable} IS NULL",
            f"@{variable} COLLATE Latin1_General_100_BIN2<>N'{expected}'",
            f"DATALENGTH(@{variable})<>DATALENGTH(N'{expected}')",
        ):
            if marker not in guard:
                findings.append(f"Eigentumsschutz fehlt: {marker}")
    if sql.count("CONVERT(nvarchar(max),value)") != 4:
        findings.append("Markerwerte dürfen nicht gekürzt werden")
    return findings


def data_assertion_findings(sql: str) -> list[str]:
    """Begrenzt die Evidenz auf deterministische Mengen, Counts und Requestparameter."""
    normalized = " ".join(sql.split())
    return [f"Ergebnisinvariante fehlt: {marker}" for marker in DATA_ASSERTION_MARKERS if marker not in normalized]


def workflow_findings(text: str) -> list[str]:
    """Prüft den eigenen CI-Schnitt einschließlich isolierter Containerentfernung."""
    findings = []
    for event in ("pull_request", "push"):
        block = re.search(rf"(?ms)^  {event}:\n(.*?)(?=^  [a-z_]+:|^permissions:|\Z)", text)
        paths = set(re.findall(r"^      - '([^']+)'$", block[1], re.MULTILINE)) if block else set()
        if paths != TRIGGER_PATHS:
            findings.append(f"Workflow-{event}-Pfade müssen exakt den Datenmodellabhängigkeiten entsprechen")
        if event == "push" and (block is None or "branches: [main]" not in block[1]):
            findings.append("Workflow-Push muss auf main begrenzt sein")
    for marker in (
        "  workflow_dispatch:", "  contents: read", "  cancel-in-progress: false",
        "    needs: [static, changes]", "    if: needs.changes.outputs.run_runtime == 'true'",
        "python Tests/Static/select_runtime_workflow.py", "      fail-fast: false", "    timeout-minutes: 100",
        "python -m unittest discover -s Tests/Static -p test_dgn007_automated_setup_runner.py",
        "python Tests/Static/validate_dgn007_automated_setup.py",
        "python Tests/Static/validate_dgn007_query_store_windows.py",
        "python Tests/Static/validate_dgn007_profile_comparison.py",
        "python Tests/Static/test_dgn007_profile_comparison.py",
        "python Tests/Static/validate_dgn007_control_capture.py",
        "python Tests/Static/test_dgn007_control_capture.py",
        "python Tests/Runtime/run_dgn007_automated_setup.py", "--target docker",
        "--scope data-model", "--scope query-store-windows", "--scope profile-comparison",
        "--scope control-ab", "--scope control-ba", "--scope control-aa",
        '--container "${SQLPERF_SQL_CONTAINER}"', "--expected-major '${{ matrix.major }}'",
        "--confirm-disposable-instance --confirm-isolated-lab",
        'container="sqlperf-dgn007-auto-${{ matrix.major }}-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"',
        "::add-mask::${password}", "export SQLCMDPASSWORD=", "export MSSQL_SA_PASSWORD=",
        "-e MSSQL_SA_PASSWORD", "--cpus 4 --memory 8g", '--cidfile "${cidfile}"',
        "--label sqlperf.scope=dgn007-automated-setup",
        'sqlperf.run=${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}-${{ matrix.major }}',
        "SQL Server is now ready for client connections", "login_ready=0",
        "docker exec -e SQLCMDPASSWORD", "SELECT 1;", '"${login_ready}" = \'1\'',
        "        if: always()", 'container_id="$(cat "${SQLPERF_SQL_CIDFILE}")"',
        '[[ "${container_id}" =~ ^[0-9a-f]{64}$ ]]',
        'index .Config.Labels "sqlperf.scope"', 'index .Config.Labels "sqlperf.run"',
        'expected="/${SQLPERF_SQL_CONTAINER}|dgn007-automated-setup|',
        '[ "${identity}" = "${expected}" ]',
        'docker rm --force --volumes "${container_id}"',
        'docker container ls --all --quiet --filter "id=${container_id}"',
    ):
        if marker not in text:
            findings.append(f"Workflow-Vertrag fehlt: {marker}")
    matrix = re.findall(r"\{year: (\d+), major: (\d+), image: '([^']+)'\}", text)
    if matrix != [(str(year), str(major), f"mcr.microsoft.com/mssql/server:{year}-latest") for year, major in ((2019, 15), (2022, 16), (2025, 17))]:
        findings.append("Workflow benötigt exakt die 2019-/2022-/2025-Matrix")
    for forbidden in (
        r"cancel-in-progress:\s*(?!false\b)\S+", r"--show-output", r"upload-artifact", r"\btee\b",
        r"(?m)^\s*set\s+-[^\n]*x", r"-e\s+['\"]?(?:SQLCMDPASSWORD|MSSQL_SA_PASSWORD)=",
        r"(?i:--password\b)|\s-P(?:\s|\$)", r"docker\s+(?:system|container|volume)\s+prune",
        r"docker\s+rm[^\n]*(?:\$\(|\*)",
        r"READY_FOR_USER", r"SQL_Server_Lab", r"run_dgn003_dgn005_pilots\.py",
    ):
        if re.search(forbidden, text):
            findings.append(f"Unzulässiger Workflow-Inhalt: {forbidden}")
    cleanup = text.split("        if: always()", 1)[-1]
    if "|| true" in cleanup:
        findings.append("Container-Cleanup darf Fehler nicht verschweigen")
    start = text.split("docker run", 1)[-1].split("ready=0", 1)[0]
    if re.search(r"(?:^|\s)(?:-p|--publish|--publish-all|-v|--volume|--mount)(?:=|\s|$)", start):
        findings.append("Datenmodell-Container darf keine Ports oder Volumes freigeben")
    commands = re.findall(r"(?m)^          python Tests/Runtime/run_dgn007_automated_setup.py \\\n((?:            .*\n)+)", text)
    if len(commands) != 6 or not all(
        f"--scope {scope}" in command and '--container "${SQLPERF_SQL_CONTAINER}"' in command
        for scope, command in zip(("data-model", "query-store-windows", "profile-comparison", "control-ab", "control-ba", "control-aa"), commands)
    ):
        findings.append("Alle sechs Scopes müssen in der festgelegten Reihenfolge denselben bereinigten Container verwenden")
    if len(re.findall(r"(?m)^          docker run\b", text)) != 1:
        findings.append("Alle Prüfschnitte benötigen genau einen frischen Matrixcontainer")
    # Tatsächliche ausführbare Pullzeile prüfen, keine kommentierte Markerkopie.
    pulls = [line.strip() for line in text.splitlines()
             if not line.lstrip().startswith("#") and re.search(r"\bdocker\s+pull\b", line)]
    if pulls != ["timeout --kill-after=10s 600s docker pull '${{ matrix.image }}'"]:
        findings.append("Der einzige Image-Pull benötigt exakt 600 Sekunden plus zehn Sekunden Abbruchgrenze")
    return findings


def runner_findings(text: str) -> list[str]:
    """Prüft ausführbare Runner-Grenzen ohne SQL-Server- oder Docker-Aufruf."""
    findings = []
    tree = ast.parse(text)
    literals = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    for marker in ("DGN-007_DATA_MODEL", "setup.manifest.json", "--confirm-disposable-instance", "--confirm-isolated-lab"):
        if marker not in literals:
            findings.append(f"Runner-Vertrag fehlt: {marker}")
    if "--show-output" in literals:
        from validate_dgn007_capture_projection import runner_projection_findings
        findings.extend(runner_projection_findings(text))
    if "--password" in literals or "-P" in literals:
        findings.append("Runner darf kein Passwortargument unterstützen")
    if "SQLPERF_LAB_DGN007_AUTO" not in literals:
        findings.append("Runner muss die AUTO-Datenbank unabhängig prüfen")
    if not any(isinstance(node, ast.Import) and any(alias.name == "execution_target" for alias in node.names) for node in ast.walk(tree)):
        findings.append("Runner muss das bestehende execution_target verwenden")
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    for name in ("validate_manifest", "assert_empty_instance", "assert_absent", "run_harness", "check_harness", "recover", "run_one", "main"):
        if name not in functions:
            findings.append(f"Runner-Vertragsprüfung fehlt: {name}")
    if "main" in functions:
        repetitions = [node for node in ast.walk(functions["main"]) if isinstance(node, ast.For)]
        if not any(isinstance(node.iter, ast.Tuple) and [item.value for item in node.iter.elts if isinstance(item, ast.Constant)] == [1, 2] for node in repetitions):
            findings.append("Runner muss exakt zwei Wiederholungen ausführen")
    if "run_one" in functions:
        final_checks = [node for block in ast.walk(functions["run_one"]) if isinstance(block, ast.Try) for statement in block.finalbody for node in ast.walk(statement) if isinstance(node, ast.Call)]
        if not any(isinstance(node.func, ast.Name) and node.func.id == "assert_absent" for node in final_checks):
            findings.append("Runner muss die unabhängige Cleanup-Prüfung im finally-Pfad ausführen")
    return findings


def main() -> int:
    findings = []
    manifest = load_manifest(AUTO / "setup.manifest.json")
    if (manifest.demo_id, manifest.run_token, manifest.safety_level) != ("DGN-007", "AUTO", "YELLOW"):
        findings.append("Manifest muss getrennten gelben AUTO-Vertrag verwenden")
    if [phase.phase_id for phase in manifest.phases] != ["PREFLIGHT", "SETUP", "DATA_ASSERTION"]:
        findings.append("Setup-Phasenfolge weicht ab")
    if manifest.timeout_seconds != 180 or manifest.cleanup_timeout_seconds != 60 or manifest.cleanup is None:
        findings.append("Zeit- oder Cleanup-Vertrag weicht ab")
    for phase in (*manifest.phases, manifest.cleanup):
        if not phase.required or not phase.require_summary or not phase.timeout_seconds:
            findings.append("Jede Phase benötigt Statusauswertung und Zeitbudget")
    sql = {path.name: path.read_text(encoding="utf-8") for path in AUTO.glob("*.sql")}
    cleanup = sql["90_Cleanup.sql"]
    findings.extend(ownership_findings(cleanup))
    # Negative Kontrollen: eine entfernte Schutzbedingung darf nicht grün bleiben.
    for marker in ("@Project IS NULL", "@Run IS NULL", " COLLATE Latin1_General_100_BIN2", "DATALENGTH(@Contract)<>DATALENGTH(N'1.0')", "CONVERT(nvarchar(max),value)"):
        if not ownership_findings(cleanup.replace(marker, "")):
            findings.append(f"Negative Eigentumskontrolle nicht erkannt: {marker}")
    combined = "\n".join(sql.values())
    for forbidden in (r"(?im)^\s*:r\b", r"(?i)DBCC\s+(?:FREEPROCCACHE|DROPCLEANBUFFERS)", r"(?i)NEWID\s*\(", r"SQLPERF_LAB_DGN007_LOCAL", r"CREATE\s+EVENT\s+SESSION"):
        if re.search(forbidden, combined):
            findings.append(f"Unzulässige Abhängigkeit oder Operation: {forbidden}")
    for filename in ("00_Preflight.sql", "10_Setup.sql", "90_Cleanup.sql"):
        for marker in ("$(ConfirmIsolatedLab)", "$(HighImpactConfirmed)", "SQLPERF_LAB_DGN007_AUTO"):
            if marker not in sql[filename]:
                findings.append(f"Sicherheitsmarker fehlt: {filename}: {marker}")
    setup = sql["10_Setup.sql"]
    for marker in ("WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170", "INSERT dbo.CaseItem(ItemId,", "BETWEEN 1 AND 24000", "BETWEEN 1 AND 3", "DGN007_CASE_SEARCH"):
        if marker not in setup:
            findings.append(f"Datenmodellmarker fehlt: {marker}")
    assertion = sql["40_Data_Assertion.sql"]
    findings.extend(data_assertion_findings(assertion))
    for marker in DATA_ASSERTION_MARKERS:
        if not data_assertion_findings(" ".join(assertion.split()).replace(marker, "")):
            findings.append(f"Negative Datenassertionskontrolle nicht erkannt: {marker}")
    if (DEMO / "manifest.json").exists() or (AUTO / "manifest.json").exists():
        findings.append("Setup-Schnitt darf keine freigegebene Demo vortäuschen")
    adapter = json.loads((ROOT / "Scenarios/DGN-007/adapter/adapter.json").read_text(encoding="utf-8"))
    if adapter["supportedSqlVersions"] != ["2025"]:
        findings.append("Bestehende Adapter-Versionsgrenze wurde verändert")
    readme = (AUTO / "README.md").read_text(encoding="utf-8")
    for marker in ("DGN-007_DATA_MODEL", "kein freigegebenes", "AUTO", "LOCAL", "FWK-010", "180 Sekunden", "Ein `PASS` gilt ausschließlich für den jeweils ausgewählten Vertrag."):
        if marker not in readme:
            findings.append(f"Status-/Vertragsgrenze fehlt: {marker}")
    for path in (RUNNER, RUNNER_TEST, WORKFLOW):
        if not path.is_file():
            findings.append(f"Datenmodell-Validierungspfad fehlt: {path.relative_to(ROOT)}")
    if WORKFLOW.is_file():
        workflow = WORKFLOW.read_text(encoding="utf-8")
        findings.extend(workflow_findings(workflow))
        # Die Sicherheitskontrollen müssen auch bei einer späteren CI-Änderung greifen.
        mutations = (
            ("cancel-in-progress: false", "cancel-in-progress: true"),
            ("--cpus 4 --memory 8g", "--cpus 2 --memory 4g"),
            ("docker exec -e SQLCMDPASSWORD", 'docker exec -e "SQLCMDPASSWORD=${password}"'),
            ('[ "${identity}" = "${expected}" ]', "true"),
            ('docker rm --force --volumes "${container_id}"', 'docker rm --force "${container_id}"'),
            ("--confirm-disposable-instance --confirm-isolated-lab", "--confirm-isolated-lab"),
            ("--target docker", "--target host"),
            ("timeout-minutes: 100", "timeout-minutes: 85"),
            ("timeout --kill-after=10s 600s docker pull", "docker pull"),
            ("timeout --kill-after=10s 600s docker pull", "timeout 600s docker pull"),
            ("timeout --kill-after=10s 600s docker pull", "timeout --kill-after=10s 1200s docker pull"),
            ("timeout --kill-after=10s 600s docker pull", "# timeout --kill-after=10s 600s docker pull"),
        )
        for original, replacement in mutations:
            if not workflow_findings(workflow.replace(original, replacement)):
                findings.append(f"Negative Workflow-Kontrolle nicht erkannt: {original}")
    if RUNNER.is_file():
        findings.extend(runner_findings(RUNNER.read_text(encoding="utf-8")))
    if findings:
        print("dgn007-automated-setup: FAIL\n" + "\n".join(findings))
        return 1
    print("dgn007-automated-setup: PASS (PROJECT_SEMANTIC; keine Runtime- oder Capstone-Abnahme)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
