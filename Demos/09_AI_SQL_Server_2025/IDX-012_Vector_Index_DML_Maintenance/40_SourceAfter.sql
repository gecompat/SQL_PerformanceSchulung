/* IDX-012: gebundenes DEC-074-Profil; eigene synthetische Datenbank. */
SET NOCOUNT ON;
IF DATALENGTH(N'$(DemoId)')<>DATALENGTH(N'IDX-012')
 OR CONVERT(varbinary(max),N'$(DemoId)')<>CONVERT(varbinary(max),N'IDX-012')
 OR DATALENGTH(N'$(RunToken)')<>32 OR N'$(RunToken)' COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-F0-9]%'
 OR DATALENGTH(N'$(TargetDatabase)')<>DATALENGTH(N'SQLPERF_LAB_IDX012_$(RunToken)')
 OR CONVERT(varbinary(max),N'$(TargetDatabase)')<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX012_$(RunToken)')
 THROW 51000,'FAIL_CONTRACT: Vollständige Demo-/Token-/DB-Bindung fehlt.',1;
IF DATALENGTH(N'$(ConfirmIsolatedLab)')<>2 OR CONVERT(varbinary(max),N'$(ConfirmIsolatedLab)')<>CONVERT(varbinary(max),N'1')
 OR DATALENGTH(N'$(HighImpactConfirmed)')<>2 OR CONVERT(varbinary(max),N'$(HighImpactConfirmed)')<>CONVERT(varbinary(max),N'1')
 OR COALESCE(TRY_CONVERT(int,N'$(MaximumRuntimeSeconds)'),-1)<>300
 THROW 51000,'FAIL_SAFETY: YELLOW-Bestätigung und festes Laufbudget fehlen.',1;


IF (SELECT COUNT(*) FROM (VALUES
 (N'SQLPERF.Project',N'SQL_PerformanceSchulung'),
 (N'SQLPERF.ContractVersion',N'1.0'),
 (N'SQLPERF.DemoId',N'IDX-012'),
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

DECLARE @IndexAfter nvarchar(max)=(SELECT * FROM sys.vector_indexes
 WHERE object_id=OBJECT_ID(N'lab.VectorFixture') ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
DECLARE @MetadataOutput nvarchar(max)=(SELECT N'INDEX_AFTER' kind,DB_ID() DatabaseId,N'$(RunToken)' RunToken,
 JSON_QUERY(@IndexAfter) metadata FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
IF @MetadataOutput IS NULL OR DATALENGTH(@MetadataOutput)>120000 THROW 51003,'Full after-index evidence outside bound.',1;
SELECT @MetadataOutput;
DECLARE @q VECTOR(3)='[1,0,0]';
DECLARE @Output nvarchar(max)=(SELECT N'SOURCE_DISTANCES' kind,DB_ID() DatabaseId,
 JSON_QUERY((SELECT Id,VECTOR_DISTANCE('cosine',V,@q) DistanceValue FROM lab.VectorFixture
 ORDER BY Id FOR JSON PATH)) rows FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'FAIL_RESULT_CONTRACT: Quellenoutput unvollständig.',1;
SELECT @Output;

DECLARE @SourceBlock int=1,@Vectors nvarchar(max);
WHILE @SourceBlock<=10
BEGIN
 SET @Vectors=(SELECT N'SOURCE_VECTOR_BLOCK' kind,DB_ID() DatabaseId,@SourceBlock BlockId,
 JSON_QUERY((SELECT Id,JsonValue FROM (SELECT Id,CONVERT(nvarchar(max),V) JsonValue FROM lab.VectorFixture) AS CurrentSource
 WHERE Id BETWEEN (@SourceBlock-1)*100+1 AND @SourceBlock*100 ORDER BY Id FOR JSON PATH)) vectors
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
 IF @Vectors IS NULL OR DATALENGTH(@Vectors)>120000 THROW 51003,'FAIL_RESULT_CONTRACT: Quellenblock unvollständig.',1;
 SELECT @Vectors;
 SET @SourceBlock+=1;
END;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
