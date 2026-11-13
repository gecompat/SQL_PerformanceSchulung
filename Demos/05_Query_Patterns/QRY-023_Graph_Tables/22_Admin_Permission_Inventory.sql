/* Read-only ADMIN inventory for the exact QRY-023 target and READER principal. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)',
        @ReaderLogin sysname=N'$(ReaderLogin)',@MajorVersion int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')),
        @ReaderPrincipalId int,@ReaderSid varbinary(85),@PublicPrincipalId int,@PublicDatabasePrincipalId int,
        @ReaderUserId int,@ReaderUserSid varbinary(85),
        @Project nvarchar(max),@Contract nvarchar(max),@MarkerDemo nvarchar(max),@MarkerRun nvarchar(max),@Sql nvarchar(max),
        @UserDatabaseCount int,@EndpointCount int,@ReaderEndpointCount int,@ExpectedObjectCount int=13,
        @ObservedObjectCount int,@PublicSystemSelectCount int=0,
        @PublicSystemSelectActualHash varchar(64),@PublicSystemSelectExpectedHash varchar(64),
        @PublicSystemSelectExpectedCount int,@PublicSystemSelectCanonical nvarchar(max),
        @PublicSystemSelectBaselineMismatch int=0,
        @Visible bit=1,@UnexpectedCount int=0,@FailureCategories nvarchar(400)=N'';

IF @DemoId<>'QRY-023' OR @TargetDatabase<>DB_NAME() OR DB_ID()<=4 OR @ReaderLogin IS NULL
    THROW 51010,'FAIL_CONTRACT: ADMIN-Inventur muss in der nichtsystemischen QRY-023-Zieldatenbank mit READER-Identität laufen.',1;

SELECT @Project=MAX(CASE WHEN name=N'SQLPERF.Project' THEN CONVERT(nvarchar(max),value) END),
       @Contract=MAX(CASE WHEN name=N'SQLPERF.ContractVersion' THEN CONVERT(nvarchar(max),value) END),
       @MarkerDemo=MAX(CASE WHEN name=N'SQLPERF.DemoId' THEN CONVERT(nvarchar(max),value) END),
       @MarkerRun=MAX(CASE WHEN name=N'SQLPERF.RunToken' THEN CONVERT(nvarchar(max),value) END)
FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;
IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
   OR @MarkerDemo IS NULL OR @MarkerDemo COLLATE Latin1_General_100_BIN2<>N'QRY-023' OR DATALENGTH(@MarkerDemo)<>DATALENGTH(N'QRY-023')
   OR @MarkerRun IS NULL OR @MarkerRun COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@RunToken) OR DATALENGTH(@MarkerRun)<>DATALENGTH(CONVERT(nvarchar(max),@RunToken))
    THROW 51011,'FAIL_SAFETY: ADMIN-Inventur ist nicht an die exakt markierte QRY-023-Datenbank gebunden.',1;

/* Require documented metadata-visibility authority before interpreting catalog rows as complete. */
IF @MajorVersion>=16
BEGIN
    IF ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW ANY SECURITY DEFINITION'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW ANY DEFINITION'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW SERVER SECURITY STATE'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW ANY DATABASE'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','VIEW SECURITY DEFINITION'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','VIEW DEFINITION'),0)<>1
        SET @Visible=0;
END
ELSE IF @MajorVersion=15
BEGIN
    IF ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW ANY DEFINITION'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW SERVER STATE'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW ANY DATABASE'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','VIEW DEFINITION'),0)<>1
        SET @Visible=0;
END
ELSE
    SET @Visible=0;

IF @Visible=0
BEGIN
    SELECT 1 AS Sequence,'ADMIN_PERMISSION_INVENTORY' AS Phase,'METADATA_VISIBILITY' AS CheckId,'FAIL' AS Outcome,'FAIL_NOT_PROVEN' AS Code,
           N'Erforderliche Security-/Datenbank-/Endpointmetadaten sind nicht nachweislich vollständig sichtbar.' AS ObservedValue,
           N'Versionsabhängige, dokumentierte ADMIN-Metadatenrechte; keine automatische Rechtevergabe' AS RequiredValue,
           N'Keine Katalogzeile wird bei unvollständiger Sicht als vollständiges Inventar interpretiert.' AS Message;
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_NOT_PROVEN';
    THROW 51012,'FAIL_NOT_PROVEN: ADMIN-Metadatensichtbarkeit reicht für die vollständige Inventur nicht aus.',1;
