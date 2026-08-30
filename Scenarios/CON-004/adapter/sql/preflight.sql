/* Versionierter Project-Adapter-Preflight fuer CON-004; strikt read-only. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname = N'SQLPERF_LAB_CON004_LOCAL';
DECLARE @Major int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @HasCreate bit = CASE
    WHEN HAS_PERMS_BY_NAME(NULL, NULL, 'CREATE ANY DATABASE') = 1
      OR HAS_PERMS_BY_NAME(NULL, NULL, 'ALTER ANY DATABASE') = 1
      OR HAS_PERMS_BY_NAME(N'master', 'DATABASE', 'CREATE DATABASE') = 1 THEN 1
    ELSE 0
END;
DECLARE @HasState bit = CASE
    WHEN HAS_PERMS_BY_NAME(NULL, NULL, 'VIEW SERVER PERFORMANCE STATE') = 1
      OR IS_SRVROLEMEMBER('sysadmin') = 1 THEN 1
    ELSE 0
END;

IF @Major <> 17
    THROW 51000, 'ADAPTER_UNSUPPORTED_SQL_VERSION: CON-004 erwartet SQL Server 2025.', 1;
IF @HasCreate = 0 OR @HasState = 0
    THROW 51001, 'ADAPTER_PERMISSION_MISSING: CREATE DATABASE und VIEW SERVER PERFORMANCE STATE sind erforderlich.', 1;
SELECT N'CON-004' AS ScenarioId, N'PREFLIGHT' AS Phase, N'PASS' AS Outcome,
       @Major AS ProductMajorVersion, @TargetDatabase AS TargetDatabase;
