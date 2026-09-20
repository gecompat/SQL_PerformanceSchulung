/* DGN-007: unabhängiger synthetischer Datenaufbau, ohne Adapter oder Incidentbehauptung. */
USE [master];
SET NOCOUNT ON;
SET XACT_ABORT ON;
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
DECLARE @Compatibility int=CASE @Major WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
DECLARE @Sql nvarchar(max);
IF '$(DemoId)' <> 'DGN-007' OR '$(RunToken)' <> 'AUTO'
   OR N'$(TargetDatabase)' <> N'SQLPERF_LAB_DGN007_AUTO' OR @Compatibility IS NULL
    THROW 51000,'FAIL_CONTRACT: Ungültige DGN-007-Kennung oder Engine-Version.',1;
IF '$(ConfirmIsolatedLab)' <> '1' OR '$(HighImpactConfirmed)' <> '1'
   OR COALESCE(TRY_CONVERT(int,'$(MaximumRuntimeSeconds)'),0) NOT BETWEEN 1 AND 180
    THROW 51001,'FAIL_SAFETY: Der Datenaufbau benötigt die Lab-Bestätigung und ein begrenztes Zeitbudget.',1;
IF @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2
    THROW 51001,'FAIL_SAFETY: Datenbankanlage innerhalb einer Transaktion ist unzulässig.',1;
IF EXISTS(SELECT 1 FROM sys.databases WHERE database_id>4)
    THROW 51002,'FAIL_STATE: Der Datenaufbau übernimmt keine vorhandene Benutzerdatenbank.',1;

CREATE DATABASE [SQLPERF_LAB_DGN007_AUTO];
/* Marker werden vor Daten- oder Konfigurationsänderungen angelegt. */
EXEC [SQLPERF_LAB_DGN007_AUTO].sys.sp_addextendedproperty @name=N'SQLPERF.Project',@value=N'SQL_PerformanceSchulung';
EXEC [SQLPERF_LAB_DGN007_AUTO].sys.sp_addextendedproperty @name=N'SQLPERF.ContractVersion',@value=N'1.0';
EXEC [SQLPERF_LAB_DGN007_AUTO].sys.sp_addextendedproperty @name=N'SQLPERF.DemoId',@value=N'DGN-007';
EXEC [SQLPERF_LAB_DGN007_AUTO].sys.sp_addextendedproperty @name=N'SQLPERF.RunToken',@value=N'AUTO';
ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET RECOVERY SIMPLE;
ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET AUTO_CLOSE OFF;
ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET AUTO_SHRINK OFF;
ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET PAGE_VERIFY CHECKSUM;
SET @Sql=N'ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET COMPATIBILITY_LEVEL = '+CONVERT(nvarchar(3),@Compatibility)+N';';
EXEC sys.sp_executesql @Sql;
GO
USE [SQLPERF_LAB_DGN007_AUTO];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
EXEC sys.sp_executesql N'CREATE SCHEMA lab AUTHORIZATION dbo;';
CREATE TABLE dbo.CaseGroup(GroupKey int NOT NULL PRIMARY KEY,GroupLabel nvarchar(64) NOT NULL);
CREATE TABLE dbo.CaseItem(
    ItemId int NOT NULL CONSTRAINT PK_CaseItem PRIMARY KEY NONCLUSTERED,
    GroupKey int NOT NULL CONSTRAINT FK_CaseItem_CaseGroup REFERENCES dbo.CaseGroup(GroupKey),
    StatusCode tinyint NOT NULL,SearchValue nvarchar(64) NOT NULL,Payload binary(96) NOT NULL);
CREATE CLUSTERED INDEX CIX_CaseItem ON dbo.CaseItem(ItemId);
CREATE NONCLUSTERED INDEX IX_CaseItem_Group_Status ON dbo.CaseItem(GroupKey,StatusCode) INCLUDE(SearchValue);
CREATE TABLE dbo.CaseItemDetail(
    ItemId int NOT NULL,DetailOrdinal int NOT NULL,DetailPayload binary(128) NOT NULL,
    CONSTRAINT PK_CaseItemDetail PRIMARY KEY(ItemId,DetailOrdinal),
    CONSTRAINT FK_CaseItemDetail_CaseItem FOREIGN KEY(ItemId) REFERENCES dbo.CaseItem(ItemId));
CREATE TABLE dbo.CaseRequestLog(
    RequestLogId bigint IDENTITY(1,1) NOT NULL CONSTRAINT PK_CaseRequestLog PRIMARY KEY NONCLUSTERED,
    GroupKey int NOT NULL,StatusCode tinyint NOT NULL,RequestedUtc datetime2(0) NOT NULL);
CREATE CLUSTERED INDEX CIX_CaseRequestLog ON dbo.CaseRequestLog(RequestLogId);

/* Explizite ItemId aus n: keine Abhängigkeit von INSERT-Reihenfolge oder IDENTITY-Zuteilung. */
;WITH Digits(n) AS (SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) d(n))
SELECT 1+a.n+10*b.n+100*c.n+1000*d.n+10000*e.n AS n
INTO #Numbers FROM Digits a CROSS JOIN Digits b CROSS JOIN Digits c CROSS JOIN Digits d CROSS JOIN Digits e;
INSERT dbo.CaseGroup(GroupKey,GroupLabel)
SELECT n,N'Group'+CONVERT(nvarchar(11),n) FROM #Numbers WHERE n BETWEEN 1 AND 12;
INSERT dbo.CaseItem(ItemId,GroupKey,StatusCode,SearchValue,Payload)
SELECT n,CASE WHEN n<=16000 THEN 1+((n-1)%4) WHEN n<=22000 THEN 5+((n-16001)%3) ELSE 8+((n-22001)%5) END,
       CASE WHEN n%7=0 THEN 1 WHEN n%7 IN(3,5) THEN 2 ELSE 3 END,
       N'Search'+CONVERT(nvarchar(11),n),CONVERT(binary(96),REPLICATE(CONVERT(binary(1),0x5A),96))
FROM #Numbers WHERE n BETWEEN 1 AND 24000;
INSERT dbo.CaseItemDetail(ItemId,DetailOrdinal,DetailPayload)
SELECT i.ItemId,n.n,CONVERT(binary(128),REPLICATE(CONVERT(binary(1),0x41),128))
FROM dbo.CaseItem i CROSS JOIN #Numbers n WHERE n.n BETWEEN 1 AND 3;
DROP TABLE #Numbers;
GO
CREATE OR ALTER PROCEDURE dbo.usp_CaseSearch @GroupKey int,@StatusCode tinyint
AS
BEGIN
    SET NOCOUNT ON;
    SELECT /* DGN007_CASE_SEARCH */ i.ItemId,i.SearchValue,i.StatusCode,g.GroupLabel,
           (SELECT COUNT(*) FROM dbo.CaseItemDetail d WHERE d.ItemId=i.ItemId) AS DetailCount
    FROM dbo.CaseItem i JOIN dbo.CaseGroup g ON g.GroupKey=i.GroupKey
    WHERE i.GroupKey=@GroupKey AND i.StatusCode=@StatusCode
    ORDER BY i.ItemId;
    INSERT dbo.CaseRequestLog(GroupKey,StatusCode,RequestedUtc) VALUES(@GroupKey,@StatusCode,SYSUTCDATETIME());
END;
GO
PRINT 'SQLPERF_SUMMARY|PASS|OK';
