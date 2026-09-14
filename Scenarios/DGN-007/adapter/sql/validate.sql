/* Project-Adapter-Validierung fuer DGN-007 (Schnitt A). */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname=N'SQLPERF_LAB_DGN007_LOCAL';
DECLARE @Project nvarchar(128),@Contract nvarchar(32),@Demo varchar(7),@Run varchar(20),@Sql nvarchar(max);
DECLARE @QsState nvarchar(32),@QsInterval int,@QsMax int,@ItemRows int,@QsQueries int;

IF DB_ID(@TargetDatabase) IS NULL THROW 51002,'PROJECT_ASSERTION_FAILED: DGN-007-Datenbank fehlt.',1;
SET @Sql=N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),'
    +N'@Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),'
    +N'@Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),'
    +N'@Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) FROM '
    +QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@Project nvarchar(128) OUTPUT,@Contract nvarchar(32) OUTPUT,@Demo varchar(7) OUTPUT,@Run varchar(20) OUTPUT',@Project OUTPUT,@Contract OUTPUT,@Demo OUTPUT,@Run OUTPUT;
IF @Project<>N'SQL_PerformanceSchulung' OR @Contract<>N'1.0' OR @Demo<>'DGN-007' OR @Run<>'LOCAL'
    THROW 51002,'PROJECT_ASSERTION_FAILED: DGN-007-Eigentumsmarker stimmen nicht ueberein.',1;
IF (SELECT compatibility_level FROM sys.databases WHERE name=@TargetDatabase)<>170
    THROW 51002,'PROJECT_ASSERTION_FAILED: Compatibility Level 170 fehlt.',1;

SET @Sql=N'SELECT @QsState=actual_state_desc,@QsInterval=interval_length_minutes,@QsMax=max_storage_size_mb'
    +N' FROM '+QUOTENAME(@TargetDatabase)+N'.sys.database_query_store_options;'
EXEC sys.sp_executesql @Sql,N'@QsState nvarchar(32) OUTPUT,@QsInterval int OUTPUT,@QsMax int OUTPUT',@QsState OUTPUT,@QsInterval OUTPUT,@QsMax OUTPUT;
IF @QsState<>N'READ_WRITE'
    THROW 51002,'PROJECT_ASSERTION_FAILED: Query Store ist nicht READ_WRITE.',1;
IF @QsInterval IS NULL OR @QsInterval<>1 OR @QsMax IS NULL OR @QsMax<>128
    THROW 51002,'PROJECT_ASSERTION_FAILED: Query-Store-Vertrag ist nicht auf das Schnitt-A-Profil gesetzt.',1;

SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';'
    +N'SELECT @ItemRows=COUNT(*) FROM dbo.CaseItem;'
    +N'SELECT @QsQueries=COUNT(DISTINCT q.query_id) FROM sys.query_store_query q;';
EXEC sys.sp_executesql @Sql,N'@ItemRows int OUTPUT,@QsQueries int OUTPUT',@ItemRows OUTPUT,@QsQueries OUTPUT;
IF @ItemRows IS NULL OR @ItemRows<>24000
    THROW 51002,'PROJECT_ASSERTION_FAILED: Das Capstone-Datenmodell ist unvollständig.',1;
IF @QsQueries IS NULL OR @QsQueries<1
    THROW 51002,'PROJECT_ASSERTION_FAILED: Query Store erfasst keine markierten Abfragen.',1;
SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';'
    +N'IF OBJECT_ID(N''dbo.usp_CaseSearch'',N''P'') IS NULL '
    +N'OR OBJECT_ID(N''lab.IncidentState'',N''U'') IS NULL '
    +N'OR (SELECT COUNT(*) FROM lab.IncidentState)<>1 '
    +N'OR (SELECT IncidentPhase FROM lab.IncidentState) NOT IN (N''T0_BASELINE'',N''T1_INCIDENT'') '
    +N'OR NOT EXISTS(SELECT 1 FROM sys.query_store_runtime_stats) '
    +N'THROW 51002,''PROJECT_ASSERTION_FAILED: DGN-007-Incident- oder Baselinestatus ist ungueltig.'',1;';
EXEC sys.sp_executesql @Sql;

SELECT N'DGN-007' AS ScenarioId,N'VALIDATE' AS Phase,N'READY_FOR_USER' AS Outcome,
       @TargetDatabase AS TargetDatabase,@QsState AS QueryStoreState;