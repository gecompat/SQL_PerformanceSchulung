/* Isolated mitigation mechanism probe. No Query Store timing or persistent DDL. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
IF @@TRANCOUNT<>0 OR DB_NAME()<>N'SQLPERF_LAB_DGN007_AUTO'
  OR COALESCE(CONVERT(varchar(128),SERVERPROPERTY('ProductVersion')),'')<>'17.0.5065.9'
  OR (SELECT COUNT(*) FROM sys.extended_properties WHERE class=0 AND (
      (name=N'SQLPERF.Project' AND CONVERT(nvarchar(128),value)=N'SQL_PerformanceSchulung')
      OR (name=N'SQLPERF.ContractVersion' AND CONVERT(nvarchar(128),value)=N'1.0')
      OR (name=N'SQLPERF.DemoId' AND CONVERT(nvarchar(128),value)=N'DGN-007')
      OR (name=N'SQLPERF.RunToken' AND CONVERT(nvarchar(128),value)=N'AUTO')))<>4
    THROW 51090,'FAIL_OWNERSHIP',1;

DECLARE @object int=OBJECT_ID(N'dbo.usp_CaseSearch',N'P');
DECLARE @definition nvarchar(max), @ansi bit, @quoted bit;
SELECT @definition=definition,@ansi=uses_ansi_nulls,@quoted=uses_quoted_identifier
FROM sys.sql_modules WHERE object_id=@object;
DECLARE @anchor nvarchar(40)=N'ORDER BY i.ItemId;';
DECLARE @header int=CHARINDEX(N'PROCEDURE',@definition), @position int=CHARINDEX(@anchor,@definition);
IF @definition IS NULL OR @ansi IS NULL OR @quoted IS NULL OR @header<1 OR @position<=@header
   OR CHARINDEX(@anchor,@definition,@position+LEN(@anchor))<>0
   OR CHARINDEX(N'OPTION (RECOMPILE)',@definition)<>0
    THROW 51091,'FAIL_CONTRACT: expected unchanged procedure',1;
DECLARE @changed nvarchar(max)=N'ALTER '+SUBSTRING(@definition,@header,LEN(@definition));
SET @changed=REPLACE(@changed,@anchor,N'ORDER BY i.ItemId OPTION (RECOMPILE);');
DECLARE @apply nvarchar(max)=
    N'SET ANSI_NULLS '+CASE @ansi WHEN 1 THEN N'ON' ELSE N'OFF' END
    +N'; SET QUOTED_IDENTIFIER '+CASE @quoted WHEN 1 THEN N'ON' ELSE N'OFF' END
    +N'; EXEC sys.sp_executesql @ddl;';
DECLARE @before varbinary(32)=HASHBYTES('SHA2_256',CONVERT(varbinary(max),@definition));

CREATE TABLE #reference(
    ItemId int NOT NULL PRIMARY KEY, SearchValue nvarchar(64), StatusCode tinyint,
    GroupLabel nvarchar(64), DetailCount int
);
SELECT TOP(0) * INTO #observed FROM #reference;
DECLARE @trial tinyint=1;
DECLARE @label varchar(16);
BEGIN TRANSACTION;
WHILE @trial<=5
BEGIN
    IF @trial IN(1,5)
    BEGIN
        EXEC sys.sp_recompile N'dbo.usp_CaseSearch';
        INSERT #observed EXEC dbo.usp_CaseSearch @GroupKey=8,@StatusCode=3;
        IF @@ROWCOUNT<>228 THROW 51092,'FAIL_RESULT',1;
        TRUNCATE TABLE #observed;
    END;
    IF @trial=3
    BEGIN
        SAVE TRANSACTION MitigationStart;
        EXEC sys.sp_executesql @apply,N'@ddl nvarchar(max)',@ddl=@changed;
        IF NOT EXISTS (
            SELECT 1 FROM sys.sql_modules WHERE object_id=@object
            AND uses_ansi_nulls=@ansi AND uses_quoted_identifier=@quoted
            AND definition LIKE N'%ORDER BY i.ItemId OPTION (RECOMPILE);%'
        )
            THROW 51093,'FAIL_MITIGATION',1;
    END;
    SET @label=CHOOSE(@trial,'BASELINE1','BASELINE2','MITIGATION1','MITIGATION2','RESTORE');
    PRINT CONCAT('DGN007_IO_BEGIN|',@label);
    SET STATISTICS IO ON;
    INSERT #observed EXEC dbo.usp_CaseSearch @GroupKey=1,@StatusCode=3;
    DECLARE @rows int=@@ROWCOUNT;
    SET STATISTICS IO OFF;
    PRINT CONCAT('DGN007_IO_END|',@label);
    IF @rows<>2286 THROW 51092,'FAIL_RESULT',1;
    IF @trial=1
        INSERT #reference SELECT * FROM #observed;
    ELSE IF EXISTS (SELECT * FROM #reference EXCEPT SELECT * FROM #observed)
         OR EXISTS (SELECT * FROM #observed EXCEPT SELECT * FROM #reference)
        THROW 51092,'FAIL_RESULT',1;
    TRUNCATE TABLE #observed;

    IF @trial=4
    BEGIN
        ROLLBACK TRANSACTION MitigationStart;
        IF NOT EXISTS (
            SELECT 1 FROM sys.sql_modules WHERE object_id=@object
            AND uses_ansi_nulls=@ansi AND uses_quoted_identifier=@quoted
            AND HASHBYTES('SHA2_256',CONVERT(varbinary(max),definition))=@before
        )
            THROW 51094,'FAIL_RESTORE',1;
    END;
    SET @trial+=1;
END;
ROLLBACK TRANSACTION;
PRINT 'DGN007_MITIGATION|RESULTS_AND_RESTORE|PASS';
