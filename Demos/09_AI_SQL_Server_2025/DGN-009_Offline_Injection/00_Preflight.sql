/* DGN-009: Manipulierte Quellen und feste Offline-Toolpolicy; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)', @RunToken varchar(16)='$(RunToken)', @TargetDatabase sysname=N'$(TargetDatabase)';
IF @DemoId <> 'DGN-009' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 16
 OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9]%'
 OR CONVERT(varbinary(max),@TargetDatabase) <> CONVERT(varbinary(max),CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken))
 THROW 51000,'FAIL_CONTRACT: Demo-ID, Run-Token oder Zieldatenbank ist ungueltig.',1;
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
IF @Major<>17 BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION'; RETURN; END;
IF CONVERT(int,SERVERPROPERTY('EngineEdition')) NOT IN (2,3,4) BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PLATFORM'; RETURN; END;
IF COALESCE(HAS_PERMS_BY_NAME(NULL,NULL,'CREATE ANY DATABASE'),0)<>1 AND COALESCE(HAS_PERMS_BY_NAME(N'master','DATABASE','CREATE DATABASE'),0)<>1 BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION'; RETURN; END;
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@ExistingDemo nvarchar(max),@ExistingRun nvarchar(max),@Sql nvarchar(max);
IF DB_ID(@TargetDatabase) IS NOT NULL
BEGIN
 SET @Sql=N'SELECT @P=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
 @C=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
 @D=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
 @R=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
 FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
 EXEC sys.sp_executesql @Sql,N'@P nvarchar(max) OUTPUT,@C nvarchar(max) OUTPUT,@D nvarchar(max) OUTPUT,@R nvarchar(max) OUTPUT',@P=@Project OUTPUT,@C=@Contract OUTPUT,@D=@ExistingDemo OUTPUT,@R=@ExistingRun OUTPUT;
 IF CONVERT(varbinary(max),ISNULL(@Project,N'')) <> CONVERT(varbinary(max),N'SQL_PerformanceSchulung')
 OR CONVERT(varbinary(max),ISNULL(@Contract,N'')) <> CONVERT(varbinary(max),N'1.0')
 OR CONVERT(varbinary(max),ISNULL(@ExistingDemo,N'')) <> CONVERT(varbinary(max),CONVERT(nvarchar(max),@DemoId))
 OR CONVERT(varbinary(max),ISNULL(@ExistingRun,N'')) <> CONVERT(varbinary(max),CONVERT(nvarchar(max),@RunToken))
 THROW 51004,'FAIL_STATE: Eigentumsmarker stimmen nicht vollstaendig und exakt ueberein.',1;
END;
BEGIN TRY EXEC sys.sp_executesql N'DECLARE @v VECTOR(3)=''[3,4,0]''; SELECT VECTORPROPERTY(@v,''Dimensions''),VECTOR_NORM(@v,''norm2'');'; END TRY
BEGIN CATCH IF ERROR_NUMBER() NOT IN (195,243,2715,4121) THROW; PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_FEATURE_UNAVAILABLE'; RETURN; END CATCH;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
