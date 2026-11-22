SET NOCOUNT ON;SET XACT_ABORT ON;SET QUOTED_IDENTIFIER ON;
DECLARE @A smallint,@B smallint,@DbId int=DB_ID(),@Start datetime2(7),@Deadline datetime2(3),@WaitObserved bit=0,
        @RangeOwnerCount int=0,
        @Object nvarchar(776)=CONCAT(DB_NAME(),N'.lab.RangeRows'),@Index sysname=N'PK_RangeRows',@HoBT bigint,
        @CandidateCount int=0,@Graph xml,@ProcessA varchar(128),@ProcessB varchar(128),@Victim varchar(128),
        @ResourceCount int=0,@DistinctResourceIds int=0,@AOwnsBWaits int=0,@BOwnsAWaits int=0,
        @VictimCount int=0,@VictimSpid smallint,
        @ActorVictims int,@ActorSurvivors int,@FinalCount int;
SELECT @Start=StartedAtUtc FROM lab.RangeRun WHERE Attempt='RANGE' AND RunToken='$(RunToken)' AND DatabaseId=@DbId;
IF @Start IS NULL
    THROW 51006,'FAIL_RESULT_CONTRACT: Range-Laufstartmarker fehlt.',1;
EXEC fwk.USP_WaitForSignal '$(DemoId)','$(RunToken)','A_RANGE_ACTOR_READY',12000;
EXEC fwk.USP_WaitForSignal '$(DemoId)','$(RunToken)','B_RANGE_ACTOR_READY',12000;
SELECT @A=MAX(CASE WHEN RoleName='ACTOR_A' THEN SessionId END),
       @B=MAX(CASE WHEN RoleName='ACTOR_B' THEN SessionId END)
FROM lab.RangeActors WITH(READUNCOMMITTED);
IF @A IS NULL OR @B IS NULL OR @A=@B
    THROW 51006,'FAIL_RESULT_CONTRACT: Range-Actor-SPIDs fehlen oder sind nicht getrennt.',1;
SELECT @HoBT=hobt_id FROM sys.partitions WHERE object_id=OBJECT_ID(N'lab.RangeRows') AND index_id=1;
IF @HoBT IS NULL THROW 51006,'FAIL_RESULT_CONTRACT: Range-Index-HoBT fehlt.',1;
SET @Deadline=DATEADD(second,12,SYSUTCDATETIME());
WHILE SYSUTCDATETIME()<@Deadline
BEGIN
    SELECT @RangeOwnerCount=COUNT(DISTINCT request_session_id)
    FROM sys.dm_tran_locks
    WHERE request_session_id IN(@A,@B) AND resource_type=N'KEY'
      AND resource_associated_entity_id=@HoBT AND request_status=N'GRANT'
      AND request_mode IN(N'RangeS-S',N'RangeS-U');
    IF @RangeOwnerCount=2 BREAK;
    WAITFOR DELAY '00:00:00.050';
END;
IF @RangeOwnerCount<>2
    THROW 51006,'FAIL_RESULT_CONTRACT: Beide Actors hielten vor der Freigabe keine KEY-Range-Sperre.',1;
EXEC fwk.USP_Signal '$(DemoId)','$(RunToken)','A_INSERT_GRANTED';
SET @Deadline=DATEADD(second,12,SYSUTCDATETIME());
WHILE SYSUTCDATETIME()<@Deadline
BEGIN
    IF EXISTS(SELECT 1 FROM sys.dm_exec_requests WHERE session_id=@A AND blocking_session_id=@B AND wait_type LIKE N'LCK_M%')
    BEGIN SET @WaitObserved=1;BREAK;END;
    WAITFOR DELAY '00:00:00.050';
END;
IF @WaitObserved<>1 THROW 51006,'FAIL_RESULT_CONTRACT: Actor A wartete nicht vor der Freigabe von Actor B.',1;
EXEC fwk.USP_Signal '$(DemoId)','$(RunToken)','B_INSERT_GRANTED';
EXEC fwk.USP_WaitForSignal '$(DemoId)','$(RunToken)','A_RANGE_DONE',20000;
EXEC fwk.USP_WaitForSignal '$(DemoId)','$(RunToken)','B_RANGE_DONE',20000;
SELECT @ActorVictims=COUNT(*) FROM lab.RangeActors WHERE Outcome='VICTIM' AND ErrorNumber=1205;
SELECT @ActorSurvivors=COUNT(*) FROM lab.RangeActors WHERE Outcome='SURVIVOR' AND ErrorNumber IS NULL;
SELECT @FinalCount=COUNT(*) FROM lab.RangeRows;
IF @ActorVictims<>1 OR @ActorSurvivors<>1 OR @FinalCount<>4
    THROW 51006,'FAIL_RESULT_CONTRACT: Range-Deadlockopfer, Survivor oder Endbestand stimmen nicht.',1;