END;

SELECT @ReaderPrincipalId=principal_id,@ReaderSid=sid
FROM master.sys.server_principals WHERE name=@ReaderLogin AND type='S' AND is_disabled=0;
SELECT @PublicPrincipalId=principal_id FROM master.sys.server_principals WHERE name=N'public' AND type='R';
SELECT @PublicDatabasePrincipalId=principal_id FROM sys.database_principals WHERE name=N'public' AND type='R';
SELECT @ReaderUserId=principal_id,@ReaderUserSid=sid
FROM sys.database_principals WHERE name=@ReaderLogin AND type='S';
SELECT @UserDatabaseCount=COUNT(*) FROM master.sys.databases WHERE database_id>4;
SELECT @EndpointCount=COUNT(*) FROM master.sys.endpoints;
SELECT @ReaderEndpointCount=COUNT(*) FROM master.sys.endpoints WHERE endpoint_id<65536 AND is_admin_endpoint=0;
/* Bind the exact public SELECT inventory to the pinned product build. */
SELECT @PublicSystemSelectExpectedCount=CASE @MajorVersion
           WHEN 15 THEN CASE WHEN CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'))=N'15.0.4500.2' THEN 186 END
           WHEN 16 THEN CASE WHEN CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'))=N'16.0.4305.5' THEN 226 END
           WHEN 17 THEN CASE WHEN CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'))=N'17.0.5035.5' THEN 232 END
       END,
       @PublicSystemSelectExpectedHash=CASE @MajorVersion
           WHEN 15 THEN CASE WHEN CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'))=N'15.0.4500.2' THEN '93f1b67ac741cf1c07dc3e7dccd38101deec45fb4307ab218d9ac34c9c19dbbb' END
           WHEN 16 THEN CASE WHEN CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'))=N'16.0.4305.5' THEN 'f127c9c0a4c5ecfd061c536d82a3def7925176c4eddbd5980335a4453e0e405a' END
           WHEN 17 THEN CASE WHEN CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'))=N'17.0.5035.5' THEN '4a3dd68e28a0d53f8041e82994a0bcfc33230873a4b7f94179b4e62486712392' END
       END;

DECLARE @PublicSystemSelects TABLE
(
    ObjectId int NOT NULL,
    SchemaName sysname NOT NULL,
    ObjectName sysname NOT NULL,
    TypeDesc nvarchar(60) NOT NULL,
    StateDesc nvarchar(60) NOT NULL,
    PermissionName sysname NOT NULL,
    MinorId int NOT NULL
);
INSERT @PublicSystemSelects(ObjectId,SchemaName,ObjectName,TypeDesc,StateDesc,PermissionName,MinorId)
SELECT p.major_id,OBJECT_SCHEMA_NAME(p.major_id),OBJECT_NAME(p.major_id),
       CASE WHEN o.object_id IS NOT NULL THEN o.type_desc
            WHEN OBJECTPROPERTYEX(p.major_id,'IsView')=1 THEN N'VIEW' ELSE N'UNKNOWN' END,
       p.state_desc,p.permission_name,p.minor_id
FROM sys.database_permissions AS p
JOIN sys.database_principals AS grantee ON grantee.principal_id=p.grantee_principal_id
LEFT JOIN sys.system_objects AS o ON o.object_id=p.major_id
WHERE grantee.name=N'public' AND p.class=1 AND p.major_id<0 AND p.permission_name=N'SELECT';

