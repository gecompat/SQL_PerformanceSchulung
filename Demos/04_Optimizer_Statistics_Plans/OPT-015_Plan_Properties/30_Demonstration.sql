/* OPT-015 demonstration: append an out-of-range group while the index statistic remains unchanged. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF EXISTS (SELECT 1 FROM lab.WorkItem WHERE EntityGroupId = 999)
    THROW 51003, 'FAIL_STATE: Die OPT-015-Problemzeilen sind bereits vorhanden.', 1;

;WITH Digits AS
(
    SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) d(n)
), Numbers AS
(
    SELECT TOP (60000)
        n = 200000 + 1 + d0.n + d1.n*10 + d2.n*100 + d3.n*1000 + d4.n*10000
    FROM Digits d0 CROSS JOIN Digits d1 CROSS JOIN Digits d2
    CROSS JOIN Digits d3 CROSS JOIN Digits d4
    ORDER BY 1
)
INSERT lab.WorkItem(WorkItemId, EntityGroupId, StatusCode, EventTime, MeasureValue, Payload)
SELECT n,
       999,
       CONVERT(tinyint, n % 5),
       DATEADD(minute, CONVERT(int, (CONVERT(bigint, n) * 41) % 1051200), CONVERT(datetime2(0), '20240101')),
       n % 10000,
       CONVERT(char(80), REPLICATE(CHAR(65 + (n % 26)), 60) + RIGHT(REPLICATE('0', 20) + CONVERT(varchar(20), n), 20))
FROM Numbers
OPTION (MAXDOP 1);

IF (SELECT COUNT_BIG(*) FROM lab.WorkItem WHERE EntityGroupId = 999) <> 60000
    THROW 51003, 'FAIL_EXECUTION: Die OPT-015-Problemverteilung ist unvollständig.', 1;

DECLARE @Rows bigint;
DECLARE @Checksum int;

EXEC sys.sp_recompile N'lab.usp_Opt015Workload';
EXEC lab.usp_Opt015Workload
    @EntityGroupId = 999,
    @ResultRowCount = @Rows OUTPUT,
    @ResultChecksum = @Checksum OUTPUT;

EXEC lab.usp_Opt015Capture
    @Phase = 'PROBLEM',
    @RequestedGroupId = 999,
    @ResultRowCount = @Rows,
    @ResultChecksum = @Checksum;

DECLARE @Estimate float;
DECLARE @Actual bigint;
DECLARE @RowsRead bigint;
DECLARE @Stats int;
DECLARE @QueryHash binary(8);

SELECT
    @Estimate = AccessEstimateRows,
    @Actual = AccessActualRows,
    @RowsRead = AccessActualRowsRead,
    @Stats = StatisticsUsageCount,
    @QueryHash = QueryHash
FROM lab.Opt015Evidence
WHERE Phase = 'PROBLEM';

IF @Rows <> 60000 OR @Checksum IS NULL OR @Actual <> 60000
   OR @Estimate IS NULL OR @Estimate >= 30000
   OR @RowsRead < @Actual OR @Stats < 1 OR @QueryHash IS NULL
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der OPT-015-Problemzustand zeigt keinen belastbaren Out-of-range-Schätzfehler.', 1;

SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Rows=', @Rows, N'; Estimate=', CONVERT(decimal(18,2), @Estimate),
              N'; ActualRowsRead=', @RowsRead, N'; StatisticsUsage=', @Stats) AS ObservedValue,
       N'60000 neue Gruppenzeilen; Access Estimate kleiner als 30000; vollständige Runtime-Evidenz' AS RequiredValue,
       N'Die unveränderte Statistik bildet die neue Gruppe noch nicht angemessen ab.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
