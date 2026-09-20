/* QRY-006 preflight: result semantics only; no plan or performance evidence. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7) = '$(DemoId)';
DECLARE @RunToken varchar(20) = '$(RunToken)';
DECLARE @TargetDatabase sysname = N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname = CONVERT(sysname, N'SQLPERF_LAB_' + REPLACE(@DemoId, '-', '') + N'_' + @RunToken);
DECLARE @MajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));

IF @DemoId <> 'QRY-006'
   OR @RunToken IS NULL
   OR LEN(@RunToken) NOT BETWEEN 1 AND 20
   OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9_]%'
   OR @TargetDatabase <> @ExpectedDatabase
    THROW 51000, 'FAIL_CONTRACT: QRY-006-Zielkennung ist ungültig.', 1;

IF @MajorVersion NOT BETWEEN 15 AND 17
BEGIN
    SELECT 1 AS Sequence, 'PREFLIGHT' AS Phase, 'ENGINE_VERSION' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_VERSION' AS Code,
           CONVERT(nvarchar(20), @MajorVersion) AS ObservedValue,
           N'SQL Server 2019 bis 2025' AS RequiredValue,
           N'QRY-006 prüft denselben Ergebnisvertrag auf SQL Server 2019 bis 2025.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';
    RETURN;
END;

IF HAS_PERMS_BY_NAME(NULL, NULL, 'CREATE ANY DATABASE') <> 1
   AND HAS_PERMS_BY_NAME(NULL, NULL, 'ALTER ANY DATABASE') <> 1
   AND HAS_PERMS_BY_NAME(N'master', 'DATABASE', 'CREATE DATABASE') <> 1
BEGIN
    SELECT 1 AS Sequence, 'PREFLIGHT' AS Phase, 'PERMISSIONS' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_PERMISSION' AS Code,
           N'CREATE DATABASE fehlt' AS ObservedValue,
           N'CREATE DATABASE' AS RequiredValue,
           N'Die markergebundene Testdatenbank kann nicht angelegt werden.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';
    RETURN;
END;

SELECT 1 AS Sequence, 'PREFLIGHT' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Major=', @MajorVersion, N'; Safety=GREEN; Ergebnissemantik ohne Planbehauptung') AS ObservedValue,
       N'SQL Server 2019 bis 2025; markergebundene synthetische Datenbank' AS RequiredValue,
       N'Preflight für QRY-006 ist bestanden.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
