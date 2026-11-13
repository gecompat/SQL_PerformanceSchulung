#!/usr/bin/env python3
"""Run FWK-010 sqlcmd calls inside the QRY-023 disposable SQL container."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys


VALUE_FLAGS = {"-r", "-s", "-h", "-w", "-S", "-d", "-i", "-U"}
BOOLEAN_FLAGS = {"-b", "-W", "-E", "-G"}
INCLUDE_PATTERN = re.compile(r"(?m)^[ \t]*:r[ \t]+(?:\"([^\"\r\n]+)\"|'([^'\r\n]+)'|([^\s\r\n]+))[ \t]*$")


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


def expand_sqlcmd_includes(script: Path, repository_root: Path) -> str:
    """Inline repository-local :r includes because the SQL container has no checkout."""
    root = repository_root.resolve(strict=True)
    active: set[Path] = set()

    def expand(path: Path, depth: int) -> str:
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(root) or resolved.suffix.lower() != ".sql":
            raise ValueError("sqlcmd include is outside the repository SQL boundary")
        if resolved in active or depth > 8:
            raise ValueError("sqlcmd include cycle or depth limit")
        active.add(resolved)
        try:
            source = resolved.read_text(encoding="utf-8")

            def replace(match: re.Match[str]) -> str:
                relative = next(group for group in match.groups() if group is not None)
                include = (root / relative).resolve(strict=True)
                return expand(include, depth + 1)

            return INCLUDE_PATTERN.sub(replace, source)
        finally:
            active.remove(resolved)

    return expand(script, 0)


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
        sql_text = expand_sqlcmd_includes(script, Path.cwd())
        result = subprocess.run(
            command, input=sql_text, check=False,
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
