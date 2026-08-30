/* Fachliche Adaptervalidierung fuer den reproduzierbaren CON-004-Ausgangszustand. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname = N'SQLPERF_LAB_CON004_LOCAL';
DECLARE @Project nvarchar(128), @Contract nvarchar(32), @Demo varchar(7), @Run varchar(20), @Sql nvarchar(max);

IF DB_ID(@TargetDatabase) IS NULL
    THROW 51002, 'PROJECT_ASSERTION_FAILED: CON-004-Datenbank fehlt.', 1;

SET @Sql = N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),'
    + N'@Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),'
    + N'@Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),'
    + N'@Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) '
    + N'FROM ' + QUOTENAME(@TargetDatabase) + N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,
    N'@Project nvarchar(128) OUTPUT,@Contract nvarchar(32) OUTPUT,@Demo varchar(7) OUTPUT,@Run varchar(20) OUTPUT',
    @Project OUTPUT, @Contract OUTPUT, @Demo OUTPUT, @Run OUTPUT;
IF @Project <> N'SQL_PerformanceSchulung' OR @Contract <> N'1.0' OR @Demo <> 'CON-004' OR @Run <> 'LOCAL'
    THROW 51002, 'PROJECT_ASSERTION_FAILED: CON-004-Eigentumsmarker stimmen nicht ueberein.', 1;
IF (SELECT compatibility_level FROM sys.databases WHERE name = @TargetDatabase) <> 170
    THROW 51002, 'PROJECT_ASSERTION_FAILED: Compatibility Level 170 fehlt.', 1;
GO
USE [SQLPERF_LAB_CON004_LOCAL];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF OBJECT_ID(N'lab.BlockingDemo', N'U') IS NULL
   OR OBJECT_ID(N'lab.BlockingEvidence', N'U') IS NULL
   OR OBJECT_ID(N'fwk.SessionSignal', N'U') IS NULL
   OR OBJECT_ID(N'fwk.USP_Signal', N'P') IS NULL
   OR OBJECT_ID(N'fwk.USP_WaitForSignal', N'P') IS NULL
   OR OBJECT_ID(N'fwk.USP_ClearSignals', N'P') IS NULL
    THROW 51002, 'PROJECT_ASSERTION_FAILED: CON-004-Objektvertrag ist unvollstaendig.', 1;
IF (SELECT COUNT(*) FROM lab.BlockingDemo) <> 2 OR EXISTS (SELECT 1 FROM lab.BlockingDemo WHERE Value <> 0)
    THROW 51002, 'PROJECT_ASSERTION_FAILED: CON-004-Baselinedaten sind ungueltig.', 1;
IF EXISTS (SELECT 1 FROM lab.BlockingEvidence) OR EXISTS (SELECT 1 FROM fwk.SessionSignal)
    THROW 51002, 'PROJECT_ASSERTION_FAILED: Alte CON-004-Evidenz oder Signale sind vorhanden.', 1;
IF EXISTS (SELECT 1 FROM sys.dm_exec_requests WHERE database_id = DB_ID() AND blocking_session_id <> 0)
    THROW 51002, 'PROJECT_ASSERTION_FAILED: Die CON-004-Datenbank ist vor der Uebergabe blockiert.', 1;

SELECT N'CON-004' AS ScenarioId, N'VALIDATE' AS Phase, N'READY_FOR_USER' AS Outcome,
       DB_NAME() AS TargetDatabase, (SELECT COUNT(*) FROM lab.BlockingDemo) AS PreparedRows;
GO
