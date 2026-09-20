/* DGN-007: sechs getrennte Evidenzstufen. Die Ausgaben erklären keine Referenzmaßnahme. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @QueryId bigint, @PlanCount int, @RuntimeRows int, @ParentQueryCount int, @EffectiveQueryCount int, @VariantCount int,
        @XeActive bit, @XeRows int = 0, @XeStartedUtc datetimeoffset(7);
DECLARE @SessionName sysname=N'SQLPERF_DGN007_LOCAL';

/* 1 – Symptom: nur der zeitliche und fachliche Rahmen. */
SELECT 1 AS EvidenceLevel, N'SYMPTOM' AS EvidenceScope, IncidentPhase, MarkerUtc
FROM lab.IncidentState WHERE IncidentPhase IN(N'T0_BASELINE',N'T1_INCIDENT') ORDER BY MarkerUtc;

/* 2 – Historie: Query Store ohne Planerklärung. */
;WITH StrictParentQuery AS
(
    SELECT q.query_id
    FROM sys.query_store_query AS q
    JOIN sys.query_store_query_text AS qt ON qt.query_text_id=q.query_text_id
    WHERE q.object_id=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')
      AND qt.query_sql_text LIKE N'%/* DGN007_CASE_SEARCH */%'
),
EffectiveQuery AS
(
    SELECT query_id FROM StrictParentQuery
    UNION
    SELECT qv.query_variant_query_id
    FROM sys.query_store_query_variant AS qv
    JOIN StrictParentQuery AS parent ON parent.query_id=qv.parent_query_id
)
SELECT TOP (20) 2 AS EvidenceLevel, N'HISTORY' AS EvidenceScope, q.query_id, p.plan_id,
       rs.first_execution_time, rs.last_execution_time, rs.count_executions,
       rs.avg_duration, rs.avg_cpu_time, rs.avg_logical_io_reads, rs.avg_rowcount
FROM EffectiveQuery AS effective
JOIN sys.query_store_query AS q ON q.query_id=effective.query_id
JOIN sys.query_store_plan AS p ON p.query_id=q.query_id
LEFT JOIN sys.query_store_runtime_stats AS rs ON rs.plan_id=p.plan_id
ORDER BY rs.last_execution_time, p.plan_id;
SELECT 2 AS EvidenceLevel,N'HISTORY' AS EvidenceScope,e.IncidentPhase,e.QueryId,e.PlanId,e.RuntimeStatsIntervalId,
       e.CountExecutions,e.FirstExecutionUtc,e.LastExecutionUtc,s.MarkerUtc,s.CompletedUtc,
       i.start_time AS IntervalStartUtc,i.end_time AS IntervalEndUtc
FROM lab.IncidentQueryStoreProfile AS e
JOIN lab.IncidentState AS s ON s.IncidentPhase=e.IncidentPhase
JOIN sys.query_store_runtime_stats_interval AS i ON i.runtime_stats_interval_id=e.RuntimeStatsIntervalId
WHERE e.IncidentPhase IN(N'T0_BASELINE',N'T1_INCIDENT')
ORDER BY s.MarkerUtc,e.QueryId,e.PlanId,e.RuntimeStatsIntervalId;

/* 3 – Kontext: Datenbank- und Cacheattribute ohne Ursachenurteil. */
SELECT 3 AS EvidenceLevel, N'CONTEXT' AS EvidenceScope, DATABASEPROPERTYEX(DB_NAME(),N'CompatibilityLevel') AS CompatibilityLevel,
       o.actual_state_desc AS QueryStoreState, o.query_capture_mode_desc AS CaptureMode
FROM sys.database_query_store_options AS o;
SELECT 3 AS EvidenceLevel, N'CONTEXT' AS EvidenceScope, pa.attribute, CONVERT(nvarchar(128),pa.value) AS AttributeValue
FROM sys.dm_exec_procedure_stats AS ps
CROSS APPLY sys.dm_exec_plan_attributes(ps.plan_handle) AS pa
WHERE ps.object_id=OBJECT_ID(N'dbo.usp_CaseSearch') AND pa.attribute IN(N'set_options',N'dbid');

/* 4 – Plan und Verteilung: XML bleibt eine Evidenzquelle, keine fest erwartete Planform. */
;WITH StrictParentQuery AS
(
    SELECT q.query_id
    FROM sys.query_store_query AS q
    JOIN sys.query_store_query_text AS qt ON qt.query_text_id=q.query_text_id
    WHERE q.object_id=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')
      AND qt.query_sql_text LIKE N'%/* DGN007_CASE_SEARCH */%'
),
EffectiveQuery AS
(
    SELECT query_id FROM StrictParentQuery
    UNION
    SELECT qv.query_variant_query_id
    FROM sys.query_store_query_variant AS qv
    JOIN StrictParentQuery AS parent ON parent.query_id=qv.parent_query_id
)
SELECT 4 AS EvidenceLevel, N'PLAN' AS EvidenceScope, p.plan_id, p.query_plan,
       p.last_compile_start_time, p.last_execution_time
FROM EffectiveQuery AS effective
JOIN sys.query_store_query AS q ON q.query_id=effective.query_id
JOIN sys.query_store_plan AS p ON p.query_id=q.query_id
SELECT 4 AS EvidenceLevel, N'PLAN' AS EvidenceScope, GroupKey, StatusCode, COUNT_BIG(*) AS ItemCount
FROM dbo.CaseItem GROUP BY GroupKey, StatusCode ORDER BY ItemCount DESC, GroupKey, StatusCode;
DBCC SHOW_STATISTICS (N'dbo.CaseItem', N'IX_CaseItem_Group_Status') WITH STAT_HEADER, HISTOGRAM;

