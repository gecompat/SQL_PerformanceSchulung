/* OPT-015 setup: marker-protected database, deterministic distribution and normalized plan evidence. */
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

IF @DemoId <> 'OPT-015' OR @TargetDatabase <> @ExpectedDatabase OR @CompatibilityLevel IS NULL
    THROW 51000, 'FAIL_CONTRACT: OPT-015-Zielkennung oder Engine-Version ist ungültig.', 1;

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

SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N'; ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS = ON;';
EXEC sys.sp_executesql @Sql;
GO

USE [$(TargetDatabase)];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;

IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
DROP PROCEDURE IF EXISTS lab.usp_Opt015Capture;
DROP PROCEDURE IF EXISTS lab.usp_Opt015Workload;
DROP TABLE IF EXISTS lab.Opt015Evidence;
DROP TABLE IF EXISTS lab.WorkItem;
DROP TABLE IF EXISTS lab.EntityGroup;

CREATE TABLE lab.EntityGroup
(
    EntityGroupId int NOT NULL CONSTRAINT PK_EntityGroup PRIMARY KEY,
    GroupCode char(4) NOT NULL CONSTRAINT UQ_EntityGroup_GroupCode UNIQUE
);

CREATE TABLE lab.WorkItem
(
    WorkItemId int NOT NULL CONSTRAINT PK_WorkItem PRIMARY KEY CLUSTERED,
    EntityGroupId int NOT NULL,
    StatusCode tinyint NOT NULL,
    EventTime datetime2(0) NOT NULL,
    MeasureValue int NOT NULL,
    Payload char(80) NOT NULL,
    CONSTRAINT FK_WorkItem_EntityGroup FOREIGN KEY(EntityGroupId) REFERENCES lab.EntityGroup(EntityGroupId)
);

CREATE TABLE lab.Opt015Evidence
(
    Phase varchar(20) NOT NULL CONSTRAINT PK_Opt015Evidence PRIMARY KEY,
    RequestedGroupId int NOT NULL,
    ResultRowCount bigint NOT NULL,
    ResultChecksum int NULL,
    QueryHash binary(8) NULL,
    StatementSubTreeCost float NULL,
    StatementEstimateRows float NULL,
    AccessPhysicalOp nvarchar(60) NULL,
    AccessLogicalOp nvarchar(60) NULL,
    AccessEstimateRows float NULL,
    AccessActualRows bigint NULL,
    AccessActualRowsRead bigint NULL,
    AccessExecutions bigint NULL,
    StatisticsUsageCount int NOT NULL,
    FirstStatisticsName nvarchar(256) NULL,
    WarningCount int NOT NULL,
    LastLogicalReads bigint NULL,
    LastWorkerTimeUs bigint NULL,
    LastElapsedTimeUs bigint NULL,
    CapturedAtUtc datetime2(3) NOT NULL CONSTRAINT DF_Opt015Evidence_Captured DEFAULT SYSUTCDATETIME()
);

INSERT lab.EntityGroup(EntityGroupId, GroupCode)
SELECT v.EntityGroupId, CONVERT(char(4), CONCAT('G', RIGHT(CONCAT('000', v.EntityGroupId), 3)))
FROM
(
    VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10),
           (11),(12),(13),(14),(15),(16),(17),(18),(19),(20),(999)
) v(EntityGroupId);

;WITH Digits AS
(
    SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) d(n)
), Numbers AS
(
    SELECT TOP (200000)
        n = 1 + d0.n + d1.n*10 + d2.n*100 + d3.n*1000 + d4.n*10000 + d5.n*100000
    FROM Digits d0 CROSS JOIN Digits d1 CROSS JOIN Digits d2
    CROSS JOIN Digits d3 CROSS JOIN Digits d4 CROSS JOIN Digits d5
    ORDER BY 1
)
INSERT lab.WorkItem(WorkItemId, EntityGroupId, StatusCode, EventTime, MeasureValue, Payload)
SELECT n,
       1 + ((n - 1) % 20),
       CONVERT(tinyint, n % 5),
       DATEADD(minute, CONVERT(int, (CONVERT(bigint, n) * 37) % 1051200), CONVERT(datetime2(0), '20230101')),
       n % 10000,
       CONVERT(char(80), REPLICATE(CHAR(65 + (n % 26)), 60) + RIGHT(REPLICATE('0', 20) + CONVERT(varchar(20), n), 20))
FROM Numbers
OPTION (MAXDOP 1);

