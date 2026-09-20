/* DGN-007: read-only Preflight des eigenständigen Datenmodell-Schnitts. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
IF '$(DemoId)' <> 'DGN-007' OR '$(RunToken)' <> 'AUTO'
   OR N'$(TargetDatabase)' <> N'SQLPERF_LAB_DGN007_AUTO'
    THROW 51000,'FAIL_CONTRACT: Der automatisierte DGN-007-Datenmodellvertrag ist ungültig.',1;
IF @Major IS NULL OR @Major NOT IN (15,16,17)
BEGIN
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION'; RETURN;
END;
IF TRY_CONVERT(int,SERVERPROPERTY('EngineEdition')) NOT IN (2,3,4)
BEGIN
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PLATFORM'; RETURN;
END;
IF COALESCE(HAS_PERMS_BY_NAME(NULL,NULL,'CREATE ANY DATABASE'),0)<>1
BEGIN
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION'; RETURN;
END;
IF '$(ConfirmIsolatedLab)' <> '1' OR '$(HighImpactConfirmed)' <> '1'
   OR COALESCE(TRY_CONVERT(int,'$(MaximumRuntimeSeconds)'),0) NOT BETWEEN 1 AND 180
    THROW 51001,'FAIL_SAFETY: Isoliertes Lab und positives Laufzeitbudget bis 180 Sekunden bestätigen.',1;
IF EXISTS(SELECT 1 FROM sys.databases WHERE database_id>4 AND name<>N'SQLPERF_LAB_DGN007_AUTO')
    THROW 51001,'FAIL_SAFETY: Der Datenmodelltest benötigt eine isolierte Wegwerfinstanz.',1;
IF DB_ID(N'SQLPERF_LAB_DGN007_AUTO') IS NOT NULL
    THROW 51002,'FAIL_STATE: Vorhandenen AUTO-Zustand zuerst mit dem markergeprüften Cleanup bereinigen.',1;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
