/* QRY-023: create or reuse only the exact marker-owned database. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @ReaderLogin sysname=N'$(ReaderLogin)',@ReaderSid varbinary(85),@ReaderUserSid varbinary(85),@ReaderUserName sysname;
DECLARE @ExpectedDatabase sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken);
DECLARE @MajorVersion int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
DECLARE @ProductVersion nvarchar(128)=CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'));
DECLARE @ExpectedBuild nvarchar(128)=CASE @MajorVersion
    WHEN 15 THEN N'15.0.4500.2'
    WHEN 16 THEN N'16.0.4305.5'
    WHEN 17 THEN N'17.0.5035.5'
END;
DECLARE @CompatibilityLevel int=CASE @MajorVersion WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
DECLARE @Created bit=0,@Sql nvarchar(max),@Project nvarchar(max),@Contract nvarchar(max),@ExistingDemo nvarchar(max),@ExistingRun nvarchar(max);

IF @DemoId<>'QRY-023' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 20
   OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9_]%'
   OR @TargetDatabase<>@ExpectedDatabase OR @CompatibilityLevel IS NULL OR @ProductVersion IS NULL
   OR @ProductVersion COLLATE Latin1_General_100_BIN2<>@ExpectedBuild
    THROW 51000,'FAIL_CONTRACT: QRY-023-Zielkennung oder Engine-Version ist ungültig.',1;

IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    DECLARE @DataDirectory nvarchar(4000),@LogDirectory nvarchar(4000),@DataPath nvarchar(4000),@LogPath nvarchar(4000);
    SELECT @DataDirectory=LEFT(physical_name,LEN(physical_name)-CHARINDEX(N'/',REVERSE(physical_name))+1)
    FROM sys.master_files WHERE database_id=DB_ID(N'model') AND type=0;
    SELECT @LogDirectory=LEFT(physical_name,LEN(physical_name)-CHARINDEX(N'/',REVERSE(physical_name))+1)
    FROM sys.master_files WHERE database_id=DB_ID(N'model') AND type=1;
    IF @DataDirectory IS NULL OR @LogDirectory IS NULL
        THROW 51006,'FAIL_RESOURCE: SQL-Server-Standardpfade für begrenzte QRY-023-Dateien sind nicht nachweisbar.',1;
    SET @DataPath=@DataDirectory+@TargetDatabase+N'.mdf';
    SET @LogPath=@LogDirectory+@TargetDatabase+N'_log.ldf';
    SET @Sql=N'CREATE DATABASE '+QUOTENAME(@TargetDatabase)+N'
ON PRIMARY (NAME='+QUOTENAME(@TargetDatabase)+N',FILENAME=N'''+REPLACE(@DataPath,N'''',N'''''')+N''',SIZE=8MB,MAXSIZE=512MB,FILEGROWTH=64MB)
LOG ON (NAME='+QUOTENAME(@TargetDatabase+N'_log')+N',FILENAME=N'''+REPLACE(@LogPath,N'''',N'''''')+N''',SIZE=8MB,MAXSIZE=512MB,FILEGROWTH=64MB);';
    EXEC sys.sp_executesql @Sql;
    SET @Created=1;
END;

IF @Created=1
BEGIN
    SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=@Demo;
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@Run;';
    BEGIN TRY
        EXEC sys.sp_executesql @Sql,N'@Demo varchar(7),@Run varchar(20)',@Demo=@DemoId,@Run=@RunToken;
    END TRY
    BEGIN CATCH
        SELECT 1 AS Sequence,'CLEANUP' AS Phase,'PRESERVE_DATABASE_AFTER_MARKER_ERROR' AS CheckId,'FAIL' AS Outcome,'FAIL_CLEANUP' AS Code,
               CONCAT(N'OriginalError=',ERROR_NUMBER(),N'; created target retained for ownership review') AS ObservedValue,
               N'No automatic removal before exact ownership markers are verified' AS RequiredValue,
               N'Die neu angelegte Datenbank bleibt bei Markerfehler erhalten; Cleanup benötigt manuelle Zustandsklärung.' AS Message;
        PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_CLEANUP';
        THROW;
    END CATCH;
END
ELSE
BEGIN
    SET @Sql=N'SELECT @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
@ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
@DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
@RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
    EXEC sys.sp_executesql @Sql,N'@ProjectOut nvarchar(max) OUTPUT,@ContractOut nvarchar(max) OUTPUT,@DemoOut nvarchar(max) OUTPUT,@RunOut nvarchar(max) OUTPUT',
         @ProjectOut=@Project OUTPUT,@ContractOut=@Contract OUTPUT,@DemoOut=@ExistingDemo OUTPUT,@RunOut=@ExistingRun OUTPUT;
    IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
       OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
       OR @ExistingDemo IS NULL OR @ExistingDemo COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@DemoId) OR DATALENGTH(@ExistingDemo)<>DATALENGTH(CONVERT(nvarchar(max),@DemoId))
       OR @ExistingRun IS NULL OR @ExistingRun COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@RunToken) OR DATALENGTH(@ExistingRun)<>DATALENGTH(CONVERT(nvarchar(max),@RunToken))
        THROW 51002,'FAIL_STATE: Gleichnamige Ziel-Datenbank besitzt nicht alle exakt passenden QRY-023-Eigentumsmarker.',1;
END;

SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET RECOVERY SIMPLE;
ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_CLOSE OFF;
ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_SHRINK OFF;
ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET PAGE_VERIFY CHECKSUM;
ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET COMPATIBILITY_LEVEL='+CONVERT(nvarchar(10),@CompatibilityLevel)+N';';
EXEC sys.sp_executesql @Sql;

SELECT @ReaderSid=sid FROM sys.server_principals
WHERE name=@ReaderLogin AND type='S' AND is_disabled=0;
IF @ReaderSid IS NULL
    THROW 51003,'FAIL_CONTRACT: READER muss ein aktiver SQL_LOGIN sein.',1;
SET @Sql=N'SELECT @UserSid=sid,@UserName=name FROM '+QUOTENAME(@TargetDatabase)+N'.sys.database_principals WHERE sid=@LoginSid AND type=''S'';';
EXEC sys.sp_executesql @Sql,N'@LoginSid varbinary(85),@UserSid varbinary(85) OUTPUT,@UserName sysname OUTPUT',
     @LoginSid=@ReaderSid,@UserSid=@ReaderUserSid OUTPUT,@UserName=@ReaderUserName OUTPUT;
IF @ReaderUserSid IS NULL
BEGIN
    SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';
        IF EXISTS(SELECT 1 FROM sys.database_principals WHERE name=@LoginName)
        THROW 51004,''FAIL_STATE: READER-Name ist bereits anders zugeordnet.'',1;
        CREATE USER '+QUOTENAME(@ReaderLogin)+N' FOR LOGIN '+QUOTENAME(@ReaderLogin)+N';';
    EXEC sys.sp_executesql @Sql,N'@LoginName sysname',@LoginName=@ReaderLogin;
    SET @ReaderUserName=@ReaderLogin;
END;
IF @ReaderUserName<>@ReaderLogin
    THROW 51005,'FAIL_STATE: READER-Login ist in der Zieldatenbank unter einem anderen Namen abgebildet.',1;

SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N'; GRANT SHOWPLAN TO '+QUOTENAME(@ReaderLogin)+N';';
EXEC sys.sp_executesql @Sql;

SELECT 1 AS Sequence,'SETUP' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'Database=',@TargetDatabase,N'; CompatibilityLevel=',@CompatibilityLevel,N'; Created=',@Created) AS ObservedValue,
       N'isolierte, vollständig markierte und versionsgebundene Datenbank' AS RequiredValue,
       N'Die QRY-023-Zieldatenbank ist bereit.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
