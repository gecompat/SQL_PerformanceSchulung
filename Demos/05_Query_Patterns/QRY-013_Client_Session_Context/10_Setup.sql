/* QRY-013 setup: marker-protected database with a deterministic skewed search model. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7) = '$(DemoId)';
DECLARE @RunToken varchar(20) = '$(RunToken)';
DECLARE @TargetDatabase sysname = N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname = CONVERT(sysname, N'SQLPERF_LAB_' + REPLACE(@DemoId, '-', '') + N'_' + @RunToken);
DECLARE @MajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @CompatibilityLevel int = CASE @MajorVersion WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
DECLARE @Created bit = 0;
DECLARE @Sql nvarchar(max);
DECLARE @Project nvarchar(128);
DECLARE @Contract nvarchar(32);
DECLARE @ExistingDemo varchar(7);
DECLARE @ExistingRun varchar(20);

IF @DemoId <> 'QRY-013' OR @TargetDatabase <> @ExpectedDatabase OR @CompatibilityLevel IS NULL
    THROW 51000, 'FAIL_CONTRACT: QRY-013-Zielkennung oder Engine-Version ist ungültig.', 1;

IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    SET @Sql = N'CREATE DATABASE ' + QUOTENAME(@TargetDatabase) + N';';
    EXEC sys.sp_executesql @Sql;
    SET @Created = 1;
END;

SET @Sql = N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET RECOVERY SIMPLE;
ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET AUTO_CLOSE OFF;
ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET AUTO_SHRINK OFF;
ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET PAGE_VERIFY CHECKSUM;
ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET COMPATIBILITY_LEVEL = ' + CONVERT(nvarchar(10), @CompatibilityLevel) + N';';
EXEC sys.sp_executesql @Sql;

IF @Created = 1
BEGIN
    SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'', @value=N''SQL_PerformanceSchulung'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'', @value=N''1.0'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'', @value=@DemoId;
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'', @value=@RunToken;';
    EXEC sys.sp_executesql @Sql, N'@DemoId varchar(7), @RunToken varchar(20)', @DemoId=@DemoId, @RunToken=@RunToken;
END
ELSE
BEGIN
    SET @Sql = N'SELECT
 @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),
 @ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),
 @DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),
 @RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END)
FROM ' + QUOTENAME(@TargetDatabase) + N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
    EXEC sys.sp_executesql @Sql,
        N'@ProjectOut nvarchar(128) OUTPUT,@ContractOut nvarchar(32) OUTPUT,@DemoOut varchar(7) OUTPUT,@RunOut varchar(20) OUTPUT',
        @ProjectOut=@Project OUTPUT,@ContractOut=@Contract OUTPUT,@DemoOut=@ExistingDemo OUTPUT,@RunOut=@ExistingRun OUTPUT;
    IF @Project <> N'SQL_PerformanceSchulung' OR @Contract <> N'1.0' OR @ExistingDemo <> @DemoId OR @ExistingRun <> @RunToken
        THROW 51002, 'FAIL_STATE: Eine gleichnamige Datenbank besitzt nicht die erwarteten Eigentumsmarker.', 1;
END;
GO

USE [$(TargetDatabase)];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;

IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
DROP PROCEDURE IF EXISTS lab.usp_Qry013Capture;
DROP PROCEDURE IF EXISTS lab.usp_Qry013Probe;
DROP TABLE IF EXISTS lab.Qry013Evidence;
DROP TABLE IF EXISTS lab.SearchItem;
DROP TABLE IF EXISTS lab.SearchItemStatus;

CREATE TABLE lab.SearchItemStatus
(
    StatusCode tinyint NOT NULL CONSTRAINT PK_Qry013_SearchItemStatus PRIMARY KEY,
    StatusName nvarchar(20) NOT NULL
);

CREATE TABLE lab.SearchItem
(
    SearchItemId int NOT NULL CONSTRAINT PK_Qry013_SearchItem PRIMARY KEY CLUSTERED,
    CategoryCode char(4) NOT NULL,
    StatusCode tinyint NOT NULL,
    Payload char(60) NOT NULL,
    CONSTRAINT FK_Qry013_SearchItem_Status FOREIGN KEY(StatusCode) REFERENCES lab.SearchItemStatus(StatusCode)
);

CREATE TABLE lab.Qry013Evidence
(
    Phase varchar(20) NOT NULL CONSTRAINT PK_Qry013Evidence PRIMARY KEY,
    ProfileCode varchar(10) NOT NULL,
    ParameterValue char(4) NOT NULL,
    SessionOptions int NOT NULL,
    DatabaseId int NOT NULL,
    CachedPlanCount int NOT NULL,
    DistinctSetOptions int NOT NULL,
    LogicalReads bigint NULL,
    EvidenceAvailable bit NOT NULL,
    ResultRowCount int NOT NULL,
    ResultChecksum int NULL,
    CapturedAt datetime2(3) NOT NULL CONSTRAINT DF_Qry013Evidence_CapturedAt DEFAULT SYSUTCDATETIME()
);

INSERT lab.SearchItemStatus (StatusCode, StatusName)
VALUES (0, N'NEW'), (1, N'ACTIVE'), (2, N'HOLD'), (3, N'CLOSED'), (4, N'ARCHIVED');

;WITH Numbers AS
(
    SELECT TOP (20020) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS Position
    FROM sys.all_objects AS a
    CROSS JOIN sys.all_objects AS b
)
INSERT lab.SearchItem (SearchItemId, CategoryCode, StatusCode, Payload)
SELECT Position,
       CASE WHEN Position <= 20 THEN 'RARE' ELSE 'CMMN' END,
       CONVERT(tinyint, Position % 5),
       REPLICATE('x', 60)
FROM Numbers;

CREATE NONCLUSTERED INDEX IX_Qry013_SearchItem_CategoryCode
    ON lab.SearchItem (CategoryCode);

UPDATE STATISTICS lab.SearchItem WITH FULLSCAN;
GO

CREATE PROCEDURE lab.usp_Qry013Probe
    @CategoryCode char(4),
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    /* QRY013_PROBE: identischer Querytext für alle Clientprofile. */
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(SearchItemId, Payload))
    FROM lab.SearchItem
    WHERE CategoryCode = @CategoryCode;
