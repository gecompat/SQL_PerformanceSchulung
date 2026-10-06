/* DGN-007_CONTROL_CONFIG_AB: feste neutrale Kontrollfolge, keine Incidentfreigabe. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 5000;
DECLARE @PhaseDeadline datetime2(7)=DATEADD(second,3,SYSUTCDATETIME());
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
DECLARE @EditionId int=TRY_CONVERT(int,SERVERPROPERTY('EditionID'));
DECLARE @ActualCompatibility int=(SELECT compatibility_level FROM sys.databases WHERE database_id=DB_ID());
IF '$(DemoId)'<>'DGN-007' OR '$(RunToken)'<>'AUTO'
   OR N'$(TargetDatabase)'<>N'SQLPERF_LAB_DGN007_AUTO'
   OR DB_NAME()<>N'SQLPERF_LAB_DGN007_AUTO'
    THROW 51000,'FAIL_CONTRACT: Unerwartetes Ziel der Kontrollkonfiguration.',1;
IF '$(ConfirmIsolatedLab)'<>'1' OR '$(HighImpactConfirmed)'<>'1'
   OR COALESCE(TRY_CONVERT(int,'$(MaximumRuntimeSeconds)'),0) NOT BETWEEN 1 AND 180
   OR @Major IS NULL OR @Major NOT IN (15,16,17)
   OR @EditionId IS NULL OR @EditionId NOT IN (-2117995310,-1785266663)
   OR @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2
    THROW 51001,'FAIL_SAFETY: Bestätigte Developer-Wegwerfinstanz und begrenztes Budget erforderlich.',1;
IF @ActualCompatibility IS NULL
   OR @ActualCompatibility<>CASE @Major WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END
    THROW 51000,'FAIL_CONTRACT: Compatibility Level entspricht nicht der Zielversion.',1;
IF EXISTS(SELECT 1 FROM sys.databases WHERE database_id>4 AND database_id<>DB_ID())
   OR NOT EXISTS(SELECT 1 FROM sys.databases WHERE database_id=DB_ID() AND database_id>4 AND state_desc=N'ONLINE')
    THROW 51001,'FAIL_SAFETY: Isolierte eigene Datenbank ohne Fremddatenbanken erforderlich.',1;

/* Vier vollständige Marker vor Zugriff auf die persistierte Labevidenz. */
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@Demo nvarchar(max),@Run nvarchar(max);
SELECT @Project=MAX(CASE WHEN name=N'SQLPERF.Project' THEN CONVERT(nvarchar(max),value) END),
       @Contract=MAX(CASE WHEN name=N'SQLPERF.ContractVersion' THEN CONVERT(nvarchar(max),value) END),
       @Demo=MAX(CASE WHEN name=N'SQLPERF.DemoId' THEN CONVERT(nvarchar(max),value) END),
       @Run=MAX(CASE WHEN name=N'SQLPERF.RunToken' THEN CONVERT(nvarchar(max),value) END)
FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;
IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
   OR @Demo IS NULL OR @Demo COLLATE Latin1_General_100_BIN2<>N'DGN-007' OR DATALENGTH(@Demo)<>DATALENGTH(N'DGN-007')
   OR @Run IS NULL OR @Run COLLATE Latin1_General_100_BIN2<>N'AUTO' OR DATALENGTH(@Run)<>DATALENGTH(N'AUTO')
    THROW 51001,'FAIL_SAFETY: Eigentumsmarker fehlen oder weichen ab.',1;

IF SCHEMA_ID(N'lab') IS NULL OR OBJECT_ID(N'lab.ControlSequence') IS NOT NULL
   OR OBJECT_ID(N'lab.IncidentState') IS NOT NULL OR OBJECT_ID(N'lab.IncidentProfile') IS NOT NULL
   OR OBJECT_ID(N'lab.QueryStoreBaseline') IS NOT NULL
   OR OBJECT_ID(N'dbo.CaseRequestLog',N'U') IS NULL
    THROW 51002,'FAIL_STATE: Frischer markierter Datenmodellzustand ohne Kontrollfolge erforderlich.',1;
IF (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>4
    THROW 51002,'FAIL_STATE: Vier vorherige Assertionsrequests erforderlich.',1;
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;
/* CONTROL_CONFIG_BEGIN */
CREATE TABLE lab.ControlSequence(
    WindowId tinyint NOT NULL PRIMARY KEY,
    ConditionCode char(1) COLLATE Latin1_General_100_BIN2 NOT NULL,
    CHECK(WindowId IN (0,1)),
    CHECK(ConditionCode IN ('A','B'))
);
INSERT lab.ControlSequence(WindowId,ConditionCode) VALUES(0,'A'),(1,'B');
/* CONTROL_CONFIG_END */
SELECT N'DGN007_CONTROL_CONFIG' AS ReportKind,'AB' AS ControlSequence;
IF SYSUTCDATETIME()>=@PhaseDeadline
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;
END;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
