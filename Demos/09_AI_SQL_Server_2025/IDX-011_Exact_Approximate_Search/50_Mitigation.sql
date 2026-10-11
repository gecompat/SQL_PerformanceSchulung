/* IDX-011: gebundenes DEC-074-Profil; eigene synthetische Datenbank. */
SET NOCOUNT ON;
IF DATALENGTH(N'$(DemoId)')<>DATALENGTH(N'IDX-011')
 OR CONVERT(varbinary(max),N'$(DemoId)')<>CONVERT(varbinary(max),N'IDX-011')
 OR DATALENGTH(N'$(RunToken)')<>32 OR N'$(RunToken)' COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-F0-9]%'
 OR DATALENGTH(N'$(TargetDatabase)')<>DATALENGTH(N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR CONVERT(varbinary(max),N'$(TargetDatabase)')<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX011_$(RunToken)')
 THROW 51000,'FAIL_CONTRACT: Vollständige Demo-/Token-/DB-Bindung fehlt.',1;
IF DATALENGTH(N'$(ConfirmIsolatedLab)')<>2 OR CONVERT(varbinary(max),N'$(ConfirmIsolatedLab)')<>CONVERT(varbinary(max),N'1')
 OR DATALENGTH(N'$(HighImpactConfirmed)')<>2 OR CONVERT(varbinary(max),N'$(HighImpactConfirmed)')<>CONVERT(varbinary(max),N'1')
 OR COALESCE(TRY_CONVERT(int,N'$(MaximumRuntimeSeconds)'),-1)<>300
 THROW 51000,'FAIL_SAFETY: YELLOW-Bestätigung und festes Laufbudget fehlen.',1;


IF (SELECT COUNT(*) FROM (VALUES
 (N'SQLPERF.Project',N'SQL_PerformanceSchulung'),
 (N'SQLPERF.ContractVersion',N'1.0'),
 (N'SQLPERF.DemoId',N'IDX-011'),
 (N'SQLPERF.RunToken',N'$(RunToken)')) e(Name,Expected)
 JOIN sys.extended_properties p ON p.name=e.Name AND p.class=0
 AND DATALENGTH(p.name)=DATALENGTH(e.Name)
 AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 AND p.major_id=0 AND p.minor_id=0
 WHERE DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Expected)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=
 CONVERT(varbinary(max),e.Expected))<>4
 THROW 51001,'Full ownership binding lost.',1;

IF OBJECT_ID(N'dbo.PreviewState',N'U') IS NULL
 THROW 51003,'Persistent preview baseline missing.',1;
IF (SELECT COUNT(*) FROM dbo.PreviewState)<>1
 THROW 51003,'Persistent preview baseline count invalid.',1;
IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE Id=1 AND OriginalValue IN(0,1)
 AND DATALENGTH(RunToken)=DATALENGTH(N'$(RunToken)')
 AND CONVERT(varbinary(max),RunToken)=CONVERT(varbinary(max),N'$(RunToken)'))
 THROW 51003,'Persistent preview baseline invalid.',1;

IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE MaxDopOriginal=0)
 THROW 51003,'Persistent actual MAXDOP baseline invalid.',1;

IF (SELECT COUNT(*) FROM sys.database_scoped_configurations WHERE
 (name=N'PREVIEW_FEATURES' AND TRY_CONVERT(int,value)=1) OR
 (name=N'MAXDOP' AND TRY_CONVERT(int,value)=1))<>2
 THROW 51003,'Actual preview and MAXDOP must both be one.',1;

IF DATALENGTH(DB_NAME())<>DATALENGTH(N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR NOT EXISTS(SELECT 1 FROM sys.schemas WHERE schema_id=SCHEMA_ID(N'lab')
 AND DATALENGTH(name)=DATALENGTH(N'lab') AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'lab'))
 OR NOT EXISTS(SELECT 1 FROM sys.tables WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND schema_id=SCHEMA_ID(N'lab') AND DATALENGTH(name)=DATALENGTH(N'VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'VectorFixture'))
 THROW 51003,'FAIL_STATE: Vollständiger tatsächlicher Quellenkontext verändert.',1;
IF (SELECT COUNT(*) FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture'))<>2
 OR NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'Id') AND DATALENGTH(name)=4
 AND TYPE_NAME(system_type_id)=N'int' AND is_nullable=0 AND is_computed=0)
 OR NOT EXISTS(SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'V') AND DATALENGTH(name)=2
 AND vector_dimensions=3 AND vector_base_type=0 AND is_nullable=0 AND is_computed=0)
 OR NOT EXISTS(SELECT 1 FROM sys.indexes i JOIN sys.index_columns c
 ON c.object_id=i.object_id AND c.index_id=i.index_id JOIN sys.columns v
 ON v.object_id=c.object_id AND v.column_id=c.column_id
 WHERE i.object_id=OBJECT_ID(N'lab.VectorFixture') AND i.type=1 AND i.is_primary_key=1
 AND i.is_unique=1 AND i.is_disabled=0 AND i.is_hypothetical=0 AND c.key_ordinal=1
 AND CONVERT(varbinary(max),v.name)=CONVERT(varbinary(max),N'Id')
 AND (SELECT COUNT(*) FROM sys.index_columns k WHERE k.object_id=i.object_id AND k.index_id=i.index_id)=1)
 THROW 51003,'FAIL_STATE: Tatsächlicher float32-VECTOR(3)/clustered-INT-PK-Vertrag verändert.',1;

IF (SELECT COUNT(*) FROM lab.VectorFixture)<>1000
 OR EXISTS(SELECT 1 FROM lab.VectorFixture WHERE Id NOT BETWEEN 1 AND 1000)
 OR (SELECT COUNT(*) FROM lab.FrozenSource)<>1000
 OR EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture
 EXCEPT SELECT Id,BytesValue FROM lab.FrozenSource)
 OR EXISTS(SELECT Id,BytesValue FROM lab.FrozenSource EXCEPT
 SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture)
 THROW 51003,'FAIL_STATE: Vollständige persistierte Quelle verändert.',1;

IF (SELECT COUNT(*) FROM lab.IndexEvidence)<>1 OR NOT EXISTS(SELECT 1 FROM lab.IndexEvidence WHERE Id=1)
 THROW 51003,'FAIL_STATE: Persistierte eigene Indexevidenz fehlt.',1;
DECLARE @ObservedIndex nvarchar(max)=(SELECT * FROM sys.vector_indexes
 WHERE object_id=OBJECT_ID(N'lab.VectorFixture') AND name=N'IDX011_OwnVector'
 ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
IF (SELECT COUNT(*) FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture'))<>1
 OR NOT EXISTS(SELECT 1 FROM lab.IndexEvidence WHERE
 DATALENGTH(MetadataJson)=DATALENGTH(@ObservedIndex)
 AND CONVERT(varbinary(max),MetadataJson)=CONVERT(varbinary(max),@ObservedIndex))
 THROW 51003,'FAIL_STATE: Vollständige eigene Indexmetadaten verändert.',1;

DROP INDEX IDX011_OwnVector ON lab.VectorFixture;
IF EXISTS(SELECT 1 FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture'))
 THROW 51003,'FAIL_STATE: Eigener Vektorindex nach Gegenmaßnahme verblieben.',1;
SELECT N'IDX011_MITIGATION|EXACT_FALLBACK|INDEX_ABSENT';
PRINT 'SQLPERF_SUMMARY|PASS|OK';
