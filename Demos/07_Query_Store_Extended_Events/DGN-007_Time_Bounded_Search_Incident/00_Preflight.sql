/* DGN-007 / Schnitt B: read-only Preflight gegen den vom Adapter vorbereiteten Zustand. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname = N'SQLPERF_LAB_DGN007_LOCAL';
DECLARE @Major int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @Project nvarchar(128), @Contract nvarchar(32), @DemoId varchar(7), @RunToken varchar(20);
DECLARE @QueryStoreState nvarchar(60), @Sql nvarchar(max);

IF @Major NOT BETWEEN 15 AND 17
BEGIN
    SELECT 1 AS Sequence, 'PREFLIGHT' AS Phase, 'ENGINE_VERSION' AS CheckId, 'SKIP' AS Outcome,
           'SKIP_VERSION' AS Code, CONVERT(nvarchar(20), @Major) AS ObservedValue, N'SQL Server 2019 bis 2025' AS RequiredValue,
           N'DGN-007 setzt eine unterstützte SQL-Server-Version voraus.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';
    RETURN;
END;
IF DB_ID(@TargetDatabase) IS NULL
    THROW 51000, 'FAIL_STATE: Der DGN-007-Adapterzustand fehlt.', 1;

SET @Sql = N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),@Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),@DemoId=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),@RunToken=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql, N'@Project nvarchar(128) OUTPUT,@Contract nvarchar(32) OUTPUT,@DemoId varchar(7) OUTPUT,@RunToken varchar(20) OUTPUT', @Project OUTPUT,@Contract OUTPUT,@DemoId OUTPUT,@RunToken OUTPUT;
IF @Project<>N'SQL_PerformanceSchulung' OR @Contract<>N'1.0' OR @DemoId<>'DGN-007' OR @RunToken<>'LOCAL'
    THROW 51001, 'FAIL_CONTRACT: Die vier DGN-007-Eigentumsmarker stimmen nicht überein.', 1;
SET @Sql=N'SELECT @QueryStoreState=actual_state_desc FROM '+QUOTENAME(@TargetDatabase)+N'.sys.database_query_store_options;';
EXEC sys.sp_executesql @Sql,N'@QueryStoreState nvarchar(60) OUTPUT',@QueryStoreState OUTPUT;
IF @QueryStoreState<>N'READ_WRITE'
BEGIN
    SELECT 2 AS Sequence, 'PREFLIGHT' AS Phase, 'QUERY_STORE' AS CheckId, 'SKIP' AS Outcome,
           'SKIP_QUERY_STORE_REQUIRED' AS Code, @QueryStoreState AS ObservedValue, N'READ_WRITE' AS RequiredValue,
           N'Der Capstone benötigt einen beschreibbaren Query Store in der markierten Testdatenbank.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_QUERY_STORE_REQUIRED';
    RETURN;
END;
IF HAS_PERMS_BY_NAME(NULL, NULL, 'ALTER ANY EVENT SESSION')<>1 OR HAS_PERMS_BY_NAME(NULL, NULL, 'VIEW SERVER STATE')<>1
BEGIN
    SELECT 3 AS Sequence, 'PREFLIGHT' AS Phase, 'XE_PERMISSION' AS CheckId, 'SKIP' AS Outcome,
           'SKIP_PERMISSION' AS Code, N'ALTER ANY EVENT SESSION oder VIEW SERVER STATE fehlt' AS ObservedValue,
           N'XE-Verwaltung und -Leserechte' AS RequiredValue, N'Die begrenzte Ereignisevidenz kann nicht sicher eingerichtet werden.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';
    RETURN;
END;
SELECT 4 AS Sequence, 'PREFLIGHT' AS Phase, 'SUMMARY' AS CheckId, 'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Major=',@Major,N'; QueryStore=',@QueryStoreState) AS ObservedValue, N'markierter Adapterzustand' AS RequiredValue,
       N'Preflight bestanden; keine globale Konfiguration wurde geändert.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
