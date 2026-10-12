/* CON-010: Tenant-Isolation vor dem Vektorkontext; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @RawDemo nvarchar(max)=N'$(DemoId)',@RawRun nvarchar(max)=N'$(RunToken)',@RawTarget nvarchar(max)=N'$(TargetDatabase)';
IF DATALENGTH(@RawDemo)<>14 OR CONVERT(varbinary(max),@RawDemo)<>CONVERT(varbinary(max),N'CON-010')
 OR DATALENGTH(@RawRun) NOT BETWEEN 2 AND 32 OR @RawRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
 OR DATALENGTH(@RawTarget)<>DATALENGTH(N'SQLPERF_LAB_CON010_'+@RawRun)
 OR CONVERT(varbinary(max),@RawTarget)<>CONVERT(varbinary(max),N'SQLPERF_LAB_CON010_'+@RawRun)
 THROW 51000,'FAIL_CONTRACT: Vollstaendige Demo-/Run-/Zielbindung verletzt.',1;
DECLARE @DemoId varchar(7)=CONVERT(varchar(7),@RawDemo),@RunToken varchar(16)=CONVERT(varchar(16),@RawRun),@TargetDatabase sysname=CONVERT(sysname,@RawTarget);
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
IF @Major<>17 BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION'; RETURN; END;
IF CONVERT(int,SERVERPROPERTY('EngineEdition')) NOT IN (2,3,4) BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PLATFORM'; RETURN; END;
IF COALESCE(HAS_PERMS_BY_NAME(NULL,NULL,'CREATE ANY DATABASE'),0)<>1 AND COALESCE(HAS_PERMS_BY_NAME(N'master','DATABASE','CREATE DATABASE'),0)<>1 BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION'; RETURN; END;
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
BEGIN TRY EXEC sys.sp_executesql N'DECLARE @v VECTOR(3)=''[3,4,0]''; SELECT VECTORPROPERTY(@v,''Dimensions''),VECTOR_NORM(@v,''norm2'');'; END TRY
BEGIN CATCH IF ERROR_NUMBER() NOT IN (195,243,2715,4121) THROW; PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_FEATURE_UNAVAILABLE'; RETURN; END CATCH;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
