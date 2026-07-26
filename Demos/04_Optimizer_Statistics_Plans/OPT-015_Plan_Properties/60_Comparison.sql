/* OPT-015 comparison: rerun the same out-of-range group after the targeted statistics refresh. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Rows bigint;
DECLARE @Checksum int;

EXEC lab.usp_Opt015Workload
    @EntityGroupId = 999,
    @ResultRowCount = @Rows OUTPUT,
    @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt015Capture
    @Phase = 'COMPARISON',
    @RequestedGroupId = 999,
    @ResultRowCount = @Rows,
    @ResultChecksum = @Checksum;

DECLARE @ProblemChecksum int;
DECLARE @ProblemEstimate float;
DECLARE @ProblemActual bigint;
DECLARE @ComparisonEstimate float;
DECLARE @ComparisonActual bigint;
DECLARE @ComparisonRowsRead bigint;
DECLARE @ComparisonStats int;

SELECT @ProblemChecksum = ResultChecksum, @ProblemEstimate = AccessEstimateRows, @ProblemActual = AccessActualRows
FROM lab.Opt015Evidence WHERE Phase = 'PROBLEM';
SELECT @ComparisonEstimate = AccessEstimateRows, @ComparisonActual = AccessActualRows,
       @ComparisonRowsRead = AccessActualRowsRead, @ComparisonStats = StatisticsUsageCount
FROM lab.Opt015Evidence WHERE Phase = 'COMPARISON';

IF @Rows <> 60000 OR @Checksum IS NULL OR @Checksum <> @ProblemChecksum
   OR @ComparisonActual <> 60000
   OR @ComparisonEstimate NOT BETWEEN 30000 AND 120000
   OR ABS(@ComparisonEstimate - @ComparisonActual) >= ABS(@ProblemEstimate - @ProblemActual)
   OR @ComparisonRowsRead < @ComparisonActual OR @ComparisonStats < 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der OPT-015-Vergleich verbessert den Schätzfehler bei identischer Ergebnismenge nicht belastbar.', 1;

SELECT Phase, RequestedGroupId, ResultRowCount, ResultChecksum,
       AccessPhysicalOp, AccessLogicalOp, AccessEstimateRows, AccessActualRows,
       AccessActualRowsRead, AccessExecutions, StatisticsUsageCount,
       FirstStatisticsName, LastLogicalReads, LastWorkerTimeUs, LastElapsedTimeUs
FROM lab.Opt015Evidence
WHERE Phase IN ('PROBLEM', 'COMPARISON')
ORDER BY CASE Phase WHEN 'PROBLEM' THEN 1 ELSE 2 END;

SELECT 1 AS Sequence, 'COMPARISON' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Rows=', @Rows, N'; ProblemEstimate=', CONVERT(decimal(18,2), @ProblemEstimate),
              N'; ComparisonEstimate=', CONVERT(decimal(18,2), @ComparisonEstimate), N'; Checksum=', @Checksum) AS ObservedValue,
       N'identische 60000-Zeilen-Ergebnismenge; kleinerer absoluter Schätzfehler; vollständige Planevidenz' AS RequiredValue,
       N'Die gezielte Statistikaktualisierung verbessert die Kardinalitätsevidenz.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
