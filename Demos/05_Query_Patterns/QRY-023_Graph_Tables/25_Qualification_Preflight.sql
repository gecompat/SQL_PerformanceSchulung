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

/* Compare the effective READER permission sets with the manifest's fixed context inventory. */
DECLARE @ExpectedPermissions TABLE(
    ContextClass nvarchar(16) NOT NULL,ContextName sysname NOT NULL,PermissionName nvarchar(128) NOT NULL,
    PRIMARY KEY(ContextClass,ContextName,PermissionName));
DECLARE @ObservedPermissions TABLE(
    ContextClass nvarchar(16) NOT NULL,ContextName sysname NOT NULL,EntityName sysname NULL,
    SubentityName sysname NULL,PermissionName nvarchar(128) NOT NULL);
DECLARE @PermissionMismatchCount int=0,@PermissionDuplicateCount int=0,@ColumnPermissionCount int=0,@EntityNameMissingCount int=0;
DECLARE @BoundObjectInventory int=TRY_CONVERT(int,'$(BoundObjectInventory)');
IF @BoundObjectInventory<>13
    THROW 51017,'FAIL_NOT_PROVEN: ADMIN hat die vollständigen 13 QRY-023-/FWK-004-Objekte nicht bestätigt.',1;
INSERT @ExpectedPermissions(ContextClass,ContextName,PermissionName) VALUES
    (N'SERVER',N'<SERVER>',N'CONNECT SQL'),(N'SERVER',N'<SERVER>',N'VIEW ANY DATABASE'),
    (N'DATABASE',N'<DATABASE>',N'CONNECT'),(N'DATABASE',N'<DATABASE>',N'SHOWPLAN'),
    (N'DATABASE',N'<DATABASE>',N'VIEW ANY COLUMN ENCRYPTION KEY DEFINITION'),
    (N'DATABASE',N'<DATABASE>',N'VIEW ANY COLUMN MASTER KEY DEFINITION'),
    (N'OBJECT',N'dbo.Person',N'SELECT'),(N'OBJECT',N'dbo.FriendOf',N'SELECT'),
    (N'OBJECT',N'dbo.RelPerson',N'SELECT'),(N'OBJECT',N'dbo.RelFriend',N'SELECT'),
    (N'OBJECT',N'dbo.OraclePerson',N'SELECT'),(N'OBJECT',N'dbo.OracleFriendOf',N'SELECT'),
    (N'OBJECT',N'dbo.OracleRelPerson',N'SELECT'),(N'OBJECT',N'dbo.OracleRelFriend',N'SELECT'),
    (N'OBJECT',N'lab.MeasurementRun',N'SELECT'),
    (N'OBJECT',N'lab.USP_Qry023MeasureVariant',N'EXECUTE');

DECLARE @StandardEndpointInventory varchar(8191)='$(StandardEndpointInventory)';
DECLARE @EndpointInput TABLE(EndpointId int NULL,EndpointName sysname NULL,EncodedName varchar(512) NULL);
IF NULLIF(@StandardEndpointInventory,'') IS NULL
   OR @StandardEndpointInventory LIKE '%[^0-9A-F:;]%' COLLATE Latin1_General_100_BIN2
   OR LEN(@StandardEndpointInventory)>8191
   OR LEFT(@StandardEndpointInventory,1)=';' OR RIGHT(@StandardEndpointInventory,1)=';'
   OR CHARINDEX(';;',@StandardEndpointInventory)>0
    THROW 51015,'FAIL_NOT_PROVEN: ADMIN-Endpointinventar fehlt oder ist nicht kanonisch gebunden.',1;
INSERT @EndpointInput(EndpointId,EndpointName,EncodedName)
SELECT TRY_CONVERT(int,LEFT(value,CHARINDEX(':',value)-1)),
       CONVERT(sysname,TRY_CONVERT(varbinary(256),SUBSTRING(value,CHARINDEX(':',value)+1,512),2)),
       SUBSTRING(value,CHARINDEX(':',value)+1,512)
