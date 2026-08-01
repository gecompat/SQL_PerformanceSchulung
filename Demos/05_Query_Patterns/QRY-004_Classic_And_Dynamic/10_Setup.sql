/* QRY-004 setup: marker-protected database, deterministic skewed search model and three strategy objects. */
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

IF @DemoId <> 'QRY-004' OR @TargetDatabase <> @ExpectedDatabase OR @CompatibilityLevel IS NULL
    THROW 51000, 'FAIL_CONTRACT: QRY-004-Zielkennung oder Engine-Version ist ungültig.', 1;

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

IF SCHEMA_ID(N'lab') IS NULL EXEC sys.sp_executesql N'CREATE SCHEMA lab AUTHORIZATION dbo;';
DROP PROCEDURE IF EXISTS lab.usp_Qry004Capture;
DROP PROCEDURE IF EXISTS lab.usp_Qry004Dynamic;
DROP PROCEDURE IF EXISTS lab.usp_Qry004Recompile;
DROP PROCEDURE IF EXISTS lab.usp_Qry004CatchAll;
DROP TABLE IF EXISTS lab.Qry004Evidence;
DROP TABLE IF EXISTS lab.Qry004AllowedFilter;
DROP TABLE IF EXISTS lab.SearchOrder;
DROP TABLE IF EXISTS lab.SearchStatus;

CREATE TABLE lab.SearchStatus
(
    StatusCode tinyint NOT NULL CONSTRAINT PK_Qry004_SearchStatus PRIMARY KEY,
    StatusName nvarchar(20) NOT NULL
);

CREATE TABLE lab.SearchOrder
(
    SearchOrderId int NOT NULL CONSTRAINT PK_Qry004_SearchOrder PRIMARY KEY CLUSTERED,
    CategoryCode char(4) NOT NULL,
    StatusCode tinyint NOT NULL,
    Payload char(200) NOT NULL,
    CONSTRAINT FK_Qry004_SearchOrder_Status FOREIGN KEY(StatusCode) REFERENCES lab.SearchStatus(StatusCode)
);

CREATE TABLE lab.Qry004AllowedFilter
(
    FilterName varchar(20) NOT NULL CONSTRAINT PK_Qry004AllowedFilter PRIMARY KEY,
    PredicateText nvarchar(200) NOT NULL
);

CREATE TABLE lab.Qry004Evidence
(
    Phase varchar(20) NOT NULL,
    Strategy varchar(12) NOT NULL,
    Combination varchar(12) NOT NULL,
    ResultRowCount int NOT NULL,
    ResultChecksum int NULL,
    LogicalReads bigint NULL,
    CachedPlanCount int NOT NULL,
    ExecutionCount bigint NULL,
    WorkerTimeUs bigint NULL,
    LiteralFreeText bit NULL,
    EvidenceAvailable bit NOT NULL,
    CapturedAt datetime2(3) NOT NULL CONSTRAINT DF_Qry004Evidence_CapturedAt DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_Qry004Evidence PRIMARY KEY (Phase, Strategy, Combination)
);

INSERT lab.SearchStatus (StatusCode, StatusName)
VALUES (0, N'NEW'), (1, N'ACTIVE'), (2, N'HOLD'), (3, N'CLOSED'), (4, N'ARCHIVED');

/* Nur diese Prädikatsbausteine dürfen in dynamisches SQL übernommen werden. */
INSERT lab.Qry004AllowedFilter (FilterName, PredicateText)
VALUES ('CategoryCode', N' AND o.CategoryCode = @p_CategoryCode'),
       ('StatusCode', N' AND o.StatusCode = @p_StatusCode');

;WITH Numbers AS
(
    SELECT TOP (20000) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS Position
    FROM sys.all_objects AS a
    CROSS JOIN sys.all_objects AS b
)
INSERT lab.SearchOrder (SearchOrderId, CategoryCode, StatusCode, Payload)
SELECT Position,
       CASE WHEN Position <= 20 THEN 'RARE' ELSE 'CMMN' END,
       CONVERT(tinyint, Position % 5),
       REPLICATE('x', 200)
FROM Numbers;

