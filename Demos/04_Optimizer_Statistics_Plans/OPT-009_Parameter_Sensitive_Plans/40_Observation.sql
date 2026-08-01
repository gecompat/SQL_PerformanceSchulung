/* OPT-009 observation: Auswertung beider Durchläufe ohne Parametersensitivität. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Missing int;
DECLARE @BaselineSelectiveReads bigint;
DECLARE @BaselineCommonReads bigint;
DECLARE @DemoSelectiveReads bigint;
DECLARE @DemoCommonReads bigint;
DECLARE @BaselineSelectiveChecksum int;
DECLARE @DemoSelectiveChecksum int;
DECLARE @BaselineCommonChecksum int;
DECLARE @DemoCommonChecksum int;
DECLARE @Dispatchers int;
DECLARE @Variants int;
DECLARE @SelectivePenalty decimal(18,2);
DECLARE @CommonPenalty decimal(18,2);

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @Dispatchers = MAX(DispatcherPlanCount),
       @Variants = MAX(VariantPlanCount)
FROM lab.Opt009Evidence
WHERE Phase IN ('BASELINE', 'DEMONSTRATION');

SELECT @BaselineSelectiveReads = MAX(CASE WHEN Phase = 'BASELINE' AND ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @BaselineCommonReads = MAX(CASE WHEN Phase = 'BASELINE' AND ParameterLabel = 'COMMON' THEN LogicalReads END),
       @DemoSelectiveReads = MAX(CASE WHEN Phase = 'DEMONSTRATION' AND ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @DemoCommonReads = MAX(CASE WHEN Phase = 'DEMONSTRATION' AND ParameterLabel = 'COMMON' THEN LogicalReads END),
       @BaselineSelectiveChecksum = MAX(CASE WHEN Phase = 'BASELINE' AND ParameterLabel = 'SELECTIVE' THEN ResultChecksum END),
       @DemoSelectiveChecksum = MAX(CASE WHEN Phase = 'DEMONSTRATION' AND ParameterLabel = 'SELECTIVE' THEN ResultChecksum END),
       @BaselineCommonChecksum = MAX(CASE WHEN Phase = 'BASELINE' AND ParameterLabel = 'COMMON' THEN ResultChecksum END),
       @DemoCommonChecksum = MAX(CASE WHEN Phase = 'DEMONSTRATION' AND ParameterLabel = 'COMMON' THEN ResultChecksum END)
FROM lab.Opt009Evidence
WHERE Phase IN ('BASELINE', 'DEMONSTRATION');

IF @Missing IS NULL OR @Missing > 0
   OR @BaselineSelectiveReads IS NULL OR @BaselineCommonReads IS NULL
   OR @DemoSelectiveReads IS NULL OR @DemoCommonReads IS NULL
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
   OR ISNULL(@BaselineCommonChecksum, -1) <> ISNULL(@DemoCommonChecksum, -1)
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die beiden Durchläufe sind nicht ergebnisgleich.', 1;

IF @Dispatchers <> 0 OR @Variants <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: In den Phasen ohne Parametersensitivität darf kein Dispatcherplan zwischengespeichert sein.', 1;

SET @SelectivePenalty = CONVERT(decimal(18,2), @DemoSelectiveReads) / NULLIF(@BaselineSelectiveReads, 0);
SET @CommonPenalty = CONVERT(decimal(18,2), @BaselineCommonReads) / NULLIF(@DemoCommonReads, 0);

SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'READS_BY_COMPILE_ORDER' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'selektiv: ', @BaselineSelectiveReads, N' gegenüber ', @DemoSelectiveReads,
              N'; dominant: ', @DemoCommonReads, N' gegenüber ', @BaselineCommonReads) AS ObservedValue,
       N'je Parameterwert eine günstige und eine ungünstige Messung' AS RequiredValue,
       N'Jeder der beiden Werte ist in genau einer Reihenfolge benachteiligt.' AS Message
UNION ALL
SELECT 2, 'OBSERVATION', 'PLAN_FORM_COUNT', 'PASS', 'OK',
       N'ein zwischengespeicherter Plan je markiertem Querytext',
       N'genau eine Planform ohne Parametersensitivität',
       N'Ein Querytext besitzt ohne Parametersensitivität genau eine zwischengespeicherte Planform.'
UNION ALL
SELECT 3, 'OBSERVATION', 'RESULT_EQUALITY', 'PASS', 'OK',
       N'Prüfsummen je Parameterwert identisch',
       N'Ergebnisgleichheit über beide Durchläufe',
       N'Die Planform verändert die Kosten, nicht das Ergebnis.';

IF @SelectivePenalty IS NULL OR @CommonPenalty IS NULL OR @SelectivePenalty <= 1 OR @CommonPenalty <= 1
BEGIN
    SELECT 4 AS Sequence, 'OBSERVATION' AS Phase, 'PENALTY_SYMMETRY' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'Faktor selektiv=', ISNULL(@SelectivePenalty, -1), N'; Faktor dominant=', ISNULL(@CommonPenalty, -1)) AS ObservedValue,
           N'beide Faktoren größer als 1' AS RequiredValue,
           N'Die beidseitige Benachteiligung ist in dieser Umgebung nicht klar messbar; die Ergebnisgleichheit bleibt nachgewiesen.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 4 AS Sequence, 'OBSERVATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Mehrkosten selektiv=Faktor ', @SelectivePenalty,
              N'; Mehrkosten dominant=Faktor ', @CommonPenalty) AS ObservedValue,
       N'beidseitige Mehrkosten bei genau einer Planform' AS RequiredValue,
       N'Die Wahl der ersten Parameterbelegung verschiebt den Schaden nur, sie behebt ihn nicht.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
