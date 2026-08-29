#!/usr/bin/env python3
"""Static contract for the ordered W-COV-001 coverage wave."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
ORDER = ["OPT-003", "OPT-005", "CON-006", "CON-009", "IDX-006", "IDX-010", "STL-008", "STL-009", "RES-007"]
PATHS = {
    "OPT-003": "Demos/04_Optimizer_Statistics_Plans/OPT-003_Sampling_Skew",
    "OPT-005": "Demos/04_Optimizer_Statistics_Plans/OPT-005_Ascending_Key",
    "CON-006": "Demos/07_Concurrency/CON-006_Deadlock_Cycle",
    "CON-009": "Demos/05_Concurrency_Isolation_TempDB/CON-009_TempDB_Cost_Classes",
    "IDX-006": "Demos/04_Rowstore_Columnstore/IDX-006_Page_Splits_Density",
    "IDX-010": "Demos/04_Rowstore_Columnstore/IDX-010_Columnstore_Segments",
    "STL-008": "Demos/01_Storage_Pages_Log/STL-008_VLF_Log_Growth",
    "STL-009": "Demos/01_Storage_Pages_Log/STL-009_Commit_Batching",
    "RES-007": "Demos/06_CPU_Memory_IO_Waits/RES-007_Wait_Scope_Deltas",
}
SAFETY = {"OPT-003":"GREEN", "OPT-005":"GREEN", "CON-006":"YELLOW", "CON-009":"YELLOW", "IDX-006":"YELLOW", "IDX-010":"YELLOW", "STL-008":"RED", "STL-009":"YELLOW", "RES-007":"YELLOW"}
STATUS = {demo_id: ("IMPLEMENTED" if demo_id == "CON-009" else "VALIDATED") for demo_id in ORDER}
SOURCES = {"OPT-003":{"SRC-005"}, "OPT-005":{"SRC-005"}, "CON-006":{"SRC-004"}, "CON-009":{"SRC-029","SRC-004"}, "IDX-006":{"SRC-014","SRC-015"}, "IDX-010":{"SRC-016","SRC-017"}, "STL-008":{"SRC-033"}, "STL-009":{"SRC-033"}, "RES-007":{"SRC-035","SRC-036","SRC-051"}}
REQUIRED = {"manifest.json", "README.md", "00_Preflight.sql", "10_Setup.sql", "20_Baseline.sql", "40_Observation.sql", "50_Mitigation.sql", "90_Cleanup.sql"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    findings: list[str] = []
    source_register = (ROOT / "Documentation/Research/SOURCE_REGISTER.md").read_text(encoding="utf-8")
    matrix = {x["demoId"]: x for x in load(ROOT / "Tests/Lab/performance-lab-matrix.json")["demos"]}
    execution = {x["demoId"]: x for x in load(ROOT / "Documentation/Demo_Catalog/demo_execution_paths.json")["demos"]}
    inventory = {x["demoId"]: x for x in load(ROOT / "Documentation/Inventories/performance_scenario_inventory.json")["scenarios"]}
    for demo_id in ORDER:
        root = ROOT / PATHS[demo_id]
        missing = sorted(name for name in REQUIRED if not (root / name).is_file())
        if missing:
            findings.append(f"{demo_id}: missing {', '.join(missing)}")
            continue
        manifest = load(root / "manifest.json")
        readme = (root / "README.md").read_text(encoding="utf-8")
        sql = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.sql"))
        if manifest.get("demo_id") != demo_id or manifest.get("safety_level") != SAFETY[demo_id]:
            findings.append(f"{demo_id}: manifest identity/safety mismatch")
        for phase in [*manifest.get("phases", []), manifest.get("cleanup", {})]:
            value = phase.get("script") or phase.get("manifest")
            if not isinstance(value, str) or not (root / value).is_file():
                findings.append(f"{demo_id}: referenced phase file missing: {value}")
        if STATUS[demo_id] not in readme or "SQLPERF_SUMMARY" not in sql or "SQLPERF.Project" not in sql:
            findings.append(f"{demo_id}: status, summary or ownership markers missing")
        if "DROP DATABASE" not in sql or "SQLPERF.RunToken" not in sql:
            findings.append(f"{demo_id}: marker-verified cleanup contract incomplete")
        for source in SOURCES[demo_id]:
            if source not in readme or not re.search(rf"\| `{source}` \|.*\| ACTIVE \|", source_register):
                findings.append(f"{demo_id}: active source {source} not anchored")
        for catalog, name in ((matrix,"lab matrix"),(execution,"execution catalog"),(inventory,"scenario inventory")):
            item = catalog.get(demo_id)
            if not item or item.get("implementationStatus") != STATUS[demo_id] or item.get("safetyLevel") != SAFETY[demo_id]:
                findings.append(f"{demo_id}: {name} mismatch")
    idx = (ROOT / PATHS["IDX-010"] / "README.md").read_text(encoding="utf-8").lower()
    con = (ROOT / PATHS["CON-009"] / "README.md").read_text(encoding="utf-8").lower()
    if "defer" not in idx or "ordered nonclustered" not in idx:
        findings.append("IDX-010: deferred ordered-NCCI boundary missing")
    if "defer" not in con or "space-governance" not in con:
        findings.append("CON-009: deferred SQL Server 2025 governance boundary missing")
    runner = (ROOT / "Tests/Runtime/run_w_cov_001.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/w-cov-001.yml").read_text(encoding="utf-8")
    for demo_id in ORDER:
        if demo_id not in runner or demo_id not in workflow:
            findings.append(f"{demo_id}: runtime runner/workflow mapping missing")
    for marker in ("login_ready=0", 'docker exec -e "SQLCMDPASSWORD=${password}"', 'SELECT 1;'):
        if marker not in workflow:
            findings.append(f"runtime workflow login-readiness probe missing: {marker}")
    if findings:
        print(f"w-cov-001: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    validated = sum(status == "VALIDATED" for status in STATUS.values())
    print(f"w-cov-001: PASS ({validated} validated; {len(ORDER) - validated} implemented with runtime evidence gap)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