SELECT @PublicSystemSelectCount=COUNT(*) FROM @PublicSystemSelects;
SELECT @PublicSystemSelectCanonical=STRING_AGG(CONVERT(nvarchar(max),
           CONVERT(nvarchar(10),DATALENGTH(SchemaName)/2)+N':'+SchemaName+
           CONVERT(nvarchar(10),DATALENGTH(ObjectName)/2)+N':'+ObjectName+
           CONVERT(nvarchar(10),DATALENGTH(TypeDesc)/2)+N':'+TypeDesc+
           CONVERT(nvarchar(10),DATALENGTH(StateDesc)/2)+N':'+StateDesc+
           CONVERT(nvarchar(10),DATALENGTH(PermissionName)/2)+N':'+PermissionName+
           CONVERT(nvarchar(10),DATALENGTH(CONVERT(nvarchar(11),MinorId))/2)+N':'+CONVERT(nvarchar(11),MinorId)),NCHAR(10))
       WITHIN GROUP (ORDER BY SchemaName COLLATE Latin1_General_100_BIN2,
                              ObjectName COLLATE Latin1_General_100_BIN2,
                              TypeDesc COLLATE Latin1_General_100_BIN2,
                              StateDesc COLLATE Latin1_General_100_BIN2,
                              PermissionName COLLATE Latin1_General_100_BIN2,
                              MinorId)
FROM @PublicSystemSelects;
SET @PublicSystemSelectCanonical=ISNULL(@PublicSystemSelectCanonical,N'')+NCHAR(10);
SET @PublicSystemSelectActualHash=LOWER(CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),@PublicSystemSelectCanonical)),2));
IF @PublicSystemSelectExpectedCount IS NULL OR @PublicSystemSelectExpectedHash IS NULL
   OR @PublicSystemSelectCount<>@PublicSystemSelectExpectedCount
   OR @PublicSystemSelectActualHash<>@PublicSystemSelectExpectedHash
    SET @PublicSystemSelectBaselineMismatch=1;
SELECT @ObservedObjectCount=COUNT(DISTINCT o.object_id)
FROM (VALUES
    (N'dbo',N'Person',N'U'),(N'dbo',N'FriendOf',N'U'),(N'dbo',N'RelPerson',N'U'),(N'dbo',N'RelFriend',N'U'),
    (N'dbo',N'OraclePerson',N'U'),(N'dbo',N'OracleFriendOf',N'U'),(N'dbo',N'OracleRelPerson',N'U'),(N'dbo',N'OracleRelFriend',N'U'),
    (N'lab',N'MeasurementRun',N'U'),(N'lab',N'MeasurementWaitSnapshot',N'U'),
    (N'lab',N'USP_Qry023MeasureVariant',N'P'),(N'lab',N'USP_BeginMeasurement',N'P'),(N'lab',N'USP_EndMeasurement',N'P')
) AS expected(schema_name,object_name,object_type)
JOIN sys.schemas AS s ON s.name=expected.schema_name
JOIN sys.objects AS o ON o.schema_id=s.schema_id AND o.name=expected.object_name
                         AND o.type=expected.object_type AND o.is_ms_shipped=0;
IF @ObservedObjectCount<>@ExpectedObjectCount
BEGIN
    SET @UnexpectedCount+=1;
    SET @FailureCategories+=N'OBJECT_INVENTORY;';
END;

IF @ReaderPrincipalId IS NULL OR @PublicPrincipalId IS NULL OR @PublicDatabasePrincipalId IS NULL OR @ReaderSid IS NULL
   OR @ReaderUserId IS NULL OR @ReaderUserSid IS NULL OR @ReaderSid<>@ReaderUserSid
   OR @UserDatabaseCount<>1 OR @EndpointCount=0 OR @ReaderEndpointCount NOT BETWEEN 1 AND 12 OR DB_NAME()<>@TargetDatabase
    BEGIN SET @UnexpectedCount+=1; SET @FailureCategories+=N'IDENTITY_OR_SCOPE;'; END;

/* public is an implicit membership. Any explicit server role is outside the READER baseline. */
IF EXISTS (SELECT 1 FROM master.sys.server_role_members
           WHERE member_principal_id=@ReaderPrincipalId AND role_principal_id<>@PublicPrincipalId)
    BEGIN SET @UnexpectedCount+=1; SET @FailureCategories+=N'SERVER_ROLE;'; END;
IF EXISTS (SELECT 1 FROM sys.database_role_members
           WHERE member_principal_id=@ReaderUserId AND role_principal_id<>@PublicDatabasePrincipalId)
    BEGIN SET @UnexpectedCount+=1; SET @FailureCategories+=N'DATABASE_ROLE;'; END;

