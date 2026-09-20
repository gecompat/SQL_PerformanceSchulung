/* DGN-007: nur vollständig markergebundenen AUTO-Datenmodellzustand entfernen. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;
IF '$(DemoId)' <> 'DGN-007' OR '$(RunToken)' <> 'AUTO'
   OR N'$(TargetDatabase)' <> N'SQLPERF_LAB_DGN007_AUTO'
    THROW 51000,'FAIL_CONTRACT: Ungültiges DGN-007-Cleanupziel.',1;
/* Die Harness-Bestätigung autorisiert Lab-Nutzung und den dokumentierten Datenbankabbau. */
IF '$(ConfirmIsolatedLab)' <> '1' OR '$(HighImpactConfirmed)' <> '1'
    THROW 51001,'FAIL_SAFETY: Lab-Nutzung und markergebundenen Abbau bestätigen.',1;
IF @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2
    THROW 51004,'FAIL_CLEANUP: Cleanup innerhalb einer Transaktion ist unzulässig.',1;
IF DB_ID(N'SQLPERF_LAB_DGN007_AUTO') IS NULL
BEGIN
    PRINT 'SQLPERF_SUMMARY|PASS|OK'; RETURN;
END;
IF NOT EXISTS(SELECT 1 FROM sys.databases WHERE name=N'SQLPERF_LAB_DGN007_AUTO' AND database_id>4 AND state_desc=N'ONLINE')
    THROW 51004,'FAIL_CLEANUP: Datenbank ist nicht online oder kein zulässiges Ziel.',1;
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@Demo nvarchar(max),@Run nvarchar(max),@Sql nvarchar(max);
/* Erst nach Existenzprüfung kompilieren; wiederholtes Cleanup benötigt keine Datenbank. */
SET @Sql=N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
       @Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
       @Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
       @Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
FROM [SQLPERF_LAB_DGN007_AUTO].sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@Project nvarchar(max) OUTPUT,@Contract nvarchar(max) OUTPUT,@Demo nvarchar(max) OUTPUT,@Run nvarchar(max) OUTPUT',
     @Project OUTPUT,@Contract OUTPUT,@Demo OUTPUT,@Run OUTPUT;
IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
   OR @Demo IS NULL OR @Demo COLLATE Latin1_General_100_BIN2<>N'DGN-007' OR DATALENGTH(@Demo)<>DATALENGTH(N'DGN-007')
   OR @Run IS NULL OR @Run COLLATE Latin1_General_100_BIN2<>N'AUTO' OR DATALENGTH(@Run)<>DATALENGTH(N'AUTO')
    THROW 51004,'FAIL_CLEANUP: Eigentumsmarker fehlen oder stimmen nicht exakt überein.',1;
ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE [SQLPERF_LAB_DGN007_AUTO];
PRINT 'SQLPERF_SUMMARY|PASS|OK';
