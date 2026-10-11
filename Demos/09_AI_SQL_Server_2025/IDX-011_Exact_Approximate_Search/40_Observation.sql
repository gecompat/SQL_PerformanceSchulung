/* IDX-011: gebundenes DEC-074-Profil; eigene synthetische Datenbank. */
SET NOCOUNT ON;
IF DATALENGTH(N'$(DemoId)')<>DATALENGTH(N'IDX-011')
 OR CONVERT(varbinary(max),N'$(DemoId)')<>CONVERT(varbinary(max),N'IDX-011')
 OR DATALENGTH(N'$(RunToken)')<>32 OR N'$(RunToken)' COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-F0-9]%'
 OR DATALENGTH(N'$(TargetDatabase)')<>DATALENGTH(N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR CONVERT(varbinary(max),N'$(TargetDatabase)')<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX011_$(RunToken)')
 THROW 51000,'FAIL_CONTRACT: Vollständige Demo-/Token-/DB-Bindung fehlt.',1;
IF DATALENGTH(N'$(ConfirmIsolatedLab)')<>2 OR CONVERT(varbinary(max),N'$(ConfirmIsolatedLab)')<>CONVERT(varbinary(max),N'1')
 OR DATALENGTH(N'$(HighImpactConfirmed)')<>2 OR CONVERT(varbinary(max),N'$(HighImpactConfirmed)')<>CONVERT(varbinary(max),N'1')
 OR COALESCE(TRY_CONVERT(int,N'$(MaximumRuntimeSeconds)'),-1)<>300
 THROW 51000,'FAIL_SAFETY: YELLOW-Bestätigung und festes Laufbudget fehlen.',1;


IF (SELECT COUNT(*) FROM (VALUES
 (N'SQLPERF.Project',N'SQL_PerformanceSchulung'),
 (N'SQLPERF.ContractVersion',N'1.0'),
 (N'SQLPERF.DemoId',N'IDX-011'),
 (N'SQLPERF.RunToken',N'$(RunToken)')) e(Name,Expected)
 JOIN sys.extended_properties p ON p.name=e.Name AND p.class=0
 AND DATALENGTH(p.name)=DATALENGTH(e.Name)
 AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 AND p.major_id=0 AND p.minor_id=0
 WHERE DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Expected)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=
 CONVERT(varbinary(max),e.Expected))<>4
 THROW 51001,'Full ownership binding lost.',1;

IF OBJECT_ID(N'dbo.PreviewState',N'U') IS NULL
 THROW 51003,'Persistent preview baseline missing.',1;
IF (SELECT COUNT(*) FROM dbo.PreviewState)<>1
 THROW 51003,'Persistent preview baseline count invalid.',1;
IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE Id=1 AND OriginalValue IN(0,1)
 AND DATALENGTH(RunToken)=DATALENGTH(N'$(RunToken)')
 AND CONVERT(varbinary(max),RunToken)=CONVERT(varbinary(max),N'$(RunToken)'))
 THROW 51003,'Persistent preview baseline invalid.',1;

IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE MaxDopOriginal=0)
 THROW 51003,'Persistent actual MAXDOP baseline invalid.',1;

IF (SELECT COUNT(*) FROM sys.database_scoped_configurations WHERE
 (name=N'PREVIEW_FEATURES' AND TRY_CONVERT(int,value)=1) OR
 (name=N'MAXDOP' AND TRY_CONVERT(int,value)=1))<>2
 THROW 51003,'Actual preview and MAXDOP must both be one.',1;

IF DATALENGTH(DB_NAME())<>DATALENGTH(N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR NOT EXISTS(SELECT 1 FROM sys.schemas WHERE schema_id=SCHEMA_ID(N'lab')
 AND DATALENGTH(name)=DATALENGTH(N'lab') AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'lab'))
 OR NOT EXISTS(SELECT 1 FROM sys.tables WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND schema_id=SCHEMA_ID(N'lab') AND DATALENGTH(name)=DATALENGTH(N'VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'VectorFixture'))
 THROW 51003,'FAIL_STATE: Vollständiger tatsächlicher Quellenkontext verändert.',1;
IF (SELECT COUNT(*) FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture'))<>2
 OR NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'Id') AND DATALENGTH(name)=4
 AND TYPE_NAME(system_type_id)=N'int' AND is_nullable=0 AND is_computed=0)
 OR NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'V') AND DATALENGTH(name)=2
 AND vector_dimensions=3 AND vector_base_type=0 AND is_nullable=0 AND is_computed=0)
 OR NOT EXISTS(SELECT 1 FROM sys.indexes i JOIN sys.index_columns c
 ON c.object_id=i.object_id AND c.index_id=i.index_id JOIN sys.columns v
 ON v.object_id=c.object_id AND v.column_id=c.column_id
 WHERE i.object_id=OBJECT_ID(N'lab.VectorFixture') AND i.type=1 AND i.is_primary_key=1
 AND i.is_unique=1 AND i.is_disabled=0 AND i.is_hypothetical=0 AND c.key_ordinal=1
 AND CONVERT(varbinary(max),v.name)=CONVERT(varbinary(max),N'Id')
 AND (SELECT COUNT(*) FROM sys.index_columns k WHERE k.object_id=i.object_id AND k.index_id=i.index_id)=1)
 THROW 51003,'FAIL_STATE: Tatsächlicher float32-VECTOR(3)/clustered-INT-PK-Vertrag verändert.',1;

