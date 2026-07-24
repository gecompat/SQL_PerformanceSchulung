/* OPT-013 comparison: identical sort after the filter statistic was refreshed. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Checksum int;
DECLARE @LastSpills bigint;
DECLARE @Plan nvarchar(max);
DECLARE @PlanHasSort bit;
DECLARE @ProblemChecksum int;
DECLARE @Tag varchar(64)=CONCAT('SQLPERF_OPT013_','COMPARISON');
DECLARE @ObjectId int=OBJECT_ID(N'lab.SpillData');
DECLARE @StatsId int=(SELECT stats_id FROM sys.stats WHERE object_id=@ObjectId AND name=N'ST_SpillData_FilterKey');
DECLARE @StatisticsRows bigint,@RowsSampled bigint,@ModificationCounter bigint,@ActualRows bigint;

SELECT @ProblemChecksum=ResultChecksum FROM lab.SpillEvidence WHERE Phase='PROBLEM';
SELECT @ActualRows=COUNT_BIG(*) FROM lab.SpillData WHERE FilterKey=1;
SELECT @StatisticsRows=rows,@RowsSampled=rows_sampled,@ModificationCounter=modification_counter
FROM sys.dm_db_stats_properties(@ObjectId,@StatsId);

SELECT @Checksum=CHECKSUM_AGG(BINARY_CHECKSUM(d.SortKey,d.RowNumber))
FROM
(
    SELECT SortKey,
           RowNumber=ROW_NUMBER() OVER(ORDER BY Payload,SortKey)
    FROM lab.SpillData /*SQLPERF_OPT013_COMPARISON*/
    WHERE FilterKey=1
) d
OPTION(MAXDOP 1);

SELECT TOP(1)
    @LastSpills=qs.last_spills,
    @Plan=qp.query_plan
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
CROSS APPLY sys.dm_exec_text_query_plan(qs.plan_handle,qs.statement_start_offset,qs.statement_end_offset) qp
CROSS APPLY
(
    VALUES
    (
        SUBSTRING(st.text,(qs.statement_start_offset/2)+1,
        CASE WHEN qs.statement_end_offset=-1
             THEN (DATALENGTH(st.text)-qs.statement_start_offset)/2+1
             ELSE (qs.statement_end_offset-qs.statement_start_offset)/2+1 END)
    )
) statement_text(value)
WHERE statement_text.value LIKE '%'+@Tag+'%'
ORDER BY qs.last_execution_time DESC;

SET @PlanHasSort=CASE WHEN @Plan LIKE '%PhysicalOp="Sort"%' THEN 1 ELSE 0 END;
DELETE lab.SpillEvidence WHERE Phase='COMPARISON';
INSERT lab.SpillEvidence
(
    Phase,ResultChecksum,LastSpills,PlanHasSort,StatisticsRows,StatisticsRowsSampled,
    ModificationCounter,ActualFilteredRows
)
VALUES
(
    'COMPARISON',@Checksum,COALESCE(@LastSpills,-1),@PlanHasSort,@StatisticsRows,@RowsSampled,
    @ModificationCounter,@ActualRows
);

IF @ProblemChecksum IS NULL OR @Checksum<>@ProblemChecksum OR @ActualRows<>299000
    THROW 51006,'FAIL_RESULT_CONTRACT: Die Vergleichsabfrage ist fachlich nicht äquivalent.',1;
IF @StatisticsRows<>300000 OR @RowsSampled<>300000 OR @ModificationCounter<>0
    THROW 51006,'FAIL_RESULT_CONTRACT: Die Vergleichsabfrage verwendet keinen vollständig aktuellen Statistikzustand.',1;
IF @LastSpills IS NULL OR @LastSpills<>0 OR @PlanHasSort<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Der Sort verschüttet trotz aktualisierter Statistik weiterhin oder die Planform ist unerwartet.',1;

SELECT
    Phase,ResultChecksum,LastSpills,PlanHasSort,StatisticsRows,StatisticsRowsSampled,
    ModificationCounter,ActualFilteredRows
FROM lab.SpillEvidence
ORDER BY CASE Phase WHEN 'BASELINE' THEN 1 WHEN 'PROBLEM' THEN 2 ELSE 3 END;

SELECT 1 Sequence,'COMPARISON' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       CONCAT(N'Checksum=',@Checksum,N'; StatsRows=',@StatisticsRows,
              N'; Modifications=',@ModificationCounter,N'; LastSpills=',@LastSpills) ObservedValue,
       N'gleiches Ergebnis; aktuelle Fullscan-Statistik; Sortoperator; last_spills=0' RequiredValue,
       N'Die Statistikaktualisierung beseitigt den kontrollierten Undergrant und Spill.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
