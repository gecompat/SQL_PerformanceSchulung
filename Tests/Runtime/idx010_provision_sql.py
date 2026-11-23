"""SQL provisioning and cleanup for the two guarded ordered NCCI databases."""
from __future__ import annotations

import re

from idx010_pilot_sequence import Target
from idx010_pilot_setup import owned_database_guard


def reader_login(run_token: str) -> str:
    if re.fullmatch(r"[A-Z0-9]{1,20}", run_token, re.ASCII) is None:
        raise ValueError("invalid pilot run token")
    return f"idx010_reader_{run_token}"


def create_reader_batch(run_token: str, password: str) -> str:
    login = reader_login(run_token)
    if re.fullmatch(r"Idx9![A-Za-z0-9]{32}", password, re.ASCII) is None:
        raise ValueError("invalid generated reader secret")
    return f"""
SET NOCOUNT ON;
IF DB_NAME() <> N'master' OR SUSER_ID(N'{login}') IS NOT NULL
    THROW 51020, 'FAIL_STATE: pilot reader target is not fresh.', 1;
CREATE LOGIN [{login}] WITH PASSWORD = '{password}',
    DEFAULT_DATABASE = [master], CHECK_POLICY = ON, CHECK_EXPIRATION = OFF;
"""


def provision_database_batch(target: Target) -> str:
    db = target.database_name
    login = reader_login(target.run_token)
    return f"""
SET NOCOUNT ON;
IF DB_NAME() <> N'master' OR DB_ID(N'{db}') IS NOT NULL OR SUSER_ID(N'{login}') IS NULL
    THROW 51021, 'FAIL_STATE: pilot database target is not fresh.', 1;
GO
CREATE DATABASE [{db}]
ON PRIMARY (NAME = N'PilotData', FILENAME = N'/var/opt/mssql/data/{db}.mdf',
    SIZE = 128 MB, MAXSIZE = 512 MB, FILEGROWTH = 32 MB)
LOG ON (NAME = N'PilotLog', FILENAME = N'/var/opt/mssql/data/{db}.ldf',
    SIZE = 64 MB, MAXSIZE = 512 MB, FILEGROWTH = 32 MB);
GO
ALTER DATABASE [{db}] SET RECOVERY SIMPLE;
ALTER DATABASE [{db}] SET COMPATIBILITY_LEVEL = 170;
USE [{db}];
SET XACT_ABORT ON;
IF (SELECT COUNT(*) FROM sys.database_files) <> 2
    OR (SELECT COUNT(*) FROM sys.database_files WHERE type IN (0, 1) AND max_size = 65536
        AND size <= max_size) <> 2
    THROW 51027, 'FAIL_CONTRACT: pilot database file caps cannot be confirmed.', 1;
BEGIN TRANSACTION;
EXEC sys.sp_addextendedproperty N'SQLPERF.Project', N'SQL_PerformanceSchulung';
EXEC sys.sp_addextendedproperty N'SQLPERF.ContractVersion', N'1.0';
EXEC sys.sp_addextendedproperty N'SQLPERF.DemoId', N'IDX-010';
EXEC sys.sp_addextendedproperty N'SQLPERF.RunToken', N'{target.run_token}';
EXEC sys.sp_addextendedproperty N'SQLPERF.PilotProfile', N'ORDERED_NCCI_{target.arm.value}';
COMMIT;
CREATE USER [{login}] FOR LOGIN [{login}];
GRANT SHOWPLAN TO [{login}];
"""


def grant_reader_batch(target: Target) -> str:
    login = reader_login(target.run_token)
    return owned_database_guard(target.run_token, target.arm) + f"""
GRANT SELECT ON OBJECT::dbo.Events TO [{login}];
EXECUTE AS USER = N'{login}';
IF COALESCE(HAS_PERMS_BY_NAME(N'dbo.Events', N'OBJECT', N'SELECT'), 0) <> 1
    OR COALESCE(HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'SHOWPLAN'), 0) <> 1
    OR COALESCE(HAS_PERMS_BY_NAME(N'dbo.Events', N'OBJECT', N'UPDATE'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(N'dbo.Events', N'OBJECT', N'INSERT'), 1) <> 0
    OR COALESCE(HAS_PERMS_BY_NAME(N'dbo.Events', N'OBJECT', N'DELETE'), 1) <> 0
BEGIN
    REVERT;
    THROW 51022, 'FAIL_CONTRACT: pilot reader permissions differ.', 1;
END;
REVERT;
"""


def drop_database_batch(target: Target) -> str:
    db = target.database_name
    return owned_database_guard(target.run_token, target.arm) + f"""
USE [master];
ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE [{db}];
IF DB_ID(N'{db}') IS NOT NULL
    THROW 51023, 'FAIL_CLEANUP: pilot database still exists.', 1;
"""


TEMPDB_CAPS = """
SET NOCOUNT ON;
DECLARE @File sysname, @Type tinyint, @Size int, @Cap int, @Command nvarchar(max);
DECLARE @DataCount int = (SELECT COUNT(*) FROM tempdb.sys.database_files WHERE type = 0);
DECLARE @LogCount int = (SELECT COUNT(*) FROM tempdb.sys.database_files WHERE type = 1);
IF @DataCount NOT BETWEEN 1 AND 16 OR @LogCount <> 1
    OR EXISTS (SELECT 1 FROM tempdb.sys.database_files WHERE type NOT IN (0, 1))
    THROW 51024, 'FAIL_CONTRACT: unexpected TempDB files.', 1;
DECLARE files CURSOR LOCAL FAST_FORWARD FOR SELECT name, type, size FROM tempdb.sys.database_files;
OPEN files;
FETCH NEXT FROM files INTO @File, @Type, @Size;
WHILE @@FETCH_STATUS = 0
BEGIN
    SET @Cap = CASE WHEN @Type = 0 THEN 512 / @DataCount ELSE 256 END;
    IF @Size > @Cap * 128
        THROW 51025, 'FAIL_CONTRACT: TempDB file already exceeds its cap.', 1;
    SET @Command = N'ALTER DATABASE [tempdb] MODIFY FILE (NAME = ' + QUOTENAME(@File)
        + N', MAXSIZE = ' + CONVERT(nvarchar(12), @Cap) + N'MB, FILEGROWTH = 8MB);';
    EXEC sys.sp_executesql @Command;
    FETCH NEXT FROM files INTO @File, @Type, @Size;
END;
CLOSE files;
DEALLOCATE files;
IF (SELECT COUNT(*) FROM tempdb.sys.database_files WHERE type = 0) <> @DataCount
    OR (SELECT COUNT(*) FROM tempdb.sys.database_files WHERE type = 1) <> @LogCount
    OR EXISTS (SELECT 1 FROM tempdb.sys.database_files WHERE max_size <= 0 OR size > max_size)
    OR (SELECT SUM(CONVERT(bigint, max_size)) FROM tempdb.sys.database_files WHERE type = 0) > 65536
    OR (SELECT SUM(CONVERT(bigint, max_size)) FROM tempdb.sys.database_files WHERE type = 1) > 32768
    THROW 51026, 'FAIL_CONTRACT: TempDB caps cannot be confirmed.', 1;
"""
