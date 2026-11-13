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
PREFLIGHT_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/00_Preflight.sql"
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


def corrupt_preflight_run_token_trailing_space(argv: list[str]) -> list[str]:
    database, script, username, raw_variables, _ = proxy.parse_args(argv)
    values: dict[str, str] = {}
    for item in raw_variables:
        name, separator, value = item.partition("=")
        if not separator or name in values:
            raise ValueError("invalid SQLCMD variable set")
        values[name] = value
    token = values.get("RunToken", "")
    if script != PREFLIGHT_SCRIPT or database != "master" or username != "sa":
        raise ValueError("invalid RunToken negative control must target the ADMIN master preflight")
    if values.get("DemoId") != "QRY-023" or not re.fullmatch(r"[A-Z0-9_]{1,20}", token):
        raise ValueError("invalid RunToken negative control requires a valid runner-provided token")
    if values.get("TargetDatabase") != f"SQLPERF_LAB_QRY023_{token}":
        raise ValueError("invalid RunToken negative control target is not bound to the original token")

    rewritten = list(argv)
    token_values = 0
    index = 0
    while index < len(rewritten):
        if rewritten[index] != "-v":
            index += 1
            continue
        index += 1
        while index < len(rewritten) and not rewritten[index].startswith("-"):
            if rewritten[index].startswith("RunToken="):
                rewritten[index] += " "
                token_values += 1
            index += 1
    if token_values != 1:
        raise ValueError("invalid RunToken negative control could not bind exactly one SQLCMD value")
    return rewritten


def corrupt_preflight_target_database_trailing_space(argv: list[str]) -> list[str]:
    database, script, username, raw_variables, _ = proxy.parse_args(argv)
    values: dict[str, str] = {}
    for item in raw_variables:
        name, separator, value = item.partition("=")
        if not separator or name in values:
            raise ValueError("invalid SQLCMD variable set")
        values[name] = value
    token = values.get("RunToken", "")
    expected_target = f"SQLPERF_LAB_QRY023_{token}"
    if script != PREFLIGHT_SCRIPT or database != "master" or username != "sa":
        raise ValueError("invalid target-name negative control must target the ADMIN master preflight")
    if values.get("DemoId") != "QRY-023" or not re.fullmatch(r"[A-Z0-9_]{1,20}", token):
        raise ValueError("invalid target-name negative control requires a valid runner-provided identity")
    if values.get("TargetDatabase") != expected_target:
        raise ValueError("invalid target-name negative control is not bound to the original RunToken")

    rewritten = list(argv)
    target_values = 0
    index = 0
    while index < len(rewritten):
        if rewritten[index] != "-v":
            index += 1
            continue
        index += 1
        while index < len(rewritten) and not rewritten[index].startswith("-"):
            if rewritten[index].startswith("TargetDatabase="):
                rewritten[index] += " "
                target_values += 1
            index += 1
    if target_values != 1:
        raise ValueError("invalid target-name negative control could not bind exactly one SQLCMD value")
    return rewritten


def corrupt_preflight_demo_id_trailing_space(argv: list[str]) -> list[str]:
    database, script, username, raw_variables, _ = proxy.parse_args(argv)
    values: dict[str, str] = {}
    for item in raw_variables:
        name, separator, value = item.partition("=")
        if not separator or name in values:
            raise ValueError("invalid SQLCMD variable set")
        values[name] = value
    token = values.get("RunToken", "")
    if script != PREFLIGHT_SCRIPT or database != "master" or username != "sa":
        raise ValueError("invalid DemoId negative control must target the ADMIN master preflight")
    if values.get("DemoId") != "QRY-023" or not re.fullmatch(r"[A-Z0-9_]{1,20}", token):
        raise ValueError("invalid DemoId negative control requires the runner-provided identity")
    if values.get("TargetDatabase") != f"SQLPERF_LAB_QRY023_{token}":
        raise ValueError("invalid DemoId negative control target is not bound to the original RunToken")

    rewritten = list(argv)
    demo_id_values = 0
    index = 0
    while index < len(rewritten):
        if rewritten[index] != "-v":
            index += 1
            continue
        index += 1
        while index < len(rewritten) and not rewritten[index].startswith("-"):
            if rewritten[index].startswith("DemoId="):
                rewritten[index] += " "
                demo_id_values += 1
            index += 1
    if demo_id_values != 1:
        raise ValueError("invalid DemoId negative control could not bind exactly one SQLCMD value")
    return rewritten


