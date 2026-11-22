"""Bounded read-only DGN-007 XE catalog inventory on pinned SQL Server images."""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import string
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
IMAGE_LOCK = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/container-images.proposed.json"
SQL_PATH = Path(__file__).with_suffix(".sql")
OWNER_LABEL = "com.sqlperf.owner"
PROJECT_LABEL = "com.sqlperf.project"
SUBJECT_LABEL = "com.sqlperf.subject"
RUN_LABEL = "com.sqlperf.run-token"
MAX_SQL_OUTPUT_BYTES = 256 * 1024
STARTUP_SECONDS = 180
QUERY_SECONDS = 30
CLEANUP_SECONDS = 60
REQUIRED_EVENTS = {"sql_statement_starting", "sql_statement_completed"}
ACTION_NAMES = {
    "database_id",
    "event_sequence",
    "query_hash",
    "query_plan_hash",
    "session_id",
    "sql_text",
    "tsql_stack",
}
_FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*:(?:data|readonly|customizable)\Z")


class ProbeError(RuntimeError):
    """The bounded metadata inventory could not be completed safely."""


def _run(command: list[str], *, env: dict[str, str] | None = None,
         timeout: float = 30, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command, text=True, capture_output=True, env=env, timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProbeError(f"command failed within its bound: {command[0]}") from exc
    if check and result.returncode:
        raise ProbeError(f"command failed ({result.returncode}): {command[0]}")
    return result


def load_profile(product_major_version: int) -> dict[str, Any]:
    if type(product_major_version) is not int or product_major_version not in {15, 16, 17}:
        raise ProbeError("product major version is outside the reviewed image matrix")
    try:
        lock = json.loads(IMAGE_LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProbeError("pinned SQL Server image lock is unavailable") from exc
    if lock.get("contract_version") != "1.0" or lock.get("status") != "PROPOSED":
        raise ProbeError("pinned image lock contract or status changed")
    if lock.get("runtime_authorized") is not False:
        raise ProbeError("shared QRY-023 runtime status changed unexpectedly")
    matches = [profile for profile in lock.get("profiles", [])
               if profile.get("product_major_version") == product_major_version]
    if len(matches) != 1:
        raise ProbeError("exactly one pinned image profile is required")
    profile = matches[0]
    digest = profile.get("manifest_digest")
    config_digest = profile.get("config_digest")
    if (not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
            or not isinstance(config_digest, str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", config_digest)
            or profile.get("image") != f"mcr.microsoft.com/mssql/server@{digest}"
            or profile.get("platform") != "linux/amd64"
            or type(profile.get("compatibility_level")) is not int
            or not isinstance(profile.get("product_version_label"), str)):
        raise ProbeError("pinned image profile is incomplete or malformed")
    return profile


def validate_image_identity(items: list[dict[str, Any]], image: str,
                            profile: dict[str, Any]) -> bool:
    """Accept Docker's config-ID or manifest-ID display, always binding the manifest ref."""
    if len(items) != 1:
        return False
    item = items[0]
    expected_ids = {profile["config_digest"], profile["manifest_digest"]}
    return (
        item.get("Id") in expected_ids
        and image in (item.get("RepoDigests") or [])
        and item.get("Os") == "linux"
        and item.get("Architecture") == "amd64"
    )


def parse_catalog_output(output: str, *, expected_major: int,
                         expected_version: str) -> dict[str, Any]:
    if type(output) is not str or len(output.encode("utf-8")) > MAX_SQL_OUTPUT_BYTES:
        raise ProbeError("catalog output is not a bounded text value")
    records = [line.strip() for line in output.splitlines()
               if line.strip().startswith("DGN007_XE|")]
    if records.count("DGN007_XE|END|1") != 1 or not records or records[-1] != "DGN007_XE|END|1":
        raise ProbeError("catalog output is incomplete or has an invalid completion marker")
    engine_rows = [row.split("|", 4) for row in records
                   if row.startswith("DGN007_XE|ENGINE|")]
    if len(engine_rows) != 1 or len(engine_rows[0]) != 5:
        raise ProbeError("exactly one engine identity row is required")
    _, _, major, version, edition = engine_rows[0]
    if not major.isdecimal() or int(major) != expected_major or version != expected_version:
        raise ProbeError("SERVERPROPERTY build differs from the pinned image")
    events: dict[str, tuple[str, ...]] = {}
    actions: set[tuple[str, str]] = set()
    for record in records:
        parts = record.split("|", 3)
        if record == "DGN007_XE|END|1":
            continue
        if len(parts) == 4 and parts[1] == "EVENT":
            event_name = parts[2]
            fields = tuple(field for field in parts[3].split(",") if field)
            if (not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", event_name)
                    or any(_FIELD_RE.fullmatch(field) is None for field in fields)
                    or event_name in events):
                raise ProbeError("event metadata row is malformed or duplicated")
            events[event_name] = fields
        elif len(parts) == 4 and parts[1] == "ACTION":
            package, action = parts[2], parts[3]
            if (not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", package)
                    or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", action)
                    or action not in ACTION_NAMES):
                raise ProbeError("action metadata row is outside the fixed inventory")
            actions.add((package, action))
        elif parts[1] != "ENGINE":
            raise ProbeError("catalog output contains an unknown or malformed record")
    missing = REQUIRED_EVENTS - events.keys()
    if missing:
        raise ProbeError("required XE event metadata is absent")
    return {
        "scope": "metadata-only; no XE session or workload executed",
        "product_major_version": expected_major,
        "product_version": version,
        "edition": edition,
        "events": {name: list(events[name]) for name in sorted(events)},
        "available_actions": [
            {"package": package, "name": action}
            for package, action in sorted(actions)
        ],
    }


def _password() -> str:
    groups = (
        "ABCDEFGHJKLMNPQRSTUVWXYZ",
        "abcdefghijkmnopqrstuvwxyz",
        "23456789",
    )
    chars = [secrets.choice(group) for group in groups] + ["!"]
    chars.extend(secrets.choice("".join(groups)) for _ in range(28))
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def _identity(container_id: str) -> dict[str, Any]:
    result = _run(["docker", "inspect", container_id], timeout=15)
    try:
        items = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError("Docker returned malformed container identity") from exc
    if len(items) != 1:
        raise ProbeError("Docker did not return exactly one container")
    return items[0]


def _cleanup(container_name: str, network_name: str, owner: str,
             container_id: str | None, network_id: str, deadline: float) -> None:
    if container_id is None:
        found = _run(["docker", "container", "ls", "-aq", "--filter",
                      f"name=^/{container_name}$", "--filter",
                      f"label={OWNER_LABEL}={owner}"], timeout=10, check=False)
        if found.returncode:
            raise ProbeError("cannot determine the result of an uncertain container start")
        ids = [item for item in found.stdout.splitlines() if item.strip()]
        if len(ids) > 1:
            raise ProbeError("uncertain start found multiple owner-matched containers")
        container_id = ids[0] if ids else None
    if container_id is not None:
        identity = _identity(container_id)
        labels = identity.get("Config", {}).get("Labels") or {}
        if (identity.get("Id") != container_id or identity.get("Name") != f"/{container_name}"
                or labels.get(OWNER_LABEL) != owner
                or labels.get(SUBJECT_LABEL) != "DGN-007-XE-METADATA"):
            raise ProbeError("container ownership changed; refusing cleanup")
        if identity.get("State", {}).get("Running"):
            remaining = max(1.0, min(15.0, deadline - time.monotonic()))
            _run(["docker", "stop", "--time", "10", container_id], timeout=remaining)
        after = _identity(container_id)
        labels = after.get("Config", {}).get("Labels") or {}
        if after.get("Id") != container_id or labels.get(OWNER_LABEL) != owner:
            raise ProbeError("container ownership changed before removal")
        _run(["docker", "rm", container_id], timeout=max(1.0, min(15.0, deadline-time.monotonic())))
    remains = _run(["docker", "container", "ls", "-aq", "--filter",
                    f"name=^/{container_name}$"], timeout=10).stdout.strip()
    if remains:
        raise ProbeError("owned container absence was not confirmed")

    result = _run(["docker", "network", "inspect", network_name], timeout=10)
    try:
        networks = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError("Docker returned malformed network identity") from exc
    if len(networks) != 1:
        raise ProbeError("owned internal network is missing or ambiguous")
    network = networks[0]
    if (network.get("Id") != network_id or network.get("Internal") is not True
            or (network.get("Labels") or {}).get(OWNER_LABEL) != owner):
        raise ProbeError("network ownership changed; refusing cleanup")
    if network.get("Containers"):
        raise ProbeError("owned network still has attached containers")
    _run(["docker", "network", "rm", network_name], timeout=15)


def run_probe(product_major_version: int) -> dict[str, Any]:
    profile = load_profile(product_major_version)
    executable = shutil.which("docker")
    if not executable:
        raise ProbeError("Docker CLI is unavailable")
    info = _run([executable, "info", "--format", "{{.OSType}}|{{.Architecture}}"], timeout=15).stdout.strip()
    if info != "linux|x86_64":
        raise ProbeError("probe requires a Linux/AMD64 Docker target")
    image = profile["image"]
    _run([executable, "pull", image], timeout=240)
    image_result = _run([executable, "image", "inspect", image], timeout=15)
    try:
        image_items = json.loads(image_result.stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError("Docker returned malformed pinned-image identity") from exc
    if not validate_image_identity(image_items, image, profile):
        raise ProbeError("pulled image manifest/config digest differs from the reviewed lock")

    owner = uuid.uuid4().hex
    run_token = secrets.token_hex(8).upper()
    container_name = f"sqlperf_dgn007_xe_meta_{product_major_version}_{run_token.lower()}"
    network_name = f"sqlperf_dgn007_xe_meta_net_{run_token.lower()}"
    password = _password()
    environment = os.environ.copy()
    environment["MSSQL_SA_PASSWORD"] = password
    environment["SQLCMDPASSWORD"] = password
    network_id: str | None = None
    container_id: str | None = None
    try:
        network_create = _run([
            executable, "network", "create", "--driver", "bridge", "--internal",
            "--label", f"{PROJECT_LABEL}=SQL_PerformanceSchulung",
            "--label", f"{SUBJECT_LABEL}=DGN-007-XE-METADATA",
            "--label", f"{OWNER_LABEL}={owner}", network_name,
        ], timeout=20)
        candidate_network_id = network_create.stdout.strip()
        if not re.fullmatch(r"[0-9a-f]{64}", candidate_network_id):
            raise ProbeError("Docker returned an incomplete internal network identity")
        network_id = candidate_network_id
        network_items = json.loads(_run([executable, "network", "inspect", network_name], timeout=10).stdout)
        if (len(network_items) != 1 or network_items[0].get("Id") != network_id
                or network_items[0].get("Internal") is not True
                or (network_items[0].get("Labels") or {}).get(OWNER_LABEL) != owner):
            raise ProbeError("internal network boundary differs from the owned probe")
        candidate_container_id = _run([
            executable, "run", "--pull=never", "--detach", "--name", container_name,
            "--hostname", container_name,
            "--label", f"{PROJECT_LABEL}=SQL_PerformanceSchulung",
            "--label", f"{SUBJECT_LABEL}=DGN-007-XE-METADATA",
            "--label", f"{OWNER_LABEL}={owner}",
            "--label", f"{RUN_LABEL}={run_token}",
            "--cpus=2", "--memory=4g", "--memory-swap=4g", "--restart=no",
            "--network", network_name,
            "--env", "ACCEPT_EULA=Y", "--env", "MSSQL_PID=Developer",
            "--env", "MSSQL_SA_PASSWORD", image,
        ], env=environment, timeout=60).stdout.strip()
        if not re.fullmatch(r"[0-9a-f]{64}", candidate_container_id):
            raise ProbeError("Docker returned an incomplete container identity")
        container_id = candidate_container_id
        identity = _identity(container_id)
        host = identity.get("HostConfig", {})
        labels = identity.get("Config", {}).get("Labels") or {}
        if (identity.get("Name") != f"/{container_name}"
                or identity.get("Config", {}).get("Image") != image
                or labels.get(OWNER_LABEL) != owner
                or labels.get(SUBJECT_LABEL) != "DGN-007-XE-METADATA"
                or host.get("NetworkMode") != network_name
                or host.get("NanoCpus") != 2_000_000_000
                or host.get("Memory") != 4 * 1024**3
                or host.get("MemorySwap") != 4 * 1024**3
                or host.get("PortBindings") not in (None, {})
                or identity.get("Mounts")):
            raise ProbeError("container boundary differs from the owned metadata probe")

        sqlcmd_probe = (
            'if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then '
            'sqlcmd=/opt/mssql-tools18/bin/sqlcmd; '
            'elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then '
            'sqlcmd=/opt/mssql-tools/bin/sqlcmd; else exit 127; fi; '
            '"$sqlcmd" -S localhost -U sa -C -b -l 5 -h -1 -W -w 8000 -Q "SELECT 1;"'
        )
        ready = False
        last_readiness = {"returncode": None, "stdout": "", "stderr": ""}
        deadline = time.monotonic() + STARTUP_SECONDS
        while time.monotonic() < deadline:
            check = _run([
                executable, "exec", "--env", "SQLCMDPASSWORD", container_id,
                "sh", "-lc", sqlcmd_probe,
            ], env=environment, timeout=12, check=False)
            last_readiness = {
                "returncode": check.returncode,
                "stdout": check.stdout[-500:],
                "stderr": check.stderr[-500:],
            }
            if check.returncode == 0 and check.stdout.strip() == "1":
                ready = True
                break
            current = _identity(container_id)
            if not current.get("State", {}).get("Running"):
                logs = _run([executable, "logs", "--tail", "80", container_id], timeout=15, check=False)
                diagnostic = (logs.stdout + logs.stderr).replace(password, "[REDACTED]")[-8_000:]
                raise ProbeError(
                    f"SQL Server exited before readiness (exit={current.get('State', {}).get('ExitCode')}); "
                    f"bounded startup diagnostics: {diagnostic}"
                )
            time.sleep(3)
        if not ready:
            logs = _run([executable, "logs", "--tail", "60", container_id], timeout=15, check=False)
            diagnostic = (logs.stdout + logs.stderr).replace(password, "[REDACTED]")[-6_000:]
            raise ProbeError(
                f"SQL Server readiness exceeded {STARTUP_SECONDS}s; "
                f"last SQLCMD check={last_readiness}; bounded startup diagnostics={diagnostic}"
            )

        sql = SQL_PATH.read_text(encoding="utf-8")
        result = subprocess.run([
            executable, "exec", "--interactive", "--env", "SQLCMDPASSWORD", container_id,
            "sh", "-lc",
            'if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then sqlcmd=/opt/mssql-tools18/bin/sqlcmd; '
            'elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then sqlcmd=/opt/mssql-tools/bin/sqlcmd; '
            'else exit 127; fi; "$sqlcmd" -S localhost -U sa -C -b -l 20 -h -1 -W -w 8000',
        ], input=sql, text=True, capture_output=True, env=environment, timeout=QUERY_SECONDS)
        if result.returncode:
            output = (result.stdout + result.stderr).replace(password, "[REDACTED]")[:4_000]
            raise ProbeError(f"read-only catalog query failed ({result.returncode}): {output}")
        inventory = parse_catalog_output(
            result.stdout, expected_major=product_major_version,
            expected_version=profile["product_version_label"],
        )
        inventory.update({
            "image": image,
            "manifest_digest": profile["manifest_digest"],
            "image_config_digest": profile["config_digest"],
            "compatibility_level": profile["compatibility_level"],
        })
        return inventory
    finally:
        if network_id is None:
            found_networks = _run([
                executable, "network", "ls", "-q", "--filter", f"name=^{network_name}$",
                "--filter", f"label={OWNER_LABEL}={owner}",
            ], timeout=10, check=False)
            if found_networks.returncode:
                raise ProbeError("cannot determine the result of an uncertain network create")
            network_ids = [value.strip() for value in found_networks.stdout.splitlines() if value.strip()]
            if len(network_ids) > 1:
                raise ProbeError("uncertain network create found multiple owner-matched networks")
            if network_ids:
                network_id = network_ids[0]
        if network_id is not None:
            _cleanup(
                container_name, network_name, owner, container_id, network_id,
                time.monotonic() + CLEANUP_SECONDS,
            )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product-major-version", type=int, choices=(15, 16, 17), required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        print(json.dumps(run_probe(args.product_major_version), ensure_ascii=False, sort_keys=True))
    except ProbeError as exc:
        print(json.dumps({"scope": "DGN-007 XE metadata-only probe", "outcome": "NOT_PROVEN",
                          "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
