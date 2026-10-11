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

SET NOCOUNT ON;
USE [SQLPERF_LAB_IDX011_$(RunToken)];

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

DECLARE @Snapshot nvarchar(max)=(SELECT DB_ID() DatabaseId,DB_NAME() context,CONVERT(nvarchar(80),SERVERPROPERTY('ProductVersion')) build,
 TRY_CONVERT(int,SERVERPROPERTY('EngineEdition')) edition,
 OBJECT_ID(N'lab.VectorFixture') fixture_object,
 (SELECT COUNT(*) FROM sys.vector_indexes) vector_indexes,
 JSON_QUERY((SELECT * FROM dbo.PreviewState ORDER BY Id FOR JSON PATH,INCLUDE_NULL_VALUES)) baseline,
 JSON_QUERY((SELECT SCHEMA_NAME(schema_id) SchemaName,name TableName,object_id
 FROM sys.tables ORDER BY object_id FOR JSON PATH,INCLUDE_NULL_VALUES)) tables,
 JSON_QUERY((SELECT name,CONVERT(varbinary(max),CONVERT(nvarchar(max),value)) ValueBytes,
 DATALENGTH(CONVERT(nvarchar(max),value)) ByteLength FROM sys.extended_properties
 WHERE class=0 AND major_id=0 AND minor_id=0 ORDER BY name FOR JSON PATH,INCLUDE_NULL_VALUES)) markers,
 JSON_QUERY((SELECT configuration_id,name,TRY_CONVERT(int,value) value,
 TRY_CONVERT(int,value_in_use) value_in_use,TRY_CONVERT(int,minimum) minimum,
 TRY_CONVERT(int,maximum) maximum,description,is_dynamic,is_advanced
 FROM sys.configurations ORDER BY configuration_id FOR JSON PATH,INCLUDE_NULL_VALUES)) host,
 JSON_QUERY((SELECT configuration_id,name,TRY_CONVERT(int,value) value,
 TRY_CONVERT(int,value_for_secondary) value_for_secondary,is_value_default
 FROM sys.database_scoped_configurations ORDER BY configuration_id
 FOR JSON PATH,INCLUDE_NULL_VALUES)) scoped,
 JSON_QUERY((SELECT compatibility_level,recovery_model,collation_name,is_read_only,
 is_auto_close_on,is_auto_shrink_on,is_auto_create_stats_on,is_auto_update_stats_on,
 is_auto_update_stats_async_on,is_ansi_null_default_on,is_ansi_nulls_on,is_ansi_padding_on,
 is_ansi_warnings_on,is_arithabort_on,is_concat_null_yields_null_on,is_quoted_identifier_on,
 is_numeric_roundabort_on,is_recursive_triggers_on,is_cursor_close_on_commit_on,
 is_local_cursor_default,is_fulltext_enabled,is_trustworthy_on,is_db_chaining_on,
 is_parameterization_forced,is_read_committed_snapshot_on,page_verify_option,
 is_broker_enabled,is_honor_broker_priority_on,is_query_store_on,containment,
 target_recovery_time_in_seconds,delayed_durability,is_accelerated_database_recovery_on
 FROM sys.databases WHERE database_id=DB_ID() FOR JSON PATH,INCLUDE_NULL_VALUES)) options,
 JSON_QUERY((SELECT file_id,type,CONVERT(varbinary(max),name) NameBytes,max_size,
 growth,is_percent_growth FROM sys.database_files ORDER BY file_id
 FOR JSON PATH,INCLUDE_NULL_VALUES)) files
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
IF @Snapshot IS NULL OR DATALENGTH(@Snapshot)>120000
 THROW 51003,'Full snapshot exceeds the bounded client output width.',1;
SELECT @Snapshot;

PRINT 'SQLPERF_SUMMARY|PASS|OK';
