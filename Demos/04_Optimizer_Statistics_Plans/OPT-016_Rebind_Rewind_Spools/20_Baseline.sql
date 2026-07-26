/* OPT-016 baseline: repeated-key profile with a supporting inner access path. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Rows bigint;
DECLARE @Checksum int;

EXEC sys.sp_recompile N'lab.usp_Opt016Workload';
EXEC lab.usp_Opt016Workload
    @ProfileCode = 'H',
    @ResultRowCount = @Rows OUTPUT,
    @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt016Capture
    @Phase = 'BASELINE',
    @ProfileCode = 'H',
    @ResultRowCount = @Rows,
    @ResultChecksum = @Checksum;

DECLARE @Loops int;
DECLARE @OuterRefs int;
DECLARE @Spools int;
DECLARE @Access nvarchar(60);
DECLARE @QueryHash binary(8);

SELECT @Loops = NestedLoopsCount, @OuterRefs = OuterReferenceCount,
       @Spools = SpoolCount, @Access = InnerAccessPhysicalOp, @QueryHash = QueryHash
FROM lab.Opt016Evidence
WHERE Phase = 'BASELINE';

IF @Rows <> 5000 OR @Checksum IS NULL OR @Loops < 1 OR @OuterRefs < 1
   OR @Spools <> 0 OR @Access NOT LIKE N'%Seek%' OR @QueryHash IS NULL
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die OPT-016-Baseline besitzt nicht den erwarteten korrelierten Seek-Pfad ohne Spool.', 1;

SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Rows=', @Rows, N'; Loops=', @Loops, N'; OuterReferences=', @OuterRefs,
              N'; Spools=', @Spools, N'; InnerAccess=', @Access) AS ObservedValue,
       N'5000 Ergebnisse; Nested Loops mit Outer References; seekfähiger innerer Zugriff; keine Spool' AS RequiredValue,
       N'Die indexgestützte Baseline ist erfasst.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
