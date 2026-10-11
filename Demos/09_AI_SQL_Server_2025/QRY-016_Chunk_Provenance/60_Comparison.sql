/* QRY-016: Chunking, Overlap und Provenienz; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)', @RunToken varchar(16)='$(RunToken)', @TargetDatabase sysname=N'$(TargetDatabase)';
IF @DemoId <> 'QRY-016' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 16
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
IF (SELECT COUNT(*) FROM lab.Documents)<>2 OR EXISTS(SELECT 1 FROM lab.Documents d CROSS JOIN (VALUES(0),(25)) p(OverlapPct) WHERE NOT EXISTS(SELECT 1 FROM lab.Chunks c WHERE c.DocId=d.DocId AND c.Version=d.Version AND c.OverlapPct=p.OverlapPct)) THROW 51003,'FAIL_RESULT_CONTRACT: Dokument-/Profilabdeckung fehlt.',1;
IF EXISTS(SELECT 1 FROM lab.Chunks c JOIN lab.Documents d ON d.DocId=c.DocId AND d.Version=c.Version WHERE CONVERT(varbinary(max),c.ChunkText)<>CONVERT(varbinary(max),SUBSTRING(d.Content,CONVERT(int,c.ChunkOffset),c.ChunkLength))) THROW 51003,'FAIL_RESULT_CONTRACT: Chunktext entspricht nicht dem dokumentierten Quellenbereich.',1;
IF EXISTS(SELECT DocId,Version,OverlapPct FROM lab.Chunks GROUP BY DocId,Version,OverlapPct HAVING MIN(ChunkOrder)<>1 OR MAX(ChunkOrder)<>COUNT(*)) THROW 51003,'FAIL_RESULT_CONTRACT: Chunkreihenfolge ist nicht lueckenlos.',1;
DECLARE @Versions int=(SELECT COUNT(*) FROM lab.Documents);
PRINT CONCAT('AI_ASSERT|comparison|document_versions|',@Versions);
DECLARE @Mismatches int=(SELECT COUNT(*) FROM lab.Chunks c JOIN lab.Documents d ON d.DocId=c.DocId AND d.Version=c.Version WHERE CONVERT(varbinary(max),c.ChunkText)<>CONVERT(varbinary(max),SUBSTRING(d.Content,CONVERT(int,c.ChunkOffset),c.ChunkLength)));
PRINT CONCAT('AI_ASSERT|comparison|source_mismatches|',@Mismatches);
PRINT 'SQLPERF_SUMMARY|PASS|OK';
