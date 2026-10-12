/* DGN-010: begrenzte synthetische Quellen- und Indexmessung. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @RawDemo nvarchar(max)=N'$(DemoId)',@RawRun nvarchar(max)=N'$(RunToken)',@RawTarget nvarchar(max)=N'$(TargetDatabase)';
IF DATALENGTH(@RawDemo)<>14 OR CONVERT(varbinary(max),@RawDemo)<>CONVERT(varbinary(max),N'DGN-010')
 OR DATALENGTH(@RawRun) NOT BETWEEN 2 AND 32 OR @RawRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
 OR DATALENGTH(@RawTarget)<>DATALENGTH(N'SQLPERF_LAB_DGN010_'+@RawRun)
 OR CONVERT(varbinary(max),@RawTarget)<>CONVERT(varbinary(max),N'SQLPERF_LAB_DGN010_'+@RawRun)
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
IF DATALENGTH(DB_NAME())<>DATALENGTH(@TargetDatabase) OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),@TargetDatabase) OR DB_ID(@TargetDatabase) IS NULL THROW 51004,'FAIL_STATE: Falscher Datenbankkontext.',1;

IF CONVERT(nvarchar(80),SERVERPROPERTY('ProductVersion'))<>N'17.0.5005.3'
 OR CONVERT(int,SERVERPROPERTY('EngineEdition'))<>3
 OR (SELECT compatibility_level FROM sys.databases WHERE database_id=DB_ID())<>170
 OR (SELECT recovery_model_desc FROM sys.databases WHERE database_id=DB_ID())<>N'SIMPLE'
 OR (SELECT COUNT(*) FROM sys.database_scoped_configurations WHERE name IN(N'MAXDOP',N'PREVIEW_FEATURES') AND value=0)<>2
 OR (SELECT COUNT(*) FROM sys.database_files WHERE (type=0 AND max_size=32768) OR (type=1 AND max_size=8192))<>2
 THROW 51003,'FAIL_RESULT_CONTRACT: Fixed DB/build/config profile missing.',1;
IF (SELECT COUNT(*) FROM lab.SourceRows)<>1000
 OR EXISTS(SELECT 1 FROM lab.SourceRows WHERE Id NOT BETWEEN 1 AND 1000 OR Value<>Id*3
 OR DATALENGTH(Payload)<>100 OR CONVERT(varbinary(max),Payload)<>CONVERT(varbinary(max),REPLICATE('F',100)))
 THROW 51003,'FAIL_RESULT_CONTRACT: Full fixed source oracle missing.',1;
IF EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') AND index_id>0
 AND name NOT IN(N'DGN010_OwnPK',N'DGN010_OwnCandidate'))
 THROW 51003,'FAIL_RESULT_CONTRACT: Unexpected source index.',1;
IF (SELECT COUNT(*) FROM sys.database_permissions WHERE grantee_principal_id=USER_ID(N'DGN010_reader'))<>2
 OR NOT EXISTS(SELECT 1 FROM sys.database_permissions WHERE grantee_principal_id=USER_ID(N'DGN010_reader') AND class=0 AND major_id=0 AND minor_id=0 AND permission_name=N'CONNECT' AND state='G')
 OR NOT EXISTS(SELECT 1 FROM sys.database_permissions WHERE grantee_principal_id=USER_ID(N'DGN010_reader') AND class=1 AND major_id=OBJECT_ID(N'lab.SourceRows') AND minor_id=0 AND permission_name=N'SELECT' AND state='G')
 OR EXISTS(SELECT 1 FROM sys.database_role_members WHERE member_principal_id=USER_ID(N'DGN010_reader'))
 THROW 51003,'FAIL_RESULT_CONTRACT: Fixed reader permissions missing.',1;
DECLARE @ReaderRows TABLE(Id int,Value int,Payload varchar(100));
DECLARE @Impersonating bit=0;
BEGIN TRY
 EXECUTE AS USER=N'DGN010_reader';SET @Impersonating=1;
 IF DATALENGTH(USER_NAME())<>DATALENGTH(N'DGN010_reader') OR CONVERT(varbinary(max),USER_NAME())<>CONVERT(varbinary(max),N'DGN010_reader')
  THROW 51003,'FAIL_RESULT_CONTRACT: Actual reader context missing.',1;
 INSERT @ReaderRows EXEC sys.sp_executesql
 N'SELECT Id,Value,Payload FROM lab.SourceRows WHERE Id BETWEEN @First AND @Last ORDER BY Id OPTION(MAXDOP 1);',
 N'@First int,@Last int',@First=101,@Last=110;
 REVERT;SET @Impersonating=0;
END TRY BEGIN CATCH IF @Impersonating=1 REVERT;THROW;END CATCH;
IF (SELECT COUNT(*) FROM @ReaderRows)<>10 OR EXISTS(SELECT 1 FROM @ReaderRows WHERE Id NOT BETWEEN 101 AND 110 OR Value<>Id*3
 OR DATALENGTH(Payload)<>100 OR CONVERT(varbinary(max),Payload)<>CONVERT(varbinary(max),REPLICATE('F',100)))
 OR EXISTS(SELECT Id FROM lab.SourceRows WHERE Id BETWEEN 101 AND 110 EXCEPT SELECT Id FROM @ReaderRows)
 THROW 51003,'FAIL_RESULT_CONTRACT: Actual reader query oracle missing.',1;
SELECT CONCAT('DGN010_SOURCE|',Id,'|',Value,'|',DATALENGTH(Payload),'|',CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),Payload)),2)) FROM lab.SourceRows ORDER BY Id;
SELECT CONCAT('DGN010_INDEX|',i.name,'|',SUM(p.row_count),'|',SUM(p.used_page_count),'|',SUM(p.reserved_page_count))
 FROM sys.indexes i JOIN sys.dm_db_partition_stats p ON i.object_id=p.object_id AND i.index_id=p.index_id
 WHERE i.object_id=OBJECT_ID(N'lab.SourceRows') AND i.name IN(N'DGN010_OwnPK',N'DGN010_OwnCandidate') GROUP BY i.name ORDER BY i.name;
SELECT 'DGN010_READER|ROWS_10|FIXED_RIGHTS_2|NO_MODEL_CALL';
SELECT 'SQLPERF_SUMMARY|PASS|OK';
