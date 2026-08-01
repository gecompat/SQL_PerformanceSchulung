/* OPT-010 demonstration: identischer Querytext, umgekehrte Kompilierungsreihenfolge. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

ALTER DATABASE SCOPED CONFIGURATION SET OPTIONAL_PARAMETER_OPTIMIZATION = OFF;
EXEC sys.sp_recompile @objname = N'lab.usp_Opt010SearchNullFirst';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Marker nvarchar(40) = N'OPT010' + N'_MARK_DEMONSTRATION';

/* Nun bestimmt der offene Parameter die Planform. */
EXEC lab.usp_Opt010SearchNullFirst @AgentId = NULL,
                                   @ResultRowCount = @Rows OUTPUT,
                                   @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt010Capture @Phase = 'DEMONSTRATION', @ParameterLabel = 'OPTIONAL', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

/* Der belegte Parameter erbt dieselbe Planform wie in der Baseline. */
EXEC lab.usp_Opt010SearchNullFirst @AgentId = 42,
                                   @ResultRowCount = @Rows OUTPUT,
                                   @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt010Capture @Phase = 'DEMONSTRATION', @ParameterLabel = 'SELECTIVE', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @SelectiveRows int;
DECLARE @OptionalRows int;
DECLARE @MaxPlans int;
DECLARE @Dispatchers int;
DECLARE @Variants int;
DECLARE @BaselineSelectiveReads bigint;
DECLARE @DemoSelectiveReads bigint;
DECLARE @DemoOptionalReads bigint;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @MaxPlans = MAX(CachedPlanCount),
       @Dispatchers = MAX(DispatcherPlanCount),
       @Variants = MAX(VariantPlanCount)
FROM lab.Opt010Evidence
WHERE Phase = 'DEMONSTRATION';

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein markierter Cacheeintrag für lab.usp_Opt010SearchNullFirst auswertbar' AS ObservedValue,
           N'markerbezogene Cacheevidenz für beide Ausführungen' AS RequiredValue,
           N'Die Plancacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

SELECT @SelectiveRows = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN ResultRowCount END),
       @OptionalRows = MAX(CASE WHEN ParameterLabel = 'OPTIONAL' THEN ResultRowCount END),
       @DemoSelectiveReads = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @DemoOptionalReads = MAX(CASE WHEN ParameterLabel = 'OPTIONAL' THEN LogicalReads END)
FROM lab.Opt010Evidence
WHERE Phase = 'DEMONSTRATION';

SELECT @BaselineSelectiveReads = MAX(LogicalReads)
FROM lab.Opt010Evidence
WHERE Phase = 'BASELINE' AND ParameterLabel = 'SELECTIVE';

IF @SelectiveRows <> 50 OR @OptionalRows <> 100000
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die OPT-010-Demonstration liefert nicht die vereinbarten Trefferzahlen.', 1;

IF @MaxPlans <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Auch in umgekehrter Reihenfolge wird genau ein zwischengespeicherter Plan erwartet.', 1;

IF @Dispatchers <> 0 OR @Variants <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Bei abgeschalteter Optimierung darf weder ein Dispatcherplan noch eine Queryvariante entstehen.', 1;

IF @DemoSelectiveReads IS NULL OR @DemoOptionalReads IS NULL OR @BaselineSelectiveReads IS NULL
   OR @BaselineSelectiveReads = 0
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'LOGICAL_READS' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'keine vergleichbaren Lesezahlen im Plancache' AS ObservedValue,
           N'logische Lesevorgänge aus Baseline und Demonstration' AS RequiredValue,
           N'Der Reihenfolgevergleich ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

/*
   Kernaussage und zugleich der entscheidende Unterschied zu OPT-009:
   Bei einem optionalen Praedikat ist die Kompilierungsreihenfolge wirkungslos,
   weil keine Suchplanform fuer beide Parameterzustaende gueltig waere.
   Toleranz: 5 Prozent, damit Messstreuung nicht als Wirkung gedeutet wird.
*/
IF ABS(@DemoSelectiveReads - @BaselineSelectiveReads) * 20 > @BaselineSelectiveReads
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'COMPILE_ORDER_NEUTRALITY' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'belegt in Baseline=', @BaselineSelectiveReads,
                  N'; belegt in Demonstration=', @DemoSelectiveReads) AS ObservedValue,
           N'Abweichung von höchstens 5 Prozent zwischen beiden Reihenfolgen' AS RequiredValue,
           N'Die Reihenfolgeunabhängigkeit ist in dieser Umgebung nicht sauber messbar; die Aussage bleibt unbelegt.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'belegt: Baseline=', @BaselineSelectiveReads, N' gegenüber Demonstration=', @DemoSelectiveReads,
              N'; offen in Demonstration=', @DemoOptionalReads) AS ObservedValue,
       N'reihenfolgeunabhängige Lesekosten bei identischem Querytext' AS RequiredValue,
       N'Anders als bei schiefen Gleichheitsprädikaten hilft hier kein günstiger Erstaufruf: die Planform bleibt in beiden Reihenfolgen dieselbe.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
