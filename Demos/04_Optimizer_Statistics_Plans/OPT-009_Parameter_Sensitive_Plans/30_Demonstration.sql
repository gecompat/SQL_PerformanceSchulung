/* OPT-009 demonstration: identischer Querytext, umgekehrte Kompilierungsreihenfolge. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

ALTER DATABASE SCOPED CONFIGURATION SET PARAMETER_SENSITIVE_PLAN_OPTIMIZATION = OFF;
EXEC sys.sp_recompile @objname = N'lab.usp_Opt009SearchCommonFirst';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Marker nvarchar(40) = N'OPT009' + N'_MARK_DEMONSTRATION';

/* Nun bestimmt der dominante Wert die Planform. */
EXEC lab.usp_Opt009SearchCommonFirst @OwnerId = 1,
                                     @ResultRowCount = @Rows OUTPUT,
                                     @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt009Capture @Phase = 'DEMONSTRATION', @ParameterLabel = 'COMMON', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

/* Der selektive Wert erbt die für ihn unpassende Planform. */
EXEC lab.usp_Opt009SearchCommonFirst @OwnerId = 2,
                                     @ResultRowCount = @Rows OUTPUT,
                                     @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt009Capture @Phase = 'DEMONSTRATION', @ParameterLabel = 'SELECTIVE', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @SelectiveRows int;
DECLARE @CommonRows int;
DECLARE @MaxPlans int;
DECLARE @Dispatchers int;
DECLARE @Variants int;
DECLARE @BaselineSelectiveReads bigint;
DECLARE @DemoSelectiveReads bigint;
DECLARE @DemoCommonReads bigint;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @MaxPlans = MAX(CachedPlanCount),
       @Dispatchers = MAX(DispatcherPlanCount),
       @Variants = MAX(VariantPlanCount)
FROM lab.Opt009Evidence
WHERE Phase = 'DEMONSTRATION';

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein markierter Cacheeintrag für lab.usp_Opt009SearchCommonFirst auswertbar' AS ObservedValue,
           N'markerbezogene Cacheevidenz für beide Ausführungen' AS RequiredValue,
           N'Die Plancacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

SELECT @SelectiveRows = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN ResultRowCount END),
       @CommonRows = MAX(CASE WHEN ParameterLabel = 'COMMON' THEN ResultRowCount END),
       @DemoSelectiveReads = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @DemoCommonReads = MAX(CASE WHEN ParameterLabel = 'COMMON' THEN LogicalReads END)
FROM lab.Opt009Evidence
WHERE Phase = 'DEMONSTRATION';

SELECT @BaselineSelectiveReads = MAX(LogicalReads)
FROM lab.Opt009Evidence
WHERE Phase = 'BASELINE' AND ParameterLabel = 'SELECTIVE';

IF @SelectiveRows <> 5 OR @CommonRows <> 99000
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die OPT-009-Demonstration liefert nicht die vereinbarten Trefferzahlen.', 1;

IF @MaxPlans <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Auch in umgekehrter Reihenfolge wird genau ein zwischengespeicherter Plan erwartet.', 1;

IF @Dispatchers <> 0 OR @Variants <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Bei abgeschalteter Optimierung darf weder ein Dispatcherplan noch eine Queryvariante entstehen.', 1;

IF @DemoSelectiveReads IS NULL OR @DemoCommonReads IS NULL OR @BaselineSelectiveReads IS NULL
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'LOGICAL_READS' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'keine vergleichbaren Lesezahlen im Plancache' AS ObservedValue,
           N'logische Lesevorgänge aus Baseline und Demonstration' AS RequiredValue,
           N'Der Reihenfolgevergleich ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

/* Kernaussage: derselbe Parameterwert kostet je nach Kompilierungsreihenfolge unterschiedlich viel. */
IF @DemoSelectiveReads <= @BaselineSelectiveReads
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'COMPILE_ORDER_EFFECT' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'selektiv in Baseline=', @BaselineSelectiveReads,
                  N'; selektiv in Demonstration=', @DemoSelectiveReads) AS ObservedValue,
           N'höhere Lesekosten für den selektiven Wert bei umgekehrter Reihenfolge' AS RequiredValue,
           N'Die Reihenfolgeabhängigkeit ist in dieser Umgebung nicht messbar; die Aussage bleibt unbelegt.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'selektiv: Baseline=', @BaselineSelectiveReads, N' gegenüber Demonstration=', @DemoSelectiveReads,
              N'; dominant in Demonstration=', @DemoCommonReads) AS ObservedValue,
       N'reihenfolgeabhängige Lesekosten bei identischem Querytext' AS RequiredValue,
       N'Ohne Parametersensitivität bleibt nur eine Planform je Querytext; die Reihenfolge entscheidet, welcher Wert benachteiligt wird.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
