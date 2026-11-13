#!/usr/bin/env python3
"""Run FWK-010 sqlcmd calls inside the QRY-023 disposable SQL container."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


VALUE_FLAGS = {"-r", "-s", "-h", "-w", "-S", "-d", "-i", "-U"}
BOOLEAN_FLAGS = {"-b", "-W", "-E", "-G"}


def parse_args(argv: list[str]) -> tuple[str, Path, str, list[str], list[str]]:
    database = "master"
    script: Path | None = None
    username: str | None = None
    variables: list[str] = []
    passthrough: list[str] = []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg in BOOLEAN_FLAGS:
            passthrough.append(arg)
            index += 1
        elif arg in VALUE_FLAGS:
            if index + 1 >= len(argv):
                raise ValueError("invalid sqlcmd arguments")
            value = argv[index + 1]
            if arg == "-d":
                database = value
            elif arg == "-i":
                script = Path(value).resolve()
            elif arg == "-U":
                username = value
            elif arg != "-S":
                passthrough.extend((arg, value))
            index += 2
        elif arg == "-v":
            index += 1
            while index < len(argv) and not argv[index].startswith("-"):
                variables.append(argv[index])
                index += 1
        else:
            raise ValueError("unsupported sqlcmd arguments")

    if script is None or not script.is_file() or script.suffix.lower() != ".sql" or not username:
        raise ValueError("QRY-023 requires a readable SQL script and SQL identity")
    if not database or any(char in database for char in "\r\n\x00"):
        raise ValueError("invalid database")
    return database, script, username, variables, passthrough


def _sqlcmd_path(container: str) -> str:
    result = subprocess.run(
        ["docker", "exec", container, "sh", "-lc",
         "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then printf /opt/mssql-tools18/bin/sqlcmd; "
         "elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then printf /opt/mssql-tools/bin/sqlcmd; "
         "else exit 127; fi"],
        check=False, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode:
        raise FileNotFoundError("sqlcmd is unavailable in the disposable SQL container")
    return result.stdout.strip()


def main() -> int:
    try:
        database, script, username, variables, passthrough = parse_args(sys.argv[1:])
        container = os.environ.get("SQLPERF_SQL_CONTAINER", "")
        password = os.environ.get("SQLCMDPASSWORD")
        if not container or not password:
            raise ValueError("container or phase-scoped SQL credential is unavailable")
        child_env = os.environ.copy()
        child_env["SQLCMDPASSWORD"] = password
        command = ["docker", "exec", "-i", "-e", "SQLCMDPASSWORD", container,
                   _sqlcmd_path(container), "-S", "localhost", "-d", database,
                   "-U", username, "-C", *passthrough]
        if variables:
            command.extend(("-v", *variables))
        result = subprocess.run(
            command, input=script.read_text(encoding="utf-8"), check=False,
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=child_env,
        )
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        return result.returncode
    except (FileNotFoundError, OSError, ValueError):
        print("qry023-docker-sqlcmd-proxy: container SQL execution failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
