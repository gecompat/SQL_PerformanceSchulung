SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 15000;
DECLARE @DemoRaw nvarchar(max)=N'$(DemoId)', @RunRaw nvarchar(max)=N'$(RunToken)',
        @TargetRaw nvarchar(max)=N'$(TargetDatabase)';
DECLARE @TrimmedRun nvarchar(max)=LTRIM(RTRIM(@RunRaw));
IF @DemoRaw IS NULL OR @DemoRaw COLLATE Latin1_General_100_BIN2<>N'CON-005' OR DATALENGTH(@DemoRaw)<>14
   OR @TrimmedRun IS NULL OR DATALENGTH(@TrimmedRun) NOT BETWEEN 2 AND 32
   OR @TrimmedRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Za-z0-9]%'
    THROW 51000,'FAIL_CONTRACT: Ungültige vollständige Demo-/Laufkennung.',1;
DECLARE @Run nvarchar(max)=UPPER(@TrimmedRun COLLATE Latin1_General_100_BIN2);
DECLARE @Expected nvarchar(max)=N'SQLPERF_LAB_CON005_'+@Run;
IF @TargetRaw IS NULL OR @TargetRaw COLLATE Latin1_General_100_BIN2<>@Expected OR DATALENGTH(@TargetRaw)<>DATALENGTH(@Expected)
    THROW 51000,'FAIL_CONTRACT: Ungültiger vollständiger Zieldatenbankname.',1;
DECLARE @Target sysname=CONVERT(sysname,@Expected), @Sql nvarchar(max);
IF @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2 THROW 51002,'FAIL_STATE: Keine explizite oder implizite Transaktion am Einstieg erlaubt.',1;

IF ISNULL(TRY_CONVERT(int,N'$(ConfirmIsolatedLab)'),0)<>1
   OR ISNULL(TRY_CONVERT(int,N'$(HighImpactConfirmed)'),0)<>1
   OR ISNULL(TRY_CONVERT(int,N'$(MaximumRuntimeSeconds)'),0) NOT BETWEEN 1 AND 120
    THROW 51001,'FAIL_SAFETY: Isoliertes Lab, Hochlastbestätigung und Budget von 1 bis 120 Sekunden erforderlich.',1;

DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')),
 @Edition int=TRY_CONVERT(int,SERVERPROPERTY('EngineEdition'));
IF @Major NOT IN(15,16,17) BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'SUMMARY' CheckId,'SKIP' Outcome,'SKIP_VERSION' Code,N'nicht erfüllt' ObservedValue,N'CON-005-Voraussetzung' RequiredValue,N'SQL Server 2019, 2022 oder 2025 erforderlich.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';RETURN;END;
IF @Edition NOT IN(2,3,4) BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'SUMMARY' CheckId,'SKIP' Outcome,'SKIP_EDITION' Code,N'nicht erfüllt' ObservedValue,N'CON-005-Voraussetzung' RequiredValue,N'Eigenständige Database Engine erforderlich.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EDITION';RETURN;END;
DECLARE @State bit=0;
IF @Major>=16 SET @State=CASE WHEN HAS_PERMS_BY_NAME(NULL,NULL,'VIEW SERVER PERFORMANCE STATE')=1 THEN 1 ELSE 0 END;
ELSE SET @State=CASE WHEN HAS_PERMS_BY_NAME(NULL,NULL,'VIEW SERVER STATE')=1 THEN 1 ELSE 0 END;
IF @State=0 OR NOT(HAS_PERMS_BY_NAME(NULL,NULL,'CREATE ANY DATABASE')=1 OR IS_SRVROLEMEMBER('sysadmin')=1)
BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'SUMMARY' CheckId,'SKIP' Outcome,'SKIP_PERMISSION' Code,N'nicht erfüllt' ObservedValue,N'CON-005-Voraussetzung' RequiredValue,N'Datenbankerstellung beziehungsweise Kontrolle und Diagnoseberechtigung erforderlich.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';RETURN;END;
IF DB_ID(@Target) IS NOT NULL
BEGIN

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

 IF HAS_PERMS_BY_NAME(@Target,'DATABASE','CONTROL')<>1
 BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'SUMMARY' CheckId,'SKIP' Outcome,'SKIP_PERMISSION' Code,N'nicht erfüllt' ObservedValue,N'CON-005-Voraussetzung' RequiredValue,N'Datenbankerstellung beziehungsweise Kontrolle und Diagnoseberechtigung erforderlich.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';RETURN;END;
END;
SELECT 1 Sequence,'PREFLIGHT' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
 N'CON-005' ObservedValue,N'begrenzter Schemasperrenvertrag' RequiredValue,N'Voraussetzungen und isolierter Sicherheitsrahmen bestätigt.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
