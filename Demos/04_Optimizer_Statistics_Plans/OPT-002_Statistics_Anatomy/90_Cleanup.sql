/* OPT-002 cleanup: marker-verified database removal. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @Expected sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken);
DECLARE @P nvarchar(max),@C nvarchar(max),@D nvarchar(max),@R nvarchar(max),@Sql nvarchar(max);
IF @DemoId<>'OPT-002' OR @TargetDatabase<>@Expected THROW 51000,'FAIL_CONTRACT: OPT-002-Cleanupziel ist ungültig.',1;
IF DB_ID(@TargetDatabase) IS NULL BEGIN SELECT 1 Sequence,'CLEANUP' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,N'bereits nicht vorhanden' ObservedValue,N'idempotent' RequiredValue,N'Kein Cleanup erforderlich.' Message;PRINT 'SQLPERF_SUMMARY|PASS|OK';RETURN;END;
SET @Sql=N'SELECT @P=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max), value) END),@C=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max), value) END),@D=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max), value) END),@R=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max), value) END) FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@P nvarchar(max) OUTPUT,@C nvarchar(max) OUTPUT,@D nvarchar(max) OUTPUT,@R nvarchar(max) OUTPUT',@P=@P OUTPUT,@C=@C OUTPUT,@D=@D OUTPUT,@R=@R OUTPUT;
IF @P IS NULL OR @P COLLATE Latin1_General_100_BIN2 <> N'SQL_PerformanceSchulung' OR DATALENGTH(@P) <> DATALENGTH(N'SQL_PerformanceSchulung')
   OR @C IS NULL OR @C COLLATE Latin1_General_100_BIN2 <> N'1.0' OR DATALENGTH(@C) <> DATALENGTH(N'1.0')
   OR @D IS NULL OR @D COLLATE Latin1_General_100_BIN2 <> CONVERT(nvarchar(max), @DemoId) OR DATALENGTH(@D) <> DATALENGTH(CONVERT(nvarchar(max), @DemoId))
   OR @R IS NULL OR @R COLLATE Latin1_General_100_BIN2 <> CONVERT(nvarchar(max), @RunToken) OR DATALENGTH(@R) <> DATALENGTH(CONVERT(nvarchar(max), @RunToken)) THROW 51004,'FAIL_CLEANUP: OPT-002-Eigentumsmarker stimmen nicht überein.',1;
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE '+QUOTENAME(@TargetDatabase)+N';';EXEC sys.sp_executesql @Sql;
SELECT 1 Sequence,'CLEANUP' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,N'markierte OPT-002-Datenbank entfernt' ObservedValue,N'vollständige Markerübereinstimmung' RequiredValue,N'Ausgangszustand wiederhergestellt.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
