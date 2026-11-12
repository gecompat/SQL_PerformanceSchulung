/* Check exact target ownership, SELECT and SHOWPLAN before any query evidence. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@MarkerDemo nvarchar(max),@MarkerRun nvarchar(max);
SELECT @Project=MAX(CASE WHEN name=N'SQLPERF.Project' THEN CONVERT(nvarchar(max),value) END),
       @Contract=MAX(CASE WHEN name=N'SQLPERF.ContractVersion' THEN CONVERT(nvarchar(max),value) END),
       @MarkerDemo=MAX(CASE WHEN name=N'SQLPERF.DemoId' THEN CONVERT(nvarchar(max),value) END),
       @MarkerRun=MAX(CASE WHEN name=N'SQLPERF.RunToken' THEN CONVERT(nvarchar(max),value) END)
FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;
IF DB_ID()<=4 OR @DemoId<>'QRY-023' OR DB_NAME()<>@TargetDatabase
   OR @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
   OR @MarkerDemo IS NULL OR @MarkerDemo COLLATE Latin1_General_100_BIN2<>N'QRY-023' OR DATALENGTH(@MarkerDemo)<>DATALENGTH(N'QRY-023')
   OR @MarkerRun IS NULL OR @MarkerRun COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@RunToken) OR DATALENGTH(@MarkerRun)<>DATALENGTH(CONVERT(nvarchar(max),@RunToken))
    THROW 51001,'FAIL_SAFETY: Zielmarker und Harness-Kontext stimmen nicht vollständig überein.',1;

DECLARE @HasShowplan bit=CASE WHEN HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','SHOWPLAN')=1 THEN 1 ELSE 0 END;
DECLARE @HasSelect bit=CASE WHEN HAS_PERMS_BY_NAME(N'dbo.Person','OBJECT','SELECT')=1
    AND HAS_PERMS_BY_NAME(N'dbo.FriendOf','OBJECT','SELECT')=1
    AND HAS_PERMS_BY_NAME(N'dbo.RelPerson','OBJECT','SELECT')=1
    AND HAS_PERMS_BY_NAME(N'dbo.RelFriend','OBJECT','SELECT')=1
    AND HAS_PERMS_BY_NAME(N'dbo.OraclePerson','OBJECT','SELECT')=1
    AND HAS_PERMS_BY_NAME(N'dbo.OracleFriendOf','OBJECT','SELECT')=1
    AND HAS_PERMS_BY_NAME(N'dbo.OracleRelPerson','OBJECT','SELECT')=1
    AND HAS_PERMS_BY_NAME(N'dbo.OracleRelFriend','OBJECT','SELECT')=1 THEN 1 ELSE 0 END;
DECLARE @HasMeasurement bit=CASE WHEN HAS_PERMS_BY_NAME(N'lab.MeasurementRun','OBJECT','SELECT')=1
    AND HAS_PERMS_BY_NAME(N'lab.USP_Qry023MeasureVariant','OBJECT','EXECUTE')=1 THEN 1 ELSE 0 END;
IF @HasShowplan=0 OR @HasSelect=0 OR @HasMeasurement=0
BEGIN
    SELECT 1 AS Sequence,'QUALIFICATION_PREFLIGHT' AS Phase,'PERMISSIONS' AS CheckId,'SKIP' AS Outcome,'SKIP_PERMISSION' AS Code,
           CONCAT(N'SHOWPLAN=',@HasShowplan,N'; SELECT=',@HasSelect,N'; MEASUREMENT=',@HasMeasurement) AS ObservedValue,
           N'SELECT auf vier Query- und vier Oracle-Tabellen sowie lab.MeasurementRun, EXECUTE auf lab.USP_Qry023MeasureVariant sowie SHOWPLAN auf der markierten Zieldatenbank' AS RequiredValue,
           N'Plan- und Vergleichsevidenz sind Pflicht; ohne Rechte beginnt kein Query-Lauf.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';
    RETURN;
END;

SELECT 1 AS Sequence,'QUALIFICATION_PREFLIGHT' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       N'exakte Zielmarker, SELECT, Messprozedurausführung und SHOWPLAN geprüft' AS ObservedValue,
       N'Plan-/Messrechte vor Korrektheits- und Messabfragen' AS RequiredValue,
       N'Der QRY-023-Qualifikationspreflight ist bestanden.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
