/* OPT-009 comparison: Ergebnisgleichheit über alle Phasen und dokumentierte Abwahl auf Abfrageebene. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Marker nvarchar(40) = N'OPT009' + N'_MARK_OPTOUT';

/* Parametersensitivität bleibt aktiv; nur diese Abfrage wählt sie ausdrücklich ab. */
EXEC lab.usp_Opt009SearchOptOut @OwnerId = 2,
                                @ResultRowCount = @Rows OUTPUT,
                                @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt009Capture @Phase = 'COMPARISON', @ParameterLabel = 'SELECTIVE', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Opt009SearchOptOut @OwnerId = 1,
                                @ResultRowCount = @Rows OUTPUT,
                                @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt009Capture @Phase = 'COMPARISON', @ParameterLabel = 'COMMON', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @DistinctSelectiveChecksums int;
DECLARE @DistinctCommonChecksums int;
DECLARE @DistinctSelectiveRows int;
DECLARE @DistinctCommonRows int;
DECLARE @PhaseCount int;
DECLARE @OptOutDispatchers int;
DECLARE @MitigationDispatchers int;
DECLARE @MitigationVariants int;

SELECT @PhaseCount = COUNT(DISTINCT Phase) FROM lab.Opt009Evidence;

SELECT @DistinctSelectiveChecksums = COUNT(DISTINCT ISNULL(ResultChecksum, -1)),
       @DistinctSelectiveRows = COUNT(DISTINCT ResultRowCount)
FROM lab.Opt009Evidence
WHERE ParameterLabel = 'SELECTIVE';

SELECT @DistinctCommonChecksums = COUNT(DISTINCT ISNULL(ResultChecksum, -1)),
       @DistinctCommonRows = COUNT(DISTINCT ResultRowCount)
FROM lab.Opt009Evidence
WHERE ParameterLabel = 'COMMON';

SELECT @OptOutDispatchers = MAX(DispatcherPlanCount)
FROM lab.Opt009Evidence
WHERE Phase = 'COMPARISON';

SELECT @MitigationDispatchers = MAX(DispatcherPlanCount),
       @MitigationVariants = MAX(VariantPlanCount)
FROM lab.Opt009Evidence
WHERE Phase = 'MITIGATION';

IF @PhaseCount <> 4
    THROW 51006, 'FAIL_RESULT_CONTRACT: Es werden Messpunkte aus vier Phasen erwartet.', 1;

IF @DistinctSelectiveRows <> 1 OR @DistinctCommonRows <> 1
   OR @DistinctSelectiveChecksums <> 1 OR @DistinctCommonChecksums <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die Phasen sind je Parameterwert nicht ergebnisgleich.', 1;

/* Die Abwahl auf Abfrageebene muss trotz eingeschalteter Datenbankeinstellung greifen. */
IF @OptOutDispatchers IS NULL OR @OptOutDispatchers <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die abgewählte Abfrage darf keinen Dispatcherplan erzeugen.', 1;

SELECT 1 AS Sequence, 'COMPARISON' AS Phase, 'RESULT_EQUALITY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       N'je Parameterwert eine Trefferzahl und eine Prüfsumme über vier Phasen' AS ObservedValue,
       N'Ergebnisgleichheit unabhängig von der Planform' AS RequiredValue,
       N'Parametersensitivität verändert ausschließlich die Ausführungskosten.' AS Message
UNION ALL
SELECT 2, 'COMPARISON', 'QUERY_LEVEL_OPT_OUT', 'PASS', 'OK',
       CONCAT(N'Dispatcherplaene mit Abwahlhinweis=', @OptOutDispatchers,
              N'; ohne Abwahlhinweis=', ISNULL(@MitigationDispatchers, -1)),
       N'kein Dispatcherplan bei ausdrücklicher Abwahl',
       N'Die Optimierung ist je Abfrage abwählbar, ohne die Datenbankeinstellung zu ändern.'
UNION ALL
SELECT 3, 'COMPARISON', 'DOCUMENTED_LIMITS', 'PASS', 'OK',
       N'nur Gleichheitsprädikate; höchstens drei Prädikate; drei Kardinalitätsbänder je Prädikat',
       N'Grenzen der Produktdokumentation',
       N'Ungleichheits-, Bereichs- und LIKE-Prädikate bleiben außerhalb des Verfahrens.'
UNION ALL
SELECT 4, 'COMPARISON', 'SUMMARY', 'PASS', 'OK',
       CONCAT(N'Phasen=', @PhaseCount, N'; Queryvarianten in der Gegenmaßnahme=', ISNULL(@MitigationVariants, -1)),
       N'gleiche Ergebnisse, unterschiedliche Planformen, abwählbares Verfahren',
       N'Parametersensitive Planoptimierung ist eine gezielte Antwort auf schiefe Gleichheitsprädikate, kein allgemeiner Beschleuniger.';
PRINT 'SQLPERF_SUMMARY|PASS|OK';
