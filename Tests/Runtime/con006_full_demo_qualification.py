"""Run the complete CON-006 demo in one owned, digest-pinned SQL container."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import string
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILES = {
    15: ("15.0.4500.2", "sha256:07d7dedecdbfcf6776035dc5eefb5bfd9aa1804b2f6b99f7dedb397d8a599069"),
    16: ("16.0.4305.5", "sha256:cf8f0ab2ebe61feec2eed2629061a07d247f791c2a8ddda74a4ac9f06a291718"),
    17: ("17.0.5035.5", "sha256:6972fb831759433def6a34e107fa32a85230bff5af8014c6263fe4633ea9cc0f"),
}
OWNER_LABEL = "sqlperf.ci.owner"
SUBJECT_LABEL = "sqlperf.ci.subject"
SUBJECT = "CON006-FULL-DEMO"


class QualificationError(RuntimeError):
    pass


def _run(args: list[str], *, env: dict[str, str], timeout: float = 30,
         capture: bool = True, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args, env=env, timeout=timeout, check=False, capture_output=capture,
        text=True, encoding="utf-8", errors="replace",
    )
    if check and result.returncode:
        raise QualificationError(f"{Path(args[0]).name} failed ({result.returncode})")
    return result


def _inspect_owned(name: str, owner: str, image: str, env: dict[str, str]) -> dict[str, Any]:
    result = _run(["docker", "inspect", name], env=env)
    rows = json.loads(result.stdout)
    if len(rows) != 1:
        raise QualificationError("owned container identity is ambiguous")
    row = rows[0]
    host = row.get("HostConfig", {})
    labels = row.get("Config", {}).get("Labels") or {}
    if (labels.get(OWNER_LABEL) != owner or labels.get(SUBJECT_LABEL) != SUBJECT
            or row.get("Config", {}).get("Image") != image
            or host.get("NetworkMode") != "none"
            or host.get("NanoCpus") != 2_000_000_000
            or host.get("Memory") != 4 * 1024**3
            or host.get("MemorySwap") != 4 * 1024**3
            or host.get("PortBindings") not in (None, {})
            or row.get("Mounts")):
        raise QualificationError("container ownership or isolation limits differ")
    return row


def qualify(major: int) -> int:
    expected_build, digest = PROFILES[major]
    image = f"mcr.microsoft.com/mssql/server@{digest}"
    owner = secrets.token_hex(16)
    suffix = secrets.randbelow(900000) + 100000
    name = f"sqlperf-con006-full-{suffix}"
    secret = "Aa7!" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    env = os.environ.copy()
    env.update(SQLCMDPASSWORD=secret, MSSQL_SA_PASSWORD=secret,
               SQLPERF_SQL_CONTAINER=name, SQLPERF_CI_OWNER=owner)
    created = False
    demo_exit = 1
    try:
        if _run(["docker", "inspect", name], env=env, check=False).returncode == 0:
            raise QualificationError("random owned container name is already in use")
        image_rows = json.loads(_run(["docker", "image", "inspect", image], env=env).stdout)
        if (len(image_rows) != 1 or image not in (image_rows[0].get("RepoDigests") or [])
                or image_rows[0].get("Os") != "linux" or image_rows[0].get("Architecture") != "amd64"):
            raise QualificationError("pinned Linux/AMD64 image identity does not match")

        _run([
            "docker", "run", "--pull=never", "--name", name,
            "--label", f"{OWNER_LABEL}={owner}", "--label", f"{SUBJECT_LABEL}={SUBJECT}",
            "--network", "none", "--cpus=2", "--memory=4g", "--memory-swap=4g",
            "--restart=no", "-e", "ACCEPT_EULA=Y", "-e", "MSSQL_PID=Developer",
            "--env", "MSSQL_SA_PASSWORD", "-d", image,
        ], env=env)
        created = True
        row = _inspect_owned(name, owner, image, env)
        container_env = dict(item.split("=", 1) for item in row["Config"].get("Env", []) if "=" in item)
        received = container_env.get("MSSQL_SA_PASSWORD", "")
        if not secrets.compare_digest(hashlib.sha256(received.encode()).digest(),
                                      hashlib.sha256(secret.encode()).digest()):
            raise QualificationError("password environment did not reach the owned container")

        ready = False
        for _ in range(90):
            logs = _run(["docker", "logs", name], env=env, check=False)
            if "SQL Server is now ready for client connections" in (logs.stdout or "") + (logs.stderr or ""):
                ready = True
                break
            state = _run(["docker", "inspect", "-f", "{{.State.Running}}", name], env=env)
            if state.stdout.strip() != "true":
                raise QualificationError("SQL Server exited before readiness")
            time.sleep(2)
        if not ready:
            raise QualificationError("SQL Server did not become ready within 180 seconds")

        sqlcmd_probe = (
            "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then s=/opt/mssql-tools18/bin/sqlcmd; "
            "elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then s=/opt/mssql-tools/bin/sqlcmd; "
            "else exit 127; fi; \"$s\" -S 127.0.0.1 -U sa -C -b "
            "-Q \"SET NOCOUNT ON; SELECT 1;\"")
        login = None
        for _ in range(30):
            login = _run(["docker", "exec", "-e", "SQLCMDPASSWORD", name,
                          "sh", "-lc", sqlcmd_probe], env=env, check=False)
            if login.returncode == 0:
                break
            time.sleep(2)
        if login is None or login.returncode:
            raise QualificationError("SQL authentication readiness failed")
        engine_query = (
            "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then s=/opt/mssql-tools18/bin/sqlcmd; "
            "else s=/opt/mssql-tools/bin/sqlcmd; fi; \"$s\" -S 127.0.0.1 -U sa -C -b "
            "-Q \"SET NOCOUNT ON; SELECT CONCAT('ENGINE|',CONVERT(varchar(10),SERVERPROPERTY('ProductMajorVersion'))," 
            "'|',CONVERT(varchar(50),SERVERPROPERTY('ProductVersion')));\"")
        engine = _run(["docker", "exec", "-e", "SQLCMDPASSWORD", name,
                       "sh", "-lc", engine_query], env=env)
        engine_line = next((line.strip() for line in engine.stdout.splitlines()
                            if line.strip().startswith("ENGINE|")), "")
        if engine_line != f"ENGINE|{major}|{expected_build}":
            raise QualificationError("SQL Server build differs from the pinned qualification profile")

        runner = ROOT / "Demos/00_Framework/Tools/run_demo.py"
        manifest = ROOT / "Demos/07_Concurrency/CON-006_Deadlock_Cycle/manifest.json"
        proxy = ROOT / "Tests/Runtime/con006_docker_sqlcmd_proxy.py"
        result = subprocess.run([
            sys.executable, str(runner), str(manifest), "--server", "127.0.0.1",
            "--auth", "sql", "--username", "sa", "--sqlcmd", str(proxy),
            "--confirm-isolated-lab", "--show-output",
        ], cwd=ROOT, env=env, timeout=245, check=False)
        demo_exit = result.returncode

        absence_query = (
            "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then s=/opt/mssql-tools18/bin/sqlcmd; "
            "else s=/opt/mssql-tools/bin/sqlcmd; fi; \"$s\" -S 127.0.0.1 -U sa -C -b -h -1 -W "
            "-Q \"SET NOCOUNT ON; SELECT COALESCE(CONVERT(varchar(11),DB_ID(N'SQLPERF_LAB_CON006_LOCAL')), 'NULL');\"")
        absence = _run(["docker", "exec", "-e", "SQLCMDPASSWORD", name,
                        "sh", "-lc", absence_query], env=env, check=False)
        if absence.returncode or absence.stdout.strip() != "NULL":
            raise QualificationError("marker-bound demo database was not verified absent")
        print(f"INTEGRATED_DEMO|version={major}|build={expected_build}|exit={demo_exit}")
    finally:
        if created:
            _inspect_owned(name, owner, image, env)
            _run(["docker", "rm", "--force", name], env=env)
            remaining = _run(["docker", "ps", "-a", "--filter", f"name=^/{name}$",
                              "--format", "{{.ID}}"], env=env)
            if remaining.stdout.strip():
                raise QualificationError("owned SQL Server container remains after cleanup")
            print("OWNED_CONTAINER_REMOVAL=PASS")
    return demo_exit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product-major-version", type=int, choices=sorted(PROFILES), required=True)
    args = parser.parse_args()
    try:
        return qualify(args.product_major_version)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, QualificationError) as exc:
        print(f"con006-full-demo: FAIL ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
