/* Versionierter Project-Adapter-Install fuer den CON-006 READY_FOR_USER-Zustand. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname = N'SQLPERF_LAB_CON006_LOCAL';
DECLARE @Created bit = 0;
DECLARE @Sql nvarchar(max);
DECLARE @Project nvarchar(128), @Contract nvarchar(32), @Demo varchar(7), @Run varchar(20);

IF TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion')) <> 17
    THROW 51000, 'ADAPTER_UNSUPPORTED_SQL_VERSION: CON-006 erwartet SQL Server 2025.', 1;
IF EXISTS (SELECT 1 FROM sys.databases WHERE database_id > 4 AND name <> @TargetDatabase)
    THROW 51001, 'ADAPTER_ISOLATION_REQUIRED: Die Wegwerf-Instanz enthaelt fremde Benutzerdatenbanken.', 1;

IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    SET @Sql = N'CREATE DATABASE ' + QUOTENAME(@TargetDatabase) + N';';
    EXEC sys.sp_executesql @Sql;
    SET @Created = 1;
END;

SET @Sql = N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET RECOVERY SIMPLE;'
    + N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET AUTO_CLOSE OFF;'
    + N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET AUTO_SHRINK OFF;'
    + N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET PAGE_VERIFY CHECKSUM;'
    + N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET COMPATIBILITY_LEVEL = 170;';
EXEC sys.sp_executesql @Sql;

IF @Created = 1
BEGIN
    SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
        + N'EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';'
        + N'EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';'
        + N'EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=N''CON-006'';'
        + N'EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=N''LOCAL'';';
    EXEC sys.sp_executesql @Sql;
END
ELSE
BEGIN
    SET @Sql = N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),'
        + N'@Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),'
        + N'@Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),'
        + N'@Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) '
        + N'FROM ' + QUOTENAME(@TargetDatabase) + N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
    EXEC sys.sp_executesql @Sql,
        N'@Project nvarchar(128) OUTPUT,@Contract nvarchar(32) OUTPUT,@Demo varchar(7) OUTPUT,@Run varchar(20) OUTPUT',
        @Project OUTPUT, @Contract OUTPUT, @Demo OUTPUT, @Run OUTPUT;
    IF @Project <> N'SQL_PerformanceSchulung' OR @Contract <> N'1.0' OR @Demo <> 'CON-006' OR @Run <> 'LOCAL'
        THROW 51002, 'ADAPTER_STATE_CONFLICT: Die vorhandene Datenbank besitzt nicht die CON-006-Eigentumsmarker.', 1;
END;
GO
USE [SQLPERF_LAB_CON006_LOCAL];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
IF SCHEMA_ID(N'fwk') IS NULL EXEC(N'CREATE SCHEMA fwk AUTHORIZATION dbo;');
DROP TABLE IF EXISTS lab.Evidence;
DROP TABLE IF EXISTS lab.DeadlockRows;
DROP TABLE IF EXISTS fwk.SessionSignal;

CREATE TABLE lab.DeadlockRows
(
    RowId int NOT NULL CONSTRAINT PK_DeadlockRows PRIMARY KEY,
    Value int NOT NULL
);
INSERT lab.DeadlockRows(RowId, Value) VALUES (1, 0), (2, 0);

CREATE TABLE lab.Evidence
(
    RoleName varchar(16) NOT NULL,
    Outcome varchar(16) NOT NULL,
    ErrorNumber int NULL,
    CapturedAtUtc datetime2(3) NOT NULL CONSTRAINT DF_Con006Evidence_Captured DEFAULT SYSUTCDATETIME()
);

CREATE TABLE fwk.SessionSignal
(
    DemoId varchar(7) NOT NULL,
    RunToken varchar(20) NOT NULL,
    SignalName varchar(64) NOT NULL,
    SignaledAtUtc datetime2(3) NOT NULL CONSTRAINT DF_Con006Signal_Captured DEFAULT SYSUTCDATETIME(),
    SignaledBySessionId smallint NOT NULL,
    CONSTRAINT PK_Con006SessionSignal PRIMARY KEY(DemoId, RunToken, SignalName)
);
GO
CREATE OR ALTER PROCEDURE fwk.USP_Signal
    @DemoId varchar(7), @RunToken varchar(20), @SignalName varchar(64)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    IF @SignalName IS NULL OR @SignalName COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9_]%'
        THROW 51000, 'FAIL_CONTRACT: Ungueltiger Signalname.', 1;
    UPDATE fwk.SessionSignal
       SET SignaledAtUtc = SYSUTCDATETIME(), SignaledBySessionId = @@SPID
     WHERE DemoId = @DemoId AND RunToken = @RunToken AND SignalName = @SignalName;
    IF @@ROWCOUNT = 0
    BEGIN TRY
        INSERT fwk.SessionSignal(DemoId, RunToken, SignalName, SignaledBySessionId)
        VALUES(@DemoId, @RunToken, @SignalName, @@SPID);
    END TRY
    BEGIN CATCH
        IF ERROR_NUMBER() NOT IN (2601, 2627) THROW;
        UPDATE fwk.SessionSignal
           SET SignaledAtUtc = SYSUTCDATETIME(), SignaledBySessionId = @@SPID
         WHERE DemoId = @DemoId AND RunToken = @RunToken AND SignalName = @SignalName;
    END CATCH;
END;
GO
CREATE OR ALTER PROCEDURE fwk.USP_WaitForSignal
    @DemoId varchar(7), @RunToken varchar(20), @SignalName varchar(64), @TimeoutMs int
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    DECLARE @Start datetime2(3) = SYSUTCDATETIME();
    IF @TimeoutMs NOT BETWEEN 1 AND 30000
        THROW 51000, 'FAIL_CONTRACT: Signal-Timeout ist ungueltig.', 1;
    WHILE NOT EXISTS
    (
        SELECT 1 FROM fwk.SessionSignal WITH (READUNCOMMITTED)
         WHERE DemoId = @DemoId AND RunToken = @RunToken AND SignalName = @SignalName
    )
    BEGIN
        IF DATEDIFF_BIG(millisecond, @Start, SYSUTCDATETIME()) >= @TimeoutMs
            THROW 51005, 'FAIL_TIMEOUT: Erwartetes CON-006-Signal fehlt.', 1;
        WAITFOR DELAY '00:00:00.050';
    END;
END;
GO
DELETE fwk.SessionSignal;
DELETE lab.Evidence;
UPDATE lab.DeadlockRows SET Value = 0;

IF (SELECT COUNT(*) FROM lab.DeadlockRows) <> 2 OR EXISTS (SELECT 1 FROM lab.DeadlockRows WHERE Value <> 0)
    THROW 51006, 'FAIL_RESULT_CONTRACT: CON-006-Ausgangsdaten sind inkonsistent.', 1;

SELECT N'CON-006' AS ScenarioId, N'INSTALL' AS Phase, N'READY_FOR_USER' AS Outcome,
       DB_NAME() AS TargetDatabase, 2 AS PreparedRows;
GO
