/* QRY-017: Relationale, Full-Text- und exakte Vektorsuche; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)', @RunToken varchar(16)='$(RunToken)', @TargetDatabase sysname=N'$(TargetDatabase)';
IF @DemoId <> 'QRY-017' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 16
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
IF CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),@TargetDatabase) OR DB_ID(@TargetDatabase) IS NULL THROW 51004,'FAIL_STATE: Falscher Datenbankkontext.',1;
DECLARE @q VECTOR(3)='[1,0,0]',@TopId int;
SELECT TOP(1) @TopId=Id FROM lab.SearchDocuments WHERE TenantId='A' ORDER BY VECTOR_DISTANCE('cosine',V,@q),Id;
IF @TopId IS NULL OR @TopId<>1 THROW 51003,'FAIL_RESULT_CONTRACT: Autorisierte Exact-Top-ID muss 1 sein.',1;
PRINT CONCAT('AI_ASSERT|comparison|exact_top_id|',@TopId);
PRINT 'AI_ASSERT|comparison|model_calls|0';
DECLARE @FullTextChecks int=0;
IF CONVERT(int,SERVERPROPERTY('IsFullTextInstalled'))=1
BEGIN
 -- LANGUAGE 0 besitzt keinen Stemmer: Das exakte Fixturewort lautet "rote".
 -- Jede Suchart prueft die vollstaendige ID-Menge statt nur einen Trefferzaehler.
 EXEC sys.sp_executesql N'
 DECLARE @Hits table(SearchKind varchar(12),Id int,Score int);
 INSERT @Hits SELECT ''CONTAINS'',Id,NULL FROM lab.SearchDocuments WHERE TenantId=''A'' AND CONTAINS(Content,N''"rote"'');
 INSERT @Hits SELECT ''FREETEXT'',Id,NULL FROM lab.SearchDocuments WHERE TenantId=''A'' AND FREETEXT(Content,N''rote'');
 INSERT @Hits SELECT ''RANKED'',d.Id,ft.[RANK] FROM CONTAINSTABLE(lab.SearchDocuments,Content,N''"rote"'') ft
 JOIN lab.SearchDocuments d ON d.Id=ft.[KEY] WHERE d.TenantId=''A'';
 INSERT @Hits SELECT ''TENANT_B'',Id,NULL FROM lab.SearchDocuments WHERE TenantId=''B'' AND CONTAINS(Content,N''"rote"'');
 INSERT @Hits SELECT ''ABSENT'',Id,NULL FROM lab.SearchDocuments WHERE TenantId=''A'' AND CONTAINS(Content,N''"quarzxyz"'');
 DECLARE @Expected table(SearchKind varchar(12),Id int);
 INSERT @Expected VALUES(''CONTAINS'',1),(''CONTAINS'',3),(''FREETEXT'',1),(''FREETEXT'',3),(''RANKED'',1),(''RANKED'',3),(''TENANT_B'',4);
 IF EXISTS(SELECT SearchKind,Id FROM @Expected EXCEPT SELECT SearchKind,Id FROM @Hits)
 OR EXISTS(SELECT SearchKind,Id FROM @Hits EXCEPT SELECT SearchKind,Id FROM @Expected)
 OR EXISTS(SELECT 1 FROM @Hits WHERE SearchKind=''RANKED'' AND (Score IS NULL OR Score<=0))
 THROW 51003,''FAIL_RESULT_CONTRACT: Volltextsuche verletzt Treffer-, Negativ- oder Tenantvertrag.'',1;';
 SET @FullTextChecks=5;
END;
PRINT CONCAT('AI_ASSERT|comparison|fulltext_checks|',@FullTextChecks);
PRINT 'SQLPERF_SUMMARY|PASS|OK';