END;
GO

CREATE PROCEDURE lab.usp_Qry013Capture
    @Phase varchar(20),
    @ProfileCode varchar(10),
    @ParameterValue char(4),
    @ResultRowCount int,
    @ResultChecksum int
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @ObjectId int = OBJECT_ID(N'lab.usp_Qry013Probe');
    DECLARE @CachedPlanCount int = 0;
    DECLARE @DistinctSetOptions int = 0;
    DECLARE @LogicalReads bigint = NULL;
    DECLARE @EvidenceAvailable bit = 1;

    BEGIN TRY
        SELECT @CachedPlanCount = COUNT(*),
               @DistinctSetOptions = COUNT(DISTINCT CONVERT(bigint, pa.value))
        FROM sys.dm_exec_procedure_stats AS ps
        CROSS APPLY sys.dm_exec_plan_attributes(ps.plan_handle) AS pa
        WHERE ps.database_id = DB_ID()
          AND ps.object_id = @ObjectId
          AND pa.attribute = 'set_options';

        SELECT TOP (1) @LogicalReads = ps.last_logical_reads
        FROM sys.dm_exec_procedure_stats AS ps
        WHERE ps.database_id = DB_ID()
          AND ps.object_id = @ObjectId
        ORDER BY ps.last_execution_time DESC;
    END TRY
    BEGIN CATCH
        SET @EvidenceAvailable = 0;
    END CATCH;

    IF @CachedPlanCount = 0
        SET @EvidenceAvailable = 0;

    DELETE FROM lab.Qry013Evidence WHERE Phase = @Phase;

    INSERT lab.Qry013Evidence
        (Phase, ProfileCode, ParameterValue, SessionOptions, DatabaseId,
         CachedPlanCount, DistinctSetOptions, LogicalReads, EvidenceAvailable,
         ResultRowCount, ResultChecksum)
    VALUES
        (@Phase, @ProfileCode, @ParameterValue, @@OPTIONS, DB_ID(),
         @CachedPlanCount, @DistinctSetOptions, @LogicalReads, @EvidenceAvailable,
         @ResultRowCount, @ResultChecksum);
END;
GO

SET NOCOUNT ON;
DECLARE @RowCount int = (SELECT COUNT(*) FROM lab.SearchItem);
DECLARE @RareCount int = (SELECT COUNT(*) FROM lab.SearchItem WHERE CategoryCode = 'RARE');

IF @RowCount <> 20020 OR @RareCount <> 20
    THROW 51002, 'FAIL_STATE: Das synthetische Suchdatenmodell hat nicht die erwartete Verteilung.', 1;

SELECT 1 AS Sequence, 'SETUP' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Zeilen=', @RowCount, N'; RARE=', @RareCount, N'; Objekte=lab.usp_Qry013Probe, lab.usp_Qry013Capture') AS ObservedValue,
       N'20020 Zeilen mit deterministisch schiefer CategoryCode-Verteilung' AS RequiredValue,
       N'Setup für QRY-013 ist abgeschlossen.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
