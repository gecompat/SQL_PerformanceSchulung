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
    + N'CLEANUP_POLICY = ( STALE_QUERY_THRESHOLD_DAYS = 2 ),'
    + N'DATA_FLUSH_INTERVAL_SECONDS = 60,'
    + N'MAX_STORAGE_SIZE_MB = 128,'
    + N'INTERVAL_LENGTH_MINUTES = 1,'
    + N'SIZE_BASED_CLEANUP_MODE = AUTO,'
    + N'QUERY_CAPTURE_MODE = ALL,'
    + N'MAX_PLANS_PER_QUERY = 20);';
EXEC sys.sp_executesql @Sql;

/* CREATE SCHEMA ist als einzige Aussage eines isolierten Kindbatches ausfuehrbar. */
EXEC [SQLPERF_LAB_DGN007_LOCAL].sys.sp_executesql N'CREATE SCHEMA lab AUTHORIZATION dbo;';
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'CREATE TABLE dbo.CaseGroup(GroupKey int NOT NULL PRIMARY KEY,GroupLabel nvarchar(64) NOT NULL);'
    + N'CREATE TABLE dbo.CaseItem(ItemId int IDENTITY(1,1) NOT NULL CONSTRAINT PK_CaseItem PRIMARY KEY NONCLUSTERED,'
    + N'GroupKey int NOT NULL CONSTRAINT FK_CaseItem_CaseGroup REFERENCES dbo.CaseGroup(GroupKey),'
    + N'StatusCode tinyint NOT NULL,SearchValue nvarchar(64) NOT NULL,Payload binary(96) NOT NULL);'
    + N'CREATE CLUSTERED INDEX CIX_CaseItem ON dbo.CaseItem(ItemId);'
    + N'CREATE NONCLUSTERED INDEX IX_CaseItem_Group_Status ON dbo.CaseItem(GroupKey,StatusCode) INCLUDE (SearchValue);'
    + N'CREATE TABLE dbo.CaseItemDetail(ItemId int NOT NULL,DetailOrdinal int NOT NULL,DetailPayload binary(128) NOT NULL,'
    + N'CONSTRAINT PK_CaseItemDetail PRIMARY KEY(ItemId,DetailOrdinal),'
    + N'CONSTRAINT FK_CaseItemDetail_CaseItem FOREIGN KEY(ItemId) REFERENCES dbo.CaseItem(ItemId));'
    + N'CREATE TABLE dbo.CaseRequestLog(RequestLogId bigint IDENTITY(1,1) NOT NULL CONSTRAINT PK_CaseRequestLog PRIMARY KEY NONCLUSTERED,'
    + N'GroupKey int NOT NULL,StatusCode tinyint NOT NULL,RequestedUtc datetime2(0) NOT NULL);'
    + N'CREATE CLUSTERED INDEX CIX_CaseRequestLog ON dbo.CaseRequestLog(RequestLogId);';
EXEC sys.sp_executesql @Sql;

/* Deterministische Daten: vier haeufige, drei mittlere und fuenf seltene Gruppen. Jeder CTE steht unmittelbar vor seinem INSERT im selben Batch. */
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'WITH Digits(n) AS (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4'
    + N' UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9),'
    + N'Numbers(n) AS (SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) FROM Digits a CROSS JOIN Digits b CROSS JOIN Digits c)'
    + N'INSERT dbo.CaseGroup(GroupKey,GroupLabel)'
    + N'SELECT n,N''Group'' + CONVERT(nvarchar(11),n) FROM Numbers WHERE n BETWEEN 1 AND 12;';
EXEC sys.sp_executesql @Sql;
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'WITH Digits(n) AS (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4'
    + N' UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9),'
    + N'Numbers(n) AS (SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) FROM Digits a CROSS JOIN Digits b CROSS JOIN Digits c CROSS JOIN Digits d CROSS JOIN Digits e),'
    + N'Items AS (SELECT n,'
    + N'CASE WHEN n <= 16000 THEN 1 + ((n - 1) % 4) '
    + N'WHEN n <= 22000 THEN 5 + ((n - 16001) % 3) ELSE 8 + ((n - 22001) % 5) END AS GroupKey,'
    + N'CASE WHEN n % 7 = 0 THEN 1 WHEN n % 7 IN (3,5) THEN 2 ELSE 3 END AS StatusCode'
    + N' FROM Numbers WHERE n BETWEEN 1 AND 24000)'
    + N'INSERT dbo.CaseItem(SearchValue,GroupKey,StatusCode,Payload)'
    + N'SELECT N''Search'' + CONVERT(nvarchar(11),n),GroupKey,StatusCode,CONVERT(binary(96),REPLICATE(CONVERT(binary(1),0x5A),96)) FROM Items;';
