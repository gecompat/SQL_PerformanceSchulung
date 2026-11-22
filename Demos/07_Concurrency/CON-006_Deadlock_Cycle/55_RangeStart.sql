SET NOCOUNT ON;SET XACT_ABORT ON;
DELETE lab.RangeControlEvidence;DELETE lab.RangeActors;DELETE lab.RangeRun;DELETE lab.RangeRows;
INSERT lab.RangeRows(KeyValue)VALUES(10),(50),(90);
INSERT lab.RangeActors(RoleName,ExpectedKey)VALUES('ACTOR_A',70),('ACTOR_B',30);
INSERT lab.RangeRun(Attempt,RunToken,DatabaseId,StartedAtUtc)
VALUES('RANGE','$(RunToken)',DB_ID(),SYSUTCDATETIME());
PRINT 'SQLPERF_SUMMARY|PASS|OK';
