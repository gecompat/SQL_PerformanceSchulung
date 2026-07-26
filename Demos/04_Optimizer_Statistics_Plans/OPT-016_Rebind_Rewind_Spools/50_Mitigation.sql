/* OPT-016 mitigation: restore the access path and the controlled no-spool counterprobe. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

CREATE INDEX IX_WorkItemDetail_Group_Sequence
ON lab.WorkItemDetail(EntityGroupId, SequenceNumber DESC, WorkItemDetailId DESC)
INCLUDE(MeasureValue);
UPDATE STATISTICS lab.WorkItemDetail IX_WorkItemDetail_Group_Sequence WITH FULLSCAN;

EXEC(N'
ALTER PROCEDURE lab.usp_Opt016Workload
    @ProfileCode char(1),
    @ResultRowCount bigint OUTPUT,
    @ResultChecksum int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        @ResultRowCount = COUNT_BIG(*),
        @ResultChecksum = CHECKSUM_AGG(BINARY_CHECKSUM(pr.ProbeRequestId, detail.WorkItemDetailId, detail.MeasureValue))
    FROM lab.ProbeRequest AS pr
    CROSS APPLY
    (
        SELECT TOP (1) wd.WorkItemDetailId, wd.MeasureValue
        FROM lab.WorkItemDetail AS wd
        WHERE wd.EntityGroupId = pr.EntityGroupId
        ORDER BY wd.SequenceNumber DESC, wd.WorkItemDetailId DESC
    ) AS detail /*SQLPERF_OPT016_WORKLOAD*/
    WHERE pr.ProfileCode = @ProfileCode
    OPTION (MAXDOP 1, FORCE ORDER, LOOP JOIN, NO_PERFORMANCE_SPOOL);
END;
');
EXEC sys.sp_recompile N'lab.usp_Opt016Workload';

IF NOT EXISTS
(
    SELECT 1 FROM sys.indexes AS i
    INNER JOIN sys.objects AS o ON o.object_id = i.object_id
    INNER JOIN sys.schemas AS s ON s.schema_id = o.schema_id
    WHERE s.name = N'lab' AND o.name = N'WorkItemDetail'
      AND i.name = N'IX_WorkItemDetail_Group_Sequence'
)
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der OPT-016-Zugriffspfad wurde nicht wiederhergestellt.', 1;

SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       N'IX_WorkItemDetail_Group_Sequence per Fullscan erfasst; kontrollierte NO_PERFORMANCE_SPOOL-Gegenprobe wiederhergestellt' AS ObservedValue,
       N'passender querylokaler Zugriffspfad ohne globale Optimizer- oder Cacheänderung' AS RequiredValue,
       N'Die korrelierte Suche besitzt wieder einen direkten Vergleichspfad.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
