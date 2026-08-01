/* OPT-009 setup: marker-protected database, skewed equality model and four comparison objects. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7) = '$(DemoId)';
DECLARE @RunToken varchar(20) = '$(RunToken)';
DECLARE @TargetDatabase sysname = N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname = CONVERT(sysname, N'SQLPERF_LAB_' + REPLACE(@DemoId, '-', '') + N'_' + @RunToken);
DECLARE @MajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @CompatibilityLevel int = CASE @MajorVersion WHEN 16 THEN 160 WHEN 17 THEN 170 END;
DECLARE @Created bit = 0;
DECLARE @Sql nvarchar(max);
DECLARE @Project nvarchar(128);
DECLARE @Contract nvarchar(32);
DECLARE @ExistingDemo varchar(7);
DECLARE @ExistingRun varchar(20);

IF @DemoId <> 'OPT-009' OR @TargetDatabase <> @ExpectedDatabase OR @CompatibilityLevel IS NULL
    THROW 51000, 'FAIL_CONTRACT: OPT-009-Zielkennung oder Engine-Version ist ungültig.', 1;

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

/* Ausgangszustand: PSP ist abgeschaltet, damit die Baseline den klassischen Einzelplan zeigt. */
ALTER DATABASE SCOPED CONFIGURATION SET PARAMETER_SENSITIVE_PLAN_OPTIMIZATION = OFF;

IF SCHEMA_ID(N'lab') IS NULL EXEC sys.sp_executesql N'CREATE SCHEMA lab AUTHORIZATION dbo;';
DROP PROCEDURE IF EXISTS lab.usp_Opt009Capture;
DROP PROCEDURE IF EXISTS lab.usp_Opt009SearchOptOut;
DROP PROCEDURE IF EXISTS lab.usp_Opt009SearchPsp;
DROP PROCEDURE IF EXISTS lab.usp_Opt009SearchCommonFirst;
DROP PROCEDURE IF EXISTS lab.usp_Opt009SearchSelectiveFirst;
DROP TABLE IF EXISTS lab.Opt009Evidence;
DROP TABLE IF EXISTS lab.PspOrder;

CREATE TABLE lab.PspOrder
(
    PspOrderId int NOT NULL CONSTRAINT PK_Opt009_PspOrder PRIMARY KEY CLUSTERED,
    OwnerId int NOT NULL,
    OrderDate date NOT NULL,
    Payload char(200) NOT NULL
);

CREATE TABLE lab.Opt009Evidence
(
    Phase varchar(20) NOT NULL,
    ParameterLabel varchar(12) NOT NULL,
    ResultRowCount int NOT NULL,
    ResultChecksum int NULL,
    LogicalReads bigint NULL,
    CachedPlanCount int NOT NULL,
    DispatcherPlanCount int NOT NULL,
    VariantPlanCount int NOT NULL,
    QueryVariantId int NULL,
    LowBoundary nvarchar(40) NULL,
    HighBoundary nvarchar(40) NULL,
    EvidenceAvailable bit NOT NULL,
    CapturedAt datetime2(3) NOT NULL CONSTRAINT DF_Opt009Evidence_CapturedAt DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_Opt009Evidence PRIMARY KEY (Phase, ParameterLabel)
);

/*
   Verteilung mit ausgepraegter Schiefe: ein dominanter Eigentuemer und viele sehr kleine.
   OwnerId = 1 traegt 99 000 Zeilen, die OwnerIds 2 bis 201 tragen je 5 Zeilen.
*/
;WITH Numbers AS
(
    SELECT TOP (100000) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS Position
    FROM sys.all_objects AS a
    CROSS JOIN sys.all_objects AS b
)
INSERT lab.PspOrder (PspOrderId, OwnerId, OrderDate, Payload)
SELECT Position,
       CASE WHEN Position <= 99000 THEN 1 ELSE 2 + ((Position - 99001) / 5) END,
       DATEADD(day, -(Position % 365), CONVERT(date, '2026-01-01')),
       REPLICATE('x', 200)
FROM Numbers;

