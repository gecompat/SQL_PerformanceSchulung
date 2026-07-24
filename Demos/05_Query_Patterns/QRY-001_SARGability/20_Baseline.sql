/* QRY-001 baseline: SARGable half-open interval. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Start datetime2(0) = '20240315';
DECLARE @End datetime2(0) = DATEADD(day,1,@Start);
DECLARE @Before bigint;
DECLARE @After bigint;
DECLARE @Result bigint;
DECLARE @Plan nvarchar(max);
DECLARE @AccessMethod varchar(32);

SELECT @Before=logical_reads FROM sys.dm_exec_sessions WHERE session_id=@@SPID;
SELECT @Result=SUM(CONVERT(bigint,MeasureValue))
FROM lab.SearchData /*SQLPERF_QRY001_BASELINE*/
WHERE EventDateTime>=@Start AND EventDateTime<@End;
SELECT @After=logical_reads FROM sys.dm_exec_sessions WHERE session_id=@@SPID;

SELECT TOP(1) @Plan=qp.query_plan
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
CROSS APPLY sys.dm_exec_text_query_plan(qs.plan_handle,qs.statement_start_offset,qs.statement_end_offset) qp
WHERE SUBSTRING(st.text,(qs.statement_start_offset/2)+1,
      CASE WHEN qs.statement_end_offset=-1
           THEN (DATALENGTH(st.text)-qs.statement_start_offset)/2+1
           ELSE (qs.statement_end_offset-qs.statement_start_offset)/2+1 END)
      LIKE '%SQLPERF_QRY001_BASELINE%'
ORDER BY qs.last_execution_time DESC;

SET @AccessMethod=CASE
    WHEN @Plan LIKE '%PhysicalOp="Index Seek"%' THEN 'INDEX_SEEK'
    WHEN @Plan LIKE '%PhysicalOp="Index Scan"%' THEN 'INDEX_SCAN'
    ELSE 'OTHER' END;

DELETE lab.Qry001Evidence WHERE Phase='BASELINE';
INSERT lab.Qry001Evidence(Phase,ResultValue,LogicalReads,AccessMethod)
VALUES('BASELINE',COALESCE(@Result,0),@After-@Before,@AccessMethod);

IF @Result IS NULL OR @AccessMethod<>'INDEX_SEEK'
    THROW 51003, 'FAIL_EXECUTION: Die QRY-001-Baseline liefert keine belastbare Seek-Evidenz.', 1;

SELECT 1 AS Sequence,'BASELINE' AS Phase,'SUMMARY' AS CheckId,
       'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'Result=',@Result,N'; LogicalReads=',@After-@Before,N'; Access=',@AccessMethod) AS ObservedValue,
       N'selektiver Index Seek mit nichtnegativen Reads' AS RequiredValue,
       N'Die SARGable Ausgangsmessung ist erfasst.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
