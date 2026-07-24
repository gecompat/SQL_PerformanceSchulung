/* OPT-013 demonstration: identical result under a deliberately stale filter statistic. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Checksum int;
DECLARE @LastSpills bigint;
DECLARE @LastGrantKb bigint;
DECLARE @LastUsedGrantKb bigint;
DECLARE @LastRows bigint;
DECLARE @Plan nvarchar(max);
DECLARE @PlanHasSort bit;
DECLARE @Tag varchar(64)=CONCAT('SQLPERF_OPT013_','PROBLEM');
DECLARE @ObjectId int=OBJECT_ID(N'lab.SpillData');
DECLARE @StatsId int=(SELECT stats_id FROM sys.stats WHERE object_id=OBJECT_ID(N'lab.SpillData') AND name=N'ST_SpillData_FilterKey');
DECLARE @StatisticsRows bigint,@RowsSampled bigint,@ModificationCounter bigint,@ActualRows bigint;

DELETE FROM lab.SpillData WHERE FilterKey=1;
UPDATE STATISTICS lab.SpillData ST_SpillData_FilterKey WITH FULLSCAN,NORECOMPUTE;

;WITH Digits AS
(
    SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) d(n)
), Numbers AS
(
    SELECT TOP(300000)
        n=1+d0.n+d1.n*10+d2.n*100+d3.n*1000+d4.n*10000+d5.n*100000
    FROM Digits d0 CROSS JOIN Digits d1 CROSS JOIN Digits d2
    CROSS JOIN Digits d3 CROSS JOIN Digits d4 CROSS JOIN Digits d5
    ORDER BY 1
)
INSERT lab.SpillData(SpillDataId,FilterKey,SortKey,Payload,MeasureValue)
SELECT n,
       1,
       CONVERT(int,(CONVERT(bigint,n)*7919)%300000),
       CONVERT(char(200),REPLICATE(CHAR(65+(n%26)),180)+RIGHT(REPLICATE('0',20)+CONVERT(varchar(20),n),20)),
       n%10000
FROM Numbers
WHERE n>1000
OPTION(MAXDOP 1);

SELECT @ActualRows=COUNT_BIG(*) FROM lab.SpillData WHERE FilterKey=1;
SELECT @StatisticsRows=rows,@RowsSampled=rows_sampled,@ModificationCounter=modification_counter
FROM sys.dm_db_stats_properties(@ObjectId,@StatsId);

SELECT @Checksum=CHECKSUM_AGG(BINARY_CHECKSUM(d.SortKey,d.RowNumber))
FROM
(
    SELECT SortKey,
           RowNumber=ROW_NUMBER() OVER(ORDER BY Payload,SortKey)
    FROM lab.SpillData /*SQLPERF_OPT013_PROBLEM*/
    WHERE FilterKey=1
) d
OPTION(MAXDOP 1);

SELECT TOP(1)
    @LastSpills=qs.last_spills,
    @LastGrantKb=qs.last_grant_kb,
    @LastUsedGrantKb=qs.last_used_grant_kb,
    @LastRows=qs.last_rows,
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
DELETE lab.SpillEvidence WHERE Phase='PROBLEM';
INSERT lab.SpillEvidence
(
    Phase,ResultChecksum,LastSpills,PlanHasSort,StatisticsRows,StatisticsRowsSampled,
    ModificationCounter,ActualFilteredRows
)
VALUES
(
    'PROBLEM',@Checksum,COALESCE(@LastSpills,-1),@PlanHasSort,@StatisticsRows,@RowsSampled,
    @ModificationCounter,@ActualRows
);

SELECT
    Diagnostic=N'OPT013_PROBLEM_STATE',
    ActualFilteredRows=@ActualRows,
    StatisticsRows=@StatisticsRows,
    StatisticsRowsSampled=@RowsSampled,
    ModificationCounter=@ModificationCounter,
    LastRows=@LastRows,
    LastGrantKb=@LastGrantKb,
    LastUsedGrantKb=@LastUsedGrantKb,
    LastSpills=@LastSpills,
    PlanHasSort=@PlanHasSort;

IF @Checksum IS NULL OR @ActualRows<>299000 OR @StatisticsRows<>1000
   OR @ModificationCounter<299000 OR @LastSpills IS NULL OR @LastSpills<=0 OR @PlanHasSort<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Der kontrollierte OPT-013-Problemzustand zeigt keine veraltete Statistik mit Sort-Spill.',1;

SELECT 1 Sequence,'DEMONSTRATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       CONCAT(N'ActualRows=',@ActualRows,N'; StatsRows=',@StatisticsRows,N'; Modifications=',@ModificationCounter,N'; LastSpills=',@LastSpills) ObservedValue,
       N'identische 299000 Zielzeilen; Statistikstand 1000 Zeilen; positive Modifikationen; last_spills>0' RequiredValue,
       N'Die veraltete Filterstatistik erzeugt den kontrollierten Undergrant und Sort-Spill.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
