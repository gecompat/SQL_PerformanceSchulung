/* DGN-007: T2 als separates Query-Store-Fenster; exakt gleiche Ergebnismengen fuer alle vorbereiteten Parameterklassen. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Phase nvarchar(32)=N'T2_COMPARISON', @ExpectedExecutions bigint=4, @ActualExecutions bigint, @VariantCount int,
        @Start datetime2(7), @DurationMs bigint, @T1IntervalEnd datetimeoffset(7), @Deadline datetime2(7), @T2Marker datetimeoffset(7);
IF NOT EXISTS(SELECT 1 FROM lab.Dgn007ReferenceState WHERE StateId=1 AND MitigationApplied=1)
    THROW 51009, 'FAIL_STATE: Die einzelne Referenzänderung ist nicht aktiv.', 1;
IF EXISTS(SELECT 1 FROM lab.IncidentState WHERE IncidentPhase=@Phase)
    THROW 51012, 'FAIL_STATE: Ein T2-Vergleichsfenster existiert bereits; zuerst Cleanup ausführen.', 1;

/* T2 darf nicht in das von T1 bereits belegte Query-Store-Intervall fallen. */
SELECT @T1IntervalEnd=MAX(i.end_time)
FROM lab.IncidentQueryStoreProfile AS p
JOIN sys.query_store_runtime_stats_interval AS i ON i.runtime_stats_interval_id=p.RuntimeStatsIntervalId
WHERE p.IncidentPhase=N'T1_INCIDENT';
IF @T1IntervalEnd IS NULL
BEGIN
    SELECT 1 AS Sequence,'COMPARISON' AS Phase,'T2_INTERVAL' AS CheckId,'SKIP' AS Outcome,'SKIP_EVIDENCE_MISSING' AS Code,
           N'T1-Query-Store-Intervall fehlt' AS ObservedValue,N'belegtes T1-Intervall' AS RequiredValue,
           N'Ohne belegte Intervallgrenze wird kein Vergleichsprofil behauptet.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING'; RETURN;
END;
SET @Deadline=DATEADD(second,90,SYSUTCDATETIME());
WHILE SYSUTCDATETIME() <= @T1IntervalEnd
BEGIN
    IF SYSUTCDATETIME() >= @Deadline
    BEGIN
        SELECT 1 AS Sequence,'COMPARISON' AS Phase,'T2_INTERVAL' AS CheckId,'SKIP' AS Outcome,'SKIP_EVIDENCE_MISSING' AS Code,
               CONVERT(nvarchar(40),@T1IntervalEnd,127) AS ObservedValue,N'neues Query-Store-Intervall vor T2' AS RequiredValue,
               N'Die Intervallgrenze wurde innerhalb des begrenzten Wartefensters nicht erreicht.' AS Message;
        PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING'; RETURN;
    END;
    WAITFOR DELAY '00:00:01';
END;

CREATE TABLE #Parameters(GroupKey int NOT NULL,StatusCode tinyint NOT NULL,PRIMARY KEY(GroupKey,StatusCode));
INSERT #Parameters(GroupKey,StatusCode) VALUES(8,3),(1,3),(5,3),(1,1);
CREATE TABLE #Expected(GroupKey int NOT NULL,StatusCode tinyint NOT NULL,ItemId int NOT NULL,SearchValue nvarchar(64) NOT NULL,ResultStatusCode tinyint NOT NULL,GroupLabel nvarchar(64) NOT NULL,DetailCount int NOT NULL,PRIMARY KEY(GroupKey,StatusCode,ItemId));
CREATE TABLE #Actual(GroupKey int NOT NULL,StatusCode tinyint NOT NULL,ItemId int NOT NULL,SearchValue nvarchar(64) NOT NULL,ResultStatusCode tinyint NOT NULL,GroupLabel nvarchar(64) NOT NULL,DetailCount int NOT NULL,PRIMARY KEY(GroupKey,StatusCode,ItemId));