FROM STRING_SPLIT(@StandardEndpointInventory,';')
WHERE CHARINDEX(':',value)>1;
IF (SELECT COUNT(*) FROM @EndpointInput) NOT BETWEEN 1 AND 12
   OR EXISTS (SELECT 1 FROM @EndpointInput WHERE EndpointId IS NULL OR EndpointId NOT BETWEEN 1 AND 65535
              OR EndpointName IS NULL OR DATALENGTH(EndpointName)=0 OR DATALENGTH(EndpointName)>256
              OR EncodedName='' OR LEN(EncodedName)%4<>0)
   OR EXISTS (SELECT EndpointId FROM @EndpointInput GROUP BY EndpointId HAVING COUNT_BIG(*)>1)
   OR EXISTS (SELECT EndpointName FROM @EndpointInput GROUP BY EndpointName HAVING COUNT_BIG(*)>1)
   OR EXISTS (SELECT value FROM STRING_SPLIT(@StandardEndpointInventory,';') WHERE CHARINDEX(':',value)<=1)
    THROW 51016,'FAIL_NOT_PROVEN: Endpointnamen aus der ADMIN-Inventur sind unvollständig oder ungültig.',1;
INSERT @ExpectedPermissions(ContextClass,ContextName,PermissionName)
SELECT N'ENDPOINT',EndpointName,N'CONNECT' FROM @EndpointInput;

INSERT @ObservedPermissions(ContextClass,ContextName,EntityName,SubentityName,PermissionName)
SELECT N'SERVER',N'<SERVER>',entity_name,subentity_name,permission_name
FROM sys.fn_my_permissions(NULL,N'SERVER');
INSERT @ObservedPermissions(ContextClass,ContextName,EntityName,SubentityName,PermissionName)
SELECT N'DATABASE',N'<DATABASE>',entity_name,subentity_name,permission_name
FROM sys.fn_my_permissions(NULL,N'DATABASE');
DECLARE @EndpointName sysname;
DECLARE ReaderEndpointCursor CURSOR LOCAL FAST_FORWARD FOR SELECT EndpointName FROM @EndpointInput ORDER BY EndpointId;
OPEN ReaderEndpointCursor;
FETCH NEXT FROM ReaderEndpointCursor INTO @EndpointName;
WHILE @@FETCH_STATUS=0
BEGIN
    INSERT @ObservedPermissions(ContextClass,ContextName,EntityName,SubentityName,PermissionName)
    SELECT N'ENDPOINT',@EndpointName,entity_name,subentity_name,permission_name
    FROM sys.fn_my_permissions(@EndpointName,N'ENDPOINT');
    FETCH NEXT FROM ReaderEndpointCursor INTO @EndpointName;
END;
CLOSE ReaderEndpointCursor;
DEALLOCATE ReaderEndpointCursor;
INSERT @ObservedPermissions(ContextClass,ContextName,EntityName,SubentityName,PermissionName)
SELECT N'SCHEMA',N'dbo',entity_name,subentity_name,permission_name
FROM sys.fn_my_permissions(N'dbo',N'SCHEMA');
INSERT @ObservedPermissions(ContextClass,ContextName,EntityName,SubentityName,PermissionName)
SELECT N'SCHEMA',N'lab',entity_name,subentity_name,permission_name
FROM sys.fn_my_permissions(N'lab',N'SCHEMA');

