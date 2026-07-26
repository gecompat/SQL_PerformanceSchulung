/* OPT-016 setup: marker-protected database with repeated and unique outer-key profiles. */
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

IF @DemoId <> 'OPT-016' OR @TargetDatabase <> @ExpectedDatabase OR @CompatibilityLevel IS NULL
    THROW 51000, 'FAIL_CONTRACT: OPT-016-Zielkennung oder Engine-Version ist ungültig.', 1;

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

SET @Sql = N'ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS = ON;';
EXEC (N'USE ' + QUOTENAME(@TargetDatabase) + N'; ' + @Sql);
GO

USE [$(TargetDatabase)];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
DROP PROCEDURE IF EXISTS lab.usp_Opt016Capture;
DROP PROCEDURE IF EXISTS lab.usp_Opt016Workload;
DROP TABLE IF EXISTS lab.Opt016Evidence;
DROP TABLE IF EXISTS lab.ProbeRequest;
DROP TABLE IF EXISTS lab.WorkItemDetail;
DROP TABLE IF EXISTS lab.EntityGroup;

CREATE TABLE lab.EntityGroup
(
    EntityGroupId int NOT NULL CONSTRAINT PK_Opt016_EntityGroup PRIMARY KEY,
    GroupCode char(4) NOT NULL CONSTRAINT UQ_Opt016_EntityGroup_GroupCode UNIQUE
);

CREATE TABLE lab.WorkItemDetail
(
    WorkItemDetailId int NOT NULL CONSTRAINT PK_WorkItemDetail PRIMARY KEY CLUSTERED,
    EntityGroupId int NOT NULL,
    SequenceNumber int NOT NULL,
    MeasureValue int NOT NULL,
    Payload char(60) NOT NULL,
    CONSTRAINT FK_WorkItemDetail_EntityGroup FOREIGN KEY(EntityGroupId) REFERENCES lab.EntityGroup(EntityGroupId)
);

CREATE TABLE lab.ProbeRequest
(
    ProbeRequestId int NOT NULL CONSTRAINT PK_ProbeRequest PRIMARY KEY CLUSTERED,
    ProfileCode char(1) NOT NULL,
    EntityGroupId int NOT NULL,
    CONSTRAINT CK_ProbeRequest_Profile CHECK(ProfileCode IN ('H', 'L')),
    CONSTRAINT FK_ProbeRequest_EntityGroup FOREIGN KEY(EntityGroupId) REFERENCES lab.EntityGroup(EntityGroupId)
);

CREATE TABLE lab.Opt016Evidence
(
    Phase varchar(20) NOT NULL CONSTRAINT PK_Opt016Evidence PRIMARY KEY,
    ProfileCode char(1) NOT NULL,
    ResultRowCount bigint NOT NULL,
    ResultChecksum int NULL,
    QueryHash binary(8) NULL,
    StatementSubTreeCost float NULL,
    NestedLoopsCount int NOT NULL,
    OuterReferenceCount int NOT NULL,
    SpoolCount int NOT NULL,
    FirstSpoolKind nvarchar(60) NULL,
    SpoolActualRebinds bigint NOT NULL,
    SpoolActualRewinds bigint NOT NULL,
    SpoolActualExecutions bigint NOT NULL,
    SpoolActualRows bigint NOT NULL,
    InnerAccessPhysicalOp nvarchar(60) NULL,
    LastLogicalReads bigint NULL,
    LastWorkerTimeUs bigint NULL,
    LastElapsedTimeUs bigint NULL,
    CapturedAtUtc datetime2(3) NOT NULL CONSTRAINT DF_Opt016Evidence_Captured DEFAULT SYSUTCDATETIME()
);

INSERT lab.EntityGroup(EntityGroupId, GroupCode)
SELECT v.EntityGroupId, CONVERT(char(4), CONCAT('G', RIGHT(CONCAT('000', v.EntityGroupId), 3)))
FROM
(
    VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10),
           (11),(12),(13),(14),(15),(16),(17),(18),(19),(20)
) v(EntityGroupId);

;WITH Digits AS
(
    SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) d(n)
), Numbers AS
(
    SELECT TOP (20000)
        n = 1 + d0.n + d1.n*10 + d2.n*100 + d3.n*1000 + d4.n*10000
    FROM Digits d0 CROSS JOIN Digits d1 CROSS JOIN Digits d2
    CROSS JOIN Digits d3 CROSS JOIN Digits d4
    ORDER BY 1
)
INSERT lab.WorkItemDetail(WorkItemDetailId, EntityGroupId, SequenceNumber, MeasureValue, Payload)
SELECT n,
       1 + ((n - 1) % 20),
       1 + ((n - 1) / 20),
       n % 10000,
       CONVERT(char(60), REPLICATE(CHAR(65 + (n % 26)), 40) + RIGHT(REPLICATE('0', 20) + CONVERT(varchar(20), n), 20))
FROM Numbers
OPTION (MAXDOP 1);

