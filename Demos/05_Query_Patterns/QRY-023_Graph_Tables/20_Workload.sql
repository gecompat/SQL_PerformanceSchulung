/* QRY-023: deterministic 10,000-path data and owned-object measurement wrapper. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId nvarchar(max),@RunToken nvarchar(max),@RequestedRunToken nvarchar(20)='$(RunToken)',@Project nvarchar(max),@Contract nvarchar(max);
SELECT @Project=MAX(CASE WHEN name=N'SQLPERF.Project' THEN CONVERT(nvarchar(max),value) END),
       @Contract=MAX(CASE WHEN name=N'SQLPERF.ContractVersion' THEN CONVERT(nvarchar(max),value) END),
       @DemoId=MAX(CASE WHEN name=N'SQLPERF.DemoId' THEN CONVERT(nvarchar(max),value) END),
       @RunToken=MAX(CASE WHEN name=N'SQLPERF.RunToken' THEN CONVERT(nvarchar(max),value) END)
FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;
IF DB_ID()<=4 OR @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
   OR @DemoId IS NULL OR @DemoId COLLATE Latin1_General_100_BIN2<>N'QRY-023' OR DATALENGTH(@DemoId)<>DATALENGTH(N'QRY-023')
   OR @RunToken IS NULL OR @RunToken COLLATE Latin1_General_100_BIN2<>CONVERT(nvarchar(max),@RequestedRunToken)
   OR DATALENGTH(@RunToken)<>DATALENGTH(CONVERT(nvarchar(max),@RequestedRunToken))
    THROW 51001,'FAIL_SAFETY: Workloadaufbau außerhalb der vollständig markierten QRY-023-Testdatenbank verweigert.',1;

IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
DROP TABLE IF EXISTS dbo.OracleRelFriend;
DROP TABLE IF EXISTS dbo.OracleRelPerson;
DROP TABLE IF EXISTS dbo.RelFriend;
DROP TABLE IF EXISTS dbo.RelPerson;
DROP TABLE IF EXISTS dbo.OracleFriendOf;
DROP TABLE IF EXISTS dbo.OraclePerson;
DROP TABLE IF EXISTS dbo.FriendOf;
DROP TABLE IF EXISTS dbo.Person;

CREATE TABLE dbo.Person
(
    PersonId int NOT NULL,
    CONSTRAINT PK_Qry023_Person PRIMARY KEY CLUSTERED(PersonId)
) AS NODE;
CREATE TABLE dbo.FriendOf AS EDGE;
CREATE TABLE dbo.RelPerson
(
    PersonId int NOT NULL CONSTRAINT PK_Qry023_RelPerson PRIMARY KEY CLUSTERED
);
CREATE TABLE dbo.RelFriend
(
    FromPersonId int NOT NULL,
    ToPersonId int NOT NULL,
    CONSTRAINT PK_Qry023_RelFriend PRIMARY KEY CLUSTERED(FromPersonId,ToPersonId)
);

CREATE TABLE dbo.OraclePerson
(
    PersonId int NOT NULL,
    CONSTRAINT PK_Qry023_OraclePerson PRIMARY KEY CLUSTERED(PersonId)
) AS NODE;
CREATE TABLE dbo.OracleFriendOf AS EDGE;
CREATE TABLE dbo.OracleRelPerson
(
    PersonId int NOT NULL CONSTRAINT PK_Qry023_OracleRelPerson PRIMARY KEY CLUSTERED
);
CREATE TABLE dbo.OracleRelFriend
(
    FromPersonId int NOT NULL,
    ToPersonId int NOT NULL,
    CONSTRAINT PK_Qry023_OracleRelFriend PRIMARY KEY CLUSTERED(FromPersonId,ToPersonId)
);

;WITH Digits(n) AS (SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) AS d(n)),
PathNumbers AS
(
    SELECT n=d0.n+d1.n*10+d2.n*100+d3.n*1000
    FROM Digits AS d0 CROSS JOIN Digits AS d1 CROSS JOIN Digits AS d2 CROSS JOIN Digits AS d3
), NodeValues AS
(
    SELECT PersonId=3*p.n+v.RoleOffset
    FROM PathNumbers AS p CROSS APPLY (VALUES(1),(2),(3)) AS v(RoleOffset)
)
INSERT dbo.Person(PersonId) SELECT PersonId FROM NodeValues;

INSERT dbo.RelPerson(PersonId) SELECT PersonId FROM dbo.Person;
INSERT dbo.FriendOf($from_id,$to_id)
SELECT sourcePerson.$node_id,targetPerson.$node_id
FROM dbo.Person AS sourcePerson
JOIN dbo.Person AS targetPerson ON targetPerson.PersonId=sourcePerson.PersonId+1
WHERE sourcePerson.PersonId BETWEEN 1 AND 29999 AND sourcePerson.PersonId%3 IN (1,2);
INSERT dbo.RelFriend(FromPersonId,ToPersonId)
SELECT PersonId,PersonId+1 FROM dbo.RelPerson
WHERE PersonId BETWEEN 1 AND 29999 AND PersonId%3 IN (1,2);

INSERT dbo.OraclePerson(PersonId) VALUES(1),(2),(3),(4),(5);
INSERT dbo.OracleRelPerson(PersonId) VALUES(1),(2),(3),(4),(5);
INSERT dbo.OracleFriendOf($from_id,$to_id)
SELECT sourcePerson.$node_id,targetPerson.$node_id
FROM dbo.OraclePerson AS sourcePerson
JOIN dbo.OraclePerson AS targetPerson ON (sourcePerson.PersonId=1 AND targetPerson.PersonId=2)
   OR (sourcePerson.PersonId=2 AND targetPerson.PersonId=5)
   OR (sourcePerson.PersonId=1 AND targetPerson.PersonId=3)
   OR (sourcePerson.PersonId=3 AND targetPerson.PersonId=5);
INSERT dbo.OracleRelFriend(FromPersonId,ToPersonId)
VALUES(1,2),(2,5),(1,3),(3,5);

CREATE INDEX IX_Qry023_FriendOf_From_To ON dbo.FriendOf($from_id,$to_id);

IF (SELECT COUNT_BIG(*) FROM dbo.Person)<>30000
   OR (SELECT COUNT_BIG(*) FROM dbo.FriendOf)<>20000
   OR (SELECT COUNT_BIG(*) FROM dbo.RelPerson)<>30000
   OR (SELECT COUNT_BIG(*) FROM dbo.RelFriend)<>20000
    THROW 51003,'FAIL_EXECUTION: QRY-023-Messworkload ist nicht vollständig aufgebaut.',1;
GO

CREATE OR ALTER PROCEDURE lab.USP_Qry023MeasureVariant
    @Variant varchar(12),
    @Phase varchar(20),
    @Iteration int,
    @RunToken varchar(20),
    @MeasurementRunId uniqueidentifier OUTPUT,
    @PathCount bigint OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    IF @Variant NOT IN ('GRAPH','RELATIONAL') OR @Phase NOT IN ('WARMUP','BASELINE','COMPARISON') OR @Iteration<1
        THROW 51000,'FAIL_CONTRACT: Ungültige QRY-023-Varianten-, Phasen- oder Iterationskennung.',1;

    EXEC lab.USP_BeginMeasurement @DemoId='QRY-023',@RunToken=@RunToken,@Phase=@Phase,@Iteration=@Iteration,
         @CaptureSessionWaits=0,@MeasurementRunId=@MeasurementRunId OUTPUT;
    IF @Variant='GRAPH'
        SELECT @PathCount=COUNT_BIG(*)
        FROM dbo.Person AS p1,dbo.FriendOf AS e1,dbo.Person AS p2,dbo.FriendOf AS e2,dbo.Person AS p3
        WHERE MATCH(p1-(e1)->p2-(e2)->p3);
    ELSE
        SELECT @PathCount=COUNT_BIG(*)
        FROM dbo.RelPerson AS p1
        JOIN dbo.RelFriend AS e1 ON e1.FromPersonId=p1.PersonId
        JOIN dbo.RelPerson AS p2 ON p2.PersonId=e1.ToPersonId
        JOIN dbo.RelFriend AS e2 ON e2.FromPersonId=p2.PersonId
        JOIN dbo.RelPerson AS p3 ON p3.PersonId=e2.ToPersonId;

    EXEC lab.USP_EndMeasurement @DemoId='QRY-023',@RunToken=@RunToken,@MeasurementRunId=@MeasurementRunId,@ResultRows=@PathCount;
END;
GO

GRANT SELECT ON OBJECT::dbo.Person TO [READER];
GRANT SELECT ON OBJECT::dbo.FriendOf TO [READER];
GRANT SELECT ON OBJECT::dbo.RelPerson TO [READER];
GRANT SELECT ON OBJECT::dbo.RelFriend TO [READER];
GRANT SELECT ON OBJECT::dbo.OraclePerson TO [READER];
GRANT SELECT ON OBJECT::dbo.OracleFriendOf TO [READER];
GRANT SELECT ON OBJECT::dbo.OracleRelPerson TO [READER];
GRANT SELECT ON OBJECT::dbo.OracleRelFriend TO [READER];
GRANT SELECT ON OBJECT::lab.MeasurementRun TO [READER];
GRANT EXECUTE ON OBJECT::lab.USP_Qry023MeasureVariant TO [READER];

SELECT 1 AS Sequence,'WORKLOAD' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       N'30.000 Knoten; 20.000 gerichtete Kanten; 10.000 disjunkte Pfade; getrenntes 5/4-Oracle' AS ObservedValue,
       N'identische logische Graph- und Relationsdaten; exakte Markerbindung' AS RequiredValue,
       N'Das deterministische QRY-023-Workload ist erstellt.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