/* Nicht abdeckender Index: der selektive Wert erhaelt Suche mit Schluesselsuche, der haeufige Wert eine Pruefung. */
CREATE NONCLUSTERED INDEX IX_Opt009_PspOrder_OwnerId
    ON lab.PspOrder (OwnerId);

UPDATE STATISTICS lab.PspOrder WITH FULLSCAN;
GO

SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

/* Der Marker steht im Anweisungstext, damit Dispatcher- und Variantenplaene eindeutig zuzuordnen sind. */
CREATE PROCEDURE lab.usp_Opt009SearchSelectiveFirst
    @OwnerId int,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(o.PspOrderId, o.Payload))
    FROM lab.PspOrder AS o
    WHERE o.OwnerId = @OwnerId
    /* OPT009_MARK_BASELINE */;
END;
GO

CREATE PROCEDURE lab.usp_Opt009SearchCommonFirst
    @OwnerId int,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(o.PspOrderId, o.Payload))
    FROM lab.PspOrder AS o
    WHERE o.OwnerId = @OwnerId
    /* OPT009_MARK_DEMONSTRATION */;
END;
GO

CREATE PROCEDURE lab.usp_Opt009SearchPsp
    @OwnerId int,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(o.PspOrderId, o.Payload))
    FROM lab.PspOrder AS o
    WHERE o.OwnerId = @OwnerId
    /* OPT009_MARK_MITIGATION */;
END;
GO

/* Dokumentierte Abwahl auf Abfrageebene; der Querytext ist ansonsten identisch. */
CREATE PROCEDURE lab.usp_Opt009SearchOptOut
    @OwnerId int,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(o.PspOrderId, o.Payload))
    FROM lab.PspOrder AS o
    WHERE o.OwnerId = @OwnerId
    /* OPT009_MARK_OPTOUT */
    OPTION (USE HINT ('DISABLE_PARAMETER_SENSITIVE_PLAN'));
END;
GO

