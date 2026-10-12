/* DGN-010: begrenzte synthetische Quellen- und Indexmessung. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @RawDemo nvarchar(max)=N'$(DemoId)',@RawRun nvarchar(max)=N'$(RunToken)',@RawTarget nvarchar(max)=N'$(TargetDatabase)';
IF DATALENGTH(@RawDemo)<>14 OR CONVERT(varbinary(max),@RawDemo)<>CONVERT(varbinary(max),N'DGN-010')
 OR DATALENGTH(@RawRun) NOT BETWEEN 2 AND 32 OR @RawRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
 OR DATALENGTH(@RawTarget)<>DATALENGTH(N'SQLPERF_LAB_DGN010_'+@RawRun)
 OR CONVERT(varbinary(max),@RawTarget)<>CONVERT(varbinary(max),N'SQLPERF_LAB_DGN010_'+@RawRun)
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
DECLARE @Path int=$(Path),@Statements int=$(Statements),@Negative int=$(Negative),@RawLabel nvarchar(max)=N'$(Label)';
IF @Path NOT IN(0,1) OR @Statements NOT IN(1,100) OR @Negative NOT IN(0,1)
 OR DATALENGTH(@RawLabel) NOT BETWEEN 2 AND 64 OR @RawLabel COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9_]%'
 THROW 51000,'FAIL_CONTRACT: Fixed bounded DML inputs required.',1;
IF @@TRANCOUNT<>0 THROW 51003,'FAIL_STATE: Own outer transaction must be absent.',1;
IF (SELECT COUNT(*) FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') AND name=N'DGN010_OwnPK' AND is_disabled=0 AND is_hypothetical=0 AND has_filter=0)<>1
 OR (SELECT COUNT(*) FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') AND name=N'DGN010_OwnCandidate')<>@Path
 OR EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') AND name=N'DGN010_OwnCandidate' AND (is_disabled=1 OR is_hypothetical=1 OR has_filter=1))
 THROW 51003,'FAIL_STATE: Actual fixed own index state differs.',1;
DECLARE @Session int=@@SPID,@Db int=DB_ID(),@Request int,@RequestStarted datetime,@Connection uniqueidentifier,
 @Cpu0 bigint,@Cpu1 bigint,@Reads0 bigint,@Reads1 bigint,@Logical0 bigint,@Logical1 bigint,@Writes0 bigint,@Writes1 bigint,
 @Started datetime2(7),@Ended datetime2(7),@Ordinal int=1,@TransactionBefore int=@@TRANCOUNT,@TransactionAfter int;
SELECT @Request=request_id,@RequestStarted=start_time,@Connection=connection_id
 FROM sys.dm_exec_requests WHERE session_id=@Session AND database_id=@Db;
IF @@ROWCOUNT<>1 OR @Request IS NULL OR @RequestStarted IS NULL OR @Connection IS NULL
 THROW 51003,'FAIL_STATE: Actual own request identity missing.',1;
DECLARE @MeasuredRows TABLE(QueryOrdinal int,Id int,Value int,Payload varchar(100),PRIMARY KEY(QueryOrdinal,Id));
SELECT @Cpu0=CONVERT(bigint,cpu_time),@Reads0=CONVERT(bigint,reads),@Logical0=CONVERT(bigint,logical_reads),@Writes0=CONVERT(bigint,writes)
 FROM sys.dm_exec_requests WHERE session_id=@Session AND request_id=@Request AND database_id=@Db AND start_time=@RequestStarted AND connection_id=@Connection;
IF @@ROWCOUNT<>1 OR @Cpu0 IS NULL OR @Reads0 IS NULL OR @Logical0 IS NULL OR @Writes0 IS NULL OR @Cpu0<0 OR @Reads0<0 OR @Logical0<0 OR @Writes0<0
 THROW 51003,'FAIL_STATE: Actual initial counters missing.',1;
SET @Started=SYSUTCDATETIME();
BEGIN TRY
 BEGIN TRANSACTION;
 WHILE @Ordinal<=@Statements
 BEGIN
  UPDATE lab.SourceRows SET Value=Value+1
   OUTPUT @Ordinal,INSERTED.Id,INSERTED.Value,INSERTED.Payload INTO @MeasuredRows
   WHERE Id BETWEEN 101 AND 110 OPTION(MAXDOP 1);
  IF @@ROWCOUNT<>10 THROW 51003,'FAIL_RESULT_CONTRACT: Actual UPDATE rowcount differs.',1;
  SET @Ordinal+=1;
 END;
 ROLLBACK TRANSACTION;
END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION;THROW;END CATCH;
SET @Ended=SYSUTCDATETIME();SET @TransactionAfter=@@TRANCOUNT;
SELECT @Cpu1=CONVERT(bigint,cpu_time),@Reads1=CONVERT(bigint,reads),@Logical1=CONVERT(bigint,logical_reads),@Writes1=CONVERT(bigint,writes)
 FROM sys.dm_exec_requests WHERE session_id=@Session AND request_id=@Request AND database_id=@Db AND start_time=@RequestStarted AND connection_id=@Connection;
IF @@ROWCOUNT<>1 OR @Cpu1 IS NULL OR @Reads1 IS NULL OR @Logical1 IS NULL OR @Writes1 IS NULL
 OR @Cpu1<@Cpu0 OR @Reads1<@Reads0 OR @Logical1<@Logical0 OR @Writes1<@Writes0 OR @Ended<@Started OR @TransactionAfter<>0
 THROW 51003,'FAIL_STATE: Actual final counters or own rollback missing.',1;
IF @Negative=1 UPDATE @MeasuredRows SET Value=0 WHERE QueryOrdinal=1 AND Id=101;
IF (SELECT COUNT(*) FROM @MeasuredRows)<>@Statements*10
 OR EXISTS(SELECT 1 FROM @MeasuredRows WHERE QueryOrdinal NOT BETWEEN 1 AND @Statements OR Id NOT BETWEEN 101 AND 110 OR Value IS NULL OR Value<>Id*3+QueryOrdinal
 OR Payload IS NULL OR DATALENGTH(Payload)<>100 OR CONVERT(varbinary(max),Payload)<>CONVERT(varbinary(max),REPLICATE('F',100)))
 OR EXISTS(SELECT QueryOrdinal FROM @MeasuredRows GROUP BY QueryOrdinal HAVING COUNT(*)<>10)
 THROW 51003,'FAIL_RESULT_CONTRACT: Actual complete per-UPDATE row oracle violated.',1;
-- Vollständige native Rollback-/Sourceprüfung außerhalb des Messfensters.
IF (SELECT COUNT(*) FROM lab.SourceRows)<>1000
 OR EXISTS(SELECT 1 FROM lab.SourceRows WHERE Id NOT BETWEEN 1 AND 1000 OR Value IS NULL OR Value<>Id*3
 OR Payload IS NULL OR DATALENGTH(Payload)<>100 OR CONVERT(varbinary(max),Payload)<>CONVERT(varbinary(max),REPLICATE('F',100)))
 THROW 51003,'FAIL_RESULT_CONTRACT: Actual full source rollback violated.',1;
DECLARE @Before nvarchar(max)=(SELECT @Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
 @Cpu0 CpuMs,@Reads0 Reads,@Logical0 LogicalReads,@Writes0 Writes FOR JSON PATH,WITHOUT_ARRAY_WRAPPER),
 @After nvarchar(max)=(SELECT @Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
 @Cpu1 CpuMs,@Reads1 Reads,@Logical1 LogicalReads,@Writes1 Writes FOR JSON PATH,WITHOUT_ARRAY_WRAPPER),
 @Queries nvarchar(max)=(SELECT QueryOrdinal Ordinal,COUNT(*) AS [Rows],MIN(Id) FirstId,MAX(Id) LastId,
 CONVERT(varchar(64),HASHBYTES('SHA2_256',STRING_AGG(CONVERT(nvarchar(max),CONCAT(Id,N'|',Value,N'|',CONVERT(varchar(200),CONVERT(varbinary(max),Payload),2))),N';') WITHIN GROUP(ORDER BY Id)),2) Digest
 FROM @MeasuredRows GROUP BY QueryOrdinal ORDER BY QueryOrdinal FOR JSON PATH);
DECLARE @Output nvarchar(max)=(SELECT @Path AS [Path],@RawLabel Label,@Statements Statements,
 @Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
 @TransactionBefore TransactionBefore,@TransactionAfter TransactionAfter,
 @Cpu1-@Cpu0 CpuMs,@Reads1-@Reads0 Reads,@Logical1-@Logical0 LogicalReads,@Writes1-@Writes0 Writes,
 DATEDIFF_BIG(microsecond,@Started,@Ended) ElapsedUs,CONVERT(nvarchar(30),@Started,126) StartedUtc,CONVERT(nvarchar(30),@Ended,126) EndedUtc,
 JSON_QUERY(@Before) CountersBefore,JSON_QUERY(@After) CountersAfter,JSON_QUERY(@Queries) Queries FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
IF @Output IS NULL OR DATALENGTH(@Output)>100000 THROW 51003,'FAIL_RESULT_CONTRACT: Actual bounded evidence missing.',1;
DECLARE @Chars int=LEN(@Output),@Part int=1,@Parts int=(LEN(@Output)+199)/200;
WHILE @Part<=@Parts
BEGIN
 SELECT CONVERT(varchar(256),'DGN010_DMLPART|'+CONVERT(varchar(10),@Part)+'|'+CONVERT(varchar(10),@Parts)+'|'+CONVERT(varchar(10),@Chars)+'|'
 +CONVERT(varchar(200),SUBSTRING(@Output,(@Part-1)*200+1,200)));
 SET @Part+=1;
END;
SELECT 'SQLPERF_SUMMARY|PASS|OK';
