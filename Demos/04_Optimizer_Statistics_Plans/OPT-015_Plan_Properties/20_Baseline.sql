/* OPT-015 baseline: known group represented by the current histogram. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Rows bigint;
DECLARE @Checksum int;

EXEC sys.sp_recompile N'lab.usp_Opt015Workload';
EXEC lab.usp_Opt015Workload
    @EntityGroupId = 5,
    @ResultRowCount = @Rows OUTPUT,
    @ResultChecksum = @Checksum OUTPUT;

EXEC lab.usp_Opt015Capture
    @Phase = 'BASELINE',
    @RequestedGroupId = 5,
    @ResultRowCount = @Rows,
    @ResultChecksum = @Checksum;

DECLARE @Estimate float;
DECLARE @Actual bigint;
DECLARE @RowsRead bigint;
DECLARE @Executions bigint;
DECLARE @Stats int;
DECLARE @QueryHash binary(8);

SELECT
    @Estimate = AccessEstimateRows,
    @Actual = AccessActualRows,
    @RowsRead = AccessActualRowsRead,
    @Executions = AccessExecutions,
    @Stats = StatisticsUsageCount,
    @QueryHash = QueryHash
FROM lab.Opt015Evidence
WHERE Phase = 'BASELINE';

IF @Rows <> 10000 OR @Checksum IS NULL OR @Actual <> 10000
   OR @Estimate NOT BETWEEN 5000 AND 20000
   OR @RowsRead < @Actual OR @Executions < 1 OR @Stats < 1 OR @QueryHash IS NULL
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die OPT-015-Baseline besitzt keine plausible und vollständige Planevidenz.', 1;

SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Rows=', @Rows, N'; Estimate=', CONVERT(decimal(18,2), @Estimate),
              N'; ActualRowsRead=', @RowsRead, N'; StatisticsUsage=', @Stats) AS ObservedValue,
       N'10000 Zeilen; Schätzung derselben Größenordnung; Actual Rows, Rows Read, Executions, Query Hash und Statistics Usage vorhanden' AS RequiredValue,
       N'Die statistisch repräsentierte Baseline ist erfasst.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