INSERT #Expected(GroupKey,StatusCode,ItemId,SearchValue,ResultStatusCode,GroupLabel,DetailCount)
SELECT p.GroupKey,p.StatusCode,i.ItemId,i.SearchValue,i.StatusCode,g.GroupLabel,COUNT(d.ItemId)
FROM #Parameters AS p
JOIN dbo.CaseItem AS i ON i.GroupKey=p.GroupKey AND i.StatusCode=p.StatusCode
JOIN dbo.CaseGroup AS g ON g.GroupKey=i.GroupKey
LEFT JOIN dbo.CaseItemDetail AS d ON d.ItemId=i.ItemId
GROUP BY p.GroupKey,p.StatusCode,i.ItemId,i.SearchValue,i.StatusCode,g.GroupLabel;

SET @T2Marker=SYSUTCDATETIME();
INSERT lab.IncidentState(IncidentPhase,MarkerUtc) VALUES(@Phase,@T2Marker);
SET @Start=SYSUTCDATETIME();
DECLARE @GroupKey int,@StatusCode tinyint;
DECLARE parameter_cursor CURSOR LOCAL FAST_FORWARD FOR SELECT GroupKey,StatusCode FROM #Parameters ORDER BY GroupKey,StatusCode;
OPEN parameter_cursor;
FETCH NEXT FROM parameter_cursor INTO @GroupKey,@StatusCode;
WHILE @@FETCH_STATUS=0
BEGIN
    CREATE TABLE #OneResult(ItemId int NOT NULL,SearchValue nvarchar(64) NOT NULL,StatusCode tinyint NOT NULL,GroupLabel nvarchar(64) NOT NULL,DetailCount int NOT NULL);
    INSERT #OneResult EXEC dbo.usp_CaseSearch @GroupKey=@GroupKey,@StatusCode=@StatusCode;
    INSERT #Actual(GroupKey,StatusCode,ItemId,SearchValue,ResultStatusCode,GroupLabel,DetailCount)
        SELECT @GroupKey,@StatusCode,ItemId,SearchValue,StatusCode,GroupLabel,DetailCount FROM #OneResult;
    DROP TABLE #OneResult;
    FETCH NEXT FROM parameter_cursor INTO @GroupKey,@StatusCode;
END;
CLOSE parameter_cursor;
DEALLOCATE parameter_cursor;
SET @DurationMs=DATEDIFF_BIG(millisecond,@Start,SYSUTCDATETIME());