CREATE PROCEDURE lab.usp_Opt009Capture
    @Phase varchar(20),
    @ParameterLabel varchar(12),
    @Marker nvarchar(40),
    @ResultRowCount int,
    @ResultChecksum int
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Pattern nvarchar(60) = N'%' + @Marker + N'%';
    /* Zusammengesetzt, damit der Prozedurtext selbst nicht auf das Suchmuster passt. */
    DECLARE @VariantPattern nvarchar(40) = N'%PLAN PER' + N' VALUE%';
    DECLARE @TablePattern nvarchar(40) = N'%Psp' + N'Order%';
    DECLARE @DispatcherPattern nvarchar(40) = N'%<Dis' + N'patcher>%';
    DECLARE @CachedPlanCount int = 0;
    DECLARE @DispatcherPlanCount int = 0;
    DECLARE @VariantPlanCount int = 0;
    DECLARE @QueryVariantId int = NULL;
    DECLARE @LowBoundary nvarchar(40) = NULL;
    DECLARE @HighBoundary nvarchar(40) = NULL;
    DECLARE @LogicalReads bigint = NULL;
    DECLARE @EvidenceAvailable bit = 1;

    BEGIN TRY
        /* Dispatcher-Evidenz haengt am markierten Anweisungstext der Prozedur. */
        SELECT @CachedPlanCount = COUNT(DISTINCT cp.plan_handle),
               @DispatcherPlanCount = COUNT(DISTINCT CASE
                   WHEN CONVERT(nvarchar(max), qp.query_plan) LIKE @DispatcherPattern THEN cp.plan_handle END)
        FROM sys.dm_exec_cached_plans AS cp
        CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
        OUTER APPLY sys.dm_exec_query_plan(cp.plan_handle) AS qp
        WHERE cp.objtype IN ('Proc', 'Prepared')
          AND st.text LIKE @Pattern;

        /*
           Query Variants entstehen laut Produktdokumentation als Prepared Statements
           und tragen den erzeugten Hinweis im Anweisungstext. Der Tabellenname ist
           innerhalb dieser Demodatenbank eindeutig und ueberlebt jede Textnormalisierung.
        */
        SELECT @VariantPlanCount = COUNT(DISTINCT cp.plan_handle)
        FROM sys.dm_exec_cached_plans AS cp
        CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
        WHERE cp.objtype = 'Prepared'
          AND st.text LIKE @VariantPattern
          AND st.text LIKE @TablePattern;

        SELECT TOP (1) @LogicalReads = qs.last_logical_reads
        FROM sys.dm_exec_query_stats AS qs
        INNER JOIN sys.dm_exec_cached_plans AS cp ON cp.plan_handle = qs.plan_handle
        CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
        WHERE (cp.objtype IN ('Proc', 'Prepared') AND st.text LIKE @Pattern)
           OR (cp.objtype = 'Prepared' AND st.text LIKE @VariantPattern AND st.text LIKE @TablePattern)
        ORDER BY qs.last_execution_time DESC, qs.last_logical_reads DESC;

        IF @VariantPlanCount > 0
        BEGIN
            ;WITH XMLNAMESPACES (DEFAULT 'http://schemas.microsoft.com/sqlserver/2004/07/showplan')
            SELECT TOP (1)
                   @LowBoundary = qp.query_plan.value('(//ParameterSensitivePredicate/@LowBoundary)[1]', 'nvarchar(40)'),
                   @HighBoundary = qp.query_plan.value('(//ParameterSensitivePredicate/@HighBoundary)[1]', 'nvarchar(40)'),
                   @QueryVariantId = qp.query_plan.value('(//QueryPlan/@QueryVariantID)[1]', 'int')
            FROM sys.dm_exec_cached_plans AS cp
            CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
            CROSS APPLY sys.dm_exec_query_plan(cp.plan_handle) AS qp
            WHERE cp.objtype = 'Prepared'
              AND st.text LIKE @VariantPattern
              AND st.text LIKE @TablePattern
            ORDER BY cp.usecounts DESC;
        END;
    END TRY
    BEGIN CATCH
        SET @EvidenceAvailable = 0;
    END CATCH;

    IF @CachedPlanCount = 0
        SET @EvidenceAvailable = 0;

    DELETE lab.Opt009Evidence WHERE Phase = @Phase AND ParameterLabel = @ParameterLabel;

    INSERT lab.Opt009Evidence
        (Phase, ParameterLabel, ResultRowCount, ResultChecksum, LogicalReads,
         CachedPlanCount, DispatcherPlanCount, VariantPlanCount, QueryVariantId,
         LowBoundary, HighBoundary, EvidenceAvailable)
    VALUES
        (@Phase, @ParameterLabel, @ResultRowCount, @ResultChecksum, @LogicalReads,
         @CachedPlanCount, @DispatcherPlanCount, @VariantPlanCount, @QueryVariantId,
         @LowBoundary, @HighBoundary, @EvidenceAvailable);
END;
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Owners int;
DECLARE @CommonRows int;
DECLARE @SelectiveRows int;

SELECT @Rows = COUNT(*), @Owners = COUNT(DISTINCT OwnerId) FROM lab.PspOrder;
SELECT @CommonRows = COUNT(*) FROM lab.PspOrder WHERE OwnerId = 1;
SELECT @SelectiveRows = COUNT(*) FROM lab.PspOrder WHERE OwnerId = 2;

IF @Rows <> 100000 OR @Owners <> 201 OR @CommonRows <> 99000 OR @SelectiveRows <> 5
    THROW 51002, 'FAIL_STATE: Das synthetische Verteilungsmodell für OPT-009 ist nicht wie vereinbart aufgebaut.', 1;

SELECT 1 AS Sequence, 'SETUP' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Zeilen=', @Rows, N'; Eigentuemer=', @Owners,
              N'; haeufig/selektiv=', @CommonRows, N'/', @SelectiveRows,
              N'; PSP=OFF als Ausgangszustand') AS ObservedValue,
       N'100000 Zeilen, 201 Eigentuemer, ausgepraegte Schiefe' AS RequiredValue,
       N'Das OPT-009-Modell ist deterministisch aufgebaut.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
