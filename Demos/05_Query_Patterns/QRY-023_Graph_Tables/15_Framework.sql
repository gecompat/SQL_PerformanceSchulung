/* Install the canonical FWK-004 measurement helpers after owned-database setup. */
:r Demos/00_Framework/Sql/FWK_Measurement.sql

SELECT 1 AS Sequence,'FRAMEWORK' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       N'FWK-004-Referenz in der markierten QRY-023-Datenbank installiert' AS ObservedValue,
       N'sessionbezogene Messung ohne Wait-Erfassung' AS RequiredValue,
       N'Die Messprozeduren sind für dieselbe Session verfügbar.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
