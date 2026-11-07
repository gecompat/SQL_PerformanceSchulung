/* QRY-023: create or reuse only the exact marker-owned database. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken);
DECLARE @MajorVersion int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
DECLARE @ProductVersion nvarchar(128)=CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'));
DECLARE @ExpectedBuild nvarchar(128)=CASE @MajorVersion
    WHEN 15 THEN N'15.0.4500.2'
    WHEN 16 THEN N'16.0.4305.5'
    WHEN 17 THEN N'17.0.5035.5'
END;
DECLARE @CompatibilityLevel int=CASE @MajorVersion WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
DECLARE @Created bit=0,@Sql nvarchar(max),@Project nvarchar(max),@Contract nvarchar(max),@ExistingDemo nvarchar(max),@ExistingRun nvarchar(max);

IF @DemoId<>'QRY-023' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 20
   OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9_]%'
   OR @TargetDatabase<>@ExpectedDatabase OR @CompatibilityLevel IS NULL OR @ProductVersion IS NULL
   OR @ProductVersion COLLATE Latin1_General_100_BIN2<>@ExpectedBuild
    THROW 51000,'FAIL_CONTRACT: QRY-023-Zielkennung oder Engine-Version ist ungültig.',1;

IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    SET @Sql=N'CREATE DATABASE '+QUOTENAME(@TargetDatabase)+N';';
    EXEC sys.sp_executesql @Sql;
    SET @Created=1;
END;

IF @Created=1
BEGIN
    SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=@Demo;
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@Run;';
    BEGIN TRY
        EXEC sys.sp_executesql @Sql,N'@Demo varchar(7),@Run varchar(20)',@Demo=@DemoId,@Run=@RunToken;
    END TRY
    BEGIN CATCH
        SELECT 1 AS Sequence,'CLEANUP' AS Phase,'PRESERVE_DATABASE_AFTER_MARKER_ERROR' AS CheckId,'FAIL' AS Outcome,'FAIL_CLEANUP' AS Code,
               CONCAT(N'OriginalError=',ERROR_NUMBER(),N'; created target retained for ownership review') AS ObservedValue,
               N'No automatic removal before exact ownership markers are verified' AS RequiredValue,
               N'Die neu angelegte Datenbank bleibt bei Markerfehler erhalten; Cleanup benötigt manuelle Zustandsklärung.' AS Message;
        PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_CLEANUP';
        THROW;
    END CATCH;
END
ELSE
BEGIN
    SET @Sql=N'SELECT @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
@ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
@DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
@RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
    EXEC sys.sp_executesql @Sql,N'@ProjectOut nvarchar(max) OUTPUT,@ContractOut nvarchar(max) OUTPUT,@DemoOut nvarchar(max) OUTPUT,@RunOut nvarchar(max) OUTPUT',
         @ProjectOut=@Project OUTPUT,@ContractOut=@Contract OUTPUT,@DemoOut=@ExistingDemo OUTPUT,@RunOut=@ExistingRun OUTPUT;
    IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
       OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
       OR @ExistingDemo IS NULL OR @ExistingDemo COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@DemoId) OR DATALENGTH(@ExistingDemo)<>DATALENGTH(CONVERT(nvarchar(max),@DemoId))
       OR @ExistingRun IS NULL OR @ExistingRun COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@RunToken) OR DATALENGTH(@ExistingRun)<>DATALENGTH(CONVERT(nvarchar(max),@RunToken))
        THROW 51002,'FAIL_STATE: Gleichnamige Ziel-Datenbank besitzt nicht alle exakt passenden QRY-023-Eigentumsmarker.',1;
END;

SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET RECOVERY SIMPLE;
ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_CLOSE OFF;
ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_SHRINK OFF;
ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET PAGE_VERIFY CHECKSUM;
ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET COMPATIBILITY_LEVEL='+CONVERT(nvarchar(10),@CompatibilityLevel)+N';';
EXEC sys.sp_executesql @Sql;

SELECT 1 AS Sequence,'SETUP' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'Database=',@TargetDatabase,N'; CompatibilityLevel=',@CompatibilityLevel,N'; Created=',@Created) AS ObservedValue,
       N'isolierte, vollständig markierte und versionsgebundene Datenbank' AS RequiredValue,
       N'Die QRY-023-Zieldatenbank ist bereit.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
