/* Project-Adapter-Install fuer den DGN-005 READY_FOR_USER-Zustand. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname = N'SQLPERF_LAB_DGN005_LOCAL';
DECLARE @SessionName sysname = N'SQLPERF_DGN005_LOCAL';
DECLARE @Sql nvarchar(max), @DatabaseId int;

IF TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion')) <> 17
    THROW 51000, 'ADAPTER_UNSUPPORTED_SQL_VERSION: DGN-005 erwartet SQL Server 2025.', 1;
IF EXISTS (SELECT 1 FROM sys.databases WHERE database_id > 4 AND name <> @TargetDatabase)
    THROW 51001, 'ADAPTER_ISOLATION_REQUIRED: Die Wegwerf-Instanz enthaelt fremde Benutzerdatenbanken.', 1;
IF DB_ID(@TargetDatabase) IS NOT NULL OR EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name = @SessionName)
    THROW 51002, 'ADAPTER_STATE_CONFLICT: DGN-005 uebernimmt keine vorhandene Datenbank oder Event Session.', 1;

CREATE DATABASE [SQLPERF_LAB_DGN005_LOCAL];
ALTER DATABASE [SQLPERF_LAB_DGN005_LOCAL] SET RECOVERY SIMPLE;
ALTER DATABASE [SQLPERF_LAB_DGN005_LOCAL] SET COMPATIBILITY_LEVEL = 170;
EXEC [SQLPERF_LAB_DGN005_LOCAL].sys.sp_addextendedproperty @name=N'SQLPERF.Project',@value=N'SQL_PerformanceSchulung';
EXEC [SQLPERF_LAB_DGN005_LOCAL].sys.sp_addextendedproperty @name=N'SQLPERF.ContractVersion',@value=N'1.0';
EXEC [SQLPERF_LAB_DGN005_LOCAL].sys.sp_addextendedproperty @name=N'SQLPERF.DemoId',@value=N'DGN-005';
EXEC [SQLPERF_LAB_DGN005_LOCAL].sys.sp_addextendedproperty @name=N'SQLPERF.RunToken',@value=N'LOCAL';
EXEC [SQLPERF_LAB_DGN005_LOCAL].sys.sp_executesql N'CREATE SCHEMA lab AUTHORIZATION dbo;';
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'CREATE TABLE lab.XeEvidence(EventCount int NULL,SessionStopped bit NOT NULL DEFAULT(0));'
    + N'INSERT lab.XeEvidence DEFAULT VALUES;';
EXEC sys.sp_executesql @Sql;

SET @DatabaseId = DB_ID(@TargetDatabase);
SET @Sql = N'CREATE EVENT SESSION ' + QUOTENAME(@SessionName) + N' ON SERVER '
    + N'ADD EVENT sqlserver.error_reported('
    + N'ACTION(sqlserver.database_id,sqlserver.session_id) '
    + N'WHERE ([error_number]>=(50000) AND [sqlserver].[database_id]=(' + CONVERT(nvarchar(20), @DatabaseId) + N'))) '
    + N'ADD TARGET package0.ring_buffer(SET MAX_EVENTS_LIMIT=(100),MAX_MEMORY=(1024)) '
    + N'WITH(MAX_MEMORY=2048 KB,EVENT_RETENTION_MODE=ALLOW_SINGLE_EVENT_LOSS,'
    + N'MAX_DISPATCH_LATENCY=1 SECONDS,TRACK_CAUSALITY=ON,STARTUP_STATE=OFF,MAX_DURATION=300 SECONDS); '
    + N'ALTER EVENT SESSION ' + QUOTENAME(@SessionName) + N' ON SERVER STATE=START;';
EXEC sys.sp_executesql @Sql;

SELECT N'DGN-005' AS ScenarioId, N'INSTALL' AS Phase, N'READY_FOR_USER' AS Outcome,
       @TargetDatabase AS TargetDatabase, @SessionName AS EventSession;
