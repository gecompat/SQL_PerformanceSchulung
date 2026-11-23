/* Markergebundener Project-Adapter-Cleanup fuer DGN-007. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname=N'SQLPERF_LAB_DGN007_LOCAL',@SessionName sysname=N'SQLPERF_DGN007_LOCAL';
DECLARE @Project nvarchar(128),@Contract nvarchar(32),@Demo varchar(7),@Run varchar(20),@Sql nvarchar(max);
IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=@SessionName)
        THROW 51004,'PROJECT_CLEANUP_FAILED: Event Session ohne markergebundene DGN-007-Datenbank wird nicht uebernommen.',1;
    SELECT N'DGN-007' AS ScenarioId,N'CLEANUP' AS Phase,N'PASS' AS Outcome,N'ALREADY_ABSENT' AS Code;
    RETURN;
END;
SET @Sql=N'SELECT @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),'
    +N'@Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),'
    +N'@Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),'
    +N'@Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) FROM '
    +QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@Project nvarchar(128) OUTPUT,@Contract nvarchar(32) OUTPUT,@Demo varchar(7) OUTPUT,@Run varchar(20) OUTPUT',@Project OUTPUT,@Contract OUTPUT,@Demo OUTPUT,@Run OUTPUT;
IF COALESCE(@Project,N'')<>N'SQL_PerformanceSchulung' OR COALESCE(@Contract,N'')<>N'1.0'
    OR COALESCE(@Demo,'')<>'DGN-007' OR COALESCE(@Run,'')<>'LOCAL'
    THROW 51004,'PROJECT_CLEANUP_FAILED: DGN-007-Eigentumsmarker stimmen nicht ueberein.',1;
IF EXISTS (SELECT 1 FROM sys.dm_xe_sessions WHERE name=@SessionName)
BEGIN
    SET @Sql=N'ALTER EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER STATE=STOP;';
    EXEC sys.sp_executesql @Sql;
END;
IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=@SessionName)
BEGIN
    SET @Sql=N'DROP EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER;';
    EXEC sys.sp_executesql @Sql;
END;
DECLARE @T2OwnedSession sysname;
IF OBJECT_ID(QUOTENAME(@TargetDatabase)+N'.lab.Dgn007T2CompileOwner',N'U') IS NOT NULL
BEGIN
    SET @Sql=N'SELECT @name=SessionName FROM '+QUOTENAME(@TargetDatabase)
        +N'.lab.Dgn007T2CompileOwner WHERE StateId=1;';
    EXEC sys.sp_executesql @Sql,N'@name sysname OUTPUT',@name=@T2OwnedSession OUTPUT;
END;
IF @T2OwnedSession IS NOT NULL
BEGIN
    DECLARE @T2Prefix sysname=N'SQLPERF_DGN007_T2_';
    IF DATALENGTH(@T2OwnedSession)<>(LEN(@T2Prefix)+32)*2
       OR LEFT(@T2OwnedSession,LEN(@T2Prefix)) COLLATE Latin1_General_100_BIN2<>@T2Prefix
       OR RIGHT(@T2OwnedSession,32) COLLATE Latin1_General_100_BIN2 LIKE N'%[^0-9a-f]%'
        THROW 51014,'FAIL_CLEANUP: Unbekannte T2-Messsitzung.',1;
    IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=@T2OwnedSession)
    BEGIN
        SET @Sql=N'DROP EVENT SESSION '+QUOTENAME(@T2OwnedSession)+N' ON SERVER;';
        EXEC sys.sp_executesql @Sql;
    END;
    IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=@T2OwnedSession)
       OR EXISTS (SELECT 1 FROM sys.dm_xe_sessions WHERE name=@T2OwnedSession)
        THROW 51014,'FAIL_CLEANUP: T2-Messsitzung noch vorhanden.',1;
END;
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE '+QUOTENAME(@TargetDatabase)+N';';
EXEC sys.sp_executesql @Sql;
SELECT N'DGN-007' AS ScenarioId,N'CLEANUP' AS Phase,N'PASS' AS Outcome,N'QUERY_STORE_AND_DATABASE_REMOVED' AS Code;
