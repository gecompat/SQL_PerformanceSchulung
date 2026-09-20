/* QRY-006 assertion: prove result sets independently of display order. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @MajorVersion int = CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @ExpectedCompatibility int = CASE @MajorVersion WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END;
DECLARE @ActualCompatibility int = (SELECT compatibility_level FROM sys.databases WHERE database_id = DB_ID());
IF @ExpectedCompatibility IS NULL OR @ActualCompatibility IS NULL OR @ActualCompatibility <> @ExpectedCompatibility
    THROW 51006, 'FAIL_RESULT_CONTRACT: Das Compatibility Level der Testdatenbank entspricht nicht der Versionsmatrix.', 1;
PRINT CONCAT('QRY006_DATABASE_CL|', @ActualCompatibility);

DECLARE @NotInCount int = (SELECT COUNT(*) FROM lab.Qry006Parent AS p WHERE p.ParentKey NOT IN (SELECT c.ChildKey FROM lab.Qry006Child AS c));
DECLARE @NotExistsCount int = (SELECT COUNT(*) FROM lab.Qry006Parent AS p WHERE NOT EXISTS (SELECT 1 FROM lab.Qry006Child AS c WHERE c.ChildKey = p.ParentKey));
DECLARE @FilteredNotInCount int = (SELECT COUNT(*) FROM lab.Qry006Parent AS p WHERE p.ParentKey NOT IN (SELECT c.ChildKey FROM lab.Qry006Child AS c WHERE c.ChildKey IS NOT NULL));

IF @NotInCount <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Ungefiltertes NOT IN muss bei Child={1,NULL} leer sein.', 1;
IF @NotExistsCount <> 2 OR @FilteredNotInCount <> 2
    THROW 51006, 'FAIL_RESULT_CONTRACT: NOT EXISTS und gefiltertes NOT IN müssen je zwei Werte liefern.', 1;

IF EXISTS
(
    SELECT p.ParentKey FROM lab.Qry006Parent AS p
    WHERE NOT EXISTS (SELECT 1 FROM lab.Qry006Child AS c WHERE c.ChildKey = p.ParentKey)
    EXCEPT SELECT v.ParentKey FROM (VALUES (2), (3)) AS v(ParentKey)
)
OR EXISTS
(
    SELECT v.ParentKey FROM (VALUES (2), (3)) AS v(ParentKey)
    EXCEPT SELECT p.ParentKey FROM lab.Qry006Parent AS p
           WHERE NOT EXISTS (SELECT 1 FROM lab.Qry006Child AS c WHERE c.ChildKey = p.ParentKey)
)
OR EXISTS
(
    SELECT p.ParentKey FROM lab.Qry006Parent AS p
    WHERE p.ParentKey NOT IN (SELECT c.ChildKey FROM lab.Qry006Child AS c WHERE c.ChildKey IS NOT NULL)
    EXCEPT SELECT v.ParentKey FROM (VALUES (2), (3)) AS v(ParentKey)
)
OR EXISTS
(
    SELECT v.ParentKey FROM (VALUES (2), (3)) AS v(ParentKey)
    EXCEPT SELECT p.ParentKey FROM lab.Qry006Parent AS p
           WHERE p.ParentKey NOT IN (SELECT c.ChildKey FROM lab.Qry006Child AS c WHERE c.ChildKey IS NOT NULL)
)
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die explizite Anti-Menge muss {2,3} sein.', 1;

SELECT 1 AS Sequence, 'ASSERTION' AS Phase, 'RESULT_CONTRACT' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'NOT IN=', @NotInCount, N'; NOT EXISTS=', @NotExistsCount, N'; gefiltertes NOT IN=', @FilteredNotInCount) AS ObservedValue,
       N'NOT IN leer; NOT EXISTS={2,3}; gefiltertes NOT IN={2,3}' AS RequiredValue,
       N'Der Ergebnisvertrag ist erfüllt.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
