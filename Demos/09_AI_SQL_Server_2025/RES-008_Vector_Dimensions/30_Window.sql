/* RES-008: begrenzte synthetische float32-Quellen-/Dimensions-/Storagevorbereitung. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @RawDemo nvarchar(max)=N'$(DemoId)',@RawRun nvarchar(max)=N'$(RunToken)',@RawTarget nvarchar(max)=N'$(TargetDatabase)';
IF DATALENGTH(@RawDemo)<>14 OR CONVERT(varbinary(max),@RawDemo)<>CONVERT(varbinary(max),N'RES-008')
 OR DATALENGTH(@RawRun) NOT BETWEEN 2 AND 32 OR @RawRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
 OR DATALENGTH(@RawTarget)<>DATALENGTH(N'SQLPERF_LAB_RES008_'+@RawRun)
 OR CONVERT(varbinary(max),@RawTarget)<>CONVERT(varbinary(max),N'SQLPERF_LAB_RES008_'+@RawRun)
 THROW 51000,'FAIL_CONTRACT: Vollstaendige Demo-/Run-/Zielbindung verletzt.',1;
DECLARE @DemoId varchar(7)=CONVERT(varchar(7),@RawDemo),@RunToken varchar(16)=CONVERT(varchar(16),@RawRun),@TargetDatabase sysname=CONVERT(sysname,@RawTarget);
DECLARE @Sql nvarchar(max),@Matches int;
IF DB_ID(@TargetDatabase) IS NOT NULL
BEGIN
 SET @Sql=N'SELECT @M=COUNT(*) FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties p
 JOIN (VALUES(N''SQLPERF.Project'',N''SQL_PerformanceSchulung''),
 (N''SQLPERF.ContractVersion'',N''1.0''),(N''SQLPERF.DemoId'',CONVERT(nvarchar(max),@D)),
 (N''SQLPERF.RunToken'',CONVERT(nvarchar(max),@R))) e(Name,Value)
 ON DATALENGTH(p.name)=DATALENGTH(e.Name) AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 WHERE p.class=0 AND p.major_id=0 AND p.minor_id=0
 AND DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Value)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=CONVERT(varbinary(max),e.Value);';
 EXEC sys.sp_executesql @Sql,N'@D varchar(7),@R varchar(16),@M int OUTPUT',@D=@DemoId,@R=@RunToken,@M=@Matches OUTPUT;
 IF @Matches<>4 THROW 51004,'FAIL_STATE: Vollstaendige bytegenaue Eigentumsmarker fehlen.',1;
END;
IF DATALENGTH(DB_NAME())<>DATALENGTH(@TargetDatabase) OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),@TargetDatabase) OR DB_ID(@TargetDatabase) IS NULL THROW 51004,'FAIL_STATE: Falscher Datenbankkontext.',1;

DECLARE @Dimension int=$(Dimension),@Statements int=$(Statements),@Negative int=$(Negative);
IF @Dimension NOT IN(32,384,768,1536) OR @Statements NOT IN(1,100) OR @Negative NOT IN(0,1)
 THROW 51000,'FAIL_CONTRACT: Fixed measurement inputs required.',1;
DECLARE @Session int=@@SPID,@Db int=DB_ID(),@Request int,@RequestStarted datetime,
 @Connection uniqueidentifier,@Cpu0 bigint,@Cpu1 bigint,@Reads0 bigint,@Reads1 bigint,
 @Logical0 bigint,@Logical1 bigint,@Writes0 bigint,@Writes1 bigint,
 @Started datetime2(7),@Ended datetime2(7),@Ordinal int=1;
SELECT @Request=request_id,@RequestStarted=start_time,@Connection=connection_id
 FROM sys.dm_exec_requests WHERE session_id=@Session AND database_id=@Db;
IF @@ROWCOUNT<>1 OR @Request IS NULL OR @RequestStarted IS NULL OR @Connection IS NULL
 THROW 51003,'FAIL_STATE: Actual request identity missing.',1;
CREATE TABLE #MeasuredRows(QueryOrdinal int NOT NULL PRIMARY KEY,Id int NOT NULL,DistanceValue float NOT NULL);
DECLARE @Q32 VECTOR(32)=CONVERT(VECTOR(32),'[1,1'+REPLICATE(',0',32-2)+']');
DECLARE @Q384 VECTOR(384)=CONVERT(VECTOR(384),'[1,1'+REPLICATE(',0',384-2)+']');
DECLARE @Q768 VECTOR(768)=CONVERT(VECTOR(768),'[1,1'+REPLICATE(',0',768-2)+']');
DECLARE @Q1536 VECTOR(1536)=CONVERT(VECTOR(1536),'[1,1'+REPLICATE(',0',1536-2)+']');

SELECT @Cpu0=CONVERT(bigint,cpu_time),@Reads0=CONVERT(bigint,reads),
 @Logical0=CONVERT(bigint,logical_reads),@Writes0=CONVERT(bigint,writes)
 FROM sys.dm_exec_requests WHERE session_id=@Session AND request_id=@Request
 AND start_time=@RequestStarted AND connection_id=@Connection AND database_id=@Db;
IF @@ROWCOUNT<>1 OR @Cpu0 IS NULL OR @Reads0 IS NULL OR @Logical0 IS NULL OR @Writes0 IS NULL
 OR @Cpu0<0 OR @Reads0<0 OR @Logical0<0 OR @Writes0<0
 THROW 51003,'FAIL_STATE: Actual initial counters missing.',1;
SET @Started=SYSUTCDATETIME();
WHILE @Ordinal<=@Statements
BEGIN
 IF @Dimension=32
  INSERT #MeasuredRows SELECT TOP(1) @Ordinal,Id,VECTOR_DISTANCE('cosine',V,@Q32) FROM lab.V32
  ORDER BY VECTOR_DISTANCE('cosine',V,@Q32),Id OPTION(MAXDOP 1);
 ELSE IF @Dimension=384
  INSERT #MeasuredRows SELECT TOP(1) @Ordinal,Id,VECTOR_DISTANCE('cosine',V,@Q384) FROM lab.V384
  ORDER BY VECTOR_DISTANCE('cosine',V,@Q384),Id OPTION(MAXDOP 1);
 ELSE IF @Dimension=768
  INSERT #MeasuredRows SELECT TOP(1) @Ordinal,Id,VECTOR_DISTANCE('cosine',V,@Q768) FROM lab.V768
  ORDER BY VECTOR_DISTANCE('cosine',V,@Q768),Id OPTION(MAXDOP 1);
 ELSE IF @Dimension=1536
  INSERT #MeasuredRows SELECT TOP(1) @Ordinal,Id,VECTOR_DISTANCE('cosine',V,@Q1536) FROM lab.V1536
  ORDER BY VECTOR_DISTANCE('cosine',V,@Q1536),Id OPTION(MAXDOP 1);

 SET @Ordinal+=1;
END;
SET @Ended=SYSUTCDATETIME();
SELECT @Cpu1=CONVERT(bigint,cpu_time),@Reads1=CONVERT(bigint,reads),
 @Logical1=CONVERT(bigint,logical_reads),@Writes1=CONVERT(bigint,writes)
 FROM sys.dm_exec_requests WHERE session_id=@Session AND request_id=@Request
 AND start_time=@RequestStarted AND connection_id=@Connection AND database_id=@Db;
IF @@ROWCOUNT<>1 OR @Cpu1 IS NULL OR @Reads1 IS NULL OR @Logical1 IS NULL OR @Writes1 IS NULL
 OR @Cpu1<@Cpu0 OR @Reads1<@Reads0 OR @Logical1<@Logical0 OR @Writes1<@Writes0 OR @Ended<@Started
 THROW 51003,'FAIL_STATE: Actual final counters missing.',1;
IF @Negative=1 UPDATE #MeasuredRows SET Id=2 WHERE QueryOrdinal=1;
IF (SELECT COUNT(*) FROM #MeasuredRows)<>@Statements
 OR EXISTS(SELECT 1 FROM #MeasuredRows WHERE QueryOrdinal NOT BETWEEN 1 AND @Statements
 OR Id<>1 OR DistanceValue IS NULL OR ABS(DistanceValue)>0.000001)
 THROW 51003,'FAIL_RESULT_CONTRACT: Actual per-query oracle violated.',1;
DECLARE @Before nvarchar(max)=(SELECT @Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,
 @Connection ConnectionId,@Db DatabaseId,@Cpu0 CpuMs,@Reads0 Reads,@Logical0 LogicalReads,@Writes0 Writes FOR JSON PATH,WITHOUT_ARRAY_WRAPPER),
 @After nvarchar(max)=(SELECT @Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,
 @Connection ConnectionId,@Db DatabaseId,@Cpu1 CpuMs,@Reads1 Reads,@Logical1 LogicalReads,@Writes1 Writes FOR JSON PATH,WITHOUT_ARRAY_WRAPPER),
 @Queries nvarchar(max)=(SELECT QueryOrdinal Ordinal,Id,DistanceValue FROM #MeasuredRows ORDER BY QueryOrdinal FOR JSON PATH);
DECLARE @Output nvarchar(max)=(SELECT @Dimension Dimension,@Statements Statements,
 @Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
 @Cpu1-@Cpu0 CpuMs,@Reads1-@Reads0 Reads,@Logical1-@Logical0 LogicalReads,@Writes1-@Writes0 Writes,
 DATEDIFF_BIG(microsecond,@Started,@Ended) ElapsedUs,CONVERT(nvarchar(30),@Started,126) StartedUtc,
 CONVERT(nvarchar(30),@Ended,126) EndedUtc,JSON_QUERY(@Before) CountersBefore,
 JSON_QUERY(@After) CountersAfter,JSON_QUERY(@Queries) Queries FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
IF @Output IS NULL OR DATALENGTH(@Output)>100000 THROW 51003,'FAIL_RESULT_CONTRACT: Bounded actual evidence missing.',1;
DECLARE @Chars int=LEN(@Output),@Part int=1,@Parts int=(LEN(@Output)+199)/200;
WHILE @Part<=@Parts
BEGIN
 SELECT CONVERT(varchar(256),'RES008_WINDOWPART|'+CONVERT(varchar(10),@Part)+'|'
 +CONVERT(varchar(10),@Parts)+'|'+CONVERT(varchar(10),@Chars)+'|'
 +CONVERT(varchar(200),SUBSTRING(@Output,(@Part-1)*200+1,200)));
 SET @Part+=1;
END;
SELECT 'SQLPERF_SUMMARY|PASS|OK';
