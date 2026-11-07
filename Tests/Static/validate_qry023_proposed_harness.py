#!/usr/bin/env python3
"""Check the offline QRY-023 draft without invoking SQL Server or its harness."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables"
EXPECTED_PHASES = [
    "PREFLIGHT",
    "SETUP",
    "FRAMEWORK",
    "WORKLOAD",
    "QUALIFICATION_PREFLIGHT",
    "CORRECTNESS",
    "MEASUREMENT",
    "PLAN_EVIDENCE",
]


def profile_counts(path_count: int) -> tuple[int, int, int]:
    """Return (nodes, directed edges, two-hop paths) for the disjoint profile."""
    return path_count * 3, path_count * 2, path_count


def paired_order(pair_number: int) -> tuple[str, str]:
    """Return the two variants in alternating AB/BA order, starting with AB."""
    if pair_number < 1:
        raise ValueError("pair_number must be positive")
    return ("GRAPH", "RELATIONAL") if pair_number % 2 else ("RELATIONAL", "GRAPH")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(demo: Path = DEMO, repository: Path = ROOT) -> list[str]:
    errors: list[str] = []
    proposed_manifest = demo / "manifest.proposed.json"
    catalog_manifest = demo / "manifest.json"
    try:
        manifest = json.loads(proposed_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Cannot load proposed manifest: {exc}"]

    require(not catalog_manifest.exists(), "QRY-023 must not have a catalog manifest.json", errors)
    require(manifest.get("demo_id") == "QRY-023", "proposed manifest must identify QRY-023", errors)
    require(manifest.get("contract_version") == "1.0", "proposed manifest contract version must be 1.0", errors)
    require(manifest.get("safety_level") == "YELLOW", "proposed manifest must retain YELLOW", errors)
    phases = manifest.get("phases")
    require(isinstance(phases, list), "proposed manifest phases must be a list", errors)
    if isinstance(phases, list):
        require([phase.get("id") for phase in phases] == EXPECTED_PHASES,
                "phase IDs/order must match the proposed QRY-023 lifecycle", errors)
        for phase in phases:
            script = phase.get("script", "")
            require(phase.get("kind") == "sql", f"phase {phase.get('id')} must be SQL", errors)
            require(phase.get("required") is True, f"phase {phase.get('id')} must be required", errors)
            require(phase.get("require_summary") is True, f"phase {phase.get('id')} must require a summary", errors)
            require((demo / script).is_file(), f"phase script is missing: {script}", errors)
    cleanup = manifest.get("cleanup", {})
    require(cleanup.get("id") == "CLEANUP" and cleanup.get("script") == "90_Cleanup.sql",
            "manifest must bind cleanup to 90_Cleanup.sql", errors)
    require(cleanup.get("required") is True and cleanup.get("require_summary") is True,
            "cleanup must be required and summary-checked", errors)
    require((demo / cleanup.get("script", "")).is_file(), "cleanup script is missing", errors)

    def read(name: str) -> str:
        try:
            return (demo / name).read_text(encoding="utf-8").casefold()
        except OSError as exc:
            errors.append(f"Cannot read {name}: {exc}")
            return ""

    preflight = read("00_Preflight.sql")
    setup = read("10_Setup.sql")
    workload = read("20_Workload.sql")
    qualification = read("25_Qualification_Preflight.sql")
    correctness = read("30_Correctness.sql")
    measurement = read("40_Measurement.sql")
    plan = read("50_Plan_Evidence.sql")
    cleanup_sql = read("90_Cleanup.sql")
    readme = read("README.md")

    image_lock_path = demo / "container-images.proposed.json"
    try:
        image_lock = json.loads(image_lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        image_lock = {}
        errors.append(f"Cannot load proposed container image lock: {exc}")

    require(image_lock.get("contract_version") == "1.0",
            "proposed image lock contract version must be 1.0", errors)
    require(image_lock.get("status") == "PROPOSED" and image_lock.get("runtime_authorized") is False,
            "image lock must remain proposed and must not authorize runtime", errors)
    require(image_lock.get("registry") == "mcr.microsoft.com/mssql/server",
            "image lock must use the declared Microsoft registry", errors)
    image_profiles = image_lock.get("profiles")
    expected_tags = {
        15: (150, "2019-CU32-ubuntu-20.04"),
        16: (160, "2022-CU27-ubuntu-22.04"),
        17: (170, "2025-CU10-ubuntu-22.04"),
    }
    require(isinstance(image_profiles, list) and len(image_profiles) == 3,
            "image lock must declare exactly three product profiles", errors)
    image_builds: dict[int, str] = {}
    if isinstance(image_profiles, list):
        for profile in image_profiles:
            major = profile.get("product_major_version")
            require(major in expected_tags, f"unsupported image product major version: {major}", errors)
            if major not in expected_tags:
                continue
            level, tag = expected_tags[major]
            digest = profile.get("manifest_digest", "")
            config_digest = profile.get("config_digest", "")
            require(profile.get("compatibility_level") == level,
                    f"product {major} image lock has the wrong compatibility level", errors)
            require(profile.get("platform") == "linux/amd64",
                    f"product {major} image must remain linux/amd64", errors)
            require(profile.get("source_tag") == tag,
                    f"product {major} must retain its reviewed MCR source tag", errors)
            require(re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None,
                    f"product {major} must have a valid manifest digest", errors)
            require(re.fullmatch(r"sha256:[0-9a-f]{64}", config_digest) is not None,
                    f"product {major} must have a valid config digest", errors)
            require(profile.get("image") == f"mcr.microsoft.com/mssql/server@{digest}",
                    f"product {major} image reference must use its immutable manifest digest", errors)
            build = profile.get("product_version_label", "")
            require(build.startswith(f"{major}."),
                    f"product {major} image label must match its major version", errors)
            image_builds[major] = build
    for major, build in image_builds.items():
        expected_sql = f"when {major} then n'{build.casefold()}'"
        require(expected_sql in preflight and expected_sql in setup,
                f"product {major} image label must match preflight and setup build pins", errors)
    build_review = repository / "Documentation/Project_Planning/GRAPH_TABLES_BUILD_EDITION_REVIEW.md"
    try:
        review_text = build_review.read_text(encoding="utf-8").casefold()
    except OSError as exc:
        review_text = ""
        errors.append(f"Cannot read image build review: {exc}")
    if isinstance(image_profiles, list):
        for profile in image_profiles:
            for field in ("manifest_digest", "config_digest"):
                digest = profile.get(field, "").casefold()
                require(bool(digest) and digest in review_text,
                        f"image review must document {field} for product {profile.get('product_major_version')}",
                        errors)

    for label, source in (("preflight", preflight), ("setup", setup), ("workload", workload),
                          ("qualification preflight", qualification), ("cleanup", cleanup_sql)):
        for marker in ("sqlperf.project", "sqlperf.contractversion", "sqlperf.demoid", "sqlperf.runtoken"):
            require(marker in source, f"{label} must bind the {marker} ownership marker", errors)
    require("has_perms_by_name" in preflight and "create database" in preflight,
            "read-only preflight must check database creation permission", errors)
    build_pins = ("15.0.4430.1", "16.0.4295.3", "17.0.5035.5")
    for build in build_pins:
        require(build in preflight and build in setup,
                f"preflight and setup must pin the proposed engine build {build}", errors)
    require("serverproperty('productversion')" in preflight and "'engine_build'" in preflight,
            "preflight must skip before setup when ProductVersion misses its pin", errors)
    require("showplan" in qualification and "has_perms_by_name" in qualification,
            "qualification preflight must check SHOWPLAN before query execution", errors)
    require("create table dbo.person" in workload and "as node" in workload,
            "workload must create a Graph NODE table", errors)
    require("create table dbo.friendof as edge" in workload,
            "workload must create a Graph EDGE table", errors)
    require("create index ix_qry023_friendof_from_to on dbo.friendof($from_id,$to_id)" in workload,
            "candidate edge index must remain explicit", errors)
    require(profile_counts(10_000) == (30_000, 20_000, 10_000),
            "deterministic workload arithmetic must remain 30k/20k/10k", errors)
    compact_workload = re.sub(r"\s+", "", workload)
    require("personid=3*p.n+v.roleoffset" in compact_workload,
            "synthetic node IDs must use the three-role path generator", errors)
    require("personid+1" in compact_workload and "personid%3in(1,2)" in compact_workload,
            "synthetic directed edges must connect consecutive roles only", errors)
    require("where match(p1-(e1)->p2-(e2)->p3)" in workload,
            "measurement wrapper must use the declared two-hop MATCH", errors)
    require("where match(p1-(e1)->p2-(e2)->p3)" in correctness,
            "correctness phase must exercise the two-hop MATCH", errors)
    require(correctness.count(" except ") >= 4,
            "correctness must compare expected and actual tuples in both directions", errors)
    require("count_big(*)" in correctness and "<>10000" in correctness,
            "full-path oracle must enforce the 10,000-result cardinality", errors)
    require("'warmup'" in measurement and "while @pair<=5" in measurement,
            "measurement must exclude warm-ups and retain five pairs", errors)
    require("@pair%2=1" in measurement and "@pair%2=0" in measurement,
            "measurement must alternate AB/BA order", errors)
    compact_measurement = re.sub(r"\s+", "", measurement)
    require("@variant=casewhen(@pair%2=1and@order=1)or(@pair%2=0and@order=2)then'graph'else'relational'end"
            in compact_measurement,
            "measurement must implement the declared alternating order", errors)
    require([paired_order(n) for n in range(1, 6)] == [
        ("GRAPH", "RELATIONAL"), ("RELATIONAL", "GRAPH"),
        ("GRAPH", "RELATIONAL"), ("RELATIONAL", "GRAPH"),
        ("GRAPH", "RELATIONAL"),
    ], "paired-order rule must alternate across five pairs", errors)
    require("statistics xml on" in plan and "statistics xml off" in plan,
            "plan evidence must be a separate, bounded Actual Plan diagnostic", errors)
    require("measurement" not in plan, "plan diagnostic must not write measured phase records", errors)
    require("drop database" in cleanup_sql and "single_user" in cleanup_sql,
            "cleanup must remove only the owned disposable database", errors)
    require("sqlperf.project" in cleanup_sql and "sqlperf.contractversion" in cleanup_sql
            and "sqlperf.demoid" in cleanup_sql and "sqlperf.runtoken" in cleanup_sql,
            "database removal must verify all exact ownership markers", errors)
    require("proposed" in readme and "not" in readme and "katalog" in readme,
            "README must explain non-catalogued proposed status", errors)
    require("not executed" in readme or "nicht ausgeführt" in readme,
            "README must state that QRY-023 has not been executed", errors)
    require(all(build in readme for build in build_pins),
            "README must document all time-bound engine build pins", errors)
    require("container-images.proposed.json" in readme,
            "README must link the proposed immutable image lock", errors)
    require("graph" in readme and "editionsmatrizen" in readme,
            "README must state the sourced Graph edition scope", errors)

    for relative in (
        "Documentation/Demo_Catalog/demo_execution_paths.json",
        "Tests/Lab/performance-lab-matrix.json",
    ):
        path = repository / relative
        try:
            text = path.read_text(encoding="utf-8").casefold()
        except OSError as exc:
            errors.append(f"Cannot read runtime catalog {relative}: {exc}")
            continue
        require('"qry-023"' not in text, f"QRY-023 must not be registered in {relative}", errors)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL QRY-023: {error}")
        return 1
    print("PASS QRY-023 proposed harness static contract (no SQL execution)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
