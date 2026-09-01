/* Project-Adapter-Validierung fuer DGN-005. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname=N'SQLPERF_LAB_DGN005_LOCAL', @SessionName sysname=N'SQLPERF_DGN005_LOCAL';
DECLARE @Project nvarchar(128),@Contract nvarchar(32),@Demo varchar(7),@Run varchar(20),@Sql nvarchar(max);
IF DB_ID(@TargetDatabase) IS NULL THROW 51002,'PROJECT_ASSERTION_FAILED: DGN-005-Datenbank fehlt.',1;
SET @Sql=N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),'
    +N'@Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),'
    +N'@Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),'
    +N'@Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) FROM '
    +QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@Project nvarchar(128) OUTPUT,@Contract nvarchar(32) OUTPUT,@Demo varchar(7) OUTPUT,@Run varchar(20) OUTPUT',@Project OUTPUT,@Contract OUTPUT,@Demo OUTPUT,@Run OUTPUT;
IF @Project<>N'SQL_PerformanceSchulung' OR @Contract<>N'1.0' OR @Demo<>'DGN-005' OR @Run<>'LOCAL'
    THROW 51002,'PROJECT_ASSERTION_FAILED: DGN-005-Eigentumsmarker stimmen nicht ueberein.',1;
IF (SELECT compatibility_level FROM sys.databases WHERE name=@TargetDatabase)<>170
    THROW 51002,'PROJECT_ASSERTION_FAILED: Compatibility Level 170 fehlt.',1;
IF NOT EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=@SessionName AND startup_state=0)
    THROW 51002,'PROJECT_ASSERTION_FAILED: Begrenzte DGN-005-Event-Session fehlt.',1;
IF NOT EXISTS (SELECT 1 FROM sys.dm_xe_sessions WHERE name=@SessionName)
    THROW 51002,'PROJECT_ASSERTION_FAILED: DGN-005-Event-Session laeuft nicht.',1;
IF NOT EXISTS (SELECT 1 FROM sys.server_event_session_targets t JOIN sys.server_event_sessions s ON s.event_session_id=t.event_session_id WHERE s.name=@SessionName AND t.name=N'ring_buffer')
    THROW 51002,'PROJECT_ASSERTION_FAILED: DGN-005-Ring-Buffer fehlt.',1;
SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';'
    +N'IF OBJECT_ID(N''lab.XeEvidence'',N''U'') IS NULL OR (SELECT COUNT(*) FROM lab.XeEvidence)<>1 '
    +N'OR EXISTS(SELECT 1 FROM lab.XeEvidence WHERE EventCount IS NOT NULL OR SessionStopped<>0) '
    +N'THROW 51002,''PROJECT_ASSERTION_FAILED: DGN-005-Baselineobjekt ist ungueltig.'',1;';
EXEC sys.sp_executesql @Sql;

SELECT N'DGN-005' AS ScenarioId,N'VALIDATE' AS Phase,N'READY_FOR_USER' AS Outcome,
       @TargetDatabase AS TargetDatabase,@SessionName AS EventSession;
