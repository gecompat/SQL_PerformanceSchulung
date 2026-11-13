#!/usr/bin/env python3
"""Create only the QRY-023 READER SQL login on its fresh disposable instance."""

from __future__ import annotations

import os
import re
import subprocess
import sys


PASSWORD_PATTERN = re.compile(r"[A-Za-z0-9!._-]{24,128}\Z")


def build_sql(password: str) -> str:
    if not isinstance(password, str) or PASSWORD_PATTERN.fullmatch(password) is None:
        raise ValueError("READER password must use the bounded safe character set")
    return (
        "SET NOCOUNT ON;\n"
        "IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'READER')\n"
        "    THROW 51023, 'READER login unexpectedly exists on the fresh instance.', 1;\n"
        f"DECLARE @password nvarchar(128) = N'{password}';\n"
        "DECLARE @statement nvarchar(max) = N'CREATE LOGIN [READER] WITH PASSWORD = '\n"
        "    + QUOTENAME(@password, '''')\n"
        "    + N', CHECK_POLICY = ON, CHECK_EXPIRATION = OFF;';\n"
        "EXEC sys.sp_executesql @statement;\n"
        "IF NOT EXISTS (SELECT 1 FROM sys.server_principals\n"
        "               WHERE name = N'READER' AND type_desc = N'SQL_LOGIN' AND is_disabled = 0)\n"
        "    THROW 51023, 'READER login was not created as an active SQL login.', 1;\n"
        "SELECT N'QRY023_READER_LOGIN|PASS' AS result;\n"
    )


def sqlcmd_path(container: str) -> str:
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
        container = os.environ.get("SQLPERF_SQL_CONTAINER", "")
        password = os.environ.get("SQLPERF_SQL_PASSWORD_READER", "")
        admin_password = os.environ.get("SQLCMDPASSWORD", "")
        if not container or not admin_password:
            raise ValueError("disposable container and ADMIN credential are required")
        sql = build_sql(password)
        command = ["docker", "exec", "-i", "-e", "SQLCMDPASSWORD", container,
                   sqlcmd_path(container), "-S", "localhost", "-d", "master",
                   "-U", "sa", "-C", "-b", "-r", "1"]
        result = subprocess.run(
            command, input=sql, check=False, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=os.environ.copy(),
        )
        if result.returncode or "QRY023_READER_LOGIN|PASS" not in result.stdout:
            print("qry023-reader-provision: READER SQL login provisioning failed", file=sys.stderr)
            return 1
        print("QRY023_READER_LOGIN|PASS")
        return 0
    except (FileNotFoundError, OSError, ValueError):
        print("qry023-reader-provision: disposable instance or credential invalid", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
