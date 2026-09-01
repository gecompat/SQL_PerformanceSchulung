/* Markergebundener Project-Adapter-Cleanup fuer DGN-005. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname=N'SQLPERF_LAB_DGN005_LOCAL',@SessionName sysname=N'SQLPERF_DGN005_LOCAL';
DECLARE @Project nvarchar(128),@Contract nvarchar(32),@Demo varchar(7),@Run varchar(20),@Sql nvarchar(max);
IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=@SessionName)
        THROW 51004,'PROJECT_CLEANUP_FAILED: Event Session ohne markergebundene DGN-005-Datenbank wird nicht uebernommen.',1;
    SELECT N'DGN-005' AS ScenarioId,N'CLEANUP' AS Phase,N'PASS' AS Outcome,N'ALREADY_ABSENT' AS Code;
    RETURN;
END;
SET @Sql=N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),'
    +N'@Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),'
    +N'@Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),'
    +N'@Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) FROM '
    +QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@Project nvarchar(128) OUTPUT,@Contract nvarchar(32) OUTPUT,@Demo varchar(7) OUTPUT,@Run varchar(20) OUTPUT',@Project OUTPUT,@Contract OUTPUT,@Demo OUTPUT,@Run OUTPUT;
IF @Project<>N'SQL_PerformanceSchulung' OR @Contract<>N'1.0' OR @Demo<>'DGN-005' OR @Run<>'LOCAL'
    THROW 51004,'PROJECT_CLEANUP_FAILED: DGN-005-Eigentumsmarker stimmen nicht ueberein.',1;
IF EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=@SessionName)
BEGIN SET @Sql=N'ALTER EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER STATE=STOP;'; EXEC sys.sp_executesql @Sql; END;
IF EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=@SessionName)
BEGIN SET @Sql=N'DROP EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER;'; EXEC sys.sp_executesql @Sql; END;
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE '+QUOTENAME(@TargetDatabase)+N';';
EXEC sys.sp_executesql @Sql;
SELECT N'DGN-005' AS ScenarioId,N'CLEANUP' AS Phase,N'PASS' AS Outcome,N'SESSION_AND_DATABASE_REMOVED' AS Code;
