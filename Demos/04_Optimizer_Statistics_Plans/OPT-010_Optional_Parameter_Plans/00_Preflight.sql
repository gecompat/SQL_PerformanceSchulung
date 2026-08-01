/* OPT-010 / ADV-008 / FWK-001 / FWK-008 / FWK-012 */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7) = '$(DemoId)';
DECLARE @RunToken varchar(20) = '$(RunToken)';
DECLARE @TargetDatabase sysname = N'$(TargetDatabase)';
DECLARE @MajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @ExpectedDatabase sysname = CONVERT(sysname, N'SQLPERF_LAB_' + REPLACE(@DemoId, '-', '') + N'_' + @RunToken);
DECLARE @HasCreateDatabase bit = 0;
DECLARE @HasServerState bit = 0;

IF @DemoId <> 'OPT-010'
   OR @RunToken IS NULL
   OR LEN(@RunToken) NOT BETWEEN 1 AND 20
   OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9_]%'
   OR @TargetDatabase <> @ExpectedDatabase
    THROW 51000, 'FAIL_CONTRACT: Demo-ID, Run-Token oder Ziel-Datenbank entsprechen nicht dem OPT-010-Vertrag.', 1;

IF @MajorVersion NOT BETWEEN 15 AND 17
BEGIN
    SELECT 1 AS Sequence, 'PREFLIGHT' AS Phase, 'ENGINE_VERSION' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_VERSION' AS Code,
           CONVERT(nvarchar(20), @MajorVersion) AS ObservedValue,
           N'15 bis 17' AS RequiredValue,
           N'OPT-010 wird ausschliesslich auf SQL Server 2019 bis 2025 ausgefuehrt.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';
    RETURN;
END;

/* Optional Parameter Plan Optimization setzt SQL Server 2025 und Compatibility Level 170 voraus. */
IF @MajorVersion < 17
BEGIN
    SELECT 1 AS Sequence, 'PREFLIGHT' AS Phase, 'FEATURE_AVAILABILITY' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_VERSION' AS Code,
           CONCAT(N'Major=', @MajorVersion) AS ObservedValue,
           N'SQL Server 2025 mit Compatibility Level 170' AS RequiredValue,
           N'Optional Parameter Plan Optimization ist in dieser Version nicht vorhanden; der Vergleich waere nicht belegbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';
    RETURN;
END;

SET @HasCreateDatabase = CASE
    WHEN HAS_PERMS_BY_NAME(NULL, NULL, 'CREATE ANY DATABASE') = 1
      OR HAS_PERMS_BY_NAME(NULL, NULL, 'ALTER ANY DATABASE') = 1
      OR HAS_PERMS_BY_NAME(N'master', 'DATABASE', 'CREATE DATABASE') = 1
    THEN 1 ELSE 0 END;

SET @HasServerState = CASE
    WHEN HAS_PERMS_BY_NAME(NULL, NULL, 'VIEW SERVER PERFORMANCE STATE') = 1
      OR IS_SRVROLEMEMBER('sysadmin') = 1
    THEN 1 ELSE 0 END;

IF @HasCreateDatabase = 0 OR @HasServerState = 0
BEGIN
    SELECT 1 AS Sequence, 'PREFLIGHT' AS Phase, 'PERMISSIONS' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_PERMISSION' AS Code,
           CONCAT(N'CreateDatabase=', @HasCreateDatabase, N'; ServerState=', @HasServerState) AS ObservedValue,
           N'CREATE DATABASE und VIEW SERVER PERFORMANCE STATE' AS RequiredValue,
           N'Dispatcher- und Variantenevidenz stammt aus dem Plancache und ist ohne diese Rechte nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';
    RETURN;
END;

SELECT 1 AS Sequence, 'PREFLIGHT' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Major=', @MajorVersion, N'; Safety=GREEN; Planauswertung ausschliesslich marker- und objektbezogen') AS ObservedValue,
       N'SQL Server 2025; markergebundene synthetische Datenbank' AS RequiredValue,
       N'Preflight fuer OPT-010 ist bestanden.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
