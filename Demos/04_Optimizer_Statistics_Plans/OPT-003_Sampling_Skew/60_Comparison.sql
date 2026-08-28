SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @Rows bigint,@Sampled bigint,@Steps int,@Hot bigint;
SELECT @Rows=RowsTotal,@Sampled=RowsSampled,@Steps=Steps,@Hot=HotRows FROM lab.Evidence WHERE Stage='FULLSCAN';
IF @Rows<>200000 OR @Sampled<>@Rows OR @Steps NOT BETWEEN 1 AND 200 OR @Hot<>180000 THROW 51006,'FAIL_RESULT_CONTRACT: Fullscan-Invarianten fehlen.',1;
SELECT * FROM lab.Evidence ORDER BY Stage;PRINT 'SQLPERF_SUMMARY|PASS|OK';