EXEC sys.sp_executesql @Sql;
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'WITH Digits(n) AS (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4'
    + N' UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9),'
    + N'Numbers(n) AS (SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) FROM Digits a CROSS JOIN Digits b)'
    + N'INSERT dbo.CaseItemDetail(ItemId,DetailOrdinal,DetailPayload)'
    + N'SELECT i.ItemId,x.n,CONVERT(binary(128),REPLICATE(CONVERT(binary(1),0x41),128))'
    + N'FROM dbo.CaseItem i CROSS JOIN Numbers x WHERE x.n BETWEEN 1 AND 3;';
EXEC sys.sp_executesql @Sql;

/* Markierte Suchprozedur mit festem Ergebnisvertrag; kompilierter Parameterwert ergibt sich aus der Aufrufreihenfolge. CREATE/ALTER PROCEDURE ist die erste Aussage eines isolierten Kindbatches; Segmente enden auf Leerzeichen. */
SET @Sql = N'CREATE OR ALTER PROCEDURE dbo.usp_CaseSearch @GroupKey int, @StatusCode tinyint '
    + N'AS BEGIN SET NOCOUNT ON; '
    + N'SELECT /* DGN007_CASE_SEARCH */ i.ItemId,i.SearchValue,i.StatusCode,g.GroupLabel, '
    + N'(SELECT COUNT(*) FROM dbo.CaseItemDetail d WHERE d.ItemId = i.ItemId) AS DetailCount '
    + N'FROM dbo.CaseItem i JOIN dbo.CaseGroup g ON g.GroupKey = i.GroupKey '
    + N'WHERE i.GroupKey = @GroupKey AND i.StatusCode = @StatusCode '
    + N'ORDER BY i.ItemId; '
    + N'INSERT dbo.CaseRequestLog(GroupKey,StatusCode,RequestedUtc) VALUES(@GroupKey,@StatusCode,SYSUTCDATETIME()); '
    + N'END;';
EXEC [SQLPERF_LAB_DGN007_LOCAL].sys.sp_executesql @Sql;

/* Phasen und ihre Query-Store-Profile bleiben getrennt in der markierten Datenbank. */
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';'
    + N'CREATE TABLE lab.IncidentState(IncidentPhase nvarchar(32) NOT NULL PRIMARY KEY,'
    + N'MarkerUtc datetimeoffset(7) NOT NULL,CompletedUtc datetimeoffset(7) NULL);'
    + N'CREATE TABLE lab.IncidentQueryStoreProfile(IncidentPhase nvarchar(32) NOT NULL '
    + N'REFERENCES lab.IncidentState(IncidentPhase),QueryId bigint NOT NULL,PlanId bigint NOT NULL,'
    + N'RuntimeStatsIntervalId bigint NOT NULL,CountExecutions bigint NOT NULL,'
    + N'FirstExecutionUtc datetimeoffset(7) NOT NULL,LastExecutionUtc datetimeoffset(7) NOT NULL,'
    + N'PRIMARY KEY(IncidentPhase,QueryId,PlanId,RuntimeStatsIntervalId));';
EXEC sys.sp_executesql @Sql;

/* Der beobachtete Intervallabschluss steuert T1; Flush allein erzeugt kein neues Intervall. */
SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';
DECLARE @PhaseNumber int = 0, @Phase nvarchar(32), @ExpectedExecutions bigint,
        @ActualExecutions bigint, @VariantCount int, @EvidenceMessage nvarchar(2048),
        @IntervalEnd datetimeoffset(7), @Deadline datetime2(7);
