/* QRY-019: Feste SQL-Struktur, Parameterbindung und eingeschraenkte Rechte; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)', @RunToken varchar(16)='$(RunToken)', @TargetDatabase sysname=N'$(TargetDatabase)';
IF @DemoId <> 'QRY-019' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 16
 OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9]%'
 OR CONVERT(varbinary(max),@TargetDatabase) <> CONVERT(varbinary(max),CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken))
 THROW 51000,'FAIL_CONTRACT: Demo-ID, Run-Token oder Zieldatenbank ist ungueltig.',1;
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@ExistingDemo nvarchar(max),@ExistingRun nvarchar(max),@Sql nvarchar(max);
IF DB_ID(@TargetDatabase) IS NOT NULL
BEGIN
 SET @Sql=N'SELECT @P=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
 @C=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
 @D=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
 @R=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
 FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
 EXEC sys.sp_executesql @Sql,N'@P nvarchar(max) OUTPUT,@C nvarchar(max) OUTPUT,@D nvarchar(max) OUTPUT,@R nvarchar(max) OUTPUT',@P=@Project OUTPUT,@C=@Contract OUTPUT,@D=@ExistingDemo OUTPUT,@R=@ExistingRun OUTPUT;
 IF CONVERT(varbinary(max),ISNULL(@Project,N'')) <> CONVERT(varbinary(max),N'SQL_PerformanceSchulung')
 OR CONVERT(varbinary(max),ISNULL(@Contract,N'')) <> CONVERT(varbinary(max),N'1.0')
 OR CONVERT(varbinary(max),ISNULL(@ExistingDemo,N'')) <> CONVERT(varbinary(max),CONVERT(nvarchar(max),@DemoId))
 OR CONVERT(varbinary(max),ISNULL(@ExistingRun,N'')) <> CONVERT(varbinary(max),CONVERT(nvarchar(max),@RunToken))
 THROW 51004,'FAIL_STATE: Eigentumsmarker stimmen nicht vollstaendig und exakt ueberein.',1;
END;
IF DB_ID(@TargetDatabase) IS NULL
BEGIN
 SET @Sql=N'CREATE DATABASE '+QUOTENAME(@TargetDatabase)+N';'; EXEC sys.sp_executesql @Sql;
 SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=@D;
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@R;';
 EXEC sys.sp_executesql @Sql,N'@D varchar(7),@R varchar(16)',@D=@DemoId,@R=@RunToken;
END;
-- Marker wurden vor jeder Aenderung an einer vorhandenen Datenbank validiert.
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET COMPATIBILITY_LEVEL=170;
 ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET RECOVERY SIMPLE;
 ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_CLOSE OFF;
 ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_SHRINK OFF;';
EXEC sys.sp_executesql @Sql;
DECLARE @LogicalName sysname,@FileType int;
DECLARE OwnFiles CURSOR LOCAL FAST_FORWARD FOR SELECT name,type FROM sys.master_files WHERE database_id=DB_ID(@TargetDatabase) AND type IN (0,1);
OPEN OwnFiles; FETCH NEXT FROM OwnFiles INTO @LogicalName,@FileType;
WHILE @@FETCH_STATUS=0
BEGIN
 SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' MODIFY FILE (NAME='+QUOTENAME(@LogicalName,N'''')+N',MAXSIZE='+CASE WHEN @FileType=0 THEN N'256MB' ELSE N'64MB' END+N',FILEGROWTH=16MB);';
 EXEC sys.sp_executesql @Sql;
 FETCH NEXT FROM OwnFiles INTO @LogicalName,@FileType;
END;
CLOSE OwnFiles; DEALLOCATE OwnFiles;
GO
USE [$(TargetDatabase)];
GO
SET NOCOUNT ON; SET XACT_ABORT ON;
IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
DROP PROCEDURE IF EXISTS lab.RunControls;
DROP VIEW IF EXISTS lab.InputPolicy;
DROP TABLE IF EXISTS lab.Candidates;
DROP TABLE IF EXISTS lab.Inventory;
IF USER_ID(N'QRY019_reader') IS NOT NULL DROP USER [QRY019_reader];
CREATE TABLE lab.Inventory(ModuleCode nvarchar(200) NOT NULL PRIMARY KEY,Colour nvarchar(20) NOT NULL);
INSERT lab.Inventory VALUES(N'MOD-A',N'blue'),(N'MOD-B',N'green'),(N'MOD-A''; DROP TABLE lab.Inventory;--',N'literal');
CREATE USER [QRY019_reader] WITHOUT LOGIN;
GRANT SELECT ON OBJECT::lab.Inventory TO [QRY019_reader];
CREATE TABLE lab.Candidates(Id int PRIMARY KEY,StatementText nvarchar(max),IdentifierText nvarchar(max),ValueText nvarchar(max));
DECLARE @Canonical nvarchar(max)=N'SELECT Colour FROM lab.Inventory WHERE ModuleCode=@ModuleCode;';
INSERT lab.Candidates VALUES
(1,@Canonical,N'Inventory',N'MOD-A'),
(2,@Canonical,N'Inventory',N'MOD-A''; DROP TABLE lab.Inventory;--'),
(3,@Canonical+N' DROP TABLE lab.Inventory;',N'Inventory',N'MOD-A'),
(4,@Canonical,N'Inventory; DROP TABLE lab.Inventory;--',N'MOD-A'),
(5,@Canonical+N' ',N'Inventory',N'MOD-A'),
(6,NULL,N'Inventory',N'MOD-A'),
(7,@Canonical,N'Inventory'+REPLICATE(N'X',256),N'MOD-A'),
(8,@Canonical,N'Inventory',REPLICATE(N'X',201));
GO
CREATE VIEW lab.InputPolicy AS
SELECT *,CASE WHEN
 CONVERT(varbinary(max),StatementText)=CONVERT(varbinary(max),N'SELECT Colour FROM lab.Inventory WHERE ModuleCode=@ModuleCode;')
 AND CONVERT(varbinary(max),IdentifierText)=CONVERT(varbinary(max),N'Inventory')
 AND ValueText IS NOT NULL AND DATALENGTH(ValueText)<=400
 THEN CONVERT(bit,1) ELSE CONVERT(bit,0) END AS Allowed
FROM lab.Candidates;
GO
CREATE PROCEDURE lab.RunControls
AS
BEGIN
 SET NOCOUNT ON;
 DECLARE @Allowed int=(SELECT COUNT(*) FROM lab.InputPolicy WHERE Allowed=1),
  @Denied int=(SELECT COUNT(*) FROM lab.InputPolicy WHERE Allowed=0);
 IF (SELECT COUNT(*) FROM lab.InputPolicy)<>8 OR @Allowed<>2 OR @Denied<>6
  OR EXISTS(SELECT 1 FROM lab.InputPolicy WHERE Id NOT BETWEEN 1 AND 8 OR Allowed<>CASE WHEN Id IN(1,2) THEN 1 ELSE 0 END)
  THROW 51003,'FAIL_RESULT_CONTRACT: Nichtleere feste Policyfaelle verletzt.',1;
 -- Counts allein ersetzen keine sechs unterschiedlichen negativen Fallinhalte.
 DECLARE @Frozen TABLE(Id int PRIMARY KEY,StatementText nvarchar(max),IdentifierText nvarchar(max),ValueText nvarchar(max));
 DECLARE @FrozenCanonical nvarchar(max)=N'SELECT Colour FROM lab.Inventory WHERE ModuleCode=@ModuleCode;';
 INSERT @Frozen VALUES
 (1,@FrozenCanonical,N'Inventory',N'MOD-A'),
 (2,@FrozenCanonical,N'Inventory',N'MOD-A''; DROP TABLE lab.Inventory;--'),
 (3,@FrozenCanonical+N' DROP TABLE lab.Inventory;',N'Inventory',N'MOD-A'),
 (4,@FrozenCanonical,N'Inventory; DROP TABLE lab.Inventory;--',N'MOD-A'),
 (5,@FrozenCanonical+N' ',N'Inventory',N'MOD-A'),
 (6,NULL,N'Inventory',N'MOD-A'),
 (7,@FrozenCanonical,N'Inventory'+REPLICATE(N'X',256),N'MOD-A'),
 (8,@FrozenCanonical,N'Inventory',REPLICATE(N'X',201));
 IF EXISTS(SELECT Id,CONVERT(varbinary(max),StatementText),CONVERT(varbinary(max),IdentifierText),CONVERT(varbinary(max),ValueText) FROM lab.Candidates
  EXCEPT SELECT Id,CONVERT(varbinary(max),StatementText),CONVERT(varbinary(max),IdentifierText),CONVERT(varbinary(max),ValueText) FROM @Frozen)
  OR EXISTS(SELECT Id,CONVERT(varbinary(max),StatementText),CONVERT(varbinary(max),IdentifierText),CONVERT(varbinary(max),ValueText) FROM @Frozen
  EXCEPT SELECT Id,CONVERT(varbinary(max),StatementText),CONVERT(varbinary(max),IdentifierText),CONVERT(varbinary(max),ValueText) FROM lab.Candidates)
  THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige eingefrorene Fallinhalte verletzt.',1;
 -- Vor EXECUTE AS werden Inputs in lokale Tabellenvariablen kopiert; keine Grant-Ausweitung.
 DECLARE @Values TABLE(Id int PRIMARY KEY,StatementText nvarchar(max),IdentifierText nvarchar(max),ValueText nvarchar(max));
 INSERT @Values SELECT Id,StatementText,IdentifierText,ValueText FROM lab.InputPolicy WHERE Allowed=1;
 DECLARE @Rows TABLE(Colour nvarchar(20));
 DECLARE @Id int=1,@Statement nvarchar(max),@Identifier nvarchar(max),@Value nvarchar(max),@Bound nvarchar(200),@Expected nvarchar(20),
  @Canonical nvarchar(max)=N'SELECT Colour FROM lab.Inventory WHERE ModuleCode=@ModuleCode;',@Impersonating bit=0,@BoundCount int=0,@Denials int=0;
 BEGIN TRY
  EXECUTE AS USER=N'QRY019_reader'; SET @Impersonating=1;
  IF CONVERT(varbinary(max),USER_NAME())<>CONVERT(varbinary(max),N'QRY019_reader')
   THROW 51003,'FAIL_RESULT_CONTRACT: Falscher Ausfuehrungsbenutzer.',1;
  WHILE @Id<=2
  BEGIN
   SELECT @Statement=StatementText,@Identifier=IdentifierText,@Value=ValueText FROM @Values WHERE Id=@Id;
   IF @Statement IS NULL OR @Identifier IS NULL OR @Value IS NULL
    OR CONVERT(varbinary(max),@Statement)<>CONVERT(varbinary(max),@Canonical)
    OR CONVERT(varbinary(max),@Identifier)<>CONVERT(varbinary(max),N'Inventory') OR DATALENGTH(@Value)>400
    THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige Eingabebindung fehlt.',1;
   SET @Expected=CASE WHEN @Id=1 THEN N'blue' ELSE N'literal' END;
   SET @Bound=CONVERT(nvarchar(200),@Value);
   DELETE FROM @Rows;
   -- Ausschliesslich kanonischer SQL-Text; Modelltext/Identifier werden nie konkateniert.
   INSERT @Rows EXEC sys.sp_executesql @Canonical,N'@ModuleCode nvarchar(200)',@ModuleCode=@Bound;
   IF (SELECT COUNT(*) FROM @Rows)<>1 OR NOT EXISTS(SELECT 1 FROM @Rows WHERE CONVERT(varbinary(max),Colour)=CONVERT(varbinary(max),@Expected))
    THROW 51003,'FAIL_RESULT_CONTRACT: Parameterergebnis verletzt.',1;
   SET @BoundCount+=1; SET @Id+=1;
  END;
  -- Feste Gegenproben, niemals ein unkontrollierter Modellstring.
  BEGIN TRY
   EXEC(N'UPDATE lab.Inventory SET Colour=N''changed'' WHERE ModuleCode=N''MOD-A'';');
   THROW 51003,'FAIL_RESULT_CONTRACT: UPDATE unerwartet erlaubt.',1;
  END TRY BEGIN CATCH
   IF ERROR_NUMBER()<>229 THROW;
   SET @Denials+=1;
  END CATCH;
  BEGIN TRY
   EXEC(N'DROP TABLE lab.Inventory;');
   THROW 51003,'FAIL_RESULT_CONTRACT: DROP unerwartet erlaubt.',1;
  END TRY BEGIN CATCH
   IF ERROR_NUMBER() NOT IN(229,3701) THROW;
   SET @Denials+=1;
  END CATCH;
  BEGIN TRY
   EXEC(N'CREATE TABLE lab.Counterprobe(Id int);');
   THROW 51003,'FAIL_RESULT_CONTRACT: CREATE unerwartet erlaubt.',1;
  END TRY BEGIN CATCH
   IF ERROR_NUMBER()<>262 THROW;
   SET @Denials+=1;
  END CATCH;
  REVERT; SET @Impersonating=0;
 END TRY BEGIN CATCH
  IF @Impersonating=1 REVERT;
  THROW;
 END CATCH;
 IF @BoundCount<>2 OR @Denials<>3 OR OBJECT_ID(N'lab.Inventory',N'U') IS NULL OR OBJECT_ID(N'lab.Counterprobe',N'U') IS NOT NULL
  OR (SELECT COUNT(*) FROM lab.Inventory)<>3
  OR NOT EXISTS(SELECT 1 FROM lab.Inventory WHERE CONVERT(varbinary(max),ModuleCode)=CONVERT(varbinary(max),N'MOD-A') AND CONVERT(varbinary(max),Colour)=CONVERT(varbinary(max),N'blue'))
  OR NOT EXISTS(SELECT 1 FROM lab.Inventory WHERE CONVERT(varbinary(max),ModuleCode)=CONVERT(varbinary(max),N'MOD-B') AND CONVERT(varbinary(max),Colour)=CONVERT(varbinary(max),N'green'))
  OR NOT EXISTS(SELECT 1 FROM lab.Inventory WHERE CONVERT(varbinary(max),ModuleCode)=CONVERT(varbinary(max),N'MOD-A''; DROP TABLE lab.Inventory;--') AND CONVERT(varbinary(max),Colour)=CONVERT(varbinary(max),N'literal'))
  THROW 51003,'FAIL_RESULT_CONTRACT: Rechtegegenprobe oder unveraenderter Bestand fehlt.',1;
 PRINT CONCAT('AI_ASSERT|comparison|allowed_inputs|',@Allowed);
 PRINT CONCAT('AI_ASSERT|comparison|denied_inputs|',@Denied);
 PRINT CONCAT('AI_ASSERT|comparison|bound_values|',@BoundCount);
 PRINT CONCAT('AI_ASSERT|comparison|permission_denials|',@Denials);
END;
GO
PRINT 'SQLPERF_SUMMARY|PASS|OK';