IF EXISTS(SELECT 1 FROM lab.RangeRows WHERE KeyValue NOT IN(10,30,50,70,90))
 OR EXISTS(SELECT 1 FROM lab.RangeActors WHERE (RoleName='ACTOR_A' AND ((Outcome='SURVIVOR' AND NOT EXISTS(SELECT 1 FROM lab.RangeRows WHERE KeyValue=70)) OR (Outcome='VICTIM' AND EXISTS(SELECT 1 FROM lab.RangeRows WHERE KeyValue=70))))
                                      OR (RoleName='ACTOR_B' AND ((Outcome='SURVIVOR' AND NOT EXISTS(SELECT 1 FROM lab.RangeRows WHERE KeyValue=30)) OR (Outcome='VICTIM' AND EXISTS(SELECT 1 FROM lab.RangeRows WHERE KeyValue=30)))))
    THROW 51006,'FAIL_RESULT_CONTRACT: Endbestand stimmt nicht mit dem Actor-Survivor ueberein.',1;
DECLARE @Events TABLE(Graph xml NOT NULL,EventAt datetimeoffset(7) NULL);
INSERT @Events(Graph,EventAt)
SELECT G.Graph,TRY_CONVERT(datetimeoffset(7),G.Graph.value('(/event/@timestamp)[1]','nvarchar(40)'),127)
FROM sys.dm_xe_session_targets AS t
JOIN sys.dm_xe_sessions AS s ON s.address=t.event_session_address
CROSS APPLY(SELECT TRY_CONVERT(xml,t.target_data) AS TargetData) AS D
CROSS APPLY D.TargetData.nodes('//event[@name="xml_deadlock_report"]') AS X(e)
CROSS APPLY(SELECT e.query('.') AS Graph) AS G
WHERE s.name=N'system_health' AND t.target_name=N'ring_buffer';
SELECT @CandidateCount=COUNT(*)
FROM @Events AS E
WHERE E.EventAt>=@Start AND E.EventAt<=SYSUTCDATETIME()
  AND E.Graph.value('count(/event/data[@name="xml_report"]/value/deadlock/process-list/process)','int')=2
  AND E.Graph.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@A") and @currentdb=sql:variable("@DbId")]')=1
  AND E.Graph.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@B") and @currentdb=sql:variable("@DbId")]')=1;
IF @CandidateCount<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Kein eindeutiger, actor- und indexgebundener Range-Deadlockgraph.',1;
SELECT TOP(1) @Graph=Graph FROM @Events AS E WHERE E.EventAt>=@Start AND E.EventAt<=SYSUTCDATETIME()
  AND E.Graph.value('count(/event/data[@name="xml_report"]/value/deadlock/process-list/process)','int')=2
  AND E.Graph.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@A") and @currentdb=sql:variable("@DbId")]')=1
  AND E.Graph.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@B") and @currentdb=sql:variable("@DbId")]')=1;
SELECT @ProcessA=@Graph.value('(/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@A")]/@id)[1]','varchar(128)'),
       @ProcessB=@Graph.value('(/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@B")]/@id)[1]','varchar(128)'),
       @Victim=@Graph.value('(/event/data[@name="xml_report"]/value/deadlock/victim-list/victimProcess/@id)[1]','varchar(128)'),
       @VictimCount=@Graph.value('count(/event/data[@name="xml_report"]/value/deadlock/victim-list/victimProcess)','int');
IF @VictimCount<>1 OR @Victim IS NULL OR @Victim NOT IN(@ProcessA,@ProcessB)
    THROW 51006,'FAIL_RESULT_CONTRACT: Graph muss genau einen Actor als Opfer ausweisen.',1;
SELECT @VictimSpid=TRY_CONVERT(smallint,P.value('string((@spid)[1])','varchar(16)'))
FROM @Graph.nodes('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@id=sql:variable("@Victim")]') AS V(P);
DECLARE @Edges TABLE(ResourceId nvarchar(128),OwnerId varchar(128),OwnerMode varchar(32),WaiterId varchar(128),WaiterMode varchar(32),RequestType varchar(16),OwnerCount int,WaiterCount int);
INSERT @Edges(ResourceId,OwnerId,OwnerMode,WaiterId,WaiterMode,RequestType,OwnerCount,WaiterCount)
SELECT N.value('string((@id)[1])','nvarchar(128)'),
       N.value('string((owner-list/owner/@id)[1])','varchar(128)'),
       N.value('string((owner-list/owner/@mode)[1])','varchar(32)'),
       N.value('string((waiter-list/waiter/@id)[1])','varchar(128)'),
       N.value('string((waiter-list/waiter/@mode)[1])','varchar(32)'),
       N.value('string((waiter-list/waiter/@requestType)[1])','varchar(16)'),
       N.value('count(owner-list/owner)','int'),N.value('count(waiter-list/waiter)','int')
