/* OPT-013 baseline: correct filter statistics and an adequate sort grant. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Checksum int;
DECLARE @LastSpills bigint;
DECLARE @Plan nvarchar(max);
DECLARE @PlanHasSort bit;
DECLARE @Tag varchar(64)=CONCAT('SQLPERF_OPT013_','BASELINE');
DECLARE @ObjectId int=OBJECT_ID(N'lab.SpillData');
DECLARE @StatsId int=(SELECT stats_id FROM sys.stats WHERE object_id=OBJECT_ID(N'lab.SpillData') AND name=N'ST_SpillData_FilterKey');
DECLARE @StatisticsRows bigint,@RowsSampled bigint,@ModificationCounter bigint,@ActualRows bigint;

SELECT @ActualRows=COUNT_BIG(*) FROM lab.SpillData WHERE FilterKey=1;
SELECT @StatisticsRows=rows,@RowsSampled=rows_sampled,@ModificationCounter=modification_counter
FROM sys.dm_db_stats_properties(@ObjectId,@StatsId);

SELECT @Checksum=CHECKSUM_AGG(BINARY_CHECKSUM(d.SortKey,d.RowNumber))
FROM
(
    SELECT SortKey,
           RowNumber=ROW_NUMBER() OVER(ORDER BY Payload,SortKey)
    FROM lab.SpillData /*SQLPERF_OPT013_BASELINE*/
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
DELETE lab.SpillEvidence WHERE Phase='BASELINE';
INSERT lab.SpillEvidence
(
    Phase,ResultChecksum,LastSpills,PlanHasSort,StatisticsRows,StatisticsRowsSampled,
    ModificationCounter,ActualFilteredRows
)
VALUES
(
    'BASELINE',@Checksum,COALESCE(@LastSpills,-1),@PlanHasSort,@StatisticsRows,@RowsSampled,
    @ModificationCounter,@ActualRows
);

IF @Checksum IS NULL OR @ActualRows<>299000 OR @StatisticsRows<>300000
   OR @ModificationCounter<>0 OR @LastSpills IS NULL OR @LastSpills<>0 OR @PlanHasSort<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Die OPT-013-Baseline besitzt nicht die erwartete aktuelle Statistik und den nicht verschütteten Sort.',1;

SELECT 1 Sequence,'BASELINE' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       CONCAT(N'ActualRows=',@ActualRows,N'; StatsRows=',@StatisticsRows,N'; Modifications=',@ModificationCounter,N'; LastSpills=',@LastSpills) ObservedValue,
       N'aktuelle Statistik; Sortoperator; last_spills=0' RequiredValue,
       N'Die Baseline mit korrekter Kardinalitätsgrundlage ist erfasst.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
