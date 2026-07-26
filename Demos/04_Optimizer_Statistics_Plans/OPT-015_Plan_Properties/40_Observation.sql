/* OPT-015 observation: expose normalized statement and operator evidence without persisting plan XML. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF NOT EXISTS (SELECT 1 FROM lab.Opt015Evidence WHERE Phase = 'BASELINE')
   OR NOT EXISTS (SELECT 1 FROM lab.Opt015Evidence WHERE Phase = 'PROBLEM')
    THROW 51003, 'FAIL_STATE: OPT-015 benötigt Baseline- und Problem-Evidenz.', 1;

SELECT
    Phase, RequestedGroupId, ResultRowCount, ResultChecksum,
    QueryHashHex = CONVERT(varchar(18), QueryHash, 1),
    StatementSubTreeCost, StatementEstimateRows,
    AccessPhysicalOp, AccessLogicalOp, AccessEstimateRows,
    AccessActualRows, AccessActualRowsRead, AccessExecutions,
    StatisticsUsageCount, FirstStatisticsName, WarningCount,
    LastLogicalReads, LastWorkerTimeUs, LastElapsedTimeUs
FROM lab.Opt015Evidence
WHERE Phase IN ('BASELINE', 'PROBLEM')
ORDER BY CASE Phase WHEN 'BASELINE' THEN 1 ELSE 2 END;

DECLARE @BaselineActual bigint;
DECLARE @BaselineEstimate float;
DECLARE @ProblemActual bigint;
DECLARE @ProblemEstimate float;

SELECT @BaselineActual = AccessActualRows, @BaselineEstimate = AccessEstimateRows
FROM lab.Opt015Evidence WHERE Phase = 'BASELINE';
SELECT @ProblemActual = AccessActualRows, @ProblemEstimate = AccessEstimateRows
FROM lab.Opt015Evidence WHERE Phase = 'PROBLEM';

IF @BaselineActual <> 10000 OR @ProblemActual <> 60000
   OR @BaselineEstimate IS NULL OR @ProblemEstimate IS NULL
   OR ABS(@ProblemEstimate - @ProblemActual) <= ABS(@BaselineEstimate - @BaselineActual)
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der Problemzustand besitzt nicht den erwarteten größeren absoluten Schätzfehler.', 1;

SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'BaselineError=', CONVERT(decimal(18,2), ABS(@BaselineEstimate - @BaselineActual)),
              N'; ProblemError=', CONVERT(decimal(18,2), ABS(@ProblemEstimate - @ProblemActual))) AS ObservedValue,
       N'Problemzustand mit größerem absolutem Operator-Schätzfehler; Statistics Usage und Laufzeitwerte sichtbar' AS RequiredValue,
       N'Planweite und operatorbezogene Evidenz sind getrennt lesbar.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