FROM @Graph.nodes('/event/data[@name="xml_report"]/value/deadlock/resource-list/keylock') AS K(N)
WHERE N.value('string((@dbid)[1])','varchar(16)')=CONVERT(varchar(16),@DbId)
  AND N.value('string((@objectname)[1])','nvarchar(776)')=@Object
  AND N.value('string((@indexname)[1])','nvarchar(128)')=@Index
  AND N.value('string((@hobtid)[1])','varchar(32)')=CONVERT(varchar(32),@HoBT);
SELECT @ResourceCount=COUNT(*),@DistinctResourceIds=COUNT(DISTINCT NULLIF(ResourceId,N'')) FROM @Edges;
DECLARE @Compatible TABLE(HeldMode varchar(32) NOT NULL,RequestedMode varchar(32) NOT NULL,PRIMARY KEY(HeldMode,RequestedMode));
INSERT @Compatible(HeldMode,RequestedMode)VALUES
('S','S'),('S','U'),('S','RangeS-S'),('S','RangeS-U'),('S','RangeI-N'),
('U','S'),('U','RangeS-S'),('U','RangeI-N'),('X','RangeI-N'),
('RangeS-S','S'),('RangeS-S','U'),('RangeS-S','RangeS-S'),('RangeS-S','RangeS-U'),
('RangeS-U','S'),('RangeS-U','RangeS-S'),('RangeI-N','S'),('RangeI-N','U'),('RangeI-N','X'),('RangeI-N','RangeI-N');
SELECT @AOwnsBWaits=COUNT(*) FROM @Edges AS E
WHERE E.OwnerId=@ProcessA AND E.WaiterId=@ProcessB AND E.RequestType='wait'
  AND E.OwnerCount=1 AND E.WaiterCount=1
  AND E.OwnerMode IN('S','U','X','RangeS-S','RangeS-U','RangeI-N')
  AND E.WaiterMode IN('S','U','X','RangeS-S','RangeS-U','RangeI-N')
  AND NOT EXISTS(SELECT 1 FROM @Compatible AS C WHERE C.HeldMode=E.OwnerMode AND C.RequestedMode=E.WaiterMode);
SELECT @BOwnsAWaits=COUNT(*) FROM @Edges AS E
WHERE E.OwnerId=@ProcessB AND E.WaiterId=@ProcessA AND E.RequestType='wait'
  AND E.OwnerCount=1 AND E.WaiterCount=1
  AND E.OwnerMode IN('S','U','X','RangeS-S','RangeS-U','RangeI-N')
  AND E.WaiterMode IN('S','U','X','RangeS-S','RangeS-U','RangeI-N')
  AND NOT EXISTS(SELECT 1 FROM @Compatible AS C WHERE C.HeldMode=E.OwnerMode AND C.RequestedMode=E.WaiterMode);
IF @ResourceCount<>2 OR @DistinctResourceIds<>2 OR @AOwnsBWaits<>1 OR @BOwnsAWaits<>1
   OR @VictimCount<>1 OR @VictimSpid IS NULL
   OR NOT EXISTS(SELECT 1 FROM lab.RangeActors WHERE SessionId=@VictimSpid AND Outcome='VICTIM' AND ErrorNumber=1205)
   OR NOT EXISTS(SELECT 1 FROM lab.RangeActors WHERE SessionId IN(@A,@B) AND SessionId<>@VictimSpid AND Outcome='SURVIVOR' AND ErrorNumber IS NULL)
    THROW 51006,'FAIL_RESULT_CONTRACT: Range-Graph bildet keinen reziproken Zyklus aus zwei inkompatiblen KEY-Waits.',1;
UPDATE lab.RangeRun SET WaitObserved=1,GraphCount=1 WHERE Attempt='RANGE' AND RunToken='$(RunToken)' AND DatabaseId=@DbId;
IF @@ROWCOUNT<>1 THROW 51006,'FAIL_RESULT_CONTRACT: Range-Graph konnte nicht an den Lauf gebunden werden.',1;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
