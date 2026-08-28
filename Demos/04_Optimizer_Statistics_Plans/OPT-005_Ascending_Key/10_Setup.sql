USE [master];SET NOCOUNT ON;SET XACT_ABORT ON;DECLARE @R varchar(20)='$(RunToken)',@T sysname=N'$(TargetDatabase)',@S nvarchar(max),@C int=CASE TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')) WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
IF '$(DemoId)'<>'OPT-005' OR @T<>N'SQLPERF_LAB_OPT005_'+@R OR @C IS NULL THROW 51000,'FAIL_CONTRACT: OPT-005-Setupziel ist ungueltig.',1;IF DB_ID(@T) IS NOT NULL THROW 51002,'FAIL_STATE: OPT-005-Zieldatenbank existiert.',1;
SET @S=N'CREATE DATABASE '+QUOTENAME(@T)+N';ALTER DATABASE '+QUOTENAME(@T)+N' SET RECOVERY SIMPLE;ALTER DATABASE '+QUOTENAME(@T)+N' SET COMPATIBILITY_LEVEL='+CONVERT(nvarchar(3),@C)+N';ALTER DATABASE '+QUOTENAME(@T)+N' SET AUTO_UPDATE_STATISTICS ON;ALTER DATABASE '+QUOTENAME(@T)+N' SET AUTO_UPDATE_STATISTICS_ASYNC OFF;';EXEC(@S);
SET @S=N'USE '+QUOTENAME(@T)+N';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=N''OPT-005'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@R;';EXEC sys.sp_executesql @S,N'@R varchar(20)',@R=@R;
GO
USE [$(TargetDatabase)];IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');CREATE TABLE lab.AscendingData(EventId int NOT NULL CONSTRAINT PK_OPT005 PRIMARY KEY,EventDate date NOT NULL,Payload char(40) NOT NULL);
;WITH D(n) AS(SELECT n FROM(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))v(n)),N(n) AS(SELECT TOP(100000) ROW_NUMBER() OVER(ORDER BY(SELECT NULL)) FROM D a CROSS JOIN D b CROSS JOIN D c CROSS JOIN D d CROSS JOIN D e)
INSERT lab.AscendingData SELECT n,DATEADD(day,(n-1)/1000,CONVERT(date,'2025-01-01')),REPLICATE('A',40) FROM N;
CREATE INDEX IX_OPT005_Date ON lab.AscendingData(EventDate);UPDATE STATISTICS lab.AscendingData IX_OPT005_Date WITH FULLSCAN;
CREATE TABLE lab.Evidence(Stage varchar(20) PRIMARY KEY,RowsTotal bigint NOT NULL,ModificationCounter bigint NOT NULL,MaximumDate date NOT NULL,LastUpdated datetime2 NULL,AsyncEnabled bit NOT NULL);
PRINT 'SQLPERF_SUMMARY|PASS|OK';
