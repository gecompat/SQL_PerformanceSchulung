/* OPT-010 setup: marker-protected database, uniform optional-parameter model and four comparison objects. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7) = '$(DemoId)';
DECLARE @RunToken varchar(20) = '$(RunToken)';
DECLARE @TargetDatabase sysname = N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname = CONVERT(sysname, N'SQLPERF_LAB_' + REPLACE(@DemoId, '-', '') + N'_' + @RunToken);
DECLARE @MajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @CompatibilityLevel int = CASE @MajorVersion WHEN 17 THEN 170 END;
DECLARE @Created bit = 0;
DECLARE @Sql nvarchar(max);
DECLARE @Project nvarchar(128);
DECLARE @Contract nvarchar(32);
DECLARE @ExistingDemo varchar(7);
DECLARE @ExistingRun varchar(20);

IF @DemoId <> 'OPT-010' OR @TargetDatabase <> @ExpectedDatabase OR @CompatibilityLevel IS NULL
    THROW 51000, 'FAIL_CONTRACT: OPT-010-Zielkennung oder Engine-Version ist ungültig.', 1;

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
/* ANSI_NULLS OFF schliesst die Optimierung laut Produktdokumentation aus; die Demo arbeitet ausschliesslich mit ANSI_NULLS ON. */
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;

/* Ausgangszustand: die Optimierung ist abgeschaltet, damit die Baseline den klassischen Einzelplan zeigt. */
ALTER DATABASE SCOPED CONFIGURATION SET OPTIONAL_PARAMETER_OPTIMIZATION = OFF;

IF SCHEMA_ID(N'lab') IS NULL EXEC sys.sp_executesql N'CREATE SCHEMA lab AUTHORIZATION dbo;';
DROP PROCEDURE IF EXISTS lab.usp_Opt010Capture;
DROP PROCEDURE IF EXISTS lab.usp_Opt010SearchOptOut;
DROP PROCEDURE IF EXISTS lab.usp_Opt010SearchOppo;
DROP PROCEDURE IF EXISTS lab.usp_Opt010SearchNullFirst;
DROP PROCEDURE IF EXISTS lab.usp_Opt010SearchSelectiveFirst;
DROP TABLE IF EXISTS lab.Opt010Evidence;
DROP TABLE IF EXISTS lab.OppoListing;

CREATE TABLE lab.OppoListing
(
    OppoListingId int NOT NULL CONSTRAINT PK_Opt010_OppoListing PRIMARY KEY CLUSTERED,
    AgentId int NOT NULL,
    ListedOn date NOT NULL,
    Payload char(200) NOT NULL
);

CREATE TABLE lab.Opt010Evidence
(
    Phase varchar(20) NOT NULL,
    ParameterLabel varchar(12) NOT NULL,
    ResultRowCount int NOT NULL,
    ResultChecksum int NULL,
    LogicalReads bigint NULL,
    CachedPlanCount int NOT NULL,
    DispatcherPlanCount int NOT NULL,
    VariantPlanCount int NOT NULL,
    OptionalPredicatePlanCount int NOT NULL,
    SensitivePredicatePlanCount int NOT NULL,
    OptionalPredicateCount int NULL,
    QueryVariantId int NULL,
    EvidenceAvailable bit NOT NULL,
    CapturedAt datetime2(3) NOT NULL CONSTRAINT DF_Opt010Evidence_CapturedAt DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_Opt010Evidence PRIMARY KEY (Phase, ParameterLabel)
);

/*
   Bewusst gleichmaessige Verteilung: 100 000 Zeilen auf 2 000 Agenten zu je 50 Zeilen.
   Damit liegt keine Schiefe vor; der Planunterschied entsteht allein aus dem
   optionalen Praedikat und nicht aus der Kardinalitaetsverteilung.
*/
;WITH Numbers AS
(
    SELECT TOP (100000) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS Position
    FROM sys.all_objects AS a
    CROSS JOIN sys.all_objects AS b
)
INSERT lab.OppoListing (OppoListingId, AgentId, ListedOn, Payload)
SELECT Position,
       1 + ((Position - 1) / 50),
       DATEADD(day, -(Position % 365), CONVERT(date, '2026-01-01')),
       REPLICATE('x', 200)
FROM Numbers;

/* Nicht abdeckender Index: der belegte Parameter erhaelt Suche mit Schluesselsuche, der offene Parameter eine Prüfung. */
CREATE NONCLUSTERED INDEX IX_Opt010_OppoListing_AgentId
    ON lab.OppoListing (AgentId);

UPDATE STATISTICS lab.OppoListing WITH FULLSCAN;
GO

SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

/* Der Marker steht im Anweisungstext, damit Dispatcher- und Variantenplaene eindeutig zuzuordnen sind. */
CREATE PROCEDURE lab.usp_Opt010SearchSelectiveFirst
    @AgentId int,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(o.OppoListingId, o.Payload))
    FROM lab.OppoListing AS o
    WHERE (o.AgentId = @AgentId OR @AgentId IS NULL)
    /* OPT010_MARK_BASELINE */;
END;
GO

CREATE PROCEDURE lab.usp_Opt010SearchNullFirst
    @AgentId int,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(o.OppoListingId, o.Payload))
    FROM lab.OppoListing AS o
    WHERE (o.AgentId = @AgentId OR @AgentId IS NULL)
    /* OPT010_MARK_DEMONSTRATION */;
