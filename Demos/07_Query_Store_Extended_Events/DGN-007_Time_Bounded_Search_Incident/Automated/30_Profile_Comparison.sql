/* DGN-007_PROFILE_COMPARISON: neutraler Vergleich vorhandener Capture-Profile.
   Primärquellen: Microsoft Learn sys.query_store_runtime_stats,
   sys.query_store_query_variant, sys.query_store_query_hints; geprüft 2026-10-06.
   Keine zusätzlichen Suchrequests oder direkten Lab-/Konfigurationsänderungen.
   Capture ALL kann die Beobachtungsqueries selbst erfassen. Vergleichsevidenz;
   keine Regression, Incidentreproduktion oder Ursachenbewertung. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 5000;
DECLARE @PhaseDeadline datetime2(7)=DATEADD(second,8,SYSUTCDATETIME());
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
DECLARE @EditionId int=TRY_CONVERT(int,SERVERPROPERTY('EditionID'));
DECLARE @ActualCompatibility int=(SELECT compatibility_level FROM sys.databases WHERE database_id=DB_ID());
IF '$(DemoId)'<>'DGN-007' OR '$(RunToken)'<>'AUTO'
   OR N'$(TargetDatabase)'<>N'SQLPERF_LAB_DGN007_AUTO'
   OR DB_NAME()<>N'SQLPERF_LAB_DGN007_AUTO'
    THROW 51000,'FAIL_CONTRACT: Unerwartetes Ziel des Profilvergleichs.',1;
IF '$(ConfirmIsolatedLab)'<>'1' OR '$(HighImpactConfirmed)'<>'1'
   OR COALESCE(TRY_CONVERT(int,'$(MaximumRuntimeSeconds)'),0) NOT BETWEEN 1 AND 180
   OR @Major IS NULL OR @Major NOT IN (15,16,17)
   OR @EditionId IS NULL OR @EditionId NOT IN (-2117995310,-1785266663)
   OR @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2
    THROW 51001,'FAIL_SAFETY: Bestätigte Developer-Wegwerfinstanz und begrenztes Budget erforderlich.',1;
IF @ActualCompatibility IS NULL
   OR @ActualCompatibility<>CASE @Major WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END
    THROW 51000,'FAIL_CONTRACT: Compatibility Level entspricht nicht der Zielversion.',1;
IF EXISTS(SELECT 1 FROM sys.databases WHERE database_id>4 AND database_id<>DB_ID())
   OR NOT EXISTS(SELECT 1 FROM sys.databases WHERE database_id=DB_ID() AND database_id>4 AND state_desc=N'ONLINE')
    THROW 51001,'FAIL_SAFETY: Isolierte eigene Datenbank ohne Fremddatenbanken erforderlich.',1;

/* Vier vollständige Marker vor Zugriff auf die persistierte Labevidenz. */
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@Demo nvarchar(max),@Run nvarchar(max);
SELECT @Project=MAX(CASE WHEN name=N'SQLPERF.Project' THEN CONVERT(nvarchar(max),value) END),
       @Contract=MAX(CASE WHEN name=N'SQLPERF.ContractVersion' THEN CONVERT(nvarchar(max),value) END),
       @Demo=MAX(CASE WHEN name=N'SQLPERF.DemoId' THEN CONVERT(nvarchar(max),value) END),
       @Run=MAX(CASE WHEN name=N'SQLPERF.RunToken' THEN CONVERT(nvarchar(max),value) END)
FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;
IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
   OR @Demo IS NULL OR @Demo COLLATE Latin1_General_100_BIN2<>N'DGN-007' OR DATALENGTH(@Demo)<>DATALENGTH(N'DGN-007')
   OR @Run IS NULL OR @Run COLLATE Latin1_General_100_BIN2<>N'AUTO' OR DATALENGTH(@Run)<>DATALENGTH(N'AUTO')
    THROW 51001,'FAIL_SAFETY: Eigentumsmarker fehlen oder weichen ab.',1;
