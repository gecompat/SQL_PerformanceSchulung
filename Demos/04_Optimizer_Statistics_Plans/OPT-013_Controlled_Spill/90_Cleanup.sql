/* OPT-013 cleanup: marker-verified removal of the isolated spill database. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7)='$(DemoId)';
DECLARE @RunToken varchar(20)='$(RunToken)';
DECLARE @TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @Expected sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken);
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@ExistingDemo nvarchar(max),@ExistingRun nvarchar(max);
DECLARE @Sql nvarchar(max);

IF @DemoId<>'OPT-013' OR @TargetDatabase<>@Expected
    THROW 51000,'FAIL_CONTRACT: OPT-013-Cleanupziel ist ungültig.',1;

IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    SELECT 1 Sequence,'CLEANUP' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
           N'Zieldatenbank bereits nicht vorhanden' ObservedValue,N'idempotenter Cleanup' RequiredValue,
           N'Es war keine Bereinigung erforderlich.' Message;
    PRINT 'SQLPERF_SUMMARY|PASS|OK';
    RETURN;
END;

SET @Sql=N'SELECT
 @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max), value) END),
 @ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max), value) END),
 @DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max), value) END),
 @RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max), value) END)
FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties
WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,
 N'@ProjectOut nvarchar(max) OUTPUT,@ContractOut nvarchar(max) OUTPUT,@DemoOut nvarchar(max) OUTPUT,@RunOut nvarchar(max) OUTPUT',
 @ProjectOut=@Project OUTPUT,@ContractOut=@Contract OUTPUT,@DemoOut=@ExistingDemo OUTPUT,@RunOut=@ExistingRun OUTPUT;

IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2 <> N'SQL_PerformanceSchulung' OR DATALENGTH(@Project) <> DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2 <> N'1.0' OR DATALENGTH(@Contract) <> DATALENGTH(N'1.0')
   OR @ExistingDemo IS NULL OR @ExistingDemo COLLATE Latin1_General_100_BIN2 <> CONVERT(nvarchar(max), @DemoId) OR DATALENGTH(@ExistingDemo) <> DATALENGTH(CONVERT(nvarchar(max), @DemoId))
   OR @ExistingRun IS NULL OR @ExistingRun COLLATE Latin1_General_100_BIN2 <> CONVERT(nvarchar(max), @RunToken) OR DATALENGTH(@ExistingRun) <> DATALENGTH(CONVERT(nvarchar(max), @RunToken))
    THROW 51004,'FAIL_CLEANUP: OPT-013-Eigentumsmarker stimmen nicht vollständig überein.',1;

SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE '+QUOTENAME(@TargetDatabase)+N';';
EXEC sys.sp_executesql @Sql;

SELECT 1 Sequence,'CLEANUP' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       N'markierte OPT-013-Datenbank entfernt' ObservedValue,N'vollständige Markerübereinstimmung' RequiredValue,
       N'Der definierte Ausgangszustand ist wiederhergestellt.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
