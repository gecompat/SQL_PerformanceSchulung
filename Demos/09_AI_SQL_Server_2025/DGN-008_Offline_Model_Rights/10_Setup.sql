/* DGN-008: External-Model-Metadaten und getrennte Offline-Rechte; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)', @RunToken varchar(16)='$(RunToken)', @TargetDatabase sysname=N'$(TargetDatabase)';
IF @DemoId <> 'DGN-008' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 16
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
DROP PROCEDURE IF EXISTS lab.ExerciseRights;
DROP PROCEDURE IF EXISTS lab.CheckState;
DROP TABLE IF EXISTS lab.Sources;
DROP TABLE IF EXISTS lab.EndpointPolicy;
DROP TABLE IF EXISTS lab.EndpointCandidates;
DROP TABLE IF EXISTS lab.ModelBinding;
DROP TABLE IF EXISTS lab.HostOptions;
IF EXISTS(SELECT 1 FROM sys.external_models WHERE name=N'DGN008_OfflineModel') EXEC(N'DROP EXTERNAL MODEL DGN008_OfflineModel;');
IF USER_ID(N'DGN008_setup') IS NOT NULL DROP USER DGN008_setup;
IF USER_ID(N'DGN008_ingestion') IS NOT NULL DROP USER DGN008_ingestion;
IF USER_ID(N'DGN008_reader') IS NOT NULL DROP USER DGN008_reader;
IF DATABASE_PRINCIPAL_ID(N'DGN008_setupRole') IS NOT NULL DROP ROLE DGN008_setupRole;
IF DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole') IS NOT NULL DROP ROLE DGN008_ingestionRole;
IF DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole') IS NOT NULL DROP ROLE DGN008_retrievalRole;
GO
CREATE TABLE lab.Sources(Id int PRIMARY KEY,FactDays int NOT NULL);
INSERT lab.Sources VALUES(1,7);
CREATE TABLE lab.EndpointPolicy(Id int PRIMARY KEY,Location nvarchar(200) NOT NULL,CredentialAlias nvarchar(80) NOT NULL);
INSERT lab.EndpointPolicy VALUES(1,N'https://model.example.invalid/v1/embeddings',N'SYNTHETIC_NO_SECRET');
CREATE TABLE lab.EndpointCandidates(Id int PRIMARY KEY,Location nvarchar(200) NOT NULL);
INSERT lab.EndpointCandidates VALUES(1,N'https://model.example.invalid/v1/embeddings'),(2,N'http://model.example.invalid/v1/embeddings'),(3,N'https://foreign.example.invalid/v1/embeddings'),(4,N'https://model.example.invalid/v1/embeddings ');
CREATE TABLE lab.HostOptions(NameBytes varbinary(256) PRIMARY KEY,ConfiguredValue int NOT NULL,ActiveValue int NOT NULL);
INSERT lab.HostOptions SELECT CONVERT(varbinary(256),name),CONVERT(int,value),CONVERT(int,value_in_use) FROM sys.configurations;
CREATE ROLE DGN008_setupRole AUTHORIZATION dbo;
CREATE ROLE DGN008_ingestionRole AUTHORIZATION dbo;
CREATE ROLE DGN008_retrievalRole AUTHORIZATION dbo;
CREATE USER DGN008_setup WITHOUT LOGIN;
CREATE USER DGN008_ingestion WITHOUT LOGIN;
CREATE USER DGN008_reader WITHOUT LOGIN;
ALTER ROLE DGN008_setupRole ADD MEMBER DGN008_setup;
ALTER ROLE DGN008_ingestionRole ADD MEMBER DGN008_ingestion;
ALTER ROLE DGN008_retrievalRole ADD MEMBER DGN008_reader;
GRANT CREATE EXTERNAL MODEL TO DGN008_setupRole;
GRANT SELECT,UPDATE ON OBJECT::lab.Sources TO DGN008_ingestionRole;
GRANT SELECT ON OBJECT::lab.Sources TO DGN008_retrievalRole;
-- Bewusst zusaetzliche initiale Retrievalgrants; MITIGATION nimmt nur diese zurueck.
GRANT SELECT ON OBJECT::lab.EndpointPolicy TO DGN008_retrievalRole;
DECLARE @Impersonating bit=0;
BEGIN TRY
 EXECUTE AS USER=N'DGN008_setup';SET @Impersonating=1;
 -- Ausschliesslich Objekt-DDL: kein Embedding-/REST-Aufruf und kein Credential.
 EXEC(N'CREATE EXTERNAL MODEL DGN008_OfflineModel WITH(LOCATION=''https://model.example.invalid/v1/embeddings'',API_FORMAT=''OpenAI'',MODEL_TYPE=EMBEDDINGS,MODEL=''synthetic-model'');');
 REVERT;SET @Impersonating=0;
END TRY BEGIN CATCH IF @Impersonating=1 REVERT;THROW;END CATCH;
GRANT EXECUTE ON EXTERNAL MODEL::DGN008_OfflineModel TO DGN008_ingestionRole;
GRANT EXECUTE ON EXTERNAL MODEL::DGN008_OfflineModel TO DGN008_retrievalRole;
SELECT external_model_id,name,principal_id,location,api_format,model_type_id,model_type_desc,model,credential_id,CONVERT(nvarchar(max),parameters) AS ParametersText,create_time,modify_time INTO lab.ModelBinding FROM sys.external_models WHERE name=N'DGN008_OfflineModel';
GO
CREATE PROCEDURE lab.CheckState @Reduced bit AS
BEGIN
 SET NOCOUNT ON;
 IF CONVERT(varbinary(max),USER_NAME())<>CONVERT(varbinary(max),N'dbo') THROW 51003,'FAIL_RESULT_CONTRACT: Privilegierter Labowner fehlt.',1;
 IF (SELECT COUNT(*) FROM lab.Sources)<>1 OR NOT EXISTS(SELECT 1 FROM lab.Sources WHERE Id=1 AND FactDays=7)
 OR (SELECT COUNT(*) FROM lab.EndpointPolicy)<>1 OR NOT EXISTS(SELECT 1 FROM lab.EndpointPolicy WHERE Id=1 AND CONVERT(varbinary(max),Location)=CONVERT(varbinary(max),N'https://model.example.invalid/v1/embeddings') AND CONVERT(varbinary(max),CredentialAlias)=CONVERT(varbinary(max),N'SYNTHETIC_NO_SECRET'))
 OR (SELECT COUNT(*) FROM lab.EndpointCandidates)<>4
 OR EXISTS(SELECT Id,CONVERT(varbinary(max),Location) FROM lab.EndpointCandidates EXCEPT SELECT Id,CONVERT(varbinary(max),Location) FROM (VALUES(1,N'https://model.example.invalid/v1/embeddings'),(2,N'http://model.example.invalid/v1/embeddings'),(3,N'https://foreign.example.invalid/v1/embeddings'),(4,N'https://model.example.invalid/v1/embeddings '))e(Id,Location))
 THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige Quellen-/Endpointfixture fehlt.',1;
 IF (SELECT COUNT(*) FROM sys.external_models)<>1 OR (SELECT COUNT(*) FROM lab.ModelBinding)<>1
 OR NOT EXISTS(SELECT 1 FROM lab.ModelBinding WHERE CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'DGN008_OfflineModel') AND principal_id=USER_ID(N'DGN008_setup') AND CONVERT(varbinary(max),location)=CONVERT(varbinary(max),N'https://model.example.invalid/v1/embeddings') AND CONVERT(varbinary(max),api_format)=CONVERT(varbinary(max),N'OpenAI') AND model_type_id=1 AND CONVERT(varbinary(max),model_type_desc)=CONVERT(varbinary(max),N'EMBEDDINGS') AND CONVERT(varbinary(max),model)=CONVERT(varbinary(max),N'synthetic-model') AND credential_id IS NULL AND ParametersText IS NULL)
 OR EXISTS(SELECT 1 FROM sys.database_scoped_credentials)
 THROW 51003,'FAIL_RESULT_CONTRACT: Kanonische Offline-Modellbindung fehlt.',1;
 IF EXISTS(SELECT external_model_id,CONVERT(varbinary(max),name),principal_id,CONVERT(varbinary(max),location),CONVERT(varbinary(max),api_format),model_type_id,CONVERT(varbinary(max),model_type_desc),CONVERT(varbinary(max),model),credential_id,CONVERT(varbinary(max),CONVERT(nvarchar(max),parameters)),create_time,modify_time FROM sys.external_models EXCEPT SELECT external_model_id,CONVERT(varbinary(max),name),principal_id,CONVERT(varbinary(max),location),CONVERT(varbinary(max),api_format),model_type_id,CONVERT(varbinary(max),model_type_desc),CONVERT(varbinary(max),model),credential_id,CONVERT(varbinary(max),ParametersText),create_time,modify_time FROM lab.ModelBinding)
 OR EXISTS(SELECT external_model_id,CONVERT(varbinary(max),name),principal_id,CONVERT(varbinary(max),location),CONVERT(varbinary(max),api_format),model_type_id,CONVERT(varbinary(max),model_type_desc),CONVERT(varbinary(max),model),credential_id,CONVERT(varbinary(max),ParametersText),create_time,modify_time FROM lab.ModelBinding EXCEPT SELECT external_model_id,CONVERT(varbinary(max),name),principal_id,CONVERT(varbinary(max),location),CONVERT(varbinary(max),api_format),model_type_id,CONVERT(varbinary(max),model_type_desc),CONVERT(varbinary(max),model),credential_id,CONVERT(varbinary(max),CONVERT(nvarchar(max),parameters)),create_time,modify_time FROM sys.external_models)
 THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige Modellmetadaten geaendert.',1;
 DECLARE @Permissions TABLE(Grantee int,Class int,MajorId int,MinorId int,PermissionName nvarchar(128),State char(1));
 INSERT @Permissions VALUES
 (USER_ID(N'DGN008_setup'),0,0,0,N'CONNECT','G'),(USER_ID(N'DGN008_ingestion'),0,0,0,N'CONNECT','G'),(USER_ID(N'DGN008_reader'),0,0,0,N'CONNECT','G'),
 (DATABASE_PRINCIPAL_ID(N'DGN008_setupRole'),0,0,0,N'CREATE EXTERNAL MODEL','G'),
 (DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),1,OBJECT_ID(N'lab.Sources'),0,N'SELECT','G'),(DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),1,OBJECT_ID(N'lab.Sources'),0,N'UPDATE','G'),
 (DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),110,(SELECT external_model_id FROM lab.ModelBinding),0,N'EXECUTE','G'),
 (DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole'),1,OBJECT_ID(N'lab.Sources'),0,N'SELECT','G');
 IF @Reduced=0 INSERT @Permissions VALUES(DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole'),1,OBJECT_ID(N'lab.EndpointPolicy'),0,N'SELECT','G'),(DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole'),110,(SELECT external_model_id FROM lab.ModelBinding),0,N'EXECUTE','G');
 IF (SELECT COUNT(*) FROM sys.database_principals WHERE name IN(N'DGN008_setup',N'DGN008_ingestion',N'DGN008_reader') AND type='S' AND authentication_type=0)<>3
 OR (SELECT COUNT(*) FROM sys.database_principals WHERE name IN(N'DGN008_setupRole',N'DGN008_ingestionRole',N'DGN008_retrievalRole') AND type='R' AND owning_principal_id=USER_ID(N'dbo'))<>3
 OR EXISTS(SELECT role_principal_id,member_principal_id FROM sys.database_role_members WHERE member_principal_id IN(USER_ID(N'DGN008_setup'),USER_ID(N'DGN008_ingestion'),USER_ID(N'DGN008_reader'),DATABASE_PRINCIPAL_ID(N'DGN008_setupRole'),DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole')) EXCEPT SELECT r,m FROM (VALUES(DATABASE_PRINCIPAL_ID(N'DGN008_setupRole'),USER_ID(N'DGN008_setup')),(DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),USER_ID(N'DGN008_ingestion')),(DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole'),USER_ID(N'DGN008_reader')))e(r,m))
 OR EXISTS(SELECT r,m FROM (VALUES(DATABASE_PRINCIPAL_ID(N'DGN008_setupRole'),USER_ID(N'DGN008_setup')),(DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),USER_ID(N'DGN008_ingestion')),(DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole'),USER_ID(N'DGN008_reader')))e(r,m) EXCEPT SELECT role_principal_id,member_principal_id FROM sys.database_role_members)
 OR EXISTS(SELECT grantee_principal_id,class,major_id,minor_id,CONVERT(varbinary(max),permission_name),CONVERT(varbinary(max),state) FROM sys.database_permissions WHERE grantee_principal_id IN(USER_ID(N'DGN008_setup'),USER_ID(N'DGN008_ingestion'),USER_ID(N'DGN008_reader'),DATABASE_PRINCIPAL_ID(N'DGN008_setupRole'),DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole')) EXCEPT SELECT Grantee,Class,MajorId,MinorId,CONVERT(varbinary(max),PermissionName),CONVERT(varbinary(max),State) FROM @Permissions)
 OR EXISTS(SELECT Grantee,Class,MajorId,MinorId,CONVERT(varbinary(max),PermissionName),CONVERT(varbinary(max),State) FROM @Permissions EXCEPT SELECT grantee_principal_id,class,major_id,minor_id,CONVERT(varbinary(max),permission_name),CONVERT(varbinary(max),state) FROM sys.database_permissions WHERE grantee_principal_id IN(USER_ID(N'DGN008_setup'),USER_ID(N'DGN008_ingestion'),USER_ID(N'DGN008_reader'),DATABASE_PRINCIPAL_ID(N'DGN008_setupRole'),DATABASE_PRINCIPAL_ID(N'DGN008_ingestionRole'),DATABASE_PRINCIPAL_ID(N'DGN008_retrievalRole')))
 THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige Benutzer-/Rollen-/Grantbindung fehlt.',1;
 IF EXISTS(SELECT * FROM lab.HostOptions EXCEPT SELECT CONVERT(varbinary(256),name),CONVERT(int,value),CONVERT(int,value_in_use) FROM sys.configurations)
 OR EXISTS(SELECT CONVERT(varbinary(256),name),CONVERT(int,value),CONVERT(int,value_in_use) FROM sys.configurations EXCEPT SELECT * FROM lab.HostOptions)
 THROW 51003,'FAIL_RESULT_CONTRACT: Hostoptionen geaendert.',1;
END;
GO
CREATE PROCEDURE lab.ExerciseRights @Reduced bit=0,@Baseline bit=0,@EmitEvidence bit=0 AS
BEGIN
 SET NOCOUNT ON;
 EXEC lab.CheckState @Reduced=@Reduced;
 DECLARE @Impersonating bit=0,@ReaderPermission int,@IngestionPermission int,@CreateReader int=0,@CreateIngestion int=0,@UpdateReader int=0,@PolicyIngestion int=0,@PolicyReader int=0;
 DECLARE @Rows TABLE(FactDays int); DECLARE @Writes TABLE(FactDays int); DECLARE @PolicyRows TABLE(Location nvarchar(200),CredentialAlias nvarchar(80));
 BEGIN TRY
  EXECUTE AS USER=N'DGN008_reader';SET @Impersonating=1;
  IF CONVERT(varbinary(max),USER_NAME())<>CONVERT(varbinary(max),N'DGN008_reader') THROW 51003,'FAIL_RESULT_CONTRACT: Readerkontext fehlt.',1;
  INSERT @Rows EXEC sys.sp_executesql N'SELECT FactDays FROM lab.Sources WHERE Id=@Id;',N'@Id int',@Id=1;
  SET @ReaderPermission=HAS_PERMS_BY_NAME(N'DGN008_OfflineModel',N'EXTERNAL MODEL',N'EXECUTE');
  IF @Baseline=0
  BEGIN
   BEGIN TRY EXEC(N'CREATE EXTERNAL MODEL DGN008_CounterModel WITH(LOCATION=''https://model.example.invalid/v1/embeddings'',API_FORMAT=''OpenAI'',MODEL_TYPE=EMBEDDINGS,MODEL=''synthetic-model'');');THROW 51003,'FAIL_RESULT_CONTRACT: Reader-CREATE erlaubt.',1;END TRY BEGIN CATCH IF ERROR_NUMBER()<>262 THROW;SET @CreateReader=ERROR_NUMBER();END CATCH;
   BEGIN TRY EXEC(N'UPDATE lab.Sources SET FactDays=99 WHERE Id=1;');THROW 51003,'FAIL_RESULT_CONTRACT: Reader-UPDATE erlaubt.',1;END TRY BEGIN CATCH IF ERROR_NUMBER()<>229 THROW;SET @UpdateReader=ERROR_NUMBER();END CATCH;
   IF @Reduced=0 INSERT @PolicyRows EXEC(N'SELECT Location,CredentialAlias FROM lab.EndpointPolicy;');
   ELSE BEGIN BEGIN TRY EXEC(N'SELECT Location,CredentialAlias FROM lab.EndpointPolicy;');THROW 51003,'FAIL_RESULT_CONTRACT: Reduzierter Policyzugriff erlaubt.',1;END TRY BEGIN CATCH IF ERROR_NUMBER()<>229 THROW;SET @PolicyReader=ERROR_NUMBER();END CATCH;END;
  END;
  REVERT;SET @Impersonating=0;
 END TRY BEGIN CATCH IF @Impersonating=1 REVERT;THROW;END CATCH;
 IF (SELECT COUNT(*) FROM @Rows)<>1 OR NOT EXISTS(SELECT 1 FROM @Rows WHERE FactDays=7) OR ISNULL(@ReaderPermission,-1)<>CASE WHEN @Reduced=0 THEN 1 ELSE 0 END THROW 51003,'FAIL_RESULT_CONTRACT: Erlaubte Readerrow/Metadatenrechte fehlen.',1;
 IF @Baseline=1 BEGIN DECLARE @BaselineRows int=(SELECT COUNT(*) FROM @Rows);PRINT CONCAT('AI_ASSERT|baseline|baseline_rows|',@BaselineRows);SELECT FactDays FROM @Rows;RETURN;END;
 BEGIN TRY
  EXECUTE AS USER=N'DGN008_ingestion';SET @Impersonating=1;
  IF CONVERT(varbinary(max),USER_NAME())<>CONVERT(varbinary(max),N'DGN008_ingestion') THROW 51003,'FAIL_RESULT_CONTRACT: Ingestionkontext fehlt.',1;
  SET @IngestionPermission=HAS_PERMS_BY_NAME(N'DGN008_OfflineModel',N'EXTERNAL MODEL',N'EXECUTE');
  INSERT @Writes EXEC sys.sp_executesql N'UPDATE lab.Sources SET FactDays=@Days OUTPUT inserted.FactDays WHERE Id=@Id;',N'@Days int,@Id int',@Days=8,@Id=1;
  INSERT @Writes EXEC sys.sp_executesql N'UPDATE lab.Sources SET FactDays=@Days OUTPUT inserted.FactDays WHERE Id=@Id;',N'@Days int,@Id int',@Days=7,@Id=1;
  BEGIN TRY EXEC(N'CREATE EXTERNAL MODEL DGN008_CounterModel WITH(LOCATION=''https://model.example.invalid/v1/embeddings'',API_FORMAT=''OpenAI'',MODEL_TYPE=EMBEDDINGS,MODEL=''synthetic-model'');');THROW 51003,'FAIL_RESULT_CONTRACT: Ingestion-CREATE erlaubt.',1;END TRY BEGIN CATCH IF ERROR_NUMBER()<>262 THROW;SET @CreateIngestion=ERROR_NUMBER();END CATCH;
  BEGIN TRY EXEC(N'SELECT Location,CredentialAlias FROM lab.EndpointPolicy;');THROW 51003,'FAIL_RESULT_CONTRACT: Ingestion-Policyzugriff erlaubt.',1;END TRY BEGIN CATCH IF ERROR_NUMBER()<>229 THROW;SET @PolicyIngestion=ERROR_NUMBER();END CATCH;
  REVERT;SET @Impersonating=0;
 END TRY BEGIN CATCH IF @Impersonating=1 REVERT;THROW;END CATCH;
 IF @CreateReader<>262 OR @CreateIngestion<>262 OR @UpdateReader<>229 OR @PolicyIngestion<>229 OR ISNULL(@IngestionPermission,-1)<>1
 OR (SELECT COUNT(*) FROM @Writes)<>2 OR (SELECT COUNT(*) FROM @Writes WHERE FactDays=8)<>1 OR (SELECT COUNT(*) FROM @Writes WHERE FactDays=7)<>1
 OR (@Reduced=0 AND ((SELECT COUNT(*) FROM @PolicyRows)<>1 OR NOT EXISTS(SELECT 1 FROM @PolicyRows WHERE CONVERT(varbinary(max),Location)=CONVERT(varbinary(max),N'https://model.example.invalid/v1/embeddings') AND CONVERT(varbinary(max),CredentialAlias)=CONVERT(varbinary(max),N'SYNTHETIC_NO_SECRET'))))
 OR (@Reduced=1 AND (@PolicyReader<>229 OR EXISTS(SELECT 1 FROM @PolicyRows))) THROW 51003,'FAIL_RESULT_CONTRACT: Tatsaechliche erlaubte Writes/Rechteverweigerungen fehlen.',1;
 DECLARE @EndpointResults TABLE(Id int,Allowed bit);
 INSERT @EndpointResults SELECT c.Id,CASE WHEN CONVERT(varbinary(max),c.Location)=CONVERT(varbinary(max),p.Location) THEN 1 ELSE 0 END FROM lab.EndpointCandidates c CROSS JOIN lab.EndpointPolicy p;
 DECLARE @EndpointAllowed int=(SELECT COUNT(*) FROM @EndpointResults WHERE Allowed=1),@EndpointDenied int=(SELECT COUNT(*) FROM @EndpointResults WHERE Allowed=0);
 IF @EndpointAllowed<>1 OR @EndpointDenied<>3 THROW 51003,'FAIL_RESULT_CONTRACT: Feste Endpointpolicy verletzt.',1;
 EXEC lab.CheckState @Reduced=@Reduced;
 SELECT @Reduced AS GrantsReduced,@ReaderPermission AS ReaderModelExecuteMetadata,@IngestionPermission AS IngestionModelExecuteMetadata,@CreateReader AS ReaderCreateDenial,@CreateIngestion AS IngestionCreateDenial,@UpdateReader AS ReaderUpdateDenial,@PolicyIngestion AS IngestionPolicyDenial,@PolicyReader AS ReducedReaderPolicyDenial;
 SELECT Id,Allowed FROM @EndpointResults ORDER BY Id;
 IF @EmitEvidence=1
 BEGIN
  DECLARE @ReaderRows int=(SELECT COUNT(*) FROM @Rows),@WriteRows int=(SELECT COUNT(*) FROM @Writes),@ModelRows int=(SELECT COUNT(*) FROM sys.external_models);
  PRINT CONCAT('AI_ASSERT|comparison|reader_rows|',@ReaderRows);
  PRINT CONCAT('AI_ASSERT|comparison|ingestion_writes|',@WriteRows);
  PRINT CONCAT('AI_ASSERT|comparison|permission_denials|',CASE WHEN @CreateReader=262 THEN 1 ELSE 0 END+CASE WHEN @CreateIngestion=262 THEN 1 ELSE 0 END+CASE WHEN @UpdateReader=229 THEN 1 ELSE 0 END+CASE WHEN @PolicyIngestion=229 THEN 1 ELSE 0 END+CASE WHEN @PolicyReader=229 THEN 1 ELSE 0 END);
  PRINT CONCAT('AI_ASSERT|comparison|reader_model_execute_metadata|',@ReaderPermission);
  PRINT CONCAT('AI_ASSERT|comparison|ingestion_model_execute_metadata|',@IngestionPermission);
  PRINT CONCAT('AI_ASSERT|comparison|endpoint_allowed|',@EndpointAllowed);
  PRINT CONCAT('AI_ASSERT|comparison|endpoint_denied|',@EndpointDenied);
  PRINT CONCAT('AI_ASSERT|comparison|owned_model_rows|',@ModelRows);
 END;
END;
GO
PRINT 'SQLPERF_SUMMARY|PASS|OK';