CREATE NONCLUSTERED INDEX IX_Qry004_SearchOrder_CategoryCode
    ON lab.SearchOrder (CategoryCode);

CREATE NONCLUSTERED INDEX IX_Qry004_SearchOrder_StatusCode
    ON lab.SearchOrder (StatusCode);

UPDATE STATISTICS lab.SearchOrder WITH FULLSCAN;
GO

CREATE PROCEDURE lab.usp_Qry004CatchAll
    @CategoryCode char(4) = NULL,
    @StatusCode tinyint = NULL,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    /* QRY004_CATCHALL: optionale Prädikate in einem einzigen statischen Querytext. */
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(SearchOrderId, Payload))
    FROM lab.SearchOrder
    WHERE (@CategoryCode IS NULL OR CategoryCode = @CategoryCode)
      AND (@StatusCode IS NULL OR StatusCode = @StatusCode);
END;
GO

CREATE PROCEDURE lab.usp_Qry004Recompile
    @CategoryCode char(4) = NULL,
    @StatusCode tinyint = NULL,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    /* QRY004_RECOMPILE: identischer Querytext, je Ausführung neu optimiert. */
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(SearchOrderId, Payload))
    FROM lab.SearchOrder
    WHERE (@CategoryCode IS NULL OR CategoryCode = @CategoryCode)
      AND (@StatusCode IS NULL OR StatusCode = @StatusCode)
    OPTION (RECOMPILE);
END;
GO

CREATE PROCEDURE lab.usp_Qry004Dynamic
    @FilterSpec varchar(100),
    @CategoryCode char(4) = NULL,
    @StatusCode tinyint = NULL,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Marker nvarchar(40) = N'QRY004' + N'_DYNAMIC_FORM';
    DECLARE @Predicates nvarchar(1000);
    DECLARE @Unknown varchar(20);
    DECLARE @Sql nvarchar(max);

    SELECT @Unknown = MIN(LTRIM(RTRIM(s.value)))
    FROM STRING_SPLIT(@FilterSpec, ';') AS s
    WHERE LTRIM(RTRIM(s.value)) <> ''
      AND NOT EXISTS (SELECT 1 FROM lab.Qry004AllowedFilter AS f WHERE f.FilterName = LTRIM(RTRIM(s.value)));

    IF @Unknown IS NOT NULL
        THROW 51000, 'FAIL_CONTRACT: Die angeforderte Filterdefinition steht nicht auf der Positivliste.', 1;

    /* Die Prädikatsreihenfolge ist normalisiert, damit gleiche Filterformen denselben Querytext ergeben. */
    SELECT @Predicates = STRING_AGG(f.PredicateText, N'') WITHIN GROUP (ORDER BY f.FilterName)
    FROM STRING_SPLIT(@FilterSpec, ';') AS s
    INNER JOIN lab.Qry004AllowedFilter AS f ON f.FilterName = LTRIM(RTRIM(s.value));

    SET @Sql = N'SELECT @RowsOut = COUNT(*),
       @ChecksumOut = CHECKSUM_AGG(CHECKSUM(o.SearchOrderId, o.Payload))
FROM lab.SearchOrder AS o
WHERE 1 = 1' + ISNULL(@Predicates, N'') + N'
/* ' + @Marker + N' */;';

    EXEC sys.sp_executesql @Sql,
        N'@p_CategoryCode char(4), @p_StatusCode tinyint, @RowsOut int OUTPUT, @ChecksumOut int OUTPUT',
        @p_CategoryCode = @CategoryCode,
        @p_StatusCode = @StatusCode,
        @RowsOut = @ResultRowCount OUTPUT,
        @ChecksumOut = @ResultChecksum OUTPUT;
END;
GO

