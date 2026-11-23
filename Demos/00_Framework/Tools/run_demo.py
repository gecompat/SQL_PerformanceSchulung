#!/usr/bin/env python3
"""FWK-010 runtime harness for one SQL Server performance demo.

The harness invokes the external Microsoft sqlcmd tool without a shell, parses
machine-readable SQLPERF summaries, enforces one global phase budget, and runs
cleanup after a started setup phase. It never writes captured SQL output to
disk. Raw output is shown only with --show-output.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Mapping

from orchestrate_sessions import run_manifest as run_session_manifest
from sqlcmd_process import (
    build_sqlcmd_command,
    extract_summary,
    resolve_sqlcmd,
    run_sqlcmd,
)


DEMO_ID_PATTERN = re.compile(r"(STL|OPT|QRY|IDX|CON|RES|DGN)-[0-9]{3}")
RUN_TOKEN_PATTERN = re.compile(r"[A-Z0-9][A-Z0-9_]{0,19}")
PHASE_ID_PATTERN = re.compile(r"[A-Z][A-Z0-9_]{0,31}")
IDENTITY_PROFILE_PATTERN = re.compile(r"[A-Z][A-Z0-9_]{0,31}")
SQLCMD_IDENTITY_PATTERN = re.compile(r"[A-Za-z0-9_]{1,128}")
CORE_SQLCMD_VARIABLES = frozenset({
    "DemoId", "RunToken", "TargetDatabase", "SafetyLevel", "ConfirmIsolatedLab",
    "HighImpactConfirmed", "DisposableEnvironmentConfirmed", "RecoveryPlanConfirmed",
    "MaximumRuntimeSeconds", "StandardEndpointInventory", "BoundObjectInventory",
})
CORE_SQLCMD_VARIABLE_NAMES = frozenset(name.casefold() for name in CORE_SQLCMD_VARIABLES)
CONTAINER_PHASE_KINDS = frozenset({"idx007_container", "opt018_container"})
OPT018_MANIFEST = Path(__file__).resolve().parents[2] / (
    "04_Optimizer_Statistics_Plans/OPT-018_Optimized_Sp_Executesql/manifest.json"
)
OUTCOME_PRIORITY = {"PASS": 0, "WARN": 1, "SKIP": 2, "FAIL": 3}
QRY023_ENDPOINT_INVENTORY_HANDOFF = {
    "format": "ENDPOINT_ID_G_NAME_HEX_H_RECORDS_UTF16LE_HEX",
    "markers": ["QRY023_ENDPOINT_INVENTORY|BEGIN|N", "QRY023_ENDPOINT|ID|HEX", "QRY023_ENDPOINT_INVENTORY|END|N"],
    "maximum_endpoints": 12,
    "consumer": "ACTUAL_READER_CONNECTION",
    "invalid_or_incomplete": "FAIL_NOT_PROVEN",
}
QRY023_OBJECT_INVENTORY_HANDOFF = {
    "format": "FIXED_EXPECTED_OBJECT_COUNT",
    "marker": "QRY023_OBJECT_INVENTORY|PASS|13",
    "consumer": "ACTUAL_READER_CONNECTION",
    "invalid_or_incomplete": "FAIL_NOT_PROVEN",
}
QRY023_SQLCMD_INPUT_VALIDATION = {
    "must_validate_before": "SQLCMD_EXPANSION",
    "reject_invalid": True,
    "demo_id": {"mode": "EXACT", "value": "QRY-023"},
    "run_token": {
        "encoding": "ASCII",
        "allowed_characters": "A-Z0-9_",
        "first_character": "A-Z0-9",
        "min_bytes": 1,
        "max_bytes": 20,
    },
    "target_database": {
        "template": "SQLPERF_LAB_{DEMO_ID_WITHOUT_HYPHEN}_{RUN_TOKEN}"
    },
}


@dataclass(frozen=True)
class PhaseSpec:
    phase_id: str
    kind: str
    path: Path
    database_selector: str
    required: bool
    require_summary: bool
    timeout_seconds: int | None
    credential_profile: str | None


@dataclass(frozen=True)
class DemoManifest:
    demo_id: str
    run_token: str
    safety_level: str
    timeout_seconds: int
    cleanup_timeout_seconds: int
    phases: tuple[PhaseSpec, ...]
    cleanup: PhaseSpec | None
    credential_profiles: tuple[str, ...]
    sqlcmd_identity_variables: Mapping[str, str]


@dataclass(frozen=True)
class PhaseResult:
    phase_id: str
    outcome: str
    code: str
    message: str
    duration_seconds: float
    started_ns: int | None = None
    finished_ns: int | None = None


@dataclass(frozen=True)
class HarnessResult:
    outcome: str
    code: str
    message: str
    phases: tuple[PhaseResult, ...]

    @property
    def exit_code(self) -> int:
        if self.outcome in {"PASS", "WARN", "SKIP"}:
            return 0
        if self.code == "FAIL_TIMEOUT":
            return 3
        if self.code == "FAIL_CLEANUP":
            return 4
        return 2


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid demo manifest: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("demo manifest root must be a JSON object")
    return payload


def _resolve_local_path(base: Path, relative_value: str, suffixes: set[str]) -> Path:
    candidate = (base / relative_value).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError("manifest path escapes its directory") from exc
    if not candidate.is_file() or candidate.suffix.lower() not in suffixes:
        raise ValueError(f"manifest file missing or has invalid suffix: {relative_value}")
    return candidate


def _parse_phase(raw: Any, base: Path, *, cleanup: bool = False) -> PhaseSpec:
    if not isinstance(raw, dict):
        raise ValueError("each phase must be a JSON object")

    phase_id = raw.get("id")
    kind = raw.get("kind", "sql")
    path_value = raw.get("script" if kind in {"sql", *CONTAINER_PHASE_KINDS} else "manifest")
    database_selector = raw.get("database", "target")
    required = raw.get("required", True)
    require_summary = raw.get("require_summary", phase_id == "PREFLIGHT")
    timeout_seconds = raw.get("timeout_seconds")
    credential_profile = raw.get("credential_profile")

    if not isinstance(phase_id, str) or not PHASE_ID_PATTERN.fullmatch(phase_id):
        raise ValueError(f"invalid phase id: {phase_id!r}")
    if kind not in {"sql", "multi_session", *CONTAINER_PHASE_KINDS}:
        raise ValueError(f"invalid phase kind for {phase_id}")
    if not isinstance(path_value, str):
        raise ValueError(f"phase {phase_id} requires a file path")
    if database_selector not in {"master", "target"}:
        raise ValueError(f"phase {phase_id} database must be master or target")
    if not isinstance(required, bool) or not isinstance(require_summary, bool):
        raise ValueError(f"phase {phase_id} required/require_summary must be boolean")
    if timeout_seconds is not None and (
        not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 3600
    ):
        raise ValueError(f"phase {phase_id} timeout_seconds must be 1 through 3600")
    if credential_profile is not None and (
        not isinstance(credential_profile, str)
        or not IDENTITY_PROFILE_PATTERN.fullmatch(credential_profile)
    ):
        raise ValueError(f"invalid credential profile for {phase_id}")
    if cleanup and kind != "sql":
        raise ValueError("cleanup must be a SQL phase")

    if kind in CONTAINER_PHASE_KINDS and (database_selector != "master" or credential_profile is not None):
        raise ValueError("IDX-007 container phase cannot use a server database or credentials")

    suffixes = {".sql"} if kind == "sql" else ({".py"} if kind in CONTAINER_PHASE_KINDS else {".json"})
    return PhaseSpec(
        phase_id=phase_id,
        kind=kind,
        path=_resolve_local_path(base, path_value, suffixes),
        database_selector=database_selector,
        required=required,
        require_summary=require_summary,
        timeout_seconds=timeout_seconds,
        credential_profile=credential_profile,
    )


def _parse_credential_profiles(payload: dict[str, Any]) -> tuple[str, ...]:
    if "credential_profiles" not in payload:
        return ()
    raw_profiles = payload["credential_profiles"]
    if (type(raw_profiles) is not list or not 2 <= len(raw_profiles) <= 16
            or any(type(profile) is not str
                   or IDENTITY_PROFILE_PATTERN.fullmatch(profile) is None
                   for profile in raw_profiles)
            or len(raw_profiles) != len(set(raw_profiles))):
        raise ValueError("credential_profiles must contain 2 through 16 unique uppercase names")
    return tuple(raw_profiles)


def _parse_sqlcmd_identity_variables(payload: dict[str, Any], profiles: tuple[str, ...]) -> dict[str, str]:
    raw = payload.get("sqlcmd_identity_variables", {})
    if not isinstance(raw, dict):
        raise ValueError("sqlcmd_identity_variables must be an object")
    parsed: dict[str, str] = {}
    for variable, profile in raw.items():
        if (not isinstance(variable, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", variable)
                or variable.casefold() in CORE_SQLCMD_VARIABLE_NAMES
                or not isinstance(profile, str) or profile not in profiles):
            raise ValueError("invalid or reserved sqlcmd_identity_variables mapping")
        parsed[variable] = profile
    return parsed


def _validate_sqlcmd_input_contract(payload: dict[str, Any], demo_id: str, run_token: str) -> None:
    """Enforce the declared QRY-023 caller contract before any SQLCMD process starts."""
    if "sqlcmd_input_validation" not in payload:
        return

    contract = payload["sqlcmd_input_validation"]
    expected = json.dumps(QRY023_SQLCMD_INPUT_VALIDATION, sort_keys=True, separators=(",", ":"))
    actual = json.dumps(contract, sort_keys=True, separators=(",", ":"))
    if type(contract) is not dict or actual != expected:
        raise ValueError("invalid sqlcmd_input_validation contract")

    if demo_id != "QRY-023":
        raise ValueError("sqlcmd_input_validation requires demo_id QRY-023")
    if not run_token.isascii() or not re.fullmatch(r"[A-Z0-9][A-Z0-9_]{0,19}", run_token):
        raise ValueError("run_token does not satisfy sqlcmd_input_validation")

    target_template = contract["target_database"]["template"]
    target_name = target_template.format(
        DEMO_ID_WITHOUT_HYPHEN=demo_id.replace("-", ""),
        RUN_TOKEN=run_token,
    )
    if target_name != target_database_name(demo_id, run_token):
        raise ValueError("target database does not satisfy sqlcmd_input_validation")


def load_manifest(path: Path) -> DemoManifest:
    payload = _load_json_object(path)
    if payload.get("contract_version") != "1.0":
        raise ValueError("contract_version must be 1.0")

    demo_id = payload.get("demo_id")
    run_token = payload.get("run_token")
    safety_level = payload.get("safety_level")
    timeout_seconds = payload.get("timeout_seconds")
    cleanup_timeout_seconds = payload.get("cleanup_timeout_seconds", 60)

    if not isinstance(demo_id, str) or not DEMO_ID_PATTERN.fullmatch(demo_id):
        raise ValueError("invalid demo_id")
    if not isinstance(run_token, str) or not RUN_TOKEN_PATTERN.fullmatch(run_token):
        raise ValueError("invalid run_token")
    _validate_sqlcmd_input_contract(payload, demo_id, run_token)
    if safety_level not in {"GREEN", "YELLOW", "RED"}:
        raise ValueError("safety_level must be GREEN, YELLOW, or RED")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 7200:
        raise ValueError("timeout_seconds must be 1 through 7200")
    if not isinstance(cleanup_timeout_seconds, int) or not 1 <= cleanup_timeout_seconds <= 900:
        raise ValueError("cleanup_timeout_seconds must be 1 through 900")

    raw_phases = payload.get("phases")
    if not isinstance(raw_phases, list) or not 1 <= len(raw_phases) <= 20:
        raise ValueError("phases must contain 1 through 20 entries")

    credential_profiles = _parse_credential_profiles(payload)
    sqlcmd_identity_variables = _parse_sqlcmd_identity_variables(payload, credential_profiles)
    phases = tuple(_parse_phase(raw, path.parent) for raw in raw_phases)
    ids = [phase.phase_id for phase in phases]
    if len(ids) != len(set(ids)):
        raise ValueError("phase ids must be unique")
    if "PREFLIGHT" not in ids:
        raise ValueError("a PREFLIGHT phase is required")
    cleanup_raw = payload.get("cleanup")
    cleanup = _parse_phase(cleanup_raw, path.parent, cleanup=True) if cleanup_raw is not None else None
    container_phases = tuple(phase for phase in phases if phase.kind == "idx007_container")
    if container_phases and (
        demo_id != "IDX-007" or safety_level != "YELLOW" or len(phases) != 1
        or len(container_phases) != 1 or container_phases[0].phase_id != "PREFLIGHT"
        or container_phases[0].path.name != "run_idx007_demo.py" or cleanup is not None
        or payload.get("resource_lifecycle") != "self_cleaning_idx007_container"
    ):
        raise ValueError("container runtime is restricted to the self-cleaning IDX-007 demo contract")
    opt018_phases = tuple(phase for phase in phases if phase.kind == "opt018_container")
    if opt018_phases and (
        demo_id != "OPT-018" or safety_level != "YELLOW" or run_token != "LOCAL"
        or path.resolve() != OPT018_MANIFEST or len(phases) != 1
        or opt018_phases[0].phase_id != "PREFLIGHT" or not opt018_phases[0].required
        or not opt018_phases[0].require_summary or opt018_phases[0].timeout_seconds != 325
        or opt018_phases[0].path != OPT018_MANIFEST.with_name("run_opt018_demo.py")
        or cleanup is not None or timeout_seconds != 330 or cleanup_timeout_seconds != 60
        or payload.get("resource_lifecycle") != "self_cleaning_opt018_container"
    ):
        raise ValueError("container runtime is restricted to the self-cleaning OPT-018 demo contract")
    if "ADMIN_PERMISSION_INVENTORY" in ids:
        expected_handoff = json.dumps(QRY023_ENDPOINT_INVENTORY_HANDOFF, sort_keys=True, separators=(",", ":"))
        contract = payload.get("admin_permission_inventory_contract")
        actual_handoff = json.dumps(contract.get("endpoint_inventory_handoff") if isinstance(contract, dict) else None,
                                    sort_keys=True, separators=(",", ":"))
        expected_objects = json.dumps(QRY023_OBJECT_INVENTORY_HANDOFF, sort_keys=True, separators=(",", ":"))
        actual_objects = json.dumps(contract.get("object_inventory_handoff") if isinstance(contract, dict) else None,
                                    sort_keys=True, separators=(",", ":"))
        if demo_id != "QRY-023" or actual_handoff != expected_handoff or actual_objects != expected_objects:
            raise ValueError("invalid QRY-023 endpoint inventory handoff contract")

    all_phases = (*phases, *((cleanup,) if cleanup is not None else ()))
    used_profiles = {phase.credential_profile for phase in all_phases
                     if phase.credential_profile is not None}
    if credential_profiles:
        if any(phase.kind != "sql" or phase.credential_profile is None
               for phase in all_phases):
            raise ValueError("credential profile manifests require a profile on every SQL phase and do not support multi-session phases")
        if used_profiles != set(credential_profiles):
            raise ValueError("credential_profiles must exactly match profiles assigned to phases")
    elif used_profiles:
        raise ValueError("phase credential_profile requires manifest credential_profiles")

    return DemoManifest(
        demo_id=demo_id,
        run_token=run_token,
        safety_level=safety_level,
        timeout_seconds=timeout_seconds,
        cleanup_timeout_seconds=cleanup_timeout_seconds,
        phases=phases,
        cleanup=cleanup,
        credential_profiles=credential_profiles,
        sqlcmd_identity_variables=sqlcmd_identity_variables,
    )


def _resolve_credential_profiles(
    profile_names: tuple[str, ...],
) -> dict[str, tuple[str, str]]:
    resolved: dict[str, tuple[str, str]] = {}
    seen_usernames: set[str] = set()
    for profile in profile_names:
        username = os.environ.get(f"SQLPERF_SQL_USERNAME_{profile}")
        password = os.environ.get(f"SQLPERF_SQL_PASSWORD_{profile}")
        if (not isinstance(username, str) or not username.strip()
                or any(char in username for char in "\r\n\x00")):
            raise ValueError(f"missing or invalid SQL username for credential profile {profile}")
        if not isinstance(password, str) or not password or "\x00" in password:
            raise ValueError(f"missing or invalid SQL password for credential profile {profile}")
        normalized_username = username.strip().casefold()
        if normalized_username in seen_usernames:
            raise ValueError("credential profiles must resolve to distinct SQL usernames")
        seen_usernames.add(normalized_username)
        resolved[profile] = (username.strip(), password)
    return resolved


def _phase_connection(
    phase: PhaseSpec,
    *,
    username: str | None,
    credentials: Mapping[str, tuple[str, str]],
) -> tuple[str | None, Mapping[str, str]]:
    environment = os.environ.copy()
    for key in tuple(environment):
        if key.upper().startswith(("SQLPERF_SQL_USERNAME_", "SQLPERF_SQL_PASSWORD_", "SQLCMDPASSWORD_")):
            environment.pop(key, None)
    if phase.credential_profile is None:
        return username, environment
    profile_username, password = credentials[phase.credential_profile]
    environment["SQLCMDPASSWORD"] = password
    return profile_username, environment


def target_database_name(demo_id: str, run_token: str) -> str:
    return f"SQLPERF_LAB_{demo_id.replace('-', '')}_{run_token}"


def _combine_result(current: tuple[str, str], candidate: tuple[str, str]) -> tuple[str, str]:
    if candidate == ("FAIL", "FAIL_CLEANUP") or OUTCOME_PRIORITY[candidate[0]] > OUTCOME_PRIORITY[current[0]]:
        return candidate
    return current


def _emit_raw_output(phase_id: str, stdout: str, stderr: str) -> None:
    if stdout:
        for line in stdout.rstrip().splitlines():
            print(f"[{phase_id}:stdout] {line}")
    if stderr:
        for line in stderr.rstrip().splitlines():
            print(f"[{phase_id}:stderr] {line}", file=sys.stderr)


def _validate_qry023_object_inventory(*texts: str) -> None:
    """Require exactly one successful ADMIN binding for all 13 expected objects."""
    lines = [line.strip() for text in texts for line in text.splitlines()]
    markers = [line for line in lines if line.startswith("QRY023_OBJECT_INVENTORY|")]
    if markers != [QRY023_OBJECT_INVENTORY_HANDOFF["marker"]]:
        raise ValueError("missing, duplicate, or invalid ADMIN object inventory marker")


def _extract_qry023_endpoint_inventory(*texts: str) -> str:
    """Parse and canonicalize the bounded ADMIN-to-READER endpoint handoff."""
    lines = [line.strip() for text in texts for line in text.splitlines()]
    begins = [line for line in lines if line.startswith("QRY023_ENDPOINT_INVENTORY|BEGIN|")]
    ends = [line for line in lines if line.startswith("QRY023_ENDPOINT_INVENTORY|END|")]
    records = [line for line in lines if line.startswith("QRY023_ENDPOINT|")]
    if len(begins) != 1 or len(ends) != 1:
        raise ValueError("missing or duplicate endpoint inventory boundary")
    count_pattern = re.compile(r"QRY023_ENDPOINT_INVENTORY\|(BEGIN|END)\|([1-9][0-9]?)\Z")
    begin = count_pattern.fullmatch(begins[0])
    end = count_pattern.fullmatch(ends[0])
    if begin is None or end is None or begin.group(2) != end.group(2):
        raise ValueError("invalid endpoint inventory count")
    count = int(begin.group(2))
    if count > 12 or len(records) != count:
        raise ValueError("endpoint inventory is incomplete or exceeds its bound")
    lines_between = [line for line in lines if line.startswith("QRY023_ENDPOINT")]
    if lines_between[0] != begins[0] or lines_between[-1] != ends[0] or lines_between[1:-1] != records:
        raise ValueError("endpoint records are outside their inventory boundary")
    ids: set[int] = set()
    names: set[str] = set()
    parsed: list[tuple[int, str]] = []
    for record in records:
        match = re.fullmatch(r"QRY023_ENDPOINT\|([1-9][0-9]{0,4})\|([0-9A-F]{4,512})", record)
        if match is None or len(match.group(2)) % 4:
            raise ValueError("invalid endpoint record")
        endpoint_id = int(match.group(1))
        if endpoint_id > 65535:
            raise ValueError("endpoint ID outside supported range")
        try:
            name = bytes.fromhex(match.group(2)).decode("utf-16le", errors="strict")
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError("invalid UTF-16LE endpoint name") from exc
        if not name or len(name) > 128 or "\x00" in name:
            raise ValueError("invalid endpoint name")
        folded = name.casefold()
        if endpoint_id in ids or folded in names:
            raise ValueError("duplicate endpoint ID or name")
        ids.add(endpoint_id)
        names.add(folded)
        parsed.append((endpoint_id, match.group(2)))
    # G/H delimiters are outside hexadecimal and keep the -v scalar free of SQLCMD separators.
    encoded = "H".join(f"{endpoint_id}G{hex_name}" for endpoint_id, hex_name in sorted(parsed))
    if len(encoded) > 8191:
        raise ValueError("canonical endpoint inventory exceeds SQLCMD variable limit")
    return encoded


def _execute_sql_phase(
    *,
    phase: PhaseSpec,
    executable: str,
    server: str,
    target_database: str,
    auth: str,
    username: str | None,
    environment: Mapping[str, str],
    timeout_seconds: float,
    variables: dict[str, str],
    show_output: bool,
) -> PhaseResult:
    database = "master" if phase.database_selector == "master" else target_database
    password_present = bool(environment.get("SQLCMDPASSWORD"))
    had_ambient_password = "SQLCMDPASSWORD" in os.environ
    ambient_password = os.environ.get("SQLCMDPASSWORD")
    try:
        if password_present:
            # The command builder checks presence only; keep the real secret in the child env.
            os.environ["SQLCMDPASSWORD"] = "credential-profile-configured"
        command = build_sqlcmd_command(
            executable=executable,
            server=server,
            database=database,
            script=phase.path,
            auth=auth,
            username=username,
            variables=variables,
        )
    finally:
        if had_ambient_password:
            os.environ["SQLCMDPASSWORD"] = ambient_password or ""
        else:
            os.environ.pop("SQLCMDPASSWORD", None)
    started = time.monotonic()
    result = run_sqlcmd(command, timeout_seconds=timeout_seconds, environment=environment)
    if show_output:
        _emit_raw_output(phase.phase_id, result.stdout, result.stderr)
    if result.timed_out:
        return PhaseResult(phase.phase_id, "FAIL", "FAIL_TIMEOUT", "Die SQL-Phase überschritt ihr Zeitbudget.", time.monotonic() - started)
    if result.returncode != 0:
        return PhaseResult(phase.phase_id, "FAIL", "FAIL_EXECUTION", "sqlcmd meldete einen Fehler für diese Phase.", time.monotonic() - started)

    summary = extract_summary(result.stdout, result.stderr)
    if summary is None:
        if phase.require_summary:
            return PhaseResult(phase.phase_id, "FAIL", "FAIL_CONTRACT", "Die erforderliche SQLPERF-Summary fehlt.", time.monotonic() - started)
        return PhaseResult(phase.phase_id, "PASS", "OK", "Die Phase wurde ohne strukturierten Fehler abgeschlossen.", time.monotonic() - started)

    outcome, code = summary
    if phase.phase_id == "ADMIN_PERMISSION_INVENTORY" and variables.get("DemoId") == "QRY-023":
        if outcome != "PASS":
            return PhaseResult(phase.phase_id, "FAIL", "FAIL_NOT_PROVEN",
                               "ADMIN-Rechte- und Endpointinventar ist nicht vollständig bestanden.",
                               time.monotonic() - started)
        try:
            _validate_qry023_object_inventory(result.stdout, result.stderr)
            variables["BoundObjectInventory"] = "13"
            variables["StandardEndpointInventory"] = _extract_qry023_endpoint_inventory(result.stdout, result.stderr)
        except ValueError as exc:
            return PhaseResult(phase.phase_id, "FAIL", "FAIL_CONTRACT",
                               f"ADMIN-Endpointinventar ist nicht vollständig gebunden: {exc}.",
                               time.monotonic() - started)
    if outcome == "SKIP" and not phase.required:
        return PhaseResult(phase.phase_id, "WARN", "WARN_OPTIONAL_EVIDENCE_SKIPPED", f"Optionale Phase wurde kontrolliert übersprungen: {code}.", time.monotonic() - started)
    return PhaseResult(phase.phase_id, outcome, code, "Strukturierte Phase-Summary wurde ausgewertet.", time.monotonic() - started)


def _execute_idx007_container_phase(phase: PhaseSpec, *, major: int, timeout_seconds: float,
                                    show_output: bool) -> PhaseResult:
    started = time.monotonic()
    owner_token = os.urandom(16).hex()
    command = [sys.executable, str(phase.path), "--major", str(major)]
    environment = os.environ.copy()
    for name in tuple(environment):
        if name.upper().startswith(("SQLPERF_SQL_", "SQLCMDPASSWORD")):
            environment.pop(name, None)
    environment["SQLPERF_IDX007_OWNER_TOKEN"] = owner_token
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout_seconds, check=False, env=environment,
        )
    except subprocess.TimeoutExpired:
        cleanup_ok = _cleanup_idx007_owned_container(owner_token)
        code = "FAIL_TIMEOUT" if cleanup_ok else "FAIL_CLEANUP"
        message = "IDX-007 Laufzeitbudget überschritten; markierte Wegwerfcontainer wurden entfernt." if cleanup_ok else "IDX-007 Zeitlimit und anschließende Containerbereinigung fehlgeschlagen."
        return PhaseResult(phase.phase_id, "FAIL", code, message, time.monotonic() - started)
    if show_output:
        _emit_raw_output(phase.phase_id, result.stdout, result.stderr)
    else:
        visible_prefixes = (
            "LESSON|", "ENGINE_BUILD|", "RIGHT_EDGE|", "COMPATIBILITY|", "XE_PROFILE|",
            "WAIT_OVERLAP|", "CHAIN_BRACKET|", "RESULT|", "DB_ABSENT=", "CONTAINER_REMOVED=",
            "NOT_PROVEN|", "SQLPERF_SUMMARY|", "TRIAL_START|", "TRIAL_SUMMARY|",
        )
        for line in result.stdout.splitlines():
            if line.startswith(visible_prefixes):
                print(f"[{phase.phase_id}] {line}")
        if result.stderr.strip():
            print(f"[{phase.phase_id}:stderr] {result.stderr.strip()}", file=sys.stderr)
    summaries = [line.strip() for line in result.stdout.splitlines()
                 if line.startswith("SQLPERF_SUMMARY|")]
    if len(summaries) != 1:
        return PhaseResult(phase.phase_id, "FAIL", "FAIL_CONTRACT", "IDX-007 muss genau eine strukturierte SQLPERF_SUMMARY liefern.", time.monotonic() - started)
    if result.returncode == 0 and summaries[0] == "SQLPERF_SUMMARY|PASS|OK":
        return PhaseResult(phase.phase_id, "PASS", "OK", "IDX-007 Messlauf und Ressourcenbereinigung wurden bestätigt.", time.monotonic() - started)
    if result.returncode == 0 and summaries[0] == "SQLPERF_SUMMARY|WARN|WARN_NOT_PROVEN":
        return PhaseResult(phase.phase_id, "WARN", "WARN_NOT_PROVEN", "Der kontrollierte Lauf konnte die erwartete Wait/Page-Überlappung nicht belegen; der Container wurde bereinigt.", time.monotonic() - started)
    return PhaseResult(phase.phase_id, "FAIL", "FAIL_EXECUTION", "IDX-007 Lauf oder markergebundene Bereinigung fehlgeschlagen.", time.monotonic() - started)


def _execute_opt018_container_phase(phase: PhaseSpec, *, timeout_seconds: float) -> PhaseResult:
    started = time.monotonic()
    command = [sys.executable, str(phase.path)]
    environment = {key: value for key, value in os.environ.items()
                   if not key.upper().startswith(("SQLPERF_SQL_", "SQLCMDPASSWORD"))}
    owner = os.urandom(16).hex()
    environment["SQLPERF_OPT018_OWNER_TOKEN"] = owner

    def run(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout, check=False, env=environment)

    try:
        result = run(command, timeout_seconds)
    except subprocess.TimeoutExpired:
        try:
            recovered = run([*command, "--recover"], 65).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            recovered = False
        code = "FAIL_TIMEOUT" if recovered else "FAIL_CLEANUP"
        message = "OPT-018 Zeitbudget überschritten; Containerabwesenheit wurde geprüft." if recovered else (
            f"OPT-018 Zeitbudget überschritten; Containerabwesenheit ist offen. Besitzmarker: {owner}."
        )
        return PhaseResult(phase.phase_id, "FAIL", code, message, time.monotonic() - started)
    except OSError:
        return PhaseResult(phase.phase_id, "FAIL", "FAIL_EXECUTION", "OPT-018 konnte nicht gestartet werden.",
                           time.monotonic() - started)

    lines = result.stdout.splitlines()
    markers = [line for line in lines if line.startswith("SQLPERF_SUMMARY|")]
    for line in lines:
        if re.fullmatch(r"OPTSP\|[A-Z_]+\|(PROVEN|NOT_PROVEN)\|[a-z_]+", line):
            print(f"[{phase.phase_id}] {line}")
    allowed = {
        (0, ("SQLPERF_SUMMARY|PASS|OK",)): ("PASS", "OK", "Beide OPT-018-Paare und der Abbau wurden bestätigt."),
        (1, ("SQLPERF_SUMMARY|FAIL|FAIL_NOT_PROVEN",)): ("FAIL", "FAIL_NOT_PROVEN", "Die OPT-018-Evidenz ist unvollständig."),
        (3, ("SQLPERF_SUMMARY|FAIL|FAIL_CLEANUP",)): ("FAIL", "FAIL_CLEANUP",
                                                         f"Der OPT-018-Abbau ist unbestätigt. Besitzmarker: {owner}."),
    }
    outcome, code, message = allowed.get(
        (result.returncode, tuple(markers)), ("FAIL", "FAIL_CONTRACT", "OPT-018 lieferte keine eindeutige Summary."),
    )
    return PhaseResult(phase.phase_id, outcome, code, message, time.monotonic() - started)


def _cleanup_idx007_owned_container(owner_token: str) -> bool:
    if not re.fullmatch(r"[0-9a-f]{32}", owner_token):
        return False
    try:
        listed = subprocess.run(
            ["docker", "ps", "-aq", "--filter", f"label=sqlperf.demo.owner={owner_token}"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, check=False,
        )
        if listed.returncode != 0:
            return False
        for container_id in listed.stdout.splitlines():
            container_id = container_id.strip()
            if not re.fullmatch(r"[0-9a-fA-F]{12,64}", container_id):
                return False
            inspected = subprocess.run(
                ["docker", "inspect", container_id], capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=30, check=False,
            )
            if inspected.returncode != 0:
                return False
            item = json.loads(inspected.stdout)[0]
            labels = item["Config"]["Labels"]
            isolated = item["HostConfig"]["NetworkMode"] == "none"
            if (labels.get("sqlperf.demo.id") != "IDX-007"
                    or labels.get("sqlperf.demo.owner") != owner_token or not isolated):
                return False
            removed = subprocess.run(
                ["docker", "rm", "--force", container_id], capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=30, check=False,
            )
            if removed.returncode != 0:
                return False
    except (OSError, subprocess.TimeoutExpired, IndexError, KeyError, json.JSONDecodeError):
        return False
    return True


def run_demo(
    *,
    manifest_path: Path,
    server: str | None,
    auth: str,
    username: str | None,
    sqlcmd_path: str | None,
    confirm_isolated_lab: bool,
    allow_red: bool,
    show_output: bool,
    emit_phase_timing_protocol: bool = False,
    idx007_major: int | None = None,
) -> HarnessResult:
    manifest = load_manifest(manifest_path.resolve())

    if (emit_phase_timing_protocol
            and (manifest.demo_id != "DGN-007" or manifest.run_token != "AUTO")):
        raise ValueError("phase timing protocol is reserved for DGN-007 AUTO runs")

    if manifest.safety_level == "YELLOW" and not confirm_isolated_lab:
        return HarnessResult("FAIL", "FAIL_SAFETY", "Gelbe Demo benötigt --confirm-isolated-lab.", ())
    if manifest.safety_level == "RED" and not allow_red:
        return HarnessResult("FAIL", "FAIL_SAFETY", "Rote Demo benötigt --allow-red.", ())

    has_container_phase = any(phase.kind in CONTAINER_PHASE_KINDS for phase in manifest.phases)
    if manifest.phases[0].kind == "idx007_container" and idx007_major not in {15, 16, 17}:
        raise ValueError("IDX-007 requires --idx007-major 15, 16, or 17")
    if not has_container_phase and not server:
        raise ValueError("server is required by argument or SQLPERF_SQL_SERVER")

    if manifest.credential_profiles and auth.strip().lower() != "sql":
        raise ValueError("credential_profiles require SQL authentication")
    credentials = _resolve_credential_profiles(manifest.credential_profiles)
    for variable, profile in manifest.sqlcmd_identity_variables.items():
        if not SQLCMD_IDENTITY_PATTERN.fullmatch(credentials[profile][0]):
            raise ValueError(f"credential profile {profile} username is not a safe SQLCMD identity")

    executable = None if has_container_phase else resolve_sqlcmd(sqlcmd_path)
    target_database = target_database_name(manifest.demo_id, manifest.run_token)
    variables = {
        "DemoId": manifest.demo_id,
        "RunToken": manifest.run_token,
        "TargetDatabase": target_database,
        "SafetyLevel": manifest.safety_level,
        "ConfirmIsolatedLab": "1" if confirm_isolated_lab else "0",
        "HighImpactConfirmed": "1" if confirm_isolated_lab or allow_red else "0",
        "DisposableEnvironmentConfirmed": "1" if allow_red else "0",
        "RecoveryPlanConfirmed": "1" if allow_red else "0",
        "MaximumRuntimeSeconds": str(manifest.timeout_seconds),
    }
    variables.update({variable: credentials[profile][0]
                      for variable, profile in manifest.sqlcmd_identity_variables.items()})

    deadline = time.monotonic() + manifest.timeout_seconds
    phase_results: list[PhaseResult] = []
    aggregate = ("PASS", "OK")
    setup_started = False
    stop_regular_phases = False
    suppress_qry023_cleanup = False

    for phase in manifest.phases:
        if stop_regular_phases:
            break
        phase_started_ns = time.monotonic_ns() if emit_phase_timing_protocol else None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            result = PhaseResult(phase.phase_id, "FAIL", "FAIL_TIMEOUT", "Das globale Harness-Zeitbudget ist abgelaufen.", 0.0)
        else:
            phase_timeout = min(remaining, phase.timeout_seconds or remaining)
            if phase.kind == "sql":
                phase_username, phase_environment = _phase_connection(
                    phase, username=username, credentials=credentials
                )
                if phase.phase_id == "SETUP":
                    setup_started = True
                result = _execute_sql_phase(
                    phase=phase,
                    executable=executable,
                    server=server,
                    target_database=target_database,
                    auth=auth,
                    username=phase_username,
                    environment=phase_environment,
                    timeout_seconds=phase_timeout,
                    variables=variables,
                    show_output=show_output,
                )
            elif phase.kind == "multi_session":
                orchestration = run_session_manifest(
                    manifest_path=phase.path,
                    server=server,
                    database=target_database,
                    auth=auth,
                    username=username,
                    sqlcmd_path=executable,
                    show_output=show_output,
                    timeout_override_seconds=max(1, int(phase_timeout)),
                )
                result = PhaseResult(phase.phase_id, orchestration.outcome, orchestration.code, orchestration.message, 0.0)
            elif phase.kind == "opt018_container":
                result = _execute_opt018_container_phase(phase, timeout_seconds=phase_timeout)
            else:
                result = _execute_idx007_container_phase(
                    phase, major=idx007_major or 17, timeout_seconds=phase_timeout, show_output=show_output
                )

        if emit_phase_timing_protocol:
            result = PhaseResult(result.phase_id, result.outcome, result.code, result.message,
                                 result.duration_seconds, phase_started_ns, time.monotonic_ns())
        phase_results.append(result)
        aggregate = _combine_result(aggregate, (result.outcome, result.code))
        if manifest.demo_id == "QRY-023" and result.code == "FAIL_TIMEOUT":
            suppress_qry023_cleanup = True
        if result.outcome == "FAIL" or (result.outcome == "SKIP" and phase.required):
            stop_regular_phases = True

    if setup_started and manifest.cleanup is not None:
        if suppress_qry023_cleanup:
            cleanup = PhaseResult(
                manifest.cleanup.phase_id, "FAIL", "FAIL_CLEANUP",
                "SQL-Timeout: serverseitiges Ende und TempDB-Freigabe sind nicht bewiesen; SQL-Cleanup wurde unterdrückt.",
                0.0,
            )
        else:
            cleanup_started_ns = time.monotonic_ns() if emit_phase_timing_protocol else None
            cleanup_username, cleanup_environment = _phase_connection(
                manifest.cleanup, username=username, credentials=credentials
            )
            cleanup = _execute_sql_phase(
                phase=manifest.cleanup,
                executable=executable,
                server=server,
                target_database=target_database,
                auth=auth,
                username=cleanup_username,
                environment=cleanup_environment,
                timeout_seconds=manifest.cleanup_timeout_seconds,
                variables=variables,
                show_output=show_output,
            )
            if emit_phase_timing_protocol:
                cleanup = PhaseResult(cleanup.phase_id, cleanup.outcome, cleanup.code,
                                      cleanup.message, cleanup.duration_seconds,
                                      cleanup_started_ns, time.monotonic_ns())
        if cleanup.outcome != "PASS" and cleanup.code != "FAIL_CLEANUP":
            cleanup = PhaseResult(cleanup.phase_id, "FAIL", "FAIL_CLEANUP", f"Cleanup nicht erfolgreich; ursprünglicher Code: {cleanup.code}.", cleanup.duration_seconds)
        phase_results.append(cleanup)
        aggregate = _combine_result(aggregate, (cleanup.outcome, cleanup.code))

    outcome, code = aggregate
    if outcome == "PASS":
        message = "Alle erforderlichen Phasen wurden erfolgreich abgeschlossen."
    elif outcome == "WARN":
        message = "Die Demo wurde abgeschlossen; mindestens eine optionale Evidenz war eingeschränkt."
    elif outcome == "SKIP":
        message = "Eine erforderliche Voraussetzung war nicht erfüllt; zustandsverändernde Folgephasen wurden nicht fortgesetzt."
    else:
        message = "Mindestens eine Phase oder das Cleanup ist fehlgeschlagen."
    return HarnessResult(outcome, code, message, tuple(phase_results))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a FWK-010 demo manifest.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--server", default=os.environ.get("SQLPERF_SQL_SERVER"))
    parser.add_argument("--auth", choices=("integrated", "sql", "aad"), default=os.environ.get("SQLPERF_SQL_AUTH", "integrated"))
    parser.add_argument("--username", default=os.environ.get("SQLPERF_SQL_USERNAME"))
    parser.add_argument("--sqlcmd", dest="sqlcmd_path")
    parser.add_argument("--confirm-isolated-lab", action="store_true")
    parser.add_argument("--allow-red", action="store_true")
    parser.add_argument("--show-output", action="store_true")
    parser.add_argument("--emit-phase-timing-protocol", action="store_true")
    parser.add_argument("--idx007-major", type=int, choices=(15, 16, 17), help="SQL Server major version for the isolated IDX-007 container demo")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    try:
        result = run_demo(
            manifest_path=args.manifest,
            server=args.server,
            auth=args.auth,
            username=args.username,
            sqlcmd_path=args.sqlcmd_path,
            confirm_isolated_lab=args.confirm_isolated_lab,
            allow_red=args.allow_red,
            show_output=args.show_output,
            emit_phase_timing_protocol=args.emit_phase_timing_protocol,
            idx007_major=args.idx007_major,
        )
    except FileNotFoundError as exc:
        print(f"SQLPERF_SUMMARY|SKIP|SKIP_TOOL_MISSING\n{exc}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"SQLPERF_SUMMARY|FAIL|FAIL_CONTRACT\n{exc}", file=sys.stderr)
        return 1

    print(f"SQLPERF_SUMMARY|{result.outcome}|{result.code}")
    print(result.message)
    for phase in result.phases:
        print(f"{phase.phase_id}: {phase.outcome}/{phase.code} ({phase.duration_seconds:.3f}s) - {phase.message}")
    if args.emit_phase_timing_protocol:
        for phase in result.phases:
            if type(phase.started_ns) is int and type(phase.finished_ns) is int:
                print(f"SQLPERF_PHASE_TIME|1|{phase.phase_id}|{phase.started_ns}|{phase.finished_ns}")
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
