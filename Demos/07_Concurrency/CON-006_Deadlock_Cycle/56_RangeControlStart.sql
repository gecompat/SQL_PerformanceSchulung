SET NOCOUNT ON;SET XACT_ABORT ON;
DELETE lab.RangeControlEvidence;DELETE lab.RangeRows;
INSERT lab.RangeRows(KeyValue)VALUES(10),(50),(90);
UPDATE lab.RangeRun SET ControlStartedAtUtc=SYSUTCDATETIME(),ControlFinishedAtUtc=NULL,ControlDeadlockCount=NULL
WHERE Attempt='RANGE' AND RunToken='$(RunToken)' AND DatabaseId=DB_ID() AND WaitObserved=1 AND GraphCount=1;
IF @@ROWCOUNT<>1 THROW 51006,'FAIL_RESULT_CONTRACT: Range-Kontrollarm ist nicht an einen bestandenen Deadlocklauf gebunden.',1;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
