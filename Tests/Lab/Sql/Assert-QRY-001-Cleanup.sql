SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @MajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));

IF @MajorVersion <> 17
    THROW 51000, 'LABINT-002 erwartet fuer diesen Vertical Slice SQL Server 2025.', 1;

IF DB_ID(N'SQLPERF_LAB_QRY001_LOCAL') IS NOT NULL
    THROW 51004, 'QRY-001-Cleanup unvollstaendig: Die markierte Testdatenbank ist noch vorhanden.', 1;

SELECT
    @MajorVersion AS ProductMajorVersion,
    N'QRY-001-Cleanup bestaetigt' AS Verification;
