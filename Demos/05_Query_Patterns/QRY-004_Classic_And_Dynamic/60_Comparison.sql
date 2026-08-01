/* QRY-004 comparison: Strategien nebeneinander bewerten und Ergebnisvertrag abschließen. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Rows int;
DECLARE @Checksum int;

EXEC lab.usp_Qry004CatchAll @CategoryCode = 'RARE',
                            @ResultRowCount = @Rows OUTPUT,
                            @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'COMPARISON', @Strategy = 'CATCHALL', @Combination = 'RARE',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @ComparisonRows int;
DECLARE @ComparisonPlans int;
DECLARE @BaselineChecksum int;
DECLARE @ComparisonChecksum int;
DECLARE @Mismatch int;
DECLARE @DynamicForms int;

SELECT @ComparisonRows = ResultRowCount,
       @ComparisonPlans = CachedPlanCount,
       @ComparisonChecksum = ResultChecksum
FROM lab.Qry004Evidence
WHERE Phase = 'COMPARISON' AND Strategy = 'CATCHALL' AND Combination = 'RARE';

SELECT @BaselineChecksum = ResultChecksum
FROM lab.Qry004Evidence
WHERE Phase = 'BASELINE' AND Strategy = 'CATCHALL' AND Combination = 'RARE';

IF @ComparisonRows <> 20 OR ISNULL(@ComparisonChecksum, -1) <> ISNULL(@BaselineChecksum, -1)
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die abschließende Catch-all-Ausführung weicht von der Baseline ab.', 1;

IF @ComparisonPlans <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der Catch-all-Querytext muss weiterhin genau einen Plan wiederverwenden.', 1;

SELECT @Mismatch = COUNT(*)
FROM lab.Qry004Evidence AS recompiled
INNER JOIN lab.Qry004Evidence AS dynamic_sql
        ON dynamic_sql.Phase = 'MITIGATION'
       AND dynamic_sql.Strategy = 'DYNAMIC'
       AND dynamic_sql.Combination = recompiled.Combination
WHERE recompiled.Phase = 'DEMONSTRATION'
  AND recompiled.Strategy = 'RECOMPILE'
  AND (recompiled.ResultRowCount <> dynamic_sql.ResultRowCount
       OR ISNULL(recompiled.ResultChecksum, -1) <> ISNULL(dynamic_sql.ResultChecksum, -1));

IF @Mismatch IS NULL OR @Mismatch > 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Recompile-Variante und dynamisches SQL sind nicht ergebnisgleich.', 1;

SELECT @DynamicForms = MAX(CachedPlanCount)
FROM lab.Qry004Evidence
WHERE Phase = 'MITIGATION' AND Strategy = 'DYNAMIC';

IF @DynamicForms <> 2
    THROW 51006, 'FAIL_RESULT_CONTRACT: Das dynamische SQL muss auf zwei Statementformen begrenzt bleiben.', 1;

SELECT 1 AS Sequence, 'COMPARISON' AS Phase, 'STRATEGY_COMPARISON' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Strategie=', Strategy, N'; Kombination=', Combination,
              N'; Zeilen=', ResultRowCount,
              N'; Reads=', ISNULL(LogicalReads, -1),
              N'; Planformen=', CachedPlanCount) AS ObservedValue,
       N'gleiches Ergebnis je Kombination über alle Strategien' AS RequiredValue,
       N'Strategievergleich unter identischer Datenverteilung.' AS Message
FROM lab.Qry004Evidence
WHERE Phase IN ('BASELINE', 'DEMONSTRATION', 'MITIGATION');

SELECT 2 AS Sequence, 'COMPARISON' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Catch-all Planformen=', @ComparisonPlans,
              N'; dynamische Statementformen=', @DynamicForms,
              N'; Ergebnisgleichheit ueber drei Strategien=ja') AS ObservedValue,
       N'eine Catch-all-Planform, zwei dynamische Statementformen, durchgängige Ergebnisgleichheit' AS RequiredValue,
       N'Die Strategiewahl folgt Verteilung, Wiederverwendung und Sicherheit, nicht einer allgemeinen Rangfolge.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
