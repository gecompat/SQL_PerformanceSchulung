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
IF (SELECT COUNT(*) FROM lab.RangeRun WHERE Attempt='RANGE' AND RunToken='$(RunToken)' AND DatabaseId=DB_ID() AND WaitObserved=1 AND GraphCount=1 AND ControlDeadlockCount=0 AND ControlFinishedAtUtc IS NOT NULL)<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Range-Deadlockgraph und serielle Kontrolle fehlen.',1;
IF (SELECT COUNT(*) FROM lab.RangeActors WHERE Outcome='VICTIM' AND ErrorNumber=1205)<>1
   OR (SELECT COUNT(*) FROM lab.RangeActors WHERE Outcome='SURVIVOR' AND ErrorNumber IS NULL)<>1
   OR (SELECT COUNT(*) FROM lab.RangeControlEvidence WHERE Outcome='INSERTED' AND ErrorNumber IS NULL)<>2
   OR (SELECT COUNT(DISTINCT SessionId) FROM lab.RangeControlEvidence)<>2
   OR (SELECT COUNT(*) FROM lab.RangeRows)<>5
   OR EXISTS(SELECT 1 FROM lab.RangeRows WHERE KeyValue NOT IN(10,30,50,70,90))
    THROW 51006,'FAIL_RESULT_CONTRACT: Range-Actor- oder Kontrollendbestand ist unvollstaendig.',1;
SELECT * FROM lab.Evidence;
SELECT Attempt,RoleName,Outcome,ErrorNumber,SessionId,CapturedAtUtc
FROM lab.ConversionEvidence ORDER BY Attempt,RoleName;
SELECT Attempt,RunToken,DatabaseId,StartedAtUtc,GraphCount FROM lab.ConversionRun ORDER BY Attempt;
SELECT Attempt,RunToken,DatabaseId,WaitObserved,GraphCount,ControlDeadlockCount FROM lab.RangeRun;
SELECT RoleName,SessionId,ExpectedKey,Outcome,ErrorNumber,StartedAtUtc,FinishedAtUtc FROM lab.RangeActors ORDER BY RoleName;
SELECT RoleName,SessionId,KeyValue,Outcome,ErrorNumber,CapturedAtUtc FROM lab.RangeControlEvidence ORDER BY RoleName;
SELECT KeyValue FROM lab.RangeRows ORDER BY KeyValue;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