IF (SELECT COUNT(*) FROM lab.VectorFixture)<>1000
 OR EXISTS(SELECT 1 FROM lab.VectorFixture WHERE Id NOT BETWEEN 1 AND 1000)
 OR (SELECT COUNT(*) FROM lab.FrozenSource)<>1000
 OR EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture
 EXCEPT SELECT Id,BytesValue FROM lab.FrozenSource)
 OR EXISTS(SELECT Id,BytesValue FROM lab.FrozenSource EXCEPT
 SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture)
 THROW 51003,'FAIL_STATE: Vollständige persistierte Quelle verändert.',1;

IF (SELECT COUNT(*) FROM lab.IndexEvidence)<>1 OR NOT EXISTS(SELECT 1 FROM lab.IndexEvidence WHERE Id=1)
 THROW 51003,'FAIL_STATE: Persistierte eigene Indexevidenz fehlt.',1;
DECLARE @ObservedIndex nvarchar(max)=(SELECT * FROM sys.vector_indexes
 WHERE object_id=OBJECT_ID(N'lab.VectorFixture') AND name=N'IDX011_OwnVector'
 ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
IF (SELECT COUNT(*) FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture'))<>1
 OR NOT EXISTS(SELECT 1 FROM lab.IndexEvidence WHERE
 DATALENGTH(MetadataJson)=DATALENGTH(@ObservedIndex)
 AND CONVERT(varbinary(max),MetadataJson)=CONVERT(varbinary(max),@ObservedIndex))
 THROW 51003,'FAIL_STATE: Vollständige eigene Indexmetadaten verändert.',1;
/* Privater Entwurf: noch kein vollständiges Quellen-/Runtimegate. */
DECLARE @q VECTOR(3)='[1,0,0]',@Warmup int=TRY_CONVERT(int,N'$(WarmupOrdinal)'),
 @Block int=TRY_CONVERT(int,N'$(Block)'),@Slot int=TRY_CONVERT(int,N'$(Slot)'),
 @Order nvarchar(max)=N'$(Order)',@Path nvarchar(max)=N'$(Path)';
IF @Warmup IS NULL OR @Warmup NOT BETWEEN 0 AND 5 OR @Block IS NULL OR @Slot IS NULL
 OR @Path NOT IN(N'EXACT',N'VECTOR_SEARCH')
 OR (@Warmup>0 AND (@Block<>0 OR @Slot<>0 OR @Order<>N'WARMUP'))
 OR (@Warmup=0 AND (@Block NOT BETWEEN 1 AND 3 OR @Slot NOT IN(1,2)
 OR @Order NOT IN(N'AB',N'BA',N'AA')
 OR @Path<>CASE WHEN (@Order=N'AB' AND @Slot=1) OR (@Order=N'BA' AND @Slot=2) OR @Order=N'AA'
 THEN N'EXACT' ELSE N'VECTOR_SEARCH' END))
 THROW 51000,'FAIL_CONTRACT: Feste Benchmarkphase verletzt.',1;
DECLARE @Statements int=CASE WHEN @Warmup>0 THEN 1 ELSE 100 END,
 @Session int=@@SPID,@Request int,@RequestStarted datetime,@Connection uniqueidentifier,@Db int=DB_ID(),
 @Cpu0 bigint,@Cpu1 bigint,@Reads0 bigint,@Reads1 bigint,@Logical0 bigint,@Logical1 bigint,
 @Writes0 bigint,@Writes1 bigint,@Started datetime2(7),@Ended datetime2(7),@Ordinal int=1;
SELECT @Request=request_id,@RequestStarted=start_time,@Connection=connection_id
 FROM sys.dm_exec_requests WHERE session_id=@Session AND database_id=@Db;
IF @@ROWCOUNT<>1 OR @Request IS NULL OR @RequestStarted IS NULL OR @Connection IS NULL
 THROW 51003,'FAIL_STATE: Tatsächliche Requestidentität fehlt.',1;
CREATE TABLE #MeasuredRows(QueryOrdinal int NOT NULL,Id int NOT NULL,DistanceValue float NOT NULL,
 PRIMARY KEY(QueryOrdinal,Id));
SELECT @Cpu0=CONVERT(bigint,cpu_time),@Reads0=CONVERT(bigint,reads),
 @Logical0=CONVERT(bigint,logical_reads),@Writes0=CONVERT(bigint,writes)
 FROM sys.dm_exec_requests WHERE session_id=@Session AND request_id=@Request
 AND start_time=@RequestStarted AND connection_id=@Connection AND database_id=@Db;
IF @@ROWCOUNT<>1 OR @Cpu0 IS NULL OR @Reads0 IS NULL OR @Logical0 IS NULL OR @Writes0 IS NULL
 OR @Cpu0<0 OR @Reads0<0 OR @Logical0<0 OR @Writes0<0
 THROW 51003,'FAIL_STATE: Tatsächliche Requeststartzähler fehlen.',1;
SET @Started=SYSUTCDATETIME();
WHILE @Ordinal<=@Statements
BEGIN
 IF @Path=N'EXACT'
  INSERT #MeasuredRows SELECT TOP(5) @Ordinal,Id,VECTOR_DISTANCE('cosine',V,@q)
  FROM lab.VectorFixture ORDER BY VECTOR_DISTANCE('cosine',V,@q),Id;
 ELSE
  EXEC sys.sp_executesql N'INSERT #MeasuredRows SELECT @ordinal,c.Id,r.distance FROM VECTOR_SEARCH(
  TABLE=lab.VectorFixture AS c,COLUMN=V,SIMILAR_TO=@q,METRIC=''cosine'',TOP_N=5) AS r;',
  N'@q VECTOR(3),@ordinal int',@q=@q,@ordinal=@Ordinal;
 SET @Ordinal+=1;
