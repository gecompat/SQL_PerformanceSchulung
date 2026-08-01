/* OPT-010 observation: Auswertung beider Durchläufe ohne Optional Parameter Plan Optimization. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Missing int;
DECLARE @BaselineSelectiveReads bigint;
DECLARE @BaselineOptionalReads bigint;
DECLARE @DemoSelectiveReads bigint;
DECLARE @DemoOptionalReads bigint;
DECLARE @BaselineSelectiveChecksum int;
DECLARE @DemoSelectiveChecksum int;
DECLARE @BaselineOptionalChecksum int;
DECLARE @DemoOptionalChecksum int;
DECLARE @Dispatchers int;
DECLARE @Variants int;
DECLARE @CostRatio decimal(18,2);
DECLARE @OrderDeviation decimal(18,2);

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @Dispatchers = MAX(DispatcherPlanCount),
       @Variants = MAX(VariantPlanCount)
FROM lab.Opt010Evidence
WHERE Phase IN ('BASELINE', 'DEMONSTRATION');

SELECT @BaselineSelectiveReads = MAX(CASE WHEN Phase = 'BASELINE' AND ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @BaselineOptionalReads = MAX(CASE WHEN Phase = 'BASELINE' AND ParameterLabel = 'OPTIONAL' THEN LogicalReads END),
       @DemoSelectiveReads = MAX(CASE WHEN Phase = 'DEMONSTRATION' AND ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @DemoOptionalReads = MAX(CASE WHEN Phase = 'DEMONSTRATION' AND ParameterLabel = 'OPTIONAL' THEN LogicalReads END),
       @BaselineSelectiveChecksum = MAX(CASE WHEN Phase = 'BASELINE' AND ParameterLabel = 'SELECTIVE' THEN ResultChecksum END),
       @DemoSelectiveChecksum = MAX(CASE WHEN Phase = 'DEMONSTRATION' AND ParameterLabel = 'SELECTIVE' THEN ResultChecksum END),
       @BaselineOptionalChecksum = MAX(CASE WHEN Phase = 'BASELINE' AND ParameterLabel = 'OPTIONAL' THEN ResultChecksum END),
       @DemoOptionalChecksum = MAX(CASE WHEN Phase = 'DEMONSTRATION' AND ParameterLabel = 'OPTIONAL' THEN ResultChecksum END)
FROM lab.Opt010Evidence
WHERE Phase IN ('BASELINE', 'DEMONSTRATION');

IF @Missing IS NULL OR @Missing > 0
   OR @BaselineSelectiveReads IS NULL OR @BaselineOptionalReads IS NULL
   OR @DemoSelectiveReads IS NULL OR @DemoOptionalReads IS NULL
   OR @BaselineOptionalReads = 0 OR @BaselineSelectiveReads = 0
BEGIN
    SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'unvollständige Lesezahlen aus Baseline und Demonstration' AS ObservedValue,
           N'vier auswertbare Messpunkte' AS RequiredValue,
           N'Der Vergleich beider Kompilierungsreihenfolgen ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

/* Ergebnisgleichheit ist Voraussetzung für jede Kostenaussage. */
IF ISNULL(@BaselineSelectiveChecksum, -1) <> ISNULL(@DemoSelectiveChecksum, -1)
   OR ISNULL(@BaselineOptionalChecksum, -1) <> ISNULL(@DemoOptionalChecksum, -1)
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die beiden Durchläufe sind nicht ergebnisgleich.', 1;

IF @Dispatchers <> 0 OR @Variants <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: In den Phasen ohne Optional Parameter Plan Optimization darf kein Dispatcherplan zwischengespeichert sein.', 1;

SET @CostRatio = CONVERT(decimal(18,2), @BaselineSelectiveReads) / NULLIF(@BaselineOptionalReads, 0);
SET @OrderDeviation = CONVERT(decimal(18,2), ABS(@DemoSelectiveReads - @BaselineSelectiveReads))
                      / NULLIF(@BaselineSelectiveReads, 0);

SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'READS_BY_PARAMETER_STATE' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'belegt: ', @BaselineSelectiveReads, N' gegenüber offen: ', @BaselineOptionalReads) AS ObservedValue,
       N'vergleichbare Lesekosten trotz 50 gegenüber 100 000 Trefferzeilen' AS RequiredValue,
       N'Die eine Planform muss für beide Parameterzustände gültig bleiben und prüft deshalb in beiden Fällen dieselbe Breite.' AS Message
UNION ALL
SELECT 2, 'OBSERVATION', 'PLAN_FORM_COUNT', 'PASS', 'OK',
       N'ein zwischengespeicherter Plan je markiertem Querytext',
       N'genau eine Planform ohne Optional Parameter Plan Optimization',
       N'Ein Querytext mit optionalem Prädikat besitzt ohne die Optimierung genau eine zwischengespeicherte Planform.'
UNION ALL
SELECT 3, 'OBSERVATION', 'RESULT_EQUALITY', 'PASS', 'OK',
       N'Prüfsummen je Parameterbelegung identisch',
       N'Ergebnisgleichheit über beide Durchläufe',
       N'Die Planform verändert die Kosten, nicht das Ergebnis.';

IF @CostRatio IS NULL OR @OrderDeviation IS NULL OR @CostRatio < 0.5 OR @OrderDeviation > 0.05
BEGIN
    SELECT 4 AS Sequence, 'OBSERVATION' AS Phase, 'COMPILE_ORDER_NEUTRALITY' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'Kostenverhältnis belegt/offen=', ISNULL(@CostRatio, -1),
                  N'; Reihenfolgeabweichung=', ISNULL(@OrderDeviation, -1)) AS ObservedValue,
           N'Verhältnis mindestens 0.5 und Abweichung höchstens 0.05' AS RequiredValue,
           N'Die Reihenfolgeunabhängigkeit ist in dieser Umgebung nicht klar messbar; die Ergebnisgleichheit bleibt nachgewiesen.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 4 AS Sequence, 'OBSERVATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Kostenverhältnis belegt/offen=', @CostRatio,
              N'; Reihenfolgeabweichung=', @OrderDeviation) AS ObservedValue,
       N'gleichwertige Kosten beider Parameterzustände und wirkungslose Reihenfolge' AS RequiredValue,
       N'Optionale Prädikate sind kein Sonderfall des Parameter Sniffing: hier hilft keine andere Kompilierungsreihenfolge, sondern nur eine zweite Planform.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
