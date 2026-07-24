/* OPT-013 comparison: identical low-grant query after the ordered index was added. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Checksum int;
DECLARE @LastSpills bigint;
DECLARE @Plan nvarchar(max);
DECLARE @PlanHasSort bit;
DECLARE @ProblemChecksum int;
DECLARE @Tag varchar(64)=CONCAT('SQLPERF_OPT013_','COMPARISON');

SELECT @ProblemChecksum=ResultChecksum FROM lab.SpillEvidence WHERE Phase='PROBLEM';

SELECT @Checksum=CHECKSUM_AGG(BINARY_CHECKSUM(d.SortKey,d.RowNumber))
FROM
(
    SELECT SortKey,
           RowNumber=ROW_NUMBER() OVER(ORDER BY Payload,SortKey)
    FROM lab.SpillData WITH(INDEX(IX_SpillData_Payload_SortKey)) /*SQLPERF_OPT013_COMPARISON*/
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
DELETE lab.SpillEvidence WHERE Phase='COMPARISON';
INSERT lab.SpillEvidence(Phase,ResultChecksum,LastSpills,PlanHasSort)
VALUES('COMPARISON',@Checksum,COALESCE(@LastSpills,-1),@PlanHasSort);

IF @ProblemChecksum IS NULL OR @Checksum<>@ProblemChecksum
    THROW 51006,'FAIL_RESULT_CONTRACT: Die Vergleichsabfrage ist fachlich nicht äquivalent.',1;
IF @LastSpills IS NULL OR @LastSpills<>0 OR @PlanHasSort<>0
    THROW 51006,'FAIL_RESULT_CONTRACT: Der geordnete Zugriffspfad beseitigt Sort und Spill nicht wie erwartet.',1;

SELECT Phase,ResultChecksum,LastSpills,PlanHasSort
FROM lab.SpillEvidence
ORDER BY CASE Phase WHEN 'BASELINE' THEN 1 WHEN 'PROBLEM' THEN 2 ELSE 3 END;

SELECT 1 Sequence,'COMPARISON' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       CONCAT(N'Checksum=',@Checksum,N'; LastSpills=',@LastSpills,N'; Sort=',@PlanHasSort) ObservedValue,
       N'gleiches Ergebnis; last_spills=0; kein Sortoperator' RequiredValue,
       N'Die Zugriffspfad-Gegenmaßnahme ist unter demselben niedrigen Grant bestätigt.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
