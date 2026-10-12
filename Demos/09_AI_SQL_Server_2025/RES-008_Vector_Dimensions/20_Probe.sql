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

IF (SELECT COUNT(*) FROM lab.V32)<>100
 OR EXISTS(SELECT 1 FROM lab.V32 WHERE Id NOT BETWEEN 1 AND 100)
 OR EXISTS(SELECT 1 FROM lab.V32 v
 WHERE (SELECT COUNT(*) FROM OPENJSON(CONVERT(varchar(max),v.V)))<>32
 OR EXISTS(SELECT 1 FROM OPENJSON(CONVERT(varchar(max),v.V))j
 WHERE j.type<>2 OR TRY_CONVERT(int,j.[key]) IS NULL
 OR TRY_CONVERT(int,j.[key]) NOT BETWEEN 0 AND 32-1
 OR TRY_CONVERT(float,j.value) IS NULL
 OR TRY_CONVERT(float,j.value)<>CASE WHEN TRY_CONVERT(int,j.[key])=0 THEN CONVERT(float,v.Id)
 WHEN TRY_CONVERT(int,j.[key])=1 THEN 1.0 ELSE 0.0 END))
 THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige RES008-Quellenfixture verletzt.',1;
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.V32') AND name=N'V'
 AND vector_dimensions=32 AND vector_base_type=0 AND is_nullable=0)
 THROW 51003,'FAIL_RESULT_CONTRACT: RES008-Dimension/float32 verletzt.',1;
SELECT 'RES008_SOURCE|32|'+CONVERT(varchar(10),Id)+'|'+CONVERT(varchar(10),DATALENGTH(CONVERT(varchar(max),V)))+'|'
 +CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),CONVERT(varchar(max),V))),2)
FROM lab.V32 ORDER BY Id;
SELECT 'RES008_STORAGE|32|'+CONVERT(varchar(20),p.row_count)+'|'+CONVERT(varchar(20),p.in_row_data_page_count)
 +'|'+CONVERT(varchar(20),p.used_page_count)+'|'+CONVERT(varchar(20),p.reserved_page_count)
 +'|'+CONVERT(varchar(20),s.MinBytes)+'|'+CONVERT(varchar(20),s.MaxBytes)
FROM sys.dm_db_partition_stats p CROSS JOIN(SELECT MIN(DATALENGTH(V))MinBytes,MAX(DATALENGTH(V))MaxBytes FROM lab.V32)s
WHERE p.object_id=OBJECT_ID(N'lab.V32') AND p.index_id=1;
DECLARE @Q32 VECTOR(32)=CONVERT(VECTOR(32),'[1,1'+REPLICATE(',0',32-2)+']');
SELECT TOP(1) 'RES008_QUERY|32|'+CONVERT(varchar(10),Id)+'|'+CONVERT(varchar(40),VECTOR_DISTANCE('cosine',V,@Q32),3)
FROM lab.V32 ORDER BY VECTOR_DISTANCE('cosine',V,@Q32),Id OPTION(MAXDOP 1);

IF (SELECT COUNT(*) FROM lab.V384)<>100
 OR EXISTS(SELECT 1 FROM lab.V384 WHERE Id NOT BETWEEN 1 AND 100)
 OR EXISTS(SELECT 1 FROM lab.V384 v
 WHERE (SELECT COUNT(*) FROM OPENJSON(CONVERT(varchar(max),v.V)))<>384
 OR EXISTS(SELECT 1 FROM OPENJSON(CONVERT(varchar(max),v.V))j
 WHERE j.type<>2 OR TRY_CONVERT(int,j.[key]) IS NULL
 OR TRY_CONVERT(int,j.[key]) NOT BETWEEN 0 AND 384-1
 OR TRY_CONVERT(float,j.value) IS NULL
 OR TRY_CONVERT(float,j.value)<>CASE WHEN TRY_CONVERT(int,j.[key])=0 THEN CONVERT(float,v.Id)
 WHEN TRY_CONVERT(int,j.[key])=1 THEN 1.0 ELSE 0.0 END))
 THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige RES008-Quellenfixture verletzt.',1;
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.V384') AND name=N'V'
 AND vector_dimensions=384 AND vector_base_type=0 AND is_nullable=0)
 THROW 51003,'FAIL_RESULT_CONTRACT: RES008-Dimension/float32 verletzt.',1;
