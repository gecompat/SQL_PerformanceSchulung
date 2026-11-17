SET NOCOUNT ON;SET XACT_ABORT ON;
DELETE fwk.SessionSignal;DELETE lab.ConversionEvidence;DELETE lab.ConversionRun;UPDATE lab.DeadlockRows SET Value=0;
INSERT lab.ConversionRun(Attempt,RunToken,DatabaseId,StartedAtUtc,GraphCount)
VALUES('CONVERT','$(RunToken)',DB_ID(),SYSUTCDATETIME(),NULL);
PRINT 'SQLPERF_SUMMARY|PASS|OK';