;WITH Digits AS
(
    SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) d(n)
), Numbers AS
(
    SELECT TOP (5000)
        n = 1 + d0.n + d1.n*10 + d2.n*100 + d3.n*1000
    FROM Digits d0 CROSS JOIN Digits d1 CROSS JOIN Digits d2 CROSS JOIN Digits d3
    ORDER BY 1
)
INSERT lab.ProbeRequest(ProbeRequestId, ProfileCode, EntityGroupId)
SELECT n, 'H', 1 + ((n - 1) / 500)
FROM Numbers;

INSERT lab.ProbeRequest(ProbeRequestId, ProfileCode, EntityGroupId)
SELECT 5000 + EntityGroupId, 'L', EntityGroupId
FROM lab.EntityGroup;

CREATE INDEX IX_ProbeRequest_Profile_Group
ON lab.ProbeRequest(ProfileCode, EntityGroupId, ProbeRequestId);
CREATE INDEX IX_WorkItemDetail_Group_Sequence
ON lab.WorkItemDetail(EntityGroupId, SequenceNumber DESC, WorkItemDetailId DESC)
INCLUDE(MeasureValue);
UPDATE STATISTICS lab.ProbeRequest IX_ProbeRequest_Profile_Group WITH FULLSCAN;
UPDATE STATISTICS lab.WorkItemDetail IX_WorkItemDetail_Group_Sequence WITH FULLSCAN;

