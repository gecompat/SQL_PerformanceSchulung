SET NOCOUNT ON;SET XACT_ABORT ON;
IF (SELECT COUNT(*) FROM lab.Evidence WHERE Outcome='COMPLETED')<>2 OR EXISTS(SELECT 1 FROM lab.Evidence WHERE Outcome='VICTIM')
    THROW 51006,'FAIL_RESULT_CONTRACT: Geordnete Gegenprobe fehlgeschlagen.',1;
IF (SELECT COUNT(*) FROM lab.ConversionEvidence WHERE Attempt='CONVERT')<>2
   OR (SELECT COUNT(*) FROM lab.ConversionEvidence WHERE Attempt='CONVERT' AND RoleName='ACTOR_A' AND Outcome='VICTIM' AND ErrorNumber=1205)<>1
   OR (SELECT COUNT(*) FROM lab.ConversionEvidence WHERE Attempt='CONVERT' AND RoleName='ACTOR_B' AND Outcome='SURVIVOR' AND ErrorNumber IS NULL)<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Konversionsdeadlock und Opferergebnis fehlen.',1;
IF (SELECT COUNT(*) FROM lab.ConversionRun WHERE Attempt='CONVERT' AND GraphCount=1)<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Ein eindeutiger Konversionsgraph ist nicht belegt.',1;
IF (SELECT COUNT(*) FROM lab.ConversionEvidence WHERE Attempt='UPDLOCK' AND Outcome='COMPLETED')<>2
   OR EXISTS(SELECT 1 FROM lab.ConversionEvidence WHERE Attempt='UPDLOCK' AND Outcome='VICTIM')
    THROW 51006,'FAIL_RESULT_CONTRACT: UPDLOCK-Gegenprobe muss ohne Deadlock enden.',1;
IF (SELECT COUNT(DISTINCT SessionId) FROM lab.ConversionEvidence WHERE Attempt='UPDLOCK')<>2
    THROW 51006,'FAIL_RESULT_CONTRACT: UPDLOCK-Akteure muessen getrennte Sessions sein.',1;
SELECT * FROM lab.Evidence;
SELECT Attempt,RoleName,Outcome,ErrorNumber,SessionId,CapturedAtUtc
FROM lab.ConversionEvidence ORDER BY Attempt,RoleName;
SELECT Attempt,RunToken,DatabaseId,StartedAtUtc,GraphCount FROM lab.ConversionRun ORDER BY Attempt;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
