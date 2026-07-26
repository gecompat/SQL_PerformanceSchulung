/* OPT-015 mitigation: refresh only the statistic that supports the investigated predicate. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

UPDATE STATISTICS lab.WorkItem IX_WorkItem_EntityGroupId WITH FULLSCAN;
EXEC sys.sp_recompile N'lab.usp_Opt015Workload';

DECLARE @ObjectId int;
DECLARE @StatsId int;
DECLARE @Rows bigint;
DECLARE @RowsSampled bigint;
DECLARE @ModificationCounter bigint;

SELECT @ObjectId = o.object_id
FROM sys.objects AS o
INNER JOIN sys.schemas AS s ON s.schema_id = o.schema_id
WHERE s.name = N'lab' AND o.name = N'WorkItem' AND o.type = 'U';
SELECT @StatsId = st.stats_id
FROM sys.stats AS st
WHERE st.object_id = @ObjectId AND st.name = N'IX_WorkItem_EntityGroupId';
SELECT @Rows = sp.rows, @RowsSampled = sp.rows_sampled, @ModificationCounter = sp.modification_counter
FROM sys.dm_db_stats_properties(@ObjectId, @StatsId) AS sp;

IF @Rows <> 260000 OR @RowsSampled <> @Rows OR COALESCE(@ModificationCounter, -1) <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die gezielte OPT-015-Statistikaktualisierung ist nicht vollständig nachweisbar.', 1;

SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'StatisticsRows=', @Rows, N'; RowsSampled=', @RowsSampled, N'; ModificationCounter=', @ModificationCounter) AS ObservedValue,
       N'ausschließlich IX_WorkItem_EntityGroupId per Fullscan aktualisiert; objektbezogene Recompilation' AS RequiredValue,
       N'Die für die Hypothese relevante Statistik ist aktualisiert.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
