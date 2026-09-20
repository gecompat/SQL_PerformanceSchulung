/* Project-Adapter-Validierung fuer DGN-007 (Schnitt A). */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname=N'SQLPERF_LAB_DGN007_LOCAL';
DECLARE @Project nvarchar(128),@Contract nvarchar(32),@Demo varchar(7),@Run varchar(20),@Sql nvarchar(max);
DECLARE @QsState nvarchar(32),@QsCapture nvarchar(32),@QsInterval int,@QsMax int;

IF DB_ID(@TargetDatabase) IS NULL THROW 51002,'PROJECT_ASSERTION_FAILED: DGN-007-Datenbank fehlt.',1;
SET @Sql=N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),'
    +N'@Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),'
    +N'@Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),'
    +N'@Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) FROM '
    +QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@Project nvarchar(128) OUTPUT,@Contract nvarchar(32) OUTPUT,@Demo varchar(7) OUTPUT,@Run varchar(20) OUTPUT',@Project OUTPUT,@Contract OUTPUT,@Demo OUTPUT,@Run OUTPUT;
IF COALESCE(@Project,N'')<>N'SQL_PerformanceSchulung' OR COALESCE(@Contract,N'')<>N'1.0'
    OR COALESCE(@Demo,'')<>'DGN-007' OR COALESCE(@Run,'')<>'LOCAL'
    THROW 51002,'PROJECT_ASSERTION_FAILED: DGN-007-Eigentumsmarker stimmen nicht ueberein.',1;
IF (SELECT compatibility_level FROM sys.databases WHERE name=@TargetDatabase)<>170
    THROW 51002,'PROJECT_ASSERTION_FAILED: Compatibility Level 170 fehlt.',1;

SET @Sql=N'SELECT @QsState=actual_state_desc,@QsCapture=query_capture_mode_desc,@QsInterval=interval_length_minutes,@QsMax=max_storage_size_mb'
    +N' FROM '+QUOTENAME(@TargetDatabase)+N'.sys.database_query_store_options;'
EXEC sys.sp_executesql @Sql,N'@QsState nvarchar(32) OUTPUT,@QsCapture nvarchar(32) OUTPUT,@QsInterval int OUTPUT,@QsMax int OUTPUT',@QsState OUTPUT,@QsCapture OUTPUT,@QsInterval OUTPUT,@QsMax OUTPUT;
IF COALESCE(@QsState,N'')<>N'READ_WRITE'
    THROW 51002,'PROJECT_ASSERTION_FAILED: Query Store ist nicht READ_WRITE.',1;
IF @QsInterval IS NULL OR @QsInterval<>1 OR @QsMax IS NULL OR @QsMax<>128 OR COALESCE(@QsCapture,N'')<>N'ALL'
    THROW 51002,'PROJECT_ASSERTION_FAILED: Query-Store-Vertrag ist nicht auf das Schnitt-A-Profil gesetzt.',1;

SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';'
    +N'IF OBJECT_ID(N''dbo.usp_CaseSearch'',N''P'') IS NULL '
    +N'OR OBJECT_ID(N''lab.IncidentState'',N''U'') IS NULL '
    +N'OR OBJECT_ID(N''lab.IncidentQueryStoreProfile'',N''U'') IS NULL '
    +N'THROW 51002,''PROJECT_ASSERTION_FAILED: DGN-007-Incident- oder Baselinestatus ist ungueltig.'',1;';
EXEC sys.sp_executesql @Sql;

SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';
IF (SELECT COUNT(*) FROM dbo.CaseGroup) <> 12 OR (SELECT COUNT(*) FROM dbo.CaseItem) <> 24000
   OR (SELECT COUNT(*) FROM dbo.CaseItemDetail) <> 72000
   OR EXISTS (
       SELECT g.GroupKey FROM dbo.CaseGroup g LEFT JOIN dbo.CaseItem i ON i.GroupKey = g.GroupKey
       GROUP BY g.GroupKey HAVING g.GroupKey NOT BETWEEN 1 AND 12
       OR COUNT(i.ItemId) <> CASE WHEN g.GroupKey <= 4 THEN 4000 WHEN g.GroupKey <= 7 THEN 2000 ELSE 400 END)
    THROW 51002,''PROJECT_ASSERTION_FAILED: Die deterministische Gruppenverteilung ist unvollstaendig.'',1;
IF (SELECT COUNT(*) FROM lab.IncidentState) <> 2
   OR NOT EXISTS (SELECT 1 FROM lab.IncidentState WHERE IncidentPhase = N''T0_BASELINE'')
   OR NOT EXISTS (SELECT 1 FROM lab.IncidentState WHERE IncidentPhase = N''T1_INCIDENT'')
   OR EXISTS (SELECT 1 FROM lab.IncidentState WHERE CompletedUtc IS NULL OR CompletedUtc < MarkerUtc)
   OR EXISTS (
       SELECT 1 FROM lab.IncidentState b CROSS JOIN lab.IncidentState t
       WHERE b.IncidentPhase = N''T0_BASELINE'' AND t.IncidentPhase = N''T1_INCIDENT''
         AND b.CompletedUtc >= t.MarkerUtc)
    THROW 51002,''PROJECT_ASSERTION_FAILED: Die beiden persistierten Phasen fehlen oder ueberlappen.'',1;
