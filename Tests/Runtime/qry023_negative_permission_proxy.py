#!/usr/bin/env python3
"""Inject a controlled unexpected READER permission before ADMIN inventory."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qry023_docker_sqlcmd_proxy as proxy


TARGET_DATABASE_PATTERN = re.compile(r"SQLPERF_LAB_QRY023_[A-Z0-9_]{1,20}\Z")
INVENTORY_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/22_Admin_Permission_Inventory.sql"
)


def injection_target(argv: list[str]) -> str | None:
    database, script, username, raw_variables, _ = proxy.parse_args(argv)
    variables: dict[str, str] = {}
    for item in raw_variables:
        name, separator, value = item.partition("=")
        if not separator or name in variables:
            raise ValueError("invalid SQLCMD variable set")
        variables[name] = value
    if script != INVENTORY_SCRIPT:
        return None
    if username != "sa" or database != variables.get("TargetDatabase"):
        raise ValueError("unexpected QRY-023 ADMIN inventory invocation")
    if variables.get("ReaderLogin") != "READER" or not TARGET_DATABASE_PATTERN.fullmatch(database):
        raise ValueError("unexpected QRY-023 negative-test target")
    return database


def injection_for_mode(mode: str) -> tuple[str, str]:
    if mode == "EXTRA_GRANT_AND_ROLE":
        return (
            "GRANT SELECT ON OBJECT::lab.MeasurementWaitSnapshot TO [READER];\n"
            "ALTER ROLE [db_datareader] ADD MEMBER [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|EXTRA_GRANT_AND_ROLE_INJECTED",
        )
    if mode == "DIRECT_DENY":
        return (
            "DENY SELECT ON OBJECT::dbo.Person TO [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|DIRECT_DENY_INJECTED",
        )
    if mode == "SERVER_ROLE":
        return (
            "ALTER SERVER ROLE [dbcreator] ADD MEMBER [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|SERVER_ROLE_INJECTED",
        )
    if mode == "MISSING_OBJECT":
        return (
            "DROP TABLE lab.MeasurementWaitSnapshot;\n",
            "QRY023_NEGATIVE_PERMISSION|EXPECTED_OBJECT_REMOVED",
        )
    if mode == "SERVER_PERMISSION":
        return (
            "GRANT VIEW SERVER STATE TO [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|SERVER_PERMISSION_INJECTED",
        )
    raise ValueError("unsupported QRY-023 negative permission mode")


def main() -> int:
    try:
        target = injection_target(sys.argv[1:])
        if target is not None:
            sql, marker = injection_for_mode(
                os.environ.get("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE", "EXTRA_GRANT_AND_ROLE")
            )
            container = os.environ.get("SQLPERF_SQL_CONTAINER", "")
            password = os.environ.get("SQLCMDPASSWORD", "")
            if not container or not password:
                raise ValueError("isolated container or ADMIN credential is unavailable")
            command = [
                "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", container,
                proxy._sqlcmd_path(container), "-S", "localhost", "-d", target,
                "-U", "sa", "-C", "-b", "-r", "1",
            ]
            injected = subprocess.run(
                command, input=sql,
                check=False, capture_output=True, text=True, encoding="utf-8",
                errors="replace", env=os.environ.copy(),
            )
            if injected.returncode:
                details = "\n".join(
                    part.strip()[:2000]
                    for part in (injected.stdout, injected.stderr)
                    if part and part.strip()
                )
                raise RuntimeError(
                    "unexpected READER permission could not be injected"
                    + (f":\n{details}" if details else " (sqlcmd returned no diagnostic output)")
                )
            print(marker)
        sys.argv[0] = str(Path(proxy.__file__).resolve())
        return proxy.main()
    except (FileNotFoundError, OSError, ValueError, RuntimeError) as exc:
        print(f"qry023-negative-permission-proxy: controlled negative case failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