DECLARE @SchemaName sysname,@ObjectName sysname,@SecurableName sysname;
DECLARE PermissionObjectCursor CURSOR LOCAL FAST_FORWARD FOR
SELECT schema_name,object_name FROM (VALUES
    (N'dbo',N'Person'),(N'dbo',N'FriendOf'),(N'dbo',N'RelPerson'),(N'dbo',N'RelFriend'),
    (N'dbo',N'OraclePerson'),(N'dbo',N'OracleFriendOf'),(N'dbo',N'OracleRelPerson'),(N'dbo',N'OracleRelFriend'),
    (N'lab',N'MeasurementRun'),(N'lab',N'MeasurementWaitSnapshot'),
    (N'lab',N'USP_Qry023MeasureVariant'),(N'lab',N'USP_BeginMeasurement'),(N'lab',N'USP_EndMeasurement')
) AS expected(schema_name,object_name);
OPEN PermissionObjectCursor;
FETCH NEXT FROM PermissionObjectCursor INTO @SchemaName,@ObjectName;
WHILE @@FETCH_STATUS=0
BEGIN
    SET @SecurableName=QUOTENAME(@SchemaName)+N'.'+QUOTENAME(@ObjectName);
    INSERT @ObservedPermissions(ContextClass,ContextName,EntityName,SubentityName,PermissionName)
    SELECT N'OBJECT',@SchemaName+N'.'+@ObjectName,entity_name,subentity_name,permission_name
    FROM sys.fn_my_permissions(@SecurableName,N'OBJECT');
    FETCH NEXT FROM PermissionObjectCursor INTO @SchemaName,@ObjectName;
END;
CLOSE PermissionObjectCursor;
DEALLOCATE PermissionObjectCursor;

SELECT @PermissionMismatchCount=
    (SELECT COUNT(*) FROM @ExpectedPermissions AS e WHERE NOT EXISTS
        (SELECT 1 FROM @ObservedPermissions AS a WHERE a.ContextClass=e.ContextClass
         AND a.ContextName=e.ContextName AND a.PermissionName=e.PermissionName AND a.SubentityName IS NULL))
    + (SELECT COUNT(*) FROM @ObservedPermissions AS a WHERE NOT EXISTS
        (SELECT 1 FROM @ExpectedPermissions AS e WHERE e.ContextClass=a.ContextClass
         AND e.ContextName=a.ContextName AND e.PermissionName=a.PermissionName));
SELECT @PermissionDuplicateCount=COUNT(*) FROM
    (SELECT ContextClass,ContextName,PermissionName,SubentityName FROM @ObservedPermissions
     GROUP BY ContextClass,ContextName,PermissionName,SubentityName HAVING COUNT_BIG(*)>1) AS duplicates;
SELECT @ColumnPermissionCount=COUNT(*) FROM @ObservedPermissions WHERE SubentityName IS NOT NULL;
SELECT @EntityNameMissingCount=COUNT(*) FROM @ObservedPermissions WHERE EntityName IS NULL;
IF @PermissionMismatchCount>0 OR @PermissionDuplicateCount>0 OR @ColumnPermissionCount>0
   OR @EntityNameMissingCount>0
BEGIN
    SELECT 1 AS Sequence,'QUALIFICATION_PREFLIGHT' AS Phase,'EFFECTIVE_PERMISSION_SET' AS CheckId,'FAIL' AS Outcome,'FAIL_NOT_PROVEN' AS Code,
           CONCAT(N'Mengenabweichungen=',@PermissionMismatchCount,N'; Duplikate=',@PermissionDuplicateCount,N'; Spaltenrechte=',@ColumnPermissionCount,N'; fehlende Entitynamen=',@EntityNameMissingCount) AS ObservedValue,
           N'Exakte vorab deklarierte READER-Rechtemengen je Server-, Endpoint-, Datenbank-, Schema- und Objektscope' AS RequiredValue,
           N'Ohne vollständige Mengengleichheit beginnt keine Korrektheits- oder Messphase.' AS Message;
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_NOT_PROVEN';
    THROW 51014,'FAIL_NOT_PROVEN: Effektive READER-Rechte weichen von der vorab gebundenen Sollmenge ab.',1;
END;

SELECT 1 AS Sequence,'QUALIFICATION_PREFLIGHT' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       N'exakte Zielmarker, SELECT, Messprozedurausführung und SHOWPLAN geprüft' AS ObservedValue,
       N'Plan-/Messrechte vor Korrektheits- und Messabfragen' AS RequiredValue,
       N'Der QRY-023-Qualifikationspreflight ist bestanden.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
