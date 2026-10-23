SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 15000;
DECLARE @DemoRaw nvarchar(max)=N'$(DemoId)', @RunRaw nvarchar(max)=N'$(RunToken)',
        @TargetRaw nvarchar(max)=N'$(TargetDatabase)';
DECLARE @TrimmedRun nvarchar(max)=LTRIM(RTRIM(@RunRaw));
IF @DemoRaw IS NULL OR @DemoRaw COLLATE Latin1_General_100_BIN2<>N'OPT-007' OR DATALENGTH(@DemoRaw)<>14
   OR @TrimmedRun IS NULL OR DATALENGTH(@TrimmedRun) NOT BETWEEN 2 AND 32
   OR @TrimmedRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Za-z0-9]%'
    THROW 51000,'FAIL_CONTRACT: Ungültige vollständige Demo-/Laufkennung.',1;
DECLARE @Run nvarchar(max)=UPPER(@TrimmedRun COLLATE Latin1_General_100_BIN2);
DECLARE @Expected nvarchar(max)=N'SQLPERF_LAB_OPT007_'+@Run;
IF @TargetRaw IS NULL OR @TargetRaw COLLATE Latin1_General_100_BIN2<>@Expected OR DATALENGTH(@TargetRaw)<>DATALENGTH(@Expected)
    THROW 51000,'FAIL_CONTRACT: Ungültiger vollständiger Zieldatenbankname.',1;
DECLARE @Target sysname=CONVERT(sysname,@Expected), @Sql nvarchar(max);
IF @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2 THROW 51002,'FAIL_STATE: Keine explizite oder implizite Transaktion am Einstieg erlaubt.',1;

IF ISNULL(TRY_CONVERT(int,N'$(ConfirmIsolatedLab)'),0)<>1
   OR ISNULL(TRY_CONVERT(int,N'$(HighImpactConfirmed)'),0)<>1
   OR ISNULL(TRY_CONVERT(int,N'$(MaximumRuntimeSeconds)'),0) NOT BETWEEN 1 AND 120
    THROW 51001,'FAIL_SAFETY: Isoliertes Lab, Hochlastbestätigung und Budget von 1 bis 120 Sekunden erforderlich.',1;

IF DB_ID(@Target)<=4 OR NOT EXISTS(SELECT 1 FROM sys.databases WHERE database_id=DB_ID(@Target) AND state=0 AND is_read_only=0)
    THROW 51002,'FAIL_STATE: Zieldatenbank fehlt, ist geschützt oder nicht online und schreibbar.',1;
DECLARE @P nvarchar(max),@C nvarchar(max),@D nvarchar(max),@R nvarchar(max);
SET @Sql=N'SELECT @P=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
 @C=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
 @D=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
 @R=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
 FROM '+QUOTENAME(@Target)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@P nvarchar(max) OUTPUT,@C nvarchar(max) OUTPUT,@D nvarchar(max) OUTPUT,@R nvarchar(max) OUTPUT',@P OUTPUT,@C OUTPUT,@D OUTPUT,@R OUTPUT;
IF @P IS NULL OR @P COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@P)<>DATALENGTH(N'SQL_PerformanceSchulung')
 OR @C IS NULL OR @C COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@C)<>DATALENGTH(N'1.0')
 OR @D IS NULL OR @D COLLATE Latin1_General_100_BIN2<>@DemoRaw OR DATALENGTH(@D)<>DATALENGTH(@DemoRaw)
 OR @R IS NULL OR @R COLLATE Latin1_General_100_BIN2<>@Run OR DATALENGTH(@R)<>DATALENGTH(@Run)
    THROW 51002,'FAIL_STATE: Vollständige Eigentumsmarker fehlen oder weichen ab; Datenbank bleibt erhalten.',1;

USE [$(TargetDatabase)];
SET ANSI_NULLS ON;SET ANSI_PADDING ON;SET ANSI_WARNINGS ON;SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;SET QUOTED_IDENTIFIER ON;SET NUMERIC_ROUNDABORT OFF;
SET LANGUAGE us_english;SET DATEFORMAT mdy;SET DATEFIRST 7;
EXEC lab.USP_Context @Run,0;
IF EXISTS(SELECT 1 FROM lab.CacheState) OR EXISTS(SELECT 1 FROM lab.CacheSnapshot) OR EXISTS(SELECT 1 FROM lab.CacheResult)
 THROW 51002,'FAIL_STATE: Frischer Lauf benötigt leere Evidenz.',1;
INSERT lab.CacheState SELECT 1,SYSUTCDATETIME(),@Run,DB_ID(),1,@@OPTIONS,
 (SELECT name,value,value_for_secondary FROM sys.database_scoped_configurations ORDER BY name FOR XML RAW,ROOT('Config'),TYPE),
 (SELECT is_parameterization_forced FROM sys.databases WHERE database_id=DB_ID()),
 (SELECT compatibility_level FROM sys.databases WHERE database_id=DB_ID()),@@LANGID,@@DATEFIRST,
 (SELECT date_format FROM sys.dm_exec_sessions WHERE session_id=@@SPID);
EXEC lab.USP_Capture @Run,'L',0,1;
EXEC lab.USP_Capture @Run,'P',0,1;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
