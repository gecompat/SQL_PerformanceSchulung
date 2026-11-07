/* QRY-023 preflight: read-only server checks before test database creation. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7) = '$(DemoId)';
DECLARE @RunToken varchar(20) = '$(RunToken)';
DECLARE @TargetDatabase sysname = N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname = CONVERT(sysname, N'SQLPERF_LAB_' + REPLACE(@DemoId, '-', '') + N'_' + @RunToken);
DECLARE @MajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @ProductVersion nvarchar(128) = CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion'));
DECLARE @ExpectedBuild nvarchar(128) = CASE @MajorVersion
    WHEN 15 THEN N'15.0.4430.1'
    WHEN 16 THEN N'16.0.4295.3'
    WHEN 17 THEN N'17.0.5035.5'
END;
DECLARE @HasCreateDatabase bit = CASE WHEN HAS_PERMS_BY_NAME(NULL,NULL,'CREATE ANY DATABASE')=1 OR HAS_PERMS_BY_NAME(NULL,NULL,'ALTER ANY DATABASE')=1 OR HAS_PERMS_BY_NAME(N'master','DATABASE','CREATE DATABASE')=1 THEN 1 ELSE 0 END;
DECLARE @ExistingDatabaseId int = DB_ID(@TargetDatabase);

IF @DemoId <> 'QRY-023'
   OR @RunToken IS NULL
   OR LEN(@RunToken) NOT BETWEEN 1 AND 20
   OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9_]%'
   OR @TargetDatabase <> @ExpectedDatabase
    THROW 51000, 'FAIL_CONTRACT: Demo-ID, Run-Token oder Ziel-Datenbank entsprechen nicht dem QRY-023-Vertrag.', 1;

IF @MajorVersion NOT BETWEEN 15 AND 17
BEGIN
    SELECT 1 AS Sequence,'PREFLIGHT' AS Phase,'ENGINE_VERSION' AS CheckId,'SKIP' AS Outcome,'SKIP_VERSION' AS Code,
           CONVERT(nvarchar(20),@MajorVersion) AS ObservedValue,N'15 bis 17' AS RequiredValue,
           N'QRY-023 ist auf SQL Server 2019, 2022 und 2025 begrenzt.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';
    RETURN;
END;

IF @ProductVersion IS NULL OR @ProductVersion COLLATE Latin1_General_100_BIN2<>@ExpectedBuild
BEGIN
    SELECT 1 AS Sequence,'PREFLIGHT' AS Phase,'ENGINE_BUILD' AS CheckId,'SKIP' AS Outcome,'SKIP_VERSION' AS Code,
           @ProductVersion AS ObservedValue,@ExpectedBuild AS RequiredValue,
           N'Der QRY-023-Entwurf ist an die aktuell festgeschriebenen Builds der Projektprofile gebunden.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';
    RETURN;
END;

IF @HasCreateDatabase=0
BEGIN
    SELECT 1 AS Sequence,'PREFLIGHT' AS Phase,'CREATE_DATABASE_PERMISSION' AS CheckId,'SKIP' AS Outcome,'SKIP_PERMISSION' AS Code,
           N'CREATE DATABASE nicht verfügbar' AS ObservedValue,N'CREATE DATABASE' AS RequiredValue,
           N'Die isolierte QRY-023-Testdatenbank kann nicht sicher angelegt werden.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';
    RETURN;
END;

IF @ExistingDatabaseId IS NOT NULL
BEGIN
    DECLARE @Project nvarchar(max),@Contract nvarchar(max),@ExistingDemo nvarchar(max),@ExistingRun nvarchar(max),@Sql nvarchar(max);
    SET @Sql=N'SELECT @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
@ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
@DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
@RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
    EXEC sys.sp_executesql @Sql,N'@ProjectOut nvarchar(max) OUTPUT,@ContractOut nvarchar(max) OUTPUT,@DemoOut nvarchar(max) OUTPUT,@RunOut nvarchar(max) OUTPUT',
         @ProjectOut=@Project OUTPUT,@ContractOut=@Contract OUTPUT,@DemoOut=@ExistingDemo OUTPUT,@RunOut=@ExistingRun OUTPUT;
    IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
       OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
       OR @ExistingDemo IS NULL OR @ExistingDemo COLLATE Latin1_General_100_BIN2<>N'QRY-023' OR DATALENGTH(@ExistingDemo)<>DATALENGTH(N'QRY-023')
       OR @ExistingRun IS NULL OR @ExistingRun COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@RunToken) OR DATALENGTH(@ExistingRun)<>DATALENGTH(CONVERT(nvarchar(max),@RunToken))
        THROW 51002,'FAIL_STATE: Gleichnamige Ziel-Datenbank besitzt nicht alle exakt passenden QRY-023-Eigentumsmarker.',1;
END;

SELECT 1 AS Sequence,'PREFLIGHT' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'Major=',@MajorVersion,N'; Build=',@ProductVersion,N'; Edition=',CONVERT(nvarchar(128),SERVERPROPERTY('Edition')),N'; ExistingTarget=',CASE WHEN @ExistingDatabaseId IS NULL THEN N'no' ELSE N'owned' END) AS ObservedValue,
       @ExpectedBuild AS RequiredValue,
       N'Der unverändernde QRY-023-Preflight ist bestanden.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