EXEC(N'
CREATE PROCEDURE lab.usp_Opt016Workload
    @ProfileCode char(1),
    @ResultRowCount bigint OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        @ResultRowCount = COUNT_BIG(*),
        @ResultChecksum = CHECKSUM_AGG(BINARY_CHECKSUM(pr.ProbeRequestId, detail.WorkItemDetailId, detail.MeasureValue))
    FROM lab.ProbeRequest AS pr
    CROSS APPLY
    (
        SELECT TOP (1) wd.WorkItemDetailId, wd.MeasureValue
        FROM lab.WorkItemDetail AS wd
        WHERE wd.EntityGroupId = pr.EntityGroupId
        ORDER BY wd.SequenceNumber DESC, wd.WorkItemDetailId DESC
    ) AS detail /*SQLPERF_OPT016_WORKLOAD*/
    WHERE pr.ProfileCode = @ProfileCode
    OPTION (MAXDOP 1, FORCE ORDER, LOOP JOIN);
END;
');

EXEC(N'
CREATE PROCEDURE lab.usp_Opt016Capture
    @Phase varchar(20),
    @ProfileCode char(1),
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
    DECLARE @NestedLoopsCount int = 0;
    DECLARE @OuterReferenceCount int = 0;
    DECLARE @SpoolCount int = 0;
    DECLARE @FirstSpoolKind nvarchar(60);
    DECLARE @SpoolActualRebinds bigint = 0;
    DECLARE @SpoolActualRewinds bigint = 0;
    DECLARE @SpoolActualExecutions bigint = 0;
    DECLARE @SpoolActualRows bigint = 0;
    DECLARE @InnerAccessPhysicalOp nvarchar(60);

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
            SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1,
                CASE WHEN qs.statement_end_offset = -1
                     THEN (DATALENGTH(st.text) - qs.statement_start_offset) / 2 + 1
                     ELSE (qs.statement_end_offset - qs.statement_start_offset) / 2 + 1 END)
        )
    ) AS statement_text(value)
    WHERE statement_text.value LIKE ''%SQLPERF_OPT016_WORKLOAD%''
    ORDER BY qs.last_execution_time DESC;

    IF @Plan IS NULL
        THROW 51005, ''FAIL_EVIDENCE: Der letzte Actual Plan für OPT-016 ist nicht verfügbar.'', 1;

    ;WITH XMLNAMESPACES(DEFAULT ''http://schemas.microsoft.com/sqlserver/2004/07/showplan'')
    SELECT TOP (1)
        @StatementSubTreeCost = stmt.node.value(''@StatementSubTreeCost'', ''float''),
        @NestedLoopsCount = stmt.node.value(''count(.//RelOp[@PhysicalOp="Nested Loops"])'', ''int''),
        @OuterReferenceCount = stmt.node.value(''count(.//NestedLoops/OuterReferences/ColumnReference)'', ''int''),
        @SpoolCount = stmt.node.value(''count(.//RelOp[@PhysicalOp="Index Spool" or @PhysicalOp="Table Spool"])'', ''int'')
    FROM @Plan.nodes(''//StmtSimple'') AS stmt(node)
    WHERE stmt.node.value(''@StatementText'', ''nvarchar(4000)'') LIKE ''%SQLPERF_OPT016_WORKLOAD%'';

    ;WITH XMLNAMESPACES(DEFAULT ''http://schemas.microsoft.com/sqlserver/2004/07/showplan'')
    SELECT TOP (1) @FirstSpoolKind = rel.node.value(''@PhysicalOp'', ''nvarchar(60)'')
    FROM @Plan.nodes(''//StmtSimple'') AS stmt(node)
    CROSS APPLY stmt.node.nodes(''.//RelOp[@PhysicalOp="Index Spool" or @PhysicalOp="Table Spool"]'') AS rel(node)
    WHERE stmt.node.value(''@StatementText'', ''nvarchar(4000)'') LIKE ''%SQLPERF_OPT016_WORKLOAD%''
    ORDER BY rel.node.value(''@NodeId'', ''int'');

    ;WITH XMLNAMESPACES(DEFAULT ''http://schemas.microsoft.com/sqlserver/2004/07/showplan'')
    SELECT
        @SpoolActualRebinds = COALESCE(SUM(CASE WHEN rt.node.exist(''@ActualRebinds'') = 1 THEN rt.node.value(''@ActualRebinds'', ''bigint'') ELSE 0 END), 0),
        @SpoolActualRewinds = COALESCE(SUM(CASE WHEN rt.node.exist(''@ActualRewinds'') = 1 THEN rt.node.value(''@ActualRewinds'', ''bigint'') ELSE 0 END), 0),
        @SpoolActualExecutions = COALESCE(SUM(CASE WHEN rt.node.exist(''@ActualExecutions'') = 1 THEN rt.node.value(''@ActualExecutions'', ''bigint'') ELSE 0 END), 0),
        @SpoolActualRows = COALESCE(SUM(CASE WHEN rt.node.exist(''@ActualRows'') = 1 THEN rt.node.value(''@ActualRows'', ''bigint'') ELSE 0 END), 0)
    FROM @Plan.nodes(''//StmtSimple'') AS stmt(node)
    CROSS APPLY stmt.node.nodes(''.//RelOp[@PhysicalOp="Index Spool" or @PhysicalOp="Table Spool"]/RunTimeInformation/RunTimeCountersPerThread'') AS rt(node)
    WHERE stmt.node.value(''@StatementText'', ''nvarchar(4000)'') LIKE ''%SQLPERF_OPT016_WORKLOAD%'';

    ;WITH XMLNAMESPACES(DEFAULT ''http://schemas.microsoft.com/sqlserver/2004/07/showplan'')
    SELECT TOP (1) @InnerAccessPhysicalOp = rel.node.value(''@PhysicalOp'', ''nvarchar(60)'')
    FROM @Plan.nodes(''//StmtSimple'') AS stmt(node)
    CROSS APPLY stmt.node.nodes(''.//RelOp'') AS rel(node)
    WHERE stmt.node.value(''@StatementText'', ''nvarchar(4000)'') LIKE ''%SQLPERF_OPT016_WORKLOAD%''
      AND rel.node.exist(''.//Object[contains(@Table, "WorkItemDetail")]'') = 1
      AND rel.node.value(''@PhysicalOp'', ''nvarchar(60)'') NOT IN (N''Index Spool'', N''Table Spool'')
    ORDER BY rel.node.value(''@NodeId'', ''int'') DESC;

    DELETE lab.Opt016Evidence WHERE Phase = @Phase;
    INSERT lab.Opt016Evidence
    (
        Phase, ProfileCode, ResultRowCount, ResultChecksum, QueryHash, StatementSubTreeCost,
        NestedLoopsCount, OuterReferenceCount, SpoolCount, FirstSpoolKind,
        SpoolActualRebinds, SpoolActualRewinds, SpoolActualExecutions, SpoolActualRows,
        InnerAccessPhysicalOp, LastLogicalReads, LastWorkerTimeUs, LastElapsedTimeUs
    )
    VALUES
    (
        @Phase, @ProfileCode, @ResultRowCount, @ResultChecksum, @QueryHash, @StatementSubTreeCost,
        COALESCE(@NestedLoopsCount, 0), COALESCE(@OuterReferenceCount, 0), COALESCE(@SpoolCount, 0), @FirstSpoolKind,
        COALESCE(@SpoolActualRebinds, 0), COALESCE(@SpoolActualRewinds, 0),
        COALESCE(@SpoolActualExecutions, 0), COALESCE(@SpoolActualRows, 0),
        @InnerAccessPhysicalOp, @LastLogicalReads, @LastWorkerTimeUs, @LastElapsedTimeUs
    );
END;
');

IF (SELECT COUNT_BIG(*) FROM lab.WorkItemDetail) <> 20000
   OR (SELECT COUNT_BIG(*) FROM lab.ProbeRequest WHERE ProfileCode = 'H') <> 5000
   OR (SELECT COUNT_BIG(*) FROM lab.ProbeRequest WHERE ProfileCode = 'L') <> 20
    THROW 51003, 'FAIL_EXECUTION: OPT-016-Datenprofile sind unvollständig.', 1;

SELECT 1 AS Sequence, 'SETUP' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       N'20000 Detailzeilen; Profil H mit 5000 Anforderungen und 10 Schlüsseln; Profil L mit 20 eindeutigen Schlüsseln' AS ObservedValue,
       N'markierte Testdatenbank; passender Baseline-Index; normalisierte Actual-Plan-Evidenz' AS RequiredValue,
       N'OPT-016 wurde reproduzierbar aufgebaut.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
GO
