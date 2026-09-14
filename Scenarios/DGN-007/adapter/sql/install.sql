/* Project-Adapter-Install fuer den DGN-007 READY_FOR_USER-Zustand (Schnitt A: Datenaufbau, Query-Store-Zeitfenster, Incident-Erzeugung). */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname = N'SQLPERF_LAB_DGN007_LOCAL';
DECLARE @Sql nvarchar(max), @DatabaseId int;

IF TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion')) <> 17
    THROW 51000, 'ADAPTER_UNSUPPORTED_SQL_VERSION: DGN-007 erwartet SQL Server 2025.', 1;
IF EXISTS (SELECT 1 FROM sys.databases WHERE database_id > 4 AND name <> @TargetDatabase)
    THROW 51001, 'ADAPTER_ISOLATION_REQUIRED: Die Wegwerf-Instanz enthaelt fremde Benutzerdatenbanken.', 1;
IF DB_ID(@TargetDatabase) IS NOT NULL
    THROW 51002, 'ADAPTER_STATE_CONFLICT: DGN-007 uebernimmt keine vorhandene Datenbank.', 1;

CREATE DATABASE [SQLPERF_LAB_DGN007_LOCAL];
ALTER DATABASE [SQLPERF_LAB_DGN007_LOCAL] SET RECOVERY SIMPLE;
ALTER DATABASE [SQLPERF_LAB_DGN007_LOCAL] SET COMPATIBILITY_LEVEL = 170;
EXEC [SQLPERF_LAB_DGN007_LOCAL].sys.sp_addextendedproperty @name=N'SQLPERF.Project',@value=N'SQL_PerformanceSchulung';
EXEC [SQLPERF_LAB_DGN007_LOCAL].sys.sp_addextendedproperty @name=N'SQLPERF.ContractVersion',@value=N'1.0';
EXEC [SQLPERF_LAB_DGN007_LOCAL].sys.sp_addextendedproperty @name=N'SQLPERF.DemoId',@value=N'DGN-007';
EXEC [SQLPERF_LAB_DGN007_LOCAL].sys.sp_addextendedproperty @name=N'SQLPERF.RunToken',@value=N'LOCAL';

