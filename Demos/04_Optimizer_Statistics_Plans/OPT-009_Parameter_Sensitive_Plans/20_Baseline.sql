/* OPT-009 baseline: PSP abgeschaltet, der selektive Wert erzeugt den zwischengespeicherten Plan. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

ALTER DATABASE SCOPED CONFIGURATION SET PARAMETER_SENSITIVE_PLAN_OPTIMIZATION = OFF;
EXEC sys.sp_recompile @objname = N'lab.usp_Opt009SearchSelectiveFirst';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Marker nvarchar(40) = N'OPT009' + N'_MARK_BASELINE';

/* Kompilierungsreihenfolge: der selektive Wert bestimmt die Planform. */
EXEC lab.usp_Opt009SearchSelectiveFirst @OwnerId = 2,
                                        @ResultRowCount = @Rows OUTPUT,
                                        @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt009Capture @Phase = 'BASELINE', @ParameterLabel = 'SELECTIVE', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

/* Derselbe zwischengespeicherte Plan wird für den dominanten Wert wiederverwendet. */
EXEC lab.usp_Opt009SearchSelectiveFirst @OwnerId = 1,
                                        @ResultRowCount = @Rows OUTPUT,
                                        @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt009Capture @Phase = 'BASELINE', @ParameterLabel = 'COMMON', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @SelectiveRows int;
DECLARE @CommonRows int;
DECLARE @MaxPlans int;
DECLARE @Dispatchers int;
DECLARE @Variants int;
DECLARE @SelectiveReads bigint;
DECLARE @CommonReads bigint;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @MaxPlans = MAX(CachedPlanCount),
       @Dispatchers = MAX(DispatcherPlanCount),
       @Variants = MAX(VariantPlanCount)
FROM lab.Opt009Evidence
WHERE Phase = 'BASELINE';

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein markierter Cacheeintrag für lab.usp_Opt009SearchSelectiveFirst auswertbar' AS ObservedValue,
           N'markerbezogene Cacheevidenz für beide Ausführungen' AS RequiredValue,
           N'Die Plancacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

SELECT @SelectiveRows = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN ResultRowCount END),
       @CommonRows = MAX(CASE WHEN ParameterLabel = 'COMMON' THEN ResultRowCount END),
       @SelectiveReads = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @CommonReads = MAX(CASE WHEN ParameterLabel = 'COMMON' THEN LogicalReads END)
FROM lab.Opt009Evidence
WHERE Phase = 'BASELINE';

IF @SelectiveRows <> 5 OR @CommonRows <> 99000
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die OPT-009-Baseline liefert nicht die vereinbarten Trefferzahlen.', 1;

IF @MaxPlans <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Für den markierten Querytext wird in der Baseline genau ein zwischengespeicherter Plan erwartet.', 1;

IF @Dispatchers <> 0 OR @Variants <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Bei abgeschalteter Optimierung darf weder ein Dispatcherplan noch eine Queryvariante entstehen.', 1;

IF @SelectiveReads IS NULL OR @CommonReads IS NULL
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'LOGICAL_READS' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'keine Lesezahlen im Plancache' AS ObservedValue,
           N'logische Lesevorgänge je Parameterwert' AS RequiredValue,
           N'Die Lesekosten sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @CommonReads <= @SelectiveReads
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'PARAMETER_SENSITIVITY' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'selektiv=', @SelectiveReads, N'; dominant=', @CommonReads) AS ObservedValue,
           N'deutlich höhere Lesekosten für den dominanten Wert' AS RequiredValue,
           N'Der wiederverwendete Plan verhält sich in dieser Umgebung nicht wie erwartet; die Aussage ist nicht belegt.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'ein Plan; Lesevorgänge selektiv=', @SelectiveReads,
              N', dominant=', @CommonReads,
              N'; Dispatcher=0; Varianten=0') AS ObservedValue,
       N'ein wiederverwendeter Plan mit stark unterschiedlichen Lesekosten' AS RequiredValue,
       N'Der auf den selektiven Wert kompilierte Plan belastet den dominanten Wert messbar.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