END;
GO

CREATE PROCEDURE lab.usp_Opt010SearchOppo
    @AgentId int,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(o.OppoListingId, o.Payload))
    FROM lab.OppoListing AS o
    WHERE (o.AgentId = @AgentId OR @AgentId IS NULL)
    /* OPT010_MARK_MITIGATION */;
END;
GO

/* Dokumentierte Abwahl auf Abfrageebene; der Querytext ist ansonsten identisch. */
CREATE PROCEDURE lab.usp_Opt010SearchOptOut
    @AgentId int,
    @ResultRowCount int OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ResultRowCount = COUNT(*),
           @ResultChecksum = CHECKSUM_AGG(CHECKSUM(o.OppoListingId, o.Payload))
    FROM lab.OppoListing AS o
    WHERE (o.AgentId = @AgentId OR @AgentId IS NULL)
    /* OPT010_MARK_OPTOUT */
    OPTION (USE HINT ('DISABLE_OPTIONAL_PARAMETER_OPTIMIZATION'));
END;
GO

CREATE PROCEDURE lab.usp_Opt010Capture
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
    DECLARE @TablePattern nvarchar(40) = N'%Oppo' + N'Listing%';
    DECLARE @DispatcherPattern nvarchar(40) = N'%<Dis' + N'patcher>%';
    DECLARE @OptionalPattern nvarchar(60) = N'%<Optional' + N'ParameterPredicate%';
    DECLARE @SensitivePattern nvarchar(60) = N'%<Parameter' + N'SensitivePredicate%';
    DECLARE @CachedPlanCount int = 0;
    DECLARE @DispatcherPlanCount int = 0;
    DECLARE @VariantPlanCount int = 0;
    DECLARE @OptionalPredicatePlanCount int = 0;
    DECLARE @SensitivePredicatePlanCount int = 0;
    DECLARE @OptionalPredicateCount int = NULL;
    DECLARE @QueryVariantId int = NULL;
    DECLARE @LogicalReads bigint = NULL;
    DECLARE @EvidenceAvailable bit = 1;

    BEGIN TRY
        /* Dispatcher-Evidenz haengt am markierten Anweisungstext der Prozedur. */
        SELECT @CachedPlanCount = COUNT(DISTINCT cp.plan_handle),
               @DispatcherPlanCount = COUNT(DISTINCT CASE
                   WHEN CONVERT(nvarchar(max), qp.query_plan) LIKE @DispatcherPattern THEN cp.plan_handle END),
               @OptionalPredicatePlanCount = COUNT(DISTINCT CASE
                   WHEN CONVERT(nvarchar(max), qp.query_plan) LIKE @OptionalPattern THEN cp.plan_handle END),
               @SensitivePredicatePlanCount = COUNT(DISTINCT CASE
                   WHEN CONVERT(nvarchar(max), qp.query_plan) LIKE @SensitivePattern THEN cp.plan_handle END)
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
                   @OptionalPredicateCount = qp.query_plan.value('count(//Dispatcher/OptionalParameterPredicate)', 'int'),
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

    DELETE lab.Opt010Evidence WHERE Phase = @Phase AND ParameterLabel = @ParameterLabel;

    INSERT lab.Opt010Evidence
        (Phase, ParameterLabel, ResultRowCount, ResultChecksum, LogicalReads,
         CachedPlanCount, DispatcherPlanCount, VariantPlanCount,
         OptionalPredicatePlanCount, SensitivePredicatePlanCount,
         OptionalPredicateCount, QueryVariantId, EvidenceAvailable)
    VALUES
        (@Phase, @ParameterLabel, @ResultRowCount, @ResultChecksum, @LogicalReads,
         @CachedPlanCount, @DispatcherPlanCount, @VariantPlanCount,
         @OptionalPredicatePlanCount, @SensitivePredicatePlanCount,
         @OptionalPredicateCount, @QueryVariantId, @EvidenceAvailable);
END;
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Agents int;
DECLARE @SelectiveRows int;
DECLARE @MinPerAgent int;
DECLARE @MaxPerAgent int;

SELECT @Rows = COUNT(*), @Agents = COUNT(DISTINCT AgentId) FROM lab.OppoListing;
SELECT @SelectiveRows = COUNT(*) FROM lab.OppoListing WHERE AgentId = 42;
SELECT @MinPerAgent = MIN(PerAgent), @MaxPerAgent = MAX(PerAgent)
FROM (SELECT COUNT(*) AS PerAgent FROM lab.OppoListing GROUP BY AgentId) AS Distribution;

IF @Rows <> 100000 OR @Agents <> 2000 OR @SelectiveRows <> 50 OR @MinPerAgent <> 50 OR @MaxPerAgent <> 50
    THROW 51002, 'FAIL_STATE: Das synthetische Verteilungsmodell für OPT-010 ist nicht wie vereinbart aufgebaut.', 1;

SELECT 1 AS Sequence, 'SETUP' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Zeilen=', @Rows, N'; Agenten=', @Agents,
              N'; Zeilen je Agent=', @MinPerAgent, N'..', @MaxPerAgent,
              N'; Optimierung=OFF als Ausgangszustand') AS ObservedValue,
       N'100000 Zeilen, 2000 Agenten, gleichmaessige Verteilung ohne Schiefe' AS RequiredValue,
       N'Das OPT-010-Modell ist deterministisch aufgebaut.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
