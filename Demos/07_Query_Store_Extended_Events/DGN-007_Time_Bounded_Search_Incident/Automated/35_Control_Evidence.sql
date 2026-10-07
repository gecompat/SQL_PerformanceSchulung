/* DGN-007_CONTROL_EVIDENCE: read-only Kontrolle realer Reihenfolge und ausgeführter Planmengen.
   Microsoft Learn sys.query_store_plan und sys.query_store_runtime_stats,
   geprüft am 2026-10-07. Kein Incident-, Richtungs- oder Ursachenvertrag.
   Query Store ALL kann die Beobachtungsqueries erfassen; keine zusätzlichen Suchrequests. */
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
    THROW 51000,'FAIL_CONTRACT: Unerwartetes Ziel der Kontrollevidenz.',1;
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
   /* CAPTURE_REQUIRED_GUARD_BEGIN */
   OR OBJECT_ID(N'lab.RequestResultCapture',N'U') IS NULL
   /* CAPTURE_REQUIRED_GUARD_END */
    THROW 51002,'FAIL_STATE: Markierter Fenster- und Profilzustand fehlt.',1;
IF NOT EXISTS(SELECT 1 FROM sys.database_query_store_options
              WHERE actual_state=2 AND desired_state=2 AND query_capture_mode=1
                AND max_storage_size_mb=128 AND interval_length_minutes=1 AND flush_interval_seconds=60)
    THROW 51002,'FAIL_STATE: Begrenzter Query Store ist nicht aktiv.',1;

/* CONTROL_SEQUENCE_GUARD_BEGIN */
IF OBJECT_ID(N'lab.ControlSequence',N'U') IS NULL
    THROW 51002,'FAIL_STATE: Kontrollkonfiguration fehlt.',1;
IF (SELECT COUNT_BIG(*) FROM lab.ControlSequence)<>2
   OR EXISTS(SELECT 1 FROM lab.ControlSequence
             WHERE WindowId IS NULL OR WindowId NOT IN (0,1)
                OR ConditionCode IS NULL OR ConditionCode COLLATE Latin1_General_100_BIN2 NOT IN ('A','B')
                OR DATALENGTH(ConditionCode)<>1)
   OR NOT EXISTS(SELECT 1 FROM lab.ControlSequence WHERE WindowId=0)
   OR NOT EXISTS(SELECT 1 FROM lab.ControlSequence WHERE WindowId=1)
   OR EXISTS(SELECT 1 FROM lab.ControlSequence a JOIN lab.ControlSequence b ON a.WindowId=0 AND b.WindowId=1
             WHERE a.ConditionCode='B' AND b.ConditionCode='B')
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* CONTROL_SEQUENCE_GUARD_END */

/* DGN007_CONTROL_WINDOW_GUARD_BEGIN */
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
/* DGN007_CONTROL_WINDOW_GUARD_END */

CREATE TABLE #ExpectedParameters(GroupKey int NOT NULL,StatusCode tinyint NOT NULL,PRIMARY KEY(GroupKey,StatusCode));
INSERT #ExpectedParameters VALUES(8,3),(1,3),(5,3),(1,1);
/* DGN007_CONTROL_REQUEST_GUARD_BEGIN */
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
/* DGN007_CONTROL_REQUEST_GUARD_END */

/* CONTROL_PARAMETERS_BEGIN */
CREATE TABLE #Parameters(WindowId tinyint NOT NULL,Sequence int NOT NULL,GroupKey int NOT NULL,StatusCode tinyint NOT NULL,ExpectedCount int NOT NULL,PRIMARY KEY(WindowId,Sequence));
INSERT #Parameters(WindowId,Sequence,GroupKey,StatusCode,ExpectedCount)
SELECT c.WindowId,p.Sequence,p.GroupKey,p.StatusCode,p.ExpectedCount
FROM lab.ControlSequence c JOIN
 (VALUES('A',1,8,3,228),('A',2,1,3,2286),('A',3,5,3,1144),('A',4,1,1,571),
        ('B',1,1,3,2286),('B',2,8,3,228),('B',3,5,3,1144),('B',4,1,1,571))
 p(ConditionCode,Sequence,GroupKey,StatusCode,ExpectedCount) ON p.ConditionCode=c.ConditionCode;
/* CONTROL_PARAMETERS_END */
/* CONTROL_ORDER_ROWS_BEGIN */
SELECT w.WindowId,ROW_NUMBER() OVER(PARTITION BY w.WindowId ORDER BY r.RequestLogId) AS Sequence,
       r.GroupKey,r.StatusCode
