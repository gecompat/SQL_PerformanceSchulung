/* Read-only Project-Adapter-Preflight fuer DGN-005. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Major int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @HasCreate bit = CASE WHEN HAS_PERMS_BY_NAME(NULL, NULL, 'CREATE ANY DATABASE') = 1
    OR HAS_PERMS_BY_NAME(NULL, NULL, 'ALTER ANY DATABASE') = 1
    OR HAS_PERMS_BY_NAME(N'master', 'DATABASE', 'CREATE DATABASE') = 1 THEN 1 ELSE 0 END;
DECLARE @HasXe bit = CASE WHEN HAS_PERMS_BY_NAME(NULL, NULL, 'CREATE ANY EVENT SESSION') = 1
    OR HAS_PERMS_BY_NAME(NULL, NULL, 'ALTER ANY EVENT SESSION') = 1
    OR IS_SRVROLEMEMBER('sysadmin') = 1 THEN 1 ELSE 0 END;
DECLARE @HasState bit = CASE WHEN HAS_PERMS_BY_NAME(NULL, NULL, 'VIEW SERVER PERFORMANCE STATE') = 1
    OR IS_SRVROLEMEMBER('sysadmin') = 1 THEN 1 ELSE 0 END;

IF @Major <> 17
    THROW 51000, 'ADAPTER_UNSUPPORTED_SQL_VERSION: DGN-005 erwartet SQL Server 2025.', 1;
IF @HasCreate = 0 OR @HasXe = 0 OR @HasState = 0
    THROW 51001, 'ADAPTER_PERMISSION_MISSING: Datenbank-, Event-Session- und Statusberechtigungen sind erforderlich.', 1;
IF NOT EXISTS (SELECT 1 FROM sys.dm_xe_objects WHERE object_type = N'event' AND name = N'error_reported')
    THROW 51001, 'ADAPTER_CAPABILITY_MISSING: sqlserver.error_reported fehlt.', 1;

SELECT N'DGN-005' AS ScenarioId, N'PREFLIGHT' AS Phase, N'PASS' AS Outcome,
       @Major AS ProductMajorVersion, N'SQLPERF_LAB_DGN005_LOCAL' AS TargetDatabase;
