SET NOCOUNT ON;
SET QUOTED_IDENTIFIER ON;
SET XACT_ABORT ON;
IF COALESCE(CONVERT(varchar(128),SERVERPROPERTY('ProductVersion')),'')<>'17.0.5065.9'
  THROW 51080,'FAIL_ENGINE_BUILD',1;
IF DB_NAME() <> N'SQLPERF_LAB_DGN007_AUTO'
  OR (SELECT COUNT(*) FROM sys.extended_properties WHERE class=0 AND (
      (name=N'SQLPERF.Project' AND CONVERT(nvarchar(128),value)=N'SQL_PerformanceSchulung')
      OR (name=N'SQLPERF.ContractVersion' AND CONVERT(nvarchar(128),value)=N'1.0')
      OR (name=N'SQLPERF.DemoId' AND CONVERT(nvarchar(128),value)=N'DGN-007')
      OR (name=N'SQLPERF.RunToken' AND CONVERT(nvarchar(128),value)=N'AUTO')))<>4
  THROW 51081,'FAIL_OWNERSHIP',1;
CREATE TABLE #answers(ItemId int, SearchValue nvarchar(64), StatusCode tinyint, GroupLabel nvarchar(64), DetailCount int);
CREATE TABLE #reference(
    InputGroup int NOT NULL, ItemId int NOT NULL, SearchValue nvarchar(64),
    StatusCode tinyint, GroupLabel nvarchar(64), DetailCount int,
    PRIMARY KEY (InputGroup, ItemId)
);
DECLARE @phase tinyint=1, @ordinal tinyint, @group int, @status tinyint, @expected int;
DECLARE @profiles table (Trial int, Sample int, CompiledClass varchar(10), PlanHash binary(8), ExecCount bigint, Reads bigint, PhysicalReads bigint, PRIMARY KEY (Trial, Sample));
DECLARE @positiveBefore bigint=COALESCE((
    SELECT waiting_tasks_count FROM sys.dm_exec_session_wait_stats
    WHERE session_id=@@SPID AND wait_type=N'WAITFOR'),0);
WAITFOR DELAY '00:00:00.050';
IF COALESCE((SELECT waiting_tasks_count FROM sys.dm_exec_session_wait_stats
             WHERE session_id=@@SPID AND wait_type=N'WAITFOR'),0)<=@positiveBefore
    THROW 51095,'NOT_PROVEN: wait telemetry positive control failed',1;
