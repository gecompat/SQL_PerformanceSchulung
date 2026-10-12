/* CON-010: Tenant-Isolation vor dem Vektorkontext; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @RawDemo nvarchar(max)=N'$(DemoId)',@RawRun nvarchar(max)=N'$(RunToken)',@RawTarget nvarchar(max)=N'$(TargetDatabase)';
IF DATALENGTH(@RawDemo)<>14 OR CONVERT(varbinary(max),@RawDemo)<>CONVERT(varbinary(max),N'CON-010')
 OR DATALENGTH(@RawRun) NOT BETWEEN 2 AND 32 OR @RawRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
 OR DATALENGTH(@RawTarget)<>DATALENGTH(N'SQLPERF_LAB_CON010_'+@RawRun)
 OR CONVERT(varbinary(max),@RawTarget)<>CONVERT(varbinary(max),N'SQLPERF_LAB_CON010_'+@RawRun)
 THROW 51000,'FAIL_CONTRACT: Vollstaendige Demo-/Run-/Zielbindung verletzt.',1;
DECLARE @DemoId varchar(7)=CONVERT(varchar(7),@RawDemo),@RunToken varchar(16)=CONVERT(varchar(16),@RawRun),@TargetDatabase sysname=CONVERT(sysname,@RawTarget);
DECLARE @Sql nvarchar(max),@Matches int;
IF DB_ID(@TargetDatabase) IS NOT NULL
BEGIN
 SET @Sql=N'SELECT @M=COUNT(*) FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties p
 JOIN (VALUES(N''SQLPERF.Project'',N''SQL_PerformanceSchulung''),
 (N''SQLPERF.ContractVersion'',N''1.0''),(N''SQLPERF.DemoId'',CONVERT(nvarchar(max),@D)),
 (N''SQLPERF.RunToken'',CONVERT(nvarchar(max),@R))) e(Name,Value)
 ON DATALENGTH(p.name)=DATALENGTH(e.Name) AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 WHERE p.class=0 AND p.major_id=0 AND p.minor_id=0
 AND DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Value)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=CONVERT(varbinary(max),e.Value);';
 EXEC sys.sp_executesql @Sql,N'@D varchar(7),@R varchar(16),@M int OUTPUT',@D=@DemoId,@R=@RunToken,@M=@Matches OUTPUT;
 IF @Matches<>4 THROW 51004,'FAIL_STATE: Vollstaendige bytegenaue Eigentumsmarker fehlen.',1;
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
IF SCHEMA_ID(N'sec') IS NULL EXEC(N'CREATE SCHEMA sec AUTHORIZATION dbo;');
DROP PROCEDURE IF EXISTS lab.RunControls;
DROP PROCEDURE IF EXISTS lab.ReadTenantSet;
DROP PROCEDURE IF EXISTS lab.AssertFixture;
IF EXISTS(SELECT 1 FROM sys.security_policies WHERE object_id=OBJECT_ID(N'sec.TenantPolicy')) DROP SECURITY POLICY sec.TenantPolicy;
DROP FUNCTION IF EXISTS sec.TenantPredicate;
DROP TABLE IF EXISTS lab.Documents;
IF USER_ID(N'CON010_TenantA') IS NOT NULL DROP USER [CON010_TenantA];
IF USER_ID(N'CON010_TenantB') IS NOT NULL DROP USER [CON010_TenantB];
IF USER_ID(N'CON010_Unmapped') IS NOT NULL DROP USER [CON010_Unmapped];
CREATE TABLE lab.Documents(Id int NOT NULL PRIMARY KEY,TenantId int NOT NULL,Content nvarchar(100) NOT NULL,V VECTOR(3) NOT NULL);
INSERT lab.Documents VALUES(1,1,N'Synthetische Quelle A','[1,0,0]'),(2,2,N'Synthetische Quelle B','[1,0,0]');
CREATE USER [CON010_TenantA] WITHOUT LOGIN;
CREATE USER [CON010_TenantB] WITHOUT LOGIN;
CREATE USER [CON010_Unmapped] WITHOUT LOGIN;
GRANT SELECT ON OBJECT::lab.Documents TO [CON010_TenantA],[CON010_TenantB],[CON010_Unmapped];
SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON;
EXEC(N'CREATE FUNCTION sec.TenantPredicate(@TenantId int)
RETURNS TABLE WITH SCHEMABINDING AS
RETURN SELECT 1 AS Allowed WHERE USER_NAME()=N''dbo''
 OR (@TenantId=1 AND USER_NAME()=N''CON010_TenantA'')
 OR (@TenantId=2 AND USER_NAME()=N''CON010_TenantB'');');
EXEC(N'CREATE SECURITY POLICY sec.TenantPolicy ADD FILTER PREDICATE sec.TenantPredicate(TenantId) ON lab.Documents WITH(STATE=ON,SCHEMABINDING=ON);');
GO
CREATE PROCEDURE lab.AssertFixture AS
BEGIN
 SET NOCOUNT ON;
 IF DATALENGTH(USER_NAME())<>DATALENGTH(N'dbo') OR CONVERT(varbinary(max),USER_NAME())<>CONVERT(varbinary(max),N'dbo')
  THROW 51003,'FAIL_RESULT_CONTRACT: Kontrollharness erfordert den privilegierten Labowner.',1;
 DECLARE @FrozenFunction nvarchar(max)=N'CREATE FUNCTION sec.TenantPredicate(@TenantId int)
RETURNS TABLE WITH SCHEMABINDING AS
RETURN SELECT 1 AS Allowed WHERE USER_NAME()=N''dbo''
 OR (@TenantId=1 AND USER_NAME()=N''CON010_TenantA'')
 OR (@TenantId=2 AND USER_NAME()=N''CON010_TenantB'');';
 IF OBJECT_ID(N'sec.TenantPredicate',N'IF') IS NULL
  OR DATALENGTH(OBJECT_DEFINITION(OBJECT_ID(N'sec.TenantPredicate')))<>DATALENGTH(@FrozenFunction)
  OR CONVERT(varbinary(max),ISNULL(OBJECT_DEFINITION(OBJECT_ID(N'sec.TenantPredicate')),N''))<>CONVERT(varbinary(max),@FrozenFunction)
  OR (SELECT COUNT(*) FROM sys.security_policies)<>1
  OR NOT EXISTS(SELECT 1 FROM sys.security_policies WHERE object_id=OBJECT_ID(N'sec.TenantPolicy') AND is_enabled=1 AND is_schema_bound=1)
  OR (SELECT COUNT(*) FROM sys.security_predicates)<>1
  OR NOT EXISTS(SELECT 1 FROM sys.security_predicates WHERE object_id=OBJECT_ID(N'sec.TenantPolicy') AND target_object_id=OBJECT_ID(N'lab.Documents')
   AND predicate_type=0 AND operation IS NULL AND DATALENGTH(predicate_definition)=DATALENGTH(N'([sec].[TenantPredicate]([TenantId]))') AND CONVERT(varbinary(max),predicate_definition)=CONVERT(varbinary(max),N'([sec].[TenantPredicate]([TenantId]))'))
  THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige aktive RLS-Bindung verletzt.',1;
 DECLARE @V VECTOR(3)='[1,0,0]';
 DECLARE @Frozen TABLE(Id int,TenantId int,Content nvarchar(100),VectorText varchar(max));
 INSERT @Frozen VALUES(1,1,N'Synthetische Quelle A',CONVERT(varchar(max),@V)),(2,2,N'Synthetische Quelle B',CONVERT(varchar(max),@V));
 IF (SELECT COUNT(*) FROM lab.Documents)<>2
  OR EXISTS(SELECT Id,TenantId,DATALENGTH(Content),CONVERT(varbinary(max),Content),DATALENGTH(CONVERT(varchar(max),V)),CONVERT(varbinary(max),CONVERT(varchar(max),V)) FROM lab.Documents
   EXCEPT SELECT Id,TenantId,DATALENGTH(Content),CONVERT(varbinary(max),Content),DATALENGTH(VectorText),CONVERT(varbinary(max),VectorText) FROM @Frozen)
  OR EXISTS(SELECT Id,TenantId,DATALENGTH(Content),CONVERT(varbinary(max),Content),DATALENGTH(VectorText),CONVERT(varbinary(max),VectorText) FROM @Frozen
   EXCEPT SELECT Id,TenantId,DATALENGTH(Content),CONVERT(varbinary(max),Content),DATALENGTH(CONVERT(varchar(max),V)),CONVERT(varbinary(max),CONVERT(varchar(max),V)) FROM lab.Documents)
  THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige synthetische Quellen-/Vektorfixture verletzt.',1;
 DECLARE @Users TABLE(Name sysname,Id int);
 INSERT @Users SELECT e.Name,p.principal_id FROM (VALUES(N'CON010_TenantA'),(N'CON010_TenantB'),(N'CON010_Unmapped')) e(Name)
 JOIN sys.database_principals p ON DATALENGTH(p.name)=DATALENGTH(e.Name) AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 WHERE p.type='S' AND p.authentication_type=0;
 DECLARE @Permissions TABLE(Grantee int,Grantor int,Class int,MajorId int,MinorId int,PermissionName varbinary(256),NameBytes int,State char(1));
 INSERT @Permissions SELECT u.Id,USER_ID(N'dbo'),v.Class,v.MajorId,0,CONVERT(varbinary(256),v.PermissionName),DATALENGTH(v.PermissionName),'G'
 FROM @Users u CROSS JOIN (VALUES(0,0,CONVERT(nvarchar(128),N'CONNECT')),(1,OBJECT_ID(N'lab.Documents'),CONVERT(nvarchar(128),N'SELECT'))) v(Class,MajorId,PermissionName);
 IF (SELECT COUNT(*) FROM @Users)<>3
  OR (SELECT COUNT(*) FROM sys.database_permissions WHERE grantee_principal_id IN(SELECT Id FROM @Users))<>6
  OR EXISTS(SELECT grantee_principal_id,grantor_principal_id,class,major_id,minor_id,CONVERT(varbinary(256),permission_name),DATALENGTH(permission_name),CONVERT(varbinary(1),state)
    FROM sys.database_permissions WHERE grantee_principal_id IN(SELECT Id FROM @Users)
    EXCEPT SELECT Grantee,Grantor,Class,MajorId,MinorId,PermissionName,NameBytes,CONVERT(varbinary(1),State) FROM @Permissions)
  OR EXISTS(SELECT Grantee,Grantor,Class,MajorId,MinorId,PermissionName,NameBytes,CONVERT(varbinary(1),State) FROM @Permissions
    EXCEPT SELECT grantee_principal_id,grantor_principal_id,class,major_id,minor_id,CONVERT(varbinary(256),permission_name),DATALENGTH(permission_name),CONVERT(varbinary(1),state)
    FROM sys.database_permissions WHERE grantee_principal_id IN(SELECT Id FROM @Users))
  OR EXISTS(SELECT 1 FROM sys.database_role_members WHERE member_principal_id IN(SELECT Id FROM @Users))
  THROW 51003,'FAIL_RESULT_CONTRACT: Eingefrorene eingeschraenkte Benutzerrechte verletzt.',1;
END;
GO
CREATE PROCEDURE lab.ReadTenantSet @Baseline bit=0,@EmitEvidence bit=0 AS
BEGIN
 SET NOCOUNT ON;
 EXEC lab.AssertFixture;
 DECLARE @Rows TABLE(Id int,TenantId int,Content nvarchar(100),VectorText varchar(max),Distance float);
 DECLARE @Captured TABLE(ContextId int,Id int,TenantId int,Content nvarchar(100),VectorText varchar(max),Distance float);
 DECLARE @Context int=1,@Max int=CASE WHEN @Baseline=1 THEN 2 ELSE 3 END,@Impersonating bit=0,@V VECTOR(3)='[1,0,0]';
 BEGIN TRY
  WHILE @Context<=@Max
  BEGIN
   DELETE FROM @Rows;
   IF @Context=1 EXECUTE AS USER=N'CON010_TenantA';
   ELSE IF @Context=2 EXECUTE AS USER=N'CON010_TenantB';
   ELSE EXECUTE AS USER=N'CON010_Unmapped';
   SET @Impersonating=1;
   IF @Baseline=0 EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=2;
   -- Dynamisches festes SQL vermeidet einen Eigentumsketten-Bypass der SELECT-Rechte.
   IF @Baseline=1
    INSERT @Rows EXEC sys.sp_executesql N'SELECT Id,TenantId,Content,CONVERT(varchar(max),V),CONVERT(float,0) FROM lab.Documents;';
   ELSE
    INSERT @Rows EXEC sys.sp_executesql N'DECLARE @Q VECTOR(3)=''[1,0,0]''; SELECT Id,TenantId,Content,CONVERT(varchar(max),V),VECTOR_DISTANCE(''cosine'',V,@Q) FROM lab.Documents WHERE VECTOR_DISTANCE(''cosine'',V,@Q)<=0.05;';
   REVERT; SET @Impersonating=0;
   INSERT @Captured SELECT @Context,Id,TenantId,Content,VectorText,Distance FROM @Rows;
   SET @Context+=1;
  END;
  EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=NULL;
 END TRY BEGIN CATCH
  IF @Impersonating=1 REVERT;
  EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=NULL;
  THROW;
 END CATCH;
 IF (SELECT COUNT(*) FROM @Captured)<>2
  OR NOT EXISTS(SELECT 1 FROM @Captured WHERE ContextId=1 AND Id=1 AND TenantId=1 AND DATALENGTH(Content)=DATALENGTH(N'Synthetische Quelle A') AND CONVERT(varbinary(max),Content)=CONVERT(varbinary(max),N'Synthetische Quelle A') AND DATALENGTH(VectorText)=DATALENGTH(CONVERT(varchar(max),@V)) AND CONVERT(varbinary(max),VectorText)=CONVERT(varbinary(max),CONVERT(varchar(max),@V)) AND Distance=0)
  OR NOT EXISTS(SELECT 1 FROM @Captured WHERE ContextId=2 AND Id=2 AND TenantId=2 AND DATALENGTH(Content)=DATALENGTH(N'Synthetische Quelle B') AND CONVERT(varbinary(max),Content)=CONVERT(varbinary(max),N'Synthetische Quelle B') AND DATALENGTH(VectorText)=DATALENGTH(CONVERT(varchar(max),@V)) AND CONVERT(varbinary(max),VectorText)=CONVERT(varbinary(max),CONVERT(varchar(max),@V)) AND Distance=0)
  OR EXISTS(SELECT 1 FROM @Captured WHERE ContextId=3 OR ContextId<>TenantId)
  OR SESSION_CONTEXT(N'CON010_TenantId') IS NOT NULL
  THROW 51003,'FAIL_RESULT_CONTRACT: Positive Quellen-/Vektorkontexte oder Isolation/Reset verletzt.',1;
 SELECT ContextId,Id,TenantId,Content,VectorText,Distance FROM @Captured ORDER BY ContextId;
 DECLARE @Authorized int=(SELECT COUNT(*) FROM @Captured WHERE ContextId=TenantId),@Foreign int=(SELECT COUNT(*) FROM @Captured WHERE ContextId=3 OR ContextId<>TenantId);
 IF @EmitEvidence=1 AND @Baseline=1 PRINT CONCAT('AI_ASSERT|baseline|baseline_rows|',@Authorized);
 ELSE IF @EmitEvidence=1
 BEGIN
  PRINT CONCAT('AI_ASSERT|comparison|authorized_contexts|',@Authorized);
  PRINT CONCAT('AI_ASSERT|comparison|unauthorized_rows|',@Foreign);
 END;
END;
GO
CREATE PROCEDURE lab.RunControls AS
BEGIN
 SET NOCOUNT ON;
 EXEC lab.ReadTenantSet @Baseline=0,@EmitEvidence=1;
 DECLARE @Depth int=0,@Revoked bit=0,@Denials int=0,@RevokedRows int=0;
 DECLARE @Rows TABLE(Id int);
 BEGIN TRY
  EXECUTE AS USER=N'CON010_TenantA'; SET @Depth=1;
  BEGIN TRY
   EXEC(N'ALTER SECURITY POLICY sec.TenantPolicy WITH(STATE=OFF);');
   THROW 51003,'FAIL_RESULT_CONTRACT: Policyaenderung unerwartet erlaubt.',1;
  END TRY BEGIN CATCH
   IF ERROR_NUMBER()<>33268 THROW;
   SET @Denials+=1;
  END CATCH;
  BEGIN TRY
   EXECUTE AS USER=N'CON010_TenantB'; SET @Depth=2;
   THROW 51003,'FAIL_RESULT_CONTRACT: Tenant-Impersonation unerwartet erlaubt.',1;
  END TRY BEGIN CATCH
   IF ERROR_NUMBER()<>15517 THROW;
   SET @Denials+=1;
  END CATCH;
  REVERT; SET @Depth=0;
  EXEC lab.AssertFixture;
  -- Nur der privilegierte Owner widerruft den zuvor exakt geprueften Grant.
  REVOKE SELECT ON OBJECT::lab.Documents FROM [CON010_TenantA]; SET @Revoked=1;
  EXECUTE AS USER=N'CON010_TenantA'; SET @Depth=1;
  BEGIN TRY
   INSERT @Rows EXEC sys.sp_executesql N'SELECT Id FROM lab.Documents;';
   THROW 51003,'FAIL_RESULT_CONTRACT: Widerrufene Quell-/Vektorrechte unerwartet erlaubt.',1;
  END TRY BEGIN CATCH
   IF ERROR_NUMBER()<>229 THROW;
   SET @Denials+=1;
  END CATCH;
  SET @RevokedRows=(SELECT COUNT(*) FROM @Rows);
  REVERT; SET @Depth=0;
  GRANT SELECT ON OBJECT::lab.Documents TO [CON010_TenantA]; SET @Revoked=0;
  EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=NULL;
 END TRY BEGIN CATCH
  WHILE @Depth>0 BEGIN REVERT; SET @Depth-=1; END;
  IF @Revoked=1 GRANT SELECT ON OBJECT::lab.Documents TO [CON010_TenantA];
  EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=NULL;
  THROW;
 END CATCH;
 EXEC lab.AssertFixture;
 DECLARE @Reset int=CASE WHEN SESSION_CONTEXT(N'CON010_TenantId') IS NULL THEN 1 ELSE 0 END;
 IF @Denials<>3 OR @RevokedRows<>0 OR @Reset<>1
  THROW 51003,'FAIL_RESULT_CONTRACT: Tatsaechliche Rechtegegenproben oder Reset verletzt.',1;
 PRINT CONCAT('AI_ASSERT|comparison|permission_denials|',@Denials);
 PRINT CONCAT('AI_ASSERT|comparison|revoked_rows|',@RevokedRows);
 PRINT CONCAT('AI_ASSERT|comparison|session_resets|',@Reset);
END;
GO
PRINT 'SQLPERF_SUMMARY|PASS|OK';
