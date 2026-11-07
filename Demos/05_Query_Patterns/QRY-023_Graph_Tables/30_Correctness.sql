/* Full tuple equality for the small oracle and the separate measurement profile. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @OracleExpected table(StartId int,MiddleId int,EndId int);
DECLARE @OracleGraph table(StartId int,MiddleId int,EndId int);
DECLARE @OracleRel table(StartId int,MiddleId int,EndId int);
DECLARE @GraphPaths table(StartId int,MiddleId int,EndId int);
DECLARE @RelPaths table(StartId int,MiddleId int,EndId int);
INSERT @OracleExpected VALUES(1,2,5),(1,3,5);

INSERT @OracleGraph(StartId,MiddleId,EndId)
SELECT p1.PersonId,p2.PersonId,p3.PersonId
FROM dbo.OraclePerson AS p1,dbo.OracleFriendOf AS e1,dbo.OraclePerson AS p2,dbo.OracleFriendOf AS e2,dbo.OraclePerson AS p3
WHERE MATCH(p1-(e1)->p2-(e2)->p3);
INSERT @OracleRel(StartId,MiddleId,EndId)
SELECT p1.PersonId,p2.PersonId,p3.PersonId
FROM dbo.OracleRelPerson AS p1
JOIN dbo.OracleRelFriend AS e1 ON e1.FromPersonId=p1.PersonId
JOIN dbo.OracleRelPerson AS p2 ON p2.PersonId=e1.ToPersonId
JOIN dbo.OracleRelFriend AS e2 ON e2.FromPersonId=p2.PersonId
JOIN dbo.OracleRelPerson AS p3 ON p3.PersonId=e2.ToPersonId;

IF EXISTS(SELECT StartId,MiddleId,EndId FROM @OracleGraph EXCEPT SELECT StartId,MiddleId,EndId FROM @OracleExpected)
   OR EXISTS(SELECT StartId,MiddleId,EndId FROM @OracleExpected EXCEPT SELECT StartId,MiddleId,EndId FROM @OracleGraph)
   OR EXISTS(SELECT StartId,MiddleId,EndId FROM @OracleRel EXCEPT SELECT StartId,MiddleId,EndId FROM @OracleExpected)
   OR EXISTS(SELECT StartId,MiddleId,EndId FROM @OracleExpected EXCEPT SELECT StartId,MiddleId,EndId FROM @OracleRel)
   OR (SELECT COUNT_BIG(*) FROM @OracleGraph)<>2 OR (SELECT COUNT_BIG(*) FROM @OracleRel)<>2
    THROW 51006,'FAIL_RESULT_CONTRACT: Das kleine Graph-/Relationsoracle stimmt nicht exakt mit den zwei erwarteten Pfaden überein.',1;

INSERT @GraphPaths(StartId,MiddleId,EndId)
SELECT p1.PersonId,p2.PersonId,p3.PersonId
FROM dbo.Person AS p1,dbo.FriendOf AS e1,dbo.Person AS p2,dbo.FriendOf AS e2,dbo.Person AS p3
WHERE MATCH(p1-(e1)->p2-(e2)->p3);
INSERT @RelPaths(StartId,MiddleId,EndId)
SELECT p1.PersonId,p2.PersonId,p3.PersonId
FROM dbo.RelPerson AS p1
JOIN dbo.RelFriend AS e1 ON e1.FromPersonId=p1.PersonId
JOIN dbo.RelPerson AS p2 ON p2.PersonId=e1.ToPersonId
JOIN dbo.RelFriend AS e2 ON e2.FromPersonId=p2.PersonId
JOIN dbo.RelPerson AS p3 ON p3.PersonId=e2.ToPersonId;

IF (SELECT COUNT_BIG(*) FROM @GraphPaths)<>10000 OR (SELECT COUNT_BIG(*) FROM @RelPaths)<>10000
   OR EXISTS(SELECT StartId,MiddleId,EndId FROM @GraphPaths EXCEPT SELECT StartId,MiddleId,EndId FROM @RelPaths)
   OR EXISTS(SELECT StartId,MiddleId,EndId FROM @RelPaths EXCEPT SELECT StartId,MiddleId,EndId FROM @GraphPaths)
   OR EXISTS(SELECT StartId,MiddleId,EndId FROM @GraphPaths GROUP BY StartId,MiddleId,EndId HAVING COUNT_BIG(*)<>1)
   OR EXISTS(SELECT StartId,MiddleId,EndId FROM @RelPaths GROUP BY StartId,MiddleId,EndId HAVING COUNT_BIG(*)<>1)
    THROW 51006,'FAIL_RESULT_CONTRACT: Das 10.000-Pfade-Profil ist unvollständig, nicht eindeutig oder zwischen Graph und Relation verschieden.',1;

SELECT StartId,MiddleId,EndId FROM @OracleGraph ORDER BY StartId,MiddleId,EndId;
SELECT 1 AS Sequence,'CORRECTNESS' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       CONCAT(N'Oracle=2; GraphPaths=',(SELECT COUNT_BIG(*) FROM @GraphPaths),N'; RelationalPaths=',(SELECT COUNT_BIG(*) FROM @RelPaths)) AS ObservedValue,
       N'kleines Zweipfadoracle exakt; 10.000 eindeutige Vollpfade je Variante; beidseitiges EXCEPT leer' AS RequiredValue,
       N'Ergebnisgleichheit wurde vor allen Messwiederholungen festgestellt.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
