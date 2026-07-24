/* OPT-013 mitigation: refresh the stale filter statistic without changing server memory settings. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

UPDATE STATISTICS lab.SpillData ST_SpillData_FilterKey
WITH FULLSCAN,NORECOMPUTE;

DECLARE @ObjectId int=OBJECT_ID(N'lab.SpillData');
DECLARE @StatsId int=(SELECT stats_id FROM sys.stats WHERE object_id=@ObjectId AND name=N'ST_SpillData_FilterKey');
DECLARE @Rows bigint,@RowsSampled bigint,@ModificationCounter bigint;
SELECT @Rows=rows,@RowsSampled=rows_sampled,@ModificationCounter=modification_counter
FROM sys.dm_db_stats_properties(@ObjectId,@StatsId);

IF @Rows<>300000 OR @RowsSampled<>300000 OR @ModificationCounter<>0
    THROW 51006,'FAIL_RESULT_CONTRACT: Die OPT-013-Gegenmaßnahme hat keinen vollständig aktuellen Statistikzustand hergestellt.',1;

SELECT 1 Sequence,'MITIGATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       CONCAT(N'Rows=',@Rows,N'; RowsSampled=',@RowsSampled,N'; Modifications=',@ModificationCounter) ObservedValue,
       N'FULLSCAN über 300000 Zeilen; modification_counter=0' RequiredValue,
       N'Die Filterstatistik wurde vollständig aktualisiert; instanzweite Speicheroptionen bleiben unverändert.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
