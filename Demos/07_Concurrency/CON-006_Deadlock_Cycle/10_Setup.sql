USE [master];SET NOCOUNT ON;SET XACT_ABORT ON;DECLARE @R varchar(20)='$(RunToken)',@T sysname=N'$(TargetDatabase)',@S nvarchar(max),@C int=CASE TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')) WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
IF '$(DemoId)'<>'CON-006' OR @T<>N'SQLPERF_LAB_CON006_'+@R OR @C IS NULL THROW 51000,'FAIL_CONTRACT: CON-006-Setupziel ist ungueltig.',1;IF DB_ID(@T) IS NOT NULL THROW 51002,'FAIL_STATE: CON-006-Zieldatenbank existiert.',1;
SET @S=N'CREATE DATABASE '+QUOTENAME(@T)+N';ALTER DATABASE '+QUOTENAME(@T)+N' SET RECOVERY SIMPLE;ALTER DATABASE '+QUOTENAME(@T)+N' SET COMPATIBILITY_LEVEL='+CONVERT(nvarchar(3),@C)+N';';EXEC(@S);SET @S=N'USE '+QUOTENAME(@T)+N';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=N''CON-006'';EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@R;';EXEC sys.sp_executesql @S,N'@R varchar(20)',@R=@R;
GO
USE [$(TargetDatabase)];IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');IF SCHEMA_ID(N'fwk') IS NULL EXEC(N'CREATE SCHEMA fwk AUTHORIZATION dbo;');
CREATE TABLE lab.DeadlockRows(RowId int PRIMARY KEY,Value int NOT NULL);INSERT lab.DeadlockRows VALUES(1,0),(2,0);
CREATE TABLE lab.Evidence(RoleName varchar(16) NOT NULL,Outcome varchar(16) NOT NULL,ErrorNumber int NULL,CapturedAtUtc datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME());
CREATE TABLE fwk.SessionSignal(DemoId varchar(7),RunToken varchar(20),SignalName varchar(64),SignaledAtUtc datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME(),PRIMARY KEY(DemoId,RunToken,SignalName));
GO
CREATE OR ALTER PROCEDURE fwk.USP_Signal @DemoId varchar(7),@RunToken varchar(20),@SignalName varchar(64) AS BEGIN SET NOCOUNT ON;UPDATE fwk.SessionSignal SET SignaledAtUtc=SYSUTCDATETIME() WHERE DemoId=@DemoId AND RunToken=@RunToken AND SignalName=@SignalName;IF @@ROWCOUNT=0 INSERT fwk.SessionSignal(DemoId,RunToken,SignalName)VALUES(@DemoId,@RunToken,@SignalName);END;
GO
CREATE OR ALTER PROCEDURE fwk.USP_WaitForSignal @DemoId varchar(7),@RunToken varchar(20),@SignalName varchar(64),@TimeoutMs int AS BEGIN SET NOCOUNT ON;DECLARE @S datetime2(3)=SYSUTCDATETIME();WHILE NOT EXISTS(SELECT 1 FROM fwk.SessionSignal WITH(READUNCOMMITTED) WHERE DemoId=@DemoId AND RunToken=@RunToken AND SignalName=@SignalName)BEGIN IF DATEDIFF_BIG(millisecond,@S,SYSUTCDATETIME())>=@TimeoutMs THROW 51005,'FAIL_TIMEOUT: CON-006-Signal fehlt.',1;WAITFOR DELAY '00:00:00.050';END;END;
GO
PRINT 'SQLPERF_SUMMARY|PASS|OK';
