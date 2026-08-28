/* DGN-003 setup: marker-owned database, deterministic skew and bounded Query Store. */
USE [master]; GO
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)',@Sql nvarchar(max),@Created bit=0;
DECLARE @Expected sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken),@Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')),@Cl int;
SET @Cl=CASE @Major WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
IF @DemoId<>'DGN-003' OR @TargetDatabase<>@Expected OR @Cl IS NULL THROW 51000,'FAIL_CONTRACT: DGN-003-Setupziel ist ungültig.',1;
IF DB_ID(@TargetDatabase) IS NULL BEGIN SET @Sql=N'CREATE DATABASE '+QUOTENAME(@TargetDatabase)+N';'; EXEC sys.sp_executesql @Sql; SET @Created=1; END
ELSE THROW 51002,'FAIL_STATE: DGN-003 übernimmt keine vorhandene Datenbank.',1;
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET RECOVERY SIMPLE; ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET COMPATIBILITY_LEVEL = '+CONVERT(nvarchar(10),@Cl)+N';'; EXEC sys.sp_executesql @Sql;
SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=@DemoId;
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@RunToken;';
EXEC sys.sp_executesql @Sql,N'@DemoId varchar(7),@RunToken varchar(20)',@DemoId,@RunToken;
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET QUERY_STORE = ON (OPERATION_MODE = READ_WRITE, MAX_STORAGE_SIZE_MB = 128, INTERVAL_LENGTH_MINUTES = 1, QUERY_CAPTURE_MODE = ALL, SIZE_BASED_CLEANUP_MODE = AUTO, DATA_FLUSH_INTERVAL_SECONDS = 60);'; EXEC sys.sp_executesql @Sql;
GO
USE [$(TargetDatabase)]; GO
SET NOCOUNT ON; SET XACT_ABORT ON;
IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
CREATE TABLE lab.SearchData(Id int NOT NULL CONSTRAINT PK_Dgn003 PRIMARY KEY,GroupId int NOT NULL,Payload char(120) NOT NULL);
CREATE INDEX IX_Dgn003_GroupId ON lab.SearchData(GroupId);
WITH n AS (SELECT TOP (50000) ROW_NUMBER() OVER(ORDER BY (SELECT NULL)) rn FROM sys.all_objects a CROSS JOIN sys.all_objects b)
INSERT lab.SearchData(Id,GroupId,Payload) SELECT rn,CASE WHEN rn<=45000 THEN 1 ELSE 2+(rn%98) END,REPLICATE(CHAR(65+(rn%26)),120) FROM n;
CREATE TABLE lab.QueryStoreEvidence(Phase varchar(20) NOT NULL,RowCount bigint NOT NULL,ChecksumValue int NULL,QueryCount int NULL,PlanCount int NULL,RuntimeRows int NULL,WaitRows int NULL);
EXEC(N'CREATE OR ALTER PROCEDURE lab.usp_Dgn003Search @GroupId int AS SELECT Id,GroupId FROM lab.SearchData WHERE GroupId=@GroupId OPTION (MAXDOP 1);');
SELECT 1 Sequence,'SETUP' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'Rows=',COUNT_BIG(*)) ObservedValue,N'50000 synthetische Zeilen; Query Store READ_WRITE' RequiredValue,N'DGN-003 ist vorbereitet.' Message FROM lab.SearchData;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
