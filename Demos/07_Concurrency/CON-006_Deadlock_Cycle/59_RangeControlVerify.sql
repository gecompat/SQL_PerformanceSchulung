SET NOCOUNT ON;SET XACT_ABORT ON;SET QUOTED_IDENTIFIER ON;
DECLARE @DbId int=DB_ID(),@Start datetime2(7),@Finish datetime2(7)=SYSUTCDATETIME(),@A smallint,@B smallint,@Events int=0;
SELECT @Start=ControlStartedAtUtc FROM lab.RangeRun WHERE Attempt='RANGE' AND RunToken='$(RunToken)' AND DatabaseId=@DbId AND WaitObserved=1 AND GraphCount=1;
SELECT @A=MAX(CASE WHEN RoleName='ACTOR_A' THEN SessionId END),@B=MAX(CASE WHEN RoleName='ACTOR_B' THEN SessionId END)
FROM lab.RangeControlEvidence;
IF @Start IS NULL OR @A IS NULL OR @B IS NULL OR @A=@B
BEGIN
    DECLARE @Diagnostic nvarchar(2048)=CONCAT(
        N'FAIL_RESULT_CONTRACT: Serielle Range-Kontrolle oder getrennte Sessions fehlen. start=',
        COALESCE(CONVERT(nvarchar(40),@Start,127),N'NULL'),N'; actor_a=',COALESCE(CONVERT(nvarchar(12),@A),N'NULL'),
        N'; actor_b=',COALESCE(CONVERT(nvarchar(12),@B),N'NULL'));
    THROW 51006,@Diagnostic,1;
END;
IF (SELECT COUNT(*) FROM lab.RangeControlEvidence WHERE Outcome='INSERTED' AND ErrorNumber IS NULL)<>2
 OR (SELECT COUNT(*) FROM lab.RangeControlEvidence WHERE RoleName='ACTOR_A' AND KeyValue=70)<>1
 OR (SELECT COUNT(*) FROM lab.RangeControlEvidence WHERE RoleName='ACTOR_B' AND KeyValue=30)<>1
 OR (SELECT COUNT(*) FROM lab.RangeRows)<>5
 OR EXISTS(SELECT 1 FROM lab.RangeRows WHERE KeyValue NOT IN(10,30,50,70,90))
    THROW 51006,'FAIL_RESULT_CONTRACT: Serielle Range-Kontrolle hat nicht beide Inserts und den exakten Endbestand.',1;
;WITH Targets AS
(
    SELECT TRY_CONVERT(xml,t.target_data) AS TargetData
    FROM sys.dm_xe_session_targets AS t JOIN sys.dm_xe_sessions AS s ON s.address=t.event_session_address
    WHERE s.name=N'system_health' AND t.target_name=N'ring_buffer'
),Events AS
(
    SELECT e.query('.') AS Graph FROM Targets CROSS APPLY TargetData.nodes('//RingBufferTarget/event[@name="xml_deadlock_report"]') AS X(e)
)
SELECT @Events=COUNT(*) FROM Events
WHERE TRY_CONVERT(datetime2(7),Graph.value('(/event/@timestamp)[1]','nvarchar(40)'),127) BETWEEN @Start AND @Finish
  AND (Graph.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@A")]')=1
       OR Graph.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@B")]')=1);
IF @Events<>0 THROW 51006,'FAIL_RESULT_CONTRACT: Serielle Range-Kontrolle hatte ein passendes Deadlockereignis.',1;
UPDATE lab.RangeRun SET ControlFinishedAtUtc=@Finish,ControlDeadlockCount=@Events WHERE Attempt='RANGE' AND RunToken='$(RunToken)' AND DatabaseId=@DbId;
IF @@ROWCOUNT<>1 THROW 51006,'FAIL_RESULT_CONTRACT: Kontrollbefund konnte nicht an den Range-Lauf gebunden werden.',1;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
