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

SET NOCOUNT ON;
SET QUOTED_IDENTIFIER ON;
USE [SQLPERF_LAB_IDX011_$(RunToken)];

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

IF NOT EXISTS(SELECT 1 FROM sys.databases WHERE database_id=DB_ID()
 AND compatibility_level=170 AND recovery_model_desc=N'SIMPLE')
 THROW 51003,'Database options not bound.',1;
IF (SELECT SUM(CONVERT(bigint,size)) FROM sys.database_files)>65536
 OR EXISTS(SELECT 1 FROM sys.database_files WHERE is_percent_growth<>0
 OR growth<>2048 OR max_size NOT IN(32768,8192))
 THROW 51003,'File limits not bound.',1;
SELECT configuration_id,CONVERT(varbinary(max),name) NameBytes,value,value_in_use
 INTO #Host FROM sys.configurations;
SELECT compatibility_level,recovery_model INTO #Db FROM sys.databases WHERE database_id=DB_ID();
SELECT file_id,type,CONVERT(varbinary(max),name) NameBytes,max_size,growth,is_percent_growth
 INTO #Files FROM sys.database_files;
-- Beide Baselines mit isolierten Gegenfixtures, Original bleibt unverändert.
CREATE TABLE #Baseline(Id int,OriginalValue int,RunToken nvarchar(40),MaxDopOriginal int);
DECLARE @Case int=0,@Rejected int;
WHILE @Case<9
BEGIN
 DELETE #Baseline;
 IF @Case<>0 INSERT #Baseline VALUES(1,
 CASE @Case WHEN 1 THEN NULL WHEN 2 THEN 2 ELSE 0 END,
 CASE WHEN @Case=4 THEN N'$(RunToken) ' ELSE N'$(RunToken)' END,
 CASE @Case WHEN 5 THEN NULL WHEN 6 THEN 1 WHEN 7 THEN -1 ELSE 0 END);
 IF @Case=3 INSERT #Baseline VALUES(1,1,N'$(RunToken)',0);
 IF @Case=8 UPDATE #Baseline SET Id=2;
 SET @Rejected=CASE WHEN (SELECT COUNT(*) FROM #Baseline)=1 AND EXISTS(
 SELECT 1 FROM #Baseline WHERE Id=1 AND OriginalValue IN(0,1) AND MaxDopOriginal=0
 AND DATALENGTH(RunToken)=DATALENGTH(N'$(RunToken)')
 AND CONVERT(varbinary(max),RunToken)=CONVERT(varbinary(max),N'$(RunToken)')) THEN 0 ELSE 1 END;
 IF @Rejected<>1 THROW 51003,'Dual baseline negative accepted.',1;
 SET @Case+=1;
END;
SELECT * INTO #SavedBaseline FROM dbo.PreviewState;
SELECT configuration_id,name,value,value_for_secondary,is_value_default INTO #Scoped
 FROM sys.database_scoped_configurations;
SELECT name,class,major_id,minor_id,CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) ValueBytes
 INTO #FullMarkers FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;
-- Vollständige Marker, auch unsichtbare Suffixe und fehlende Werte ablehnen.
CREATE TABLE #Markers(Name nvarchar(128),Expected nvarchar(max),Actual nvarchar(max));
INSERT #Markers VALUES(N'SQLPERF.Project',N'SQL_PerformanceSchulung',N'SQL_PerformanceSchulung'),
 (N'SQLPERF.ContractVersion',N'1.0',N'1.0'),(N'SQLPERF.DemoId',N'IDX-011',N'IDX-011'),
 (N'SQLPERF.RunToken',N'$(RunToken)',N'$(RunToken)');
DECLARE @Marker int=0,@Name nvarchar(128),@Expected nvarchar(max);
DECLARE mc CURSOR LOCAL FAST_FORWARD FOR SELECT Name,Expected FROM #Markers;
OPEN mc;FETCH NEXT FROM mc INTO @Name,@Expected;
WHILE @@FETCH_STATUS=0
BEGIN
 SET @Case=0;
 WHILE @Case<6
 BEGIN
  UPDATE #Markers SET Actual=CASE @Case WHEN 0 THEN NULL WHEN 1 THEN LEFT(@Expected,LEN(@Expected)-1)
   WHEN 2 THEN @Expected+N' ' WHEN 3 THEN @Expected+NCHAR(0) WHEN 4 THEN N'x'+@Expected
   ELSE @Expected+N'X' END WHERE Name=@Name;
  IF (SELECT COUNT(*) FROM #Markers WHERE DATALENGTH(Actual)=DATALENGTH(Expected)
   AND CONVERT(varbinary(max),Actual)=CONVERT(varbinary(max),Expected))=4
   THROW 51003,'Marker negative accepted.',1;
  SET @Case+=1;SET @Marker+=1;
 END;
 UPDATE #Markers SET Actual=Expected WHERE Name=@Name;
 FETCH NEXT FROM mc INTO @Name,@Expected;