DECLARE @memoryBefore bigint,@ioBefore bigint,@memoryAfter bigint,@ioAfter bigint,@actual int;
DECLARE @waitDeltas table (MemWait bigint, IOWait bigint);
WHILE @phase <= 2
BEGIN
    EXEC sys.sp_recompile N'dbo.usp_CaseSearch';
    SET @ordinal=1;
    WHILE @ordinal<=2
    BEGIN
        SELECT @group=CASE WHEN @phase=@ordinal THEN 8 ELSE 1 END, @status=3;
        SET @expected = CASE @group WHEN 8 THEN 228 ELSE 2286 END;
        TRUNCATE TABLE #answers;
        SELECT @memoryBefore=COALESCE(SUM(CASE WHEN wait_type LIKE N'RESOURCE[_]SEMAPHORE%' THEN waiting_tasks_count END),0),
               @ioBefore=COALESCE(SUM(CASE WHEN wait_type LIKE N'PAGEIOLATCH[_]%' THEN waiting_tasks_count END),0)
        FROM sys.dm_exec_session_wait_stats WHERE session_id=@@SPID;
        INSERT #answers EXEC dbo.usp_CaseSearch @GroupKey=@group,@StatusCode=@status;
        SET @actual=@@ROWCOUNT;
        SELECT @memoryAfter=COALESCE(SUM(CASE WHEN wait_type LIKE N'RESOURCE[_]SEMAPHORE%' THEN waiting_tasks_count END),0),
               @ioAfter=COALESCE(SUM(CASE WHEN wait_type LIKE N'PAGEIOLATCH[_]%' THEN waiting_tasks_count END),0)
        FROM sys.dm_exec_session_wait_stats WHERE session_id=@@SPID;
        IF @memoryAfter<@memoryBefore OR @ioAfter<@ioBefore THROW 51096,'NOT_PROVEN: wait counters moved backwards',1;
        INSERT @waitDeltas VALUES(@memoryAfter-@memoryBefore,@ioAfter-@ioBefore);
        IF @actual<>@expected THROW 51082,'FAIL_RESULT',1;
        IF @phase=1
            INSERT #reference SELECT @group, ItemId, SearchValue, StatusCode, GroupLabel, DetailCount FROM #answers;
        ELSE IF EXISTS (
            SELECT ItemId, SearchValue, StatusCode, GroupLabel, DetailCount FROM #answers
            EXCEPT
            SELECT ItemId, SearchValue, StatusCode, GroupLabel, DetailCount FROM #reference WHERE InputGroup=@group
        ) OR EXISTS (
            SELECT ItemId, SearchValue, StatusCode, GroupLabel, DetailCount FROM #reference WHERE InputGroup=@group
            EXCEPT
            SELECT ItemId, SearchValue, StatusCode, GroupLabel, DetailCount FROM #answers
        )
            THROW 51082,'FAIL_RESULT',1;

        ;WITH XMLNAMESPACES(DEFAULT 'http://schemas.microsoft.com/sqlserver/2004/07/showplan')
        INSERT @profiles
        SELECT @phase,@ordinal,
            CASE n.x.value('@ParameterCompiledValue','varchar(20)') WHEN '(8)' THEN 'A'
                WHEN '(1)' THEN 'B' ELSE 'UNKNOWN' END,
            qs.query_plan_hash, qs.execution_count, qs.total_logical_reads, qs.total_physical_reads
        FROM sys.dm_exec_query_stats AS qs
        CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS t
        CROSS APPLY sys.dm_exec_text_query_plan(qs.plan_handle,qs.statement_start_offset,qs.statement_end_offset) AS tp
        CROSS APPLY (SELECT TRY_CONVERT(xml,tp.query_plan) AS x) AS p
        CROSS APPLY p.x.nodes('//StmtSimple/QueryPlan/ParameterList/ColumnReference[@Column="@GroupKey"]') AS n(x)
        WHERE t.dbid=DB_ID() AND t.objectid=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')
            AND SUBSTRING(t.text,qs.statement_start_offset/2+1,
                (CASE WHEN qs.statement_end_offset<0 THEN DATALENGTH(t.text) ELSE qs.statement_end_offset END - qs.statement_start_offset)/2+1)
                LIKE N'%/* DGN007_CASE_SEARCH */%';
        SET @ordinal+=1;
    END;
    SET @phase+=1;
END;
IF (SELECT COUNT(*) FROM @profiles)<>4
   OR EXISTS (
       SELECT 1 FROM @profiles
       WHERE ExecCount<>Sample OR PlanHash IS NULL OR PhysicalReads IS NULL OR PhysicalReads<0
          OR CompiledClass<>CASE Trial WHEN 1 THEN 'A' ELSE 'B' END
   )
   OR EXISTS (SELECT Trial FROM @profiles GROUP BY Trial HAVING COUNT(DISTINCT PlanHash)<>1)
   OR (SELECT COUNT(DISTINCT PlanHash) FROM @profiles)<>2
    THROW 51083,'NOT_PROVEN: compiled parameter or plan reuse evidence is incomplete',1;
DECLARE @AWithA bigint=(SELECT Reads FROM @profiles WHERE Trial=1 AND Sample=1);
DECLARE @BWithA bigint=(SELECT Reads FROM @profiles WHERE Trial=1 AND Sample=2)-@AWithA;
DECLARE @BWithB bigint=(SELECT Reads FROM @profiles WHERE Trial=2 AND Sample=1);
DECLARE @AWithB bigint=(SELECT Reads FROM @profiles WHERE Trial=2 AND Sample=2)-@BWithB;
IF COALESCE(@AWithA,0)<=0 OR COALESCE(@BWithB,0)<=0 OR COALESCE(@AWithB,0)<=@AWithA OR COALESCE(@BWithA,0)<=@BWithB
    THROW 51085,'NOT_PROVEN: per-request logical reads do not follow the compile context',1;
SELECT 'DGN007_COMPILE_VALUE|PASS|two_compile_values;two_plan_hashes;two_reused_executions;logical_reads_follow_compile_context' AS Evidence;
SELECT CONCAT('DGN007_WAIT_CONTEXT|',COUNT(*),'|',
 CASE WHEN SUM(MemWait)=0 THEN 'no_grant_wait' ELSE 'grant_wait_present' END,'|',
 CASE WHEN SUM(IOWait)=0 THEN 'no_page_io_wait' ELSE 'io_wait_present' END,'|',
 CASE WHEN NOT EXISTS(SELECT 1 FROM @profiles WHERE PhysicalReads<>0)
      THEN 'no_physical_reads' ELSE 'physical_reads_present' END) FROM @waitDeltas;