/* 5 – Systemsignale: eng begrenzter Request-/Eventscope, keine serverweite Rangliste. */
SELECT @XeActive=CASE WHEN EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=@SessionName) THEN 1 ELSE 0 END;
SELECT @XeStartedUtc=XeStartedUtc FROM lab.Dgn007ReferenceState WHERE StateId=1;
IF @XeActive=1
BEGIN
    SELECT @XeRows=COUNT(*)
    FROM sys.dm_xe_session_targets AS t
    JOIN sys.dm_xe_sessions AS s ON s.address=t.event_session_address
    CROSS APPLY (SELECT TRY_CONVERT(xml,t.target_data) AS x) AS d
    CROSS APPLY d.x.nodes(N'RingBufferTarget/event') AS n(e)
    WHERE s.name=@SessionName AND t.target_name=N'ring_buffer';
END;
SELECT 5 AS EvidenceLevel, N'SYSTEM_SIGNALS' AS EvidenceScope, @XeActive AS XeSessionActive, @XeRows AS RingBufferEvents, @XeStartedUtc AS XeStartedUtc,
       N'XE begann nach T1; Ereignisse sind nur begrenzte Evidenz fuer nachfolgende Vergleichsausfuehrungen.' AS ScopeLimit;
SELECT 5 AS EvidenceLevel, N'SYSTEM_SIGNALS' AS EvidenceScope, session_id, status, wait_type, wait_time, granted_query_memory
FROM sys.dm_exec_requests WHERE database_id=DB_ID() AND session_id<>@@SPID;

;WITH StrictParentQuery AS
(
    SELECT q.query_id
    FROM sys.query_store_query AS q
    JOIN sys.query_store_query_text AS qt ON qt.query_text_id=q.query_text_id
    WHERE q.object_id=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')
      AND qt.query_sql_text LIKE N'%/* DGN007_CASE_SEARCH */%'
),
EffectiveQuery AS
(
    SELECT query_id FROM StrictParentQuery
    UNION
    SELECT qv.query_variant_query_id
    FROM sys.query_store_query_variant AS qv
    JOIN StrictParentQuery AS parent ON parent.query_id=qv.parent_query_id
)
SELECT @QueryId=MIN(q.query_id), @PlanCount=COUNT(DISTINCT p.plan_id), @RuntimeRows=COUNT(rs.runtime_stats_id),
       @EffectiveQueryCount=COUNT(DISTINCT q.query_id)
FROM EffectiveQuery AS effective
JOIN sys.query_store_query AS q ON q.query_id=effective.query_id
JOIN sys.query_store_plan AS p ON p.query_id=q.query_id LEFT JOIN sys.query_store_runtime_stats AS rs ON rs.plan_id=p.plan_id
;
SELECT @ParentQueryCount=COUNT(*), @VariantCount=COUNT(DISTINCT qv.query_variant_query_id)
FROM sys.query_store_query AS q
JOIN sys.query_store_query_text AS qt ON qt.query_text_id=q.query_text_id
LEFT JOIN sys.query_store_query_variant AS qv ON qv.parent_query_id=q.query_id
WHERE q.object_id=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')
  AND qt.query_sql_text LIKE N'%/* DGN007_CASE_SEARCH */%';
IF @QueryId IS NULL OR @RuntimeRows=0 OR @XeActive=0
BEGIN
    SELECT 6 AS Sequence, 'OBSERVATION' AS Phase, 'EVIDENCE_SOURCE' AS CheckId, 'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           CONCAT(N'ParentQueries=',@ParentQueryCount,N'; EffectiveQueries=',@EffectiveQueryCount,N'; QueryVariantCount=',@VariantCount,
                  N'; QueryId=',COALESCE(CONVERT(nvarchar(20),@QueryId),N'NULL'),N'; RuntimeRows=',@RuntimeRows,N'; XeActive=',@XeActive) AS ObservedValue,
           N'Query Store, Runtime-Historie und aktive begrenzte XE-Session' AS RequiredValue, N'Mindestens eine Evidenzquelle ist nicht geeignet; keine Ursachenbewertung wurde ausgegeben.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING'; RETURN;
END;
IF @PlanCount<2
BEGIN
    SELECT 7 AS Sequence, 'OBSERVATION' AS Phase, 'DISTINGUISHABLE_PROFILES' AS CheckId, 'SKIP' AS Outcome, 'SKIP_INCIDENT_NOT_REPRODUCED' AS Code,
           CONCAT(N'Plans=',@PlanCount,N'; ParentQueries=',@ParentQueryCount,N'; EffectiveQueries=',@EffectiveQueryCount,N'; QueryVariantCount=',@VariantCount) AS ObservedValue,
           N'mindestens zwei Plan- oder Laufzeitprofile' AS RequiredValue, N'Der vorbereitete Fall ist in dieser Umgebung nicht ausreichend unterscheidbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_INCIDENT_NOT_REPRODUCED'; RETURN;
END;
SELECT 8 AS Sequence, 'OBSERVATION' AS Phase, 'SUMMARY' AS CheckId, 'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'QueryId=',@QueryId,N'; Plans=',@PlanCount,N'; RuntimeRows=',@RuntimeRows,N'; ParentQueries=',@ParentQueryCount,
              N'; EffectiveQueries=',@EffectiveQueryCount,N'; QueryVariantCount=',@VariantCount,N'; XeEvents=',@XeRows) AS ObservedValue,
       N'sechs Evidenzstufen bis zur eigenen Hypothese' AS RequiredValue, N'Die Evidenz ist für die Hypothesenprüfung verfügbar; sie ist kein alleiniger Ursachenbeweis.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