IF EXISTS (
    SELECT s.IncidentPhase FROM lab.IncidentState s
    LEFT JOIN lab.IncidentQueryStoreProfile e ON e.IncidentPhase = s.IncidentPhase
    GROUP BY s.IncidentPhase
    HAVING COALESCE(SUM(e.CountExecutions),0) <> CASE s.IncidentPhase WHEN N''T0_BASELINE'' THEN 3 ELSE 5 END)
    THROW 51002,''PROJECT_ASSERTION_FAILED: Ein Phasenprofil ist unvollstaendig.'',1;

/* Die strenge Elternmenge bindet Objekt und Marker; PSP-Varianten liefern ihre Runtime unter Kind-Query-IDs. */
;WITH StrictParentQuery AS
(
    SELECT q.query_id
    FROM sys.query_store_query AS q
    JOIN sys.query_store_query_text AS qt ON qt.query_text_id = q.query_text_id
    WHERE q.object_id = OBJECT_ID(N''dbo.usp_CaseSearch'',N''P'')
      AND qt.query_sql_text LIKE N''%/* DGN007_CASE_SEARCH */%''
),
EffectiveQuery AS
(
    SELECT query_id FROM StrictParentQuery
    UNION
    SELECT qv.query_variant_query_id
    FROM sys.query_store_query_variant AS qv
    JOIN StrictParentQuery AS parent ON parent.query_id = qv.parent_query_id
)
SELECT q.query_id,p.plan_id,rs.runtime_stats_interval_id,SUM(rs.count_executions) AS CountExecutions,
       MIN(rs.first_execution_time) AS FirstExecutionUtc,MAX(rs.last_execution_time) AS LastExecutionUtc
INTO #SearchRuntime
FROM EffectiveQuery AS effective
JOIN sys.query_store_query AS q ON q.query_id=effective.query_id
JOIN sys.query_store_plan p ON p.query_id = q.query_id
JOIN sys.query_store_runtime_stats rs ON rs.plan_id = p.plan_id
WHERE rs.execution_type = 0 AND rs.count_executions > 0
GROUP BY q.query_id,p.plan_id,rs.runtime_stats_interval_id;
IF EXISTS (
    SELECT 1 FROM lab.IncidentQueryStoreProfile e
    JOIN lab.IncidentState s ON s.IncidentPhase = e.IncidentPhase
    LEFT JOIN #SearchRuntime r ON r.query_id = e.QueryId AND r.plan_id = e.PlanId
                             AND r.runtime_stats_interval_id = e.RuntimeStatsIntervalId
    LEFT JOIN sys.query_store_runtime_stats_interval i ON i.runtime_stats_interval_id = e.RuntimeStatsIntervalId
    WHERE r.query_id IS NULL OR i.runtime_stats_interval_id IS NULL
       OR e.CountExecutions <= 0 OR r.CountExecutions < e.CountExecutions
       OR i.end_time <= s.MarkerUtc OR i.start_time > s.CompletedUtc
       OR e.LastExecutionUtc < e.FirstExecutionUtc
       OR r.FirstExecutionUtc > e.FirstExecutionUtc OR r.LastExecutionUtc < e.LastExecutionUtc
       OR e.FirstExecutionUtc < i.start_time OR e.LastExecutionUtc > i.end_time)
    THROW 51002,''PROJECT_ASSERTION_FAILED: Query-Store-Profile gehoeren nicht zur markierten Suchprozedur oder zum Phasenfenster.'',1;
IF EXISTS (
    SELECT 1 FROM lab.IncidentQueryStoreProfile b
    JOIN sys.query_store_runtime_stats_interval bi ON bi.runtime_stats_interval_id = b.RuntimeStatsIntervalId
    CROSS JOIN lab.IncidentQueryStoreProfile t
    JOIN sys.query_store_runtime_stats_interval ti ON ti.runtime_stats_interval_id = t.RuntimeStatsIntervalId
    WHERE b.IncidentPhase = N''T0_BASELINE'' AND t.IncidentPhase = N''T1_INCIDENT''
      AND bi.end_time > ti.start_time)
    THROW 51002,''PROJECT_ASSERTION_FAILED: Baseline und Incident sind nicht durch Query-Store-Intervalle getrennt.'',1;';
EXEC sys.sp_executesql @Sql;

SELECT N'DGN-007' AS ScenarioId,N'VALIDATE' AS Phase,N'READY_FOR_USER' AS Outcome,
       @TargetDatabase AS TargetDatabase,@QsState AS QueryStoreState;
