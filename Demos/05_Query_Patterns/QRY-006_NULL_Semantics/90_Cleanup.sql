/* QRY-006 cleanup: remove only the database with complete ownership markers. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7) = '$(DemoId)';
DECLARE @RunToken varchar(20) = '$(RunToken)';
DECLARE @TargetDatabase sysname = N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname = CONVERT(sysname, N'SQLPERF_LAB_' + REPLACE(@DemoId, '-', '') + N'_' + @RunToken);
DECLARE @Project nvarchar(max);
DECLARE @Contract nvarchar(max);
DECLARE @ExistingDemo nvarchar(max);
DECLARE @ExistingRun nvarchar(max);
DECLARE @Sql nvarchar(max);

IF @DemoId <> 'QRY-006' OR @TargetDatabase <> @ExpectedDatabase
    THROW 51000, 'FAIL_CONTRACT: QRY-006-Cleanupziel ist ungültig.', 1;

IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    SELECT 1 AS Sequence, 'CLEANUP' AS Phase, 'SUMMARY' AS CheckId, 'PASS' AS Outcome, 'OK' AS Code,
           N'Zieldatenbank bereits nicht vorhanden' AS ObservedValue, N'idempotenter Cleanup' AS RequiredValue,
           N'Es war keine Bereinigung erforderlich.' AS Message;
    PRINT 'SQLPERF_SUMMARY|PASS|OK';
    RETURN;
END;

SET @Sql = N'SELECT @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max), value) END),
@ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max), value) END),
@DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max), value) END),
@RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max), value) END)
FROM ' + QUOTENAME(@TargetDatabase) + N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql, N'@ProjectOut nvarchar(max) OUTPUT, @ContractOut nvarchar(max) OUTPUT, @DemoOut nvarchar(max) OUTPUT, @RunOut nvarchar(max) OUTPUT',
     @ProjectOut=@Project OUTPUT, @ContractOut=@Contract OUTPUT, @DemoOut=@ExistingDemo OUTPUT, @RunOut=@ExistingRun OUTPUT;

-- NULL, abweichende Schreibweise und angehängte Zeichen verweigern das Entfernen.
IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2 <> N'SQL_PerformanceSchulung' OR DATALENGTH(@Project) <> DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2 <> N'1.0' OR DATALENGTH(@Contract) <> DATALENGTH(N'1.0')
   OR @ExistingDemo IS NULL OR @ExistingDemo COLLATE Latin1_General_100_BIN2 <> CONVERT(nvarchar(max), @DemoId) OR DATALENGTH(@ExistingDemo) <> DATALENGTH(CONVERT(nvarchar(max), @DemoId))
   OR @ExistingRun IS NULL OR @ExistingRun COLLATE Latin1_General_100_BIN2 <> CONVERT(nvarchar(max), @RunToken) OR DATALENGTH(@ExistingRun) <> DATALENGTH(CONVERT(nvarchar(max), @RunToken))
    THROW 51004, 'FAIL_CLEANUP: Die Eigentumsmarker stimmen nicht vollständig überein.', 1;

SET @Sql = N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE ' + QUOTENAME(@TargetDatabase) + N';';
EXEC sys.sp_executesql @Sql;

SELECT 1 AS Sequence, 'CLEANUP' AS Phase, 'SUMMARY' AS CheckId, 'PASS' AS Outcome, 'OK' AS Code,
       N'markierte QRY-006-Datenbank entfernt' AS ObservedValue, N'vollständige Markerübereinstimmung' AS RequiredValue,
       N'Der definierte Ausgangszustand ist wiederhergestellt.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
