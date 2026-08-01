/* QRY-013 comparison: Wiederholung von CLIENT_PROFILE_A nach der Angleichung und Gesamtbewertung. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ANSI_NULL_DFLT_ON ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET QUOTED_IDENTIFIER ON;
SET NUMERIC_ROUNDABORT OFF;
SET ARITHABORT ON;
GO

SET NOCOUNT ON;
DECLARE @ResultRowCount int;
DECLARE @ResultChecksum int;

EXEC lab.usp_Qry013Probe @CategoryCode = 'RARE',
                         @ResultRowCount = @ResultRowCount OUTPUT,
                         @ResultChecksum = @ResultChecksum OUTPUT;

EXEC lab.usp_Qry013Capture @Phase = 'COMPARISON',
                           @ProfileCode = 'A',
                           @ParameterValue = 'RARE',
                           @ResultRowCount = @ResultRowCount,
                           @ResultChecksum = @ResultChecksum;
GO

SET NOCOUNT ON;
DECLARE @ComparisonPlans int;
DECLARE @ComparisonChecksum int;
DECLARE @ComparisonRows int;
DECLARE @EvidenceAvailable bit;
DECLARE @BaselineChecksum int;
DECLARE @BaselineRows int;
DECLARE @DemonstrationPlans int;
DECLARE @DemonstrationChecksum int;
DECLARE @ObservationRows int;

SELECT @ComparisonPlans = CachedPlanCount,
       @ComparisonChecksum = ResultChecksum,
       @ComparisonRows = ResultRowCount,
       @EvidenceAvailable = EvidenceAvailable
FROM lab.Qry013Evidence
WHERE Phase = 'COMPARISON';

SELECT @BaselineChecksum = ResultChecksum, @BaselineRows = ResultRowCount
FROM lab.Qry013Evidence WHERE Phase = 'BASELINE';

SELECT @DemonstrationPlans = CachedPlanCount, @DemonstrationChecksum = ResultChecksum
FROM lab.Qry013Evidence WHERE Phase = 'DEMONSTRATION';

SELECT @ObservationRows = ResultRowCount
FROM lab.Qry013Evidence WHERE Phase = 'OBSERVATION';

IF @EvidenceAvailable = 0 OR @BaselineChecksum IS NULL OR @DemonstrationPlans IS NULL OR @ObservationRows IS NULL
BEGIN
    SELECT 1 AS Sequence, 'COMPARISON' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'nicht alle Phasenwerte liegen vor' AS ObservedValue,
           N'Werte aus Baseline, Demonstration, Observation und Comparison' AS RequiredValue,
           N'Der Gesamtvergleich ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @ComparisonRows <> @BaselineRows
   OR @ComparisonChecksum <> @BaselineChecksum
   OR @DemonstrationChecksum <> @BaselineChecksum
    THROW 51006, 'FAIL_RESULT_CONTRACT: Alle Proben mit demselben Parameterwert müssen dasselbe Ergebnis liefern.', 1;

IF @ComparisonPlans >= @DemonstrationPlans
    THROW 51006, 'FAIL_RESULT_CONTRACT: Nach der Angleichung wird eine geringere Anzahl Cacheeintraege erwartet.', 1;

IF @ObservationRows = @BaselineRows
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die Parameterdimension ist nicht von der Kontextdimension unterscheidbar.', 1;

SELECT 1 AS Sequence, 'COMPARISON' AS Phase, 'CONTEXT_DIMENSIONS' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Cacheeintraege vorher=', @DemonstrationPlans, N', nachher=', @ComparisonPlans,
              N'; Ergebnis unveraendert; Parameterdimension weiterhin wirksam (',
              @BaselineRows, N' gegenueber ', @ObservationRows, N' Zeilen)') AS ObservedValue,
       N'Kontext- und Parameterdimension bleiben getrennt beurteilbar' AS RequiredValue,
       N'Die Angleichung des Sessionkontexts beseitigt den zusätzlichen Cacheeintrag, nicht aber die Parameterabhaengigkeit.' AS Message;

SELECT 2 AS Sequence, 'COMPARISON' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Phasen=', (SELECT COUNT(*) FROM lab.Qry013Evidence),
              N'; identische Ergebnischecksumme über alle RARE-Proben') AS ObservedValue,
       N'gleicher Querytext ohne garantiert gleiche Ausfuehrungsbedingungen' AS RequiredValue,
       N'Gleicher Querytext garantiert keine identischen Ausfuehrungsbedingungen; eine einzelne SET-Option erklaert den Unterschied nicht.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
