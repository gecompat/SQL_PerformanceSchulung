#!/usr/bin/env python3
"""Offline-Kantenprofil für DGN-007-Docker-CLI und sechs SQL-only-Manifeste.

Nur bereits Git-/rohbytegebundene Bodies werden statisch geprüft. Das reviewte
Ganzdatei-AST-Profil ist konservativ geschlossen, kein Python-Interpreter,
Sandbox-, tatsächlicher Resolver- oder Toolsicherheitsbeweis. Host-Target und
generische Sessionmanifeste sind vorhandene, hier ungewählte Pfade.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tokenize

import dgn007_source_bundle as bundle

PROFILE = "dgn007-docker-sql-only/v1"
PYTHON_AST_VERSIONS = ((3, 12),)
AUTOMATED = bundle.DEMO + "Automated/"
CONTRACT = bundle.DEMO + "Contracts/incident-acceptance.contract.json"
# ast.dump(include_attributes=False), Parsergrammatik Python 3.12. Kommentare
# und Layout sind kein ausführbarer AST; Encoding bleibt separat geschlossen.
PYTHON_AST_SHA256 = (
    "23279ea73c10d0999d6ad10fa1b41615936ff17b8a7278887165529224438f8a",
    "585493e97ba6e4c759bccf8fe983d6b61d32253435b4b2481a195f6784d38925",
    "958e555b9e25392e4bf6024eef6ea528305bf489b43ab1ed5af35388eddd37c8",
    "555a3adc06030e7a3a2edde38cca6eee547c2bd7b2fbaecd1e93d3f87e1a0614",
    "f25c55b61537c2304cfcb1c0266215c87c80a28e8558d7e607b96b05fc8edca2",
    "d55a50c4390dcd740e050e0d9b2e471c60a6498bb70b49ed1d1231e1fb887210",
    "770372e6beba2b8ad1993d581c87038e0ed3cdb059dfad58206133f201e49d4e",
    "37c201d2d3049005fe886cc77c68f8e54a4886f911c5a459d5f0d46e57d2cc99",
    "3e11c0177f398f6144f9a1264c7a5320a4a4bdad9d5cc3aad483108f8f1caa2b",
)
# Deklarierte Kanten im oben gebundenen Profil; keine automatische Reachability.
# Externe Tools/OS/Python und spätere Importumgebung bleiben Vertrauensgrenzen.
DECLARED_EDGES = (
    ("runner.run_harness", "run_demo.py", "sys.executable + manifest + connection_arguments"),
    ("target.docker_target", "docker_sqlcmd_proxy.py", "--sqlcmd shim"),
    ("harness._execute_sql_phase", "proxy.main", "build_sqlcmd_command + _launcher"),
    ("proxy.main", "external:docker/sqlcmd", "script.read_text -> stdin; SQLCMDPASSWORD env"),
    ("runner.resolve_target", "external:docker/sh", "fixed tools18/tools probe"),
    ("target.run_sql", "external:docker/sqlcmd", "embedded engine/empty/absence SQL -> stdin"),
    ("runner.recover", "90_Cleanup.sql", "build_sqlcmd_command -> proxy"),
    ("runner.main", "incident-acceptance.contract.json", "read_text -> contract_from_mapping"),
    ("harness.load_manifest", "six fixed manifests", "SQL-only local phase paths"),
    ("process._terminate_process_tree", "external:OS", "taskkill or proc/killpg"),
)
BASE = (("PREFLIGHT", "00_Preflight.sql", "master", 30),
        ("SETUP", "10_Setup.sql", "master", 90),
        ("DATA_ASSERTION", "40_Data_Assertion.sql", "target", 30))
CLEANUP = ("CLEANUP", "90_Cleanup.sql", "master", 60)
WINDOW = ("QUERY_STORE_WINDOWS", "20_Query_Store_Windows.sql", "target", 150)
COMPARISON = ("PROFILE_COMPARISON", "30_Profile_Comparison.sql", "target", 10)
MANIFEST_PROJECTIONS = (
    ("setup.manifest.json", BASE),
    ("windows.manifest.json", BASE + (WINDOW,)),
    ("profile-comparison.manifest.json", BASE + (WINDOW, COMPARISON)),
) + tuple(("control-" + name.lower() + ".manifest.json", BASE + (
    ("CONTROL_CONFIG", "15_Control_" + name + ".sql", "target", 5),
    ("CONTROL_WINDOWS", "21_Controlled_Query_Store_Windows.sql", "target", 150),
    COMPARISON, ("CONTROL_EVIDENCE", "35_Control_Evidence.sql", "target", 10)))
    for name in ("AB", "BA", "AA"))
# Elf SQL- und ausschließlich drei Kontrollmanifeste im unveränderten v1-Vertrag.
SOURCE_KEYS = tuple(Path(p).name for p in bundle.DATA_MEMBERS if p.endswith(".sql")) + (
    "control-ab.manifest.json", "control-ba.manifest.json", "control-aa.manifest.json")
CONTRACT_POLICY_SHA256 = "2ef6f78bb9b2c604ae7dfe39b266838f6cc1bda4c14e178e1b541fc30f92f66c"


@dataclass(frozen=True)
class EdgeReport(bundle.Report):
    declared_execution_edges_verified: bool = False
    source_profile: str = PROFILE


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def _json(body: bytes) -> dict:
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise bundle.Rejected("JSON_DUPLICATE_KEY")
            result[key] = value
        return result

    def forbidden(_):
        raise bundle.Rejected("JSON_NUMBER")

    def integer(text):
        if len(text.lstrip("-")) > 19:
            raise bundle.Rejected("JSON_LIMIT")
        return int(text)

    def bounded(value, depth=0):
        if depth > 8:
            raise bundle.Rejected("JSON_LIMIT")
        if type(value) is dict:
            for item in value.values():
                bounded(item, depth + 1)
        elif type(value) is list:
            if len(value) > 32:
                raise bundle.Rejected("JSON_LIMIT")
            for item in value:
                bounded(item, depth + 1)

    try:
        value = json.loads(body.decode("utf-8"), object_pairs_hook=pairs,
                           parse_int=integer, parse_float=forbidden, parse_constant=forbidden)
        if type(value) is not dict:
            raise bundle.Rejected("JSON_SHAPE")
        bounded(value)
        return value
    except (ValueError, UnicodeError, RecursionError) as error:
        if isinstance(error, bundle.Rejected):
            raise
        raise bundle.Rejected("JSON_SHAPE") from None


def _phase(spec) -> dict:
    phase_id, script, database, timeout = spec
    return {"id": phase_id, "kind": "sql", "script": script,
            "database": database, "required": True, "require_summary": True,
            "timeout_seconds": timeout}


def _validate_edges(bodies) -> None:
    """Trusted Callback: keine Datei-, Prozess- oder Kandidaten-Codeausführung."""
    if set(bodies) != set(bundle.DGN007.members) or any(type(b) is not bytes for b in bodies.values()):
        raise bundle.Rejected("EDGE_MEMBER_SET")
    if sys.version_info[:2] not in PYTHON_AST_VERSIONS:
        raise bundle.Rejected("PYTHON_AST_VERSION")
    for path, digest in zip(bundle.PYTHON_MEMBERS, PYTHON_AST_SHA256):
        body = bodies[path]
        try:
            encoding, _ = tokenize.detect_encoding(io.BytesIO(body).readline)
            if encoding not in ("utf-8", "utf-8-sig"):
                raise bundle.Rejected("PYTHON_ENCODING")
            tree = ast.parse(body.decode("utf-8"), filename="candidate", feature_version=(3, 12))
            actual = hashlib.sha256(ast.dump(tree, include_attributes=False).encode("utf-8")).hexdigest()
        except bundle.Rejected:
            raise
        except (SyntaxError, UnicodeError, ValueError, RecursionError, MemoryError):
            raise bundle.Rejected("PYTHON_PROFILE_CHANGED") from None
        if actual != digest:
            raise bundle.Rejected("PYTHON_PROFILE_CHANGED")
    for name, specs in MANIFEST_PROJECTIONS:
        expected = {"contract_version": "1.0", "demo_id": "DGN-007", "run_token": "AUTO",
                    "safety_level": "YELLOW", "timeout_seconds": 180,
                    "cleanup_timeout_seconds": 60, "phases": [_phase(p) for p in specs],
                    "cleanup": _phase(CLEANUP)}
        if _canonical(_json(bodies[AUTOMATED + name])) != _canonical(expected):
            raise bundle.Rejected("MANIFEST_PROJECTION")
    contract = _json(bodies[CONTRACT])
    sources = contract.pop("source_sha256", None)
    if hashlib.sha256(_canonical(contract)).hexdigest() != CONTRACT_POLICY_SHA256:
        raise bundle.Rejected("CONTRACT_POLICY")
    if type(sources) is not dict or set(sources) != set(SOURCE_KEYS):
        raise bundle.Rejected("CONTRACT_SOURCE_KEYS")
    for name, digest in sources.items():
        if type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise bundle.Rejected("CONTRACT_SOURCE_HASH")
        if hashlib.sha256(bodies[AUTOMATED + name].replace(b"\r\n", b"\n")).hexdigest() != digest:
            raise bundle.Rejected("CONTRACT_SOURCE_HASH")
    for path in bundle.DATA_MEMBERS:
        if path.endswith(".sql"):
            text = bodies[path].decode("utf-8")
            if "\ufeff" in text or "\x00" in text:
                raise bundle.Rejected("SQL_ENCODING")
            # Alle SQLcmd-Zeilenbefehle, auch unbekannte und :!!, bleiben geschlossen.
            if any(line.lstrip().startswith(":") or line.lstrip().startswith("!!")
                   for line in text.splitlines()):
                raise bundle.Rejected("SQLCMD_DIRECTIVE")


def verify_execution_edges(repository: Path, commit: str, candidate: Path) -> EdgeReport:
    """Fixe Policy; Default-Bundle-API, CLI und Fehlercodes bleiben erhalten."""
    report = bundle.verify_bundle(repository, commit, candidate, bound_validator=_validate_edges)
    return EdgeReport(**asdict(report), declared_execution_edges_verified=
                      report.status == "PASS_STATIC_CANDIDATE")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args(argv)
    result = verify_execution_edges(args.repository, args.commit, args.candidate)
    print(json.dumps(asdict(result), sort_keys=True))
    return 0 if result.declared_execution_edges_verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