SELECT 'RES008_SOURCE|384|'+CONVERT(varchar(10),Id)+'|'+CONVERT(varchar(10),DATALENGTH(CONVERT(varchar(max),V)))+'|'
 +CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),CONVERT(varchar(max),V))),2)
FROM lab.V384 ORDER BY Id;
SELECT 'RES008_STORAGE|384|'+CONVERT(varchar(20),p.row_count)+'|'+CONVERT(varchar(20),p.in_row_data_page_count)
 +'|'+CONVERT(varchar(20),p.used_page_count)+'|'+CONVERT(varchar(20),p.reserved_page_count)
 +'|'+CONVERT(varchar(20),s.MinBytes)+'|'+CONVERT(varchar(20),s.MaxBytes)
FROM sys.dm_db_partition_stats p CROSS JOIN(SELECT MIN(DATALENGTH(V))MinBytes,MAX(DATALENGTH(V))MaxBytes FROM lab.V384)s
WHERE p.object_id=OBJECT_ID(N'lab.V384') AND p.index_id=1;
DECLARE @Q384 VECTOR(384)=CONVERT(VECTOR(384),'[1,1'+REPLICATE(',0',384-2)+']');
SELECT TOP(1) 'RES008_QUERY|384|'+CONVERT(varchar(10),Id)+'|'+CONVERT(varchar(40),VECTOR_DISTANCE('cosine',V,@Q384),3)
FROM lab.V384 ORDER BY VECTOR_DISTANCE('cosine',V,@Q384),Id OPTION(MAXDOP 1);

IF (SELECT COUNT(*) FROM lab.V768)<>100
 OR EXISTS(SELECT 1 FROM lab.V768 WHERE Id NOT BETWEEN 1 AND 100)
 OR EXISTS(SELECT 1 FROM lab.V768 v
 WHERE (SELECT COUNT(*) FROM OPENJSON(CONVERT(varchar(max),v.V)))<>768
 OR EXISTS(SELECT 1 FROM OPENJSON(CONVERT(varchar(max),v.V))j
 WHERE j.type<>2 OR TRY_CONVERT(int,j.[key]) IS NULL
 OR TRY_CONVERT(int,j.[key]) NOT BETWEEN 0 AND 768-1
 OR TRY_CONVERT(float,j.value) IS NULL
 OR TRY_CONVERT(float,j.value)<>CASE WHEN TRY_CONVERT(int,j.[key])=0 THEN CONVERT(float,v.Id)
 WHEN TRY_CONVERT(int,j.[key])=1 THEN 1.0 ELSE 0.0 END))
 THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige RES008-Quellenfixture verletzt.',1;
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.V768') AND name=N'V'
 AND vector_dimensions=768 AND vector_base_type=0 AND is_nullable=0)
 THROW 51003,'FAIL_RESULT_CONTRACT: RES008-Dimension/float32 verletzt.',1;
SELECT 'RES008_SOURCE|768|'+CONVERT(varchar(10),Id)+'|'+CONVERT(varchar(10),DATALENGTH(CONVERT(varchar(max),V)))+'|'
 +CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),CONVERT(varchar(max),V))),2)
FROM lab.V768 ORDER BY Id;
SELECT 'RES008_STORAGE|768|'+CONVERT(varchar(20),p.row_count)+'|'+CONVERT(varchar(20),p.in_row_data_page_count)
 +'|'+CONVERT(varchar(20),p.used_page_count)+'|'+CONVERT(varchar(20),p.reserved_page_count)
 +'|'+CONVERT(varchar(20),s.MinBytes)+'|'+CONVERT(varchar(20),s.MaxBytes)
