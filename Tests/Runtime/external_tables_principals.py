"""Run-bound SQL login setup and effective-rights probes for External Tables."""

from __future__ import annotations

from enum import Enum
import re

from external_tables_pilot_sql import (
    SOURCE_CREDENTIAL, SOURCE_READER_PREFIX, Role, Route, database_guard, database_name, owned_database_guard,
)


PASSWORD = re.compile(r"Ext9![0-9a-f]{32}", re.ASCII)


class Principal(Enum):
    SOURCE_READER = SOURCE_READER_PREFIX
    QUERY_READER = "SqlPerfExtQueryReader"
    OBSERVER = "SqlPerfExtObserver"

    @property
    def role(self) -> Role:
        return Role.SOURCE if self is Principal.SOURCE_READER else Role.QUERY


def principal_name(token: str, principal: Principal) -> str:
    if not isinstance(principal, Principal):
        raise ValueError("expected an External Tables principal")
    database_name(token, principal.role)
    return f"{principal.value}_{token}"


def create_principal_batch(token: str, principal: Principal, password: str) -> str:
    """Prepare secret-bearing SQL for the owned guest, with setup capture disabled."""
    name = principal_name(token, principal)
    if not PASSWORD.fullmatch(password):
        raise ValueError("expected a generated per-run SQL login secret")
    db = database_name(token, principal.role)
    sql = owned_database_guard(token, principal.role) + f"""
IF SUSER_ID(N'{name}') IS NOT NULL OR USER_ID(N'{name}') IS NOT NULL
    THROW 51066, 'FAIL_STATE: External Tables principal already exists.', 1;
"""
    if principal is Principal.QUERY_READER:
        sql += """
IF NOT EXISTS (SELECT 1 FROM sys.external_tables WHERE object_id = OBJECT_ID(N'dbo.FactsPush'))
    OR NOT EXISTS (SELECT 1 FROM sys.external_tables WHERE object_id = OBJECT_ID(N'dbo.FactsLocalFilter'))
    THROW 51067, 'FAIL_STATE: intended external tables are not available.', 1;
"""
    sql += f"""
BEGIN TRANSACTION;
USE [master];
CREATE LOGIN [{name}] WITH PASSWORD = '{password}', DEFAULT_DATABASE = [{db}],
    CHECK_POLICY = ON, CHECK_EXPIRATION = OFF;
"""
    if principal is Principal.OBSERVER:
        sql += f"GRANT VIEW SERVER PERFORMANCE STATE TO [{name}];\n"
    sql += f"USE [{db}];\nCREATE USER [{name}] FOR LOGIN [{name}];\n"
    if principal is not Principal.OBSERVER:
        routes = (Route.LOCAL,) if principal is Principal.SOURCE_READER else tuple(Route)
        for route in routes:
            sql += f"GRANT SELECT ON OBJECT::dbo.{route.value} TO [{name}];\n"
    return sql + "COMMIT;\n"


def create_connector_credential_batch(token: str, source_password: str, master_key_password: str) -> str:
    """Bind the source reader secret to the owned query database."""
    source_login = principal_name(token, Principal.SOURCE_READER)
    if (
        not PASSWORD.fullmatch(source_password) or not PASSWORD.fullmatch(master_key_password)
        or source_password == master_key_password
    ):
        raise ValueError("expected two distinct generated pilot secrets")
    return owned_database_guard(token, Role.QUERY) + f"""
IF EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = N'##MS_DatabaseMasterKey##')
    OR EXISTS (SELECT 1 FROM sys.database_scoped_credentials WHERE name = N'{SOURCE_CREDENTIAL}')
    THROW 51073, 'FAIL_STATE: External Tables key or credential already exists.', 1;
BEGIN TRANSACTION;
CREATE MASTER KEY ENCRYPTION BY PASSWORD = '{master_key_password}';
CREATE DATABASE SCOPED CREDENTIAL [{SOURCE_CREDENTIAL}]
WITH IDENTITY = N'{source_login}', SECRET = '{source_password}';
COMMIT;
"""


def principal_probe_batch(token: str, principal: Principal) -> str:
    """Check the actual connection, avoiding SQL impersonation or writes."""
    name = principal_name(token, principal)
    sql = database_guard(token, principal.role) + f"""
IF ORIGINAL_LOGIN() COLLATE Latin1_General_100_BIN2 <> N'{name}'
    OR USER_NAME() COLLATE Latin1_General_100_BIN2 <> N'{name}'
    OR DATALENGTH(ORIGINAL_LOGIN()) <> DATALENGTH(N'{name}')
    OR DATALENGTH(USER_NAME()) <> DATALENGTH(N'{name}')
    OR COALESCE(IS_SRVROLEMEMBER(N'sysadmin'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(NULL, NULL, N'CONTROL SERVER'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(NULL, NULL, N'ALTER ANY LOGIN'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'CONTROL'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'CREATE TABLE'), 1) <> 0
    THROW 51068, 'FAIL_CONTRACT: External Tables login or base privileges differ.', 1;
"""
    observer = principal is Principal.OBSERVER
    sql += f"""
IF COALESCE(HAS_PERMS_BY_NAME(NULL, NULL, N'VIEW SERVER STATE'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(NULL, NULL, N'VIEW SERVER PERFORMANCE STATE'), -1) <> {int(observer)}
    THROW 51069, 'FAIL_CONTRACT: External Tables diagnosis privileges differ.', 1;

BEGIN TRY
    DECLARE @prohibited int;
    SELECT TOP (0) @prohibited = FactId FROM dbo.PilotDenied;
    THROW 51070, 'FAIL_CONTRACT: External Tables principal can read the negative-control object.', 1;
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() <> 229 THROW;
END CATCH;
"""
    if observer:
        return sql + """
IF COALESCE(HAS_PERMS_BY_NAME(N'dbo.Facts', N'OBJECT', N'SELECT'), 0) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(N'dbo.FactsPush', N'OBJECT', N'SELECT'), 0) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(N'dbo.FactsLocalFilter', N'OBJECT', N'SELECT'), 0) <> 0
    THROW 51071, 'FAIL_CONTRACT: observer has direct fixture access.', 1;
DECLARE @diagnosis int;
SELECT TOP (1) @diagnosis = r.session_id
FROM sys.dm_exec_requests AS r CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) AS t
WHERE r.database_id = DB_ID();
"""
    routes = (Route.LOCAL,) if principal is Principal.SOURCE_READER else tuple(Route)
    for route in routes:
        sql += f"""
IF COALESCE(HAS_PERMS_BY_NAME(N'dbo.{route.value}', N'OBJECT', N'SELECT'), 0) <> 1
    OR COALESCE(HAS_PERMS_BY_NAME(N'dbo.{route.value}', N'OBJECT', N'INSERT'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(N'dbo.{route.value}', N'OBJECT', N'UPDATE'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(N'dbo.{route.value}', N'OBJECT', N'DELETE'), 1) <> 0
    THROW 51072, 'FAIL_CONTRACT: External Tables reader rights differ.', 1;
"""
    return sql