INTO #OrderedRequests
FROM lab.IncidentState w JOIN dbo.CaseRequestLog r
  ON r.RequestLogId BETWEEN w.FirstRequestLogId AND w.LastRequestLogId;
/* CONTROL_ORDER_ROWS_END */
/* CONTROL_ORDER_GUARD_BEGIN */
IF EXISTS(SELECT WindowId,Sequence,GroupKey,StatusCode FROM #OrderedRequests
          EXCEPT SELECT WindowId,Sequence,GroupKey,StatusCode FROM #Parameters)
   OR EXISTS(SELECT WindowId,Sequence,GroupKey,StatusCode FROM #Parameters
             EXCEPT SELECT WindowId,Sequence,GroupKey,StatusCode FROM #OrderedRequests)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* CONTROL_ORDER_GUARD_END */

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

/* DGN007_CONTROL_METRIC_GUARD_BEGIN */
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
/* DGN007_CONTROL_METRIC_GUARD_END */

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

/* Hashes ergänzen die Plan-ID, sind kein Gleichheits- oder Ursachenbeweis.
   Ausschließlich ausgeführte positive reguläre Profile zählen als aktive Pläne;
   ungenutzte historische Pläne und Dispatcher kommen nicht in diese Menge. */
/* CONTROL_HASH_GUARD_BEGIN */
IF EXISTS(SELECT 1 FROM lab.IncidentProfile p
          JOIN sys.query_store_plan q ON q.plan_id=p.PlanId AND q.query_id=p.QueryId
          WHERE q.query_plan_hash IS NULL OR DATALENGTH(q.query_plan_hash)<>8)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* CONTROL_HASH_GUARD_END */
/* CONTROL_ACTIVE_PLANS_BEGIN */
SELECT p.WindowId,p.ParentQueryId,p.QueryId,p.PlanId,q.query_plan_hash AS QueryPlanHash,
       SUM(p.ExecutionCount) AS ExecutionCount
INTO #ExecutedPlans
FROM lab.IncidentProfile p
JOIN sys.query_store_plan q ON q.plan_id=p.PlanId AND q.query_id=p.QueryId
WHERE p.ExecutionType=0 AND p.ExecutionCount>0
GROUP BY p.WindowId,p.ParentQueryId,p.QueryId,p.PlanId,q.query_plan_hash;
/* CONTROL_ACTIVE_PLANS_END */
DECLARE @InvalidPlanType bit=0;
IF @Major>=16
    EXEC sys.sp_executesql N'
        IF EXISTS(SELECT 1 FROM #ExecutedPlans e JOIN sys.query_store_plan p ON p.plan_id=e.PlanId AND p.query_id=e.QueryId
                  WHERE p.plan_type IS NULL OR p.plan_type NOT IN (0,2))
            SET @Invalid=1;',N'@Invalid bit OUTPUT',@Invalid=@InvalidPlanType OUTPUT;
IF @InvalidPlanType=1
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
IF (SELECT COUNT_BIG(*) FROM #ExecutedPlans)=0
   OR EXISTS(SELECT 1 FROM lab.IncidentState w
             WHERE COALESCE((SELECT SUM(p.ExecutionCount) FROM #ExecutedPlans p WHERE p.WindowId=w.WindowId),0)<>4)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;
/* CONTROL_SEQUENCE_REPORT_BEGIN */
SELECT N'DGN007_CONTROL_WINDOW' AS ReportKind,c.WindowId,c.ConditionCode,
       w.RequestCount,w.CapturedExecutions,COUNT(DISTINCT p.PlanId) AS ExecutedPlanCount
FROM lab.ControlSequence c JOIN lab.IncidentState w ON w.WindowId=c.WindowId
JOIN #ExecutedPlans p ON p.WindowId=c.WindowId
GROUP BY c.WindowId,c.ConditionCode,w.RequestCount,w.CapturedExecutions
ORDER BY c.WindowId;
/* CONTROL_SEQUENCE_REPORT_END */
/* CONTROL_PLAN_REPORT_BEGIN */
SELECT N'DGN007_CONTROL_PLAN' AS ReportKind,p.WindowId,c.ConditionCode,p.ParentQueryId,p.QueryId,p.PlanId,
       CONVERT(varchar(18),p.QueryPlanHash,1) AS QueryPlanHashHex,p.ExecutionCount
FROM #ExecutedPlans p JOIN lab.ControlSequence c ON c.WindowId=p.WindowId
ORDER BY p.WindowId,p.ParentQueryId,p.QueryId,p.PlanId;
/* CONTROL_PLAN_REPORT_END */
/* CONTROL_PLAN_UNION_BEGIN */
SELECT N'DGN007_CONTROL_PLAN_UNION' AS ReportKind,ParentQueryId,QueryId,PlanId,
       CONVERT(varchar(18),QueryPlanHash,1) AS QueryPlanHashHex,
       MAX(CASE WHEN WindowId=0 THEN 1 ELSE 0 END) AS ExecutedInT0,
       MAX(CASE WHEN WindowId=1 THEN 1 ELSE 0 END) AS ExecutedInT1
FROM #ExecutedPlans
GROUP BY ParentQueryId,QueryId,PlanId,QueryPlanHash
ORDER BY ParentQueryId,QueryId,PlanId;
/* CONTROL_PLAN_UNION_END */
SELECT N'DGN007_CONTROL_SCOPE' AS ReportKind,N'Kontrollcapture; keine Incidentfreigabe' AS ScopeMessage;
/* CAPTURE_PROJECTION_BEGIN */
/* Gemessene Skalarprojektion vor Cleanup; keine Herkunfts-/Freezeattestation.
   Primärquellen Microsoft Learn PRINT, FOR JSON, JSON_QUERY, CONVERT Style 3
   und DATEDIFF_BIG, geprüft am 2026-10-07. Kein Querytext oder Plan-XML im Body.
   Schema und Digests ergänzt ausschließlich der externe reine Packager. */
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;
/* CAPTURE_REQUEST_ROWS_BEGIN */
SELECT w.WindowId,ROW_NUMBER() OVER(PARTITION BY w.WindowId ORDER BY r.RequestLogId) AS Ordinal,
       r.RequestLogId,r.GroupKey,r.StatusCode
INTO #CaptureRequestSource
FROM lab.IncidentState w JOIN dbo.CaseRequestLog r
  ON r.RequestLogId BETWEEN w.FirstRequestLogId AND w.LastRequestLogId;
SELECT r.WindowId,r.Ordinal,r.RequestLogId,r.GroupKey,r.StatusCode,c.ReturnedRows
INTO #CaptureRequests
FROM #CaptureRequestSource r LEFT JOIN lab.RequestResultCapture c
  ON c.WindowId=r.WindowId AND c.Ordinal=r.Ordinal AND c.RequestLogId=r.RequestLogId;
/* CAPTURE_REQUEST_ROWS_END */
/* CAPTURE_REQUEST_GUARD_BEGIN */
IF (SELECT COUNT_BIG(*) FROM lab.RequestResultCapture)<>8
   OR (SELECT COUNT_BIG(*) FROM #CaptureRequests)<>8
   OR EXISTS(SELECT 1 FROM #CaptureRequests r LEFT JOIN #Parameters p
               ON p.WindowId=r.WindowId AND p.Sequence=r.Ordinal
             WHERE p.WindowId IS NULL OR r.ReturnedRows IS NULL OR r.ReturnedRows<=0
                OR r.ReturnedRows<>p.ExpectedCount OR r.GroupKey<>p.GroupKey OR r.StatusCode<>p.StatusCode)
   OR EXISTS(SELECT WindowId,Ordinal FROM #CaptureRequests GROUP BY WindowId,Ordinal HAVING COUNT_BIG(*)<>1)
   OR EXISTS(SELECT RequestLogId FROM #CaptureRequests GROUP BY RequestLogId HAVING COUNT_BIG(*)<>1)
   OR EXISTS(SELECT 1 FROM lab.IncidentState w
             WHERE (SELECT COUNT_BIG(*) FROM #CaptureRequests r WHERE r.WindowId=w.WindowId)<>4)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* CAPTURE_REQUEST_GUARD_END */
/* CAPTURE_EXECUTION_BOUNDS_BEGIN */
IF EXISTS(SELECT 1 FROM lab.IncidentProfile p JOIN lab.IncidentState w ON w.WindowId=p.WindowId
          WHERE p.FirstExecutionTime<w.ExecutionStarted OR p.LastExecutionTime>w.ExecutionFinished)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* CAPTURE_EXECUTION_BOUNDS_END */

/* Nur tatsächlich verwendete Familien plus nötige Self-Parent-Anker.
   Selbst ein nicht ausgeführter Parent/Dispatcher ist damit nur Familienanker,
   niemals aktiver Plan oder Element der ausgeführten Planunion. */
/* CAPTURE_FAMILY_ROWS_BEGIN */
SELECT s.QueryId,s.ParentQueryId INTO #CaptureFamilies FROM #ScopedQueries s
WHERE EXISTS(SELECT 1 FROM lab.IncidentProfile p WHERE p.QueryId=s.QueryId)
   OR EXISTS(SELECT 1 FROM lab.IncidentProfile p WHERE p.ParentQueryId=s.QueryId AND s.ParentQueryId=s.QueryId);
/* CAPTURE_FAMILY_ROWS_END */
/* CAPTURE_WEIGHTED_TOTALS_BEGIN */
SELECT p.WindowId,SUM(p.ExecutionCount) AS ExecutionCount,
       COUNT(DISTINCT p.PlanId) AS ObservedPlanCount,
       SUM(p.ExecutionCount*p.AvgDurationUs)/NULLIF(SUM(p.ExecutionCount),0) AS AvgDurationUs,
       SUM(p.ExecutionCount*p.AvgCpuUs)/NULLIF(SUM(p.ExecutionCount),0) AS AvgCpuUs,
       SUM(p.ExecutionCount*p.AvgLogicalReads)/NULLIF(SUM(p.ExecutionCount),0) AS AvgLogicalReads,
       SUM(p.ExecutionCount*p.AvgRowCount)/NULLIF(SUM(p.ExecutionCount),0) AS AvgRowCount,
       SUM(p.ExecutionCount*p.AvgRowCount) AS TotalRows
INTO #CaptureTotals FROM lab.IncidentProfile p GROUP BY p.WindowId;
/* CAPTURE_WEIGHTED_TOTALS_END */
/* CAPTURE_TOTALS_GUARD_BEGIN */
IF (SELECT COUNT_BIG(*) FROM #CaptureTotals)<>2
   OR EXISTS(SELECT 1 FROM #CaptureTotals
             WHERE ExecutionCount<>4 OR AvgDurationUs IS NULL OR AvgDurationUs<0
                OR AvgCpuUs IS NULL OR AvgCpuUs<0 OR AvgLogicalReads IS NULL OR AvgLogicalReads<0
                OR AvgRowCount IS NULL OR AvgRowCount<0 OR TotalRows IS NULL OR ABS(TotalRows-4229.0)>0.000001)
   OR (SELECT COUNT_BIG(*) FROM #CaptureFamilies) NOT BETWEEN 1 AND 12
   OR (SELECT COUNT_BIG(*) FROM #ExecutedPlans) NOT BETWEEN 1 AND 8
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* CAPTURE_TOTALS_GUARD_END */

/* UTC datetimeoffset(7) zuerst normalisieren. Der Tagesrest ist höchstens ein
   Tag: ein Nanosekunden-DATEDIFF über Jahrtausende würde bigint überlaufen. */
/* CAPTURE_TIME_ROWS_BEGIN */
SELECT w.WindowId,t.TimeKind,
       DATEDIFF_BIG(day,CONVERT(datetime2(7),'0001-01-01'),u.UtcTime)*CONVERT(bigint,864000000000)
       +DATEDIFF_BIG(nanosecond,CONVERT(datetime2(7),CONVERT(date,u.UtcTime)),u.UtcTime)/100 AS Ticks
INTO #CaptureWindowTicks
FROM lab.IncidentState w
CROSS APPLY(VALUES('interval_start',w.IntervalStart),('interval_end',w.IntervalEnd),
                  ('execution_started',w.ExecutionStarted),('execution_finished',w.ExecutionFinished)) t(TimeKind,TimeValue)
CROSS APPLY(SELECT CONVERT(datetime2(7),SWITCHOFFSET(t.TimeValue,'+00:00')) AS UtcTime) u;
SELECT p.WindowId,p.PlanId,t.TimeKind,
       DATEDIFF_BIG(day,CONVERT(datetime2(7),'0001-01-01'),u.UtcTime)*CONVERT(bigint,864000000000)
       +DATEDIFF_BIG(nanosecond,CONVERT(datetime2(7),CONVERT(date,u.UtcTime)),u.UtcTime)/100 AS Ticks
INTO #CapturePlanTicks
FROM lab.IncidentProfile p
CROSS APPLY(VALUES('first',p.FirstExecutionTime),('last',p.LastExecutionTime)) t(TimeKind,TimeValue)
CROSS APPLY(SELECT CONVERT(datetime2(7),SWITCHOFFSET(t.TimeValue,'+00:00')) AS UtcTime) u;
/* CAPTURE_TIME_ROWS_END */
/* CAPTURE_TIME_GUARD_BEGIN */
IF (SELECT COUNT_BIG(*) FROM #CaptureWindowTicks)<>8
   OR EXISTS(SELECT 1 FROM #CaptureWindowTicks WHERE Ticks IS NULL OR Ticks<0 OR Ticks>3155378975999999999)
   OR EXISTS(SELECT 1 FROM #CapturePlanTicks WHERE Ticks IS NULL OR Ticks<0 OR Ticks>3155378975999999999)
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* CAPTURE_TIME_GUARD_END */

SELECT p.WindowId,p.ParentQueryId,p.QueryId,p.PlanId,p.RuntimeStatsIntervalId,p.ExecutionType,p.ExecutionCount,
       f.Ticks AS FirstTicks,l.Ticks AS LastTicks,CONVERT(varchar(16),q.query_plan_hash,2) AS PlanHash,
       CONVERT(int,NULL) AS PlanType
INTO #CapturePlans
FROM lab.IncidentProfile p JOIN sys.query_store_plan q ON q.plan_id=p.PlanId AND q.query_id=p.QueryId
JOIN #CapturePlanTicks f ON f.WindowId=p.WindowId AND f.PlanId=p.PlanId AND f.TimeKind='first'
JOIN #CapturePlanTicks l ON l.WindowId=p.WindowId AND l.PlanId=p.PlanId AND l.TimeKind='last';
/* Keine statische Referenz auf plan_type, die Spalte fehlt auf SQL2019. */
IF @Major>=16
    EXEC sys.sp_executesql N'
        UPDATE c SET PlanType=p.plan_type FROM #CapturePlans c
        JOIN sys.query_store_plan p ON p.plan_id=c.PlanId AND p.query_id=c.QueryId;';
IF (SELECT COUNT_BIG(*) FROM #CapturePlans)<>(SELECT COUNT_BIG(*) FROM lab.IncidentProfile)
   OR EXISTS(SELECT 1 FROM #CapturePlans WHERE @Major>=16 AND (PlanType IS NULL OR PlanType NOT IN (0,2)))
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;

/* CAPTURE_JSON_BEGIN */
DECLARE @CaptureScope varchar(24)=
    (SELECT CASE a.ConditionCode+b.ConditionCode WHEN 'AB' THEN 'DGN-007_CONTROL_AB'
                 WHEN 'BA' THEN 'DGN-007_CONTROL_BA' WHEN 'AA' THEN 'DGN-007_CONTROL_AA' END
     FROM lab.ControlSequence a JOIN lab.ControlSequence b ON a.WindowId=0 AND b.WindowId=1);
DECLARE @ProjectionJson nvarchar(max)=
 (SELECT @Major AS major,@ActualCompatibility AS compatibility,@CaptureScope AS scope,@ObjectId AS parent_object_id,
    JSON_QUERY((SELECT w.WindowId AS window_id,c.ConditionCode AS condition,w.RuntimeStatsIntervalId AS interval_id,
      i.Ticks AS interval_start_ticks,e.Ticks AS interval_end_ticks,s.Ticks AS execution_started_ticks,f.Ticks AS execution_finished_ticks,
      w.FirstRequestLogId AS first_request_log_id,w.LastRequestLogId AS last_request_log_id,
      w.RequestCount AS request_count,w.CapturedExecutions AS captured_executions,t.ExecutionCount AS execution_count,
      t.ObservedPlanCount AS observed_plan_count,
      (SELECT COUNT_BIG(*) FROM #ExecutedPlans p WHERE p.WindowId=w.WindowId) AS executed_plan_count,
      CONVERT(varchar(64),t.AvgDurationUs,3) AS avg_duration_us,CONVERT(varchar(64),t.AvgCpuUs,3) AS avg_cpu_us,
      CONVERT(varchar(64),t.AvgLogicalReads,3) AS avg_logical_reads,CONVERT(varchar(64),t.AvgRowCount,3) AS avg_row_count,
      CONVERT(varchar(64),t.TotalRows,3) AS total_rows
     FROM lab.IncidentState w JOIN lab.ControlSequence c ON c.WindowId=w.WindowId JOIN #CaptureTotals t ON t.WindowId=w.WindowId
     JOIN #CaptureWindowTicks i ON i.WindowId=w.WindowId AND i.TimeKind='interval_start'
     JOIN #CaptureWindowTicks e ON e.WindowId=w.WindowId AND e.TimeKind='interval_end'
     JOIN #CaptureWindowTicks s ON s.WindowId=w.WindowId AND s.TimeKind='execution_started'
     JOIN #CaptureWindowTicks f ON f.WindowId=w.WindowId AND f.TimeKind='execution_finished'
     ORDER BY w.WindowId FOR JSON PATH,INCLUDE_NULL_VALUES)) AS windows,
    JSON_QUERY((SELECT WindowId AS window_id,Ordinal AS ordinal,RequestLogId AS request_log_id,
      GroupKey AS group_key,StatusCode AS status_code,ReturnedRows AS returned_rows,'MEASURED' AS row_evidence
      FROM #CaptureRequests ORDER BY WindowId,Ordinal FOR JSON PATH,INCLUDE_NULL_VALUES)) AS requests,
    JSON_QUERY((SELECT QueryId AS query_id,ParentQueryId AS parent_query_id,@ObjectId AS parent_object_id,
      'dbo.usp_CaseSearch' AS parent_object_name,'/* DGN007_CASE_SEARCH */' AS statement_marker
      FROM #CaptureFamilies ORDER BY QueryId FOR JSON PATH,INCLUDE_NULL_VALUES)) AS families,
    JSON_QUERY((SELECT WindowId AS window_id,ParentQueryId AS parent_query_id,QueryId AS query_id,PlanId AS plan_id,
      RuntimeStatsIntervalId AS interval_id,ExecutionType AS execution_type,ExecutionCount AS execution_count,
      FirstTicks AS first_execution_ticks,LastTicks AS last_execution_ticks,PlanHash AS query_plan_hash,PlanType AS plan_type
      FROM #CapturePlans ORDER BY WindowId,ParentQueryId,QueryId,PlanId FOR JSON PATH,INCLUDE_NULL_VALUES)) AS plans,
    JSON_QUERY((SELECT ParentQueryId AS parent_query_id,QueryId AS query_id,PlanId AS plan_id,
      CONVERT(varchar(16),QueryPlanHash,2) AS query_plan_hash,
      MAX(CASE WHEN WindowId=0 THEN 1 ELSE 0 END) AS executed_in_t0,
      MAX(CASE WHEN WindowId=1 THEN 1 ELSE 0 END) AS executed_in_t1
      FROM #ExecutedPlans GROUP BY ParentQueryId,QueryId,PlanId,QueryPlanHash
      ORDER BY ParentQueryId,QueryId,PlanId FOR JSON PATH,INCLUDE_NULL_VALUES)) AS plan_union
  FOR JSON PATH,INCLUDE_NULL_VALUES,WITHOUT_ARRAY_WRAPPER);
/* CAPTURE_JSON_END */
/* CAPTURE_FRAME_GUARD_BEGIN */
IF @ProjectionJson IS NULL OR LEN(@ProjectionJson) NOT BETWEEN 1 AND 32000
   OR @ProjectionJson COLLATE Latin1_General_100_BIN2 LIKE N'%[^ -~]%'
   OR DATALENGTH(@ProjectionJson)<>2*LEN(@ProjectionJson) OR ISJSON(@ProjectionJson)<>1
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
/* CAPTURE_FRAME_GUARD_END */
/* CAPTURE_FRAMES_BEGIN */
DECLARE @ProjectionAscii varchar(max)=CONVERT(varchar(max),@ProjectionJson);
DECLARE @PayloadLength int=DATALENGTH(@ProjectionAscii),@FrameCount int=(DATALENGTH(@ProjectionAscii)+ 511)/512,@FrameOrdinal int=1;
DECLARE @Frame varchar(8000);
WHILE @FrameOrdinal<=@FrameCount
BEGIN
    IF SYSUTCDATETIME()>=@PhaseDeadline
    BEGIN
        PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
    END;
    SET @Frame=CONCAT('DGN007_CAPTURE_FRAME|1|',CONVERT(varchar(2),@FrameOrdinal),'|',CONVERT(varchar(2),@FrameCount),'|',
                      CONVERT(varchar(5),@PayloadLength),'|',SUBSTRING(@ProjectionAscii,(@FrameOrdinal-1)*512+1,512));
    PRINT @Frame;
    SET @FrameOrdinal+=1;
END;
/* CAPTURE_FRAMES_END */
/* CAPTURE_PROJECTION_END */
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