CREATE PROCEDURE lab.usp_Qry004Capture
    @Phase varchar(20),
    @Strategy varchar(12),
    @Combination varchar(12),
    @ResultRowCount int,
    @ResultChecksum int
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @ObjectId int = CASE @Strategy
                                WHEN 'CATCHALL' THEN OBJECT_ID(N'lab.usp_Qry004CatchAll')
                                WHEN 'RECOMPILE' THEN OBJECT_ID(N'lab.usp_Qry004Recompile')
                            END;
    DECLARE @Pattern nvarchar(60) = N'%' + N'QRY004' + N'_DYNAMIC_FORM%';
    DECLARE @CachedPlanCount int = 0;
    DECLARE @LogicalReads bigint = NULL;
    DECLARE @ExecutionCount bigint = NULL;
    DECLARE @WorkerTimeUs bigint = NULL;
    DECLARE @LiteralFreeText bit = NULL;
    DECLARE @EvidenceAvailable bit = 1;

    BEGIN TRY
        IF @Strategy = 'DYNAMIC'
        BEGIN
            SELECT @CachedPlanCount = COUNT(DISTINCT cp.plan_handle)
            FROM sys.dm_exec_cached_plans AS cp
            CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
            WHERE cp.objtype = 'Prepared'
              AND st.text LIKE @Pattern;

            SELECT @LiteralFreeText = CASE WHEN EXISTS
                   (
                       SELECT 1
                       FROM sys.dm_exec_cached_plans AS cp
                       CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
                       WHERE cp.objtype = 'Prepared'
                         AND st.text LIKE @Pattern
                         AND (st.text LIKE N'%RARE%' OR st.text LIKE N'%CMMN%')
                   ) THEN 0 ELSE 1 END;

            SELECT TOP (1) @LogicalReads = qs.last_logical_reads,
                           @ExecutionCount = qs.execution_count,
                           @WorkerTimeUs = qs.total_worker_time
            FROM sys.dm_exec_query_stats AS qs
            CROSS APPLY sys.dm_exec_sql_text(qs.plan_handle) AS st
            WHERE st.text LIKE @Pattern
            ORDER BY qs.last_execution_time DESC;
        END
        ELSE
        BEGIN
            SELECT @CachedPlanCount = COUNT(*),
                   @LogicalReads = MAX(ps.last_logical_reads),
                   @ExecutionCount = SUM(ps.execution_count),
                   @WorkerTimeUs = SUM(ps.total_worker_time)
            FROM sys.dm_exec_procedure_stats AS ps
            WHERE ps.database_id = DB_ID()
              AND ps.object_id = @ObjectId;
        END;
    END TRY
    BEGIN CATCH
        SET @EvidenceAvailable = 0;
    END CATCH;

    IF @CachedPlanCount = 0
        SET @EvidenceAvailable = 0;

    DELETE FROM lab.Qry004Evidence WHERE Phase = @Phase AND Strategy = @Strategy AND Combination = @Combination;

    INSERT lab.Qry004Evidence
        (Phase, Strategy, Combination, ResultRowCount, ResultChecksum, LogicalReads,
         CachedPlanCount, ExecutionCount, WorkerTimeUs, LiteralFreeText, EvidenceAvailable)
    VALUES
        (@Phase, @Strategy, @Combination, @ResultRowCount, @ResultChecksum, @LogicalReads,
         @CachedPlanCount, @ExecutionCount, @WorkerTimeUs, @LiteralFreeText, @EvidenceAvailable);
END;
GO

SET NOCOUNT ON;
DECLARE @RowCount int = (SELECT COUNT(*) FROM lab.SearchOrder);
DECLARE @RareCount int = (SELECT COUNT(*) FROM lab.SearchOrder WHERE CategoryCode = 'RARE');
DECLARE @StatusCount int = (SELECT COUNT(*) FROM lab.SearchOrder WHERE StatusCode = 1);
DECLARE @FilterCount int = (SELECT COUNT(*) FROM lab.Qry004AllowedFilter);

IF @RowCount <> 20000 OR @RareCount <> 20 OR @StatusCount <> 4000 OR @FilterCount <> 2
    THROW 51002, 'FAIL_STATE: Das synthetische Suchdatenmodell hat nicht die erwartete Verteilung.', 1;

SELECT 1 AS Sequence, 'SETUP' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Zeilen=', @RowCount, N'; RARE=', @RareCount, N'; Status1=', @StatusCount,
              N'; Positivliste=', @FilterCount) AS ObservedValue,
       N'20000 Zeilen, deterministisch schiefe Verteilung und zwei zugelassene Filterbausteine' AS RequiredValue,
       N'Setup für QRY-004 ist abgeschlossen.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
