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

DECLARE @Dimension int=$(Dimension);
IF @Dimension NOT IN(32,384,768,1536) THROW 51000,'FAIL_CONTRACT: Fixed dimensions required.',1;
IF @Dimension=32
BEGIN
 DECLARE @Q32 VECTOR(32)=CONVERT(VECTOR(32),'[1,1'+REPLICATE(',0',32-2)+']');
 SET STATISTICS XML ON;
 SELECT TOP(1) Id,VECTOR_DISTANCE('cosine',V,@Q32) AS DistanceValue FROM lab.V32 ORDER BY VECTOR_DISTANCE('cosine',V,@Q32),Id OPTION(MAXDOP 1);
 SET STATISTICS XML OFF;
END;
IF @Dimension=384
BEGIN
 DECLARE @Q384 VECTOR(384)=CONVERT(VECTOR(384),'[1,1'+REPLICATE(',0',384-2)+']');
 SET STATISTICS XML ON;
 SELECT TOP(1) Id,VECTOR_DISTANCE('cosine',V,@Q384) AS DistanceValue FROM lab.V384 ORDER BY VECTOR_DISTANCE('cosine',V,@Q384),Id OPTION(MAXDOP 1);
 SET STATISTICS XML OFF;
END;
IF @Dimension=768
BEGIN
 DECLARE @Q768 VECTOR(768)=CONVERT(VECTOR(768),'[1,1'+REPLICATE(',0',768-2)+']');
 SET STATISTICS XML ON;
 SELECT TOP(1) Id,VECTOR_DISTANCE('cosine',V,@Q768) AS DistanceValue FROM lab.V768 ORDER BY VECTOR_DISTANCE('cosine',V,@Q768),Id OPTION(MAXDOP 1);
 SET STATISTICS XML OFF;
END;
IF @Dimension=1536
BEGIN
 DECLARE @Q1536 VECTOR(1536)=CONVERT(VECTOR(1536),'[1,1'+REPLICATE(',0',1536-2)+']');
 SET STATISTICS XML ON;
 SELECT TOP(1) Id,VECTOR_DISTANCE('cosine',V,@Q1536) AS DistanceValue FROM lab.V1536 ORDER BY VECTOR_DISTANCE('cosine',V,@Q1536),Id OPTION(MAXDOP 1);
 SET STATISTICS XML OFF;
END;
SELECT 'SQLPERF_SUMMARY|PASS|OK';