/* Explicit server grants are restricted to the declared login/public baselines and standard endpoints. */
IF EXISTS (
    SELECT 1
    FROM master.sys.server_permissions AS p
    WHERE p.grantee_principal_id IN (@ReaderPrincipalId,@PublicPrincipalId)
      AND NOT (
          p.state='G' AND p.class_desc='SERVER' AND (
              (p.grantee_principal_id=@ReaderPrincipalId AND p.permission_name=N'CONNECT SQL')
              OR (p.grantee_principal_id=@PublicPrincipalId AND p.permission_name=N'VIEW ANY DATABASE')
          )
          OR p.state='G' AND p.class_desc='ENDPOINT' AND p.permission_name=N'CONNECT'
             AND p.grantee_principal_id=@PublicPrincipalId
             AND EXISTS (SELECT 1 FROM master.sys.endpoints AS e
                         WHERE e.endpoint_id=p.major_id AND e.endpoint_id<65536
                           AND e.is_admin_endpoint=0)
      )
)
    BEGIN SET @UnexpectedCount+=1; SET @FailureCategories+=N'SERVER_PERMISSION;'; END;

/* User-defined endpoints are not classified as the documented built-in endpoint baseline. */
IF EXISTS (SELECT 1 FROM master.sys.endpoints WHERE endpoint_id>=65536)
    BEGIN SET @UnexpectedCount+=1; SET @FailureCategories+=N'CUSTOM_ENDPOINT;'; END;

/* Target database grants may only contribute declared CONNECT/SHOWPLAN/object rights; DENY is never accepted. */
IF EXISTS (
    SELECT 1
    FROM sys.database_permissions AS p
    WHERE p.grantee_principal_id IN (@ReaderUserId,@PublicDatabasePrincipalId)
      AND (
          p.state<>'G'
          OR NOT (
              p.class_desc='DATABASE' AND p.grantee_principal_id IN (@PublicDatabasePrincipalId,@ReaderUserId) AND p.permission_name=N'CONNECT'
              OR p.class_desc='DATABASE' AND p.grantee_principal_id=@PublicDatabasePrincipalId
                 AND p.permission_name IN (N'VIEW ANY COLUMN ENCRYPTION KEY DEFINITION',N'VIEW ANY COLUMN MASTER KEY DEFINITION')
              OR p.class_desc='DATABASE' AND p.grantee_principal_id=@ReaderUserId AND p.permission_name=N'SHOWPLAN'
              OR p.class_desc='OBJECT_OR_COLUMN' AND p.grantee_principal_id=@PublicDatabasePrincipalId
                 AND p.permission_name=N'SELECT' AND p.minor_id=0 AND p.major_id<0
                 AND @PublicSystemSelectBaselineMismatch=0
                 AND EXISTS (SELECT 1 FROM @PublicSystemSelects AS baseline
                             WHERE baseline.ObjectId=p.major_id AND baseline.MinorId=p.minor_id
                               AND baseline.PermissionName COLLATE Latin1_General_100_BIN2=p.permission_name COLLATE Latin1_General_100_BIN2
                               AND baseline.StateDesc COLLATE Latin1_General_100_BIN2=N'GRANT')
              OR p.class_desc='OBJECT_OR_COLUMN' AND p.minor_id=0 AND p.grantee_principal_id=@ReaderUserId
                 AND EXISTS (
                     SELECT 1 FROM (VALUES
                       (N'dbo',N'Person',N'SELECT'),(N'dbo',N'FriendOf',N'SELECT'),
                       (N'dbo',N'RelPerson',N'SELECT'),(N'dbo',N'RelFriend',N'SELECT'),
                       (N'dbo',N'OraclePerson',N'SELECT'),(N'dbo',N'OracleFriendOf',N'SELECT'),
                       (N'dbo',N'OracleRelPerson',N'SELECT'),(N'dbo',N'OracleRelFriend',N'SELECT'),
                       (N'lab',N'MeasurementRun',N'SELECT'),(N'lab',N'USP_Qry023MeasureVariant',N'EXECUTE')
                     ) AS expected(schema_name,object_name,permission_name)
                     JOIN sys.schemas AS s ON s.name=expected.schema_name
                     JOIN sys.objects AS o ON o.schema_id=s.schema_id AND o.name=expected.object_name
                     WHERE o.object_id=p.major_id AND expected.permission_name=p.permission_name
                 )
          )
      )
)
    BEGIN SET @UnexpectedCount+=1; SET @FailureCategories+=N'DATABASE_PERMISSION;'; END;

