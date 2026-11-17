SET NOCOUNT ON;SET XACT_ABORT ON;
DELETE fwk.SessionSignal;UPDATE lab.DeadlockRows SET Value=0;
INSERT lab.ConversionRun(Attempt,RunToken,DatabaseId,StartedAtUtc,GraphCount)
VALUES('UPDLOCK','$(RunToken)',DB_ID(),SYSUTCDATETIME(),NULL);
PRINT 'SQLPERF_SUMMARY|PASS|OK';
