#!/usr/bin/env python3
"""Validate the SQL_Server_Lab test catalog and scenario boundary.

The validator starts neither SQL Server nor a provider. It verifies that every
productive demo manifest is represented exactly once in the automated test
catalog and that interactive training scenarios remain the primary goal.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Tests" / "Lab" / "performance-lab-matrix.json"
SCHEMA_PATH = ROOT / "Tests" / "Lab" / "performance-lab-matrix.schema.json"
AUTOMATION_PATH = ROOT / "Documentation" / "Architecture" / "SQL_SERVER_LAB_TEST_AUTOMATION.md"
SCENARIO_PATH = ROOT / "Documentation" / "Architecture" / "SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md"
INFRASTRUCTURE_README = ROOT / "Infrastructure" / "README.md"
BACKLOG = ROOT / ".ai" / "BACKLOG.md"
DECISIONS = ROOT / ".ai" / "DECISIONS.md"
QRY001_LAB_MANIFEST = ROOT / "Scenarios" / "QRY-001" / "sql-server-lab.json"
QRY001_PODMAN_LAB_MANIFEST = ROOT / "Scenarios" / "QRY-001" / "sql-server-lab.podman.json"
SCENARIO_TEST_RUNNER = ROOT / "Tests" / "Lab" / "Invoke-SqlServerLabScenarioTest.ps1"
QRY001_CLEANUP_PROBE = ROOT / "Tests" / "Lab" / "Sql" / "Assert-QRY-001-Cleanup.sql"

DEMO_ID = re.compile(r"^(STL|OPT|QRY|IDX|CON|RES|DGN)-[0-9]{3}$")
CAPABILITY = re.compile(r"^[A-Z][A-Z0-9_]+$")
PROVIDERS = {"docker", "podman"}
VERSIONS = {"2019", "2022", "2025"}
SAFETY_LEVELS = {"GREEN", "YELLOW", "RED"}
PROFILES = {"compact", "standard", "performance"}
ISOLATION = {"SHARED_PROVIDER_VERSION", "FRESH_INSTANCE", "DEDICATED_DISPOSABLE"}
OUTCOMES = {"PASS", "WARN", "SKIP"}
LANES = {"SMOKE", "CORE", "PROVIDER_PARITY", "FULL_CONTAINER_MATRIX", "RED_DISPOSABLE"}


class ContractError(RuntimeError):
    pass


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"{relative(path)}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{relative(path)}: root must be an object")
    return value


def discover_manifests(excluded: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in sorted((ROOT / "Demos").rglob("manifest.json")):
        rel = relative(path)
        if any(rel.startswith(prefix) for prefix in excluded):
            continue
        manifest = read_json(path)
        demo_id = manifest.get("demo_id")
        if not isinstance(demo_id, str) or not DEMO_ID.fullmatch(demo_id):
            raise ContractError(f"{rel}: invalid demo_id")
        if demo_id in result:
            raise ContractError(f"duplicate productive demo_id {demo_id}")
        result[demo_id] = path
    return result


def validate_lane(name: str, lane: Any) -> None:
    if not isinstance(lane, dict):
        raise ContractError(f"lane {name} must be an object")
    if lane.get("providerMode") not in {"FIRST_AVAILABLE", "SELECTED", "ALL"}:
        raise ContractError(f"lane {name}: invalid providerMode")

    versions = lane.get("versions")
    safety = lane.get("safetyLevels")
    repetitions = lane.get("repetitions")
    if not isinstance(versions, list) or not versions or set(versions) - VERSIONS:
        raise ContractError(f"lane {name}: invalid versions")
    if len(versions) != len(set(versions)):
        raise ContractError(f"lane {name}: duplicate versions")
    if not isinstance(safety, list) or not safety or set(safety) - SAFETY_LEVELS:
        raise ContractError(f"lane {name}: invalid safetyLevels")
    if len(safety) != len(set(safety)):
        raise ContractError(f"lane {name}: duplicate safetyLevels")
    if not isinstance(repetitions, int) or not 1 <= repetitions <= 5:
        raise ContractError(f"lane {name}: invalid repetitions")

    if "YELLOW" in safety and lane.get("requiresYellowConfirmation") is not True:
        raise ContractError(f"lane {name}: YELLOW requires confirmation")
    if "RED" in safety and lane.get("requiresRedConfirmation") is not True:
        raise ContractError(f"lane {name}: RED requires confirmation")
    if name == "FULL_CONTAINER_MATRIX" and "RED" in safety:
        raise ContractError("FULL_CONTAINER_MATRIX must not contain RED")
    if name == "RED_DISPOSABLE" and safety != ["RED"]:
        raise ContractError("RED_DISPOSABLE must contain RED only")


def validate_demo(entry: Any, manifests: dict[str, Path]) -> None:
    if not isinstance(entry, dict):
        raise ContractError("each demo entry must be an object")

    demo_id = entry.get("demoId")
    if not isinstance(demo_id, str) or not DEMO_ID.fullmatch(demo_id):
        raise ContractError(f"invalid demoId {demo_id!r}")
    if demo_id not in manifests:
        raise ContractError(f"unknown catalog demo {demo_id}")

    expected_path = relative(manifests[demo_id])
    if entry.get("manifest") != expected_path:
        raise ContractError(f"{demo_id}: manifest path must be {expected_path}")

    manifest = read_json(manifests[demo_id])
    if manifest.get("contract_version") != "1.0":
        raise ContractError(f"{demo_id}: contract_version must be 1.0")
    if manifest.get("run_token") != "LOCAL":
        raise ContractError(f"{demo_id}: checked-in run_token must be LOCAL")
    if not isinstance(manifest.get("phases"), list) or not manifest["phases"]:
        raise ContractError(f"{demo_id}: phases missing")
    if not isinstance(manifest.get("cleanup"), dict):
        raise ContractError(f"{demo_id}: cleanup missing")

    safety = entry.get("safetyLevel")
    if safety not in SAFETY_LEVELS or safety != manifest.get("safety_level"):
        raise ContractError(f"{demo_id}: safety mismatch")
    if entry.get("implementationStatus") not in {"IMPLEMENTED", "VALIDATED"}:
        raise ContractError(f"{demo_id}: invalid implementationStatus")

    sessions = entry.get("sessions")
    if not isinstance(sessions, int) or not 1 <= sessions <= 200:
        raise ContractError(f"{demo_id}: invalid sessions")

    providers = entry.get("providers")
    versions = entry.get("versions")
    if not isinstance(providers, list) or not providers or set(providers) - PROVIDERS:
        raise ContractError(f"{demo_id}: invalid providers")
    if not isinstance(versions, list) or not versions or set(versions) - VERSIONS:
        raise ContractError(f"{demo_id}: invalid versions")
    if len(providers) != len(set(providers)) or len(versions) != len(set(versions)):
        raise ContractError(f"{demo_id}: duplicate provider or version")

    if entry.get("resourceProfile") not in PROFILES:
        raise ContractError(f"{demo_id}: invalid resourceProfile")
    isolation = entry.get("environmentIsolation")
    if isolation not in ISOLATION:
        raise ContractError(f"{demo_id}: invalid environmentIsolation")
    if safety == "YELLOW" and isolation == "SHARED_PROVIDER_VERSION":
        raise ContractError(f"{demo_id}: YELLOW requires a fresh instance")
    if safety == "RED" and isolation != "DEDICATED_DISPOSABLE":
        raise ContractError(f"{demo_id}: RED requires DEDICATED_DISPOSABLE")

    capabilities = entry.get("requiredCapabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise ContractError(f"{demo_id}: requiredCapabilities missing")
    if len(capabilities) != len(set(capabilities)):
        raise ContractError(f"{demo_id}: duplicate capability")
    if any(not isinstance(item, str) or not CAPABILITY.fullmatch(item) for item in capabilities):
        raise ContractError(f"{demo_id}: invalid capability")
    if sessions > 1 and "MULTI_SESSION_SQLCMD" not in capabilities:
        raise ContractError(f"{demo_id}: multi-session capability missing")

    outcomes = entry.get("expectedOutcomes")
    if not isinstance(outcomes, list) or not outcomes or set(outcomes) - OUTCOMES:
        raise ContractError(f"{demo_id}: invalid expectedOutcomes")
    repetitions = entry.get("defaultRepetitions")
    if not isinstance(repetitions, int) or not 1 <= repetitions <= 5:
        raise ContractError(f"{demo_id}: invalid defaultRepetitions")

    forbidden = {"password", "secret", "hostname", "hostPath", "connectionString", "username"}
    if forbidden.intersection(entry):
        raise ContractError(f"{demo_id}: runtime or secret field in catalog")


def validate_project_boundary() -> None:
    scenario = SCENARIO_PATH.read_text(encoding="utf-8")
    scenario_markers = (
        "`READY_FOR_USER`",
        "Docker, Podman, Hyper-V und gemischte Topologien",
        "Benutzer führt das Beispiel interaktiv durch",
        "Jedes interaktive Szenario benötigt einen definierten Reset",
        "Die Umgebung darf nach erfolgreicher Vorbereitung nicht automatisch entfernt werden",
        "`LABSCN-002`",
        "`LABSCN-003`",
    )
    for marker in scenario_markers:
        if marker not in scenario:
            raise ContractError(f"interactive scenario document missing marker {marker}")

    automation = AUTOMATION_PATH.read_text(encoding="utf-8")
    for marker in (
        "ausschließlich ein Qualitätssicherungsinstrument",
        "ist nicht der spätere Benutzerszenariokatalog",
        "Der automatische Abbau eines Testlaufs darf daher nicht als Zielverhalten",
    ):
        if marker not in automation:
            raise ContractError(f"automation document missing subordinate-role marker {marker}")

    backlog = BACKLOG.read_text(encoding="utf-8")
    for marker in ("`LABSCN-001`", "`LABSCN-002`", "`LABSCN-003`", "`LABINT-001`"):
        if marker not in backlog:
            raise ContractError(f"backlog lacks {marker}")

    decisions = DECISIONS.read_text(encoding="utf-8")
    if "DEC-044" not in decisions or "READY_FOR_USER" not in decisions:
        raise ContractError("DEC-044 interactive scenario decision is missing")

    infrastructure = INFRASTRUCTURE_README.read_text(encoding="utf-8")
    for marker in ("SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md", "READY_FOR_USER", "Docker, Podman, Hyper-V"):
        if marker not in infrastructure:
            raise ContractError(f"Infrastructure/README.md missing marker {marker}")


def validate_executable_vertical_slice() -> None:
    for provider, path, expected_name in (
        ("docker", QRY001_LAB_MANIFEST, "sql-performance-qry-001"),
        ("podman", QRY001_PODMAN_LAB_MANIFEST, "sql-performance-qry-001-podman"),
    ):
        manifest = read_json(path)
        if manifest.get("name") != expected_name:
            raise ContractError(f"QRY-001 {provider} SQL_Server_Lab manifest has an unexpected name")
        if manifest.get("automation") != {"mode": "unattended"}:
            raise ContractError(f"QRY-001 {provider} manifest must be unattended and secret-free")

        instances = manifest.get("instances")
        if not isinstance(instances, list) or len(instances) != 1:
            raise ContractError(f"QRY-001 {provider} manifest must contain one instance")
        instance = instances[0]
        expected = {
            "id": "primary",
            "version": "2025",
            "provider": provider,
            "os": "linux",
            "profile": "compact",
            "collation": "SQL_Latin1_General_CP1_CS_AS",
            "databases": [],
        }
        if instance != expected:
            raise ContractError(f"QRY-001 {provider} SQL_Server_Lab instance contract mismatch")
        if "hyperv" in json.dumps(manifest).lower():
            raise ContractError("QRY-001 vertical slice must not require Hyper-V")

    try:
        runner = SCENARIO_TEST_RUNNER.read_text(encoding="utf-8")
        cleanup_probe = QRY001_CLEANUP_PROBE.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"executable QRY-001 vertical slice is incomplete: {exc}") from exc

    runner_markers = (
        "Test-SqlServerLabManifest",
        "New-SqlServerLab",
        "Get-SqlServerLab",
        "Invoke-SqlServerLabScript",
        "Remove-SqlServerLab",
        "Runtime\\State\\SqlServerLab",
        "Demos\\00_Framework\\Tools\\run_demo.py",
        "SQLCMDPASSWORD",
        "QRY-001",
        "podman",
    )
    for marker in runner_markers:
        if marker not in runner:
            raise ContractError(f"QRY-001 scenario runner missing marker {marker}")

    if "SQLPERF_LAB_QRY001_LOCAL" not in cleanup_probe or "DB_ID" not in cleanup_probe:
        raise ContractError("QRY-001 independent cleanup probe is incomplete")


def main() -> int:
    try:
        catalog = read_json(CATALOG_PATH)
        schema = read_json(SCHEMA_PATH)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ContractError("catalog schema must use draft 2020-12")
        if catalog.get("contractVersion") != "1.0":
            raise ContractError("contractVersion must be 1.0")
        if catalog.get("labRepository") != "gecompat/SQL_Server_Lab":
            raise ContractError("unexpected labRepository")
        if set(catalog.get("providers", [])) != PROVIDERS:
            raise ContractError("automated provider matrix must contain docker and podman")
        if set(catalog.get("targetVersions", [])) != VERSIONS:
            raise ContractError("versions must be 2019, 2022 and 2025")

        discovery = catalog.get("discovery")
        if not isinstance(discovery, dict):
            raise ContractError("discovery contract missing")
        excluded = discovery.get("excludePrefixes")
        if not isinstance(excluded, list) or "Demos/00_Framework/" not in excluded:
            raise ContractError("framework examples must be excluded")
        if discovery.get("missingCatalogEntry") != "FAIL" or discovery.get("unknownCatalogEntry") != "FAIL":
            raise ContractError("catalog mismatch policies must be FAIL")

        lanes = catalog.get("lanes")
        if not isinstance(lanes, dict) or set(lanes) != LANES:
            raise ContractError("lane set mismatch")
        for name, lane in lanes.items():
            validate_lane(name, lane)

        manifests = discover_manifests(excluded)
        entries = catalog.get("demos")
        if not isinstance(entries, list):
            raise ContractError("demos must be a list")
        ids = [entry.get("demoId") for entry in entries if isinstance(entry, dict)]
        if len(ids) != len(set(ids)):
            raise ContractError("duplicate demoId in catalog")
        if set(ids) != set(manifests):
            raise ContractError(
                f"catalog mismatch; missing={sorted(set(manifests) - set(ids))}; "
                f"unknown={sorted(set(ids) - set(manifests))}"
            )
        for entry in entries:
            validate_demo(entry, manifests)

        validate_project_boundary()
        validate_executable_vertical_slice()

        full_lane = lanes["FULL_CONTAINER_MATRIX"]
        eligible = [entry for entry in entries if entry["safetyLevel"] in full_lane["safetyLevels"]]
        runs = len(eligible) * len(PROVIDERS) * len(full_lane["versions"]) * full_lane["repetitions"]
        if runs != 252:
            raise ContractError(f"current full matrix must contain 252 runs, got {runs}")

        print(
            "sql-server-lab-scenario-contract: PASS "
            f"({len(entries)} automated demos, interactive scenario goal anchored, full_runs={runs})"
        )
        return 0
    except (ContractError, KeyError, TypeError) as exc:
        print(f"sql-server-lab-scenario-contract: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
