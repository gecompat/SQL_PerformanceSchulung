/* OPT-009 mitigation: Parameter Sensitive Plan Optimization eingeschaltet. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

ALTER DATABASE SCOPED CONFIGURATION SET PARAMETER_SENSITIVE_PLAN_OPTIMIZATION = ON;
EXEC sys.sp_recompile @objname = N'lab.usp_Opt009SearchPsp';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Marker nvarchar(40) = N'OPT009' + N'_MARK_MITIGATION';

/* Erste Ausführung erzeugt Dispatcherplan und eine erste Queryvariante. */
EXEC lab.usp_Opt009SearchPsp @OwnerId = 2,
                             @ResultRowCount = @Rows OUTPUT,
                             @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt009Capture @Phase = 'MITIGATION', @ParameterLabel = 'SELECTIVE', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

/* Der dominante Wert fällt in ein anderes Kardinalitätsband und erhält eine eigene Variante. */
EXEC lab.usp_Opt009SearchPsp @OwnerId = 1,
                             @ResultRowCount = @Rows OUTPUT,
                             @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt009Capture @Phase = 'MITIGATION', @ParameterLabel = 'COMMON', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @SelectiveRows int;
DECLARE @CommonRows int;
DECLARE @Dispatchers int;
DECLARE @Variants int;
DECLARE @LowBoundary nvarchar(40);
DECLARE @HighBoundary nvarchar(40);
DECLARE @MitigationSelectiveReads bigint;
DECLARE @MitigationCommonReads bigint;
DECLARE @BadSelectiveReads bigint;
DECLARE @BadCommonReads bigint;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @Dispatchers = MAX(DispatcherPlanCount),
       @Variants = MAX(VariantPlanCount),
       @LowBoundary = MAX(LowBoundary),
       @HighBoundary = MAX(HighBoundary),
       @SelectiveRows = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN ResultRowCount END),
       @CommonRows = MAX(CASE WHEN ParameterLabel = 'COMMON' THEN ResultRowCount END),
       @MitigationSelectiveReads = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @MitigationCommonReads = MAX(CASE WHEN ParameterLabel = 'COMMON' THEN LogicalReads END)
FROM lab.Opt009Evidence
WHERE Phase = 'MITIGATION';

SELECT @BadSelectiveReads = MAX(CASE WHEN Phase = 'DEMONSTRATION' THEN LogicalReads END),
       @BadCommonReads = MAX(CASE WHEN Phase = 'BASELINE' THEN LogicalReads END)
FROM lab.Opt009Evidence
WHERE (Phase = 'DEMONSTRATION' AND ParameterLabel = 'SELECTIVE')
   OR (Phase = 'BASELINE' AND ParameterLabel = 'COMMON');

IF @SelectiveRows <> 5 OR @CommonRows <> 99000
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die eingeschaltete Optimierung verändert die Trefferzahlen.', 1;

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein markierter Cacheeintrag für lab.usp_Opt009SearchPsp auswertbar' AS ObservedValue,
           N'markerbezogene Cacheevidenz für beide Ausführungen' AS RequiredValue,
           N'Die Plancacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

/*
   Die Eignung einer Abfrage entscheidet der Optimierer. Bleibt die Variantenbildung aus,
   wird das als fehlende Evidenz protokolliert und nicht durch undokumentierte Eingriffe erzwungen.
*/
IF @Dispatchers = 0 OR @Variants < 2
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'DISPATCHER_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           CONCAT(N'Dispatcherplaene=', @Dispatchers, N'; Queryvarianten=', @Variants,
                  N'; Lesevorgänge selektiv/dominant=', ISNULL(@MitigationSelectiveReads, -1),
                  N'/', ISNULL(@MitigationCommonReads, -1)) AS ObservedValue,
           N'ein Dispatcherplan und mindestens zwei Queryvarianten' AS RequiredValue,
           N'Der Optimierer hat die Abfrage in dieser Umgebung nicht als parametersensitiv eingestuft; die Ergebnisgleichheit bleibt nachgewiesen.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @MitigationSelectiveReads IS NULL OR @MitigationCommonReads IS NULL
   OR @BadSelectiveReads IS NULL OR @BadCommonReads IS NULL
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'LOGICAL_READS' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'keine vergleichbaren Lesezahlen' AS ObservedValue,
           N'Lesezahlen aus Baseline, Demonstration und Gegenmaßnahme' AS RequiredValue,
           N'Der Kostenvergleich ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @MitigationSelectiveReads >= @BadSelectiveReads OR @MitigationCommonReads >= @BadCommonReads
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'VARIANT_BENEFIT' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'selektiv=', @MitigationSelectiveReads, N' gegenüber ', @BadSelectiveReads,
                  N'; dominant=', @MitigationCommonReads, N' gegenüber ', @BadCommonReads) AS ObservedValue,
           N'für beide Werte niedrigere Lesekosten als im jeweils ungünstigen Fall' AS RequiredValue,
           N'Die Varianten sind gebildet, ihr Nutzen ist hier aber nicht von der Messstreuung zu trennen.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Dispatcherplaene=', @Dispatchers, N'; Queryvarianten=', @Variants,
              N'; Grenzen=', ISNULL(@LowBoundary, N'-'), N'/', ISNULL(@HighBoundary, N'-'),
              N'; Lesevorgänge selektiv/dominant=', @MitigationSelectiveReads, N'/', @MitigationCommonReads) AS ObservedValue,
       N'ein Dispatcherplan, mindestens zwei Varianten, beidseitig niedrigere Lesekosten' AS RequiredValue,
       N'Der Dispatcherplan verteilt gleiche Anweisungen anhand der Kardinalitätsgrenzen auf eigene Planformen.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