DECLARE @ObjectId int=OBJECT_ID(N'dbo.usp_CaseSearch',N'P');
IF @ObjectId IS NULL OR OBJECT_DEFINITION(@ObjectId) IS NULL
   OR CHARINDEX(N'/* DGN007_CASE_SEARCH */',OBJECT_DEFINITION(@ObjectId) COLLATE Latin1_General_100_BIN2)=0
   OR OBJECT_ID(N'lab.IncidentState',N'U') IS NULL
   OR OBJECT_ID(N'lab.IncidentProfile',N'U') IS NULL
   OR OBJECT_ID(N'dbo.CaseRequestLog',N'U') IS NULL
    THROW 51002,'FAIL_STATE: Markierter Fenster- und Profilzustand fehlt.',1;
IF NOT EXISTS(SELECT 1 FROM sys.database_query_store_options
              WHERE actual_state=2 AND desired_state=2 AND query_capture_mode=1
                AND max_storage_size_mb=128 AND interval_length_minutes=1 AND flush_interval_seconds=60)
    THROW 51002,'FAIL_STATE: Begrenzter Query Store ist nicht aktiv.',1;

/* DGN007_PROFILE_WINDOW_GUARD_BEGIN */
IF (SELECT COUNT_BIG(*) FROM lab.IncidentState)<>2
   OR EXISTS(SELECT 1 FROM lab.IncidentState
             WHERE WindowId IS NULL OR WindowId NOT IN (0,1)
                OR RequestCount IS NULL OR RequestCount<>4
                OR CapturedExecutions IS NULL OR CapturedExecutions<>4
                OR RuntimeStatsIntervalId IS NULL OR IntervalStart IS NULL OR IntervalEnd IS NULL
                OR IntervalStart>=IntervalEnd OR ExecutionStarted IS NULL OR ExecutionFinished IS NULL
                OR ExecutionStarted<IntervalStart OR ExecutionFinished<ExecutionStarted OR ExecutionFinished>=IntervalEnd
                OR FirstRequestLogId IS NULL OR LastRequestLogId IS NULL OR FirstRequestLogId>LastRequestLogId)
   OR NOT EXISTS(SELECT 1 FROM lab.IncidentState a JOIN lab.IncidentState b ON a.WindowId=0 AND b.WindowId=1
                 WHERE a.RuntimeStatsIntervalId<>b.RuntimeStatsIntervalId AND a.IntervalEnd<=b.IntervalStart
                   AND a.LastRequestLogId<b.FirstRequestLogId)
   OR EXISTS(SELECT 1 FROM lab.IncidentState w
             LEFT JOIN sys.query_store_runtime_stats_interval i ON i.runtime_stats_interval_id=w.RuntimeStatsIntervalId
             WHERE i.runtime_stats_interval_id IS NULL OR i.start_time<>w.IntervalStart OR i.end_time<>w.IntervalEnd)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* DGN007_PROFILE_WINDOW_GUARD_END */

