SET NOCOUNT ON;SET XACT_ABORT ON;
EXEC fwk.USP_WaitForSignal '$(DemoId)','$(RunToken)','CONVERSION_A_DONE',30000;
EXEC fwk.USP_WaitForSignal '$(DemoId)','$(RunToken)','CONVERSION_B_DONE',30000;
IF (SELECT COUNT(*) FROM lab.ConversionEvidence WHERE Attempt='CONVERT')<>2
    THROW 51006,'FAIL_RESULT_CONTRACT: Beide Konversionsakteure muessen abgeschlossen sein.',1;
IF (SELECT COUNT(*) FROM lab.ConversionEvidence WHERE Attempt='CONVERT' AND RoleName='ACTOR_A' AND Outcome='VICTIM' AND ErrorNumber=1205)<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: ACTOR_A muss als niedrig priorisiertes Konversionsopfer Fehler 1205 erhalten.',1;
IF (SELECT COUNT(*) FROM lab.ConversionEvidence WHERE Attempt='CONVERT' AND RoleName='ACTOR_B' AND Outcome='SURVIVOR' AND ErrorNumber IS NULL)<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: ACTOR_B muss als hoch priorisierter Konversionsgegenpart abschliessen.',1;
IF (SELECT COUNT(DISTINCT SessionId) FROM lab.ConversionEvidence WHERE Attempt='CONVERT')<>2
    THROW 51006,'FAIL_RESULT_CONTRACT: Konversionsakteure muessen getrennte Sessions sein.',1;
SELECT Attempt,RoleName,Outcome,ErrorNumber,SessionId,CapturedAtUtc
FROM lab.ConversionEvidence WHERE Attempt='CONVERT' ORDER BY RoleName;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