FROM sys.dm_db_partition_stats p CROSS JOIN(SELECT MIN(DATALENGTH(V))MinBytes,MAX(DATALENGTH(V))MaxBytes FROM lab.V768)s
WHERE p.object_id=OBJECT_ID(N'lab.V768') AND p.index_id=1;
DECLARE @Q768 VECTOR(768)=CONVERT(VECTOR(768),'[1,1'+REPLICATE(',0',768-2)+']');
SELECT TOP(1) 'RES008_QUERY|768|'+CONVERT(varchar(10),Id)+'|'+CONVERT(varchar(40),VECTOR_DISTANCE('cosine',V,@Q768),3)
FROM lab.V768 ORDER BY VECTOR_DISTANCE('cosine',V,@Q768),Id OPTION(MAXDOP 1);

IF (SELECT COUNT(*) FROM lab.V1536)<>100
 OR EXISTS(SELECT 1 FROM lab.V1536 WHERE Id NOT BETWEEN 1 AND 100)
 OR EXISTS(SELECT 1 FROM lab.V1536 v
 WHERE (SELECT COUNT(*) FROM OPENJSON(CONVERT(varchar(max),v.V)))<>1536
 OR EXISTS(SELECT 1 FROM OPENJSON(CONVERT(varchar(max),v.V))j
 WHERE j.type<>2 OR TRY_CONVERT(int,j.[key]) IS NULL
 OR TRY_CONVERT(int,j.[key]) NOT BETWEEN 0 AND 1536-1
 OR TRY_CONVERT(float,j.value) IS NULL
 OR TRY_CONVERT(float,j.value)<>CASE WHEN TRY_CONVERT(int,j.[key])=0 THEN CONVERT(float,v.Id)
 WHEN TRY_CONVERT(int,j.[key])=1 THEN 1.0 ELSE 0.0 END))
 THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige RES008-Quellenfixture verletzt.',1;
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.V1536') AND name=N'V'
 AND vector_dimensions=1536 AND vector_base_type=0 AND is_nullable=0)
 THROW 51003,'FAIL_RESULT_CONTRACT: RES008-Dimension/float32 verletzt.',1;
SELECT 'RES008_SOURCE|1536|'+CONVERT(varchar(10),Id)+'|'+CONVERT(varchar(10),DATALENGTH(CONVERT(varchar(max),V)))+'|'
 +CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),CONVERT(varchar(max),V))),2)
FROM lab.V1536 ORDER BY Id;
SELECT 'RES008_STORAGE|1536|'+CONVERT(varchar(20),p.row_count)+'|'+CONVERT(varchar(20),p.in_row_data_page_count)
 +'|'+CONVERT(varchar(20),p.used_page_count)+'|'+CONVERT(varchar(20),p.reserved_page_count)
 +'|'+CONVERT(varchar(20),s.MinBytes)+'|'+CONVERT(varchar(20),s.MaxBytes)
FROM sys.dm_db_partition_stats p CROSS JOIN(SELECT MIN(DATALENGTH(V))MinBytes,MAX(DATALENGTH(V))MaxBytes FROM lab.V1536)s
WHERE p.object_id=OBJECT_ID(N'lab.V1536') AND p.index_id=1;
DECLARE @Q1536 VECTOR(1536)=CONVERT(VECTOR(1536),'[1,1'+REPLICATE(',0',1536-2)+']');
SELECT TOP(1) 'RES008_QUERY|1536|'+CONVERT(varchar(10),Id)+'|'+CONVERT(varchar(40),VECTOR_DISTANCE('cosine',V,@Q1536),3)
FROM lab.V1536 ORDER BY VECTOR_DISTANCE('cosine',V,@Q1536),Id OPTION(MAXDOP 1);
SELECT 'RES008_DB_CONFIG|'+name+'|'+CONVERT(varchar(20),value) FROM sys.database_scoped_configurations WHERE name IN(N'PREVIEW_FEATURES',N'MAXDOP') ORDER BY name;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