END;
SET @Ended=SYSUTCDATETIME();
SELECT @Cpu1=CONVERT(bigint,cpu_time),@Reads1=CONVERT(bigint,reads),
 @Logical1=CONVERT(bigint,logical_reads),@Writes1=CONVERT(bigint,writes)
 FROM sys.dm_exec_requests WHERE session_id=@Session AND request_id=@Request
 AND start_time=@RequestStarted AND connection_id=@Connection AND database_id=@Db;
IF @@ROWCOUNT<>1 OR @Cpu1 IS NULL OR @Reads1 IS NULL OR @Logical1 IS NULL OR @Writes1 IS NULL
 OR @Cpu1<@Cpu0 OR @Reads1<@Reads0 OR @Logical1<@Logical0 OR @Writes1<@Writes0
 OR @Ended<@Started THROW 51003,'FAIL_STATE: Tatsächliches Requestendfenster fehlt.',1;
IF (SELECT COUNT(*) FROM #MeasuredRows)<>@Statements*5
 OR EXISTS(SELECT QueryOrdinal FROM #MeasuredRows GROUP BY QueryOrdinal HAVING COUNT(*)<>5)
 OR EXISTS(SELECT 1 FROM #MeasuredRows r LEFT JOIN lab.VectorFixture s ON s.Id=r.Id
 WHERE s.Id IS NULL OR r.DistanceValue NOT BETWEEN 0 AND 2
 OR ABS(r.DistanceValue-VECTOR_DISTANCE('cosine',s.V,@q))>0.0001)
 OR EXISTS(SELECT r.QueryOrdinal FROM #MeasuredRows r LEFT JOIN lab.ExactOracle e ON e.Id=r.Id
 GROUP BY r.QueryOrdinal HAVING COUNT(e.Id)<CASE WHEN @Path=N'EXACT' THEN 5 ELSE 4 END)
 THROW 51003,'FAIL_RESULT_CONTRACT: Tatsächliche Queryqualität verletzt.',1;
DECLARE @Before nvarchar(max)=(SELECT N'LIVE_REQUEST' CounterSource,@Session SessionId,@Request RequestId,
 @RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
 @Cpu0 CpuMs,@Reads0 Reads,@Logical0 LogicalReads,@Writes0 Writes FOR JSON PATH,WITHOUT_ARRAY_WRAPPER),
 @After nvarchar(max)=(SELECT N'LIVE_REQUEST' CounterSource,@Session SessionId,@Request RequestId,
 @RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
 @Cpu1 CpuMs,@Reads1 Reads,@Logical1 LogicalReads,@Writes1 Writes FOR JSON PATH,WITHOUT_ARRAY_WRAPPER),
 @Queries nvarchar(max)=(SELECT q.QueryOrdinal Ordinal,
 JSON_QUERY((SELECT Id,DistanceValue FROM #MeasuredRows r WHERE r.QueryOrdinal=q.QueryOrdinal
 ORDER BY DistanceValue,Id FOR JSON PATH)) ResultRows
 FROM (SELECT DISTINCT QueryOrdinal FROM #MeasuredRows) q ORDER BY q.QueryOrdinal FOR JSON PATH);
DECLARE @Output nvarchar(max)=(SELECT CASE WHEN @Warmup>0 THEN N'WARMUP_REQUEST' ELSE N'MEASURED_WINDOW' END kind,
 N'LIVE_REQUEST' CounterSource,@Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,
 @Connection ConnectionId,@Db DatabaseId,@Path Path,@Warmup Ordinal,@Block Block,@Order [Order],@Slot Slot,
 @Statements Statements,@Cpu1-@Cpu0 CpuMs,DATEDIFF_BIG(microsecond,@Started,@Ended) ElapsedUs,
 @Reads1-@Reads0 Reads,@Logical1-@Logical0 LogicalReads,@Writes1-@Writes0 Writes,
 CONVERT(nvarchar(30),@Started,126) StartedUtc,CONVERT(nvarchar(30),@Ended,126) EndedUtc,
 JSON_QUERY(@Before) CountersBefore,JSON_QUERY(@After) CountersAfter,
 JSON_QUERY(CASE WHEN @Warmup>0 THEN (SELECT Id,DistanceValue FROM #MeasuredRows ORDER BY DistanceValue,Id FOR JSON PATH) END) ResultRows,
 JSON_QUERY(CASE WHEN @Warmup=0 THEN @Queries END) Queries
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'FAIL_RESULT_CONTRACT: Vollständiger Ergebnisoutput fehlt.',1;
SELECT @Output;

IF DATALENGTH(DB_NAME())<>DATALENGTH(N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR NOT EXISTS(SELECT 1 FROM sys.schemas WHERE schema_id=SCHEMA_ID(N'lab')
 AND DATALENGTH(name)=DATALENGTH(N'lab') AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'lab'))
 OR NOT EXISTS(SELECT 1 FROM sys.tables WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND schema_id=SCHEMA_ID(N'lab') AND DATALENGTH(name)=DATALENGTH(N'VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'VectorFixture'))
 THROW 51003,'FAIL_STATE: Vollständiger tatsächlicher Quellenkontext verändert.',1;
IF (SELECT COUNT(*) FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture'))<>2
 OR NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'Id') AND DATALENGTH(name)=4
 AND TYPE_NAME(system_type_id)=N'int' AND is_nullable=0 AND is_computed=0)
 OR NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'V') AND DATALENGTH(name)=2
 AND vector_dimensions=3 AND vector_base_type=0 AND is_nullable=0 AND is_computed=0)
 OR NOT EXISTS(SELECT 1 FROM sys.indexes i JOIN sys.index_columns c
 ON c.object_id=i.object_id AND c.index_id=i.index_id JOIN sys.columns v
 ON v.object_id=c.object_id AND v.column_id=c.column_id
 WHERE i.object_id=OBJECT_ID(N'lab.VectorFixture') AND i.type=1 AND i.is_primary_key=1
 AND i.is_unique=1 AND i.is_disabled=0 AND i.is_hypothetical=0 AND c.key_ordinal=1
 AND CONVERT(varbinary(max),v.name)=CONVERT(varbinary(max),N'Id')
 AND (SELECT COUNT(*) FROM sys.index_columns k WHERE k.object_id=i.object_id AND k.index_id=i.index_id)=1)
 THROW 51003,'FAIL_STATE: Tatsächlicher float32-VECTOR(3)/clustered-INT-PK-Vertrag verändert.',1;

IF (SELECT COUNT(*) FROM lab.VectorFixture)<>1000
 OR EXISTS(SELECT 1 FROM lab.VectorFixture WHERE Id NOT BETWEEN 1 AND 1000)
 OR (SELECT COUNT(*) FROM lab.FrozenSource)<>1000
 OR EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture
 EXCEPT SELECT Id,BytesValue FROM lab.FrozenSource)
 OR EXISTS(SELECT Id,BytesValue FROM lab.FrozenSource EXCEPT
 SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture)
 THROW 51003,'FAIL_STATE: Vollständige persistierte Quelle verändert.',1;

PRINT 'SQLPERF_SUMMARY|WARN|WARN_OPTIONAL_EVIDENCE_SKIPPED';
