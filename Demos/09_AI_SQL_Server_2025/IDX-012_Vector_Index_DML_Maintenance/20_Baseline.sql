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
EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
CREATE TABLE lab.VectorFixture(Id int PRIMARY KEY CLUSTERED,V VECTOR(3) NOT NULL);
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND name=N'V' AND vector_dimensions=3 AND vector_base_type=0 AND is_nullable=0)
 THROW 51003,'Actual vector column type not bound.',1;
INSERT lab.VectorFixture SELECT value,CAST(CONCAT('[1,',
 CONVERT(varchar(30),CONVERT(decimal(12,6),value/1000.0)),',',
 CONVERT(varchar(30),CONVERT(decimal(12,6),((value*17)%97)/97.0)),']') AS VECTOR(3))
 FROM GENERATE_SERIES(1,999);

IF DATALENGTH(DB_NAME())<>DATALENGTH(N'SQLPERF_LAB_IDX012_$(RunToken)')
 OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX012_$(RunToken)')
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
SELECT Id,CONVERT(nvarchar(max),V) JsonValue,
 CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) BytesValue INTO #Frozen FROM lab.VectorFixture;
IF (SELECT COUNT(*) FROM #Frozen)<>999 OR EXISTS(
 SELECT 1 FROM #Frozen f WHERE ISJSON(f.JsonValue)<>1
 OR (SELECT COUNT(*) FROM OPENJSON(f.JsonValue))<>3
 OR NOT EXISTS(SELECT 1 FROM OPENJSON(f.JsonValue) WHERE [key]='0' AND [type]=2
 AND TRY_CONVERT(float,value)=1)
 OR NOT EXISTS(SELECT 1 FROM OPENJSON(f.JsonValue) WHERE [key]='1' AND [type]=2
 AND ABS(TRY_CONVERT(float,value)-CONVERT(decimal(12,6),f.Id/1000.0))<0.000001)
 OR NOT EXISTS(SELECT 1 FROM OPENJSON(f.JsonValue) WHERE [key]='2' AND [type]=2
 AND ABS(TRY_CONVERT(float,value)-CONVERT(decimal(12,6),((f.Id*17)%97)/97.0))<0.000001)
 OR CONVERT(varbinary(max),CONVERT(nvarchar(max),CAST(f.JsonValue AS VECTOR(3))))<>f.BytesValue)
 THROW 51003,'Stored vector JSON, dimension or float32 values not bound.',1;

SELECT * INTO lab.FrozenSource FROM #Frozen;
DECLARE @q VECTOR(3)='[1,0,0]';
SELECT TOP(5) Id,VECTOR_DISTANCE('cosine',V,@q) DistanceValue INTO lab.ExactOracle
 FROM lab.VectorFixture ORDER BY VECTOR_DISTANCE('cosine',V,@q),Id;
IF (SELECT COUNT(*) FROM lab.ExactOracle)<>5 THROW 51003,'FAIL_RESULT_CONTRACT: Exact-Oracle fehlt.',1;
DECLARE @Output nvarchar(max)=(SELECT N'SOURCE_DISTANCES' kind,DB_ID() DatabaseId,
 JSON_QUERY((SELECT Id,VECTOR_DISTANCE('cosine',V,@q) DistanceValue FROM lab.VectorFixture
 ORDER BY Id FOR JSON PATH)) rows FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'FAIL_RESULT_CONTRACT: Quellenoutput unvollständig.',1;
SELECT @Output;

DECLARE @SourceBlock int=1,@Vectors nvarchar(max);
WHILE @SourceBlock<=10
BEGIN
 SET @Vectors=(SELECT N'SOURCE_VECTOR_BLOCK' kind,DB_ID() DatabaseId,@SourceBlock BlockId,
 JSON_QUERY((SELECT Id,JsonValue FROM lab.FrozenSource
 WHERE Id BETWEEN (@SourceBlock-1)*100+1 AND @SourceBlock*100 ORDER BY Id FOR JSON PATH)) vectors
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
 IF @Vectors IS NULL OR DATALENGTH(@Vectors)>120000 THROW 51003,'FAIL_RESULT_CONTRACT: Quellenblock unvollständig.',1;
 SELECT @Vectors;
 SET @SourceBlock+=1;
END;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