END;
CLOSE mc;DEALLOCATE mc;

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
SELECT Id,CONVERT(nvarchar(max),V) JsonValue,
 CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) BytesValue INTO #Frozen FROM lab.VectorFixture;
IF (SELECT COUNT(*) FROM #Frozen)<>1000 OR EXISTS(
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
DECLARE @q VECTOR(3)='[1,0,0]';
CREATE TABLE #Exact(Id int PRIMARY KEY,DistanceValue float NOT NULL);
CREATE TABLE #Approx(Id int PRIMARY KEY,DistanceValue float NOT NULL);
INSERT #Exact SELECT TOP(5) Id,VECTOR_DISTANCE('cosine',V,@q) FROM lab.VectorFixture
 ORDER BY VECTOR_DISTANCE('cosine',V,@q),Id;
IF (SELECT COUNT(*) FROM lab.ExactOracle)<>5 OR EXISTS(SELECT Id,DistanceValue FROM lab.ExactOracle EXCEPT SELECT Id,DistanceValue FROM #Exact) OR EXISTS(SELECT Id,DistanceValue FROM #Exact EXCEPT SELECT Id,DistanceValue FROM lab.ExactOracle) THROW 51003,'FAIL_STATE: Persistiertes Oracle verändert.',1;


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

IF COALESCE(TRY_CONVERT(int,SESSIONPROPERTY('QUOTED_IDENTIFIER')),-1)<>1
 THROW 51003,'Actual QUOTED_IDENTIFIER session option missing before Build.',1;
SELECT N'ANN_BUILD_SESSION|QUOTED_IDENTIFIER_1';

CREATE TABLE #FilterCases(CaseId int PRIMARY KEY,Lo int NOT NULL,Hi int NOT NULL,MinRows int NOT NULL);
INSERT #FilterCases VALUES(1,1,1000,4),(2,1,100,4),(3,501,510,0);
CREATE TABLE #FilterExact(CaseId int NOT NULL,Id int NOT NULL,DistanceValue float NOT NULL,
 PRIMARY KEY(CaseId,Id));
INSERT #FilterExact SELECT f.CaseId,e.Id,e.DistanceValue FROM #FilterCases f
 CROSS APPLY(SELECT TOP(5) v.Id,VECTOR_DISTANCE('cosine',v.V,@q) DistanceValue
 FROM lab.VectorFixture v WHERE v.Id BETWEEN f.Lo AND f.Hi
 ORDER BY VECTOR_DISTANCE('cosine',v.V,@q),v.Id) e;
IF EXISTS(SELECT f.CaseId FROM #FilterCases f LEFT JOIN #FilterExact e ON e.CaseId=f.CaseId
 GROUP BY f.CaseId HAVING COUNT(e.Id)<>5)
 THROW 51003,'Fixed filtered Exact oracle missing before Build.',1;

DECLARE @BuildStarted datetime2(7)=SYSUTCDATETIME();
EXEC(N'CREATE VECTOR INDEX IDX011_OwnVector ON lab.VectorFixture(V)
 WITH(METRIC=''cosine'',TYPE=''DiskANN'',MAXDOP=1);');
SELECT CONCAT(N'IDX011_BUILD_ELAPSED_US|',DATEDIFF_BIG(microsecond,@BuildStarted,SYSUTCDATETIME()));
IF N'$(FaultAfterIndexBuild)'=N'1' BEGIN SELECT N'IDX011_FAULT|AFTER_INDEX_BUILD|BEFORE_SEARCH';THROW 51003,'FAIL_EXECUTION: Kontrollierter Fehler nach Indexbuild.',1;END;
DECLARE @IndexBefore nvarchar(max),@IndexAfter nvarchar(max),@Raw nvarchar(max);
IF (SELECT COUNT(*) FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND name=N'IDX011_OwnVector')<>1 THROW 51003,'Own index identity missing.',1;
SET @IndexBefore=(SELECT * FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND name=N'IDX011_OwnVector' ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
DECLARE @Output nvarchar(max)=(SELECT N'INDEX' kind,JSON_QUERY(@IndexBefore) metadata
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'Full index output missing or too large.',1;
SELECT @Output;
SELECT (SELECT SQL_VARIANT_PROPERTY(vector_index_type,'BaseType') vector_type_storage,
 DATALENGTH(vector_index_type) vector_type_bytes,
 SQL_VARIANT_PROPERTY(distance_metric,'BaseType') metric_storage,
 DATALENGTH(distance_metric) metric_bytes
 FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND name=N'IDX011_OwnVector' FOR JSON PATH,WITHOUT_ARRAY_WRAPPER) AS TypeProfile;
-- Beide unterstützten Textspeicherformen in unveränderter Unicodeform vergleichen.
DECLARE @Ascii varchar(7)='DiskANN',@Unicode nvarchar(7)=N'DiskANN';
IF DATALENGTH(CONVERT(nvarchar(max),@Ascii))<>DATALENGTH(@Unicode)
 OR CONVERT(varbinary(max),CONVERT(nvarchar(max),@Ascii))<>CONVERT(varbinary(max),@Unicode)
 THROW 51003,'Supported text storage comparison failed.',1;
CREATE TABLE #TypeProfiles(KindValue nvarchar(30),MetricValue nvarchar(30));
INSERT #TypeProfiles VALUES
 (N'DiskANN ',N'COSINE'),(N'diskann',N'COSINE'),(NULL,N'COSINE'),(N'',N'COSINE'),
 (N'Other',N'COSINE'),(N'DiskANN',N'COSINE '),(N'DiskANN',N'cosine'),
 (N'DiskANN',NULL),(N'DiskANN',N''),(N'DiskANN',N'Other');
IF EXISTS(SELECT 1 FROM #TypeProfiles WHERE
 DATALENGTH(KindValue)=DATALENGTH(N'DiskANN') AND
 CONVERT(varbinary(max),KindValue)=CONVERT(varbinary(max),N'DiskANN') AND
 DATALENGTH(MetricValue)=DATALENGTH(N'COSINE') AND
 CONVERT(varbinary(max),MetricValue)=CONVERT(varbinary(max),N'COSINE'))
 THROW 51003,'Changed text profile accepted.',1;
SELECT N'ANN_TYPE_PROFILE_NEGATIVE|10_REJECTED';
IF NOT EXISTS(SELECT 1 FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND name=N'IDX011_OwnVector' AND type=8 AND type_desc=N'VECTOR'
 AND is_disabled=0 AND is_hypothetical=0
 AND DATALENGTH(CONVERT(nvarchar(max),vector_index_type))=DATALENGTH(N'DiskANN')
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),vector_index_type))=CONVERT(varbinary(max),N'DiskANN')
 AND DATALENGTH(CONVERT(nvarchar(max),distance_metric))=DATALENGTH(N'COSINE')
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),distance_metric))=CONVERT(varbinary(max),N'COSINE'))
 THROW 51003,'Fixed own index type or metric profile missing before legacy trial.',1;
