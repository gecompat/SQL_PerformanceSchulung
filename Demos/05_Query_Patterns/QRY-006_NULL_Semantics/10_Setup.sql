/* QRY-006 setup: small, deterministic Parent/Child counterexample. */
USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7) = '$(DemoId)';
DECLARE @RunToken varchar(20) = '$(RunToken)';
DECLARE @TargetDatabase sysname = N'$(TargetDatabase)';
DECLARE @ExpectedDatabase sysname = CONVERT(sysname, N'SQLPERF_LAB_' + REPLACE(@DemoId, '-', '') + N'_' + @RunToken);
DECLARE @MajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @CompatibilityLevel int = CASE @MajorVersion WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
DECLARE @Sql nvarchar(max);
DECLARE @Project nvarchar(max);
DECLARE @Contract nvarchar(max);
DECLARE @ExistingDemo nvarchar(max);
DECLARE @ExistingRun nvarchar(max);

IF @DemoId <> 'QRY-006' OR @TargetDatabase <> @ExpectedDatabase OR @CompatibilityLevel IS NULL
    THROW 51000, 'FAIL_CONTRACT: QRY-006-Zielkennung oder Engine-Version ist ungültig.', 1;

IF DB_ID(@TargetDatabase) IS NULL
BEGIN
    SET @Sql = N'CREATE DATABASE ' + QUOTENAME(@TargetDatabase) + N';';
    EXEC sys.sp_executesql @Sql;
    SET @Sql = N'USE ' + QUOTENAME(@TargetDatabase) + N';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'', @value=N''SQL_PerformanceSchulung'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'', @value=N''1.0'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'', @value=@DemoId;
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'', @value=@RunToken;';
    EXEC sys.sp_executesql @Sql, N'@DemoId varchar(7), @RunToken varchar(20)', @DemoId, @RunToken;
END
ELSE
BEGIN
    SET @Sql = N'SELECT @ProjectOut=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max), value) END),
@ContractOut=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max), value) END),
@DemoOut=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max), value) END),
@RunOut=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max), value) END)
FROM ' + QUOTENAME(@TargetDatabase) + N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
    EXEC sys.sp_executesql @Sql, N'@ProjectOut nvarchar(max) OUTPUT, @ContractOut nvarchar(max) OUTPUT, @DemoOut nvarchar(max) OUTPUT, @RunOut nvarchar(max) OUTPUT',
         @ProjectOut=@Project OUTPUT, @ContractOut=@Contract OUTPUT, @DemoOut=@ExistingDemo OUTPUT, @RunOut=@ExistingRun OUTPUT;
    -- NULL, abweichende Schreibweise und angehängte Zeichen verweigern die Wiederverwendung.
    IF @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2 <> N'SQL_PerformanceSchulung' OR DATALENGTH(@Project) <> DATALENGTH(N'SQL_PerformanceSchulung')
       OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2 <> N'1.0' OR DATALENGTH(@Contract) <> DATALENGTH(N'1.0')
       OR @ExistingDemo IS NULL OR @ExistingDemo COLLATE Latin1_General_100_BIN2 <> CONVERT(nvarchar(max), @DemoId) OR DATALENGTH(@ExistingDemo) <> DATALENGTH(CONVERT(nvarchar(max), @DemoId))
       OR @ExistingRun IS NULL OR @ExistingRun COLLATE Latin1_General_100_BIN2 <> CONVERT(nvarchar(max), @RunToken) OR DATALENGTH(@ExistingRun) <> DATALENGTH(CONVERT(nvarchar(max), @RunToken))
        THROW 51002, 'FAIL_STATE: Eine gleichnamige Datenbank besitzt nicht die erwarteten Eigentumsmarker.', 1;
END;

SET @Sql = N'ALTER DATABASE ' + QUOTENAME(@TargetDatabase) + N' SET COMPATIBILITY_LEVEL = ' + CONVERT(nvarchar(10), @CompatibilityLevel) + N';';
EXEC sys.sp_executesql @Sql;
GO

USE [$(TargetDatabase)];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;

IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
DROP TABLE IF EXISTS lab.Qry006Child;
DROP TABLE IF EXISTS lab.Qry006Parent;

CREATE TABLE lab.Qry006Parent (ParentKey int NOT NULL CONSTRAINT PK_Qry006Parent PRIMARY KEY);
CREATE TABLE lab.Qry006Child (ChildKey int NULL);

INSERT lab.Qry006Parent (ParentKey) VALUES (1), (2), (3);
INSERT lab.Qry006Child (ChildKey) VALUES (1), (NULL);

IF (SELECT COUNT(*) FROM lab.Qry006Parent) <> 3
   OR (SELECT COUNT(*) FROM lab.Qry006Child) <> 2
   OR (SELECT COUNT(*) FROM lab.Qry006Child WHERE ChildKey IS NULL) <> 1
    THROW 51002, 'FAIL_STATE: Die QRY-006-Parent-/Child-Menge entspricht nicht dem Ergebnisvertrag.', 1;

SELECT 1 AS Sequence, 'SETUP' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       N'Parent={1,2,3}; Child={1,NULL}' AS ObservedValue,
       N'3 Parent-Zeilen und genau 2 Child-Zeilen mit exakt einem NULL' AS RequiredValue,
       N'Das synthetische Gegenbeispiel ist eingerichtet.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
