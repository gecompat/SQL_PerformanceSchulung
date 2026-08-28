USE [master];SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @D varchar(7)='$(DemoId)',@R varchar(20)='$(RunToken)',@T sysname=N'$(TargetDatabase)',@S nvarchar(max),@C int=CASE TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')) WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
IF @D<>'OPT-003' OR @T<>N'SQLPERF_LAB_OPT003_'+@R OR @C IS NULL THROW 51000,'FAIL_CONTRACT: OPT-003-Setupziel ist ungueltig.',1;
IF DB_ID(@T) IS NOT NULL THROW 51002,'FAIL_STATE: OPT-003-Zieldatenbank existiert bereits.',1;
SET @S=N'CREATE DATABASE '+QUOTENAME(@T)+N';ALTER DATABASE '+QUOTENAME(@T)+N' SET RECOVERY SIMPLE;ALTER DATABASE '+QUOTENAME(@T)+N' SET COMPATIBILITY_LEVEL='+CONVERT(nvarchar(3),@C)+N';';EXEC(@S);
SET @S=N'USE '+QUOTENAME(@T)+N';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=N''OPT-003'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@R;';EXEC sys.sp_executesql @S,N'@R varchar(20)',@R=@R;
GO
USE [$(TargetDatabase)];SET NOCOUNT ON;SET XACT_ABORT ON;
IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
CREATE TABLE lab.SkewData(RowId int NOT NULL CONSTRAINT PK_OPT003 PRIMARY KEY,CategoryId int NOT NULL,Payload char(80) NOT NULL);
;WITH D(n) AS(SELECT n FROM(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))v(n)),N(n) AS(SELECT TOP(200000) ROW_NUMBER() OVER(ORDER BY(SELECT NULL)) FROM D a CROSS JOIN D b CROSS JOIN D c CROSS JOIN D d CROSS JOIN D e CROSS JOIN D f)
INSERT lab.SkewData SELECT n,CASE WHEN n<=180000 THEN 1 ELSE 2+(n%999) END,REPLICATE('X',80) FROM N;
CREATE INDEX IX_OPT003_Category ON lab.SkewData(CategoryId);
UPDATE STATISTICS lab.SkewData IX_OPT003_Category WITH SAMPLE 1 PERCENT;
CREATE TABLE lab.Evidence(Stage varchar(16) PRIMARY KEY,RowsTotal bigint NOT NULL,RowsSampled bigint NOT NULL,Steps int NOT NULL,HotRows bigint NOT NULL);
PRINT 'SQLPERF_SUMMARY|PASS|OK';