SELECT @Raw=build_parameters FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND name=N'IDX011_OwnVector';
IF COALESCE(ISJSON(@Raw),0)<>1 THROW 51003,'Build parameters are not JSON.',1;
IF LEFT(LTRIM(@Raw),1)<>N'{' THROW 51003,'Build parameter object profile changed.',1;
IF EXISTS(SELECT 1 FROM OPENJSON(@Raw) WHERE LOWER([key])=N'version')
 THROW 51003,'Version field present; this fixed UNKNOWN profile no longer applies.',1;
SELECT N'ANN_LEGACY_PROFILE|VERSION_FIELD_ABSENT|GENERATION_UNKNOWN';


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

IF EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture
 EXCEPT SELECT Id,BytesValue FROM #Frozen) OR EXISTS(SELECT Id,BytesValue FROM #Frozen
 EXCEPT SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture)
 THROW 51003,'Full source binding lost before Search.',1;

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

IF EXISTS(SELECT * FROM dbo.PreviewState EXCEPT SELECT * FROM #SavedBaseline)
 OR EXISTS(SELECT * FROM #SavedBaseline EXCEPT SELECT * FROM dbo.PreviewState)
 THROW 51003,'Full dual baseline changed.',1;
IF EXISTS(SELECT configuration_id,name,value,value_for_secondary,is_value_default FROM sys.database_scoped_configurations
 EXCEPT SELECT * FROM #Scoped) OR EXISTS(SELECT * FROM #Scoped EXCEPT
 SELECT configuration_id,name,value,value_for_secondary,is_value_default FROM sys.database_scoped_configurations)
 THROW 51003,'Full DB scoped configuration changed.',1;
IF EXISTS(SELECT name,class,major_id,minor_id,CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) FROM sys.extended_properties
 WHERE class=0 AND major_id=0 AND minor_id=0 EXCEPT SELECT * FROM #FullMarkers)
 OR EXISTS(SELECT * FROM #FullMarkers EXCEPT SELECT name,class,major_id,minor_id,
 CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0)
 THROW 51003,'Full database marker set changed.',1;

SET STATISTICS XML ON;
EXEC sys.sp_executesql N'INSERT #Approx SELECT c.Id,r.distance FROM VECTOR_SEARCH(
 TABLE=lab.VectorFixture AS c,COLUMN=V,SIMILAR_TO=@q,METRIC=''cosine'',TOP_N=5) AS r;',N'@q VECTOR(3)',@q=@q;
SET STATISTICS XML OFF;

IF (SELECT COUNT(*) FROM #Exact)<>5 OR (SELECT COUNT(*) FROM #Approx)<>5
 OR EXISTS(SELECT 1 FROM #Approx a LEFT JOIN lab.VectorFixture c ON c.Id=a.Id
 WHERE c.Id IS NULL OR VECTOR_DISTANCE('cosine',c.V,@q) IS NULL
 OR ABS(a.DistanceValue-VECTOR_DISTANCE('cosine',c.V,@q))>0.0001)
 THROW 51003,'Actual ANN result invalid.',1;
IF (SELECT COUNT(*) FROM #Approx a JOIN #Exact e ON a.Id=e.Id)<4 THROW 51003,'FAIL_RESULT_CONTRACT: Repräsentative Query Recall unter 0.8.',1;
SELECT (SELECT N'EXACT' kind,Id,DistanceValue FOR JSON PATH,WITHOUT_ARRAY_WRAPPER) FROM #Exact ORDER BY DistanceValue,Id;
SELECT (SELECT N'APPROX' kind,Id,DistanceValue FOR JSON PATH,WITHOUT_ARRAY_WRAPPER) FROM #Approx ORDER BY DistanceValue,Id;
SELECT Id,DistanceValue INTO lab.ApproxBaseline FROM #Approx;
CREATE TABLE lab.IndexEvidence(Id int NOT NULL PRIMARY KEY CHECK(Id=1),MetadataJson nvarchar(max) NOT NULL);
INSERT lab.IndexEvidence VALUES(1,@IndexBefore);

SELECT CONCAT(N'ANN_MEASURED|GEN_UNKNOWN|ROWS_5|RECALL_HITS_',COUNT(*))
 FROM #Approx a JOIN #Exact e ON e.Id=a.Id;
SELECT * INTO #Good FROM #Approx;
SET @Case=0;
WHILE @Case<3
BEGIN
 DELETE #Approx;INSERT #Approx SELECT * FROM #Good;
 IF @Case=0 DELETE #Approx WHERE Id=(SELECT MIN(Id) FROM #Approx);
 IF @Case=1 UPDATE #Approx SET Id=1001 WHERE Id=(SELECT MIN(Id) FROM #Approx);
 IF @Case=2 UPDATE #Approx SET DistanceValue=DistanceValue+1 WHERE Id=(SELECT MIN(Id) FROM #Approx);
 IF (SELECT COUNT(*) FROM #Approx)=5 AND NOT EXISTS(
 SELECT 1 FROM #Approx a LEFT JOIN lab.VectorFixture c ON c.Id=a.Id
 WHERE c.Id IS NULL OR VECTOR_DISTANCE('cosine',c.V,@q) IS NULL
 OR ABS(a.DistanceValue-VECTOR_DISTANCE('cosine',c.V,@q))>0.0001)
 THROW 51003,'Result negative accepted.',1;
 SET @Case+=1;
END;


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

CREATE TABLE #FilterApprox(CaseId int NOT NULL,Id int NOT NULL,DistanceValue float NOT NULL,
 PRIMARY KEY(CaseId,Id));
DECLARE @FilterCase int=1,@FilterLo int,@FilterHi int,@FilterMinimum int;
WHILE @FilterCase<=3
BEGIN
 SELECT @FilterLo=Lo,@FilterHi=Hi,@FilterMinimum=MinRows FROM #FilterCases WHERE CaseId=@FilterCase;
 EXEC sys.sp_executesql N'INSERT #FilterApprox SELECT @fc,c.Id,r.distance FROM VECTOR_SEARCH(
 TABLE=lab.VectorFixture AS c,COLUMN=V,SIMILAR_TO=@q,METRIC=''cosine'',TOP_N=5) AS r
 WHERE c.Id BETWEEN @lo AND @hi;',N'@q VECTOR(3),@fc int,@lo int,@hi int',
 @q=@q,@fc=@FilterCase,@lo=@FilterLo,@hi=@FilterHi;
 IF (SELECT COUNT(*) FROM #FilterApprox WHERE CaseId=@FilterCase) NOT BETWEEN @FilterMinimum AND 5
 OR EXISTS(SELECT 1 FROM #FilterApprox a LEFT JOIN lab.VectorFixture v ON v.Id=a.Id
 WHERE a.CaseId=@FilterCase AND (v.Id IS NULL OR a.Id NOT BETWEEN @FilterLo AND @FilterHi
 OR VECTOR_DISTANCE('cosine',v.V,@q) IS NULL
 OR ABS(a.DistanceValue-VECTOR_DISTANCE('cosine',v.V,@q))>0.0001))
 THROW 51003,'Actual filtered source IDs or distances invalid.',1;
 IF @FilterCase<3 AND (SELECT COUNT(*) FROM #FilterApprox a JOIN #FilterExact e
 ON e.CaseId=a.CaseId AND e.Id=a.Id WHERE a.CaseId=@FilterCase)<4
 THROW 51003,'Fixed broad filtered quality floor failed.',1;
 IF @FilterCase=3 AND EXISTS(SELECT 1 FROM #FilterApprox WHERE CaseId=3)
 THROW 51003,'Fixed narrow postfilter profile changed.',1;
 SELECT (SELECT N'FILTER_EXACT' kind,CaseId,Id,DistanceValue
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER) FROM #FilterExact WHERE CaseId=@FilterCase ORDER BY DistanceValue,Id;
 SELECT (SELECT N'FILTER_APPROX' kind,CaseId,Id,DistanceValue
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER) FROM #FilterApprox WHERE CaseId=@FilterCase ORDER BY DistanceValue,Id;
 SELECT (SELECT N'FILTER_MEASURED' kind,@FilterCase CaseId,@FilterLo Lo,@FilterHi Hi,
 (SELECT COUNT(*) FROM #FilterExact WHERE CaseId=@FilterCase) ExactRows,
 (SELECT COUNT(*) FROM #FilterApprox WHERE CaseId=@FilterCase) ApproxRows,
 (SELECT COUNT(*) FROM #FilterApprox a JOIN #FilterExact e ON e.CaseId=a.CaseId AND e.Id=a.Id
 WHERE a.CaseId=@FilterCase) RecallHits FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
 SET @FilterCase+=1;
END;
SELECT Id,DistanceValue INTO #FilterBad FROM #FilterApprox WHERE CaseId=2;
DECLARE @FilterBadCase int=0;
WHILE @FilterBadCase<4
BEGIN
 DELETE #FilterBad;INSERT #FilterBad SELECT Id,DistanceValue FROM #FilterApprox WHERE CaseId=2;
 IF @FilterBadCase=0 DELETE #FilterBad WHERE Id IN(SELECT TOP(2) Id FROM #FilterBad ORDER BY Id);
 IF @FilterBadCase=1 UPDATE #FilterBad SET Id=1001 WHERE Id=(SELECT MIN(Id) FROM #FilterBad);
 IF @FilterBadCase=2 UPDATE #FilterBad SET Id=501 WHERE Id=(SELECT MIN(Id) FROM #FilterBad);
 IF @FilterBadCase=3 UPDATE #FilterBad SET DistanceValue=DistanceValue+1 WHERE Id=(SELECT MIN(Id) FROM #FilterBad);
 IF (SELECT COUNT(*) FROM #FilterBad) BETWEEN 4 AND 5 AND NOT EXISTS(
 SELECT 1 FROM #FilterBad a LEFT JOIN lab.VectorFixture v ON v.Id=a.Id
 WHERE v.Id IS NULL OR a.Id NOT BETWEEN 1 AND 100 OR VECTOR_DISTANCE('cosine',v.V,@q) IS NULL
 OR ABS(a.DistanceValue-VECTOR_DISTANCE('cosine',v.V,@q))>0.0001)
 THROW 51003,'Filtered result negative accepted.',1;
 SET @FilterBadCase+=1;
END;
SELECT N'ANN_FILTER_NEGATIVE|4_REJECTED';

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


SET @IndexAfter=(SELECT * FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND name=N'IDX011_OwnVector' ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
IF DATALENGTH(@IndexBefore)<>DATALENGTH(@IndexAfter)
 OR CONVERT(varbinary(max),@IndexBefore)<>CONVERT(varbinary(max),@IndexAfter)
 THROW 51003,'Full index metadata changed.',1;
IF EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture
 EXCEPT SELECT Id,BytesValue FROM #Frozen) OR EXISTS(SELECT Id,BytesValue FROM #Frozen
 EXCEPT SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture)
 THROW 51003,'Full source vector binding changed.',1;
SELECT Id,BytesValue INTO #SourceNegative FROM #Frozen;
SET @Case=0;
WHILE @Case<3
BEGIN
 DELETE #SourceNegative;INSERT #SourceNegative SELECT Id,BytesValue FROM #Frozen;
 IF @Case=0 DELETE #SourceNegative WHERE Id=1000;
 IF @Case=1 INSERT #SourceNegative VALUES(1001,0x0100);
 IF @Case=2 UPDATE #SourceNegative SET BytesValue=0x0100 WHERE Id=1000;
 IF NOT EXISTS(SELECT Id,BytesValue FROM #SourceNegative EXCEPT SELECT Id,BytesValue FROM #Frozen)
 AND NOT EXISTS(SELECT Id,BytesValue FROM #Frozen EXCEPT SELECT Id,BytesValue FROM #SourceNegative)
 THROW 51003,'Source negative accepted.',1;
 SET @Case+=1;
END;
IF EXISTS(SELECT configuration_id,CONVERT(varbinary(max),name),value,value_in_use FROM sys.configurations
 EXCEPT SELECT * FROM #Host) OR EXISTS(SELECT * FROM #Host EXCEPT
 SELECT configuration_id,CONVERT(varbinary(max),name),value,value_in_use FROM sys.configurations)
 THROW 51003,'Host configuration changed.',1;
IF EXISTS(SELECT compatibility_level,recovery_model FROM sys.databases WHERE database_id=DB_ID()
 EXCEPT SELECT * FROM #Db) OR EXISTS(SELECT * FROM #Db EXCEPT
 SELECT compatibility_level,recovery_model FROM sys.databases WHERE database_id=DB_ID())
 OR EXISTS(SELECT file_id,type,CONVERT(varbinary(max),name),max_size,growth,is_percent_growth
 FROM sys.database_files EXCEPT SELECT * FROM #Files) OR EXISTS(SELECT * FROM #Files EXCEPT
 SELECT file_id,type,CONVERT(varbinary(max),name),max_size,growth,is_percent_growth FROM sys.database_files)
 THROW 51003,'Database options changed.',1;

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

SELECT CONCAT(N'ANN_PROBE|PASS|MARKER_NEG_',@Marker,N'|BASELINE_NEG_9|RESULT_NEG_3|SOURCE_NEG_3|JSON_ROWS_1000');


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

IF EXISTS(SELECT * FROM dbo.PreviewState EXCEPT SELECT * FROM #SavedBaseline)
 OR EXISTS(SELECT * FROM #SavedBaseline EXCEPT SELECT * FROM dbo.PreviewState)
 THROW 51003,'Full dual baseline changed.',1;
IF EXISTS(SELECT configuration_id,name,value,value_for_secondary,is_value_default FROM sys.database_scoped_configurations
 EXCEPT SELECT * FROM #Scoped) OR EXISTS(SELECT * FROM #Scoped EXCEPT
 SELECT configuration_id,name,value,value_for_secondary,is_value_default FROM sys.database_scoped_configurations)
 THROW 51003,'Full DB scoped configuration changed.',1;
IF EXISTS(SELECT name,class,major_id,minor_id,CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) FROM sys.extended_properties
 WHERE class=0 AND major_id=0 AND minor_id=0 EXCEPT SELECT * FROM #FullMarkers)
 OR EXISTS(SELECT * FROM #FullMarkers EXCEPT SELECT name,class,major_id,minor_id,
 CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0)
 THROW 51003,'Full database marker set changed.',1;

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
