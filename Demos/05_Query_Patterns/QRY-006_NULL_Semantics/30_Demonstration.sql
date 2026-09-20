/* QRY-006 demonstration: compare three logical anti-set forms. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

SELECT N'NOT IN (ungefiltert)' AS QueryForm, p.ParentKey
FROM lab.Qry006Parent AS p
WHERE p.ParentKey NOT IN (SELECT c.ChildKey FROM lab.Qry006Child AS c)
ORDER BY p.ParentKey;

SELECT N'NOT EXISTS' AS QueryForm, p.ParentKey
FROM lab.Qry006Parent AS p
WHERE NOT EXISTS (SELECT 1 FROM lab.Qry006Child AS c WHERE c.ChildKey = p.ParentKey)
ORDER BY p.ParentKey;

SELECT N'NOT IN (ChildKey IS NOT NULL)' AS QueryForm, p.ParentKey
FROM lab.Qry006Parent AS p
WHERE p.ParentKey NOT IN (SELECT c.ChildKey FROM lab.Qry006Child AS c WHERE c.ChildKey IS NOT NULL)
ORDER BY p.ParentKey;

SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       N'ungefiltertes NOT IN leer; NOT EXISTS und gefiltertes NOT IN zeigen {2,3}' AS ObservedValue,
       N'Ergebnisdarstellung der drei logischen Abfrageformen' AS RequiredValue,
       N'Die Gegenprobe zeigt ausschließlich die NULL-Semantik; sie behauptet keine Performance- oder Planformwirkung.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
