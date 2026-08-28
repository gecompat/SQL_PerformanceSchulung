SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @R bigint,@S bigint,@P int,@H bigint=(SELECT COUNT_BIG(*) FROM lab.SkewData WHERE CategoryId=1);
SELECT @R=rows,@S=rows_sampled,@P=steps FROM sys.dm_db_stats_properties(OBJECT_ID(N'lab.SkewData'),INDEXPROPERTY(OBJECT_ID(N'lab.SkewData'),N'IX_OPT003_Category','IndexId'));
INSERT lab.Evidence VALUES('SAMPLE',@R,@S,@P,@H);
IF @R<>200000 OR @H<>180000 THROW 51006,'FAIL_RESULT_CONTRACT: OPT-003-Verteilung stimmt nicht.',1;
SELECT * FROM lab.Evidence;PRINT 'SQLPERF_SUMMARY|PASS|OK';
