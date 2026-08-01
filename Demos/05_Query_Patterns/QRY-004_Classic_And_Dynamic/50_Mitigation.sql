/* QRY-004 mitigation: sicher parameterisiertes dynamisches SQL mit fester Positivliste. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Rows int;
DECLARE @Checksum int;

EXEC lab.usp_Qry004Dynamic @FilterSpec = 'CategoryCode', @CategoryCode = 'RARE',
                           @ResultRowCount = @Rows OUTPUT, @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'MITIGATION', @Strategy = 'DYNAMIC', @Combination = 'RARE',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Qry004Dynamic @FilterSpec = 'CategoryCode', @CategoryCode = 'CMMN',
                           @ResultRowCount = @Rows OUTPUT, @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'MITIGATION', @Strategy = 'DYNAMIC', @Combination = 'COMMON',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Qry004Dynamic @FilterSpec = 'StatusCode', @StatusCode = 1,
                           @ResultRowCount = @Rows OUTPUT, @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'MITIGATION', @Strategy = 'DYNAMIC', @Combination = 'STATUS',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @Mismatch int;
DECLARE @RarePlans int;
DECLARE @CommonPlans int;
DECLARE @StatusPlans int;
DECLARE @LiteralFree int;
DECLARE @Rejected bit = 0;
DECLARE @IgnoredRows int;
DECLARE @IgnoredChecksum int;

BEGIN TRY
    EXEC lab.usp_Qry004Dynamic @FilterSpec = 'CategoryCode;PayloadDrop', @CategoryCode = 'RARE',
                               @ResultRowCount = @IgnoredRows OUTPUT, @ResultChecksum = @IgnoredChecksum OUTPUT;
END TRY
BEGIN CATCH
    SET @Rejected = 1;
END CATCH;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END)
FROM lab.Qry004Evidence
WHERE Phase = 'MITIGATION';

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'keine markerbezogene Cacheevidenz für das dynamische Statement auswertbar' AS ObservedValue,
           N'Cacheevidenz für alle drei Ausführungen' AS RequiredValue,
           N'Die Cacheattribute des vorbereiteten Statements sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @Rejected = 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Eine unbekannte Filterdefinition muss zu einem kontrollierten Abbruch führen.', 1;

SELECT @Mismatch = COUNT(*)
FROM lab.Qry004Evidence AS baseline
INNER JOIN lab.Qry004Evidence AS dynamic_sql
        ON dynamic_sql.Phase = 'MITIGATION'
       AND dynamic_sql.Strategy = 'DYNAMIC'
       AND dynamic_sql.Combination = baseline.Combination
WHERE baseline.Phase = 'BASELINE'
  AND baseline.Strategy = 'CATCHALL'
  AND (baseline.ResultRowCount <> dynamic_sql.ResultRowCount
       OR ISNULL(baseline.ResultChecksum, -1) <> ISNULL(dynamic_sql.ResultChecksum, -1));

IF @Mismatch IS NULL OR @Mismatch > 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Dynamisches SQL und Catch-all-Baseline liefern nicht dasselbe Ergebnis.', 1;

SELECT @RarePlans = MAX(CASE WHEN Combination = 'RARE' THEN CachedPlanCount END),
       @CommonPlans = MAX(CASE WHEN Combination = 'COMMON' THEN CachedPlanCount END),
       @StatusPlans = MAX(CASE WHEN Combination = 'STATUS' THEN CachedPlanCount END),
       @LiteralFree = MIN(CONVERT(int, LiteralFreeText))
FROM lab.Qry004Evidence
WHERE Phase = 'MITIGATION' AND Strategy = 'DYNAMIC';

IF @LiteralFree IS NULL OR @LiteralFree <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der zwischengespeicherte Statementtext darf keine Filterwerte enthalten.', 1;

IF @RarePlans <> 1 OR @CommonPlans <> 1 OR @StatusPlans <> 2
    THROW 51006, 'FAIL_RESULT_CONTRACT: Erwartet werden zwei Statementformen für drei Ausführungen.', 1;

SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Statementformen nach RARE/COMMON/STATUS=', @RarePlans, N'/', @CommonPlans, N'/', @StatusPlans,
              N'; Werte im Statementtext=nein; unbekannte Filterdefinition abgewiesen=ja') AS ObservedValue,
       N'zwei Statementformen für drei Ausführungen, gebundene Werte und abgewiesene Positivlistenverletzung' AS RequiredValue,
       N'Dynamisches SQL bindet Werte als Parameter und begrenzt die Zahl der Statementformen auf die Filterform.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