/* Query-Store mit begrenztem Capture- und Groessenvertrag. */
SET @Sql = N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET QUERY_STORE = ON ('
    + N'OPERATION_MODE = READ_WRITE,'
    + N'CLEANUP_POLICY = STALE_QUERY_THRESHOLD_DAYS = 2,'
    + N'DATA_FLUSH_INTERVAL_SECONDS = 60,'
    + N'MAX_STORAGE_SIZE_MB = 128,'
    + N'INTERVAL_LENGTH_MINUTES = 1,'
    + N'SIZE_BASED_CLEANUP_MODE = AUTO,'
    + N'QUERY_CAPTURE_MODE = AUTO,'
    + N'MAX_PLANS_PER_QUERY = 20);';
EXEC sys.sp_executesql @Sql;

/* Capstone-Datenmodell: neutrale Gruppen- und Statusverteilung mit deterministischem Skew. */
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'CREATE SCHEMA dbo AUTHORIZATION dbo;'
    + N'CREATE TABLE dbo.CaseGroup(GroupKey int NOT NULL PRIMARY KEY,GroupLabel nvarchar(64) NOT NULL);'
    + N'CREATE TABLE dbo.CaseItem(ItemId int IDENTITY(1,1) NOT NULL PRIMARY KEY,'
    + N'GroupKey int NOT NULL CONSTRAINT FK_CaseItem_CaseGroup REFERENCES dbo.CaseGroup(GroupKey),'
    + N'StatusCode tinyint NOT NULL,SearchValue nvarchar(64) NOT NULL,Payload binary(96) NOT NULL,'
    + N'CONSTRAINT IX_CaseItem_Group_Status NONCLUSTERED (GroupKey,StatusCode) INCLUDE (SearchValue));'
    + N'CREATE CLUSTERED INDEX CIX_CaseItem ON dbo.CaseItem(ItemId);'
    + N'CREATE TABLE dbo.CaseItemDetail(ItemId int NOT NULL,DetailOrdinal int NOT NULL,DetailPayload binary(128) NOT NULL,'
    + N'CONSTRAINT PK_CaseItemDetail PRIMARY KEY(ItemId,DetailOrdinal),'
    + N'CONSTRAINT FK_CaseItemDetail_CaseItem FOREIGN KEY(ItemId) REFERENCES dbo.CaseItem(ItemId));'
    + N'CREATE TABLE dbo.CaseRequestLog(RequestLogId bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,'
    + N'GroupKey int NOT NULL,StatusCode tinyint NOT NULL,RequestedUtc datetime2(0) NOT NULL);'
    + N'CREATE CLUSTERED INDEX CIX_CaseRequestLog ON dbo.CaseRequestLog(RequestLogId);';
EXEC sys.sp_executesql @Sql;

/* Deterministische Daten: vier haeufige, drei mittlere und fuenf seltene Gruppen. */
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N';WITH Digits(n) AS (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4'
    + N' UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9),'
    + N'Numbers(n) AS (SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) FROM Digits a CROSS JOIN Digits b CROSS JOIN Digits c)'
    + N'INSERT dbo.CaseGroup(GroupKey,GroupLabel)'
    + N'SELECT n,N''Group'' + CONVERT(nvarchar(11),n) FROM Numbers WHERE n BETWEEN 1 AND 12;'
    + N';WITH Digits(n) AS (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4'
    + N' UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9),'
    + N'Numbers(n) AS (SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) FROM Digits a CROSS JOIN Digits b CROSS JOIN Digits c),'
    + N'Items AS (SELECT n,'
    + N'CASE WHEN n % 5 IN (1,2) THEN 1 WHEN n % 5 = 3 THEN 2 ELSE 3 + (n % 9) END AS GroupKey,'
    + N'CASE WHEN n % 7 = 0 THEN 1 WHEN n % 7 IN (3,5) THEN 2 ELSE 3 END AS StatusCode'
    + N' FROM Numbers WHERE n BETWEEN 1 AND 24000)'
    + N'INSERT dbo.CaseItem(SearchValue,GroupKey,StatusCode,Payload)'
    + N'SELECT N''Search'' + CONVERT(nvarchar(11),n),GroupKey,StatusCode,CONVERT(binary(96),REPLICATE(CONVERT(binary(1),0x5A),96)) FROM Items;'
    + N';WITH Digits(n) AS (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4'
    + N' UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9),'
    + N'Numbers(n) AS (SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) FROM Digits a CROSS JOIN Digits b)'
    + N'INSERT dbo.CaseItemDetail(ItemId,DetailOrdinal,Payload)'
    + N'SELECT i.ItemId,d.n,CONVERT(binary(128),REPLICATE(CONVERT(binary(1),0x41),128))'
    + N'FROM dbo.CaseItem i JOIN Numbers x ON x.n BETWEEN 1 AND 3;';
EXEC sys.sp_executesql @Sql;

/* Markierte Suchprozedur mit festem Ergebnisvertrag; kompilierter Parameterwert ergibt sich aus der Aufrufreihenfolge. */
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'CREATE OR ALTER PROCEDURE dbo.usp_CaseSearch @GroupKey int, @StatusCode tinyint'
    + N' AS BEGIN SET NOCOUNT ON;'
    + N'SELECT i.ItemId,i.SearchValue,i.StatusCode,g.GroupLabel,'
    + N'(SELECT COUNT(*) FROM dbo.CaseItemDetail d WHERE d.ItemId = i.ItemId) AS DetailCount'
    + N'FROM dbo.CaseItem i JOIN dbo.CaseGroup g ON g.GroupKey = i.GroupKey'
    + N'WHERE i.GroupKey = @GroupKey AND i.StatusCode = @StatusCode'
    + N'ORDER BY i.ItemId;'
    + N'INSERT dbo.CaseRequestLog(GroupKey,StatusCode,RequestedUtc) VALUES(@GroupKey,@StatusCode,SYSUTCDATETIME());'
    + N'END;';
EXEC sys.sp_executesql @Sql;

/* Baseline-Marker fuer den VALIDATE-Entrypoint. */
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'CREATE TABLE lab.IncidentState(IncidentPhase nvarchar(32) NOT NULL,MarkerUtc datetime2(0) NOT NULL);'
    + N'INSERT lab.IncidentState VALUES(N''T0_BASELINE'',SYSUTCDATETIME());';
EXEC sys.sp_executesql @Sql;

/* Query-Store-Zeitfenster T0_BASELINE und Incidentfenster T1_INCIDENT erzeugen. */
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'EXEC dbo.usp_CaseSearch 3,3; EXEC dbo.usp_CaseSearch 3,3; EXEC dbo.usp_CaseSearch 3,3;'
    + N'WAITFOR DELAY ''00:00:02'';'
    + N'EXEC dbo.usp_CaseSearch 1,3; EXEC dbo.usp_CaseSearch 1,3; EXEC dbo.usp_CaseSearch 1,3;'
    + N'EXEC dbo.usp_CaseSearch 1,1; EXEC dbo.usp_CaseSearch 1,1;'
    + N'UPDATE lab.IncidentState SET IncidentPhase = N''T1_INCIDENT'', IncidentUtc = SYSUTCDATETIME();';
EXEC sys.sp_executesql @Sql;

SELECT N'DGN-007' AS ScenarioId, N'INSTALL' AS Phase, N'READY_FOR_USER' AS Outcome,
       @TargetDatabase AS TargetDatabase;