CREATE TABLE #ExpectedParameters(GroupKey int NOT NULL,StatusCode tinyint NOT NULL,PRIMARY KEY(GroupKey,StatusCode));
INSERT #ExpectedParameters VALUES(8,3),(1,3),(5,3),(1,1);
/* DGN007_PROFILE_REQUEST_GUARD_BEGIN */
IF (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>12
   OR EXISTS(SELECT 1 FROM lab.IncidentState w
             WHERE (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog r
                    WHERE r.RequestLogId BETWEEN w.FirstRequestLogId AND w.LastRequestLogId)<>4)
   OR EXISTS(SELECT w.WindowId,r.GroupKey,r.StatusCode FROM lab.IncidentState w
             JOIN dbo.CaseRequestLog r ON r.RequestLogId BETWEEN w.FirstRequestLogId AND w.LastRequestLogId
             GROUP BY w.WindowId,r.GroupKey,r.StatusCode HAVING COUNT_BIG(*)<>1)
   OR EXISTS(SELECT w.WindowId,r.GroupKey,r.StatusCode FROM lab.IncidentState w
             JOIN dbo.CaseRequestLog r ON r.RequestLogId BETWEEN w.FirstRequestLogId AND w.LastRequestLogId
             EXCEPT SELECT w.WindowId,p.GroupKey,p.StatusCode FROM lab.IncidentState w CROSS JOIN #ExpectedParameters p)
   OR EXISTS(SELECT w.WindowId,p.GroupKey,p.StatusCode FROM lab.IncidentState w CROSS JOIN #ExpectedParameters p
             EXCEPT SELECT w.WindowId,r.GroupKey,r.StatusCode FROM lab.IncidentState w
             JOIN dbo.CaseRequestLog r ON r.RequestLogId BETWEEN w.FirstRequestLogId AND w.LastRequestLogId)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* DGN007_PROFILE_REQUEST_GUARD_END */

CREATE TABLE #ParentQueries(QueryId bigint NOT NULL PRIMARY KEY);
CREATE TABLE #ScopedQueries(QueryId bigint NOT NULL PRIMARY KEY,ParentQueryId bigint NOT NULL);
INSERT #ParentQueries(QueryId)
SELECT q.query_id FROM sys.query_store_query q JOIN sys.query_store_query_text t ON t.query_text_id=q.query_text_id
WHERE q.object_id=@ObjectId
  AND CHARINDEX(N'/* DGN007_CASE_SEARCH */',t.query_sql_text COLLATE Latin1_General_100_BIN2)>0;
/* Neuere Katalogsichten werden auf 2019 nicht statisch gebunden. */
IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_variant',N'V') IS NOT NULL
    EXEC sys.sp_executesql N'DELETE p FROM #ParentQueries p JOIN sys.query_store_query_variant v ON v.query_variant_query_id=p.QueryId;';
INSERT #ScopedQueries(QueryId,ParentQueryId) SELECT QueryId,QueryId FROM #ParentQueries;
IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_variant',N'V') IS NOT NULL
    EXEC sys.sp_executesql N'
        INSERT #ScopedQueries(QueryId,ParentQueryId)
        SELECT DISTINCT v.query_variant_query_id,v.parent_query_id
        FROM sys.query_store_query_variant v JOIN #ParentQueries p ON p.QueryId=v.parent_query_id
        WHERE NOT EXISTS(SELECT 1 FROM #ScopedQueries s WHERE s.QueryId=v.query_variant_query_id);';

/* DGN007_PROFILE_METRIC_GUARD_BEGIN */
IF EXISTS(SELECT 1 FROM lab.IncidentProfile p
          LEFT JOIN lab.IncidentState w ON w.WindowId=p.WindowId
          LEFT JOIN #ScopedQueries s ON s.QueryId=p.QueryId AND s.ParentQueryId=p.ParentQueryId
          LEFT JOIN sys.query_store_plan q ON q.plan_id=p.PlanId AND q.query_id=p.QueryId
          WHERE w.WindowId IS NULL OR s.QueryId IS NULL OR q.plan_id IS NULL
             OR p.RuntimeStatsIntervalId IS NULL OR p.RuntimeStatsIntervalId<>w.RuntimeStatsIntervalId
             OR p.ExecutionType IS NULL OR p.ExecutionType<>0 OR p.ExecutionCount IS NULL OR p.ExecutionCount<=0
             OR p.AvgDurationUs IS NULL OR p.AvgDurationUs<0 OR p.AvgCpuUs IS NULL OR p.AvgCpuUs<0
             OR p.AvgLogicalReads IS NULL OR p.AvgLogicalReads<0 OR p.AvgRowCount IS NULL OR p.AvgRowCount<0
             OR p.FirstExecutionTime IS NULL OR p.LastExecutionTime IS NULL
             OR p.FirstExecutionTime<w.IntervalStart OR p.LastExecutionTime>=w.IntervalEnd
             OR p.LastExecutionTime<p.FirstExecutionTime)
   OR EXISTS(SELECT 1 FROM lab.IncidentState w
             WHERE COALESCE((SELECT SUM(p.ExecutionCount) FROM lab.IncidentProfile p WHERE p.WindowId=w.WindowId),0)<>4)
   OR EXISTS(SELECT 1 FROM lab.IncidentProfile GROUP BY WindowId,PlanId,RuntimeStatsIntervalId,ExecutionType HAVING COUNT_BIG(*)<>1)
   OR EXISTS(SELECT ParentQueryId FROM lab.IncidentProfile WHERE WindowId=0
             EXCEPT SELECT ParentQueryId FROM lab.IncidentProfile WHERE WindowId=1)
   OR EXISTS(SELECT ParentQueryId FROM lab.IncidentProfile WHERE WindowId=1
             EXCEPT SELECT ParentQueryId FROM lab.IncidentProfile WHERE WindowId=0)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* DGN007_PROFILE_METRIC_GUARD_END */

IF EXISTS(SELECT 1 FROM #ScopedQueries s JOIN sys.query_store_plan p ON p.query_id=s.QueryId WHERE p.is_forced_plan IS NULL OR p.is_forced_plan<>0)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_hints',N'V') IS NOT NULL
    EXEC sys.sp_executesql N'
        IF EXISTS(SELECT 1 FROM sys.query_store_query_hints h JOIN #ScopedQueries s ON s.QueryId=h.query_id)
            THROW 51002,''FAIL_STATE: Query-Store-Hints im eigenen Queryscope sind unzulässig.'',1;';

/* Live-Capture gegen IDs, Counts und Grenzen prüfen, ohne Ausführung oder Flush.
   Disk- und In-Memory-Zeilen nach Plan/Intervall/ExecutionType aggregieren. */
IF EXISTS(SELECT 1 FROM #ScopedQueries s JOIN sys.query_store_plan p ON p.query_id=s.QueryId
          JOIN sys.query_store_runtime_stats r ON r.plan_id=p.plan_id
          JOIN lab.IncidentState w ON w.RuntimeStatsIntervalId=r.runtime_stats_interval_id
          WHERE r.count_executions>0 AND (r.execution_type IS NULL OR r.execution_type<>0
             OR r.avg_duration IS NULL OR r.avg_duration<0 OR r.avg_cpu_time IS NULL OR r.avg_cpu_time<0
             OR r.avg_logical_io_reads IS NULL OR r.avg_logical_io_reads<0 OR r.avg_rowcount IS NULL OR r.avg_rowcount<0))
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
SELECT w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id AS PlanId,r.runtime_stats_interval_id AS RuntimeStatsIntervalId,
       r.execution_type AS ExecutionType,SUM(r.count_executions) AS ExecutionCount,
       MIN(r.first_execution_time) AS FirstExecutionTime,MAX(r.last_execution_time) AS LastExecutionTime
INTO #LiveRuntime
FROM #ScopedQueries s JOIN sys.query_store_plan p ON p.query_id=s.QueryId
JOIN sys.query_store_runtime_stats r ON r.plan_id=p.plan_id
JOIN lab.IncidentState w ON w.RuntimeStatsIntervalId=r.runtime_stats_interval_id
WHERE r.execution_type=0
GROUP BY w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id,r.runtime_stats_interval_id,r.execution_type
HAVING SUM(r.count_executions)>0;
IF EXISTS(SELECT WindowId,ParentQueryId,QueryId,PlanId,RuntimeStatsIntervalId,ExecutionType,ExecutionCount,FirstExecutionTime,LastExecutionTime
          FROM lab.IncidentProfile
          EXCEPT SELECT WindowId,ParentQueryId,QueryId,PlanId,RuntimeStatsIntervalId,ExecutionType,ExecutionCount,FirstExecutionTime,LastExecutionTime FROM #LiveRuntime)
   OR EXISTS(SELECT WindowId,ParentQueryId,QueryId,PlanId,RuntimeStatsIntervalId,ExecutionType,ExecutionCount,FirstExecutionTime,LastExecutionTime
             FROM #LiveRuntime
             EXCEPT SELECT WindowId,ParentQueryId,QueryId,PlanId,RuntimeStatsIntervalId,ExecutionType,ExecutionCount,FirstExecutionTime,LastExecutionTime FROM lab.IncidentProfile)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;

/* DGN007_PROFILE_WEIGHTED_BEGIN */
SELECT WindowId,SUM(ExecutionCount) AS ExecutionCount,COUNT(DISTINCT PlanId) AS ObservedPlanCount,
       SUM(ExecutionCount*AvgDurationUs)/NULLIF(SUM(ExecutionCount),0) AS AvgDurationUs,
       SUM(ExecutionCount*AvgCpuUs)/NULLIF(SUM(ExecutionCount),0) AS AvgCpuUs,
       SUM(ExecutionCount*AvgLogicalReads)/NULLIF(SUM(ExecutionCount),0) AS AvgLogicalReads,
       SUM(ExecutionCount*AvgRowCount)/NULLIF(SUM(ExecutionCount),0) AS AvgRowCount,
       SUM(ExecutionCount*AvgRowCount) AS TotalRows
INTO #WindowTotals
FROM lab.IncidentProfile
GROUP BY WindowId;
/* DGN007_PROFILE_WEIGHTED_END */
/* Toleranz ausschließlich für Rundung der float-Aggregation, keine Lasttoleranz. */
/* DGN007_PROFILE_TOTALS_GUARD_BEGIN */
IF (SELECT COUNT_BIG(*) FROM #WindowTotals)<>2
   OR EXISTS(SELECT 1 FROM #WindowTotals WHERE ExecutionCount<>4 OR TotalRows IS NULL OR ABS(TotalRows-4229.0)>0.000001)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* DGN007_PROFILE_TOTALS_GUARD_END */
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;

SELECT N'DGN007_PROFILE_WINDOW' AS ReportKind,WindowId,ExecutionCount,ObservedPlanCount,
       AvgDurationUs,AvgCpuUs,AvgLogicalReads,AvgRowCount,TotalRows
FROM #WindowTotals ORDER BY WindowId;
/* DGN007_PROFILE_DELTA_BEGIN */
;WITH MetricWindow AS
(
    SELECT WindowId,'DurationUs' AS MetricName,AvgDurationUs AS MetricValue FROM #WindowTotals
    UNION ALL SELECT WindowId,'CpuUs',AvgCpuUs FROM #WindowTotals
    UNION ALL SELECT WindowId,'LogicalReads',AvgLogicalReads FROM #WindowTotals
    UNION ALL SELECT WindowId,'Rows',AvgRowCount FROM #WindowTotals
)
SELECT 'DGN007_PROFILE_METRIC' AS ReportKind,a.MetricName,a.MetricValue AS T0,b.MetricValue AS T1,
       b.MetricValue-a.MetricValue AS DeltaT1MinusT0,
       b.MetricValue/NULLIF(a.MetricValue,0) AS RatioT1ToT0,
       CASE WHEN a.MetricValue=0 THEN 1 ELSE 0 END AS BaselineZero
FROM MetricWindow a JOIN MetricWindow b ON b.MetricName=a.MetricName AND a.WindowId=0 AND b.WindowId=1
ORDER BY a.MetricName;
/* DGN007_PROFILE_DELTA_END */
SELECT N'DGN007_PROFILE_SCOPE' AS ReportKind,N'Vergleichsevidenz; keine Regression' AS ScopeMessage;
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