def corrupt_preflight_demo_id_case_variant(argv: list[str]) -> list[str]:
    database, script, username, raw_variables, _ = proxy.parse_args(argv)
    values: dict[str, str] = {}
    for item in raw_variables:
        name, separator, value = item.partition("=")
        if not separator or name in values:
            raise ValueError("invalid SQLCMD variable set")
        values[name] = value
    token = values.get("RunToken", "")
    if script != PREFLIGHT_SCRIPT or database != "master" or username != "sa":
        raise ValueError("invalid DemoId case negative control must target the ADMIN master preflight")
    if values.get("DemoId") != "QRY-023" or not re.fullmatch(r"[A-Z0-9_]{1,20}", token):
        raise ValueError("invalid DemoId case negative control requires the runner-provided identity")
    if values.get("TargetDatabase") != f"SQLPERF_LAB_QRY023_{token}":
        raise ValueError("invalid DemoId case negative control target is not bound to the original RunToken")

    replacements = {
        "DemoId=QRY-023": "DemoId=qry-023",
        f"TargetDatabase=SQLPERF_LAB_QRY023_{token}": f"TargetDatabase=SQLPERF_LAB_qry023_{token}",
    }
    rewritten = list(argv)
    seen = {name: 0 for name in replacements}
    index = 0
    while index < len(rewritten):
        if rewritten[index] != "-v":
            index += 1
            continue
        index += 1
        while index < len(rewritten) and not rewritten[index].startswith("-"):
            for original, replacement in replacements.items():
                if rewritten[index] == original:
                    rewritten[index] = replacement
                    seen[original] += 1
            index += 1
    if any(count != 1 for count in seen.values()):
        raise ValueError("invalid DemoId case negative control could not bind its identity values")
    return rewritten


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
    if mode == "SECURITYADMIN_ROLE":
        return (
            "DECLARE @membership int=IS_SRVROLEMEMBER(N'securityadmin',N'READER'); "
            "IF @membership IS NULL OR @membership<>0 "
            "THROW 51039,'QRY-023 securityadmin negative control requires a known non-member baseline.',1; "
            "ALTER SERVER ROLE [securityadmin] ADD MEMBER [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|SECURITYADMIN_ROLE_INJECTED",
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
    if mode == "SERVER_PERMISSION_DENY":
        return (
            "DENY VIEW SERVER STATE TO [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|SERVER_PERMISSION_DENY_INJECTED",
        )
    if mode == "VIEW_ANY_DATABASE_GRANT":
        return (
            "GRANT VIEW ANY DATABASE TO [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|VIEW_ANY_DATABASE_GRANT_INJECTED",
        )
    if mode == "VIEW_ANY_DATABASE_DENY":
        return (
            "DENY VIEW ANY DATABASE TO [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|VIEW_ANY_DATABASE_DENY_INJECTED",
        )
    if mode == "CONNECT_SQL_DENY":
        return (
            "DECLARE @reader_id int=SUSER_ID(N'READER'); "
            "IF @reader_id IS NULL OR NOT EXISTS (SELECT 1 FROM master.sys.server_permissions "
            "WHERE grantee_principal_id=@reader_id AND class_desc=N'SERVER' "
            "AND permission_name=N'CONNECT SQL' AND state=N'G') "
            "THROW 51038,'QRY-023 CONNECT SQL DENY requires its granted baseline.',1; "
            "DENY CONNECT SQL TO [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|CONNECT_SQL_DENY_INJECTED",
        )
    if mode == "DATABASE_PERMISSION":
        return (
            "GRANT VIEW DEFINITION TO [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|DATABASE_PERMISSION_INJECTED",
        )
    if mode == "DATABASE_PERMISSION_DENY":
        return (
            "DENY VIEW DEFINITION TO [READER];\n",
            "QRY023_NEGATIVE_PERMISSION|DATABASE_PERMISSION_DENY_INJECTED",
        )
    if mode in {"ENDPOINT_PERMISSION", "ENDPOINT_PERMISSION_DENY"}:
        is_deny = mode == "ENDPOINT_PERMISSION_DENY"
        verb = "DENY" if is_deny else "GRANT"
        marker = (
            "QRY023_NEGATIVE_PERMISSION|ENDPOINT_PERMISSION_DENY_INJECTED"
            if is_deny else "QRY023_NEGATIVE_PERMISSION|ENDPOINT_PERMISSION_INJECTED"
        )
        return (
            "DECLARE @reader_id int=SUSER_ID(N'READER'); DECLARE @endpoint_id int; "
            "SELECT @endpoint_id=endpoint_id FROM master.sys.endpoints "
            "WHERE name=N'TSQL Default TCP' AND endpoint_id<65536 AND is_admin_endpoint=0; "
            "IF @reader_id IS NULL OR @endpoint_id IS NULL "
            "THROW 51027,'QRY-023 endpoint negative control target is unavailable.',1; "
            "IF EXISTS (SELECT 1 FROM master.sys.server_permissions "
            "WHERE grantee_principal_id=@reader_id AND class_desc=N'ENDPOINT' AND major_id=@endpoint_id) "
            "THROW 51028,'QRY-023 endpoint negative control found a preexisting permission.',1; "
            f"{verb} CONNECT ON ENDPOINT::[TSQL Default TCP] TO [READER];\n",
            marker,
        )
    if mode == "CUSTOM_ENDPOINT":
        return (
            "IF EXISTS (SELECT 1 FROM master.sys.endpoints WHERE name=N'QRY023_NEGATIVE_ENDPOINT' "
            "OR endpoint_id>=65536) THROW 51033,'QRY-023 custom endpoint negative control requires a clean endpoint baseline.',1; "
            "CREATE ENDPOINT [QRY023_NEGATIVE_ENDPOINT] STATE=STOPPED AS TCP (LISTENER_PORT=25032) FOR TSQL();\n",
            "QRY023_NEGATIVE_PERMISSION|CUSTOM_ENDPOINT_INJECTED",
        )
    raise ValueError("unsupported QRY-023 negative permission mode")


def main() -> int:
    try:
        mode = os.environ.get("SQLPERF_QRY023_NEGATIVE_PERMISSION_MODE", "EXTRA_GRANT_AND_ROLE")
        if mode in {
            "RUNTOKEN_TRAILING_SPACE", "TARGETDATABASE_TRAILING_SPACE",
            "DEMOID_TRAILING_SPACE", "DEMOID_CASE_VARIANT",
        }:
            _, script, _, _, _ = proxy.parse_args(sys.argv[1:])
            if script != PREFLIGHT_SCRIPT:
                identity = {
                    "RUNTOKEN_TRAILING_SPACE": "RunToken",
                    "TARGETDATABASE_TRAILING_SPACE": "TargetDatabase",
                    "DEMOID_TRAILING_SPACE": "DemoId",
                    "DEMOID_CASE_VARIANT": "DemoId case variant",
                }[mode]
                raise ValueError(f"the SQL preflight did not reject trailing-space {identity}; later phases are blocked")
            if mode == "RUNTOKEN_TRAILING_SPACE":
                sys.argv = [sys.argv[0], *corrupt_preflight_run_token_trailing_space(sys.argv[1:])]
                print("QRY023_RUN_TOKEN_NEGATIVE|TRAILING_SPACE_INJECTED")
            elif mode == "TARGETDATABASE_TRAILING_SPACE":
                sys.argv = [sys.argv[0], *corrupt_preflight_target_database_trailing_space(sys.argv[1:])]
                print("QRY023_TARGET_DATABASE_NEGATIVE|TRAILING_SPACE_INJECTED")
            else:
                if mode == "DEMOID_TRAILING_SPACE":
                    sys.argv = [sys.argv[0], *corrupt_preflight_demo_id_trailing_space(sys.argv[1:])]
                    print("QRY023_DEMO_ID_NEGATIVE|TRAILING_SPACE_INJECTED")
                else:
                    sys.argv = [sys.argv[0], *corrupt_preflight_demo_id_case_variant(sys.argv[1:])]
                    print("QRY023_DEMO_ID_NEGATIVE|CASE_VARIANT_INJECTED")
        target = injection_target(sys.argv[1:])
        if target is not None:
            sql, marker = injection_for_mode(mode)
            container = os.environ.get("SQLPERF_SQL_CONTAINER", "")
            password = os.environ.get("SQLCMDPASSWORD", "")
            if not container or not password:
                raise ValueError("isolated container or ADMIN credential is unavailable")
            injection_database = "master" if mode in {
                "SERVER_PERMISSION", "SERVER_PERMISSION_DENY",
                "VIEW_ANY_DATABASE_GRANT",
                "VIEW_ANY_DATABASE_DENY",
                "CONNECT_SQL_DENY",
                "SECURITYADMIN_ROLE",
                "ENDPOINT_PERMISSION", "ENDPOINT_PERMISSION_DENY",
                "CUSTOM_ENDPOINT",
            } else target
            command = [
                "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", container,
                proxy._sqlcmd_path(container), "-S", "localhost", "-d", injection_database,
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
