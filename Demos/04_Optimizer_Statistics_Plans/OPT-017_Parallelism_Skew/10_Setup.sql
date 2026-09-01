/* OPT-017 setup: marker-protected database and deterministic PARALLEL profile. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @Expected sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken);
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')),@Compatibility int=CASE TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')) WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
DECLARE @Created bit=0,@Sql nvarchar(max),@Project nvarchar(128),@Contract nvarchar(32),@ExistingDemo varchar(7),@ExistingRun varchar(20);
IF @DemoId<>'OPT-017' OR @TargetDatabase<>@Expected OR @Compatibility IS NULL THROW 51000,'FAIL_CONTRACT: OPT-017-Zielkennung ist ungueltig.',1;
IF DB_ID(@TargetDatabase) IS NULL BEGIN SET @Sql=N'CREATE DATABASE '+QUOTENAME(@TargetDatabase)+N';';EXEC sys.sp_executesql @Sql;SET @Created=1;END;
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET RECOVERY SIMPLE;ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_CLOSE OFF;ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_SHRINK OFF;ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET PAGE_VERIFY CHECKSUM;ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET COMPATIBILITY_LEVEL='+CONVERT(nvarchar(10),@Compatibility)+N';USE '+QUOTENAME(@TargetDatabase)+N';ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS = ON;USE [master];';
EXEC sys.sp_executesql @Sql;
IF @Created=1 BEGIN
  SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=@Demo;EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@Run;';
  EXEC sys.sp_executesql @Sql,N'@Demo varchar(7),@Run varchar(20)',@Demo=@DemoId,@Run=@RunToken;
END ELSE BEGIN
  SET @Sql=N'SELECT @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),@ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(32),value) END),@DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(varchar(7),value) END),@RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(varchar(20),value) END) FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
  EXEC sys.sp_executesql @Sql,N'@ProjectOut nvarchar(128) OUTPUT,@ContractOut nvarchar(32) OUTPUT,@DemoOut varchar(7) OUTPUT,@RunOut varchar(20) OUTPUT',@ProjectOut=@Project OUTPUT,@ContractOut=@Contract OUTPUT,@DemoOut=@ExistingDemo OUTPUT,@RunOut=@ExistingRun OUTPUT;
  IF @Project<>N'SQL_PerformanceSchulung' OR @Contract<>N'1.0' OR @ExistingDemo<>@DemoId OR @ExistingRun<>@RunToken THROW 51002,'FAIL_STATE: Gleichnamige Datenbank ohne passende Eigentumsmarker.',1;
END;
GO

USE [$(TargetDatabase)];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
DROP PROCEDURE IF EXISTS lab.usp_Opt017Aggregate;
DROP TABLE IF EXISTS lab.Opt017Evidence;
DROP TABLE IF EXISTS lab.ParallelFact;
DROP TABLE IF EXISTS lab.DemoControl;

CREATE TABLE lab.DemoControl(StopRequested bit NOT NULL CONSTRAINT DF_Opt017_Stop DEFAULT(0),UpdatedUtc datetime2(3) NOT NULL CONSTRAINT DF_Opt017_Updated DEFAULT SYSUTCDATETIME());
INSERT lab.DemoControl(StopRequested) VALUES(0);
CREATE TABLE lab.ParallelFact(ProfileCode char(1) NOT NULL,FactId int NOT NULL,GroupKey int NOT NULL,MeasureValue int NOT NULL,Payload char(40) NOT NULL,CONSTRAINT PK_Opt017_ParallelFact PRIMARY KEY CLUSTERED(ProfileCode,FactId));
CREATE TABLE lab.Opt017Evidence(Phase varchar(16) NOT NULL CONSTRAINT PK_Opt017_Evidence PRIMARY KEY,ProfileCode char(1) NOT NULL,RequestedDop int NOT NULL,ActualDop int NULL,ExchangeCount int NULL,ActiveThreads int NULL,MinimumThreadRows bigint NULL,MaximumThreadRows bigint NULL,SkewRatio decimal(19,4) NULL,ResultChecksum int NULL,ResultRows bigint NULL,ResultMeasure bigint NULL,CapturedAtUtc datetime2(3) NOT NULL CONSTRAINT DF_Opt017_Captured DEFAULT SYSUTCDATETIME());

;WITH Digits AS(SELECT n FROM(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))d(n)),Numbers AS(SELECT TOP(600000) n=1+d0.n+d1.n*10+d2.n*100+d3.n*1000+d4.n*10000+d5.n*100000 FROM Digits d0 CROSS JOIN Digits d1 CROSS JOIN Digits d2 CROSS JOIN Digits d3 CROSS JOIN Digits d4 CROSS JOIN Digits d5 ORDER BY 1)
INSERT lab.ParallelFact(ProfileCode,FactId,GroupKey,MeasureValue,Payload)
SELECT 'B',n,n%4096,n%1000,CONVERT(char(40),REPLICATE(CHAR(65+n%26),40)) FROM Numbers
UNION ALL
SELECT 'S',n,CASE WHEN n%100<95 THEN 1 ELSE n%4096 END,n%1000,CONVERT(char(40),REPLICATE(CHAR(65+n%26),40)) FROM Numbers
OPTION(MAXDOP 1);
GO

CREATE OR ALTER PROCEDURE lab.usp_Opt017Aggregate
  @ProfileCode char(1),@RequestedDop int,@ResultChecksum int OUTPUT,@ResultRows bigint OUTPUT,@ResultMeasure bigint OUTPUT
AS
BEGIN
  SET NOCOUNT ON;
  IF EXISTS(SELECT 1 FROM lab.DemoControl WHERE StopRequested=1) THROW 51008,'FAIL_TIMEOUT: OPT-017-Kill-Switch ist gesetzt.',1;
  IF @RequestedDop=1
    SELECT @ResultChecksum=CHECKSUM_AGG(BINARY_CHECKSUM(GroupKey,[RowCount],TotalMeasure)),@ResultRows=SUM([RowCount]),@ResultMeasure=SUM(TotalMeasure)
    FROM
    (
      SELECT GroupKey,COUNT_BIG(*)/16 [RowCount],SUM(CONVERT(bigint,MeasureValue))/16 TotalMeasure
      FROM lab.ParallelFact
      CROSS JOIN(VALUES(1),(2),(3),(4),(5),(6),(7),(8),(9),(10),(11),(12),(13),(14),(15),(16)) AS multiplier(Sequence)
      WHERE ProfileCode=@ProfileCode
      GROUP BY GroupKey
    )g OPTION(MAXDOP 1);
  ELSE
    SELECT @ResultChecksum=CHECKSUM_AGG(BINARY_CHECKSUM(GroupKey,[RowCount],TotalMeasure)),@ResultRows=SUM([RowCount]),@ResultMeasure=SUM(TotalMeasure)
    FROM
    (
      SELECT GroupKey,COUNT_BIG(*)/16 [RowCount],SUM(CONVERT(bigint,MeasureValue))/16 TotalMeasure
      FROM lab.ParallelFact
      CROSS JOIN(VALUES(1),(2),(3),(4),(5),(6),(7),(8),(9),(10),(11),(12),(13),(14),(15),(16)) AS multiplier(Sequence)
      WHERE ProfileCode=@ProfileCode
      GROUP BY GroupKey
    )g OPTION(MAXDOP 4);
END;
GO

IF (SELECT COUNT_BIG(*) FROM lab.ParallelFact)<>1200000 THROW 51003,'FAIL_EXECUTION: Das PARALLEL-Datenprofil ist unvollstaendig.',1;
SELECT 1 Sequence,'SETUP' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,N'je 600000 balancierte und konzentrierte Zeilen' ObservedValue,N'identische Zeilenzahl; deterministische Verteilung; kooperativer Kill-Switch' RequiredValue,N'OPT-017 ist aufgebaut.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
GO