IF EXISTS(SELECT GroupKey,StatusCode,ItemId,SearchValue,ResultStatusCode,GroupLabel,DetailCount FROM #Expected EXCEPT SELECT GroupKey,StatusCode,ItemId,SearchValue,ResultStatusCode,GroupLabel,DetailCount FROM #Actual)
   OR EXISTS(SELECT GroupKey,StatusCode,ItemId,SearchValue,ResultStatusCode,GroupLabel,DetailCount FROM #Actual EXCEPT SELECT GroupKey,StatusCode,ItemId,SearchValue,ResultStatusCode,GroupLabel,DetailCount FROM #Expected)
    THROW 51010, 'FAIL_RESULT_CONTRACT: Die Referenzänderung hat eine Ergebnismenge verändert.', 1;

UPDATE lab.IncidentState SET CompletedUtc=SYSUTCDATETIME() WHERE IncidentPhase=@Phase;
EXEC sys.sp_query_store_flush_db;
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
INSERT lab.IncidentQueryStoreProfile(IncidentPhase,QueryId,PlanId,RuntimeStatsIntervalId,CountExecutions,FirstExecutionUtc,LastExecutionUtc)
SELECT @Phase,q.query_id,p.plan_id,rs.runtime_stats_interval_id,SUM(rs.count_executions),MIN(rs.first_execution_time),MAX(rs.last_execution_time)
FROM EffectiveQuery AS effective
JOIN sys.query_store_query AS q ON q.query_id=effective.query_id
JOIN sys.query_store_plan AS p ON p.query_id=q.query_id
JOIN sys.query_store_runtime_stats AS rs ON rs.plan_id=p.plan_id
JOIN sys.query_store_runtime_stats_interval AS i ON i.runtime_stats_interval_id=rs.runtime_stats_interval_id
JOIN lab.IncidentState AS s ON s.IncidentPhase=@Phase
WHERE rs.execution_type=0 AND rs.count_executions>0
  /* Phasenzuordnung ueber echte Intervalle, nicht ueber millisekundengenaue Runtime-Zeitstempel. */
  AND i.end_time > s.MarkerUtc AND i.start_time <= s.CompletedUtc
GROUP BY q.query_id,p.plan_id,rs.runtime_stats_interval_id;
SELECT @ActualExecutions=COALESCE(SUM(CountExecutions),0) FROM lab.IncidentQueryStoreProfile WHERE IncidentPhase=@Phase;
SELECT @VariantCount=COUNT(DISTINCT qv.query_variant_query_id)
FROM sys.query_store_query AS q
JOIN sys.query_store_query_text AS qt ON qt.query_text_id=q.query_text_id
JOIN sys.query_store_query_variant AS qv ON qv.parent_query_id=q.query_id
WHERE q.object_id=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')
  AND qt.query_sql_text LIKE N'%/* DGN007_CASE_SEARCH */%';
IF @ActualExecutions<>@ExpectedExecutions
BEGIN
    SELECT 2 AS Sequence,'COMPARISON' AS Phase,'T2_PROFILE' AS CheckId,'SKIP' AS Outcome,'SKIP_EVIDENCE_MISSING' AS Code,
           CONCAT(N'Phase=',@Phase,N'; ExpectedExecutions=',@ExpectedExecutions,N'; ActualExecutions=',@ActualExecutions,
                  N'; QueryVariantCount=',@VariantCount) AS ObservedValue,
           CONVERT(nvarchar(20),@ExpectedExecutions) AS RequiredValue,N'Die fachliche Ergebnisgleichheit wurde geprüft, aber T2 ist nicht vollständig im Query Store erfasst.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING'; RETURN;
END;
IF EXISTS(
    SELECT 1 FROM lab.IncidentQueryStoreProfile AS t JOIN sys.query_store_runtime_stats_interval AS ti ON ti.runtime_stats_interval_id=t.RuntimeStatsIntervalId
    CROSS JOIN lab.IncidentQueryStoreProfile AS b JOIN sys.query_store_runtime_stats_interval AS bi ON bi.runtime_stats_interval_id=b.RuntimeStatsIntervalId
    WHERE t.IncidentPhase=@Phase AND b.IncidentPhase IN(N'T0_BASELINE',N'T1_INCIDENT') AND ti.start_time < bi.end_time)
BEGIN
    SELECT 3 AS Sequence,'COMPARISON' AS Phase,'T2_PROFILE' AS CheckId,'SKIP' AS Outcome,'SKIP_EVIDENCE_MISSING' AS Code,
           N'T2 teilt ein Query-Store-Intervall' AS ObservedValue,N'T2 in eigenem Query-Store-Intervall' AS RequiredValue,
           N'Es wird keine Zeit- oder Profilbeziehung über überlappende Intervalle behauptet.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING'; RETURN;
END;
UPDATE lab.Dgn007ReferenceState SET T2Utc=(SELECT CompletedUtc FROM lab.IncidentState WHERE IncidentPhase=@Phase) WHERE StateId=1;
SELECT 6 AS EvidenceLevel,N'COMPARISON' AS EvidenceScope,(SELECT COUNT(*) FROM #Actual) AS ResultRows,@DurationMs AS DurationMs,
       N'vier vorbereitete Parameterklassen, bidirektionaler Mengenvergleich und separates T2-Query-Store-Profil' AS ResultContract;
SELECT 4 AS Sequence,'COMPARISON' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'T2; Rows=',(SELECT COUNT(*) FROM #Actual),N'; DurationMs=',@DurationMs) AS ObservedValue,N'gleiches fachliches Ergebnis bei einer Änderung' AS RequiredValue,
       N'Die Vergleichsausführungen und das getrennte T2-Profil sind erfasst. Absolute Zeiten und Planwahl bleiben empirisch.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
