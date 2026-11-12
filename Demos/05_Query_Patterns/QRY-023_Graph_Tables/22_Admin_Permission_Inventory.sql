/* Read-only ADMIN inventory for the exact QRY-023 target and READER principal. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)',
        @ReaderLogin sysname=N'$(ReaderLogin)',@MajorVersion int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')),
        @ReaderPrincipalId int,@ReaderSid varbinary(85),@PublicPrincipalId int,@PublicDatabasePrincipalId int,
        @ReaderUserId int,@ReaderUserSid varbinary(85),
        @Project nvarchar(max),@Contract nvarchar(max),@MarkerDemo nvarchar(max),@MarkerRun nvarchar(max),@Sql nvarchar(max),
        @UserDatabaseCount int,@EndpointCount int,@UnqualifiedPublicSystemSelectCount int=0,
        @Visible bit=1,@UnexpectedCount int=0;

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
    IF ISNULL(HAS_PERMS_BY_NAME(NULL,'SERVER','VIEW ANY SECURITY DEFINITION'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,'SERVER','VIEW ANY DEFINITION'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,'SERVER','VIEW SERVER SECURITY STATE'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,'SERVER','VIEW ANY DATABASE'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','VIEW SECURITY DEFINITION'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','VIEW DEFINITION'),0)<>1
        SET @Visible=0;
END
ELSE IF @MajorVersion=15
BEGIN
    IF ISNULL(HAS_PERMS_BY_NAME(NULL,'SERVER','VIEW ANY DEFINITION'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,'SERVER','VIEW SERVER STATE'),0)<>1
       OR ISNULL(HAS_PERMS_BY_NAME(NULL,'SERVER','VIEW ANY DATABASE'),0)<>1
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
SELECT @UnqualifiedPublicSystemSelectCount=COUNT(*)
FROM sys.database_permissions
WHERE grantee_principal_id=@PublicDatabasePrincipalId AND class_desc='OBJECT_OR_COLUMN'
  AND permission_name=N'SELECT' AND minor_id=0 AND major_id<0;

IF @ReaderPrincipalId IS NULL OR @PublicPrincipalId IS NULL OR @PublicDatabasePrincipalId IS NULL OR @ReaderSid IS NULL
   OR @ReaderUserId IS NULL OR @ReaderUserSid IS NULL OR @ReaderSid<>@ReaderUserSid
   OR @UserDatabaseCount<>1 OR @EndpointCount=0 OR DB_NAME()<>@TargetDatabase
    SET @UnexpectedCount+=1;

/* public is an implicit membership. Any explicit server role is outside the READER baseline. */
IF EXISTS (SELECT 1 FROM master.sys.server_role_members
           WHERE member_principal_id=@ReaderPrincipalId AND role_principal_id<>@PublicPrincipalId)
    SET @UnexpectedCount+=1;
IF EXISTS (SELECT 1 FROM sys.database_role_members
           WHERE member_principal_id=@ReaderUserId AND role_principal_id<>@PublicDatabasePrincipalId)
    SET @UnexpectedCount+=1;

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
    SET @UnexpectedCount+=1;

/* User-defined endpoints are not classified as the documented built-in endpoint baseline. */
IF EXISTS (SELECT 1 FROM master.sys.endpoints WHERE endpoint_id>=65536)
    SET @UnexpectedCount+=1;

/* Target database grants may only contribute declared CONNECT/SHOWPLAN/object rights; DENY is never accepted. */
IF EXISTS (
    SELECT 1
    FROM sys.database_permissions AS p
    WHERE p.grantee_principal_id IN (@ReaderUserId,@PublicDatabasePrincipalId)
      AND (
          p.state<>'G'
          OR NOT (
              p.class_desc='DATABASE' AND p.grantee_principal_id=@PublicDatabasePrincipalId AND p.permission_name=N'CONNECT'
              OR p.class_desc='DATABASE' AND p.grantee_principal_id=@PublicDatabasePrincipalId
                 AND p.permission_name IN (N'VIEW ANY COLUMN ENCRYPTION KEY DEFINITION',N'VIEW ANY COLUMN MASTER KEY DEFINITION')
              OR p.class_desc='DATABASE' AND p.grantee_principal_id=@ReaderUserId AND p.permission_name=N'SHOWPLAN'
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
    SET @UnexpectedCount+=1;

IF @UnexpectedCount>0 OR @UnqualifiedPublicSystemSelectCount>0
BEGIN
    SELECT 1 AS Sequence,'ADMIN_PERMISSION_INVENTORY' AS Phase,'BASELINE' AS CheckId,'FAIL' AS Outcome,'FAIL_NOT_PROVEN' AS Code,
           CONCAT(N'Abweichungsgruppen=',@UnexpectedCount,N'; public-Systemobjekt-SELECT-Grants ohne exakte versionsgebundene Sollmenge=',@UnqualifiedPublicSystemSelectCount) AS ObservedValue,
           N'Exakte versionsgebundene Baseline der SQL-Server-public-Systemobjektrechte; bis zur Enginequalifikation kein PASS' AS RequiredValue,
           N'Keine Berechtigungen werden vergeben oder geändert.' AS Message;
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_NOT_PROVEN';
    THROW 51013,'FAIL_NOT_PROVEN: ADMIN-Inventar weicht von der freigegebenen QRY-023-Baseline ab.',1;
END;

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

SELECT 1 AS Sequence,'ADMIN_PERMISSION_INVENTORY' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'ReaderProfile=READER; ReaderSidBound=1; UserDatabases=',@UserDatabaseCount,
              N'; Endpoints=',@EndpointCount,N'; ExplicitInventory=complete') AS ObservedValue,
       N'exakte READER-SID, keine Zusatzrollen/-rechte, vollständiges Ein-Datenbank- und Standardendpointinventar' AS RequiredValue,
       N'Diese ADMIN-Prüfung belegt keine tatsächlichen READER-Effektrechte oder Ownership-Chain-Wirkung.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
