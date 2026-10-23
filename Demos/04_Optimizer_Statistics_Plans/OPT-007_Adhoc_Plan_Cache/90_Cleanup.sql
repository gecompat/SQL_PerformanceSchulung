USE [master];

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

IF DB_ID(@Target) IS NULL BEGIN PRINT 'SQLPERF_SUMMARY|PASS|OK';RETURN;END;

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

-- Bereits vollständig gebundene Handles vor dem Drop kopieren; kein Querytext-/Planexport.
DECLARE @Handles TABLE(Handle varbinary(64) PRIMARY KEY);
SET @Sql=N'IF OBJECT_ID(N'''+QUOTENAME(@Target)+N'.lab.CacheSnapshot'') IS NOT NULL SELECT DISTINCT Handle FROM '+QUOTENAME(@Target)+N'.lab.CacheSnapshot;';
INSERT @Handles EXEC sys.sp_executesql @Sql;
-- Auch vor dem ersten 20er-Messpunkt abgebrochene eigene Aufrufe binden.
INSERT @Handles
SELECT cp.plan_handle FROM sys.dm_exec_cached_plans cp
CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) st
WHERE EXISTS(SELECT 1 FROM sys.dm_exec_plan_attributes(cp.plan_handle) a WHERE a.attribute='dbid' AND CONVERT(int,a.value)=DB_ID(@Target))
 AND (CHARINDEX(N'/* OPT-007:'+@Run+N':LITERAL */',st.text COLLATE Latin1_General_100_BIN2)>0
  OR CHARINDEX(N'/* OPT-007:'+@Run+N':PARAMETER */',st.text COLLATE Latin1_General_100_BIN2)>0)
 AND NOT EXISTS(SELECT 1 FROM @Handles h WHERE h.Handle=cp.plan_handle);
-- Vor dem mutierenden Abbau sämtliche Marker erneut exakt gelesen; keine fremden Datenbanken.
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@Target)+N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE;DROP DATABASE '+QUOTENAME(@Target)+N';';
EXEC sys.sp_executesql @Sql;

DECLARE @Until datetime2(3)=DATEADD(second,15,SYSUTCDATETIME());
WHILE EXISTS(SELECT 1 FROM sys.dm_exec_cached_plans cp JOIN @Handles h ON h.Handle=cp.plan_handle)
BEGIN
 IF SYSUTCDATETIME()>=@Until THROW 51004,'FAIL_CLEANUP: Zuvor gebundene eigene Cacheobjekte verbleiben.',1;
 WAITFOR DELAY '00:00:00.100';
END;
IF DB_ID(@Target) IS NOT NULL THROW 51004,'FAIL_CLEANUP: Eigene Datenbank verbleibt.',1;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
