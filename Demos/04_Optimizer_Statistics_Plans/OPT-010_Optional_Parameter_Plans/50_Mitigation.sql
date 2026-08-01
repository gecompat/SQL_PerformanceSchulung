/* OPT-010 mitigation: Optional Parameter Plan Optimization einschalten und Dispatcherplan belegen. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

ALTER DATABASE SCOPED CONFIGURATION SET OPTIONAL_PARAMETER_OPTIMIZATION = ON;
EXEC sys.sp_recompile @objname = N'lab.usp_Opt010SearchOppo';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Marker nvarchar(40) = N'OPT010' + N'_MARK_MITIGATION';

EXEC lab.usp_Opt010SearchOppo @AgentId = 42,
                              @ResultRowCount = @Rows OUTPUT,
                              @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt010Capture @Phase = 'MITIGATION', @ParameterLabel = 'SELECTIVE', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Opt010SearchOppo @AgentId = NULL,
                              @ResultRowCount = @Rows OUTPUT,
                              @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt010Capture @Phase = 'MITIGATION', @ParameterLabel = 'OPTIONAL', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @SelectiveRows int;
DECLARE @OptionalRows int;
DECLARE @Dispatchers int;
DECLARE @Variants int;
DECLARE @OptionalPredicatePlans int;
DECLARE @SensitivePredicatePlans int;
DECLARE @OptionalPredicateCount int;
DECLARE @QueryVariantId int;
DECLARE @MitigationSelectiveReads bigint;
DECLARE @MitigationOptionalReads bigint;
DECLARE @BaselineSelectiveReads bigint;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @SelectiveRows = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN ResultRowCount END),
       @OptionalRows = MAX(CASE WHEN ParameterLabel = 'OPTIONAL' THEN ResultRowCount END),
       @Dispatchers = MAX(DispatcherPlanCount),
       @Variants = MAX(VariantPlanCount),
       @OptionalPredicatePlans = MAX(OptionalPredicatePlanCount),
       @SensitivePredicatePlans = MAX(SensitivePredicatePlanCount),
       @OptionalPredicateCount = MAX(OptionalPredicateCount),
       @QueryVariantId = MAX(QueryVariantId),
       @MitigationSelectiveReads = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @MitigationOptionalReads = MAX(CASE WHEN ParameterLabel = 'OPTIONAL' THEN LogicalReads END)
FROM lab.Opt010Evidence
WHERE Phase = 'MITIGATION';

SELECT @BaselineSelectiveReads = MAX(LogicalReads)
FROM lab.Opt010Evidence
WHERE Phase = 'BASELINE' AND ParameterLabel = 'SELECTIVE';

IF @SelectiveRows <> 50 OR @OptionalRows <> 100000
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die Gegenmaßnahme verändert das Ergebnis; das widerspricht dem Demovertrag.', 1;

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein markierter Cacheeintrag für lab.usp_Opt010SearchOppo auswertbar' AS ObservedValue,
           N'markerbezogene Cacheevidenz für beide Ausführungen' AS RequiredValue,
           N'Die Plancacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @Dispatchers = 0 OR @Variants < 2
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'DISPATCHER_PLAN' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           CONCAT(N'Dispatcher=', @Dispatchers, N'; Varianten=', @Variants) AS ObservedValue,
           N'ein Dispatcherplan und mindestens zwei Queryvarianten' AS RequiredValue,
           N'Die Optimierung ist eingeschaltet, hat diese Abfrage in dieser Umgebung aber nicht als geeignet eingestuft.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @OptionalPredicatePlans = 0
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'OPTIONAL_PARAMETER_PREDICATE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'Dispatcherplan ohne optionales Parameterprädikat' AS ObservedValue,
           N'Dispatcherplan mit mindestens einem optionalen Parameterprädikat' AS RequiredValue,
           N'Es liegt ein Dispatcherplan vor, er ist aber nicht der Optional Parameter Plan Optimization zuzuordnen.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

/* Sauberkeit der Zuordnung: die parametersensitive Planoptimierung darf nicht zugleich greifen. */
IF @SensitivePredicatePlans > 0
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'ATTRIBUTION' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'optionale Prädikate=', @OptionalPredicatePlans,
                  N'; sensitive Prädikate=', @SensitivePredicatePlans) AS ObservedValue,
           N'ausschließlich optionale Parameterprädikate im Dispatcherplan' AS RequiredValue,
           N'Beide Mehrplanverfahren greifen gleichzeitig; die Wirkung ist nicht eindeutig der Optional Parameter Plan Optimization zuzuschreiben.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

IF @MitigationSelectiveReads IS NULL OR @BaselineSelectiveReads IS NULL
   OR @MitigationSelectiveReads >= @BaselineSelectiveReads
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'SELECTIVE_COST_REDUCTION' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'belegt mit Optimierung=', ISNULL(@MitigationSelectiveReads, -1),
                  N'; belegt in Baseline=', ISNULL(@BaselineSelectiveReads, -1)) AS ObservedValue,
           N'geringere Lesekosten des belegten Parameters gegenüber der Baseline' AS RequiredValue,
           N'Der Dispatcherplan ist belegt, die Kostensenkung ist in dieser Umgebung aber nicht messbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Dispatcher=', @Dispatchers, N'; Varianten=', @Variants,
              N'; optionale Prädikate im Dispatcher=', ISNULL(@OptionalPredicateCount, -1),
              N'; QueryVariantID=', ISNULL(@QueryVariantId, -1),
              N'; Lesevorgänge belegt=', @MitigationSelectiveReads,
              N', offen=', ISNULL(@MitigationOptionalReads, -1),
              N'; Baseline belegt=', @BaselineSelectiveReads) AS ObservedValue,
       N'Dispatcherplan mit optionalem Parameterprädikat und mindestens zwei Queryvarianten' AS RequiredValue,
       N'Die eingeschaltete Optimierung erzeugt je Parameterzustand eine eigene Variante; der belegte Parameter zahlt den offenen Fall nicht mehr mit.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
