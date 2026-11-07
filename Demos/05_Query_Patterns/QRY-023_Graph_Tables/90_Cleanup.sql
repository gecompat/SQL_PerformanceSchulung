/* Remove the database only after complete project/demo/run ownership checks. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken);
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@ExistingDemo nvarchar(max),@ExistingRun nvarchar(max),@Sql nvarchar(max);

IF @DemoId<>'QRY-023' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 20
   OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9_]%' OR @TargetDatabase<>@ExpectedDatabase
    THROW 51000,'FAIL_CONTRACT: QRY-023-Cleanupziel ist ungültig.',1;

IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    SELECT 1 AS Sequence,'CLEANUP' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
           N'Zieldatenbank ist bereits nicht vorhanden' AS ObservedValue,N'idempotenter Cleanup' AS RequiredValue,
           N'Es war keine Bereinigung erforderlich.' AS Message;
    PRINT 'SQLPERF_SUMMARY|PASS|OK';
    RETURN;
END;

SET @Sql=N'SELECT @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
@ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
@DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
@RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@ProjectOut nvarchar(max) OUTPUT,@ContractOut nvarchar(max) OUTPUT,@DemoOut nvarchar(max) OUTPUT,@RunOut nvarchar(max) OUTPUT',
     @ProjectOut=@Project OUTPUT,@ContractOut=@Contract OUTPUT,@DemoOut=@ExistingDemo OUTPUT,@RunOut=@ExistingRun OUTPUT;
IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
   OR @ExistingDemo IS NULL OR @ExistingDemo COLLATE Latin1_General_100_BIN2<>N'QRY-023' OR DATALENGTH(@ExistingDemo)<>DATALENGTH(N'QRY-023')
   OR @ExistingRun IS NULL OR @ExistingRun COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@RunToken) OR DATALENGTH(@ExistingRun)<>DATALENGTH(CONVERT(nvarchar(max),@RunToken))
    THROW 51004,'FAIL_CLEANUP: Die vollständigen QRY-023-Eigentumsmarker stimmen nicht; Zieldatenbank bleibt erhalten.',1;

SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE '+QUOTENAME(@TargetDatabase)+N';';
BEGIN TRY
    EXEC sys.sp_executesql @Sql;
END TRY
BEGIN CATCH
    SELECT 1 AS Sequence,'CLEANUP' AS Phase,'DROP_OWNED_DATABASE' AS CheckId,'FAIL' AS Outcome,'FAIL_CLEANUP' AS Code,
           CONCAT(N'OriginalError=',ERROR_NUMBER(),N'; owned target preserved for recovery') AS ObservedValue,
           N'vollständige Marker geprüft; kein weiterer erzwungener Cleanup' AS RequiredValue,
           N'Der Löschversuch ist fehlgeschlagen; Zustand der eigenen Ziel-Datenbank muss geprüft werden.' AS Message;
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_CLEANUP';
    THROW;
END CATCH;
SELECT 1 AS Sequence,'CLEANUP' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       N'markierte QRY-023-Datenbank entfernt' AS ObservedValue,N'vollständige Markerübereinstimmung' AS RequiredValue,
       N'Der definierte Ausgangszustand ist wiederhergestellt.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
