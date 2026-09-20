/* DGN-007: genau eine reversible, querylokale Referenzänderung. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Original nvarchar(max), @Changed nvarchar(max), @Expected sysname=N'SQLPERF_LAB_DGN007_LOCAL', @ProcedurePosition int;
IF DB_NAME()<>@Expected THROW 51004, 'FAIL_CONTRACT: Mitigation muss in der markierten DGN-007-Testdatenbank laufen.', 1;
IF NOT EXISTS(SELECT 1 FROM lab.Dgn007ReferenceState WHERE StateId=1)
    THROW 51005, 'FAIL_STATE: Die Baseline hat den reversiblen Referenzzustand nicht vorbereitet.', 1;
SELECT @Original=OBJECT_DEFINITION(OBJECT_ID(N'dbo.usp_CaseSearch'));
IF @Original IS NULL THROW 51006, 'FAIL_STATE: Die markierte Suchprozedur fehlt.', 1;
IF EXISTS(SELECT 1 FROM lab.Dgn007ReferenceState WHERE StateId=1 AND MitigationApplied=1)
    THROW 51007, 'FAIL_STATE: Die Referenzänderung ist bereits aktiv; zuerst Cleanup ausführen.', 1;
IF CHARINDEX(N'ORDER BY i.ItemId;',@Original)=0
    THROW 51008, 'FAIL_CONTRACT: Der bekannte Originalvertrag der Suchprozedur ist nicht vorhanden.', 1;
UPDATE lab.Dgn007ReferenceState
SET OriginalProcedureDefinition=@Original, OriginalChecksum=HASHBYTES('SHA2_256',CONVERT(varbinary(max),@Original)), MitigationApplied=1
WHERE StateId=1;
SET @Changed=REPLACE(@Original,N'ORDER BY i.ItemId;',N'ORDER BY i.ItemId OPTION (RECOMPILE);');
/* OBJECT_DEFINITION kann den CREATE-Kopf mit abweichendem Whitespace liefern; nur der DDL-Kopf wird für die bestehende Prozedur ersetzt. */
SET @ProcedurePosition=CHARINDEX(N'PROCEDURE',@Changed);
IF @ProcedurePosition=0
    THROW 51014, 'FAIL_CONTRACT: Der erwartete Prozedurkopf für die reversible Änderung fehlt.', 1;
SET @Changed=N'ALTER '+SUBSTRING(@Changed,@ProcedurePosition,LEN(@Changed));
EXEC sys.sp_executesql @Changed;
SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'SUMMARY' AS CheckId, 'PASS' AS Outcome, 'OK' AS Code,
       N'eine querylokale, reversible Änderung aktiv' AS ObservedValue, N'genau eine Referenzvariable' AS RequiredValue,
       N'Der Originaltext wurde in der markierten Testdatenbank für Cleanup und Rückfall gesichert.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
