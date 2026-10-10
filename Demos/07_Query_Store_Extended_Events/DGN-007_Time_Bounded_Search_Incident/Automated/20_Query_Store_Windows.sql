/* DGN-007_QUERY_STORE_WINDOWS: zwei getrennte Capture-Fenster, keine Incidentabnahme.
   Primärquellen: Microsoft Learn sys.database_query_store_options,
   sys.query_store_runtime_stats_interval, sys.query_store_runtime_stats,
   sys.query_store_query_variant; geprüft am 2026-10-06.
   FWK-007: rekonstruierbaren Snapshot vor Änderung sichern. Der strengere
   Frischdatenbankvertrag restituiert durch markergebundenes DROP den ursprünglichen
   Zustand (keine Datenbank, kein Query Store); Snapshot bleibt ausschließlich im Lab. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 5000;
DECLARE @PhaseDeadline datetime2(7)=DATEADD(second,145,SYSUTCDATETIME());
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
DECLARE @EditionId int=TRY_CONVERT(int,SERVERPROPERTY('EditionID'));
IF '$(DemoId)'<>'DGN-007' OR '$(RunToken)'<>'AUTO'
   OR N'$(TargetDatabase)'<>N'SQLPERF_LAB_DGN007_AUTO'
   OR DB_NAME()<>N'SQLPERF_LAB_DGN007_AUTO'
    THROW 51000,'FAIL_CONTRACT: Unerwartetes Ziel des Fenstervertrags.',1;
IF '$(ConfirmIsolatedLab)'<>'1' OR '$(HighImpactConfirmed)'<>'1'
   OR COALESCE(TRY_CONVERT(int,'$(MaximumRuntimeSeconds)'),0) NOT BETWEEN 1 AND 180
   OR @Major IS NULL OR @Major NOT IN (15,16,17)
   OR @EditionId IS NULL OR @EditionId NOT IN (-2117995310,-1785266663)
   OR @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2
    THROW 51001,'FAIL_SAFETY: Bestätigte Developer-Wegwerfinstanz und begrenztes Budget erforderlich.',1;
IF EXISTS(SELECT 1 FROM sys.databases WHERE database_id>4 AND database_id<>DB_ID())
   OR NOT EXISTS(SELECT 1 FROM sys.databases WHERE database_id=DB_ID() AND database_id>4 AND state_desc=N'ONLINE'
                 AND compatibility_level=CASE @Major WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END)
    THROW 51001,'FAIL_SAFETY: Keine Fremddatenbanken oder abweichenden Zielzustände zulässig.',1;

/* Alle vier Marker exakt und ohne abgeschnittene Werte vor der ersten Mutation. */
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
IF @ObjectId IS NULL OR SCHEMA_ID(N'lab') IS NULL
   OR OBJECT_DEFINITION(@ObjectId) IS NULL
   OR CHARINDEX(N'/* DGN007_CASE_SEARCH */',OBJECT_DEFINITION(@ObjectId) COLLATE Latin1_General_100_BIN2)=0
   OR OBJECT_ID(N'lab.QueryStoreBaseline',N'U') IS NOT NULL
   OR OBJECT_ID(N'lab.IncidentState',N'U') IS NOT NULL
   OR OBJECT_ID(N'lab.IncidentProfile',N'U') IS NOT NULL
   OR (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>4
    THROW 51002,'FAIL_STATE: Frischer Datenmodellzustand nach vier Assertionsrequests erforderlich.',1;
IF EXISTS(SELECT GroupKey,StatusCode FROM dbo.CaseRequestLog GROUP BY GroupKey,StatusCode HAVING COUNT_BIG(*)<>1)
   OR EXISTS(SELECT GroupKey,StatusCode FROM dbo.CaseRequestLog
             EXCEPT SELECT GroupKey,StatusCode FROM (VALUES(8,3),(1,3),(5,3),(1,1)) p(GroupKey,StatusCode))
   OR EXISTS(SELECT GroupKey,StatusCode FROM (VALUES(8,3),(1,3),(5,3),(1,1)) p(GroupKey,StatusCode)
             EXCEPT SELECT GroupKey,StatusCode FROM dbo.CaseRequestLog)
    THROW 51002,'FAIL_RESULT_CONTRACT: Vorherige Datenassertion nicht vollständig.',1;

/* CUSTOM, READ_ONLY, Fehler-/Sekundärzustände und unbekannte Optionen werden
   vor Änderung abgewiesen. Snapshot enthält nur Konfiguration, keine Querytexte. */
IF (SELECT COUNT_BIG(*) FROM sys.database_query_store_options)<>1
   OR EXISTS(SELECT 1 FROM sys.database_query_store_options
      WHERE desired_state IS NULL OR desired_state NOT IN (0,2)
         OR actual_state IS NULL OR actual_state<>desired_state
         OR query_capture_mode IS NULL OR query_capture_mode NOT IN (1,2,3)
         OR size_based_cleanup_mode IS NULL OR size_based_cleanup_mode NOT IN (0,1)
         OR wait_stats_capture_mode IS NULL OR wait_stats_capture_mode NOT IN (0,1)
         OR flush_interval_seconds IS NULL OR flush_interval_seconds<1
         OR interval_length_minutes IS NULL OR interval_length_minutes NOT IN (1,5,10,15,30,60,1440)
         OR max_storage_size_mb IS NULL OR max_storage_size_mb<1
         OR stale_query_threshold_days IS NULL OR stale_query_threshold_days<0
         OR max_plans_per_query IS NULL OR max_plans_per_query<0
         OR readonly_reason IS NULL OR readonly_reason<>0)
    THROW 51002,'FAIL_STATE: Query-Store-Ausgangskonfiguration ist nicht rekonstruierbar.',1;
SELECT desired_state,actual_state,readonly_reason,flush_interval_seconds,
       interval_length_minutes,max_storage_size_mb,stale_query_threshold_days,
       max_plans_per_query,query_capture_mode,size_based_cleanup_mode,wait_stats_capture_mode,
       capture_policy_execution_count,capture_policy_total_compile_cpu_time_ms,
       capture_policy_total_execution_cpu_time_ms,capture_policy_stale_threshold_hours
INTO lab.QueryStoreBaseline
FROM sys.database_query_store_options;
IF (SELECT COUNT_BIG(*) FROM lab.QueryStoreBaseline)<>1
    THROW 51002,'FAIL_STATE: Ausgangssnapshot fehlt.',1;

CREATE TABLE lab.IncidentState(
    WindowId tinyint NOT NULL PRIMARY KEY,
    RuntimeStatsIntervalId bigint NOT NULL UNIQUE,
    IntervalStart datetimeoffset(7) NOT NULL,
    IntervalEnd datetimeoffset(7) NOT NULL,
    ExecutionStarted datetimeoffset(7) NOT NULL,
    ExecutionFinished datetimeoffset(7) NOT NULL,
    FirstRequestLogId bigint NOT NULL,
    LastRequestLogId bigint NOT NULL,
    RequestCount bigint NOT NULL,
    CapturedExecutions bigint NULL,
    CONSTRAINT CK_DGN007_Window CHECK(WindowId IN (0,1)),
    CONSTRAINT CK_DGN007_WindowBounds CHECK(IntervalStart<IntervalEnd)
);
CREATE TABLE lab.IncidentProfile(
    WindowId tinyint NOT NULL,
    ParentQueryId bigint NOT NULL,
    QueryId bigint NOT NULL,
    PlanId bigint NOT NULL,
    RuntimeStatsIntervalId bigint NOT NULL,
    ExecutionType tinyint NOT NULL,
    ExecutionCount bigint NOT NULL,
    AvgDurationUs float NOT NULL,
    AvgCpuUs float NOT NULL,
    AvgLogicalReads float NOT NULL,
    AvgRowCount float NOT NULL,
    FirstExecutionTime datetimeoffset(7) NOT NULL,
    LastExecutionTime datetimeoffset(7) NOT NULL,
    PRIMARY KEY(WindowId,PlanId,RuntimeStatsIntervalId,ExecutionType),
    FOREIGN KEY(WindowId) REFERENCES lab.IncidentState(WindowId)
);
ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET QUERY_STORE=ON
 (OPERATION_MODE=READ_WRITE,QUERY_CAPTURE_MODE=ALL,MAX_STORAGE_SIZE_MB=128,
  INTERVAL_LENGTH_MINUTES=1,DATA_FLUSH_INTERVAL_SECONDS=60);
IF NOT EXISTS(SELECT 1 FROM sys.database_query_store_options
              WHERE actual_state=2 AND desired_state=2 AND query_capture_mode=1
                AND max_storage_size_mb=128 AND interval_length_minutes=1 AND flush_interval_seconds=60)
    THROW 51002,'FAIL_STATE: Begrenzte Query-Store-Konfiguration nicht aktiv.',1;

CREATE TABLE #Parameters(WindowId tinyint NOT NULL,Sequence int NOT NULL,GroupKey int NOT NULL,StatusCode tinyint NOT NULL,ExpectedCount int NOT NULL,PRIMARY KEY(WindowId,Sequence));
INSERT #Parameters VALUES(0,1,8,3,228),(0,2,1,3,2286),(0,3,5,3,1144),(0,4,1,1,571),
                         (1,1,1,3,2286),(1,2,8,3,228),(1,3,5,3,1144),(1,4,1,1,571);
CREATE TABLE #Actual(ItemId int NOT NULL,SearchValue nvarchar(64) NOT NULL,StatusCode tinyint NOT NULL,GroupLabel nvarchar(64) NOT NULL,DetailCount int NOT NULL);
DECLARE @InitialRequestId bigint=(SELECT MAX(RequestLogId) FROM dbo.CaseRequestLog);
DECLARE @PreviousIntervalId bigint=NULL,@PreviousEnd datetimeoffset(7)=NULL;
DECLARE @IntervalId bigint,@IntervalStart datetimeoffset(7),@IntervalEnd datetimeoffset(7);
DECLARE @Pulse bigint;
DECLARE @PollDeadline datetime2(7)=DATEADD(second,90,SYSUTCDATETIME());
IF @PollDeadline>@PhaseDeadline SET @PollDeadline=@PhaseDeadline;

/* Zuerst das tatsächlich beobachtete aktuelle Intervall bestimmen; die vier
   früheren Requests werden nie als T0-Capture gewertet. WAITFOR ist nur Polling. */
WHILE @PreviousIntervalId IS NULL
BEGIN
    IF SYSUTCDATETIME()>=@PollDeadline
    BEGIN
        PRINT 'DGN007_WINDOW_TIMEOUT|INITIAL_INTERVAL';
        PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
    END;
    /* Eigenständiger Kontrollquery: kein Suchrequest, keine Parent-Capture.
       sp_executesql kompiliert den festen separaten Batch erst beim Aufruf nach
       Query Store ON (Microsoft Learn sp_executesql). Dass Vorabkompilierung
       die beobachtete 2019-Abweichung verursachte, bleibt eine Hypothese.
       Ausführung und Flush unterstützen nur Sichtbarkeit, nicht Rotation. */
    EXEC sys.sp_executesql N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;',
         N'@Rows bigint OUTPUT',@Rows=@Pulse OUTPUT;
    IF @Pulse IS NULL OR @Pulse<>12
    BEGIN
        PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
    END;
    EXEC sys.sp_query_store_flush_db;
    SELECT TOP(1) @PreviousIntervalId=runtime_stats_interval_id,@PreviousEnd=end_time
    FROM sys.query_store_runtime_stats_interval
    WHERE start_time<=TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00')
      AND end_time>TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00')
    ORDER BY start_time DESC;
    IF SYSUTCDATETIME()>=@PollDeadline
    BEGIN
        PRINT 'DGN007_WINDOW_TIMEOUT|INITIAL_INTERVAL';
        PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
    END;
    IF @PreviousIntervalId IS NOT NULL BREAK;
    WAITFOR DELAY '00:00:01';
END;
PRINT 'DGN007_WINDOW_CHECKPOINT|INITIAL_INTERVAL';
DECLARE @InitialIntervalStart datetimeoffset(7)=
    (SELECT start_time FROM sys.query_store_runtime_stats_interval WHERE runtime_stats_interval_id=@PreviousIntervalId);
DECLARE @BaselineIntervalMinutes bigint=(SELECT interval_length_minutes FROM lab.QueryStoreBaseline);
PRINT CONCAT('DGN007_WINDOW_INTERVAL|id=',CONVERT(varchar(20),@PreviousIntervalId),
             '|start=',CONVERT(varchar(40),SWITCHOFFSET(@InitialIntervalStart,'+00:00'),127),
             '|end=',CONVERT(varchar(40),SWITCHOFFSET(@PreviousEnd,'+00:00'),127),
             '|baseline_minutes=',CONVERT(varchar(20),@BaselineIntervalMinutes));

DECLARE @WindowId tinyint=0,@Sequence int,@GroupKey int,@StatusCode tinyint,@ExpectedCount int;
DECLARE @Started datetimeoffset(7),@Finished datetimeoffset(7),@BeforeRequestId bigint,@FirstRequestId bigint,@LastRequestId bigint;
WHILE @WindowId<=1
BEGIN
    SET @PollDeadline=DATEADD(second,90,SYSUTCDATETIME());
    IF @PollDeadline>@PhaseDeadline SET @PollDeadline=@PhaseDeadline;
    SET @IntervalId=NULL;
    IF @WindowId=0 PRINT 'DGN007_WINDOW_CHECKPOINT|WAIT_T0';
    ELSE PRINT 'DGN007_WINDOW_CHECKPOINT|WAIT_T1';
    /* Zweimal derselbe Nachweis: Warmup->T0, danach T0->T1. Alle Grenzen
       stammen aus dem Katalog, niemals aus einer berechneten Wartezeit. */
    WHILE @IntervalId IS NULL
    BEGIN
        IF SYSUTCDATETIME()>=@PollDeadline
        BEGIN
            PRINT 'DGN007_WINDOW_TIMEOUT|NEXT_INTERVAL';
            PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
        END;
        /* Nur die zwölf synthetischen Gruppen lesen; usp_CaseSearch und
           CaseRequestLog bleiben während des Boundary-Polls unverändert.
           Derselbe feste separate Batch wird erst beim Aufruf kompiliert. */
        EXEC sys.sp_executesql N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;',
             N'@Rows bigint OUTPUT',@Rows=@Pulse OUTPUT;
        IF @Pulse IS NULL OR @Pulse<>12
        BEGIN
            PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
        END;
        EXEC sys.sp_query_store_flush_db;
        SELECT TOP(1) @IntervalId=runtime_stats_interval_id,@IntervalStart=start_time,@IntervalEnd=end_time
        FROM sys.query_store_runtime_stats_interval
        WHERE runtime_stats_interval_id<>@PreviousIntervalId AND start_time>=@PreviousEnd
          AND start_time<=TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00')
          AND end_time>TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00')
        ORDER BY start_time;
        IF SYSUTCDATETIME()>=@PollDeadline
        BEGIN
            PRINT 'DGN007_WINDOW_TIMEOUT|NEXT_INTERVAL';
            DECLARE @LatestIntervalId bigint,@LatestIntervalStart datetimeoffset(7),@LatestIntervalEnd datetimeoffset(7);
            SELECT TOP(1) @LatestIntervalId=runtime_stats_interval_id,@LatestIntervalStart=start_time,@LatestIntervalEnd=end_time
            FROM sys.query_store_runtime_stats_interval ORDER BY start_time DESC,runtime_stats_interval_id DESC;
            PRINT CONCAT('DGN007_WINDOW_TIMEOUT_DETAIL|id=',COALESCE(CONVERT(varchar(20),@LatestIntervalId),'NONE'),
                         '|start=',COALESCE(CONVERT(varchar(40),SWITCHOFFSET(@LatestIntervalStart,'+00:00'),127),'NONE'),
                         '|end=',COALESCE(CONVERT(varchar(40),SWITCHOFFSET(@LatestIntervalEnd,'+00:00'),127),'NONE'));
            PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
        END;
        IF @IntervalId IS NOT NULL BREAK;
        WAITFOR DELAY '00:00:01';
    END;
    IF SYSUTCDATETIME()>=@PhaseDeadline
    BEGIN
        PRINT 'DGN007_WINDOW_TIMEOUT|PHASE_BEFORE_WINDOW';
        PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
    END;
    /* Ausschließlich die eigene markierte Prozedur objektbezogen kompilieren. */
    EXEC sys.sp_recompile N'dbo.usp_CaseSearch';
    SET @Started=TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00');
    SET @BeforeRequestId=(SELECT MAX(RequestLogId) FROM dbo.CaseRequestLog);
    SET @FirstRequestId=NULL;
    SET @Sequence=1;
    WHILE @Sequence<=4
    BEGIN
        IF SYSUTCDATETIME()>=@PhaseDeadline
        BEGIN
            PRINT 'DGN007_WINDOW_TIMEOUT|PHASE_BEFORE_REQUEST';
            PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
        END;
        SELECT @GroupKey=GroupKey,@StatusCode=StatusCode,@ExpectedCount=ExpectedCount
        FROM #Parameters WHERE WindowId=@WindowId AND Sequence=@Sequence;
        TRUNCATE TABLE #Actual;
        INSERT #Actual EXEC dbo.usp_CaseSearch @GroupKey,@StatusCode;
        /* Bidirektionaler vollständiger Ergebnisvertrag einschließlich Anzahl. */
        IF (SELECT COUNT_BIG(*) FROM #Actual)<>@ExpectedCount
           OR EXISTS(SELECT i.ItemId,i.SearchValue,i.StatusCode,g.GroupLabel,CONVERT(int,3)
                     FROM dbo.CaseItem i JOIN dbo.CaseGroup g ON i.GroupKey=g.GroupKey
                     WHERE i.GroupKey=@GroupKey AND i.StatusCode=@StatusCode
                     EXCEPT SELECT ItemId,SearchValue,StatusCode,GroupLabel,DetailCount FROM #Actual)
           OR EXISTS(SELECT ItemId,SearchValue,StatusCode,GroupLabel,DetailCount FROM #Actual
                     EXCEPT SELECT i.ItemId,i.SearchValue,i.StatusCode,g.GroupLabel,CONVERT(int,3)
                     FROM dbo.CaseItem i JOIN dbo.CaseGroup g ON i.GroupKey=g.GroupKey
                     WHERE i.GroupKey=@GroupKey AND i.StatusCode=@StatusCode)
            THROW 51002,'FAIL_RESULT_CONTRACT: Suchergebnis verletzt den festen Fenstervertrag.',1;
        IF (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog WHERE RequestLogId>@BeforeRequestId)<>1
           OR NOT EXISTS(SELECT 1 FROM dbo.CaseRequestLog WHERE RequestLogId>@BeforeRequestId
                         AND GroupKey=@GroupKey AND StatusCode=@StatusCode)
            THROW 51002,'FAIL_RESULT_CONTRACT: Genau ein passender Request je Parameterpaar erforderlich.',1;
        SET @LastRequestId=(SELECT MAX(RequestLogId) FROM dbo.CaseRequestLog);
        IF @FirstRequestId IS NULL SET @FirstRequestId=@LastRequestId;
        SET @BeforeRequestId=@LastRequestId;
        SET @Sequence+=1;
    END;
    SET @Finished=TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00');
    IF @Started<@IntervalStart OR @Finished>=@IntervalEnd
        THROW 51002,'FAIL_RESULT_CONTRACT: Requests überschreiten das beobachtete Intervall.',1;
    IF (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog WHERE RequestLogId BETWEEN @FirstRequestId AND @LastRequestId)<>4
       OR EXISTS(SELECT GroupKey,StatusCode FROM dbo.CaseRequestLog WHERE RequestLogId BETWEEN @FirstRequestId AND @LastRequestId
                 GROUP BY GroupKey,StatusCode HAVING COUNT_BIG(*)<>1)
        THROW 51002,'FAIL_RESULT_CONTRACT: Je Fenster vier unterschiedliche feste Requests erforderlich.',1;
    INSERT lab.IncidentState(WindowId,RuntimeStatsIntervalId,IntervalStart,IntervalEnd,ExecutionStarted,ExecutionFinished,
                             FirstRequestLogId,LastRequestLogId,RequestCount)
    VALUES(@WindowId,@IntervalId,@IntervalStart,@IntervalEnd,@Started,@Finished,@FirstRequestId,@LastRequestId,4);
    IF @WindowId=0 PRINT 'DGN007_WINDOW_CHECKPOINT|T0_DONE';
    ELSE PRINT 'DGN007_WINDOW_CHECKPOINT|T1_DONE';
    SET @PreviousIntervalId=@IntervalId;
    SET @PreviousEnd=@IntervalEnd;
    SET @WindowId+=1;
END;
IF (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>12
   OR (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog WHERE RequestLogId>@InitialRequestId)<>8
   OR NOT EXISTS(SELECT 1 FROM lab.IncidentState a JOIN lab.IncidentState b ON a.WindowId=0 AND b.WindowId=1
                 WHERE a.RuntimeStatsIntervalId<>b.RuntimeStatsIntervalId AND a.IntervalEnd<=b.IntervalStart
                   AND a.LastRequestLogId<b.FirstRequestLogId)
    THROW 51002,'FAIL_RESULT_CONTRACT: Zwei disjunkte Fenster und acht neue Requests erforderlich.',1;

/* Flush unterstützt nur die Sichtbarkeit; er ersetzt keinen Intervallnachweis. */
EXEC sys.sp_query_store_flush_db;
CREATE TABLE #ParentQueries(QueryId bigint NOT NULL PRIMARY KEY);
CREATE TABLE #ScopedQueries(QueryId bigint NOT NULL PRIMARY KEY,ParentQueryId bigint NOT NULL);
SET @PollDeadline=DATEADD(second,10,SYSUTCDATETIME());
IF @PollDeadline>@PhaseDeadline SET @PollDeadline=@PhaseDeadline;
DECLARE @Captured bigint,@Ready bit=0;
WHILE @Ready=0
BEGIN
    TRUNCATE TABLE #ParentQueries;
    TRUNCATE TABLE #ScopedQueries;
    INSERT #ParentQueries(QueryId)
    SELECT q.query_id FROM sys.query_store_query q JOIN sys.query_store_query_text t ON t.query_text_id=q.query_text_id
    WHERE q.object_id=@ObjectId
      AND CHARINDEX(N'/* DGN007_CASE_SEARCH */',t.query_sql_text COLLATE Latin1_General_100_BIN2)>0;
    /* Eine statische Referenz auf die neuere View wäre auf SQL Server 2019 ungültig. */
    IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_variant',N'V') IS NOT NULL
        EXEC sys.sp_executesql N'DELETE p FROM #ParentQueries p JOIN sys.query_store_query_variant v ON v.query_variant_query_id=p.QueryId;';
    INSERT #ScopedQueries(QueryId,ParentQueryId) SELECT QueryId,QueryId FROM #ParentQueries;
    IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_variant',N'V') IS NOT NULL
        EXEC sys.sp_executesql N'
            INSERT #ScopedQueries(QueryId,ParentQueryId)
            SELECT DISTINCT v.query_variant_query_id,v.parent_query_id
            FROM sys.query_store_query_variant v JOIN #ParentQueries p ON p.QueryId=v.parent_query_id
            WHERE NOT EXISTS(SELECT 1 FROM #ScopedQueries s WHERE s.QueryId=v.query_variant_query_id);';
    DELETE FROM lab.IncidentProfile;
    /* Aktive Intervalle können Disk- und In-Memory-Zeilen für denselben Plan
       enthalten: Counts summieren, Mittelwerte nach ExecutionCount gewichten. */
    INSERT lab.IncidentProfile(WindowId,ParentQueryId,QueryId,PlanId,RuntimeStatsIntervalId,ExecutionType,
                              ExecutionCount,AvgDurationUs,AvgCpuUs,AvgLogicalReads,AvgRowCount,FirstExecutionTime,LastExecutionTime)
    SELECT w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id,r.runtime_stats_interval_id,r.execution_type,
           SUM(r.count_executions),
           SUM(r.avg_duration*r.count_executions)/NULLIF(SUM(r.count_executions),0),
           SUM(r.avg_cpu_time*r.count_executions)/NULLIF(SUM(r.count_executions),0),
           SUM(r.avg_logical_io_reads*r.count_executions)/NULLIF(SUM(r.count_executions),0),
           SUM(r.avg_rowcount*r.count_executions)/NULLIF(SUM(r.count_executions),0),
           MIN(r.first_execution_time),MAX(r.last_execution_time)
    FROM #ScopedQueries s JOIN sys.query_store_plan p ON p.query_id=s.QueryId
    JOIN sys.query_store_runtime_stats r ON r.plan_id=p.plan_id
    JOIN lab.IncidentState w ON w.RuntimeStatsIntervalId=r.runtime_stats_interval_id
    WHERE r.execution_type=0
    GROUP BY w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id,r.runtime_stats_interval_id,r.execution_type
    HAVING SUM(r.count_executions)>0;
    IF NOT EXISTS(SELECT 1 FROM lab.IncidentState w
                  WHERE COALESCE((SELECT SUM(p.ExecutionCount) FROM lab.IncidentProfile p WHERE p.WindowId=w.WindowId),0)<>4)
        SET @Ready=1;
    IF @Ready=1 OR SYSUTCDATETIME()>=@PollDeadline BREAK;
    WAITFOR DELAY '00:00:01';
    EXEC sys.sp_query_store_flush_db;
END;
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'DGN007_WINDOW_TIMEOUT|CAPTURE_DEADLINE';
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;
PRINT 'DGN007_WINDOW_CHECKPOINT|CAPTURE_DONE';
SELECT @Captured=COALESCE(SUM(ExecutionCount),0) FROM lab.IncidentProfile;
IF @Captured=0
BEGIN
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING'; RETURN;
END;
IF @Ready<>1
BEGIN
    /* Nur im echten SQL20-Fehlerpfad: begrenzte skalare Diagnose einer
       erneuten Query-Store-Abfrage; kein atomarer Snapshot der Poll-Aufnahme. */
    BEGIN TRY
    SELECT TOP(17) ROW_NUMBER() OVER(ORDER BY w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id,
                                      r.runtime_stats_interval_id,r.execution_type,r.first_execution_time) AS Ordinal,
           w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id AS PlanId,
           r.runtime_stats_interval_id AS IntervalId,r.execution_type AS ExecutionType,
           r.count_executions AS ExecutionCount,r.first_execution_time AS FirstTime,
           r.last_execution_time AS LastTime
    INTO #Sql20FailureRaw
    FROM #ScopedQueries s JOIN sys.query_store_plan p ON p.query_id=s.QueryId
    JOIN sys.query_store_runtime_stats r ON r.plan_id=p.plan_id
    JOIN lab.IncidentState w ON w.RuntimeStatsIntervalId=r.runtime_stats_interval_id
    ORDER BY w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id,r.runtime_stats_interval_id,
             r.execution_type,r.first_execution_time;
    DECLARE @DiagRows int=(SELECT COUNT(*) FROM #Sql20FailureRaw),@DiagWindow tinyint=0;
    PRINT CONCAT('DGN007_SQL20_RAW|1|BEGIN|',CASE WHEN @DiagRows>16 THEN 'OVERFLOW' ELSE 'COMPLETE' END,
                 '|',@DiagRows);
    DECLARE @DiagRequestCount bigint,@DiagProfileCount bigint,@DiagRawCount bigint;
    WHILE @DiagWindow<=1
    BEGIN
        SELECT @DiagRequestCount=RequestCount FROM lab.IncidentState WHERE WindowId=@DiagWindow;
        SELECT @DiagProfileCount=COALESCE(SUM(ExecutionCount),0)
        FROM lab.IncidentProfile WHERE WindowId=@DiagWindow;
        SELECT @DiagRawCount=COALESCE(SUM(r.count_executions),0)
        FROM #ScopedQueries s JOIN sys.query_store_plan p ON p.query_id=s.QueryId
        JOIN sys.query_store_runtime_stats r ON r.plan_id=p.plan_id
        JOIN lab.IncidentState w ON w.RuntimeStatsIntervalId=r.runtime_stats_interval_id
        WHERE w.WindowId=@DiagWindow AND r.execution_type=0;
        PRINT CONCAT('DGN007_SQL20_RAW|1|WINDOW|',@DiagWindow,'|',
            COALESCE(CONVERT(varchar(20),@DiagRequestCount),'N'),'|',@DiagProfileCount,'|',@DiagRawCount);
        SET @DiagWindow+=1;
    END;
    DECLARE @DiagOrdinal int=1;
    DECLARE @DiagLine varchar(512);
    WHILE @DiagOrdinal<=@DiagRows AND @DiagOrdinal<=16
    BEGIN
        SELECT @DiagLine=CONCAT('DGN007_SQL20_RAW|1|ROW|',Ordinal,'|',WindowId,'|',ParentQueryId,
                             '|',QueryId,'|',PlanId,'|',IntervalId,'|',ExecutionType,'|',ExecutionCount,
                             '|',COALESCE(CONVERT(varchar(40),SWITCHOFFSET(FirstTime,'+00:00'),127),'N'),
                             '|',COALESCE(CONVERT(varchar(40),SWITCHOFFSET(LastTime,'+00:00'),127),'N'))
        FROM #Sql20FailureRaw WHERE Ordinal=@DiagOrdinal;
        PRINT @DiagLine;
        SET @DiagOrdinal+=1;
    END;
    PRINT CONCAT('DGN007_SQL20_RAW|1|END|',CASE WHEN @DiagRows>16 THEN 0 ELSE @DiagRows END);
    END TRY
    BEGIN CATCH
        PRINT 'DGN007_SQL20_RAW|1|BEGIN|INSUFFICIENT|0';
        PRINT 'DGN007_SQL20_RAW|1|END|0';
    END CATCH;
    THROW 51002,'FAIL_RESULT_CONTRACT: Query Store erfasste nicht genau vier Suchausführungen je Fenster.',1;
END;
IF EXISTS(SELECT 1 FROM lab.IncidentProfile p JOIN lab.IncidentState w ON w.WindowId=p.WindowId
          WHERE p.FirstExecutionTime<w.IntervalStart OR p.LastExecutionTime>=w.IntervalEnd)
   OR EXISTS(SELECT 1 FROM #ScopedQueries s JOIN sys.query_store_plan p ON p.query_id=s.QueryId WHERE p.is_forced_plan=1)
    THROW 51002,'FAIL_RESULT_CONTRACT: Capture liegt außerhalb des Fenster- oder Planvertrags.',1;
IF NOT EXISTS(SELECT 1 FROM sys.database_query_store_options
              WHERE actual_state=2 AND desired_state=2 AND query_capture_mode=1
                AND max_storage_size_mb=128 AND interval_length_minutes=1 AND flush_interval_seconds=60)
    THROW 51002,'FAIL_STATE: Query Store verlor den begrenzten Capturezustand.',1;
UPDATE w SET CapturedExecutions=p.Executions
FROM lab.IncidentState w JOIN (SELECT WindowId,SUM(ExecutionCount) AS Executions FROM lab.IncidentProfile GROUP BY WindowId) p ON p.WindowId=w.WindowId;
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'DGN007_WINDOW_TIMEOUT|FINAL_DEADLINE';
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;
/* Ausschließlich WINDOWS: keine Reproduktion, Regression oder Performancefreigabe. */
PRINT 'SQLPERF_SUMMARY|PASS|OK';