IF @UnexpectedCount>0 OR @PublicSystemSelectBaselineMismatch>0
BEGIN
    SELECT N'DATABASE_PERMISSION' AS FailureDetail,dp.name AS PrincipalName,p.class_desc,p.major_id,p.minor_id,
           p.permission_name,p.state_desc,OBJECT_SCHEMA_NAME(p.major_id) AS SchemaName,OBJECT_NAME(p.major_id) AS ObjectName
    FROM sys.database_permissions AS p
    JOIN sys.database_principals AS dp ON dp.principal_id=p.grantee_principal_id
    WHERE p.grantee_principal_id IN (@ReaderUserId,@PublicDatabasePrincipalId)
    ORDER BY dp.name,p.class_desc,p.major_id,p.minor_id,p.permission_name;
    SELECT 1 AS Sequence,'ADMIN_PERMISSION_INVENTORY' AS Phase,'BASELINE' AS CheckId,'FAIL' AS Outcome,'FAIL_NOT_PROVEN' AS Code,
           CONCAT(N'Abweichungsgruppen=',@UnexpectedCount,N'; Kategorien=',@FailureCategories,N'; public-Systemobjekt-SELECT count=',@PublicSystemSelectCount,N'/',COALESCE(@PublicSystemSelectExpectedCount,-1),N'; SHA256=',COALESCE(@PublicSystemSelectActualHash,'UNKNOWN'),N'/',COALESCE(@PublicSystemSelectExpectedHash,'UNKNOWN')) AS ObservedValue,
           N'Exakte public-Systemobjekt-SELECT-Menge für den festgeschriebenen SQL-Server-Build' AS RequiredValue,
           N'Keine Berechtigungen werden vergeben oder geändert.' AS Message;
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_NOT_PROVEN';
    THROW 51013,'FAIL_NOT_PROVEN: ADMIN-Inventar weicht von der freigegebenen QRY-023-Baseline ab.',1;
END;

SELECT 1 AS Sequence,'ADMIN_PERMISSION_INVENTORY' AS Phase,'PUBLIC_SYSTEM_SELECT_BASELINE' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'Build=',CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion')),N'; Objekte=',@PublicSystemSelectCount,N'; SHA256=',@PublicSystemSelectActualHash) AS ObservedValue,
       CONCAT(N'Objekte=',@PublicSystemSelectExpectedCount,N'; SHA256=',@PublicSystemSelectExpectedHash) AS RequiredValue,
       N'Die versionsgebundene unveränderliche public-Systemobjektbaseline stimmt exakt.' AS Message;

SELECT N'READER_IDENTITY' AS InventoryClass,sp.type_desc AS LoginType,sp.is_disabled,
       CAST(CASE WHEN sp.name=@ReaderLogin THEN 1 ELSE 0 END AS bit) AS ExactNameMatch,
       CAST(CASE WHEN sp.sid=dp.sid THEN 1 ELSE 0 END AS bit) AS SidMatch,dp.type_desc AS DatabaseUserType
FROM master.sys.server_principals AS sp
JOIN sys.database_principals AS dp ON dp.principal_id=@ReaderUserId
WHERE sp.principal_id=@ReaderPrincipalId;
SELECT N'SERVER_ROLE' AS InventoryClass,r.name AS PrincipalName,m.name AS MemberName
FROM master.sys.server_role_members AS rm
JOIN master.sys.server_principals AS r ON r.principal_id=rm.role_principal_id
JOIN master.sys.server_principals AS m ON m.principal_id=rm.member_principal_id
WHERE rm.member_principal_id=@ReaderPrincipalId AND rm.role_principal_id<>@PublicPrincipalId;
SELECT N'SERVER_PERMISSION' AS InventoryClass,
       CASE WHEN p.grantee_principal_id=@ReaderPrincipalId THEN N'READER_LOGIN' ELSE N'PUBLIC' END AS GranteeClass,
       p.class_desc,p.major_id,p.permission_name,p.state_desc
