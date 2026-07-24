/* OPT-013 demonstration: same ordered result with an intentionally restricted grant. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Checksum int;
DECLARE @LastSpills bigint;
DECLARE @Plan nvarchar(max);
DECLARE @PlanHasSort bit;
DECLARE @Tag varchar(64)=CONCAT('SQLPERF_OPT013_','PROBLEM');

SELECT @Checksum=CHECKSUM_AGG(BINARY_CHECKSUM(d.SortKey,d.RowNumber))
FROM
(
    SELECT SortKey,
           RowNumber=ROW_NUMBER() OVER(ORDER BY Payload,SortKey)
    FROM lab.SpillData /*SQLPERF_OPT013_PROBLEM*/
) d
OPTION(MAXDOP 1,MAX_GRANT_PERCENT=0.1);

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
DELETE lab.SpillEvidence WHERE Phase='PROBLEM';
INSERT lab.SpillEvidence(Phase,ResultChecksum,LastSpills,PlanHasSort)
VALUES('PROBLEM',@Checksum,COALESCE(@LastSpills,-1),@PlanHasSort);

IF @Checksum IS NULL OR @LastSpills IS NULL OR @LastSpills<=0 OR @PlanHasSort<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Der kontrollierte OPT-013-Problemzustand zeigt keinen Sort-Spill.',1;

SELECT 1 Sequence,'DEMONSTRATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       CONCAT(N'Checksum=',@Checksum,N'; LastSpills=',@LastSpills,N'; Sort=',@PlanHasSort) ObservedValue,
       N'gleicher Sortoperator; last_spills>0' RequiredValue,
       N'Der niedrige nutzbare Grant erzeugt den kontrollierten Spill.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
