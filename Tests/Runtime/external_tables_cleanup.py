"""Guarded and resumable SQL cleanup for the two External Tables guests."""

from __future__ import annotations

from collections.abc import Mapping

from external_tables_pilot_sql import EDITION, SOURCE_CREDENTIAL, VERSION, Role, Route, database_name, owned_database_guard
from external_tables_principals import Principal, login_sid_literal, principal_name


def drop_pilot_database_batch(token: str, role: Role) -> str:
    """Run on a dedicated admin connection to the existing owned database."""
    db = database_name(token, role)
    sql = """IF @@TRANCOUNT <> 0 OR (@@OPTIONS & 2) <> 0
    THROW 51074, 'FAIL_CLEANUP: database teardown requires an autocommit session.', 1;
""" + owned_database_guard(token, role)
    sql += """
IF EXISTS (
    SELECT 1 FROM sys.dm_exec_sessions
    WHERE session_id <> @@SPID AND database_id = DB_ID()
)
    THROW 51074, 'FAIL_CLEANUP: close outstanding connections before dropping the database.', 1;
"""
    if role is Role.QUERY:
        sql += "BEGIN TRANSACTION;\n"
        for route in (Route.PUSHDOWN_ON, Route.PUSHDOWN_OFF):
            sql += f"""
IF EXISTS (SELECT 1 FROM sys.external_tables WHERE object_id = OBJECT_ID(N'dbo.{route.value}'))
    DROP EXTERNAL TABLE dbo.{route.value};
"""
        for source in ("PilotPush", "PilotLocalFilter"):
            sql += f"""
IF EXISTS (SELECT 1 FROM sys.external_data_sources WHERE name = N'{source}')
    DROP EXTERNAL DATA SOURCE [{source}];
"""
        sql += f"""
IF EXISTS (SELECT 1 FROM sys.database_scoped_credentials WHERE name = N'{SOURCE_CREDENTIAL}')
    DROP DATABASE SCOPED CREDENTIAL [{SOURCE_CREDENTIAL}];
IF EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = N'##MS_DatabaseMasterKey##')
    DROP MASTER KEY;
COMMIT;
"""
    return sql + f"""
USE [master];
DROP DATABASE [{db}];
IF DB_ID(N'{db}') IS NOT NULL
    THROW 51075, 'FAIL_CLEANUP: External Tables database still exists.', 1;
"""


def drop_pilot_logins_batch(token: str, role: Role, login_sids: Mapping[Principal, bytes]) -> str:
    """Run in master using SIDs recorded before attempting login creation."""
    db = database_name(token, role)
    principals = tuple(principal for principal in Principal if principal.role is role)
    if any(principal not in principals for principal in login_sids):
        raise ValueError("login inventory contains a principal from another guest role")
    sid_literals = {principal: login_sid_literal(sid) for principal, sid in login_sids.items()}
    if len(set(sid_literals.values())) != len(sid_literals):
        raise ValueError("login inventory has duplicate SIDs")

    sql = f"""SET NOCOUNT ON;
SET XACT_ABORT ON;
IF DB_NAME() <> N'master'
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'ProductVersion')), N'') <> N'{VERSION}'
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'Edition')), N'') <> N'{EDITION}'
    OR DB_ID(N'{db}') IS NOT NULL
    THROW 51076, 'FAIL_CLEANUP: unexpected guest or External Tables database still exists.', 1;
"""
    for principal in principals:
        name = principal_name(token, principal)
        sid_literal = sid_literals.get(principal)
        if sid_literal is None:
            sql += f"""
IF SUSER_ID(N'{name}') IS NOT NULL
    THROW 51077, 'FAIL_OWNERSHIP: External Tables login was not recorded.', 1;
"""
            continue
        sql += f"""
IF EXISTS (
    SELECT 1 FROM sys.server_principals WHERE principal_id = SUSER_ID(N'{name}')
        AND (type <> 'S' OR sid <> {sid_literal}
            OR name COLLATE Latin1_General_100_BIN2 <> N'{name}' OR DATALENGTH(name) <> DATALENGTH(N'{name}'))
) OR EXISTS (
    SELECT 1 FROM sys.server_principals WHERE sid = {sid_literal}
        AND principal_id <> COALESCE(SUSER_ID(N'{name}'), -1)
)
    THROW 51077, 'FAIL_OWNERSHIP: External Tables SQL login differs from the inventory.', 1;
IF EXISTS (SELECT 1 FROM sys.dm_exec_sessions WHERE original_security_id = {sid_literal})
    THROW 51078, 'FAIL_CLEANUP: an owned External Tables login still has a session.', 1;
"""
    for principal in sid_literals:
        name = principal_name(token, principal)
        sql += f"""
IF EXISTS (SELECT 1 FROM sys.server_principals WHERE principal_id = SUSER_ID(N'{name}') AND sid = {sid_literals[principal]})
    DROP LOGIN [{name}];
"""
    for principal in principals:
        name = principal_name(token, principal)
        sql += f"""
IF SUSER_ID(N'{name}') IS NOT NULL
    THROW 51079, 'FAIL_CLEANUP: External Tables SQL login still exists.', 1;
"""
    return sql