CREATE INDEX IX_WorkItem_EntityGroupId
ON lab.WorkItem(EntityGroupId, WorkItemId)
INCLUDE(StatusCode, MeasureValue);

UPDATE STATISTICS lab.WorkItem IX_WorkItem_EntityGroupId WITH FULLSCAN, NORECOMPUTE;

EXEC(N'
CREATE PROCEDURE lab.usp_Opt015Workload
    @EntityGroupId int,
    @ResultRowCount bigint OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        @ResultRowCount = COUNT_BIG(*),
        @ResultChecksum = CHECKSUM_AGG(BINARY_CHECKSUM(w.WorkItemId, w.EntityGroupId, w.StatusCode))
    FROM lab.WorkItem AS w /*SQLPERF_OPT015_WORKLOAD*/
    WHERE w.EntityGroupId = @EntityGroupId
    OPTION (MAXDOP 1);
END;
');

EXEC(N'
CREATE PROCEDURE lab.usp_Opt015Capture
    @Phase varchar(20),
    @RequestedGroupId int,
    @ResultRowCount bigint,
    @ResultChecksum int
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Plan xml;
    DECLARE @QueryHash binary(8);
    DECLARE @LastLogicalReads bigint;
    DECLARE @LastWorkerTimeUs bigint;
    DECLARE @LastElapsedTimeUs bigint;
    DECLARE @StatementSubTreeCost float;
    DECLARE @StatementEstimateRows float;
    DECLARE @AccessNodeId int;
    DECLARE @AccessPhysicalOp nvarchar(60);
    DECLARE @AccessLogicalOp nvarchar(60);
    DECLARE @AccessEstimateRows float;
    DECLARE @AccessActualRows bigint;
    DECLARE @AccessActualRowsRead bigint;
    DECLARE @AccessExecutions bigint;
    DECLARE @StatisticsUsageCount int = 0;
    DECLARE @FirstStatisticsName nvarchar(256);
    DECLARE @WarningCount int = 0;

    SELECT TOP (1)
        @Plan = ps.query_plan,
        @QueryHash = qs.query_hash,
        @LastLogicalReads = qs.last_logical_reads,
        @LastWorkerTimeUs = qs.last_worker_time,
        @LastElapsedTimeUs = qs.last_elapsed_time
    FROM sys.dm_exec_query_stats AS qs
    CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
    CROSS APPLY sys.dm_exec_query_plan_stats(qs.plan_handle) AS ps
    CROSS APPLY
    (
        VALUES
        (
            SUBSTRING
            (
                st.text,
                (qs.statement_start_offset / 2) + 1,
                CASE
                    WHEN qs.statement_end_offset = -1
                    THEN (DATALENGTH(st.text) - qs.statement_start_offset) / 2 + 1
                    ELSE (qs.statement_end_offset - qs.statement_start_offset) / 2 + 1
                END
            )
        )
    ) AS statement_text(value)
    WHERE statement_text.value LIKE ''%SQLPERF_OPT015_WORKLOAD%''
    ORDER BY qs.last_execution_time DESC;

    IF @Plan IS NULL
        THROW 51005, ''FAIL_EVIDENCE: Der letzte Actual Plan für OPT-015 ist nicht verfügbar.'', 1;

    ;WITH XMLNAMESPACES(DEFAULT ''http://schemas.microsoft.com/sqlserver/2004/07/showplan'')
    SELECT TOP (1)
        @StatementSubTreeCost = stmt.node.value(''@StatementSubTreeCost'', ''float''),
        @StatementEstimateRows = stmt.node.value(''@StatementEstRows'', ''float''),
        @StatisticsUsageCount = stmt.node.value(''count(.//OptimizerStatsUsage/StatisticsInfo)'', ''int''),
        @WarningCount = stmt.node.value(''count(.//Warnings/*)'', ''int'')
    FROM @Plan.nodes(''//StmtSimple'') AS stmt(node)
    WHERE stmt.node.value(''@StatementText'', ''nvarchar(4000)'') LIKE ''%SQLPERF_OPT015_WORKLOAD%'';

    ;WITH XMLNAMESPACES(DEFAULT ''http://schemas.microsoft.com/sqlserver/2004/07/showplan'')
    SELECT TOP (1)
        @FirstStatisticsName = CONCAT
        (
            stats.node.value(''@Database'', ''nvarchar(128)''), N''.'',
            stats.node.value(''@Schema'', ''nvarchar(128)''), N''.'',
            stats.node.value(''@Table'', ''nvarchar(128)''), N''.'',
            stats.node.value(''@Statistics'', ''nvarchar(128)'')
        )
    FROM @Plan.nodes(''//StmtSimple'') AS stmt(node)
    CROSS APPLY stmt.node.nodes(''.//OptimizerStatsUsage/StatisticsInfo'') AS stats(node)
    WHERE stmt.node.value(''@StatementText'', ''nvarchar(4000)'') LIKE ''%SQLPERF_OPT015_WORKLOAD%'';

    ;WITH XMLNAMESPACES(DEFAULT ''http://schemas.microsoft.com/sqlserver/2004/07/showplan'')
    SELECT TOP (1)
        @AccessNodeId = rel.node.value(''@NodeId'', ''int''),
        @AccessPhysicalOp = rel.node.value(''@PhysicalOp'', ''nvarchar(60)''),
        @AccessLogicalOp = rel.node.value(''@LogicalOp'', ''nvarchar(60)''),
        @AccessEstimateRows = rel.node.value(''@EstimateRows'', ''float'')
    FROM @Plan.nodes(''//StmtSimple'') AS stmt(node)
    CROSS APPLY stmt.node.nodes(''.//RelOp'') AS rel(node)
    WHERE stmt.node.value(''@StatementText'', ''nvarchar(4000)'') LIKE ''%SQLPERF_OPT015_WORKLOAD%''
      AND rel.node.exist(''.//Object[contains(@Table, "WorkItem")]'') = 1
    ORDER BY rel.node.value(''@NodeId'', ''int'') DESC;

    ;WITH XMLNAMESPACES(DEFAULT ''http://schemas.microsoft.com/sqlserver/2004/07/showplan'')
    SELECT
        @AccessActualRows = SUM(rt.node.value(''@ActualRows'', ''bigint'')),
        @AccessActualRowsRead = SUM(CASE WHEN rt.node.exist(''@ActualRowsRead'') = 1 THEN rt.node.value(''@ActualRowsRead'', ''bigint'') ELSE rt.node.value(''@ActualRows'', ''bigint'') END),
        @AccessExecutions = SUM(CASE WHEN rt.node.exist(''@ActualExecutions'') = 1 THEN rt.node.value(''@ActualExecutions'', ''bigint'') ELSE 1 END)
    FROM @Plan.nodes(''//StmtSimple'') AS stmt(node)
    CROSS APPLY stmt.node.nodes(''.//RelOp[@NodeId=sql:variable("@AccessNodeId")]/RunTimeInformation/RunTimeCountersPerThread'') AS rt(node)
    WHERE stmt.node.value(''@StatementText'', ''nvarchar(4000)'') LIKE ''%SQLPERF_OPT015_WORKLOAD%'';

    DELETE lab.Opt015Evidence WHERE Phase = @Phase;
    INSERT lab.Opt015Evidence
    (
        Phase, RequestedGroupId, ResultRowCount, ResultChecksum, QueryHash,
        StatementSubTreeCost, StatementEstimateRows, AccessPhysicalOp, AccessLogicalOp,
        AccessEstimateRows, AccessActualRows, AccessActualRowsRead, AccessExecutions,
        StatisticsUsageCount, FirstStatisticsName, WarningCount,
        LastLogicalReads, LastWorkerTimeUs, LastElapsedTimeUs
    )
    VALUES
    (
        @Phase, @RequestedGroupId, @ResultRowCount, @ResultChecksum, @QueryHash,
        @StatementSubTreeCost, @StatementEstimateRows, @AccessPhysicalOp, @AccessLogicalOp,
        @AccessEstimateRows, @AccessActualRows, @AccessActualRowsRead, @AccessExecutions,
        COALESCE(@StatisticsUsageCount, 0), @FirstStatisticsName, COALESCE(@WarningCount, 0),
        @LastLogicalReads, @LastWorkerTimeUs, @LastElapsedTimeUs
    );
END;
');

IF (SELECT COUNT_BIG(*) FROM lab.WorkItem) <> 200000
    THROW 51003, 'FAIL_EXECUTION: OPT-015-Basisdatenmenge ist unvollständig.', 1;

SELECT 1 AS Sequence, 'SETUP' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       N'200000 Zeilen in 20 Gruppen; Fullscan-Statistik mit NORECOMPUTE; normalisierte Actual-Plan-Evidenz' AS ObservedValue,
       N'markierte Testdatenbank; LAST_QUERY_PLAN_STATS nur datenbankbezogen' AS RequiredValue,
       N'OPT-015 wurde reproduzierbar aufgebaut.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
GO