FROM master.sys.server_permissions AS p
JOIN master.sys.server_principals AS grantee ON grantee.principal_id=p.grantee_principal_id
WHERE p.grantee_principal_id IN (@ReaderPrincipalId,@PublicPrincipalId)
ORDER BY grantee.name,p.class_desc,p.major_id,p.permission_name;
SELECT N'ENDPOINT' AS InventoryClass,e.endpoint_id,e.name,e.type_desc,e.protocol_desc,e.is_admin_endpoint,e.state_desc
FROM master.sys.endpoints AS e ORDER BY e.endpoint_id;
SELECT N'DATABASE_ROLE' AS InventoryClass,r.name AS PrincipalName,m.name AS MemberName
FROM sys.database_role_members AS rm
JOIN sys.database_principals AS r ON r.principal_id=rm.role_principal_id
JOIN sys.database_principals AS m ON m.principal_id=rm.member_principal_id
WHERE rm.member_principal_id=@ReaderUserId AND rm.role_principal_id<>@PublicDatabasePrincipalId;
SELECT N'DATABASE_LIST' AS InventoryClass,d.name,d.state_desc,d.user_access_desc,d.is_read_only
FROM master.sys.databases AS d WHERE d.database_id>4 ORDER BY d.database_id;
SELECT N'DATABASE_PERMISSION' AS InventoryClass,
       CASE WHEN p.grantee_principal_id=@ReaderUserId THEN N'READER_USER' ELSE N'PUBLIC' END AS GranteeClass,
       p.class_desc,p.major_id,p.minor_id,p.permission_name,p.state_desc
FROM sys.database_permissions AS p
JOIN sys.database_principals AS grantee ON grantee.principal_id=p.grantee_principal_id
WHERE p.grantee_principal_id IN (@ReaderUserId,@PublicDatabasePrincipalId)
ORDER BY grantee.name,p.class_desc,p.major_id,p.minor_id,p.permission_name;

PRINT 'QRY023_OBJECT_INVENTORY|PASS|13';
PRINT CONCAT('QRY023_ENDPOINT_INVENTORY|BEGIN|',@ReaderEndpointCount);
DECLARE @EndpointId int,@EndpointName sysname;
DECLARE EndpointHandoffCursor CURSOR LOCAL FAST_FORWARD FOR
SELECT endpoint_id,name FROM master.sys.endpoints WHERE endpoint_id<65536 AND is_admin_endpoint=0 ORDER BY endpoint_id;
OPEN EndpointHandoffCursor;
FETCH NEXT FROM EndpointHandoffCursor INTO @EndpointId,@EndpointName;
WHILE @@FETCH_STATUS=0
BEGIN
    PRINT CONCAT('QRY023_ENDPOINT|',@EndpointId,'|',CONVERT(varchar(512),CONVERT(varbinary(256),@EndpointName),2));
    FETCH NEXT FROM EndpointHandoffCursor INTO @EndpointId,@EndpointName;
END;
CLOSE EndpointHandoffCursor;
DEALLOCATE EndpointHandoffCursor;
PRINT CONCAT('QRY023_ENDPOINT_INVENTORY|END|',@ReaderEndpointCount);

SELECT 1 AS Sequence,'ADMIN_PERMISSION_INVENTORY' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'ReaderProfile=READER; ReaderSidBound=1; UserDatabases=',@UserDatabaseCount,
              N'; Endpoints=',@EndpointCount,N'; ReaderEndpoints=',@ReaderEndpointCount,N'; ExplicitInventory=complete') AS ObservedValue,
       N'exakte READER-SID, keine Zusatzrollen/-rechte, vollständiges Ein-Datenbank- und Standardendpointinventar' AS RequiredValue,
       N'Diese ADMIN-Prüfung belegt keine tatsächlichen READER-Effektrechte oder Ownership-Chain-Wirkung.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
