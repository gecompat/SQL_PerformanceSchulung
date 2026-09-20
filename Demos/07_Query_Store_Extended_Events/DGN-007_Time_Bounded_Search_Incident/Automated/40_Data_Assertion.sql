/* DGN-007: exakte Dateninvarianten; kein Query-Store- oder Incidentnachweis. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
IF DB_NAME()<>N'SQLPERF_LAB_DGN007_AUTO'
    THROW 51000,'FAIL_CONTRACT: Datenassertion in unerwarteter Datenbank.',1;
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
IF CONVERT(int,DATABASEPROPERTYEX(DB_NAME(),'CompatibilityLevel'))<>CASE @Major WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END
    THROW 51002,'FAIL_STATE: Compatibility Level entspricht nicht dem Versionsvertrag.',1;
IF (SELECT COUNT_BIG(*) FROM dbo.CaseGroup)<>12
   OR (SELECT COUNT_BIG(*) FROM dbo.CaseItem)<>24000
   OR (SELECT COUNT_BIG(*) FROM dbo.CaseItemDetail)<>72000
   OR EXISTS(SELECT 1 FROM dbo.CaseRequestLog)
    THROW 51002,'FAIL_RESULT_CONTRACT: Zeilenzahlen oder initialer Requestzustand weichen ab.',1;
IF EXISTS(SELECT 1 FROM dbo.CaseItem
          WHERE GroupKey<>CASE WHEN ItemId<=16000 THEN 1+((ItemId-1)%4) WHEN ItemId<=22000 THEN 5+((ItemId-16001)%3) ELSE 8+((ItemId-22001)%5) END
             OR StatusCode<>CASE WHEN ItemId%7=0 THEN 1 WHEN ItemId%7 IN(3,5) THEN 2 ELSE 3 END
             OR SearchValue<>N'Search'+CONVERT(nvarchar(11),ItemId))
   OR EXISTS(SELECT 1 FROM dbo.CaseItem i LEFT JOIN dbo.CaseItemDetail d ON d.ItemId=i.ItemId
             GROUP BY i.ItemId HAVING COUNT(d.ItemId)<>3 OR MIN(d.DetailOrdinal)<>1 OR MAX(d.DetailOrdinal)<>3)
    THROW 51002,'FAIL_RESULT_CONTRACT: Deterministische Verteilung oder Detailvertrag verletzt.',1;
CREATE TABLE #Actual(ItemId int NOT NULL,SearchValue nvarchar(64) NOT NULL,StatusCode tinyint NOT NULL,GroupLabel nvarchar(64) NOT NULL,DetailCount int NOT NULL);
DECLARE @GroupKey int,@StatusCode tinyint;
DECLARE parameters CURSOR LOCAL FAST_FORWARD FOR SELECT GroupKey,StatusCode FROM (VALUES(8,3),(1,3),(5,3),(1,1)) p(GroupKey,StatusCode);
OPEN parameters;
FETCH NEXT FROM parameters INTO @GroupKey,@StatusCode;
WHILE @@FETCH_STATUS=0
BEGIN
    TRUNCATE TABLE #Actual;
    INSERT #Actual EXEC dbo.usp_CaseSearch @GroupKey,@StatusCode;
    IF EXISTS(SELECT ItemId,SearchValue,StatusCode FROM dbo.CaseItem WHERE GroupKey=@GroupKey AND StatusCode=@StatusCode
              EXCEPT SELECT ItemId,SearchValue,StatusCode FROM #Actual)
       OR EXISTS(SELECT ItemId,SearchValue,StatusCode FROM #Actual
                 EXCEPT SELECT ItemId,SearchValue,StatusCode FROM dbo.CaseItem WHERE GroupKey=@GroupKey AND StatusCode=@StatusCode)
       OR EXISTS(SELECT 1 FROM #Actual WHERE DetailCount<>3 OR GroupLabel<>N'Group'+CONVERT(nvarchar(11),@GroupKey))
       OR (SELECT COUNT(*) FROM #Actual)<>(SELECT COUNT(*) FROM dbo.CaseItem WHERE GroupKey=@GroupKey AND StatusCode=@StatusCode)
        THROW 51002,'FAIL_RESULT_CONTRACT: Suchprozedur verletzt den bekannten Ergebnisvertrag.',1;
    FETCH NEXT FROM parameters INTO @GroupKey,@StatusCode;
END;
CLOSE parameters;
DEALLOCATE parameters;
IF (SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>4
    THROW 51002,'FAIL_RESULT_CONTRACT: Genau vier synthetische Suchrequests erwartet.',1;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
