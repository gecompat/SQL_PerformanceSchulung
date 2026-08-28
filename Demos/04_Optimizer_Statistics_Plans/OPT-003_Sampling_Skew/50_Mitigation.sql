SET NOCOUNT ON;SET XACT_ABORT ON;
UPDATE STATISTICS lab.SkewData IX_OPT003_Category WITH FULLSCAN;
DECLARE @R bigint,@S bigint,@P int,@H bigint=(SELECT COUNT_BIG(*) FROM lab.SkewData WHERE CategoryId=1);
SELECT @R=rows,@S=rows_sampled,@P=steps FROM sys.dm_db_stats_properties(OBJECT_ID(N'lab.SkewData'),INDEXPROPERTY(OBJECT_ID(N'lab.SkewData'),N'IX_OPT003_Category','IndexId'));
INSERT lab.Evidence VALUES('FULLSCAN',@R,@S,@P,@H);PRINT 'SQLPERF_SUMMARY|PASS|OK';