WHILE @PhaseNumber < 2
BEGIN
    SET @Phase = CASE @PhaseNumber WHEN 0 THEN N''T0_BASELINE'' ELSE N''T1_INCIDENT'' END;
    SET @ExpectedExecutions = CASE @PhaseNumber WHEN 0 THEN 3 ELSE 5 END;
    INSERT lab.IncidentState(IncidentPhase,MarkerUtc) VALUES(@Phase,SYSUTCDATETIME());
    IF @PhaseNumber = 0
    BEGIN
        EXEC dbo.usp_CaseSearch 8,3;
        EXEC dbo.usp_CaseSearch 8,3;
        EXEC dbo.usp_CaseSearch 8,3;
    END
    ELSE
    BEGIN
        EXEC dbo.usp_CaseSearch 1,3;
        EXEC dbo.usp_CaseSearch 1,3;
        EXEC dbo.usp_CaseSearch 1,3;
        EXEC dbo.usp_CaseSearch 5,3;
        EXEC dbo.usp_CaseSearch 1,1;
    END;
    UPDATE lab.IncidentState SET CompletedUtc = SYSUTCDATETIME() WHERE IncidentPhase = @Phase;
    EXEC sys.sp_query_store_flush_db;
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
    INSERT lab.IncidentQueryStoreProfile
        (IncidentPhase,QueryId,PlanId,RuntimeStatsIntervalId,CountExecutions,FirstExecutionUtc,LastExecutionUtc)
    SELECT @Phase,q.query_id,p.plan_id,rs.runtime_stats_interval_id,
           SUM(rs.count_executions),MIN(rs.first_execution_time),MAX(rs.last_execution_time)
    FROM EffectiveQuery AS effective
    JOIN sys.query_store_query AS q ON q.query_id = effective.query_id
    JOIN sys.query_store_plan p ON p.query_id = q.query_id
    JOIN sys.query_store_runtime_stats rs ON rs.plan_id = p.plan_id
    JOIN sys.query_store_runtime_stats_interval i ON i.runtime_stats_interval_id = rs.runtime_stats_interval_id
    JOIN lab.IncidentState s ON s.IncidentPhase = @Phase
    WHERE rs.execution_type = 0 AND rs.count_executions > 0
      /* Zuordnung nach belegtem Intervall; Runtime-Zeitstempel sind keine praezisen Phasengrenzen. */
      AND i.end_time > s.MarkerUtc AND i.start_time <= s.CompletedUtc
    GROUP BY q.query_id,p.plan_id,rs.runtime_stats_interval_id;
    SELECT @ActualExecutions=COALESCE(SUM(CountExecutions),0)
    FROM lab.IncidentQueryStoreProfile WHERE IncidentPhase = @Phase;
    SELECT @VariantCount=COUNT(DISTINCT qv.query_variant_query_id)
    FROM sys.query_store_query AS q
    JOIN sys.query_store_query_text AS qt ON qt.query_text_id=q.query_text_id
    JOIN sys.query_store_query_variant AS qv ON qv.parent_query_id=q.query_id
    WHERE q.object_id=OBJECT_ID(N''dbo.usp_CaseSearch'',N''P'')
      AND qt.query_sql_text LIKE N''%/* DGN007_CASE_SEARCH */%'';
    IF @ActualExecutions <> @ExpectedExecutions
    BEGIN
        /* Begrenzte, textfreie Diagnose: nur die strikt markierte Parent-Query und ihre PSP-Varianten; bewusst vor dem Intervallfilter. */
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
        ),
        ScopedRuntimeGroup AS
        (
            SELECT q.query_id,p.plan_id,rs.runtime_stats_interval_id,rs.execution_type,
                   rs.count_executions,rs.first_execution_time,rs.last_execution_time
            FROM EffectiveQuery AS effective
            JOIN sys.query_store_query AS q ON q.query_id = effective.query_id
            JOIN sys.query_store_plan AS p ON p.query_id = q.query_id
            JOIN sys.query_store_runtime_stats AS rs ON rs.plan_id = p.plan_id
        )
        SELECT N''DGN007_QUERY_STORE_DIAGNOSTIC_COUNTS'' AS DiagnosticKind,@Phase AS IncidentPhase,
               (SELECT COUNT(*) FROM StrictParentQuery) AS ParentQueryCount,
               (SELECT COUNT(*) FROM EffectiveQuery) AS EffectiveQueryCount,
               (SELECT COUNT(DISTINCT plan_id) FROM ScopedRuntimeGroup) AS PlanCount,
               (SELECT COUNT(*) FROM ScopedRuntimeGroup) AS RuntimeGroupCount,
               state.actual_state_desc AS QueryStoreActualState,state.query_capture_mode_desc AS QueryStoreCaptureMode,
               state.readonly_reason AS QueryStoreReadOnlyReason
        FROM sys.database_query_store_options AS state;

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
        ),
        ScopedRuntimeGroup AS
        (
            SELECT q.query_id,p.plan_id,rs.runtime_stats_interval_id,rs.execution_type,
                   rs.count_executions,rs.first_execution_time,rs.last_execution_time
            FROM EffectiveQuery AS effective
            JOIN sys.query_store_query AS q ON q.query_id = effective.query_id
            JOIN sys.query_store_plan AS p ON p.query_id = q.query_id
            JOIN sys.query_store_runtime_stats AS rs ON rs.plan_id = p.plan_id
        )
        SELECT TOP (32) N''DGN007_QUERY_STORE_DIAGNOSTIC_GROUP'' AS DiagnosticKind,@Phase AS IncidentPhase,
               runtime.query_id,runtime.plan_id,runtime.runtime_stats_interval_id,runtime.execution_type,
               runtime.count_executions,runtime.first_execution_time,runtime.last_execution_time,
               interval_bounds.start_time AS IntervalStartUtc,interval_bounds.end_time AS IntervalEndUtc,
               phase.MarkerUtc AS PhaseMarkerUtc,phase.CompletedUtc AS PhaseCompletedUtc,
               CONVERT(bit,CASE WHEN runtime.first_execution_time < phase.MarkerUtc THEN 1 ELSE 0 END) AS FirstBeforeMarker,
               CONVERT(bit,CASE WHEN runtime.last_execution_time > phase.CompletedUtc THEN 1 ELSE 0 END) AS LastAfterCompleted
        FROM ScopedRuntimeGroup AS runtime
        JOIN sys.query_store_runtime_stats_interval AS interval_bounds
          ON interval_bounds.runtime_stats_interval_id = runtime.runtime_stats_interval_id
        JOIN lab.IncidentState AS phase ON phase.IncidentPhase = @Phase
        ORDER BY runtime.query_id,runtime.plan_id,runtime.runtime_stats_interval_id,runtime.execution_type;

        SET @EvidenceMessage=CONCAT(N''SKIP_EVIDENCE_MISSING: Phase='',@Phase,N''; ExpectedExecutions='',@ExpectedExecutions,
                                    N''; ActualExecutions='',@ActualExecutions,N''; QueryVariantCount='',@VariantCount,
                                    N'': Die markierten Suchausfuehrungen sind nicht vollstaendig im Query Store erfasst.'');
        THROW 51002,@EvidenceMessage,1;
    END;
    IF @PhaseNumber = 0
    BEGIN
        SELECT @IntervalEnd = MAX(i.end_time)
        FROM lab.IncidentQueryStoreProfile e
        JOIN sys.query_store_runtime_stats_interval i ON i.runtime_stats_interval_id = e.RuntimeStatsIntervalId
        WHERE e.IncidentPhase = N''T0_BASELINE'';
        IF @IntervalEnd IS NULL
            THROW 51002,''SKIP_EVIDENCE_MISSING: Das Baseline-Intervall fehlt.'',1;
        SET @Deadline = DATEADD(second,90,SYSUTCDATETIME());
        WHILE SYSUTCDATETIME() <= @IntervalEnd
        BEGIN
            IF SYSUTCDATETIME() >= @Deadline
                THROW 51002,''SKIP_EVIDENCE_MISSING: Query-Store-Intervallgrenze nicht rechtzeitig erreicht.'',1;
            WAITFOR DELAY ''00:00:01'';
        END;
    END;
    SET @PhaseNumber += 1;
END;
IF EXISTS (
    SELECT 1 FROM lab.IncidentQueryStoreProfile b
    JOIN sys.query_store_runtime_stats_interval bi ON bi.runtime_stats_interval_id = b.RuntimeStatsIntervalId
    CROSS JOIN lab.IncidentQueryStoreProfile t
    JOIN sys.query_store_runtime_stats_interval ti ON ti.runtime_stats_interval_id = t.RuntimeStatsIntervalId
    WHERE b.IncidentPhase = N''T0_BASELINE'' AND t.IncidentPhase = N''T1_INCIDENT''
      AND bi.end_time > ti.start_time)
    THROW 51002,''SKIP_EVIDENCE_MISSING: Baseline und Incident teilen ein Query-Store-Intervall.'',1;';
EXEC sys.sp_executesql @Sql;

SELECT N'DGN-007' AS ScenarioId, N'INSTALL' AS Phase, N'READY_FOR_USER' AS Outcome,
       @TargetDatabase AS TargetDatabase;
