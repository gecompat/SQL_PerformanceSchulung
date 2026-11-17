SET NOCOUNT ON;SET XACT_ABORT ON;SET QUOTED_IDENTIFIER ON;
IF TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'))=15 AND ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW SERVER STATE'),0)<>1
    THROW 51006,'FAIL_PERMISSION: Konversionsgraph kann nicht gelesen werden.',1;
IF TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'))>=16 AND ISNULL(HAS_PERMS_BY_NAME(NULL,NULL,'VIEW SERVER PERFORMANCE STATE'),0)<>1
    THROW 51006,'FAIL_PERMISSION: Konversionsgraph kann nicht gelesen werden.',1;
DECLARE @DbId int=DB_ID(),@A smallint,@B smallint,@Start datetime2(7),@End datetime2(7)=SYSUTCDATETIME(),
        @Object nvarchar(776)=CONCAT(DB_NAME(),N'.lab.DeadlockRows'),@HoBT bigint,@Matches int=0;
SELECT @Start=StartedAtUtc FROM lab.ConversionRun WHERE Attempt='CONVERT' AND RunToken='$(RunToken)' AND DatabaseId=@DbId;
SELECT @A=SessionId FROM lab.ConversionEvidence WHERE Attempt='CONVERT' AND RoleName='ACTOR_A';
SELECT @B=SessionId FROM lab.ConversionEvidence WHERE Attempt='CONVERT' AND RoleName='ACTOR_B';
SELECT @HoBT=hobt_id FROM sys.partitions WHERE object_id=OBJECT_ID(N'lab.DeadlockRows') AND index_id=1;
IF @Start IS NULL OR @A IS NULL OR @B IS NULL OR @A=@B OR @HoBT IS NULL
    THROW 51006,'FAIL_RESULT_CONTRACT: Konversionslauf, Akteure oder Indexpartition sind nicht gebunden.',1;
;WITH Targets AS
(
    SELECT TRY_CONVERT(xml,st.target_data) AS TargetData
    FROM sys.dm_xe_session_targets AS st
    JOIN sys.dm_xe_sessions AS s ON s.address=st.event_session_address
    WHERE s.name=N'system_health' AND st.target_name=N'ring_buffer'
), Events AS
(
    SELECT e.query('.') AS Graph
    FROM Targets
    CROSS APPLY TargetData.nodes('//event[@name="xml_deadlock_report"]') AS X(e)
), Bound AS
(
    SELECT Graph,
           TRY_CONVERT(datetimeoffset(7),Graph.value('(/event/@timestamp)[1]','nvarchar(40)'),127) AS EventAt,
           Graph.value('count(/event/data[@name="xml_report"]/value/deadlock/process-list/process)','int') AS ProcessCount,
           Graph.value('count(/event/data[@name="xml_report"]/value/deadlock/resource-list/keylock[@dbid=sql:variable("@DbId") and @objectname=sql:variable("@Object") and @indexname="PK_DeadlockRows" and @hobtid=sql:variable("@HoBT")])','int') AS KeyLockCount,
           Graph.value('(/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@A")]/@id)[1]','varchar(128)') AS ProcessA,
           Graph.value('(/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@B")]/@id)[1]','varchar(128)') AS ProcessB
    FROM Events
)
SELECT @Matches=COUNT(*)
FROM Bound
WHERE EventAt IS NOT NULL
  AND CONVERT(datetime2(7),EventAt)>=@Start
  AND CONVERT(datetime2(7),EventAt)<=@End
  AND ProcessCount=2
  AND KeyLockCount=2
  AND NULLIF(ProcessA,'') IS NOT NULL
  AND NULLIF(ProcessB,'') IS NOT NULL
  AND Graph.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@A") and @currentdb=sql:variable("@DbId")]')=1
  AND Graph.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid=sql:variable("@B") and @currentdb=sql:variable("@DbId")]')=1
  AND Graph.exist('/event/data[@name="xml_report"]/value/deadlock/victim-list/victimProcess[@id=sql:column("Bound.ProcessA")]')=1
  AND Graph.exist('/event/data[@name="xml_report"]/value/deadlock/resource-list/keylock[@dbid=sql:variable("@DbId") and @objectname=sql:variable("@Object") and @indexname="PK_DeadlockRows" and @hobtid=sql:variable("@HoBT")][owner-list/owner[@id=sql:column("Bound.ProcessA") and @mode="S"]][waiter-list/waiter[@id=sql:column("Bound.ProcessB") and @mode="X" and @requestType="convert"]]')=1
  AND Graph.exist('/event/data[@name="xml_report"]/value/deadlock/resource-list/keylock[@dbid=sql:variable("@DbId") and @objectname=sql:variable("@Object") and @indexname="PK_DeadlockRows" and @hobtid=sql:variable("@HoBT")][owner-list/owner[@id=sql:column("Bound.ProcessB") and @mode="S"]][waiter-list/waiter[@id=sql:column("Bound.ProcessA") and @mode="X" and @requestType="convert"]]')=1;
IF @Matches<>1
BEGIN
    THROW 51006,'FAIL_RESULT_CONTRACT: Kein eindeutiger same-key S-to-X-Konversionsgraph fuer diesen Lauf.',1;
END;
UPDATE lab.ConversionRun SET GraphCount=@Matches WHERE Attempt='CONVERT' AND RunToken='$(RunToken)' AND DatabaseId=@DbId;
IF @@ROWCOUNT<>1 THROW 51006,'FAIL_RESULT_CONTRACT: Graphbefund konnte nicht an den Lauf gebunden werden.',1;
SELECT @DbId AS DatabaseId,@A AS ActorASpid,@B AS ActorBSpid,@HoBT AS HoBT,@Matches AS MatchingConversionGraphs;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
