/* Separate diagnostic execution; do not combine these values with measured runs. */
/* Keep complete SHOWPLAN XML in sqlcmd output; this process emits only two plan results. */
:setvar SQLCMDMAXVARTYPEWIDTH 0

SET NOCOUNT ON;
SET XACT_ABORT ON;
BEGIN TRY
    SET STATISTICS XML ON;

    SELECT PathCount=COUNT_BIG(*)
    FROM dbo.Person AS p1,dbo.FriendOf AS e1,dbo.Person AS p2,dbo.FriendOf AS e2,dbo.Person AS p3
    WHERE MATCH(p1-(e1)->p2-(e2)->p3);

    SELECT PathCount=COUNT_BIG(*)
    FROM dbo.RelPerson AS p1
    JOIN dbo.RelFriend AS e1 ON e1.FromPersonId=p1.PersonId
    JOIN dbo.RelPerson AS p2 ON p2.PersonId=e1.ToPersonId
    JOIN dbo.RelFriend AS e2 ON e2.FromPersonId=p2.PersonId
    JOIN dbo.RelPerson AS p3 ON p3.PersonId=e2.ToPersonId;

    SET STATISTICS XML OFF;
END TRY
BEGIN CATCH
    SET STATISTICS XML OFF;
    THROW;
END CATCH;
SELECT 1 AS Sequence,'PLAN_EVIDENCE' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       N'Actual-Plan-XML für je eine getrennte Diagnoseausführung ausgegeben' AS ObservedValue,
       N'SHOWPLAN vorab geprüft; Planlauf nicht Teil der Performance-Messreihe' AS RequiredValue,
       N'Planmetadaten dienen der Interpretation, nicht als Ergebnis der fünf Messpaare.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
